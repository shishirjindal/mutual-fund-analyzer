import pandas as pd
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class StaticAlphaCalculator:
    """Calculates static Jensen's Alpha for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Alpha (Jensen's Alpha) for periods defined in Constants.STATIC_ALPHA_YEARS.
        
        Alpha = (Rp - Rf) - Beta * (Rm - Rf)
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with static_alphas data.
        """
        df_scheme = Utils.convert_to_dataframe(scheme_data)
        df_benchmark = Utils.convert_to_dataframe(benchmark_data)
        
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        static_alphas = {}
        
        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
             for year in Constants.STATIC_ALPHA_YEARS:
                 static_alphas[year] = {'error': 'Data conversion failed or empty data'}
             return {'scheme_name': scheme_name, 'static_alphas': static_alphas}
        
        # Align dataframes on dates
        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'), 
            df_benchmark['nav'].rename('benchmark_nav'), 
            left_index=True, 
            right_index=True, 
            how='inner'
        )
        
        if combined_df.empty:
             for year in Constants.STATIC_ALPHA_YEARS:
                static_alphas[year] = {'error': 'No overlapping data with benchmark'}
             return {'scheme_name': scheme_name, 'static_alphas': static_alphas}

        end_date = combined_df.index[-1]

        for year in Constants.STATIC_ALPHA_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_alphas[year] = {
                    'error': 'Insufficient overlapping data for Alpha calculation'
                }
                continue
                
            try:
                # Calculate daily returns
                daily_returns = relevant_df.pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_alphas[year] = {
                        'error': 'Insufficient valid returns for Alpha calculation'
                    }
                    continue
                
                scheme_returns = daily_returns['scheme_nav']
                benchmark_returns = daily_returns['benchmark_nav']
                
                # Calculate Beta
                covariance = scheme_returns.cov(benchmark_returns)
                variance = benchmark_returns.var()
                
                if variance == 0:
                     static_alphas[year] = {'error': 'Benchmark variance is zero'}
                     continue

                beta = covariance / variance
                
                # Calculate Annualized Returns
                # Using mean * TRADING_DAYS_PER_YEAR for consistency with Sharpe Ratio
                scheme_ann_return = scheme_returns.mean() * Constants.TRADING_DAYS_PER_YEAR
                benchmark_ann_return = benchmark_returns.mean() * Constants.TRADING_DAYS_PER_YEAR
                
                # Alpha formula: Alpha = (Rp - Rf) - Beta * (Rm - Rf)
                rf = Constants.RISK_FREE_RATE
                
                # Expected Return (CAPM)
                expected_return = rf + beta * (benchmark_ann_return - rf)
                
                # Jensen's Alpha
                alpha = scheme_ann_return - expected_return
                
                # Convert to percentage
                static_alphas[year] = round(alpha * 100, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_alphas[year] = {
                    'error': f'Error calculating Alpha: {str(e)}'
                }
                
        return {
            'scheme_name': scheme_name,
            'static_alphas': static_alphas
        }
