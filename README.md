# HunarLens

HunarLens is a CT-378 machine-learning project exploring youth unemployment in Pakistan. It combines an explainable classification model with a separate weighted skills-gap analysis, presented in a Streamlit dashboard.

The model describes associations among people aged **15–24 who are in the labour force**. The skills-gap analysis uses education and training as proxies; it does not directly measure individual skills or employer demand. **HunarLens is a research and education tool, not a decision tool for individuals.**

**Live app:** [hunar-lens.streamlit.app](https://hunar-lens.streamlit.app/)

## Run the app

Use Python **3.12**. The packages required by the app are pinned in [requirements.txt](requirements.txt); notebook, data-processing and test tools are listed in [requirements-dev.txt](requirements-dev.txt).

From the repository root on Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

If the virtual environment already exists, activate it instead of creating it again. On macOS or Linux, use `python3.12 -m venv .venv` and `source .venv/bin/activate`. Install the development dependencies as well when working with the notebooks or rebuilding data:

```bash
python -m pip install -r requirements-dev.txt
```

Open the local URL printed by Streamlit. Add `?classic=1` to the URL for the native Streamlit fallback.

The dashboard reads the saved model and metadata, the Census and rare-combination lookups, and aggregate tables and figures in `reports/`. It does not need the raw survey files to run.

## What the dashboard contains

- **Overview:** published and reproduced survey indicators.
- **Skills gap:** weighted education, training, occupation and approximate NEET comparisons.
- **Profile explorer:** an illustrative prediction using the frozen model and permitted inputs.
- **Model performance:** saved evaluation results, baseline comparisons and subgroup information.
- **Data and methodology:** sources, definitions and limitations.

## Data and model

The project uses the Pakistan Bureau of Statistics Labour Force Survey 2024–25 and regional information from the 2023 Population and Housing Census. [DATA_SOURCES.md](DATA_SOURCES.md) lists source links, accessibility and terms of use; [data/README.md](data/README.md) describes the data. The downloader discovers official PBS files and writes a local manifest:

```bash
python scripts/download_data.py
```

Raw files in `data/raw/` and intermediate files in `data/interim/` are Git-ignored. The person-level youth dataset, split assignments and test-prediction cache are also ignored. A fresh clone will not contain those local files. `data/processed/census_lookup.csv` and `data/processed/rare_combinations.csv` are small tracked reference tables used by the app.

The frozen model is [models/final_pipeline.joblib](models/final_pipeline.joblib), with settings and input categories in [models/metadata.json](models/metadata.json). Its SHA-256 is:

```text
6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3
```

The saved test evaluation reports HGB F1 **0.360**, average precision **0.303** and ROC-AUC **0.752**. The stratified Dummy baseline has F1 **0.123** and average precision **0.127**. These are unweighted results for the held-out labour-force youth sample. See [docs/test_findings.md](docs/test_findings.md) and [reports/tables/test_metrics.csv](reports/tables/test_metrics.csv) for context and operating-point comparisons.

## Analysis workflow

The scripts below are available in the current directory. Data-building and analysis scripts may write outputs or require locally downloaded files; some can take substantial time. Review a script before running it.

| Topic | Main files | Purpose |
| --- | --- | --- |
| Acquisition and audit | `scripts/download_data.py`, `scripts/audit_raw_data.py` | Download official sources and inspect survey fields. |
| Modelling dataset | `scripts/build_modeling_dataset.py` | Build the label, roster features and Census lookup; compare weighted label totals with PBS figures. |
| Household splits | `scripts/make_splits.py` | Produce household-grouped split assignments. |
| Baselines and experiments | `scripts/compute_baselines.py`, `scripts/compare_models.py`, `scripts/review_model_comparison.py` | Compare baseline and candidate models using training and validation data. |
| Model freeze | `scripts/save_final_model.py` | Historical training and validation freeze procedure. |
| Explanations | `scripts/explain_model.py`, `scripts/analyze_enrolment_ablation.py` | Produce validation explanations and the enrolment ablation. |
| Test evaluation | `scripts/evaluate_on_test_set.py` | Historical one-time evaluation and aggregate results. |
| App support | `scripts/build_rare_flags.py`, `scripts/compute_score_quantiles.py`, `scripts/audit_app.py` | Prepare reference artefacts and audit app behaviour. |
| Skills-gap analysis | `scripts/build_skills_dataset.py`, `scripts/analyze_skills_gap.py`, `scripts/compute_skills_refinements.py`, `scripts/analyze_occupation_variants.py`, `scripts/analyze_model_shift.py` | Build and analyse weighted survey measures and validation-only model shifts. |

**The model and thresholds are frozen and the test split has already been evaluated. Do not rerun model freezing or rescore the test set for a review.** The original `data/processed/test_predictions.csv` cache is currently unavailable, although the saved aggregate test results and figures remain. The evaluation receipt is retained in `data/processed/`.

## Notebooks and documentation

The `notebooks/` directory contains the data audit, exploratory analysis, baseline pipeline, model comparison, final-model explanation, test-evaluation and skills-gap notebooks. Their saved outputs are part of the project record; review the frozen-evaluation notes before rerunning cells.

The main supporting documents are:

- [Label definition](docs/label_definition.md) and [data dictionary](docs/data_dictionary.md).
- [Decision log](docs/DECISIONS.md) and [EDA findings](docs/eda_findings.md).
- [Model findings](docs/model_findings.md) and [test findings](docs/test_findings.md).
- [Skills-gap methods](docs/skills_gap_methods.md), [findings](docs/skills_gap_findings.md) and [summary](docs/skills_gap_summary.md).
- [Skills-gap data audit](docs/skills_gap_data_audit.md) and the planning documents in `docs/process/`.

## Repository tour

| Path | Contents |
| --- | --- |
| `app/` | Streamlit entry point, dashboard component and interface assets. |
| `src/hunarlens/` | Data, preprocessing, model, explanation, skills and UI helpers. |
| `scripts/` | Data, modelling, analysis and app-support scripts. |
| `models/` | Frozen pipeline, metadata and validation-score quantiles. |
| `reports/tables/` and `reports/figures/` | Saved aggregate evidence and plots. |
| `notebooks/` | Project notebooks and saved outputs. |
| `docs/` | Decisions, methods, audit and findings. |
| `data/` | Source documentation, local ignored data and small tracked reference lookups. |


