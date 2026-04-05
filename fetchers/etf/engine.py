# -*- coding: utf-8 -*-
"""
ETF analytics engine — orchestrates the full pipeline.

Wires together: downloader → benchmark → tracker → scorer.
"""

import datetime
import logging
from typing import Dict

from fetchers.etf.downloader import _download_batch, _period_to_dates
from fetchers.etf.benchmark import _build_benchmark
from fetchers.etf.tracker import compute_etf_metrics
from fetchers.etf.scorer import compute_quality_scores
from fetchers.etf.metadata_cache import load_etf_metadata

logger = logging.getLogger(__name__)


def fetch_all_etf_metrics(
    etf_tickers: Dict[str, str],
    commodity: str,
    period: str,
    holding_period_years: float = None,
) -> list:
    """
    Fetch and compute metrics for all ETFs in a category.

    Args:
        etf_tickers:          dict of display_name → Yahoo Finance ticker
        commodity:            "gold" or "silver"
        period:               "6mo", "1y", "3y", or "5y"
        holding_period_years: Investment horizon in years. Affects cost model:
                              longer horizon → expense cost dominates (favours low TER);
                              shorter horizon → impact cost dominates (favours liquidity).
                              Defaults to ETF_DEFAULT_HOLDING_YEARS if not provided.

    Returns:
        List of metric dicts — liquid ETFs sorted by total_cost ASC,
        illiquid ETFs appended, errored ETFs last.
    """
    from constants.etf_constants import ETF_DEFAULT_HOLDING_YEARS
    if holding_period_years is None:
        holding_period_years = ETF_DEFAULT_HOLDING_YEARS
    start, end = _period_to_dates(period)

    # Build benchmark with 4Y history to support 3Y TD computation
    bench_start = end - datetime.timedelta(days=4 * 365)
    benchmark_inr = _build_benchmark(commodity, bench_start, end)
    if benchmark_inr is None:
        logger.error("Could not build %s INR benchmark", commodity)
        return []

    # Download all ETF prices for split detection (4Y window)
    tickers     = list(etf_tickers.values())
    peer_prices = _download_batch(tickers, bench_start, end)
    if not peer_prices.empty:
        min_rows    = int(peer_prices.shape[0] * 0.8)
        peer_prices = peer_prices.dropna(axis=1, thresh=min_rows)

    # Compute tracking metrics per ETF
    results = [
        compute_etf_metrics(name, ticker, benchmark_inr, peer_prices, start, end, period)
        for name, ticker in etf_tickers.items()
    ]

    valid  = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]

    # Load metadata from cache and score
    expense_ratios, aum_crores, _ = load_etf_metadata()
    ranked = compute_quality_scores(valid, expense_ratios, aum_crores, holding_period_years)

    return ranked + errors
