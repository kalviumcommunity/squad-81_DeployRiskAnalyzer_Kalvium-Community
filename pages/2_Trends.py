"""
Multipage App Section: Trend Analysis Page
"""

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Trend Analysis", page_icon="📈", layout="wide")

st.title("📈 Trend Analysis")
st.header("Revenue & Retention Trends")
st.subheader("12-Month Performance Trajectory")

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthly_rev = [4.1, 4.3, 4.5, 4.7, 4.8, 5.0, 5.1, 3.8, 5.3, 5.5, 5.7, 6.1]

fig = go.Figure(data=go.Scatter(x=months, y=monthly_rev, mode='lines+markers', line=dict(color='#2ca02c', width=3)))
fig.update_layout(title="Monthly Revenue Trend ($M)", template="plotly_white", height=380)

st.plotly_chart(fig, use_container_width=True)

st.divider()

with st.expander("🔍 Historical Seasonality Notes"):
    st.write("Seasonal adjustments applied for August summer slowdown.")
