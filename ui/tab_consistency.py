"""Tab 5 — Consistency (Rolling)."""

import logging
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any
from ui.metric_colors import get_color


class ConsistencyTab:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def render(metrics: Dict[str, Any]) -> None:
        st.subheader("Consistency (Rolling)")
        col1, col2 = st.columns(2)
        with col1:
            ConsistencyTab._rolling_returns_chart(metrics)
            ConsistencyTab._rolling_hit_ratio_chart(metrics)
        with col2:
            ConsistencyTab._rolling_sharpe_chart(metrics)
        with st.expander("View Raw Metrics JSON"):
            st.json(metrics)

    @staticmethod
    def _rolling_returns_chart(metrics):
        st.markdown("#### Rolling Returns Consistency — 3Y vs 5Y")
        roll = metrics.get('rolling_data', {})
        stat_labels = ['Median', '25th %ile', 'Std Dev']
        stat_keys   = ['median', 'percentile_25', 'std_dev']
        mid_3y = ['rolling_3y_median', 'rolling_3y_percentile_25', 'rolling_3y_std_dev']
        mid_5y = ['rolling_5y_median', 'rolling_5y_percentile_25', 'rolling_5y_std_dev']

        def _vals(y):
            entry = roll.get(y, {})
            return [entry.get(k, 0) if isinstance(entry, dict) else 0 for k in stat_keys]

        v3, v5 = _vals(3), _vals(5)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='3Y Window', x=stat_labels, y=v3,
                             text=[f"{v:.2f}%" for v in v3], textposition='auto',
                             marker_color=[get_color(m, v) for m, v in zip(mid_3y, v3)]))
        fig.add_trace(go.Bar(name='5Y Window', x=stat_labels, y=v5,
                             text=[f"{v:.2f}%" for v in v5], textposition='auto',
                             marker_color=[get_color(m, v) for m, v in zip(mid_5y, v5)]))
        fig.update_layout(template="plotly_white", barmode='group',
                          title="Rolling Returns: Median / 25th %ile / Std Dev",
                          yaxis_title="Return (%)", height=380)
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _rolling_hit_ratio_chart(metrics):
        st.markdown("#### Rolling Hit Ratio Consistency — 3Y vs 5Y")
        roll_hit = metrics.get('rolling_hit_ratio_data', [])
        hit_3y = next((i for i in roll_hit if i.get('rolling_window') == 3), None)
        hit_5y = next((i for i in roll_hit if i.get('rolling_window') == 5), None)
        hit_labels = ['Median', '25th %ile']
        mid_3y = ['rolling_hit_ratio_3y_median', 'rolling_hit_ratio_3y_percentile_25']
        mid_5y = ['rolling_hit_ratio_5y_median', 'rolling_hit_ratio_5y_percentile_25']

        def _safe(entry, key):
            return entry.get(key, 0) if entry and 'error' not in entry else 0

        h3 = [_safe(hit_3y, 'median'), _safe(hit_3y, 'percentile_25')]
        h5 = [_safe(hit_5y, 'median'), _safe(hit_5y, 'percentile_25')]

        if any(h3) or any(h5):
            fig = go.Figure()
            fig.add_trace(go.Bar(name='3Y Window', x=hit_labels, y=h3,
                                 text=[f"{v:.2f}%" for v in h3], textposition='auto',
                                 marker_color=[get_color(m, v) for m, v in zip(mid_3y, h3)]))
            fig.add_trace(go.Bar(name='5Y Window', x=hit_labels, y=h5,
                                 text=[f"{v:.2f}%" for v in h5], textposition='auto',
                                 marker_color=[get_color(m, v) for m, v in zip(mid_5y, h5)]))
            fig.update_layout(template="plotly_white", barmode='group',
                              title="Rolling Hit Ratio: Median / 25th %ile",
                              yaxis_title="Hit Ratio (%)", height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Rolling Hit Ratio data not available (requires benchmark).")

    @staticmethod
    def _rolling_sharpe_chart(metrics):
        st.markdown("#### Rolling Sharpe Consistency — 3Y vs 5Y")
        roll_sharpe = metrics.get('rolling_sharpe_data', [])
        sh_3y = next((i for i in roll_sharpe if i.get('rolling_window') == 3), None)
        sh_5y = next((i for i in roll_sharpe if i.get('rolling_window') == 5), None)
        sh_labels = ['Median', '25th %ile', 'Std Dev']
        sh_keys   = ['median', 'percentile_25', 'std_dev']
        mid_3y = ['rolling_sharpe_3y_median', 'rolling_sharpe_3y_percentile_25', 'rolling_sharpe_3y_std_dev']
        mid_5y = ['rolling_sharpe_5y_median', 'rolling_sharpe_5y_percentile_25', 'rolling_sharpe_5y_std_dev']

        def _safe(entry, key):
            return entry.get(key, 0) if entry and 'error' not in entry else 0

        s3 = [_safe(sh_3y, k) for k in sh_keys]
        s5 = [_safe(sh_5y, k) for k in sh_keys]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='3Y Window', x=sh_labels, y=s3,
                             text=[f"{v:.2f}" for v in s3], textposition='auto',
                             marker_color=[get_color(m, v) for m, v in zip(mid_3y, s3)]))
        fig.add_trace(go.Bar(name='5Y Window', x=sh_labels, y=s5,
                             text=[f"{v:.2f}" for v in s5], textposition='auto',
                             marker_color=[get_color(m, v) for m, v in zip(mid_5y, s5)]))
        fig.update_layout(template="plotly_white", barmode='group',
                          title="Rolling Sharpe: Median / 25th %ile / Std Dev",
                          yaxis_title="Sharpe Ratio", height=380)
        st.plotly_chart(fig, use_container_width=True)


render = ConsistencyTab.render
