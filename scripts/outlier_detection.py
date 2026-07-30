"""
Statistical Outlier Detection Pipeline
Detects outliers using Z-score and Interquartile Range (IQR) methods,
applies capping/flagging strategies, and documents all decisions in an auditable cleaning log.

Tasks Implemented:
1. Z-Score Outlier Detection (scipy.stats.zscore > 3)
2. IQR Outlier Detection (Q1 - 1.5*IQR to Q3 + 1.5*IQR)
3. Cap Outliers at Boundaries (.clip(lower, upper))
4. Flag Outliers with Binary Column (combined boolean flag)
5. Create Cleaning Log (export audit log to output/cleaning_log.csv)
"""

import sys
import os
import pandas as pd
import numpy as np
from scipy import stats

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/customer_revenue.csv'):
    """Loads customer dataset or generates a synthetic dataset if missing."""
    if os.path.exists(filepath):
        print(f"Loading raw dataset from '{filepath}'...")
        df = pd.read_csv(filepath)
    else:
        print(f"File '{filepath}' not found. Generating synthetic dataset with outliers...")
        data = {
            'customer_id': range(101, 121),
            'age': [28, 34, 45, 22, 52, 31, 152, 29, 40, 36, 58, 25, 48, 33, 41, 27, 50, 30, 39, 63],
            'revenue': [450.0, 1200.5, 850.0, 310.0, 2400.0, 650.0, 1800.0, 500000.0, 920.0, 1100.0,
                        3100.0, 520.0, 1650.0, 780.0, 1350.0, 490.0, 2800.0, 880.0, 1420.0, 3300.0],
            'transactions_count': [5, 12, 8, 3, 20, 6, 15, 2, 9, 11, 25, 4, 14, 7, 13, 4, 22, 8, 16, 28],
            'signup_date': ["2024-01-15", "2024-02-10", "2024-02-18", "2024-03-01", "2024-03-15",
                            "2024-03-20", "2024-04-02", "2024-04-10", "2024-04-12", "2024-04-18",
                            "2024-04-25", "2024-05-01", "2024-05-10", "2024-05-15", "2024-05-20",
                            "2024-06-01", "2024-06-08", "2024-06-14", "2024-06-21", "2024-06-30"]
        }
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
    return df


def detect_zscore_outliers(df, col='revenue'):
    """Task 1: Detect outliers beyond ±3 standard deviations from mean."""
    print("\n--- Task 1: Z-Score Outlier Detection ---")
    df[f'{col}_zscore'] = np.abs(stats.zscore(df[col]))
    z_outliers = df[df[f'{col}_zscore'] > 3]

    print(f"Z-score outliers detected: {len(z_outliers)}")
    if not z_outliers.empty:
        print(f"Outlier rows ({col}_zscore > 3):")
        print(z_outliers[['customer_id', col, f'{col}_zscore']])
    return df, z_outliers


def detect_iqr_outliers(df, col='revenue'):
    """Task 2: Detect outliers beyond 1.5 × IQR from quartiles."""
    print("\n--- Task 2: IQR Outlier Detection ---")
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    df['is_outlier_iqr'] = (df[col] < lower) | (df[col] > upper)
    iqr_outliers = df[df['is_outlier_iqr']]

    print(f"Q1 (25th percentile): {Q1:.2f}")
    print(f"Q3 (75th percentile): {Q3:.2f}")
    print(f"IQR: {IQR:.2f}")
    print(f"Lower Bound: {lower:.2f}")
    print(f"Upper Bound: {upper:.2f}")
    print(f"IQR outliers detected: {len(iqr_outliers)}")
    if not iqr_outliers.empty:
        print(f"Outlier rows ({col} < {lower:.2f} or > {upper:.2f}):")
        print(iqr_outliers[['customer_id', col, 'is_outlier_iqr']])
    return df, lower, upper, iqr_outliers


def cap_outliers(df, lower, upper, col='revenue'):
    """Task 3: Apply capping strategy - replace extreme values with boundary values."""
    print("\n--- Task 3: Cap Outliers at Boundaries ---")
    df[f'{col}_capped'] = df[col].clip(lower=lower, upper=upper)

    print(f"Before capping: min={df[col].min():.2f}, max={df[col].max():.2f}")
    print(f"After capping:  min={df[f'{col}_capped'].min():.2f}, max={df[f'{col}_capped'].max():.2f}")
    return df


def flag_outliers_binary(df, col='revenue'):
    """Task 4: Flag anomalies with binary column without removing data."""
    print("\n--- Task 4: Flag Outliers with Binary Column ---")
    # Combine IQR and Z-score outlier detection methods
    df['is_outlier'] = (df['is_outlier_iqr']) | (df[f'{col}_zscore'] > 3)
    df['is_outlier_binary'] = df['is_outlier'].astype(int)

    normal = df[~df['is_outlier']]
    anomalies = df[df['is_outlier']]

    print(f"Normal records: {len(normal)}")
    print(f"Anomalies detected: {len(anomalies)}")
    if not anomalies.empty:
        print("Anomaly Details:")
        print(anomalies[['customer_id', col, 'is_outlier_iqr', f'{col}_zscore', 'is_outlier_binary']])

    return df, normal, anomalies


def create_cleaning_log(df, lower, upper, col='revenue'):
    """Task 5: Document all outlier-related transformations in a cleaning log."""
    print("\n--- Task 5: Create Cleaning Log ---")
    os.makedirs('output', exist_ok=True)

    affected_count = int(df['is_outlier_iqr'].sum())
    now_ts = pd.Timestamp.now()

    cleaning_log = [{
        'column': col,
        'method': 'IQR',
        'action': 'cap',
        'threshold_lower': lower,
        'threshold_upper': upper,
        'affected_rows': affected_count,
        'date': now_ts
    }, {
        'column': col,
        'method': 'Z-Score',
        'action': 'flag',
        'threshold_lower': -3.0,
        'threshold_upper': 3.0,
        'affected_rows': int((df[f'{col}_zscore'] > 3).sum()),
        'date': now_ts
    }]

    # Also log age outlier handling if present
    if 'age' in df.columns:
        age_Q1 = df['age'].quantile(0.25)
        age_Q3 = df['age'].quantile(0.75)
        age_IQR = age_Q3 - age_Q1
        age_lower = max(0, age_Q1 - 1.5 * age_IQR)
        age_upper = min(120, age_Q3 + 1.5 * age_IQR)
        age_affected = int(((df['age'] < age_lower) | (df['age'] > age_upper)).sum())
        
        cleaning_log.append({
            'column': 'age',
            'method': 'IQR',
            'action': 'cap',
            'threshold_lower': age_lower,
            'threshold_upper': age_upper,
            'affected_rows': age_affected,
            'date': now_ts
        })

    log_df = pd.DataFrame(cleaning_log)
    log_file_path = 'output/cleaning_log.csv'
    log_df.to_csv(log_file_path, index=False)

    print(f"Cleaning log successfully generated and saved to '{log_file_path}':")
    print(log_df.to_string(index=False))
    return log_df


def main():
    print("==================================================")
    print("   STATISTICAL OUTLIER DETECTION PIPELINE")
    print("==================================================")

    # Load dataset
    df = load_dataset()
    print("\n--- Initial Raw Dataset Preview ---")
    print(df.head(10))

    # Task 1: Z-Score Outlier Detection
    df, z_outliers = detect_zscore_outliers(df, col='revenue')

    # Task 2: IQR Outlier Detection
    df, lower, upper, iqr_outliers = detect_iqr_outliers(df, col='revenue')

    # Task 3: Cap Outliers at Boundaries
    df = cap_outliers(df, lower=lower, upper=upper, col='revenue')
    if 'age' in df.columns:
        age_Q1 = df['age'].quantile(0.25)
        age_Q3 = df['age'].quantile(0.75)
        age_IQR = age_Q3 - age_Q1
        df['age_capped'] = df['age'].clip(lower=max(0, age_Q1 - 1.5 * age_IQR), upper=min(100, age_Q3 + 1.5 * age_IQR))

    # Task 4: Flag Outliers with Binary Column
    df, normal, anomalies = flag_outliers_binary(df, col='revenue')

    # Task 5: Create Cleaning Log
    log_df = create_cleaning_log(df, lower=lower, upper=upper, col='revenue')

    # Save cleaned / processed dataset to data/processed
    os.makedirs('data/processed', exist_ok=True)
    processed_filepath = 'data/processed/cleaned_revenue_data.csv'
    df.to_csv(processed_filepath, index=False)
    print(f"\n[SUCCESS] Processed dataset saved to '{processed_filepath}'.")


if __name__ == '__main__':
    main()
