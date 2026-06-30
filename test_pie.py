from src.data_loader import load_transactions
from src.categorizer import categorize_dataframe
from src.dashboard import spending_by_category

df = load_transactions("data/sample_transactions.csv")
df = categorize_dataframe(df)

fig = spending_by_category(df)

fig.show()