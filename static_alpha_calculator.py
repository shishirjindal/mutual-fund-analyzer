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
            Dictionary containing static Alpha data.
        """
        static_alphas = {}
        
        combined_df = Utils.align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
             for year in Constants.STATIC_ALPHA_YEARS:
                 static_alphas[year] = {'error': 'Data alignment failed or no overlapping data'}
             return static_alphas

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
                
        return static_alphas
