"""
Financial Insights Module

Pure Pandas functions for financial analysis.

These functions contain NO LangChain code.
They are reusable, easy to test, and are wrapped
later as LangChain tools.
"""

from __future__ import annotations

import pandas as pd


def get_category_total(
    df: pd.DataFrame,
    category: str,
) -> dict:
    """
    Calculate total spending for a category.

    Parameters
    ----------
    df : pd.DataFrame
        Categorized transaction DataFrame.

    category : str
        Spending category.

    Returns
    -------
    dict
    """

    expenses = df[df["amount"] < 0]

    category_df = expenses[
        expenses["category"] == category
    ]

    total = abs(category_df["amount"].sum())

    return {
        "category": category,
        "total_spent": round(float(total), 2),
        "transactions": len(category_df),
    }


def get_monthly_summary(
    df: pd.DataFrame,
    month: str,
) -> dict:
    """
    Generate summary statistics for one month.

    Parameters
    ----------
    month : str

    Example:
        "2026-01"

    Returns
    -------
    dict
    """

    month_df = df[
        df["month"] == month
    ]

    income = (
        month_df[month_df["amount"] > 0]["amount"]
        .sum()
    )

    expenses = abs(
        month_df[month_df["amount"] < 0]["amount"]
        .sum()
    )

    savings = income - expenses

    savings_rate = (
        (savings / income * 100)
        if income > 0
        else 0
    )

    largest = (
        month_df[month_df["amount"] < 0]
        .sort_values("amount")
        .head(1)
    )

    if largest.empty:
        largest_expense = None
    else:
        largest_expense = {
            "description": largest.iloc[0]["description"],
            "amount": abs(
                float(largest.iloc[0]["amount"])
            ),
        }

    return {
        "month": month,
        "income": round(float(income), 2),
        "expenses": round(float(expenses), 2),
        "savings": round(float(savings), 2),
        "savings_rate": round(float(savings_rate), 2),
        "largest_expense": largest_expense,
    }


def find_top_transactions(
    df: pd.DataFrame,
    n: int = 5,
) -> pd.DataFrame:
    """
    Return the largest expense transactions.

    Parameters
    ----------
    n : int

    Returns
    -------
    pd.DataFrame
    """

    expenses = (
        df[df["amount"] < 0]
        .copy()
    )

    top = (
        expenses.sort_values("amount")
        .head(n)
        .copy()
    )

    top["amount"] = top["amount"].abs()

    return top


def compare_months(
    df: pd.DataFrame,
    month1: str,
    month2: str,
) -> dict:
    """
    Compare spending between two months.

    Returns
    -------
    dict
    """

    m1 = abs(
        df[
            (df["month"] == month1)
            & (df["amount"] < 0)
        ]["amount"].sum()
    )

    m2 = abs(
        df[
            (df["month"] == month2)
            & (df["amount"] < 0)
        ]["amount"].sum()
    )

    difference = m2 - m1

    if difference > 0:
        trend = "Increased"

    elif difference < 0:
        trend = "Decreased"

    else:
        trend = "No Change"

    return {
        "month_1": month1,
        "month_2": month2,
        "month_1_spending": round(float(m1), 2),
        "month_2_spending": round(float(m2), 2),
        "difference": round(float(difference), 2),
        "trend": trend,
    }