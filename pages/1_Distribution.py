import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data_utils import CLASS_COL, BENIGN_VAL, MALICIOUS_VAL, get_dataframe, get_numeric_cols

st.set_page_config(page_title="Distribution", page_icon="📈", layout="wide")

st.title("📈 Distribution — Malicious vs Benign")
st.markdown(
    "Compares how a selected score is spread across benign and malicious packages. "
    "Curves are **density-normalized** (not raw counts) so the malicious class — a small "
    "minority in this dataset — isn't visually flattened by the much larger benign class."
)

df = get_dataframe(sidebar_label="Dataset")

if CLASS_COL not in df.columns:
    st.error(
        f"This CSV has no `{CLASS_COL}` column, which this page requires to separate "
        "benign vs malicious packages."
    )
    st.caption(f"Columns found: {', '.join(df.columns)}")
    st.stop()

numeric_cols = get_numeric_cols(df)

if not numeric_cols:
    st.info("No numeric metric/aspect/score columns found besides the classification column.")
    st.stop()

st.markdown("---")

metric = st.selectbox("Metric / Attribute / Aspect / Composite Score", numeric_cols)

benign_data = df.loc[df[CLASS_COL] == BENIGN_VAL, metric].dropna()
malicious_data = df.loc[df[CLASS_COL] == MALICIOUS_VAL, metric].dropna()

# Shared bin edges so both classes are compared on the same x-axis grid
combined = pd.concat([benign_data, malicious_data])
bin_edges = np.linspace(combined.min(), combined.max(), 41)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

benign_hist, _ = np.histogram(benign_data, bins=bin_edges, density=True)
malicious_hist, _ = np.histogram(malicious_data, bins=bin_edges, density=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=bin_centers,
    y=benign_hist,
    mode="lines",
    name=f"Benign (n={len(benign_data):,})",
    line=dict(color="#1f77b4", width=2, shape="spline"),
    fill="tozeroy",
    fillcolor="rgba(31, 119, 180, 0.15)",
))
fig.add_trace(go.Scatter(
    x=bin_centers,
    y=malicious_hist,
    mode="lines",
    name=f"Malicious (n={len(malicious_data):,})",
    line=dict(color="#d62728", width=2, shape="spline"),
    fill="tozeroy",
    fillcolor="rgba(214, 39, 40, 0.15)",
))
fig.update_layout(
    title=f"Distribution of {metric} — Benign vs Malicious (density-normalized)",
    xaxis_title=metric,
    yaxis_title="Density",
    legend_title="Class",
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Line-based frequency curves (density-normalized) instead of overlapping bars, so neither "
    "class visually overpowers the other despite the class imbalance."
)
