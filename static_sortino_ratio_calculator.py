import pandas as pd
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class StaticSortinoRatioCalculator:
    """Calculates static Sortino Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate annualized Static Sortino Ratio for periods defined in Constants.STATIC_SORTINO_RATIO_YEARS.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary containing static Sortino Ratio data.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        
        static_sortino_ratios = {}
        
        if df is None or df.empty:
            for year in Constants.STATIC_SORTINO_RATIO_YEARS:
                static_sortino_ratios[year] = {'error': 'No data available'}
            return static_sortino_ratios
        end_date = df.index[-1]
        
        for year in Constants.STATIC_SORTINO_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            # Filter DataFrame
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_sortino_ratios[year] = {
                    'error': 'Insufficient daily data points for Sortino Ratio calculation'
                }
                continue
            
            try:
                # Calculate daily returns
                daily_returns = relevant_df['nav'].pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_sortino_ratios[year] = {
                        'error': 'Insufficient valid returns for Sortino Ratio calculation'
                    }
                    continue

                # Calculate mean of daily returns
                mean_daily_return = daily_returns.mean()
                
                # Annualize return (arithmetic mean * days, consistent with Sharpe calculation)
                annualized_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR
                
                # Calculate Downside Deviation
                # Target return for downside is 0 (standard Sortino) or risk-free rate.
                # Here we use 0 to capture absolute downside risk.
                downside_dev_daily = Utils.calculate_downside_deviation(daily_returns, 0.0)
                
                if downside_dev_daily == 0:
                    static_sortino_ratios[year] = {
                        'error': 'Downside deviation is zero (no negative returns)'
                    }
                    continue
                
                # Annualize downside deviation
                annualized_downside_dev = downside_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                # Calculate Sortino Ratio
                # Sortino Ratio = (Annualized Return - Risk Free Rate) / Annualized Downside Deviation
                sortino_ratio = (annualized_return - Constants.RISK_FREE_RATE) / annualized_downside_dev
                
                static_sortino_ratios[year] = round(sortino_ratio, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_sortino_ratios[year] = {
                    'error': f'Error calculating Sortino Ratio: {str(e)}'
                }
        
        return static_sortino_ratios
