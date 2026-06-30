"""
AI Transaction Categorizer

Uses a local Ollama model (Qwen2.5) to classify
bank transactions into predefined spending categories.
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd


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
# Local LLM
# ==========================================================

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)


# ==========================================================
# Prompt
# ==========================================================

prompt = ChatPromptTemplate.from_template(
"""
You are a personal finance assistant.

Your task is to classify ONE bank transaction.

Choose ONLY ONE category from:

Food & Dining
Transport
Shopping
Bills & Utilities
Entertainment
Healthcare
Income
Other


Examples

Salary -> Income
Freelance Payment -> Income
Bank Interest -> Income

Uber -> Transport
Pathao -> Transport
Bus Ticket -> Transport
Fuel Station -> Transport
Parking Fee -> Transport

KFC DHAKA -> Food & Dining
Pizza Hut -> Food & Dining
Domino's -> Food & Dining
North End Coffee -> Food & Dining
Star Kabab -> Food & Dining
Sultan's Dine -> Food & Dining

Daraz Online -> Shopping
Aarong -> Shopping
Electronics Store -> Shopping
Bata -> Shopping

DESCO BILL -> Bills & Utilities
Internet Bill -> Bills & Utilities
WASA BILL -> Bills & Utilities
Electricity Bill -> Bills & Utilities

Netflix -> Entertainment
Spotify -> Entertainment
Star Cineplex -> Entertainment

Popular Diagnostic -> Healthcare
Doctor Consultation -> Healthcare
Medicine Store -> Healthcare

ATM Withdrawal -> Other
Donation -> Other
Courier Service -> Other


Transaction:

{description}

Return ONLY the category.

Do NOT explain your answer.
"""
)


# ==========================================================
# Build chain ONCE
# ==========================================================

llm_chain = prompt | llm


# ==========================================================
# Categorize One Transaction
# ==========================================================

def categorize_transaction(description: str) -> str:
    """
    Categorize a single transaction description.
    """

    response = llm_chain.invoke(
        {
            "description": description,
        }
    )

    category = response.content.strip()

    if category not in CATEGORIES:
        category = "Other"

    return category


# ==========================================================
# Categorize Entire DataFrame
# ==========================================================

def categorize_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Categorize every transaction in a DataFrame.
    """

    df = df.copy()

    categories = []

    for description in df["description"]:

        category = categorize_transaction(
            description
        )

        categories.append(category)

    df["category"] = categories

    return df