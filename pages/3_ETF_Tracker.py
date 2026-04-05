import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from log.logger_config import configure_logging
from fetchers.etf_fetcher import fetch_all_etf_metrics
from constants.etf_constants import (
    GOLD_ETF_TICKERS, SILVER_ETF_TICKERS, ETF_PERIODS,
)

configure_logging()

st.title("📊 ETF Tracker")
st.markdown("Track Gold and Silver ETFs — compare tracking difference, tracking error, and price performance.")

# ── Controls ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 2])
with col1:
    commodity = st.radio("Commodity", ["Gold", "Silver"], horizontal=True)
with col2:
    period = st.selectbox("Period", ETF_PERIODS, index=1)

etf_tickers = GOLD_ETF_TICKERS if commodity == "Gold" else SILVER_ETF_TICKERS

# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner(f"Fetching {commodity} ETF data..."):
    results = fetch_all_etf_metrics(etf_tickers, commodity.lower(), period)

from fetchers.etf_metadata_cache import cache_written_date
_meta_date = cache_written_date()
st.caption(f"Expense ratio & AUM data as of: **{_meta_date}** (refreshes every 30 days — update `etf_constants.py` to change values)")

if not results:
    st.error("Could not fetch data. Check your internet connection.")
    st.stop()

valid  = [r for r in results if "error" not in r]
errors = [r for r in results if "error" in r]

# ── Summary table ─────────────────────────────────────────────────────────────
st.subheader(f"{commodity} ETF Comparison")

if valid:
    df = pd.DataFrame(valid)[[
        "name", "ticker", "current_price",
        "etf_return", "benchmark_return",
        "tracking_difference", "weekly_tracking_error", "market_tracking_error",
        "quality_score",
    ]]
    df.columns = [
        "Fund", "Ticker", "Price (₹)",
        f"ETF Return ({period} %)", f"Benchmark Return ({period} %)",
        "Tracking Diff (%)", "Weekly TE (% ann.)", "Daily TE (% ann.)",
        "Quality Score",
    ]

    def _color_td(val):
        a = abs(val)
        if a < 0.25:  return "background-color:#2ecc7133"
        if a < 0.5:   return "background-color:#3498db33"
        if a < 1.0:   return "background-color:#f39c1233"
        return "background-color:#e74c3c33"

    def _color_score(val):
        if val >= 70:  return "background-color:#2ecc7133"
        if val >= 50:  return "background-color:#3498db33"
        if val >= 30:  return "background-color:#f39c1233"
        return "background-color:#e74c3c33"

    styled = (df.style
              .applymap(_color_td,    subset=["Tracking Diff (%)"])
              .applymap(_color_score, subset=["Quality Score"]))
    st.dataframe(styled, use_container_width=True, hide_index=True)

if errors:
    with st.expander(f"⚠️ {len(errors)} ETF(s) with data issues"):
        for r in errors:
            st.write(f"- **{r['name']}** ({r['ticker']}): {r['error']}")

# ── Tracking difference bar chart ─────────────────────────────────────────────
if valid:
    st.subheader("Tracking Difference (%)")
    st.caption("Cumulative return gap vs gold/silver INR benchmark over the selected period. Closer to 0 = better.")

    colors = ["#2ecc71" if abs(r["tracking_difference"]) < 0.25
              else "#3498db" if abs(r["tracking_difference"]) < 0.5
              else "#f39c12" if abs(r["tracking_difference"]) < 1.0
              else "#e74c3c" for r in valid]

    fig = go.Figure(go.Bar(
        x=[r["name"] for r in valid],
        y=[r["tracking_difference"] for r in valid],
        marker_color=colors,
        text=[f"{r['tracking_difference']:+.3f}%" for r in valid],
        textposition="outside",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        yaxis_title="Tracking Difference (%)",
        xaxis_tickangle=-30,
        height=400,
        margin=dict(t=20, b=80),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Quality score bar chart ───────────────────────────────────────────────
    st.subheader("Quality Score (0–100)")
    st.caption("Composite score: 40% tracking, 25% expense ratio, 20% AUM, 15% liquidity. Higher = better.")
    fig_q = go.Figure(go.Bar(
        x=[r["name"] for r in valid],
        y=[r.get("quality_score", 0) for r in valid],
        marker_color=["#2ecc71" if r.get("quality_score", 0) >= 70
                      else "#3498db" if r.get("quality_score", 0) >= 50
                      else "#f39c12" if r.get("quality_score", 0) >= 30
                      else "#e74c3c" for r in valid],
        text=[f"{r.get('quality_score', 0):.1f}" for r in valid],
        textposition="outside",
    ))
    fig_q.update_layout(
        yaxis=dict(title="Quality Score", range=[0, 110]),
        xaxis_tickangle=-30,
        height=400,
        margin=dict(t=20, b=80),
        showlegend=False,
    )
    st.plotly_chart(fig_q, use_container_width=True)

# ── Price chart: ETF vs gold/silver INR benchmark ────────────────────────────
st.subheader("Price Performance (Indexed to 100)")
st.caption(f"ETF price vs {commodity} price in INR (GC=F × USDINR), both indexed to 100 at start.")

selected_name   = st.selectbox("Select ETF", [r["name"] for r in valid])
selected_ticker = etf_tickers[selected_name]

with st.spinner("Loading price chart..."):
    from fetchers.etf_fetcher import _download, _build_benchmark, _period_to_dates
    start, end = _period_to_dates(period)
    etf_prices    = _download(selected_ticker, start, end)
    benchmark_inr = _build_benchmark(commodity.lower(), start, end)

fig2 = go.Figure()
if etf_prices is not None and benchmark_inr is not None:
    # Align on inner join — same as tracking error calculation
    df_chart = pd.concat([benchmark_inr, etf_prices], axis=1, join="inner").dropna()
    df_chart.columns = ["benchmark", "etf"]
    indexed = df_chart / df_chart.iloc[0] * 100

    fig2.add_trace(go.Scatter(
        x=indexed.index, y=indexed["etf"],
        name=selected_name, line=dict(color="#3498db", width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=indexed.index, y=indexed["benchmark"],
        name=f"{commodity} INR (GC=F × USDINR)", line=dict(color="#f39c12", width=2, dash="dash")
    ))
    fig2.update_layout(
        yaxis_title="Indexed Price (Base=100)",
        height=400,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Could not load price data for chart.")

# ── Legend ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
**Quality Score** = composite rank (0–100): 40% tracking + 25% expense ratio + 20% AUM + 15% liquidity.
Higher = better overall investment choice.

**Tracking Difference (TD)** = ETF cumulative return − benchmark (gold/silver INR) return over the period.
Primary tracking metric — shows total return gap. Negative = ETF underperformed the commodity.

**Weekly TE** = annualized std of weekly return differences. More stable than daily TE.
Reduces noise from timezone and calendar differences between NYSE and NSE.

**Daily TE** = annualized std of daily return differences. Structurally high (~30–60%) because
ETF prices (NSE) and benchmark prices (NYSE) are from different exchanges with different
trading hours, holidays, and currency timing. Not comparable to AMC-reported TE (<1%),
which uses official daily NAV data.

| Color | Quality Score | Tracking Difference |
|---|---|---|
| 🟢 Green | ≥ 70 — Excellent | < 0.25% |
| 🔵 Blue | 50–70 — Good | 0.25–0.5% |
| 🟡 Yellow | 30–50 — Average | 0.5–1% |
| 🔴 Red | < 30 — Weak | > 1% |
""")
