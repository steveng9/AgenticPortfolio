"""
Core portfolio calculation logic — no I/O, no charts.
All functions take DataFrames and return numbers/arrays.
"""

import numpy as np
import pandas as pd

from prices import download_prices, get_available_date, get_price_change


def get_current_value(
    ticker: str,
    history_df: pd.DataFrame,
    inception: str,
) -> dict:
    """
    Replay all buys/sells for a ticker and return its current state.

    Returns a dict with keys: ticker, invested, current_value, earnings.
    Returns None if price data is unavailable.
    """
    prices = download_prices(ticker, inception)
    if prices.empty:
        print(f"  [skip] no price data for {ticker}")
        return None

    invested = 0.0
    running_total = 0.0
    earnings_total = 0.0
    last_date = None

    ticker_history = history_df[history_df["ticker"] == ticker].sort_values("date")

    for _, row in ticker_history.iterrows():
        date = get_available_date(prices, str(row["date"]))
        change = get_price_change(prices, last_date, date)
        running_total *= change

        overall_change = 1.0 if invested == 0 else running_total / invested
        running_total += row["amount"]

        if row["amount"] < 0:
            # Selling: remove proportional cost basis, book earnings
            sell_amount = -row["amount"]
            earnings_total += sell_amount * ((overall_change - 1) / overall_change)
            invested -= sell_amount * (1 / overall_change)
        else:
            invested += row["amount"]

        last_date = date

    # Bring value to today
    today = get_available_date(prices, pd.Timestamp.today().date().strftime("%Y-%m-%d"), direction=-1)
    running_total *= get_price_change(prices, last_date, today)

    return {
        "ticker": ticker,
        "invested": invested,
        "current_value": running_total,
        "earnings": earnings_total,
    }


def get_performance(
    ticker: str,
    history_df: pd.DataFrame,
    inception: str,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build daily time series of invested and portfolio value for one ticker,
    from inception to today.

    Returns (invested_array, value_array), both length = days_since_inception.
    """
    days_since_inception = (pd.Timestamp.today() - pd.to_datetime(inception)).days + 1
    invested = np.zeros(days_since_inception, dtype=float)
    value = np.zeros(days_since_inception, dtype=float)

    prices = download_prices(ticker, inception)
    if prices.empty:
        return invested, value

    ticker_history = history_df[history_df["ticker"] == ticker]
    day = pd.to_datetime(inception) + pd.Timedelta(days=1)
    yesterday = None  # last known trading day with a price

    for i in range(1, days_since_inception):
        day_s = day.date().strftime("%Y-%m-%d")

        # Check for a transaction on this day
        trades = ticker_history[ticker_history["date"].astype(str) == day_s]
        assert len(trades) <= 1, f"Multiple trades for {ticker} on {day_s} — not handled."
        invested_change = trades["amount"].values[0] if len(trades) == 1 else 0.0

        # Apply market movement if a price exists for this day
        change = 1.0
        if day_s in prices.index:
            change = get_price_change(prices, yesterday, day_s)
            yesterday = day_s

        value[i] = value[i - 1] * change

        overall_change = 1.0 if invested[i - 1] == 0 else value[i - 1] / invested[i - 1]
        value[i] += invested_change

        if invested_change < 0:
            invested[i] = invested[i - 1] + invested_change * (1 / overall_change)
        else:
            invested[i] = invested[i - 1] + invested_change

        day += pd.Timedelta(days=1)

    return invested, value


def build_performance_dataframes(
    all_tickers: list[str],
    history_df: pd.DataFrame,
    inception: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run get_performance() for all tickers and return (invested_df, value_df).
    Both DataFrames have a 'date' column and one column per ticker, plus 'total'.
    """
    date_range = pd.date_range(inception, pd.Timestamp.today(), freq="D").strftime("%Y-%m-%d").tolist()

    invested_df = pd.DataFrame({"date": date_range})
    value_df = pd.DataFrame({"date": date_range})

    for ticker in all_tickers:
        print(f"  {ticker}")
        inv, val = get_performance(ticker, history_df, inception)
        invested_df[ticker] = inv
        value_df[ticker] = val

    invested_df["total"] = invested_df[all_tickers].sum(axis=1)
    value_df["total"] = value_df[all_tickers].sum(axis=1)

    return invested_df, value_df
