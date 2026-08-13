"""
Multipage App Section: Business Overview Page
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Business Overview", page_icon="📊", layout="wide")

st.title("📊 Business Overview")
st.caption("Multipage App Convention — Executive Summary & Real-Time Performance Status")

# Top row KPI metrics
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

st.divider()

st.header("Executive Highlights")
st.write("Overview metrics and strategic summary indicators.")

with st.expander("📖 About These Metrics"):
    st.write("Revenue, active users, and churn rate calculations follow core data layer definitions.")
