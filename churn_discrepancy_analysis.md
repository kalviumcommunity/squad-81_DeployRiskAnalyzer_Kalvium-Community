# Churn Metric Discrepancy Analysis

## 1. Churn Metric Discrepancy Analysis
* **Observed Difference**: SQL churn calculation included orders from previous calendar years (such as August 2025), whereas Python correctly bounded the cohorts by specific month-year ranges (July 2026 and August 2026).
* **Investigation**:
  * Traced transactional records: Orders from customer accounts created in August 2025 were matched during the SQL query's `strftime('%m')` join because it checked the month number ('08') without checking the year ('2025' vs '2026').
  * Hand calculation confirmed that the Python output of July-to-August churn was correct.
* **Root Cause**: The buggy SQL query stripped the year component using `strftime('%m')`, causing all historic years to conflate.
* **Fix Applied**: Revised the SQL filter to apply explicit date comparisons (`order_date >= '2026-07-01' AND order_date <= '2026-07-31'`), matching Python's logical boundaries.
* **Validation**: Post-fix verification yielded a **100% match** (Status: PASS).

---

## 2. Answers to Follow-Up Questions

### Question: Why is manual investigation necessary when drift is flagged? What is the risk of auto-fixing based on a tolerance threshold?
1. **Divergence vs. Correctness**: A validation script can tell you that SQL and Python results *do not match*, but it cannot determine *which layer is logically correct*. Both scripts could run successfully without syntax errors, but one might contain a flawed business definition (like the missing year boundary).
2. **Creeping Drift**: Auto-adjusting parameters to force alignment risks hiding systemic bugs. A minor logic error might cause a 0.05% difference today (which falls under tolerance) but expand to a 20% error as the dataset expands.
3. **Preventative Engineering**: A manual review identifies *why* the metrics diverged (e.g. difference in NULL handling, floating-point precision, timezone offsets) and allows developers to apply a permanent code fix in the source queries, preventing future data drift.
