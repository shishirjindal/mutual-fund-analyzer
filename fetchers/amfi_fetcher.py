"""
AMFI Fetcher - Fetches and parses NAVAll.txt from AMFI portal.
Filters for Direct Plan + Growth oriented funds and classifies by category.
"""

import logging
import requests
from typing import Dict, List, Optional
from constants.amfi_constants import (
    AMFI_URL, CATEGORY_KEYWORDS, DIRECT_KEYWORDS, GROWTH_KEYWORDS, EXCLUDE_KEYWORDS
)


class AmfiFetcher:
    """Fetches and parses the AMFI NAVAll.txt feed into categorized Direct Growth fund lists."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_all_categories(self) -> List[str]:
        """Return the list of all supported categories."""
        return list(CATEGORY_KEYWORDS.keys())

    def get_funds_for_category(self, category: str) -> List[Dict]:
        """
        Fetch all Direct Growth funds for a specific category.

        Returns:
            List of dicts with scheme_code and scheme_name.
        """
        result = self.fetch_and_parse(category_filter=category)
        return result.get(category, [])

    def fetch_and_parse(self, category_filter: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Fetch NAVAll.txt from AMFI and parse into categorized fund lists.

        Args:
            category_filter: If provided, return only funds matching this category.

        Returns:
            Dict mapping category name -> list of dicts with keys: scheme_code, scheme_name.
        """
        self.logger.info("Fetching AMFI NAVAll.txt from %s", AMFI_URL)
        response = requests.get(AMFI_URL, timeout=30)
        response.raise_for_status()

        categorized: Dict[str, List[Dict]] = {cat: [] for cat in CATEGORY_KEYWORDS}

        for line in response.text.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.split(";")
            if len(parts) < 4:
                continue

            scheme_code = parts[0].strip()
            scheme_name = parts[3].strip()

            if not scheme_code.isdigit():
                continue

            if not self._is_direct_growth(scheme_name):
                continue

            category = self._classify_category(scheme_name)
            if category is None:
                continue

            if category_filter and category != category_filter:
                continue

            categorized[category].append({
                "scheme_code": scheme_code,
                "scheme_name": scheme_name,
            })

        total = sum(len(v) for v in categorized.values())
        self.logger.info("Parsed %d Direct Growth funds across %d categories", total, len(categorized))
        return categorized

    def _is_direct_growth(self, name: str) -> bool:
        name_lower = name.lower()
        has_direct = any(k in name_lower for k in DIRECT_KEYWORDS)
        has_growth = any(k in name_lower for k in GROWTH_KEYWORDS)
        has_exclude = any(k in name_lower for k in EXCLUDE_KEYWORDS)
        return has_direct and has_growth and not has_exclude

    def _classify_category(self, name: str) -> Optional[str]:
        name_lower = name.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in name_lower for kw in keywords):
                return category
        return None
