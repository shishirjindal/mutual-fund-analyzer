#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-

"""
Mutual Fund Returns Calculator

This script calculates various types of returns for mutual fund schemes:
- Rolling returns: CAGR (Compound Annual Growth Rate) over rolling periods (1, 3, 5 years)
- Calendar year returns: Returns for the last 5 calendar years
"""

import sys
import json
import datetime
import statistics
import math
from mftool import Mftool
from constants import Constants


class MutualFundAnalyzer:
    """Analyzer for mutual fund parameters including returns, risk measures, and performance metrics."""
    
    def __init__(self, scheme_code):
        """
        Initialize the calculator and fetch scheme data.
        
        Initializes instance variables:
        - mf_tool: Mftool instance for fetching NAV data
        - years_to_calculate: List of years for calendar year returns calculation
        - scheme_code: Mutual fund scheme code
        - scheme_data: Historical NAV data for the scheme
        
        Args:
            scheme_code: Mutual fund scheme code
        """
        self.mf_tool = Mftool()
        self.years_to_calculate = [datetime.date.today().year - i for i in range(1, Constants.NUM_CALENDAR_YEARS + 1)]
        self.scheme_code = scheme_code
        self.scheme_data = self._fetch_scheme_data()
    
    @staticmethod
    def _calculate_cagr(absolute_return_percent, years):
        """
        Calculate CAGR (Compound Annual Growth Rate) from absolute return percentage.
        Internal helper method.
        
        Args:
            absolute_return_percent: Absolute return as a percentage (e.g., 50 for 50%)
            years: Number of years for compounding
        
        Returns:
            CAGR as a percentage
        """
        return (pow((1.0 * absolute_return_percent) / 100 + 1, 1.0 / years) - 1) * 100
    
    def _fetch_scheme_data(self):
        """
        Fetch historical NAV data for the scheme (private method).
        Uses self.scheme_code stored during initialization.
        
        Returns:
            Dictionary containing scheme data, or None if error occurs
        """
        try:
            nav_data = self.mf_tool.get_scheme_historical_nav(self.scheme_code, as_json=True)
            
            # Handle case where invalid scheme code returns None
            if nav_data is None:
                print(f"Error: No data found for scheme code {self.scheme_code}")
                return None
            
            # Parse JSON string to dictionary
            return json.loads(nav_data)
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON response for scheme code {self.scheme_code}: {e}")
            return None
        except TypeError as e:
            print(f"Error: Invalid data type for scheme code {self.scheme_code}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error processing scheme code {self.scheme_code}: {e}")
            return None
    
    def _calculate_rolling_returns(self):
        """
        Calculate rolling returns for 1, 3 and 5 years using stored scheme data.
        Internal method.
        
        Returns:
            Dictionary with scheme_name and rolling_returns data, or None if error occurs.
            rolling_returns is a dictionary mapping year (1, 3, 5) to a dict with:
            - 'min': minimum CAGR percentage
            - 'avg': average CAGR percentage
            - 'max': maximum CAGR percentage
            - 'error': error message if calculation failed
        """
        if self.scheme_data is None:
            return None
        
        historical_data = self.scheme_data['data']
        rolling_returns = {}
        
        for year in Constants.ROLLING_YEARS:
            cagr_values = []
            required_data_points = year * Constants.TRADING_DAYS_PER_YEAR + 1
            
            if len(historical_data) < required_data_points:
                rolling_returns[year] = {
                    'error': f'Insufficient data (need {required_data_points}, have {len(historical_data)})'
                }
                continue
            
            # Calculate rolling returns
            for start_index in range(len(historical_data) - required_data_points):
                try:
                    initial_index = start_index + year * Constants.TRADING_DAYS_PER_YEAR
                    initial_nav = float(historical_data[initial_index]['nav'])
                    final_nav = float(historical_data[start_index]['nav'])
                    
                    if initial_nav == 0:
                        continue
                    
                    absolute_return = (final_nav - initial_nav) * 100 / initial_nav
                    cagr = self._calculate_cagr(absolute_return, year)
                    cagr_values.append(cagr)
                    
                except (ValueError, KeyError, IndexError, ZeroDivisionError):
                    continue
                except Exception:
                    continue
            
            if len(cagr_values) == 0:
                rolling_returns[year] = {'error': 'No valid data points'}
            else:
                rolling_returns[year] = {
                    'min': round(min(cagr_values), Constants.DECIMAL_PLACES),
                    'avg': round(sum(cagr_values) / len(cagr_values), Constants.DECIMAL_PLACES),
                    'max': round(max(cagr_values), Constants.DECIMAL_PLACES)
                }
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'rolling_returns': rolling_returns
        }
    
    def _calculate_calendar_year_returns(self):
        """
        Calculate calendar year returns for the last 5 years using stored scheme data.
        Internal method.
        
        For each year, calculates return from earliest available NAV in January to 
        earliest available NAV in January of the next year.
        
        Returns:
            Dictionary with scheme_name and calendar_returns data, or None if error occurs.
            calendar_returns is a dictionary mapping year to return percentage or None if unavailable.
        """
        if self.scheme_data is None:
            return None
        
        # Create a date-to-NAV lookup dictionary for faster access
        nav_lookup = {entry['date']: float(entry['nav']) for entry in self.scheme_data['data']}
        calendar_returns = {}
        
        for year in self.years_to_calculate:
            try:
                # Find initial NAV: earliest available date in January
                initial_nav = 0.0
                for day in Constants.JANUARY_DATE_DAYS:
                    date_pattern = f"{day:02d}-{Constants.JANUARY_MONTH:02d}-{year}"
                    if date_pattern in nav_lookup:
                        initial_nav = nav_lookup[date_pattern]
                        break
                
                # Find final NAV: early January of next year
                final_nav = 0.0
                for day in Constants.JANUARY_DATE_DAYS:
                    date_pattern = f"{day:02d}-{Constants.JANUARY_MONTH:02d}-{year + 1}"
                    if date_pattern in nav_lookup:
                        final_nav = nav_lookup[date_pattern]
                        break
                
                # Calculate return
                if initial_nav > 0 and final_nav > 0:
                    return_percent = (final_nav - initial_nav) * 100 / initial_nav
                    calendar_returns[year] = round(return_percent, Constants.DECIMAL_PLACES)
                else:
                    calendar_returns[year] = None
                    
            except (ValueError, KeyError, IndexError, ZeroDivisionError):
                calendar_returns[year] = None
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'calendar_returns': calendar_returns
        }
    
    def _calculate_sharpe_ratio(self):
        """
        Calculate annualized Sharpe Ratio for 1, 3, and 5 years using daily NAV returns.
        Internal method.
        
        Calculation methodology for each period:
        1. Compute daily returns from consecutive NAV values
        2. Calculate arithmetic mean of daily returns
        3. Annualize the mean return: Annualized Return = Mean Daily Return × Trading Days × 100
        4. Calculate standard deviation of daily returns
        5. Annualize volatility: Annualized Volatility = Std Dev × √Trading Days × 100
        6. Apply Sharpe Ratio formula: (Annualized Return - Risk-free Rate) / Annualized Volatility
        
        Uses the most recent N years of daily NAV data for each period (1, 3, 5 years).
        All values are converted to percentages for consistency.
        
        Returns:
            Dictionary with scheme_name and sharpe_ratios data, or None if error occurs.
            sharpe_ratios is a dictionary mapping year (1, 3, 5) to Sharpe Ratio value or error message.
        """
        if self.scheme_data is None:
            return None
        
        historical_data = self.scheme_data['data']
        sharpe_ratios = {}
        
        for year in Constants.SHARPE_RATIO_YEARS:
            # Calculate required data points for this period
            required_data_points = year * Constants.TRADING_DAYS_PER_YEAR + 1
            
            if len(historical_data) < required_data_points:
                sharpe_ratios[year] = {
                    'error': f'Insufficient data (need {required_data_points}, have {len(historical_data)})'
                }
                continue
            
            # Use only the last N years of data (most recent data)
            # NAV data is ordered with most recent first (index 0), so we reverse it for chronological order
            recent_data = historical_data[:required_data_points]
            chronological_data = list(reversed(recent_data))  # Reverse to get oldest first
            
            # Step 1: Calculate daily returns
            daily_returns = []
            
            for i in range(len(chronological_data) - 1):
                try:
                    # Data is in chronological order (oldest first)
                    nav_yesterday = float(chronological_data[i]['nav'])
                    nav_today = float(chronological_data[i + 1]['nav'])
                    
                    if nav_yesterday == 0:
                        continue
                    
                    # Calculate daily return
                    daily_return = (nav_today - nav_yesterday) / nav_yesterday
                    daily_returns.append(daily_return)
                    
                except (ValueError, KeyError, IndexError, ZeroDivisionError):
                    continue
            
            # Need at least 2 data points to calculate standard deviation
            if len(daily_returns) < 2:
                sharpe_ratios[year] = {
                    'error': 'Insufficient daily data points for Sharpe Ratio calculation'
                }
                continue
            
            try:
                # Step 2: Calculate mean of daily returns
                mean_daily_return = sum(daily_returns) / len(daily_returns)
                
                # Step 3: Annualize return (convert to percentage)
                annualized_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR * 100
                
                # Step 4: Compute standard deviation of daily returns
                std_dev_daily = statistics.stdev(daily_returns)
                
                # Check for zero standard deviation
                if std_dev_daily == 0:
                    sharpe_ratios[year] = {
                        'error': 'Standard deviation of daily returns is zero'
                    }
                    continue
                
                # Step 5: Calculate annualized volatility (convert to percentage)
                annualized_volatility = std_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR) * 100
                
                # Step 6: Apply formula: Sharpe = (Annualized return - Risk-free rate) / Annualized volatility
                sharpe_ratio = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
                
                sharpe_ratios[year] = round(sharpe_ratio, Constants.DECIMAL_PLACES)
                
            except (ValueError, ZeroDivisionError) as e:
                sharpe_ratios[year] = {
                    'error': f'Error calculating Sharpe Ratio: {e}'
                }
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'sharpe_ratios': sharpe_ratios
        }
    
    def _print_returns(self, rolling_data, calendar_data, sharpe_data):
        """
        Print the returns data for a scheme in a formatted way.
        Internal method.
        
        Prints rolling returns (min/avg/max CAGR), calendar year returns, and Sharpe Ratio
        in a formatted table format.
        
        Args:
            rolling_data: Dictionary returned by _calculate_rolling_returns(), or None
            calendar_data: Dictionary returned by _calculate_calendar_year_returns(), or None
            sharpe_data: Dictionary returned by _calculate_sharpe_ratio(), or None
        """
        if rolling_data is None and calendar_data is None and sharpe_data is None:
            return
        
        scheme_name = (
            rolling_data['scheme_name'] if rolling_data else
            calendar_data['scheme_name'] if calendar_data else
            sharpe_data['scheme_name'] if sharpe_data else 'Unknown'
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
        
        # Print Sharpe Ratio
        if sharpe_data:
            print("\nSharpe Ratio:")
            print("-" * 60)
            
            for year in Constants.SHARPE_RATIO_YEARS:
                if year in sharpe_data['sharpe_ratios']:
                    sharpe_value = sharpe_data['sharpe_ratios'][year]
                    if isinstance(sharpe_value, dict) and 'error' in sharpe_value:
                        print(f"{year} Year(s): {sharpe_value['error']}")
                    else:
                        print(f"{year} Year(s): {sharpe_value}")
        
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
        
        rolling_data = self._calculate_rolling_returns()
        calendar_data = self._calculate_calendar_year_returns()
        sharpe_data = self._calculate_sharpe_ratio()
        self._print_returns(rolling_data, calendar_data, sharpe_data)


def main():
    """
    Main entry point for the script.
    
    Parses command-line arguments and processes each scheme code.
    Calculates and prints returns for all provided scheme codes.
    
    Usage:
        python mfReturns.py <scheme_codes>
        Example: python mfReturns.py 101206,101207
    """
    if len(sys.argv) < 2:
        print("Error: Scheme codes not provided")
        print("Usage: python mfReturns.py <scheme_codes>")
        print("Example: python mfReturns.py 101206,101207")
        return
    
    scheme_codes = [code.strip() for code in sys.argv[1].split(",")]
    
    for scheme_code in scheme_codes:
        mf_analyzer = MutualFundAnalyzer(scheme_code)
        mf_analyzer.process_scheme()


if __name__ == "__main__":
    main()
