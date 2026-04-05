# -*- coding: utf-8 -*-
"""
Personal portfolio allocation by percentage.
All values sum to 100.
Update here whenever your allocation changes.
"""

from typing import List, Dict

PORTFOLIO: List[Dict] = [
    # ── Equity — Core (60%) ───────────────────────────────────────────────────
    {"asset_class": "Equity",        "category": "Large Cap",             "pct": 15.0},
    {"asset_class": "Equity",        "category": "Mid Cap",               "pct": 15.0},
    {"asset_class": "Equity",        "category": "Small Cap",             "pct":  7.5},
    {"asset_class": "Equity",        "category": "Flexi Cap",             "pct": 15.0},
    {"asset_class": "Equity",        "category": "Value Fund",            "pct":  3.75},
    {"asset_class": "Equity",        "category": "Contra Fund",           "pct":  3.75},
    # ── Equity — Sectoral (14%) ───────────────────────────────────────────────
    {"asset_class": "Equity",        "category": "Technology",            "pct":  2.3, "is_sectoral": True},
    {"asset_class": "Equity",        "category": "Banking & Financial",   "pct":  2.4, "is_sectoral": True},
    {"asset_class": "Equity",        "category": "Healthcare",            "pct":  2.4, "is_sectoral": True},
    {"asset_class": "Equity",        "category": "Energy",                "pct":  2.3, "is_sectoral": True},
    {"asset_class": "Equity",        "category": "Infrastructure",        "pct":  2.3, "is_sectoral": True},
    {"asset_class": "Equity",        "category": "Consumption",           "pct":  2.3, "is_sectoral": True},
    # ── International (11%) ───────────────────────────────────────────────────
    {"asset_class": "International", "category": "US Funds",              "pct":  3.7},
    {"asset_class": "International", "category": "Europe Funds",          "pct":  3.0},
    {"asset_class": "International", "category": "Asian Funds",           "pct":  3.0},
    {"asset_class": "International", "category": "Taiwan Funds",          "pct":  1.3},
    # ── Commodities (15%) ─────────────────────────────────────────────────────
    {"asset_class": "Commodities",   "category": "Gold",                  "pct":  7.5},
    {"asset_class": "Commodities",   "category": "Silver",                "pct":  7.5},
]
