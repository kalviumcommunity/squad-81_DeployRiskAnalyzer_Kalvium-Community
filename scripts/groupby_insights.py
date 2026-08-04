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
    Adds a synthetic 'support_tickets' and 'product' columns if missing for groupby tasks.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file '{filepath}' is missing. Please run generation script.")
    
    print(f"Loading dataset from '{filepath}'...")
    df = pd.read_csv(filepath)

    np.random.seed(42)
    n = len(df)

    # Adding a 'product' column if missing
    if 'product' not in df.columns:
        df['product'] = np.random.choice(['SaaS Platform', 'Consulting Service', 'API Access', 'Enterprise Support'], size=n)

    # Adding a 'support_tickets' column if missing
    if 'support_tickets' not in df.columns:
        # Higher churn segment has more support tickets raised
        tickets = np.random.poisson(lam=4.0, size=n)
        tickets = np.where(df['flag_churn'] == 1, tickets + np.random.randint(5, 12, size=n), tickets)
        df['support_tickets'] = tickets

    return df


def task1_single_level_groupby(df):
    """
    Task 1: Single-Level GroupBy with Multiple Aggregations
    Groups by 'customer_segment' and calculates segment-specific performance metrics.
    """
    print("\n--- Task 1: Single-Level GroupBy Segment Metrics ---")
    segment_metrics = df.groupby('customer_segment').agg({
        'flag_churn': 'mean',
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
    Groups by 'customer_segment' and 'product' simultaneously.
    """
    print("\n--- Task 2: Multi-Level GroupBy (Segment & Product) ---")
    product_segment = df.groupby(['customer_segment', 'product']).agg({
        'revenue': 'sum',
        'customer_id': 'count'
    })

    product_segment.columns = ['total_revenue', 'customer_count']
    
    # Unstack for a cleaner multi-dimensional view
    product_segment_pivot = product_segment.unstack()
    print("Multi-level unstacked view:")
    print(product_segment_pivot)
    return product_segment_pivot


def task3_pivot_table(df):
    """
    Task 3: Pivot Table
    Generates a clean pivot table of total revenue by customer segment and product.
    """
    print("\n--- Task 3: Pivot Table ---")
    pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_segment',
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
    
    # Rank segments by churn (rank 1 = lowest churn, best performer)
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()
    
    # Sort to see worst churn segment first
    worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
    print("Worst Performers First (Sorted by Churn Rate):")
    print(worst_first)

    # Profit/revenue contribution ranking
    total_rev = segment_metrics['total_revenue'].sum()
    segment_metrics['revenue_contribution'] = (segment_metrics['total_revenue'] / total_rev) * 100
    
    print("\nRevenue Contribution and Churn Rates:")
    print(segment_metrics[['revenue_contribution', 'churn_rate']])
    return segment_metrics


def task5_actionable_insights(segment_metrics):
    """
    Task 5: Surface Actionable Segment Insights
    """
    print("\n--- Task 5: Actionable Segment Insights ---")
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
        
        # Action criteria based on churn rate thresholds
        if row['churn_rate'] > 0.10:
            insight['action'] = 'HIGH PRIORITY: Churn above 10%. Investigate product pain points and setup retention campaigns.'
        elif row['churn_rate'] < 0.02:
            insight['action'] = 'Healthy. Maintain current high-touch service level and identify upsell opportunities.'
        else:
            insight['action'] = 'Monitor. Optimize onboarding flow and check support tickets raised trend.'
        
        insights.append(insight)

    insights_df = pd.DataFrame(insights)
    print(insights_df.to_string(index=False))

    # Export to processed and output directories
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

    # Task 5: Actionable Segment Insights
    task5_actionable_insights(segment_metrics)

    print("\n==================================================")
    print("      AGGREGATION PIPELINE COMPLETED              ")
    print("==================================================")


if __name__ == '__main__':
    main()
