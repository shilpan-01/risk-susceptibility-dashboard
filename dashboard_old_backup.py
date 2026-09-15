import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="RubyGems Investigative Study",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Sidebar: Upload ----------
st.sidebar.title("💎 Upload Data")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded is None:
    st.title("Software Supply Chain RubyGems Investigative Study")
    st.info("Upload a CSV in the left sidebar to begin.")
    st.stop()

df = pd.read_csv(uploaded)
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
all_cols = df.columns.tolist()

# ---------- Sidebar: Classification column ----------
default_guess = 0
for kw in ["label", "classification", "verdict", "status", "malicious", "class"]:
    matches = [c for c in all_cols if kw in c.lower()]
    if matches:
        default_guess = all_cols.index(matches[0])
        break

st.sidebar.markdown("---")
class_col = st.sidebar.selectbox(
    "Classification column (benign / malicious)", all_cols, index=default_guess
)

# ---------- Main: Title ----------
st.title("Software Supply Chain RubyGems Investigative Study")

# ---------- KPIs + Pie Chart ----------
value_counts = df[class_col].value_counts()
total_packages = len(df)

benign_val = next((v for v in value_counts.index if "benign" in str(v).lower()), None)
malicious_val = next((v for v in value_counts.index if "malicious" in str(v).lower()), None)

k1, k2, k3 = st.columns(3)
k1.metric("Total Packages", f"{total_packages:,}")

if benign_val is not None and malicious_val is not None:
    k2.metric(f"Benign ({benign_val})", f"{value_counts[benign_val]:,}")
    k3.metric(f"Malicious ({malicious_val})", f"{value_counts[malicious_val]:,}")
else:
    top_two = value_counts.head(2)
    for col, (val, count) in zip([k2, k3], top_two.items()):
        col.metric(str(val), f"{count:,}")

pie_fig = px.pie(
    names=value_counts.index,
    values=value_counts.values,
    title=f"Package Breakdown by {class_col}",
    hole=0.4,
)
st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("---")

# ---------- Line Chart ----------
st.subheader("Line Chart")
if numeric_cols:
    line_metric = st.selectbox("Metric", numeric_cols, key="line_metric")
    line_color = class_col if class_col else None
    line_df = df.reset_index().rename(columns={"index": "row_index"})
    line_fig = px.line(
        line_df.sort_values(line_metric),
        x="row_index",
        y=line_metric,
        color=line_color,
        title=f"{line_metric} Across Packages",
    )
    st.plotly_chart(line_fig, use_container_width=True)
else:
    st.info("No numeric columns available for a line chart.")

st.markdown("---")

# ---------- Graph Options ----------
st.subheader("Graph Options")
graph_type = st.selectbox("Graph type", ["Histogram", "Scatter Plot", "Heatmap"])

if graph_type == "Histogram":
    if numeric_cols:
        hist_col = st.selectbox("Column", numeric_cols, key="hist_col")
        nbins = st.slider("Bins", 5, 100, 30)
        fig = px.histogram(df, x=hist_col, nbins=nbins, color=class_col, title=f"Distribution of {hist_col}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns available for a histogram.")

elif graph_type == "Scatter Plot":
    if len(numeric_cols) >= 2:
        c1, c2 = st.columns(2)
        with c1:
            x_axis = st.selectbox("X axis", numeric_cols, index=0, key="scatter_x")
        with c2:
            y_axis = st.selectbox("Y axis", numeric_cols, index=1, key="scatter_y")
        fig = px.scatter(df, x=x_axis, y=y_axis, color=class_col, title=f"{x_axis} vs {y_axis}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least two numeric columns for a scatter plot.")

elif graph_type == "Heatmap":
    if len(numeric_cols) >= 2:
        heatmap_cols = st.multiselect("Columns to include", numeric_cols, default=numeric_cols)
        if len(heatmap_cols) >= 2:
            corr = df[heatmap_cols].corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least two columns.")
    else:
        st.info("Need at least two numeric columns for a heatmap.")

st.markdown("---")

# ---------- Columns Selection Filter ----------
st.subheader("Column Selection")
selected_cols = st.multiselect(
    "Select numeric columns to summarize", numeric_cols, default=numeric_cols
)

st.markdown("---")

# ---------- Summary Table ----------
st.subheader("Summary Table")
if selected_cols:
    st.dataframe(df[selected_cols].describe().T, use_container_width=True)
else:
    st.info("Select at least one column above to see summary statistics.")