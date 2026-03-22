# -*- coding: utf-8 -*-
"""
Confidence multiplier calculation for the Decision Engine.

confidence_multiplier drives the penalty for insufficient data:
  final_score = raw_score * (0.7 + 0.3 * confidence_multiplier)

Three components:
  data_confidence    = available_weight_sum / total_weight_sum  (within category)
  time_confidence    = min(1.0, fund_age_years / 5)
  rolling_confidence = weighted avg of (actual_count / expected_count) per rolling metric

For pure-static categories:
  confidence = 0.6 * data_conf + 0.4 * time_conf

For pure-rolling categories:
  confidence = 0.5 * data_conf + 0.3 * time_conf + 0.2 * rolling_conf

For mixed categories:
  static_conf  = 0.6 * data_conf + 0.4 * time_conf
  rolling_conf_combined = weighted avg rolling confidence
  confidence = (static_weight * static_conf + rolling_weight * rolling_conf_combined)
               / (static_weight + rolling_weight)
"""

import datetime
from typing import Dict, Any, List, Optional

from constants.constants import Constants
from decision_engine.metric_extractor import extract_rolling_count


ROLLING_EXPECTED_POINTS = Constants.ROLLING_EXPECTED_POINTS


def _fund_age_years(metrics: Dict[str, Any]) -> float:
    """Compute fund age in years from launch_date in metrics."""
    launch = metrics.get('launch_date', 'N/A')
    if not launch or launch == 'N/A':
        return 0.0
    for fmt in ('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try:
            launch_dt = datetime.datetime.strptime(launch, fmt).date()
            return (datetime.date.today() - launch_dt).days / 365.25
        except ValueError:
            continue
    return 0.0


def _rolling_confidence_for_metric(
    metric_id: str,
    rolling_window: int,
    metrics: Dict[str, Any],
) -> Optional[float]:
    """Return rolling_confidence (0–1) for a single rolling metric."""
    count = extract_rolling_count(metric_id, rolling_window, metrics)
    if count is None:
        return None
    expected = ROLLING_EXPECTED_POINTS.get(rolling_window, 1200)
    return min(1.0, count / expected)


def compute_category_confidence(
    configs: List[Dict[str, Any]],
    available_mask: List[bool],
    metrics: Dict[str, Any],
) -> float:
    """
    Compute the confidence multiplier for one category.

    Args:
        configs:        List of metric config dicts (with 'weight', 'is_rolling', 'rolling_window').
        available_mask: Boolean list — True if the metric value was available.
        metrics:        Full fund metrics dict (for rolling counts and launch_date).

    Returns:
        confidence in [0, 1].
    """
    total_weight = sum(c['weight'] for c in configs)
    if total_weight == 0:
        return 0.0

    available_weight = sum(
        c['weight'] for c, avail in zip(configs, available_mask) if avail
    )
    data_conf = available_weight / total_weight

    age_years = _fund_age_years(metrics)
    time_conf = min(1.0, age_years / 5.0)

    # Split into static vs rolling — only count AVAILABLE metrics
    static_weight = sum(
        c['weight'] for c, avail in zip(configs, available_mask)
        if avail and not c.get('is_rolling', False)
    )
    rolling_weight = sum(
        c['weight'] for c, avail in zip(configs, available_mask)
        if avail and c.get('is_rolling', False)
    )
    rolling_configs_avail = [
        (c, avail) for c, avail in zip(configs, available_mask)
        if c.get('is_rolling', False)
    ]

    # Compute weighted rolling confidence
    rolling_conf_num = 0.0
    rolling_conf_den = 0.0
    for c, avail in rolling_configs_avail:
        if not avail:
            continue
        rc = _rolling_confidence_for_metric(
            c['id'], c.get('rolling_window', 3), metrics
        )
        if rc is not None:
            rolling_conf_num += c['weight'] * rc
            rolling_conf_den += c['weight']

    rolling_conf = (rolling_conf_num / rolling_conf_den) if rolling_conf_den > 0 else 0.0

    total_avail_weight = static_weight + rolling_weight
    if total_avail_weight == 0:
        # No available metrics at all — use pure time/data signal
        return 0.6 * data_conf + 0.4 * time_conf

    if rolling_weight == 0:
        # Pure static
        return 0.6 * data_conf + 0.4 * time_conf

    if static_weight == 0:
        # Pure rolling
        return 0.5 * data_conf + 0.3 * time_conf + 0.2 * rolling_conf

    # Mixed: combine static_conf and rolling_conf weighted by their metric weights
    static_conf = 0.6 * data_conf + 0.4 * time_conf
    rolling_conf_full = 0.5 * data_conf + 0.3 * time_conf + 0.2 * rolling_conf
    return (static_weight * static_conf + rolling_weight * rolling_conf_full) / (static_weight + rolling_weight)
