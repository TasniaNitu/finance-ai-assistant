"""
Finance Dashboard Module

Reusable visualization functions for the Finance AI Assistant.

This module contains NO Streamlit code.
It simply returns Plotly figures and summary statistics.

Functions
---------
summary_cards(df)
    Returns income, expenses, savings and savings rate
    for the latest month.

spending_by_category(df)
    Returns a Plotly donut chart of expense categories.

monthly_spending_trend(df)
    Returns a Plotly bar chart showing monthly expenses.

income_vs_expenses(df)
    Returns a grouped bar chart comparing monthly
    income and expenses.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------------------------------
# Consistent category colors
# ---------------------------------------------------------

CATEGORY_COLORS = {
    "Income": "#2ECC71",
    "Food & Dining": "#E74C3C",
    "Transport": "#9B59B6",
    "Shopping": "#3498DB",
    "Bills & Utilities": "#F39C12",
    "Entertainment": "#E91E63",
    "Healthcare": "#1ABC9C",
    "Other": "#95A5A6",
}


# ---------------------------------------------------------
# Summary Cards
# ---------------------------------------------------------

def summary_cards(df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for the latest month.
    """

    if df.empty:
        return {
            "month": None,
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "savings_rate": 0.0,
        }

    latest_month = df["month"].max()

    month_df = df[df["month"] == latest_month]

    income = month_df.loc[
        month_df["amount"] > 0,
        "amount",
    ].sum()

    expenses = abs(
        month_df.loc[
            month_df["amount"] < 0,
            "amount",
        ].sum()
    )

    savings = income - expenses

    savings_rate = (
        (savings / income) * 100
        if income > 0
        else 0
    )

    return {
        "month": latest_month,
        "income": round(float(income), 2),
        "expenses": round(float(expenses), 2),
        "savings": round(float(savings), 2),
        "savings_rate": round(float(savings_rate), 2),
    }


# ---------------------------------------------------------
# Spending by Category
# ---------------------------------------------------------

def spending_by_category(df: pd.DataFrame):
    """
    Create a donut chart showing spending by category.
    """

    expenses = df[df["amount"] < 0].copy()

    expenses["amount"] = expenses["amount"].abs()

    category_totals = (
        expenses
        .groupby(
            "category",
            as_index=False,
        )["amount"]
        .sum()
        .sort_values(
            "amount",
            ascending=False,
        )
    )

    fig = px.pie(
        category_totals,
        names="category",
        values="amount",
        hole=0.45,
        title="Spending by Category",
        color="category",
        color_discrete_map=CATEGORY_COLORS,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Amount: %{value:,.0f} BDT"
            "<br>%{percent}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        legend_title="Category",
        margin=dict(
            t=60,
            l=20,
            r=20,
            b=20,
        ),
    )

    return fig


# ---------------------------------------------------------
# Monthly Spending Trend
# ---------------------------------------------------------

def monthly_spending_trend(df: pd.DataFrame):
    """
    Create monthly spending trend chart.
    """

    expenses = df[df["amount"] < 0].copy()

    expenses["amount"] = expenses["amount"].abs()

    monthly = (
        expenses
        .groupby(
            "month",
            as_index=False,
        )["amount"]
        .sum()
    )

    fig = px.bar(
        monthly,
        x="month",
        y="amount",
        title="Monthly Spending Trend",
        text="amount",
        color_discrete_sequence=["#3498DB"],
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Expenses: %{y:,.0f} BDT"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Expenses (BDT)",
        showlegend=False,
        margin=dict(
            t=60,
            l=20,
            r=20,
            b=20,
        ),
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=monthly["month"].tolist(),
        ),
    )

    return fig


# ---------------------------------------------------------
# Income vs Expenses
# ---------------------------------------------------------

def income_vs_expenses(df: pd.DataFrame):
    """
    Compare monthly income and expenses.
    """

    monthly = (
        df.groupby("month")
        .apply(
            lambda x: pd.Series(
                {
                    "Income": x.loc[
                        x["amount"] > 0,
                        "amount",
                    ].sum(),
                    "Expenses": abs(
                        x.loc[
                            x["amount"] < 0,
                            "amount",
                        ].sum()
                    ),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )

    fig = go.Figure()

    fig.add_bar(
        x=monthly["month"],
        y=monthly["Income"],
        name="Income",
        marker_color=CATEGORY_COLORS["Income"],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Income: %{y:,.0f} BDT"
            "<extra></extra>"
        ),
    )

    fig.add_bar(
        x=monthly["month"],
        y=monthly["Expenses"],
        name="Expenses",
        marker_color="#E74C3C",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Expenses: %{y:,.0f} BDT"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        barmode="group",
        title="Income vs Expenses",
        xaxis_title="Month",
        yaxis_title="Amount (BDT)",
        legend_title="Type",
        margin=dict(
            t=60,
            l=20,
            r=20,
            b=20,
        ),
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=monthly["month"].tolist(),
        ),
    )

    return fig