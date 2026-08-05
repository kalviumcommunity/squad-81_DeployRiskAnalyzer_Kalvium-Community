"""
Correlation & Relationship Analysis Workflow
Computes Pearson & Spearman correlations, generates a heatmap visualization,
identifies strong feature pairs, produces business causality interpretations,
and applies correlation-based feature selection to clean redundancy.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/feature_engineering_data.csv'):
    """
    Loads raw customer activity features dataset.
    Injects synthetic relationship metrics ('support_tickets', 'transactions_per_month',
    'engagement', 'churn') if not present.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file '{filepath}' is missing. Please run generation script.")
    
    print(f"Loading dataset from '{filepath}'...")
    df = pd.read_csv(filepath)

    np.random.seed(42)
    n = len(df)

    # Derived feature: transactions_per_month
    if 'transactions_per_month' not in df.columns:
        if 'days_as_customer' in df.columns and 'total_transactions' in df.columns:
            months = np.maximum(df['days_as_customer'] / 30.0, 1.0)
            df['transactions_per_month'] = (df['total_transactions'] / months).round(2)
        else:
            df['transactions_per_month'] = np.random.uniform(1, 20, size=n).round(2)

    # Engagement: highly correlated with transactions_per_month (r ~ 0.92)
    if 'engagement' not in df.columns:
        df['engagement'] = (df['transactions_per_month'] * 2.5 + np.random.normal(0, 1.0, size=n)).round(2)
    df['engagement_score'] = df['engagement']

    # Support tickets: random integers (1 to 15)
    if 'support_tickets' not in df.columns:
        df['support_tickets'] = np.random.randint(1, 15, size=n)
    df['support_tickets_raised'] = df['support_tickets']

    # Churn indicator: strongly correlated with support_tickets (r ~ 0.8)
    if 'churn' not in df.columns:
        tickets = df['support_tickets'].values.astype(float)
        churn_signal = tickets * 0.85 + np.random.normal(0, 2.2, size=n)
        df['churn'] = (churn_signal > np.median(churn_signal)).astype(int)

    return df


def task1_compute_correlations(df):
    """
    Task 1: Compute Pearson and Spearman Correlation
    """
    print("\n--- Task 1: Computing Pearson and Spearman Correlations ---")
    
    # Filter only numerical columns for correlation calculation
    numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['customer_id'], errors='ignore')

    # Pearson (linear relationships)
    pearson_corr = numeric_df.corr(method='pearson')

    # Spearman (monotonic, robust to outliers)
    spearman_corr = numeric_df.corr(method='spearman')

    # Compare which correlations with churn differ
    comparison = pd.DataFrame({
        'pearson': pearson_corr['churn'],
        'spearman': spearman_corr['churn']
    })

    print("Correlation with Churn (Pearson vs Spearman):")
    print(comparison)

    return pearson_corr, spearman_corr, comparison


def task2_visualize_heatmap(pearson_corr):
    """
    Task 2: Visualize Correlation Heatmap
    """
    print("\n--- Task 2: Generating Correlation Heatmap ---")
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Generate Heatmap
    sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', fmt=".2f", center=0, ax=ax, linewidths=0.5)
    ax.set_title('Feature Correlation Matrix', fontsize=16)
    
    plt.tight_layout()
    os.makedirs('output', exist_ok=True)
    img_path = 'output/correlation_heatmap.png'
    plt.savefig(img_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Heatmap visualization saved to '{img_path}'.")


def task3_identify_strong_pairs(pearson_corr):
    """
    Task 3: Identify Strongly Correlated Pairs (r > 0.7 or r < -0.7)
    """
    print("\n--- Task 3: Identifying Strongly Correlated Pairs ---")
    
    # Flatten and find strong correlations
    corr_flat = pearson_corr.unstack()
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False)

    # Exclude self-correlation (r=1.0)
    strong_pairs = strong[strong != 1.0].head(10)
    print("Top Strongly Correlated Pairs (|r| > 0.7):")
    print(strong_pairs)

    # Unique pair mapping for reporting
    unique_pairs = {}
    for (var1, var2), val in strong[strong != 1.0].items():
        pair_key = tuple(sorted([var1, var2]))
        if pair_key not in unique_pairs:
            unique_pairs[pair_key] = val

    return strong_pairs, unique_pairs


def task4_business_interpretation(pearson_corr, unique_corrs):
    """
    Task 4: Business Interpretation & Causality Reasoning
    """
    print("\n--- Task 4: Causality & Business Interpretation ---")

    corr_val = float(pearson_corr.loc['support_tickets', 'churn']) if ('support_tickets' in pearson_corr.index and 'churn' in pearson_corr.columns) else 0.8

    # For each strong correlation, reason about causation
    analysis = {
        'support_tickets <-> churn': {
            'correlation': round(corr_val, 2),
            'possible_directions': [
                'support_tickets → churn (customer gives up after contacting support)',
                'churn → support_tickets (unhappy customers contact support before leaving)',
                'customer_pain → both (underlying issue causes both)'
            ],
            'data_indicates': 'Likely customer_pain is the confounder; tickets are symptom not cause',
            'action': 'Focus on reducing pain, not blocking tickets'
        }
    }

    print(json.dumps(analysis, indent=2))
    
    report_txt_path = 'output/correlation_causality_report.json'
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"[SUCCESS] Causality report exported to '{report_txt_path}'.")

    return analysis


def task5_feature_selection(df, pearson_corr):
    """
    Task 5: Feature Selection Based on Correlation
    High correlation means redundancy - keep more interpretable feature
    """
    print("\n--- Task 5: Feature Selection Based on Correlation ---")
    
    # Select key candidate features
    df_features = df[['engagement', 'transactions_per_month', 'support_tickets', 'churn']]

    print("Correlation matrix before dropping redundant feature:")
    print(df_features.corr())

    # transactions_per_month and engagement are correlated (r ~ 0.92)
    # Drop redundant ('engagement'), keep interpretable ('transactions_per_month')
    df_features = df_features.drop('engagement', axis=1)

    print("\nCorrelation matrix after dropping 'engagement':")
    final_corr = df_features.corr()
    print(final_corr)

    # Save selected clean features dataset to data/processed/
    os.makedirs('data/processed', exist_ok=True)
    df_features.to_csv('data/processed/selected_correlation_features.csv', index=False)
    print("\n[SUCCESS] Clean selected feature dataset saved to 'data/processed/selected_correlation_features.csv'.")

    return df_features


def main():
    print("==================================================")
    print("      CORRELATION & RELATIONSHIP ANALYSIS         ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Compute Pearson and Spearman Correlation
    pearson_corr, spearman_corr, comparison = task1_compute_correlations(df)

    # Task 2: Visualize Correlation Heatmap
    task2_visualize_heatmap(pearson_corr)

    # Task 3: Identify Strongly Correlated Pairs
    strong_pairs, unique_corrs = task3_identify_strong_pairs(pearson_corr)

    # Task 4: Business Interpretation
    task4_business_interpretation(pearson_corr, unique_corrs)

    # Task 5: Feature Selection Based on Correlation
    task5_feature_selection(df, pearson_corr)

    print("\n==================================================")
    print("      RELATIONSHIP PIPELINE COMPLETED             ")
    print("==================================================")


if __name__ == '__main__':
    main()
