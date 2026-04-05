# -*- coding: utf-8 -*-
"""Backward-compatible shim — delegates to etf.metadata_cache."""
from etf.metadata_cache import load_etf_metadata, cache_written_date

__all__ = ["load_etf_metadata", "cache_written_date"]
