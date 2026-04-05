# -*- coding: utf-8 -*-
"""
ETF quality scorer with cost-based optimization.

Selection model:
  Total Cost = Expense Cost + Impact Cost

  expense_cost = expense_ratio (%) × holding_period_years
  impact_cost  = spread × 2          (buy + sell round-trip)
  spread       = ETF_SPREAD_K / liquidity_score

  ETF with minimum total_cost is ranked first.

Behaviour:
  Long holding period  → expense_cost dominates → favours low-TER ETFs (e.g. SBI)
  Short holding period → impact_cost dominates  → favours high-liquidity ETFs (e.g. Nippon)

Quality score (0–100) is still computed for display, but ranking uses total_cost.
"""

import math
import logging
import numpy as np
from typing import Dict, List, Optional

from constants.etf_constants import (
    ETF_QUALITY_WEIGHTS,
    ETF_MIN_TRADED_VALUE_INR,
    ETF_SPREAD_K,
    ETF_DEFAULT_HOLDING_YEARS,
)

logger = logging.getLogger(__name__)


def _log_score(val: Optional[float], lo: Optional[float], hi: Optional[float]) -> float:
    """Normalize val to 0–100 using log scaling. Returns 50 if inputs are invalid."""
    if not val or val <= 0 or lo is None or hi is None:
        return 50.0
    if lo == hi:
        return 100.0
    return float(np.clip(
        (math.log(val) - math.log(lo)) / (math.log(hi) - math.log(lo)) * 100,
        0, 100
    ))


def _estimate_spread(liquidity_score: float) -> float:
    """
    Estimate bid-ask spread (%) from liquidity score using inverse relationship.
    spread = ETF_SPREAD_K / liquidity_score
    A score of 50 → spread ≈ 0.05% (ETF_SPREAD_K=2.5).
    A score of 100 → spread ≈ 0.025%.
    A score of 10  → spread ≈ 0.25%.
    """
    if liquidity_score <= 0:
        return ETF_SPREAD_K  # worst case
    return ETF_SPREAD_K / liquidity_score


def compute_quality_scores(
    results: List[Dict],
    expense_ratios: Dict[str, float],
    aum_crores: Dict[str, float],
    holding_period_years: float = ETF_DEFAULT_HOLDING_YEARS,
) -> List[Dict]:
    """
    Score and rank ETFs using a cost-based optimization model.

    Steps:
      1. Hard filter: ETFs with avg_traded_value < ETF_MIN_TRADED_VALUE_INR → score 0.
      2. Compute liquidity score (log-scaled) for each ETF.
      3. Estimate spread from liquidity score.
      4. Compute total_cost = expense_cost + impact_cost.
      5. Compute quality score (0–100) for display.
      6. Rank by total_cost ascending (lowest cost = best).

    Args:
        results:              List of ETF metric dicts from tracker.
        expense_ratios:       ticker → expense ratio (% p.a.).
        aum_crores:           ticker → AUM in INR crores.
        holding_period_years: Investment horizon in years (affects expense vs impact cost balance).

    Returns:
        Liquid ETFs sorted by total_cost ASC, illiquid appended last.
    """
    valid = [r for r in results if "error" not in r]
    if not valid:
        return results

    # Step 1: hard liquidity filter
    liquid, illiquid = [], []
    for r in valid:
        if r.get("avg_traded_value", 0) < ETF_MIN_TRADED_VALUE_INR:
            r["filtered_reason"] = (
                f"avg traded value ₹{r.get('avg_traded_value', 0):,.0f} "
                f"< ₹{ETF_MIN_TRADED_VALUE_INR:,.0f} threshold"
            )
            logger.warning("[%s] Filtered out: %s", r["name"], r["filtered_reason"])
            r["quality_score"]   = 0.0
            r["total_cost"]      = float("inf")
            r["expense_cost"]    = None
            r["impact_cost"]     = None
            r["score_breakdown"] = {"tracking": 0, "expense": 0, "aum": 0, "liquidity": 0}
            illiquid.append(r)
        else:
            liquid.append(r)

    if not liquid:
        return results

    # Step 2: compute liquidity scores (log-scaled across peer group)
    vol_vals  = [r.get("avg_volume") for r in liquid]
    aum_vals  = [aum_crores.get(r["ticker"]) for r in liquid]
    vol_clean = [v for v in vol_vals if v and v > 0]
    aum_clean = [v for v in aum_vals if v and v > 0]
    min_vol, max_vol = (min(vol_clean), max(vol_clean)) if vol_clean else (None, None)
    min_aum, max_aum = (min(aum_clean), max(aum_clean)) if aum_clean else (None, None)

    for r in liquid:
        exp = expense_ratios.get(r["ticker"])
        aum = aum_crores.get(r["ticker"])
        vol = r.get("avg_volume")

        # Use multi-period tracking_score if available (0–100 already normalized),
        # otherwise derive from td_1y / tracking_difference
        td_score = r.get("tracking_score")
        if td_score is None:
            td = r.get("tracking_difference")
            td_score = float(np.clip(100 - abs(td) * 20, 0, 100)) if td is not None else 50.0

        # Normalized sub-scores (0–100) for display
        exp_score = float(np.clip(100 - exp * 200,    0, 100)) if exp is not None else 50.0
        aum_score = _log_score(aum, min_aum, max_aum)
        liq_score = _log_score(vol, min_vol, max_vol)

        quality_score = round(
            ETF_QUALITY_WEIGHTS["tracking"]  * td_score  +
            ETF_QUALITY_WEIGHTS["expense"]   * exp_score +
            ETF_QUALITY_WEIGHTS["aum"]       * aum_score +
            ETF_QUALITY_WEIGHTS["liquidity"] * liq_score,
            2
        )

        # Step 3–4: cost model
        spread       = _estimate_spread(liq_score)
        impact_cost  = spread * 2                                          # buy + sell
        expense_cost = (exp or 0) * holding_period_years
        total_cost   = expense_cost + impact_cost

        r["quality_score"]   = quality_score
        r["expense_ratio"]   = exp
        r["aum_crores"]      = aum
        r["total_cost"]      = round(total_cost, 4)
        r["expense_cost"]    = round(expense_cost, 4)
        r["impact_cost"]     = round(impact_cost, 4)
        r["score_breakdown"] = {
            "tracking":  round(td_score, 2),
            "expense":   round(exp_score, 2),
            "aum":       round(aum_score, 2),
            "liquidity": round(liq_score, 2),
        }

        logger.debug(
            "[%s] exp_cost=%.3f%% impact_cost=%.3f%% total=%.3f%% (holding=%.1fy spread=%.3f%%)",
            r["name"], expense_cost, impact_cost, total_cost, holding_period_years, spread,
        )

    # Step 6: rank by total_cost ascending
    liquid.sort(key=lambda x: x.get("total_cost", float("inf")))

    return liquid + illiquid
