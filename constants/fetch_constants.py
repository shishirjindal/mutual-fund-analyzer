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
