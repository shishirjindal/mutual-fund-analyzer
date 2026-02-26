from typing import List, Dict, Any, Optional
import pandas as pd
import math
from constants import Constants

class Utils:
    """
    Utility class for financial calculations and helper methods.
    
    Provides static methods for common financial formulas used across the application.
    """
    @staticmethod
    def calculate_cagr(absolute_return_percent: float, years: float) -> float:
        """
        Calculate CAGR (Compound Annual Growth Rate) from absolute return percentage.
        
        Args:
            absolute_return_percent: Absolute return as a percentage (e.g., 50 for 50%)
            years: Number of years for compounding
        
        Returns:
            CAGR as a percentage
        """
        if years == 0:
            return 0.0
        # Formula: ((Absolute Return % / 100 + 1)^(1 / Years) - 1) * 100
        return (pow((1.0 * absolute_return_percent) / 100 + 1, 1.0 / years) - 1) * 100

    @staticmethod
    def calculate_daily_returns(chronological_data: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate daily returns from chronological NAV data.
        
        Robustly handles cases with insufficient data by returning an empty list.
        Skips invalid entries (zero NAVs, non-numeric values).
        
        Args:
            chronological_data: List of dictionaries containing 'nav' key, sorted by date (oldest first)
            
        Returns:
            List of daily returns (floats). Returns empty list if input has fewer than 2 entries.
        """
        if len(chronological_data) < 2:
            return []
            
        daily_returns = []
        for i in range(len(chronological_data) - 1):
            try:
                nav_yesterday = float(chronological_data[i]['nav'])
                nav_today = float(chronological_data[i + 1]['nav'])
                
                if nav_yesterday == 0 or nav_today == 0:
                    continue
                
                # Calculate daily return
                daily_return = (nav_today - nav_yesterday) / nav_yesterday
                daily_returns.append(daily_return)
                
            except (ValueError, KeyError, IndexError, ZeroDivisionError):
                continue
        return daily_returns

    @staticmethod
    def convert_to_dataframe(scheme_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Convert scheme data dictionary to a Pandas DataFrame.
        
        Args:
            scheme_data: Dictionary containing scheme data with 'data' key
            
        Returns:
            Pandas DataFrame with DateTime index and 'nav' column (sorted chronologically),
            or None if data is invalid.
        """
        if scheme_data is None or 'data' not in scheme_data or not scheme_data['data']:
            return None
            
        try:
            df = pd.DataFrame(scheme_data['data'])
            
            # Ensure required columns exist
            if 'date' not in df.columns or 'nav' not in df.columns:
                return None
                
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'], format=Constants.DATE_FORMAT)
            
            # Convert NAV to numeric, coercing errors to NaN
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            
            # Set date as index
            df.set_index('date', inplace=True)
            
            # Sort chronologically (Oldest -> Newest)
            df.sort_index(ascending=True, inplace=True)
            
            # Drop rows with NaN NAV
            df.dropna(subset=['nav'], inplace=True)
            
            # Drop rows with 0 NAV (to prevent division by zero in calculations)
            df = df[df['nav'] != 0]
            
            return df
        except (ValueError, KeyError, TypeError, Exception):
            return None

    @staticmethod
    def align_dataframes(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Align scheme and benchmark DataFrames by date using an inner join.
        
        Args:
            scheme_data: Dictionary containing scheme data
            benchmark_data: Dictionary containing benchmark data
            
        Returns:
            Pandas DataFrame with DateTime index and 'scheme_nav', 'benchmark_nav' columns,
            or None if alignment fails or results in empty DataFrame.
        """
        df_scheme = Utils.convert_to_dataframe(scheme_data)
        df_benchmark = Utils.convert_to_dataframe(benchmark_data)
        
        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
            return None
            
        # Align dataframes on dates using inner join
        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'), 
            df_benchmark['nav'].rename('benchmark_nav'), 
            left_index=True, 
            right_index=True, 
            how='inner'
        )
        
        if combined_df.empty:
            return None
            
        return combined_df

    @staticmethod
    def calculate_downside_deviation(returns: pd.Series, target: float = 0.0) -> float:
        """
        Calculate downside deviation (risk).
        
        Calculated as the Root Mean Square of the underperformance (returns below target).
        Formula: sqrt(mean(min(0, return - target)^2))
        
        Args:
            returns: Series of daily returns
            target: Risk free rate per day (default 0.0)
            
        Returns:
            Downside deviation (float)
        """
        # Calculate downside difference
        downside_diff = returns - target
        
        # Keep only negative values (underperformance), replace positive with 0
        downside_diff = downside_diff.clip(upper=0)
        
        # Square the differences
        downside_sq = downside_diff ** 2
        
        # Mean of squares (using full population N)
        mean_sq = downside_sq.mean()
        
        # Square root
        return math.sqrt(mean_sq)
