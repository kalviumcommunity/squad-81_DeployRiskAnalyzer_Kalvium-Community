"""
GroupBy Aggregation & Segment Insights Workflow (Assignment Tasks)
Implements:
1. Segmenting by Customer Type and calculating lifetime_value, churn, support_tickets, retention_days.
2. Generating a Summary Statistics Table with ranks and formatting.
3. Visual comparison using a Seaborn heatmap.
4. Top and bottom performer analysis.
5. Actionable segment-specific business insights.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def generate_segment_data():
    """Generates synthetic dataset that mirrors the customer segmentation scenario."""
    np.random.seed(42)
    n = 1000

    # Define customer types based on segment distribution (5% Enterprise, 40% SMB, 55% Startup)
    types = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=n, p=[0.05, 0.40, 0.55])
    
    # Churn rates (Enterprise 1%, SMB 12%, Startup 8%)
    churn_map = {'Enterprise': 0.01, 'SMB': 0.12, 'Startup': 0.08}
    churns = [np.random.binomial(1, churn_map[t]) for t in types]
    
    # LTV distribution (Enterprise ~$150k, SMB ~$8k, Startup ~$2k)
    rev_map = {'Enterprise': (150000, 12000), 'SMB': (8000, 800), 'Startup': (2000, 250)}
    ltv = [max(100.0, np.random.normal(rev_map[t][0], rev_map[t][1])) for t in types]
    
    # Support tickets
    ticket_map = {'Enterprise': 1.5, 'SMB': 8.5, 'Startup': 5.2}
    tickets = [max(0, int(np.random.poisson(ticket_map[t]))) for t in types]
    
    # Retention days
    retention_map = {'Enterprise': (1200, 100), 'SMB': (320, 40), 'Startup': (600, 70)}
    retention = [max(1, int(np.random.normal(retention_map[t][0], retention_map[t][1]))) for t in types]
    
    df = pd.DataFrame({
        'customer_id': np.arange(1001, 1001 + n),
        'customer_type': types,
        'lifetime_value': np.round(ltv, 2),
        'churn': churns,
        'support_tickets': tickets,
        'retention_days': retention
    })
    return df

def main():
    print("==================================================")
    print("      CUSTOMER SEGMENTATION & INSIGHTS            ")
    print("==================================================")

    # Task 1: Define Segments and Compute Metrics
    print("\n--- Task 1: Define Segments and Compute Metrics ---")
    df = generate_segment_data()
    
    segment_metrics = df.groupby('customer_type').agg({
        'lifetime_value': 'mean',
        'churn': 'mean',
        'support_tickets': 'mean',
        'retention_days': 'mean',
        'customer_id': 'count'
    })

    segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'count']
    print(segment_metrics)

    # Document segment sizes
    for seg in segment_metrics.index:
        size = segment_metrics.loc[seg, 'count']
        pct = (size / len(df)) * 100
        print(f"Segment: {seg} | Size: {size} customers ({pct:.1f}% of base)")

    # Task 2: Summary Statistics Table
    print("\n--- Task 2: Summary Statistics Table ---")
    segment_summary = segment_metrics.copy()
    segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False)
    segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True)

    # Format values for readability
    formatted_summary = pd.DataFrame(index=segment_summary.index)
    formatted_summary['Average LTV'] = segment_summary['avg_ltv'].apply(lambda x: f"${x:,.2f}")
    formatted_summary['LTV Rank'] = segment_summary['ltv_rank'].astype(int)
    formatted_summary['Churn Rate'] = segment_summary['churn_rate'].apply(lambda x: f"{x:.1%}")
    formatted_summary['Churn Rank'] = segment_summary['churn_rank'].astype(int)
    formatted_summary['Avg Tickets'] = segment_summary['avg_tickets'].apply(lambda x: f"{x:.1f}")
    formatted_summary['Avg Retention (Days)'] = segment_summary['avg_retention'].apply(lambda x: f"{x:.0f}")
    
    print(formatted_summary)

    # Task 3: Visual Comparison
    print("\n--- Task 3: Visual Comparison ---")
    plt.figure(figsize=(10, 6))
    
    # Normalize metrics for heatmap visibility (since LTV is on a different scale than churn)
    # But print the actual raw values in the annotations
    metrics_to_plot = segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention']]
    normalized_metrics = (metrics_to_plot - metrics_to_plot.min()) / (metrics_to_plot.max() - metrics_to_plot.min())
    
    # Let's format annotations manually to display original values
    annot_labels = segment_metrics.copy()
    annot_labels['avg_ltv'] = annot_labels['avg_ltv'].apply(lambda x: f"${x:,.0f}")
    annot_labels['churn_rate'] = annot_labels['churn_rate'].apply(lambda x: f"{x:.1%}")
    annot_labels['avg_tickets'] = annot_labels['avg_tickets'].apply(lambda x: f"{x:.1f}")
    annot_labels['avg_retention'] = annot_labels['avg_retention'].apply(lambda x: f"{x:.0f}d")
    
    sns.heatmap(
        normalized_metrics,
        annot=annot_labels[['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention']].values,
        fmt='',
        cmap='RdYlGn_r',  # Red is bad (high churn, tickets), Green is good (high ltv, retention)
        cbar=False,
        linewidths=0.5
    )
    plt.title('Customer Segment Performance Comparison Heatmap')
    plt.ylabel('Customer Segment')
    plt.xlabel('Metrics')
    plt.tight_layout()
    plt.savefig('segment_heatmap.png', dpi=300)
    plt.savefig('output/segment_heatmap.png', dpi=300)
    plt.close()
    print("Saved heatmap to segment_heatmap.png and output/segment_heatmap.png")

    # Task 4: Top and Bottom Performer Analysis
    print("\n--- Task 4: Top and Bottom Performer Analysis ---")
    top_segment = segment_metrics['avg_ltv'].idxmax()
    top_value = segment_metrics.loc[top_segment, 'avg_ltv']
    high_churn = segment_metrics['churn_rate'].idxmax()
    best_retention = segment_metrics['avg_retention'].idxmax()

    insights = f"""
HIGHEST VALUE SEGMENT: {top_segment} = ${top_value:,.2f} Average LTV
HIGHEST CHURN SEGMENT: {high_churn} = {segment_metrics.loc[high_churn, 'churn_rate']:.1%} Churn Rate
BEST RETENTION SEGMENT: {best_retention} = {segment_metrics.loc[best_retention, 'avg_retention']:.0f} Days Avg Retention
"""
    print(insights)

    # Task 5: Business-Facing Insights
    print("\n--- Task 5: Business-Facing Insights ---")
    
    # Calculate percentage contributions
    base_sizes = segment_metrics['count'] / segment_metrics['count'].sum() * 100
    
    business_summary = f"""
SEGMENT STRATEGY SUMMARY:

Enterprise ({base_sizes.loc['Enterprise']:.0f}% of base, ${segment_metrics.loc['Enterprise', 'avg_ltv']:,.0f} LTV, {segment_metrics.loc['Enterprise', 'churn_rate']:.1%} churn):
- Highest value, lowest churn. Excellent health with very long retention times.
- Action: Maintain premium high-touch support and expand account penetration through upsells.

SMB ({base_sizes.loc['SMB']:.0f}% of base, ${segment_metrics.loc['SMB', 'avg_ltv']:,.0f} LTV, {segment_metrics.loc['SMB', 'churn_rate']:.1%} churn):
- Middle value, high churn risk. Requires immediate retention focus.
- Action: Improve onboarding experience, streamline support tickets handling, and offer flexible billing tiers.

Startup ({base_sizes.loc['Startup']:.0f}% of base, ${segment_metrics.loc['Startup', 'avg_ltv']:,.0f} LTV, {segment_metrics.loc['Startup', 'churn_rate']:.1%} churn):
- Lowest value, moderate churn. High volume customer segment.
- Action: Provide self-service onboarding, tutorials, and automated educational emails.
"""
    print(business_summary)

    # Save outputs
    with open('output/segment_insights_report.txt', 'w', encoding='utf-8') as f:
        f.write(business_summary)
    
    segment_metrics.to_csv('output/segment_metrics.csv')
    print("Saved segment metrics csv and business summary report to output/")

if __name__ == '__main__':
    main()
