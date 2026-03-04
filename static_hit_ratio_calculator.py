import pandas as pd
from typing import Dict, Any
from constants import Constants
from utils import Utils

class StaticHitRatioCalculator:
    """Calculates Static Hit Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Hit Ratio for periods defined in Constants.STATIC_HIT_RATIO_YEARS.
        
        Hit Ratio = (Number of outperformance days / Total trading days) * 100
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary containing static Hit Ratio data.
        """
        static_hit_ratios = {}
        
        combined_df = Utils.align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
            for year in Constants.STATIC_HIT_RATIO_YEARS:
                static_hit_ratios[year] = {'error': 'Data alignment failed or no overlapping data'}
            return static_hit_ratios
            
        end_date = combined_df.index[-1]
        
        for year in Constants.STATIC_HIT_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_hit_ratios[year] = {'error': 'Insufficient overlapping data for Hit Ratio calculation'}
                continue
                
            try:
                # Calculate daily returns
                daily_returns = relevant_df.pct_change().dropna()
                
                if daily_returns.empty:
                    static_hit_ratios[year] = {'error': 'No returns data available'}
                    continue
                
                # Compare returns: scheme outperformed benchmark
                outperformance = (daily_returns['scheme_nav'] > daily_returns['benchmark_nav']).sum()
                total_days = len(daily_returns)
                
                hit_ratio = (outperformance / total_days) * 100
                static_hit_ratios[year] = round(hit_ratio, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_hit_ratios[year] = {'error': f'Error calculating Hit Ratio: {str(e)}'}
                
        return static_hit_ratios
