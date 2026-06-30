"""
Data Loading & Cleaning Module

This module loads bank transaction CSV files,
cleans inconsistent formatting,
and returns a standardized DataFrame.
"""

from pathlib import Path
import pandas as pd


# Required standardized columns
REQUIRED_COLUMNS = [
    "date",
    "description",
    "amount",
    "balance",
]


# Common variations found in bank exports
COLUMN_MAPPING = {
    "transaction date": "date",
    "txn date": "date",
    "posting date": "date",
    "value date": "date",

    "details": "description",
    "transaction": "description",
    "narration": "description",
    "merchant": "description",
    "remarks": "description",

    "withdrawal": "amount",
    "deposit": "amount",
    "debit": "amount",
    "credit": "amount",

    "running balance": "balance",
    "closing balance": "balance",
}


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    """
    Load and clean transaction CSV.

    Parameters
    ----------
    file_path : str | Path

    Returns
    -------
    pd.DataFrame
    """

    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
    )

    # Rename known variants
    df.rename(
        columns=COLUMN_MAPPING,
        inplace=True,
    )

    # Check required columns
    missing = [
        c
        for c in REQUIRED_COLUMNS
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Convert dates
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="mixed"
    )

    # Convert amount
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    # Convert balance
    df["balance"] = pd.to_numeric(
        df["balance"],
        errors="coerce",
    )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "date",
            "amount",
        ]
    )

    # Standardize descriptions
    df["description"] = (
        df["description"]
        .astype(str)
        .str.strip()
    )

    # Remove duplicates
    df = df.drop_duplicates()

    # Sort chronologically
    df = df.sort_values("date")

    # Add month column
    df["month"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    df.reset_index(
        drop=True,
        inplace=True,
    )

    return df

def split_transactions(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separate income and expenses.
    """

    income = (
        df[df["amount"] > 0]
        .copy()
        .reset_index(drop=True)
    )

    expenses = (
        df[df["amount"] < 0]
        .copy()
        .reset_index(drop=True)
    )

    return income, expenses