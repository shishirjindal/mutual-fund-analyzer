"""Tab 3 — Risk-Adjusted Performance."""

import logging
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


class RiskAdjustedTab:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def render(metrics: Dict[str, Any]) -> None:
        st.subheader("Risk-Adjusted Performance")
        col1, col2 = st.columns(2)

        with col1:
            RiskAdjustedTab._ratio_bar(metrics, 'static_sharpe_data', "Sharpe Ratio (3Y / 5Y)", "Sharpe Ratio", "Ratio")
            RiskAdjustedTab._ratio_bar(metrics, 'static_calmar_ratio_data', "Calmar Ratio (3Y / 5Y)", "Calmar Ratio", "Ratio",
                                       colors=['#00CC96', '#AB63FA'])

        with col2:
            RiskAdjustedTab._ratio_bar(metrics, 'static_sortino_data', "Sortino Ratio (3Y / 5Y)", "Sortino Ratio", "Ratio",
                                       colors=['#FFA15A', '#19D3F3'])
            RiskAdjustedTab._ratio_bar(metrics, 'static_treynor_ratio_data', "Treynor Ratio (3Y / 5Y)", "Treynor Ratio", "Ratio",
                                       colors=['#FF6692', '#B6E880'])

        st.markdown("#### All Risk-Adjusted Ratios — 3Y vs 5Y Comparison")
        ratio_names = ['Sharpe', 'Sortino', 'Calmar', 'Treynor']
        ratio_keys = ['static_sharpe_data', 'static_sortino_data', 'static_calmar_ratio_data', 'static_treynor_ratio_data']
        vals_3y = [v if isinstance(v := metrics.get(k, {}).get(3), (int, float)) else 0 for k in ratio_keys]
        vals_5y = [v if isinstance(v := metrics.get(k, {}).get(5), (int, float)) else 0 for k in ratio_keys]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='3Y', x=ratio_names, y=vals_3y, text=[f"{v:.2f}" for v in vals_3y], textposition='auto'))
        fig.add_trace(go.Bar(name='5Y', x=ratio_names, y=vals_5y, text=[f"{v:.2f}" for v in vals_5y], textposition='auto'))
        fig.update_layout(template="plotly_white", barmode='group', title="Risk-Adjusted Ratios: 3Y vs 5Y",
                          yaxis_title="Ratio Value", height=400)
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _ratio_bar(metrics, key, heading, title, yaxis_title, colors=None):
        st.markdown(f"#### {heading}")
        data = metrics.get(key, {})
        vals = {y: data.get(y) for y in [3, 5] if not isinstance(data.get(y), dict) and data.get(y) is not None}
        if vals:
            fig = go.Figure(go.Bar(
                x=[f"{y}Y" for y in vals], y=list(vals.values()),
                text=[f"{v:.2f}" for v in vals.values()], textposition='auto',
                marker_color=colors or ['#636EFA', '#EF553B']
            ))
            fig.update_layout(template="plotly_white", title=title, yaxis_title=yaxis_title, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"{title} data not available.")


render = RiskAdjustedTab.render
