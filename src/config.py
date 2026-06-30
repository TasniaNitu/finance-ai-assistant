"""
Application Configuration

Centralized configuration values for the
Finance AI Assistant.

Keeping configuration here avoids hardcoding
values throughout the project.
"""

from __future__ import annotations


# ==========================================================
# LLM Configuration
# ==========================================================

MODEL_NAME = "qwen2.5:3b"

TEMPERATURE = 0.0

MAX_TOKENS = 1024

REQUEST_TIMEOUT = 120


# ==========================================================
# Conversation Configuration
# ==========================================================

MAX_CHAT_HISTORY = 12

SYSTEM_NAME = "Finance AI Assistant"


# ==========================================================
# Dashboard
# ==========================================================

DEFAULT_CURRENCY = "৳"

DEFAULT_TOP_TRANSACTIONS = 5


# ==========================================================
# Categories
# ==========================================================

CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Entertainment",
    "Healthcare",
    "Income",
    "Other",
]


# ==========================================================
# Dashboard Colors
# ==========================================================

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


# ==========================================================
# Streamlit
# ==========================================================

PAGE_TITLE = "Finance AI Assistant"

PAGE_ICON = "💰"

LAYOUT = "wide"


# ==========================================================
# Sidebar
# ==========================================================

SIDEBAR_TITLE = "Finance AI Assistant"

UPLOAD_TEXT = "Upload Bank Statement (CSV)"

RESET_BUTTON_TEXT = "Reset Session"


# ==========================================================
# Tabs
# ==========================================================

TAB_DASHBOARD = "📊 Dashboard"

TAB_TRANSACTIONS = "📋 Transactions"

TAB_CHAT = "🤖 AI Chat"


# ==========================================================
# Chat
# ==========================================================

STARTER_QUESTIONS = [
    "What did I spend the most on?",
    "Show my biggest expenses.",
    "How much did I spend on Food & Dining?",
    "Give me my latest monthly summary.",
    "Compare the last two months.",
    "Where can I reduce my spending?",
]

WELCOME_MESSAGE = (
    "👋 Welcome to Finance AI Assistant!\n\n"
    "Upload a transaction CSV and ask questions "
    "about your spending, savings, or monthly trends."
)


# ==========================================================
# File Upload
# ==========================================================

ALLOWED_FILE_TYPES = ["csv"]


# ==========================================================
# DataFrame Columns
# ==========================================================

REQUIRED_COLUMNS = [
    "date",
    "description",
    "amount",
    "balance",
]


# ==========================================================
# Metric Labels
# ==========================================================

METRIC_INCOME = "Income"

METRIC_EXPENSES = "Expenses"

METRIC_SAVINGS = "Savings"

METRIC_SAVINGS_RATE = "Savings Rate"


# ==========================================================
# Chart Titles
# ==========================================================

CHART_CATEGORY = "Spending by Category"

CHART_MONTHLY = "Monthly Spending Trend"

CHART_INCOME = "Income vs Expenses"