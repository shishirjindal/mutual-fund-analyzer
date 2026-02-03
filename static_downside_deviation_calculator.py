import pandas as pd
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class StaticDownsideDeviationCalculator:
    """Calculates annualized static downside deviation for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Calculate annualized Static Downside Deviation for periods defined in Constants.STATIC_DOWNSIDE_DEVIATION_YEARS.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and downside_devs data, or None if error occurs.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        if df is None or df.empty:
            return None
        
        downside_devs = {}
        end_date = df.index[-1]
        
        for year in Constants.STATIC_DOWNSIDE_DEVIATION_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            # Filter DataFrame
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                downside_devs[year] = {
                    'error': 'Insufficient daily data points for Downside Deviation calculation'
                }
                continue
            
            try:
                # Calculate daily returns
                daily_returns = relevant_df['nav'].pct_change().dropna()
                
                if daily_returns.empty:
                    downside_devs[year] = {
                        'error': 'Insufficient valid returns for Downside Deviation calculation'
                    }
                    continue

                # Calculate downside deviation of daily returns
                # Target return for downside is 0 (capture absolute downside risk)
                downside_dev_daily = Utils.calculate_downside_deviation(daily_returns, Constants.RISK_FREE_RATE // Constants.TRADING_DAYS_PER_YEAR)
                
                # Annualize downside deviation
                # Annualized Downside Dev = Daily Downside Dev * Sqrt(Trading Days)
                annualized_downside_dev = downside_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR) * 100
                
                downside_devs[year] = round(annualized_downside_dev, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                downside_devs[year] = {
                    'error': f'Error calculating Downside Deviation: {str(e)}'
                }
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'downside_devs': downside_devs
        }
