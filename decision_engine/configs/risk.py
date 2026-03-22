# -*- coding: utf-8 -*-
"""Metric configs for Risk category."""

RISK = [
    # Static MDD 5Y (Total Weight 35%): Max DD 70%, Duration 30%
    {'id': 'static_mdd_5y_value',          'name': 'Max Drawdown (5Y)',  'weight': 0.245, 'steepness': -2.3, 'is_rolling': False},
    {'id': 'static_mdd_5y_duration',       'name': 'MDD Duration (5Y)',  'weight': 0.105, 'steepness': -1.7, 'is_rolling': False},
    # Annualized Volatility (Total Weight 40%): 60/40 split 5Y/3Y
    {'id': 'static_std_dev_5y',            'name': 'Std Dev (5Y)',       'weight': 0.25,  'steepness': -2.1, 'is_rolling': False},
    {'id': 'static_std_dev_3y',            'name': 'Std Dev (3Y)',       'weight': 0.15,  'steepness': -2.0, 'is_rolling': False},
    # Downside Risk (Total Weight 18%)
    {'id': 'static_ulcer_5y',              'name': 'Ulcer Index',        'weight': 0.18,  'steepness': -2.2, 'is_rolling': False},
    # Rolling MDD 3Y (Total Weight 7%): Median 50%, 75th%ile 30%, Worst 20%
    {'id': 'rolling_mdd_3y_median',        'name': 'Rolling Median DD',  'weight': 0.035, 'steepness': -2.2, 'is_rolling': True, 'rolling_window': 3},
    {'id': 'rolling_mdd_3y_percentile_75', 'name': 'Rolling 75%ile DD',  'weight': 0.021, 'steepness': -2.3, 'is_rolling': True, 'rolling_window': 3},
    {'id': 'rolling_mdd_3y_worst',         'name': 'Rolling Worst DD',   'weight': 0.014, 'steepness': -2.4, 'is_rolling': True, 'rolling_window': 3},
]
