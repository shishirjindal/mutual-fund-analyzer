# -*- coding: utf-8 -*-
"""Metric configs for Consistency (Rolling) category."""

CONSISTENCY_ROLLING = [
    # Rolling Returns (Total Weight 50%): 5Y 30%, 3Y 20%
    {'id': 'rolling_5y_median',              'name': 'Rolling Returns (5Y Median)',   'weight': 0.15,  'steepness':  2.0},
    {'id': 'rolling_5y_percentile_25',       'name': 'Rolling Returns (5Y 25th%)',    'weight': 0.09,  'steepness':  2.1},
    {'id': 'rolling_5y_std_dev',             'name': 'Rolling Returns (5Y Std Dev)',  'weight': 0.06,  'steepness': -2.0},
    {'id': 'rolling_3y_median',              'name': 'Rolling Returns (3Y Median)',   'weight': 0.10,  'steepness':  1.9},
    {'id': 'rolling_3y_percentile_25',       'name': 'Rolling Returns (3Y 25th%)',    'weight': 0.06,  'steepness':  2.0},
    {'id': 'rolling_3y_std_dev',             'name': 'Rolling Returns (3Y Std Dev)',  'weight': 0.04,  'steepness': -1.9},
    # Rolling Sharpe (Total Weight 30%): 5Y 18%, 3Y 12%
    {'id': 'rolling_sharpe_5y_median',       'name': 'Rolling Sharpe (5Y Median)',    'weight': 0.09,  'steepness':  2.5},
    {'id': 'rolling_sharpe_5y_percentile_25','name': 'Rolling Sharpe (5Y 25th%)',     'weight': 0.054, 'steepness':  2.6},
    {'id': 'rolling_sharpe_5y_std_dev',      'name': 'Rolling Sharpe (5Y Std Dev)',   'weight': 0.036, 'steepness': -2.3},
    {'id': 'rolling_sharpe_3y_median',       'name': 'Rolling Sharpe (3Y Median)',    'weight': 0.06,  'steepness':  2.4},
    {'id': 'rolling_sharpe_3y_percentile_25','name': 'Rolling Sharpe (3Y 25th%)',     'weight': 0.036, 'steepness':  2.5},
    {'id': 'rolling_sharpe_3y_std_dev',      'name': 'Rolling Sharpe (3Y Std Dev)',   'weight': 0.024, 'steepness': -2.2},
    # Rolling Hit Ratio (Total Weight 20%): 5Y 12%, 3Y 8%
    {'id': 'rolling_hit_ratio_5y_median',        'name': 'Rolling Hit Ratio (5Y Median)', 'weight': 0.072, 'steepness': 1.7},
    {'id': 'rolling_hit_ratio_5y_percentile_25', 'name': 'Rolling Hit Ratio (5Y 25th%)',  'weight': 0.048, 'steepness': 1.8},
    {'id': 'rolling_hit_ratio_3y_median',        'name': 'Rolling Hit Ratio (3Y Median)', 'weight': 0.048, 'steepness': 1.6},
    {'id': 'rolling_hit_ratio_3y_percentile_25', 'name': 'Rolling Hit Ratio (3Y 25th%)',  'weight': 0.032, 'steepness': 1.7},
]
