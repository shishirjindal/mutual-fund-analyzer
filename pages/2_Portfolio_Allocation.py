import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from log.logger_config import configure_logging
from constants.portfolio_constants import PORTFOLIO

configure_logging()

df = pd.DataFrame(PORTFOLIO)
total = df["amount"].sum()

# ── Asset class summary ───────────────────────────────────────────────────────
st.subheader("Asset Class Breakdown")

asset_summary = (
    df.groupby("asset_class")["amount"]
    .sum()
    .reset_index()
    .rename(columns={"asset_class": "Asset Class", "amount": "Amount (₹)"})
)
asset_summary["Allocation (%)"] = (asset_summary["Amount (₹)"] / total * 100).round(1)
asset_summary = asset_summary.sort_values("Amount (₹)", ascending=False)

# Asset class donut chart
fig_asset = px.pie(
    asset_summary,
    names="Asset Class",
    values="Amount (₹)",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_asset.update_traces(textposition="outside", textinfo="label+percent")
fig_asset.update_layout(
    showlegend=False,
    margin=dict(t=60, b=60, l=80, r=80),
    annotations=[dict(text=f"₹{total:,.0f}", x=0.5, y=0.5,
                      font_size=16, showarrow=False)]
)

col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(fig_asset, use_container_width=True)
with col2:
    rows = ""
    for _, row in asset_summary.iterrows():
        rows += f"""<tr>
          <td style="padding:10px">{row['Asset Class']}</td>
          <td style="text-align:right;padding:10px">₹{row['Amount (₹)']:,.0f}</td>
          <td style="text-align:right;padding:10px;font-weight:600">{row['Allocation (%)']:.1f}%</td>
        </tr>"""
    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="border-bottom:2px solid #333">
          <th style="padding:10px;text-align:left;font-weight:700;font-size:15px">Asset Class</th>
          <th style="padding:10px;text-align:right;font-weight:700;font-size:15px">Amount</th>
          <th style="padding:10px;text-align:right;font-weight:700;font-size:15px">Allocation</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
      <tfoot>
        <tr style="border-top:2px solid #333">
          <td style="padding:10px;font-weight:700">Total</td>
          <td style="text-align:right;padding:10px;font-weight:700">₹{total:,.0f}</td>
          <td style="text-align:right;padding:10px;font-weight:700">100%</td>
        </tr>
      </tfoot>
    </table>
    """, unsafe_allow_html=True)

st.divider()

# ── Detailed breakdown by category ───────────────────────────────────────────
st.subheader("Category Breakdown")

tabs = st.tabs(["Equity", "Sectoral", "International", "Commodities"])

for tab, asset_class in zip(tabs, ["Equity", "Sectoral", "International", "Commodities"]):
    with tab:
        subset = df[df["asset_class"] == asset_class].copy()
        subset_total = subset["amount"].sum()
        subset["pct_of_class"] = (subset["amount"] / subset_total * 100).round(1)
        subset["pct_of_total"] = (subset["amount"] / total * 100).round(1)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            fig = px.bar(
                subset,
                x="category",
                y="amount",
                color="category",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={"amount": "Amount (₹)", "category": ""},
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(t=50, b=10, l=10, r=10),
                height=350,
                xaxis_tickangle=-20,
                yaxis=dict(range=[0, subset["amount"].max() * 1.25]),
            )
            fig.update_traces(text=[f"₹{v:,.0f}" for v in subset["amount"]],
                              textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            rows = ""
            for _, row in subset.iterrows():
                rows += f"""<tr>
                  <td style="padding:8px">{row['category']}</td>
                  <td style="text-align:right;padding:8px">₹{row['amount']:,.0f}</td>
                  <td style="text-align:right;padding:8px">{row['pct_of_class']:.1f}%</td>
                  <td style="text-align:right;padding:8px;color:#888">{row['pct_of_total']:.1f}%</td>
                </tr>"""
            st.markdown(f"""
            <table style="width:100%;border-collapse:collapse;font-size:13px">
              <thead>
                <tr style="border-bottom:2px solid #333">
                  <th style="padding:8px;text-align:left;font-weight:700">Category</th>
                  <th style="padding:8px;text-align:right;font-weight:700">Amount</th>
                  <th style="padding:8px;text-align:right;font-weight:700">% of Class</th>
                  <th style="padding:8px;text-align:right;font-weight:700;color:#888">% of Total</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
              <tfoot>
                <tr style="border-top:1px solid #333">
                  <td style="padding:8px;font-weight:700">Total</td>
                  <td style="text-align:right;padding:8px;font-weight:700">₹{subset_total:,.0f}</td>
                  <td style="text-align:right;padding:8px;font-weight:700">100%</td>
                  <td style="text-align:right;padding:8px;color:#888">{subset_total/total*100:.1f}%</td>
                </tr>
              </tfoot>
            </table>
            """, unsafe_allow_html=True)
