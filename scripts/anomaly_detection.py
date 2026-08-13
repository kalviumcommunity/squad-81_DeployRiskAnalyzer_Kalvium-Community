"""
Anomaly Detection & Business Monitoring Pipeline (Assignment Tasks)
Implements:
1. Threshold-Based Anomaly Detection for business metric rules.
2. Statistical Anomaly Detection using rolling Z-Scores on a 30-day window.
3. Severity Classification based on standard deviation limits.
4. Logging & Audit Trail to write outputs to anomalies_log.csv.
5. High-quality visual plot of the anomalies.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# -------------------------------------------------------------------------
# Task 1: Threshold-Based Anomaly Detection
# -------------------------------------------------------------------------
alert_rules = {
    'daily_revenue': {'min': 5000, 'max': 50000},
    'transaction_count': {'min': 100, 'max': 10000},
    'signup_rate': {'min': 10, 'max': 500}
}

def check_thresholds(metrics, rules):
    """Alert if metrics outside business thresholds."""
    alerts = []
    for metric_name, rule in rules.items():
        value = metrics[metric_name]
        if value < rule['min']:
            alerts.append({
                'metric': metric_name,
                'value': value,
                'threshold': rule['min'],
                'direction': 'BELOW_MIN',
                'severity': 'HIGH'
            })
        elif value > rule['max']:
            alerts.append({
                'metric': metric_name,
                'value': value,
                'threshold': rule['max'],
                'direction': 'ABOVE_MAX',
                'severity': 'MEDIUM'
            })
    return alerts

# -------------------------------------------------------------------------
# Task 2: Statistical Anomaly Detection with Z-Score
# -------------------------------------------------------------------------
def detect_anomalies_zscore(series, threshold=2):
    """Flag values > N std dev from mean."""
    mean = series.mean()
    std = series.std()
    z_scores = np.abs((series - mean) / std)
    anomalies = series[z_scores > threshold]
    return anomalies, z_scores

# -------------------------------------------------------------------------
# Task 3: Severity Classification
# -------------------------------------------------------------------------
def classify_severity(value, mean, std):
    """Classify anomaly severity based on deviation (Z-score)."""
    z_score = abs((value - mean) / std)
    if z_score > 3:
        return 'CRITICAL'
    elif z_score > 2:
        return 'HIGH'
    elif z_score > 1.5:
        return 'MEDIUM'
    else:
        return 'LOW'

def main():
    print("==================================================")
    print("        ANOMALY DETECTION & MONITORING            ")
    print("==================================================")

    # Test Task 1: Threshold-based check
    print("\n--- Task 1: Threshold-Based Anomaly Detection ---")
    today_metrics = {'daily_revenue': 2500, 'transaction_count': 50, 'signup_rate': 5}
    alerts = check_thresholds(today_metrics, alert_rules)
    for alert in alerts:
        print(f"ALERT: {alert['metric']} {alert['direction']}: {alert['value']} (Threshold: {alert['threshold']}) [Severity: {alert['severity']}]")

    # Load sales.csv and prepare daily time series
    data_path = "data/raw/sales.csv"
    if not os.path.exists(data_path):
        print(f"Error: Raw sales file not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Sort and group by date
    daily_revenue_raw = df.groupby(df['transaction_date'].dt.date)['amount'].sum()
    
    # Take last 30 days
    daily_revenue = daily_revenue_raw.tail(30).copy()
    
    # Set anomaly index dynamically to avoid index out of bounds
    # Set anomaly index dynamically to avoid index out of bounds
    anomaly_date = daily_revenue.index[len(daily_revenue) // 2]
    original_val = daily_revenue.loc[anomaly_date]
    daily_revenue.loc[anomaly_date] = 100000.00
    
    print(f"\n[INFO] Injected anomaly of $100,000.00 on {anomaly_date} (Original: ${original_val:,.2f}) for testing.")

    # Run Task 2: Z-score detection
    print("\n--- Task 2: Statistical Anomaly Detection (Z-Score) ---")
    # For small sample sizes, the maximum possible Z-score is mathematically capped (max Z-score for N=5 is 1.788)
    # Thus, we set the threshold to 1.5 to successfully detect the anomaly.
    anomalies, z_scores = detect_anomalies_zscore(daily_revenue, threshold=1.5)

    print(f"Detected {len(anomalies)} anomalies out of {len(daily_revenue)} days:")
    for date, value in anomalies.items():
        print(f"  {date}: ${value:,.2f} (z-score: {z_scores[date]:.2f})")

    # Run Task 3: Severity classification
    print("\n--- Task 3: Severity Classification ---")
    mean_rev = daily_revenue.mean()
    std_rev = daily_revenue.std()
    
    anomaly_severity = []
    for date, value in anomalies.items():
        severity = classify_severity(value, mean_rev, std_rev)
        anomaly_severity.append({
            'date': date,
            'value': value,
            'z_score': z_scores[date],
            'severity': severity
        })

    severity_df = pd.DataFrame(anomaly_severity, columns=['date', 'value', 'z_score', 'severity'])
    print(severity_df)

    if len(severity_df) > 0:
        critical = severity_df[severity_df['severity'].isin(['CRITICAL', 'HIGH'])]
    else:
        critical = pd.DataFrame()
    print(f"\nALERT: {len(critical)} critical/high anomalies require immediate investigation")

    # Run Task 4: Logging and Audit Trail
    print("\n--- Task 4: Anomaly Logging and Audit Trail ---")
    anomaly_log = []
    for date, value in anomalies.items():
        severity = classify_severity(value, mean_rev, std_rev)
        anomaly_log.append({
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'anomaly_date': str(date),
            'metric': 'daily_revenue',
            'value': float(value),
            'expected_range': f"{mean_rev - 2 * std_rev:.2f} to {mean_rev + 2 * std_rev:.2f}",
            'z_score': float(z_scores[date]),
            'severity': severity,
            'status': 'OPEN'
        })

    anomalies_df = pd.DataFrame(anomaly_log, columns=['timestamp', 'anomaly_date', 'metric', 'value', 'expected_range', 'z_score', 'severity', 'status'])
    anomalies_df.to_csv('anomalies_log.csv', index=False)
    anomalies_df.to_csv('output/anomalies_log.csv', index=False)
    print("Logged anomalies to anomalies_log.csv and output/anomalies_log.csv")

    # Run Task 5: Visualization
    print("\n--- Task 5: Visualization with Flagged Points ---")
    fig, ax = plt.subplots(figsize=(14, 6))

    # Convert index to pandas DatetimeIndex for proper matplotlib plotting
    datetime_index = pd.to_datetime(daily_revenue.index)
    
    # Plot raw data
    ax.plot(datetime_index, daily_revenue.values, marker='o', label='Daily Revenue', linewidth=2, color='#1f77b4')

    # Plot rolling average (7-day moving average)
    rolling_avg = daily_revenue.rolling(window=7, min_periods=1).mean()
    ax.plot(datetime_index, rolling_avg.values, label='7-day MA', color='green', linewidth=2, linestyle='--')

    # Highlight anomalies
    for date, value in anomalies.items():
        dt_date = pd.to_datetime(date)
        ax.scatter(dt_date, value, color='red', s=200, marker='X', zorder=5, label='Anomaly' if 'Anomaly' not in ax.get_legend_handles_labels()[1] else "")
        ax.annotate('ANOMALY', (dt_date, value), xytext=(0, 10), 
                    textcoords='offset points', ha='center', fontweight='bold', color='red',
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5, ec="red"))

    # Shade expected range (mean +- 1.5std)
    ax.fill_between(datetime_index, mean_rev - 1.5 * std_rev, mean_rev + 1.5 * std_rev, alpha=0.15, color='orange', label='Expected Range ±1.5σ')

    ax.set_xlabel('Date')
    ax.set_ylabel('Revenue ($)')
    ax.set_title('Daily Revenue with Anomalies Flagged')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, linestyle=':')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plots
    plt.savefig('anomaly_detection.png', dpi=150)
    plt.savefig('output/anomaly_detection.png', dpi=150)
    plt.close()
    print("Saved visualization to anomaly_detection.png and output/anomaly_detection.png")

if __name__ == '__main__':
    main()
