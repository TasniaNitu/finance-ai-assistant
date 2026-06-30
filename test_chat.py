from src.data_loader import load_transactions
from src.categorizer import categorize_dataframe

from src.chat import (
    load_dataframe,
    ask_finance_ai,
)

print("=" * 60)
print("LOADING DATA")
print("=" * 60)

df = load_transactions(
    "data/sample_transactions.csv"
)

df = categorize_dataframe(df)

load_dataframe(df)

print(df.head())

print()

questions = [

    "How much did I spend on Food & Dining?",

    "Show my biggest expenses.",

    "Compare 2026-03 and 2026-04.",

    "Give me my monthly summary for 2026-04.",

    "How can I reduce my spending?"
]

for q in questions:

    print("=" * 60)

    print("QUESTION")

    print(q)

    print()

    response = ask_finance_ai(q)

    print("ANSWER")

    print(response["answer"])

    print()

print("=" * 60)
print("CHAT TEST COMPLETE")
print("=" * 60)