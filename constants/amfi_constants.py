# -*- coding: utf-8 -*-

"""
AMFI-related constants for fetching and classifying mutual fund schemes.
"""

from typing import Dict, List

AMFI_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"

# Category definitions: order matters — more specific patterns first.
# Matching is case-insensitive against the fund name.
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Large Cap": ["large cap"],
    "Mid Cap": ["mid cap"],
    "Small Cap": ["small cap"],
    "Large & Mid Cap": ["large & mid cap", "large and mid cap", "large mid cap"],
    "Mid & Small Cap": ["mid & small cap", "mid and small cap", "mid small cap"],
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

# Keywords that must appear in the fund name to qualify as a Direct Plan
DIRECT_KEYWORDS: List[str] = ["direct"]

# Keywords that must appear in the fund name to qualify as Growth oriented
GROWTH_KEYWORDS: List[str] = ["growth"]

# Keywords that disqualify a fund (IDCW, dividend, bonus, etc.)
EXCLUDE_KEYWORDS: List[str] = [
    "idcw", "dividend", "bonus", "weekly", "monthly", "quarterly",
    "annual", "payout", "reinvest", "sweep",
]
