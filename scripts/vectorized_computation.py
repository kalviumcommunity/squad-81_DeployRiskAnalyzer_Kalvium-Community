"""
NumPy Vectorised Computation Workflow
Implements vectorized NumPy operations for normalization, scoring, ranking, timing comparison,
and DataFrame integration to eliminate slow Python loops on analytical workloads.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/customer_revenue.csv'):
    """
    Loads customer revenue dataset or generates a realistic synthetic dataset if missing.
    """
    if os.path.exists(filepath):
        print(f"Loading dataset from '{filepath}'...")
        df = pd.read_csv(filepath)
    else:
        print(f"File '{filepath}' not found. Generating dataset at '{filepath}'...")
        np.random.seed(42)
        n = 100000
        data = {
            'customer_id': np.arange(1001, 1001 + n),
            'age': np.random.randint(18, 80, size=n),
            'revenue': np.round(np.random.exponential(scale=1000.0, size=n) + 10.0, 2),
            'transactions_count': np.random.randint(1, 200, size=n),
            'signup_date': pd.date_range(start='2020-01-01', periods=n, freq='min').astype(str),
            'customer_segment': np.random.choice(['B2B', 'B2C', 'SMB', 'Enterprise'], size=n),
            'country': np.random.choice(['USA', 'UK', 'India', 'Germany', 'France', 'Japan', 'Canada', 'Australia', 'UAE', 'Singapore'], size=n),
            'flag_churn': np.random.choice([0, 1], size=n, p=[0.8, 0.2])
        }
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Generated synthetic dataset with {n} rows at '{filepath}'.")

    return df


def task1_min_max_normalization(df):
    """
    Task 1: Replace Loop with NumPy Vectorization (Min-Max Normalization)
    Applies formula: (arr - arr.min()) / (arr.max() - arr.min())
    """
    print("\n--- Task 1: Min-Max Normalization (NumPy Vectorized) ---")
    revenue_array = df['revenue'].values.astype(float)
    rev_min = revenue_array.min()
    rev_max = revenue_array.max()

    normalized_np = (revenue_array - rev_min) / (rev_max - rev_min)
    df['revenue_normalized'] = normalized_np

    print(f"Revenue Min: {rev_min:.2f}, Max: {rev_max:.2f}")
    print(f"Normalized Range: Min={df['revenue_normalized'].min():.4f}, Max={df['revenue_normalized'].max():.4f}")
    print(f"Sample Normalized Values:\n{df[['revenue', 'revenue_normalized']].head()}")
    return df, normalized_np


def task2_z_score_normalization(df):
    """
    Task 2: Z-Score Normalization (NumPy Vectorized)
    Applies formula: (arr - arr.mean()) / arr.std()
    """
    print("\n--- Task 2: Z-Score Normalization (NumPy Vectorized) ---")
    revenue_array = df['revenue'].values.astype(float)
    rev_mean = revenue_array.mean()
    rev_std = revenue_array.std()

    z_scores = (revenue_array - rev_mean) / rev_std
    df['revenue_zscore'] = z_scores

    print(f"Revenue Mean: {rev_mean:.2f}, Std: {rev_std:.2f}")
    print(f"Z-Score Metrics: Mean={df['revenue_zscore'].mean():.4f}, Std={df['revenue_zscore'].std():.4f}")
    print(f"Sample Z-Scores:\n{df[['revenue', 'revenue_zscore']].head()}")
    return df, z_scores


def task3_bulk_ranking(df):
    """
    Task 3: Bulk Ranking / Scoring (NumPy Vectorized)
    Ranks customers by revenue descending (Rank 1 = Highest Revenue)
    """
    print("\n--- Task 3: Bulk Ranking (NumPy Vectorized) ---")
    revenue_array = df['revenue'].values.astype(float)
    
    # argsort on -revenue_array gives indices that sort array descending
    rankings = np.argsort(-revenue_array)
    revenue_rank = np.empty_like(rankings)
    revenue_rank[rankings] = np.arange(1, len(rankings) + 1)

    df['revenue_rank'] = revenue_rank

    print("Top 5 Revenue Customers and Ranks:")
    print(df.sort_values('revenue_rank')[['customer_id', 'revenue', 'revenue_rank']].head())
    return df, revenue_rank


def task4_time_performance_comparison(df):
    """
    Task 4: Time Performance Comparison (Python Loop vs NumPy Vectorization)
    """
    print("\n--- Task 4: Time Performance Comparison ---")
    
    # 1. Benchmark simple element-wise calculation (e.g. val * 1.1)
    start = time.perf_counter()
    result_loop = []
    for val in df['revenue']:
        result_loop.append(val * 1.1)
    loop_time = time.perf_counter() - start

    start = time.perf_counter()
    result_np = df['revenue'].values * 1.1
    np_time = time.perf_counter() - start

    speedup = loop_time / np_time if np_time > 0 else 0.0

    print(f"Loop Time (1.1x multiplier): {loop_time:.6f}s")
    print(f"NumPy Time (1.1x multiplier): {np_time:.6f}s")
    print(f"Speedup: {speedup:.2f}x")

    # 2. Benchmark Min-Max Normalization loop vs numpy
    start = time.perf_counter()
    min_val = df['revenue'].min()
    max_val = df['revenue'].max()
    denom = max_val - min_val
    loop_norm = []
    for val in df['revenue']:
        loop_norm.append((val - min_val) / denom)
    loop_norm_time = time.perf_counter() - start

    start = time.perf_counter()
    rev_arr = df['revenue'].values
    np_norm = (rev_arr - rev_arr.min()) / (rev_arr.max() - rev_arr.min())
    np_norm_time = time.perf_counter() - start

    norm_speedup = loop_norm_time / np_norm_time if np_norm_time > 0 else 0.0

    print(f"Normalization Loop Time: {loop_norm_time:.6f}s")
    print(f"Normalization NumPy Time: {np_norm_time:.6f}s")
    print(f"Normalization Speedup: {norm_speedup:.2f}x")

    performance_metrics = {
        'row_count': len(df),
        'multiplier_loop_time_sec': round(loop_time, 6),
        'multiplier_numpy_time_sec': round(np_time, 6),
        'multiplier_speedup': round(speedup, 2) if speedup != float('inf') else "inf",
        'normalization_loop_time_sec': round(loop_norm_time, 6),
        'normalization_numpy_time_sec': round(np_norm_time, 6),
        'normalization_speedup': round(norm_speedup, 2) if norm_speedup != float('inf') else "inf"
    }

    return performance_metrics


def task5_integrate_and_verify(df, normalized_np, z_scores, revenue_rank):
    """
    Task 5: Integrate Results Back to DataFrame & Verify Shape / Types
    """
    print("\n--- Task 5: Integrate Back to DataFrame & Verification ---")
    df['revenue_normalized'] = normalized_np
    df['revenue_zscore'] = z_scores
    df['revenue_rank'] = revenue_rank

    print(f"Shape: {df.shape}")
    print(f"Dtypes:\n{df.dtypes}")

    # Check for missing values in new columns
    new_cols = ['revenue_normalized', 'revenue_zscore', 'revenue_rank']
    null_counts = df[new_cols].isna().sum()
    print(f"\nMissing Values Check:\n{null_counts}")
    assert null_counts.sum() == 0, "Error: NaNs found in vectorized result columns!"

    # Save processed dataframe
    os.makedirs('data/processed', exist_ok=True)
    output_csv = 'data/processed/vectorized_customer_revenue.csv'
    df.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] Vectorized results saved to '{output_csv}'.")

    # Save summary report to output/
    os.makedirs('output', exist_ok=True)
    report = {
        'dataset_rows': len(df),
        'dataset_cols': len(df.columns),
        'added_vectorized_columns': new_cols,
        'summary_statistics': {
            'revenue_normalized_min': float(df['revenue_normalized'].min()),
            'revenue_normalized_max': float(df['revenue_normalized'].max()),
            'revenue_zscore_mean': float(df['revenue_zscore'].mean()),
            'revenue_zscore_std': float(df['revenue_zscore'].std()),
            'min_rank': int(df['revenue_rank'].min()),
            'max_rank': int(df['revenue_rank'].max())
        }
    }

    report_path = 'output/vectorized_computation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"[SUCCESS] Summary report saved to '{report_path}'.")

    return df, report


def main():
    print("==================================================")
    print("  NUMPY VECTORISED COMPUTATION WORKFLOW PIPELINE  ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Min-Max Normalization
    df, normalized_np = task1_min_max_normalization(df)

    # Task 2: Z-Score Normalization
    df, z_scores = task2_z_score_normalization(df)

    # Task 3: Bulk Ranking
    df, revenue_rank = task3_bulk_ranking(df)

    # Task 4: Time Performance Comparison
    perf_metrics = task4_time_performance_comparison(df)

    # Task 5: Integration & Verification
    df, report = task5_integrate_and_verify(df, normalized_np, z_scores, revenue_rank)

    # Save perf metrics into report
    report['performance_comparison'] = perf_metrics
    with open('output/vectorized_computation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print("\n==================================================")
    print("  PIPELINE EXECUTION COMPLETED SUCCESSFULLY      ")
    print("==================================================")


if __name__ == '__main__':
    main()
