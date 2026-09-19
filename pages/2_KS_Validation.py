import streamlit as st
from data_utils import (
    CLASS_COL, BENIGN_VAL, MALICIOUS_VAL,
    get_dataframe, get_numeric_cols, ks_statistic_and_curve, build_ks_summary,
)
import plotly.graph_objects as go

st.set_page_config(page_title="KS Validation", page_icon="🧪", layout="wide")

st.title("🧪 Statistical Validation — Kolmogorov–Smirnov (KS) Test")

with st.expander("Methodology (from thesis)", expanded=False):
    st.markdown(
        """
Per the thesis methodology, the **Kolmogorov–Smirnov (KS) statistic** is used as an
independent, non-parametric check on how well each score separates benign from malicious
packages — complementing the ROC-AUC analysis used to derive metric weights.

The KS statistic is the **maximum vertical distance** between the empirical cumulative
distribution functions (ECDFs) of the two classes:

**KS = sup |F₍malicious₎(x) − F₍benign₎(x)|**

- **KS = 0** → the two distributions are identical (no separation)
- **KS = 1** → the two distributions are fully separated

In the thesis evaluation, the composite score achieved **KS ≈ 0.175** (moderate
separation), with the **Maintenance aspect** showing the strongest separation
(KS ≈ 0.210), ahead of Complexity (≈ 0.125) and Impact (≈ 0.107) — reinforcing the
finding that maintenance-related signals are the most discriminative.
"""
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

ks_stat, x_grid, ecdf_benign, ecdf_malicious, ks_idx = ks_statistic_and_curve(
    benign_data.values, malicious_data.values
)

ks_fig = go.Figure()
ks_fig.add_trace(go.Scatter(
    x=x_grid, y=ecdf_benign, mode="lines", name="Benign ECDF",
    line=dict(color="#1f77b4", width=2, shape="hv"),
))
ks_fig.add_trace(go.Scatter(
    x=x_grid, y=ecdf_malicious, mode="lines", name="Malicious ECDF",
    line=dict(color="#d62728", width=2, shape="hv"),
))
ks_fig.add_trace(go.Scatter(
    x=[x_grid[ks_idx], x_grid[ks_idx]],
    y=[ecdf_benign[ks_idx], ecdf_malicious[ks_idx]],
    mode="lines+markers",
    name=f"KS = {ks_stat:.3f}",
    line=dict(color="black", width=2, dash="dash"),
    marker=dict(size=6),
))
ks_fig.update_layout(
    title=f"ECDF of {metric} — Benign vs Malicious (KS statistic = {ks_stat:.3f})",
    xaxis_title=metric,
    yaxis_title="Cumulative Probability",
    legend_title="Class",
)

st.plotly_chart(ks_fig, use_container_width=True)

st.caption(
    "The KS statistic is the maximum vertical gap between the two empirical cumulative "
    "distribution functions (dashed line above)."
)

st.markdown("#### KS Summary Table — All Metrics")

ks_summary_df = build_ks_summary(df, numeric_cols)

st.dataframe(
    ks_summary_df.style.format({
        "Benign Mean": "{:.3f}", "Malicious Mean": "{:.3f}", "Mean Diff": "{:.3f}",
        "Benign Std": "{:.3f}", "Malicious Std": "{:.3f}", "KS Statistic": "{:.3f}",
        "AUC": "{:.3f}", "Strength": "{:.3f}", "Weight (%)": "{:.1f}%",
    }),
    use_container_width=True,
)

st.caption(
    "Sorted by KS statistic — largest maximum-CDF-gap first. AUC (0.5 = no separation, 1.0 = "
    "perfect separation); Strength = max(AUC − 0.5, 0), the excess over random chance; "
    "Weight (%) normalises Strength across all columns; Status flags columns with zero "
    "discriminatory contribution (AUC ≤ 0.5) as Excluded, matching the thesis's weighting scheme."
)
