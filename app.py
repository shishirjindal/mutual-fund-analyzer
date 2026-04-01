import streamlit as st

pg = st.navigation([
    st.Page("pages/1_Fund_Analyzer.py",       title="Fund Analyzer",        icon="📈"),
    st.Page("pages/2_Portfolio_Allocation.py", title="Portfolio Allocation", icon="📊"),
])
st.set_page_config(page_title="Mutual Fund Analyzer", layout="wide")
pg.run()
