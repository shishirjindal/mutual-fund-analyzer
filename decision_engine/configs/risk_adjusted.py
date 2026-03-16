# -*- coding: utf-8 -*-
"""Metric configs for Risk-Adjusted Performance category."""

RISK_ADJUSTED_PERFORMANCE = [
    # Sharpe Ratio (Total Weight 35%): 60/40 split 5Y/3Y
    {'id': 'static_sharpe_5y',  'name': 'Sharpe Ratio (5Y)',  'weight': 0.21, 'steepness': 2.6},
    {'id': 'static_sharpe_3y',  'name': 'Sharpe Ratio (3Y)',  'weight': 0.14, 'steepness': 2.4},
    # Sortino Ratio (Total Weight 30%): 60/40 split 5Y/3Y
    {'id': 'static_sortino_5y', 'name': 'Sortino Ratio (5Y)', 'weight': 0.18, 'steepness': 2.7},
    {'id': 'static_sortino_3y', 'name': 'Sortino Ratio (3Y)', 'weight': 0.12, 'steepness': 2.5},
    # Calmar Ratio (Total Weight 25%): 60/40 split 5Y/3Y
    {'id': 'static_calmar_5y',  'name': 'Calmar Ratio (5Y)',  'weight': 0.15, 'steepness': 2.6},
    {'id': 'static_calmar_3y',  'name': 'Calmar Ratio (3Y)',  'weight': 0.10, 'steepness': 2.4},
    # Treynor Ratio (Total Weight 10%): 60/40 split 5Y/3Y
    {'id': 'static_treynor_5y', 'name': 'Treynor Ratio (5Y)', 'weight': 0.06, 'steepness': 2.0},
    {'id': 'static_treynor_3y', 'name': 'Treynor Ratio (3Y)', 'weight': 0.04, 'steepness': 1.8},
]
