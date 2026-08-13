# Dashboard Design Documentation

## Information Hierarchy Applied
- **Level 1 (Status)**: 5 KPI cards at the top row indicating Revenue, Active Customers, AOV, Churn Rate, and NPS.
- **Level 2 (Trends)**: 3 time-series line charts showing Monthly Revenue Trend, Churn vs Active Customers relationship, and Average Order Value fluctuations.
- **Level 3 (Segments)**: Horizontal bar chart showing revenue distribution by cohort segments (Enterprise, Mid-Market, SMB, Starter).
- **Level 4 (Detail)**: Sidebar dropdown selectors and date range filters with a download option for transaction data.

## Design Principles Applied
1. **Progressive Disclosure**: High-level status KPIs are displayed immediately; detailed drill-down explorer filters are hidden in the sidebar or bottom section.
2. **Spatial Organisation**: Core revenue metrics are on the top-left, the most valuable position for scanning.
3. **Consistent Metaphor**: Color-coded curves (Green = active, Red = churned) keep indicators easy to read.
4. **Context Over Numbers**: Every metric card utilizes delta percentages to provide period-over-period direction.

## Colour Palette
- Primary: `#1f77b4` (blue) - main revenue metrics
- Secondary: `#ff7f0e` (orange) - average order values
- Success: `#2ca02c` (green) - active user metrics
- Danger: `#d62728` (red) - churn indicators

## Target Audience
- **Primary**: VP of Sales (monitoring daily metrics and segment contributions)
- **Secondary**: CEO (weekly summary check of the top row)
- **Tertiary**: Analysts (drilling down to CSV exports)

## Data Sources
- KPI Values: Computed from processed transaction history database tables.
- Trend Data: Aggregated monthly cohorts.
- Segment Data: Segmented customer profiles.
