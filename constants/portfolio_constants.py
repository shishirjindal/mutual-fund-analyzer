# -*- coding: utf-8 -*-
"""
Personal portfolio holdings.
Update amounts here whenever you invest/redeem.
"""

from typing import List, Dict

PORTFOLIO: List[Dict] = [
    # ── Equity — Core ─────────────────────────────────────────────────────────
    {"asset_class": "Equity",        "category": "Large Cap",             "amount": 20000},
    {"asset_class": "Equity",        "category": "Mid Cap",               "amount": 20000},
    {"asset_class": "Equity",        "category": "Small Cap",             "amount": 10000},
    {"asset_class": "Equity",        "category": "Flexi Cap",             "amount": 20000},
    {"asset_class": "Equity",        "category": "Value Fund",            "amount":  5000},
    {"asset_class": "Equity",        "category": "Contra Fund",           "amount":  5000},
    # ── Equity — Sectoral ─────────────────────────────────────────────────────
    {"asset_class": "Sectoral",      "category": "Technology",            "amount":  3000},
    {"asset_class": "Sectoral",      "category": "Banking & Financial",   "amount":  4000},
    {"asset_class": "Sectoral",      "category": "Healthcare",            "amount":  4000},
    {"asset_class": "Sectoral",      "category": "Energy",                "amount":  3000},
    {"asset_class": "Sectoral",      "category": "Infrastructure",        "amount":  3000},
    {"asset_class": "Sectoral",      "category": "Consumption",           "amount":  3000},
    # ── International ─────────────────────────────────────────────────────────
    {"asset_class": "International", "category": "International Fund",    "amount": 15000},
    # ── Commodities ───────────────────────────────────────────────────────────
    {"asset_class": "Commodities",   "category": "Gold",                  "amount": 10000},
    {"asset_class": "Commodities",   "category": "Silver",                "amount": 10000},
]
