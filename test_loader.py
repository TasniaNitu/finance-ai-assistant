from src.data_loader import (
    load_transactions,
    split_transactions,
)

df = load_transactions(
    "data/sample_transactions.csv"
)

income, expenses = split_transactions(df)

print("\nTransactions")
print(df)

print("\nIncome")
print(income)

print("\nExpenses")
print(expenses)