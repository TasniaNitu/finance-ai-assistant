"""
Finance AI Chat Module

Handles all AI conversations for the
Finance AI Assistant.

Workflow

User Question
      │
      ▼
Detect Financial Intent
      │
      ├── Explicit Month  ──► Monthly Summary Tool
      │
      ├── Latest Month    ──► Auto-detect → Monthly Summary Tool
      │
      ├── Category Spend  ──► Category Total Tool
      │
      ├── Compare Months  ──► Compare Months Tool
      │
      ├── Top Expenses    ──► Top Transactions Tool
      │
      └── General         ──► LLM Conversation (with live data context)
"""

from __future__ import annotations

import re

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from src.agent_tools import (
    set_dataframe,
    get_category_total_tool,
    get_monthly_summary_tool,
    compare_months_tool,
    find_top_transactions_tool,
)


# =====================================================
# Configuration
# =====================================================

MODEL_NAME = "qwen2.5:3b"

TEMPERATURE = 0

MAX_HISTORY = 12

LATEST_MONTH_KEYWORDS = {
    "latest",
    "last",
    "recent",
    "current",
}


# =====================================================
# Create LLM
# =====================================================

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
)


# =====================================================
# Prompts
# =====================================================

SYSTEM_PROMPT = """
You are Finance AI Assistant.

You help users understand
their personal finances.

If financial information is supplied,
explain it naturally.

Never invent numbers.

Be concise.

Use Bangladeshi Taka (৳).
Format every amount as ৳X,XXX.XX (e.g. ৳62,350.00).

Use bullet points whenever useful.
"""

# -------------------------------------------------------
# Type-specific explanation prompts
#
# One template per tool so each response is structured
# around what the user actually asked rather than forcing
# every answer into the same rigid format.
# -------------------------------------------------------

EXPLAIN_CATEGORY_PROMPT = """
You are a personal finance assistant for a user in Bangladesh.

The user asked: {question}

Bank statement data: {result}

Write a short, friendly response (under 100 words) that:
- States the total spent in this category and the number of transactions
- Gives one concrete saving tip, such as how much a 10% reduction would save
- Ends with a natural follow-up question

Use ৳X,XXX.XX format for all currency amounts.
Never add numbers not present in the data above.
"""

EXPLAIN_MONTHLY_PROMPT = """
You are a personal finance assistant for a user in Bangladesh.

The user asked: {question}

Monthly bank statement data: {result}

Write a clear, friendly summary (under 150 words) that:
- Opens with the month's income, expenses, and savings in one sentence
- Uses bullet points to highlight the top spending category and the largest single expense
- Rates the savings as Excellent (40%+), Healthy (20–39%), or Needs Attention (below 20%)
- Closes with one specific saving recommendation and a follow-up question

Use ৳X,XXX.XX format for all currency amounts.
Never add numbers not present in the data above.
"""

EXPLAIN_TOP_EXPENSES_PROMPT = """
You are a personal finance assistant for a user in Bangladesh.

The user asked: {question}

Top expense transactions: {result}

Write a clear response (under 130 words) that:
- Briefly introduces the list of largest expenses
- Shows each transaction as a bullet point including date, merchant, category, and amount
- Notes which category appears most frequently across the list
- Gives one actionable recommendation about that category
- Ends with a follow-up question

Use ৳X,XXX.XX format for all currency amounts.
Never add numbers not present in the data above.
"""

EXPLAIN_COMPARE_PROMPT = """
You are a personal finance assistant for a user in Bangladesh.

The user asked: {question}

Month-to-month comparison data: {result}

Write a direct, clear comparison (under 120 words) that:
- States in plain words which month had higher spending and by how much
- Lists both months' totals as bullet points
- Interprets whether the spending trend is improving or getting worse
- If spending went up, suggests one specific area to review
- Ends with a follow-up question

Use ৳X,XXX.XX format for all currency amounts.
Never add numbers not present in the data above.
"""

# Maps the tool name returned by _run_financial_tool to
# the appropriate explanation template.
PROMPT_BY_TOOL: dict[str, str] = {
    "category":        EXPLAIN_CATEGORY_PROMPT,
    "monthly_summary": EXPLAIN_MONTHLY_PROMPT,
    "top_transactions": EXPLAIN_TOP_EXPENSES_PROMPT,
    "compare_months":  EXPLAIN_COMPARE_PROMPT,
}


# =====================================================
# Conversation Memory
# =====================================================

class ChatMemory:
    """
    Stores recent conversation history.
    """

    def __init__(self):

        self.messages = [
            SystemMessage(
                content=SYSTEM_PROMPT
            )
        ]

    def add_user(self, text: str):

        self.messages.append(
            HumanMessage(content=text)
        )

    def add_ai(self, text: str):

        self.messages.append(
            AIMessage(content=text)
        )

    def trim(self):

        if len(self.messages) > MAX_HISTORY + 1:

            self.messages = (
                [self.messages[0]]
                + self.messages[-MAX_HISTORY:]
            )

    def clear(self):

        self.messages = [
            SystemMessage(
                content=SYSTEM_PROMPT
            )
        ]


memory = ChatMemory()


# =====================================================
# DataFrame Registration
# =====================================================

_current_df = None


def load_dataframe(df):
    """
    Register the current DataFrame
    for all financial tools.

    Also keeps a local reference so that
    _get_latest_month() and _build_data_context()
    can inspect it without going through agent_tools.
    """

    global _current_df

    _current_df = df

    set_dataframe(df)


# =====================================================
# Latest Month Helper
# =====================================================

def _get_latest_month() -> str | None:
    """
    Return the most recent YYYY-MM period
    present in the loaded DataFrame.

    Accepts any capitalisation of the date
    column: 'Date', 'date', 'DATE', etc.

    Returns None if:
    - No DataFrame has been loaded yet.
    - The DataFrame has no date column.
    - The date column is not datetime type.
    - Any unexpected error occurs.
    """

    if _current_df is None:
        return None

    try:

        date_col = next(
            (
                col
                for col in _current_df.columns
                if col.lower() == "date"
            ),
            None,
        )

        if date_col is None:
            return None

        latest = (
            _current_df[date_col]
            .dt.to_period("M")
            .astype(str)
            .max()
        )

        return latest

    except Exception:
        return None


# =====================================================
# Last Two Months Helper
# =====================================================

def _get_last_two_months() -> tuple[str, str] | None:
    """
    Return the two most recent YYYY-MM periods
    present in the loaded DataFrame.

    Used by _run_financial_tool() to power comparison
    questions like "Compare my monthly spending" that
    contain no explicit month strings.

    Returns None if:
    - No DataFrame has been loaded yet.
    - Fewer than two distinct months exist in the data.
    - Any unexpected error occurs.
    """

    if _current_df is None:
        return None

    try:

        months = sorted(
            _current_df["month"].unique().tolist()
        )

        if len(months) < 2:
            return None

        return months[-2], months[-1]

    except Exception:
        return None




def _build_data_context() -> str | None:
    """
    Build a concise statistical summary of the loaded
    DataFrame to inject into LLM fallback calls.

    This gives the model real numbers from the user's
    bank statement so it can give personalised advice
    (e.g. "Cutting Shopping by 10% saves ৳1,200/month")
    instead of generic tips that ignore the actual data.

    Returns None if no DataFrame has been loaded yet,
    or if the summary cannot be computed for any reason.
    """

    if _current_df is None:
        return None

    try:

        df = _current_df

        total_income = (
            df.loc[df["amount"] > 0, "amount"].sum()
        )

        total_expenses = (
            df.loc[df["amount"] < 0, "amount"].abs().sum()
        )

        net_savings = total_income - total_expenses

        savings_rate = (
            (net_savings / total_income * 100)
            if total_income > 0
            else 0.0
        )

        months_covered = sorted(
            df["month"].unique().tolist()
        )

        latest_month = (
            months_covered[-1]
            if months_covered
            else "Unknown"
        )

        expense_df = df[df["amount"] < 0].copy()
        expense_df["amount"] = expense_df["amount"].abs()

        top_categories = (
            expense_df
            .groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        category_lines = "\n".join(
            f"  - {cat}: ৳{amt:,.2f}"
            for cat, amt in top_categories.items()
        )

        return f"""[User's Loaded Bank Statement]
Period:              {', '.join(months_covered)}
Latest month:        {latest_month}
Total transactions:  {len(df)}

Overall Totals:
  - Income:        ৳{total_income:,.2f}
  - Expenses:      ৳{total_expenses:,.2f}
  - Net Savings:   ৳{net_savings:,.2f}
  - Savings Rate:  {savings_rate:.1f}%

Top Spending Categories:
{category_lines}

Base your answer on these numbers.
Format every amount as ৳X,XXX.XX.
Do NOT ask the user to provide data — it is already loaded above."""

    except Exception:
        return None


# =====================================================
# Category Mapping
# =====================================================

CATEGORY_MAP = {

    "food": "Food & Dining",
    "restaurant": "Food & Dining",
    "dining": "Food & Dining",
    "coffee": "Food & Dining",
    "groceries": "Food & Dining",
    "supermarket": "Food & Dining",

    "transport": "Transport",
    "uber": "Transport",
    "bus": "Transport",
    "fuel": "Transport",
    "rickshaw": "Transport",
    "pathao": "Transport",

    "shopping": "Shopping",
    "daraz": "Shopping",
    "aarong": "Shopping",
    "clothing": "Shopping",
    "clothes": "Shopping",

    "bill": "Bills & Utilities",
    "bills": "Bills & Utilities",
    "electricity": "Bills & Utilities",
    "internet": "Bills & Utilities",
    "rent": "Bills & Utilities",
    "gas": "Bills & Utilities",

    "movie": "Entertainment",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "entertainment": "Entertainment",

    "doctor": "Healthcare",
    "hospital": "Healthcare",
    "medicine": "Healthcare",
    "pharmacy": "Healthcare",
    "healthcare": "Healthcare",
}


# =====================================================
# Month Extraction
# =====================================================

MONTH_REGEX = r"(20\d{2}-\d{2})"


def extract_months(question: str):

    return re.findall(
        MONTH_REGEX,
        question,
    )


# =====================================================
# Category Extraction
# =====================================================

def extract_category(question: str):

    question = question.lower()

    for keyword, category in CATEGORY_MAP.items():

        if keyword in question:

            return category

    return None


# =====================================================
# Financial Tool Dispatcher
# =====================================================

def _run_financial_tool(
    question: str,
) -> tuple[bool, str, str | None]:
    """
    Detect whether a financial tool should answer
    the user's question.

    Returns
    -------
    tuple[bool, str, str | None]
        (handled, result_string, tool_name)

        tool_name is one of:
          "category", "monthly_summary",
          "top_transactions", "compare_months"
        or None when no tool matched.
    """

    question_lower = question.lower()

    # -------------------------------------------------
    # Category Spending
    # -------------------------------------------------

    category = extract_category(question)

    if (
        category is not None
        and (
            "spend" in question_lower
            or "spent" in question_lower
            or "expense" in question_lower
            or "expenses" in question_lower
            or "cost" in question_lower
        )
    ):

        result = get_category_total_tool.invoke(
            {"category": category}
        )

        return True, result, "category"

    # -------------------------------------------------
    # Monthly Summary — Explicit Month
    # e.g. "summary for 2026-04"
    # -------------------------------------------------

    months = extract_months(question)

    if (
        len(months) >= 1
        and (
            "summary" in question_lower
            or "income" in question_lower
            or "saving" in question_lower
            or "saved" in question_lower
            or "month" in question_lower
        )
    ):

        result = get_monthly_summary_tool.invoke(
            {"month": months[0]}
        )

        return True, result, "monthly_summary"

    # -------------------------------------------------
    # Monthly Summary — Latest / Last / Recent
    # e.g. "Give me my latest monthly summary"
    #      "What happened last month?"
    # -------------------------------------------------

    if (
        any(kw in question_lower for kw in LATEST_MONTH_KEYWORDS)
        and (
            "summary" in question_lower
            or "month" in question_lower
            or "income" in question_lower
            or "saving" in question_lower
            or "saved" in question_lower
            or "spend" in question_lower
            or "spent" in question_lower
            or "expense" in question_lower
        )
    ):

        latest = _get_latest_month()

        if latest is not None:

            result = get_monthly_summary_tool.invoke(
                {"month": latest}
            )

            return True, result, "monthly_summary"

    # -------------------------------------------------
    # Compare Months
    #
    # Two paths:
    #
    # 1. Explicit months — user typed two YYYY-MM strings:
    #    "Compare 2026-03 and 2026-04"
    #    "Is March better than 2026-04?"
    #
    # 2. Auto-detect — user said "compare" / "difference"
    #    but gave no months:
    #    "Compare my monthly spending."
    #    "Compare my last two months."
    #    "How does my spending compare month to month?"
    #
    #    In this case the two most recent months in the
    #    dataset are used automatically.
    # -------------------------------------------------

    compare_intent = (
        "compare" in question_lower
        or "difference" in question_lower
        or "more than" in question_lower
        or "less than" in question_lower
    )

    if compare_intent:

        if len(months) >= 2:
            month1, month2 = months[0], months[1]

        else:
            last_two = _get_last_two_months()

            if last_two is None:
                return False, "", None

            month1, month2 = last_two

        result = compare_months_tool.invoke(
            {
                "month1": month1,
                "month2": month2,
            }
        )

        return True, result, "compare_months"

    # -------------------------------------------------
    # Biggest Expenses / Top Spending
    #
    # Direct superlatives always imply spending:
    #   "biggest", "largest", "highest", "top"
    #   "expensive", "costly"
    #
    # "most" qualified with a spend word catches:
    #   "What did I spend the most on?"
    #   "Which category costs me the most?"
    #   "Where is most of my money going?"
    #
    # Expanded spend_words to cover "cost/costs/money"
    # so the "most" + qualifier branch routes correctly.
    #
    # "most" alone is still NOT matched to avoid
    # catching: "How can I save the most money?"
    # -------------------------------------------------

    spend_words = {
        "spend",
        "spent",
        "expense",
        "expenses",
        "expensive",
        "cost",
        "costs",
        "money",
    }

    if (
        "biggest" in question_lower
        or "largest" in question_lower
        or "highest" in question_lower
        or "top" in question_lower
        or "expensive" in question_lower
        or "costly" in question_lower
        or (
            "most" in question_lower
            and any(w in question_lower for w in spend_words)
        )
    ):

        result = find_top_transactions_tool.invoke(
            {"n": 5}
        )

        return True, result, "top_transactions"

    return False, "", None


# =====================================================
# LLM Helper — General Conversation
# =====================================================

def _ask_llm(question: str) -> str:
    """
    Send a general question to Qwen.

    Memory management (add_user / add_ai) is handled
    by ask_finance_ai() so this function has no side
    effects on the conversation history.

    If financial data is loaded, a concise summary of
    the user's real numbers is injected into the system
    prompt so the model gives specific, personalised
    advice rather than generic tips.
    """

    data_context = _build_data_context()

    if data_context:

        # Enrich the system message for this call only.
        # memory.messages[1:] contains all conversation
        # turns, including the question already added by
        # ask_finance_ai() before this function was called.
        enriched_system = SystemMessage(
            content=SYSTEM_PROMPT + "\n\n" + data_context
        )

        messages_to_send = (
            [enriched_system] + memory.messages[1:]
        )

    else:

        messages_to_send = memory.messages

    response = llm.invoke(messages_to_send)

    return response.content


# =====================================================
# LLM Financial Explanation
# =====================================================

def _explain_financial_result(
    question: str,
    result: str,
    tool_name: str | None = None,
) -> str:
    """
    Convert raw tool output into a structured response.

    Selects a prompt template from PROMPT_BY_TOOL based
    on which tool produced the result so the explanation
    is shaped around what the user actually asked:

    - category         → spending total + saving tip
    - monthly_summary  → income/expenses/savings narrative
    - top_transactions → itemised list + category note
    - compare_months   → direct before/after comparison

    Falls back to EXPLAIN_MONTHLY_PROMPT for any unknown
    tool name.

    Memory management (add_user / add_ai) is handled
    by ask_finance_ai() so this function has no side
    effects on the conversation history.
    """

    prompt_template = PROMPT_BY_TOOL.get(
        tool_name or "",
        EXPLAIN_MONTHLY_PROMPT,
    )

    prompt = prompt_template.format(
        question=question,
        result=result,
    )

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    return response.content


# =====================================================
# Starter Questions
# =====================================================

STARTER_QUESTIONS = [
    "What did I spend the most on?",
    "Where can I save the most money?",
    "How much did I spend on Food & Dining?",
    "Give me my latest monthly summary.",
    "Compare my monthly spending.",
    "How can I reduce my spending?",
]


# =====================================================
# Public Chat API
# =====================================================

def ask_finance_ai(question: str) -> dict:
    """
    Main entry point used by Streamlit.

    Parameters
    ----------
    question : str

    Returns
    -------
    dict

    Example
    -------
    {
        "answer": "...",
        "used_tool": True,
        "tool_name": "financial_tool"
    }
    """

    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "used_tool": False,
            "tool_name": None,
        }

    try:

        # Add question to memory once, before any LLM call,
        # so _ask_llm() can read it from memory.messages
        # without managing history themselves.
        memory.add_user(question)
        memory.trim()

        handled, result, tool_name = _run_financial_tool(
            question
        )

        if handled:
            answer = _explain_financial_result(
                question,
                result,
                tool_name,
            )
        else:
            answer = _ask_llm(question)

        # Add AI response to memory once, after all LLM
        # work is done.
        memory.add_ai(answer)

        return {
            "answer": answer,
            "used_tool": handled,
            "tool_name": tool_name,
        }

    except Exception as error:

        return {
            "answer": (
                "Sorry, something went wrong.\n\n"
                f"{error}"
            ),
            "used_tool": False,
            "tool_name": None,
        }


# =====================================================
# Chat Utilities
# =====================================================

def clear_chat():
    """
    Clear conversation history.
    """

    memory.clear()


def get_chat_history():
    """
    Return conversation history.
    """

    return memory.messages


def get_starter_questions():
    """
    Return suggested questions.
    """

    return STARTER_QUESTIONS.copy()


# =====================================================
# Simple Test
# =====================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Finance AI Chat")
    print("=" * 60)

    while True:

        question = input("\nYou: ")

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        response = ask_finance_ai(question)

        print("\nAssistant:\n")

        print(response["answer"])