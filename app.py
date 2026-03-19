import time
import logging
import datetime
import streamlit as st
from mfa import MutualFundAnalyzer
from decision_engine.decision_engine import DecisionEngine
from decision_engine.risk_profiles import RISK_PROFILES
from fetchers.amfi_fetcher import AmfiFetcher
from constants.amfi_constants import SECTOR_KEYWORDS
from log.logger_config import configure_logging
from ui import comparison_table, tab_returns, tab_risk, tab_risk_adjusted, tab_manager_skill, tab_consistency

configure_logging()

st.set_page_config(page_title="Mutual Fund Analyzer", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stTable"] table { width: 100% !important; }
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {
        text-align: center !important;
        vertical-align: middle !important;
        word-wrap: break-word !important;
        white-space: pre-line !important;
        min-width: 100px !important;
        padding: 10px !important;
    }
    div[data-testid="stTable"] th:first-child, div[data-testid="stTable"] td:first-child {
        min-width: 250px !important;
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Mutual Fund Analyzer")
st.markdown("Analyze mutual fund performance using various risk and return metrics.")

st.sidebar.header("Input Parameters")

risk_profile = st.sidebar.radio(
    "Risk Profile",
    list(RISK_PROFILES.keys()),
    index=0,  # default: Balanced
    help="Conservative: lower risk weight. Balanced: equal. Aggressive: higher return weight.",
)

analysis_mode = st.sidebar.radio("Analysis Mode", ["By Scheme Code", "By Category"], horizontal=True)

if analysis_mode == "By Scheme Code":
    scheme_codes_input = st.sidebar.text_input("Enter Scheme Code(s)", value="",
                                               help="Enter multiple codes separated by comma (e.g., 101206,112277)")
    analyze_button = st.sidebar.button("Analyze")
    run_analysis = analyze_button or bool(scheme_codes_input)
    selected_category = None
    selected_sector = None
else:
    scheme_codes_input = ""
    fetcher = AmfiFetcher()
    all_groups = fetcher.get_all_groups()
    selected_group = st.sidebar.selectbox("Select Fund Type", all_groups)
    categories_for_group = fetcher.get_categories_for_group(selected_group)
    selected_category = st.sidebar.selectbox("Select Category", categories_for_group)
    selected_sector = None
    if selected_category == "Sectoral / Thematic":
        with st.spinner("Loading sector list..."):
            _all_sectoral = AmfiFetcher().get_funds_for_category("Sectoral / Thematic")
            _sectors = fetcher.get_sectors_from_funds(_all_sectoral)
        if _sectors:
            selected_sector = st.sidebar.selectbox("Select Sector", _sectors)
    analyze_button = st.sidebar.button("Analyze Category")
    run_analysis = analyze_button

st.sidebar.divider()
st.sidebar.markdown("**Chart Color Guide**")
st.sidebar.markdown(
    """
<div style="line-height:2">
  <span style="color:#2ecc71;font-size:18px">●</span>&nbsp; Excellent<br>
  <span style="color:#3498db;font-size:18px">●</span>&nbsp; Good<br>
  <span style="color:#f39c12;font-size:18px">●</span>&nbsp; Average<br>
  <span style="color:#e74c3c;font-size:18px">●</span>&nbsp; Weak
</div>
""",
    unsafe_allow_html=True,
)

if run_analysis:
    if analysis_mode == "By Category" and selected_category:
        category_status = None
        with st.spinner(f"Fetching all Direct Growth funds in '{selected_category}' from AMFI..."):
            try:
                funds = AmfiFetcher().get_funds_for_category(selected_category)
            except Exception as e:
                st.error(f"Failed to fetch funds from AMFI: {e}")
                funds = []

        # Filter by sector for Sectoral / Thematic
        if selected_category == "Sectoral / Thematic" and selected_sector:
            kws = SECTOR_KEYWORDS.get(selected_sector, [selected_sector.lower()])
            funds = [f for f in funds if any(kw in f["scheme_name"].lower() for kw in kws)]
            display_label = f"'{selected_sector}' sector"
        else:
            display_label = f"'{selected_category}'"

        if not funds:
            st.warning(f"No Direct Growth funds found for {display_label}")
            scheme_codes = []
        else:
            category_status = st.empty()
            category_status.info(f"Found {len(funds)} funds in {display_label}. Starting analysis...")
            scheme_codes = [f["scheme_code"] for f in funds]
    else:
        category_status = None
        scheme_codes = [code.strip() for code in scheme_codes_input.split(",") if code.strip()]

    if not scheme_codes:
        st.info("Please enter one or more scheme codes in the sidebar.")
    else:
        all_results = []
        with st.spinner(f"Analyzing {len(scheme_codes)} mutual funds..."):
            progress = st.progress(0, text="Starting analysis...")
            for idx, code in enumerate(scheme_codes):
                progress.progress((idx + 1) / len(scheme_codes),
                                  text=f"Analyzing fund {idx + 1} of {len(scheme_codes)}...")
                try:
                    analyzer = MutualFundAnalyzer(code, sector=selected_sector or "")
                    fund_name = analyzer.scheme_data.get('scheme_name', code) if analyzer.scheme_data else code
                    progress.progress((idx + 1) / len(scheme_codes),
                                      text=f"[{idx + 1}/{len(scheme_codes)}] Analyzing: {fund_name}")
                    analyzer.process_scheme()
                    metrics = analyzer.get_metrics()
                    if metrics and metrics.get('scheme_name') != 'Unknown':
                        all_results.append(metrics)
                    else:
                        st.warning(f"Could not fetch data for scheme code {code}.")
                except Exception as e:
                    st.warning(f"Skipped scheme {code}: {str(e)}")
                if idx < len(scheme_codes) - 1:
                    time.sleep(0.5)
            progress.empty()
            if category_status:
                category_status.success(f"Analysed all {len(all_results)} funds in '{selected_category}'.")

        if all_results:
            all_results = DecisionEngine.calculate_batch_scores(all_results, risk_profile)
            st.session_state['raw_metrics'] = all_results  # store pre-score for re-scoring
            st.session_state['all_results'] = all_results
            st.session_state['selected_category'] = selected_category
            st.session_state['scored_profile'] = risk_profile

# ── Re-score if profile changed without re-fetching ──
if 'raw_metrics' in st.session_state and st.session_state.get('scored_profile') != risk_profile:
    st.session_state['all_results'] = DecisionEngine.calculate_batch_scores(
        st.session_state['raw_metrics'], risk_profile
    )
    st.session_state['scored_profile'] = risk_profile

# ── Render results (persists across widget interactions via session_state) ──
if 'all_results' in st.session_state:
    all_results = st.session_state['all_results']
    selected_category = st.session_state.get('selected_category')

    comparison_table.render(all_results, selected_category)
    st.divider()

    st.header("🔍 Individual Fund Details")
    selected_scheme_name = st.selectbox(
        "Select a fund to view detailed metrics",
        options=[m['scheme_name'] for m in all_results]
    )
    metrics = next(m for m in all_results if m['scheme_name'] == selected_scheme_name)

    st.subheader(f"Detailed Analysis: {metrics['scheme_name']}")

    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    with h_col1:
        st.metric("Overall Score", f"{metrics['final_score']}/100")
    with h_col2:
        latest_ret = "N/A"
        if metrics.get('rolling_data') and 3 in metrics['rolling_data']:
            latest_ret = f"{metrics['rolling_data'][3].get('avg', 'N/A')}%"
        st.metric("3Y Avg Rolling Return", latest_ret)
    with h_col3:
        mdd = "N/A"
        if metrics.get('static_drawdown_data') and 3 in metrics['static_drawdown_data']:
            mdd = f"{metrics['static_drawdown_data'][3].get('max_drawdown', 'N/A')}%"
        st.metric("3Y Max Drawdown", mdd)
    with h_col4:
        sharpe = "N/A"
        if metrics.get('static_sharpe_data') and 3 in metrics['static_sharpe_data']:
            sharpe = metrics['static_sharpe_data'][3]
        st.metric("3Y Sharpe Ratio", sharpe)

    from decision_engine.risk_profiles import RISK_PROFILES
    _weights = RISK_PROFILES.get(risk_profile, {})
    _labels = {
        'Return Performance':         '📈 Returns',
        'Risk':                       '📉 Risk',
        'Risk-Adjusted Performance':  '⚖️ Risk-Adjusted',
        'Manager Skill vs Benchmark': '🎯 Manager Skill',
        'Consistency (Rolling)':      '🔄 Consistency',
    }
    _weight_str = '  |  '.join(f"{_labels[k]} **{int(v*100)}%**" for k, v in _weights.items())
    st.info(f"Analyzing **{metrics['scheme_name']}** · **{risk_profile}** risk profile\n\n{_weight_str}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Return Performance",
        "📉 Risk",
        "⚖️ Risk-Adjusted Performance",
        "🎯 Manager Skill vs Benchmark",
        "🔄 Consistency (Rolling)"
    ])
    with tab1:
        tab_returns.render(metrics)
    with tab2:
        tab_risk.render(metrics)
    with tab3:
        tab_risk_adjusted.render(metrics)
    with tab4:
        tab_manager_skill.render(metrics)
    with tab5:
        tab_consistency.render(metrics)

else:
    st.info("Select an analysis mode in the sidebar and click 'Analyze' to begin.")
