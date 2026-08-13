"""
SQL Filtering Pipeline (Assignment Tasks)
Implements:
1. Populating transactions and customers tables in SQLite database.
2. Executing WHERE filtering, GROUP BY, HAVING, and ORDER BY queries.
3. Generating a Markdown guide detailing WHERE vs HAVING guidelines.
"""

import os
import sys
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def populate_filter_tables(engine):
    """Populates database with sample transaction and customer data for WHERE/HAVING demonstration."""
    print("Populating transaction database tables for filtering analysis...")
    np.random.seed(101)
    
    # 1. Customers table (50 customers)
    n_customers = 50
    customer_ids = np.arange(1, n_customers + 1)
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_customers, p=[0.20, 0.40, 0.40])
    industries = np.random.choice(['Tech', 'Finance', 'Healthcare', 'Retail', 'Education'], size=n_customers)
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_type': customer_types,
        'industry': industries
    })
    
    # 2. Transactions table (800 transactions)
    n_tx = 800
    start_date = pd.Timestamp('2023-06-01')
    random_offsets = np.random.rand(n_tx) * 500  # ~1.5 years range
    tx_dates = [start_date + pd.Timedelta(days=o) for o in random_offsets]
    
    tx_cust_ids = np.random.choice(customer_ids, size=n_tx)
    # Most transactions are completed, some are refunded/failed
    tx_status = np.random.choice(['completed', 'failed', 'refunded'], size=n_tx, p=[0.85, 0.10, 0.05])
    
    # LTV range: Enterprise spends much more
    amounts = []
    for cid in tx_cust_ids:
        ctype = df_customers.loc[df_customers['customer_id'] == cid, 'customer_type'].values[0]
        if ctype == 'Enterprise':
            amounts.append(np.random.normal(5000, 1000))
        elif ctype == 'SMB':
            amounts.append(np.random.normal(800, 200))
        else:
            amounts.append(np.random.normal(150, 40))
            
    df_transactions = pd.DataFrame({
        'transaction_id': np.arange(1, n_tx + 1),
        'order_id': np.arange(10001, 10001 + n_tx),
        'customer_id': tx_cust_ids,
        'transaction_date': tx_dates,
        'amount': np.round(amounts, 2),
        'transaction_status': tx_status
    })

    # Write to SQL
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)
    print("Database tables successfully populated.")

def load_query(query_name):
    """Load SQL query from queries/ folder."""
    query_path = f'queries/{query_name}.sql'
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"SQL file not found at: {query_path}")
    with open(query_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("==================================================")
    print("     SQL FILTERING: WHERE VS HAVING ANALYSIS      ")
    print("==================================================")

    db_path = 'analytics.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Populate tables
    populate_filter_tables(engine)

    # 1. Execute WHERE Filtering
    print("\n--- Task 1: WHERE Filtering (Filter BEFORE Grouping) ---")
    query_where = load_query('where_filtering')
    df_where = pd.read_sql(query_where, engine)
    print(df_where.head(10))

    # 2. Execute GROUP BY and Aggregation
    print("\n--- Task 2: GROUP BY and Aggregation ---")
    query_groupby = load_query('groupby_aggregation')
    df_groupby = pd.read_sql(query_groupby, engine)
    print(df_groupby.head(10))

    # 3. Execute HAVING Filtering
    print("\n--- Task 3: HAVING Filtering (Filter Groups AFTER Aggregation) ---")
    query_having = load_query('having_filtering')
    df_having = pd.read_sql(query_having, engine)
    print(df_having.head(10))

    # 4. Execute WHERE + HAVING Combined
    print("\n--- Task 4: WHERE + HAVING Combined ---")
    query_combined = load_query('where_having_combined')
    df_combined = pd.read_sql(query_combined, engine)
    print(df_combined.head(10))

    # 5. Execute ORDER BY Ranking
    print("\n--- Task 5: ORDER BY Ranking ---")
    query_orderby = load_query('orderby_ranking')
    df_orderby = pd.read_sql(query_orderby, engine)
    print(df_orderby.head(10))

    # Generate Markdown documentation
    best_practices_content = """# SQL Filtering Best Practices: WHERE vs HAVING

Understanding when to filter data in SQL is critical for both query correctness and performance. This guide documents the correct usage patterns for the team.

## Summary: The Core Difference

| Feature | `WHERE` | `HAVING` |
|---|---|---|
| **Execution Order** | Executes **BEFORE** data grouping (`GROUP BY`). | Executes **AFTER** data grouping (`GROUP BY`). |
| **Target Level** | Filters individual **rows** of data. | Filters aggregated **groups** of data. |
| **Aggregate Functions** | **Cannot** contain aggregate functions (e.g. `SUM`, `AVG`, `COUNT`). | **Can** contain aggregate functions. |
| **Primary Use Case** | Data cleaning, filtering invalid states, date range limits. | Filtering aggregated segments based on sizes or value limits. |

---

## 1. WHERE: Filtering Before Grouping
Use `WHERE` to discard irrelevant rows before any aggregation takes place. This reduces database workload.

```sql
SELECT customer_id, SUM(amount) as revenue
FROM transactions
WHERE transaction_status = 'completed'  -- Discard failed transactions first
GROUP BY customer_id;
```

---

## 2. HAVING: Filtering Groups After Aggregation
Use `HAVING` to filter groups based on aggregated calculations (e.g., total sales, customer counts).

```sql
SELECT customer_id, SUM(amount) as revenue
FROM transactions
GROUP BY customer_id
HAVING SUM(amount) > 10000;            -- Filter cohorts that spent > $10k
```

---

## 3. Combining WHERE and HAVING (Recommended Pattern)
In production, queries should combine both:
1. `WHERE` filters out row-level anomalies (refunds, date boundaries, incomplete records).
2. `GROUP BY` aggregates the clean rows.
3. `HAVING` filters the resulting cohort sizes or sum thresholds.

```sql
SELECT 
    c.customer_type,
    SUM(t.amount) as segment_revenue
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'      -- WHERE: row filter
  AND t.transaction_status = 'completed'       -- WHERE: row filter
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 10;    -- HAVING: group size filter
```
"""
    
    with open('sql_filtering_best_practices.md', 'w', encoding='utf-8') as f:
        f.write(best_practices_content)
    with open('output/sql_filtering_best_practices.md', 'w', encoding='utf-8') as f:
        f.write(best_practices_content)
    print("\n[SUCCESS] Generated best practices documentation: sql_filtering_best_practices.md")

if __name__ == '__main__':
    main()
