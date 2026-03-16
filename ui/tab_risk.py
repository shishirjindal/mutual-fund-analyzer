"""Tab 2 — Risk."""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


class RiskTab:
    """Renders the Risk tab."""

    @staticmethod
    def render(metrics: Dict[str, Any]) -> None:
        st.subheader("Risk")
        col1, col2 = st.columns(2)

        with col1:
            RiskTab._drawdown_chart(metrics)
            RiskTab._std_dev_chart(metrics)

        with col2:
            RiskTab._ulcer_chart(metrics)
            RiskTab._rolling_mdd_chart(metrics)

    @staticmethod
    def _drawdown_chart(metrics):
        st.markdown("#### Max Drawdown — Value & Duration (3Y / 5Y)")
        dd = metrics.get('static_drawdown_data', {})
        dd_periods, dd_values, dd_durations = [], [], []
        for y in [3, 5]:
            entry = dd.get(y, {})
            if isinstance(entry, dict) and 'max_drawdown' in entry:
                dd_periods.append(f"{y}Y")
                dd_values.append(abs(entry['max_drawdown']))
                dd_durations.append(entry.get('max_duration_days', 0))
        if dd_periods:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Max Drawdown (%)', x=dd_periods, y=dd_values,
                                 text=[f"{v:.2f}%" for v in dd_values], textposition='auto',
                                 marker_color='crimson'))
            fig.add_trace(go.Bar(name='Recovery Days', x=dd_periods, y=dd_durations,
                                 text=dd_durations, textposition='auto',
                                 marker_color='salmon', yaxis='y2'))
            fig.update_layout(
                template="plotly_white", barmode='group', height=380,
                title="Max Drawdown & Recovery",
                yaxis=dict(title='Drawdown (%)'),
                yaxis2=dict(title='Recovery (Days)', overlaying='y', side='right')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Drawdown data not available.")

    @staticmethod
    def _std_dev_chart(metrics):
        st.markdown("#### Annualized Std Dev (3Y / 5Y)")
        std = metrics.get('static_std_dev_data', {})
        std_periods = [f"{y}Y" for y in [3, 5] if not isinstance(std.get(y), dict) and std.get(y) is not None]
        std_values = [std[y] for y in [3, 5] if not isinstance(std.get(y), dict) and std.get(y) is not None]
        if std_periods:
            fig = go.Figure(go.Bar(
                x=std_periods, y=std_values,
                text=[f"{v:.2f}%" for v in std_values], textposition='auto',
                marker_color=['#AB63FA', '#FFA15A']
            ))
            fig.update_layout(template="plotly_white", title="Std Dev (%)", yaxis_title="Volatility (%)", height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Std Dev data not available.")

    @staticmethod
    def _ulcer_chart(metrics):
        st.markdown("#### Ulcer Index (1Y / 3Y / 5Y)")
        ulcer = metrics.get('static_ulcer_index_data', {})
        ul_periods = [f"{y}Y" for y in [1, 3, 5] if not isinstance(ulcer.get(y), dict) and ulcer.get(y) is not None]
        ul_values = [ulcer[y] for y in [1, 3, 5] if not isinstance(ulcer.get(y), dict) and ulcer.get(y) is not None]
        if ul_periods:
            fig = go.Figure(go.Bar(
                x=ul_periods, y=ul_values,
                text=[f"{v:.2f}" for v in ul_values], textposition='auto',
                marker_color='orange'
            ))
            fig.update_layout(template="plotly_white", title="Ulcer Index", yaxis_title="Index Value", height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ulcer Index data not available.")

    @staticmethod
    def _rolling_mdd_chart(metrics):
        st.markdown("#### Rolling Max Drawdown — 3Y Window (Median / 75th %ile / Worst)")
        roll_dd = metrics.get('rolling_drawdown_data', [])
        rdd_3y = next((i for i in roll_dd if i.get('rolling_window') == 3), None)
        if rdd_3y and 'error' not in rdd_3y:
            rdd_vals = [abs(rdd_3y.get('median', 0)), abs(rdd_3y.get('percentile_75', 0)), abs(rdd_3y.get('min', 0))]
            fig = go.Figure(go.Bar(
                x=['Median', '75th %ile', 'Worst'], y=rdd_vals,
                text=[f"{v:.2f}%" for v in rdd_vals], textposition='auto',
                marker_color=['#19D3F3', '#FF6692', '#B6E880']
            ))
            fig.update_layout(template="plotly_white", title="Rolling MDD 3Y (%)", yaxis_title="Drawdown (%)", height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Rolling drawdown data not available.")


render = RiskTab.render
