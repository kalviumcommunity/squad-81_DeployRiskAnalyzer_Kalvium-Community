"""
Time-Series Trend & Rolling Metrics Workflow
Computes time-series resampling (weekly/monthly), rolling window averages (7-day, 30-day),
month-over-month percentage changes, cumulative sums, trend directions, and outputs business implications.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_dataset(filepath='data/raw/sales.csv'):
    """
    Loads daily sales dataset. Synthesizes 365 days of daily transactions.
    """
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D')
    n = len(dates)

    # Base trend + weekly seasonality + daily noise
    trend = np.linspace(8000, 14000, n)
    seasonality = 1500 * np.sin(2 * np.pi * np.arange(n) / 7)
    noise = np.random.normal(0, 1200, n)
    revenue = np.maximum(1000.0, trend + seasonality + noise)

    orders = np.random.randint(80, 250, size=n)
    customers = np.random.randint(50, 180, size=n)

    df = pd.DataFrame({
        'date': dates,
        'revenue': np.round(revenue, 2),
        'orders': orders,
        'customers': customers
    })

    return df


def task1_resample_data(df):
    """
    Task 1: Resample Data by Time Period
    Aggregates daily data into weekly and monthly buckets with multiple agg functions.
    """
    print("\n--- Task 1: Resampling Data by Time Period ---")
    df_ts = df.set_index('date')

    # Weekly aggregation
    weekly_revenue = df_ts['revenue'].resample('W').sum()
    weekly_count = df_ts['orders'].resample('W').count()
    weekly_avg = df_ts['revenue'].resample('W').mean()

    # Monthly aggregation
    monthly_revenue = df_ts['revenue'].resample('ME').sum()
    monthly_count = df_ts['orders'].resample('ME').count()
    monthly_avg = df_ts['revenue'].resample('ME').mean()

    print("Weekly Revenue Summary (First 5 weeks):")
    print(weekly_revenue.head())
    print("\nWeekly Order Count (First 5 weeks):")
    print(weekly_count.head())

    # Period with highest revenue
    highest_week = weekly_revenue.idxmax()
    highest_week_val = weekly_revenue.max()
    highest_month = monthly_revenue.idxmax()
    highest_month_val = monthly_revenue.max()

    print(f"\nHighest Revenue Week: {highest_week.strftime('%Y-%m-%d')} (${highest_week_val:,.2f})")
    print(f"Highest Revenue Month: {highest_month.strftime('%Y-%m')} (${highest_month_val:,.2f})")

    return df_ts, weekly_revenue, monthly_revenue


def task2_rolling_metrics(df):
    """
    Task 2: Compute Rolling Window Averages (7-day & 30-day)
    """
    print("\n--- Task 2: Computing 7-day and 30-day Rolling Averages ---")
    df['revenue_ma7'] = df['revenue'].rolling(window=7).mean()
    df['revenue_ma30'] = df['revenue'].rolling(window=30).mean()

    # Plot raw vs rolling
    os.makedirs('output', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['revenue'], label='Raw Daily Revenue', alpha=0.3, color='gray')
    plt.plot(df['date'], df['revenue_ma7'], label='7-day Moving Average', color='blue', linewidth=1.5)
    plt.plot(df['date'], df['revenue_ma30'], label='30-day Moving Average', color='red', linewidth=2.0)
    plt.title('Daily Revenue vs 7-day & 30-day Rolling Averages', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    img_path = 'output/rolling_avg.png'
    plt.savefig(img_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Rolling average visualization saved to '{img_path}'.")

    return df


def task3_mom_change(monthly_revenue):
    """
    Task 3: Calculate Month-over-Month Percentage Change
    """
    print("\n--- Task 3: Month-over-Month Percentage Change ---")
    mom_change = monthly_revenue.pct_change() * 100

    print("Month-over-Month Percentage Change (%):")
    print(mom_change.round(2))

    growth_months = mom_change[mom_change > 0]
    decline_months = mom_change[mom_change < 0]

    print(f"\nMonths with Positive Growth ({len(growth_months)}):")
    for idx, val in growth_months.items():
        print(f"  {idx.strftime('%Y-%m')}: +{val:.2f}%")

    print(f"\nMonths with Decline ({len(decline_months)}):")
    for idx, val in decline_months.items():
        print(f"  {idx.strftime('%Y-%m')}: {val:.2f}%")

    return mom_change


def task4_cumulative_sum(df):
    """
    Task 4: Compute Cumulative Sum
    """
    print("\n--- Task 4: Computing Cumulative Revenue ---")
    df['cumulative_revenue'] = df['revenue'].cumsum()

    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['cumulative_revenue'], color='green', linewidth=2.0)
    plt.title('Cumulative Revenue Over Time', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Total Cumulative Revenue ($)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    cum_img_path = 'output/cumulative.png'
    plt.savefig(cum_img_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Cumulative revenue plot saved to '{cum_img_path}'.")

    total_rev = df['cumulative_revenue'].iloc[-1]
    print(f"Total Revenue Accumulated by Year-End: ${total_rev:,.2f}")

    return df


def task5_trend_analysis(df, mom_change):
    """
    Task 5: Identify Trend Pattern and Business Implications
    """
    print("\n--- Task 5: Trend Pattern Analysis & Business Implications ---")
    recent_ma30 = df['revenue_ma30'].dropna().iloc[-30:]
    trend_direction = 'up' if recent_ma30.iloc[-1] > recent_ma30.iloc[0] else 'down'
    trend_magnitude = ((recent_ma30.iloc[-1] - recent_ma30.iloc[0]) / recent_ma30.iloc[0]) * 100

    volatility = df['revenue'].std()

    analysis = f"""TREND & ROLLING METRICS BUSINESS ANALYSIS REPORT
==================================================

Rolling Average Trend: {trend_direction.upper()}
Change over last 30 days: {trend_magnitude:.1f}%
Month-over-Month Growth (Latest Month): {mom_change.iloc[-1]:.1f}%
Revenue Volatility (Standard Deviation): ${volatility:,.2f}

Pattern Summary:
- Daily revenue exhibits high short-term volatility (std dev ${volatility:,.0f}), which creates false alarms when inspecting individual day-to-day changes.
- The 7-day rolling average effectively eliminates day-of-week seasonality (e.g. weekend dips).
- The 30-day rolling average confirms a sustainable {trend_direction.upper()} trend across the period (+{trend_magnitude:.1f}% growth over the last month).

Business Implications:
- {['Accelerating growth - maintain current scaling strategy and support capacity.', 'Declining momentum - investigate potential churn or seasonal slowdown.'][0 if trend_direction == 'up' else 1]}
- Avoid making aggressive pricing or marketing adjustments based on daily fluctuations.

Recommended Actions:
- Rely on 7-day MA for operational scheduling and 30-day MA for strategic quarterly forecasting.
- Establish automated alerts triggered only when the 7-day MA drops below threshold boundaries, filtering out daily noise.
"""

    print(analysis)

    report_path = 'output/trend_analysis.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(analysis)
    print(f"[SUCCESS] Trend analysis report written to '{report_path}'.")

    return analysis


def main():
    print("==================================================")
    print("      TIME-SERIES TREND & ROLLING METRICS         ")
    print("==================================================")

    # Load dataset
    df = load_dataset()

    # Task 1: Resample Data
    df_ts, weekly_revenue, monthly_revenue = task1_resample_data(df)

    # Task 2: Compute Rolling Averages
    df = task2_rolling_metrics(df)

    # Task 3: Month-over-Month Change
    mom_change = task3_mom_change(monthly_revenue)

    # Task 4: Cumulative Revenue
    df = task4_cumulative_sum(df)

    # Task 5: Trend Analysis & Business Implications
    task5_trend_analysis(df, mom_change)

    print("\n==================================================")
    print("      TIME-SERIES PIPELINE COMPLETED              ")
    print("==================================================")


if __name__ == '__main__':
    main()
