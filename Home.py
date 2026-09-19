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

st.subheader("Explore the Analysis")

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_Distribution.py", label="📈 Distribution", icon="📈")
with col2:
    st.page_link("pages/2_KS_Validation.py", label="🧪 KS Validation", icon="🧪")
with col3:
    st.page_link("pages/3_Project_Summary.py", label="📊 Project Summary", icon="📊")

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
