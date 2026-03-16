import numpy as np
from typing import Dict, Any, List, Optional
from constants.constants import Constants
from decision_engine.risk_profiles import RISK_PROFILES
from decision_engine.metric_configs import METRIC_CONFIGS
from decision_engine.metric_extractor import extract_metric_value

class DecisionEngine:
    """
    Decision layer to evaluate mutual funds using a Z-Score + Sigmoid pipeline.
    This enables relative peer-group scoring.
    """

    @staticmethod
    def calculate_batch_scores(
        all_funds_metrics: List[Dict[str, Any]],
        risk_profile: str = 'Balanced',
    ) -> List[Dict[str, Any]]:
        """
        Perform batch normalization and scoring for a list of funds.
        Pipeline: Metric Value -> Z-Score -> Sigmoid -> 0-100 Score.

        Args:
            all_funds_metrics: List of raw metric dicts from MutualFundAnalyzer.
            risk_profile: One of 'Conservative', 'Balanced', 'Aggressive'.
        """
        if not all_funds_metrics:
            return []

        weights = RISK_PROFILES.get(risk_profile, RISK_PROFILES['Balanced'])

        # 1. Initialize result structure for each fund
        results = []
        for metrics in all_funds_metrics:
            results.append({
                **metrics,
                'category_scores': {cat: 0.0 for cat in METRIC_CONFIGS.keys()},
                'final_score': 0.0
            })

        # 2. Process each metric across all funds
        for category, configs in METRIC_CONFIGS.items():
            for config in configs:
                metric_id = config['id']
                
                # Extract values for all funds
                raw_values = []
                for metrics in all_funds_metrics:
                    val = extract_metric_value(metric_id, metrics)
                    raw_values.append(val)
                
                # Filter out None/Error values for calculation
                valid_values = [v for v in raw_values if v is not None]
                
                if not valid_values:
                    continue
                
                # Calculate population mean and std dev
                mean = np.mean(valid_values)
                std = np.std(valid_values)
                
                # Apply pipeline to each fund
                for i, val in enumerate(raw_values):
                    if val is None:
                        norm_score = 0.0
                    else:
                        # Step 1: Z-Score
                        # If std is 0 (or single fund), Z-score is 0
                        z_score = (val - mean) / std if std > 0 else 0.0
                        
                        # Step 2: Sigmoid Transform (Midpoint is always 0 for Z-score)
                        # Step 3: 0-100 Score
                        norm_score = 100 / (1 + np.exp(-config['steepness'] * z_score))
                    
                    # Apply metric weight within the category
                    results[i]['category_scores'][category] += norm_score * config['weight']

        # 3. Calculate final weighted score for each fund
        for fund in results:
            final_score = 0.0
            for category, weight in weights.items():
                final_score += fund['category_scores'].get(category, 0.0) * weight
            fund['final_score'] = round(float(final_score), 2)
            
            # Round category scores for display
            for cat in fund['category_scores']:
                fund['category_scores'][cat] = round(float(fund['category_scores'][cat]), 2)

        return results

