import numpy as np
import datetime
import math
from constants import Constants
from utils import Utils

class StaticSharpeRatioCalculator:
    """Calculates static Sharpe Ratio for mutual funds."""
    
    @staticmethod
    def calculate(scheme_data):
        """
        Calculate annualized Static Sharpe Ratio.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and static_sharpe_ratios data, or None if error occurs.
        """
        if scheme_data is None:
            return None
        
        historical_data = scheme_data['data']
        static_sharpe_ratios = {}
        
        for year in Constants.STATIC_SHARPE_RATIO_YEARS:
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
                static_sharpe_ratios[year] = {
                    'error': 'Insufficient daily data points for Sharpe Ratio calculation'
                }
                continue
            
            try:
                # Step 2: Calculate mean of daily returns
                mean_daily_return = np.mean(daily_returns)
                
                # Step 3: Annualize return (convert to percentage)
                annualized_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR
                
                # Step 4: Compute population standard deviation of daily returns
                std_dev_daily = np.std(daily_returns, ddof=0)
                
                # Check for zero standard deviation
                if std_dev_daily == 0:
                    static_sharpe_ratios[year] = {
                        'error': 'Standard deviation of daily returns is zero'
                    }
                    continue
                
                # Step 5: Calculate annualized volatility (convert to percentage)
                annualized_volatility = std_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                # Step 6: Apply formula: Sharpe = (Annualized return - Risk-free rate) / Annualized volatility
                sharpe_ratio = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
                
                static_sharpe_ratios[year] = round(sharpe_ratio, Constants.DECIMAL_PLACES)
                
            except (ValueError, ZeroDivisionError) as e:
                static_sharpe_ratios[year] = {
                    'error': f'Error calculating Sharpe Ratio: {e}'
                }
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'static_sharpe_ratios': static_sharpe_ratios
        }
