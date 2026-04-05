# -*- coding: utf-8 -*-
"""
Backward-compatible shim — delegates to fetchers.etf package.
Import from fetchers.etf directly for new code.
"""
from fetchers.etf import fetch_all_etf_metrics, _download, _download_batch, _period_to_dates
from fetchers.etf.benchmark import _build_benchmark

__all__ = [
    "fetch_all_etf_metrics",
    "_download",
    "_download_batch",
    "_period_to_dates",
    "_build_benchmark",
]
