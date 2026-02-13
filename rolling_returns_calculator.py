import pandas as pd
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class RollingReturnsCalculator:
    """Calculates rolling returns for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling returns for periods defined in Constants.ROLLING_YEARS using stored scheme data.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and rolling_returns data.
        """
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        df = Utils.convert_to_dataframe(scheme_data)
        
        rolling_returns = {}
        
        if df is None or df.empty:
            for year in Constants.ROLLING_YEARS:
                rolling_returns[year] = {'error': 'No data available'}
            return {'scheme_name': scheme_name, 'rolling_returns': rolling_returns}
        
        for year in Constants.ROLLING_YEARS:
            days = year * Constants.TRADING_DAYS_PER_YEAR
            
            # Check if we have enough data points (approximate check)
            # Need at least 'days' points to calculate one rolling return
            if len(df) <= days:
                rolling_returns[year] = {
                    'error': f'Insufficient data (need {days} days, have {len(df)})'
                }
                continue
            
            # Calculate absolute return over 'days' period
            # pct_change computes (current - shifted) / shifted
            # We want percentage, so multiply by 100
            # This is a vectorized operation, much faster than looping
            absolute_returns = df['nav'].pct_change(periods=days) * 100
            
            # Check for and handle infinite values (e.g., division by zero)
            absolute_returns = absolute_returns.replace([float('inf'), -float('inf')], float('nan'))
            
            # Drop NaN values (first 'days' rows will be NaN because of shift)
            valid_returns = absolute_returns.dropna()
            
            # Filter out invalid returns (<= -100%) which would cause math errors in CAGR
            # or imply impossible negative prices
            valid_returns = valid_returns[valid_returns > -100]
            
            if valid_returns.empty:
                rolling_returns[year] = {'error': 'No valid data points'}
                continue
                
            # Calculate CAGR for each rolling return
            # Formula: ((1 + abs_ret/100)^(1/years) - 1) * 100
            # Vectorized calculation using Pandas
            cagr_values = ((1 + valid_returns / 100).pow(1 / year) - 1) * 100
            
            rolling_returns[year] = {
                'min': round(cagr_values.min(), Constants.DECIMAL_PLACES),
                'avg': round(cagr_values.mean(), Constants.DECIMAL_PLACES),
                'max': round(cagr_values.max(), Constants.DECIMAL_PLACES)
            }
        
        return {
            'scheme_name': scheme_name,
            'rolling_returns': rolling_returns
        }
