# Performance Evaluation

## Manual vs Application

The application's performance was evaluated using the same transaction dataset employed during manual validation.

| Metric | Manual | Application |
|---------|--------|-------------|
| Dataset | `sample_transactions.csv` (179 transactions) | `sample_transactions.csv` (179 transactions) |
| Questions Evaluated | 8 | 8 |
| Accuracy | 100% | 100% |
| Analysis Time | Approximately 60 minutes | 3 minutes 57 seconds (average of 2 runs) |

## Performance Improvement

The application produced identical results to the manually verified calculations while reducing financial analysis time from approximately **60 minutes** to **3 minutes 57 seconds**, representing an improvement of approximately **15×** for the evaluated workflow.

## Evaluation Methodology

- Dataset: `sample_transactions.csv`
- Transactions Evaluated: **179**
- Manual analysis included calculating income, expenses, savings, savings rate, largest spending category, highest spending month, largest expense, and comparing March vs. April.
- Application analysis time was measured from uploading the CSV file until the dashboard and calculated metrics were fully displayed.
- Application timing was averaged across **two independent runs**.