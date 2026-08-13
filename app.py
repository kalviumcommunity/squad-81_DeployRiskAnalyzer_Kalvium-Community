"""
Streamlit Analytics App Shell with File Upload & Dynamic Preview Engine
Supports CSV and JSON file uploads, automated data profiling, column summary tables,
descriptive statistics, error handling, and downstream charting.
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

# Configure Page Layout - Wide mode
st.set_page_config(
    page_title="Analytics Dashboard & Dataset Upload System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to generate default benchmark dataset
@st.cache_data
def load_default_benchmark_data():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=180, freq='D')
    products = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on']
    n = 500
    df = pd.DataFrame({
        'order_id': [f"ORD-{1000+i}" for i in range(n)],
        'order_date': np.random.choice(dates, size=n),
        'product_line': np.random.choice(products, size=n, p=[0.35, 0.25, 0.15, 0.15, 0.10]),
        'amount': np.round(np.random.normal(4500, 1200, size=n), 2),
        'churn_risk_score': np.round(np.random.uniform(0.01, 0.99, size=n), 3)
    }).sort_values('order_date').reset_index(drop=True)
    return df

# Task 1 & Task 4: File Upload & Robust Error Handling
st.sidebar.title("🧭 Navigation & Data Source")
page = st.sidebar.radio(
    "Go to Section",
    ["Overview", "Dataset Upload & Preview", "Trends", "Segments", "Data Explorer"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.header("📤 Bring Your Own Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset (CSV or JSON)",
    type=["csv", "json"],
    help="Upload a CSV or JSON file to analyze custom dataset dynamically."
)

df = None
is_custom_upload = False

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.sidebar.error("Unsupported file type. Please upload a .csv or .json file.")
            st.stop()
            
        if len(df) == 0:
            st.sidebar.warning("The uploaded file is empty. Please check your data.")
            st.stop()
            
        is_custom_upload = True
        st.sidebar.success(f"✓ Loaded: `{uploaded_file.name}` ({len(df):,} rows, {len(df.columns)} cols)")
    except Exception as e:
        st.sidebar.error(f"Could not read this file. Check the format and try again. ({str(e)})")
        st.stop()
else:
    st.sidebar.info("No file uploaded. Using default benchmark sales dataset.")
    df = load_default_benchmark_data()

# Store active DataFrame in session state for downstream persistence
st.session_state['active_df'] = df

# Page 1: Overview
if page == "Overview":
    st.title("📊 Executive Business Overview")
    st.caption("Key Performance Indicators & Top-Level Dashboard Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Total Revenue", value=f"${df['amount'].sum():,.2f}" if 'amount' in df.columns else "$5.24M", delta="+12.5%")
    with col2:
        st.metric(label="Total Records", value=f"{len(df):,}", delta="+5.2%")
    with col3:
        st.metric(label="Avg Value", value=f"${df['amount'].mean():,.2f}" if 'amount' in df.columns else "$45.00", delta="+2.1%")
    with col4:
        st.metric(label="Churn Rate", value="5.2%", delta="-2.8%", delta_color="inverse")
    with col5:
        st.metric(label="Customer NPS", value="72 / 100", delta="+4 pts")

    st.divider()
    st.info("💡 Navigate to **Dataset Upload & Preview** in the sidebar to inspect full dataset profiling.")

# Page 2: Dataset Upload & Preview (Tasks 2, 3, 4, 5)
elif page == "Dataset Upload & Preview":
    st.title("📂 Dataset Upload & Dynamic Preview System")
    st.caption("Automatic data profiling, schema validation, and summary statistics")
    
    if is_custom_upload:
        st.success(f"🎉 Custom Dataset Active: `{uploaded_file.name}`")
    else:
        st.info("ℹ️ Displaying default benchmark dataset. Use the sidebar file uploader to analyze custom CSV/JSON files.")
        
    st.header("Dataset Overview & Metrics")
    
    # Task 2: Data shape summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", str(len(df.columns)))
    with col3:
        total_nulls = int(df.isnull().sum().sum())
        total_cells = int(df.shape[0] * df.shape[1])
        null_pct = (total_nulls / total_cells * 100.0) if total_cells > 0 else 0.0
        st.metric("Overall Null %", f"{null_pct:.1f}%")
        
    st.divider()
    
    # Task 2: First 10 Rows Preview
    st.subheader("First 10 Rows Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.divider()
    
    # Task 2: Column Summary Table
    st.subheader("Column Summary & Schema Profile")
    summary = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Non-Null Count": df.notnull().sum().values,
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
    })
    st.dataframe(summary, use_container_width=True)
    
    st.divider()
    
    # Task 3: Basic Descriptive Statistics
    st.subheader("Descriptive Statistics (Numeric Columns)")
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        st.dataframe(df.describe().T, use_container_width=True)
    else:
        st.info("No numeric columns found for descriptive statistics.")
        
    st.divider()
    
    # Task 5: Downstream Exploration (Charts & Selectbox Filtering)
    st.subheader("Quick Data Exploration & Visualisation")
    numeric_cols = numeric_df.columns.tolist()
    
    if numeric_cols:
        col_select, col_chart = st.columns([1, 2])
        with col_select:
            selected_col = st.selectbox("Select a numeric column to visualize:", numeric_cols)
            st.markdown(f"**Column Summary for `{selected_col}`:**")
            st.write(f"- Mean: {df[selected_col].mean():,.2f}")
            st.write(f"- Min: {df[selected_col].min():,.2f}")
            st.write(f"- Max: {df[selected_col].max():,.2f}")
            
        with col_chart:
            fig = go.Figure(data=go.Histogram(
                x=df[selected_col],
                nbinsx=20,
                marker=dict(color='#1f77b4', line=dict(color='white', width=1))
            ))
            fig.update_layout(
                title=f"Distribution of `{selected_col}`",
                xaxis_title=selected_col,
                yaxis_title="Frequency",
                template="plotly_white",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload a dataset containing numeric values to enable interactive distribution charts.")

elif page == "Trends":
    st.title("📈 Time-Series Trends")
    if 'amount' in df.columns and 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
        daily = df.groupby('order_date')['amount'].sum().reset_index()
        fig = go.Figure(data=go.Scatter(x=daily['order_date'], y=daily['amount'], mode='lines', line=dict(color='#2ca02c')))
        fig.update_layout(title="Daily Amount Trend", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload dataset with `order_date` and `amount` columns to view trends.")

elif page == "Segments":
    st.title("🧩 Segment Breakdown")
    if 'product_line' in df.columns and 'amount' in df.columns:
        seg = df.groupby('product_line')['amount'].sum().reset_index()
        fig = go.Figure(data=go.Bar(x=seg['product_line'], y=seg['amount'], marker=dict(color='#ff7f0e')))
        fig.update_layout(title="Amount by Product Line", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload dataset with categorical columns to view segment breakdown.")

elif page == "Data Explorer":
    st.title("🔍 Data Explorer & Raw View")
    st.dataframe(df, use_container_width=True)
    st.download_button(
        label="📥 Download Current Data CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="active_dataset.csv",
        mime="text/csv"
    )
