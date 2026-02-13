import pandas as pd
import math
from typing import Dict, Any, Optional
from constants import Constants
from utils import Utils

class InformationRatioCalculator:
    """Calculates Information Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Information Ratio for periods defined in Constants.INFORMATION_RATIO_YEARS.
        
        IR = (Rp - Rm) / Tracking Error
        Tracking Error = StdDev(Rp - Rm) * sqrt(252)
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary with information_ratios data.
        """
        df_scheme = Utils.convert_to_dataframe(scheme_data)
        df_benchmark = Utils.convert_to_dataframe(benchmark_data)
        
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        information_ratios = {}
        
        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
             for year in Constants.INFORMATION_RATIO_YEARS:
                 information_ratios[year] = {'error': 'Data conversion failed or empty data'}
             return {'scheme_name': scheme_name, 'information_ratios': information_ratios}
        
        # Align dataframes on dates
        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'), 
            df_benchmark['nav'].rename('benchmark_nav'), 
            left_index=True, 
            right_index=True, 
            how='inner'
        )
        
        if combined_df.empty:
             for year in Constants.INFORMATION_RATIO_YEARS:
                information_ratios[year] = {'error': 'No overlapping data with benchmark'}
             return {'scheme_name': scheme_name, 'information_ratios': information_ratios}

        end_date = combined_df.index[-1]

        for year in Constants.INFORMATION_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                information_ratios[year] = {
                    'error': 'Insufficient overlapping data for Information Ratio calculation'
                }
                continue
                
            try:
                # Calculate daily returns
                daily_returns = relevant_df.pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    information_ratios[year] = {
                        'error': 'Insufficient valid returns for Information Ratio calculation'
                    }
                    continue

                scheme_returns = daily_returns['scheme_nav']
                benchmark_returns = daily_returns['benchmark_nav']

                # Active Returns (Daily)
                active_returns_daily = scheme_returns - benchmark_returns
                
                # Annualized Active Return (Numerator)
                # Mean of daily active returns * 252
                annualized_active_return = active_returns_daily.mean() * Constants.TRADING_DAYS_PER_YEAR
                
                # Tracking Error (Denominator)
                # Std Dev of daily active returns * Sqrt(252)
                # Using ddof=0 for population std dev (consistent with other calculators)
                tracking_error = active_returns_daily.std(ddof=0) * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                if tracking_error == 0:
                     information_ratios[year] = {'error': 'Tracking Error is zero'}
                     continue

                ir = annualized_active_return / tracking_error
                information_ratios[year] = round(ir, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                information_ratios[year] = {
                    'error': f'Error calculating Information Ratio: {str(e)}'
                }
                
        return {
            'scheme_name': scheme_name,
            'information_ratios': information_ratios
        }
