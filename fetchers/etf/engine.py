# -*- coding: utf-8 -*-
"""
ETF analytics engine — orchestrates the full pipeline.

Wires together: downloader → benchmark → tracker → scorer.
"""

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
) -> list:
    """
    Fetch and compute metrics for all ETFs in a category.

    Pipeline:
      1. Build commodity INR benchmark (GLD/SLV × USDINR).
      2. Download all ETF prices for split detection.
      3. Compute tracking metrics per ETF.
      4. Load expense ratio / AUM from 30-day cache.
      5. Score and rank ETFs by quality.

    Args:
        etf_tickers: dict of display_name → Yahoo Finance ticker
        commodity:   "gold" or "silver"
        period:      "6mo", "1y", "3y", or "5y"

    Returns:
        List of metric dicts — liquid ETFs sorted by quality_score DESC,
        illiquid ETFs appended, errored ETFs last.
    """
    start, end = _period_to_dates(period)

    # Build benchmark
    benchmark_inr = _build_benchmark(commodity, start, end)
    if benchmark_inr is None:
        logger.error("Could not build %s INR benchmark", commodity)
        return []

    # Download all ETF prices for split detection
    tickers     = list(etf_tickers.values())
    peer_prices = _download_batch(tickers, start, end)
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
    ranked = compute_quality_scores(valid, expense_ratios, aum_crores)

    return ranked + errors
