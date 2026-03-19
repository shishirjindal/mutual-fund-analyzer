# -*- coding: utf-8 -*-

"""
Constants for fetching benchmark TRI data from niftyindices.com.
"""

BENCHMARK_DEFAULT_INDEX = "NIFTY 50"

# Per-category benchmark index names (keys match CATEGORY_KEYWORDS in amfi_constants.py)
CATEGORY_BENCHMARK_MAP = {
    # ── Equity ────────────────────────────────────────────────────────────────
    "Large Cap":              "NIFTY 100",
    "Large & Mid Cap":        "NIFTY LARGEMIDCAP 250",
    "Mid Cap":                "NIFTY MIDCAP 150",
    "Small Cap":              "NIFTY SMALLCAP 250",
    "Mid & Small Cap":        "NIFTY MIDSMALLCAP 400",
    "Flexi Cap":              "NIFTY 500",
    "Multi Cap":              "NIFTY500 MULTICAP 50:25:25",
    "ELSS":                   "NIFTY 500",
    "Focused Fund":           "NIFTY 500",
    "Dividend Yield":         "NIFTY DIVIDEND OPPORTUNITIES 50",
    "Value Fund":             "NIFTY500 VALUE 50",
    "Contra Fund":            "NIFTY 500",

    # ── Debt ──────────────────────────────────────────────────────────────────
    "Banking & PSU":          "NIFTY PSU BANK",

    # ── Hybrid ────────────────────────────────────────────────────────────────
    "Aggressive Hybrid":      "NIFTY 500",
    "Multi Asset Allocation": "NIFTY 500",
    "Arbitrage Fund":         "NIFTY 50 ARBITRAGE",
}

# Per-sector benchmark index names (keys match AmfiFetcher.SECTOR_KEYWORDS)
SECTOR_BENCHMARK_MAP = {
    "Banking & Financial":  "NIFTY BANK",
    "IT & Technology":      "NIFTY IT",
    "Pharma & Healthcare":  "NIFTY PHARMA",
    "Infrastructure":       "NIFTY INFRASTRUCTURE",
    "Energy":               "NIFTY ENERGY",
    "Manufacturing":        "NIFTY INDIA MANUFACTURING",
    "Consumption":          "NIFTY INDIA CONSUMPTION",
    "PSU":                  "NIFTY PSE",
    "MNC":                  "NIFTY MNC",
    "ESG":                  "NIFTY100 ESG",
    "Real Estate":          "NIFTY REALTY",
    "Commodities":          "NIFTY COMMODITIES",
    "Transportation":       "NIFTY TRANSPORTATION & LOGISTICS",
    "Business Cycle":       "NIFTY 500",
    "Quant":                "NIFTY 500",
    "Special Opportunities":"NIFTY 500",
}

BENCHMARK_TRI_URL = "https://www.niftyindices.com/Backpage.aspx/getTotalReturnIndexString"

BENCHMARK_TRI_HEADERS = {
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

BENCHMARK_TRI_START_DATE = "01-Jan-2000"

BENCHMARK_CACHE_DIR = ".cache/benchmark"
BENCHMARK_CACHE_TTL_DAYS = 7
