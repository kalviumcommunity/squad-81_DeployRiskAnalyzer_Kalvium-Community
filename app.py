"""
Streamlit Application Shell & Navigation Scaffolding
Demonstrates multi-section layout architecture, sidebar navigation,
columns for horizontal metrics, expanders for progressive disclosure,
and visual hierarchy.
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

# Configure Page Layout - Wide mode, custom title & icon
st.set_page_config(
    page_title="Executive Analytics Dashboard Shell",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Shared Data Caching for Performance Optimization
@st.cache_data
def load_cached_data():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=180, freq='D')
    products = ['SaaS Platform', 'Enterprise Support', 'Consulting Service', 'API Access', 'Analytics Add-on']
    
    n = 1000
    df = pd.DataFrame({
        'order_id': [f"ORD-{1000+i}" for i in range(n)],
        'order_date': np.random.choice(dates, size=n),
        'product_line': np.random.choice(products, size=n, p=[0.35, 0.25, 0.15, 0.15, 0.10]),
        'amount': np.round(np.random.normal(4500, 1200, size=n), 2),
        'churn_flag': np.random.choice([0, 1], size=n, p=[0.93, 0.07])
    }).sort_values('order_date').reset_index(drop=True)
    return df

df = load_cached_data()

# Task 1: Sidebar Navigation Control
st.sidebar.title("🧭 Navigation")
st.sidebar.markdown("Select a dashboard section:")
page = st.sidebar.radio(
    "Go to Section",
    ["Overview", "Trends", "Segments", "Data Explorer"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Streamlit Execution Note:** Script reruns from top-to-bottom on every widget interaction. Data functions use `@st.cache_data` for speed.")

# Task 5: Content Above the Fold in Overview Section
if page == "Overview":
    # Main Page Title (Once per page)
    st.title("📊 Business Overview")
    st.caption("Executive Summary & Real-Time Performance Status")
    
    # Task 2 & 5: Top Row - 5 KPI Metric Cards in Columns (Above the Fold)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="Total Revenue", value="$5.24M", delta="+12.5%")
    with col2:
        st.metric(label="Active Users", value="2,500", delta="+5.2%")
    with col3:
        st.metric(label="Avg Order Value", value="$45.00", delta="+2.1%")
    with col4:
        st.metric(label="Churn Rate", value="5.2%", delta="-2.8%", delta_color="inverse")
    with col5:
        st.metric(label="Customer NPS", value="72 / 100", delta="+4 pts")

    # Task 3: Consistent Visual Hierarchy - Divider between sections
    st.divider()

    # Major Section Header
    st.header("Executive Highlights & Performance Overview")
    
    # Subheader for Subsection
    st.subheader("Quarterly Performance Summary")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        # Overview Chart
        daily_rev = df.groupby('order_date')['amount'].sum().reset_index()
        fig = go.Figure(data=go.Scatter(
            x=daily_rev['order_date'], y=daily_rev['amount'],
            mode='lines', line=dict(color='#1f77b4', width=2.5)
        ))
        fig.update_layout(title="Daily Revenue Trajectory", template="plotly_white", height=320)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown("### 🎯 Strategic Goals")
        st.markdown("- **Revenue Target**: Exceeded Q4 target by 8.5%.")
        st.markdown("- **Retention Target**: 2-hour support SLA reduced churn by 4x.")
        st.markdown("- **Expansion Target**: Enterprise support line grew 25% YoY.")

    # Task 2: Progressive Disclosure via Expander
    with st.expander("📖 About These Metrics & Calculation Methodology"):
        st.write("""
        **Data & Calculation Rules:**
        - **Total Revenue**: Sum of all completed order amounts in the current evaluation period.
        - **Active Users**: Count of unique customer IDs with login or transaction activity in the last 30 days.
        - **Churn Rate**: Percentage of active customer accounts that canceled subscriptions within the last 30 days. Lower is better (`delta_color='inverse'`).
        """)

elif page == "Trends":
    st.title("📈 Time-Series Trend Analysis")
    st.caption("Deep-dive historical trends and seasonal variation")
    
    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_rev = [4.1, 4.3, 4.5, 4.7, 4.8, 5.0, 5.1, 3.8, 5.3, 5.5, 5.7, 6.1]
    
    fig_trend = go.Figure(data=go.Scatter(
        x=months, y=monthly_rev, mode='lines+markers',
        line=dict(color='#2ca02c', width=3), marker=dict(size=8)
    ))
    fig_trend.update_layout(title="12-Month Revenue Growth ($M)", template="plotly_white", height=380)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()
    
    st.header("Customer Activity & Retention Trends")
    st.subheader("Active Customers Over Time")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("📌 **Key Takeaway**: Customer activity peaked in December following Q4 campaign launches.")
    with col_b:
        st.warning("⚠️ **Seasonal Note**: August exhibited a seasonal summer slowdown (-12% temporary dip).")

    with st.expander("🔍 View Detailed Seasonality & Historical Adjustments"):
        st.write("Historical trend calculations adjust for business calendar variations and holiday workdays.")

elif page == "Segments":
    st.title("🧩 Product & Customer Segment Breakdown")
    st.caption("Compare performance across product lines and market segments")
    
    st.header("Product Performance")
    st.subheader("Revenue Contribution by Product Line")
    
    prod_summary = df.groupby('product_line')['amount'].sum().reset_index()
    fig_pie = go.Figure(data=go.Pie(
        labels=prod_summary['product_line'],
        values=prod_summary['amount'],
        hole=0.4,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    ))
    fig_pie.update_layout(title="Revenue Share by Product Line", template="plotly_white", height=380)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    st.header("Customer Cohorts")
    st.subheader("Enterprise vs. SMB Performance")
    
    col_seg1, col_seg2 = st.columns(2)
    with col_seg1:
        st.markdown("#### Enterprise Tier")
        st.markdown("Generates **65% of total revenue** with 1% monthly churn.")
    with col_seg2:
        st.markdown("#### SMB Tier")
        st.markdown("Generates **35% of total revenue** with 8% monthly churn.")
        
    with st.expander("📑 View Segment Criteria & Definition Rules"):
        st.write("Enterprise accounts are defined as contracts >$10,000 ARR; SMB accounts are contracts <$10,000 ARR.")

elif page == "Data Explorer":
    st.title("🔍 Interactive Data Explorer & Export")
    st.caption("Filter raw transactions, inspect schemas, and download export reports")
    
    st.header("Filterable Dataset")
    st.subheader("Transactions Table")
    
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    st.header("Data Export")
    st.subheader("Download Artifacts")
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📊 Download CSV Dataset",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="transactions_export.csv",
            mime="text/csv"
        )
    with col_dl2:
        st.info("Export options for PDF and HTML reports are available in the export sidebar module.")
        
    with st.expander("📄 View Full Schema Metadata & Column Dictionary"):
        st.json({
            "record_count": len(df),
            "columns": list(df.columns),
            "date_range": [str(df['order_date'].min()), str(df['order_date'].max())]
        })
