# Mutual Fund Returns Script

This script calculates mutual fund returns using the `mftool` library.

**Requires Python 3.10+ (tested with Python 3.14.2)**

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
/opt/homebrew/bin/python3 mfReturns.py <function> [arguments]
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
python3 mfReturns.py <function> [arguments]
```

Or make it executable and run directly:
```bash
chmod +x mfReturns.py
./mfReturns.py <function> [arguments]
```

**Note:** If `python3` points to system Python 3.9.6, use the full path:
```bash
/opt/homebrew/bin/python3 mfReturns.py <function> [arguments]
```

The script supports three functions:

### 1. Rolling Returns (`rolling-returns`)
Calculates rolling returns for specified years. Returns min / average / max CAGR (Compound Annual Growth Rate).

**Syntax:**
```bash
python3 mfReturns.py rolling-returns <scheme_codes> <years>
```

**Parameters:**
- `scheme_codes`: Comma-separated list of mutual fund scheme codes
- `years`: Comma-separated list of years (e.g., 1,3,5)

**Example:**
```bash
python3 mfReturns.py rolling-returns 101206,101207 1,3,5
```

**Output:** For each scheme and year, displays min / average / max CAGR (Compound Annual Growth Rate).

---

### 2. Point-to-Point Returns (`point-to-point`)
Calculates returns between two specific dates.

**Syntax:**
```bash
python3 mfReturns.py point-to-point <scheme_code> <initial_date> <final_date>
```

**Parameters:**
- `scheme_code`: Single mutual fund scheme code
- `initial_date`: Start date in DD-MM-YYYY format
- `final_date`: End date in DD-MM-YYYY format

**Example:**
```bash
python3 mfReturns.py point-to-point 101206 01-01-2020 31-12-2023
```

**Output:** Displays the percentage return between the two dates.

---

### 3. Calendar Year Returns (`calendar-year`)
Calculates returns for specific calendar years.

**Syntax:**
```bash
python3 mfReturns.py calendar-year <scheme_codes> <years>
```

**Parameters:**
- `scheme_codes`: Comma-separated list of mutual fund scheme codes
- `years`: Comma-separated list of calendar years (e.g., 2020,2021,2022)

**Example:**
```bash
python3 mfReturns.py calendar-year 101206,101207 2020,2021,2022
```

**Output:** Displays returns for each year separated by " / ".

---

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

### Date Format
For `point-to-point` function, dates must be in `DD-MM-YYYY` format (e.g., `01-01-2020`).

