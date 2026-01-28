import json
from mftool import Mftool
from typing import Dict, Any, Optional

class SchemeDataFetcher:
    """
    Fetcher class to retrieve mutual fund scheme data.
    
    Provides methods to fetch historical NAV data using Mftool.
    """
    
    @staticmethod
    def fetch_scheme_data(scheme_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical NAV data for the scheme.
        
        Args:
            scheme_code: Mutual fund scheme code
            
        Returns:
            Dictionary containing scheme data with keys 'meta' (scheme details) and 
            'data' (list of NAV entries), or None if error occurs.
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
