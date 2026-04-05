# -*- coding: utf-8 -*-
"""
Benchmark builder for ETF analytics.

Builds the commodity price series in INR by combining the USD spot price
(GLD/SLV) with the USD/INR exchange rate.

Why GLD/SLV instead of futures (GC=F/SI=F):
  Futures contracts roll between expiry months, causing artificial price jumps
  on roll dates that inflate return calculations. GLD/SLV track spot prices
  continuously without roll effects.

Why inner join before multiplying:
  GLD trades on NYSE and USDINR=X on forex markets — they have slightly
  different trading calendars. Multiplying misaligned series would pair
  different days' prices. Inner join ensures each row uses the same date.
"""

import logging
import datetime
import pandas as pd
from typing import Optional

from constants.etf_constants import GOLD_BENCHMARK_TICKER, SILVER_BENCHMARK_TICKER, USD_INR_TICKER
from etf.downloader import _download

logger = logging.getLogger(__name__)


def _build_benchmark(commodity: str, start: datetime.date,
                     end: datetime.date) -> Optional[pd.Series]:
    """
    Build the commodity price series in INR.

    Steps:
      1. Download commodity USD price (GLD or SLV) and USDINR=X independently.
      2. Align on inner join — never multiply misaligned series.
      3. commodity_inr = commodity_usd × usd_inr

    Returns a price series in INR on the benchmark's own trading calendar.
    """
    ticker        = GOLD_BENCHMARK_TICKER if commodity == "gold" else SILVER_BENCHMARK_TICKER
    commodity_usd = _download(ticker, start, end)
    usd_inr       = _download(USD_INR_TICKER, start, end)

    if commodity_usd is None or usd_inr is None:
        return None

    df = pd.concat([commodity_usd, usd_inr], axis=1, join="inner").dropna()
    if df.empty:
        return None
    df.columns = ["commodity_usd", "usd_inr"]
    return (df["commodity_usd"] * df["usd_inr"]).dropna()
