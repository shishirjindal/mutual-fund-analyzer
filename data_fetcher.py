import json
import time
import logging
import datetime
import requests
from mftool import Mftool
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Keywords that indicate a rate-limit / quota-exceeded response
_QUOTA_SIGNALS = ("quota exceeded", "rate limit", "too many requests", "throttled", "throttling")


def _is_quota_error(exc: Exception) -> bool:
    """Return True if the exception looks like a quota / rate-limit error."""
    return any(signal in str(exc).lower() for signal in _QUOTA_SIGNALS)


def _fetch_with_backoff(fn, *args, max_retries: int = 5, base_delay: float = 2.0, **kwargs):
    """
    Call fn(*args, **kwargs) with exponential backoff on quota/rate-limit errors.
    Delays: 2s, 4s, 8s, 16s, 32s. Raises on non-quota errors or exhausted retries.
    """
    delay = base_delay
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            if _is_quota_error(exc) and attempt < max_retries - 1:
                logger.warning(
                    "Rate limit hit calling %s — waiting %.0fs before retry (attempt %d of %d)",
                    fn.__name__, delay, attempt + 1, max_retries - 1,
                )
                time.sleep(delay)
                delay *= 2
            else:
                raise


class DataFetcher:
    """Fetcher class to retrieve mutual fund scheme and benchmark data."""

    _benchmark_cache: Dict[str, Any] = {}  # keyed by index_name

    @staticmethod
    def fetch_scheme_data(scheme_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical NAV data for the scheme.

        Returns a dict with fund_house, scheme_type, scheme_category, scheme_code,
        scheme_name, scheme_start_date, and data (list of NAV entries), or None on error.
        """
        logger.info("Fetching historical NAV data for scheme code '%s'", scheme_code)
        mf_tool = Mftool()
        try:
            nav_data = _fetch_with_backoff(
                mf_tool.get_scheme_historical_nav, scheme_code, as_json=True
            )

            if nav_data is None:
                logger.error(
                    "No data returned for scheme code '%s' — scheme may be invalid or delisted",
                    scheme_code,
                )
                return None

            result = json.loads(nav_data)
            logger.info(
                "Successfully fetched NAV data for '%s' (scheme code: %s)",
                result.get("scheme_name", "Unknown"), scheme_code,
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse JSON response for scheme code '%s': %s", scheme_code, e
            )
        except TypeError as e:
            logger.error(
                "Unexpected response type for scheme code '%s': %s", scheme_code, e
            )
        except Exception as e:
            logger.error(
                "Unexpected error fetching scheme code '%s': %s", scheme_code, e
            )
        return None

    @staticmethod
    def fetch_benchmark_data(index_name: str = "NIFTY 50") -> Optional[Dict[str, Any]]:
        """
        Fetch historical TRI (Total Return Index) data for a benchmark index from NSE.

        Returns a dict with 'data' key — list of {'date': 'DD-MM-YYYY', 'nav': float}
        sorted oldest-first, or None on error.
        """
        logger.info("Fetching benchmark TRI data for index '%s' from niftyindices.com", index_name)

        if index_name in DataFetcher._benchmark_cache:
            logger.info("Returning cached benchmark data for '%s'", index_name)
            return DataFetcher._benchmark_cache[index_name]

        url = "https://www.niftyindices.com/Backpage.aspx/getTotalReturnIndexString"
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Origin": "https://www.niftyindices.com",
            "X-Requested-With": "XMLHttpRequest",
        }

        start_date = "01-Jan-2000"
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
            response = _fetch_with_backoff(
                requests.post, url, headers=headers, data=payload, timeout=15
            )
            response.raise_for_status()
            records = json.loads(response.json()["d"])
            # Records arrive newest-first; reverse to oldest-first
            data = [
                {
                    "date": datetime.datetime.strptime(r["Date"], "%d %b %Y").strftime("%d-%m-%Y"),
                    "nav": float(r["TotalReturnsIndex"]),
                }
                for r in reversed(records)
            ]
            logger.info(
                "Successfully fetched %d TRI data points for benchmark '%s'",
                len(data), index_name,
            )
            result = {"data": data}
            DataFetcher._benchmark_cache[index_name] = result
            return result
        except Exception as e:
            logger.error(
                "Failed to fetch benchmark TRI data for '%s': %s", index_name, e
            )
            return None
