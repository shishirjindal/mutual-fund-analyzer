import pandas as pd
from typing import Dict, Any
from constants.constants import Constants
from utils.return_utils import calculate_daily_returns, calculate_downside_deviation
from utils.dataframe_utils import convert_to_dataframe, align_dataframes

class StaticTreynorRatioCalculator:
    """Calculates Static Treynor Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Treynor Ratio for periods defined in Constants.STATIC_TREYNOR_RATIO_YEARS.
        
        Treynor Ratio = (Annualized Fund Return - Risk Free Rate) / Fund Beta
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Dictionary containing static Treynor Ratio data.
        """
        static_treynor_ratios = {}
        
        combined_df = align_dataframes(scheme_data, benchmark_data)
        
        if combined_df is None:
             for year in Constants.STATIC_TREYNOR_RATIO_YEARS:
                 static_treynor_ratios[year] = {'error': 'Data alignment failed or no overlapping data'}
             return static_treynor_ratios

        end_date = combined_df.index[-1]

        for year in Constants.STATIC_TREYNOR_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            
            relevant_df = combined_df[combined_df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_treynor_ratios[year] = {
                    'error': 'Insufficient overlapping data for Treynor Ratio calculation'
                }
                continue
                
            try:
                # Calculate daily returns
                daily_returns = relevant_df.pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_treynor_ratios[year] = {
                        'error': 'Insufficient valid returns for Treynor Ratio calculation'
                    }
                    continue
                
                scheme_returns = daily_returns['scheme_nav']
                benchmark_returns = daily_returns['benchmark_nav']
                
                # Annualized Fund Return
                mean_daily_return = scheme_returns.mean()
                annualized_fund_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR
                
                # Fund Beta
                covariance = scheme_returns.cov(benchmark_returns)
                variance = benchmark_returns.var()
                
                if variance == 0:
                     static_treynor_ratios[year] = {'error': 'Benchmark variance is zero'}
                     continue

                beta = covariance / variance
                
                if beta == 0:
                     static_treynor_ratios[year] = {'error': 'Beta is zero'}
                     continue

                treynor_ratio = (annualized_fund_return - Constants.RISK_FREE_RATE) / beta
                static_treynor_ratios[year] = round(treynor_ratio, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_treynor_ratios[year] = {
                    'error': f'Error calculating Treynor Ratio: {str(e)}'
                }
                
        return static_treynor_ratios
