import pandas as pd
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class StaticBetaCalculator:
    """Calculates static Beta for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Beta for periods defined in Constants.STATIC_BETA_YEARS.
        
        Beta = Covariance(Fund, Benchmark) / Variance(Benchmark)
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with static_betas data.
        """
        df_scheme = Utils.convert_to_dataframe(scheme_data)
        df_benchmark = Utils.convert_to_dataframe(benchmark_data)
        
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        static_betas = {}
        
        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
             for year in Constants.STATIC_BETA_YEARS:
                 static_betas[year] = {'error': 'Data conversion failed or empty data'}
             return {'scheme_name': scheme_name, 'static_betas': static_betas}
        
        # Align dataframes on dates using inner join
        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'), 
            df_benchmark['nav'].rename('benchmark_nav'), 
            left_index=True, 
            right_index=True, 
            how='inner'
        )
        
        if combined_df.empty:
             for year in Constants.STATIC_BETA_YEARS:
                static_betas[year] = {'error': 'No overlapping data with benchmark'}
             return {'scheme_name': scheme_name, 'static_betas': static_betas}

        # Update end_date to be the latest common date
        end_date = combined_df.index[-1]

        for year in Constants.STATIC_BETA_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_betas[year] = {
                    'error': 'Insufficient overlapping data for Beta calculation'
                }
                continue
                
            try:
                # Calculate daily returns
                daily_returns = relevant_df.pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_betas[year] = {
                        'error': 'Insufficient valid returns for Beta calculation'
                    }
                    continue
                
                scheme_returns = daily_returns['scheme_nav']
                benchmark_returns = daily_returns['benchmark_nav']
                
                # Calculate Covariance and Variance
                # cov() returns a matrix, we need the scalar value
                covariance = scheme_returns.cov(benchmark_returns)
                variance = benchmark_returns.var()
                
                if variance == 0:
                     static_betas[year] = {'error': 'Benchmark variance is zero'}
                     continue

                beta = covariance / variance
                static_betas[year] = round(beta, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_betas[year] = {
                    'error': f'Error calculating Beta: {str(e)}'
                }
                
        return {'scheme_name': scheme_name, 'static_betas': static_betas}
