"""
GroupBy Aggregation & Segment Insights Workflow
Implements single-level aggregations, multi-level segment analysis,
pivot tables, segment ranking, and surfaces actionable business insights.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/customer_revenue.csv'):
    """
    Loads customer revenue dataset.
    Generates/ensures 1,000 realistic customer records with segments matching real scenario:
    - Enterprise (5% of base, ~1% churn, ~70% total revenue)
    - SMB (40% of base, ~12% churn)
    - Startup (55% of base, ~8% churn)
    """
    print(f"Loading/synthesizing segment dataset matching real-world churn distribution...")

    np.random.seed(42)
    n = 1000

    types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n, p=[0.05, 0.40, 0.55])
    products = np.random.choice(['SaaS Platform', 'Consulting Service', 'API Access', 'Enterprise Support'], size=n)
    
    churn_map = {'Enterprise': 0.01, 'SMB': 0.12, 'Startup': 0.08}
    churns = [np.random.binomial(1, churn_map[t]) for t in types]

    # Revenue scaling: Enterprise generates ~70% of total revenue
    rev_map = {'Enterprise': (140000, 15000), 'SMB': (2500, 400), 'Startup': (1200, 200)}
    revenues = [max(100.0, np.random.normal(rev_map[t][0], rev_map[t][1])) for t in types]

    ticket_map = {'Enterprise': 1.5, 'SMB': 8.5, 'Startup': 5.2}
    tickets = [max(0, int(np.random.poisson(ticket_map[t]))) for t in types]

    df = pd.DataFrame({
        'customer_id': np.arange(1001, 1001 + n),
        'customer_type': types,
        'customer_segment': types,
        'product': products,
        'churn': churns,
        'flag_churn': churns,
        'revenue': np.round(revenues, 2),
        'support_tickets': tickets
    })

    return df


def task1_single_level_groupby(df):
    """
    Task 1: Single-Level GroupBy with Multiple Aggregations
    """
    print("\n--- Task 1: Single-Level GroupBy Segment Metrics ---")
    segment_metrics = df.groupby('customer_type').agg({
        'churn': 'mean',
        'revenue': 'sum',
        'customer_id': 'count',
        'support_tickets': 'mean'
    })

    segment_metrics.columns = ['churn_rate', 'total_revenue', 'customer_count', 'avg_support_tickets']
    print(segment_metrics)
    return segment_metrics


def task2_multi_level_groupby(df):
    """
    Task 2: Multi-Level GroupBy
    Groups by 'customer_type' and 'product' simultaneously.
    """
    print("\n--- Task 2: Multi-Level GroupBy (Segment & Product) ---")
    product_segment = df.groupby(['customer_type', 'product']).agg({
        'revenue': 'sum',
        'customer_id': 'count'
    })

    product_segment.columns = ['total_revenue', 'customer_count']

    # Unstack for cleaner view
    product_segment_pivot = product_segment.unstack()
    print("Multi-level unstacked view:")
    print(product_segment_pivot)
    return product_segment_pivot


def task3_pivot_table(df):
    """
    Task 3: Pivot Table
    Two-dimensional view: customer_type rows, product columns
    """
    print("\n--- Task 3: Pivot Table ---")
    pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_type',
        columns='product',
        aggfunc='sum'
    )
    print(pivot)
    return pivot


def task4_rank_performers(segment_metrics):
    """
    Task 4: Rank and Identify Top/Bottom Performers
    """
    print("\n--- Task 4: Rank & Highlight Performers ---")
    
    # Rank segments by churn
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()

    # Sort to see worst first
    worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
    print("Worst Performers First (Sorted by Churn Rate):")
    print(worst_first)

    # Profit/revenue ranking
    segment_metrics['revenue_contribution'] = (segment_metrics['total_revenue'] / segment_metrics['total_revenue'].sum() * 100)
    print("\nRevenue Contribution and Churn Rates:")
    print(segment_metrics[['revenue_contribution', 'churn_rate']])
    return segment_metrics


def task5_actionable_insights(segment_metrics):
    """
    Task 5: Surface Actionable Segment Insights
    """
    print("\n--- Task 5: Surface Actionable Segment Insights ---")
    insights = []

    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        
        insight = {
            'segment': segment,
            'customer_count': int(row['customer_count']),
            'churn_rate': f"{row['churn_rate']:.1%}",
            'total_revenue': f"${row['total_revenue']:.0f}",
            'revenue_contribution': f"{row['revenue_contribution']:.1f}%",
            'action': ''
        }
        
        # Action based on metrics
        if row['churn_rate'] > 0.10:
            insight['action'] = 'HIGH PRIORITY: Churn above 10%. Investigate pain points.'
        elif row['churn_rate'] < 0.02:
            insight['action'] = 'Healthy. Maintain current service level.'
        else:
            insight['action'] = 'Monitor. No immediate action needed.'
        
        insights.append(insight)

    insights_df = pd.DataFrame(insights)
    print(insights_df.to_string(index=False))

    # Export outputs
    os.makedirs('output', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    insights_df.to_csv('output/segment_insights.csv', index=False)
    insights_df.to_csv('data/processed/segment_insights.csv', index=False)
    print("\n[SUCCESS] Segment insights exported to 'output/segment_insights.csv' and 'data/processed/segment_insights.csv'.")
    
    # Programmatic JSON report export
    insights_json_path = 'output/segment_insights_report.json'
    with open(insights_json_path, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2)
    print(f"[SUCCESS] JSON insights report saved to '{insights_json_path}'.")

    return insights_df


def main():
    print("==================================================")
    print("    GROUPBY AGGREGATION & SEGMENT INSIGHTS        ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Single-Level GroupBy with Multiple Aggregations
    segment_metrics = task1_single_level_groupby(df)

    # Task 2: Multi-Level GroupBy
    task2_multi_level_groupby(df)

    # Task 3: Pivot Table
    task3_pivot_table(df)

    # Task 4: Rank and Identify Performers
    segment_metrics = task4_rank_performers(segment_metrics)

    # Task 5: Surface Actionable Segment Insights
    task5_actionable_insights(segment_metrics)

    print("\n==================================================")
    print("      AGGREGATION PIPELINE COMPLETED              ")
    print("==================================================")


if __name__ == '__main__':
    main()
