## Performance Evaluation

The application was evaluated using a manually verified bank statement containing **179 transactions**. All financial metrics produced by the application were compared against independently calculated ground-truth values.

### Validation Results

| Metric | Manual Calculation | Application Output | Match |
|---------|------------------:|-------------------:|:-----:|
| Total Income | ৳257,400.00 | ৳257,400.00 | ✅ |
| Total Expenses | ৳160,883.00 | ৳160,883.00 | ✅ |
| Net Savings | ৳96,517.00 | ৳96,517.00 | ✅ |
| Savings Rate | 37.50% | 37.50% | ✅ |
| Largest Spending Category | Shopping | Shopping | ✅ |
| Highest Spending Month | January 2026 | January 2026 | ✅ |
| Largest Expense | ৳6,500.00 | ৳6,500.00 | ✅ |
| March vs April | April spending decreased by ৳6,804.00 | April spending decreased by ৳6,804.00 | ✅ |

**Result:** **100% (8/8 metrics matched).**

### Manual vs Automated Analysis

| Metric | Value |
|---------|------:|
| Dataset | Demo bank statement (179 transactions) |
| Metrics Evaluated | 8 |
| Manual Analysis Time | ~60 minutes |
| Application Processing Time | 3.18 seconds (average of 3 runs on the demo dataset) |
| Accuracy | 100% |
| Time Reduction | ~99.9% faster than manual analysis |

The application produced identical results to the manually verified calculations while reducing the analysis time from approximately **60 minutes** to **3.18 seconds**.

## Upload Bank Statement

![Upload Sidebar](screenshots/upload_sidebar.png)

Upload a CSV bank statement to automatically generate financial summaries, interactive dashboards, transaction history, and AI-powered insights.

## Dashboard

![Dashboard](screenshots/dashboard.png)

## Transactions

![Transactions](screenshots/transactions.png)

## AI Chat

![AI Chat](screenshots/ai_chat.png)