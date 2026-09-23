import plotly.express as px
import streamlit as st
from data_utils import get_dataframe, get_numeric_cols, build_ks_summary, dataset_counts

st.set_page_config(page_title="Project Summary", page_icon="📊", layout="wide")

st.title("📊 Project Summary")
st.markdown(
    "A simplified, chart-only view of the RubyGems risk scoring results — no technical "
    "background needed to read this page."
)

df = get_dataframe(sidebar_label="Dataset")
numeric_cols = get_numeric_cols(df)

if not numeric_cols:
    st.info("No numeric metric/aspect/score columns found besides the classification column.")
    st.stop()

total_count, benign_count, malicious_count, benign_pct, malicious_pct = dataset_counts(df)
ks_summary_df = build_ks_summary(df, numeric_cols)

st.markdown("---")

# ---------- Dataset Composition ----------
st.subheader("Dataset Composition")

c1, c2, c3 = st.columns(3)
c1.metric("Total Packages", f"{total_count:,}")
c2.metric("Malicious", f"{malicious_count:,}", f"{malicious_pct:.2f}%")
c3.metric("Benign", f"{benign_count:,}", f"{benign_pct:.2f}%")

col_a, col_b = st.columns(2)

with col_a:
    bar_fig = px.bar(
        x=["Benign", "Malicious"],
        y=[benign_pct, malicious_pct],
        text=[f"{benign_pct:.1f}%", f"{malicious_pct:.1f}%"],
        labels={"x": "Class", "y": "Percentage of Dataset"},
        color=["Benign", "Malicious"],
        color_discrete_map={"Benign": "#1f77b4", "Malicious": "#d62728"},
        title="Benign vs Malicious (%)",
    )
    bar_fig.update_traces(textposition="outside")
    bar_fig.update_layout(showlegend=False, yaxis_range=[0, 100])
    st.plotly_chart(bar_fig, use_container_width=True)

with col_b:
    pie_fig = px.pie(
        names=["Benign", "Malicious"],
        values=[benign_count, malicious_count],
        hole=0.4,
        color_discrete_sequence=["#1f77b4", "#d62728"],
        title="Benign vs Malicious (Share)",
    )
    st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("---")

# ---------- Which Metrics Matter Most ----------
st.subheader("Which Scores Best Separate Malicious from Benign?")
st.caption(
    "Higher bars = stronger separation between malicious and benign packages on that score."
)

metric_choice = st.radio(
    "Rank metrics by:", ["KS Statistic", "AUC", "Weight (%)"], horizontal=True
)

ranked = ks_summary_df.sort_values(metric_choice, ascending=False)

rank_fig = px.bar(
    ranked,
    x="Metric",
    y=metric_choice,
    text=ranked[metric_choice].round(3),
    color="Status",
    color_discrete_map={"Included": "#2ca02c", "Excluded": "#999999"},
    title=f"{metric_choice} by Metric",
)
rank_fig.update_traces(textposition="outside")
rank_fig.update_layout(xaxis_tickangle=-30)
st.plotly_chart(rank_fig, use_container_width=True)

st.caption(
    "Green bars (Included) contribute to the composite risk score; gray bars (Excluded) "
    "perform no better than random guessing (AUC ≤ 0.5) and are given zero weight."
)

st.markdown("---")

# ---------- Weight Distribution ----------
st.subheader("How Much Each Metric Contributes (Weight %)")

weight_ranked = ks_summary_df[ks_summary_df["Weight (%)"] > 0].sort_values(
    "Weight (%)", ascending=False
)

if not weight_ranked.empty:
    weight_fig = px.bar(
        weight_ranked,
        x="Metric",
        y="Weight (%)",
        text=weight_ranked["Weight (%)"].round(1).astype(str) + "%",
        title="Normalized Weight per Metric",
        color_discrete_sequence=["#1f77b4"],
    )
    weight_fig.update_traces(textposition="outside")
    weight_fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(weight_fig, use_container_width=True)
else:
    st.info("No metric currently has a positive weight (all AUC values ≤ 0.5).")
