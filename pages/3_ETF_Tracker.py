import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from log.logger_config import configure_logging
from fetchers.etf_fetcher import fetch_all_etf_metrics
from fetchers.etf_metadata_cache import cache_written_date
from fetchers.etf_fetcher import _download, _build_benchmark, _period_to_dates
from constants.etf_constants import (
    GOLD_ETF_TICKERS, SILVER_ETF_TICKERS, ETF_DEFAULT_HOLDING_YEARS,
)

configure_logging()

st.title("📊 ETF Tracker")
st.markdown("Track Gold and Silver ETFs — ranked by quality score.")

# ── Controls ──────────────────────────────────────────────────────────────────
col1, _ = st.columns([2, 4])
with col1:
    commodity = st.radio("Commodity", ["Gold", "Silver"], horizontal=True)

etf_tickers = GOLD_ETF_TICKERS if commodity == "Gold" else SILVER_ETF_TICKERS

# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner(f"Fetching {commodity} ETF data..."):
    results = fetch_all_etf_metrics(etf_tickers, commodity.lower(), "1y",
                                    holding_period_years=ETF_DEFAULT_HOLDING_YEARS)

_meta_date = cache_written_date()
st.caption(f"Expense ratio & AUM data as of: **{_meta_date}** — update `etf_constants.py` to refresh")

if not results:
    st.error("Could not fetch data. Check your internet connection.")
    st.stop()

valid  = [r for r in results if "error" not in r]
errors = [r for r in results if "error" in r]

# ── Summary table — Fund, ETF Return, Quality Score only ─────────────────────
st.subheader(f"{commodity} ETF Ranking")

if valid:
    def _score_color(val):
        if val >= 70: return "#2ecc71"
        if val >= 50: return "#3498db"
        if val >= 30: return "#f39c12"
        return "#e74c3c"

    def _score_label(val):
        if val >= 70: return "Excellent"
        if val >= 50: return "Good"
        if val >= 30: return "Average"
        return "Weak"

    rows = ""
    for i, r in enumerate(sorted(valid, key=lambda x: x.get("quality_score", 0), reverse=True)):
        rank      = i + 1
        name      = r["name"]
        ret       = r.get("etf_return")
        score     = r.get("quality_score", 0)
        color     = _score_color(score)
        label     = _score_label(score)
        ret_str   = f"{ret:+.2f}%" if ret is not None else "N/A"
        ret_color = "#2ecc71" if ret and ret >= 0 else "#e74c3c"
        exp       = r.get("expense_ratio")
        aum       = r.get("aum_crores")
        exp_str   = f"{exp:.2f}%" if exp is not None else "N/A"
        aum_str   = f"₹{aum:,.0f} Cr" if aum is not None else "N/A"
        rows += f"""
        <tr>
          <td style="text-align:center;color:#888;padding:10px">#{rank}</td>
          <td style="padding:10px">{name}</td>
          <td style="text-align:center;color:{ret_color};padding:10px">{ret_str}</td>
          <td style="text-align:center;padding:10px">{exp_str}</td>
          <td style="text-align:center;padding:10px">{aum_str}</td>
          <td style="text-align:center;padding:10px">
            <span style="background:{color}22;color:{color};border:1px solid {color};
                         border-radius:20px;padding:3px 14px;font-weight:700;font-size:15px">
              {score:.1f}
            </span>
          </td>
          <td style="text-align:center;color:{color};font-size:12px;padding:10px">{label}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="border-bottom:2px solid #333">
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px;width:50px">#</th>
          <th style="padding:10px;text-align:left;font-weight:700;font-size:15px">Fund</th>
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">ETF Return (1Y)</th>
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">Expense Ratio</th>
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">AUM</th>
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">Quality Score</th>
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">Rating</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("")

if errors:
    with st.expander(f"⚠️ {len(errors)} ETF(s) with data issues"):
        for r in errors:
            st.write(f"- **{r['name']}** ({r['ticker']}): {r['error']}")

# ── Quality score bar chart ───────────────────────────────────────────────────
if valid:
    st.subheader("Quality Score (0–100)")
    st.caption(f"Composite score based on tracking, expense ratio, AUM and liquidity. "
               f"Ranked by total cost over {ETF_DEFAULT_HOLDING_YEARS:.0f}-year holding period.")

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

# ── Price chart: ETF vs benchmark ────────────────────────────────────────────
st.subheader("Price Performance (Indexed to 100)")
st.caption(f"ETF price vs {commodity} INR benchmark, both indexed to 100 at start.")

selected_name   = st.selectbox("Select ETF", [r["name"] for r in valid])
selected_ticker = etf_tickers[selected_name]

with st.spinner("Loading price chart..."):
    start, end    = _period_to_dates("1y")
    etf_prices    = _download(selected_ticker, start, end)
    benchmark_inr = _build_benchmark(commodity.lower(), start, end)

fig2 = go.Figure()
if etf_prices is not None and benchmark_inr is not None:
    df_chart = pd.concat([benchmark_inr, etf_prices], axis=1, join="inner").dropna()
    df_chart.columns = ["benchmark", "etf"]
    indexed = df_chart / df_chart.iloc[0] * 100
    fig2.add_trace(go.Scatter(
        x=indexed.index, y=indexed["etf"],
        name=selected_name, line=dict(color="#3498db", width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=indexed.index, y=indexed["benchmark"],
        name=f"{commodity} INR", line=dict(color="#f39c12", width=2, dash="dash")
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
