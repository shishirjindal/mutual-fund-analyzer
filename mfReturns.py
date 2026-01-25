#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-

"""
Mutual Fund Returns Calculator

This script calculates various types of returns for mutual fund schemes:
- Rolling returns: CAGR (Compound Annual Growth Rate) over rolling periods
- Point to point returns: Returns between two specific dates
- Calendar year returns: Returns for specific calendar years
"""

import sys
import json
import datetime
from mftool import Mftool

# Constants
TRADING_DAYS_PER_YEAR = 247
DECIMAL_PLACES = 2

# Initialize Mftool instance
mf_tool = Mftool()


def calculate_cagr(absolute_return_percent, years):
    """
    Calculate CAGR (Compound Annual Growth Rate) from absolute return percentage.
    
    Args:
        absolute_return_percent: Absolute return as a percentage (e.g., 50 for 50%)
        years: Number of years for compounding
    
    Returns:
        CAGR as a percentage
    """
    return (pow((1.0 * absolute_return_percent) / 100 + 1, 1.0 / years) - 1) * 100


def fetch_scheme_data(scheme_code):
    """
    Fetch historical NAV data for a scheme.
    
    Args:
        scheme_code: Mutual fund scheme code
    
    Returns:
        Dictionary containing scheme data, or None if error occurs
    """
    try:
        nav_data = mf_tool.get_scheme_historical_nav(scheme_code, as_json=True)
        
        # Handle case where invalid scheme code returns None
        if nav_data is None:
            print(f"Error: No data found for scheme code {scheme_code}")
            return None
        
        # Parse JSON string to dictionary
        return json.loads(nav_data)
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON response for scheme code {scheme_code}: {e}")
        return None
    except TypeError as e:
        print(f"Error: Invalid data type for scheme code {scheme_code}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing scheme code {scheme_code}: {e}")
        return None


def calculate_rolling_returns():
    """
    Calculate rolling returns for specified schemes and time periods.
    Outputs min / average / max CAGR (Compound Annual Growth Rate) for each period.
    """
    if len(sys.argv) < 4:
        print("Error: rolling-returns function requires scheme_codes and years arguments")
        print("Usage: python mfReturns.py rolling-returns <scheme_codes> <years>")
        print("Example: python mfReturns.py rolling-returns 101206,101207 1,3,5")
        return
    
    scheme_codes = sys.argv[2].split(",")
    years_string = sys.argv[3]
    
    for scheme_code in scheme_codes:
        scheme_code = scheme_code.strip()
        scheme_data = fetch_scheme_data(scheme_code)
        
        if scheme_data is None:
            continue
        
        print(scheme_data['scheme_name'])
        historical_data = scheme_data['data']
        
        for year_string in years_string.split(","):
            year = int(year_string.strip())
            cagr_values = []
            required_data_points = year * TRADING_DAYS_PER_YEAR + 1
            
            if len(historical_data) < required_data_points:
                print(f"Insufficient data for {year} year(s) rolling returns. "
                      f"Need at least {required_data_points} data points, have {len(historical_data)}")
                print("0 / 0 / 0")
                continue
            
            # Calculate rolling returns
            for start_index in range(len(historical_data) - required_data_points):
                try:
                    initial_index = start_index + year * TRADING_DAYS_PER_YEAR
                    initial_nav = float(historical_data[initial_index]['nav'])
                    final_nav = float(historical_data[start_index]['nav'])
                    
                    if initial_nav == 0:
                        continue
                    
                    absolute_return = (final_nav - initial_nav) * 100 / initial_nav
                    cagr = calculate_cagr(absolute_return, year)
                    cagr_values.append(cagr)
                    
                except (ValueError, KeyError, IndexError, ZeroDivisionError):
                    continue
                except Exception:
                    continue
            
            if len(cagr_values) == 0:
                print("0 / 0 / 0")
                continue
            
            min_return = str(round(min(cagr_values), DECIMAL_PLACES))
            max_return = str(round(max(cagr_values), DECIMAL_PLACES))
            avg_return = str(round(sum(cagr_values) / len(cagr_values), DECIMAL_PLACES))
            print(f"{min_return} / {avg_return} / {max_return}")


def calculate_point_to_point_returns():
    """
    Calculate returns between two specific dates for a scheme.
    """
    if len(sys.argv) < 5:
        print("Error: point to point function requires scheme_code, initial_date, and final_date arguments")
        print("Usage: python mfReturns.py point-to-point <scheme_code> <initial_date> <final_date>")
        print("Example: python mfReturns.py point-to-point 101206 01-01-2020 31-12-2023")
        return
    
    scheme_code = sys.argv[2]
    initial_date = sys.argv[3]
    final_date = sys.argv[4]
    initial_nav = 0.0
    final_nav = 0.0

    scheme_data = fetch_scheme_data(scheme_code)
    
    if scheme_data is None:
        return
    
    print(scheme_data['scheme_name'])

    # Find NAV values for the specified dates
    for nav_entry in scheme_data['data']:
        if nav_entry['date'] == initial_date:
            initial_nav = float(nav_entry['nav'])
        if nav_entry['date'] == final_date:
            final_nav = float(nav_entry['nav'])
    
    if initial_nav == 0:
        print(f"Error: Could not find NAV for initial date {initial_date}")
        return
    
    if final_nav == 0:
        print(f"Error: Could not find NAV for final date {final_date}")
        return
    
    return_percent = (final_nav - initial_nav) * 100 / initial_nav
    print(round(return_percent, DECIMAL_PLACES))


def calculate_calendar_year_returns():
    """
    Calculate returns for specific calendar years.
    """
    if len(sys.argv) < 4:
        print("Error: calendar-year function requires scheme_codes and years arguments")
        print("Usage: python mfReturns.py calendar-year <scheme_codes> <years>")
        print("Example: python mfReturns.py calendar-year 101206,101207 2020,2021,2022")
        return
    
    scheme_codes = sys.argv[2].split(",")
    years = sys.argv[3].split(",")

    for scheme_code in scheme_codes:
        scheme_code = scheme_code.strip()
        scheme_data = fetch_scheme_data(scheme_code)
        
        if scheme_data is None:
            continue
        
        returns = []

        for year_string in years:
            year_string = year_string.strip()
            initial_nav = 0.0
            final_nav = 0.0
            
            try:
                # Find initial NAV (early in the year)
                initial_date_patterns = [
                    f"01-01-{year_string}",
                    f"02-01-{year_string}",
                    f"03-01-{year_string}",
                    f"04-01-{year_string}"
                ]
                
                # Find final NAV (end of year or early next year)
                year_int = int(year_string)
                final_date_patterns = [
                    f"31-12-{year_int}",
                    f"01-01-{year_int + 1}",
                    f"02-01-{year_int + 1}",
                    f"03-01-{year_int + 1}"
                ]
                
                for nav_entry in scheme_data['data']:
                    if nav_entry['date'] in initial_date_patterns:
                        initial_nav = float(nav_entry['nav'])
                    if nav_entry['date'] in final_date_patterns:
                        final_nav = float(nav_entry['nav'])
                
                # For current year, use the most recent NAV
                if year_string == str(datetime.date.today().year):
                    final_nav = float(scheme_data['data'][0]['nav'])
                
                if initial_nav == 0 or final_nav == 0:
                    returns.append("0.0")
                else:
                    return_percent = (final_nav - initial_nav) * 100 / initial_nav
                    returns.append(str(round(return_percent, DECIMAL_PLACES)))
                    
            except (ValueError, KeyError, IndexError, ZeroDivisionError):
                returns.append("0.0")
        
        print(' / '.join(returns))


def main():
    """
    Main entry point for the script.
    Routes to appropriate function based on command-line arguments.
    """
    if len(sys.argv) < 2:
        print("Error: No function specified")
        print("Usage: python mfReturns.py <function> [arguments]")
        print("Available functions:")
        print("  rolling-returns    - Calculate rolling returns")
        print("  point-to-point     - Calculate point to point returns")
        print("  calendar-year      - Calculate calendar year returns")
        return
    
    function_name = sys.argv[1]
    
    if function_name == "point-to-point":
        calculate_point_to_point_returns()
    elif function_name == "calendar-year":
        calculate_calendar_year_returns()
    elif function_name == "rolling-returns":
        calculate_rolling_returns()
    else:
        print(f"Error: Unknown function '{function_name}'")
        print("Available functions:")
        print("  rolling-returns    - Calculate rolling returns")
        print("  point-to-point     - Calculate point to point returns")
        print("  calendar-year      - Calculate calendar year returns")


if __name__ == "__main__":
    main()
