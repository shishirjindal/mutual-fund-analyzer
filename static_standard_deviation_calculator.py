import pandas as pd
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class StaticStandardDeviationCalculator:
    """Calculates annualized static standard deviation (volatility) for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Calculate annualized Static Standard Deviation for 1, 3, and 5 years.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and std_devs data, or None if error occurs.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        if df is None or df.empty:
            return None
        
        std_devs = {}
        end_date = df.index[-1]
        
        for year in Constants.STATIC_STANDARD_DEVIATION_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            # Filter DataFrame
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                std_devs[year] = {
                    'error': 'Insufficient daily data points for Standard Deviation calculation'
                }
                continue
            
            try:
                # Calculate daily returns
                daily_returns = relevant_df['nav'].pct_change().dropna()
                
                if daily_returns.empty:
                    std_devs[year] = {
                        'error': 'Insufficient valid returns for Standard Deviation calculation'
                    }
                    continue

                # Calculate population standard deviation of daily returns
                # We use ddof=0 for population standard deviation (default is ddof=1 for sample)
                std_dev_daily = daily_returns.std(ddof=0)
                
                # Annualize volatility
                # Annualized Volatility = Daily Std Dev * Sqrt(Trading Days)
                annualized_volatility = std_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR) * 100
                
                std_devs[year] = round(annualized_volatility, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                std_devs[year] = {
                    'error': f'Error calculating Standard Deviation: {str(e)}'
                }
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'std_devs': std_devs
        }
