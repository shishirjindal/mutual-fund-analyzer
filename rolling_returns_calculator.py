import numpy as np
from constants import Constants
from utils import Utils

class RollingReturnsCalculator:
    """Calculates rolling returns for mutual funds."""
    
    @staticmethod
    def calculate(scheme_data):
        """
        Calculate rolling returns for 1, 3 and 5 years using stored scheme data.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary with scheme_name and rolling_returns data, or None if error occurs.
        """
        if scheme_data is None:
            return None
        
        historical_data = scheme_data['data']
        rolling_returns = {}
        
        for year in Constants.ROLLING_YEARS:
            cagr_values = []
            required_data_points = year * Constants.TRADING_DAYS_PER_YEAR + 1
            
            if len(historical_data) < 2 * required_data_points:
                rolling_returns[year] = {
                    'error': f'Insufficient data (need {required_data_points}, have {len(historical_data)})'
                }
                continue
            
            # Calculate rolling returns.
            # We start from the end of the data and move backwards.
            for start_index in range(len(historical_data) - required_data_points):
                try:
                    initial_index = start_index + year * Constants.TRADING_DAYS_PER_YEAR
                    initial_nav = float(historical_data[initial_index]['nav'])
                    final_nav = float(historical_data[start_index]['nav'])
                    
                    if initial_nav == 0 or final_nav == 0:
                        continue
                    
                    absolute_return = (final_nav - initial_nav) * 100 / initial_nav
                    cagr = Utils.calculate_cagr(absolute_return, year)
                    cagr_values.append(cagr)
                    
                except (ValueError, KeyError, IndexError, ZeroDivisionError):
                    continue
                except Exception:
                    continue
            
            if len(cagr_values) == 0:
                rolling_returns[year] = {'error': 'No valid data points'}
            else:
                rolling_returns[year] = {
                    'min': round(np.min(cagr_values), Constants.DECIMAL_PLACES),
                    'avg': round(np.mean(cagr_values), Constants.DECIMAL_PLACES),
                    'max': round(np.max(cagr_values), Constants.DECIMAL_PLACES)
                }
        
        return {
            'scheme_name': scheme_data['scheme_name'],
            'rolling_returns': rolling_returns
        }
