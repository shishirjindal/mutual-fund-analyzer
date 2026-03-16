import json
import logging
import datetime
import requests
from functools import lru_cache
from typing import Dict, Any, Optional
from utils.fetch_utils import fetch_with_backoff
from constants.benchmark_constants import (
    BENCHMARK_DEFAULT_INDEX, BENCHMARK_TRI_URL, BENCHMARK_TRI_HEADERS, BENCHMARK_TRI_START_DATE
)


@lru_cache(maxsize=8)
def _fetch_tri_cached(index_name: str) -> Optional[Dict[str, Any]]:
    """Module-level cached fetch — keyed by index_name, survives across BenchmarkFetcher instances."""
    logger = logging.getLogger(__name__)
    url = BENCHMARK_TRI_URL
    headers = BENCHMARK_TRI_HEADERS
    start_date = BENCHMARK_TRI_START_DATE
    end_date = datetime.date.today().strftime("%d-%b-%Y")
    logger.info("Requesting TRI data for '%s' from %s to %s", index_name, start_date, end_date)

    payload = json.dumps({
        "cinfo": json.dumps({
            "name": index_name,
            "startDate": start_date,
            "endDate": end_date,
            "indexName": index_name,
        })
    })

    try:
        response = fetch_with_backoff(
            requests.post, url, headers=headers, data=payload, timeout=15
        )
        response.raise_for_status()
        records = json.loads(response.json()["d"])
        data = [
            {
                "date": datetime.datetime.strptime(r["Date"], "%d %b %Y").strftime("%d-%m-%Y"),
                "nav": float(r["TotalReturnsIndex"]),
            }
            for r in reversed(records)
        ]
        logger.info("Successfully fetched %d TRI data points for '%s'", len(data), index_name)
        return {"data": data}
    except Exception as e:
        logger.error("Failed to fetch benchmark TRI data for '%s': %s", index_name, e)
        return None


class BenchmarkFetcher:
    """Fetches historical TRI (Total Return Index) data for NSE benchmark indices."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def fetch(self, index_name: str = BENCHMARK_DEFAULT_INDEX) -> Optional[Dict[str, Any]]:
        """
        Fetch historical TRI data for a benchmark index from niftyindices.com.

        Returns a dict with 'data' key — list of {'date': 'DD-MM-YYYY', 'nav': float}
        sorted oldest-first, or None on error. Results are cached by index_name.
        """
        self.logger.info("Fetching benchmark TRI data for index '%s'", index_name)
        return _fetch_tri_cached(index_name)
