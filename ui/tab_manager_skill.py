"""Tab 4 — Manager Skill vs Benchmark."""

import logging
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any

_NO_DATA_FIG_HEIGHT = 350
_NO_DATA_ANNOTATION = dict(text="Benchmark data unavailable", showarrow=False, font_size=14)


class ManagerSkillTab:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def render(metrics: Dict[str, Any]) -> None:
        st.subheader("Manager Skill vs Benchmark")
        if not metrics.get('static_alpha_data'):
            st.info("Benchmark data is not yet available. This tab will show Alpha, Information Ratio, Hit Ratio, and rolling statistics once available.")

        col1, col2 = st.columns(2)

        with col1:
            ManagerSkillTab._alpha_chart(metrics)
            ManagerSkillTab._ir_chart(metrics)

        with col2:
            ManagerSkillTab._hit_ratio_chart(metrics)
            ManagerSkillTab._rolling_alpha_chart(metrics)

        ManagerSkillTab._rolling_ir_chart(metrics)

    @staticmethod
    def _alpha_chart(metrics):
        st.markdown("#### Alpha — Jensen's Alpha % (3Y / 5Y)")
        alpha = metrics.get('static_alpha_data', {})
        vals = {y: alpha.get(y) for y in [3, 5] if not isinstance(alpha.get(y), dict) and alpha.get(y) is not None}
        if vals:
            fig = go.Figure(go.Bar(
                x=[f"{y}Y" for y in vals], y=list(vals.values()),
                text=[f"{v:.2f}%" for v in vals.values()], textposition='auto',
                marker_color=['green' if v >= 0 else 'red' for v in vals.values()]
            ))
            fig.update_layout(template="plotly_white", title="Alpha (%)", yaxis_title="Alpha (%)", height=350)
        else:
            fig = ManagerSkillTab._no_data_fig("Alpha (%) — No Data")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _ir_chart(metrics):
        st.markdown("#### Information Ratio (3Y / 5Y)")
        ir = metrics.get('static_information_ratio_data', {})
        vals = {y: ir.get(y) for y in [3, 5] if not isinstance(ir.get(y), dict) and ir.get(y) is not None}
        if vals:
            fig = go.Figure(go.Bar(
                x=[f"{y}Y" for y in vals], y=list(vals.values()),
                text=[f"{v:.2f}" for v in vals.values()], textposition='auto',
                marker_color=['#636EFA', '#EF553B']
            ))
            fig.update_layout(template="plotly_white", title="Information Ratio", yaxis_title="IR", height=350)
        else:
            fig = ManagerSkillTab._no_data_fig("Information Ratio — No Data")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _hit_ratio_chart(metrics):
        st.markdown("#### Hit Ratio — Outperformance % (3Y / 5Y)")
        hr = metrics.get('static_hit_ratio_data', {})
        vals = {y: hr.get(y) for y in [3, 5] if not isinstance(hr.get(y), dict) and hr.get(y) is not None}
        if vals:
            fig = go.Figure(go.Bar(
                x=[f"{y}Y" for y in vals], y=list(vals.values()),
                text=[f"{v:.2f}%" for v in vals.values()], textposition='auto',
                marker_color=['#00CC96', '#AB63FA']
            ))
            fig.update_layout(template="plotly_white", title="Hit Ratio (%)", yaxis_title="Hit Ratio (%)", height=350)
        else:
            fig = ManagerSkillTab._no_data_fig("Hit Ratio (%) — No Data")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _rolling_alpha_chart(metrics):
        st.markdown("#### Rolling Alpha 3Y — Median / % Positive / Std Dev")
        ra_3y = next((i for i in metrics.get('rolling_alpha_data', []) if i.get('rolling_window') == 3), None)
        if ra_3y and 'error' not in ra_3y:
            vals = [ra_3y.get('median', 0), ra_3y.get('positive_share', 0), ra_3y.get('std_dev', 0)]
            fig = go.Figure(go.Bar(
                x=['Median Alpha', '% Positive Windows', 'Std Dev'], y=vals,
                text=[f"{v:.2f}" for v in vals], textposition='auto',
                marker_color=['#19D3F3', '#FF6692', '#B6E880']
            ))
            fig.update_layout(template="plotly_white", title="Rolling Alpha 3Y Stats", height=350)
        else:
            fig = ManagerSkillTab._no_data_fig("Rolling Alpha 3Y — No Data")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _rolling_ir_chart(metrics):
        st.markdown("#### Rolling Information Ratio 3Y — Median / % Positive / Std Dev")
        rir_3y = next((i for i in metrics.get('rolling_information_ratio_data', []) if i.get('rolling_window') == 3), None)
        if rir_3y and 'error' not in rir_3y:
            vals = [rir_3y.get('median', 0), rir_3y.get('positive_share', 0), rir_3y.get('std_dev', 0)]
            fig = go.Figure(go.Bar(
                x=['Median IR', '% Positive IR', 'Std Dev'], y=vals,
                text=[f"{v:.2f}" for v in vals], textposition='auto',
                marker_color=['#636EFA', '#EF553B', '#00CC96']
            ))
            fig.update_layout(template="plotly_white", title="Rolling IR 3Y Stats", height=350)
        else:
            fig = ManagerSkillTab._no_data_fig("Rolling IR 3Y — No Data")
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _no_data_fig(title: str) -> go.Figure:
        fig = go.Figure()
        fig.update_layout(template="plotly_white", title=title,
                          height=_NO_DATA_FIG_HEIGHT, annotations=[_NO_DATA_ANNOTATION])
        return fig


render = ManagerSkillTab.render
