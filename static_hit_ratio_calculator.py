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
            Dictionary with scheme_name and static_hit_ratios data.
        """
        df_scheme = Utils.convert_to_dataframe(scheme_data)
        df_benchmark = Utils.convert_to_dataframe(benchmark_data)
        
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        static_hit_ratios = {}
        
        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
            for year in Constants.STATIC_HIT_RATIO_YEARS:
                static_hit_ratios[year] = {'error': 'Data conversion failed or empty data'}
            return {'scheme_name': scheme_name, 'static_hit_ratios': static_hit_ratios}
        
        # Align dataframes
        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'), 
            df_benchmark['nav'].rename('benchmark_nav'), 
            left_index=True, 
            right_index=True, 
            how='inner'
        )
        
        if combined_df.empty:
            for year in Constants.STATIC_HIT_RATIO_YEARS:
                static_hit_ratios[year] = {'error': 'No overlapping data with benchmark'}
            return {'scheme_name': scheme_name, 'static_hit_ratios': static_hit_ratios}
            
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
                
        return {
            'scheme_name': scheme_name,
            'static_hit_ratios': static_hit_ratios
        }
