"""
Finance AI Assistant

Interactive personal finance dashboard powered by
Streamlit, Plotly and a local LLM.

Author: Tasnia Nitu
"""

import time
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_loader import load_transactions
from src.categorizer import categorize_dataframe

from src.dashboard import (
    summary_cards,
    spending_by_category,
    monthly_spending_trend,
    income_vs_expenses,
)

from src.chat import (
    load_dataframe,
    ask_finance_ai,
    clear_chat,
    get_starter_questions,
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Finance AI Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Constants
# ==========================================================

PLOTLY_CONFIG = {
    "displaylogo": False,
    "displayModeBar": False,
    "responsive": True,
}

APP_VERSION = "1.0.0"
DEMO_CSV = Path("demo/sample_transactions.csv")

# ==========================================================
# Session State
# ==========================================================

DEFAULT_STATE = {
    "df": None,
    "messages": [],
    "uploaded_filename": None,
    "data_loaded": False,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# Helper Functions
# ==========================================================

def format_currency(value: float) -> str:
    """
    Format currency as Bangladeshi Taka.
    """
    return f"৳{value:,.2f}"


def extract_ai_response(response) -> str:
    """
    Safely extract the answer string from an AI agent response.

    The LangChain agent can return either:
      - a plain string
      - a dict such as {'answer': '...', 'used_tool': True, ...}

    This helper normalises both cases so the UI always receives
    a clean string ready for st.markdown().
    """
    if isinstance(response, dict):
        return response.get("answer", str(response))
    return str(response)


def reset_application() -> None:
    """
    Reset the application state.
    """
    st.session_state.df = None
    st.session_state.messages = []
    st.session_state.uploaded_filename = None
    st.session_state.data_loaded = False

    clear_chat()


def show_upload_message() -> None:
    """
    Display a placeholder when no CSV has been uploaded.
    """
    st.info(
        "⬅️ Upload a transaction CSV from the sidebar "
        "to begin exploring your finances."
    )


def render_title() -> None:
    """
    Display the page title.
    """
    st.title("💰 Finance AI Assistant")

    st.caption(
        "Upload your bank statement, analyse spending, "
        "and chat with your AI finance assistant."
    )

# ==========================================================
# Sidebar & Data Loading
# ==========================================================

def render_sidebar() -> None:
    """
    Render the sidebar controls.

    Returns
    -------
    None
    """

    with st.sidebar:

        st.header("⚙️ Controls")

        uploaded_file = st.file_uploader(
            "Upload Bank Statement",
            type=["csv"],
            help=(
                "Upload a CSV file containing your "
                "bank transactions."
            ),
        )

        st.divider()

        if st.button(
            "🗑 Reset Session",
            use_container_width=True,
        ):
            reset_application()
            st.success("Session reset successfully.")
            st.rerun()

        st.divider()

        # --------------------------------------------------
        # Use uploaded file or demo dataset
        # --------------------------------------------------
        
        if uploaded_file is None:
            if not DEMO_CSV.exists():
                return
            
            file_source = DEMO_CSV
            display_name = "sample_transactions.csv (Demo)"
            
        else:

            file_source = uploaded_file
            display_name = uploaded_file.name

        # --------------------------------------------------
        # Prevent reprocessing the same file
        # --------------------------------------------------

        if (
            st.session_state.data_loaded
            and display_name
            == st.session_state.uploaded_filename
        ):

            df = st.session_state.df

        else:

            progress = st.progress(0)

            status = st.empty()

            try:

                status.info("Loading transactions...")

                progress.progress(10)

                time.sleep(0.2)

                # ------------------------------
                # Load CSV
                # ------------------------------

                df = load_transactions(
                    file_source
                )

                progress.progress(40)

                status.info(
                    "Categorizing transactions..."
                )

                # ------------------------------
                # Categorize
                # ------------------------------

                df = categorize_dataframe(df)

                progress.progress(85)

                status.info(
                    "Preparing dashboard..."
                )

                # ------------------------------
                # Register dataframe
                # ------------------------------

                load_dataframe(df)

                st.session_state.df = df

                st.session_state.data_loaded = True

                st.session_state.uploaded_filename = (
                    display_name
                )

                progress.progress(100)

                status.success(
                    "Dataset loaded successfully!"
                )

                time.sleep(0.5)

                progress.empty()

                status.empty()

            except Exception as exc:

                progress.empty()

                status.empty()

                st.error(
                    f"❌ {type(exc).__name__}: {exc}"
                )

                st.stop()

        # --------------------------------------------------
        # Dataset Statistics
        # --------------------------------------------------

        st.success("Dataset Ready")
        st.caption(f"📄 {display_name}")

        st.metric(
            "Transactions",
            len(df),
        )

        st.metric(
            "Latest Month",
            df["month"].max(),
        )

        st.metric(
            "Categories",
            df["category"].nunique(),
        )

        total_income = (
            df.loc[
                df["amount"] > 0,
                "amount",
            ]
            .sum()
        )

        total_expenses = abs(
            df.loc[
                df["amount"] < 0,
                "amount",
            ]
            .sum()
        )

        net_savings = total_income - total_expenses

        savings_rate = (
            (net_savings / total_income * 100)
            if total_income > 0
            else 0.0
        )

        st.metric(
            "Total Income",
            format_currency(total_income),
        )

        st.metric(
            "Total Expenses",
            format_currency(total_expenses),
        )

        st.metric(
            "Net Savings",
            format_currency(net_savings),
        )

        st.metric(
            "Savings Rate",
            f"{savings_rate:.1f}%",
        )


# ==========================================================
# Render Title & Sidebar
# ==========================================================

render_title()

render_sidebar()


# ==========================================================
# Wait Until Data Is Loaded
# ==========================================================

if not st.session_state.data_loaded:

    show_upload_message()

    st.stop()


# ==========================================================
# Shared Objects
# ==========================================================

df = st.session_state.df

# ==========================================================
# Tabs
# ==========================================================

tab_dashboard, tab_transactions, tab_chat = st.tabs(
    [
        "📊 Dashboard",
        "📄 Transactions",
        "💬 AI Chat",
    ]
)


# ==========================================================
# Dashboard
# ==========================================================

def render_dashboard() -> None:
    """
    Render the dashboard tab.
    """

    with tab_dashboard:

        summary = summary_cards(df)

        st.header("📊 Financial Overview")

        st.caption(
            f"Latest reporting month: **{summary['month']}**"
        )

        st.write("")

        # --------------------------------------------------
        # Summary Cards
        # --------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            with st.container(border=True):

                st.metric(
                    "💰 Income",
                    format_currency(summary["income"]),
                    help="Total income for the latest month.",
                )

        with col2:
            with st.container(border=True):

                st.metric(
                    "💸 Expenses",
                    format_currency(summary["expenses"]),
                    help="Total expenses for the latest month.",
                )

        with col3:
            with st.container(border=True):

                st.metric(
                    "🏦 Savings",
                    format_currency(summary["savings"]),
                    help="Income minus expenses.",
                )

        with col4:
            with st.container(border=True):

                st.metric(
                    "📈 Savings Rate",
                    f"{summary['savings_rate']:.2f}%",
                    help="Savings divided by income.",
                )

        st.divider()

        # --------------------------------------------------
        # Charts
        # --------------------------------------------------

        left, right = st.columns(2)

        with left:

            st.subheader("🍩 Spending by Category")

            st.plotly_chart(
                spending_by_category(df),
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        with right:

            st.subheader("📈 Monthly Spending Trend")

            st.plotly_chart(
                monthly_spending_trend(df),
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        st.divider()

        st.subheader("📊 Income vs Expenses")

        st.plotly_chart(
            income_vs_expenses(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

        st.divider()

        # --------------------------------------------------
        # AI Insights
        # --------------------------------------------------

        st.subheader("💡 Financial Insights")

        expenses = df[df["amount"] < 0].copy()

        expenses["amount"] = expenses["amount"].abs()

        savings_rate = summary["savings_rate"]

        # Savings rate banner — always shown, regardless of
        # whether expense rows exist in the dataset.

        if savings_rate >= 40:

            st.success(
                f"Excellent savings rate ({savings_rate:.2f}%). "
                "You are saving a large portion of your income."
            )

        elif savings_rate >= 20:

            st.info(
                f"Healthy savings rate ({savings_rate:.2f}%). "
                "There is still room for improvement."
            )

        else:

            st.warning(
                f"Low savings rate ({savings_rate:.2f}%). "
                "Consider reducing discretionary spending."
            )

        # Category and month insight cards require at least one
        # expense row. Guard against an income-only dataset or
        # an empty CSV to prevent idxmax() raising on empty data.

        if expenses.empty:

            st.info(
                "No expense records found in the loaded dataset. "
                "Category and monthly insights will appear once "
                "expense transactions are included."
            )

        else:

            category_totals = (
                expenses
                .groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
            )

            monthly_totals = (
                expenses
                .groupby("month")["amount"]
                .sum()
            )

            top_category = category_totals.idxmax()
            top_category_amount = category_totals.max()

            highest_month = monthly_totals.idxmax()
            highest_month_amount = monthly_totals.max()

            insight1, insight2 = st.columns(2)

            with insight1:

                st.info(
                    f"""
**Largest Expense Category**

{top_category}

{format_currency(top_category_amount)}
"""
                )

            with insight2:

                st.info(
                    f"""
**Highest Spending Month**

{highest_month}

{format_currency(highest_month_amount)}
"""
                )


# ==========================================================
# Render Dashboard
# ==========================================================

render_dashboard()

# ==========================================================
# Transactions Tab
# ==========================================================

def render_transactions() -> None:
    """
    Render the transactions explorer.
    """

    with tab_transactions:

        st.header("📄 Transactions")

        st.caption(
            "Browse, search and filter your transaction history."
        )

        st.write("")

        filtered_df = df.copy()

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            months = sorted(
                filtered_df["month"].unique().tolist()
            )

            selected_month = st.selectbox(
                "Month",
                ["All"] + months,
            )

        with col2:

            categories = sorted(
                filtered_df["category"].unique().tolist()
            )

            selected_category = st.selectbox(
                "Category",
                ["All"] + categories,
            )

        with col3:

            search_text = st.text_input(
                "Search Description",
                placeholder="e.g. Uber, KFC, Salary...",
            )

        # --------------------------------------------------
        # Apply Filters
        # --------------------------------------------------

        if selected_month != "All":

            filtered_df = filtered_df[
                filtered_df["month"] == selected_month
            ]

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["category"]
                == selected_category
            ]

        if search_text:

            filtered_df = filtered_df[
                filtered_df["description"]
                .str.contains(
                    search_text,
                    case=False,
                    na=False,
                )
            ]

        st.write("")

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        total_income = (
            filtered_df.loc[
                filtered_df["amount"] > 0,
                "amount",
            ]
            .sum()
        )

        total_expenses = abs(
            filtered_df.loc[
                filtered_df["amount"] < 0,
                "amount",
            ]
            .sum()
        )

        summary1, summary2, summary3 = st.columns(3)

        with summary1:

            st.metric(
                "Transactions",
                len(filtered_df),
            )

        with summary2:

            st.metric(
                "Income",
                format_currency(total_income),
            )

        with summary3:

            st.metric(
                "Expenses",
                format_currency(total_expenses),
            )

        st.divider()

        # --------------------------------------------------
        # Download
        # --------------------------------------------------

        csv = filtered_df.to_csv(index=False)

        # Build a descriptive filename that reflects any
        # active filters so exported files are easy to tell
        # apart (e.g. transactions_2026-04_Shopping.csv).
        filename_parts = ["transactions"]

        if selected_month != "All":
            filename_parts.append(selected_month)

        if selected_category != "All":
            safe_cat = (
                selected_category
                .replace(" & ", "_")
                .replace(" ", "_")
            )
            filename_parts.append(safe_cat)

        download_filename = "_".join(filename_parts) + ".csv"

        st.download_button(
            "⬇️ Download Filtered CSV",
            data=csv,
            file_name=download_filename,
            mime="text/csv",
            use_container_width=True,
        )

        st.write("")

        # --------------------------------------------------
        # Data Table
        # --------------------------------------------------

        if filtered_df.empty:

            st.info(
                "No transactions match your current filters. "
                "Try adjusting the month, category, or search."
            )

        else:

            display_df = filtered_df.copy()

            display_df["date"] = (
                display_df["date"]
                .dt.strftime("%Y-%m-%d")
            )

            display_df["amount"] = (
                display_df["amount"]
                .map(lambda x: f"৳{x:,.2f}")
            )

            display_df["balance"] = (
                display_df["balance"]
                .map(lambda x: f"৳{x:,.2f}")
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=600,
            )


# ==========================================================
# Render Transactions
# ==========================================================

render_transactions()

# ==========================================================
# AI Chat Tab
# ==========================================================

def render_chat() -> None:
    """
    Render the AI chat interface.
    """

    with tab_chat:

        st.header("💬 AI Finance Assistant")

        st.caption(
            "Ask questions about your transactions, spending patterns, monthly summaries, "
            "or receive personalized financial insights from your uploaded bank statement."
        )

        st.divider()

        # --------------------------------------------------
        # Starter Questions
        # --------------------------------------------------

        if len(st.session_state.messages) == 0:

            st.subheader("Suggested Questions")

            questions = get_starter_questions()

            cols = st.columns(2)

            for i, question in enumerate(questions):

                with cols[i % 2]:

                    if st.button(
                        question,
                        key=f"starter_{i}",
                        use_container_width=True,
                    ):

                        with st.spinner("Thinking..."):

                            raw = ask_finance_ai(question)

                        # FIX: extract plain text from agent
                        # response before storing or rendering
                        answer = extract_ai_response(raw)

                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": question,
                            }
                        )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                        st.rerun()

            st.divider()

        # --------------------------------------------------
        # Chat History
        # --------------------------------------------------

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

        # --------------------------------------------------
        # Chat Input
        # --------------------------------------------------

        prompt = st.chat_input(
            "Ask about your finances..."
        )

        if prompt:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            with st.chat_message("user"):

                st.markdown(prompt)

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    raw = ask_finance_ai(prompt)

                # FIX: extract plain text from agent
                # response before storing or rendering
                answer = extract_ai_response(raw)

                st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        st.divider()

        # --------------------------------------------------
        # Clear Conversation
        # --------------------------------------------------

        if st.button(
            "🗑 Clear Conversation",
            use_container_width=True,
        ):

            clear_chat()

            st.session_state.messages = []

            st.rerun()


# ==========================================================
# Render Chat
# ==========================================================

render_chat()

# ==========================================================
# Application Health Check
# ==========================================================
# Runs before the footer so any data warning appears in
# context rather than after the page has "ended".
# Note: the show_upload_message() / st.stop() guard earlier
# in the file already prevents reaching this point when no
# data is loaded, so only the empty-dataframe case is needed.
# ==========================================================

if st.session_state.df.empty:

    st.warning(
        "The uploaded dataset contains no transactions."
    )

# ==========================================================
# Footer
# ==========================================================

st.divider()

footer_left, footer_right = st.columns([3, 1])

with footer_left:

    st.caption(
        "💰 Finance AI Assistant • "
        "Built with Streamlit, Plotly, Pandas, "
        "LangChain and Ollama"
    )

with footer_right:

    st.caption(f"Version {APP_VERSION}")