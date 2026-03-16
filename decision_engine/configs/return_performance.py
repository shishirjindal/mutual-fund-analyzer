# -*- coding: utf-8 -*-
"""Metric configs for Return Performance category."""

RETURN_PERFORMANCE = [
    # CAGR Performance (Total Weight 75%)
    {'id': 'static_5y_cagr',      'name': '5Y CAGR',             'weight': 0.45, 'steepness':  1.8},
    {'id': 'static_3y_cagr',      'name': '3Y CAGR',             'weight': 0.30, 'steepness':  1.7},
    # Short term & Calendar Performance (Total Weight 25%)
    {'id': 'static_1y_return',    'name': '1Y Return',           'weight': 0.10, 'steepness':  1.4},
    {'id': 'calendar_avg',        'name': 'Calendar Avg',        'weight': 0.07, 'steepness':  1.5},
    {'id': 'worst_calendar_year', 'name': 'Worst Calendar Year', 'weight': 0.08, 'steepness': -1.8},
]
