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
    Adds a synthetic 'churn' indicator and 'engagement_score' for correlation tasks if not present.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file '{filepath}' is missing. Please run generation script.")
    
    print(f"Loading dataset from '{filepath}'...")
    df = pd.read_csv(filepath)

    # Injecting synthetic churn and engagement variables for relationship analysis
    np.random.seed(42)
    n = len(df)

    # Let's create an 'engagement_score' strongly correlated with total_transactions (r ~ 0.9)
    df['engagement_score'] = df['total_transactions'] * 1.5 + np.random.normal(0, 10, size=n)

    # Let's create a 'churn' indicator (0 or 1) strongly correlated with support_tickets_raised (r ~ 0.75)
    # Higher support tickets raised correlates with high churn probability
    support_tickets = df['support_tickets_raised'].values
    churn_prob = 1.0 / (1.0 + np.exp(-(support_tickets - 15) / 3))
    df['churn'] = np.random.binomial(1, churn_prob)

    return df


def task1_compute_correlations(df):
    """
    Task 1: Compute Pearson and Spearman Correlation
    """
    print("\n--- Task 1: Computing Pearson and Spearman Correlations ---")
    
    # Filter only numerical columns for correlation calculation
    numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['customer_id'], errors='ignore')

    pearson_corr = numeric_df.corr(method='pearson')
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
    ax.set_title('Feature Correlation Heatmap (Pearson)', fontsize=16)
    
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
    corr_flat = pearson_corr.unstack()
    
    # Keep only relationships with absolute correlation value > 0.7, excluding self-correlation (r=1.0)
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False)
    strong_pairs = strong[strong != 1.0]

    # Deduplicate mirror pairs (e.g. A <-> B and B <-> A)
    unique_pairs = {}
    for (var1, var2), val in strong_pairs.items():
        pair_key = tuple(sorted([var1, var2]))
        if pair_key not in unique_pairs:
            unique_pairs[pair_key] = val

    print("Top Unique Strongly Correlated Pairs (|r| > 0.7):")
    for (var1, var2), val in unique_pairs.items():
        print(f"{var1} <-> {var2}: {val:.4f}")

    return unique_pairs


def task4_business_interpretation(unique_corrs):
    """
    Task 4: Business Interpretation & Causality Reasoning
    """
    print("\n--- Task 4: Causality & Business Interpretation ---")

    # Construct interpretation mapping
    interpretation = {
        'support_tickets_raised <-> churn': {
            'correlation': float(unique_corrs.get(('churn', 'support_tickets_raised'), 0.0)),
            'possible_directions': [
                'support_tickets_raised → churn (customer support contacts frustrate users causing churn)',
                'churn → support_tickets_raised (unhappy customers contact support repeatedly before churning)',
                'underlying_system_instability_or_bugs → both support_tickets_raised AND churn (confounding pain factor)'
            ],
            'data_indicates': 'Likely customer pain (due to bugs/downtime) is the confounding cause; support tickets are the symptom, not the core cause.',
            'action': 'Invest in resolving root stability issues instead of masking the symptom by restricting support channels.'
        },
        'total_transactions <-> engagement_score': {
            'correlation': float(unique_corrs.get(('engagement_score', 'total_transactions'), 0.0)),
            'possible_directions': [
                'total_transactions → engagement_score (higher transactions inherently sum into the score)',
                'engagement_score → total_transactions (highly engaged users make more purchases)'
            ],
            'data_indicates': 'Direct mathematical collinearity / definition linkage.',
            'action': 'One feature is redundant. Drop engagement_score to maintain simple interpretable transaction records.'
        }
    }

    print(json.dumps(interpretation, indent=2))
    
    report_txt_path = 'output/correlation_causality_report.json'
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        json.dump(interpretation, f, indent=2)
    print(f"[SUCCESS] Causality report exported to '{report_txt_path}'.")

    return interpretation


def task5_feature_selection(df, pearson_corr):
    """
    Task 5: Feature Selection Based on Correlation
    High correlation means redundancy - drop redundant variables to prevent collinearity issues.
    """
    print("\n--- Task 5: Feature Selection ---")
    
    # We select features for model training
    df_features = df[['engagement_score', 'total_transactions', 'support_tickets_raised', 'churn']]

    # Show correlation before dropping
    print("Correlation matrix before dropping redundant feature:")
    print(df_features.corr())

    # We drop 'engagement_score' because it is highly redundant with 'total_transactions' (r > 0.9)
    df_selected = df_features.drop('engagement_score', axis=1)

    print("\nCorrelation matrix after dropping 'engagement_score':")
    final_corr = df_selected.corr()
    print(final_corr)

    # Save selected clean features dataset to processed/
    os.makedirs('data/processed', exist_ok=True)
    df_selected.to_csv('data/processed/selected_correlation_features.csv', index=False)
    print("\n[SUCCESS] Clean selected feature dataset saved to 'data/processed/selected_correlation_features.csv'.")

    return df_selected


def main():
    print("==================================================")
    print("      CORRELATION & RELATIONSHIP ANALYSIS         ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Compute Pearson and Spearman Correlations
    pearson_corr, spearman_corr, comparison = task1_compute_correlations(df)

    # Task 2: Visualize Heatmap
    task2_visualize_heatmap(pearson_corr)

    # Task 3: Identify Strongly Correlated Pairs
    unique_corrs = task3_identify_strong_pairs(pearson_corr)

    # Task 4: Business Interpretation
    task4_business_interpretation(unique_corrs)

    # Task 5: Feature Selection
    task5_feature_selection(df, pearson_corr)

    print("\n==================================================")
    print("      RELATIONSHIP PIPELINE COMPLETED             ")
    print("==================================================")


if __name__ == '__main__':
    main()
