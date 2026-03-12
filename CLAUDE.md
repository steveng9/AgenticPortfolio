# Claude guidance for AgenticPortfolio

## What this project is

A personal investment tracker + finance learning tool. It reads buy/sell history
from Google Sheets, calculates portfolio performance with yfinance price data,
and renders charts.

The user wants:
- Accurate portfolio math and clean, maintainable Python
- Educational finance discussion and analysis
- **Not** investment decisions or authoritative advice — frame everything as learning

---

## Code conventions

- **Python 3.11+**. Use modern type hints (`str | None`, `list[dict]`, etc.)
- Keep modules focused on their single concern — see architecture below
- No over-engineering: no CLI frameworks, no database, no Docker, no async
- `portfolio.py` must remain pure computation: no I/O, no gspread, no matplotlib
- `prices.py` is the only place that calls `yfinance`
- `sheets.py` is the only place that calls `gspread`
- yfinance: always pass `auto_adjust=True, progress=False`; use `"Close"` column
- Dollar-weighted (not time-weighted) return calculation throughout

## Module map

```
config.py     — constants only (sheet names, paths)
auth.py       — gspread.service_account() wrapper
sheets.py     — all Sheets I/O
prices.py     — yfinance helpers: download_prices, get_available_date, get_price_change
portfolio.py  — math: get_current_value, get_performance, build_performance_dataframes
charts.py     — matplotlib/seaborn: plot_portfolio_performance, plot_ticker_allocation, plot_ticker_performance
main.py       — orchestrator (--charts-only, --no-charts flags)
```

Future additions go in new files (e.g. `analysis.py`) that import from `portfolio.py`.
Don't add financial analysis logic to existing modules.

## Key data contracts

**history_df** (from `sheets.read_history`):
- Columns: `date` (Python date objects), `ticker` (str), `amount` (float)
- Positive amount = buy, negative = sell
- One row per transaction; duplicate ticker+date raises AssertionError

**prices DataFrame** (from `prices.download_prices`):
- Index: date strings `"YYYY-MM-DD"`
- Column: `"Close"` (single ticker, auto-adjusted)

**Holdings list** (output of `portfolio.get_current_value`):
- `{"ticker": str, "invested": float, "current_value": float, "earnings": float}`
- Returns `None` if yfinance has no data for the ticker

**invested_df / value_df** (from `portfolio.build_performance_dataframes`):
- Index: integer 0..N
- Columns: `"date"` (str), one column per ticker, `"total"` (sum)

## Finance discussion norms

When discussing portfolio performance or finance concepts:
- Frame as educational / analytical, not prescriptive
- Acceptable: explaining what a metric means, showing how to calculate it, discussing tradeoffs
- Avoid: "you should buy/sell X", "this is a good/bad investment"
- Good topics to introduce unprompted when relevant:
  - Sharpe / Sortino ratio
  - Max drawdown
  - Benchmark comparison (SPY, IVV)
  - Dollar-cost averaging
  - Cost basis methods (average cost vs FIFO)
  - Portfolio concentration / diversification
  - Sector/asset-class exposure

## Credentials & secrets

- `credentials/service_account.json` is gitignored — never commit it
- Never log or print the contents of the credentials file
- The service account email (in the JSON) must have Editor access on the spreadsheet

## Running the tool

```bash
python main.py               # full run
python main.py --charts-only # read + chart, no Sheets writes
python main.py --no-charts   # update Sheets, no chart popup
```

## When making changes

1. Read the relevant module(s) before editing
2. Keep `portfolio.py` pure — if you need I/O, it belongs in `sheets.py` or `main.py`
3. New chart types go in `charts.py` and get called from `main.py`
4. New analysis metrics go in a new `analysis.py`, imported in `main.py`
5. Don't add error handling for scenarios that can't happen; trust the data contract
