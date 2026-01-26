# -*- coding: utf-8 -*-

"""
Constants for Mutual Fund Returns Calculator

This module contains all constants used for mutual fund returns calculations.
"""


class Constants:
    """Constants used for mutual fund returns calculations."""
    
    # Trading and calculation constants
    TRADING_DAYS_PER_YEAR = 252
    DECIMAL_PLACES = 2
    
    # Rolling returns configuration
    ROLLING_YEARS = [1, 3, 5]
    
    # Calendar year returns configuration
    NUM_CALENDAR_YEARS = 5
    
    # Date patterns for NAV lookup
    # Days to check for NAV at the start of a year (for both initial and final NAV)
    JANUARY_DATE_DAYS = [1, 2, 3, 4]  # January 1st, 2nd, 3rd, 4th
    JANUARY_MONTH = 1  # January
