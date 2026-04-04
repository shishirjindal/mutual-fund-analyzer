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
    "Large Cap":          ["large cap", "largecap"],
    "Mid Cap":            ["mid cap", "midcap"],
    "Small Cap":          ["small cap", "smallcap"],
    "Large & Mid Cap":    ["large & mid cap", "large and mid cap", "large mid cap",
                           "large & midcap", "large and midcap"],
    "Mid & Small Cap":    ["mid & small cap", "mid and small cap", "mid small cap",
                           "mid & smallcap", "midsmallcap"],
    "Multi Cap":          ["multi cap", "multicap", "multi-cap"],
    "Flexi Cap":          ["flexi cap", "flexicap", "flexible cap"],
    "Focused Fund":       ["focused fund", "focused equity"],
    "Value Fund":         ["value fund"],
    "Contra Fund":        ["contra fund", "contra "],
    "Dividend Yield":     ["dividend yield fund", "dividend yield equity"],
    "ELSS":               ["elss", "tax saver", "tax saving", "linked savings"],
    "Sectoral / Thematic":["sectoral", "thematic", "infrastructure", "banking and financial",
                           "technology", "pharma", "healthcare", "consumption", "energy",
                           "manufacturing", "psu equity", "psu fund", "mnc", "esg",
                           "business cycle", "special opportunities", "innovation",
                           "transportation", "real estate", "commodities",
                           "quant fund", "momentum fund", "quality fund", "quality equity",
                           "minimum variance", "multi-factor", "multifactor",
                           "financial services fund", "banking & financial services",
                           "banking and financial services",
                           "fmcg fund", "digital india", "digital bharat",
                           "housing opportunities", "rural opportunities",
                           "services fund", "services opportunities",
                           "conglomerate", "ethical fund", "teck fund",
                           "bfsi fund", "quantamental", "sector rotation",
                           "india consumer", "consumer trends", "great consumer",
                           "commodity equities", "comma fund",
                           "automotive", "defence fund",
                           "international equity", "global agri",
                           "asian equity", "japan equity", "taiwan equity",
                           "us equity", "us bluechip", "nasdaq",
                           "emerging market", "global emerging",
                           "europe", "brazil fund", "greater china",
                           "build india", "opportunities fund",
                           "active momentum", "export", "ipo fund",
                           "innovative opportunities", "best-in-class",
                           "health and wellness", "power & infra", "power and infra",
                           "tiger fund", "t.i.g.e.r",
                           "manufacture in india", "pioneer fund",
                           "offshore fund", "off-shore fund",
                           "asean equity", "us value equity"],

    # ── Debt ──────────────────────────────────────────────────────────────────
    "Overnight Fund":           ["overnight fund"],
    "Liquid Fund":              ["liquid fund", "liquidity fund", "liquid cash",
                                 "mmf", "money manager fund"],
    "Ultra Short Duration":     ["ultra short duration", "ultra short term",
                                 "ultra short bond", "ultra short fund"],
    "Low Duration":             ["low duration"],
    "Money Market":             ["money market", "savings fund", "treasury advantage"],
    "Short Duration":           ["short duration", "short term bond", "short term debt",
                                 "short term fund", "short term income", "short  term",
                                 "hdfc short term"],
    "Medium Duration":          ["medium duration", "medium term"],
    "Medium to Long Duration":  ["medium to long duration", "medium long duration"],
    "Long Duration":            ["long duration", "long term bond", "long term advantage"],
    "Dynamic Bond":             ["dynamic bond", "dynamic accrual", "dynamic debt",
                                 "all seasons bond", "strategic bond"],
    "Corporate Bond":           ["corporate bond", "corporate debt", "bond fund",
                                 "bond short term"],
    "Credit Risk":              ["credit risk"],
    "Banking & PSU":            ["banking & psu", "banking and psu", "bank & psu"],
    "Gilt":                     ["gilt fund", "gilt-investment", "gilt securities",
                                 "gilt  fund", "nippon india gilt",
                                 "government securities fund", "gsec fund",
                                 "g-sec fund", "crisil-ibx gilt", "crisil ibx gilt",
                                 "ibx gilt", "ibx sdl", "gilt plus sdl"],
    "Gilt 10Y Constant":        ["constant maturity gilt fund", "constant maturity gilt",
                                 "constant duration gilt", "10 year gilt", "10yr gilt"],
    "Floater":                  ["floater fund", "floating rate fund", "floating rate debt",
                                 "floating interest"],
    "Income Fund":              ["income fund", "income opportunities", "income plan"],

    # ── Hybrid ────────────────────────────────────────────────────────────────
    "Conservative Hybrid":      ["conservative hybrid", "mip", "hybrid debt",
                                 "debt hybrid"],
    "Balanced Hybrid":          ["balanced hybrid", "equity hybrid", "equity & debt",
                                 "equity and debt", "hybrid equity", "blended plan",
                                 "equity hybrid'95"],
    "Aggressive Hybrid":        ["aggressive hybrid"],
    "Balanced Advantage":       ["balanced advantage", "dynamic asset allocation"],
    "Multi Asset Allocation":   ["multi asset allocation", "multi asset fund",
                                 "multi-asset fund", "multi asset omni",
                                 "multi-asset passive"],
    "Arbitrage Fund":           ["arbitrage fund"],
    "Equity Savings":           ["equity savings fund", "equity savings"],

    # ── Index / Passive ───────────────────────────────────────────────────────
    "Index Fund":               ["index fund", "nifty 50 fund", "sensex fund",
                                 "crisil-ibx aaa", "crisil ibx aaa", "ibx aaa",
                                 "bse india sector"],
    "Fund of Funds":            ["fund of fund", "fof ", "asset allocation fof",
                                 "passive fof", "omni fof", "gold fund",
                                 "global advantage fund", "global stable equity",
                                 "bharat bond fof", "us specific equity passive",
                                 "income plus arbitrage active fof",
                                 "income plus arbitrage active"],
    "ETF":                      ["etf"],

    # ── Life Cycle / Retirement ───────────────────────────────────────────────
    "Retirement Fund":          ["retirement fund", "pension fund", "retirement benefit",
                                 "bal bhavishya"],
    "Children's Fund":          ["children", "child benefit", "child care"],
}

# Keywords that must appear in the fund name to qualify as a Direct Plan
DIRECT_KEYWORDS: List[str] = ["direct"]

# Keywords that must appear in the fund name to qualify as Growth oriented
GROWTH_KEYWORDS: List[str] = ["growth", "cumulative"]

# Keywords that disqualify a fund (IDCW, dividend payout, bonus, etc.)
# Note: "dividend yield" is a legitimate SEBI equity category — only exclude
# payout/reinvestment variants, not the fund category itself.
EXCLUDE_KEYWORDS: List[str] = [
    "idcw", "bonus", "weekly", "monthly", "quarterly",
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
        "Banking & PSU", "Gilt", "Gilt 10Y Constant", "Floater", "Income Fund",
    ],
    "Hybrid": [
        "Conservative Hybrid", "Balanced Hybrid", "Aggressive Hybrid",
        "Balanced Advantage", "Multi Asset Allocation", "Arbitrage Fund", "Equity Savings",
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

# Sector keyword map for Sectoral / Thematic funds
SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "Banking & Financial":   ["banking", "financial", "bank & fin", "fintech", "bfsi"],
    "IT & Technology":       ["technology", "it fund", "digital", "innovation", "tech",
                              "teck", "nasdaq", "internet"],
    "Pharma & Healthcare":   ["pharma", "healthcare", "health care", "medic",
                              "health and wellness", "diagnostics"],
    "Infrastructure":        ["infrastructure", "infra", "build india", "tiger",
                              "t.i.g.e.r", "housing", "real estate", "realty"],
    "Energy":                ["energy", "power", "oil", "gas", "commodit"],
    "Manufacturing":         ["manufacturing", "industrial", "industry",
                              "manufacture in india", "comma fund", "automotive",
                              "auto ", "ev & new age", "defence", "mobility"],
    "Transportation":        ["transport", "logistics", "transportation"],
    "Consumption":           ["consumption", "consumer", "fmcg", "retail",
                              "services", "rural", "india opportunities",
                              "opportunities fund", "export", "mnc"],
    "PSU":                   ["psu", "public sector", "cpse"],
    "ESG":                   ["esg", "sustainability", "responsible", "ethical",
                              "best-in-class"],
    "Quant / Factor":        ["quant fund", "multi-factor", "multifactor",
                              "minimum variance", "momentum fund", "quality fund",
                              "quality equity", "quantamental", "active momentum",
                              "sector rotation", "innovative"],
    "International":         ["international equity", "global", "asian equity",
                              "japan equity", "taiwan equity", "us equity",
                              "us bluechip", "us value equity", "asean equity",
                              "emerging market", "europe", "brazil fund",
                              "greater china", "offshore fund", "off-shore fund",
                              "overseas", "world"],
    "Business Cycle":        ["business cycle", "conglomerate", "pioneer",
                              "ipo fund", "recently listed ipo"],
    "Special Opportunities": ["special opportunities", "special situation"],
}

# Sub-category keyword map for ETFs
ETF_KEYWORDS: Dict[str, List[str]] = {
    "Gold":   ["gold"],
    "Silver": ["silver"],
}
