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
from mftool import Mftool
from constants import Constants


class MutualFundReturnsCalculator:
    """Calculator for mutual fund returns including rolling returns and calendar year returns."""
    
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
                    cagr = MutualFundReturnsCalculator._calculate_cagr(absolute_return, year)
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
    
    def _print_returns(self, rolling_data, calendar_data):
        """
        Print the returns data for a scheme in a formatted way.
        Internal method.
        
        Prints rolling returns (min/avg/max CAGR) and calendar year returns
        in a formatted table format.
        
        Args:
            rolling_data: Dictionary returned by _calculate_rolling_returns(), or None
            calendar_data: Dictionary returned by _calculate_calendar_year_returns(), or None
        """
        if rolling_data is None and calendar_data is None:
            return
        
        scheme_name = rolling_data['scheme_name'] if rolling_data else calendar_data['scheme_name']
        
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
        self._print_returns(rolling_data, calendar_data)


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
        mf_calculator = MutualFundReturnsCalculator(scheme_code)
        mf_calculator.process_scheme()


if __name__ == "__main__":
    main()
