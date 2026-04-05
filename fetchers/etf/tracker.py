# -*- coding: utf-8 -*-
"""
ETF tracking metrics calculator — multi-period evaluation.

Metric period rules:
  Tracking Difference (TD):
    - 1Y (primary) + 3Y (consistency check)
    - tracking_score = 0.7 * td_score_1y + 0.3 * td_score_3y
    - If 3Y data unavailable, falls back to 1Y only
    - 6mo NOT used for TD (too noisy)

  Tracking Error (TE):
    - Computed over 1Y (daily + weekly variants)
    - Not computed over >1Y (long periods add calendar noise without benefit)

  Liquidity:
    - Last 60 trading days average volume (recent, not stale)

  Expense Ratio / AUM:
    - Current values (no time dimension)

Calendar mismatch note:
  GLD/SLV trade on NYSE; Indian ETFs trade on NSE. A shift(1) is applied to
  benchmark daily returns to account for the ~half-day timezone gap.
"""

import logging
import numpy as np
import pandas as pd
import yfinance as yf
import datetime
from typing import Dict, Optional, Tuple

from fetchers.etf.downloader import _download

logger = logging.getLogger(__name__)

_MIN_DATA_POINTS    = 200
_MIN_DATA_POINTS_3Y = 500   # minimum rows needed to attempt 3Y TD

# Exact trading-day windows for each period
_TRADING_DAYS = {"6mo": 126, "1y": 252, "3y": 756, "5y": 1260}

# Validation thresholds (normal-year expectations, warnings only)
_BENCH_RET_MIN = -20.0
_BENCH_RET_MAX =  40.0
_ETF_DIFF_MAX  =   5.0
_TE_MAX        =   2.0
_CORR_MIN      =   0.95


def _is_anomalous_split(prices: pd.Series, peer_prices: pd.DataFrame) -> bool:
    """
    Detect ETFs with unadjusted stock splits.
    Flags any ETF whose period return deviates > 50pp from the peer median.
    """
    if peer_prices.empty or len(prices) < 2:
        return False
    etf_ret   = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
    peer_rets = (peer_prices.iloc[-1] / peer_prices.iloc[0] - 1) * 100
    return abs(etf_ret - peer_rets.median()) > 50


def _compute_td(df_aligned: pd.DataFrame, n_days: int) -> Optional[float]:
    """
    Compute Tracking Difference (%) over the last n_days of an aligned df.
    Returns None if insufficient data.
    """
    if len(df_aligned) < n_days:
        return None
    window = df_aligned.iloc[-n_days:]
    etf_ret   = (window["etf"].iloc[-1]       / window["etf"].iloc[0]       - 1) * 100
    bench_ret = (window["benchmark"].iloc[-1] / window["benchmark"].iloc[0] - 1) * 100
    return round(etf_ret - bench_ret, 3)


def _compute_te(df_aligned: pd.DataFrame, n_days: int) -> Tuple[float, float, float]:
    """
    Compute daily and weekly Tracking Error (annualized %) and correlation
    over the last n_days of an aligned df.
    Returns (te_daily, te_weekly, correlation).
    """
    window = df_aligned.iloc[-n_days:]

    # Daily TE with timezone shift
    ret = window.pct_change(fill_method=None).dropna()
    ret["benchmark"] = ret["benchmark"].shift(1)
    ret = ret.dropna()
    diff = ret["etf"] - ret["benchmark"]
    te_daily = diff.std() * np.sqrt(252) * 100
    corr     = ret.corr().iloc[0, 1]

    # Weekly TE (more stable)
    ret_w = window.resample("W").last().pct_change(fill_method=None).dropna()
    ret_w["benchmark"] = ret_w["benchmark"].shift(1)
    ret_w = ret_w.dropna()
    te_weekly = (ret_w["etf"] - ret_w["benchmark"]).std() * np.sqrt(52) * 100

    return round(te_daily, 2), round(te_weekly, 2), round(corr, 4)


def _avg_volume_60d(ticker: str, end: datetime.date) -> int:
    """
    Fetch last 60 trading days average volume from yfinance.
    Falls back to averageVolume from info if price history unavailable.
    """
    start = end - datetime.timedelta(days=100)  # fetch extra to get 60 trading days
    try:
        df = yf.download(ticker, start=start, end=end,
                         auto_adjust=True, progress=False)
        if not df.empty and "Volume" in df.columns:
            vol = df["Volume"].squeeze().dropna()
            return int(vol.iloc[-60:].mean()) if len(vol) >= 10 else 0
    except Exception:
        pass
    # Fallback to info
    return int(yf.Ticker(ticker).info.get("averageVolume") or 0)


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
    Compute multi-period tracking metrics for a single ETF.

    Multi-period rules:
      TD:  1Y (primary) + 3Y (consistency). tracking_score = 0.7*td_1y + 0.3*td_3y.
           Falls back to 1Y only if 3Y data unavailable.
      TE:  1Y window only (daily + weekly).
      Vol: Last 60 trading days average.

    Returns a dict with all metrics plus warnings list.
    """
    # Download enough history for 3Y TD (need ~4Y raw to get 756 common days)
    fetch_start = end - datetime.timedelta(days=4 * 365)
    etf_prices  = _download(ticker, fetch_start, end)

    if etf_prices is None or len(etf_prices) < _MIN_DATA_POINTS:
        n = len(etf_prices) if etf_prices is not None else 0
        return {"name": name, "ticker": ticker, "error": f"Insufficient data ({n} days)"}

    if _is_anomalous_split(etf_prices, peer_prices):
        logger.warning("Skipping '%s' — likely unadjusted split", name)
        return {"name": name, "ticker": ticker, "error": "Unadjusted split detected"}

    # Align ETF and benchmark on common trading dates
    df = pd.concat([benchmark_inr, etf_prices], axis=1, join="inner").dropna()
    df.columns = ["benchmark", "etf"]

    if len(df) < _MIN_DATA_POINTS:
        return {"name": name, "ticker": ticker,
                "error": f"Insufficient overlapping data ({len(df)} days)"}

    # ── Tracking Difference: 1Y (primary) + 3Y (consistency) ─────────────────
    td_1y = _compute_td(df, _TRADING_DAYS["1y"])
    td_3y = _compute_td(df, _TRADING_DAYS["3y"])  # None if < 756 common days

    if td_1y is None:
        return {"name": name, "ticker": ticker, "error": "Insufficient 1Y data for TD"}

    # Normalize TD to 0–100 score (lower abs TD = higher score)
    td_score_1y = max(0.0, 100 - abs(td_1y) * 20)
    if td_3y is not None:
        td_score_3y    = max(0.0, 100 - abs(td_3y) * 20)
        tracking_score = round(0.7 * td_score_1y + 0.3 * td_score_3y, 2)
        logger.debug("[%s] TD 1Y=%.3f%% 3Y=%.3f%% → tracking_score=%.1f",
                     name, td_1y, td_3y, tracking_score)
    else:
        tracking_score = round(td_score_1y, 2)
        logger.debug("[%s] TD 1Y=%.3f%% (no 3Y data) → tracking_score=%.1f",
                     name, td_1y, tracking_score)

    # ── Tracking Error: 1Y window ─────────────────────────────────────────────
    te_daily, te_weekly, corr = _compute_te(df, _TRADING_DAYS["1y"])

    # ── Period returns for display (use user-selected period) ─────────────────
    n_display = _TRADING_DAYS.get(period, 252)
    bench_ret = None
    etf_ret   = None
    if len(df) >= n_display:
        w = df.iloc[-n_display:]
        bench_ret = round((w["benchmark"].iloc[-1] / w["benchmark"].iloc[0] - 1) * 100, 2)
        etf_ret   = round((w["etf"].iloc[-1]       / w["etf"].iloc[0]       - 1) * 100, 2)

    # ── Validation warnings ───────────────────────────────────────────────────
    warnings = []
    if bench_ret is not None and not (_BENCH_RET_MIN <= bench_ret <= _BENCH_RET_MAX):
        warnings.append(
            f"Benchmark return {bench_ret:.1f}% outside normal range "
            f"[{_BENCH_RET_MIN}%, {_BENCH_RET_MAX}%] — may reflect exceptional market conditions"
        )
    if td_1y is not None and abs(td_1y) > _ETF_DIFF_MAX:
        warnings.append(f"1Y tracking difference {td_1y:.2f}% exceeds ±{_ETF_DIFF_MAX}%")
    if te_daily > _TE_MAX:
        warnings.append(
            f"Market TE {te_daily:.2f}% > {_TE_MAX}% — structurally high due to NYSE/NSE "
            f"timezone differences; not comparable to AMC-reported NAV-based TE"
        )
    if corr < _CORR_MIN:
        warnings.append(
            f"Correlation {corr:.3f} < {_CORR_MIN} — NYSE/NSE calendar gap effect on daily data"
        )
    for w in warnings:
        logger.warning("[%s] %s", name, w)

    # ── Liquidity: last 60 trading days ──────────────────────────────────────
    avg_vol = _avg_volume_60d(ticker, end)

    return {
        "name":                   name,
        "ticker":                 ticker,
        "current_price":          round(float(etf_prices.iloc[-1]), 2),
        "etf_return":             etf_ret,
        "benchmark_return":       bench_ret,
        # Multi-period TD
        "td_1y":                  td_1y,
        "td_3y":                  td_3y,
        "tracking_score":         tracking_score,
        # Keep tracking_difference as alias for td_1y (used by scorer/cost model)
        "tracking_difference":    td_1y,
        # TE (1Y window)
        "market_tracking_error":  te_daily,
        "weekly_tracking_error":  te_weekly,
        "correlation":            corr,
        # Liquidity (60-day)
        "avg_volume":             avg_vol,
        "avg_traded_value":       round(float(etf_prices.iloc[-1]) * avg_vol, 2),
        "warnings":               warnings,
    }
