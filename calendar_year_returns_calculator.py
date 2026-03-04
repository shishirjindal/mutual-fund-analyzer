import pandas as pd
from typing import Dict, Any, List, Optional
from constants import Constants
from utils import Utils

class CalendarYearReturnsCalculator:
    """Calculates calendar year returns for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any], years_to_calculate: List[int]) -> Dict[str, Any]:
        """
        Calculate calendar year returns for the specified years using stored scheme data.
        
        Args:
            scheme_data: Dictionary containing scheme data
            years_to_calculate: List of years to calculate returns for
            
        Returns:
            Dictionary containing calendar year returns.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        
        calendar_returns = {}
        
        if df is None or df.empty:
            for year in years_to_calculate:
                calendar_returns[year] = None
            return calendar_returns
        
        for year in years_to_calculate:
            try:
                # Define the start window (Jan 1-4) for the current year
                start_window_begin = pd.Timestamp(f"{year}-01-01")
                start_window_end = pd.Timestamp(f"{year}-01-04")
                
                # Define the end window (Jan 1-4) for the next year
                end_window_begin = pd.Timestamp(f"{year + 1}-01-01")
                end_window_end = pd.Timestamp(f"{year + 1}-01-04")
                
                # Find initial NAV: first available NAV in the start window
                # We slice the dataframe for the window
                start_data = df.loc[start_window_begin:start_window_end]
                
                if start_data.empty:
                    calendar_returns[year] = None
                    continue
                    
                initial_nav = start_data.iloc[0]['nav']
                
                # Find final NAV: first available NAV in the end window
                end_data = df.loc[end_window_begin:end_window_end]
                
                if end_data.empty:
                    calendar_returns[year] = None
                    continue
                    
                final_nav = end_data.iloc[0]['nav']

                if initial_nav == 0 or final_nav == 0:
                    calendar_returns[year] = None
                    continue

                return_percent = (final_nav - initial_nav) * 100 / initial_nav
                calendar_returns[year] = round(return_percent, Constants.DECIMAL_PLACES)

            except Exception:
                calendar_returns[year] = None
        
        return calendar_returns
