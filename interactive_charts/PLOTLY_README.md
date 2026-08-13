# Interactive Plotly Chart Design Analysis & Documentation

## Executive Overview
Static visualisations communicate static findings, but interactive visualisations empower business stakeholders to explore data independently. This document provides full architectural documentation for interactive charts created using **Plotly Python** and integrated into a **Streamlit** web application.

---

## Task 1: Hover Tooltips (Detail on Demand)

Hover tooltips provide progressive disclosure: keeping the primary chart clean while revealing precise metrics on demand.

### Chart 1: Revenue Trend with Custom Hover (`chart1_revenue_trend.html`)
- **Type**: Multi-point Line Plot with Markers (`go.Scatter`).
- **Data**: 90-day daily revenue trend and order count data.
- **Hover Implementation**:
  ```python
  hovertemplate=(
      '<b>Date: %{x|%B %d, %Y}</b><br>' +
      'Revenue: $%{y:,.2f}<br>' +
      'Orders: %{customdata:,} orders<br>' +
      '<extra></extra>'
  )
  ```
- **Formatting Highlights**:
  - `%{x|%B %d, %Y}` formats dates as human-readable strings (e.g., "March 15, 2024").
  - `$%{y:,.2f}` formats revenue as comma-separated currency values.
  - `<extra></extra>` suppresses default trace identifier boxes for a clean layout.
  - `hovermode='x unified'` aggregates crosshair details along the time axis.

### Chart 2: Product Performance with Multi-Field Hover (`chart2_product_performance.html`)
- **Type**: Categorical Bar Chart (`go.Bar`).
- **Data**: Product line revenue, total order volume, average order value (AOV), and YoY growth rate.
- **Multi-Field Matrix via `customdata`**:
  ```python
  custom_data_matrix = np.column_stack((orders, avg_order_val, yoy_growth))
  fig = go.Figure(data=go.Bar(
      x=products,
      y=revenue,
      customdata=custom_data_matrix,
      hovertemplate=(
          '<b>Product Line: %{x}</b><br>' +
          'Total Revenue: $%{y:,.2f}<br>' +
          'Total Orders: %{customdata[0]:,} orders<br>' +
          'Avg Order Value: $%{customdata[1]:,.2f}<br>' +
          'YoY Growth: %{customdata[2]:+.1f}%<br>' +
          '<extra></extra>'
      )
  ))
  ```

---

## Task 2: Dropdown Filter Views (`chart3_metric_selector.html`)

Dropdown menus using Plotly's `updatemenus` allow users to toggle between multiple metric views (Revenue, Profit, Order Count) instantly in client-side HTML without triggering page reloads or server round-trips.

```python
fig.update_layout(
    updatemenus=[dict(
        active=0,
        x=0.0, xanchor='left', y=1.15, yanchor='top',
        buttons=[
            dict(label='Revenue ($)', method='update',
                 args=[{'visible': [True, False, False]}, {'title': 'Product Revenue ($)', 'yaxis': {'title': 'Revenue ($)'}}]),
            dict(label='Profit ($)', method='update',
                 args=[{'visible': [False, True, False]}, {'title': 'Product Profit ($)', 'yaxis': {'title': 'Profit ($)'}}]),
            dict(label='Order Count', method='update',
                 args=[{'visible': [False, False, True]}, {'title': 'Product Order Count', 'yaxis': {'title': 'Total Orders'}}])
        ]
    )]
)
```

---

## Task 3: Zoom, Pan, Select, and Reset Interactions (`chart4_interactive.html`)

Native client-side navigation features allow stakeholders to explore large datasets visually:
1. **Click and Drag (Zoom)**: Encloses any date or metric range to isolate data subsets.
2. **Shift + Click + Drag (Pan)**: Navigates across spatial axes without changing zoom scale.
3. **Double Click (Reset)**: Instantly restores initial scale and viewport boundaries.
4. **Box Select & Lasso Select**: Highlights specific sub-clusters of data points visually.

```python
fig.update_layout(
    dragmode='zoom',
    hovermode='closest',
    template='plotly_white'
)
```

---

## Task 4: Streamlit Integration (`streamlit_app.py`)

Plotly charts integrate seamlessly into full-stack Streamlit web applications via `st.plotly_chart`:
```python
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout='wide')
st.title("Interactive Sales Analytics Dashboard")

# Render interactive Plotly chart with responsive width
st.plotly_chart(fig, use_container_width=True)
```
- **Combined Workflow**: Streamlit sidebar sliders (`min_amount`, `selected_date_range`, `multiselect`) perform server-side data filtering, while embedded Plotly charts maintain client-side hover, zoom, and pan interactions.

---

## Task 5: Answer to Follow-Up Question

### Question:
*You have a time-series Plotly chart showing revenue by week. You want to add a date range slider so users can select which weeks to view (e.g., "show me only Q1 2024"). How would you implement this in Plotly?*

### Solution & Code Implementation:

Plotly provides native support for time-series date navigation through `rangeselector` buttons and `rangeslider` configured on the x-axis (`update_xaxes`).

```python
import plotly.graph_objects as go
import pandas as pd

fig = go.Figure(data=go.Scatter(
    x=df['week_start_date'],
    y=df['weekly_revenue'],
    mode='lines+markers',
    hovertemplate='<b>Week of %{x|%b %d, %Y}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
))

# Configure RangeSelector buttons and RangeSlider on X-axis
fig.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M (Q1)", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(step="all", label="All")
        ]),
        bgcolor="#e6f2ff",
        activecolor="#1f77b4"
    ),
    rangeslider=dict(visible=True),
    type="date"
)

fig.update_layout(
    title="Weekly Revenue Trend with Date Range Selector",
    xaxis_title="Date",
    yaxis_title="Weekly Revenue ($)"
)

fig.write_html("chart5_date_rangeslider.html")
```

### Comparative Analysis: When to Use Each Approach

| Feature | RangeSelector Buttons | RangeSlider Bar | Streamlit Date Input Filter |
| :--- | :--- | :--- | :--- |
| **Mechanism** | 1-click preset buttons | Drag-to-select bottom bar | Server-side query re-execution |
| **Interactivity** | Instant client-side | Instant client-side | Triggers Streamlit re-run |
| **Best Used For** | Quick standard periods (1M, Q1, YTD) | Dragging/scrubbing continuous trends | Filtering entire multi-chart dashboards |
| **User Experience** | Minimum effort for executives | High granularity exploration | Controls backend SQL/DataFrame operations |

---

## File Deliverables Checklist
- `interactive_charts/chart1_revenue_trend.html`
- `interactive_charts/chart2_product_performance.html`
- `interactive_charts/chart3_metric_selector.html`
- `interactive_charts/chart4_interactive.html`
- `interactive_charts/chart5_date_rangeslider.html`
- `interactive_charts/generate_charts.py`
- `interactive_charts/PLOTLY_README.md`
- `streamlit_app.py`
