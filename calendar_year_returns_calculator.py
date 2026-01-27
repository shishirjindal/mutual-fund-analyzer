from constants import Constants

class CalendarYearReturnsCalculator:
    """Calculates calendar year returns for mutual funds."""
    
    @staticmethod
    def calculate(scheme_data, years_to_calculate):
        """
        Calculate calendar year returns for the last 5 years using stored scheme data.
        
        Args:
            scheme_data: Dictionary containing scheme data
            years_to_calculate: List of years to calculate returns for
            
        Returns:
            Dictionary with scheme_name and calendar_returns data, or None if error occurs.
        """
        if scheme_data is None:
            return None
        
        # Create a date-to-NAV lookup dictionary for faster access
        nav_lookup = {entry['date']: float(entry['nav']) for entry in scheme_data['data']}
        calendar_returns = {}
        
        for year in years_to_calculate:
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
            'scheme_name': scheme_data['scheme_name'],
            'calendar_returns': calendar_returns
        }
