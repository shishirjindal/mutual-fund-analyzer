import json
import logging
import datetime
import pathlib
import requests
from functools import lru_cache
from typing import Dict, Any, Optional
from utils.fetch_utils import fetch_with_backoff
from constants.benchmark_constants import (
    BENCHMARK_DEFAULT_INDEX, BENCHMARK_TRI_URL, BENCHMARK_TRI_HEADERS,
    BENCHMARK_TRI_START_DATE, BENCHMARK_CACHE_DIR, BENCHMARK_CACHE_TTL_DAYS,
    CATEGORY_BENCHMARK_MAP, SECTOR_BENCHMARK_MAP,
)

logger = logging.getLogger(__name__)


def _safe_index_name(index_name: str) -> str:
    return index_name.replace(" ", "_").replace("/", "-")


def _cache_dir() -> pathlib.Path:
    p = pathlib.Path(BENCHMARK_CACHE_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_from_disk(index_name: str) -> Optional[Dict[str, Any]]:
    """Find the most recent cache file for index_name. Return data if within TTL, else None."""
    prefix = _safe_index_name(index_name)
    files = sorted(_cache_dir().glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    latest = files[0]
    try:
        # Parse date from filename: {prefix}_{YYYY-MM-DD}.json
        date_str = latest.stem.split("_")[-1]
        file_date = datetime.date.fromisoformat(date_str)
        age_days = (datetime.date.today() - file_date).days
    except (ValueError, IndexError):
        age_days = BENCHMARK_CACHE_TTL_DAYS  # unparseable — treat as stale

    if age_days >= BENCHMARK_CACHE_TTL_DAYS:
        logger.info("Disk cache '%s' is %d days old — will refresh", latest.name, age_days)
        return None
    logger.info("Loading '%s' TRI data from disk cache (%s)", index_name, latest.name)
    return json.loads(latest.read_text(encoding="utf-8"))


def _save_to_disk(index_name: str, data: Dict[str, Any]) -> None:
    prefix = _safe_index_name(index_name)
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    p = _cache_dir() / f"{prefix}_{date_str}.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    logger.info("Saved '%s' TRI data to disk cache (%s)", index_name, p.name)
    # Delete any older cache files for this index
    for old in _cache_dir().glob(f"{prefix}_*.json"):
        if old != p:
            old.unlink()
            logger.debug("Deleted old cache file '%s'", old.name)


def _latest_cache_file(index_name: str) -> Optional[pathlib.Path]:
    """Return the most recent cache file for index_name, regardless of age."""
    prefix = _safe_index_name(index_name)
    files = sorted(_cache_dir().glob(f"{prefix}_*.json"), reverse=True)
    return files[0] if files else None


@lru_cache(maxsize=8)
def _fetch_tri_cached(index_name: str) -> Optional[Dict[str, Any]]:
    """Fetch TRI data — disk cache first, then network. In-process lru_cache on top."""
    cached = _load_from_disk(index_name)
    if cached is not None:
        return cached

    end_date = datetime.date.today().strftime("%d-%b-%Y")
    logger.info("Requesting TRI data for '%s' from %s to %s", index_name, BENCHMARK_TRI_START_DATE, end_date)

    payload = json.dumps({
        "cinfo": json.dumps({
            "name": index_name,
            "startDate": BENCHMARK_TRI_START_DATE,
            "endDate": end_date,
            "indexName": index_name,
        })
    })

    try:
        response = fetch_with_backoff(
            requests.post, BENCHMARK_TRI_URL, headers=BENCHMARK_TRI_HEADERS,
            data=payload, timeout=15
        )
        response.raise_for_status()
        records = json.loads(response.json()["d"])
        data = {
            "data": [
                {
                    "date": datetime.datetime.strptime(r["Date"], "%d %b %Y").strftime("%d-%m-%Y"),
                    "nav": float(r["TotalReturnsIndex"]),
                }
                for r in reversed(records)
            ]
        }
        logger.info("Fetched %d TRI data points for '%s'", len(data["data"]), index_name)
        _save_to_disk(index_name, data)
        return data
    except Exception as e:
        logger.error("Failed to fetch TRI data for '%s': %s", index_name, e)
        # Fall back to stale disk cache rather than returning nothing
        stale = _latest_cache_file(index_name)
        if stale:
            logger.warning("Using stale disk cache '%s' due to fetch failure", stale.name)
            return json.loads(stale.read_text(encoding="utf-8"))
        return None


class BenchmarkFetcher:
    """Fetches historical TRI (Total Return Index) data for NSE benchmark indices."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @staticmethod
    def index_for_category(category: str) -> str:
        """Return the appropriate benchmark index name for a fund category.

        `category` may be a raw mftool scheme_category string like
        'Equity Scheme - Large Cap Fund', so we do a case-insensitive
        substring match against the map keys.
        """
        category_lower = category.lower()
        for key, index in CATEGORY_BENCHMARK_MAP.items():
            if key.lower() in category_lower:
                return index
        return BENCHMARK_DEFAULT_INDEX

    @staticmethod
    def index_for_sector(sector: str) -> str:
        """Return the appropriate benchmark index name for a sector label."""
        return SECTOR_BENCHMARK_MAP.get(sector, BENCHMARK_DEFAULT_INDEX)

    def fetch(self, index_name: str = BENCHMARK_DEFAULT_INDEX) -> Optional[Dict[str, Any]]:
        """
        Fetch TRI data for a benchmark index.

        Priority: in-process lru_cache → disk cache (< 7 days old) → network.
        On network failure, falls back to stale disk cache if available.
        """
        self.logger.info("Fetching benchmark TRI data for index '%s'", index_name)
        return _fetch_tri_cached(index_name)

    def fetch_for_category(self, category: str) -> Optional[Dict[str, Any]]:
        """Resolve the correct benchmark for a fund category and fetch it."""
        index_name = self.index_for_category(category)
        self.logger.info("Category '%s' → benchmark '%s'", category, index_name)
        return self.fetch(index_name)

    def fetch_for_sector(self, sector: str) -> Optional[Dict[str, Any]]:
        """Resolve the correct benchmark for a sector label and fetch it."""
        index_name = self.index_for_sector(sector)
        self.logger.info("Sector '%s' → benchmark '%s'", sector, index_name)
        return self.fetch(index_name)
