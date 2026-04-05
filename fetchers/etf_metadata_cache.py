# -*- coding: utf-8 -*-
"""
ETF Metadata Cache — expense ratio and AUM with 30-day TTL.

Why a cache instead of always reading from constants:
  Expense ratios and AUM change periodically (AMCs revise TER, AUM fluctuates).
  The static values in etf_constants.py are the source of truth. This cache
  layer writes them to disk with a timestamp so the ETF tracker page can detect
  when data is stale (>30 days) and prompt the user to update the constants.

  Since no free public API provides these values for Indian ETFs, the update
  workflow is: edit EXPENSE_RATIOS / AUM_CRORES in etf_constants.py, then
  delete the cache file (or wait for TTL expiry) to force a refresh.
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
    """Return age of cache file in days, or infinity if it doesn't exist."""
    if not _CACHE_PATH.exists():
        return float("inf")
    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        written = datetime.date.fromisoformat(data["written_date"])
        return (datetime.date.today() - written).days
    except Exception:
        return float("inf")


def _write_cache() -> dict:
    """Write current constants to cache file and return the payload."""
    payload = {
        "written_date": datetime.date.today().isoformat(),
        "expense_ratios": EXPENSE_RATIOS,
        "aum_crores": AUM_CRORES,
    }
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("ETF metadata cache written (%s)", _CACHE_PATH)
    return payload


def load_etf_metadata() -> tuple[dict, dict, bool]:
    """
    Load expense ratios and AUM from cache, refreshing if stale (>30 days).

    Returns:
        (expense_ratios, aum_crores, is_stale)
        is_stale=True means the cache was just refreshed from constants.
    """
    age = _cache_age_days()

    if age >= ETF_METADATA_CACHE_TTL_DAYS:
        logger.info(
            "ETF metadata cache is %.0f days old (TTL=%d) — refreshing from constants",
            age, ETF_METADATA_CACHE_TTL_DAYS,
        )
        payload = _write_cache()
        return payload["expense_ratios"], payload["aum_crores"], True

    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        logger.info(
            "Loaded ETF metadata from cache (written %s, age %d days)",
            data["written_date"], int(age),
        )
        return data["expense_ratios"], data["aum_crores"], False
    except Exception as e:
        logger.warning("Failed to read ETF metadata cache: %s — falling back to constants", e)
        return EXPENSE_RATIOS, AUM_CRORES, False


def cache_written_date() -> str:
    """Return the date the cache was last written, or 'never'."""
    if not _CACHE_PATH.exists():
        return "never"
    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        return data.get("written_date", "unknown")
    except Exception:
        return "unknown"
