import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from constants.constants import Constants
from utils.return_utils import calculate_daily_returns, calculate_downside_deviation
from utils.dataframe_utils import convert_to_dataframe, align_dataframes

class StaticDrawdownCalculator:
    """Calculates Maximum Drawdown and Drawdown Duration for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Maximum Drawdown and Drawdown Duration for periods defined in Constants.STATIC_DRAWDOWN_YEARS.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary containing static drawdown data.
        """
        df = convert_to_dataframe(scheme_data)
        
        drawdowns = {}
        
        if df is None or df.empty:
            for year in Constants.STATIC_DRAWDOWN_YEARS:
                drawdowns[year] = {'error': 'No data available'}
            return drawdowns
        end_date = df.index[-1]
        
        for year in Constants.STATIC_DRAWDOWN_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                drawdowns[year] = {'error': 'Insufficient data for Drawdown calculation'}
                continue
            
            try:
                # Calculate Cumulative Maximum
                cummax = relevant_df['nav'].cummax()
                
                # Calculate Drawdown (percentage)
                drawdown_series = (relevant_df['nav'] - cummax) / cummax
                max_drawdown = drawdown_series.min() * 100
                
                # Robustly identify peaks using a small epsilon to handle floating point issues
                # A peak is where NAV is effectively equal to the running cumulative maximum
                is_peak = np.isclose(relevant_df['nav'], cummax, rtol=1e-09, atol=1e-09)
                peak_dates = relevant_df.index[is_peak]
                
                max_duration_days = 0
                
                if not peak_dates.empty:
                    # Gaps between consecutive peaks represent the Time to Recover (in calendar days)
                    # This logic works because 'cummax' stays flat during a drawdown and only increases/matches
                    # when the price recovers to the previous high or sets a new one.
                    # So the difference between two 'peak' timestamps includes the time spent in the valley.
                    
                    # Ensure index is DatetimeIndex for .dt accessor
                    peak_dates_series = peak_dates.to_series()
                    if not pd.api.types.is_datetime64_any_dtype(peak_dates_series):
                         peak_dates_series = pd.to_datetime(peak_dates_series)
                         
                    recovery_times = peak_dates_series.diff().dt.days.fillna(0)
                    
                    # Current ongoing drawdown duration (from last peak to now)
                    # Only relevant if the last date in data is NOT a peak (i.e. we are currently in drawdown)
                    current_drawdown = 0
                    if not is_peak[-1]:
                        current_drawdown = (relevant_df.index[-1] - peak_dates[-1]).days
                    
                    # Max of all recovery times and current drawdown
                    max_duration_days = max(recovery_times.max(), current_drawdown)
                
                drawdowns[year] = {
                    'max_drawdown': round(max_drawdown, Constants.DECIMAL_PLACES),
                    'max_duration_days': int(max_duration_days)
                }
            except Exception as e:
                drawdowns[year] = {'error': f'Error calculating Drawdown: {str(e)}'}
        
        return drawdowns
