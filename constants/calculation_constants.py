# -*- coding: utf-8 -*-
"""Core calculation constants — trading days, rates, formats."""


class CalculationConstants:
    TRADING_DAYS_PER_YEAR = 252
    DECIMAL_PLACES = 2
    DATE_FORMAT = "%d-%m-%Y"
    RISK_FREE_RATE = 0.065
    NUM_CALENDAR_YEARS = 5
    ROLLING_YEARS = [1, 3, 5]

    # Date patterns for NAV lookup at year boundaries
    JANUARY_DATE_DAYS = [1, 2, 3, 4]
    JANUARY_MONTH = 1
