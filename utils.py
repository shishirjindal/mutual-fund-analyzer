
class Utils:
    """
    Utility class for financial calculations and helper methods.
    
    Provides static methods for common financial formulas used across the application.
    """
    @staticmethod
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

    @staticmethod
    def calculate_daily_returns(chronological_data):
        """
        Calculate daily returns from chronological NAV data.
        
        Args:
            chronological_data: List of dictionaries containing 'nav' key, sorted by date (oldest first)
            
        Returns:
            List of daily returns (floats)
        """
        daily_returns = []
        for i in range(len(chronological_data) - 1):
            try:
                nav_yesterday = float(chronological_data[i]['nav'])
                nav_today = float(chronological_data[i + 1]['nav'])
                
                if nav_yesterday == 0 or nav_today == 0:
                    continue
                
                # Calculate daily return
                daily_return = (nav_today - nav_yesterday) / nav_yesterday
                daily_returns.append(daily_return)
                
            except (ValueError, KeyError, IndexError, ZeroDivisionError):
                continue
        return daily_returns
