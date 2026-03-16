# -*- coding: utf-8 -*-

"""
Constants for fetching benchmark TRI data from niftyindices.com.
"""

BENCHMARK_DEFAULT_INDEX = "NIFTY 50"

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
