"""
Multi-Source Merging & Join Validation Pipeline
Merges customer and orders datasets, validates join types, detects unmatched keys,
verifies cardinality/duplication, and exports audit logs & join decision reports.

Tasks Implemented:
1. Explicit Join with Row Count Validation (Left join with before/after count checks)
2. Detect Unmatched Keys (Unmatched customers without orders, orphaned orders)
3. Compare Join Types (Inner, Left, Right, Outer row count comparisons)
4. Validate No Unexpected Duplication (Column conflict & key cardinality checks)
5. Document Join Decision (Structured JSON export to output/join_decision_report.json)
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def generate_synthetic_data(cust_path='data/raw/join_customers.csv', orders_path='data/raw/join_orders.csv'):
    """Generates customer (1000 rows) and orders (5000 rows) datasets if not present."""
    os.makedirs('data/raw', exist_ok=True)
    
    if os.path.exists(cust_path) and os.path.exists(orders_path):
        print(f"Loading existing datasets: '{cust_path}' and '{orders_path}'...")
        df_customers = pd.read_csv(cust_path)
        df_orders = pd.read_csv(orders_path)
        return df_customers, df_orders

    print("Generating synthetic Customer (1000 rows) and Orders (5000 rows) datasets...")
    np.random.seed(42)

    # 1. Customers Table: 1000 customers (IDs 1 to 1000)
    customer_ids = np.arange(1, 1001)
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_name': [f"Customer_{i}" for i in customer_ids],
        'email': [f"user_{i}@example.com" for i in customer_ids],
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=1000),
        'signup_date': pd.date_range(start='2023-01-01', periods=1000, freq='D').strftime('%Y-%m-%d')
    })

    # 2. Orders Table: 5000 orders
    # - 4970 orders distributed among customer IDs 1..950 (leaving 50 customers without orders)
    # - 30 orphaned orders with customer IDs 1001..1030 (customer_id not in customers table)
    matched_cust_pool = np.random.choice(np.arange(1, 951), size=4970)
    orphaned_cust_pool = np.random.choice(np.arange(1001, 1031), size=30)
    all_order_cust_ids = np.concatenate([matched_cust_pool, orphaned_cust_pool])
    np.random.shuffle(all_order_cust_ids)

    df_orders = pd.DataFrame({
        'order_id': np.arange(5001, 10001),
        'customer_id': all_order_cust_ids,
        'order_date': pd.date_range(start='2024-01-01', periods=5000, freq='h').strftime('%Y-%m-%d'),
        'order_amount': np.round(np.random.uniform(15.0, 500.0, size=5000), 2),
        'status': np.random.choice(['Completed', 'Pending', 'Shipped', 'Cancelled'], size=5000)
    })

    df_customers.to_csv(cust_path, index=False)
    df_orders.to_csv(orders_path, index=False)
    print(f"Datasets saved to '{cust_path}' and '{orders_path}'.")

    return df_customers, df_orders


def task1_explicit_join(df_customers, df_orders):
    """Task 1: Explicit Join with Row Count Validation."""
    print("\n--- Task 1: Explicit Join with Row Count Validation ---")
    print(f"Left: {len(df_customers)}")
    print(f"Right: {len(df_orders)}")

    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='left')

    print(f"Merged: {len(df_merged)}")
    print(f"Change: {len(df_merged) - len(df_customers)}")
    return df_merged


def task2_detect_unmatched_keys(df_customers, df_orders):
    """Task 2: Detect Unmatched Keys."""
    print("\n--- Task 2: Detect Unmatched Keys ---")
    unmatched_customers = df_customers[~df_customers['customer_id'].isin(df_orders['customer_id'])]
    unmatched_orders = df_orders[~df_orders['customer_id'].isin(df_customers['customer_id'])]

    print(f"Customers without orders: {len(unmatched_customers)}")
    print(f"Orphaned orders: {len(unmatched_orders)}")

    os.makedirs('output', exist_ok=True)
    unmatched_cust_path = 'output/unmatched_customers.csv'
    unmatched_orders_path = 'output/unmatched_orders.csv'

    unmatched_customers.to_csv(unmatched_cust_path, index=False)
    unmatched_orders.to_csv(unmatched_orders_path, index=False)
    print(f"Saved unmatched customers to '{unmatched_cust_path}'")
    print(f"Saved unmatched orders to '{unmatched_orders_path}'")

    return unmatched_customers, unmatched_orders


def task3_compare_join_types(df_customers, df_orders):
    """Task 3: Compare Join Types."""
    print("\n--- Task 3: Compare Join Types ---")
    inner = pd.merge(df_customers, df_orders, on='customer_id', how='inner')
    left = pd.merge(df_customers, df_orders, on='customer_id', how='left')
    right = pd.merge(df_customers, df_orders, on='customer_id', how='right')
    outer = pd.merge(df_customers, df_orders, on='customer_id', how='outer')

    print(f"Inner: {len(inner)}, Left: {len(left)}, Right: {len(right)}, Outer: {len(outer)}")

    join_comparison = {
        'Inner': len(inner),
        'Left': len(left),
        'Right': len(right),
        'Outer': len(outer)
    }
    return join_comparison, inner, left, right, outer


def task4_validate_no_unexpected_duplication(df_merged):
    """Task 4: Validate No Unexpected Duplication."""
    print("\n--- Task 4: Validate No Unexpected Duplication ---")
    print(f"Merged columns: {list(df_merged.columns)}")

    key_counts = df_merged['customer_id'].value_counts()
    print(f"Max orders per customer: {key_counts.max()}")
    print(f"Unique customers in merged dataset: {df_merged['customer_id'].nunique()}")

    # Verify no unexpected column suffix conflicts (e.g. customer_id_x, customer_id_y)
    conflicting_cols = [c for c in df_merged.columns if c.endswith('_x') or c.endswith('_y')]
    if conflicting_cols:
        print(f"WARNING: Found overlapping column names with suffixes: {conflicting_cols}")
    else:
        print("Column names clean - no suffix conflicts.")

    return key_counts


def task5_document_join_decision(df_customers, df_orders, df_merged, unmatched_customers, unmatched_orders):
    """Task 5: Document Join Decision."""
    print("\n--- Task 5: Document Join Decision ---")
    join_report = {
        'join_type': 'left',
        'left_table': 'customers',
        'right_table': 'orders',
        'join_key': 'customer_id',
        'left_rows': len(df_customers),
        'right_rows': len(df_orders),
        'result_rows': len(df_merged),
        'unmatched_left': len(unmatched_customers),
        'unmatched_right': len(unmatched_orders),
        'reasoning': 'Left join preserves all customers; unmatched customers have no orders'
    }

    print(json.dumps(join_report, indent=2))

    report_path = 'output/join_decision_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(join_report, f, indent=2)
    print(f"\n[SUCCESS] Join decision report saved to '{report_path}'.")

    # Save merged dataset to data/processed
    os.makedirs('data/processed', exist_ok=True)
    processed_path = 'data/processed/merged_customer_orders.csv'
    df_merged.to_csv(processed_path, index=False)
    print(f"[SUCCESS] Merged dataset saved to '{processed_path}'.")

    return join_report


def main():
    print("==================================================")
    print("   MULTI-SOURCE MERGING & JOIN VALIDATION PIPELINE ")
    print("==================================================")

    # Load / Generate Datasets
    df_customers, df_orders = generate_synthetic_data()

    # Task 1: Explicit Join with Row Count Validation
    df_merged = task1_explicit_join(df_customers, df_orders)

    # Task 2: Detect Unmatched Keys
    unmatched_customers, unmatched_orders = task2_detect_unmatched_keys(df_customers, df_orders)

    # Task 3: Compare Join Types
    join_comp, inner, left, right, outer = task3_compare_join_types(df_customers, df_orders)

    # Task 4: Validate No Unexpected Duplication
    key_counts = task4_validate_no_unexpected_duplication(df_merged)

    # Task 5: Document Join Decision
    join_report = task5_document_join_decision(df_customers, df_orders, df_merged, unmatched_customers, unmatched_orders)


if __name__ == '__main__':
    main()
