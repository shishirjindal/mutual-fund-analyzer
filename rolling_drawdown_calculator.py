import pandas as pd
from typing import Dict, Any
from constants import Constants
from utils import Utils

class RollingDrawdownCalculator:
    """Calculates rolling Maximum Drawdown for mutual funds using Pandas."""
    
    @staticmethod
    def calculate(scheme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rolling Maximum Drawdown for configurations defined in Constants.ROLLING_DRAWDOWN_MAP.
        
        Args:
            scheme_data: Dictionary containing scheme data
            
        Returns:
            List of dictionaries containing rolling Max Drawdown stats.
        """
        df = Utils.convert_to_dataframe(scheme_data)
        
        rolling_drawdowns = []
        
        if df is None or df.empty:
            for config in Constants.ROLLING_DRAWDOWN_MAP:
                rolling_drawdowns.append({
                    'total_data': config['total_data'],
                    'rolling_window': config['rolling_window'],
                    'error': 'No data available'
                })
            return rolling_drawdowns
            
        for config in Constants.ROLLING_DRAWDOWN_MAP:
            total_years = config['total_data']
            window_years = config['rolling_window']
            
            # Filter data for total years
            end_date = df.index[-1]
            start_date = end_date - pd.Timedelta(days=365 * total_years)
            relevant_df = df[df.index >= start_date].copy()
            
            if relevant_df.empty:
                rolling_drawdowns.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data for {total_years} years'
                })
                continue
                
            # Window size in trading days
            window_size = window_years * Constants.TRADING_DAYS_PER_YEAR
            
            if len(relevant_df) < window_size:
                rolling_drawdowns.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Insufficient data (need {window_size} days, have {len(relevant_df)})'
                })
                continue
                
            try:
                # Calculate rolling max drawdown
                # We use apply with a helper function to calculate MDD for each window
                # MDD = min(NAV / cumulative_max_NAV - 1)
                def calc_mdd(x):
                    return (x / x.cummax() - 1).min()
                
                rolling_mdd = relevant_df['nav'].rolling(window=window_size).apply(calc_mdd, raw=False)
                
                # Convert to percentage
                rolling_mdd_pct = rolling_mdd * 100
                
                # Filter valid values
                valid_mdds = rolling_mdd_pct.dropna()
                
                if valid_mdds.empty:
                    rolling_drawdowns.append({
                        'total_data': total_years,
                        'rolling_window': window_years,
                        'error': 'Could not calculate valid Drawdown values'
                    })
                else:
                    rolling_drawdowns.append({
                        'total_data': total_years,
                        'rolling_window': window_years,
                        # Note: MDD is negative, so 'min' is the worst drawdown (largest absolute value)
                        # 'max' is the best drawdown (closest to zero)
                        'median': round(valid_mdds.median(), Constants.DECIMAL_PLACES),
                        'mean': round(valid_mdds.mean(), Constants.DECIMAL_PLACES),
                        'percentile_75': round(valid_mdds.quantile(0.75), Constants.DECIMAL_PLACES),
                        'min': round(valid_mdds.min(), Constants.DECIMAL_PLACES),
                        'max': round(valid_mdds.max(), Constants.DECIMAL_PLACES),
                        'latest': round(valid_mdds.iloc[-1], Constants.DECIMAL_PLACES)
                    })
                    
            except Exception as e:
                rolling_drawdowns.append({
                    'total_data': total_years,
                    'rolling_window': window_years,
                    'error': f'Error calculating Rolling Drawdown: {str(e)}'
                })
                
        return rolling_drawdowns
