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
import numpy as np
import datetime
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
            
            if len(historical_data) < 2 * required_data_points:
                rolling_returns[year] = {
                    'error': f'Insufficient data (need {required_data_points}, have {len(historical_data)})'
                }
                continue
            
            # Calculate rolling returns.
            # We start from the end of the data and move backwards.
            for start_index in range(len(historical_data) - required_data_points):
                try:
                    initial_index = start_index + year * Constants.TRADING_DAYS_PER_YEAR
                    initial_nav = float(historical_data[initial_index]['nav'])
                    final_nav = float(historical_data[start_index]['nav'])
                    
                    if initial_nav == 0 or final_nav == 0:
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
                    'min': round(np.min(cagr_values), Constants.DECIMAL_PLACES),
                    'avg': round(np.mean(cagr_values), Constants.DECIMAL_PLACES),
                    'max': round(np.max(cagr_values), Constants.DECIMAL_PLACES)
                }
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'rolling_returns': rolling_returns
        }
    
    def _calculate_calendar_year_returns(self):
        """
        Calculate calendar year returns for the last 5 years using stored scheme data.
        
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

                if initial_nav == 0 or final_nav == 0:
                    calendar_returns[year] = None
                    continue

                return_percent = (final_nav - initial_nav) * 100 / initial_nav
                calendar_returns[year] = round(return_percent, Constants.DECIMAL_PLACES)

            except (ValueError, KeyError, IndexError, ZeroDivisionError):
                calendar_returns[year] = None
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'calendar_returns': calendar_returns
        }
    
    def _calculate_static_sharpe_ratio(self):
        """
        Calculate annualized Static Sharpe Ratio.
        The Static Sharpe Ratio measures the excess return earned per unit of volatility over the entire period.

        Calculation methodology for each period:
        1. Compute daily returns from consecutive NAV values
        2. Calculate arithmetic mean of daily returns
        3. Annualize the mean return: Annualized Return = Mean Daily Return x Trading Days x 100
        4. Calculate standard deviation of daily returns
        5. Annualize volatility: Annualized Volatility = Std Dev x √Trading Days x 100
        6. Apply Sharpe Ratio formula: (Annualized Return - Risk-free Rate) / Annualized Volatility

        Result interpretation:
        Static Sharpe   Interpretation  What it actually means
        -------------   --------------  ----------------------
        > 1.5           Exceptional     Rare skill or strong market tailwind
        1.0 - 1.5       Very good       Strong risk-adjusted performance
        0.7 - 1.0       Good            Acceptable efficiency
        0.4 - 0.7       Weak            Marginal value add
        0 - 0.4         Poor            Barely beats risk-free
        < 0             Bad             Value destruction
        
        Uses the most recent N years of daily NAV data for each period (1, 3, 5 years).
        All values are converted to decimal for consistency.
        
        Returns:
            Dictionary with scheme_name and static_sharpe_ratios data, or None if error occurs.
            static_sharpe_ratios is a dictionary mapping year to Sharpe Ratio value or error message.
        """
        if self.scheme_data is None:
            return None
        
        historical_data = self.scheme_data['data']
        static_sharpe_ratios = {}
        
        for year in Constants.STATIC_SHARPE_RATIO_YEARS:
            end_date = datetime.datetime.strptime(historical_data[0]['date'], "%d-%m-%Y")
            start_date = end_date - datetime.timedelta(days=365 * year)
            
            # Use only the last N years of data (most recent data)
            # NAV data is ordered with most recent first (index 0), so we reverse it for chronological order
            recent_data = [
                d for d in historical_data
                if datetime.datetime.strptime(d['date'], "%d-%m-%Y") >= start_date
            ]
            chronological_data = list(reversed(recent_data))  # Reverse to get oldest first
            
            # Step 1: Calculate daily returns
            daily_returns = []
            
            for i in range(len(chronological_data) - 1):
                try:
                    # Data is in chronological order (oldest first)
                    nav_yesterday = float(chronological_data[i]['nav'])
                    nav_today = float(chronological_data[i + 1]['nav'])
                    
                    if nav_yesterday == 0 or nav_today == 0:
                        continue
                    
                    # Calculate daily return
                    daily_return = (nav_today - nav_yesterday) / nav_yesterday
                    daily_returns.append(daily_return)
                    
                except (ValueError, KeyError, IndexError, ZeroDivisionError):
                    continue
            
            # Need at least 2 data points to calculate standard deviation
            if len(daily_returns) < 2:
                static_sharpe_ratios[year] = {
                    'error': 'Insufficient daily data points for Sharpe Ratio calculation'
                }
                continue
            
            try:
                # Step 2: Calculate mean of daily returns
                mean_daily_return = np.mean(daily_returns)
                
                # Step 3: Annualize return (convert to percentage)
                annualized_return = mean_daily_return * Constants.TRADING_DAYS_PER_YEAR
                
                # Step 4: Compute population standard deviation of daily returns
                std_dev_daily = np.std(daily_returns, ddof=0)
                
                # Check for zero standard deviation
                if std_dev_daily == 0:
                    static_sharpe_ratios[year] = {
                        'error': 'Standard deviation of daily returns is zero'
                    }
                    continue
                
                # Step 5: Calculate annualized volatility (convert to percentage)
                annualized_volatility = std_dev_daily * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                # Step 6: Apply formula: Sharpe = (Annualized return - Risk-free rate) / Annualized volatility
                sharpe_ratio = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
                
                static_sharpe_ratios[year] = round(sharpe_ratio, Constants.DECIMAL_PLACES)
                
            except (ValueError, ZeroDivisionError) as e:
                static_sharpe_ratios[year] = {
                    'error': f'Error calculating Sharpe Ratio: {e}'
                }
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'static_sharpe_ratios': static_sharpe_ratios
        }
    
    def _calculate_rolling_sharpe_ratio(self):
        """
        Calculate rolling Sharpe Ratio.
        A rolling Sharpe ratio measures an investment's risk-adjusted return over a moving, fixed-length time window rather than a single static period.

        Result interpretation:
        
        1. Median Rolling Sharpe (primary quality metric)
        Median Rolling Sharpe   Interpretation  Meaning
        ---------------------   --------------  -------
        > 1.0                   Excellent       Strong, repeatable risk-adjusted performance
        0.7 - 1.0               Very Good       Consistent value creation
        0.4 - 0.7               Acceptable      Moderate fund quality
        0.2 - 0.4               Weak            Marginal risk-adjusted returns
        0 - 0.2                 Poor            Barely beats risk-free
        < 0                     Bad             Risk-adjusted value destruction

        2. Percentage of Time Rolling Sharpe > 0 (consistency)
        % Time Sharpe > 0       Interpretation  Meaning
        -----------------       --------------  -------
        > 75%                   Excellent       Adds value most of the time
        65 - 75%                Good            Reliable performance
        55 - 65%                Borderline      Inconsistent
        45 - 55%                Weak            Random-like behavior
        < 45%                   Poor            Unreliable fund

        3. 10th Percentile Rolling Sharpe (downside behavior)
        10th Percentile Sharpe  Interpretation  Meaning
        ----------------------  --------------  -------
        > 0                     Excellent       No destructive regimes
        0 to -0.3               Acceptable      Mild stress periods
        -0.3 to -0.6            Weak            Painful drawdowns
        < -0.6                  Poor            Severe downside risk

        4. Latest Rolling Sharpe (current regime indicator)
        Latest Rolling Sharpe   Interpretation  Action
        ---------------------   --------------  ------
        > 0.7                   Strong          Add / Hold
        0.3 - 0.7               Stable          Hold
        0 - 0.3                 Weak            Monitor
        < 0                     Negative        Avoid fresh investment / Review

        5. Mean vs Median Rolling Sharpe (stability check)
        Mean - Median           Interpretation  Insight
        -------------           --------------  -------
        approx 0                Stable          Consistent performance
        Positive                Skewed          Few good periods inflate average
        Negative                Deteriorating   Recent performance weakening
        
        Returns:
            Dictionary with scheme_name and rolling_sharpe_ratios data, or None if error occurs.
            rolling_sharpe_ratios is a list of dictionaries with:
            - 'total_data': total years of data considered
            - 'rolling_window': window size in years
            - 'median': median Sharpe Ratio
            - 'mean': mean Sharpe Ratio
            - 'positive_share': percentage of time Sharpe Ratio > 0
            - 'percentile_10': 10th percentile Sharpe Ratio
            - 'latest': latest rolling Sharpe Ratio
            - 'error': error message if calculation failed
        """
        if self.scheme_data is None:
            return None
        
        historical_data = self.scheme_data['data']
        rolling_sharpe_ratios = []
        
        for config in Constants.ROLLING_SHARPE_RATIO_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Calculate start date for data filtering
            end_date = datetime.datetime.strptime(historical_data[0]['date'], "%d-%m-%Y")
            start_date = end_date - datetime.timedelta(days=365 * total_years)
            
            # Filter data
            relevant_data = [
                d for d in historical_data
                if datetime.datetime.strptime(d['date'], "%d-%m-%Y") >= start_date
            ]
            chronological_data = list(reversed(relevant_data))
            
            # Calculate daily returns
            daily_returns = []
            for i in range(len(chronological_data) - 1):
                try:
                    nav_yesterday = float(chronological_data[i]['nav'])
                    nav_today = float(chronological_data[i + 1]['nav'])
                    
                    if nav_yesterday == 0 or nav_today == 0:
                        continue
                        
                    daily_return = (nav_today - nav_yesterday) / nav_yesterday
                    daily_returns.append(daily_return)
                except (ValueError, KeyError, IndexError, ZeroDivisionError):
                    continue
            
            # Define window size (trading days)
            window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
            
            if len(daily_returns) < window_size:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(daily_returns)})'
                })
                continue
            
            # Calculate rolling Sharpe Ratios
            window_sharpes = []
            for i in range(len(daily_returns) - window_size + 1):
                window = daily_returns[i : i + window_size]
                
                if not window:
                    continue
                
                # Check for zero variance to avoid division by zero
                std_dev = np.std(window, ddof=0)
                if std_dev == 0:
                    continue
                
                mean_return = np.mean(window)
                annualized_return = mean_return * Constants.TRADING_DAYS_PER_YEAR
                annualized_volatility = std_dev * math.sqrt(Constants.TRADING_DAYS_PER_YEAR)
                
                sharpe = (annualized_return - Constants.RISK_FREE_RATE) / annualized_volatility
                window_sharpes.append(sharpe)
            
            if not window_sharpes:
                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': 'Could not calculate valid Sharpe Ratios'
                })
            else:
                median_val = round(np.median(window_sharpes), Constants.DECIMAL_PLACES)
                mean_val = round(np.mean(window_sharpes), Constants.DECIMAL_PLACES)
                percentile_10_val = round(np.percentile(window_sharpes, 10), Constants.DECIMAL_PLACES)
                latest_val = round(window_sharpes[-1], Constants.DECIMAL_PLACES)

                rolling_sharpe_ratios.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'median': median_val,
                    'mean': mean_val,
                    'positive_share': round((len([s for s in window_sharpes if s > 0]) / len(window_sharpes)) * 100, Constants.DECIMAL_PLACES),
                    'percentile_10': percentile_10_val,
                    'latest': latest_val
                })
        
        return {
            'scheme_name': self.scheme_data['scheme_name'],
            'rolling_sharpe_ratios': rolling_sharpe_ratios
        }
    
    def _print_returns(self, rolling_data, calendar_data, static_sharpe_data, rolling_sharpe_data=None):
        """
        Print the returns data for a scheme in a formatted way.
        
        Prints rolling returns (min/avg/max CAGR), calendar year returns, Sharpe Ratio,
        and Rolling Sharpe Ratio in a formatted table format.
        
        Args:
            rolling_data: Dictionary returned by _calculate_rolling_returns(), or None
            calendar_data: Dictionary returned by _calculate_calendar_year_returns(), or None
            static_sharpe_data: Dictionary returned by _calculate_static_sharpe_ratio(), or None
            rolling_sharpe_data: Dictionary returned by _calculate_rolling_sharpe_ratio(), or None
        """
        if rolling_data is None and calendar_data is None and static_sharpe_data is None and rolling_sharpe_data is None:
            return
        
        scheme_name = (
            rolling_data['scheme_name'] if rolling_data else
            calendar_data['scheme_name'] if calendar_data else
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
        
        rolling_data = self._calculate_rolling_returns()
        calendar_data = self._calculate_calendar_year_returns()
        static_sharpe_data = self._calculate_static_sharpe_ratio()
        rolling_sharpe_data = self._calculate_rolling_sharpe_ratio()
        self._print_returns(rolling_data, calendar_data, static_sharpe_data, rolling_sharpe_data)


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
