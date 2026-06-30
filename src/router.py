"""
Finance AI Router

This module determines which financial tool
should answer the user's question.

If no financial tool matches,
the question is handled directly by the LLM.
"""

from __future__ import annotations

import re
from enum import Enum

from src.config import CATEGORIES


# ==========================================================
# Intent Types
# ==========================================================

class Intent(Enum):
    CATEGORY_TOTAL = "category_total"

    MONTHLY_SUMMARY = "monthly_summary"

    COMPARE_MONTHS = "compare_months"

    TOP_TRANSACTIONS = "top_transactions"

    GENERAL = "general"


# ==========================================================
# Category Aliases
# ==========================================================

CATEGORY_ALIASES = {

    "food": "Food & Dining",
    "restaurant": "Food & Dining",
    "dining": "Food & Dining",
    "coffee": "Food & Dining",

    "transport": "Transport",
    "uber": "Transport",
    "bus": "Transport",
    "fuel": "Transport",

    "shopping": "Shopping",
    "daraz": "Shopping",
    "aarong": "Shopping",

    "bill": "Bills & Utilities",
    "electricity": "Bills & Utilities",
    "internet": "Bills & Utilities",
    "utility": "Bills & Utilities",

    "movie": "Entertainment",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "entertainment": "Entertainment",

    "doctor": "Healthcare",
    "hospital": "Healthcare",
    "health": "Healthcare",
    "medicine": "Healthcare",

    "income": "Income",
    "salary": "Income",
}

# ==========================================================
# Question Normalization
# ==========================================================

def normalize_question(question: str) -> str:
    """
    Normalize the user's question for easier matching.

    Parameters
    ----------
    question : str

    Returns
    -------
    str
    """

    question = question.lower().strip()

    question = re.sub(
        r"[^\w\s]",
        "",
        question,
    )

    question = re.sub(
        r"\s+",
        " ",
        question,
    )

    return question


# ==========================================================
# Category Extraction
# ==========================================================

def extract_category(question: str) -> str | None:
    """
    Extract a spending category from a question.

    Returns
    -------
    str | None
    """

    question = normalize_question(question)

    # Exact category names
    for category in CATEGORIES:

        if category.lower() in question:

            return category

    # Aliases
    for alias, category in CATEGORY_ALIASES.items():

        if alias in question:

            return category

    return None


# ==========================================================
# Month Extraction
# ==========================================================

MONTH_PATTERN = re.compile(
    r"(20\d{2}-\d{2})"
)


MONTH_NAMES = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


def extract_months(
    question: str,
) -> list[str]:
    """
    Extract months from a question.

    Supported examples

    2026-03

    March 2026

    April 2026

    Returns
    -------
    list[str]
    """

    question = normalize_question(question)

    months = []

    # ----------------------------------------
    # ISO format
    # ----------------------------------------

    matches = MONTH_PATTERN.findall(
        question
    )

    months.extend(matches)

    # ----------------------------------------
    # Month name + year
    # ----------------------------------------

    for month_name, number in MONTH_NAMES.items():

        pattern = (
            rf"{month_name}\s+(20\d{{2}})"
        )

        result = re.search(
            pattern,
            question,
        )

        if result:

            year = result.group(1)

            months.append(
                f"{year}-{number}"
            )

    return list(dict.fromkeys(months))


# ==========================================================
# Detect Intent
# ==========================================================

def detect_intent(
    question: str,
) -> Intent:
    """
    Detect the user's intent.

    Parameters
    ----------
    question : str

    Returns
    -------
    Intent
    """

    q = normalize_question(question)

    # ----------------------------------------
    # Compare months
    # ----------------------------------------

    if (
        "compare" in q
        or "difference" in q
        or "last month" in q
    ):
        return Intent.COMPARE_MONTHS

    # ----------------------------------------
    # Monthly summary
    # ----------------------------------------

    if (
        "summary" in q
        or "this month" in q
        or "monthly" in q
        or "save" in q
        or "saved" in q
    ):
        return Intent.MONTHLY_SUMMARY

    # ----------------------------------------
    # Top expenses
    # ----------------------------------------

    if (
        "biggest" in q
        or "largest" in q
        or "highest" in q
        or "top" in q
    ):
        return Intent.TOP_TRANSACTIONS

    # ----------------------------------------
    # Category spending
    # ----------------------------------------

    if extract_category(q):

        return Intent.CATEGORY_TOTAL

    # ----------------------------------------
    # General
    # ----------------------------------------

    return Intent.GENERAL

# ==========================================================
# Tool Imports
# ==========================================================

from src.agent_tools import (
    get_category_total_tool,
    get_monthly_summary_tool,
    compare_months_tool,
    find_top_transactions_tool,
)


# ==========================================================
# Route Question
# ==========================================================

def route_question(question: str) -> dict:
    """
    Route a user's question to the appropriate
    financial tool.

    Parameters
    ----------
    question : str

    Returns
    -------
    dict

    Example
    -------
    {
        "handled": True,
        "intent": "category_total",
        "result": "...tool output..."
    }
    """

    intent = detect_intent(question)

    # --------------------------------------------------
    # Category Spending
    # --------------------------------------------------

    if intent == Intent.CATEGORY_TOTAL:

        category = extract_category(question)

        if category is None:
            return {
                "handled": False,
                "intent": intent.value,
                "result": None,
            }

        result = get_category_total_tool.invoke(
            {
                "category": category
            }
        )

        return {
            "handled": True,
            "intent": intent.value,
            "result": result,
        }

    # --------------------------------------------------
    # Monthly Summary
    # --------------------------------------------------

    if intent == Intent.MONTHLY_SUMMARY:

        months = extract_months(question)

        if len(months) == 0:

            return {
                "handled": False,
                "intent": intent.value,
                "result": None,
            }

        result = get_monthly_summary_tool.invoke(
            {
                "month": months[0]
            }
        )

        return {
            "handled": True,
            "intent": intent.value,
            "result": result,
        }

    # --------------------------------------------------
    # Compare Months
    # --------------------------------------------------

    if intent == Intent.COMPARE_MONTHS:

        months = extract_months(question)

        if len(months) < 2:

            return {
                "handled": False,
                "intent": intent.value,
                "result": None,
            }

        result = compare_months_tool.invoke(
            {
                "month1": months[0],
                "month2": months[1],
            }
        )

        return {
            "handled": True,
            "intent": intent.value,
            "result": result,
        }

    # --------------------------------------------------
    # Top Transactions
    # --------------------------------------------------

    if intent == Intent.TOP_TRANSACTIONS:

        result = find_top_transactions_tool.invoke(
            {
                "n": 5
            }
        )

        return {
            "handled": True,
            "intent": intent.value,
            "result": result,
        }

    # --------------------------------------------------
    # General Question
    # --------------------------------------------------

    return {
        "handled": False,
        "intent": Intent.GENERAL.value,
        "result": None,
    }


# ==========================================================
# Debug Helper
# ==========================================================

if __name__ == "__main__":

    tests = [

        "How much did I spend on food?",

        "Compare 2026-03 and 2026-04",

        "Show my biggest expenses",

        "Give me my summary for 2026-02",

        "How can I reduce my spending?",
    ]

    for question in tests:

        print("=" * 60)

        print("Question:")
        print(question)

        print()

        print(route_question(question))