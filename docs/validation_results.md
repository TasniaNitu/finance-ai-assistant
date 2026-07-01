# Validation Results

## Dashboard Validation

The application's financial calculations were independently verified against manually calculated ground-truth values using the `sample_transactions.csv` dataset.

| Metric | Manual | Application | Match |
|--------|--------:|------------:|:-----:|
| Total Income | ৳257,400.00 | ৳257,400.00 | ✅ |
| Total Expenses | ৳160,883.00 | ৳160,883.00 | ✅ |
| Net Savings | ৳96,517.00 | ৳96,517.00 | ✅ |
| Savings Rate | 37.50% | 37.50% | ✅ |
| Largest Spending Category | Shopping | Shopping | ✅ |
| Highest Spending Month | January 2026 | January 2026 | ✅ |
| Largest Expense | ৳6,500.00 | ৳6,500.00 | ✅ |
| March vs April Comparison | April spending decreased by ৳6,804.00 | April spending decreased by ৳6,804.00 | ✅ |

## Result

All dashboard calculations matched the manually verified ground-truth values.

**Validation Accuracy:** **100% (8/8 metrics matched)**

### Validation Methodology

- Dataset: `sample_transactions.csv`
- Transactions Evaluated: **179**
- Validation Method: Independent manual calculation followed by comparison with the application's output.