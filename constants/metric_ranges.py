# -*- coding: utf-8 -*-
"""
Quality band thresholds for each metric.

Each entry: metric_id -> (lower_is_better, [threshold_excellent, threshold_good, threshold_average])
  higher-is-better: value >= excellent → Excellent, >= good → Good, >= average → Average, else Weak
  lower-is-better:  value <= excellent → Excellent, <= good → Good, <= average → Average, else Weak
"""

from typing import Dict, Tuple, List

MetricRange = Tuple[bool, List[float]]

METRIC_RANGES: Dict[str, MetricRange] = {
    # ── Return Performance ────────────────────────────────────────────────────
    'static_5y_cagr':        (False, [14,  11,  9  ]),
    'static_3y_cagr':        (False, [13,  10,  8  ]),
    'static_1y_return':      (False, [15,  8,   4  ]),
    'calendar_avg':          (False, [12,  9,   7  ]),
    'worst_calendar_year':   (False, [-15, -20, -25]),  # higher (less negative) is better

    # ── Risk ──────────────────────────────────────────────────────────────────
    'static_mdd_5y_value':          (False, [-25, -30, -35]),  # less negative = better
    'static_mdd_5y_duration':       (True,  [10,  16,  24 ]),  # months, lower = better
    'static_std_dev_5y':            (True,  [14,  16,  18 ]),
    'static_std_dev_3y':            (True,  [15,  18,  20 ]),
    'static_ulcer_5y':              (True,  [6,   8,   10 ]),
    'rolling_mdd_3y_median':        (False, [-18, -25, -30]),
    'rolling_mdd_3y_percentile_75': (False, [-22, -28, -35]),
    'rolling_mdd_3y_worst':         (False, [-35, -45, -55]),

    # ── Risk-Adjusted Performance ─────────────────────────────────────────────
    'static_sharpe_5y':  (False, [1.3, 1.0, 0.7]),
    'static_sharpe_3y':  (False, [1.2, 0.9, 0.6]),
    'static_sortino_5y': (False, [2.2, 1.5, 1.0]),
    'static_sortino_3y': (False, [2.0, 1.4, 0.9]),
    'static_calmar_5y':  (False, [0.9, 0.6, 0.4]),
    'static_calmar_3y':  (False, [0.8, 0.5, 0.3]),
    'static_treynor_5y': (False, [12,  8,   5  ]),
    'static_treynor_3y': (False, [10,  7,   4  ]),

    # ── Manager Skill vs Benchmark ────────────────────────────────────────────
    'static_alpha_5y':           (False, [3,    1,    0   ]),
    'static_alpha_3y':           (False, [2.5,  0.8,  0   ]),
    'static_ir_5y':              (False, [0.7,  0.4,  0.2 ]),
    'static_ir_3y':              (False, [0.6,  0.3,  0.1 ]),
    'static_hit_ratio_5y':       (False, [65,   55,   50  ]),
    'static_hit_ratio_3y':       (False, [65,   55,   50  ]),
    'rolling_alpha_3y_median':   (False, [2,    1,    0   ]),
    'rolling_alpha_3y_positive': (False, [65,   55,   50  ]),
    'rolling_alpha_3y_std':      (True,  [1.5,  2.5,  3.5 ]),
    'rolling_ir_3y_median':      (False, [0.6,  0.3,  0.1 ]),
    'rolling_ir_3y_positive':    (False, [65,   55,   50  ]),
    'rolling_ir_3y_std':         (True,  [0.35, 0.55, 0.75]),

    # ── Consistency (Rolling) ─────────────────────────────────────────────────
    'rolling_5y_median':               (False, [13,  11,  9  ]),
    'rolling_5y_percentile_25':        (False, [7,   5,   3  ]),
    'rolling_5y_std_dev':              (True,  [3,   5,   7  ]),
    'rolling_3y_median':               (False, [12,  10,  8  ]),
    'rolling_3y_percentile_25':        (False, [6,   4,   2  ]),
    'rolling_3y_std_dev':              (True,  [4,   6,   8  ]),
    'rolling_sharpe_5y_median':        (False, [1.2, 0.9, 0.6]),
    'rolling_sharpe_5y_percentile_25': (False, [0.9, 0.6, 0.4]),
    'rolling_sharpe_5y_std_dev':       (True,  [0.35,0.55,0.75]),
    'rolling_sharpe_3y_median':        (False, [1.1, 0.8, 0.5]),
    'rolling_sharpe_3y_percentile_25': (False, [0.8, 0.5, 0.3]),
    'rolling_sharpe_3y_std_dev':       (True,  [0.45,0.65,0.85]),
    'rolling_hit_ratio_5y_median':        (False, [65, 55, 50]),
    'rolling_hit_ratio_5y_percentile_25': (False, [60, 50, 45]),
    'rolling_hit_ratio_3y_median':        (False, [65, 55, 50]),
    'rolling_hit_ratio_3y_percentile_25': (False, [60, 50, 45]),
}
