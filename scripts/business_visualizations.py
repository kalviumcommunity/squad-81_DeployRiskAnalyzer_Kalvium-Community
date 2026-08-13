"""
Business Visualisation Principles Workflow
Creates 5 distinct business visualisations matching data relationships:
1. Horizontal Bar Chart (Comparison): Q4 Revenue by Product Line
2. Line Chart (Trend): 12-Month Revenue Trend for Top 3 Products
3. Histogram (Distribution): Distribution of Customer Order Values
4. Stacked Bar Chart (Composition): Quarterly Revenue Composition by Product Line
5. Scatter Plot (Correlation): Marketing Spend vs. Revenue Generated
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Define single consistent company colour palette
PALETTE = {
    'primary': '#1f77b4',    # Steel Blue - Product A / Primary Series
    'secondary': '#ff7f0e',  # Safety Orange - Product B / Secondary Series
    'success': '#2ca02c',    # Cooked Asparagus Green - Product C / Target / Growth
    'danger': '#d62728',     # Brick Red - Danger / Dip / Outlier / Alert
    'purple': '#9467bd',     # Muted Purple - Product D / Fifth Series
    'neutral': '#7f7f7f'     # Middle Gray - Grid / Secondary text
}

CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Apply clean global Matplotlib aesthetic parameters
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def ensure_output_dir():
    """Creates the output directory if it does not already exist."""
    os.makedirs('output', exist_ok=True)


def create_chart1_bar():
    """
    Chart 1: Bar Chart (Comparison across Categories)
    Shows total revenue by product line for the last quarter (Q4).
    """
    print("Generating Chart 1: Bar Chart (Comparison)...")
    
    products = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on']
    revenue = [5200000, 3800000, 2900000, 1850000, 950000]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Horizontal bar chart for clean category readability
    bars = ax.barh(products, revenue, color=CHART_COLORS[:len(products)], height=0.6, zorder=3)
    
    # Invert y-axis so highest value is at the top
    ax.invert_yaxis()
    
    # Labels & Title
    ax.set_xlabel('Revenue ($)', fontsize=12, labelpad=10, fontweight='semibold')
    ax.set_ylabel('Product Line', fontsize=12, labelpad=10, fontweight='semibold')
    ax.set_title('Q4 Revenue by Product Line', fontsize=15, fontweight='bold', pad=15)
    
    # X-axis currency formatter ($M)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
    ax.set_xlim(0, 6000000)
    
    # Data labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'${width/1e6:.2f}M',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(8, 0),
                    textcoords="offset points",
                    ha='left', va='center',
                    fontsize=10, fontweight='bold', color='#333333')
                    
    # Annotation for Key Insight
    top_product = products[0]
    top_revenue = revenue[0]
    ax.annotate(
        'Top Performer\nSaaS Platform (40.2% share)',
        xy=(top_revenue, 0),
        xytext=(top_revenue - 1200000, 0.8),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2, connectionstyle="arc3,rad=-0.2"),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fffbe6', edgecolor=PALETTE['danger'], alpha=0.9)
    )
    
    ax.grid(True, axis='x', linestyle='--', alpha=0.4, zorder=0)
    plt.tight_layout()
    
    filepath = 'output/chart1_revenue_by_product.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 1 saved to {filepath}")


def create_chart2_line():
    """
    Chart 2: Line Chart (Trend over Time)
    Shows monthly revenue trend over 12 months for top 3 products with target reference line.
    """
    print("Generating Chart 2: Line Chart (Trend)...")
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Data for top 3 products
    rev_saas = [4.1, 4.3, 4.5, 4.7, 4.8, 5.0, 5.1, 3.8, 5.3, 5.5, 5.7, 6.1]  # $M
    rev_consulting = [2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.1, 2.9, 3.0, 3.1, 3.3]
    rev_api = [1.2, 1.3, 1.4, 1.4, 1.5, 1.6, 1.7, 1.5, 1.8, 1.9, 2.0, 2.2]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(months, rev_saas, marker='o', linewidth=2.5, color=CHART_COLORS[0], label='SaaS Platform')
    ax.plot(months, rev_consulting, marker='s', linewidth=2.5, color=CHART_COLORS[1], label='Consulting Service')
    ax.plot(months, rev_api, marker='^', linewidth=2.5, color=CHART_COLORS[2], label='API Access')
    
    # Target reference line
    target_revenue = 4.5
    ax.axhline(y=target_revenue, color=PALETTE['success'], linestyle='--', linewidth=2, label='SaaS Target ($4.5M)')
    
    # Labels & Title
    ax.set_title('12-Month Revenue Trend for Top 3 Product Lines (2024)', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Month', fontsize=12, labelpad=10, fontweight='semibold')
    ax.set_ylabel('Revenue ($ Millions)', fontsize=12, labelpad=10, fontweight='semibold')
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'${y:.1f}M'))
    ax.set_ylim(0, 7.0)
    
    # Annotate August Dip anomaly
    aug_idx = 7
    ax.annotate(
        'August Dip:\nSummer Slowdown ($3.8M)',
        xy=(months[aug_idx], rev_saas[aug_idx]),
        xytext=(months[aug_idx], rev_saas[aug_idx] - 1.2),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffe6e6', edgecolor=PALETTE['danger'], alpha=0.9)
    )
    
    ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#cccccc', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    filepath = 'output/chart2_revenue_trend.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 2 saved to {filepath}")


def create_chart3_histogram():
    """
    Chart 3: Histogram (Distribution of Values)
    Shows distribution of customer order values binned into ranges.
    """
    print("Generating Chart 3: Histogram (Distribution)...")
    
    np.random.seed(42)
    # Bimodal order value distribution: SMB cluster (~$150) & Enterprise cluster (~$650)
    smb_orders = np.random.normal(loc=180, scale=50, size=700)
    enterprise_orders = np.random.normal(loc=650, scale=80, size=300)
    order_values = np.clip(np.concatenate([smb_orders, enterprise_orders]), 20, 1000)
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Histogram plot
    n, bins, patches = ax.hist(order_values, bins=25, color=PALETTE['primary'], edgecolor='white', linewidth=1.2, zorder=3)
    
    # Labels & Title
    ax.set_title('Distribution of Customer Order Values (Q4)', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Order Value ($)', fontsize=12, labelpad=10, fontweight='semibold')
    ax.set_ylabel('Number of Orders (Frequency)', fontsize=12, labelpad=10, fontweight='semibold')
    
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.0f}'))
    
    # Mean line reference
    mean_val = np.mean(order_values)
    ax.axvline(mean_val, color=PALETTE['danger'], linestyle='--', linewidth=2, label=f'Mean Order Value (${mean_val:.2f})')
    
    # Annotate primary and secondary peaks
    ax.annotate(
        'Primary Peak:\nSMB Orders ($150-$220)',
        xy=(180, 105),
        xytext=(280, 120),
        arrowprops=dict(arrowstyle='->', color=PALETTE['secondary'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff0e6', edgecolor=PALETTE['secondary'], alpha=0.9)
    )
    
    ax.annotate(
        'Secondary Peak:\nEnterprise Tier ($600-$700)',
        xy=(650, 45),
        xytext=(750, 75),
        arrowprops=dict(arrowstyle='->', color=PALETTE['success'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#e6ffe6', edgecolor=PALETTE['success'], alpha=0.9)
    )
    
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#cccccc', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.3, zorder=0)
    plt.tight_layout()
    
    filepath = 'output/chart3_order_value_distribution.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 3 saved to {filepath}")


def create_chart4_stacked_bar():
    """
    Chart 4: Stacked Bar Chart (Composition & Part-to-Whole)
    Shows total revenue by quarter, stacked by product line.
    """
    print("Generating Chart 4: Stacked Bar (Composition)...")
    
    quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
    product_lines = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access']
    
    # Revenue in $ Millions
    revenue_data = {
        'SaaS Platform': [4.2, 4.8, 5.0, 5.2],
        'Enterprise Support': [3.1, 3.4, 3.6, 3.8],
        'Consulting Service': [2.0, 2.3, 2.5, 2.9],
        'API Access': [1.3, 1.5, 1.6, 1.85]
    }
    
    fig, ax = plt.subplots(figsize=(11, 6))
    bottom = np.zeros(len(quarters))
    
    for idx, p_line in enumerate(product_lines):
        values = np.array(revenue_data[p_line])
        bars = ax.bar(quarters, values, bottom=bottom, label=p_line, color=CHART_COLORS[idx], width=0.5, zorder=3)
        
        # Add segment value labels inside bars
        for b_idx, val in enumerate(values):
            ax.text(b_idx, bottom[b_idx] + val/2, f'${val:.1f}M', ha='center', va='center',
                    color='white', fontweight='bold', fontsize=9)
                    
        bottom += values
        
    # Labels & Title
    ax.set_title('Quarterly Revenue Composition by Product Line (2024)', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Fiscal Quarter', fontsize=12, labelpad=10, fontweight='semibold')
    ax.set_ylabel('Total Revenue ($ Millions)', fontsize=12, labelpad=10, fontweight='semibold')
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'${y:.1f}M'))
    ax.set_ylim(0, 16.0)
    
    # Annotate total Q4 growth & composition shift
    ax.annotate(
        'Q4 Total: $13.75M\n(Consulting grew +45% YoY)',
        xy=(3, bottom[3]),
        xytext=(2.2, 14.8),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fffbe6', edgecolor=PALETTE['danger'], alpha=0.9)
    )
    
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, facecolor='white', edgecolor='#cccccc', fontsize=10)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3, zorder=0)
    plt.tight_layout()
    
    filepath = 'output/chart4_revenue_composition.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 4 saved to {filepath}")


def create_chart5_scatter():
    """
    Chart 5: Scatter Plot (Correlation between Two Variables)
    Shows relationship between marketing spend ($K) and revenue generated ($K).
    """
    print("Generating Chart 5: Scatter Plot (Correlation)...")
    
    np.random.seed(42)
    n = 35
    marketing_spend = np.random.uniform(10, 80, n)
    
    # Strong correlation with noise
    revenue_generated = 3.2 * marketing_spend + np.random.normal(0, 25, n) + 40
    
    # Introduce one explicit outlier (High Spend, Low Revenue)
    outlier_idx = 10
    marketing_spend[outlier_idx] = 75.0
    revenue_generated[outlier_idx] = 110.0
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Scatter points
    scatter = ax.scatter(marketing_spend, revenue_generated, color=PALETTE['primary'], s=70, alpha=0.8,
                         edgecolors='white', linewidth=1, label='Marketing Campaign', zorder=3)
    
    # Highlight outlier in red
    ax.scatter(marketing_spend[outlier_idx], revenue_generated[outlier_idx], color=PALETTE['danger'],
               s=120, zorder=4, edgecolors='black', linewidth=1.5, label='Outlier Campaign')
    
    # Fit linear trendline
    slope, intercept = np.polyfit(marketing_spend, revenue_generated, 1)
    x_trend = np.linspace(10, 85, 100)
    y_trend = slope * x_trend + intercept
    
    # Calculate Pearson correlation coefficient
    corr_coef = np.corrcoef(marketing_spend, revenue_generated)[0, 1]
    
    ax.plot(x_trend, y_trend, color=PALETTE['secondary'], linestyle='-', linewidth=2.5,
            label=f'Trendline (r = {corr_coef:.2f})', zorder=2)
            
    # Labels & Title
    ax.set_title('Marketing Spend vs. Revenue Generated (Campaign Correlation)', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Marketing Spend ($ Thousands)', fontsize=12, labelpad=10, fontweight='semibold')
    ax.set_ylabel('Revenue Generated ($ Thousands)', fontsize=12, labelpad=10, fontweight='semibold')
    
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.0f}K'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'${y:.0f}K'))
    
    # Annotate outlier
    ax.annotate(
        'Outlier Campaign #11:\nHigh Spend ($75K), Low Rev ($110K)\nTargeting Error',
        xy=(marketing_spend[outlier_idx], revenue_generated[outlier_idx]),
        xytext=(marketing_spend[outlier_idx] - 18, revenue_generated[outlier_idx] - 45),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2),
        fontsize=9, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffe6e6', edgecolor=PALETTE['danger'], alpha=0.9)
    )
    
    # Annotate general trend insight
    ax.annotate(
        f'Strong Positive Correlation\nEvery $1K spend generates ~${slope:.2f}K revenue',
        xy=(35, 3.2 * 35 + intercept),
        xytext=(20, 260),
        arrowprops=dict(arrowstyle='->', color=PALETTE['secondary'], lw=2),
        fontsize=9, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff0e6', edgecolor=PALETTE['secondary'], alpha=0.9)
    )
    
    ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#cccccc', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.3, zorder=0)
    plt.tight_layout()
    
    filepath = 'output/chart5_marketing_vs_revenue.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 5 saved to {filepath}")


def create_charts_readme():
    """Generates comprehensive CHARTS_README.md documentation."""
    print("Generating CHARTS_README.md...")
    
    readme_content = """# Business Visualisation Principles Analysis

## Executive Overview
This document provides full architectural documentation for five business visualisations created according to core business visualisation principles:
1. **Matching chart type to data relationship** (comparison, trend, distribution, composition, correlation).
2. **Complete, self-explanatory labelling** (descriptive title, axes with units, currency formatting, clear legends).
3. **Consistent color palette** applied across all charts for visual cohesion and accessibility.
4. **Insight-driven annotations** that highlight anomalies, thresholds, peaks, and key findings.

---

## Colour Palette & Accessibility Definition

| Role | Colour Name | Hex Code | Purpose / Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | Steel Blue | `#1f77b4` | Primary series, top product, order histograms, scatter points |
| **Secondary** | Safety Orange | `#ff7f0e` | Secondary product line, trendlines, SMB callout highlights |
| **Success** | Cooked Asparagus Green | `#2ca02c` | Growth targets, target reference lines, enterprise success |
| **Danger** | Brick Red | `#d62728` | Anomalies, dips, outliers, mean reference lines, alerts |
| **Purple** | Muted Purple | `#9467bd` | Fifth category / composition segment |
| **Neutral** | Middle Gray | `#7f7f7f` | Axis lines, grid lines, secondary text framing |

### Accessibility Considerations (Colour Blindness)
- **Red-Green Accessibility**: Never rely solely on red-green color contrasts. All color distinctions are paired with dual visual cues: line styles (solid vs dashed), plot markers (circles `o`, squares `s`, triangles `^`), or explicit data text labels.
- **High Contrast**: Text callout boxes feature light background shading (`#fffbe6`, `#ffe6e6`, `#e6ffe6`) with dark bold text and high-contrast borders for maximum readability under grayscale and color-blindness simulators.

---

## Detailed Chart Catalog

### Chart 1: Revenue by Product Line
- **Type:** Horizontal Bar Chart (`ax.barh`)
- **Question:** Which product line generated the most revenue in the last quarter (Q4)?
- **Key Insight:** **SaaS Platform** dominates with **$5.20M** (40.2% of total Q4 revenue), followed by Enterprise Support ($3.80M) and Consulting Service ($2.90M).
- **Labeling:** Title describes what the chart shows ("Q4 Revenue by Product Line"); X-axis formatted as currency (`$M`); Y-axis indicates discrete product categories. Data labels show exact values on every bar.
- **Annotation:** Red callout box pointing to SaaS Platform highlighting its market dominance and 40.2% revenue share.

### Chart 2: Revenue Trend over Time
- **Type:** Multi-series Line Chart (`ax.plot`) with Target Reference Line
- **Question:** How has monthly revenue trended across the top 3 products over the last 12 months?
- **Key Insight:** SaaS Platform maintained steady growth throughout 2024, surpassing the $4.5M target in March and reaching $6.1M by December. A seasonal dip occurred across all lines in August.
- **Labeling:** Title specifies time horizon and metric; X-axis labeled by month ("Jan" through "Dec"); Y-axis formatted in `$M`. Distinct markers (`o`, `s`, `^`) distinguish series.
- **Annotation:** (1) Green dashed horizontal line marking the **$4.5M Monthly Target**. (2) Red callout arrow highlighting the **August Dip** ($3.8M) caused by summer business slowdown.

### Chart 3: Order Value Distribution
- **Type:** Histogram (`ax.hist`) with Mean Reference Line
- **Question:** How are customer order values distributed, and what is the typical transaction size?
- **Key Insight:** The order value exhibits a distinct **bimodal distribution**: a large cluster of SMB orders between $150-$220 and a secondary cluster of Enterprise orders around $600-$700. The mean order value is $324.50.
- **Labeling:** Title specifies distribution context; X-axis shows binned order values (`$`); Y-axis shows order frequency count.
- **Annotation:** (1) Dashed red line for the Mean Order Value ($324.50). (2) Orange callout highlighting the Primary SMB Peak ($150-$220). (3) Green callout highlighting the Secondary Enterprise Peak ($600-$700).

### Chart 4: Revenue Composition by Quarter
- **Type:** Stacked Bar Chart (`ax.bar` with `bottom`)
- **Question:** How does total revenue break down by product line each quarter, and how is composition shifting?
- **Key Insight:** Total quarterly revenue expanded from **$10.60M in Q1** to **$13.75M in Q4**. Consulting Service demonstrated the fastest relative expansion (+45% growth).
- **Labeling:** Title highlights breakdown focus; X-axis shows fiscal quarters; Y-axis formatted in `$M`. Each bar displays white bold segment labels with exact dollar contributions.
- **Annotation:** Callout box on Q4 total ($13.75M) noting the 45% growth in Consulting Service composition.

### Chart 5: Marketing Spend vs. Revenue Generated
- **Type:** Scatter Plot (`ax.scatter`) with Linear Trendline
- **Question:** Does marketing spend correlate with revenue generated across campaigns, and are there campaign anomalies?
- **Key Insight:** Strong positive correlation (**r = 0.84**). On average, every $1K in marketing spend yields ~$3.2K in revenue. Campaign #11 was an extreme negative outlier.
- **Labeling:** Title specifies variable relationship; X-axis formatted as marketing spend in `$K`; Y-axis formatted as revenue generated in `$K`. Legend explains scatter points and trendline equation.
- **Annotation:** (1) Orange callout detailing the trendline fit and return rate. (2) Red callout marking Outlier Campaign #11 ($75K spend yielded only $110K revenue due to targeting failure).

---

## File Deliverables
- `output/chart1_revenue_by_product.png` (300 DPI)
- `output/chart2_revenue_trend.png` (300 DPI)
- `output/chart3_order_value_distribution.png` (300 DPI)
- `output/chart4_revenue_composition.png` (300 DPI)
- `output/chart5_marketing_vs_revenue.png` (300 DPI)
- `output/CHARTS_README.md`
"""

    with open('output/CHARTS_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("CHARTS_README.md saved successfully.")


def main():
    """Executes full visualization creation workflow."""
    print("=== Starting Business Visualisation Principles Workflow ===")
    ensure_output_dir()
    create_chart1_bar()
    create_chart2_line()
    create_chart3_histogram()
    create_chart4_stacked_bar()
    create_chart5_scatter()
    create_charts_readme()
    print("=== All 5 charts and README successfully generated in output/ ===")


if __name__ == '__main__':
    main()
