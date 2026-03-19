# -*- coding: utf-8 -*-
"""UI-level constants shared across tabs."""

# Chart quality-band colors
COLOR_EXCELLENT = '#2ecc71'
COLOR_GOOD      = '#3498db'
COLOR_AVERAGE   = '#f39c12'
COLOR_WEAK      = '#e74c3c'

# Shared chart defaults
NO_DATA_FIG_HEIGHT = 350
NO_DATA_ANNOTATION = dict(text="Data unavailable", showarrow=False, font_size=14)
BENCHMARK_NO_DATA_ANNOTATION = dict(text="Benchmark data unavailable", showarrow=False, font_size=14)

# Maps (data_key, year) → metric_id for risk-adjusted tab
RISK_ADJUSTED_METRIC_ID = {
    ('static_sharpe_data',        3): 'static_sharpe_3y',
    ('static_sharpe_data',        5): 'static_sharpe_5y',
    ('static_sortino_data',       3): 'static_sortino_3y',
    ('static_sortino_data',       5): 'static_sortino_5y',
    ('static_calmar_ratio_data',  3): 'static_calmar_3y',
    ('static_calmar_ratio_data',  5): 'static_calmar_5y',
    ('static_treynor_ratio_data', 3): 'static_treynor_3y',
    ('static_treynor_ratio_data', 5): 'static_treynor_5y',
}
