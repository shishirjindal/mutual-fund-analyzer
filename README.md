# Mutual Fund Analyzer

A Streamlit-based tool for deep quantitative analysis of Indian mutual funds. Fetches live NAV data from AMFI, computes 20+ risk/return metrics, and scores funds using a Z-Score + Sigmoid pipeline — enabling objective, peer-relative comparison.

---

## Overview

The analyzer supports two modes:

- **By Scheme Code** — analyze one or more funds by their AMFI scheme codes
- **By Category** — fetch all Direct Growth funds in a category from AMFI and rank them

Each fund is evaluated across five dimensions:

| Dimension | Metrics |
|---|---|
| Return Performance | Rolling CAGR (1Y/3Y/5Y), Calendar Year Returns, Worst Year |
| Risk | Max Drawdown, Std Deviation, Downside Deviation, Ulcer Index |
| Risk-Adjusted | Sharpe, Sortino, Calmar, Treynor Ratios |
| Manager Skill | Alpha, Beta, Information Ratio, Hit Ratio |
| Consistency | Rolling Sharpe, Rolling Hit Ratio, Rolling Returns distribution |

Scores are computed relative to the peer group using Z-Score normalization followed by a Sigmoid transform, producing a final 0–100 score per fund.

---

## Requirements

Python 3.10 or higher (tested with Python 3.14.2).

### Setup

**1. Create and activate a virtual environment**

```bash
python3 -m venv mfenv
source mfenv/bin/activate        # macOS / Linux
mfenv\Scripts\activate           # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Deactivate when done**

```bash
deactivate
```

### Dependencies

```
mftool>=3.0
pandas>=2.0.0
numpy>=1.24.0
streamlit>=1.0.0
plotly>=5.0.0
scipy>=1.10.0
matplotlib>=3.7.0
```

---

## Usage

### Web UI (recommended)

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

**By Scheme Code:**
1. Select "By Scheme Code" in the sidebar
2. Enter one or more AMFI scheme codes, comma-separated (e.g. `101206,112277`)
3. Click "Analyze"

**By Category:**
1. Select "By Category" in the sidebar
2. Pick a fund category from the dropdown (fetched live from AMFI)
3. Click "Analyze Category"

Results show a ranked comparison table with per-category scores and a CSV download. Select any fund to drill into its detailed metric tabs.

---

### CLI

Analyze one or more funds from the terminal:

```bash
# Single fund
python3 main.py 112277

# Multiple funds
python3 main.py 112277,120465
```

---

## Screenshots

> Screenshots will be added once the UI is finalized. To preview, run `streamlit run app.py` and explore the five analysis tabs.

---

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
