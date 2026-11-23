# HunarLens Complete Project and File Guide

This guide explains the HunarLens project by file and by lifecycle stage.

It covers:

- what each part does,
- why it exists,
- where it belongs,
- how it connects to the rest of the project,
- how to explain it in a viva.

This explanation is based on the current repository. Development-only folders such as `.venv/` and ignored raw person-level files are not part of the submitted source.

---

# 1. Project Summary

HunarLens is a CT-378 project that studies youth unemployment in Pakistan.

The binary target is `is_unemployed`.

- `1` means unemployed.
- `0` means employed.

The model population is youth aged 15–24 who are in the labour force.

The project combines:

1. A frozen machine-learning model.
2. A separate weighted skills-gap analysis.
3. A Streamlit dashboard.
4. A final report and reproducible evidence.

The project is not a diagnosis or an individual decision tool.

The main end-to-end flow is:

```text
PBS LFS
  -> official-source download
  -> source audit
  -> label reproduction
  -> modelling dataset
  -> household-aware 70/15/15 split
  -> preprocessing pipeline
  -> model comparison
  -> validation threshold selection
  -> frozen HistGradientBoosting model
  -> one-time test evaluation
  -> tables, figures and dashboard
```

---

# 2. Repository Structure

```text
HunarLens/
├── app/                  Streamlit interface and dashboard assets
├── src/hunarlens/        Reusable Python source package
├── scripts/              Reproducible data, modelling and analysis programs
├── notebooks/            Lifecycle narrative and saved outputs
├── models/               Frozen pipeline and metadata
├── data/                 Source documentation and aggregate reference data
├── reports/              Generated tables and figures
├── docs/                 Plans, decisions, findings and viva notes
├── requirements.txt      Runtime dependency pins
├── requirements-dev.txt  Development dependency pins
├── README.md             Setup and repository guide
└── AGENTS.md             Project rules and delivery instructions
```

---

# 3. Root Files

## [README.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/README.md)

### What it is

The main setup, data and repository guide.

### What we did

We documented:

- Python 3.12 setup,
- virtual-environment setup,
- runtime and development dependency installation,
- Streamlit startup,
- official data download,
- frozen model information,
- main test results,
- repository paths,
- the public app URL.

### Why it exists

It gives a new team member or examiner the shortest route to running the project.

### How to explain it

> README.md is the entry point for setup and reproduction. It explains what the project contains and how to start the app.

---

## [AGENTS.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/AGENTS.md)

### What it is

The project rule and lifecycle instruction file.

### What it controls

It specifies rules for:

- feature allowlisting,
- leakage prevention,
- household-aware splits,
- pipeline preprocessing,
- test-set sealing,
- model metrics,
- reproducibility,
- privacy,
- dependency pins,
- documentation,
- stage-based work,
- viva preparation.

### Why it exists

It prevents unsafe changes such as:

- adding labour-market status as a predictor,
- scaling or encoding before splitting,
- tuning on test data,
- opening test data multiple times,
- mixing household members across partitions,
- committing raw survey records.

### How to explain it

> AGENTS.md is the project's governance file. It defines the rules that every implementation stage must follow.

---

## [DATA_SOURCES.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/DATA_SOURCES.md)

### What it is

The source register for official data.

### What it records

- source names,
- official landing pages,
- downloaded files,
- access checks,
- source terms,
- source hashes,
- privacy or redistribution limitations.

### Why it exists

The project must be traceable to Pakistan Bureau of Statistics sources.

### How to explain it

> DATA_SOURCES.md explains where the data came from and records source-access evidence.

---

## [requirements.txt](C:/Users/sarim_llbpzcp/Desktop/HunarLens/requirements.txt)

### What it is

The exact runtime dependency list.

It pins packages including:

- pandas,
- numpy,
- scikit-learn,
- matplotlib,
- joblib,
- Streamlit,
- Altair.

### Why exact pins are used

The frozen pipeline was created with a particular scikit-learn version. Loading it with an incompatible version can produce incorrect or unusable results.

Exact pins also make the Streamlit deployment predictable.

### How to explain it

> requirements.txt keeps the app environment small and records the exact tested library versions.

---

## [requirements-dev.txt](C:/Users/sarim_llbpzcp/Desktop/HunarLens/requirements-dev.txt)

### What it is

Development-only dependencies.

It includes pytest, Jupyter and openpyxl.

### Why it exists

The deployed app does not need test tools or notebook libraries.

Data-building scripts need openpyxl to read Census Excel workbooks.

### How to explain it

> requirements-dev.txt separates development tools from the runtime app dependencies.

---

## [.gitignore](C:/Users/sarim_llbpzcp/Desktop/HunarLens/.gitignore)

### What it ignores

- `.venv/`
- Python caches
- pytest caches
- Jupyter checkpoints
- `data/raw/`
- `data/interim/`
- `hunarlens_youth.csv`
- `split_assignments.csv`
- `test_predictions.csv`
- submission archives

### Why it exists

Person-level survey records must not be committed unless redistribution is explicitly allowed.

Virtual environments and caches are also not source code.

### How to explain it

> The Git ignore file protects privacy and keeps generated or local-only artefacts out of the repository.

---

## [.streamlit/config.toml](C:/Users/sarim_llbpzcp/Desktop/HunarLens/.streamlit/config.toml)

### What it is

The Streamlit runtime configuration.

### Why it exists

It provides app-level Streamlit settings.

### How to explain it

> This file controls local and cloud Streamlit runtime behavior.

---

# 4. `src/hunarlens/` Source Package

## [src/hunarlens/__init__.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/__init__.py)

### What it is

Marks `hunarlens` as an importable Python package.

### Why it exists

Scripts, notebooks and tests can reuse source code instead of duplicating logic.

### How it works

```python
from hunarlens.config import RANDOM_STATE
from hunarlens.pipeline import build_model_pipeline
```

### Viva explanation

> It makes all HunarLens source modules importable as one package.

---

## [src/hunarlens/config.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/config.py)

### What it is

The central project configuration.

### What it contains

Repository paths, constants and the feature allowlist.

Important constants include:

- `RANDOM_STATE = 42`
- `TARGET = "is_unemployed"`
- `GROUP = "group_id"`
- `SPLIT = "split"`
- `AGE_MIN = 15`
- `AGE_MAX = 24`
- 70/15/15 split fractions
- five CV folds
- household clipping percentile
- category-frequency threshold

### Numeric features

- `age`
- `household_size`
- `children_under_15`
- `other_youth_15_24`
- `census_density`
- `census_urban_proportion`
- `census_household_size`

### Categorical features

- `sex`
- `marital_status`
- `relationship_to_head`
- `can_read`
- `can_write`
- `education_level`
- `currently_enrolled`
- `has_training`
- `province`
- `area`
- `head_sex`
- `head_education`

### Why it exists

It keeps settings in one source of truth.

Most importantly, it is the final feature allowlist.

### How to explain it

> config.py defines the shared constants and strictly limits model inputs. Anything not in FEATURES is excluded.

---

## [src/hunarlens/data.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/data.py)

### What it is

The household and Census data transformation module.

### What it does

- validates roster keys,
- combines `PCode + EBCode + HHNo`,
- creates integer household `group_id` values,
- counts household members,
- counts children under 15,
- counts other youth aged 15–24,
- identifies the household head,
- reads provincial and area Census workbooks,
- creates the Census lookup.

### Why it exists

Household context is needed for selected features, but raw household identifiers must not enter the machine-learning table.

### How it works

It processes the full roster before selecting youth.

This is necessary because an individual-level youth-only filter would remove children and older adults from household-size calculations.

### Viva explanation

> data.py calculates household summaries from the full roster and removes survey identifiers from the final feature table.

---

## [src/hunarlens/features.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/features.py)

### What it is

A custom scikit-learn transformer called `ApprovedFeatures`.

### What it creates

- `education_ordinal`
- `age_band`
- `children_share`
- `household_size_clipped`
- `sex_area`

### The feature meanings

`age_band` divides age into:

- 15–17,
- 18–20,
- 21–24.

`children_share` means:

```text
children_under_15 / household_size
```

`household_size_clipped` limits household size to a learned 99th percentile.

`sex_area` combines sex and rural/urban area.

### Why it exists

It performs feature engineering inside the machine-learning pipeline.

### How it learns safely

The `fit()` method learns the household-size cutoff from its training fold.

The `transform()` method applies that learned cutoff to later rows.

The cutoff is never learned from validation or test data.

### Viva explanation

> ApprovedFeatures creates derived fields and learns the household clipping threshold inside the pipeline.

---

## [src/hunarlens/pipeline.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/pipeline.py)

### What it is

The complete preprocessing-and-estimator pipeline.

### Pipeline structure

```text
ApprovedFeatures
  -> numeric preprocessing
  -> categorical preprocessing
  -> machine-learning estimator
```

### Numeric preprocessing

1. Median imputation.
2. Standard scaling.

### Categorical preprocessing

1. Most-frequent-category imputation.
2. One-hot encoding.
3. Rare-category grouping using the configured frequency threshold.

### Why it exists

It prevents preprocessing from being fitted outside the training fold.

It also ensures deployment uses exactly the same transformations as training.

### Viva explanation

> The saved pipeline contains feature engineering, imputation, scaling, encoding and the HGB estimator.

---

## [src/hunarlens/splits.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/splits.py)

### What it is

The household-aware split implementation.

### What it does

- creates 20 `StratifiedGroupKFold` folds,
- assigns 14 folds to training,
- assigns 3 folds to validation,
- assigns 3 folds to test,
- hashes the dataset,
- rejects stale split assignments.

### Why it exists

Members of one household should not appear in both training and validation.

Otherwise, the model could see nearly identical household members during both model fitting and evaluation.

### How it works

It uses `group_id` for grouping and `is_unemployed` for stratification.

### Viva explanation

> StratifiedGroupKFold keeps household members together while preserving approximate class balance.

---

## [src/hunarlens/eda.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/eda.py)

### What it is

Reproducible EDA functions.

### What it creates

- class-balance chart,
- age distribution,
- sex × area unemployment rates,
- province chart,
- education chart,
- training chart,
- missingness chart,
- numeric correlation heatmap,
- boxplots,
- household-size distributions,
- rare-category tables.

### Why it exists

EDA findings must be reproducible and not manually typed.

### How it works

It reads the modelling dataset and writes CSV tables and 200-DPI PNG figures.

It does not fit or tune a model.

### Viva explanation

> EDA describes the sample and detects distributions or unusual patterns. It does not make model decisions.

---

## [src/hunarlens/explain.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/explain.py)

### What it is

The model-explanation module.

### What it provides

- training medians and modes,
- individual permutation importance,
- grouped permutation importance,
- local what-if predictions,
- average predictions under alternative profiles.

### Permutation importance

For each feature or feature group:

1. Shuffle values.
2. Predict through the complete pipeline.
3. Measure decrease in average precision.
4. Repeat 20 times.

A decrease means the model relied on that field or group for ranking.

### Local what-if

One field is replaced with:

- its training median, or
- its training mode.

The prediction is recalculated while every other value stays fixed.

### Why it exists

The project needs model explainability without SHAP or causal claims.

### Viva explanation

> Permutation importance and what-if analysis explain model reliance. They do not prove that changing a person would cause unemployment to change.

---

## [src/hunarlens/app_utils.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/app_utils.py)

### What it is

Shared dashboard validation and prediction code.

### What it does

- normalizes category codes,
- validates numeric ranges,
- checks household-count consistency,
- checks household-head consistency,
- checks literacy consistency,
- joins Census values,
- detects rare combinations,
- calls the frozen pipeline,
- converts probability into a risk band.

### Why it exists

The app must use the same prediction and validation behavior as the saved model.

### How it works

Arbitrary user values are not sent directly to the model. They are first validated and normalized.

---

## [src/hunarlens/ui.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/ui.py)

### What it is

The probability-percentile helper.

### What it does

Interpolates a score against 101 validation quantiles.

### Why it exists

The app needs a relative ruler showing whether a profile score is lower or higher than the validation sample.

### Viva explanation

> It locates a score among saved aggregate validation quantiles. It does not calculate an individual percentile from the full population.

---

## [src/hunarlens/skills.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/skills.py)

### What it is

Disclosure-safe skills-gap helper functions.

### What it does

- suppresses small cells,
- flags unreliable estimates,
- renders aggregate totals,
- verifies report totals against generated tables.

### Why it exists

The skills extension must prevent small-cell disclosure and stale report values.

### Viva explanation

> It enforces small-cell rules and keeps skills documents synchronized with generated aggregate evidence.

---

## [src/hunarlens/evaluate.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/evaluate.py)

### What it is

A reserved evaluation module.

### Current role

It contains a placeholder and basic organization.

The complete test logic is currently implemented in [evaluate_on_test_set.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/evaluate_on_test_set.py).

### How to explain it

> The project intended this module to hold reusable metrics, but test-evaluation implementation is currently concentrated in the script.

---

# 5. `scripts/` Lifecycle Scripts

## [scripts/download_data.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/download_data.py)

### What it does

- discovers links from official PBS pages,
- downloads LFS and Census files,
- extracts ZIP archives,
- writes `data/raw/MANIFEST.json`.

### Why it exists

It avoids guessed URLs and makes acquisition traceable.

### Viva explanation

> The downloader obtains official PBS files and records URL, size and SHA-256 hash.

---

## [scripts/audit_raw_data.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/audit_raw_data.py)

### What it does

Summarizes survey schema and Census worksheet shapes.

### Why it exists

Before choosing a label or features, the team must inspect real column names and source structures.

### Viva explanation

> It provides source evidence without constructing a model or label prematurely.

---

## [scripts/build_modeling_dataset.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/build_modeling_dataset.py)

### What it does

- reconstructs the employment/unemployment label,
- tests search and availability routes,
- compares weighted totals with PBS totals,
- calculates full-roster household features,
- filters youth aged 15–24,
- joins Census lookup values,
- writes the modelling dataset,
- writes the row waterfall,
- writes missingness and reproduction evidence.

### Why it exists

The model dataset must be built only after the proposed label is approximately reproducible.

### Viva explanation

> It contains the official-label reproduction gate and creates the de-identified modelling table.

---

## [scripts/make_splits.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/make_splits.py)

### What it does

Creates the persistent train/validation/test assignments.

### Why it exists

Every experiment must use exactly the same household partition.

### Viva explanation

> It saves grouped split assignments and rejects stale assignments if the dataset changes.

---

## [scripts/compute_baselines.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/compute_baselines.py)

### What it does

- loads train and validation splits,
- evaluates the dummy baseline,
- scans individual features,
- creates baseline and leakage-tripwire outputs.

### Why it exists

It establishes a non-informative reference and checks whether a single field appears unexpectedly strong.

### Viva explanation

> The baseline shows what prevalence-only information achieves, while the tripwire asks whether suspicious predictors need investigation.

---

## [scripts/compare_models.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/compare_models.py)

### What it does

Runs model comparison experiments for:

- Logistic Regression,
- Random Forest,
- HistGradientBoosting,
- the dummy baseline.

### How it works

- training only supplies CV and tuning,
- validation supplies threshold and model comparison,
- test remains untouched,
- grouped CV refits on average precision,
- experiment checkpoints prevent lost or duplicate work.

### Why it exists

It provides a fair, reproducible model comparison.

### Viva explanation

> It is the main experiment script. It only uses training and validation for model choice.

---

## [scripts/review_model_comparison.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/review_model_comparison.py)

### What it does

Creates paired grouped-CV review tables and ablation evidence.

### Why it exists

The team needed more than final average scores before freezing HGB.

### Viva explanation

> Identical folds make paired differences more meaningful than unrelated model runs.

---

## [scripts/save_final_model.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/save_final_model.py)

### What it does

- fits HGB on training rows,
- compares raw and sigmoid calibration on validation,
- selects F1 and screening thresholds,
- creates risk bands,
- saves the Joblib pipeline,
- writes model metadata.

### Why it exists

It performs the historical model freeze.

### Important rule

This script should not be rerun on the submitted frozen artefact.

### Viva explanation

> It fits on training rows, chooses calibration and thresholds on validation labels, and freezes the pipeline before test access.

---

## [scripts/explain_model.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/explain_model.py)

### What it does

Creates permutation importance, grouped importance and partial profiles.

### Why it exists

The project needs an explanation process that uses validation only.

### Viva explanation

> It shuffles raw inputs through the full pipeline and reports changes in average precision.

---

## [scripts/analyze_enrolment_ablation.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/analyze_enrolment_ablation.py)

### What it does

Repeats grouped HGB CV with and without `currently_enrolled`.

### Why it exists

Enrolment was highly important but may interact with labour-force selection.

### Viva explanation

> The ablation estimates how much the field contributes while keeping identical household folds.

---

## [scripts/analyze_validation_calibration.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/analyze_validation_calibration.py)

### What it does

Compares validation observed rates with mean model probabilities.

### Why it exists

It shows whether subgroup averages and model probabilities differ substantially.

### Viva explanation

> These are descriptive validation averages, not individual calibration or proof of discrimination.

---

## [scripts/evaluate_on_test_set.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/evaluate_on_test_set.py)

### What it does

- verifies the frozen model SHA-256,
- writes the test-opening receipt,
- opens test rows once,
- saves test probabilities,
- calculates F1 and ranking metrics,
- performs household bootstrap,
- creates subgroup and error tables,
- creates test figures.

### Why it exists

It provides the final holdout evaluation and makes repeated rescores impossible.

### How it is protected

The script refuses to:

- run if predictions already exist,
- run if a test-opening receipt already exists,
- use a model hash different from the approved hash,
- rescore saved test probabilities.

### Viva explanation

> The test set was opened once. Every later analysis reads saved probabilities rather than rerunning the model.

---

## [scripts/build_rare_flags.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/build_rare_flags.py)

### What it does

Creates training-derived boolean flags for rare profiles.

### Why it exists

The app should warn about combinations with fewer than 20 training records.

### Privacy behavior

It stores no person rows or counts.

---

## [scripts/compute_score_quantiles.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/compute_score_quantiles.py)

### What it does

Creates 101 validation-probability quantiles.

### Why it exists

The app can show relative score position.

### Viva explanation

> Quantiles summarize validation scores but do not become individual records.

---

## [scripts/audit_app.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/audit_app.py)

### What it does

Checks app fixtures and descriptive profile patterns.

### Why it exists

The interface must use the exact pipeline, category values and validation logic.

---

## [scripts/check_app_runtime.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/check_app_runtime.py)

### What it does

Runs fixed app profiles using runtime dependencies only.

### Why it exists

The Streamlit cloud environment may not install development dependencies.

---

# 6. Skills-Gap Scripts

## [scripts/build_skills_dataset.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/build_skills_dataset.py)

Builds the separate weighted skills dataset and performs the skills reproduction checks.

It is separate from the unemployment model inputs.

---

## [scripts/analyze_skills_gap.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/analyze_skills_gap.py)

Creates weighted:

- unemployment by education,
- training differences,
- occupation mismatch,
- graduate absorption,
- approximate NEET,
- cluster-bootstrap intervals.

---

## [scripts/compute_skills_refinements.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/compute_skills_refinements.py)

Adds mismatch sensitivity, education-band tolerance and graduate outcomes.

---

## [scripts/analyze_occupation_variants.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/analyze_occupation_variants.py)

Compares mismatch measures between occupation norms.

It re-estimates occupation modes in cluster resamples.

---

## [scripts/analyze_model_shift.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/analyze_model_shift.py)

Creates validation-profile shifts for alternative education and training inputs.

These are model associations, not causal effects.

---

## [scripts/audit_skills_data.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/audit_skills_data.py)

Produces aggregate route and variable-availability evidence.

---

## [scripts/complete_skills_audit.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/complete_skills_audit.py)

Creates field-by-field variable verification evidence.

---

## [scripts/verify_skills_analysis.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/verify_skills_analysis.py)

Checks routes, categories and plausible age ranges in the skills dataset.

---

# 7. `app/` Dashboard Files

## [app/streamlit_app.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/streamlit_app.py)

### What it is

The public Streamlit entry point.

### What it does

- loads the frozen model,
- loads metadata,
- renders dashboard sections,
- validates profile inputs,
- predicts probabilities,
- renders risk bands,
- renders what-if explanations,
- loads report tables,
- displays limitations.

### How it uses the pipeline

The app passes a validated raw feature row to `predict_proba()`.

The pipeline performs the feature engineering and preprocessing again.

---

## [app/dashboard_component.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/dashboard_component.py)

### What it is

Python bridge for the custom HTML dashboard.

### Why it exists

The supplied prototype needs Streamlit integration.

### How it works

It:

- loads HTML,
- loads CSS,
- loads JavaScript,
- builds aggregate dashboard data,
- validates profile state,
- calls the same Python prediction functions.

It does not cache individual profile selections as personal records.

---

## [app/dashboard.html](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/dashboard.html)

### What it is

The custom dashboard markup.

It defines the overview, profile, skills and methodology layout.

---

## [app/dashboard.css](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/dashboard.css)

### What it is

Desktop and mobile dashboard styles.

### Why it exists

It implements the prototype layout and responsive behavior.

---

## [app/dashboard.js](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/dashboard.js)

### What it is

Dashboard interaction code.

It controls:

- page navigation,
- profile inputs,
- alternative profiles,
- result rendering,
- copy summary,
- chart updates.

---

## [app/skills_dashboard.js](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/skills_dashboard.js)

### What it is

The JavaScript for skills-gap dashboard visualizations.

### Why it exists

Skills-gap content is separate from individual model profiles.

---

## [app/style.css](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/style.css)

### What it is

Additional interface styling.

### Why it exists

It supplements Streamlit and the custom dashboard styles.

---

# 8. `models/`

## [models/final_pipeline.joblib](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models/final_pipeline.joblib)

### What it is

The frozen complete HGB pipeline.

### What it contains

- approved feature construction,
- numeric imputation,
- standard scaling,
- categorical imputation,
- one-hot encoding,
- HGB estimator.

### SHA-256

```text
6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3
```

### Why it matters

The app loads this file directly. There is no second model definition in the app.

---

## [models/metadata.json](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models/metadata.json)

### What it contains

- model parameters,
- Python and library versions,
- feature names,
- numeric ranges,
- category values,
- training reference values,
- prevalence,
- thresholds,
- risk bands,
- validation metrics,
- calibration comparison.

### Why it exists

It supplies app validation and display information without retraining.

---

## [models/score_quantiles.json](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models/score_quantiles.json)

### What it contains

101 frozen-model validation score quantiles.

### Why it exists

It supports the dashboard percentile ruler.

It contains aggregate values, not user profiles or test records.

---

# 9. `data/`

## [data/README.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/README.md)

Documents source, privacy and storage policies.

It explains:

- which raw files are ignored,
- why person-level data is not committed,
- which aggregate files are safe to track,
- source redistribution limitations.

---

## [data/pbs_table15_excerpt.txt](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/pbs_table15_excerpt.txt)

Stores a short source excerpt used for report and reproduction evidence.

---

## [data/processed/census_lookup.csv](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/processed/census_lookup.csv)

A small tracked province × area lookup containing:

- Census density,
- Census urban proportion,
- Census average household size.

The app joins it directly and does not load the raw Census workbooks.

---

## [data/processed/rare_combinations.csv](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/processed/rare_combinations.csv)

Contains boolean flags for rare age/enrolment and age/education combinations.

It contains no person records or exact counts.

---

## [data/processed/test_evaluation_receipt.json](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/processed/test_evaluation_receipt.json)

Records:

- test opening status,
- frozen model hash,
- prediction cache status,
- prediction SHA-256.

It prevents automatic test rescoring.

---

## Ignored person-level files

The project is designed to exclude:

- `data/raw/`
- `data/interim/`
- `data/processed/hunarlens_youth.csv`
- `data/processed/split_assignments.csv`
- `data/processed/test_predictions.csv`

The README says the test-prediction cache is currently unavailable. The saved aggregate test outputs remain.

---

# 10. `notebooks/`

The notebooks narrate the life cycle. Logic is placed in source modules and scripts, while notebooks provide readable saved outputs.

## [notebooks/data_audit.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/data_audit.ipynb)

Covers source audit, field uncertainty and questionnaire/Stata conflicts.

---

## [notebooks/exploratory_analysis.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/exploratory_analysis.ipynb)

Covers class balance, age, missingness, correlations and descriptive unemployment rates.

---

## [notebooks/baseline_and_pipeline.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/baseline_and_pipeline.ipynb)

Covers the dummy baseline, grouped split and preprocessing pipeline.

---

## [notebooks/model_comparison.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/model_comparison.ipynb)

Covers Logistic Regression, Random Forest, HGB, CV and validation thresholding.

---

## [notebooks/final_model_and_explainability.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/final_model_and_explainability.ipynb)

Covers final HGB, calibration, metadata, permutation importance and partial profiles.

---

## [notebooks/test_set_evaluation.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/test_set_evaluation.ipynb)

Covers the sealed test opening, test metrics, bootstrap and subgroup findings.

It should not be rerun simply to obtain new test metrics.

---

## [notebooks/skills_gap_analysis.ipynb](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks/skills_gap_analysis.ipynb)

Covers education, training, mismatch, occupation, NEET and model-shift findings.

---

# 11. `docs/`

## [docs/process/project_plan.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/process/project_plan.md)

The original stage-by-stage implementation plan.

It contains lifecycle stages, acceptance gates and viva questions.

It should not be edited casually because repository rules restrict changes.

---

## [docs/process/skills_gap_plan.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/process/skills_gap_plan.md)

The stage plan for the skills-gap extension.

It separates labour-market analyses from model predictors.

---

## [docs/data_dictionary.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/data_dictionary.md)

A preliminary raw-field dictionary.

It helps explain Stata fields and whether they are safe, uncertain or forbidden.

---

## [docs/label_definition.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/label_definition.md)

The detailed unemployment-label decision record.

It documents:

- employed routes,
- unemployed routes,
- future-starter approximation,
- search and availability,
- absence-code conflicts,
- weighted reproduction,
- household and geographic decisions.

---

## [docs/DECISIONS.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/DECISIONS.md)

The main decision audit trail.

It records:

- human decisions,
- technical approvals,
- rejected approaches,
- test-set opening,
- model freeze,
- dashboard choices,
- skills-gap decisions.

---

## [docs/eda_findings.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/eda_findings.md)

Human-readable explanations of EDA tables and figures.

---

## [docs/model_findings.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/model_findings.md)

Validation model-explanation findings.

It distinguishes:

- permutation importance,
- observed subgroup unemployment,
- partial profiles,
- local what-if,
- individual app profiles,
- causation.

---

## [docs/test_findings.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/test_findings.md)

The final sealed-test report.

It summarizes test:

- F1,
- precision,
- recall,
- PR-AUC,
- ROC-AUC,
- lift,
- bootstrap intervals,
- subgroup results,
- risk bands,
- limitations.

---

## [docs/skills_gap_methods.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_methods.md)

Explains weighting, cluster bootstrap, mismatch definitions and model-profile shifts.

---

## [docs/skills_gap_findings.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_findings.md)

Contains the detailed skills-gap results and sensitivity comparisons.

---

## [docs/skills_gap_summary.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_summary.md)

A short plain-language summary of skills-gap findings.

---

## [docs/skills_gap_data_audit.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_data_audit.md)

The variable-routing and data-quality audit for the skills extension.

---

# 12. `reports/`

## `reports/tables/`

This folder contains generated CSV evidence.

Important groups include:

- row waterfall,
- feature missingness,
- feature value counts,
- rare categories,
- split summary,
- baseline validation,
- experiments,
- CV fold scores,
- learning curves,
- ablations,
- calibration validation,
- validation thresholds,
- permutation importance,
- test metrics,
- test bootstrap confidence intervals,
- test subgroups,
- test error distributions,
- skills-gap outcome tables.

### Why it exists

Tables are generated from code and can be cited in reports and notebooks.

---

## `reports/figures/`

This folder contains 200-DPI PNG figures.

Important figures include:

- class balance,
- age distribution,
- sex × area unemployment,
- province and education rates,
- missingness,
- numeric correlations,
- validation PR curves,
- validation calibration,
- permutation importance,
- test confusion matrix,
- test PR curve,
- test calibration,
- test gain/lift,
- skills graphs.

### Why it exists

The project creates figures programmatically so they remain reproducible.

---

# 13. Major Project Results

## Frozen model

- Model: HistGradientBoostingClassifier
- Python: 3.12.10
- scikit-learn: 1.9.1
- Random state: 42
- Calibration: raw probabilities
- F1 threshold: 0.1829313608888501
- Screening threshold: 0.154107368289897
- Training rows: 18,657
- Validation rows: 3,997
- Test rows: 3,999

## Test results

| Result | Value |
|---|---:|
| F1 | 0.360 |
| Precision | 0.273 |
| Recall | 0.530 |
| PR-AUC | 0.303 |
| ROC-AUC | 0.752 |
| Top-10% lift | 2.81 |
| Stratified dummy F1 | 0.123 |
| Stratified dummy PR-AUC | 0.127 |
| Test prevalence | 12.703% |

---

# 14. Techniques Used

## Binary classification

The target has two classes:

- 0 = employed,
- 1 = unemployed.

## Supervised learning

The model learns from labelled survey records.

## Grouped stratified splitting

Households remain in one partition and class balance is preserved approximately.

## Imputation

Missing numeric values use a median.

Missing categorical values use the most frequent category.

## Standard scaling

Numeric variables are put on a comparable scale.

## One-hot encoding

Categorical variables become binary indicator columns.

## Feature engineering

The pipeline creates age bands, household clipping, children share and sex × area interaction.

## Logistic Regression

A linear probabilistic classifier.

## Random Forest

An ensemble of decision trees.

## HistGradientBoosting

An additive ensemble of sequential tree learners.

## Grid search

Tests a defined parameter grid.

## Randomized search

Tests a limited random parameter selection.

## Average-precision refit

Model selection prioritizes the ranking of the positive class.

## Calibration

The project checks whether predicted probabilities match observed frequencies.

## Threshold tuning

Validation labels choose F1 and screening cutoffs.

## Permutation importance

Feature shuffling measures reliance.

## What-if explanations

One field is replaced with a reference value.

## Household bootstrap

Whole households are sampled for test uncertainty intervals.

## Survey weighting

Weights estimate population totals in skills-gap and reproduction analysis.

---

# 15. Project Limitations

- The model covers labour-force youth, not all youth.
- Model evaluation is unweighted.
- The model may encode historical sex and geographic associations.
- Enrolment may be affected by labour-force selection.
- Future-starter timing cannot be verified from the available data.
- Subgroup estimates can be unstable.
- Skills mismatch is statistical, not a direct measure of competence.
- The app should not be used for individual employment or benefit decisions.

---

# 16. Recommended Viva Sequence

A student should explain the project in this order:

1. Project goal and target.
2. LFS and Census data sources.
3. Unemployment label construction.
4. Approved feature allowlist.
5. Household and Census feature creation.
6. Household-aware train/validation/test split.
7. Preprocessing pipeline.
8. Dummy and candidate models.
9. CV and model selection.
10. Validation calibration and thresholds.
11. Frozen model and SHA-256.
12. One-time test evaluation.
13. Confusion matrix and positive-class metrics.
14. Permutation importance and what-if limitations.
15. Skills-gap distinction.
16. Streamlit app behavior.
17. Privacy and final limitations.

A strong one-sentence summary is:

> HunarLens constructs a leak-free household-aware pipeline for predicting youth unemployment, freezes one HGB model using training and validation data, evaluates it once on a sealed test set and presents its aggregate associations through a Streamlit dashboard.
