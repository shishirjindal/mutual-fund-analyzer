# -*- coding: utf-8 -*-
"""
Metric color coding — maps metric values to quality-band colors.

Colors: #2ecc71 Excellent · #3498db Good · #f39c12 Average · #e74c3c Weak
Ranges are defined in constants/metric_ranges.py.
"""

from typing import Optional
from constants.metric_ranges import METRIC_RANGES

EXCELLENT = '#2ecc71'
GOOD      = '#3498db'
AVERAGE   = '#f39c12'
WEAK      = '#e74c3c'


def get_color(metric_id: str, value: Optional[float], fallback: str = GOOD) -> str:
    """Return a hex color for a metric value based on its quality band."""
    if value is None or metric_id not in METRIC_RANGES:
        return fallback

    lower_is_better, (t_exc, t_good, t_avg) = METRIC_RANGES[metric_id]

    if lower_is_better:
        if value <= t_exc:  return EXCELLENT
        if value <= t_good: return GOOD
        if value <= t_avg:  return AVERAGE
        return WEAK
    else:
        if value >= t_exc:  return EXCELLENT
        if value >= t_good: return GOOD
        if value >= t_avg:  return AVERAGE
        return WEAK


def get_colors(metric_id: str, values: list, fallback: str = GOOD) -> list:
    """Convenience wrapper — returns a color list for a list of values."""
    return [get_color(metric_id, v, fallback) for v in values]
