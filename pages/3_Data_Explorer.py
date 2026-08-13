"""
Multipage App Section: Data Explorer Page
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Explorer", page_icon="🔍", layout="wide")

st.title("🔍 Data Explorer")
st.header("Raw Transactions & Metadata")

np.random.seed(42)
df = pd.DataFrame({
    'order_id': [f"ORD-{1000+i}" for i in range(100)],
    'amount': np.round(np.random.normal(4500, 1000, 100), 2),
    'status': np.random.choice(['Completed', 'Pending', 'Shipped'], size=100)
})

st.dataframe(df, use_container_width=True)

st.divider()

with st.expander("📄 Schema Details"):
    st.json({"total_rows": len(df), "columns": list(df.columns)})
