# 📈 Mutual Fund & Portfolio Analyzer

A crisp, high-performance tool for mutual fund quantitative analysis and personal portfolio tracking.

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   python3 -m venv mfenv && source mfenv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Dashboard**:
   ```bash
   mfenv/bin/streamlit run app.py
   ```

## 📸 Screenshots

1. **Fund Analyzer**
   ![Fund Analyzer](assets/screenshots/fund_analyzer.png)

2. **Portfolio Allocation**
   ![Portfolio Allocation](assets/screenshots/portfolio_allocation.png)

3. **Category Comparison**
   ![Category Comparison](assets/screenshots/category_comparison.png)

4. **ETF Tracker**
   ![ETF Tracker](assets/screenshots/etf_tracker.png)

## 🛠️ Key Features

### 1. Fund Analyzer
- **Deep Quantitative Analysis**: 20+ metrics across Returns, Risk, Skill, and Consistency.
- **Relative Scoring**: Z-Score + Sigmoid pipeline for objective peer-group ranking.
- **Detailed Visuals**: Interactive charts for rolling CAGR, Drawdowns, and Alpha generation.

### 2. Portfolio Allocation
- **Asset Breakdown**: Real-time view of Equity (Core + Sectoral), International, and Commodities.
- **Smart Categorization**: Automatic "Sectoral -" prefixing for theme-based funds.
- **Visual Hierarchy**: Large category breakdown charts followed by detailed allocation tables.

### 3. ETF Tracker
- Track performance and allocation specifically for Exchange Traded Funds.

## 📁 Project Structure
- `app.py`: Main Streamlit application and navigation hub.
- `pages/`: Individual dashboard modules (Analyzer, Portfolio, ETF).
- `mfa.py`: Core logic for mutual fund analysis and scoring.
- `calculators/`: Modular math engines for static and rolling metrics.
- `constants/`: Configuration, portfolio data, and system constants.
- `decision_engine/`: Logic for relative scoring, confidence, and risk profiling.
- `etf/`: Specialized logic for ETF tracking and performance.
- `fetchers/`: Data retrieval from AMFI, benchmarks, and other sources.
- `ui/`: Reusable UI components and specialized dashboard tabs.
- `utils/`: Common utilities for dataframes, returns, and fetching.
- `assets/`: Screenshots and static assets.
- `log/`: System logging configuration.

## 📊 Requirements
- Python 3.10+
- Streamlit, Pandas, Plotly, MFTool

---
*Built for objective financial decision-making.*
