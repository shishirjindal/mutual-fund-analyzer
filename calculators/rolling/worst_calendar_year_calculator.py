from typing import Dict, Any, Optional
from utils.return_utils import calculate_daily_returns, calculate_downside_deviation
from utils.dataframe_utils import convert_to_dataframe, align_dataframes

class WorstCalendarYearCalculator:
    """Calculates the worst (minimum) return achieved by a fund in any full calendar year."""

    @staticmethod
    def calculate(calendar_returns: Dict[int, Optional[float]]) -> Dict[str, Any]:
        """
        Identifies the worst calendar year and its return from a dictionary of annual returns.
        
        Args:
            calendar_returns: Dictionary where keys are years and values are percentage returns.
            
        Returns:
            Dictionary containing 'worst_return' and 'worst_year'.
        """
        if not calendar_returns:
            return {'worst_return': None, 'worst_year': None, 'error': 'No calendar data available'}

        # Filter out None values and non-digit keys (if any)
        valid_data = {
            year: ret for year, ret in calendar_returns.items() 
            if ret is not None and isinstance(year, (int, str)) and str(year).isdigit()
        }

        if not valid_data:
            return {'worst_return': None, 'worst_year': None, 'error': 'No valid calendar returns found'}

        # Find the year with the minimum return
        worst_year = min(valid_data, key=valid_data.get)
        worst_return = valid_data[worst_year]

        return {
            'worst_return': worst_return,
            'worst_year': int(worst_year)
        }
