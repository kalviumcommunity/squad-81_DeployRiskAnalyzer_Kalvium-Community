"""
SQL Query Optimization and Performance Profiling (Assignment Tasks)
Implements:
1. Mock dataset generation for transactions, customers, and products tables.
2. Side-by-side execution and profiling of SELECT * vs explicit columns.
3. Pre-join filtering size reduction comparison.
4. CTE nested subquery refactoring.
5. Execution reports and best practices documentation detailing Z-score, index tradeoff, and cache behaviors.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def populate_optimization_tables(engine):
    """Populates transaction, customer, and product tables for profiling."""
    print("Populating analytical database tables for performance profiling...")
    np.random.seed(42)
    
    # 1. Customers Table (500 rows)
    n_customers = 500
    df_customers = pd.DataFrame({
        'id': np.arange(1, n_customers + 1),
        'customer_name': [f"Customer_{i}" for i in range(1, n_customers + 1)],
        'country': np.random.choice(['USA', 'Canada', 'UK', 'Germany', 'France'], size=n_customers, p=[0.50, 0.15, 0.15, 0.10, 0.10]),
        'account_type': np.random.choice(['Enterprise', 'Mid-Market', 'SMB', 'Starter'], size=n_customers),
        'customer_segment': np.random.choice(['Segment A', 'Segment B', 'Segment C'], size=n_customers)
    })
    
    # 2. Products Table (100 rows)
    n_products = 100
    df_products = pd.DataFrame({
        'id': np.arange(1, n_products + 1),
        'product_name': [f"Product_{i}" for i in range(1, n_products + 1)]
    })
    
    # 3. Transactions Table (10000 rows)
    n_tx = 10000
    start_date = pd.Timestamp('2023-01-01')
    random_offsets = np.random.rand(n_tx) * 730  # 2 years range (includes 2024)
    tx_dates = [start_date + pd.Timedelta(days=o) for o in random_offsets]
    
    df_transactions = pd.DataFrame({
        'transaction_id': np.arange(1, n_tx + 1),
        'customer_id': np.random.choice(df_customers['id'], size=n_tx),
        'product_id': np.random.choice(df_products['id'], size=n_tx),
        'transaction_date': tx_dates,
        'amount': np.round(np.random.exponential(scale=150, size=n_tx) + 5, 2)
    })

    # Write to SQL
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_products.to_sql('products', engine, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)
    print("Database populated successfully.")

def load_query(query_name):
    """Load SQL query from queries/ folder."""
    query_path = f'queries/{query_name}.sql'
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"SQL file not found at: {query_path}")
    with open(query_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("==================================================")
    print("       SQL ANALYTICAL QUERY OPTIMIZATION          ")
    print("==================================================")

    db_path = 'analytics.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Populate tables
    populate_optimization_tables(engine)

    # -------------------------------------------------------------------------
    # Task 1: Refactor SELECT * to Explicit Columns
    # -------------------------------------------------------------------------
    print("\n--- Task 1: SELECT * vs Explicit Columns ---")
    
    original_query_1 = """
    SELECT *
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    WHERE strftime('%Y', t.transaction_date) = '2024'
    LIMIT 1000;
    """
    
    optimized_query_1 = load_query('select_explicit')

    # Execute original
    t0 = time.perf_counter()
    res_orig_1 = pd.read_sql(original_query_1, engine)
    orig_time_1 = time.perf_counter() - t0

    # Execute optimized
    t0 = time.perf_counter()
    res_opt_1 = pd.read_sql(optimized_query_1, engine)
    opt_time_1 = time.perf_counter() - t0

    print(f"Original Columns: {res_orig_1.shape[1]} | Time: {orig_time_1:.4f}s")
    print(f"Optimized Columns: {res_opt_1.shape[1]} | Time: {opt_time_1:.4f}s")
    reduction_cols = ((res_orig_1.shape[1] - res_opt_1.shape[1]) / res_orig_1.shape[1]) * 100
    print(f"Improvement: {reduction_cols:.1f}% fewer columns loaded into memory")

    # -------------------------------------------------------------------------
    # Task 2: Apply Filters Before JOINs
    # -------------------------------------------------------------------------
    print("\n--- Task 2: Apply Filters Before JOINs ---")
    
    # Original Join then filter
    original_query_2 = """
    SELECT t.transaction_id, t.amount, c.customer_name, p.product_name
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    JOIN products p ON t.product_id = p.id
    WHERE t.transaction_date >= '2024-01-01'
      AND t.amount > 100
      AND c.country = 'USA'
    LIMIT 5000;
    """
    
    optimized_query_2 = load_query('filter_before_join')

    # Total row counts for reduction calculation
    transactions_count = pd.read_sql("SELECT COUNT(*) as ct FROM transactions", engine).iloc[0, 0]
    
    filtered_transactions_count = pd.read_sql("""
        SELECT COUNT(*) as ct FROM transactions
        WHERE transaction_date >= '2024-01-01'
          AND amount > 100
    """, engine).iloc[0, 0]

    # Execute both and verify same shapes
    res_orig_2 = pd.read_sql(original_query_2, engine)
    res_opt_2 = pd.read_sql(optimized_query_2, engine)

    print(f"Original transaction table size: {transactions_count:,} rows")
    print(f"Filtered transaction size (before join): {filtered_transactions_count:,} rows ({(filtered_transactions_count/transactions_count)*100:.1f}%)")
    print(f"Reduction factor: {transactions_count / filtered_transactions_count:.1f}x smaller dataset before joining")
    assert len(res_orig_2) == len(res_opt_2), "Query result row mismatch!"

    # -------------------------------------------------------------------------
    # Task 3: Use CTEs for Readability
    # -------------------------------------------------------------------------
    print("\n--- Task 3: Use CTEs for Readability ---")
    
    original_query_3 = """
    SELECT customer_segment, AVG(revenue_per_transaction) as avg_transaction_value
    FROM (
        SELECT 
            c.customer_segment,
            AVG(t.amount) as revenue_per_transaction,
            COUNT(DISTINCT t.transaction_id) as transaction_count
        FROM (
            SELECT t.transaction_id, t.amount, t.customer_id
            FROM transactions t
            WHERE t.transaction_date >= '2024-01-01'
        ) t
        JOIN customers c ON t.customer_id = c.id
        GROUP BY c.customer_segment
    ) grouped
    GROUP BY customer_segment
    ORDER BY avg_transaction_value DESC;
    """
    
    optimized_query_3 = load_query('cte_readability')

    res_orig_3 = pd.read_sql(original_query_3, engine)
    res_opt_3 = pd.read_sql(optimized_query_3, engine)

    print("\nOptimized Query Segment Metrics Result:")
    print(res_opt_3)
    
    # Confirm identical
    pd.testing.assert_frame_equal(res_orig_3[['customer_segment', 'avg_transaction_value']], res_opt_3[['customer_segment', 'avg_transaction_value']])
    print("[PASS] Nested subqueries replaced by CTEs return identical results.")

    # -------------------------------------------------------------------------
    # Task 4 & 5: Write Documentation and Answers
    # -------------------------------------------------------------------------
    print("\n--- Task 4 & 5: Generating Comparison Report ---")
    
    markdown_table = (
        "| Metric | Original | Optimized |\n"
        "| :--- | :--- | :--- |\n"
        f"| Columns Selected | 10 (SELECT *) | 5 explicit (Task 1) |\n"
        f"| Intermediate Rows | {transactions_count:,} rows | {filtered_transactions_count:,} rows |\n"
        "| Filters Applied Before Join | No | Yes |\n"
        "| Nesting Depth | 3 levels | 1 level (CTEs) |\n"
        "| Readability Score | Hard to follow | Clear steps |\n"
    )
    
    report_markdown = f"""# SQL Query Optimization Comparison Report

## 1. Summary Comparison Table

{markdown_table}

---

## 2. Refactoring Detailed Analyses

### Query 1: SELECT * to Explicit Columns
* **Original Inefficiency**: Loading all columns from both tables, including internal keys (`customer_id`, `id`) and unused variables.
* **Optimized Strategy**: Selecting only `transaction_id`, `transaction_date`, `amount`, `customer_name`, and `country`.
* **Performance Impact**: Reduced loaded column count by **50%**, minimizing memory consumption and network I/O.

### Query 2: Apply Filters Before JOINs
* **Original Inefficiency**: Joining the full transactions table (10,000 rows) with customers and products before applying filters.
* **Optimized Strategy**: Filtered the transaction history by date and amount inside a CTE, reducing row size before executing JOINs.
* **Performance Impact**: Intermediate dataset was reduced by **{transactions_count / filtered_transactions_count:.1f}x** before joining.

### Query 3: CTE Refactoring for Readability
* **Original Inefficiency**: Nested subqueries that make tracing columns, join contexts, and aliases difficult.
* **Optimized Strategy**: Structured sequentially using CTEs (`recent_transactions`, `customer_with_segment`, `segment_metrics`).
* **Impact**: Improved readability and allowed testing of individual CTE blocks independently.

---

## 3. Answers to Follow-Up Questions

### Question 1: Indexing High-Cardinality Columns
* **How it improves performance**: An index creates a lookup tree (B-Tree) structure. Instead of running a full table scan ($O(N)$) to check date boundaries or specific values, the database traverses the tree ($O(\\log N)$), locating the exact rows instantaneously.
* **Tradeoffs**: Indexes require storage space. Furthermore, every write operation (`INSERT`, `UPDATE`, `DELETE`) becomes slower as the database must rebuild or update the index tree.

### Question 2: CTE Caching vs Recalculation
* **Database Behavior**: In SQLite and PostgreSQL, simple CTEs are treated as inline subqueries. In PostgreSQL 12+, CTEs are materialized (cached) by default if referenced more than once, preventing duplicate scans. You can also explicitly control this using `WITH recent_transactions AS MATERIALIZED (...)`. SQLite evaluates CTEs inline unless they are recursive, where it uses temporary tables.

### Question 3: Handling 100M+ Row Datasets
If the pre-join dataset is still massive, we should apply:
1. **Partitioning**: Split the physical table by date ranges (e.g. monthly partitions), allowing the database to prune partitions entirely.
2. **Materialized Views**: Store pre-calculated joined datasets that are refreshed asynchronously during off-peak hours.
3. **Pre-computation**: Maintain daily summary tables, allowing queries to read aggregated results directly instead of parsing raw transactions.
"""

    with open("sql_optimization_report.md", "w", encoding="utf-8") as f:
        f.write(report_markdown)
    with open("output/sql_optimization_report.md", "w", encoding="utf-8") as f:
        f.write(report_markdown)
    print("Saved optimization comparison report to sql_optimization_report.md and output/sql_optimization_report.md")

if __name__ == '__main__':
    main()
