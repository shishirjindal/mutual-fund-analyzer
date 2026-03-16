import math
from typing import List, Dict, Any
import pandas as pd


class ReturnUtils:
    """Utility methods for return and deviation calculations."""

    @staticmethod
    def calculate_cagr(absolute_return_percent: float, years: float) -> float:
        """Calculate CAGR from absolute return percentage."""
        if years == 0:
            return 0.0
        return (pow((1.0 * absolute_return_percent) / 100 + 1, 1.0 / years) - 1) * 100

    @staticmethod
    def calculate_daily_returns(chronological_data: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate daily returns from chronological NAV data.
        Skips invalid entries (zero NAVs, non-numeric values).
        Returns empty list if fewer than 2 entries.
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
                daily_returns.append((nav_today - nav_yesterday) / nav_yesterday)
            except (ValueError, KeyError, IndexError, ZeroDivisionError):
                continue
        return daily_returns

    @staticmethod
    def calculate_downside_deviation(returns: pd.Series, target: float = 0.0) -> float:
        """Calculate downside deviation (Root Mean Square of returns below target)."""
        downside_diff = (returns - target).clip(upper=0)
        return math.sqrt((downside_diff ** 2).mean())


# Module-level aliases so calculators can call the functions directly
calculate_cagr = ReturnUtils.calculate_cagr
calculate_daily_returns = ReturnUtils.calculate_daily_returns
calculate_downside_deviation = ReturnUtils.calculate_downside_deviation
