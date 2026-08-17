import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Data ----------
@st.cache_data
def load_sample_data():
    rng = np.random.default_rng(42)
    dates = pd.date_range(end=datetime.today(), periods=180, freq="D")
    regions = ["North", "South", "East", "West"]
    categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]

    rows = []
    for d in dates:
        for _ in range(rng.integers(3, 8)):
            rows.append({
                "date": d,
                "region": rng.choice(regions),
                "category": rng.choice(categories),
                "sales": round(rng.uniform(50, 2000), 2),
                "units": int(rng.integers(1, 25)),
                "customer_rating": round(rng.uniform(2.5, 5.0), 1),
            })
    return pd.DataFrame(rows)


def load_data():
    uploaded = st.sidebar.file_uploader("Upload a CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        # Try to parse a date-like column automatically
        for col in df.columns:
            if "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                    df = df.rename(columns={col: "date"})
                    break
                except Exception:
                    pass
        return df, True
    return load_sample_data(), False


# ---------- Sidebar ----------
st.sidebar.title("📊 Dashboard Controls")
df, is_uploaded = load_data()

if not is_uploaded:
    st.sidebar.info("Showing sample data. Upload your own CSV to replace it.")

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = [c for c in df.select_dtypes(include="object").columns.tolist()]
has_date = "date" in df.columns

if has_date:
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.sidebar.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        df = df[(df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))]

filter_col = None
if categorical_cols:
    filter_col = st.sidebar.selectbox("Filter by column", ["(none)"] + categorical_cols)
    if filter_col != "(none)":
        options = sorted(df[filter_col].dropna().unique().tolist())
        selected = st.sidebar.multiselect(f"Select {filter_col}", options, default=options)
        df = df[df[filter_col].isin(selected)]

st.sidebar.markdown("---")
st.sidebar.caption(f"{len(df):,} rows after filters")

# ---------- Header ----------
st.title("📊 Interactive Dashboard")
st.caption("Upload your own CSV in the sidebar, or explore the sample dataset below.")

# ---------- KPIs ----------
if numeric_cols:
    kpi_cols = st.columns(min(len(numeric_cols), 4))
    for i, col in enumerate(numeric_cols[:4]):
        with kpi_cols[i]:
            total = df[col].sum()
            avg = df[col].mean()
            st.metric(label=f"Total {col}", value=f"{total:,.0f}", delta=f"avg {avg:,.1f}")
else:
    st.metric("Rows", len(df))

st.markdown("---")

# ---------- Charts ----------
tab1, tab2, tab3, tab4 = st.tabs(["Trend", "Breakdown", "Distribution", "Raw Data"])

with tab1:
    if has_date and numeric_cols:
        metric = st.selectbox("Metric over time", numeric_cols, key="trend_metric")
        trend = df.groupby("date", as_index=False)[metric].sum()
        fig = px.line(trend, x="date", y=metric, title=f"{metric.title()} Over Time")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date column detected — trend chart unavailable for this dataset.")

with tab2:
    if categorical_cols and numeric_cols:
        c1, c2 = st.columns(2)
        with c1:
            group_col = st.selectbox("Group by", categorical_cols, key="group_col")
        with c2:
            metric2 = st.selectbox("Metric", numeric_cols, key="breakdown_metric")
        breakdown = df.groupby(group_col, as_index=False)[metric2].sum().sort_values(metric2, ascending=False)
        fig2 = px.bar(breakdown, x=group_col, y=metric2, title=f"{metric2.title()} by {group_col.title()}", color=group_col)
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.pie(breakdown, names=group_col, values=metric2, title=f"Share of {metric2.title()}")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Need at least one categorical and one numeric column for breakdown charts.")

with tab3:
    if numeric_cols:
        dist_metric = st.selectbox("Metric", numeric_cols, key="dist_metric")
        fig4 = px.histogram(df, x=dist_metric, nbins=30, title=f"Distribution of {dist_metric.title()}")
        st.plotly_chart(fig4, use_container_width=True)

        if len(numeric_cols) >= 2:
            c1, c2 = st.columns(2)
            with c1:
                x_axis = st.selectbox("X axis", numeric_cols, index=0, key="scatter_x")
            with c2:
                y_axis = st.selectbox("Y axis", numeric_cols, index=1, key="scatter_y")
            color_by = filter_col if filter_col and filter_col != "(none)" else None
            fig5 = px.scatter(df, x=x_axis, y=y_axis, color=color_by, title=f"{x_axis.title()} vs {y_axis.title()}")
            st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No numeric columns found.")

with tab4:
    st.dataframe(df, use_container_width=True, height=500)
    st.download_button(
        "Download filtered data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_data.csv",
        mime="text/csv",
    )