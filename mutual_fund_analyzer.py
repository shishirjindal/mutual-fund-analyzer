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
from information_ratio_calculator import InformationRatioCalculator


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
        self.information_ratio_data: Dict[str, Any] = {}
    
    def _display_metrics(self) -> None:
        """
        Display the calculated metrics (returns and risk) for a scheme in a formatted way.
        
        Prints rolling returns (min/avg/max CAGR), calendar year returns, Standard Deviation,
        Downside Deviation, Rolling Standard Deviation, Sharpe Ratio, Rolling Sharpe Ratio, Sortino Ratio, 
        and Rolling Sortino Ratio in a formatted table format.
        
        Uses instance variables for data.
        """
        if (not self.rolling_data and not self.calendar_data and not self.static_std_dev_data and 
            not self.static_downside_dev_data and not self.rolling_std_dev_data and not self.static_sharpe_data and 
            not self.rolling_sharpe_data and not self.static_sortino_data and not self.rolling_sortino_data and
            not self.static_drawdown_data and not self.static_alpha_data and not self.static_beta_data and
            not self.information_ratio_data):
            return
        
        scheme_name = 'Unknown'
        if self.rolling_data and 'scheme_name' in self.rolling_data:
            scheme_name = self.rolling_data['scheme_name']
        elif self.calendar_data and 'scheme_name' in self.calendar_data:
            scheme_name = self.calendar_data['scheme_name']
        elif self.static_std_dev_data and 'scheme_name' in self.static_std_dev_data:
            scheme_name = self.static_std_dev_data['scheme_name']
        elif self.static_downside_dev_data and 'scheme_name' in self.static_downside_dev_data:
            scheme_name = self.static_downside_dev_data['scheme_name']
        elif self.rolling_std_dev_data and 'scheme_name' in self.rolling_std_dev_data:
            scheme_name = self.rolling_std_dev_data['scheme_name']
        elif self.static_sharpe_data and 'scheme_name' in self.static_sharpe_data:
            scheme_name = self.static_sharpe_data['scheme_name']
        elif self.rolling_sharpe_data and 'scheme_name' in self.rolling_sharpe_data:
            scheme_name = self.rolling_sharpe_data['scheme_name']
        elif self.static_sortino_data and 'scheme_name' in self.static_sortino_data:
            scheme_name = self.static_sortino_data['scheme_name']
        elif self.rolling_sortino_data and 'scheme_name' in self.rolling_sortino_data:
            scheme_name = self.rolling_sortino_data['scheme_name']
        
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
        
        # Print Standard Deviation
        if self.static_std_dev_data:
            print("\nStatic Standard Deviation (Annualized Volatility %):")
            print("-" * 60)
            
            for year in Constants.STATIC_STANDARD_DEVIATION_YEARS:
                if year in self.static_std_dev_data['std_devs']:
                    std_dev_value = self.static_std_dev_data['std_devs'][year]
                    if isinstance(std_dev_value, dict) and 'error' in std_dev_value:
                        print(f"{year} Year(s): {std_dev_value['error']}")
                    else:
                        print(f"{year} Year(s): {std_dev_value}%")

        # Print Downside Deviation
        if self.static_downside_dev_data:
            print("\nStatic Downside Deviation (Annualized Downside Volatility %):")
            print("-" * 60)
            
            for year in Constants.STATIC_DOWNSIDE_DEVIATION_YEARS:
                if year in self.static_downside_dev_data['downside_devs']:
                    dev_value = self.static_downside_dev_data['downside_devs'][year]
                    if isinstance(dev_value, dict) and 'error' in dev_value:
                        print(f"{year} Year(s): {dev_value['error']}")
                    else:
                        print(f"{year} Year(s): {dev_value}%")

        # Print Rolling Standard Deviation
        if self.rolling_std_dev_data:
            print("\nRolling Standard Deviation (Volatility %):")
            print("-" * 60)
            
            # Print column headers
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'Min':<10} {'Max':<10} {'Latest':<10}")
            print("-" * 80)
            
            for item in self.rolling_std_dev_data['rolling_std_devs']:
                total_data = item['total_data']
                window = item['rolling_window']
                if 'error' in item:
                    print(f"{window:<10} {total_data:<10} Error: {item['error']}")
                else:
                    print(f"{window:<10} {total_data:<10} {item['median']:<10} {item['mean']:<10} {item['min']:<10} {item['max']:<10} {item['latest']:<10}")

        # Print Sharpe Ratio
        if self.static_sharpe_data:
            print("\nSharpe Ratio:")
            print("-" * 60)
            
            for year in Constants.STATIC_SHARPE_RATIO_YEARS:
                if year in self.static_sharpe_data['static_sharpe_ratios']:
                    sharpe_value = self.static_sharpe_data['static_sharpe_ratios'][year]
                    if isinstance(sharpe_value, dict) and 'error' in sharpe_value:
                        print(f"{year} Year(s): {sharpe_value['error']}")
                    else:
                        print(f"{year} Year(s): {sharpe_value}")

        # Print Rolling Sharpe Ratio
        if self.rolling_sharpe_data:
            print("\nRolling Sharpe Ratio:")
            print("-" * 60)
            
            # Print column headers
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'10%ile':<10} {'Latest':<10} {'% > 0':<8}")
            print("-" * 80)
            
            for item in self.rolling_sharpe_data['rolling_sharpe_ratios']:
                total_data = item['total_data']
                window = item['rolling_window']
                if 'error' in item:
                    print(f"{window:<10} {total_data:<10} Error: {item['error']}")
                else:
                    print(f"{window:<10} {total_data:<10} {item['median']:<10} {item['mean']:<10} {item['percentile_10']:<10} {item['latest']:<10} {item['positive_share']:<8}")

        # Print Sortino Ratio
        if self.static_sortino_data:
            print("\nSortino Ratio:")
            print("-" * 60)
            
            for year in Constants.STATIC_SORTINO_RATIO_YEARS:
                if year in self.static_sortino_data['static_sortino_ratios']:
                    sortino_value = self.static_sortino_data['static_sortino_ratios'][year]
                    if isinstance(sortino_value, dict) and 'error' in sortino_value:
                        print(f"{year} Year(s): {sortino_value['error']}")
                    else:
                        print(f"{year} Year(s): {sortino_value}")

        # Print Rolling Sortino Ratio
        if self.rolling_sortino_data:
            print("\nRolling Sortino Ratio:")
            print("-" * 60)
            
            # Print column headers
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'10%ile':<10} {'Latest':<10} {'% > 0':<8}")
            print("-" * 80)
            
            for item in self.rolling_sortino_data['rolling_sortino_ratios']:
                total_data = item['total_data']
                window = item['rolling_window']
                if 'error' in item:
                    print(f"{window:<10} {total_data:<10} Error: {item['error']}")
                else:
                    print(f"{window:<10} {total_data:<10} {item['median']:<10} {item['mean']:<10} {item['percentile_10']:<10} {item['latest']:<10} {item['positive_share']:<8}")
        
        # Print Max Drawdown
        if self.static_drawdown_data:
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

        # Print Static Alpha
        if self.static_alpha_data:
            print("\nStatic Alpha (Jensen's Alpha %):")
            print("-" * 60)
            
            for year in Constants.STATIC_ALPHA_YEARS:
                if year in self.static_alpha_data['static_alphas']:
                    alpha_value = self.static_alpha_data['static_alphas'][year]
                    if isinstance(alpha_value, dict) and 'error' in alpha_value:
                        print(f"{year} Year(s): {alpha_value['error']}")
                    else:
                        print(f"{year} Year(s): {alpha_value}%")

        # Print Static Beta
        if self.static_beta_data:
            print("\nStatic Beta:")
            print("-" * 60)
            
            for year in Constants.STATIC_BETA_YEARS:
                if year in self.static_beta_data['static_betas']:
                    beta_value = self.static_beta_data['static_betas'][year]
                    if isinstance(beta_value, dict) and 'error' in beta_value:
                        print(f"{year} Year(s): {beta_value['error']}")
                    else:
                        print(f"{year} Year(s): {beta_value}")

        # Print Information Ratio
        if self.information_ratio_data:
            print("\nInformation Ratio:")
            print("-" * 60)
            
            for year in Constants.INFORMATION_RATIO_YEARS:
                if year in self.information_ratio_data['information_ratios']:
                    ir_value = self.information_ratio_data['information_ratios'][year]
                    if isinstance(ir_value, dict) and 'error' in ir_value:
                        print(f"{year} Year(s): {ir_value['error']}")
                    else:
                        print(f"{year} Year(s): {ir_value}")
        
        print("=" * 60)
    
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

        # Calculate Static Alpha, Beta, and Information Ratio if benchmark data is available
        if self.benchmark_data:
            self.static_alpha_data = StaticAlphaCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.static_beta_data = StaticBetaCalculator.calculate(self.scheme_data, self.benchmark_data)
            self.information_ratio_data = InformationRatioCalculator.calculate(self.scheme_data, self.benchmark_data)

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
