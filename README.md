# RubyGems Software Supply Chain Investigative Study — Dashboard

An interactive Streamlit dashboard for exploring benign vs. malicious RubyGems packages,
built to accompany the ROC (Research/Thesis) project on software supply chain risk scoring.

Upload a scored CSV and the dashboard shows:

- **Dataset composition** — total packages, benign/malicious counts and percentages, an
  imbalance ratio, and a benign-vs-malicious pie chart (sidebar).
- **Distribution comparison** — density-normalized, line-based frequency curves for any
  selected metric, attribute, aspect, or the composite score, so the minority (malicious)
  class isn't visually flattened by the majority class.
- **Statistical validation (KS test)** — an ECDF plot with the Kolmogorov–Smirnov statistic
  marked, plus a full summary table (KS statistic, AUC, Strength, normalized Weight %, and
  Included/Excluded status) across every numeric column.

## Requirements

- Python 3.9+
- See `requirements.txt` (Streamlit, pandas, numpy, plotly)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run dashboard.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Expected CSV format

The dashboard expects a CSV with, at minimum:

| Column | Type | Description |
|---|---|---|
| `is_malicious` | 0/1 | Ground-truth label (0 = benign, 1 = malicious) |

Plus any number of numeric score/metric/aspect columns (e.g. `dep_score`, `file_score`,
`usage_score`, `popularity_score`, `activity_score`, `stakeholder_score`,
`complexity_aspect`, `impact_aspect`, `maintenance_aspect`, `composite_score`). These are
auto-detected from the uploaded file — no code changes needed to add or remove a metric.

`gem_id` and `gem_name` are recognized and excluded from the numeric analysis if present,
but are not required.

If a required column is missing, the dashboard shows a clear on-screen error instead of
crashing.

## Project Structure

```
.
├── dashboard.py        # Main Streamlit app
├── requirements.txt    # Python dependencies
├── README.md
├── LICENSE
└── .gitignore
```

## Notes

This dashboard is a companion tool to the accompanying thesis (ENGEN594) evaluating a
software supply chain risk scoring framework for RubyGems packages, and reproduces several
of its evaluation methods (AUC-based metric weighting, KS-test distributional validation)
in an interactive form.
