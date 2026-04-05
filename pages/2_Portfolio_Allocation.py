import streamlit as st
import plotly.express as px
import pandas as pd
from log.logger_config import configure_logging
from constants.portfolio_constants import PORTFOLIO

configure_logging()

st.title("📊 My Portfolio")
st.markdown("Current allocation across asset classes.")

df = pd.DataFrame(PORTFOLIO)

# ── Asset class summary ───────────────────────────────────────────────────────
st.subheader("Asset Class Breakdown")

asset_summary = (
    df.groupby("asset_class")["pct"]
    .sum()
    .reset_index()
    .rename(columns={"asset_class": "Asset Class", "pct": "Allocation (%)"})
    .sort_values("Allocation (%)", ascending=False)
)

col1, col2 = st.columns([1, 1])
with col1:
    fig = px.pie(
        asset_summary,
        names="Asset Class",
        values="Allocation (%)",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(textposition="outside", textinfo="label+percent")
    fig.update_layout(
        showlegend=False,
        margin=dict(t=60, b=60, l=80, r=80),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    rows = ""
    for _, row in asset_summary.iterrows():
        rows += f"""<tr>
          <td style="padding:10px;text-align:center">{row['Asset Class']}</td>
          <td style="text-align:center;padding:10px;font-weight:600">{row['Allocation (%)']:.1f}%</td>
        </tr>"""
    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="border-bottom:2px solid #333">
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">Asset Class</th>
          <th style="padding:10px;text-align:center;font-weight:700;font-size:15px">Allocation</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
      <tfoot>
        <tr style="border-top:2px solid #333">
          <td style="padding:10px;font-weight:700;text-align:center">Total</td>
          <td style="text-align:center;padding:10px;font-weight:700">{df['pct'].sum():.1f}%</td>
        </tr>
      </tfoot>
    </table>
    """, unsafe_allow_html=True)

st.divider()

# ── Detailed breakdown by category ───────────────────────────────────────────
st.subheader("Category Breakdown")

tabs = st.tabs(["Equity", "International", "Commodities"])

for tab, asset_class in zip(tabs, ["Equity", "International", "Commodities"]):
    with tab:
        subset = df[df["asset_class"] == asset_class].copy()
        class_total = subset["pct"].sum()
        subset["pct_of_class"] = (subset["pct"] / class_total * 100).round(2)

        # Show chart first
        fig_bar = px.bar(
            subset,
            x="category",
            y="pct_of_class",
            color="category",
            text="pct_of_class",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"pct_of_class": "% of Class", "category": ""},
        )
        fig_bar.update_layout(
            showlegend=False,
            margin=dict(t=50, b=10, l=10, r=10),
            height=400,
            xaxis_tickangle=-30,
            yaxis=dict(range=[0, subset["pct_of_class"].max() * 1.3]),
        )
        fig_bar.update_traces(
            texttemplate='%{text:.1f}%',
            textposition="outside",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Show table below
        rows = ""
        for _, row in subset.iterrows():
            display_category = row['category']
            if row.get('is_sectoral') is True:
                display_category = f"Sectoral - {display_category}"
                
            rows += f"""<tr>
              <td style="padding:8px;text-align:center">{display_category}</td>
              <td style="text-align:center;padding:8px;font-weight:600">{row['pct_of_class']:.1f}%</td>
            </tr>"""
        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:20px">
          <thead>
            <tr style="border-bottom:2px solid #333">
              <th style="padding:8px;text-align:center;font-weight:700">Category</th>
              <th style="padding:8px;text-align:center;font-weight:700">% of Class</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
          <tfoot>
            <tr style="border-top:1px solid #333">
              <td style="padding:8px;font-weight:700;text-align:center">Total</td>
              <td style="text-align:center;padding:8px;font-weight:700">100%</td>
            </tr>
          </tfoot>
        </table>
        """, unsafe_allow_html=True)
