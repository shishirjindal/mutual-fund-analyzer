# -*- coding: utf-8 -*-
"""
ETF tracking metrics calculator.

Computes per-ETF tracking metrics against the commodity INR benchmark:
  - Tracking Difference (TD): cumulative return gap over the period.
  - Market Tracking Error: annualized std of daily return differences.
  - Weekly Tracking Error: annualized std of weekly return differences
    (more stable; reduces NYSE/NSE timezone noise).

Calendar mismatch note:
  GLD/SLV trade on NYSE (US hours); Indian ETFs trade on NSE (Indian hours).
  A shift(1) is applied to benchmark daily returns: NSE Tuesday close reflects
  NYSE Monday close. This reduces artificial daily differences caused by the
  ~half-day timezone gap.

Validation thresholds are based on normal-year expectations and logged as
warnings only — 2025-2026 was exceptional (gold +70% INR).
"""

import logging
import numpy as np
import pandas as pd
import yfinance as yf
import datetime
from typing import Dict

from fetchers.etf.downloader import _download, _TRADING_DAYS

logger = logging.getLogger(__name__)

_MIN_DATA_POINTS = 200

# Validation thresholds (normal-year expectations, warnings only)
_BENCH_RET_MIN = -20.0
_BENCH_RET_MAX =  40.0
_ETF_DIFF_MAX  =   5.0
_TE_MAX        =   2.0   # only achievable with NAV data, not market price
_CORR_MIN      =   0.95  # only achievable with NAV data; market price gives ~0.4


def _is_anomalous_split(prices: pd.Series, peer_prices: pd.DataFrame) -> bool:
    """
    Detect ETFs with unadjusted stock splits in Yahoo Finance data.
    Flags any ETF whose period return deviates > 50pp from the peer median.
    Example: LIC Gold ETF had a ~64:1 split; Yahoo shows -98% vs peers at +58%.
    """
    if peer_prices.empty or len(prices) < 2:
        return False
    etf_ret   = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
    peer_rets = (peer_prices.iloc[-1] / peer_prices.iloc[0] - 1) * 100
    return abs(etf_ret - peer_rets.median()) > 50


def compute_etf_metrics(
    name: str,
    ticker: str,
    benchmark_inr: pd.Series,
    peer_prices: pd.DataFrame,
    start: datetime.date,
    end: datetime.date,
    period: str = "1y",
) -> Dict:
    """
    Compute tracking metrics for a single ETF against the commodity INR benchmark.

    Pipeline:
      1. Download ETF market prices (adjusted close).
      2. Detect and skip ETFs with unadjusted splits.
      3. Align ETF and benchmark on inner join (common trading dates only).
      4. Slice to exact trading-day window (iloc[-n:]) — consistent start/end.
      5. Period returns: (last/first) - 1. Unit-independent (% change).
      6. Daily pct_change with shift(1) on benchmark → Tracking Error × √252.
      7. Weekly resample → Weekly Tracking Error × √52.

    Returns a dict with all metrics plus warnings list.
    """
    etf_prices = _download(ticker, start, end)
    if etf_prices is None or len(etf_prices) < _MIN_DATA_POINTS:
        n = len(etf_prices) if etf_prices is not None else 0
        return {"name": name, "ticker": ticker, "error": f"Insufficient data ({n} days)"}

    if _is_anomalous_split(etf_prices, peer_prices):
        logger.warning("Skipping '%s' — likely unadjusted split", name)
        return {"name": name, "ticker": ticker, "error": "Unadjusted split detected"}

    # Align on common trading dates
    df = pd.concat([benchmark_inr, etf_prices], axis=1, join="inner").dropna()
    df.columns = ["benchmark", "etf"]

    # Slice to exact trading-day window
    n_days = _TRADING_DAYS.get(period, 252)
    df = df.iloc[-n_days:]

    if len(df) < _MIN_DATA_POINTS:
        return {"name": name, "ticker": ticker,
                "error": f"Insufficient overlapping data ({len(df)} days)"}

    # Period returns (unit-independent percentage change)
    bench_ret  = (df["benchmark"].iloc[-1] / df["benchmark"].iloc[0] - 1) * 100
    etf_ret    = (df["etf"].iloc[-1]       / df["etf"].iloc[0]       - 1) * 100
    track_diff = etf_ret - bench_ret

    # Daily tracking error with timezone shift
    ret = df.pct_change(fill_method=None).dropna()
    ret["benchmark"] = ret["benchmark"].shift(1)
    ret = ret.dropna()
    diff = ret["etf"] - ret["benchmark"]
    te   = diff.std() * np.sqrt(252) * 100
    corr = ret.corr().iloc[0, 1]

    # Weekly tracking error (more stable)
    ret_w = df.resample("W").last().pct_change(fill_method=None).dropna()
    ret_w["benchmark"] = ret_w["benchmark"].shift(1)
    ret_w = ret_w.dropna()
    te_weekly = (ret_w["etf"] - ret_w["benchmark"]).std() * np.sqrt(52) * 100

    # Validation warnings
    warnings = []
    if not (_BENCH_RET_MIN <= bench_ret <= _BENCH_RET_MAX):
        warnings.append(
            f"Benchmark return {bench_ret:.1f}% outside normal range "
            f"[{_BENCH_RET_MIN}%, {_BENCH_RET_MAX}%] — may reflect exceptional market conditions"
        )
    if abs(track_diff) > _ETF_DIFF_MAX:
        warnings.append(f"Tracking difference {track_diff:.2f}% exceeds ±{_ETF_DIFF_MAX}%")
    if te > _TE_MAX:
        warnings.append(
            f"Market TE {te:.2f}% > {_TE_MAX}% — structurally high due to NYSE/NSE timezone "
            f"and calendar differences; not comparable to AMC-reported NAV-based TE"
        )
    if corr < _CORR_MIN:
        warnings.append(
            f"Correlation {corr:.3f} < {_CORR_MIN} — NYSE/NSE calendar gap effect on daily data"
        )
    for w in warnings:
        logger.warning("[%s] %s", name, w)

    # Fetch volume info (single call, reuse ticker object)
    info       = yf.Ticker(ticker).info
    avg_volume = int(info.get("averageVolume") or 0)

    return {
        "name":                   name,
        "ticker":                 ticker,
        "current_price":          round(float(etf_prices.iloc[-1]), 2),
        "etf_return":             round(float(etf_ret), 2),
        "benchmark_return":       round(float(bench_ret), 2),
        "tracking_difference":    round(float(track_diff), 3),
        "market_tracking_error":  round(float(te), 2),
        "weekly_tracking_error":  round(float(te_weekly), 2),
        "correlation":            round(float(corr), 4),
        "data_points":            len(ret),
        "avg_volume":             avg_volume,
        "avg_traded_value":       round(float(etf_prices.iloc[-1]) * avg_volume, 2),
        "warnings":               warnings,
    }
