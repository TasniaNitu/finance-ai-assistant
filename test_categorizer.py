from src.data_loader import load_transactions
from src.categorizer import categorize_dataframe

df = load_transactions(
    "data/sample_transactions.csv"
)

df = categorize_dataframe(df)

print(df.head(10))

print()

print(df.tail(10))

print()

print(df["category"].value_counts().sort_index())