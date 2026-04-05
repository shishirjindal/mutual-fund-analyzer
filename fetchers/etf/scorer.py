# -*- coding: utf-8 -*-
"""
ETF quality scorer.

Computes a composite quality score (0–100) ranking ETFs by:
  - Tracking efficiency (how closely the ETF follows the commodity)
  - Cost (expense ratio)
  - Stability (AUM size)
  - Liquidity (trading volume / traded value)

Weights and thresholds are configured in constants/etf_constants.py.

Liquidity dominance rule:
  If ETF A's liquidity score >= ETF_LIQUIDITY_DOMINANCE_FACTOR × ETF B's,
  prefer A over B unless B has a meaningfully lower expense ratio
  (difference > ETF_EXPENSE_OVERRIDE_THRESHOLD). This reflects the real-world
  principle that execution cost (bid-ask spread) often matters more than small
  TER differences.
"""

import math
import logging
import numpy as np
from typing import Dict, List, Optional

from constants.etf_constants import (
    ETF_QUALITY_WEIGHTS,
    ETF_MIN_TRADED_VALUE_INR,
    ETF_LIQUIDITY_DOMINANCE_FACTOR,
    ETF_EXPENSE_OVERRIDE_THRESHOLD,
)

logger = logging.getLogger(__name__)


def _log_score(val: Optional[float], lo: Optional[float], hi: Optional[float]) -> float:
    """
    Normalize val to 0–100 using log scaling between lo and hi.
    Returns neutral score of 50 if any input is missing or invalid.
    """
    if not val or val <= 0 or lo is None or hi is None:
        return 50.0
    if lo == hi:
        return 100.0
    return float(np.clip(
        (math.log(val) - math.log(lo)) / (math.log(hi) - math.log(lo)) * 100,
        0, 100
    ))


def compute_quality_scores(results: List[Dict],
                            expense_ratios: Dict[str, float],
                            aum_crores: Dict[str, float]) -> List[Dict]:
    """
    Compute quality scores for all ETFs and return them sorted best-first.

    Steps:
      1. Hard filter: ETFs with avg_traded_value < ETF_MIN_TRADED_VALUE_INR
         are marked illiquid and scored 0.
      2. Normalize tracking difference, expense ratio, AUM, and volume to 0–100.
      3. Compute weighted composite score.
      4. Apply liquidity dominance rule to re-rank pairs where one ETF
         significantly dominates on liquidity.

    Returns liquid ETFs sorted by quality_score DESC, illiquid appended last.
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
            r["score_breakdown"] = {"tracking": 0, "expense": 0, "aum": 0, "liquidity": 0}
            illiquid.append(r)
        else:
            liquid.append(r)

    if not liquid:
        return results

    # Step 2: collect peer-group min/max for log-scaling
    aum_vals = [aum_crores.get(r["ticker"]) for r in liquid]
    vol_vals = [r.get("avg_volume") for r in liquid]
    aum_clean = [v for v in aum_vals if v and v > 0]
    vol_clean = [v for v in vol_vals if v and v > 0]
    min_aum, max_aum = (min(aum_clean), max(aum_clean)) if aum_clean else (None, None)
    min_vol, max_vol = (min(vol_clean), max(vol_clean)) if vol_clean else (None, None)

    # Step 3: score each ETF
    for r in liquid:
        td  = r.get("tracking_difference")
        exp = expense_ratios.get(r["ticker"])
        aum = aum_crores.get(r["ticker"])
        vol = r.get("avg_volume")

        td_score  = float(np.clip(100 - abs(td) * 20, 0, 100)) if td  is not None else 50.0
        exp_score = float(np.clip(100 - exp * 200,    0, 100)) if exp is not None else 50.0
        aum_score = _log_score(aum, min_aum, max_aum)
        liq_score = _log_score(vol, min_vol, max_vol)

        r["quality_score"] = round(
            ETF_QUALITY_WEIGHTS["tracking"]  * td_score  +
            ETF_QUALITY_WEIGHTS["expense"]   * exp_score +
            ETF_QUALITY_WEIGHTS["aum"]       * aum_score +
            ETF_QUALITY_WEIGHTS["liquidity"] * liq_score,
            2
        )
        r["score_breakdown"] = {
            "tracking":  round(td_score, 2),
            "expense":   round(exp_score, 2),
            "aum":       round(aum_score, 2),
            "liquidity": round(liq_score, 2),
        }

    # Step 4: sort then apply liquidity dominance rule
    liquid.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    for i in range(len(liquid)):
        for j in range(i + 1, len(liquid)):
            a, b = liquid[i], liquid[j]
            liq_a = a["score_breakdown"]["liquidity"]
            liq_b = b["score_breakdown"]["liquidity"]
            exp_a = expense_ratios.get(a["ticker"], 0)
            exp_b = expense_ratios.get(b["ticker"], 0)
            if liq_b >= ETF_LIQUIDITY_DOMINANCE_FACTOR * liq_a:
                if (exp_a - exp_b) <= ETF_EXPENSE_OVERRIDE_THRESHOLD:
                    liquid[i], liquid[j] = liquid[j], liquid[i]
                    logger.info(
                        "Liquidity dominance: %s ranked above %s "
                        "(liq %.1f vs %.1f, exp diff %.2f%%)",
                        b["name"], a["name"], liq_b, liq_a, exp_a - exp_b,
                    )

    return liquid + illiquid
