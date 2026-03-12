"""
AgenticPortfolio — main entry point.

Usage:
    python main.py                    # full run: update Sheets + show charts
    python main.py --charts-only      # skip Sheets writes, just show charts
    python main.py --no-charts        # update Sheets, skip charts
"""

import argparse

import pandas as pd

from auth import get_client
from charts import plot_portfolio_performance, plot_ticker_allocation, plot_ticker_performance
from config import CREDENTIALS_PATH, SHEETS, SPREADSHEET_NAME
from portfolio import build_performance_dataframes, get_current_value
from sheets import (
    read_history,
    update_holdings,
    update_invested,
    update_performance,
    update_values,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Portfolio tracker")
    parser.add_argument("--charts-only", action="store_true", help="Skip Sheets writes")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart display")
    return parser.parse_args()


def main():
    args = parse_args()

    print("Connecting to Google Sheets…")
    client = get_client(CREDENTIALS_PATH)
    spreadsheet = client.open(SPREADSHEET_NAME)

    print("Reading transaction history…")
    history_df = read_history(spreadsheet.worksheet(SHEETS["history"]))
    all_tickers = history_df["ticker"].unique().tolist()
    inception = (history_df["date"].min() - pd.Timedelta(days=5)).strftime("%Y-%m-%d")
    print(f"  {len(all_tickers)} tickers, inception {inception}")

    print("\nCalculating current holdings…")
    holdings = [get_current_value(t, history_df, inception) for t in all_tickers]
    holdings = [h for h in holdings if h is not None]

    print("\nBuilding daily performance time series…")
    invested_df, value_df = build_performance_dataframes(all_tickers, history_df, inception)

    if not args.charts_only:
        print("\nWriting to Google Sheets…")
        update_holdings(spreadsheet.worksheet(SHEETS["holdings"]), holdings)
        update_performance(spreadsheet.worksheet(SHEETS["performance"]), invested_df, value_df)
        update_invested(spreadsheet.worksheet(SHEETS["invested"]), invested_df)
        update_values(spreadsheet.worksheet(SHEETS["values"]), value_df)
        print("  Done.")

    if not args.no_charts:
        print("\nRendering charts…")
        plot_portfolio_performance(invested_df, value_df)
        plot_ticker_allocation(holdings)
        plot_ticker_performance(invested_df, value_df)

    # Summary table
    print("\n── Portfolio Summary ─────────────────────────────────")
    total_invested = sum(h["invested"] for h in holdings)
    total_value = sum(h["current_value"] for h in holdings)
    total_earnings = sum(h["earnings"] for h in holdings)
    gain = total_value - total_invested
    gain_pct = (total_value / total_invested - 1) * 100 if total_invested else 0

    print(f"  Total invested:   ${total_invested:>12,.2f}")
    print(f"  Portfolio value:  ${total_value:>12,.2f}")
    print(f"  Realised gains:   ${total_earnings:>12,.2f}")
    print(f"  Unrealised gain:  ${gain:>12,.2f}  ({gain_pct:+.2f}%)")
    print()

    print(f"  {'Ticker':<8} {'Invested':>12} {'Value':>12} {'Gain':>10} {'%':>8}")
    print(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
    for h in sorted(holdings, key=lambda x: -x["current_value"]):
        g = h["current_value"] - h["invested"]
        pct = (h["current_value"] / h["invested"] - 1) * 100 if h["invested"] else 0
        print(f"  {h['ticker']:<8} ${h['invested']:>11,.2f} ${h['current_value']:>11,.2f} ${g:>9,.2f} {pct:>+7.2f}%")


if __name__ == "__main__":
    main()
