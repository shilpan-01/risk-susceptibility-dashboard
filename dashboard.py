import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="RubyGems Investigative Study",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

CLASS_COL = "is_malicious"
BENIGN_VAL = 0
MALICIOUS_VAL = 1

# ---------- Sidebar: Upload ----------
st.sidebar.title("💎 Upload Data")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded is None:
    st.title("Software Supply Chain RubyGems Investigative Study")
    st.info("Upload a CSV in the left sidebar to begin.")
    st.stop()

df = pd.read_csv(uploaded)

if CLASS_COL not in df.columns:
    st.title("Software Supply Chain RubyGems Investigative Study")
    st.error(
        f"This CSV has no `{CLASS_COL}` column, which this dashboard requires to separate "
        "benign vs malicious packages. Please upload a CSV with a 0/1 `is_malicious` column "
        "(0 = benign, 1 = malicious)."
    )
    st.caption(f"Columns found: {', '.join(df.columns)}")
    st.stop()

# ---------- Main: Title ----------
st.title("Software Supply Chain RubyGems Investigative Study")

benign_count = int((df[CLASS_COL] == BENIGN_VAL).sum())
malicious_count = int((df[CLASS_COL] == MALICIOUS_VAL).sum())

# ---------- Sidebar: Benign vs Malicious ----------
st.sidebar.markdown("---")
st.sidebar.subheader("Benign vs Malicious")

total_count = len(df)
benign_pct = benign_count / total_count * 100 if total_count else 0
malicious_pct = malicious_count / total_count * 100 if total_count else 0

st.sidebar.metric("Total Dataset", f"{total_count:,}")
st.sidebar.metric("Malicious", f"{malicious_count:,}", delta=f"{malicious_pct:.2f}% of total", delta_color="off")
st.sidebar.metric("Benign", f"{benign_count:,}", delta=f"{benign_pct:.2f}% of total", delta_color="off")

pie_fig = px.pie(
    names=["Benign", "Malicious"],
    values=[benign_count, malicious_count],
    hole=0.4,
    color_discrete_sequence=["#1f77b4", "#d62728"],
)
pie_fig.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    height=300,
)
st.sidebar.plotly_chart(pie_fig, use_container_width=True)

if malicious_count > 0:
    ratio = benign_count / malicious_count
    imbalance_text = f"1 : {ratio:,.1f}  (malicious : benign)"
else:
    imbalance_text = "N/A (no malicious samples)"
st.sidebar.caption(f"**Imbalance ratio:** {imbalance_text}")

# Non-id, non-classification numeric columns become the metric dropdown options
exclude_cols = {CLASS_COL, "gem_id", "gem_name"}
numeric_cols = [
    c for c in df.select_dtypes(include=np.number).columns.tolist() if c not in exclude_cols
]

st.markdown("---")

# ---------- Overlapping Line Histogram ----------
st.subheader("Distribution — Malicious vs Benign")

if not numeric_cols:
    st.info("No numeric metric/aspect/score columns found besides the classification column.")
    st.stop()

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
    "Line-based frequency curves (density-normalized) instead of overlapping bars, so neither class "
    "visually overpowers the other despite the class imbalance."
)

st.markdown("---")

# ---------- Statistical Validation: Kolmogorov-Smirnov (KS) Test ----------
st.subheader("Statistical Validation — Kolmogorov–Smirnov (KS) Test")


def ks_statistic_and_curve(benign_vals, malicious_vals):
    """Two-sample KS statistic plus the ECDF curves needed to plot it."""
    b_sorted = np.sort(benign_vals)
    m_sorted = np.sort(malicious_vals)
    combined_x = np.sort(np.concatenate([b_sorted, m_sorted]))

    ecdf_b = np.searchsorted(b_sorted, combined_x, side="right") / len(b_sorted)
    ecdf_m = np.searchsorted(m_sorted, combined_x, side="right") / len(m_sorted)

    diffs = np.abs(ecdf_b - ecdf_m)
    ks_idx = int(np.argmax(diffs))
    ks_stat = diffs[ks_idx]

    return ks_stat, combined_x, ecdf_b, ecdf_m, ks_idx


ks_stat, x_grid, ecdf_benign, ecdf_malicious, ks_idx = ks_statistic_and_curve(benign_data, malicious_data)

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
    "The KS statistic is the maximum vertical gap between the two empirical cumulative distribution "
    "functions (dashed line above). 0 = distributions identical, 1 = fully separated."
)

st.markdown("#### KS Summary Table — All Metrics")


def summarize_column_ks(col):
    b = df.loc[df[CLASS_COL] == BENIGN_VAL, col].dropna()
    m = df.loc[df[CLASS_COL] == MALICIOUS_VAL, col].dropna()
    n1, n2 = len(m), len(b)

    b_mean, m_mean = b.mean(), m.mean()
    b_std, m_std = b.std(ddof=1), m.std(ddof=1)

    ks_val, _, _, _, _ = ks_statistic_and_curve(b.values, m.values)

    # AUC via Mann-Whitney rank-sum (probability a random malicious score > random benign score)
    combined = pd.concat([b, m])
    ranks = combined.rank()
    m_rank_sum = ranks.iloc[n2:].sum()
    auc = (m_rank_sum - n1 * (n1 + 1) / 2) / (n1 * n2) if n1 > 0 and n2 > 0 else np.nan

    # Strength (Eq. 4.5 in thesis): only AUC above the 0.5 random baseline counts
    strength = max(auc - 0.5, 0) if pd.notna(auc) else np.nan

    return {
        "Metric": col,
        "Benign Mean": b_mean,
        "Malicious Mean": m_mean,
        "Mean Diff": m_mean - b_mean,
        "Benign Std": b_std,
        "Malicious Std": m_std,
        "KS Statistic": ks_val,
        "AUC": auc,
        "Strength": strength,
    }


ks_summary_df = pd.DataFrame([summarize_column_ks(c) for c in numeric_cols])

# Weight = strength normalised across all included metrics (Eq. 4.6 in thesis), shown as %
total_strength = ks_summary_df["Strength"].sum()
ks_summary_df["Weight (%)"] = (
    ks_summary_df["Strength"] / total_strength * 100 if total_strength > 0 else 0
)
ks_summary_df["Status"] = np.where(ks_summary_df["Strength"] > 0, "Included", "Excluded")

ks_summary_df = ks_summary_df.sort_values("KS Statistic", ascending=False).reset_index(drop=True)

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