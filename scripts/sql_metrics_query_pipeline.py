"""
SQL Business Metrics Query Design Pipeline (Assignment Tasks)
Implements:
1. Database tables mock generation (transactions, customers, users).
2. Query loader module to read SQL queries from file.
3. Pandas SQL execution of active users, segment revenue, and daily funnel.
4. Validation functions checking nulls, ranges, and logical consistency.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def populate_mock_tables(engine):
    """Creates and populates mock tables in SQLite for testing queries."""
    print("Generating mock database tables for SQL metrics queries...")
    np.random.seed(42)
    
    # 1. Users table (1000 users)
    n_users = 1000
    start_date = pd.Timestamp('2026-05-15')
    random_offsets = np.random.rand(n_users) * 90  # 90 days range
    created_at = [start_date + pd.Timedelta(days=o) for o in random_offsets]
    
    email_verified_at = []
    first_purchase_at = []
    
    for t in created_at:
        # 80% verify email
        if np.random.rand() < 0.80:
            email_verified_at.append(t + pd.Timedelta(minutes=np.random.randint(1, 60)))
        else:
            email_verified_at.append(None)
            
        # 20% complete first purchase
        if np.random.rand() < 0.20:
            first_purchase_at.append(t + pd.Timedelta(days=np.random.randint(1, 10)))
        else:
            first_purchase_at.append(None)
            
    df_users = pd.DataFrame({
        'user_id': np.arange(1001, 1001 + n_users),
        'created_at': created_at,
        'email_verified_at': email_verified_at,
        'first_purchase_at': first_purchase_at
    })
    
    # 2. Customers table (200 customers)
    n_customers = 200
    customer_ids = np.arange(1, n_customers + 1)
    customer_types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n_customers, p=[0.10, 0.40, 0.50])
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_type': customer_types
    })
    
    # 3. Transactions table (1000 transactions)
    n_tx = 1000
    tx_start_date = pd.Timestamp('2025-08-01')
    tx_offsets = np.random.rand(n_tx) * 365  # 1 year range
    tx_dates = [tx_start_date + pd.Timedelta(days=o) for o in tx_offsets]
    
    tx_cust_ids = np.random.choice(customer_ids, size=n_tx)
    # Join customer_type to transactions
    tx_cust_types = [df_customers.loc[df_customers['customer_id'] == cid, 'customer_type'].values[0] for cid in tx_cust_ids]
    
    amounts = np.random.choice([50.0, 100.0, 500.0, 1500.0], size=n_tx, p=[0.40, 0.30, 0.20, 0.10])
    
    df_transactions = pd.DataFrame({
        'transaction_id': np.arange(1, n_tx + 1),
        'order_id': np.arange(100001, 100001 + n_tx),
        'customer_id': tx_cust_ids,
        'customer_type': tx_cust_types,
        'transaction_date': tx_dates,
        'amount': amounts
    })
    
    # Write to SQL database
    df_users.to_sql('users', engine, if_exists='replace', index=False)
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)
    print("Mock tables 'users', 'customers', and 'transactions' successfully populated.")

def load_query(query_name):
    """Load SQL query from file."""
    query_path = f'queries/{query_name}.sql'
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"SQL file not found at: {query_path}")
    with open(query_path, 'r', encoding='utf-8') as f:
        return f.read()

def validate_metrics(mau_df, revenue_df, funnel_df):
    """Validate metric computation."""
    print("\nStarting metric validation checks...")
    
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue has nulls"
    
    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue <= 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion out of range"
    
    # Check consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, "Zero orders"
        assert row['monthly_revenue'] > 0, "Zero revenue"
        
    print("[PASS] All metrics validated successfully (No nulls, valid ranges, and logical consistency verified)")
    return True

def main():
    print("==================================================")
    print("        BUSINESS METRICS SQL QUERY PIPELINE       ")
    print("==================================================")

    # Setup database engine
    db_path = 'analytics.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Populate tables
    populate_mock_tables(engine)

    # Load and execute Task 1: MAU
    print("\n--- Task 1 & 4: Loading and Executing MAU Query ---")
    mau_query = load_query('monthly_active_users')
    mau = pd.read_sql(mau_query, engine)
    print("\n[Monthly Active Users (First 5 rows)]:")
    print(mau.head())

    # Load and execute Task 2 & 4: Revenue by Segment
    print("\n--- Task 2 & 4: Loading and Executing Revenue Query ---")
    revenue_query = load_query('revenue_by_segment')
    revenue = pd.read_sql(revenue_query, engine)
    print("\n[Revenue by Segment (First 5 rows)]:")
    print(revenue.head())

    # Load and execute Task 3 & 4: Funnel Conversion
    print("\n--- Task 3 & 4: Loading and Executing Funnel Query ---")
    funnel_query = load_query('conversion_funnel')
    funnel = pd.read_sql(funnel_query, engine)
    print("\n[Conversion Funnel (First 5 rows)]:")
    print(funnel.head())

    # Task 5: Validate Query Results
    print("\n--- Task 5: Validate Query Results ---")
    try:
        validate_metrics(mau, revenue, funnel)
    except AssertionError as e:
        print(f"[FAIL] Metrics validation failed: {str(e)}")
        sys.exit(1)

    # Save outputs as reports
    mau.to_csv("output/monthly_active_users_report.csv", index=False)
    revenue.to_csv("output/revenue_by_segment_report.csv", index=False)
    funnel.to_csv("output/conversion_funnel_report.csv", index=False)
    print("\n[SUCCESS] Reports successfully generated and exported under output/ directory.")

if __name__ == '__main__':
    main()
