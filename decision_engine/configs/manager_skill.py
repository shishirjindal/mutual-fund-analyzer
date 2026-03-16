# -*- coding: utf-8 -*-
"""Metric configs for Manager Skill vs Benchmark category."""

MANAGER_SKILL_VS_BENCHMARK = [
    # Alpha Generation (Total Weight 45%)
    {'id': 'static_alpha_5y',           'name': 'Alpha (5Y)',                'weight': 0.25,  'steepness':  2.2},
    {'id': 'static_alpha_3y',           'name': 'Alpha (3Y)',                'weight': 0.20,  'steepness':  2.0},
    # Risk Efficiency (Total Weight 27%)
    {'id': 'static_ir_5y',              'name': 'Info Ratio (5Y)',           'weight': 0.15,  'steepness':  2.7},
    {'id': 'static_ir_3y',              'name': 'Info Ratio (3Y)',           'weight': 0.12,  'steepness':  2.5},
    # Outperformance Frequency (Total Weight 13%)
    {'id': 'static_hit_ratio_5y',       'name': 'Hit Ratio (5Y)',            'weight': 0.08,  'steepness':  1.8},
    {'id': 'static_hit_ratio_3y',       'name': 'Hit Ratio (3Y)',            'weight': 0.05,  'steepness':  1.6},
    # Rolling IR Consistency (Total Weight 8%): Median 40%, % Positive 40%, Std Dev 20%
    {'id': 'rolling_ir_3y_median',      'name': 'Rolling IR (3Y Median)',    'weight': 0.032, 'steepness':  2.6},
    {'id': 'rolling_ir_3y_positive',    'name': 'Rolling IR (3Y % > 0)',     'weight': 0.032, 'steepness':  2.4},
    {'id': 'rolling_ir_3y_std',         'name': 'Rolling IR (3Y Std Dev)',   'weight': 0.016, 'steepness': -2.2},
    # Rolling Alpha Consistency (Total Weight 7%): Median 40%, % Positive 40%, Std Dev 20%
    {'id': 'rolling_alpha_3y_median',   'name': 'Rolling Alpha (3Y Median)', 'weight': 0.028, 'steepness':  2.2},
    {'id': 'rolling_alpha_3y_positive', 'name': 'Rolling Alpha (3Y % > 0)',  'weight': 0.028, 'steepness':  2.0},
    {'id': 'rolling_alpha_3y_std',      'name': 'Rolling Alpha (3Y Std Dev)','weight': 0.014, 'steepness': -2.0},
]
