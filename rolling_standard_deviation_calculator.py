import pandas as pd
import datetime
import math
from typing import Dict, List, Optional, Any
from constants import Constants
from utils import Utils

class RollingStandardDeviationCalculator:
    """Calculates rolling Standard Deviation (Volatility) for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling Standard Deviation for configurations defined in Constants.ROLLING_STANDARD_DEVIATION_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data with 'data' key holding list of NAVs
            
        Returns:
            List of dictionaries containing rolling Standard Deviation stats.
        """
        if 'data' not in scheme_data or not scheme_data['data']:
            rolling_std_devs = []
            for config in Constants.ROLLING_STANDARD_DEVIATION_MAP:
                rolling_std_devs.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'No data available'
                })
            return rolling_std_devs
        
        historical_data = scheme_data['data']
        rolling_std_devs = []
        
        for config in Constants.ROLLING_STANDARD_DEVIATION_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            try:
                # Calculate start date for data filtering
                # Assumes data is sorted new-to-old, so index 0 is latest
                end_date = datetime.datetime.strptime(historical_data[0]['date'], Constants.DATE_FORMAT)
                start_date = end_date - datetime.timedelta(days=365 * total_years)
                
                # Filter data to get the required history range
                relevant_data = [
                    d for d in historical_data
                    if datetime.datetime.strptime(d['date'], Constants.DATE_FORMAT) >= start_date
                ]
                
                # Reverse to chronological order (Oldest -> Newest) for returns calculation
                chronological_data = list(reversed(relevant_data))
                
                # Calculate daily returns using Utils (handles NAV validation and 0 checks)
                daily_returns = Utils.calculate_daily_returns(chronological_data)
                
                # Define window size (trading days)
                window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
                
                if len(daily_returns) < window_size:
                    rolling_std_devs.append({
                        'total_data': total_years,
                        'rolling_window': window_years,
                        'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                    })
                    continue
                
                # Create Pandas Series from daily returns
                daily_returns_series = pd.Series(daily_returns)
                
                # Calculate rolling standard deviation
                # using ddof=0 for population standard deviation to match previous implementation logic
                rolling_std = daily_returns_series.rolling(window=window_size).std(ddof=0)
                
                # Annualize volatility
                # Annualized Volatility = Daily Std Dev * sqrt(Trading Days) * 100 (for percentage)
                annualized_rolling_std = rolling_std * math.sqrt(Constants.TRADING_DAYS_PER_YEAR) * 100
                
                # Drop NaN values (first window_size - 1 elements)
                valid_std_devs = annualized_rolling_std.dropna()
                
                if valid_std_devs.empty:
                    rolling_std_devs.append({
                        'total_data': total_years,
                        'rolling_window': window_years,
                        'error': 'Could not calculate valid Standard Deviations'
                    })
                else:
                    min_val = round(valid_std_devs.min(), Constants.DECIMAL_PLACES)
                    max_val = round(valid_std_devs.max(), Constants.DECIMAL_PLACES)
                    mean_val = round(valid_std_devs.mean(), Constants.DECIMAL_PLACES)
                    median_val = round(valid_std_devs.median(), Constants.DECIMAL_PLACES)
                    latest_val = round(valid_std_devs.iloc[-1], Constants.DECIMAL_PLACES)

                    rolling_std_devs.append({
                        'total_data': total_years,
                        'rolling_window': window_years,
                        'min': min_val,
                        'max': max_val,
                        'mean': mean_val,
                        'median': median_val,
                        'latest': latest_val
                    })
            except (ValueError, IndexError) as e:
                # Handle potential date parsing errors or data issues gracefully
                rolling_std_devs.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Calculation error: {str(e)}'
                })
                continue
        
        return rolling_std_devs
