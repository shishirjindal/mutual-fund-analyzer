# -*- coding: utf-8 -*-
"""ETF tracker constants — tickers and benchmark mappings."""

from typing import Dict, List

# Benchmark tickers (Yahoo Finance)
# Using spot ETF proxies (GLD/SLV) instead of futures (GC=F/SI=F)
# to avoid futures roll effects on returns.
GOLD_BENCHMARK_TICKER   = "GLD"        # SPDR Gold Shares — tracks spot gold in USD
SILVER_BENCHMARK_TICKER = "SLV"        # iShares Silver Trust — tracks spot silver in USD
USD_INR_TICKER          = "USDINR=X"   # USD/INR exchange rate

# Gold ETFs: display name → Yahoo Finance ticker
GOLD_ETF_TICKERS: Dict[str, str] = {
    "Nippon India Gold BeES":       "GOLDBEES.NS",
    "SBI Gold ETF":                 "SETFGOLD.NS",
    "HDFC Gold ETF":                "HDFCGOLD.NS",
    "Axis Gold ETF":                "AXISGOLD.NS",
    "Invesco India Gold ETF":       "IVZINGOLD.NS",
    "LIC Gold ETF":                 "LICMFGOLD.NS",
}

# Silver ETFs: display name → Yahoo Finance ticker
SILVER_ETF_TICKERS: Dict[str, str] = {
    "Nippon India Silver ETF":      "SILVERBEES.NS",
    "HDFC Silver ETF":              "HDFCSILVER.NS",
    "Axis Silver ETF":              "AXISILVER.NS",
}

# Expense ratios (% p.a.) — sourced from AMC websites / NSE ETF page
# Update periodically as AMCs revise TER
EXPENSE_RATIOS: Dict[str, float] = {
    # Gold ETFs
    "GOLDBEES.NS":  0.82,
    "SETFGOLD.NS":  0.20,
    "HDFCGOLD.NS":  0.59,
    "AXISGOLD.NS":  0.49,
    "IVZINGOLD.NS": 0.55,
    "LICMFGOLD.NS": 0.49,
    # Silver ETFs
    "SILVERBEES.NS": 0.40,
    "HDFCSILVER.NS": 0.35,
    "AXISILVER.NS":  0.40,
}

# AUM in INR crores — sourced from NSE ETF page / AMC factsheets
# Update periodically
AUM_CRORES: Dict[str, float] = {
    # Gold ETFs
    "GOLDBEES.NS":  9800.0,
    "SETFGOLD.NS":  2800.0,
    "HDFCGOLD.NS":  3200.0,
    "AXISGOLD.NS":   950.0,
    "IVZINGOLD.NS":  180.0,
    "LICMFGOLD.NS":  120.0,
    # Silver ETFs
    "SILVERBEES.NS": 2100.0,
    "HDFCSILVER.NS":  850.0,
    "AXISILVER.NS":   420.0,
}

# Periods available for analysis
ETF_PERIODS: List[str] = ["6mo", "1y", "3y", "5y"]
