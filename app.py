"""
Streamlit Interactive Widgets & Reactive Filter Chain System
Implements Date Picker, Multi-Select, Range Slider, and Radio Button widgets,
chained DataFrame filtering, default value management, empty state handling, and filter reset.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure Page Layout
st.set_page_config(
    page_title="Interactive Filters & Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Shared Data Caching for Baseline Dataset
@st.cache_data
def load_base_dataset():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=180, freq='D')
    products = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on']
    regions = ['North America', 'EMEA', 'APAC', 'LATAM']
    n = 1200
    
    df = pd.DataFrame({
        'order_id': [f"ORD-{10000+i}" for i in range(n)],
        'order_date': np.random.choice(dates, size=n),
        'product_line': np.random.choice(products, size=n, p=[0.35, 0.25, 0.15, 0.15, 0.10]),
        'region': np.random.choice(regions, size=n),
        'amount': np.round(np.random.normal(5200, 1500, size=n), 2),
        'churn_risk_score': np.round(np.random.uniform(0.01, 0.99, size=n), 3)
    }).sort_values('order_date').reset_index(drop=True)
    return df

base_df = load_base_dataset()

# Handle custom file upload or use base dataset
st.sidebar.title("🧭 Navigation & Filters")

page = st.sidebar.radio(
    "Go to Section",
    ["Overview", "Interactive Filter Explorer", "Trends", "Segments"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Filter Controls")

# Allow file upload
uploaded_file = st.sidebar.file_uploader("Upload CSV/JSON (Optional)", type=["csv", "json"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        df = base_df
else:
    df = base_df.copy()

# Ensure order_date is datetime
if 'order_date' in df.columns:
    df['order_date'] = pd.to_datetime(df['order_date'])

# Task 1 & Task 3: Interactive Widgets with Meaningful Defaults

# Task 5: Reset Filters Mechanism Button
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

st.sidebar.markdown("---")

# Widget 1: Date Range Picker (Defaults to full dataset range)
if 'order_date' in df.columns:
    min_date_val = df['order_date'].min().date()
    max_date_val = df['order_date'].max().date()
    
    date_range = st.sidebar.date_input(
        "1. Date Range Picker",
        value=(min_date_val, max_date_val),
        min_value=min_date_val,
        max_value=max_date_val
    )
else:
    date_range = None

# Widget 2: Multi-Select for Categories (Defaults to ALL items selected)
if 'product_line' in df.columns:
    all_products = sorted(df['product_line'].dropna().unique().tolist())
    selected_products = st.sidebar.multiselect(
        "2. Product Line Multi-Select",
        options=all_products,
        default=all_products
    )
else:
    selected_products = []

# Widget 3: Range Slider for Numeric Values (Defaults to full min/max range)
if 'amount' in df.columns:
    min_amt = float(df['amount'].min())
    max_amt = float(df['amount'].max())
    
    amount_range = st.sidebar.slider(
        "3. Revenue Amount Range ($)",
        min_value=min_amt,
        max_value=max_amt,
        value=(min_amt, max_amt),
        step=100.0
    )
else:
    amount_range = (0.0, 100000.0)

# Widget 4: Radio Button for View Granularity / Aggregation
view_granularity = st.sidebar.radio(
    "4. Chart Granularity",
    ["Daily", "Weekly", "Monthly"],
    index=0
)

# Task 2: Chained DataFrame Filtering Logic
filtered_df = df.copy()

if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[
        (filtered_df['order_date'].dt.date >= start_d) &
        (filtered_df['order_date'].dt.date <= end_d)
    ]

if selected_products and 'product_line' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['product_line'].isin(selected_products)]

if amount_range and 'amount' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['amount'] >= amount_range[0]) &
        (filtered_df['amount'] <= amount_range[1])
    ]

# Task 4: Empty Filter Combination Handling
if len(filtered_df) == 0:
    st.warning("⚠️ **No data matches the current filter criteria.** Try broadening your selections or clicking 'Reset All Filters' in the sidebar.")
    st.info("Tip: Check if the date range, product selections, or amount sliders are too restrictive.")
    st.stop()

# Store active filtered DataFrame in session state
st.session_state['filtered_df'] = filtered_df

# Page Rendering Logic
if page == "Overview":
    st.title("📊 Executive Business Overview")
    st.caption(f"Displaying {len(filtered_df):,} of {len(df):,} total records")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${filtered_df['amount'].sum():,.2f}" if 'amount' in filtered_df.columns else "$0")
    with col2:
        st.metric("Filtered Records", f"{len(filtered_df):,}")
    with col3:
        st.metric("Average Order Value", f"${filtered_df['amount'].mean():,.2f}" if 'amount' in filtered_df.columns else "$0")
    with col4:
        st.metric("Selected Products", f"{filtered_df['product_line'].nunique()}" if 'product_line' in filtered_df.columns else "N/A")

    st.divider()
    st.dataframe(filtered_df.head(10), use_container_width=True)

elif page == "Interactive Filter Explorer":
    st.title("⚡ Interactive Widgets & Filter Explorer")
    st.caption("All widgets in the sidebar reactively update downstream metrics, charts, and tables.")
    
    # Summary Metrics Row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Filtered Rows", f"{len(filtered_df):,}")
    col_m2.metric("Total Filtered Revenue", f"${filtered_df['amount'].sum():,.2f}")
    col_m3.metric("Min Amount Filtered", f"${filtered_df['amount'].min():,.2f}")
    col_m4.metric("Max Amount Filtered", f"${filtered_df['amount'].max():,.2f}")
    
    st.divider()
    
    # Reactive Time-Series Chart
    st.header("1. Reactive Revenue Trend Chart")
    
    if view_granularity == "Daily":
        time_grp = filtered_df.groupby('order_date')['amount'].sum().reset_index()
    elif view_granularity == "Weekly":
        time_grp = filtered_df.groupby(pd.Grouper(key='order_date', freq='W-MON'))['amount'].sum().reset_index()
    else:
        time_grp = filtered_df.groupby(pd.Grouper(key='order_date', freq='ME'))['amount'].sum().reset_index()
        
    fig_trend = go.Figure(data=go.Scatter(
        x=time_grp['order_date'],
        y=time_grp['amount'],
        mode='lines+markers',
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=6),
        hovertemplate='<b>Date: %{x|%b %d, %Y}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    fig_trend.update_layout(
        title=f"Filtered Revenue Trend ({view_granularity} Granularity)",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()
    
    # Reactive Categorical Bar Chart
    st.header("2. Reactive Product Revenue Share")
    prod_grp = filtered_df.groupby('product_line')['amount'].sum().reset_index()
    
    fig_bar = go.Figure(data=go.Bar(
        x=prod_grp['product_line'],
        y=prod_grp['amount'],
        marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']),
        hovertemplate='<b>Product: %{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    fig_bar.update_layout(
        title="Filtered Revenue by Product Line",
        xaxis_title="Product Line",
        yaxis_title="Total Revenue ($)",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    
    # Filtered Table View
    st.header("3. Filtered Data Table")
    st.dataframe(filtered_df, use_container_width=True)

elif page == "Trends":
    st.title("📈 Trend Analysis")
    st.dataframe(filtered_df[['order_date', 'product_line', 'amount']].head(20), use_container_width=True)

elif page == "Segments":
    st.title("🧩 Segment Breakdown")
    st.dataframe(filtered_df.groupby('product_line')['amount'].agg(['count', 'sum', 'mean']), use_container_width=True)
