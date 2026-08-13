"""
Revenue Trend Analysis and Time-Series Analytics (Assignment Tasks)
Implements:
1. Resampling data by Weekly and Monthly periods with various aggregations.
2. Computing and plotting 7-day and 30-day rolling averages.
3. Calculating Month-over-Month (MoM) growth/decline percentage changes.
4. Computing cumulative sums for revenue growth.
5. Identifying trend direction, magnitude, volatility, and business implications.
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def main():
    print("==================================================")
    print("        REVENUE TREND ANALYSIS PIPELINE           ")
    print("==================================================")

    # Load and prepare data
    raw_data_path = "data/raw/sales.csv"
    if not os.path.exists(raw_data_path):
        print(f"Error: Raw sales file not found at {raw_data_path}")
        return

    print(f"Loading data from {raw_data_path}...")
    df_raw = pd.read_csv(raw_data_path)
    
    # Parse dates and sort
    df_raw['transaction_date'] = pd.to_datetime(df_raw['transaction_date'])
    df_raw = df_raw.sort_values('transaction_date')
    
    # Aggregate daily
    print("Aggregating raw transactions into daily records...")
    df = df_raw.groupby('transaction_date').agg(
        revenue=('amount', 'sum'),
        orders=('transaction_id', 'count')
    ).reset_index()
    df = df.rename(columns={'transaction_date': 'date'})
    
    # -------------------------------------------------------------------------
    # Task 1: Resample Data by Time Period
    # -------------------------------------------------------------------------
    print("\n--- Task 1: Resample Data by Time Period ---")
    df_ts = df.set_index('date')

    # Weekly aggregation
    weekly_revenue = df_ts['revenue'].resample('W').sum()
    weekly_count = df_ts['orders'].resample('W').count()
    weekly_avg = df_ts['revenue'].resample('W').mean()

    # Monthly aggregation
    monthly_revenue = df_ts['revenue'].resample('M').sum()
    monthly_count = df_ts['orders'].resample('M').count()
    monthly_avg = df_ts['revenue'].resample('M').mean()

    print("\n[Weekly Summary (First 5 weeks)]:")
    for d, rev, cnt, avg in zip(weekly_revenue.index[:5], weekly_revenue.iloc[:5], weekly_count.iloc[:5], weekly_avg.iloc[:5]):
        print(f"  Week ending {d.strftime('%Y-%m-%d')}: Revenue: ${rev:,.2f}, Orders/Days: {cnt}, Avg Daily Rev: ${avg:,.2f}")

    print("\n[Monthly Summary]:")
    for d, rev, cnt, avg in zip(monthly_revenue.index, monthly_revenue, monthly_count, monthly_avg):
        print(f"  Month ending {d.strftime('%Y-%m-%d')}: Revenue: ${rev:,.2f}, Orders/Days: {cnt}, Avg Daily Rev: ${avg:,.2f}")

    # Compare results
    max_weekly_week = weekly_revenue.idxmax()
    max_weekly_val = weekly_revenue.max()
    max_monthly_month = monthly_revenue.idxmax()
    max_monthly_val = monthly_revenue.max()

    print(f"\nHighest Weekly Revenue: ${max_weekly_val:,.2f} (Week ending {max_weekly_week.strftime('%Y-%m-%d')})")
    print(f"Highest Monthly Revenue: ${max_monthly_val:,.2f} (Month ending {max_monthly_month.strftime('%Y-%m-%d')})")

    # -------------------------------------------------------------------------
    # Task 2: Compute Rolling Window Average
    # -------------------------------------------------------------------------
    print("\n--- Task 2: Compute Rolling Window Average ---")
    df['revenue_ma7'] = df['revenue'].rolling(window=7, min_periods=1).mean()
    df['revenue_ma30'] = df['revenue'].rolling(window=30, min_periods=1).mean()

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['revenue'], label='Raw Daily Revenue', alpha=0.3, color='gray')
    plt.plot(df['date'], df['revenue_ma7'], label='7-day MA', color='blue', linewidth=1.5)
    plt.plot(df['date'], df['revenue_ma30'], label='30-day MA', color='red', linewidth=2)
    plt.title('Daily Revenue with Rolling Window Averages')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Save plots
    plt.savefig('output/rolling_avg.png', dpi=300, bbox_inches='tight')
    plt.savefig('rolling_avg.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved rolling average plot to output/rolling_avg.png and rolling_avg.png")

    # Trend revealed by rolling averages
    print("Trend observation: The 30-day moving average filters out extreme daily fluctuations (noise) to show the long-term trend.")

    # -------------------------------------------------------------------------
    # Task 3: Calculate Month-over-Month Percentage Change
    # -------------------------------------------------------------------------
    print("\n--- Task 3: Calculate Month-over-Month Percentage Change ---")
    mom_change = monthly_revenue.pct_change() * 100

    print("Month-over-Month (MoM) Growth Percentage:")
    for d, pct in zip(mom_change.index, mom_change):
        if pd.isna(pct):
            print(f"  Month ending {d.strftime('%Y-%m-%d')}: N/A (Baseline)")
        else:
            print(f"  Month ending {d.strftime('%Y-%m-%d')}: {pct:+.2f}%")

    growth_months = mom_change[mom_change > 0]
    decline_months = mom_change[mom_change < 0]

    print("\nMonths with Growth (Positive MoM Change):")
    for d, pct in zip(growth_months.index, growth_months):
        print(f"  {d.strftime('%B %Y')}: {pct:+.2f}%")

    print("\nMonths with Decline (Negative MoM Change):")
    for d, pct in zip(decline_months.index, decline_months):
        print(f"  {d.strftime('%B %Y')}: {pct:+.2f}%")

    # Explain pattern
    positive_count = len(growth_months)
    negative_count = len(decline_months)
    avg_change = mom_change.mean()
    print(f"\nPattern Analysis: Average monthly growth rate is {avg_change:+.2f}%.")
    print(f"Out of {positive_count + negative_count} comparison periods, {positive_count} showed growth and {negative_count} showed decline.")

    # -------------------------------------------------------------------------
    # Task 4: Compute Cumulative Sum
    # -------------------------------------------------------------------------
    print("\n--- Task 4: Compute Cumulative Sum ---")
    df['cumulative_revenue'] = df['revenue'].cumsum()

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['cumulative_revenue'], color='green', linewidth=2)
    plt.title('Cumulative Revenue Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Cumulative Revenue ($)')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Save plots
    plt.savefig('output/cumulative.png', dpi=300, bbox_inches='tight')
    plt.savefig('cumulative.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved cumulative revenue plot to output/cumulative.png and cumulative.png")

    total_revenue = df['cumulative_revenue'].iloc[-1]
    print(f"Total accumulated revenue by end of period: ${total_revenue:,.2f}")

    # -------------------------------------------------------------------------
    # Task 5: Identify Trend Pattern and Business Implications
    # -------------------------------------------------------------------------
    print("\n--- Task 5: Identify Trend Pattern and Business Implications ---")
    recent_ma30 = df['revenue_ma30'].iloc[-30:]
    trend_direction = 'up' if recent_ma30.iloc[-1] > recent_ma30.iloc[0] else 'down'
    trend_magnitude = ((recent_ma30.iloc[-1] - recent_ma30.iloc[0]) / recent_ma30.iloc[0]) * 100

    volatility = df['revenue'].std()

    analysis = f"""
TREND ANALYSIS SUMMARY:
-----------------------
Rolling Average Trend (last 30 days): {trend_direction.upper()}
Change magnitude over last 30 days: {trend_magnitude:+.2f}%
Latest Month-over-month growth: {mom_change.iloc[-1]:+.2f}%
Daily Revenue Volatility (Standard Deviation): ${volatility:,.2f}

Business Implications:
- {"Accelerating growth - maintain current strategy and scale operations." if trend_direction == 'up' else "Declining momentum - investigate causes, check marketing channels, or review customer churn."}
- High daily revenue volatility of ${volatility:,.2f} indicates significant transaction noise. Sustainable business metrics like 30-day moving average and cumulative sum are crucial for strategic planning.

Strategic Action Plan:
1. {"Capitalize on the upward trajectory by expanding marketing budget and optimizing customer acquisition funnel." if trend_direction == "up" else "Formulate immediate retention campaigns and run diagnostic surveys on customer segments to isolate the decline causes."}
2. Continue using rolling averages rather than raw daily figures to set targets, mitigating overreactions to daily revenue fluctuations.
"""
    print(analysis)

    # Save summary report to output/revenue_trend_analysis_report.txt
    report_path = "output/revenue_trend_analysis_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(analysis)
    print(f"Saved analysis report to {report_path}")

if __name__ == '__main__':
    main()
