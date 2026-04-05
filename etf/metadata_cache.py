# -*- coding: utf-8 -*-
"""
ETF metadata cache — expense ratio and AUM with 30-day TTL.

Since no free public API provides expense ratios or AUM for Indian ETFs,
the static values in etf_constants.py are the source of truth. This module
writes them to a JSON cache file with a timestamp.

Cache lifecycle:
  - First use → writes cache from constants.
  - Within 30 days → reads from cache (fast).
  - After 30 days → refreshes cache from constants.
  - To force update → edit EXPENSE_RATIOS/AUM_CRORES in etf_constants.py,
    then delete .cache/etf_metadata.json (or wait for TTL expiry).
"""

import json
import logging
import datetime
import pathlib

from constants.fetch_constants import ETF_METADATA_CACHE_PATH, ETF_METADATA_CACHE_TTL_DAYS
from constants.etf_constants import EXPENSE_RATIOS, AUM_CRORES

logger = logging.getLogger(__name__)

_CACHE_PATH = pathlib.Path(ETF_METADATA_CACHE_PATH)


def _cache_age_days() -> float:
    """Return age of cache in days, or infinity if missing/unreadable."""
    if not _CACHE_PATH.exists():
        return float("inf")
    try:
        data    = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        written = datetime.date.fromisoformat(data["written_date"])
        return (datetime.date.today() - written).days
    except Exception:
        return float("inf")


def _write_cache() -> dict:
    """Write current constants to cache and return the payload."""
    payload = {
        "written_date":  datetime.date.today().isoformat(),
        "expense_ratios": EXPENSE_RATIOS,
        "aum_crores":     AUM_CRORES,
    }
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("ETF metadata cache written (%s)", _CACHE_PATH)
    return payload


def load_etf_metadata() -> tuple[dict, dict, bool]:
    """
    Load expense ratios and AUM, refreshing cache if stale (>30 days).

    Returns:
        (expense_ratios, aum_crores, refreshed)
        refreshed=True means the cache was just rebuilt from constants.
    """
    age = _cache_age_days()
    if age >= ETF_METADATA_CACHE_TTL_DAYS:
        logger.info(
            "ETF metadata cache %.0f days old (TTL=%d) — refreshing",
            age, ETF_METADATA_CACHE_TTL_DAYS,
        )
        payload = _write_cache()
        return payload["expense_ratios"], payload["aum_crores"], True

    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        logger.info("ETF metadata loaded from cache (written %s)", data["written_date"])
        return data["expense_ratios"], data["aum_crores"], False
    except Exception as e:
        logger.warning("Cache read failed: %s — using constants", e)
        return EXPENSE_RATIOS, AUM_CRORES, False


def cache_written_date() -> str:
    """Return the date the cache was last written, or 'never'."""
    if not _CACHE_PATH.exists():
        return "never"
    try:
        return json.loads(_CACHE_PATH.read_text(encoding="utf-8")).get("written_date", "unknown")
    except Exception:
        return "unknown"
