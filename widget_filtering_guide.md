# Streamlit Filters & Interactive Widgets Guide

## Executive Overview
Interactive widgets turn static data displays into responsive analytical applications. By wiring date pickers, multi-select dropdowns, range sliders, and radio buttons into a reactive filter chain, business users can explore any slice of their data independently without modifying code.

---

## 1. Filter Chain Architecture & Component Mapping

```
[ Sidebar Widgets (Date Input, Multi-Select, Slider, Radio) ]
                             │
                             ▼
               [ Reactive Filter Chain Logic ]
                             │
                             ▼
         [ Empty DataFrame Check (len(df) == 0) ]
              ├── If Empty: st.warning() + st.stop()
              └── If Valid: Update st.session_state
                             │
                             ▼
    [ Reactive Downstream Output (Metrics, Charts, Tables) ]
```

---

## 2. Widget Implementation Matrix & Default Strategies

| Widget Type | Streamlit Function | Target Data Type | Default Strategy (Task 3) |
| :--- | :--- | :--- | :--- |
| **Date Range Picker** | `st.sidebar.date_input` | Datetime / Date | Full dataset range `(min_date, max_date)` |
| **Multi-Select Dropdown** | `st.sidebar.multiselect` | Categorical / String | All unique categories selected `default=all_items` |
| **Numeric Range Slider** | `st.sidebar.slider` | Float / Integer | Full dataset range `value=(min_val, max_val)` |
| **Radio Button** | `st.sidebar.radio` | Mode / Granularity | Primary default option (e.g. `"Daily"`) |

---

## 3. Filter Chain Code Pattern (Task 1 & Task 2)

```python
# 1. Widget inputs with full defaults
date_range = st.sidebar.date_input("Date Range", value=(df["date"].min(), df["date"].max()))
selected_segments = st.sidebar.multiselect("Segments", options=all_segments, default=all_segments)
min_rev, max_rev = st.sidebar.slider("Revenue Range", min_value=min_val, max_value=max_val, value=(min_val, max_val))

# 2. Chained Boolean Indexing
filtered_df = df[
    (df["date"] >= pd.Timestamp(date_range[0])) &
    (df["date"] <= pd.Timestamp(date_range[1])) &
    (df["segment"].isin(selected_segments)) &
    (df["revenue"] >= min_rev) &
    (df["revenue"] <= max_rev)
]

# 3. Empty State Protection (Task 4)
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the current filter criteria. Try broadening your selection.")
    st.stop()

# 4. Filter Reset Mechanism (Task 5)
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()
```

---

## 4. Answer to Follow-Up Question: Cascading / Linked Dependent Dropdowns

### Question:
*How would you implement linked/cascading dropdowns where the options in a second dropdown depend dynamically on the selection made in the first dropdown (e.g., selecting a "Region" filters the available "Cities" or "Product Lines")?*

### Solution & Technical Implementation:

To build dependent cascading dropdowns, query the DataFrame based on the selection of the primary widget (`selected_region`) to extract the dynamic subset of valid secondary options before instantiating the secondary widget (`selected_city`).

```python
import streamlit as st
import pandas as pd

# Sample dataset with regions and cities
data = pd.DataFrame({
    'Region': ['North America', 'North America', 'EMEA', 'EMEA', 'APAC', 'APAC'],
    'City': ['New York', 'Toronto', 'London', 'Paris', 'Tokyo', 'Sydney'],
    'Sales': [120000, 95000, 110000, 85000, 130000, 90000]
})

st.sidebar.header("🎯 Linked Cascading Filters")

# Primary Dropdown: Region Selection
all_regions = sorted(data['Region'].unique().tolist())
selected_region = st.sidebar.selectbox(
    "1. Select Region",
    options=all_regions,
    index=0
)

# Dynamic Secondary Options: Filter dataset based on selected primary region
valid_cities = data[data['Region'] == selected_region]['City'].unique().tolist()

# Secondary Dropdown: City Selection (options update reactively!)
selected_cities = st.sidebar.multiselect(
    f"2. Select Cities in {selected_region}",
    options=valid_cities,
    default=valid_cities
)

# Apply combined filter
cascaded_df = data[
    (data['Region'] == selected_region) &
    (data['City'].isin(selected_cities))
]

st.subheader(f"Sales Data for {selected_region}")
st.dataframe(cascaded_df, use_container_width=True)
```

### Key Principles of Linked Dropdowns:
1. **Dynamic Execution**: Because Streamlit reruns the script upon selecting `selected_region`, `valid_cities` is recomputed immediately before the secondary `st.multiselect` renders.
2. **Session State Key Reset**: If switching the primary dropdown makes previously selected secondary options invalid, wrap the selection update in `st.session_state` to reset the secondary selection automatically.
