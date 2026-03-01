import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from mfa import MutualFundAnalyzer
from constants import Constants
import datetime

st.set_page_config(page_title="Mutual Fund Analyzer", layout="wide")

st.title("📈 Mutual Fund Analyzer")
st.markdown("Analyze mutual fund performance using various risk and return metrics.")

# Sidebar for input
st.sidebar.header("Input Parameters")
scheme_code = st.sidebar.text_input("Enter Scheme Code", value="112277")
analyze_button = st.sidebar.button("Analyze")

if analyze_button or scheme_code:
    with st.spinner(f"Fetching and analyzing data for scheme {scheme_code}..."):
        try:
            analyzer = MutualFundAnalyzer(scheme_code)
            analyzer.process_scheme()
            metrics = analyzer.get_metrics()
            
            if not metrics or metrics.get('scheme_name') == 'Unknown':
                st.error("Could not fetch data for the given scheme code. Please check the code and try again.")
            else:
                st.header(f"Scheme: {metrics['scheme_name']}")
                
                # Create tabs for different metric categories
                tab_returns, tab_risk, tab_drawdown, tab_benchmark = st.tabs(["Returns", "Risk Metrics", "Drawdown & Management", "Benchmark Metrics"])
                
                with tab_returns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Rolling Returns (CAGR %)")
                        rolling_returns_data = metrics.get('rolling_data', {}).get('rolling_returns', {})
                        if rolling_returns_data:
                            plot_data = []
                            for year, vals in rolling_returns_data.items():
                                if 'error' not in vals:
                                    plot_data.append({
                                        'Years': f"{year}Y",
                                        'Min': vals['min'],
                                        'Average': vals['avg'],
                                        'Max': vals['max']
                                    })
                            
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df_plot['Years'], y=df_plot['Min'], name='Min', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Years'], y=df_plot['Average'], name='Average', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Years'], y=df_plot['Max'], name='Max', mode='lines+markers'))
                                fig.update_layout(title="Rolling CAGR Returns", xaxis_title="Period", yaxis_title="CAGR (%)")
                                st.plotly_chart(fig, width="stretch")
                            else:
                                st.warning("No rolling returns data available.")
                        
                    with col2:
                        st.subheader("Calendar Year Returns")
                        calendar_returns = metrics.get('calendar_data', {}).get('calendar_returns', {})
                        if calendar_returns:
                            plot_data = sorted([(year, val) for year, val in calendar_returns.items() if val is not None])
                            if plot_data:
                                df_cal = pd.DataFrame(plot_data, columns=['Year', 'Return (%)'])
                                fig = go.Figure(go.Bar(x=df_cal['Year'], y=df_cal['Return (%)'], marker_color='indianred'))
                                fig.update_layout(title="Calendar Year Returns", xaxis_title="Year", yaxis_title="Return (%)")
                                st.plotly_chart(fig, width="stretch")
                            else:
                                st.warning("No calendar returns data available.")

                with tab_risk:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sharpe Ratio
                        st.subheader("Sharpe Ratio")
                        sharpe_static = metrics.get('static_sharpe_data', {}).get('static_sharpe_ratios', {})
                        if sharpe_static:
                            plot_data = [{'Years': f"{y}Y", 'Ratio': v} for y, v in sharpe_static.items() if not isinstance(v, dict)]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Scatter(x=df_plot['Years'], y=df_plot['Ratio'], mode='lines+markers', name='Static Sharpe'))
                                fig.update_layout(title="Static Sharpe Ratio (1, 3, 5 Years)", xaxis_title="Period", yaxis_title="Ratio")
                                st.plotly_chart(fig, width="stretch")

                        # Volatility (Standard Deviation)
                        st.subheader("Standard Deviation (Volatility %)")
                        std_static = metrics.get('static_std_dev_data', {}).get('std_devs', {})
                        if std_static:
                            plot_data = [{'Years': f"{y}Y", 'Volatility (%)': v} for y, v in std_static.items() if not isinstance(v, dict)]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Scatter(x=df_plot['Years'], y=df_plot['Volatility (%)'], mode='lines+markers', name='Static Volatility'))
                                fig.update_layout(title="Static Volatility (1, 3, 5 Years)", xaxis_title="Period", yaxis_title="Volatility (%)")
                                st.plotly_chart(fig, width="stretch")

                    with col2:
                        # Sortino Ratio
                        st.subheader("Sortino Ratio")
                        sortino_static = metrics.get('static_sortino_data', {}).get('static_sortino_ratios', {})
                        if sortino_static:
                            plot_data = [{'Years': f"{y}Y", 'Ratio': v} for y, v in sortino_static.items() if not isinstance(v, dict)]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Scatter(x=df_plot['Years'], y=df_plot['Ratio'], mode='lines+markers', name='Static Sortino'))
                                fig.update_layout(title="Static Sortino Ratio (1, 3, 5 Years)", xaxis_title="Period", yaxis_title="Ratio")
                                st.plotly_chart(fig, width="stretch")

                        # Downside Deviation
                        st.subheader("Downside Deviation (%)")
                        downside_static = metrics.get('static_downside_dev_data', {}).get('downside_devs', {})
                        if downside_static:
                            plot_data = [{'Years': f"{y}Y", 'Downside Vol (%)': v} for y, v in downside_static.items() if not isinstance(v, dict)]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Scatter(x=df_plot['Years'], y=df_plot['Downside Vol (%)'], mode='lines+markers', name='Static Downside Vol'))
                                fig.update_layout(title="Static Downside Deviation (1, 3, 5 Years)", xaxis_title="Period", yaxis_title="Downside Vol (%)")
                                st.plotly_chart(fig, width="stretch")

                    st.divider()
                    st.subheader("Rolling Risk Metrics Statistics")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Rolling Sharpe
                        rolling_sharpe = metrics.get('rolling_sharpe_data', {}).get('rolling_sharpe_ratios', [])
                        if rolling_sharpe:
                            plot_data = [{'Window': f"{i['rolling_window']}Y", 'Median': i['median'], 'Latest': i['latest']} for i in rolling_sharpe if 'error' not in i]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Median'], name='Median', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Latest'], name='Latest', mode='lines+markers'))
                                fig.update_layout(title="Rolling Sharpe Ratio Statistics", xaxis_title="Window Size", yaxis_title="Ratio")
                                st.plotly_chart(fig, width="stretch")

                        # Rolling Std Dev
                        rolling_std = metrics.get('rolling_std_dev_data', {}).get('rolling_std_devs', [])
                        if rolling_std:
                            plot_data = [{'Window': f"{i['rolling_window']}Y", 'Median': i['median'], 'Latest': i['latest']} for i in rolling_std if 'error' not in i]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Median'], name='Median Vol', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Latest'], name='Latest Vol', mode='lines+markers'))
                                fig.update_layout(title="Rolling Volatility Statistics", xaxis_title="Window Size", yaxis_title="Volatility (%)")
                                st.plotly_chart(fig, width="stretch")

                    with col2:
                        # Rolling Sortino
                        rolling_sortino = metrics.get('rolling_sortino_data', {}).get('rolling_sortino_ratios', [])
                        if rolling_sortino:
                            plot_data = [{'Window': f"{i['rolling_window']}Y", 'Median': i['median'], 'Latest': i['latest']} for i in rolling_sortino if 'error' not in i]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Median'], name='Median', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Latest'], name='Latest', mode='lines+markers'))
                                fig.update_layout(title="Rolling Sortino Ratio Statistics", xaxis_title="Window Size", yaxis_title="Ratio")
                                st.plotly_chart(fig, width="stretch")

                with tab_drawdown:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Static Max Drawdown
                        st.subheader("Static Max Drawdown (%)")
                        dd_static = metrics.get('static_drawdown_data', {}).get('drawdowns', {})
                        if dd_static:
                            plot_data = [{'Years': f"{y}Y", 'Max Drawdown (%)': v['max_drawdown']} for y, v in dd_static.items() if not isinstance(v, dict) or 'error' not in v]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Bar(x=df_plot['Years'], y=df_plot['Max Drawdown (%)'], marker_color='crimson'))
                                fig.update_layout(title="Max Drawdown (1, 3, 5 Years)", xaxis_title="Period", yaxis_title="Max Drawdown (%)")
                                st.plotly_chart(fig, width="stretch")

                        # Ulcer Index
                        st.subheader("Static Ulcer Index")
                        ulcer_static = metrics.get('static_ulcer_index_data', {}).get('static_ulcer_indices', {})
                        if ulcer_static:
                            plot_data = [{'Years': f"{y}Y", 'Ulcer Index': v} for y, v in ulcer_static.items() if not isinstance(v, dict)]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Scatter(x=df_plot['Years'], y=df_plot['Ulcer Index'], mode='lines+markers', name='Ulcer Index'))
                                fig.update_layout(title="Ulcer Index (1, 3, 5 Years)", xaxis_title="Period", yaxis_title="Index Value")
                                st.plotly_chart(fig, width="stretch")

                    with col2:
                        # Rolling Max Drawdown
                        st.subheader("Rolling Max Drawdown Statistics")
                        rolling_dd = metrics.get('rolling_drawdown_data', {}).get('rolling_drawdowns', [])
                        if rolling_dd:
                            plot_data = [{'Window': f"{i['rolling_window']}Y", 'Median': i['median'], 'Worst (Min)': i['min'], 'Latest': i['latest']} for i in rolling_dd if 'error' not in i]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Median'], name='Median MDD', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Worst (Min)'], name='Worst MDD', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=df_plot['Window'], y=df_plot['Latest'], name='Latest MDD', mode='lines+markers'))
                                fig.update_layout(title="Rolling Max Drawdown Statistics", xaxis_title="Window Size", yaxis_title="Drawdown (%)")
                                st.plotly_chart(fig, width="stretch")

                        # Calmar Ratio
                        st.subheader("Static Calmar Ratio")
                        calmar_static = metrics.get('static_calmar_ratio_data', {}).get('static_calmar_ratios', {})
                        if calmar_static:
                            plot_data = [{'Years': f"{y}Y", 'Ratio': v} for y, v in calmar_static.items() if not isinstance(v, dict)]
                            if plot_data:
                                df_plot = pd.DataFrame(plot_data)
                                fig = go.Figure(go.Scatter(x=df_plot['Years'], y=df_plot['Ratio'], mode='lines+markers', name='Calmar Ratio'))
                                fig.update_layout(title="Calmar Ratio (3, 5 Years)", xaxis_title="Period", yaxis_title="Ratio")
                                st.plotly_chart(fig, width="stretch")

                with tab_benchmark:
                    st.subheader("Benchmark Comparison Metrics")
                    if not metrics.get('static_alpha_data'):
                        st.info("Benchmark metrics are only available if benchmark data can be fetched.")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            # Alpha
                            alpha_data = metrics.get('static_alpha_data', {}).get('static_alphas', {})
                            if alpha_data:
                                plot_data = [{'Years': f"{y}Y", 'Alpha (%)': v} for y, v in alpha_data.items() if not isinstance(v, dict)]
                                if plot_data:
                                    fig = go.Figure(go.Scatter(x=[d['Years'] for d in plot_data], y=[d['Alpha (%)'] for d in plot_data], mode='lines+markers'))
                                    fig.update_layout(title="Static Alpha (Jensen's Alpha)", xaxis_title="Period", yaxis_title="Alpha (%)")
                                    st.plotly_chart(fig, width="stretch")
                            
                            # Beta
                            beta_data = metrics.get('static_beta_data', {}).get('static_betas', {})
                            if beta_data:
                                plot_data = [{'Years': f"{y}Y", 'Beta': v} for y, v in beta_data.items() if not isinstance(v, dict)]
                                if plot_data:
                                    fig = go.Figure(go.Scatter(x=[d['Years'] for d in plot_data], y=[d['Beta'] for d in plot_data], mode='lines+markers'))
                                    fig.update_layout(title="Static Beta", xaxis_title="Period", yaxis_title="Beta")
                                    st.plotly_chart(fig, width="stretch")

                        with col2:
                            # Information Ratio
                            ir_data = metrics.get('static_information_ratio_data', {}).get('static_information_ratios', {})
                            if ir_data:
                                plot_data = [{'Years': f"{y}Y", 'Information Ratio': v} for y, v in ir_data.items() if not isinstance(v, dict)]
                                if plot_data:
                                    fig = go.Figure(go.Scatter(x=[d['Years'] for d in plot_data], y=[d['Information Ratio'] for d in plot_data], mode='lines+markers'))
                                    fig.update_layout(title="Static Information Ratio", xaxis_title="Period", yaxis_title="Ratio")
                                    st.plotly_chart(fig, width="stretch")
                            
                            # Hit Ratio
                            hit_data = metrics.get('static_hit_ratio_data', {}).get('static_hit_ratios', {})
                            if hit_data:
                                plot_data = [{'Years': f"{y}Y", 'Hit Ratio (%)': v} for y, v in hit_data.items() if not isinstance(v, dict)]
                                if plot_data:
                                    fig = go.Figure(go.Scatter(x=[d['Years'] for d in plot_data], y=[d['Hit Ratio (%)'] for d in plot_data], mode='lines+markers'))
                                    fig.update_layout(title="Static Hit Ratio", xaxis_title="Period", yaxis_title="Hit Ratio (%)")
                                    st.plotly_chart(fig, width="stretch")

                # Show Raw Data in an expander
                with st.expander("View Raw Metrics JSON"):
                    st.json(metrics)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)
else:
    st.info("Enter a scheme code in the sidebar and click 'Analyze' to begin.")
