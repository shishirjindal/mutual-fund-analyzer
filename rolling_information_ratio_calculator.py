import pandas as pd
import math
from typing import Dict, Any
from constants import Constants
from utils import Utils

class RollingInformationRatioCalculator:
    """Calculates rolling Information Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling Information Ratio for configurations defined in Constants.ROLLING_INFORMATION_RATIO_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with scheme_name and rolling_information_ratios data.
        """
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        rolling_information_ratios = []
        
        combined_df = Utils.align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
            for config in Constants.ROLLING_INFORMATION_RATIO_MAP:
                rolling_information_ratios.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'Data alignment failed or no overlapping data'
                })
            return {'scheme_name': scheme_name, 'rolling_information_ratios': rolling_information_ratios}
        
        for config in Constants.ROLLING_INFORMATION_RATIO_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for the total years required
            end_date = combined_df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_information_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data for {total_years} years'
                })
                continue

            # Calculate daily returns
            daily_returns = relevant_df.pct_change().dropna()
            
            # Define window size (trading days)
            window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
            
            if len(daily_returns) < window_size:
                rolling_information_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate daily active returns
            active_returns_daily = daily_returns['scheme_nav'] - daily_returns['benchmark_nav']
            
            # Calculate rolling mean and standard deviation of active returns
            rolling_mean_active = active_returns_daily.rolling(window=window_size).mean()
            rolling_std_active = active_returns_daily.rolling(window=window_size).std(ddof=0)
            
            # Annualize
            ann_active_return = rolling_mean_active * Constants.TRADING_DAYS_PER_YEAR
            ann_tracking_error = rolling_std_active * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
            
            # Information Ratio = Annualized Active Return / Annualized Tracking Error
            ir = ann_active_return / ann_tracking_error
            
            # Drop NaNs and infinite values
            valid_ir = ir.replace([float('inf'), -float('inf')], float('nan')).dropna()
            
            if valid_ir.empty:
                rolling_information_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Information Ratio values'
                })
            else:
                rolling_information_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': round(valid_ir.median(), Constants.DECIMAL_PLACES),
                    'mean': round(valid_ir.mean(), Constants.DECIMAL_PLACES),
                    'min': round(valid_ir.min(), Constants.DECIMAL_PLACES),
                    'max': round(valid_ir.max(), Constants.DECIMAL_PLACES),
                    'latest': round(valid_ir.iloc[-1], Constants.DECIMAL_PLACES)
                })
        
        return {
            'scheme_name': scheme_name,
            'rolling_information_ratios': rolling_information_ratios
        }
