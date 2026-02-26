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
- **Static Treynor Ratio**: Calculates Treynor Ratio (Excess Return / Beta) for 1, 3, and 5 years
- **Static Calmar Ratio**: Calculates Calmar Ratio (Annualized Return / Max Drawdown) for 3 and 5 years
- **Static Ulcer Index**: Calculates Ulcer Index (Measure of downside risk) for 1, 3, and 5 years

## Project Structure

The project is modularized into the following components:

- **`mutual_fund_analyzer.py`**: The main entry point script that coordinates data fetching and analysis.
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
- **`static_treynor_ratio_calculator.py`**: Calculates static Treynor Ratio.
- **`static_calmar_ratio_calculator.py`**: Calculates static Calmar Ratio.
- **`static_ulcer_index_calculator.py`**: Calculates static Ulcer Index.
- **`utils.py`**: Contains utility functions for financial calculations (e.g., CAGR, daily returns).
- **`constants.py`**: Defines configuration constants (e.g., trading days, risk-free rate, date formats).

## Technical Implementation Details

- **Type Safety**: The codebase is fully type-hinted using Python's `typing` module for better code quality and developer experience.
- **Vectorized Calculations**: Uses `pandas` and `numpy` for efficient, vectorized financial calculations instead of slow loops.
- **Robustness**: Includes comprehensive error handling for:
  - Missing or insufficient data points
  - Zero or invalid NAV values
  - Infinite returns or division-by-zero scenarios
- **Standardization**: Centralized logic for daily returns and data processing in `utils.py` ensures consistency across all metrics.

## Requirements

- Python 3.10 or higher (Python 3.14.2 recommended)
- **Note:** This script uses Homebrew Python 3.14.2 (`/opt/homebrew/bin/python3`), not the system Python 3.9.6
- Required packages (see `requirements.txt`)

## Setup

**Important:** Ensure you're using Homebrew Python 3.14.2, not system Python 3.9.6:
```bash
which python3  # Should show /opt/homebrew/bin/python3
python3 --version  # Should show Python 3.14.2
```

If `python3` points to system Python 3.9.6, use the full path:
```bash
/opt/homebrew/bin/python3 mutual_fund_analyzer.py <scheme_codes>
```

Install dependencies using one of the following methods:

### Option 1: System-wide installation (requires --break-system-packages flag)
```bash
/opt/homebrew/bin/python3 -m pip install --break-system-packages -r requirements.txt
```

### Option 2: User installation (recommended)
```bash
/opt/homebrew/bin/python3 -m pip install --user -r requirements.txt
```

### Option 3: Verify installation
```bash
/opt/homebrew/bin/python3 -c "from mftool import Mftool; print('Installation successful!')"
```

## Usage

Run the script directly (using Homebrew Python 3.14.2):
```bash
python3 mutual_fund_analyzer.py <scheme_codes>
```

Or make it executable and run directly:
```bash
chmod +x mutual_fund_analyzer.py
./mutual_fund_analyzer.py <scheme_codes>
```

**Note:** If `python3` points to system Python 3.9.6, use the full path:
```bash
/opt/homebrew/bin/python3 mutual_fund_analyzer.py <scheme_codes>
```

### Syntax

```bash
python3 mutual_fund_analyzer.py <scheme_codes>
```

**Parameters:**
- `scheme_codes`: Comma-separated list of mutual fund scheme codes

**Example:**
```bash
python3 mutual_fund_analyzer.py 101206,101207
```

### Output

The script prints a detailed analysis for each scheme code provided:

```text
Axis Large Cap Fund - Regular Plan - Growth
============================================================

Rolling Returns (Min / Average / Max CAGR):
------------------------------------------------------------
1 Year(s): -23.51% / 13.34% / 63.12%
3 Year(s): 1.21% / 13.66% / 30.59%
5 Year(s): 3.45% / 13.99% / 21.05%

Calendar Year Returns:
------------------------------------------------------------
2025: 6.23%
2024: 14.29%
2023: 17.04%
2022: -6.89%
2021: 22.36%

Static Standard Deviation (Annualized Volatility %):
------------------------------------------------------------
1 Year(s): 10.88%
3 Year(s): 11.18%
5 Year(s): 13.17%

Static Downside Deviation (Annualized Downside Volatility %):
------------------------------------------------------------
1 Year(s): 7.22%
3 Year(s): 7.73%
5 Year(s): 9.29%

Rolling Standard Deviation (Volatility %):
------------------------------------------------------------
Window     Data       Median     Mean       Min        Max        Latest    
--------------------------------------------------------------------------------
1          5          12.69      12.88      8.74       17.44      10.92     
3          10         14.46      15.22      11.1       19.72      11.17     

Sharpe Ratio:
------------------------------------------------------------
1 Year(s): 0.2
3 Year(s): 0.57
5 Year(s): 0.35

Rolling Sharpe Ratio:
------------------------------------------------------------
Window     Data       Median     Mean       10%ile     Latest     % > 0   
--------------------------------------------------------------------------------
1          5          0.06       0.31       -0.71      0.14       53.41   
3          10         0.49       0.5        0.21       0.49       99.71   

Sortino Ratio:
------------------------------------------------------------
1 Year(s): 0.3
3 Year(s): 0.83
5 Year(s): 0.5

Rolling Sortino Ratio:
------------------------------------------------------------
Window     Data       Median     Mean       10%ile     Latest     % > 0   
--------------------------------------------------------------------------------
1          5          0.09       0.47       -0.94      0.22       53.41   
3          10         0.69       0.71       0.28       0.71       99.71   

Max Drawdown & Recovery Time:
------------------------------------------------------------
Period          Max Drawdown         Recovery Time (Days)
------------------------------------------------------------
1 Year(s)       -7.08%               82                  
3 Year(s)       -15.82%              489                 
5 Year(s)       -22.22%              782                 
============================================================
```

### Metrics Explained

1. **Rolling Returns**: Compound Annual Growth Rate (CAGR) over moving windows (1, 3, 5 years).
2. **Calendar Year Returns**: Absolute returns for specific calendar years (Jan 1st to Jan 1st).
3. **Static Standard Deviation**: Annualized volatility calculated from daily returns over fixed periods.
4. **Static Downside Deviation**: Annualized downside volatility (considering only negative returns) calculated from daily returns over fixed periods.
5. **Rolling Standard Deviation**: Distribution of annualized volatility over moving windows.
6. **Static Sharpe Ratio**: Risk-adjusted return metric ((Return - Risk Free Rate) / Volatility).
7. **Rolling Sharpe Ratio**: Distribution of Sharpe Ratio over moving windows.
8. **Static Sortino Ratio**: Risk-adjusted return metric ((Return - Risk Free Rate) / Downside Deviation). Penalizes only negative volatility.
9. **Rolling Sortino Ratio**: Distribution of Sortino Ratio over moving windows.
10. **Max Drawdown**: The maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained. Also includes Recovery Time (days to reach a new high).
11. **Static Alpha**: Jensen's Alpha measures the excess return of the fund over its expected return (predicted by CAPM). A positive alpha indicates the fund has outperformed its benchmark after adjusting for risk.
12. **Static Beta**: A measure of the volatility (or systematic risk) of the fund in comparison to the market/benchmark. Beta = 1 indicates volatility matches the market.
13. **Static Information Ratio**: A measure of the risk-adjusted return of the fund relative to a benchmark. Calculated as (Active Return / Tracking Error). Higher is better.
14. **Static Treynor Ratio**: A risk-adjusted performance measure that uses Beta as the risk measure. Calculated as (Fund Return - Risk Free Rate) / Beta.
15. **Static Calmar Ratio**: A comparison of the annualized return to the maximum drawdown. Calculated as (Annualized Return / Max Drawdown). Higher is better.
16. **Static Ulcer Index**: A measure of the depth and duration of drawdowns. Higher value indicates greater risk of loss. Unlike standard deviation, it only penalizes downside risk.
17. **Rolling Alpha**: Distribution of Jensen's Alpha over moving windows.
18. **Rolling Beta**: Distribution of Beta over moving windows.
19. **Rolling Information Ratio**: Distribution of Information Ratio over moving windows.
20. **Static Hit Ratio**: The percentage of days the fund's return was higher than the benchmark's return over fixed periods.
21. **Rolling Hit Ratio**: Distribution of the Hit Ratio over moving windows.
