import pandas as pd
import math
from typing import Dict, Any
from constants import Constants
from utils import Utils


class StaticInformationRatioCalculator:
    """Calculates Static Information Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Information Ratio for periods defined in Constants.STATIC_INFORMATION_RATIO_YEARS.
        
        IR = (Rp - Rm) / Tracking Error
        Tracking Error = StdDev(Rp - Rm)
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary containing static Information Ratio data.
        """
        static_information_ratios = {}
        
        combined_df = Utils.align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
            for year in Constants.STATIC_INFORMATION_RATIO_YEARS:
                static_information_ratios[year] = {'error': 'Data alignment failed or no overlapping data'}
            return static_information_ratios

        end_date = combined_df.index[-1]

        for year in Constants.STATIC_INFORMATION_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_information_ratios[year] = {
                    'error': 'Insufficient overlapping data for Information Ratio calculation'
                }
                continue
                
            try:
                daily_returns = relevant_df.pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_information_ratios[year] = {
                        'error': 'Insufficient valid returns for Information Ratio calculation'
                    }
                    continue

                scheme_returns = daily_returns['scheme_nav']
                benchmark_returns = daily_returns['benchmark_nav']

                active_returns_daily = scheme_returns - benchmark_returns
                
                annualized_active_return = active_returns_daily.mean() * Constants.TRADING_DAYS_PER_YEAR
                
                tracking_error = active_returns_daily.std(ddof=0)

                annualized_tracking_error = tracking_error * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                if annualized_tracking_error == 0:
                    static_information_ratios[year] = {'error': 'Annualized Tracking Error is zero'}
                    continue

                ir = annualized_active_return / annualized_tracking_error
                static_information_ratios[year] = round(ir, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_information_ratios[year] = {
                    'error': f'Error calculating Information Ratio: {str(e)}'
                }
                
        return static_information_ratios
