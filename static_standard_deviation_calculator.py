import numpy as np
import datetime
import math
from constants import Constants
from utils import Utils

class StaticStandardDeviationCalculator:
    """Calculates annualized static standard deviation (volatility) for mutual funds."""
    
    @staticmethod
    def calculate(scheme_data):
        """
        Calculate annualized Static Standard Deviation for 1, 3, and 5 years.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and std_devs data, or None if error occurs.
        """
        if scheme_data is None:
            return None
        
        historical_data = scheme_data['data']
        std_devs = {}
        
        # We use the STATIC_STANDARD_DEVIATION_YEARS constant
        for year in Constants.STATIC_STANDARD_DEVIATION_YEARS:
            end_date = datetime.datetime.strptime(historical_data[0]['date'], Constants.DATE_FORMAT)
            start_date = end_date - datetime.timedelta(days=365 * year)
            
            # Use only the last N years of data (most recent data)
            recent_data = [
                d for d in historical_data
                if datetime.datetime.strptime(d['date'], Constants.DATE_FORMAT) >= start_date
            ]
            chronological_data = list(reversed(recent_data))  # Reverse to get oldest first
            
            # Step 1: Calculate daily returns
            daily_returns = Utils.calculate_daily_returns(chronological_data)
            
            # Need at least 2 data points to calculate standard deviation
            if len(daily_returns) < 2:
                std_devs[year] = {
                    'error': 'Insufficient daily data points for Standard Deviation calculation'
                }
                continue
            
            try:
                # Step 2: Compute population standard deviation of daily returns
                std_dev_daily = np.std(daily_returns, ddof=0)
                
                # Step 3: Calculate annualized volatility (standard deviation)
                # Annualized Volatility = Daily Std Dev * sqrt(Trading Days) * 100 (for percentage)
                annualized_volatility = std_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR) * 100
                
                std_devs[year] = round(annualized_volatility, Constants.DECIMAL_PLACES)
                
            except (ValueError, ZeroDivisionError) as e:
                std_devs[year] = {
                    'error': f'Error calculating Standard Deviation: {e}'
                }
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'std_devs': std_devs
        }
