import numpy as np
import plotly.graph_objects as go
import streamlit as st
from data_utils import (
    CLASS_COL, get_dataframe, get_numeric_cols, enrichment_table, capture_curve,
)

st.set_page_config(page_title="Enrichment", page_icon="🎯", layout="wide")

st.title("🎯 Enrichment Analysis — Tail Concentration")

with st.expander("Methodology (from thesis)", expanded=False):
    st.markdown(
        """
Per the thesis methodology (§5.2), packages are ranked by a chosen score in descending
order, and the top-X% slice is examined for how concentrated malicious packages are
compared to picking that same number of packages **at random**.

- **Expected (Random)** = Top N × (overall malicious rate) — how many malicious packages
  you'd expect to find in that slice by chance alone
- **Enrichment factor** = Actual ÷ Expected — how many times *more* malicious packages
  showed up than random chance would predict (1.0× = no better than random)
- **Capture (%)** = Actual ÷ Total malicious — what share of *all* malicious packages in
  the dataset are caught within that top slice

In the thesis evaluation (ranking by composite score), the top 5% and top 10% both showed
**≈1.58× enrichment**, capturing **≈7.89%** and **≈15.79%** of all malicious packages
respectively — while the top 1% *underperformed* random chance (≈0.26×), indicating the
very highest-ranked packages aren't necessarily where malicious packages concentrate most.
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

default_idx = numeric_cols.index("composite_score") if "composite_score" in numeric_cols else 0
score_col = st.selectbox(
    "Rank packages by (Metric / Attribute / Aspect / Composite Score)",
    numeric_cols,
    index=default_idx,
)

# ---------- Enrichment Table ----------
st.subheader(f"Enrichment Table — Ranked by `{score_col}`")

table_df = enrichment_table(df, score_col)

st.dataframe(
    table_df.style.format({
        "Expected (Random)": "{:.1f}",
        "Enrichment (x)": "{:.2f}×",
        "Capture (%)": "{:.2f}%",
    }),
    use_container_width=True,
)

row10 = table_df[table_df["Top %"] == 10]
if not row10.empty:
    r = row10.iloc[0]
    st.info(
        f"**How to read this:** if you reviewed the top 10% of packages by `{score_col}` "
        f"({int(r['Top N Packages']):,} packages), picking at random would be expected to include about "
        f"{r['Expected (Random)']:.0f} malicious ones. This ranking included {int(r['Actual Malicious'])}, "
        f"which is {r['Enrichment (x)']:.2f}× the random rate and covers {r['Capture (%)']:.1f}% of all "
        f"malicious packages. An enrichment of 1.0× would mean no better than random."
    )

row1 = table_df[table_df["Top %"] == 1]
if not row1.empty and not np.isnan(row1.iloc[0]["Enrichment (x)"]) and row1.iloc[0]["Enrichment (x)"] < 1:
    r1 = row1.iloc[0]
    st.warning(
        f"**Note on the very top 1%:** it found {int(r1['Actual Malicious'])} malicious package(s) against "
        f"{r1['Expected (Random)']:.1f} expected ({r1['Enrichment (x)']:.2f}×). With counts this small, a single "
        "package changes the result, so read it as *no clear signal at the very top* rather than proof "
        "it is worse. The score is best used to prioritise a wider band of packages, not as a detector."
    )

st.markdown("---")

# ---------- Custom top-% + dynamic conclusion ----------
st.subheader("Explore a Custom Threshold")

custom_pct = st.slider("Top % of packages", min_value=1, max_value=50, value=5, step=1)
custom_row = enrichment_table(df, score_col, percentages=(custom_pct,)).iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Top N Packages", f"{int(custom_row['Top N Packages']):,}")
c2.metric("Expected (Random)", f"{custom_row['Expected (Random)']:.1f}")
c3.metric("Actual Malicious", f"{int(custom_row['Actual Malicious']):,}")
c4.metric("Enrichment", f"{custom_row['Enrichment (x)']:.2f}×")

enrichment_val = custom_row["Enrichment (x)"]
capture_val = custom_row["Capture (%)"]

if np.isnan(enrichment_val):
    conclusion = f"No malicious packages exist in this dataset to compare against for `{score_col}`."
elif enrichment_val >= 1.5:
    conclusion = (
        f"Ranking by **{score_col}**, the top {custom_pct}% of packages contain **{enrichment_val:.2f}×** "
        f"more malicious packages than random chance would predict, capturing **{capture_val:.2f}%** of "
        f"all malicious packages in the dataset — a meaningfully concentrated tail."
    )
elif enrichment_val >= 1.0:
    conclusion = (
        f"Ranking by **{score_col}**, the top {custom_pct}% shows mild enrichment (**{enrichment_val:.2f}×**), "
        f"capturing **{capture_val:.2f}%** of malicious packages — somewhat better than random, but not "
        f"strongly concentrated."
    )
else:
    conclusion = (
        f"Ranking by **{score_col}**, the top {custom_pct}% performs **worse than random** "
        f"(**{enrichment_val:.2f}×** enrichment), capturing only **{capture_val:.2f}%** of malicious "
        f"packages — this score does not concentrate malicious packages at this threshold."
    )

st.info(conclusion)

st.markdown("---")

# ---------- Cumulative Capture Curve ----------
st.subheader("Cumulative Capture Curve vs. Random Baseline")

percentiles, capture_pct_curve = capture_curve(df, score_col)

curve_fig = go.Figure()
curve_fig.add_trace(go.Scatter(
    x=percentiles, y=capture_pct_curve, mode="lines", name=f"Ranked by {score_col}",
    line=dict(color="#1f77b4", width=2.5),
))
curve_fig.add_trace(go.Scatter(
    x=[0, 100], y=[0, 100], mode="lines", name="Random baseline",
    line=dict(color="gray", width=2, dash="dash"),
))
curve_fig.add_vline(x=custom_pct, line_dash="dot", line_color="black", opacity=0.5)
curve_fig.update_layout(
    title=f"Cumulative Malicious Capture — Ranked by {score_col}",
    xaxis_title="Top % of Packages (by score, descending)",
    yaxis_title="Cumulative % of Malicious Packages Captured",
    legend_title="",
)

st.plotly_chart(curve_fig, use_container_width=True)

st.caption(
    "The blue line above the gray diagonal means the ranking is doing better than random at "
    "surfacing malicious packages; below the diagonal means worse. The dotted vertical line marks "
    "your currently selected top-% threshold."
)
