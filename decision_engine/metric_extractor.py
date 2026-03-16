"""
Metric extraction for the Decision Engine.
Pulls specific scalar values out of a fund's metrics dict.
"""

from typing import Dict, Any, Optional


class MetricExtractor:
    """Extracts individual metric values from a fund metrics dictionary."""

    @staticmethod
    def extract(metric_id: str, metrics: Dict[str, Any]) -> Optional[float]:
        """Extract a specific metric value from the metrics dictionary."""
        try:
            if metric_id == 'static_5y_cagr':
                return metrics.get('rolling_data', {}).get(5, {}).get('avg')
            elif metric_id == 'static_3y_cagr':
                return metrics.get('rolling_data', {}).get(3, {}).get('avg')
            elif metric_id == 'static_1y_return':
                return metrics.get('rolling_data', {}).get(1, {}).get('avg')
            elif metric_id == 'calendar_avg':
                cal_vals = MetricExtractor._calendar_vals(metrics)
                return sum(cal_vals) / len(cal_vals) if cal_vals else None
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
                cal_vals = MetricExtractor._calendar_vals(metrics)
                return sum(cal_vals[-3:]) / min(len(cal_vals), 3) if cal_vals else None
            elif metric_id == 'calendar_5y_avg':
                cal_vals = MetricExtractor._calendar_vals(metrics)
                return sum(cal_vals[-5:]) / min(len(cal_vals), 5) if cal_vals else None
            elif metric_id == 'static_std_dev_3y':
                return MetricExtractor._scalar(metrics, 'static_std_dev_data', 3)
            elif metric_id == 'static_std_dev_5y':
                return MetricExtractor._scalar(metrics, 'static_std_dev_data', 5)
            elif metric_id == 'rolling_std_dev_3y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_std_dev_data', 3, 'median')
            elif metric_id == 'static_mdd_3y':
                return MetricExtractor._abs_nested(metrics, 'static_drawdown_data', 3, 'max_drawdown')
            elif metric_id == 'static_mdd_5y_value':
                return MetricExtractor._abs_nested(metrics, 'static_drawdown_data', 5, 'max_drawdown')
            elif metric_id == 'static_mdd_5y_duration':
                return metrics.get('static_drawdown_data', {}).get(5, {}).get('max_duration_days')
            elif metric_id == 'rolling_mdd_3y_median':
                return MetricExtractor._abs_rolling_stat(metrics, 'rolling_drawdown_data', 3, 'median')
            elif metric_id == 'rolling_mdd_3y_percentile_75':
                return MetricExtractor._abs_rolling_stat(metrics, 'rolling_drawdown_data', 3, 'percentile_75')
            elif metric_id == 'rolling_mdd_3y_worst':
                return MetricExtractor._abs_rolling_stat(metrics, 'rolling_drawdown_data', 3, 'min')
            elif metric_id == 'static_ulcer_3y':
                return MetricExtractor._scalar(metrics, 'static_ulcer_index_data', 3)
            elif metric_id == 'static_ulcer_5y':
                return MetricExtractor._scalar(metrics, 'static_ulcer_index_data', 5)
            elif metric_id == 'static_sharpe_3y':
                return MetricExtractor._scalar(metrics, 'static_sharpe_data', 3)
            elif metric_id == 'static_sharpe_5y':
                return MetricExtractor._scalar(metrics, 'static_sharpe_data', 5)
            elif metric_id == 'static_sortino_3y':
                return MetricExtractor._scalar(metrics, 'static_sortino_data', 3)
            elif metric_id == 'static_sortino_5y':
                return MetricExtractor._scalar(metrics, 'static_sortino_data', 5)
            elif metric_id == 'static_calmar_3y':
                return MetricExtractor._scalar(metrics, 'static_calmar_ratio_data', 3)
            elif metric_id == 'static_calmar_5y':
                return MetricExtractor._scalar(metrics, 'static_calmar_ratio_data', 5)
            elif metric_id == 'static_treynor_3y':
                return MetricExtractor._scalar(metrics, 'static_treynor_ratio_data', 3)
            elif metric_id == 'static_treynor_5y':
                return MetricExtractor._scalar(metrics, 'static_treynor_ratio_data', 5)
            elif metric_id == 'static_alpha_3y':
                return MetricExtractor._scalar(metrics, 'static_alpha_data', 3)
            elif metric_id == 'static_alpha_5y':
                return MetricExtractor._scalar(metrics, 'static_alpha_data', 5)
            elif metric_id == 'static_beta_3y':
                return MetricExtractor._scalar(metrics, 'static_beta_data', 3)
            elif metric_id == 'static_beta_5y':
                return MetricExtractor._scalar(metrics, 'static_beta_data', 5)
            elif metric_id == 'static_ir_3y':
                return MetricExtractor._scalar(metrics, 'static_information_ratio_data', 3)
            elif metric_id == 'static_ir_5y':
                return MetricExtractor._scalar(metrics, 'static_information_ratio_data', 5)
            elif metric_id == 'static_hit_ratio_3y':
                return MetricExtractor._scalar(metrics, 'static_hit_ratio_data', 3)
            elif metric_id == 'static_hit_ratio_5y':
                return MetricExtractor._scalar(metrics, 'static_hit_ratio_data', 5)
            elif metric_id == 'rolling_alpha_3y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_alpha_data', 3, 'median')
            elif metric_id == 'rolling_alpha_3y_positive':
                return MetricExtractor._rolling_stat(metrics, 'rolling_alpha_data', 3, 'positive_share')
            elif metric_id == 'rolling_alpha_3y_std':
                return MetricExtractor._rolling_stat(metrics, 'rolling_alpha_data', 3, 'std_dev')
            elif metric_id == 'rolling_ir_3y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_information_ratio_data', 3, 'median')
            elif metric_id == 'rolling_ir_3y_positive':
                return MetricExtractor._rolling_stat(metrics, 'rolling_information_ratio_data', 3, 'positive_share')
            elif metric_id == 'rolling_ir_3y_std':
                return MetricExtractor._rolling_stat(metrics, 'rolling_information_ratio_data', 3, 'std_dev')
            elif metric_id == 'rolling_sharpe_3y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 3, 'median')
            elif metric_id == 'rolling_sharpe_3y_percentile_25':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 3, 'percentile_25')
            elif metric_id == 'rolling_sharpe_3y_std_dev':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 3, 'std_dev')
            elif metric_id == 'rolling_sharpe_3y_positive':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 3, 'positive_share')
            elif metric_id == 'rolling_sharpe_5y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 5, 'median')
            elif metric_id == 'rolling_sharpe_5y_percentile_25':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 5, 'percentile_25')
            elif metric_id == 'rolling_sharpe_5y_std_dev':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sharpe_data', 5, 'std_dev')
            elif metric_id == 'rolling_hit_ratio_3y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_hit_ratio_data', 3, 'median')
            elif metric_id == 'rolling_hit_ratio_3y_percentile_25':
                return MetricExtractor._rolling_stat(metrics, 'rolling_hit_ratio_data', 3, 'percentile_25')
            elif metric_id == 'rolling_hit_ratio_5y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_hit_ratio_data', 5, 'median')
            elif metric_id == 'rolling_hit_ratio_5y_percentile_25':
                return MetricExtractor._rolling_stat(metrics, 'rolling_hit_ratio_data', 5, 'percentile_25')
            elif metric_id == 'rolling_sortino_3y_median':
                return MetricExtractor._rolling_stat(metrics, 'rolling_sortino_data', 3, 'median')
        except Exception:
            return None
        return None

    @staticmethod
    def _calendar_vals(metrics: Dict[str, Any]):
        cal = metrics.get('calendar_data', {})
        return [v for k, v in cal.items() if str(k).isdigit() and v is not None]

    @staticmethod
    def _scalar(metrics: Dict[str, Any], key: str, year: int) -> Optional[float]:
        val = metrics.get(key, {}).get(year)
        return val if not isinstance(val, dict) else None

    @staticmethod
    def _rolling_stat(metrics: Dict[str, Any], key: str, window: int, stat: str) -> Optional[float]:
        entry = next((i for i in metrics.get(key, []) if i.get('rolling_window') == window), None)
        return entry.get(stat) if entry else None

    @staticmethod
    def _abs_nested(metrics: Dict[str, Any], key: str, year: int, stat: str) -> Optional[float]:
        val = metrics.get(key, {}).get(year, {}).get(stat)
        return abs(val) if val is not None else None

    @staticmethod
    def _abs_rolling_stat(metrics: Dict[str, Any], key: str, window: int, stat: str) -> Optional[float]:
        entry = next((i for i in metrics.get(key, []) if i.get('rolling_window') == window), None)
        val = entry.get(stat) if entry and stat in entry else None
        return abs(val) if val is not None else None


# Module-level alias so decision_engine.py can call extract_metric_value(...)
extract_metric_value = MetricExtractor.extract
