import numpy as np
from typing import Dict, Any, List, Optional
from decision_engine.risk_profiles import RISK_PROFILES
from decision_engine.metric_configs import METRIC_CONFIGS
from decision_engine.metric_extractor import extract_metric_value
from decision_engine.confidence import compute_category_confidence


class DecisionEngine:
    """
    Decision layer to evaluate mutual funds using a Z-Score + Sigmoid pipeline.

    Scoring pipeline per category:
      1. Z-score + sigmoid → norm_score per metric (peer-relative, 0–100)
      2. raw_score = weighted avg over AVAILABLE metrics only (no zero-fill)
      3. confidence_multiplier = f(data_confidence, time_confidence, rolling_confidence)
      4. category_score = raw_score * (0.7 + 0.3 * confidence_multiplier)
      5. final_score = sum(category_score * category_weight)
    """

    @staticmethod
    def calculate_batch_scores(
        all_funds_metrics: List[Dict[str, Any]],
        risk_profile: str = 'Balanced',
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        if not all_funds_metrics:
            return []

        weights = (
            custom_weights
            if risk_profile == 'Custom' and custom_weights
            else RISK_PROFILES.get(risk_profile, RISK_PROFILES['Balanced'])
        )

        # Initialize result structure
        results = [{
            **m,
            'category_scores': {cat: 0.0 for cat in METRIC_CONFIGS},
            'final_score': 0.0,
        } for m in all_funds_metrics]

        for category, configs in METRIC_CONFIGS.items():
            # --- Step 1: extract raw values for all funds ---
            raw_values = [
                [extract_metric_value(cfg['id'], m) for cfg in configs]
                for m in all_funds_metrics
            ]

            # --- Step 2: Z-score + sigmoid per metric across the peer group ---
            # norm_scores[fund_idx][metric_idx] = 0–100 or None
            norm_scores: List[List[Optional[float]]] = [
                [None] * len(configs) for _ in all_funds_metrics
            ]

            for mi, cfg in enumerate(configs):
                col = [raw_values[fi][mi] for fi in range(len(all_funds_metrics))]
                valid = [v for v in col if v is not None]
                if not valid:
                    continue
                mean = np.mean(valid)
                std = np.std(valid)
                for fi, val in enumerate(col):
                    if val is None:
                        continue
                    z = (val - mean) / std if std > 0 else 0.0
                    norm_scores[fi][mi] = 100 / (1 + np.exp(-cfg['steepness'] * z))

            # --- Step 3: per-fund raw_score (normalized to available weights) + confidence ---
            for fi, fund in enumerate(results):
                available_mask = [norm_scores[fi][mi] is not None for mi in range(len(configs))]
                avail_weight = sum(
                    cfg['weight'] for mi, cfg in enumerate(configs) if available_mask[mi]
                )

                if avail_weight == 0:
                    fund['category_scores'][category] = 0.0
                    continue

                raw_score = sum(
                    norm_scores[fi][mi] * cfg['weight']
                    for mi, cfg in enumerate(configs)
                    if available_mask[mi]
                ) / avail_weight

                confidence = compute_category_confidence(
                    configs, available_mask, all_funds_metrics[fi]
                )
                fund['category_scores'][category] = round(
                    raw_score * (0.7 + 0.3 * confidence), 2
                )

        # --- Step 4: final weighted score ---
        for fund in results:
            fund['final_score'] = round(
                sum(fund['category_scores'].get(cat, 0.0) * w for cat, w in weights.items()), 2
            )

        return results
