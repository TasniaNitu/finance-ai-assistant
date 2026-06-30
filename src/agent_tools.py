"""
LangChain Tool Wrappers

This module exposes the financial insight functions
as LangChain tools.

The actual calculations are implemented in
insights.py.
"""

from langchain_core.tools import tool

from src.insights import (
    get_category_total,
    get_monthly_summary,
    find_top_transactions,
    compare_months,
)


# ---------------------------------------------------------------------
# Shared DataFrame
#
# This is assigned by app.py after a CSV is uploaded.
# ---------------------------------------------------------------------

TRANSACTIONS_DF = None


def set_dataframe(df):
    """
    Register the transaction DataFrame for all tools.

    This should be called once after the CSV has been
    loaded and categorized.
    """

    global TRANSACTIONS_DF
    TRANSACTIONS_DF = df


def _check_dataframe():
    """
    Ensure a DataFrame has been loaded before a tool runs.

    Raises
    ------
    ValueError
        If set_dataframe() has not been called yet.
    """

    if TRANSACTIONS_DF is None:
        raise ValueError(
            "No transaction data loaded. "
            "Upload a CSV first."
        )


# =====================================================================
# Tool 1 — Category Total
# =====================================================================

@tool
def get_category_total_tool(category: str) -> str:
    """
    Use when the user asks:

    - How much did I spend on food?
    - How much did I spend on shopping?
    - How much did I spend on transport?
    - How much did I spend on healthcare?
    - What is my spending in a category?

    Returns the total expense for a spending category.
    """

    _check_dataframe()

    result = get_category_total(
        TRANSACTIONS_DF,
        category,
    )

    return (
        f"Category: {result['category']}\n"
        f"Total Spent: ৳{result['total_spent']:,.2f}\n"
        f"Transactions: {result['transactions']}"
    )


# =====================================================================
# Tool 2 — Monthly Summary
# =====================================================================

@tool
def get_monthly_summary_tool(month: str) -> str:
    """
    Use when the user asks:

    - What happened in January?
    - Give me my monthly summary.
    - Show my spending in March.
    - How much did I save in April?

    Returns a complete monthly financial summary.
    """

    _check_dataframe()

    summary = get_monthly_summary(
        TRANSACTIONS_DF,
        month,
    )

    # ----------------------------------------------------------------
    # Largest single transaction
    # ----------------------------------------------------------------

    largest = summary["largest_expense"]

    if largest is None:
        largest_text = "None"
    else:
        largest_text = (
            f"{largest['description']} "
            f"(৳{largest['amount']:,.2f})"
        )

    # ----------------------------------------------------------------
    # Top spending category for this month
    #
    # Computed directly from the raw DataFrame so the LLM has
    # enough context to give a category-specific recommendation
    # (e.g. "Shopping was your top category — cutting it by 10%
    # would save ৳X per month").
    # ----------------------------------------------------------------

    month_expenses = TRANSACTIONS_DF[
        (TRANSACTIONS_DF["month"] == month)
        & (TRANSACTIONS_DF["amount"] < 0)
    ].copy()

    month_expenses["amount"] = month_expenses["amount"].abs()

    if month_expenses.empty:
        top_category_text = "None"
    else:
        by_cat = (
            month_expenses
            .groupby("category")["amount"]
            .sum()
        )
        top_cat = by_cat.idxmax()
        top_cat_amount = by_cat.max()
        top_category_text = (
            f"{top_cat} (৳{top_cat_amount:,.2f})"
        )

    return (
        f"Month: {summary['month']}\n"
        f"Income: ৳{summary['income']:,.2f}\n"
        f"Expenses: ৳{summary['expenses']:,.2f}\n"
        f"Savings: ৳{summary['savings']:,.2f}\n"
        f"Savings Rate: {summary['savings_rate']:.2f}%\n"
        f"Largest Single Expense: {largest_text}\n"
        f"Top Spending Category: {top_category_text}"
    )


# =====================================================================
# Tool 3 — Top Transactions
# =====================================================================

@tool
def find_top_transactions_tool(n: int = 5) -> str:
    """
    Use when the user asks:

    - What are my biggest expenses?
    - Show my largest purchases.
    - Top spending.
    - Biggest transactions.

    Returns the largest expense transactions.
    """

    _check_dataframe()

    top = find_top_transactions(
        TRANSACTIONS_DF,
        n,
    )

    lines = []

    for _, row in top.iterrows():

        # row['date'] is a pandas Timestamp; slice to YYYY-MM-DD
        # to avoid printing the full "2026-04-15 00:00:00" string.
        date_str = str(row['date'])[:10]

        lines.append(
            f"{date_str} | "
            f"{row['description']} | "
            f"{row['category']} | "
            f"৳{row['amount']:,.2f}"
        )

    return "\n".join(lines)


# =====================================================================
# Tool 4 — Compare Months
# =====================================================================

@tool
def compare_months_tool(
    month1: str,
    month2: str,
) -> str:
    """
    Use when the user asks:

    - Compare January and February.
    - Am I spending more this month?
    - Compare two months.
    - Did my spending increase?

    Returns a comparison between two months.
    """

    _check_dataframe()

    result = compare_months(
        TRANSACTIONS_DF,
        month1,
        month2,
    )

    return (
        f"{result['month_1']}: "
        f"৳{result['month_1_spending']:,.2f}\n"
        f"{result['month_2']}: "
        f"৳{result['month_2_spending']:,.2f}\n"
        f"Difference: "
        f"৳{result['difference']:,.2f}\n"
        f"Trend: {result['trend']}"
    )


# =====================================================================
# Export Tool List
#
# Not used by the current keyword-routing architecture in chat.py,
# which calls tools directly via .invoke(). Retained here so the
# project can switch to an LLM-driven agent (ChatOllama with
# bind_tools) without any changes to this file.
# =====================================================================

TOOLS = [
    get_category_total_tool,
    get_monthly_summary_tool,
    find_top_transactions_tool,
    compare_months_tool,
]