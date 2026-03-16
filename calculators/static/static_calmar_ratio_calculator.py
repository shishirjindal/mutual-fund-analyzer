import pandas as pd
from typing import Dict, Any
from constants.constants import Constants
from utils.return_utils import calculate_daily_returns, calculate_downside_deviation
from utils.dataframe_utils import convert_to_dataframe, align_dataframes

class StaticCalmarRatioCalculator:
    """Calculates Static Calmar Ratio for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Static Calmar Ratio for periods defined in Constants.STATIC_CALMAR_RATIO_YEARS.
        
        Calmar Ratio = Annualized Fund Return / Max Drawdown (Absolute value)
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            Dictionary containing static Calmar Ratio data.
        """
        df = convert_to_dataframe(scheme_data)
        
        static_calmar_ratios = {}
        
        if df is None or df.empty:
            for year in Constants.STATIC_CALMAR_RATIO_YEARS:
                static_calmar_ratios[year] = {'error': 'No data available'}
            return static_calmar_ratios
        end_date = df.index[-1]
        
        for year in Constants.STATIC_CALMAR_RATIO_YEARS:
            start_date = end_date - pd.Timedelta(days=365 * year)
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty or len(relevant_df) < 2:
                static_calmar_ratios[year] = {'error': 'Insufficient data for Calmar Ratio calculation'}
                continue
            
            try:
                # 1. Calculate Annualized Return (following Sharpe/Sortino logic)
                daily_returns = relevant_df['nav'].pct_change().dropna()
                
                if daily_returns.empty or len(daily_returns) < 2:
                    static_calmar_ratios[year] = {'error': 'Insufficient returns for calculation'}
                    continue
                
                mean_daily_return = daily_returns.mean()
                annualized_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR
                
                # 2. Calculate Maximum Drawdown (following StaticDrawdownCalculator logic)
                cummax = relevant_df['nav'].cummax()
                drawdown_series = (relevant_df['nav'] - cummax) / cummax
                max_drawdown = abs(drawdown_series.min()) # Max drawdown as positive value
                
                if max_drawdown == 0:
                     static_calmar_ratios[year] = {'error': 'Max drawdown is zero'}
                     continue

                calmar_ratio = annualized_return / max_drawdown
                static_calmar_ratios[year] = round(calmar_ratio, Constants.DECIMAL_PLACES)
                
            except Exception as e:
                static_calmar_ratios[year] = {'error': f'Error calculating Calmar Ratio: {str(e)}'}
        
        return static_calmar_ratios
