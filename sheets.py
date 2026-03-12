import numpy as np
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe


# ── Read ─────────────────────────────────────────────────────────────────────

def read_history(worksheet: gspread.Worksheet) -> pd.DataFrame:
    """
    Read transaction history. Expected columns: date, ticker, amount.
    Amount values may include '$' and ',' formatting (e.g. "$1,200.00").
    Negative amounts represent sells/withdrawals.
    """
    df = pd.DataFrame(worksheet.get_all_records())
    df.replace("", np.nan, inplace=True)
    df.dropna(inplace=True)
    df["amount"] = (
        df["amount"]
        .apply(lambda x: str(x).replace("$", "").replace(",", ""))
        .astype(float)
    )
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(object)
    return df


# ── Write ─────────────────────────────────────────────────────────────────────

def update_holdings(
    worksheet: gspread.Worksheet,
    holdings: list[dict],
) -> None:
    """
    Rewrite the holdings sheet in a single batch write.
    Preserves any header row already in row 1; writes data from row 2 onward.
    Each dict has keys: ticker, invested, current_value, earnings.
    """
    # Read current sheet to find the header row structure
    existing = worksheet.get_all_values()
    header = existing[0] if existing else []

    # Find header columns (case-insensitive); default to cols 2,3,4,5 if not found
    def _col(name: str, default: int) -> int:
        for i, h in enumerate(header):
            if h.strip().lower() == name.lower():
                return i
        return default - 1  # 0-indexed

    ticker_idx = _col("ticker", 2)
    invested_idx = _col("invested", 3)
    cv_idx = _col("current value", 4)
    earnings_idx = _col("earnings", 5)

    n_cols = max(ticker_idx, invested_idx, cv_idx, earnings_idx) + 1

    # Build rows: keep header, overwrite data rows
    rows = [header[:] if header else [""] * n_cols]
    for h in holdings:
        row = [""] * n_cols
        row[ticker_idx] = h["ticker"]
        row[invested_idx] = round(h["invested"], 2)
        row[cv_idx] = round(h["current_value"], 2)
        row[earnings_idx] = round(h["earnings"], 2)
        rows.append(row)

    # One API call: clear + write everything
    worksheet.clear()
    worksheet.update(rows, "A1")


def update_performance(
    worksheet: gspread.Worksheet,
    invested_df: pd.DataFrame,
    value_df: pd.DataFrame,
) -> None:
    """Write a combined date/invested/value summary to the Performance sheet."""
    worksheet.clear()
    totals = pd.DataFrame(
        {
            "date": invested_df["date"],
            "invested": invested_df["total"],
            "value": value_df["total"],
        }
    )
    set_with_dataframe(worksheet, totals, row=1, col=2)


def update_invested(worksheet: gspread.Worksheet, invested_df: pd.DataFrame) -> None:
    worksheet.clear()
    set_with_dataframe(worksheet, invested_df, row=1, col=1, include_index=False)


def update_values(worksheet: gspread.Worksheet, value_df: pd.DataFrame) -> None:
    worksheet.clear()
    set_with_dataframe(worksheet, value_df, row=1, col=1, include_index=False)
