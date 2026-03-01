# Mutual Fund Analyzer

This project analyzes mutual fund schemes and calculates various parameters including returns and risk measures using the `mftool` library. It provides rolling returns, calendar year returns, and Sharpe Ratio analysis for evaluating mutual fund performance.

**Requires Python 3.10+ (tested with Python 3.14.2)**

## Features

- **Rolling Returns**: Calculates CAGR (Compound Annual Growth Rate) for 1, 3, and 5 years with min/average/max statistics
- **Calendar Year Returns**: Calculates returns for the last 5 calendar years
- **Static Standard Deviation**: Calculates annualized Standard Deviation (Volatility) for 1, 3, and 5 years
- **Static Downside Deviation**: Calculates annualized Downside Deviation (Downside Volatility) for 1, 3, and 5 years
- **Rolling Standard Deviation**: Calculates rolling Standard Deviation metrics (Median, Mean, Min, Max, Latest) for configured windows
- **Static Sharpe Ratio**: Calculates annualized Sharpe Ratio for 1, 3, and 5 years using daily returns
- **Rolling Sharpe Ratio**: Calculates rolling Sharpe Ratio metrics (Median, Mean, 10th Percentile, % Positive, Latest) for configured windows
- **Static Sortino Ratio**: Calculates annualized Sortino Ratio for 1, 3, and 5 years using daily returns and downside deviation
- **Rolling Sortino Ratio**: Calculates rolling Sortino Ratio metrics (Median, Mean, 10th Percentile, % Positive, Latest) for configured windows
- **Max Drawdown**: Calculates maximum loss from a peak to a trough and the recovery time (duration) for 1, 3, and 5 years
- **Static Alpha**: Calculates Jensen's Alpha (Excess Return over CAPM Expected Return) for 1, 3, and 5 years
- **Static Beta**: Calculates Beta (Volatility relative to benchmark) for 1, 3, and 5 years
- **Static Information Ratio**: Calculates Information Ratio (Active Return / Tracking Error) for 1, 3, and 5 years
- **Rolling Alpha**: Calculates rolling Jensen's Alpha metrics for configured windows
- **Rolling Beta**: Calculates rolling Beta metrics for configured windows
- **Rolling Information Ratio**: Calculates rolling Information Ratio metrics for configured windows
- **Static Hit Ratio**: Calculates Hit Ratio (Percentage of outperformance days) for 1, 3, and 5 years
- **Rolling Hit Ratio**: Calculates rolling Hit Ratio metrics for configured windows
- **Rolling Max Drawdown**: Calculates rolling maximum drawdown metrics for configured windows
- **Static Treynor Ratio**: Calculates Treynor Ratio (Excess Return / Beta) for 1, 3, and 5 years
- **Static Calmar Ratio**: Calculates Calmar Ratio (Annualized Return / Max Drawdown) for 3 and 5 years
- **Static Ulcer Index**: Calculates Ulcer Index (Measure of downside risk) for 1, 3, and 5 years
- **Interactive Web UI**: Streamlit-based interface for visual analysis and charts

## Project Structure

The project is modularized into the following components:

- **`mfa.py`**: The main entry point script that coordinates data fetching and analysis.
- **`app.py`**: Streamlit-based web interface for interactive visualization.
- **`data_fetcher.py`**: Handles fetching historical NAV data using `mftool`.
- **`rolling_returns_calculator.py`**: Calculates rolling CAGR returns.
- **`calendar_year_returns_calculator.py`**: Calculates calendar year returns.
- **`static_standard_deviation_calculator.py`**: Calculates static annualized Standard Deviation (Volatility).
- **`static_downside_deviation_calculator.py`**: Calculates static annualized Downside Deviation.
- **`rolling_standard_deviation_calculator.py`**: Calculates rolling Standard Deviation (Volatility).
- **`static_sharpe_ratio_calculator.py`**: Calculates static annualized Sharpe Ratios.
- **`rolling_sharpe_ratio_calculator.py`**: Calculates rolling Sharpe Ratios.
- **`static_sortino_ratio_calculator.py`**: Calculates static annualized Sortino Ratios.
- **`rolling_sortino_ratio_calculator.py`**: Calculates rolling Sortino Ratios.
- **`static_drawdown_calculator.py`**: Calculates maximum drawdown and recovery duration.
- **`static_alpha_calculator.py`**: Calculates Jensen's Alpha.
- **`static_beta_calculator.py`**: Calculates Beta.
- **`static_information_ratio_calculator.py`**: Calculates static Information Ratio.
- **`rolling_alpha_calculator.py`**: Calculates rolling Jensen's Alpha.
- **`rolling_beta_calculator.py`**: Calculates rolling Beta.
- **`rolling_information_ratio_calculator.py`**: Calculates rolling Information Ratio.
- **`static_hit_ratio_calculator.py`**: Calculates static Hit Ratio.
- **`rolling_hit_ratio_calculator.py`**: Calculates rolling Hit Ratio.
- **`rolling_drawdown_calculator.py`**: Calculates rolling Maximum Drawdown.
- **`static_treynor_ratio_calculator.py`**: Calculates static Treynor Ratio.
- **`static_calmar_ratio_calculator.py`**: Calculates static Calmar Ratio.
- **`static_ulcer_index_calculator.py`**: Calculates static Ulcer Index.
- **`utils.py`**: Contains utility functions for financial calculations (e.g., CAGR, daily returns).
- **`constants.py`**: Defines configuration constants (e.g., trading days, risk-free rate, date formats).

## Requirements

- Python 3.10 or higher
- Required packages: `streamlit`, `plotly`, `pandas`, `mftool`, `numpy`, `httpx`, `beautifulsoup4`, `yfinance`, `matplotlib`

## Usage

### Command Line Interface (CLI)

1. **Calculate returns for a single scheme code:**
   ```bash
   python3 mfa.py 112277
   ```

2. **Calculate returns for multiple scheme codes (comma-separated):**
   ```bash
   python3 mfa.py 112277,120465
   ```

### Streamlit Web UI

You can also use the web-based UI for interactive analysis and visualizations:

1. **Install dependencies:**
   ```bash
   pip3 install streamlit plotly pandas mftool --break-system-packages
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

3. **Open the app in your browser:**
   The URL (typically `http://localhost:8501`) will be displayed in the terminal.

## Metric Explanations

1. **Rolling Returns**: CAGR over moving windows (1, 3, 5 years). Provides a more comprehensive view than point-to-point returns.
2. **Calendar Year Returns**: Absolute returns for specific calendar years.
3. **Static Standard Deviation**: Annualized volatility calculated over fixed periods.
4. **Static Downside Deviation**: Annualized downside volatility (considering only negative returns).
5. **Rolling Standard Deviation**: Distribution of volatility over moving windows.
6. **Static Sharpe Ratio**: Risk-adjusted return metric ((Return - Risk Free Rate) / Volatility).
7. **Rolling Sharpe Ratio**: Distribution of Sharpe Ratio over moving windows.
8. **Static Sortino Ratio**: Risk-adjusted return metric ((Return - Risk Free Rate) / Downside Deviation).
9. **Rolling Sortino Ratio**: Distribution of Sortino Ratio over moving windows.
10. **Max Drawdown**: Maximum loss from peak to trough and recovery time.
11. **Static Alpha**: Jensen's Alpha measures excess return over CAPM expected return.
12. **Static Beta**: Volatility relative to the benchmark.
13. **Static Information Ratio**: Risk-adjusted return relative to benchmark.
14. **Static Treynor Ratio**: Risk-adjusted performance using Beta as the risk measure.
15. **Static Calmar Ratio**: Annualized return divided by maximum drawdown.
16. **Static Ulcer Index**: Measure of downside risk considering depth and duration of drawdowns.
17. **Rolling Alpha**: Distribution of Alpha over moving windows.
18. **Rolling Beta**: Distribution of Beta over moving windows.
19. **Rolling Information Ratio**: Distribution of Information Ratio over moving windows.
20. **Static Hit Ratio**: Percentage of days the fund outperformed the benchmark.
21. **Rolling Hit Ratio**: Distribution of Hit Ratio over moving windows.
22. **Rolling Max Drawdown**: Distribution of Maximum Drawdown over moving windows.
