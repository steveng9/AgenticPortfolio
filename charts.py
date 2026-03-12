import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns


def plot_portfolio_performance(invested_df: pd.DataFrame, value_df: pd.DataFrame) -> None:
    """
    Plot total invested vs total portfolio value over time.
    Also shades the gain/loss region.
    """
    dates = pd.to_datetime(invested_df["date"])
    invested = invested_df["total"]
    value = value_df["total"]

    sns.set_theme(style="darkgrid")
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, invested, label="Total Invested", color="#4c72b0", linewidth=2)
    ax.plot(dates, value, label="Portfolio Value", color="#55a868", linewidth=2)

    # Shade gain/loss
    ax.fill_between(dates, invested, value, where=(value >= invested), alpha=0.15, color="#55a868", label="Gain")
    ax.fill_between(dates, invested, value, where=(value < invested), alpha=0.15, color="#c44e52", label="Loss")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title("Portfolio Performance", fontsize=16, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value (USD)")
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_ticker_allocation(holdings: list[dict]) -> None:
    """Pie chart of current portfolio value by ticker (excluding zero/negative positions)."""
    active = [h for h in holdings if h and h["current_value"] > 0]
    if not active:
        print("No active holdings to chart.")
        return

    labels = [h["ticker"] for h in active]
    sizes = [h["current_value"] for h in active]

    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.82,
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Current Portfolio Allocation", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_ticker_performance(invested_df: pd.DataFrame, value_df: pd.DataFrame) -> None:
    """One subplot per ticker showing its invested vs value over time."""
    tickers = [c for c in invested_df.columns if c not in ("date", "total")]
    if not tickers:
        return

    dates = pd.to_datetime(invested_df["date"])
    cols = min(3, len(tickers))
    rows = (len(tickers) + cols - 1) // cols

    sns.set_theme(style="darkgrid")
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows), squeeze=False)

    for idx, ticker in enumerate(tickers):
        ax = axes[idx // cols][idx % cols]
        ax.plot(dates, invested_df[ticker], label="Invested", linewidth=1.5)
        ax.plot(dates, value_df[ticker], label="Value", linewidth=1.5)
        ax.set_title(ticker, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.legend(fontsize=8)

    # Hide unused subplots
    for idx in range(len(tickers), rows * cols):
        axes[idx // cols][idx % cols].set_visible(False)

    fig.suptitle("Per-Ticker Performance", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()
