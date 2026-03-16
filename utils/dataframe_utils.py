from typing import Dict, Any, Optional
import pandas as pd
from constants.constants import Constants
from utils.return_utils import calculate_daily_returns  # noqa: F401 — re-exported for convenience


class DataFrameUtils:
    """Utility methods for converting and aligning NAV DataFrames."""

    @staticmethod
    def convert_to_dataframe(scheme_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Convert scheme/benchmark data dict to a Pandas DataFrame.
        Returns DataFrame with DateTime index and 'nav' column, or None if invalid.
        """
        if scheme_data is None or 'data' not in scheme_data or not scheme_data['data']:
            return None

        try:
            df = pd.DataFrame(scheme_data['data'])
            if 'date' not in df.columns or 'nav' not in df.columns:
                return None

            df['date'] = pd.to_datetime(df['date'], format=Constants.DATE_FORMAT)
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            df.set_index('date', inplace=True)
            df.sort_index(ascending=True, inplace=True)
            df.dropna(subset=['nav'], inplace=True)
            df = df[df['nav'] != 0]
            return df
        except Exception:
            return None

    @staticmethod
    def align_dataframes(scheme_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Align scheme and benchmark DataFrames by date using an inner join.
        Returns DataFrame with 'scheme_nav' and 'benchmark_nav' columns, or None.
        """
        df_scheme = DataFrameUtils.convert_to_dataframe(scheme_data)
        df_benchmark = DataFrameUtils.convert_to_dataframe(benchmark_data)

        if df_scheme is None or df_scheme.empty or df_benchmark is None or df_benchmark.empty:
            return None

        combined_df = pd.merge(
            df_scheme['nav'].rename('scheme_nav'),
            df_benchmark['nav'].rename('benchmark_nav'),
            left_index=True,
            right_index=True,
            how='inner',
        )
        return combined_df if not combined_df.empty else None


# Module-level aliases so calculators can call the functions directly
convert_to_dataframe = DataFrameUtils.convert_to_dataframe
align_dataframes = DataFrameUtils.align_dataframes
