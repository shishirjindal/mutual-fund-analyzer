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
from constants import Constants
from data_fetcher import SchemeDataFetcher
from rolling_returns_calculator import RollingReturnsCalculator
from calendar_year_returns_calculator import CalendarYearReturnsCalculator
from static_standard_deviation_calculator import StaticStandardDeviationCalculator
from rolling_standard_deviation_calculator import RollingStandardDeviationCalculator
from static_sharpe_ratio_calculator import StaticSharpeRatioCalculator
from rolling_sharpe_ratio_calculator import RollingSharpeRatioCalculator


class MutualFundAnalyzer:
    """Analyzer for mutual fund parameters including returns, risk measures, and performance metrics."""
    
    def __init__(self, scheme_code):
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
        self.scheme_data = SchemeDataFetcher.fetch_scheme_data(self.scheme_code)
    
    def _display_metrics(self, rolling_data, calendar_data, std_dev_data, rolling_std_dev_data, static_sharpe_data, rolling_sharpe_data):
        """
        Display the calculated metrics (returns and risk) for a scheme in a formatted way.
        
        Prints rolling returns (min/avg/max CAGR), calendar year returns, Standard Deviation,
        Rolling Standard Deviation, Sharpe Ratio, and Rolling Sharpe Ratio in a formatted table format.
        
        Args:
            rolling_data: Dictionary containing rolling returns data, or None
            calendar_data: Dictionary containing calendar year returns data, or None
            std_dev_data: Dictionary containing static standard deviation data, or None
            rolling_std_dev_data: Dictionary containing rolling standard deviation data, or None
            static_sharpe_data: Dictionary containing static Sharpe ratio data, or None
            rolling_sharpe_data: Dictionary containing rolling Sharpe ratio data, or None
        """
        if (rolling_data is None and calendar_data is None and std_dev_data is None and 
            rolling_std_dev_data is None and static_sharpe_data is None and rolling_sharpe_data is None):
            return
        
        scheme_name = (
            rolling_data['scheme_name'] if rolling_data else
            calendar_data['scheme_name'] if calendar_data else
            std_dev_data['scheme_name'] if std_dev_data else 
            rolling_std_dev_data['scheme_name'] if rolling_std_dev_data else 
            static_sharpe_data['scheme_name'] if static_sharpe_data else
            rolling_sharpe_data['scheme_name'] if rolling_sharpe_data else 'Unknown'
        )
        
        print(f"\n{scheme_name}")
        print("=" * 60)
        
        # Print rolling returns
        if rolling_data:
            print("\nRolling Returns (Min / Average / Max CAGR):")
            print("-" * 60)
            
            for year in Constants.ROLLING_YEARS:
                if year in rolling_data['rolling_returns']:
                    year_data = rolling_data['rolling_returns'][year]
                    if 'error' in year_data:
                        print(f"{year} Year(s): {year_data['error']}")
                    else:
                        print(f"{year} Year(s): {year_data['min']}% / {year_data['avg']}% / {year_data['max']}%")
        
        # Print calendar year returns
        if calendar_data:
            print("\nCalendar Year Returns:")
            print("-" * 60)
            
            for year in self.years_to_calculate:
                if year in calendar_data['calendar_returns']:
                    return_value = calendar_data['calendar_returns'][year]
                    if return_value is None:
                        print(f"{year}: N/A")
                    else:
                        print(f"{year}: {return_value}%")
        
        # Print Standard Deviation
        if std_dev_data:
            print("\nStatic Standard Deviation (Annualized Volatility %):")
            print("-" * 60)
            
            for year in Constants.STATIC_STANDARD_DEVIATION_YEARS:
                if year in std_dev_data['std_devs']:
                    std_dev_value = std_dev_data['std_devs'][year]
                    if isinstance(std_dev_value, dict) and 'error' in std_dev_value:
                        print(f"{year} Year(s): {std_dev_value['error']}")
                    else:
                        print(f"{year} Year(s): {std_dev_value}%")

        # Print Rolling Standard Deviation
        if rolling_std_dev_data:
            print("\nRolling Standard Deviation (Volatility %):")
            print("-" * 60)
            
            # Print column headers
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'Min':<10} {'Max':<10} {'Latest':<10}")
            print("-" * 80)
            
            for item in rolling_std_dev_data['rolling_std_devs']:
                total_data = item['total_data']
                window = item['rolling_window']
                if 'error' in item:
                    print(f"{window:<10} {total_data:<10} Error: {item['error']}")
                else:
                    print(f"{window:<10} {total_data:<10} {item['median']:<10} {item['mean']:<10} {item['min']:<10} {item['max']:<10} {item['latest']:<10}")

        # Print Sharpe Ratio
        if static_sharpe_data:
            print("\nSharpe Ratio:")
            print("-" * 60)
            
            for year in Constants.STATIC_SHARPE_RATIO_YEARS:
                if year in static_sharpe_data['static_sharpe_ratios']:
                    sharpe_value = static_sharpe_data['static_sharpe_ratios'][year]
                    if isinstance(sharpe_value, dict) and 'error' in sharpe_value:
                        print(f"{year} Year(s): {sharpe_value['error']}")
                    else:
                        print(f"{year} Year(s): {sharpe_value}")

        # Print Rolling Sharpe Ratio
        if rolling_sharpe_data:
            print("\nRolling Sharpe Ratio:")
            print("-" * 60)
            
            # Print column headers
            print(f"{'Window':<10} {'Data':<10} {'Median':<10} {'Mean':<10} {'10%ile':<10} {'Latest':<10} {'% > 0':<8}")
            print("-" * 80)
            
            for item in rolling_sharpe_data['rolling_sharpe_ratios']:
                total_data = item['total_data']
                window = item['rolling_window']
                if 'error' in item:
                    print(f"{window:<10} {total_data:<10} Error: {item['error']}")
                else:
                    print(f"{window:<10} {total_data:<10} {item['median']:<10} {item['mean']:<10} {item['percentile_10']:<10} {item['latest']:<10} {item['positive_share']:<8}")
        
        print("=" * 60)
    
    def process_scheme(self):
        """
        Process the scheme: calculate all returns and print results.
        
        Calculates rolling returns and calendar year returns, then prints
        the formatted results. Uses the scheme data fetched during initialization.
        
        Returns:
            None (prints results to stdout)
        """
        if self.scheme_data is None:
            return
        
        rolling_data = RollingReturnsCalculator.calculate(self.scheme_data)
        calendar_data = CalendarYearReturnsCalculator.calculate(self.scheme_data, self.years_to_calculate)
        std_dev_data = StaticStandardDeviationCalculator.calculate(self.scheme_data)
        rolling_std_dev_data = RollingStandardDeviationCalculator.calculate(self.scheme_data)
        static_sharpe_data = StaticSharpeRatioCalculator.calculate(self.scheme_data)
        rolling_sharpe_data = RollingSharpeRatioCalculator.calculate(self.scheme_data)
        self._display_metrics(rolling_data, calendar_data, std_dev_data, rolling_std_dev_data, static_sharpe_data, rolling_sharpe_data)

def main():
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
