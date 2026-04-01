import streamlit as st
import plotly.express as px
import pandas as pd
from constants.ui_constants import EQUITY_ALLOCATION
from log.logger_config import configure_logging

configure_logging()



st.title("📊 Equity Portfolio Allocation")
st.markdown("Recommended fixed allocation across equity mutual fund categories.")

df = pd.DataFrame(EQUITY_ALLOCATION)

# ── Allocation table ──────────────────────────────────────────────────────────
st.subheader("Category Allocation")
rows = "".join(
    f"<tr><td>{row['category']}</td><td>{row['allocation']}%</td></tr>"
    for row in EQUITY_ALLOCATION
)
st.markdown(f"""
<table style="width:50%;border-collapse:collapse;text-align:center">
  <thead>
    <tr>
      <th style="border:1px solid #ddd;padding:10px;text-align:center"><b>Category</b></th>
      <th style="border:1px solid #ddd;padding:10px;text-align:center"><b>Allocation (%)</b></th>
    </tr>
  </thead>
  <tbody>
    {"".join(f'<tr><td style="border:1px solid #ddd;padding:10px">{r["category"]}</td><td style="border:1px solid #ddd;padding:10px">{r["allocation"]}%</td></tr>' for r in EQUITY_ALLOCATION)}
  </tbody>
</table>
""", unsafe_allow_html=True)

# ── Pie chart ─────────────────────────────────────────────────────────────────
fig = px.pie(
    df,
    names='category',
    values='allocation',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig.update_traces(textposition='outside', textinfo='label+percent')
fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))

col, _ = st.columns([2, 1])
with col:
    st.plotly_chart(fig, use_container_width=True)
