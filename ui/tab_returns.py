"""Tab 1 — Return Performance."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any
from ui.metric_colors import get_color, get_colors


class ReturnsTab:
    """Renders the Return Performance tab."""

    @staticmethod
    def render(metrics: Dict[str, Any]) -> None:
        st.subheader("Return Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### CAGR by Period (1Y / 3Y / 5Y)")
            roll = metrics.get('rolling_data', {})
            metric_ids = ['static_1y_return', 'static_3y_cagr', 'static_5y_cagr']
            periods = ['1Y', '3Y', '5Y']
            years = [1, 3, 5]
            cagr_values = [
                roll.get(y, {}).get('avg') if isinstance(roll.get(y), dict) else None
                for y in years
            ]
            colors = [get_color(mid, v) for mid, v in zip(metric_ids, cagr_values)]
            plot_vals = [v if v is not None else 0 for v in cagr_values]
            fig = go.Figure(go.Bar(
                x=periods, y=plot_vals,
                text=[f"{v:.2f}%" for v in plot_vals], textposition='auto',
                marker_color=colors
            ))
            fig.update_layout(template="plotly_white", title="Avg Rolling CAGR (%)", yaxis_title="CAGR (%)", height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Calendar Year Returns")
            cal = metrics.get('calendar_data', {})
            cal_plot = sorted([(yr, v) for yr, v in cal.items() if v is not None])
            if cal_plot:
                df_cal = pd.DataFrame(cal_plot, columns=['Year', 'Return (%)'])
                colors = [get_color('calendar_avg', v) for v in df_cal['Return (%)']]
                fig = go.Figure(go.Bar(
                    x=df_cal['Year'].astype(str), y=df_cal['Return (%)'],
                    marker_color=colors,
                    text=[f"{v:.2f}%" for v in df_cal['Return (%)']],
                    textposition='auto'
                ))
                fig.update_layout(template="plotly_white", title="Calendar Year Returns (%)",
                                  yaxis_title="Return (%)", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Calendar year data not available.")

        worst_cal = metrics.get('worst_calendar_data', {})
        if worst_cal and worst_cal.get('worst_return') is not None:
            st.metric(
                label=f"Worst Calendar Year ({worst_cal.get('worst_year', 'N/A')})",
                value=f"{worst_cal.get('worst_return', 'N/A')}%",
                delta_color="inverse"
            )


render = ReturnsTab.render
