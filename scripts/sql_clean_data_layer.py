"""
Clean Data Layer Design and Verification Pipeline (Assignment Tasks)
Implements:
1. Creating mock analytical source tables (customers, orders, order_items, products).
2. Instantiating database views (vw_active_customers, vw_your_custom_metric).
3. Instantiating and populating the pre-aggregated summary table (agg_daily_metrics).
4. Verifying correctness and querying times of the views and aggregates.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, text

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def populate_source_tables(engine):
    """Populates raw tables with sample records for metrics views."""
    print("Populating analytical source tables in database...")
    np.random.seed(42)
    
    # 1. Customers Table (200 rows)
    n_customers = 200
    customer_ids = np.arange(1, n_customers + 1)
    customer_names = [f"Customer_{cid}" for cid in customer_ids]
    segments = np.random.choice(['Enterprise', 'Mid-Market', 'SMB', 'Starter'], size=n_customers)
    deleted_at = [pd.Timestamp('2025-06-01') if np.random.rand() < 0.05 else None for _ in range(n_customers)]
    
    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_name': customer_names,
        'segment': segments,
        'deleted_at': deleted_at
    })
    
    # 2. Products Table (50 rows)
    n_products = 50
    product_ids = np.arange(1, n_products + 1)
    product_names = [f"Product_{pid}" for pid in product_ids]
    
    df_products = pd.DataFrame({
        'product_id': product_ids,
        'product_name': product_names
    })
    
    # 3. Orders Table (1000 rows)
    n_orders = 1000
    order_ids = np.arange(10001, 10001 + n_orders)
    order_customer_ids = np.random.choice(customer_ids, size=n_orders)
    order_amounts = np.round(np.random.exponential(scale=300, size=n_orders) + 15, 2)
    # Timestamps range inside last 60 days to show active 30d window
    start_date = pd.Timestamp.now() - pd.Timedelta(days=60)
    order_dates = [start_date + pd.Timedelta(days=int(np.random.randint(0, 60)), hours=int(np.random.randint(0, 24))) for _ in range(n_orders)]
    
    df_orders = pd.DataFrame({
        'order_id': order_ids,
        'customer_id': order_customer_ids,
        'order_amount': order_amounts,
        'order_date': order_dates
    })
    
    # 4. Order Items Table (2000 rows)
    n_items = 2000
    item_ids = np.arange(1, n_items + 1)
    item_order_ids = np.random.choice(order_ids, size=n_items)
    item_product_ids = np.random.choice(product_ids, size=n_items)
    quantities = np.random.randint(1, 5, size=n_items)
    unit_prices = np.round(np.random.uniform(10.0, 150.0, size=n_items), 2)
    
    df_items = pd.DataFrame({
        'item_id': item_ids,
        'order_id': item_order_ids,
        'product_id': item_product_ids,
        'quantity': quantities,
        'unit_price': unit_prices
    })

    # Save to SQL
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_products.to_sql('products', engine, if_exists='replace', index=False)
    df_orders.to_sql('orders', engine, if_exists='replace', index=False)
    df_items.to_sql('order_items', engine, if_exists='replace', index=False)
    print("Analytical tables successfully populated.")

def load_sql_file(filepath):
    """Load DDL string from .sql file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("==================================================")
    print("           CLEAN DATA LAYER INTERACTIVE           ")
    print("==================================================")

    db_path = 'analytics.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Populate tables
    populate_source_tables(engine)

    # 1. Instantiate Views
    print("\n--- Task 1: Instantiating Database Views ---")
    
    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vw_active_customers;"))
        conn.execute(text("DROP VIEW IF EXISTS vw_your_custom_metric;"))
        
        view_1_sql = load_sql_file("database/views/vw_active_customers.sql")
        view_2_sql = load_sql_file("database/views/vw_your_custom_metric.sql")
        
        conn.execute(text(view_1_sql))
        conn.execute(text(view_2_sql))
        print("Views 'vw_active_customers' and 'vw_your_custom_metric' successfully created.")

    # 2. Instantiate and Populate Pre-Aggregated Table
    print("\n--- Task 2: Instantiating Pre-Aggregated Tables ---")
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS agg_daily_metrics;"))
        table_ddl = load_sql_file("database/aggregations/agg_daily_metrics.sql")
        conn.execute(text(table_ddl))
        
        # Populate pre-aggregated table
        populate_sql = """
        INSERT INTO agg_daily_metrics
        SELECT 
            date(o.order_date) as aggregation_date,
            'total_revenue' as metric_name,
            SUM(o.order_amount) as metric_value,
            COUNT(*) as row_count,
            datetime('now') as updated_at
        FROM orders o
        GROUP BY date(o.order_date);
        """
        conn.execute(text(populate_sql))
        print("Pre-aggregated table 'agg_daily_metrics' successfully created and populated.")

    # 3. Verify querying from python
    print("\n--- Task 3: Querying clean data layer ---")
    
    # Query Active Customers
    active_customers = pd.read_sql("""
        SELECT 
            customer_id, 
            customer_name, 
            revenue_30d,
            days_since_order
        FROM vw_active_customers
        WHERE days_since_order <= 30
        ORDER BY revenue_30d DESC
        LIMIT 10
    """, engine)
    
    print("\nTop 10 Active Customers (last 30 days):")
    print(active_customers)

    # Query Product Performance View
    product_performance = pd.read_sql("SELECT * FROM vw_your_custom_metric LIMIT 10", engine)
    print("\nProduct Performance (First 10 items):")
    print(product_performance)

    # Query Pre-aggregated Table
    start_time = time.perf_counter()
    agg_data = pd.read_sql("""
        SELECT 
            aggregation_date,
            metric_name,
            metric_value
        FROM agg_daily_metrics
        ORDER BY aggregation_date DESC
        LIMIT 10
    """, engine)
    elapsed_time = (time.perf_counter() - start_time) * 1000
    
    print(f"\nPre-aggregated query completed in {elapsed_time:.2f}ms. Rows retrieved:")
    print(agg_data)

    # Segment Aggregation
    segment_rev = pd.read_sql("""
        SELECT 
            segment,
            COUNT(*) as customer_count,
            SUM(revenue_30d) as total_segment_revenue,
            AVG(revenue_30d) as avg_customer_revenue
        FROM vw_active_customers
        GROUP BY segment
        ORDER BY total_segment_revenue DESC
    """, engine)
    print("\nActive Revenue grouped by segment:")
    print(segment_rev)

if __name__ == '__main__':
    main()
