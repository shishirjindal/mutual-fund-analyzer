import pandas as pd
import numpy as np
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class RollingSortinoRatioCalculator:
    """Calculates rolling Sortino Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Calculate rolling Sortino Ratio for configurations defined in Constants.ROLLING_SORTINO_RATIO_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and rolling_sortino_ratios data, or None if error occurs.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        if df is None or df.empty:
            return None
        
        rolling_sortino_ratios = []
        
        for config in Constants.ROLLING_SORTINO_RATIO_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for the total years required
            end_date = df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            
            # Filter DataFrame
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_sortino_ratios.append({
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
                rolling_sortino_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate rolling mean return
            rolling_mean = daily_returns.rolling(window=window_size).mean()
            
            # Calculate rolling downside deviation efficiently
            # 1. Filter negative returns (underperformance relative to 0)
            downside_returns = daily_returns.clip(upper=0)
            
            # 2. Square the negative returns
            downside_sq = downside_returns ** 2
            
            # 3. Calculate rolling mean of squares
            rolling_downside_mean_sq = downside_sq.rolling(window=window_size).mean()
            
            # 4. Calculate rolling downside deviation (daily)
            rolling_downside_dev = np.sqrt(rolling_downside_mean_sq)
            
            # Annualize
            annualized_return = rolling_mean * Constants.TRADING_DAYS_PER_YEAR
            annualized_downside_dev = rolling_downside_dev * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
            
            # Calculate Sortino Ratio
            # Avoid division by zero
            sortino_ratios = (annualized_return - Constants.RISK_FREE_RATE) / annualized_downside_dev
            
            # Drop NaNs and infinite values
            valid_sortinos = sortino_ratios.replace([float('inf'), -float('inf')], float('nan')).dropna()
            
            if valid_sortinos.empty:
                rolling_sortino_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Sortino Ratios'
                })
            else:
                rolling_sortino_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': round(valid_sortinos.median(), Constants.DECIMAL_PLACES),
                    'mean': round(valid_sortinos.mean(), Constants.DECIMAL_PLACES),
                    'positive_share': round((valid_sortinos > 0).mean() * 100, Constants.DECIMAL_PLACES),
                    'percentile_10': round(valid_sortinos.quantile(0.10), Constants.DECIMAL_PLACES),
                    'latest': round(valid_sortinos.iloc[-1], Constants.DECIMAL_PLACES)
                })
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'rolling_sortino_ratios': rolling_sortino_ratios
        }
