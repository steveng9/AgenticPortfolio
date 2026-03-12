import pandas as pd
import yfinance as yf


def download_prices(ticker: str, start_date: str) -> pd.DataFrame:
    """Download historical closing prices for a ticker from start_date to today."""
    prices = yf.download(ticker, start=start_date, auto_adjust=True, progress=False)
    return prices


def get_available_date(prices: pd.DataFrame, date_: str, direction: int = 1) -> str:
    """
    Find the nearest available trading day in prices.index at or after (direction=1)
    or at or before (direction=-1) the given date string.
    """
    today = pd.Timestamp.today().date().strftime("%Y-%m-%d")
    while date_ not in prices.index:
        date_ = (
            pd.to_datetime(date_) + pd.Timedelta(days=direction)
        ).date().strftime("%Y-%m-%d")
        if date_ >= today:
            raise ValueError(
                f"Could not find a trading day near {date_} (reached today: {today})"
            )
    return date_


def get_price_change(prices: pd.DataFrame, last_date: str | None, current_date: str) -> float:
    """
    Return the price ratio Close[current_date] / Close[last_date].
    Returns 1.0 if last_date is None (no prior position).
    """
    if last_date is None:
        return 1.0
    prior_price = prices["Close"].loc[last_date].values[0]
    new_price = prices["Close"].loc[current_date].values[0]
    return new_price / prior_price
