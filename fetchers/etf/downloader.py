# -*- coding: utf-8 -*-
"""
Price data downloader for ETF analytics.
Handles yfinance downloads and period-to-date conversion.
"""

import logging
import datetime
import pandas as pd
import yfinance as yf
from typing import List, Optional

logger = logging.getLogger(__name__)

# Expected trading days per period — used for iloc[-n:] slicing after alignment.
# Ensures both ETF and benchmark cover the exact same trading window.
_TRADING_DAYS = {"6mo": 126, "1y": 252, "3y": 756, "5y": 1260}


def _period_to_dates(period: str):
    """
    Convert a period string ("6mo", "1y", "3y", "5y") to a (start, end) date tuple.

    Fetches 2× the requested period so that after inner-join alignment between
    the benchmark (NYSE calendar) and ETF (NSE calendar), at least the required
    number of common trading days remain for slicing.
    """
    end = datetime.date.today()
    days = {"6mo": 366, "1y": 730, "3y": 2190, "5y": 3650}
    delta = days.get(period, 730)
    return end - datetime.timedelta(days=delta), end


def _download(ticker: str, start: datetime.date, end: datetime.date) -> Optional[pd.Series]:
    """
    Download adjusted close prices for a single ticker over an explicit date range.
    Uses auto_adjust=True to get dividend/split-adjusted prices.
    Returns None if no data is available.
    """
    try:
        df = yf.download(ticker, start=start, end=end,
                         auto_adjust=True, progress=False)
        if df.empty:
            logger.warning("No data for ticker '%s'", ticker)
            return None
        return df["Close"].squeeze().dropna()
    except Exception as e:
        logger.error("Failed to download '%s': %s", ticker, e)
        return None


def _download_batch(tickers: List[str], start: datetime.date,
                    end: datetime.date) -> pd.DataFrame:
    """
    Download adjusted close prices for multiple tickers in one API call.
    Drops columns that are entirely NaN (unavailable/delisted tickers).
    """
    try:
        df = yf.download(tickers, start=start, end=end,
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        prices = df["Close"]
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=tickers[0])
        return prices.dropna(axis=1, how="all")
    except Exception as e:
        logger.error("Failed batch download: %s", e)
        return pd.DataFrame()
