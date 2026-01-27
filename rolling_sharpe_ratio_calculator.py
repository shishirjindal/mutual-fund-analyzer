import numpy as np
import datetime
import math
from constants import Constants
from utils import Utils

class RollingSharpeRatioCalculator:
    """Calculates rolling Sharpe Ratio for mutual funds."""
    
    @staticmethod
    def calculate(scheme_data):
        """
        Calculate rolling Sharpe Ratio.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and rolling_sharpe_ratios data, or None if error occurs.
        """
        if scheme_data is None:
            return None
        
        historical_data = scheme_data['data']
        rolling_sharpe_ratios = []
        
        for config in Constants.ROLLING_SHARPE_RATIO_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Calculate start date for data filtering
            end_date = datetime.datetime.strptime(historical_data[0]['date'], Constants.DATE_FORMAT)
            start_date = end_date - datetime.timedelta(days=365 * total_years)
            
            # Filter data
            relevant_data = [
                d for d in historical_data
                if datetime.datetime.strptime(d['date'], Constants.DATE_FORMAT) >= start_date
            ]
            chronological_data = list(reversed(relevant_data))
            
            # Calculate daily returns
            daily_returns = Utils.calculate_daily_returns(chronological_data)
            
            # Define window size (trading days)
            window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
            
            if len(daily_returns) < window_size:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate rolling Sharpe Ratios
            window_sharpes = []
            for i in range(len(daily_returns) - window_size + 1):
                window = daily_returns[i : i + window_size]
                
                if not window:
                    continue
                
                # Check for zero variance to avoid division by zero
                std_dev = np.std(window, ddof=0)
                if std_dev == 0:
                    continue
                
                mean_return = np.mean(window)
                annualized_return = mean_return * Constants.TRADING_DAYS_PER_YEAR
                annualized_volatility = std_dev * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                sharpe = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
                window_sharpes.append(sharpe)
            
            if not window_sharpes:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Sharpe Ratios'
                })
            else:
                median_val = round(np.median(window_sharpes), Constants.DECIMAL_PLACES)
                mean_val = round(np.mean(window_sharpes), Constants.DECIMAL_PLACES)
                percentile_10_val = round(np.percentile(window_sharpes, 10), Constants.DECIMAL_PLACES)
                latest_val = round(window_sharpes[-1], Constants.DECIMAL_PLACES)

                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': median_val,
                    'mean': mean_val,
                    'positive_share': round((len([s for s in window_sharpes if s > 0]) / len(window_sharpes)) * 100, Constants.DECIMAL_PLACES),
                    'percentile_10': percentile_10_val,
                    'latest': latest_val
                })
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'rolling_sharpe_ratios': rolling_sharpe_ratios
        }
