"""
SQL Multi-Source Merging & Join Validation (Assignment Tasks)
Implements:
1. Database population (customers, orders, order_items, products) with intentional unmatched keys.
2. LEFT JOIN validation and multiplication factor tracking.
3. Unmatched keys detection (customers without orders, orphaned orders).
4. Join types comparison (INNER, LEFT, simulated FULL OUTER).
5. Multi-table join validation checking against line total duplicates.
6. Centralized join strategy documentation guide.
"""

import os
import sys
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def populate_join_tables(engine):
    """Populates analytical tables in SQLite database with mock customer purchase histories."""
    print("Populating analytical database tables for join validation...")
    np.random.seed(42)
    
    # 1. Customers Table (1000 rows)
    n_customers = 1000
    customer_ids = np.arange(1, n_customers + 1)
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_customers, p=[0.05, 0.40, 0.55])
    start_date = pd.Timestamp('2025-01-01')
    signup_dates = [start_date + pd.Timedelta(days=int(np.random.randint(0, 365))) for _ in range(n_customers)]
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_type': customer_types,
        'signup_date': signup_dates
    })
    
    # 2. Products Table (500 rows)
    n_products = 500
    product_ids = np.arange(1, n_products + 1)
    product_names = [f"Product_{pid}" for pid in product_ids]
    
    df_products = pd.DataFrame({
        'product_id': product_ids,
        'product_name': product_names
    })
    
    # 3. Orders Table (5000 rows total)
    n_orders = 5000
    order_ids = np.arange(100001, 100001 + n_orders)
    
    # Intentional Unmatched keys:
    # 100 customers will have NO orders (so only 900 customers get orders)
    active_customers = customer_ids[:-100]
    
    # Generate customer_ids for orders
    order_customer_ids = np.random.choice(active_customers, size=n_orders)
    
    # Inject 50 orphaned orders (orders with customer_id that does not exist in customers table, e.g., 9999)
    orphaned_indices = np.random.choice(n_orders, size=50, replace=False)
    order_customer_ids[orphaned_indices] = 9999
    
    order_amounts = np.round(np.random.exponential(scale=200, size=n_orders) + 10, 2)
    order_dates = [start_date + pd.Timedelta(days=int(np.random.randint(0, 365))) for _ in range(n_orders)]
    
    df_orders = pd.DataFrame({
        'order_id': order_ids,
        'customer_id': order_customer_ids,
        'order_amount': order_amounts,
        'order_date': order_dates
    })
    
    # 4. Order Items Table (8000 rows)
    n_items = 8000
    item_ids = np.arange(1, n_items + 1)
    item_order_ids = np.random.choice(order_ids, size=n_items)
    item_product_ids = np.random.choice(product_ids, size=n_items)
    quantities = np.random.randint(1, 5, size=n_items)
    unit_prices = np.round(np.random.uniform(5.0, 100.0, size=n_items), 2)
    
    df_items = pd.DataFrame({
        'item_id': item_ids,
        'order_id': item_order_ids,
        'product_id': item_product_ids,
        'quantity': quantities,
        'unit_price': unit_prices
    })
    
    # Write to SQL
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_products.to_sql('products', engine, if_exists='replace', index=False)
    df_orders.to_sql('orders', engine, if_exists='replace', index=False)
    df_items.to_sql('order_items', engine, if_exists='replace', index=False)
    print("Join validation tables populated successfully.")

def load_query(query_name):
    """Load SQL query from queries/ folder."""
    query_path = f'queries/{query_name}.sql'
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"SQL file not found at: {query_path}")
    with open(query_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("==================================================")
    print("        MULTI-SOURCE MERGING & JOIN VALIDATION    ")
    print("==================================================")

    db_path = 'analytics.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Populate tables
    populate_join_tables(engine)

    # Task 1: LEFT JOIN with Row Count Validation
    print("\n--- Task 1: LEFT JOIN & Row Count Validation ---")
    query_left_val = load_query('left_join_validation')
    df_left_val = pd.read_sql(query_left_val, engine)
    
    customers_count = 1000
    print(f"Before: {customers_count} customers")
    print(f"After (grouped): {len(df_left_val)} rows")
    
    # Multiplication factor (Orders per customer)
    # Let's run a query that doesn't group to show raw rows after LEFT JOIN
    raw_left = pd.read_sql("SELECT c.customer_id, o.order_id FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id", engine)
    print(f"Raw LEFT JOIN rows: {len(raw_left)} rows")
    print(f"Change: {len(raw_left) - customers_count} ({((len(raw_left)-customers_count)/customers_count)*100:+.1f}%)")
    print(f"Average Orders per Customer: {len(raw_left)/customers_count:.2f}")

    # Task 2: Detect Unmatched Keys
    print("\n--- Task 2: Detect Unmatched Keys ---")
    query_unmatched_cust = load_query('unmatched_keys_customers')
    df_unmatched_cust = pd.read_sql(query_unmatched_cust, engine)
    
    query_unmatched_ord = load_query('unmatched_keys_orders')
    df_unmatched_ord = pd.read_sql(query_unmatched_ord, engine)
    
    print(f"Customers without orders: {len(df_unmatched_cust)} ({len(df_unmatched_cust)/customers_count * 100:.1f}%)")
    print(f"Orphaned orders (no matching customer): {len(df_unmatched_ord)}")
    if len(df_unmatched_ord) > 0:
        print("[WARNING] Orphaned records found - investigate customer_id mismatch!")

    # Task 3: Compare Join Types
    print("\n--- Task 3: Compare Join Types ---")
    inner_query = "SELECT c.customer_id, o.order_id, o.order_amount FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id"
    left_query = "SELECT c.customer_id, o.order_id, o.order_amount FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id"
    
    # SQLite full outer join simulation
    full_query = """
    SELECT c.customer_id, o.order_id, o.order_amount
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    UNION
    SELECT c.customer_id, o.order_id, o.order_amount
    FROM orders o
    LEFT JOIN customers c ON c.customer_id = o.customer_id
    """
    
    inner_df = pd.read_sql(inner_query, engine)
    left_df = pd.read_sql(left_query, engine)
    full_df = pd.read_sql(full_query, engine)
    
    print(f"INNER: {len(inner_df)} rows (only matching records, excludes unmatched customers and orphaned orders)")
    print(f"LEFT:  {len(left_df)} rows (all customers kept, unmatched customers have NULL order values)")
    print(f"FULL:  {len(full_df)} rows (all records kept, includes unmatched customers and orphaned orders)")

    assert len(left_df) >= len(inner_df)
    assert len(full_df) >= max(len(left_df), 1000)
    print("[PASS] Join relationships validated successfully")

    # Task 4: Multi-Table Join
    print("\n--- Task 4: Multi-Table Join ---")
    query_multi = load_query('multi_table_join')
    df_multi = pd.read_sql(query_multi, engine)
    print(f"Multi-table join retrieved {len(df_multi)} rows for Enterprise customers.")
    
    # Check for duplication: aggregate line_total must equal the sum of order_items line_totals
    product_total = df_multi['line_total'].sum()
    
    # Expected total is only for Enterprise customer order items
    expected_total_enterprise = pd.read_sql("""
        SELECT SUM(oi.quantity * oi.unit_price) 
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_type = 'Enterprise'
    """, engine).iloc[0, 0] or 0.0

    print(f"Decomposition match: Sum in multi-table join: ${product_total:,.2f} | Expected: ${expected_total_enterprise:,.2f}")
    assert abs(product_total - expected_total_enterprise) < 0.01, "Duplication in multi-table join!"
    print("[PASS] Multi-table join validated - no row duplication detected.")

    # Task 5: Document Join Decisions
    print("\n--- Task 5: Document Join Decisions ---")
    join_documentation = """JOIN STRATEGY DOCUMENTATION

Table Structure and Primary Keys:
* Table: customers (1000 rows, PK: customer_id)
* Table: orders (5000 rows, FK: customer_id)
* Table: order_items (8000 rows, FK: order_id)
* Table: products (500 rows, PK: product_id)

Decision 1: customers LEFT JOIN orders
- Purpose: Retrieve comprehensive customer history, ensuring inactive customers are kept.
- Row count change: 1000 -> 5050 (all 1000 customers retained, active customers multiplied by their order count, 100 unmatched customers included).
- Unmatched keys: 100 customers had 0 orders, 50 orphaned orders detected.
- Business use: Customer lifetime value (LTV), segment active/inactive rates.

Decision 2: orders LEFT JOIN order_items  
- Purpose: View detailed product transaction details per order.
- Row count change: 5000 -> 8000 (orders multiplied by the number of line items inside them).
- Unmatched keys: 0 (no orphaned order items without a parent order).
- Business use: Basket size analysis, SKU popularity.

Decision 3: Full 4-table join
- Purpose: Map customer profile to order items and product descriptions.
- Row count: Base orders count multiplied out to item counts.
- Risk of Double Counting: Summing order_amount directly on a combined table will yield double-counting due to line-item multipliers.
- Mitigation: Perform aggregations at the appropriate grouping level.
"""
    print(join_documentation)
    
    with open('output/join_documentation.txt', 'w', encoding='utf-8') as f:
        f.write(join_documentation)
    print("Saved strategy documentation to output/join_documentation.txt")

if __name__ == '__main__':
    main()
