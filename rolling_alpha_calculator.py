import pandas as pd
import math
from typing import Dict, Any
from constants import Constants
from utils import Utils

class RollingAlphaCalculator:
    """Calculates rolling Jensen's Alpha for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling Alpha for configurations defined in Constants.ROLLING_ALPHA_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with scheme_name and rolling_alphas data.
        """
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        df_scheme = Utils.convert_to_dataframe(scheme_data)
        df_benchmark = Utils.convert_to_dataframe(benchmark_data)
        
        rolling_alphas = []
        
        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
            for config in Constants.ROLLING_ALPHA_MAP:
                rolling_alphas.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'No data available'
                })
            return {'scheme_name': scheme_name, 'rolling_alphas': rolling_alphas}
        
        # Align dataframes
        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'), 
            df_benchmark['nav'].rename('benchmark_nav'), 
            left_index=True, 
            right_index=True, 
            how='inner'
        )
        
        if combined_df.empty:
            for config in Constants.ROLLING_ALPHA_MAP:
                rolling_alphas.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'No overlapping data with benchmark'
                })
            return {'scheme_name': scheme_name, 'rolling_alphas': rolling_alphas}
        
        for config in Constants.ROLLING_ALPHA_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for the total years required
            end_date = combined_df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_alphas.append({
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
                rolling_alphas.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate rolling returns and beta
            scheme_returns = daily_returns['scheme_nav']
            benchmark_returns = daily_returns['benchmark_nav']
            
            rolling_mean_scheme = scheme_returns.rolling(window=window_size).mean()
            rolling_mean_benchmark = benchmark_returns.rolling(window=window_size).mean()
            
            rolling_cov = scheme_returns.rolling(window=window_size).cov(benchmark_returns, ddof=0)
            rolling_var = benchmark_returns.rolling(window=window_size).var(ddof=0)
            
            rolling_beta = rolling_cov / rolling_var
            
            # Annualize returns
            ann_fund_return = rolling_mean_scheme * Constants.TRADING_DAYS_PER_YEAR
            ann_bench_return = rolling_mean_benchmark * Constants.TRADING_DAYS_PER_YEAR
            
            # Jensen's Alpha: Alpha = (Rp - Rf) - Beta * (Rm - Rf)
            rf = Constants.RISK_FREE_RATE
            expected_return = rf + rolling_beta * (ann_bench_return - rf)
            alphas = ann_fund_return - expected_return
            
            # Convert to percentage
            alphas_pct = alphas * 100
            
            # Drop NaNs and infinite values
            valid_alphas = alphas_pct.replace([float('inf'), -float('inf')], float('nan')).dropna()
            
            if valid_alphas.empty:
                rolling_alphas.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Alpha values'
                })
            else:
                rolling_alphas.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': round(valid_alphas.median(), Constants.DECIMAL_PLACES),
                    'mean': round(valid_alphas.mean(), Constants.DECIMAL_PLACES),
                    'min': round(valid_alphas.min(), Constants.DECIMAL_PLACES),
                    'max': round(valid_alphas.max(), Constants.DECIMAL_PLACES),
                    'latest': round(valid_alphas.iloc[-1], Constants.DECIMAL_PLACES)
                })
        
        return {
            'scheme_name': scheme_name,
            'rolling_alphas': rolling_alphas
        }
