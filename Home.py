import streamlit as st
from data_utils import get_dataframe, dataset_counts

st.set_page_config(
    page_title="RubyGems Investigative Study — Home",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💎 Software Supply Chain RubyGems Investigative Study")

st.markdown(
    """
This dashboard accompanies a Master of Engineering thesis (University of Waikato, 2026):

> *Investigating RubyGems Packages for Software Supply Chain Attack Susceptibility Through
> Socio-Technical Metadata* — Shilpa Nair

The thesis proposes a **risk profiling framework** that scores RubyGems packages using
socio-technical metadata (dependency structure, ecosystem impact, maintenance activity)
rather than known-vulnerability databases, and evaluates it against **79,000 packages**,
including **380 known-malicious** packages.
"""
)

st.markdown("---")

st.subheader("What is the risk score?")
st.markdown(
    """
Every package gets a score from **0 to 1** estimating how *attractive and easy a target*
it may be for an attacker. **Higher = more susceptible.** It is **not a malware detector**:
it never looks at what the code does, it ranks packages using public metadata only.

The score is built up in four levels:

| Level | What it is | Examples |
|---|---|---|
| **Metrics** (13) | Raw measurements | downloads, days since last commit, number of dependencies |
| **Attributes** (6) | Related metrics grouped | Dependency, Codebase, Usage, Popularity, Activity, Stakeholders |
| **Aspects** (3) | Attributes grouped into themes | **Complexity** (dependency + codebase), **Impact** = "blast radius" (usage + popularity), **Maintenance** (activity + stakeholders) |
| **Composite score** | Average of the three aspects | One overall susceptibility score per package |

Metrics are weighted by how well they separated *known* malicious packages from benign ones
(using ROC-AUC), so signals that don't help get zero weight. The dropdown on each page lets
you look at any level: attribute scores (`dep_score`, `usage_score`, ...), aspect scores, or
the composite.
"""
)

st.subheader("How to read the results")
st.markdown(
    """
- **📈 Distribution** — do malicious packages tend to score *higher* than benign ones, and how much do the two groups overlap?
- **🧪 KS Validation** — how well does each score separate the two groups? (0 = not at all, 1 = perfectly)
- **🎯 Enrichment** — if you reviewed only the highest-scoring X% of packages, would you find *more* malicious ones than by picking at random?
"""
)

st.info(
    "**Bottom line (thesis dataset):** malicious packages tend to score higher, most clearly on "
    "the *maintenance* aspect, and reviewing the top-ranked 5–20% of packages finds roughly "
    "1.5× more malicious packages than random selection. That makes the score a useful "
    "**prioritisation signal** — a way to decide what to review first — but the two groups "
    "overlap heavily, so it cannot identify malicious packages on its own."
)

st.markdown("---")

st.subheader("Explore the Analysis")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("pages/1_Distribution.py", label="📈 Distribution", icon="📈")
    st.caption("Do malicious packages score higher than benign ones, and how much do the two groups overlap?")
with col2:
    st.page_link("pages/2_KS_Validation.py", label="🧪 KS Validation", icon="🧪")
    st.caption("A statistical test of how well each score separates malicious from benign packages.")
with col3:
    st.page_link("pages/3_Enrichment.py", label="🎯 Enrichment", icon="🎯")
    st.caption("If you reviewed only the top-ranked packages, would you find more malicious ones than by chance?")
with col4:
    st.page_link("pages/4_Project_Summary.py", label="📊 Project Summary", icon="📊")
    st.caption("A simple, chart-only summary of the results, with no technical background needed.")

st.markdown("---")

# ---------- Quick dataset snapshot ----------
st.subheader("Dataset at a Glance")
df = get_dataframe(sidebar_label="Dataset")
total, benign, malicious, benign_pct, malicious_pct = dataset_counts(df)

c1, c2, c3 = st.columns(3)
c1.metric("Total Packages", f"{total:,}")
c2.metric("Benign", f"{benign:,}", f"{benign_pct:.2f}%")
c3.metric("Malicious", f"{malicious:,}", f"{malicious_pct:.2f}%")

st.markdown("---")

# ---------- References ----------
st.subheader("References")
st.markdown(
    """
Marc Ohm et al. *"Backstabber's Knife Collection: A Review of Open Source Software
Supply Chain Attacks."* DIMVA, 2020.
[dasfreak.github.io/Backstabbers-Knife-Collection](https://dasfreak.github.io/Backstabbers-Knife-Collection/)
"""
)
