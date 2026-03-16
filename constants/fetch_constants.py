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
