"""
AMFI Fetcher - Fetches and parses NAVAll.txt from AMFI portal.
Filters for Direct Plan + Growth oriented funds and classifies by category.
"""

import requests
from typing import Dict, List, Optional

AMFI_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"

# Category definitions: order matters — more specific patterns first
# Matching is case-insensitive against the fund name
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Large Cap": ["large cap"],
    "Mid Cap": ["mid cap"],
    "Small Cap": ["small cap"],
    "Large & Mid Cap": ["large & mid cap", "large and mid cap", "large mid cap"],
    "Multi Cap": ["multi cap", "multicap"],
    "Flexi Cap": ["flexi cap", "flexicap", "flexible cap"],
    "Focused Fund": ["focused fund", "focused equity"],
    "Value Fund": ["value fund"],
    "Contra Fund": ["contra fund", "contra "],
    "ELSS": ["elss", "tax saver", "tax saving", "linked savings"],
    "Dividend Yield": ["dividend yield"],
    "Sectoral / Thematic": ["sectoral", "thematic", "infrastructure", "banking", "technology",
                            "pharma", "healthcare", "consumption", "energy", "manufacturing",
                            "psu", "mnc", "esg", "business cycle", "special opportunities"],
}

# Keywords that must appear in name to qualify as Direct Plan
DIRECT_KEYWORDS = ["direct"]

# Keywords that must appear in name to qualify as Growth oriented
GROWTH_KEYWORDS = ["growth"]

# Keywords that disqualify a fund (IDCW, dividend, bonus, etc.)
EXCLUDE_KEYWORDS = ["idcw", "dividend", "bonus", "weekly", "monthly", "quarterly",
                    "annual", "payout", "reinvest", "sweep"]


def _is_direct_growth(name: str) -> bool:
    """Return True if fund name indicates Direct Plan and Growth option."""
    name_lower = name.lower()
    has_direct = any(k in name_lower for k in DIRECT_KEYWORDS)
    has_growth = any(k in name_lower for k in GROWTH_KEYWORDS)
    has_exclude = any(k in name_lower for k in EXCLUDE_KEYWORDS)
    return has_direct and has_growth and not has_exclude


def _classify_category(name: str) -> Optional[str]:
    """Return the category for a fund name, or None if unclassified."""
    name_lower = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return None


def fetch_and_parse(category_filter: Optional[str] = None) -> Dict[str, List[Dict]]:
    """
    Fetch NAVAll.txt from AMFI and parse into categorized fund lists.

    Args:
        category_filter: If provided, return only funds matching this category.

    Returns:
        Dict mapping category name -> list of dicts with keys:
            scheme_code, scheme_name
    """
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

        # Must be numeric scheme code
        if not scheme_code.isdigit():
            continue

        # Must be Direct + Growth
        if not _is_direct_growth(scheme_name):
            continue

        category = _classify_category(scheme_name)
        if category is None:
            continue

        if category_filter and category != category_filter:
            continue

        categorized[category].append({
            "scheme_code": scheme_code,
            "scheme_name": scheme_name,
        })

    return categorized


def get_funds_for_category(category: str) -> List[Dict]:
    """
    Fetch all Direct Growth funds for a specific category.

    Returns:
        List of dicts with scheme_code and scheme_name.
    """
    result = fetch_and_parse(category_filter=category)
    return result.get(category, [])


def get_all_categories() -> List[str]:
    """Return the list of all supported categories."""
    return list(CATEGORY_KEYWORDS.keys())
