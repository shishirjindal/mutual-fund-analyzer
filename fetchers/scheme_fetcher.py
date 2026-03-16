import json
import logging
from mftool import Mftool
from typing import Dict, Any, Optional
from utils.fetch_utils import fetch_with_backoff


class SchemeFetcher:
    """Fetches historical NAV data for mutual fund schemes via mftool."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def fetch(self, scheme_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical NAV data for a scheme.

        Returns a dict with fund_house, scheme_type, scheme_category, scheme_code,
        scheme_name, scheme_start_date, and data (list of NAV entries), or None on error.
        """
        self.logger.info("Fetching historical NAV data for scheme code '%s'", scheme_code)
        mf_tool = Mftool()
        try:
            nav_data = fetch_with_backoff(
                mf_tool.get_scheme_historical_nav, scheme_code, as_json=True
            )

            if nav_data is None:
                self.logger.error(
                    "No data returned for scheme code '%s' — scheme may be invalid or delisted",
                    scheme_code,
                )
                return None

            result = json.loads(nav_data)
            self.logger.info(
                "Successfully fetched NAV data for '%s' (scheme code: %s)",
                result.get("scheme_name", "Unknown"), scheme_code,
            )
            return result

        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse JSON response for scheme code '%s': %s", scheme_code, e)
        except TypeError as e:
            self.logger.error("Unexpected response type for scheme code '%s': %s", scheme_code, e)
        except Exception as e:
            self.logger.error("Unexpected error fetching scheme code '%s': %s", scheme_code, e)
        return None
