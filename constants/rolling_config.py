# -*- coding: utf-8 -*-
"""Window/data-range configuration for rolling calculators."""

_STANDARD_MAP = [
    {'rolling_window': 1, 'total_data': 5},
    {'rolling_window': 3, 'total_data': 10},
    {'rolling_window': 5, 'total_data': 15},
]


class RollingConfig:
    ROLLING_STANDARD_DEVIATION_MAP = _STANDARD_MAP
    ROLLING_SHARPE_RATIO_MAP = _STANDARD_MAP
    ROLLING_SORTINO_RATIO_MAP = _STANDARD_MAP
    ROLLING_ALPHA_MAP = _STANDARD_MAP
    ROLLING_BETA_MAP = _STANDARD_MAP
    ROLLING_INFORMATION_RATIO_MAP = _STANDARD_MAP
    ROLLING_HIT_RATIO_MAP = _STANDARD_MAP
    ROLLING_DRAWDOWN_MAP = _STANDARD_MAP
