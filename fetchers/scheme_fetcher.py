import json
import logging
import datetime
import pathlib
from mftool import Mftool
from typing import Dict, Any, Optional
from utils.fetch_utils import fetch_with_backoff
from constants.fetch_constants import NAV_CACHE_DIR, NAV_CACHE_TTL_DAYS

logger = logging.getLogger(__name__)


def _cache_dir() -> pathlib.Path:
    p = pathlib.Path(NAV_CACHE_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_from_disk(scheme_code: str) -> Optional[Dict[str, Any]]:
    """Return cached NAV data if within TTL, else None."""
    files = sorted(_cache_dir().glob(f"{scheme_code}_*.json"), reverse=True)
    if not files:
        return None
    latest = files[0]
    try:
        # Parse date from filename: {scheme_code}_{YYYY-MM-DD}.json
        date_str = latest.stem.split("_")[-1]
        file_date = datetime.date.fromisoformat(date_str)
        age_days = (datetime.date.today() - file_date).days
    except (ValueError, IndexError):
        age_days = NAV_CACHE_TTL_DAYS  # unparseable — treat as stale

    if age_days >= NAV_CACHE_TTL_DAYS:
        logger.info("Disk cache '%s' is %d days old — will refresh", latest.name, age_days)
        return None
    logger.info("Loading NAV data for scheme '%s' from disk cache (%s)", scheme_code, latest.name)
    return json.loads(latest.read_text(encoding="utf-8"))


def _save_to_disk(scheme_code: str, data: Dict[str, Any]) -> None:
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    p = _cache_dir() / f"{scheme_code}_{date_str}.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    logger.info("Saved NAV data for scheme '%s' to disk cache (%s)", scheme_code, p.name)


def _latest_cache_file(scheme_code: str) -> Optional[pathlib.Path]:
    files = sorted(_cache_dir().glob(f"{scheme_code}_*.json"), reverse=True)
    return files[0] if files else None


class SchemeFetcher:
    """Fetches historical NAV data for mutual fund schemes via mftool."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def fetch(self, scheme_code: str) -> tuple[Optional[Dict[str, Any]], bool]:
        """
        Fetch historical NAV data for a scheme.

        Priority: disk cache (< 7 days old) → network.
        On network failure, falls back to stale disk cache if available.

        Returns (data, from_cache) where from_cache=True means no network call was made.
        """
        self.logger.info("Fetching NAV data for scheme code '%s'", scheme_code)

        cached = _load_from_disk(scheme_code)
        if cached is not None:
            return cached, True

        mf_tool = Mftool()
        try:
            nav_data = fetch_with_backoff(
                mf_tool.get_scheme_historical_nav, scheme_code, as_json=True
            )
            if nav_data is None:
                self.logger.error(
                    "No data returned for scheme '%s' — may be invalid or delisted", scheme_code
                )
                return None, False

            result = json.loads(nav_data)
            self.logger.info(
                "Successfully fetched NAV data for '%s' (scheme code: %s)",
                result.get("scheme_name", "Unknown"), scheme_code,
            )
            _save_to_disk(scheme_code, result)
            return result, False

        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse JSON for scheme '%s': %s", scheme_code, e)
        except TypeError as e:
            self.logger.error("Unexpected response type for scheme '%s': %s", scheme_code, e)
        except Exception as e:
            self.logger.error("Unexpected error fetching scheme '%s': %s", scheme_code, e)

        # Fall back to stale cache rather than returning nothing
        stale = _latest_cache_file(scheme_code)
        if stale:
            self.logger.warning("Using stale disk cache '%s' due to fetch failure", stale.name)
            return json.loads(stale.read_text(encoding="utf-8")), True
        return None, False
