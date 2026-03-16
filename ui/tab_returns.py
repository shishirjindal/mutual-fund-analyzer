"""Tab 1 — Return Performance."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any


class ReturnsTab:
    """Renders the Return Performance tab."""

    @staticmethod
    def render(metrics: Dict[str, Any]) -> None:
        st.subheader("Return Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### CAGR by Period (1Y / 3Y / 5Y)")
            roll = metrics.get('rolling_data', {})
            cagr_periods, cagr_values = [], []
            for y, label in [(1, '1Y'), (3, '3Y'), (5, '5Y')]:
                val = roll.get(y, {}).get('avg') if isinstance(roll.get(y), dict) else None
                cagr_periods.append(label)
                cagr_values.append(val if val is not None else 0)
            fig = go.Figure(go.Bar(
                x=cagr_periods, y=cagr_values,
                text=[f"{v:.2f}%" for v in cagr_values], textposition='auto',
                marker_color=['#636EFA', '#EF553B', '#00CC96']
            ))
            fig.update_layout(template="plotly_white", title="Avg Rolling CAGR (%)", yaxis_title="CAGR (%)", height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Calendar Year Returns")
            cal = metrics.get('calendar_data', {})
            cal_plot = sorted([(yr, v) for yr, v in cal.items() if v is not None])
            if cal_plot:
                df_cal = pd.DataFrame(cal_plot, columns=['Year', 'Return (%)'])
                colors = ['crimson' if v < 0 else 'steelblue' for v in df_cal['Return (%)']]
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
