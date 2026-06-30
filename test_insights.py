"""
Test Financial Insight Functions
"""

from src.data_loader import load_transactions
from src.categorizer import categorize_dataframe
from src.insights import (
    get_category_total,
    get_monthly_summary,
    find_top_transactions,
    compare_months,
)


# ----------------------------------------------------
# Load and categorize data
# ----------------------------------------------------

df = load_transactions("data/sample_transactions.csv")
df = categorize_dataframe(df)

print("=" * 60)
print("DATA LOADED")
print("=" * 60)
print()

print(df.head())

print()

# ----------------------------------------------------
# Category Total
# ----------------------------------------------------

print("=" * 60)
print("CATEGORY TOTAL")
print("=" * 60)

result = get_category_total(
    df,
    "Food & Dining",
)

print(result)

print()

# ----------------------------------------------------
# Monthly Summary
# ----------------------------------------------------

print("=" * 60)
print("MONTHLY SUMMARY")
print("=" * 60)

summary = get_monthly_summary(
    df,
    "2026-03",
)

print(summary)

print()

# ----------------------------------------------------
# Top Transactions
# ----------------------------------------------------

print("=" * 60)
print("TOP 5 EXPENSES")
print("=" * 60)

top = find_top_transactions(
    df,
    5,
)

print(top)

print()

# ----------------------------------------------------
# Month Comparison
# ----------------------------------------------------

print("=" * 60)
print("MONTH COMPARISON")
print("=" * 60)

comparison = compare_months(
    df,
    "2026-02",
    "2026-03",
)

print(comparison)

print()

print("=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 60)