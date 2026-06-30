from src.data_loader import load_transactions
from src.categorizer import categorize_dataframe

from src.dashboard import (
    summary_cards,
    spending_by_category,
    monthly_spending_trend,
    income_vs_expenses,
)

print("=" * 60)
print("LOADING DATA")
print("=" * 60)

df = load_transactions("data/sample_transactions.csv")

df = categorize_dataframe(df)

print(df.head())

print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)

summary = summary_cards(df)

print(summary)

print()

print("=" * 60)
print("OPENING CHARTS")
print("=" * 60)

pie = spending_by_category(df)
pie.show()

bar = monthly_spending_trend(df)
bar.show()

income_bar = income_vs_expenses(df)
income_bar.show()

print()

print("=" * 60)
print("ALL DASHBOARD TESTS PASSED")
print("=" * 60)