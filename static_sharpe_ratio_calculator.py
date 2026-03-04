import pandas as pd
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class StaticSharpeRatioCalculator:
    """Calculates static Sharpe Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate annualized Static Sharpe Ratio for periods defined in Constants.STATIC_SHARPE_RATIO_YEARS.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary containing static Sharpe Ratio data.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        
        static_sharpe_ratios = {}
        
        if df is None or df.empty:
            for year in Constants.STATIC_SHARPE_RATIO_YEARS:
                static_sharpe_ratios[year] = {'error': 'No data available'}
            return static_sharpe_ratios
        end_date = df.index[-1]
        
        for year in Constants.STATIC_SHARPE_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            # Filter DataFrame
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_sharpe_ratios[year] = {
                    'error': 'Insufficient daily data points for Sharpe Ratio calculation'
                }
                continue
            
            try:
                # Calculate daily returns
                daily_returns = relevant_df['nav'].pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_sharpe_ratios[year] = {
                        'error': 'Insufficient valid returns for Sharpe Ratio calculation'
                    }
                    continue

                # Calculate mean of daily returns
                mean_daily_return = daily_returns.mean()
                
                # Annualize return (convert to percentage)
                # We multiply by trading days to get annualized return from daily average.
                # Note: This approximation (arithmetic mean * days) is standard for Sharpe Ratio,
                # even though CAGR is preferred for returns.
                annualized_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR
                
                # Calculate population standard deviation of daily returns
                # We use ddof=0 for population standard deviation
                std_dev_daily = daily_returns.std(ddof=0)
                
                if std_dev_daily == 0:
                    static_sharpe_ratios[year] = {
                        'error': 'Standard deviation of daily returns is zero'
                    }
                    continue
                
                # Annualize volatility
                annualized_volatility = std_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                # Calculate Sharpe Ratio
                sharpe_ratio = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
                
                static_sharpe_ratios[year] = round(sharpe_ratio, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_sharpe_ratios[year] = {
                    'error': f'Error calculating Sharpe Ratio: {str(e)}'
                }
        
        return static_sharpe_ratios
