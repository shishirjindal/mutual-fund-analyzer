# -*- coding: utf-8 -*-
"""Backward-compatible shim — delegates to etf package."""
from etf import fetch_all_etf_metrics, _download, _download_batch, _period_to_dates
from etf.benchmark import _build_benchmark

__all__ = ["fetch_all_etf_metrics", "_download", "_download_batch",
           "_period_to_dates", "_build_benchmark"]
