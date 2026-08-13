# Dataset Upload & Dynamic Preview System Guide

## Executive Overview
The **Dataset Upload & Dynamic Preview System** enables business stakeholders and operational managers to bring their own CSV and JSON data files directly into the Streamlit analytics app. Within seconds of dragging a file into the browser, the application parses the raw file bytes into a Pandas DataFrame, executes automated schema validation, computes null percentage data quality metrics, renders a column summary table, and unlocks immediate downstream charting.

---

## 1. Core Architecture & Workflow

```
[ User Drags File (CSV / JSON) ] ──> [ st.file_uploader(type=["csv", "json"]) ]
                                                     │
                                                     ▼
                                     [ Extension & Empty File Validation ]
                                                     │
                                   ┌─────────────────┴─────────────────┐
                                   ▼                                   ▼
                            [ Invalid / Empty ]                 [ Valid File ]
                            - st.error()                        - pd.read_csv() / pd.read_json()
                            - st.stop() (Halt script)           - Calculate Null % & Column Summary
                                                                - Persist in st.session_state
                                                                - Render Preview & Downstream Charts
```

---

## 2. Component Implementation Breakdown

### Task 1: File Upload Handling (`st.file_uploader`)
```python
uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset (CSV or JSON)",
    type=["csv", "json"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".json"):
        df = pd.read_json(uploaded_file)
```

### Task 2: Data Shape & Column Summary Preview
```python
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

# Column summary table
summary = pd.DataFrame({
    "Column": df.columns,
    "Data Type": df.dtypes.astype(str).values,
    "Non-Null Count": df.notnull().sum().values,
    "Null Count": df.isnull().sum().values,
    "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
})
st.dataframe(summary, use_container_width=True)
```

### Task 3: Descriptive Statistics
```python
# Automatically isolates numeric columns and renders transposed describe statistics
st.subheader("Descriptive Statistics (Numeric Columns)")
st.dataframe(df.describe().T, use_container_width=True)
```

### Task 4: Error Handling without Python Tracebacks
```python
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".json"):
        df = pd.read_json(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload CSV or JSON.")
        st.stop()
        
    if len(df) == 0:
        st.warning("Uploaded file is empty. Please check your data.")
        st.stop()
except Exception as e:
    st.error("Could not read this file. Check the format and try again.")
    st.stop()
```

### Task 5: Downstream Usage & Session State Persistence
```python
st.session_state['active_df'] = df

# Interactive column visualization
numeric_cols = df.select_dtypes(include="number").columns.tolist()
if numeric_cols:
    selected_col = st.selectbox("Select a numeric column to visualize:", numeric_cols)
    fig = go.Figure(data=go.Histogram(x=df[selected_col]))
    st.plotly_chart(fig, use_container_width=True)
```

---

## 3. Answer to Follow-Up Question: Multi-File Upload & Auto-Merging

### Question:
*How would you extend the file upload system to support uploading multiple files simultaneously and merging them automatically?*

### Solution & Technical Implementation:

Set `accept_multiple_files=True` in `st.file_uploader`. When multiple files are uploaded, iterate through the list of file objects, load each into a DataFrame, align schemas or join on common primary keys, and concatenate into a unified master DataFrame (`pd.concat` or `pd.merge`).

```python
import streamlit as st
import pandas as pd

st.sidebar.header("📤 Multi-File Upload & Merging")

uploaded_files = st.sidebar.file_uploader(
    "Upload Multiple Files (CSV/JSON)",
    type=["csv", "json"],
    accept_multiple_files=True
)

if uploaded_files:
    dataframes = []
    
    for file in uploaded_files:
        try:
            if file.name.endswith(".csv"):
                temp_df = pd.read_csv(file)
            elif file.name.endswith(".json"):
                temp_df = pd.read_json(file)
            
            # Tag source file name for data lineage tracking
            temp_df['_source_file'] = file.name
            dataframes.append(temp_df)
            st.sidebar.caption(f"✓ Loaded `{file.name}` ({len(temp_df):,} rows)")
        except Exception as e:
            st.sidebar.error(f"Failed to parse `{file.name}`: {e}")
            
    if dataframes:
        try:
            # Union/Concatenate all uploaded files along row axis
            merged_df = pd.concat(dataframes, axis=0, ignore_index=True)
            st.success(f"🎉 Successfully merged {len(uploaded_files)} files into {len(merged_df):,} total rows!")
            
            # Display merged preview
            st.subheader("Merged Dataset Preview")
            st.dataframe(merged_df.head(10), use_container_width=True)
            
            # Store in session state for downstream use
            st.session_state['active_df'] = merged_df
        except Exception as e:
            st.error(f"Error during file concatenation: {e}")
            st.stop()
```

### Key Capabilities of Multi-File Merging:
1. **Schema Alignment**: `pd.concat(..., axis=0)` automatically matches identical column names while filling missing columns with NaN values if schemas differ slightly.
2. **Data Lineage Tagging**: Adding `_source_file` tracks which file supplied each row.
3. **Primary Key Join Option**: If files represent relational tables (e.g. `orders.csv` and `customers.csv`), use `pd.merge(orders_df, customers_df, on='customer_id')` to build a combined analytical view automatically.
