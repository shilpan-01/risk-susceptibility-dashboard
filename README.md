# RubyGems Software Supply Chain Investigative Study — Dashboard

An interactive, multipage Streamlit dashboard exploring benign vs. malicious RubyGems
packages, built to accompany the Master of Engineering thesis:

> *Investigating RubyGems Packages for Software Supply Chain Attack Susceptibility
> Through Socio-Technical Metadata* — Shilpa Nair, University of Waikato, 2026.

The app ships with the actual thesis dataset bundled in, so anyone opening it sees real
results immediately — no upload required (though uploading a different CSV with the same
schema is supported as an optional override).

## Pages

- **Home** — thesis introduction, methodology summary, quick dataset snapshot, and references
- **Distribution** — density-normalized benign vs. malicious score distributions, selectable
  by metric / aspect / composite score
- **KS Validation** — Kolmogorov–Smirnov statistical test (ECDF plot + summary table with
  KS statistic, AUC, Strength, and normalized Weight %), with thesis methodology notes
- **Project Summary** — a simplified, chart-only view (percentages, ranked bar charts) for
  a non-technical audience

An **Enrichment analysis** page (top-% capture rate vs. random baseline, per the thesis's
tail-concentration analysis) is planned as a future addition.

## Requirements

- Python 3.9+
- See `requirements.txt` (Streamlit, pandas, numpy, plotly)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run Home.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`). Streamlit
automatically builds the sidebar navigation from the `pages/` folder.

## Expected CSV format

If you upload your own file (optional — the bundled dataset is used by default), it needs
at minimum:

| Column | Type | Description |
|---|---|---|
| `is_malicious` | 0/1 | Ground-truth label (0 = benign, 1 = malicious) |

Plus any number of numeric score/metric/aspect columns (e.g. `dep_score`, `file_score`,
`usage_score`, `popularity_score`, `activity_score`, `stakeholder_score`,
`complexity_aspect`, `impact_aspect`, `maintenance_aspect`, `composite_score`). These are
auto-detected — no code changes needed to add or remove a metric.

`gem_id` and `gem_name` are recognized and excluded from the numeric analysis if present,
but are not required. If `is_malicious` is missing, each page shows a clear on-screen error
instead of crashing.

## Project Structure

```
.
├── Home.py                        # Main entry point — intro, methodology, references
├── data_utils.py                  # Shared data loading + KS/AUC statistics functions
├── pages/
│   ├── 1_Distribution.py          # Benign vs malicious score distributions
│   ├── 2_KS_Validation.py         # KS test ECDF plot + summary table
│   └── 3_Project_Summary.py       # Simplified chart-only summary
├── data/
│   └── scoring_results_with_AUC.csv   # Bundled thesis dataset (79,000 packages)
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Ground Truth Reference

Marc Ohm et al. *"Backstabber's Knife Collection: A Review of Open Source Software Supply
Chain Attacks."* In: *Detection of Intrusions and Malware, and Vulnerability Assessment
(DIMVA)*. Springer International Publishing, 2020.

Dataset: https://dasfreak.github.io/Backstabbers-Knife-Collection/
