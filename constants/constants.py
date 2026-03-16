# -*- coding: utf-8 -*-
"""
Unified Constants class — re-exports from calculation_constants, static_config, rolling_config.
All existing callers use `from constants.constants import Constants` unchanged.
"""

from constants.calculation_constants import CalculationConstants
from constants.static_config import StaticConfig
from constants.rolling_config import RollingConfig


class Constants(CalculationConstants, StaticConfig, RollingConfig):
    """Single access point for all configuration constants."""
