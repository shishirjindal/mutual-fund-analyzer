import numpy as np
from typing import Dict, Any, List, Optional
from constants import Constants
from decision_config import CATEGORY_WEIGHTS, METRIC_CONFIGS

class DecisionEngine:
    """
    Decision layer to evaluate mutual funds using a Z-Score + Sigmoid pipeline.
    This enables relative peer-group scoring.
    """

    @staticmethod
    def calculate_batch_scores(all_funds_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform batch normalization and scoring for a list of funds.
        Pipeline: Metric Value -> Z-Score -> Sigmoid -> 0-100 Score.
        """
        if not all_funds_metrics:
            return []

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
                    val = DecisionEngine._extract_metric_value(metric_id, metrics)
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
            for category, weight in CATEGORY_WEIGHTS.items():
                final_score += fund['category_scores'].get(category, 0.0) * weight
            fund['final_score'] = round(float(final_score), 2)
            
            # Round category scores for display
            for cat in fund['category_scores']:
                fund['category_scores'][cat] = round(float(fund['category_scores'][cat]), 2)

        return results

    @staticmethod
    def _extract_metric_value(metric_id: str, metrics: Dict[str, Any]) -> Optional[float]:
        """Extract a specific metric value from the metrics dictionary."""
        try:
            if metric_id == 'static_5y_cagr':
                return metrics.get('rolling_data', {}).get(5, {}).get('avg')
            elif metric_id == 'static_3y_cagr':
                return metrics.get('rolling_data', {}).get(3, {}).get('avg')
            elif metric_id == 'static_1y_return':
                return metrics.get('rolling_data', {}).get(1, {}).get('avg')
            elif metric_id == 'calendar_avg':
                calendar_data = metrics.get('calendar_data', {})
                cal_vals = [v for k, v in calendar_data.items() if str(k).isdigit() and v is not None]
                if cal_vals:
                    return sum(cal_vals) / len(cal_vals)
            elif metric_id == 'worst_calendar_year':
                return metrics.get('worst_calendar_data', {}).get('worst_return')
            elif metric_id == 'rolling_3y_median':
                return metrics.get('rolling_data', {}).get(3, {}).get('median')
            elif metric_id == 'rolling_3y_percentile_25':
                return metrics.get('rolling_data', {}).get(3, {}).get('percentile_25')
            elif metric_id == 'rolling_3y_std_dev':
                return metrics.get('rolling_data', {}).get(3, {}).get('std_dev')
            elif metric_id == 'rolling_5y_median':
                return metrics.get('rolling_data', {}).get(5, {}).get('median')
            elif metric_id == 'rolling_5y_percentile_25':
                return metrics.get('rolling_data', {}).get(5, {}).get('percentile_25')
            elif metric_id == 'rolling_5y_std_dev':
                return metrics.get('rolling_data', {}).get(5, {}).get('std_dev')
            elif metric_id == 'rolling_3y_avg':
                return metrics.get('rolling_data', {}).get(3, {}).get('avg')
            elif metric_id == 'rolling_5y_avg':
                return metrics.get('rolling_data', {}).get(5, {}).get('avg')
            elif metric_id == 'calendar_3y_avg':
                calendar_data = metrics.get('calendar_data', {})
                cal_vals = [v for k, v in calendar_data.items() if str(k).isdigit() and v is not None]
                if cal_vals:
                    # Filter for last 3 unique years if possible, otherwise just last 3 values
                    return sum(cal_vals[-3:]) / min(len(cal_vals), 3)
            elif metric_id == 'calendar_5y_avg':
                calendar_data = metrics.get('calendar_data', {})
                cal_vals = [v for k, v in calendar_data.items() if str(k).isdigit() and v is not None]
                if cal_vals:
                    return sum(cal_vals[-5:]) / min(len(cal_vals), 5)
            elif metric_id == 'static_std_dev_3y':
                val = metrics.get('static_std_dev_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_std_dev_5y':
                val = metrics.get('static_std_dev_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'rolling_std_dev_3y_median':
                roll_std_data = metrics.get('rolling_std_dev_data', [])
                three_yr = next((i for i in roll_std_data if i['rolling_window'] == 3), None)
                return three_yr.get('median') if three_yr else None
            elif metric_id == 'static_mdd_3y':
                val = metrics.get('static_drawdown_data', {}).get(3, {}).get('max_drawdown')
                return abs(val) if val is not None else None
            elif metric_id == 'static_mdd_5y_value':
                val = metrics.get('static_drawdown_data', {}).get(5, {}).get('max_drawdown')
                return abs(val) if val is not None else None
            elif metric_id == 'static_mdd_5y_duration':
                return metrics.get('static_drawdown_data', {}).get(5, {}).get('max_duration_days')
            elif metric_id == 'rolling_mdd_3y_median':
                roll_dd_data = metrics.get('rolling_drawdown_data', [])
                three_yr = next((i for i in roll_dd_data if i['rolling_window'] == 3), None)
                return abs(three_yr.get('median')) if three_yr and 'median' in three_yr else None
            elif metric_id == 'rolling_mdd_3y_percentile_75':
                roll_dd_data = metrics.get('rolling_drawdown_data', [])
                three_yr = next((i for i in roll_dd_data if i['rolling_window'] == 3), None)
                return abs(three_yr.get('percentile_75')) if three_yr and 'percentile_75' in three_yr else None
            elif metric_id == 'rolling_mdd_3y_worst':
                roll_dd_data = metrics.get('rolling_drawdown_data', [])
                three_yr = next((i for i in roll_dd_data if i['rolling_window'] == 3), None)
                return abs(three_yr.get('min')) if three_yr and 'min' in three_yr else None
            elif metric_id == 'static_ulcer_3y':
                val = metrics.get('static_ulcer_index_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_ulcer_5y':
                val = metrics.get('static_ulcer_index_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_sharpe_3y':
                val = metrics.get('static_sharpe_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_sharpe_5y':
                val = metrics.get('static_sharpe_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_sortino_3y':
                val = metrics.get('static_sortino_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_sortino_5y':
                val = metrics.get('static_sortino_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_calmar_3y':
                val = metrics.get('static_calmar_ratio_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_calmar_5y':
                val = metrics.get('static_calmar_ratio_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_treynor_3y':
                val = metrics.get('static_treynor_ratio_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_treynor_5y':
                val = metrics.get('static_treynor_ratio_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_alpha_3y':
                val = metrics.get('static_alpha_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_alpha_5y':
                val = metrics.get('static_alpha_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_beta_3y':
                val = metrics.get('static_beta_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_beta_5y':
                val = metrics.get('static_beta_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'rolling_alpha_3y_median':
                roll_alpha_data = metrics.get('rolling_alpha_data', [])
                three_yr = next((i for i in roll_alpha_data if i['rolling_window'] == 3), None)
                return three_yr.get('median') if three_yr else None
            elif metric_id == 'rolling_alpha_3y_positive':
                roll_alpha_data = metrics.get('rolling_alpha_data', [])
                three_yr = next((i for i in roll_alpha_data if i['rolling_window'] == 3), None)
                return three_yr.get('positive_share') if three_yr else None
            elif metric_id == 'rolling_alpha_3y_std':
                roll_alpha_data = metrics.get('rolling_alpha_data', [])
                three_yr = next((i for i in roll_alpha_data if i['rolling_window'] == 3), None)
                return three_yr.get('std_dev') if three_yr else None
            elif metric_id == 'rolling_ir_3y_median':
                roll_ir_data = metrics.get('rolling_information_ratio_data', [])
                three_yr = next((i for i in roll_ir_data if i['rolling_window'] == 3), None)
                return three_yr.get('median') if three_yr else None
            elif metric_id == 'rolling_ir_3y_positive':
                roll_ir_data = metrics.get('rolling_information_ratio_data', [])
                three_yr = next((i for i in roll_ir_data if i['rolling_window'] == 3), None)
                return three_yr.get('positive_share') if three_yr else None
            elif metric_id == 'rolling_ir_3y_std':
                roll_ir_data = metrics.get('rolling_information_ratio_data', [])
                three_yr = next((i for i in roll_ir_data if i['rolling_window'] == 3), None)
                return three_yr.get('std_dev') if three_yr else None
            elif metric_id == 'static_ir_3y':
                val = metrics.get('static_information_ratio_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_ir_5y':
                val = metrics.get('static_information_ratio_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_hit_ratio_3y':
                val = metrics.get('static_hit_ratio_data', {}).get(3)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'static_hit_ratio_5y':
                val = metrics.get('static_hit_ratio_data', {}).get(5)
                return val if not isinstance(val, dict) else None
            elif metric_id == 'rolling_sharpe_3y_median':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                three_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 3), None)
                return three_yr.get('median') if three_yr else None
            elif metric_id == 'rolling_sharpe_3y_percentile_25':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                three_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 3), None)
                return three_yr.get('percentile_25') if three_yr else None
            elif metric_id == 'rolling_sharpe_3y_std_dev':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                three_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 3), None)
                return three_yr.get('std_dev') if three_yr else None
            elif metric_id == 'rolling_sharpe_5y_median':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                five_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 5), None)
                return five_yr.get('median') if five_yr else None
            elif metric_id == 'rolling_sharpe_5y_percentile_25':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                five_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 5), None)
                return five_yr.get('percentile_25') if five_yr else None
            elif metric_id == 'rolling_sharpe_5y_std_dev':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                five_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 5), None)
                return five_yr.get('std_dev') if five_yr else None
            elif metric_id == 'rolling_hit_ratio_3y_median':
                roll_hit_data = metrics.get('rolling_hit_ratio_data', [])
                three_yr = next((i for i in roll_hit_data if i['rolling_window'] == 3), None)
                return three_yr.get('median') if three_yr else None
            elif metric_id == 'rolling_hit_ratio_3y_percentile_25':
                roll_hit_data = metrics.get('rolling_hit_ratio_data', [])
                three_yr = next((i for i in roll_hit_data if i['rolling_window'] == 3), None)
                return three_yr.get('percentile_25') if three_yr else None
            elif metric_id == 'rolling_hit_ratio_5y_median':
                roll_hit_data = metrics.get('rolling_hit_ratio_data', [])
                five_yr = next((i for i in roll_hit_data if i['rolling_window'] == 5), None)
                return five_yr.get('median') if five_yr else None
            elif metric_id == 'rolling_hit_ratio_5y_percentile_25':
                roll_hit_data = metrics.get('rolling_hit_ratio_data', [])
                five_yr = next((i for i in roll_hit_data if i['rolling_window'] == 5), None)
                return five_yr.get('percentile_25') if five_yr else None
            elif metric_id == 'rolling_sharpe_3y_positive':
                roll_sharpe_data = metrics.get('rolling_sharpe_data', [])
                three_yr = next((i for i in roll_sharpe_data if i['rolling_window'] == 3), None)
                return three_yr.get('positive_share') if three_yr else None
            elif metric_id == 'rolling_sortino_3y_median':
                roll_sortino_data = metrics.get('rolling_sortino_data', [])
                three_yr = next((i for i in roll_sortino_data if i['rolling_window'] == 3), None)
                return three_yr.get('median') if three_yr else None
        except Exception:
            return None
        return None
