# -*- coding: utf-8 -*-

"""
Constants for HTTP fetch utilities.
"""

from typing import Tuple

# Keywords that indicate a rate-limit / quota-exceeded response
QUOTA_SIGNALS: Tuple[str, ...] = (
    "quota exceeded",
    "rate limit",
    "too many requests",
    "throttled",
    "throttling",
)

# NAV disk cache configuration
NAV_CACHE_DIR = ".cache/nav"
NAV_CACHE_TTL_DAYS = 7

# Benchmark TRI disk cache configuration
BENCHMARK_CACHE_DIR = ".cache/benchmark"
BENCHMARK_CACHE_TTL_DAYS = 7

# ETF metadata cache (expense ratio, AUM) — updated monthly
ETF_METADATA_CACHE_PATH = ".cache/etf_metadata.json"
ETF_METADATA_CACHE_TTL_DAYS = 30
