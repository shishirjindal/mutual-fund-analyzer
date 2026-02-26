#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-

"""
Mutual Fund Analyzer

This script calculates various types of returns and risk metrics for mutual fund schemes:
- Rolling returns: CAGR (Compound Annual Growth Rate) over rolling periods (1, 3, 5 years)
- Calendar year returns: Returns for the last 5 calendar years
- Static Sharpe Ratio: Risk-adjusted return metric over fixed periods
- Rolling Sharpe Ratio: Risk-adjusted return metric over rolling windows
"""

import sys
import datetime
from typing import List, Dict, Any, Optional
from constants import Constants
from data_fetcher import DataFetcher
from rolling_returns_calculator import RollingReturnsCalculator
from calendar_year_returns_calculator import CalendarYearReturnsCalculator
from static_standard_deviation_calculator import StaticStandardDeviationCalculator
from static_downside_deviation_calculator import StaticDownsideDeviationCalculator
from rolling_standard_deviation_calculator import RollingStandardDeviationCalculator
from static_sharpe_ratio_calculator import StaticSharpeRatioCalculator
from rolling_sharpe_ratio_calculator import RollingSharpeRatioCalculator
from static_sortino_ratio_calculator import StaticSortinoRatioCalculator
from rolling_sortino_ratio_calculator import RollingSortinoRatioCalculator
from static_drawdown_calculator import StaticDrawdownCalculator
from static_alpha_calculator import StaticAlphaCalculator
from static_beta_calculator import StaticBetaCalculator
from static_information_ratio_calculator import StaticInformationRatioCalculator
from static_treynor_ratio_calculator import StaticTreynorRatioCalculator
from static_calmar_ratio_calculator import StaticCalmarRatioCalculator
from static_ulcer_index_calculator import StaticUlcerIndexCalculator
from rolling_alpha_calculator import RollingAlphaCalculator
from rolling_beta_calculator import RollingBetaCalculator
from rolling_information_ratio_calculator import RollingInformationRatioCalculator
from static_hit_ratio_calculator import StaticHitRatioCalculator
from rolling_hit_ratio_calculator import RollingHitRatioCalculator
from rolling_drawdown_calculator import RollingDrawdownCalculator


class MutualFundAnalyzer:
    """Analyzer for mutual fund parameters including returns, risk measures, and performance metrics."""
    
    def __init__(self, scheme_code: str):
        """
        Initialize the calculator and fetch scheme data.
        
        Initializes instance variables:
        - years_to_calculate: List of years for calendar year returns calculation
        - scheme_code: Mutual fund scheme code
        - scheme_data: Historical NAV data for the scheme
        
        Args:
            scheme_code: Mutual fund scheme code
        """
        self.years_to_calculate = [datetime.date.today().year - i for i in range(1, Constants.NUM_CALENDAR_YEARS + 1)]
        self.scheme_code = scheme_code
        self.scheme_data = DataFetcher.fetch_scheme_data(self.scheme_code)
        self.benchmark_data = DataFetcher.fetch_benchmark_data()
        
        # Initialize results variables
        self.rolling_data: Dict[str, Any] = {}
        self.calendar_data: Dict[str, Any] = {}
        self.static_std_dev_data: Dict[str, Any] = {}
        self.static_downside_dev_data: Dict[str, Any] = {}
        self.rolling_std_dev_data: Dict[str, Any] = {}
        self.static_sharpe_data: Dict[str, Any] = {}
        self.rolling_sharpe_data: Dict[str, Any] = {}
        self.static_sortino_data: Dict[str, Any] = {}
        self.rolling_sortino_data: Dict[str, Any] = {}
        self.static_drawdown_data: Dict[str, Any] = {}
        self.static_alpha_data: Dict[str, Any] = {}
        self.static_beta_data: Dict[str, Any] = {}
        self.static_information_ratio_data: Dict[str, Any] = {}
        self.static_treynor_ratio_data: Dict[str, Any] = {}
        self.static_calmar_ratio_data: Dict[str, Any] = {}
        self.static_ulcer_index_data: Dict[str, Any] = {}
        self.rolling_alpha_data: Dict[str, Any] = {}
        self.rolling_beta_data: Dict[str, Any] = {}
        self.rolling_information_ratio_data: Dict[str, Any] = {}
        self.static_hit_ratio_data: Dict[str, Any] = {}
        self.rolling_hit_ratio_data: Dict[str, Any] = {}
        self.rolling_drawdown_data: Dict[str, Any] = {}
    
    def _display_metrics(self) -> None:
        """
        Display the calculated metrics (returns and risk) for a scheme in a formatted way.
        
        Prints rolling returns (min/avg/max CAGR), calendar year returns, Standard Deviation,
        Downside Deviation, Rolling Standard Deviation, Sharpe Ratio, Rolling Sharpe Ratio, Sortino Ratio, 
        and Rolling Sortino Ratio in a formatted table format.
        
        Uses instance variables for data.
        """
        # Get scheme name from scheme_data (guaranteed to exist if we reach here)
        scheme_name = self.scheme_data.get('scheme_name', 'Unknown') if self.scheme_data else 'Unknown'
        
        print(f"\n{scheme_name}")
        print("=" * 60)
        
        # Print rolling returns
        if self.rolling_data:
            print("\nRolling Returns (Min / Average / Max CAGR):")
            print("-" * 60)
            
            for year in Constants.ROLLING_YEARS:
                if year in self.rolling_data['rolling_returns']:
                    year_data = self.rolling_data['rolling_returns'][year]
                    if 'error' in year_data:
                        print(f"{year} Year(s): {year_data['error']}")
                    else:
                        print(f"{year} Year(s): {year_data['min']}% / {year_data['avg']}% / {year_data['max']}%")
        
        # Print calendar year returns
        if self.calendar_data:
            print("\nCalendar Year Returns:")
            print("-" * 60)
            
            for year in self.years_to_calculate:
                if year in self.calendar_data['calendar_returns']:
                    return_value = self.calendar_data['calendar_returns'][year]
                    if return_value is None:
                        print(f"{year}: N/A")
                    else:
                        print(f"{year}: {return_value}%")
        
        # Static Metrics
        self._print_static_metrics("Static Standard Deviation (Annualized Volatility %)", self.static_std_dev_data, 'std_devs', "%")
        self._print_static_metrics("Static Downside Deviation (Annualized Downside Volatility %)", self.static_downside_dev_data, 'downside_devs', "%")
        self._print_static_metrics("Static Hit Ratio (Outperformance %)", self.static_hit_ratio_data, 'static_hit_ratios', "%")
        self._print_static_metrics("Sharpe Ratio", self.static_sharpe_data, 'static_sharpe_ratios')
        self._print_static_metrics("Sortino Ratio", self.static_sortino_data, 'static_sortino_ratios')
        self._print_static_metrics("Static Alpha (Jensen's Alpha %)", self.static_alpha_data, 'static_alphas', "%")
        self._print_static_metrics("Static Beta", self.static_beta_data, 'static_betas')
        self._print_static_metrics("Static Information Ratio", self.static_information_ratio_data, 'static_information_ratios')
        self._print_static_metrics("Static Treynor Ratio", self.static_treynor_ratio_data, 'static_treynor_ratios')
        self._print_static_metrics("Static Calmar Ratio", self.static_calmar_ratio_data, 'static_calmar_ratios')
        self._print_static_metrics("Static Ulcer Index", self.static_ulcer_index_data, 'static_ulcer_indices')

        # Rolling Metrics Tables
        self._print_rolling_table("Rolling Standard Deviation (Volatility %)", self.rolling_std_dev_data, 'rolling_std_devs')
        self._print_rolling_table("Rolling Hit Ratio (Outperformance %)", self.rolling_hit_ratio_data, 'rolling_hit_ratios', is_percentage=True)
        self._print_rolling_table("Rolling Sharpe Ratio", self.rolling_sharpe_data, 'rolling_sharpe_ratios', is_ratio=True)
        self._print_rolling_table("Rolling Sortino Ratio", self.rolling_sortino_data, 'rolling_sortino_ratios', is_ratio=True)
        self._print_rolling_table("Rolling Alpha (Jensen's Alpha %)", self.rolling_alpha_data, 'rolling_alphas')
        self._print_rolling_table("Rolling Beta", self.rolling_beta_data, 'rolling_betas')
        self._print_rolling_table("Rolling Information Ratio", self.rolling_information_ratio_data, 'rolling_information_ratios')
        self._print_rolling_table("Rolling Max Drawdown", self.rolling_drawdown_data, 'rolling_drawdowns', is_percentage=True)
        
        # Static Max Drawdown Table
        self._print_static_drawdown_table()
        
        print("=" * 60)

    def _print_static_drawdown_table(self) -> None:
        """Helper to print the static max drawdown and recovery table."""
        if not self.static_drawdown_data or 'drawdowns' not in self.static_drawdown_data:
            return
            
        print("\nMax Drawdown & Recovery Time:")
        print("-" * 60)
        print(f"{'Period':<15} {'Max Drawdown':<20} {'Recovery Time (Days)':<20}")
        print("-" * 60)
        
        for year in Constants.STATIC_DRAWDOWN_YEARS:
            if year in self.static_drawdown_data['drawdowns']:
                dd_value = self.static_drawdown_data['drawdowns'][year]
                if isinstance(dd_value, dict) and 'error' in dd_value:
                    print(f"{year} Year(s): {dd_value['error']}")
                else:
                    print(f"{str(year) + ' Year(s)':<15} {str(dd_value['max_drawdown']) + '%':<20} {dd_value['max_duration_days']:<20}")

    def _print_static_metrics(self, title: str, data: Dict[str, Any], key: str, unit: str = "") -> None:
        """Helper to print static metrics in a consistent format."""
        if not data or key not in data:
            return
            
        print(f"\n{title}:")
        print("-" * 60)
        
        for period, value in data[key].items():
            if isinstance(value, dict) and 'error' in value:
                print(f"{period} Year(s): {value['error']}")
            else:
                print(f"{period} Year(s): {value}{unit}")

    def _print_rolling_table(self, title: str, data: Dict[str, Any], key: str, is_ratio: bool = False, is_percentage: bool = False) -> None:
        """Helper to print rolling metrics tables in a consistent format."""
        if not data or key not in data:
            return
            
        print(f"\n{title}:")
        print("-" * 60)
        
        unit = "%" if is_percentage else ""
        
        if is_ratio:
            # Format for Sharpe/Sortino ratios
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'10%ile':<10} {'Latest':<10} {'% > 0':<8}")
            print("-" * 80)
            for item in data[key]:
                w, d = item['rolling_window'], item['total_data']
                if 'error' in item:
                    print(f"{w:<10} {d:<10} Error: {item['error']}")
                else:
                    print(f"{w:<10} {d:<10} {item['median']:<10} {item['mean']:<10} {item['percentile_10']:<10} {item['latest']:<10} {item['positive_share']:<8}")
        else:
            # Standard format for Alpha, Beta, Std Dev, etc.
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'Min':<10} {'Max':<10} {'Latest':<10}")
            print("-" * 80)
            for item in data[key]:
                w, d = item['rolling_window'], item['total_data']
                if 'error' in item:
                    print(f"{w:<10} {d:<10} Error: {item['error']}")
                else:
                    print(f"{w:<10} {d:<10} {item['median']}{unit:<9} {item['mean']}{unit:<9} {item['min']}{unit:<9} {item['max']}{unit:<9} {item['latest']}{unit:<9}")
    
    def process_scheme(self) -> None:
        """
        Process the scheme: calculate all returns and print results.
        
        Calculates rolling returns and calendar year returns, then prints
        the formatted results. Uses the scheme data fetched during initialization.
        
        Returns:
            None (prints results to stdout)
        """
        if self.scheme_data is None:
            return
        
        self.rolling_data = RollingReturnsCalculator.calculate(self.scheme_data)
        self.calendar_data = CalendarYearReturnsCalculator.calculate(self.scheme_data, self.years_to_calculate)
        self.static_std_dev_data = StaticStandardDeviationCalculator.calculate(self.scheme_data)
        self.static_downside_dev_data = StaticDownsideDeviationCalculator.calculate(self.scheme_data)
        self.rolling_std_dev_data = RollingStandardDeviationCalculator.calculate(self.scheme_data)
        self.static_sharpe_data = StaticSharpeRatioCalculator.calculate(self.scheme_data)
        self.rolling_sharpe_data = RollingSharpeRatioCalculator.calculate(self.scheme_data)
        self.static_sortino_data = StaticSortinoRatioCalculator.calculate(self.scheme_data)
        self.rolling_sortino_data = RollingSortinoRatioCalculator.calculate(self.scheme_data)
        self.static_drawdown_data = StaticDrawdownCalculator.calculate(self.scheme_data)
        self.rolling_drawdown_data = RollingDrawdownCalculator.calculate(self.scheme_data)
        self.static_calmar_ratio_data = StaticCalmarRatioCalculator.calculate(self.scheme_data)
        self.static_ulcer_index_data = StaticUlcerIndexCalculator.calculate(self.scheme_data)

        # Calculate Static Alpha, Beta, and Information Ratio if benchmark data is available
        if self.benchmark_data:
            self.static_alpha_data = StaticAlphaCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.static_beta_data = StaticBetaCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.static_information_ratio_data = StaticInformationRatioCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.static_treynor_ratio_data = StaticTreynorRatioCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.rolling_alpha_data = RollingAlphaCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.rolling_beta_data = RollingBetaCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.rolling_information_ratio_data = RollingInformationRatioCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.static_hit_ratio_data = StaticHitRatioCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.rolling_hit_ratio_data = RollingHitRatioCalculator.calculate(self.scheme_data, self.benchmark_data)

        # Display all metrics
        self._display_metrics()

def main() -> None:
    """
    Main entry point for the script.
    
    Parses command-line arguments and processes each scheme code.
    Calculates and prints returns for all provided scheme codes.
    
    Usage:
        python mutual_fund_analyzer.py <scheme_codes>
        Example: python mutual_fund_analyzer.py 101206,101207
    """
    if len(sys.argv) < 2:
        print("Error: Scheme codes not provided")
        print("Usage: python mutual_fund_analyzer.py <scheme_codes>")
        print("Example: python mutual_fund_analyzer.py 101206,101207")
        return
    
    scheme_codes = [code.strip() for code in sys.argv[1].split(",")]
    
    for scheme_code in scheme_codes:
        mf_analyzer = MutualFundAnalyzer(scheme_code)
        mf_analyzer.process_scheme()


if __name__ == "__main__":
    main()
