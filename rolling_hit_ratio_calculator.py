import pandas as pd
from typing import Dict, Any
from constants import Constants
from utils import Utils

class RollingHitRatioCalculator:
    """Calculates rolling Hit Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling Hit Ratio for configurations defined in Constants.ROLLING_HIT_RATIO_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with scheme_name and rolling_hit_ratios data.
        """
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        rolling_hit_ratios = []
        
        combined_df = Utils.align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
            for config in Constants.ROLLING_HIT_RATIO_MAP:
                rolling_hit_ratios.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'Data alignment failed or no overlapping data'
                })
            return {'scheme_name': scheme_name, 'rolling_hit_ratios': rolling_hit_ratios}
            
        for config in Constants.ROLLING_HIT_RATIO_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for total years
            end_date = combined_df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_hit_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data for {total_years} years'
                })
                continue
                
            # Calculate daily returns
            daily_returns = relevant_df.pct_change().dropna()
            
            # Window size in trading days
            window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
            
            if len(daily_returns) < window_size:
                rolling_hit_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
                
            # Boolean series for outperformance
            outperformance = (daily_returns['scheme_nav'] > daily_returns['benchmark_nav']).astype(int)
            
            # Rolling sum of outperformance days / window size * 100
            rolling_hit_ratio = (outperformance.rolling(window=window_size).sum() / window_size) * 100
            
            # Filter valid ratios
            valid_ratios = rolling_hit_ratio.dropna()
            
            if valid_ratios.empty:
                rolling_hit_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Hit Ratio values'
                })
            else:
                rolling_hit_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': round(valid_ratios.median(), Constants.DECIMAL_PLACES),
                    'mean': round(valid_ratios.mean(), Constants.DECIMAL_PLACES),
                    'min': round(valid_ratios.min(), Constants.DECIMAL_PLACES),
                    'max': round(valid_ratios.max(), Constants.DECIMAL_PLACES),
                    'latest': round(valid_ratios.iloc[-1], Constants.DECIMAL_PLACES)
                })
                
        return {
            'scheme_name': scheme_name,
            'rolling_hit_ratios': rolling_hit_ratios
        }
