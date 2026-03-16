import datetime
from typing import Dict, Any, Optional


class WorstCalendarYearCalculator:
    """Calculates the worst (minimum) return achieved by a fund in any full calendar year."""

    _MIN_MONTHS = 8  # exclude current year unless at least this many months have elapsed

    @staticmethod
    def calculate(calendar_returns: Dict[int, Optional[float]]) -> Dict[str, Any]:
        if not calendar_returns:
            return {'worst_return': None, 'worst_year': None, 'error': 'No calendar data available'}

        current_year = datetime.date.today().year
        current_month = datetime.date.today().month

        valid_data = {}
        for year, ret in calendar_returns.items():
            if ret is None:
                continue
            if not isinstance(year, (int, str)) or not str(year).isdigit():
                continue
            # Skip current year if fewer than 8 months have elapsed
            if int(year) == current_year and current_month < WorstCalendarYearCalculator._MIN_MONTHS:
                continue
            valid_data[int(year)] = ret

        if not valid_data:
            return {'worst_return': None, 'worst_year': None, 'error': 'No valid calendar returns found'}

        worst_year = min(valid_data, key=valid_data.get)
        return {
            'worst_return': valid_data[worst_year],
            'worst_year': worst_year,
        }
