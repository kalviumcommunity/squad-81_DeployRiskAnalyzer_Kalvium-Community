"""
Interactive Plotly Chart Design Generator
Generates five standalone interactive HTML charts showcasing Plotly capabilities:
Task 1: Chart 1 (Daily Revenue Trend with Custom Hover) & Chart 2 (Product Performance with Multi-Field Hover)
Task 2: Chart 3 (Metric Selector Dropdown Filter)
Task 3: Chart 4 (Interactive Zoom, Pan, Select, Hover)
Task 5: Chart 5 (Time Series with Date Range Selector & Range Slider)
"""

import os
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def ensure_directories():
    """Creates target output directories if they do not exist."""
    os.makedirs('interactive_charts', exist_ok=True)
    os.makedirs('output', exist_ok=True)


def create_chart1():
    """
    Task 1: Chart 1 - Daily Revenue Trend with Custom Hover Tooltip
    """
    print("Building Chart 1: Revenue Trend with Custom Hover...")
    
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    base_rev = np.linspace(40000, 85000, 90)
    noise = np.random.normal(0, 6000, 90)
    revenue = np.maximum(20000, base_rev + noise)
    order_count = (revenue / np.random.uniform(120, 180, 90)).astype(int)
    
    df = pd.DataFrame({'date': dates, 'revenue': revenue, 'order_count': order_count})
    
    fig = go.Figure(data=go.Scatter(
        x=df['date'],
        y=df['revenue'],
        mode='lines+markers',
        customdata=df['order_count'],
        hovertemplate=(
            '<b>Date: %{x|%B %d, %Y}</b><br>' +
            'Revenue: $%{y:,.2f}<br>' +
            'Orders: %{customdata:,} orders<br>' +
            '<extra></extra>'
        ),
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=7, color='#1f77b4', symbol='circle')
    ))
    
    fig.update_layout(
        title=dict(text='Daily Revenue Trend (Q1 2024)', font=dict(size=18, family='Arial')),
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        template='plotly_white',
        height=550
    )
    
    # Save to interactive_charts and root
    fig.write_html('interactive_charts/chart1_revenue_trend.html')
    fig.write_html('chart1_revenue_trend.html')
    print("Chart 1 exported to interactive_charts/chart1_revenue_trend.html")


def create_chart2():
    """
    Task 1: Chart 2 - Product Performance with Multi-Column Hover Tooltip
    """
    print("Building Chart 2: Product Performance with Multi-Field Hover...")
    
    products = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on']
    revenue = [5200000, 3800000, 2900000, 1850000, 950000]
    orders = [14200, 4800, 1250, 18500, 3800]
    avg_order_val = [rev / ord_cnt for rev, ord_cnt in zip(revenue, orders)]
    yoy_growth = [24.5, 18.2, 45.0, 12.8, -5.2]
    
    # Stack customdata into a 2D array: [orders, avg_order_val, yoy_growth]
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
        ),
        marker=dict(
            color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            line=dict(color='#ffffff', width=1.5)
        )
    ))
    
    fig.update_layout(
        title=dict(text='Product Performance Overview (Multi-Metric Hover)', font=dict(size=18, family='Arial')),
        xaxis_title='Product Line',
        yaxis_title='Total Revenue ($)',
        template='plotly_white',
        height=550
    )
    
    fig.write_html('interactive_charts/chart2_product_performance.html')
    fig.write_html('chart2_product_performance.html')
    print("Chart 2 exported to interactive_charts/chart2_product_performance.html")


def create_chart3():
    """
    Task 2: Chart 3 - Metric Selector Dropdown Filter (Revenue, Profit, Order Count)
    """
    print("Building Chart 3: Metric Selector Dropdown...")
    
    products = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on']
    revenue_data = [5200000, 3800000, 2900000, 1850000, 950000]
    profit_data = [3640000, 2280000, 1450000, 1295000, 380000]
    order_count = [14200, 4800, 1250, 18500, 3800]
    
    fig = go.Figure()
    
    # Trace 0: Revenue
    fig.add_trace(go.Bar(
        x=products,
        y=revenue_data,
        name='Revenue',
        marker=dict(color='#1f77b4'),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>',
        visible=True
    ))
    
    # Trace 1: Profit
    fig.add_trace(go.Bar(
        x=products,
        y=profit_data,
        name='Profit',
        marker=dict(color='#2ca02c'),
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>',
        visible=False
    ))
    
    # Trace 2: Order Count
    fig.add_trace(go.Bar(
        x=products,
        y=order_count,
        name='Order Count',
        marker=dict(color='#ff7f0e'),
        hovertemplate='<b>%{x}</b><br>Order Count: %{y:,}<extra></extra>',
        visible=False
    ))
    
    # Updatemenus dropdown configuration
    dropdown_buttons = [
        dict(
            label='Revenue ($)',
            method='update',
            args=[
                {'visible': [True, False, False]},
                {
                    'title': 'Product Revenue ($)',
                    'yaxis': {'title': 'Revenue ($)'}
                }
            ]
        ),
        dict(
            label='Profit ($)',
            method='update',
            args=[
                {'visible': [False, True, False]},
                {
                    'title': 'Product Profit ($)',
                    'yaxis': {'title': 'Profit ($)'}
                }
            ]
        ),
        dict(
            label='Order Count',
            method='update',
            args=[
                {'visible': [False, False, True]},
                {
                    'title': 'Product Order Count',
                    'yaxis': {'title': 'Total Orders'}
                }
            ]
        )
    ]
    
    fig.update_layout(
        title=dict(text='Product Performance (Select Metric View)', font=dict(size=18, family='Arial')),
        xaxis_title='Product Line',
        yaxis_title='Revenue ($)',
        template='plotly_white',
        height=550,
        updatemenus=[dict(
            active=0,
            x=0.0,
            xanchor='left',
            y=1.15,
            yanchor='top',
            buttons=dropdown_buttons,
            showactive=True
        )]
    )
    
    fig.write_html('interactive_charts/chart3_metric_selector.html')
    fig.write_html('chart3_metric_selector.html')
    print("Chart 3 exported to interactive_charts/chart3_metric_selector.html")


def create_chart4():
    """
    Task 3: Chart 4 - Interactive Scatter with Native Zoom, Pan, Select & Reset
    """
    print("Building Chart 4: Interactive Zoom, Pan, Select Scatter...")
    
    np.random.seed(42)
    n = 120
    marketing_spend = np.random.uniform(5000, 95000, n)
    ltv = 4.5 * marketing_spend + np.random.normal(0, 35000, n) + 25000
    customer_ids = [f"CUST-{1000+i}" for i in range(n)]
    regions = np.random.choice(['North America', 'EMEA', 'APAC', 'LATAM'], size=n)
    
    custom_matrix = np.column_stack((customer_ids, regions))
    
    fig = go.Figure(data=go.Scatter(
        x=marketing_spend,
        y=ltv,
        mode='markers',
        customdata=custom_matrix,
        hovertemplate=(
            '<b>%{customdata[0]} (%{customdata[1]})</b><br>' +
            'Marketing Spend: $%{x:,.2f}<br>' +
            'Customer LTV: $%{y:,.2f}<br>' +
            '<extra></extra>'
        ),
        marker=dict(
            size=10,
            color=marketing_spend,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Spend ($)')
        )
    ))
    
    fig.update_layout(
        title=dict(text='Marketing Acquisition Spend vs. Customer Lifetime Value (LTV)', font=dict(size=18, family='Arial')),
        xaxis_title='Marketing Spend ($)',
        yaxis_title='Customer LTV ($)',
        dragmode='zoom',
        hovermode='closest',
        template='plotly_white',
        height=600
    )
    
    fig.write_html('interactive_charts/chart4_interactive.html')
    fig.write_html('chart4_interactive.html')
    print("Chart 4 exported to interactive_charts/chart4_interactive.html")


def create_chart5():
    """
    Task 5: Chart 5 - Time Series with Range Selector Buttons & Range Slider
    """
    print("Building Chart 5: Time Series with Range Selector & Slider...")
    
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='W')
    base_rev = np.linspace(250000, 680000, len(dates))
    seasonality = 80000 * np.sin(np.linspace(0, 4*np.pi, len(dates)))
    revenue = base_rev + seasonality + np.random.normal(0, 25000, len(dates))
    
    fig = go.Figure(data=go.Scatter(
        x=dates,
        y=revenue,
        mode='lines',
        hovertemplate='<b>Week of %{x|%b %d, %Y}</b><br>Weekly Revenue: $%{y:,.2f}<extra></extra>',
        line=dict(color='#2ca02c', width=2.5)
    ))
    
    fig.update_layout(
        title=dict(text='Weekly Revenue Trend with Date Range Selector & Range Slider', font=dict(size=18, family='Arial')),
        xaxis_title='Date',
        yaxis_title='Weekly Revenue ($)',
        template='plotly_white',
        height=600
    )
    
    # Configure date range selector buttons and range slider
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
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
    
    fig.write_html('interactive_charts/chart5_date_rangeslider.html')
    fig.write_html('chart5_date_rangeslider.html')
    print("Chart 5 exported to interactive_charts/chart5_date_rangeslider.html")


def main():
    """Executes chart generation."""
    print("=== Generating Interactive Plotly Charts ===")
    ensure_directories()
    create_chart1()
    create_chart2()
    create_chart3()
    create_chart4()
    create_chart5()
    print("=== All 5 interactive Plotly HTML charts generated successfully ===")


if __name__ == '__main__':
    main()
