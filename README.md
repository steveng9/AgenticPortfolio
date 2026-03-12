# AgenticPortfolio

A local Python tool that reads your investment transaction history from Google Sheets,
calculates portfolio performance, writes results back to Sheets, and renders charts.

---

## What it does

- Reads your buy/sell history from a Google Sheet
- Calculates per-ticker and total: **amount invested**, **current value**, **realised earnings**
- Builds a daily time series from inception to today
- Writes results back into your spreadsheet (Holdings, Performance, Invested, Values sheets)
- Renders three charts:
  - Total invested vs. portfolio value over time (with gain/loss shading)
  - Current allocation pie chart
  - Per-ticker performance grid

---

## One-time setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google Sheets access (service account)

You need a service account so the script can read/write your spreadsheet without a browser.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project (or use an existing one)
2. Enable two APIs:
   - **Google Sheets API**
   - **Google Drive API**
3. Go to **IAM & Admin → Service Accounts → Create Service Account**
4. Give it any name (e.g. `portfolio-tracker`), click through, then open the account
5. Go to **Keys → Add Key → Create new key → JSON** — download the file
6. Save it as `credentials/service_account.json` in this folder
7. Open your **"Financial Portfolio"** Google Sheet → Share → paste the service account's email address (found in the JSON file under `"client_email"`) with **Editor** access

### 3. Verify your spreadsheet structure

Your spreadsheet should have these sheets (names must match exactly):

| Sheet name  | Purpose                                      |
|-------------|----------------------------------------------|
| `Historic`  | Your transaction log — **you maintain this** |
| `Holdings`  | Per-ticker summary — written by this tool    |
| `Performance` | Total invested vs value over time          |
| `Invested`  | Daily invested time series per ticker        |
| `Values`    | Daily value time series per ticker           |

**Historic sheet format** (the only sheet you need to fill in manually):

| date       | ticker | amount     |
|------------|--------|------------|
| 2022-01-15 | IVV    | 500.00     |
| 2022-03-10 | GOOGL  | $1,200.00  |
| 2023-06-01 | IVV    | -300.00    |

- `amount` is in USD. Positive = buy, negative = sell.
- Dollar signs and commas in amounts are handled automatically.
- One row per transaction. Multiple transactions on the same day for the same ticker are not supported.

---

## Running

```bash
# Full run: update Sheets + display charts
python main.py

# Only show charts, don't write to Sheets
python main.py --charts-only

# Update Sheets, skip charts
python main.py --no-charts
```

A summary table is always printed to the terminal:

```
── Portfolio Summary ─────────────────────────────────
  Total invested:     $10,000.00
  Portfolio value:    $12,450.00
  Realised gains:       $320.00
  Unrealised gain:    $2,450.00  (+24.50%)

  Ticker   Invested        Value       Gain        %
  -------- ------------ ------------ ---------- --------
  IVV       $5,000.00    $6,300.00    $1,300.00  +26.00%
  GOOGL     $3,000.00    $3,800.00      $800.00  +26.67%
  ...
```

---

## File structure

```
AgenticPortfolio/
├── main.py           # Entry point
├── config.py         # Spreadsheet/sheet names, credentials path
├── auth.py           # Google Sheets authentication
├── sheets.py         # All Sheets read/write
├── prices.py         # yfinance price data helpers
├── portfolio.py      # Core calculation logic (pure, no I/O)
├── charts.py         # Matplotlib/seaborn visualisations
├── requirements.txt
├── credentials/      # Gitignored — put your service_account.json here
└── .gitignore
```

---

## Troubleshooting

**`gspread.exceptions.SpreadsheetNotFound`**
→ The service account hasn't been given access. Share the spreadsheet with the `client_email` from your JSON key.

**`KeyError: 'Close'`**
→ yfinance returned an unexpected shape — usually a network issue. Try running again.

**`ValueError: Could not find a trading day near ...`**
→ A transaction date is very recent and prices haven't loaded yet, or the ticker has no data.

**Multiple trades on the same day for one ticker**
→ The tool raises an assertion error. Combine same-day trades into a single row in the Historic sheet.
