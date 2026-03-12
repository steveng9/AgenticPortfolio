---
name: update
description: Run the portfolio tracker to update Google Sheets and display performance charts. Use when the user wants to refresh their portfolio, sync to Sheets, or see latest charts.
disable-model-invocation: true
allowed-tools: Bash
---

Run the portfolio update tool and report back on what happened.

## Steps

1. Run the tool:
!`python main.py --no-charts 2>&1`

2. Parse the output above and:
   - Confirm whether the run succeeded or failed
   - If it failed, diagnose the error and suggest a fix (check credentials, network, yfinance rate limit, date issues, etc.)
   - If it succeeded, display the Portfolio Summary table cleanly
   - Note any tickers that were skipped due to missing price data

3. Offer to show charts by running `python main.py --charts-only` if the user wants them.
