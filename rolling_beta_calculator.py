import pandas as pd
from typing import Dict, Any
from constants import Constants
from utils import Utils

class RollingBetaCalculator:
    """Calculates rolling Beta for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling Beta for configurations defined in Constants.ROLLING_BETA_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with scheme_name and rolling_betas data.
        """
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        rolling_betas = []
        
        combined_df = Utils.align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
            for config in Constants.ROLLING_BETA_MAP:
                rolling_betas.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'Data alignment failed or no overlapping data'
                })
            return {'scheme_name': scheme_name, 'rolling_betas': rolling_betas}
        
        for config in Constants.ROLLING_BETA_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for the total years required
            end_date = combined_df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_betas.append({
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
                rolling_betas.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate rolling covariance and variance
            # ddof=0 for population stats
            scheme_returns = daily_returns['scheme_nav']
            benchmark_returns = daily_returns['benchmark_nav']
            
            rolling_cov = scheme_returns.rolling(window=window_size).cov(benchmark_returns, ddof=0)
            rolling_var = benchmark_returns.rolling(window=window_size).var(ddof=0)
            
            # Beta = Cov / Var
            betas = rolling_cov / rolling_var
            
            # Drop NaNs and infinite values
            valid_betas = betas.replace([float('inf'), -float('inf')], float('nan')).dropna()
            
            if valid_betas.empty:
                rolling_betas.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Beta values'
                })
            else:
                rolling_betas.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': round(valid_betas.median(), Constants.DECIMAL_PLACES),
                    'mean': round(valid_betas.mean(), Constants.DECIMAL_PLACES),
                    'min': round(valid_betas.min(), Constants.DECIMAL_PLACES),
                    'max': round(valid_betas.max(), Constants.DECIMAL_PLACES),
                    'latest': round(valid_betas.iloc[-1], Constants.DECIMAL_PLACES)
                })
        
        return {
            'scheme_name': scheme_name,
            'rolling_betas': rolling_betas
        }
