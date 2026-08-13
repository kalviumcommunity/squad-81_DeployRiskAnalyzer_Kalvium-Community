# SQL Query Optimization Comparison Report

## 1. Summary Comparison Table

| Metric | Original | Optimized |
| :--- | :--- | :--- |
| Columns Selected | 10 (SELECT *) | 5 explicit (Task 1) |
| Intermediate Rows | 10,000 rows | 2,674 rows |
| Filters Applied Before Join | No | Yes |
| Nesting Depth | 3 levels | 1 level (CTEs) |
| Readability Score | Hard to follow | Clear steps |


---

## 2. Refactoring Detailed Analyses

### Query 1: SELECT * to Explicit Columns
* **Original Inefficiency**: Loading all columns from both tables, including internal keys (`customer_id`, `id`) and unused variables.
* **Optimized Strategy**: Selecting only `transaction_id`, `transaction_date`, `amount`, `customer_name`, and `country`.
* **Performance Impact**: Reduced loaded column count by **50%**, minimizing memory consumption and network I/O.

### Query 2: Apply Filters Before JOINs
* **Original Inefficiency**: Joining the full transactions table (10,000 rows) with customers and products before applying filters.
* **Optimized Strategy**: Filtered the transaction history by date and amount inside a CTE, reducing row size before executing JOINs.
* **Performance Impact**: Intermediate dataset was reduced by **3.7x** before joining.

### Query 3: CTE Refactoring for Readability
* **Original Inefficiency**: Nested subqueries that make tracing columns, join contexts, and aliases difficult.
* **Optimized Strategy**: Structured sequentially using CTEs (`recent_transactions`, `customer_with_segment`, `segment_metrics`).
* **Impact**: Improved readability and allowed testing of individual CTE blocks independently.

---

## 3. Answers to Follow-Up Questions

### Question 1: Indexing High-Cardinality Columns
* **How it improves performance**: An index creates a lookup tree (B-Tree) structure. Instead of running a full table scan ($O(N)$) to check date boundaries or specific values, the database traverses the tree ($O(\log N)$), locating the exact rows instantaneously.
* **Tradeoffs**: Indexes require storage space. Furthermore, every write operation (`INSERT`, `UPDATE`, `DELETE`) becomes slower as the database must rebuild or update the index tree.

### Question 2: CTE Caching vs Recalculation
* **Database Behavior**: In SQLite and PostgreSQL, simple CTEs are treated as inline subqueries. In PostgreSQL 12+, CTEs are materialized (cached) by default if referenced more than once, preventing duplicate scans. You can also explicitly control this using `WITH recent_transactions AS MATERIALIZED (...)`. SQLite evaluates CTEs inline unless they are recursive, where it uses temporary tables.

### Question 3: Handling 100M+ Row Datasets
If the pre-join dataset is still massive, we should apply:
1. **Partitioning**: Split the physical table by date ranges (e.g. monthly partitions), allowing the database to prune partitions entirely.
2. **Materialized Views**: Store pre-calculated joined datasets that are refreshed asynchronously during off-peak hours.
3. **Pre-computation**: Maintain daily summary tables, allowing queries to read aggregated results directly instead of parsing raw transactions.
