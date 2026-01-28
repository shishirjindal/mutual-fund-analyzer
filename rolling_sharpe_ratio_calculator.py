import pandas as pd
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class RollingSharpeRatioCalculator:
    """Calculates rolling Sharpe Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Calculate rolling Sharpe Ratio.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and rolling_sharpe_ratios data, or None if error occurs.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        if df is None or df.empty:
            return None
        
        rolling_sharpe_ratios = []
        
        for config in Constants.ROLLING_SHARPE_RATIO_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for the total years required
            # Calculate start date
            end_date = df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            
            # Filter DataFrame
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data for {total_years} years'
                })
                continue

            # Calculate daily returns
            daily_returns = relevant_df['nav'].pct_change()
            
            # Define window size (trading days)
            window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
            
            if len(daily_returns) < window_size:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate rolling mean and standard deviation
            # ddof=0 for population standard deviation
            rolling_mean = daily_returns.rolling(window=window_size).mean()
            rolling_std = daily_returns.rolling(window=window_size).std(ddof=0)
            
            # Annualize
            # Annualized Return = Daily Mean * Trading Days
            # Annualized Volatility = Daily Std Dev * Sqrt(Trading Days)
            annualized_return = rolling_mean * Constants.TRADING_DAYS_PER_YEAR
            annualized_volatility = rolling_std * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
            
            # Calculate Sharpe Ratio
            # Avoid division by zero
            sharpe_ratios = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
            
            # Drop NaNs and infinite values
            valid_sharpes = sharpe_ratios.replace([float('inf'), -float('inf')], float('nan')).dropna()
            
            if valid_sharpes.empty:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Sharpe Ratios'
                })
            else:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': round(valid_sharpes.median(), Constants.DECIMAL_PLACES),
                    'mean': round(valid_sharpes.mean(), Constants.DECIMAL_PLACES),
                    'positive_share': round((valid_sharpes > 0).mean() * 100, Constants.DECIMAL_PLACES),
                    'percentile_10': round(valid_sharpes.quantile(0.10), Constants.DECIMAL_PLACES),
                    'latest': round(valid_sharpes.iloc[-1], Constants.DECIMAL_PLACES)
                })
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'rolling_sharpe_ratios': rolling_sharpe_ratios
        }
