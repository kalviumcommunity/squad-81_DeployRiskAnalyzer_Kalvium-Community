"""
Streamlit Interactive Analytics Dashboard
Integrates interactive Plotly visualisations with Streamlit sidebar controls.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Configure Streamlit page layout
st.set_page_config(
    page_title="Interactive Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Interactive Sales Analytics Dashboard")
st.markdown("Explore revenue trends, product performance, and customer order breakdowns interactively.")

@st.cache_data
def load_data():
    """Generates synthetic sales transaction dataset for demonstration."""
    np.random.seed(42)
    n_records = 1500
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    random_dates = np.random.choice(dates, size=n_records)
    products = np.random.choice(
        ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on'],
        size=n_records,
        p=[0.35, 0.25, 0.15, 0.15, 0.10]
    )
    regions = np.random.choice(['North America', 'EMEA', 'APAC', 'LATAM'], size=n_records)
    
    # Revenue distribution based on product
    rev_map = {
        'SaaS Platform': (3500, 800),
        'Enterprise Support': (8000, 2000),
        'Consulting Service': (12000, 3500),
        'API Access': [1200, 300],
        'Analytics Add-on': [600, 150]
    }
    
    amounts = []
    for p in products:
        mean, std = rev_map[p]
        amounts.append(max(50.0, float(np.random.normal(mean, std))))
        
    df = pd.DataFrame({
        'order_id': [f"ORD-{10000+i}" for i in range(n_records)],
        'order_date': pd.to_datetime(random_dates),
        'product_line': products,
        'region': regions,
        'amount': np.round(amounts, 2)
    }).sort_values('order_date').reset_index(drop=True)
    
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🎯 Interactive Filters")

# Date range selection
min_date_val = df['order_date'].min().date()
max_date_val = df['order_date'].max().date()

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date_val, max_date_val),
    min_value=min_date_val,
    max_value=max_date_val
)

# Product line multi-select
available_products = list(df['product_line'].unique())
selected_products = st.sidebar.multiselect(
    "Filter Product Line",
    options=available_products,
    default=available_products
)

# Minimum order amount slider
max_order_amt = int(df['amount'].max())
min_amount = st.sidebar.slider(
    "Min Order Amount ($)",
    min_value=0,
    max_value=15000,
    value=500,
    step=250
)

# Apply filters
start_date, end_date = selected_date_range if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2 else (min_date_val, max_date_val)

filtered_df = df[
    (df['order_date'].dt.date >= start_date) &
    (df['order_date'].dt.date <= end_date) &
    (df['product_line'].isin(selected_products)) &
    (df['amount'] >= min_amount)
]

# Display KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Filtered Orders", f"{len(filtered_df):,}")
col2.metric("Total Revenue", f"${filtered_df['amount'].sum():,.2f}")
col3.metric("Average Order Value", f"${filtered_df['amount'].mean():,.2f}" if len(filtered_df) > 0 else "$0.00")
col4.metric("Active Product Lines", f"{filtered_df['product_line'].nunique()}")

st.divider()

# Layout Tabs
tab1, tab2, tab3 = st.tabs(["📈 Revenue Trend", "📊 Product Performance", "📄 Filtered Raw Data"])

with tab1:
    st.subheader("Daily Revenue Trend over Time")
    daily_rev = filtered_df.groupby('order_date').agg(
        total_revenue=('amount', 'sum'),
        order_count=('amount', 'count')
    ).reset_index()
    
    fig1 = go.Figure(data=go.Scatter(
        x=daily_rev['order_date'],
        y=daily_rev['total_revenue'],
        mode='lines+markers',
        customdata=daily_rev['order_count'],
        hovertemplate=(
            '<b>Date: %{x|%Y-%m-%d}</b><br>' +
            'Revenue: $%{y:,.2f}<br>' +
            'Orders: %{customdata:,}<br>' +
            '<extra></extra>'
        ),
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=6, color='#1f77b4')
    ))
    
    fig1.update_layout(
        title="Interactive Daily Revenue Trend",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode="x unified",
        template="plotly_white",
        height=500
    )
    
    # Render Plotly interactive chart in Streamlit
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Product Line Revenue & Performance Breakdown")
    prod_perf = filtered_df.groupby('product_line').agg(
        revenue=('amount', 'sum'),
        orders=('amount', 'count'),
        avg_order=('amount', 'mean')
    ).reset_index()
    
    fig2 = go.Figure(data=go.Bar(
        x=prod_perf['product_line'],
        y=prod_perf['revenue'],
        customdata=np.column_stack((prod_perf['orders'], prod_perf['avg_order'])),
        hovertemplate=(
            '<b>%{x}</b><br>' +
            'Total Revenue: $%{y:,.2f}<br>' +
            'Total Orders: %{customdata[0]:,}<br>' +
            'Avg Order Value: $%{customdata[1]:,.2f}<br>' +
            '<extra></extra>'
        ),
        marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    ))
    
    fig2.update_layout(
        title="Total Revenue by Product Line",
        xaxis_title="Product Line",
        yaxis_title="Revenue ($)",
        template="plotly_white",
        height=500
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Filtered Transactions Dataset")
    st.dataframe(filtered_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 Built with Streamlit & Plotly Interactive Chart Engine.")
