"""
Distribution Analysis for Business Trends
Implements plotting, computing skewness and kurtosis, checking for bimodality, 
segment comparison, and generation of a business interpretation report.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/customer_revenue.csv'):
    """Loads customer revenue dataset."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file '{filepath}' is missing. Please run scripts/vectorized_computation.py first.")
    print(f"Loading dataset from '{filepath}'...")
    return pd.read_csv(filepath)


def task1_distribution_plots(df):
    """
    Task 1: Distribution Plots (Histogram & KDE)
    """
    print("\n--- Task 1: Generating Distribution Plots ---")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(df['revenue'], bins=50, color='royalblue', edgecolor='black', alpha=0.8)
    axes[0].set_title('Revenue Distribution (Histogram)')
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_ylabel('Count')
    axes[0].grid(True, linestyle='--', alpha=0.6)

    # KDE (Smoothed Density)
    df['revenue'].plot(kind='density', ax=axes[1], color='crimson', linewidth=2)
    axes[1].set_title('Revenue Distribution (KDE)')
    axes[1].set_xlabel('Revenue ($)')
    axes[1].set_ylabel('Density')
    axes[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    os.makedirs('output', exist_ok=True)
    img_path = 'output/revenue_distribution.png'
    plt.savefig(img_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Distribution plots saved to '{img_path}'.")


def task2_skewness_kurtosis(df):
    """
    Task 2: Compute Skewness and Kurtosis
    """
    print("\n--- Task 2: Computing Skewness and Kurtosis ---")
    skewness = stats.skew(df['revenue'])
    kurtosis = stats.kurtosis(df['revenue'])

    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}")

    if abs(skewness) > 1:
        print("Highly skewed - use median not mean for central tendency.")
    else:
        print("Moderately skewed or symmetric distribution.")

    if kurtosis > 3:
        print("Heavy tails - expect presence of extreme values/outliers.")
    else:
        print("Light or normal tails.")

    return skewness, kurtosis


def task3_identify_abnormal_patterns(df):
    """
    Task 3: Identify Abnormal Patterns (Bimodality / Percentiles Check)
    """
    print("\n--- Task 3: Identifying Abnormal Patterns ---")
    summary = df['revenue'].describe()
    print("Descriptive Statistics:")
    print(summary)

    percentiles_list = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    percentiles = df['revenue'].quantile(percentiles_list)
    print("\nPercentiles:")
    for p, val in zip(percentiles_list, percentiles):
        print(f"{int(p*100)}th Percentile: ${val:.2f}")

    gap_75_90 = percentiles[0.9] - percentiles[0.75]
    print(f"\nGap between 75th and 90th percentile: ${gap_75_90:.2f}")
    if gap_75_90 > 5 * percentiles[0.5]:
        print("[ALERT] Large gap between 75th and 90th percentile suggests a bimodal or heavily right-tailed segmentation.")
    
    return percentiles.to_dict()


def task4_compare_segments(df):
    """
    Task 4: Compare Segment Distributions
    """
    print("\n--- Task 4: Comparing Segment Distributions ---")
    q75 = df['revenue'].quantile(0.75)
    q25 = df['revenue'].quantile(0.25)

    high_value = df[df['revenue'] > q75]
    low_value = df[df['revenue'] < q25]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # High-Value Histogram
    axes[0].hist(high_value['revenue'], bins=30, color='darkorange', edgecolor='black', alpha=0.7)
    axes[0].set_title('Revenue: High-Value Customers (Top 25%)')
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_ylabel('Count')
    axes[0].grid(True, linestyle='--', alpha=0.6)

    # Low-Value Histogram
    axes[1].hist(low_value['revenue'], bins=30, color='forestgreen', edgecolor='black', alpha=0.7)
    axes[1].set_title('Revenue: Low-Value Customers (Bottom 25%)')
    axes[1].set_xlabel('Revenue ($)')
    axes[1].set_ylabel('Count')
    axes[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    img_path = 'output/revenue_segment_comparison.png'
    plt.savefig(img_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Segment comparison plots saved to '{img_path}'.")

    # Compare Metrics
    metrics = {
        'high_value': {
            'mean': float(high_value['revenue'].mean()),
            'median': float(high_value['revenue'].median()),
            'count': int(len(high_value))
        },
        'low_value': {
            'mean': float(low_value['revenue'].mean()),
            'median': float(low_value['revenue'].median()),
            'count': int(len(low_value))
        }
    }

    print(f"High-value: Mean=${metrics['high_value']['mean']:.2f}, Median=${metrics['high_value']['median']:.2f} (Count: {metrics['high_value']['count']})")
    print(f"Low-value: Mean=${metrics['low_value']['mean']:.2f}, Median=${metrics['low_value']['median']:.2f} (Count: {metrics['low_value']['count']})")
    return metrics


def task5_business_interpretation(df, skewness, kurtosis, percentiles):
    """
    Task 5: Business Interpretation Report
    """
    print("\n--- Task 5: Generating Business Interpretation Report ---")
    mean_val = df['revenue'].mean()
    median_val = df['revenue'].median()
    max_val = df['revenue'].max()
    p99_val = percentiles[0.99]

    interpretation = f"""
Revenue Distribution Analysis Report:

Skewness: {skewness:.2f} → {"Highly right-skewed" if skewness > 1 else "Moderate"}
Mean: ${mean_val:.2f}
Median: ${median_val:.2f}
Interpretation: {'Most customers are small; few are huge enterprise accounts.' if skewness > 1 else 'Balanced distribution.'}

Kurtosis: {kurtosis:.2f} → {"Fat tails (extreme outliers present)" if kurtosis > 3 else "Normal tails"}
Max: ${max_val:.2f}
Top 1% Threshold: ${p99_val:.2f}

Business Action: {'Segment into distinct small business and enterprise tiers to target marketing, product, and sales strategies differently.' if skewness > 1 else 'Apply uniform business strategy.'}
"""
    print(interpretation)

    # Save interpretation to file
    os.makedirs('output', exist_ok=True)
    report_txt_path = 'output/revenue_distribution_interpretation.txt'
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        f.write(interpretation)
    print(f"[SUCCESS] Written interpretation text report to '{report_txt_path}'.")

    # JSON output file for programmatic ingest
    report_json = {
        'skewness': float(skewness),
        'kurtosis': float(kurtosis),
        'mean': float(mean_val),
        'median': float(median_val),
        'max': float(max_val),
        'p99': float(p99_val),
        'recommendation': 'Segment into small/enterprise' if skewness > 1 else 'Uniform Strategy'
    }
    report_json_path = 'output/revenue_distribution_metrics.json'
    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump(report_json, f, indent=2)
    print(f"[SUCCESS] Written metrics json report to '{report_json_path}'.")

    return report_json


def main():
    print("==================================================")
    print("        DISTRIBUTION ANALYSIS WORKFLOW            ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Distribution Plots
    task1_distribution_plots(df)

    # Task 2: Compute Skewness and Kurtosis
    skewness, kurtosis = task2_skewness_kurtosis(df)

    # Task 3: Identify Abnormal Patterns
    percentiles = task3_identify_abnormal_patterns(df)

    # Task 4: Compare Segment Distributions
    task4_compare_segments(df)

    # Task 5: Business Interpretation
    task5_business_interpretation(df, skewness, kurtosis, percentiles)

    print("\n==================================================")
    print("        ANALYSIS PIPELINE COMPLETED               ")
    print("==================================================")


if __name__ == '__main__':
    main()
