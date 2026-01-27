# Mutual Fund Analyzer

This project analyzes mutual fund schemes and calculates various parameters including returns and risk measures using the `mftool` library. It provides rolling returns, calendar year returns, and Sharpe Ratio analysis for evaluating mutual fund performance.

**Requires Python 3.10+ (tested with Python 3.14.2)**

## Features

- **Rolling Returns**: Calculates CAGR (Compound Annual Growth Rate) for 1, 3, and 5 years with min/average/max statistics
- **Calendar Year Returns**: Calculates returns for the last 5 calendar years
- **Sharpe Ratio**: Calculates annualized Sharpe Ratio for 1, 3, and 5 years using daily returns
- **Rolling Sharpe Ratio**: Calculates rolling Sharpe Ratio metrics (Median, Mean, 10th Percentile, % Positive, Latest) for configured windows

## Project Structure

The project is modularized into the following components:

- **`mutual_fund_analyzer.py`**: The main entry point script that coordinates data fetching and analysis.
- **`data_fetcher.py`**: Handles fetching historical NAV data using `mftool`.
- **`rolling_returns_calculator.py`**: Calculates rolling CAGR returns.
- **`calendar_year_returns_calculator.py`**: Calculates calendar year returns.
- **`static_sharpe_ratio_calculator.py`**: Calculates static annualized Sharpe Ratios.
- **`rolling_sharpe_ratio_calculator.py`**: Calculates rolling Sharpe Ratios.
- **`utils.py`**: Contains utility functions for financial calculations (e.g., CAGR, daily returns).
- **`constants.py`**: Defines configuration constants (e.g., trading days, risk-free rate, date formats).

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

For each scheme code, the script displays:

1. **Rolling Returns (Min / Average / Max CAGR)**:
   - 1 Year(s): min% / avg% / max%
   - 3 Year(s): min% / avg% / max%
   - 5 Year(s): min% / avg% / max%

2. **Calendar Year Returns**:
   - Returns for the last 5 calendar years (e.g., 2025, 2024, 2023, 2022, 2021)
   - Shows percentage return for each year or "N/A" if data is unavailable

3. **Sharpe Ratio**:
   - Annualized Sharpe Ratio for 1, 3, and 5 years
   - Calculated using daily returns and annualized
   - Formula: (Annualized Return - Risk-free Rate) / Annualized Volatility

4. **Rolling Sharpe Ratio**:
   - Rolling metrics for different windows (e.g., 1-year rolling window over 5 years data)
   - Metrics: Median, Mean, 10th Percentile, Latest value, % of positive periods
