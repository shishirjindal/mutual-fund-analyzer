import pandas as pd
import numpy as np
import math
from typing import Dict, Any
from constants.constants import Constants
from utils.return_utils import calculate_daily_returns, calculate_downside_deviation
from utils.dataframe_utils import convert_to_dataframe, align_dataframes

class StaticUlcerIndexCalculator:
    """Calculates Static Ulcer Index for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Ulcer Index for periods defined in Constants.STATIC_ULCER_INDEX_YEARS.
        
        Ulcer Index = sqrt( mean( squared_drawdown_percentages ) )
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary containing static Ulcer Index data.
        """
        df = convert_to_dataframe(scheme_data)
        
        static_ulcer_indices = {}
        
        if df is None or df.empty:
            for year in Constants.STATIC_ULCER_INDEX_YEARS:
                static_ulcer_indices[year] = {'error': 'No data available'}
            return static_ulcer_indices
        end_date = df.index[-1]
        
        for year in Constants.STATIC_ULCER_INDEX_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_ulcer_indices[year] = {'error': 'Insufficient data for Ulcer Index calculation'}
                continue
            
            try:
                # 1. Calculate Cumulative Maximum
                cummax = relevant_df['nav'].cummax()
                
                # 2. Calculate Drawdown (percentage)
                # Formula for UI: ((Price - Peak) / Peak) * 100
                drawdown_series = (relevant_df['nav'] - cummax) / cummax * 100
                
                # 3. Square the drawdowns
                squared_drawdown = drawdown_series ** 2
                
                # 4. Calculate Mean of squares
                mean_squared_drawdown = squared_drawdown.mean()
                
                # 5. Take Square Root
                ulcer_index = math.sqrt(mean_squared_drawdown)
                
                static_ulcer_indices[year] = round(ulcer_index, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_ulcer_indices[year] = {'error': f'Error calculating Ulcer Index: {str(e)}'}
        
        return static_ulcer_indices
