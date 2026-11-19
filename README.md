# HunarLens

HunarLens is a CT-378 research project exploring youth unemployment in Pakistan. A frozen explainable model estimates associations among youth in the labour force; a separate weighted skills-gap analysis uses education and training as proxies. The Streamlit dashboard combines survey context, model evaluation and limitations. **It is not a decision tool for individuals.**

**Live app:** [https://hunar-lens.streamlit.app/](https://hunar-lens.streamlit.app/) — team: verify the public deployment before submission.

## Requirements and setup

Use Python 3.12. Runtime and development packages are pinned exactly in [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt). From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
streamlit run app/streamlit_app.py
```

On macOS or Linux, use `python3.12 -m venv .venv` and `source .venv/bin/activate`. Open the local Streamlit URL; append `?classic=1` for the native fallback. Runtime-only installation uses `pip install -r requirements.txt`; rebuilding datasets and running tests require development dependencies.

## Data and reproducibility

[DATA_SOURCES.md](DATA_SOURCES.md) records official sources, access checks, terms and source-file checksums. Download raw files from official PBS landing pages using:

```powershell
python scripts/00_download_data.py
```

Raw files, intermediate data and person-level processed files are ignored by Git. The source downloader writes `data/raw/MANIFEST.json`. Reproduction requires sufficient disk space, the original survey files and optional tools documented by the download script. Network and PBS availability can affect the run.

The lifecycle scripts below are listed in order. Times are indicative only; exact end-to-end runtimes were not benchmarked and depend on hardware and data access. **Do not rerun model freezing or test scoring for a submission review:** the final model and test evaluation are already frozen. The test script has safeguards and is retained for audit, not as a routine setup step.

| Stage | Script / command | Output and approximate runtime |
|---|---|---|
| 00 | `python scripts/00_download_data.py` | Official downloads and manifest; network-dependent, usually minutes. |
| 01 | `python scripts/01_audit_raw.py`; `python scripts/01_build_dataset.py` | Audit and ignored person-level dataset, Census lookup and label reproduction; minutes, hardware-dependent. |
| 02 | `python scripts/02_make_splits.py` | Ignored household split assignments and aggregate summary; typically minutes or less. |
| 03 | `python scripts/03_stage4_baselines.py`; `python scripts/03_run_experiments.py`; `python scripts/03_g5_review.py` | Validation baselines, grouped searches, ablations and review; tuning can take hours on a laptop. |
| 04 | `python scripts/04_freeze_model.py` | Historical training-only freeze and validation thresholds; **do not rerun on the submitted artefact**. Runtime not benchmarked. |
| 05 | `python scripts/05_explain.py`; `python scripts/05_enrolment_ablation.py` | Validation explanations and ablation; grouped resampling can take substantial time. |
| 06 | `python scripts/06_final_test_eval.py` | One-time sealed test evaluation; **do not rerun or rescore**. Runtime not benchmarked. |
| 07 | `python scripts/07_build_rare_flags.py`; `python scripts/07_audit_app.py` | Aggregate rare-combination flags and app audit; runtime not benchmarked. |
| 08 | `python scripts/08_overview_indicators.py`; `python scripts/08_validation_calibration.py` | Verified overview indicators and validation calibration; runtime not benchmarked. |
| 09 | `python scripts/09_skills_gap.py --build`; `python scripts/09_analyze_skills.py`; `python scripts/09_refine_skills.py`; `python scripts/09_skills_occupation_variants.py`; `python scripts/09_model_shift.py`; `python scripts/09_skills_report.py` | Skills audit dataset, reproduction, weighted aggregate tables and report; bootstrap and model-shift analysis can take substantial time. `09_skills_audit.py`, `09_verify_skills.py` and `09_complete_audit.py` provide additional audit evidence. |

The frozen model's SHA-256 is `6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3`. The model and metadata must use the pinned scikit-learn version.

## Tests

`python -m pytest -q` runs the default suite, including five `full_data` tests when the local processed files are present. Use `python -m pytest -q -m full_data` to run only those tests, or `python -m pytest -q -m "not full_data"` when the ignored full dataset is unavailable. The full-data tests read all processed records, including the test partition already opened under the Stage 8 policy; they do not authorize a new evaluation.

## Repository tour

- `app/`: dashboard, presentation assets and Streamlit entry point.
- `src/hunarlens/`: approved pipeline, data, evaluation and skills helpers.
- `scripts/`: reproducible stage scripts and submission preparation.
- `models/`: frozen pipeline, metadata and validation score quantiles.
- `reports/tables/`, `reports/figures/`: generated aggregate evidence and figures.
- `notebooks/`: lifecycle explanations; `docs/`: decisions, reports, audit and viva notes.
- `tests/`: model, privacy, skills-analysis and interface checks.
- `data/processed/census_lookup.csv`, `rare_combinations.csv`: small tracked aggregate lookups.

The submission includes small aggregates, the Census lookup, rare-combination flags and score quantiles. It excludes raw microdata and person-level outputs for privacy and because file-specific redistribution terms require confirmation. See [cleanup candidates](docs/cleanup_candidates.md) before packaging. Run `python scripts/make_submission.py` for a **dry run**; it does not create an archive.

## AI-assistance statement — TEAM PLACEHOLDER

**[Complete this statement in accordance with the course policy: identify AI tools and how they were used, the team's verification, and each student's responsibility. Do not submit this placeholder as a final disclosure.]**
