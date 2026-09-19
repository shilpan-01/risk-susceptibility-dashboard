"""
Shared data loading and statistics utilities for the RubyGems Investigative Study dashboard.
Imported by Home.py and every page in pages/.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

CLASS_COL = "is_malicious"
BENIGN_VAL = 0
MALICIOUS_VAL = 1
EXCLUDE_COLS = {CLASS_COL, "gem_id", "gem_name"}

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_PATH = os.path.join(_APP_DIR, "data", "scoring_results_with_AUC.csv")


@st.cache_data
def _load_csv(path_or_buffer):
    return pd.read_csv(path_or_buffer)


def get_dataframe(sidebar_label="Dataset"):
    """
    Renders an optional sidebar file uploader and returns a dataframe.
    Defaults to the bundled scoring_results_with_AUC.csv if nothing is uploaded,
    so anyone opening the app sees real results immediately.
    """
    st.sidebar.markdown(f"### {sidebar_label}")
    uploaded = st.sidebar.file_uploader("Upload your own CSV (optional)", type=["csv"])

    if uploaded is not None:
        df = _load_csv(uploaded)
        st.sidebar.caption(f"Using uploaded file: **{uploaded.name}**")
    else:
        df = _load_csv(DEFAULT_DATA_PATH)
        st.sidebar.caption(
            f"Using bundled dataset: **scoring_results_with_AUC.csv** "
            f"({len(df):,} RubyGems packages)"
        )

    return df


def get_numeric_cols(df):
    """Numeric score/aspect/composite columns, excluding id and classification columns."""
    return [c for c in df.select_dtypes(include=np.number).columns.tolist() if c not in EXCLUDE_COLS]


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


def summarize_column_ks(df, col):
    """Benign/malicious mean+std, KS statistic, AUC, Strength for one numeric column."""
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

    # Strength (thesis Eq. 4.5): only AUC above the 0.5 random baseline counts
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


def build_ks_summary(df, numeric_cols):
    """Full KS/AUC/Strength/Weight%/Status table across all numeric columns."""
    ks_summary_df = pd.DataFrame([summarize_column_ks(df, c) for c in numeric_cols])

    total_strength = ks_summary_df["Strength"].sum()
    ks_summary_df["Weight (%)"] = (
        ks_summary_df["Strength"] / total_strength * 100 if total_strength > 0 else 0
    )
    ks_summary_df["Status"] = np.where(ks_summary_df["Strength"] > 0, "Included", "Excluded")

    return ks_summary_df.sort_values("KS Statistic", ascending=False).reset_index(drop=True)


def dataset_counts(df):
    """Total/benign/malicious counts and percentages."""
    total = len(df)
    benign = int((df[CLASS_COL] == BENIGN_VAL).sum())
    malicious = int((df[CLASS_COL] == MALICIOUS_VAL).sum())
    benign_pct = benign / total * 100 if total else 0
    malicious_pct = malicious / total * 100 if total else 0
    return total, benign, malicious, benign_pct, malicious_pct
