# -*- coding: utf-8 -*-

"""
AMFI-related constants for fetching and classifying mutual fund schemes.

Categories follow SEBI's official classification (Oct 2017 circular, updated 2026).
Order within the dict does not matter — _classify_category sorts by keyword length
so more specific patterns always win over shorter overlapping ones.
"""

from typing import Dict, List

AMFI_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"

CATEGORY_KEYWORDS: Dict[str, List[str]] = {

    # ── Equity ────────────────────────────────────────────────────────────────
    "Large Cap":          ["large cap"],
    "Mid Cap":            ["mid cap"],
    "Small Cap":          ["small cap"],
    "Large & Mid Cap":    ["large & mid cap", "large and mid cap", "large mid cap"],
    "Mid & Small Cap":    ["mid & small cap", "mid and small cap", "mid small cap"],
    "Multi Cap":          ["multi cap", "multicap"],
    "Flexi Cap":          ["flexi cap", "flexicap", "flexible cap"],
    "Focused Fund":       ["focused fund", "focused equity"],
    "Value Fund":         ["value fund"],
    "Contra Fund":        ["contra fund", "contra "],
    "Dividend Yield":     ["dividend yield"],
    "ELSS":               ["elss", "tax saver", "tax saving", "linked savings"],
    "Sectoral / Thematic":["sectoral", "thematic", "infrastructure", "banking and financial",
                           "technology", "pharma", "healthcare", "consumption", "energy",
                           "manufacturing", "psu", "mnc", "esg", "business cycle",
                           "special opportunities", "innovation", "transportation",
                           "real estate", "commodities", "quant"],

    # ── Debt ──────────────────────────────────────────────────────────────────
    "Overnight Fund":           ["overnight fund"],
    "Liquid Fund":              ["liquid fund"],
    "Ultra Short Duration":     ["ultra short duration", "ultra short term", "ultra short bond"],
    "Low Duration":             ["low duration"],
    "Money Market":             ["money market"],
    "Short Duration":           ["short duration", "short term bond", "short term debt"],
    "Medium Duration":          ["medium duration"],
    "Medium to Long Duration":  ["medium to long duration", "medium long duration"],
    "Long Duration":            ["long duration"],
    "Dynamic Bond":             ["dynamic bond"],
    "Corporate Bond":           ["corporate bond"],
    "Credit Risk":              ["credit risk"],
    "Banking & PSU":            ["banking & psu", "banking and psu", "bank & psu"],
    "Gilt":                     ["gilt fund", "government securities fund", "gsec fund"],
    "Gilt 10Y Constant":        ["10 year gilt", "10yr gilt", "constant maturity gilt",
                                 "constant duration gilt"],
    "Floater":                  ["floater fund", "floating rate fund"],

    # ── Hybrid ────────────────────────────────────────────────────────────────
    "Conservative Hybrid":      ["conservative hybrid"],
    "Balanced Hybrid":          ["balanced hybrid"],
    "Aggressive Hybrid":        ["aggressive hybrid"],
    "Multi Asset Allocation":   ["multi asset allocation", "multi asset fund"],
    "Arbitrage Fund":           ["arbitrage fund"],
    "Equity Savings":           ["equity savings"],

    # ── Index / Passive ───────────────────────────────────────────────────────
    "Index Fund":               ["index fund", "nifty 50 fund", "sensex fund"],
    "Fund of Funds":            ["fund of fund", "fof "],
    "ETF":                      ["etf"],

    # ── Life Cycle / Retirement ───────────────────────────────────────────────
    "Retirement Fund":          ["retirement fund", "pension fund"],
    "Children's Fund":          ["children", "child benefit", "child care"],
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

# Broad fund groups mapping to their SEBI sub-categories
FUND_GROUPS: Dict[str, List[str]] = {
    "Equity": [
        "Large Cap", "Mid Cap", "Small Cap", "Large & Mid Cap", "Mid & Small Cap",
        "Multi Cap", "Flexi Cap", "Focused Fund", "Value Fund", "Contra Fund",
        "Dividend Yield", "ELSS", "Sectoral / Thematic",
    ],
    "Debt": [
        "Overnight Fund", "Liquid Fund", "Ultra Short Duration", "Low Duration",
        "Money Market", "Short Duration", "Medium Duration", "Medium to Long Duration",
        "Long Duration", "Dynamic Bond", "Corporate Bond", "Credit Risk",
        "Banking & PSU", "Gilt", "Gilt 10Y Constant", "Floater",
    ],
    "Hybrid": [
        "Conservative Hybrid", "Balanced Hybrid", "Aggressive Hybrid",
        "Multi Asset Allocation", "Arbitrage Fund", "Equity Savings",
    ],
    "Index / Passive": [
        "Index Fund", "ETF",
    ],
    "Fund of Funds": [
        "Fund of Funds",
    ],
    "Retirement & Children": [
        "Retirement Fund", "Children's Fund",
    ],
}
