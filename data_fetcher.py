import json
from mftool import Mftool
from typing import Dict, Any, Optional

class DataFetcher:
    """
    Fetcher class to retrieve mutual fund scheme and benchmark data.
    
    Provides methods to fetch historical NAV data using Mftool.
    """
    
    @staticmethod
    def fetch_scheme_data(scheme_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical NAV data for the scheme.
        
        Args:
            scheme_code: Mutual fund scheme code
            
        Returns:
            Dictionary containing scheme data with the following keys:
            - fund_house
            - scheme_type
            - scheme_category
            - scheme_code
            - scheme_name
            - scheme_start_date
            - data (list of NAV entries)

            Returns None if error occurs.
        """
        mf_tool = Mftool()
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

    @staticmethod
    def fetch_benchmark_data(index_code: str = "NIFTY 50") -> Optional[Dict[str, Any]]:
        """
        Fetch historical data for a benchmark index.
        
        Args:
            index_code: Benchmark index code (default "NIFTY 50")
            
        Returns:
            Dictionary containing benchmark data with 'data' key (list of entries with 'date' and 'nav').
            Currently returns None as benchmark fetching is not implemented.
        """
        # TODO: Implement benchmark data fetching
        print(f"Warning: Benchmark data fetching for {index_code} is not yet implemented.")
        return None
