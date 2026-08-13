# Business Visualisation Principles Analysis

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
