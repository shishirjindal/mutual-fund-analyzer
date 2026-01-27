# Mutual Fund Analyzer

This script analyzes mutual fund schemes and calculates various parameters including returns and risk measures using the `mftool` library. It provides rolling returns, calendar year returns, and Sharpe Ratio analysis for evaluating mutual fund performance.

**Requires Python 3.10+ (tested with Python 3.14.2)**

## Features

- **Rolling Returns**: Calculates CAGR (Compound Annual Growth Rate) for 1, 3, and 5 years with min/average/max statistics
- **Calendar Year Returns**: Calculates returns for the last 5 calendar years
- **Sharpe Ratio**: Calculates annualized Sharpe Ratio for 1, 3, and 5 years using daily returns
- **Rolling Sharpe Ratio**: Calculates rolling Sharpe Ratio metrics (Median, Mean, 10th Percentile, % Positive, Latest) for configured windows

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
/opt/homebrew/bin/python3 mfReturns.py <scheme_codes>
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
python3 mfReturns.py <scheme_codes>
```

Or make it executable and run directly:
```bash
chmod +x mfReturns.py
./mfReturns.py <scheme_codes>
```

**Note:** If `python3` points to system Python 3.9.6, use the full path:
```bash
/opt/homebrew/bin/python3 mfReturns.py <scheme_codes>
```

### Syntax

```bash
python3 mfReturns.py <scheme_codes>
```

**Parameters:**
- `scheme_codes`: Comma-separated list of mutual fund scheme codes

**Example:**
```bash
python3 mfReturns.py 101206,101207
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
   - Metrics calculated over rolling windows:
     - **Median**: Median Sharpe Ratio (Primary quality metric)
     - **Mean**: Average Sharpe Ratio
     - **10th Percentile**: Downside risk indicator
     - **Latest**: Most recent rolling Sharpe Ratio
     - **% > 0**: Percentage of time the Sharpe Ratio was positive (Consistency metric)

**Example Output:**
```
Scheme Name
============================================================

Rolling Returns (Min / Average / Max CAGR):
------------------------------------------------------------
1 Year(s): 8.50% / 12.30% / 15.75%
3 Year(s): 10.20% / 13.45% / 16.80%
5 Year(s): 11.00% / 14.20% / 17.50%

Calendar Year Returns:
------------------------------------------------------------
2025: 12.50%
2024: 15.30%
2023: 10.20%
2022: -5.40%
2021: 18.75%

Sharpe Ratio:
------------------------------------------------------------
1 Year(s): 1.25
3 Year(s): 1.30
5 Year(s): 1.28

Rolling Sharpe Ratio:
--------------------------------------------------------------------------------
Window     Data       Median     Mean       10%ile     Latest     % > 0   
--------------------------------------------------------------------------------
1          5          0.85       0.82       0.45       0.90       85.5    
3          10         1.10       1.05       0.65       1.15       92.0    
============================================================
```

## Interpretation

### Static Sharpe Ratio
| Static Sharpe | Interpretation | What it actually means |
|---------------|----------------|------------------------|
| > 1.5 | Exceptional | Rare skill or strong market tailwind |
| 1.0 - 1.5 | Very good | Strong risk-adjusted performance |
| 0.7 - 1.0 | Good | Acceptable efficiency |
| 0.4 - 0.7 | Weak | Marginal value add |
| 0 - 0.4 | Poor | Barely beats risk-free |
| < 0 | Bad | Value destruction |

### Rolling Sharpe Ratio

#### 1. Median Rolling Sharpe (Primary quality metric)
| Value | Interpretation | Meaning |
|-------|----------------|---------|
| > 1.0 | Excellent | Strong, repeatable risk-adjusted performance |
| 0.7 - 1.0 | Very Good | Consistent value creation |
| 0.4 - 0.7 | Acceptable | Moderate fund quality |
| 0.2 - 0.4 | Weak | Marginal risk-adjusted returns |
| 0 - 0.2 | Poor | Barely beats risk-free |
| < 0 | Bad | Risk-adjusted value destruction |

#### 2. Percentage of Time Rolling Sharpe > 0 (Consistency)
| Value | Interpretation | Meaning |
|-------|----------------|---------|
| > 75% | Excellent | Adds value most of the time |
| 65 - 75% | Good | Reliable performance |
| 55 - 65% | Borderline | Inconsistent |
| 45 - 55% | Weak | Random-like behavior |
| < 45% | Poor | Unreliable fund |

#### 3. 10th Percentile Rolling Sharpe (Downside behavior)
| Value | Interpretation | Meaning |
|-------|----------------|---------|
| > 0 | Excellent | No destructive regimes |
| 0 to -0.3 | Acceptable | Mild stress periods |
| -0.3 to -0.6 | Weak | Painful drawdowns |
| < -0.6 | Poor | Severe downside risk |

#### 4. Latest Rolling Sharpe (Current regime indicator)
| Value | Interpretation | Action |
|-------|----------------|--------|
| > 0.7 | Strong | Add / Hold |
| 0.3 - 0.7 | Stable | Hold |
| 0 - 0.3 | Weak | Monitor |
| < 0 | Negative | Avoid fresh investment / Review |

## Architecture

The script uses a class-based architecture:

- **`MutualFundAnalyzer`**: Main class that analyzes mutual funds and calculates various parameters
  - Fetches scheme data during initialization
  - Calculates rolling returns for 1, 3, and 5 years
  - Calculates calendar year returns for the last 5 years
  - Calculates Sharpe Ratio for 1, 3, and 5 years using daily returns
  - Calculates Rolling Sharpe Ratio metrics for configured windows
  - Prints formatted results

- **`constants.py`**: Contains all configuration constants:
  - Trading days per year (252)
  - Risk-free rate (6.5%)
  - Rolling years (1, 3, 5)
  - Sharpe Ratio years (1, 3, 5)
  - Rolling Sharpe Ratio configuration (window sizes and data periods)
  - Calendar years to calculate (5)
  - Date patterns for NAV lookup

## Configuration

You can modify constants in `constants.py`:

- `TRADING_DAYS_PER_YEAR`: Number of trading days per year (default: 252)
- `RISK_FREE_RATE`: Risk-free rate in percentage for Sharpe Ratio (default: 6.5)
- `ROLLING_YEARS`: Years for rolling returns calculation (default: [1, 3, 5])
- `STATIC_SHARPE_RATIO_YEARS`: Years for Static Sharpe Ratio calculation (default: [1, 3, 5])
- `ROLLING_SHARPE_RATIO_MAP`: Configuration for Rolling Sharpe Ratio (default: 1yr window/5yr data, 3yr window/10yr data)
- `NUM_CALENDAR_YEARS`: Number of calendar years to calculate (default: 5)
- `JANUARY_DATE_DAYS`: Days to check for NAV at start of year (default: [1, 2, 3, 4])
- `DECIMAL_PLACES`: Decimal places for rounding (default: 2)

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
python3 -m pip install --user --upgrade -r requirements.txt
```

### Python Version Issues
This script requires Python 3.10 or higher. Check your Python version:
```bash
python3 --version
```

### No Data Found
If you see "Error: No data found for scheme code", verify:
- The scheme code is correct
- The scheme has historical NAV data available
- Your internet connection is working (mftool fetches data from online sources)

### Insufficient Data
If you see "Insufficient data" errors:
- **Rolling Returns**: The scheme may not have enough historical data
  - For 5-year rolling returns, you need at least 1,261 data points (5 * 252 + 1)
- **Sharpe Ratio**: Requires sufficient daily NAV data
  - For 1-year Sharpe Ratio: at least 253 data points
  - For 3-year Sharpe Ratio: at least 757 data points
  - For 5-year Sharpe Ratio: at least 1,261 data points
- **Rolling Sharpe Ratio**: Requires additional data for rolling windows
  - Data points needed = (Total Years * 252) + 1

## File Structure

```
stockMarketScripts-main/
├── mfReturns.py          # Main script with MutualFundAnalyzer class
├── constants.py          # Configuration constants
├── requirements.txt      # Python dependencies
└── README.md            # This file
```
