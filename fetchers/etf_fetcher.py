# -*- coding: utf-8 -*-
"""
ETF Fetcher — downloads price data and computes tracking metrics via yfinance.

Benchmark source:
  Gold:   GLD  (SPDR Gold Shares, USD) — spot gold proxy, no futures roll effects
  Silver: SLV  (iShares Silver Trust, USD) — spot silver proxy
  Both are multiplied by USDINR=X to convert to INR.

Why spot ETF proxies (GLD/SLV) instead of futures (GC=F/SI=F):
  Futures contracts roll between expiry months, causing artificial price jumps
  on roll dates that inflate return calculations. GLD/SLV track spot prices
  continuously without roll effects.

Why returns are compared, not price levels:
  GLD is priced in USD/share (~$430), GOLDBEES in INR/NAV-unit (~₹120).
  These are incomparable absolute values. Percentage returns (pct_change)
  are dimensionless and directly comparable regardless of unit or price level.

Two tracking metrics:
  Tracking Difference (TD):
    = ETF cumulative return − benchmark cumulative return over the period.
    Answers: "How much did the ETF underperform/outperform gold?"
    This is the primary investor-facing metric. Typically <2% for well-run ETFs.

  Tracking Error (TE):
    Two variants are computed:

    market_tracking_error (daily, annualized):
      = std(daily ETF return − daily benchmark return) × √252
      Computed using market prices across different exchanges (NYSE vs NSE),
      which introduces additional noise due to timezone differences, trading
      calendars, and currency timing. This makes the metric structurally higher
      than AMC-reported tracking error, which is based on NAV.
      Typical range with this approach: 30–60% annualized.

    weekly_tracking_error (weekly, annualized):
      = std(weekly ETF return − weekly benchmark return) × √52
      Resampling to weekly returns reduces timezone/calendar noise significantly,
      giving a more stable and interpretable figure.
      Typical range: 5–15% annualized.

    Neither is directly comparable to the <1% TE reported by AMCs, which uses
    official daily NAV data from AMFI/NSE — not market prices.

Calendar mismatch:
  GLD trades on NYSE (US hours); Indian ETFs trade on NSE (Indian hours).
  There is a ~half-day timezone gap. A shift(1) is applied to benchmark
  daily returns to account for this: NSE's Tuesday close reflects GLD's
  Monday close. This reduces artificial daily differences.
"""

import logging
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional

from constants.etf_constants import (
    GOLD_BENCHMARK_TICKER, SILVER_BENCHMARK_TICKER, USD_INR_TICKER,
    ETF_QUALITY_WEIGHTS,
)
from fetchers.etf_metadata_cache import load_etf_metadata, cache_written_date

logger = logging.getLogger(__name__)

# Minimum trading days required for a valid calculation
_MIN_DATA_POINTS = 200

# Validation thresholds — based on normal-year expectations.
# These are logged as warnings only, not hard errors.
# 2025-2026 was an exceptional year: gold returned ~70% in INR,
# well outside the normal -20% to +40% range.
_GOLD_RET_MIN = -20.0   # % — lower bound for a normal year
_GOLD_RET_MAX =  40.0   # % — upper bound for a normal year
_ETF_DIFF_MAX =   5.0   # % — max acceptable abs(TD) before flagging
_TE_MAX       =   2.0   # % annualized — only achievable with NAV data, not market price
_CORR_MIN     =   0.95  # — only achievable with NAV data; market price gives ~0.4


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


# Expected trading days per period — used for iloc[-n:] slicing after alignment.
# This ensures both ETF and benchmark cover the exact same trading window,
# eliminating inflated returns from mismatched start dates.
_TRADING_DAYS = {"6mo": 126, "1y": 252, "3y": 756, "5y": 1260}


def _build_benchmark(commodity: str, start: datetime.date,
                     end: datetime.date) -> Optional[pd.Series]:
    """
    Build the commodity price series in INR.

    Process:
      1. Download commodity USD price (GLD or SLV) and USDINR=X independently.
      2. Align both on their common trading dates (inner join) — never multiply
         misaligned series, as that would pair different days' prices.
      3. Multiply: commodity_inr = commodity_usd × usd_inr

    Returns a price series in INR on the benchmark's own trading calendar.
    """
    ticker = GOLD_BENCHMARK_TICKER if commodity == "gold" else SILVER_BENCHMARK_TICKER
    commodity_usd = _download(ticker, start, end)
    usd_inr       = _download(USD_INR_TICKER, start, end)

    if commodity_usd is None or usd_inr is None:
        return None

    df = pd.concat([commodity_usd, usd_inr], axis=1, join="inner").dropna()
    if df.empty:
        return None
    df.columns = ["commodity_usd", "usd_inr"]
    return (df["commodity_usd"] * df["usd_inr"]).dropna()


def _is_anomalous_split(prices: pd.Series, peer_prices: pd.DataFrame) -> bool:
    """
    Detect ETFs with unadjusted stock splits in Yahoo Finance data.
    Flags any ETF whose period return deviates more than 50pp from the peer median.
    Example: LIC Gold ETF had a ~64:1 split; Yahoo shows -98% return while peers show +58%.
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
      3. Align ETF and benchmark on common trading dates (inner join).
      4. Slice to exact trading-day window (iloc[-n:]) so both series share
         the same start and end date — prevents inflated returns from
         mismatched windows.
      5. Compute period returns: (last / first) - 1. Units cancel out —
         benchmark is INR/share (GLD×USDINR), ETF is INR/NAV-unit; both
         express the same thing as a percentage change.
      6. Compute daily returns via pct_change(). Apply shift(1) to benchmark
         returns to account for NYSE/NSE timezone gap (~half day). Then compute
         Tracking Error = std(diff) × √252.

    Returns a dict with: name, ticker, current_price, etf_return,
    benchmark_return, tracking_difference, tracking_error, correlation,
    data_points, warnings.
    """
    etf_prices = _download(ticker, start, end)
    if etf_prices is None or len(etf_prices) < _MIN_DATA_POINTS:
        n = len(etf_prices) if etf_prices is not None else 0
        return {"name": name, "ticker": ticker, "error": f"Insufficient data ({n} days)"}

    if _is_anomalous_split(etf_prices, peer_prices):
        logger.warning("Skipping '%s' — likely unadjusted split", name)
        return {"name": name, "ticker": ticker, "error": "Unadjusted split detected"}

    # Align on common trading dates (inner join eliminates calendar mismatches)
    df = pd.concat([benchmark_inr, etf_prices], axis=1, join="inner").dropna()
    df.columns = ["benchmark", "etf"]

    # Slice to exact trading-day window — ensures consistent return window
    n_days = _TRADING_DAYS.get(period, 252)
    df = df.iloc[-n_days:]

    if len(df) < _MIN_DATA_POINTS:
        return {"name": name, "ticker": ticker,
                "error": f"Insufficient overlapping data ({len(df)} days)"}

    # Period returns — percentage change, unit-independent
    bench_ret  = (df["benchmark"].iloc[-1] / df["benchmark"].iloc[0] - 1) * 100
    etf_ret    = (df["etf"].iloc[-1]       / df["etf"].iloc[0]       - 1) * 100
    track_diff = etf_ret - bench_ret  # negative = ETF underperformed benchmark

    # Daily returns for Tracking Error
    # shift(1) on benchmark: NSE Tuesday close reflects NYSE Monday close
    ret = df.pct_change(fill_method=None).dropna()
    ret["benchmark"] = ret["benchmark"].shift(1)
    ret = ret.dropna()

    diff = ret["etf"] - ret["benchmark"]
    te   = diff.std() * np.sqrt(252) * 100  # annualized
    corr = ret.corr().iloc[0, 1]

    # Weekly TE — resample to weekly to reduce timezone/calendar noise
    ret_weekly = df.resample("W").last().pct_change(fill_method=None).dropna()
    ret_weekly["benchmark"] = ret_weekly["benchmark"].shift(1)
    ret_weekly = ret_weekly.dropna()
    diff_weekly = ret_weekly["etf"] - ret_weekly["benchmark"]
    te_weekly   = diff_weekly.std() * np.sqrt(52) * 100  # annualized

    # Validation — warnings only, not hard errors
    warnings = []
    if not (_GOLD_RET_MIN <= bench_ret <= _GOLD_RET_MAX):
        warnings.append(
            f"Benchmark return {bench_ret:.1f}% outside normal range "
            f"[{_GOLD_RET_MIN}%, {_GOLD_RET_MAX}%] — may reflect exceptional market conditions"
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
        "avg_volume":             int(yf.Ticker(ticker).info.get("averageVolume") or 0),
        "warnings":               warnings,
    }


def _compute_quality_scores(results: list,
                             expense_ratios: dict,
                             aum_crores: dict) -> list:
    """
    Compute a composite quality score (0–100) for each ETF and add it to the result dict.

    Inputs per ETF:
      - tracking_difference  (from tracking calculation, already in results)
      - expense_ratio        (from EXPENSE_RATIOS constant, % p.a.)
      - aum                  (from AUM_CRORES constant, INR crores)
      - avg_volume           (from yfinance averageVolume, shares/day)

    Weights:
      40% Tracking Difference — lower abs(TD) is better
      25% Expense Ratio       — lower is better
      20% AUM                 — higher is better (log-scaled)
      15% Liquidity           — higher avg volume is better (log-scaled)

    Missing metrics → neutral score of 50.
    All scores clipped to [0, 100].
    """
    valid = [r for r in results if "error" not in r]
    if not valid:
        return results

    # Collect AUM and volume values for log-scaling across the peer group
    aum_vals = [aum_crores.get(r["ticker"]) for r in valid]
    vol_vals = [r.get("avg_volume") for r in valid]

    aum_vals_clean = [v for v in aum_vals if v is not None and v > 0]
    vol_vals_clean = [v for v in vol_vals if v is not None and v > 0]

    min_aum = min(aum_vals_clean) if aum_vals_clean else None
    max_aum = max(aum_vals_clean) if aum_vals_clean else None
    min_vol = min(vol_vals_clean) if vol_vals_clean else None
    max_vol = max(vol_vals_clean) if vol_vals_clean else None

    def _log_score(val, lo, hi) -> float:
        """Normalize val to 0–100 using log scaling between lo and hi."""
        if val is None or val <= 0 or lo is None or hi is None:
            return 50.0
        if lo == hi:
            return 100.0
        import math
        score = (math.log(val) - math.log(lo)) / (math.log(hi) - math.log(lo)) * 100
        return float(np.clip(score, 0, 100))

    for r in valid:
        td  = r.get("tracking_difference")
        exp = expense_ratios.get(r["ticker"])
        aum = aum_crores.get(r["ticker"])
        vol = r.get("avg_volume")

        # 1. Tracking difference score — lower abs(TD) is better
        td_score  = float(np.clip(100 - abs(td) * 20, 0, 100)) if td is not None else 50.0

        # 2. Expense ratio score — lower is better (0.5% → 0, 0% → 100)
        exp_score = float(np.clip(100 - exp * 200, 0, 100)) if exp is not None else 50.0

        # 3. AUM score — log-scaled across peer group
        aum_score = _log_score(aum, min_aum, max_aum)

        # 4. Liquidity score — log-scaled across peer group
        liq_score = _log_score(vol, min_vol, max_vol)

        quality_score = round(
            ETF_QUALITY_WEIGHTS["tracking"]  * td_score +
            ETF_QUALITY_WEIGHTS["expense"]   * exp_score +
            ETF_QUALITY_WEIGHTS["aum"]       * aum_score +
            ETF_QUALITY_WEIGHTS["liquidity"] * liq_score,
            2
        )

        r["quality_score"]   = quality_score
        r["score_breakdown"] = {
            "tracking":  round(td_score, 2),
            "expense":   round(exp_score, 2),
            "aum":       round(aum_score, 2),
            "liquidity": round(liq_score, 2),
        }

    return results


def fetch_all_etf_metrics(
    etf_tickers: Dict[str, str],
    commodity: str,
    period: str,
) -> list:
    """
    Fetch and compute metrics for all ETFs in a category.

    Args:
        etf_tickers: dict of display_name → Yahoo Finance ticker
        commodity:   "gold" or "silver"
        period:      "6mo", "1y", "3y", or "5y"

    Returns:
        List of metric dicts sorted by abs(tracking_difference) ascending
        (best trackers first), with errored ETFs appended at the end.
    """
    start, end = _period_to_dates(period)

    benchmark_inr = _build_benchmark(commodity, start, end)
    if benchmark_inr is None:
        logger.error("Could not build %s INR benchmark", commodity)
        return []

    # Download all ETF prices upfront for split detection
    tickers     = list(etf_tickers.values())
    peer_prices = _download_batch(tickers, start, end)
    if not peer_prices.empty:
        # Drop tickers with < 80% data coverage (likely delisted)
        min_rows    = int(peer_prices.shape[0] * 0.8)
        peer_prices = peer_prices.dropna(axis=1, thresh=min_rows)

    results = []
    for name, ticker in etf_tickers.items():
        metrics = compute_etf_metrics(
            name, ticker, benchmark_inr, peer_prices, start, end, period
        )
        results.append(metrics)

    valid  = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]

    # Load expense ratios and AUM from 30-day cache
    expense_ratios, aum_crores, refreshed = load_etf_metadata()
    if refreshed:
        logger.info("ETF metadata cache refreshed from constants")

    # Compute quality scores across the peer group (needs all results for log-scaling)
    valid = _compute_quality_scores(valid, expense_ratios, aum_crores)

    # Sort by quality score descending (best ETF first)
    valid.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    return valid + errors
