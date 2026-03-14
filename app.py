import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from mfa import MutualFundAnalyzer
from decision_engine import DecisionEngine
from constants import Constants
import datetime

st.set_page_config(page_title="Mutual Fund Analyzer", layout="wide")

# Custom CSS for table styling
st.markdown("""
    <style>
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
    }
    /* Center all text in the table rendered by st.table */
    div[data-testid="stTable"] table {
        width: 100% !important;
    }
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {
        text-align: center !important;
        vertical-align: middle !important;
        word-wrap: break-word !important;
        white-space: pre-line !important;
        min-width: 100px !important;
        padding: 10px !important;
    }
    /* Specific wider column for Scheme Name */
    div[data-testid="stTable"] th:first-child, div[data-testid="stTable"] td:first-child {
        min-width: 250px !important;
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Mutual Fund Analyzer")
st.markdown("Analyze mutual fund performance using various risk and return metrics.")

# Sidebar for input
st.sidebar.header("Input Parameters")
scheme_codes_input = st.sidebar.text_input("Enter Scheme Code(s)", value="", help="Enter multiple codes separated by comma (e.g., 101206,112277)")
analyze_button = st.sidebar.button("Analyze")

if analyze_button or scheme_codes_input:
    scheme_codes = [code.strip() for code in scheme_codes_input.split(",") if code.strip()]
    
    if not scheme_codes:
        st.info("Please enter one or more scheme codes in the sidebar.")
    else:
        all_results = []
        with st.spinner(f"Analyzing {len(scheme_codes)} mutual funds..."):
            for code in scheme_codes:
                try:
                    analyzer = MutualFundAnalyzer(code)
                    analyzer.process_scheme()
                    metrics = analyzer.get_metrics()
                    if metrics and metrics.get('scheme_name') != 'Unknown':
                        all_results.append(metrics)
                    else:
                        st.error(f"Could not fetch data for scheme code {code}.")
                except Exception as e:
                    st.error(f"Error analyzing scheme {code}: {str(e)}")

        if all_results:
            # st.write(f"Analyzing {len(all_results)} funds...")
            # --- Batch Calculate Scores for all funds ---
            all_results = DecisionEngine.calculate_batch_scores(all_results)
            # st.write("Batch calculation complete.")

            # --- Multi-Fund Comparison Section ---
            st.header("🏆 Mutual Fund Comparison Summary")
            
            # Prepare comparison table data with multi-line headers
            comparison_data = []
            raw_comparison_data = [] # For CSV download without newlines
            for metrics in all_results:
                row = {
                    'Scheme Name': metrics['scheme_name'],
                    'Overall\nScore': metrics['final_score']
                }
                raw_row = {
                    'Scheme Name': metrics['scheme_name'],
                    'Overall Score': metrics['final_score']
                }
                # Add categories with shorter names or newlines for wrapping
                for cat, score in metrics['category_scores'].items():
                    # Replace spaces with newlines to force multi-line headers
                    new_cat = cat.replace(' ', '\n').replace('-', '-\n')
                    row[new_cat] = score
                    raw_row[cat] = score
                comparison_data.append(row)
                raw_comparison_data.append(raw_row)
            
            comparison_df = pd.DataFrame(comparison_data).sort_values(by='Overall\nScore', ascending=False)
            raw_df = pd.DataFrame(raw_comparison_data).sort_values(by='Overall Score', ascending=False)
            
            # Display comparison table with enhanced styling
            st.subheader("📊 Ranking & Score Breakdown")
            
            # Apply styling
            styled_df = comparison_df.set_index('Scheme Name').style \
                .format("{:.2f}") \
                .background_gradient(cmap='RdYlGn', subset=['Overall\nScore'], low=0.4, high=0.2) \
                .set_properties(**{
                    'border': '1px solid #e6e9ef'
                })
            
            st.table(styled_df)
            
            # Download CSV
            csv = raw_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Comparison CSV",
                data=csv,
                file_name=f"fund_comparison_{datetime.date.today()}.csv",
                mime='text/csv',
            )

            st.divider()
            
            # --- Individual Fund Detail Section ---
            st.header("🔍 Individual Fund Details")
            selected_scheme_name = st.selectbox("Select a fund to view detailed metrics", options=[m['scheme_name'] for m in all_results])
            
            # Find selected metrics
            metrics = next(m for m in all_results if m['scheme_name'] == selected_scheme_name)
            
            st.subheader(f"Detailed Analysis: {metrics['scheme_name']}")
            
            # Key Highlights Row
            h_col1, h_col2, h_col3, h_col4 = st.columns(4)
            with h_col1:
                st.metric("Overall Score", f"{metrics['final_score']}/100")
            with h_col2:
                # Get latest rolling return if available
                latest_ret = "N/A"
                if metrics.get('rolling_data') and 3 in metrics['rolling_data']:
                    latest_ret = f"{metrics['rolling_data'][3].get('avg', 'N/A')}%"
                st.metric("3Y Avg Rolling Return", latest_ret)
            with h_col3:
                # Max Drawdown 3Y
                mdd = "N/A"
                if metrics.get('static_drawdown_data') and 3 in metrics['static_drawdown_data']:
                    mdd = f"{metrics['static_drawdown_data'][3].get('max_drawdown', 'N/A')}%"
                st.metric("3Y Max Drawdown", mdd)
            with h_col4:
                # Sharpe 3Y
                sharpe = "N/A"
                if metrics.get('static_sharpe_data') and 3 in metrics['static_sharpe_data']:
                    sharpe = metrics['static_sharpe_data'][3]
                st.metric("3Y Sharpe Ratio", sharpe)

            st.info(f"Analyzing **{metrics['scheme_name']}** based on weighted scorecard: Returns, Risk, Risk-Adjusted, Manager Skill, and Consistency.")

            # --- Tabs aligned to decision_config.py categories ---
            tab_returns, tab_risk, tab_risk_adj, tab_skill, tab_consistency = st.tabs([
                "📈 Return Performance",
                "📉 Risk",
                "⚖️ Risk-Adjusted Performance",
                "🎯 Manager Skill vs Benchmark",
                "🔄 Consistency (Rolling)"
            ])

            # ── TAB 1: Return Performance ──────────────────────────────────────────
            with tab_returns:
                st.subheader("Return Performance")
                col1, col2 = st.columns(2)

                with col1:
                    # 5Y CAGR, 3Y CAGR, 1Y Return — grouped bar (avg rolling returns)
                    st.markdown("#### CAGR by Period (1Y / 3Y / 5Y)")
                    roll = metrics.get('rolling_data', {})
                    cagr_periods = []
                    cagr_values = []
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
                    # Calendar Year Returns (calendar_avg + worst_calendar_year)
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
                        fig.update_layout(template="plotly_white", title="Calendar Year Returns (%)", yaxis_title="Return (%)", height=380)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Calendar year data not available.")

                # Worst Calendar Year metric card
                worst_cal = metrics.get('worst_calendar_data', {})
                if worst_cal and worst_cal.get('worst_return') is not None:
                    st.metric(
                        label=f"Worst Calendar Year ({worst_cal.get('worst_year', 'N/A')})",
                        value=f"{worst_cal.get('worst_return', 'N/A')}%",
                        delta_color="inverse"
                    )

            # ── TAB 2: Risk ────────────────────────────────────────────────────────
            with tab_risk:
                st.subheader("Risk")
                col1, col2 = st.columns(2)

                with col1:
                    # Max Drawdown 5Y value + duration (grouped: value vs duration on secondary axis)
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

                    # Std Dev 3Y & 5Y
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

                with col2:
                    # Ulcer Index 5Y
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

                    # Rolling MDD 3Y — Median, 75th %ile, Worst
                    st.markdown("#### Rolling Max Drawdown — 3Y Window (Median / 75th %ile / Worst)")
                    roll_dd = metrics.get('rolling_drawdown_data', [])
                    rdd_3y = next((i for i in roll_dd if i.get('rolling_window') == 3), None)
                    if rdd_3y and 'error' not in rdd_3y:
                        rdd_labels = ['Median', '75th %ile', 'Worst']
                        rdd_vals = [
                            abs(rdd_3y.get('median', 0)),
                            abs(rdd_3y.get('percentile_75', 0)),
                            abs(rdd_3y.get('min', 0))
                        ]
                        fig = go.Figure(go.Bar(
                            x=rdd_labels, y=rdd_vals,
                            text=[f"{v:.2f}%" for v in rdd_vals], textposition='auto',
                            marker_color=['#19D3F3', '#FF6692', '#B6E880']
                        ))
                        fig.update_layout(template="plotly_white", title="Rolling MDD 3Y (%)", yaxis_title="Drawdown (%)", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Rolling drawdown data not available.")

            # ── TAB 3: Risk-Adjusted Performance ──────────────────────────────────
            with tab_risk_adj:
                st.subheader("Risk-Adjusted Performance")

                # Sharpe 3Y & 5Y
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Sharpe Ratio (3Y / 5Y)")
                    sharpe = metrics.get('static_sharpe_data', {})
                    sharpe_vals = {y: sharpe.get(y) for y in [3, 5] if not isinstance(sharpe.get(y), dict) and sharpe.get(y) is not None}
                    if sharpe_vals:
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in sharpe_vals], y=list(sharpe_vals.values()),
                            text=[f"{v:.2f}" for v in sharpe_vals.values()], textposition='auto',
                            marker_color=['#636EFA', '#EF553B']
                        ))
                        fig.update_layout(template="plotly_white", title="Sharpe Ratio", yaxis_title="Ratio", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Sharpe Ratio data not available.")

                    st.markdown("#### Calmar Ratio (3Y / 5Y)")
                    calmar = metrics.get('static_calmar_ratio_data', {})
                    calmar_vals = {y: calmar.get(y) for y in [3, 5] if not isinstance(calmar.get(y), dict) and calmar.get(y) is not None}
                    if calmar_vals:
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in calmar_vals], y=list(calmar_vals.values()),
                            text=[f"{v:.2f}" for v in calmar_vals.values()], textposition='auto',
                            marker_color=['#00CC96', '#AB63FA']
                        ))
                        fig.update_layout(template="plotly_white", title="Calmar Ratio", yaxis_title="Ratio", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Calmar Ratio data not available.")

                with col2:
                    st.markdown("#### Sortino Ratio (3Y / 5Y)")
                    sortino = metrics.get('static_sortino_data', {})
                    sortino_vals = {y: sortino.get(y) for y in [3, 5] if not isinstance(sortino.get(y), dict) and sortino.get(y) is not None}
                    if sortino_vals:
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in sortino_vals], y=list(sortino_vals.values()),
                            text=[f"{v:.2f}" for v in sortino_vals.values()], textposition='auto',
                            marker_color=['#FFA15A', '#19D3F3']
                        ))
                        fig.update_layout(template="plotly_white", title="Sortino Ratio", yaxis_title="Ratio", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Sortino Ratio data not available.")

                    st.markdown("#### Treynor Ratio (3Y / 5Y)")
                    treynor = metrics.get('static_treynor_ratio_data', {})
                    treynor_vals = {y: treynor.get(y) for y in [3, 5] if not isinstance(treynor.get(y), dict) and treynor.get(y) is not None}
                    if treynor_vals:
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in treynor_vals], y=list(treynor_vals.values()),
                            text=[f"{v:.2f}" for v in treynor_vals.values()], textposition='auto',
                            marker_color=['#FF6692', '#B6E880']
                        ))
                        fig.update_layout(template="plotly_white", title="Treynor Ratio", yaxis_title="Ratio", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Treynor Ratio data not available.")

                # Grouped comparison chart — all 4 ratios side by side for 3Y vs 5Y
                st.markdown("#### All Risk-Adjusted Ratios — 3Y vs 5Y Comparison")
                ratio_names = ['Sharpe', 'Sortino', 'Calmar', 'Treynor']
                ratio_keys = ['static_sharpe_data', 'static_sortino_data', 'static_calmar_ratio_data', 'static_treynor_ratio_data']
                vals_3y = [metrics.get(k, {}).get(3) for k in ratio_keys]
                vals_5y = [metrics.get(k, {}).get(5) for k in ratio_keys]
                vals_3y = [v if isinstance(v, (int, float)) else 0 for v in vals_3y]
                vals_5y = [v if isinstance(v, (int, float)) else 0 for v in vals_5y]
                fig = go.Figure()
                fig.add_trace(go.Bar(name='3Y', x=ratio_names, y=vals_3y, text=[f"{v:.2f}" for v in vals_3y], textposition='auto'))
                fig.add_trace(go.Bar(name='5Y', x=ratio_names, y=vals_5y, text=[f"{v:.2f}" for v in vals_5y], textposition='auto'))
                fig.update_layout(template="plotly_white", barmode='group', title="Risk-Adjusted Ratios: 3Y vs 5Y", yaxis_title="Ratio Value", height=400)
                st.plotly_chart(fig, use_container_width=True)

            # ── TAB 4: Manager Skill vs Benchmark ─────────────────────────────────
            with tab_skill:
                st.subheader("Manager Skill vs Benchmark")
                has_benchmark = bool(metrics.get('static_alpha_data'))
                if not has_benchmark:
                    st.info("Benchmark data is not yet available. Once benchmark fetching is implemented, this tab will show Alpha, Information Ratio, Hit Ratio, and their rolling statistics.")

                col1, col2 = st.columns(2)
                with col1:
                    # Alpha 3Y & 5Y
                    st.markdown("#### Alpha — Jensen's Alpha % (3Y / 5Y)")
                    alpha = metrics.get('static_alpha_data', {})
                    alpha_vals = {y: alpha.get(y) for y in [3, 5] if not isinstance(alpha.get(y), dict) and alpha.get(y) is not None}
                    if alpha_vals:
                        colors = ['green' if v >= 0 else 'red' for v in alpha_vals.values()]
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in alpha_vals], y=list(alpha_vals.values()),
                            text=[f"{v:.2f}%" for v in alpha_vals.values()], textposition='auto',
                            marker_color=colors
                        ))
                        fig.update_layout(template="plotly_white", title="Alpha (%)", yaxis_title="Alpha (%)", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = go.Figure()
                        fig.update_layout(template="plotly_white", title="Alpha (%) — No Data", height=350,
                                          annotations=[dict(text="Benchmark data unavailable", showarrow=False, font_size=14)])
                        st.plotly_chart(fig, use_container_width=True)

                    # Information Ratio 3Y & 5Y
                    st.markdown("#### Information Ratio (3Y / 5Y)")
                    ir = metrics.get('static_information_ratio_data', {})
                    ir_vals = {y: ir.get(y) for y in [3, 5] if not isinstance(ir.get(y), dict) and ir.get(y) is not None}
                    if ir_vals:
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in ir_vals], y=list(ir_vals.values()),
                            text=[f"{v:.2f}" for v in ir_vals.values()], textposition='auto',
                            marker_color=['#636EFA', '#EF553B']
                        ))
                        fig.update_layout(template="plotly_white", title="Information Ratio", yaxis_title="IR", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = go.Figure()
                        fig.update_layout(template="plotly_white", title="Information Ratio — No Data", height=350,
                                          annotations=[dict(text="Benchmark data unavailable", showarrow=False, font_size=14)])
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Hit Ratio 3Y & 5Y
                    st.markdown("#### Hit Ratio — Outperformance % (3Y / 5Y)")
                    hr = metrics.get('static_hit_ratio_data', {})
                    hr_vals = {y: hr.get(y) for y in [3, 5] if not isinstance(hr.get(y), dict) and hr.get(y) is not None}
                    if hr_vals:
                        fig = go.Figure(go.Bar(
                            x=[f"{y}Y" for y in hr_vals], y=list(hr_vals.values()),
                            text=[f"{v:.2f}%" for v in hr_vals.values()], textposition='auto',
                            marker_color=['#00CC96', '#AB63FA']
                        ))
                        fig.update_layout(template="plotly_white", title="Hit Ratio (%)", yaxis_title="Hit Ratio (%)", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = go.Figure()
                        fig.update_layout(template="plotly_white", title="Hit Ratio (%) — No Data", height=350,
                                          annotations=[dict(text="Benchmark data unavailable", showarrow=False, font_size=14)])
                        st.plotly_chart(fig, use_container_width=True)

                    # Rolling Alpha 3Y — Median, % Positive, Std Dev
                    st.markdown("#### Rolling Alpha 3Y — Median / % Positive / Std Dev")
                    roll_alpha = metrics.get('rolling_alpha_data', [])
                    ra_3y = next((i for i in roll_alpha if i.get('rolling_window') == 3), None)
                    if ra_3y and 'error' not in ra_3y:
                        fig = go.Figure(go.Bar(
                            x=['Median Alpha', '% Positive Windows', 'Std Dev'],
                            y=[ra_3y.get('median', 0), ra_3y.get('positive_share', 0), ra_3y.get('std_dev', 0)],
                            text=[f"{v:.2f}" for v in [ra_3y.get('median', 0), ra_3y.get('positive_share', 0), ra_3y.get('std_dev', 0)]],
                            textposition='auto', marker_color=['#19D3F3', '#FF6692', '#B6E880']
                        ))
                        fig.update_layout(template="plotly_white", title="Rolling Alpha 3Y Stats", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = go.Figure()
                        fig.update_layout(template="plotly_white", title="Rolling Alpha 3Y — No Data", height=350,
                                          annotations=[dict(text="Benchmark data unavailable", showarrow=False, font_size=14)])
                        st.plotly_chart(fig, use_container_width=True)

                # Rolling IR 3Y — Median, % Positive, Std Dev
                st.markdown("#### Rolling Information Ratio 3Y — Median / % Positive / Std Dev")
                roll_ir = metrics.get('rolling_information_ratio_data', [])
                rir_3y = next((i for i in roll_ir if i.get('rolling_window') == 3), None)
                if rir_3y and 'error' not in rir_3y:
                    fig = go.Figure(go.Bar(
                        x=['Median IR', '% Positive IR', 'Std Dev'],
                        y=[rir_3y.get('median', 0), rir_3y.get('positive_share', 0), rir_3y.get('std_dev', 0)],
                        text=[f"{v:.2f}" for v in [rir_3y.get('median', 0), rir_3y.get('positive_share', 0), rir_3y.get('std_dev', 0)]],
                        textposition='auto', marker_color=['#636EFA', '#EF553B', '#00CC96']
                    ))
                    fig.update_layout(template="plotly_white", title="Rolling IR 3Y Stats", height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = go.Figure()
                    fig.update_layout(template="plotly_white", title="Rolling IR 3Y — No Data", height=350,
                                      annotations=[dict(text="Benchmark data unavailable", showarrow=False, font_size=14)])
                    st.plotly_chart(fig, use_container_width=True)

            # ── TAB 5: Consistency (Rolling) ───────────────────────────────────────
            with tab_consistency:
                st.subheader("Consistency (Rolling)")
                col1, col2 = st.columns(2)

                with col1:
                    # Rolling Returns — 5Y & 3Y: Median, 25th %ile, Std Dev
                    st.markdown("#### Rolling Returns Consistency — 3Y vs 5Y")
                    roll = metrics.get('rolling_data', {})
                    ret_metrics = ['Median', '25th %ile', 'Std Dev']
                    ret_3y_vals = [
                        roll.get(3, {}).get('median', 0) if isinstance(roll.get(3), dict) else 0,
                        roll.get(3, {}).get('percentile_25', 0) if isinstance(roll.get(3), dict) else 0,
                        roll.get(3, {}).get('std_dev', 0) if isinstance(roll.get(3), dict) else 0,
                    ]
                    ret_5y_vals = [
                        roll.get(5, {}).get('median', 0) if isinstance(roll.get(5), dict) else 0,
                        roll.get(5, {}).get('percentile_25', 0) if isinstance(roll.get(5), dict) else 0,
                        roll.get(5, {}).get('std_dev', 0) if isinstance(roll.get(5), dict) else 0,
                    ]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='3Y Window', x=ret_metrics, y=ret_3y_vals,
                                         text=[f"{v:.2f}%" for v in ret_3y_vals], textposition='auto'))
                    fig.add_trace(go.Bar(name='5Y Window', x=ret_metrics, y=ret_5y_vals,
                                         text=[f"{v:.2f}%" for v in ret_5y_vals], textposition='auto'))
                    fig.update_layout(template="plotly_white", barmode='group',
                                      title="Rolling Returns: Median / 25th %ile / Std Dev",
                                      yaxis_title="Return (%)", height=380)
                    st.plotly_chart(fig, use_container_width=True)

                    # Rolling Hit Ratio — 3Y & 5Y: Median, 25th %ile
                    st.markdown("#### Rolling Hit Ratio Consistency — 3Y vs 5Y")
                    roll_hit = metrics.get('rolling_hit_ratio_data', [])
                    hit_3y = next((i for i in roll_hit if i.get('rolling_window') == 3), None)
                    hit_5y = next((i for i in roll_hit if i.get('rolling_window') == 5), None)
                    hit_metrics = ['Median', '25th %ile']
                    h3 = [hit_3y.get('median', 0) if hit_3y and 'error' not in hit_3y else 0,
                          hit_3y.get('percentile_25', 0) if hit_3y and 'error' not in hit_3y else 0]
                    h5 = [hit_5y.get('median', 0) if hit_5y and 'error' not in hit_5y else 0,
                          hit_5y.get('percentile_25', 0) if hit_5y and 'error' not in hit_5y else 0]
                    if any(h3) or any(h5):
                        fig = go.Figure()
                        fig.add_trace(go.Bar(name='3Y Window', x=hit_metrics, y=h3,
                                             text=[f"{v:.2f}%" for v in h3], textposition='auto'))
                        fig.add_trace(go.Bar(name='5Y Window', x=hit_metrics, y=h5,
                                             text=[f"{v:.2f}%" for v in h5], textposition='auto'))
                        fig.update_layout(template="plotly_white", barmode='group',
                                          title="Rolling Hit Ratio: Median / 25th %ile",
                                          yaxis_title="Hit Ratio (%)", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Rolling Hit Ratio data not available (requires benchmark).")

                with col2:
                    # Rolling Sharpe — 5Y & 3Y: Median, 25th %ile, Std Dev
                    st.markdown("#### Rolling Sharpe Consistency — 3Y vs 5Y")
                    roll_sharpe = metrics.get('rolling_sharpe_data', [])
                    sh_3y = next((i for i in roll_sharpe if i.get('rolling_window') == 3), None)
                    sh_5y = next((i for i in roll_sharpe if i.get('rolling_window') == 5), None)
                    sh_metrics = ['Median', '25th %ile', 'Std Dev']
                    s3 = [sh_3y.get('median', 0) if sh_3y and 'error' not in sh_3y else 0,
                          sh_3y.get('percentile_25', 0) if sh_3y and 'error' not in sh_3y else 0,
                          sh_3y.get('std_dev', 0) if sh_3y and 'error' not in sh_3y else 0]
                    s5 = [sh_5y.get('median', 0) if sh_5y and 'error' not in sh_5y else 0,
                          sh_5y.get('percentile_25', 0) if sh_5y and 'error' not in sh_5y else 0,
                          sh_5y.get('std_dev', 0) if sh_5y and 'error' not in sh_5y else 0]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='3Y Window', x=sh_metrics, y=s3,
                                         text=[f"{v:.2f}" for v in s3], textposition='auto'))
                    fig.add_trace(go.Bar(name='5Y Window', x=sh_metrics, y=s5,
                                         text=[f"{v:.2f}" for v in s5], textposition='auto'))
                    fig.update_layout(template="plotly_white", barmode='group',
                                      title="Rolling Sharpe: Median / 25th %ile / Std Dev",
                                      yaxis_title="Sharpe Ratio", height=380)
                    st.plotly_chart(fig, use_container_width=True)

            # Show Raw Data in an expander
            with st.expander("View Raw Metrics JSON"):
                st.json(metrics)



else:
    st.info("Enter one or more scheme codes in the sidebar and click 'Analyze' to begin.")
