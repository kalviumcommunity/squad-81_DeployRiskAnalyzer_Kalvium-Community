"""
Feature Engineering & Derived Business Columns Pipeline
Transforms raw customer activity columns into high-signal business features,
including ratios, equal-width binning, quantile tiering, and composite RFM scoring.

Tasks Implemented:
1. Compute Ratio Features (transactions_per_month, avg_spend_per_transaction, lifetime_value_per_month)
2. Binning with Equal-Width Bins (engagement_tier: low, medium, high)
3. Binning with Quantiles (spend_quartile: Q1, Q2, Q3, Q4)
4. Composite Score (RFM score combining Recency, Frequency, and Monetary ranks 3 to 15)
5. Feature Validation (distribution checks, range validation, zero NaN guarantee)
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/feature_engineering_data.csv'):
    """Loads raw dataset or generates a synthetic customer activity dataset if missing."""
    if os.path.exists(filepath):
        print(f"Loading dataset from '{filepath}'...")
        df = pd.read_csv(filepath)
    else:
        print(f"File '{filepath}' not found. Generating synthetic dataset for feature engineering...")
        np.random.seed(42)
        n = 500

        data = {
            'customer_id': np.arange(1001, 1001 + n),
            'days_as_customer': np.random.randint(30, 1800, size=n),
            'total_transactions': np.random.randint(1, 200, size=n),
            'total_spent': np.round(np.random.uniform(50.0, 15000.0, size=n), 2),
            'days_since_last_purchase': np.random.randint(1, 365, size=n)
        }
        df = pd.DataFrame(data)
        # Ensure purchase_count equals total_transactions for consistency
        df['purchase_count'] = df['total_transactions']

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Synthetic dataset saved to '{filepath}'.")

    # Ensure purchase_count exists
    if 'purchase_count' not in df.columns:
        df['purchase_count'] = df['total_transactions']

    return df


def task1_compute_ratio_features(df):
    """Task 1: Compute Ratio Features."""
    print("\n--- Task 1: Compute Ratio Features ---")
    # Prevent division by zero if days_as_customer is 0
    days_in_months = np.maximum(df['days_as_customer'] / 30.0, 1 / 30.0)
    tx_count = np.maximum(df['total_transactions'], 1)

    df['transactions_per_month'] = df['total_transactions'] / days_in_months
    df['avg_spend_per_transaction'] = df['total_spent'] / tx_count
    df['lifetime_value_per_month'] = df['total_spent'] / days_in_months

    print("Ratio Features Summary Statistics:")
    print(df[['transactions_per_month', 'avg_spend_per_transaction', 'lifetime_value_per_month']].describe())
    return df


def task2_equal_width_binning(df):
    """Task 2: Binning with Equal-Width Bins."""
    print("\n--- Task 2: Binning with Equal-Width Bins ---")
    df['engagement_tier'] = pd.cut(
        df['transactions_per_month'],
        bins=[0, 2, 10, float('inf')],
        labels=['low', 'medium', 'high'],
        include_lowest=True
    )

    print("Engagement Tier Distribution:")
    print(df['engagement_tier'].value_counts())
    return df


def task3_quantile_binning(df):
    """Task 3: Binning with Quantiles."""
    print("\n--- Task 3: Binning with Quantiles ---")
    df['spend_quartile'] = pd.qcut(
        df['total_spent'],
        q=4,
        labels=['Q1', 'Q2', 'Q3', 'Q4']
    )

    print("Spend Quartile Distribution:")
    print(df['spend_quartile'].value_counts())
    return df


def task4_composite_score(df):
    """Task 4: Composite Score (RFM Ranking)."""
    print("\n--- Task 4: Composite RFM Score ---")
    # Recency: lower days_since_last_purchase is better -> ranks 5 to 1
    df['recency_score'] = pd.qcut(df['days_since_last_purchase'], q=5, labels=[5, 4, 3, 2, 1])
    # Frequency: higher purchase_count is better -> ranks 1 to 5
    df['frequency_score'] = pd.qcut(df['purchase_count'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    # Monetary: higher total_spent is better -> ranks 1 to 5
    df['monetary_score'] = pd.qcut(df['total_spent'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])

    df['rfm_score'] = (
        df['recency_score'].astype(int) +
        df['frequency_score'].astype(int) +
        df['monetary_score'].astype(int)
    )

    print("RFM Score Summary:")
    print(f"Min RFM score: {df['rfm_score'].min()}, Max RFM score: {df['rfm_score'].max()}")
    print("RFM Score Distribution:")
    print(df['rfm_score'].value_counts().sort_index())
    return df


def task5_feature_validation(df):
    """Task 5: Feature Validation."""
    print("\n--- Task 5: Feature Validation ---")
    print(f"Engagement tier distribution:\n{df['engagement_tier'].value_counts()}")
    print(f"\nRFM score range: {df['rfm_score'].min()}-{df['rfm_score'].max()}")

    missing_counts = df[['engagement_tier', 'spend_quartile', 'rfm_score']].isna().sum()
    print(f"\nMissing values:\n{missing_counts}")

    if missing_counts.sum() == 0:
        print("[SUCCESS] All engineered features are 100% complete with no NaNs.")
    else:
        print("[WARNING] Found missing values in engineered features.")

    # Save engineered dataset to data/processed
    os.makedirs('data/processed', exist_ok=True)
    processed_filepath = 'data/processed/engineered_customer_features.csv'
    df.to_csv(processed_filepath, index=False)
    print(f"\n[SUCCESS] Engineered features dataset saved to '{processed_filepath}'.")

    # Generate feature summary metrics report in output
    os.makedirs('output', exist_ok=True)
    summary_report = {
        'total_records': len(df),
        'engineered_features': [
            'transactions_per_month', 'avg_spend_per_transaction',
            'lifetime_value_per_month', 'engagement_tier',
            'spend_quartile', 'rfm_score'
        ],
        'rfm_min': int(df['rfm_score'].min()),
        'rfm_max': int(df['rfm_score'].max()),
        'missing_values_total': int(missing_counts.sum())
    }
    summary_path = 'output/feature_engineering_report.json'
    import json
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2)
    print(f"[SUCCESS] Feature summary report saved to '{summary_path}'.")

    return df, summary_report


def main():
    print("==================================================")
    print("  FEATURE ENGINEERING & DERIVED BUSINESS COLUMNS  ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Compute Ratio Features
    df = task1_compute_ratio_features(df)

    # Task 2: Binning with Equal-Width Bins
    df = task2_equal_width_binning(df)

    # Task 3: Binning with Quantiles
    df = task3_quantile_binning(df)

    # Task 4: Composite Score
    df = task4_composite_score(df)

    # Task 5: Feature Validation
    df, summary_report = task5_feature_validation(df)


if __name__ == '__main__':
    main()
