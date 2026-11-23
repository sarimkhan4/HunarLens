# HunarLens Project Overview

## 1. Purpose

HunarLens is a CT-378 machine-learning semester project investigating unemployment vulnerability among Pakistani youth aged 15–24 who are already in the labour force.

It has two separate parts:

1. A predictive model for whether a labour-force youth is employed or unemployed.
2. A skills-gap analysis examining education, training, occupation, unemployment and statistical mismatch.

The project is an explainable, aggregate-research application. It is not a decision system for making decisions about individual people.

---

## 2. Classification Task

The target column is `is_unemployed`.

- `1` means unemployed.
- `0` means employed.

The population is limited to youth aged 15–24 who are in the labour force. This means that employed youth and unemployed youth are included, while youth outside the labour force are excluded.

The main positive-class metric is F1-score. The project also reports precision, recall, PR-AUC, ROC-AUC, confusion matrix and lift.

---

## 3. Data Sources

### Labour Force Survey 2024–25

The primary person-level source is the Pakistan Bureau of Statistics Labour Force Survey 2024–25.

The local raw Stata file is [data/raw/LFS 2024-25.sav web.dta](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/raw/LFS%202024-25.sav%20web.dta). Raw person-level data is not committed to Git.

### Census 2023

The project uses Census Excel workbooks for:

- population density,
- urban proportion,
- average household size.

The small aggregate lookup is stored in [census_lookup.csv](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/processed/census_lookup.csv).

### Source documentation

- [DATA_SOURCES.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/DATA_SOURCES.md)
- [data_dictionary.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/data_dictionary.md)
- [label_definition.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/label_definition.md)

---

## 4. Data Rules

### Predictor allowlist

Only variables explicitly listed in [config.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/config.py) may enter `X`.

Numeric features are:

- `age`
- `household_size`
- `children_under_15`
- `other_youth_15_24`
- `census_density`
- `census_urban_proportion`
- `census_household_size`

Categorical features are:

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

### Forbidden predictors

The model must not use:

- employment status,
- job search,
- availability for work,
- absence reasons,
- hours worked,
- occupation,
- industry,
- wages,
- unemployment duration,
- reason for not working,
- household identifiers,
- survey weights,
- PSU identifiers,
- record identifiers,
- variables used directly to derive the label.

This allowlist prevents label leakage.

---

## 5. Central Configuration

[config.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/config.py) contains the project constants:

| Constant | Meaning |
|---|---|
| `RANDOM_STATE = 42` | Reproducible random operations |
| `TARGET = "is_unemployed"` | Positive target is unemployed |
| `GROUP = "group_id"` | Household grouping column |
| `SPLIT = "split"` | Train, validation or test assignment |
| `AGE_MIN = 15` | Minimum youth age |
| `AGE_MAX = 24` | Maximum youth age |
| `SPLIT_FRACTIONS` | 70% train, 15% validation, 15% test |
| `N_CV_FOLDS = 5` | Five grouped cross-validation folds |
| `HOUSEHOLD_CLIP_QUANTILE = 0.99` | 99th-percentile household-size clip |
| `MIN_CATEGORY_FREQUENCY = 50` | Rare categorical-value grouping threshold |

---

## 6. Dataset Construction

[build_modeling_dataset.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/build_modeling_dataset.py) constructs the modelling dataset.

Its responsibilities are:

1. Read the LFS records.
2. Reconstruct the employed and unemployed routes conservatively.
3. Compare weighted estimates with PBS totals.
4. Stop when the published-total reproduction gate fails.
5. Filter ages 15–24.
6. Keep employed or unemployed youth only.
7. Count the full household roster.
8. Add household-derived features.
9. Join province and area Census indicators.
10. Export the model table and aggregate audit tables.

The weighted reproduction check is intended to prevent an incorrect provisional label from silently becoming a permanent dataset.

[data.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/data.py) also constructs the integer `group_id` from `PCode + EBCode + HHNo`. Original identifiers are not exported to the final model table.

---

## 7. Household Features

Full-roster information is used to calculate:

- `household_size`
- `children_under_15`
- `other_youth_15_24`
- `head_sex`
- `head_education`

The household key is calculated before youth filtering. This prevents children and older household members from changing household counts.

The project found that the approved group key could contain up to 54 records. The key is therefore retained as a grouping limitation and is not used as a model feature.

---

## 8. Train, Validation and Test Splits

[splits.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/splits.py) creates the split assignments.

The project uses `StratifiedGroupKFold`, not an ordinary random split.

It creates 20 grouped folds:

- folds 1–14 become training,
- folds 15–17 become validation,
- folds 18–20 become test.

One household cannot appear in more than one split.

The split assignment file is [split_assignments.csv](C:/Users/sarim_llbpzcp/Desktop/HunarLens/data/processed/split_assignments.csv).

It also stores a SHA-256 hash of the modelling dataset so stale assignments are rejected.

The actual split sizes are:

| Split | Rows | Positive cases | Prevalence |
|---|---:|---:|---:|
| Train | 18,657 | 2,368 | 12.692% |
| Validation | 3,997 | 507 | 12.685% |
| Test | 3,999 | 508 | 12.703% |

---

## 9. Preprocessing

[pipeline.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/pipeline.py) combines feature engineering, preprocessing and the estimator in one scikit-learn `Pipeline`.

The pipeline is:

```text
ApprovedFeatures
    -> numeric preprocessing
    -> categorical preprocessing
    -> machine-learning estimator
```

### Feature engineering

[features.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/features.py) creates:

- `education_ordinal`
- `age_band`
- `children_share`
- `household_size_clipped`
- `sex_area`

The household-size clipping threshold is learned only from the training rows passed to `fit`.

Age bands are 15–17, 18–20 and 21–24.

### Numeric preprocessing

Numeric fields receive:

1. median imputation,
2. standard scaling.

Median imputation replaces missing values with the training median.

Standard scaling removes the mean and divides by the standard deviation.

### Categorical preprocessing

Categorical fields receive:

1. most-frequent-value imputation,
2. one-hot encoding.

One-hot encoding turns category values into binary columns.

Rare categories are grouped according to the minimum category-frequency setting.

The complete pipeline prevents preprocessing from fitting on validation or test data.

---

## 10. Model Comparison

[compare_models.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/compare_models.py) compares:

- `DummyClassifier`,
- Logistic Regression,
- Random Forest,
- HistGradientBoosting.

### DummyClassifier

The stratified dummy baseline makes random positive predictions according to class prevalence.

It is the no-signal reference model.

### Logistic Regression

Logistic Regression is a linear probabilistic classifier.

It estimates:

```text
P(is_unemployed = 1)
```

It was tested both with and without class weighting.

### Random Forest

Random Forest averages many decision trees.

The search considered:

- number of trees,
- maximum depth,
- minimum leaf size,
- maximum features,
- class weights.

### HistGradientBoosting

HistGradientBoosting is an additive tree model that builds new trees sequentially to correct previous errors.

It was the final selected model.

Final parameters include:

- `max_iter = 200`
- `learning_rate = 0.06`
- `max_leaf_nodes = 15`
- `min_samples_leaf = 50`
- `l2_regularization = 10`
- `class_weight = None`
- `random_state = 42`

---

## 11. Cross-Validation and Model Selection

Five-fold grouped cross-validation is performed on the training split only.

Its main metric is average precision. It measures how well the model ranks unemployed records above employed records.

The no-skill PR-AUC is approximately the positive-class prevalence.

Mean grouped-CV average precision was:

| Model | CV average precision |
|---|---:|
| Logistic Regression | 0.2811 |
| Random Forest | 0.3076 |
| HistGradientBoosting | 0.2977 |
| Stratified Dummy | 0.1260 |

Random Forest had the highest CV average precision.

However, its advantage over HGB was 0.0099, below the approved 0.01 tie margin. The team selected HGB because it had a smaller training-to-CV gap, smaller file size and faster prediction time.

---

## 12. Threshold Selection

A probability threshold converts a score into a binary prediction.

The primary F1 threshold is:

```text
0.1829313608888501
```

The screening threshold is:

```text
0.154107368289897
```

The primary threshold optimizes F1 on validation data.

The screening threshold targets at least 60% validation recall.

These thresholds were selected before test evaluation. The same validation labels were used to choose and initially measure them, so they are optimistic estimates.

---

## 13. Calibration

[save_final_model.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/save_final_model.py) compares raw HGB probabilities with sigmoid-calibrated probabilities.

| Method | Brier score | Fixed-bin ECE |
|---|---:|---:|
| Raw | 0.100341 | 0.011770 |
| Sigmoid | 0.100335 | 0.009252 |

The calibration improvement did not meet the approved 2% relative Brier-score rule, so the raw probabilities were retained.

### Brier score

The Brier score measures average squared error in probability predictions.

### ECE

Expected Calibration Error compares mean predicted probability with observed outcome frequency inside fixed probability bins.

---

## 14. Metrics

### F1-score

F1 balances precision and recall:

```text
F1 = 2 × precision × recall / (precision + recall)
```

### Precision

Precision is the fraction of predicted unemployed people who are actually unemployed.

### Recall

Recall is the fraction of unemployed people correctly identified.

### PR-AUC

PR-AUC, or average precision, summarizes precision across recall levels.

It is more informative than accuracy for a small positive class.

### ROC-AUC

ROC-AUC measures ranking quality across possible thresholds.

### Lift at 10%

Top-10% lift compares unemployment prevalence among the highest-risk 10% with overall prevalence.

### Confusion matrix

The confusion matrix contains:

- true positives,
- false positives,
- false negatives,
- true negatives.

### Accuracy

Accuracy is reported but is not used to select models because it can hide poor performance on the minority positive class.

---

## 15. Final Test Evaluation

[evaluate_on_test_set.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts/evaluate_on_test_set.py) opens the test split exactly once.

Before test access:

- model choice was frozen,
- hyperparameters were frozen,
- calibration was frozen,
- thresholds were frozen,
- model SHA-256 was verified.

The approved model hash is:

```text
6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3
```

Saved test probabilities are the only source for later test tables and figures.

The test metrics are in [test_metrics.csv](C:/Users/sarim_llbpzcp/Desktop/HunarLens/reports/tables/test_metrics.csv).

| Model or threshold | F1 | Precision | Recall | PR-AUC | ROC-AUC | Lift@10 |
|---|---:|---:|---:|---:|---:|---:|
| HGB F1 threshold | 0.360 | 0.273 | 0.530 | 0.303 | 0.752 | 2.81 |
| HGB screening threshold | 0.354 | 0.247 | 0.628 | 0.303 | 0.752 | 2.81 |
| Stratified Dummy | 0.123 | 0.125 | 0.122 | 0.127 | 0.499 | 0.87 |

At the primary threshold:

- 269 unemployed people were true positives,
- 239 unemployed people were false negatives,
- 716 employed people were false positives,
- 2,775 employed people were true negatives.

A 1,000-resample household-grouped bootstrap gave:

- F1 95% interval: 0.328–0.393,
- PR-AUC 95% interval: 0.267–0.343.

The bootstrap resamples households rather than individual records.

---

## 16. Explainability

[explain.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/explain.py) calculates permutation importance and what-if changes.

### Permutation importance

Permutation importance:

1. shuffles a field or field group,
2. predicts through the complete fitted pipeline,
3. measures the decrease in average precision,
4. repeats 20 times.

A decrease indicates model dependence on that field or group.

It does not prove causation.

Validation permutation importance findings:

| Feature group | Importance |
|---|---:|
| Education | 0.1106 |
| Enrolment | 0.0820 |
| Geography | 0.0618 |
| Sex | 0.0469 |
| Age | 0.0284 |
| Training | 0.0283 |
| Marital and relationship | 0.0225 |
| Household | 0.0221 |

### Local what-if

Local what-if replaces one input with its training median or mode and reports the change in predicted probability.

It leaves all other inputs fixed.

It demonstrates model sensitivity, not a real-world causal effect.

### Partial profiles

Partial profiles assign one value across the validation records and calculate mean predictions.

They answer:

> How does this model respond when this input is set to a sequence of values?

They do not establish causal effects or individual outcomes.

---

## 17. Risk Bands

The app derives bands from validation-score quantiles:

| Band | Probability |
|---|---:|
| High | 0.268655 or higher |
| Elevated | 0.158568–0.268654 |
| Lower than most | below 0.158568 |

On test data:

| Band | Count | Observed unemployment |
|---|---:|---:|
| High | 433 | 34.9% |
| Elevated | 813 | 19.4% |
| Lower | 2,753 | 7.2% |

These are relative ranking bands, not individual diagnoses or decision thresholds.

---

## 18. Streamlit Dashboard

The application entry point is [streamlit_app.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/app/streamlit_app.py).

Its features include:

- profile explorer,
- live unemployment probability,
- training sample base rate,
- relative risk band,
- 100-square probability graphic,
- validation percentile ruler,
- one-variable what-if chart,
- model importance chart,
- methodology and limitations,
- skills-gap sections.

[app_utils.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/app_utils.py) validates inputs, joins Census values and calls the frozen pipeline.

[ui.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/ui.py) provides display and percentile helpers.

The app does not save or log user-entered form values.

The live app is:

<https://hunar-lens.streamlit.app/>

---

## 19. Skills-Gap Analysis

The skills track is implemented in [skills.py](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens/skills.py).

It analyzes:

- unemployment by education,
- training differences,
- education mismatch,
- occupation modes,
- graduate absorption,
- approximate NEET,
- frozen-model profile shifts.

Education and training are used as skill proxies.

They do not directly measure employer demand, competence or vacancies.

### Statistical mismatch

Mismatch means that a worker's education band differs from the most common education band in their occupation group.

It is not evidence that the worker is personally underqualified or overqualified.

### Skills findings

- Unemployment rises from 8.2% for no formal education to 22.6% for degree-level youth.
- Training is 8.9 percentage points lower among unemployed youth.
- Approximate NEET is 29.3% of youth.
- Strict mismatch shares vary across reference norms from about 41% to 46%.
- Degree and occupation mismatch must be interpreted with coarse education bands and labour-force selection.

Documentation is in:

- [skills_gap_summary.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_summary.md)
- [skills_gap_methods.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_methods.md)
- [skills_gap_findings.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_findings.md)
- [skills_gap_data_audit.md](C:/Users/sarim_llbpzcp/Desktop/HunarLens/docs/skills_gap_data_audit.md)

---

## 20. Repository Structure

### Source package

[src/hunarlens/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/src/hunarlens)

- `config.py`: constants and feature allowlist
- `data.py`: household and Census construction
- `splits.py`: household-aware splits
- `features.py`: custom feature transformer
- `pipeline.py`: preprocessing and estimator pipeline
- `explain.py`: permutation importance and what-if
- `app_utils.py`: dashboard validation and prediction
- `ui.py`: interface helpers
- `skills.py`: skills-gap helpers
- `eda.py`: exploratory-analysis helpers

### Scripts

[scripts/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/scripts)

Important scripts include:

- `download_data.py`
- `audit_raw_data.py`
- `build_modeling_dataset.py`
- `make_splits.py`
- `compare_models.py`
- `save_final_model.py`
- `explain_model.py`
- `evaluate_on_test_set.py`
- `build_skills_dataset.py`
- `analyze_skills_gap.py`
- `make_submission.py`
- `write_project_report.py`

### Notebooks

[notebooks/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/notebooks)

The notebooks follow the data, EDA, pipeline, model comparison, explanation and test-evaluation stages.

### Tests

[tests/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/tests)

Tests cover:

- dataset construction,
- label reproduction,
- model pipeline,
- grouped splits,
- leakage safeguards,
- model freeze,
- test-evaluation safeguards,
- dashboard functions,
- skills calculations,
- privacy,
- reports,
- submission packaging.

The test suite is reported as 69 passing tests with no failures or errors.

### Reports

[reports/tables/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/reports/tables) contains CSV outputs.

[reports/figures/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/reports/figures) contains PNG outputs.

---

## 21. Frozen Model Artefacts

[models/](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models) contains:

- [final_pipeline.joblib](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models/final_pipeline.joblib)
- [metadata.json](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models/metadata.json)
- [score_quantiles.json](C:/Users/sarim_llbpzcp/Desktop/HunarLens/models/score_quantiles.json)

The pipeline contains:

- approved feature construction,
- imputation,
- scaling,
- one-hot encoding,
- HistGradientBoosting.

The metadata contains:

- model parameters,
- feature ranges,
- category values,
- training reference values,
- thresholds,
- risk bands,
- training prevalence,
- dependency versions.

---

## 22. Important Terminology

| Term | Meaning |
|---|---|
| Target | Column that the model predicts |
| Feature | Input used by the model |
| Allowlist | Exact approved set of permitted features |
| Leakage | Hidden outcome or future information entering the model |
| Pipeline | Linked sequence of preprocessing and modelling |
| Imputation | Replacing missing values |
| One-hot encoding | Replacing categories with binary indicator columns |
| Standard scaling | Rescaling numeric features to a mean of zero |
| Feature engineering | Creating new inputs from existing fields |
| Household-aware split | Keeping household members in one partition |
| Stratified split | Preserving positive-class prevalence |
| Cross-validation | Repeated training and validation on training data |
| Hyperparameter | Configuration set before model fitting |
| Grid search | Exhaustive parameter search |
| Randomized search | Random subset of parameter combinations |
| Threshold | Probability cut-off for a binary class |
| Baseline | Simple reference model |
| DummyClassifier | Non-informative baseline |
| Prevalence | Share of positive cases |
| F1 | Balance of precision and recall |
| Precision | Accuracy among predicted positives |
| Recall | Fraction of actual positives found |
| PR-AUC | Precision-recall ranking score |
| ROC-AUC | Overall positive/negative ranking score |
| Lift | Improvement over prevalence |
| Confusion matrix | TP, FP, FN and TN counts |
| Brier score | Probability prediction error |
| ECE | Calibration error across probability bins |
| Permutation importance | Ranking loss after shuffling input values |
| Partial profile | Average model response under substituted values |
| Frozen model | Approved model not changed after freeze |
| Bootstrap | Repeated resampling to estimate variation |
| Survey weight | Factor estimating population totals |
| NEET | Not in education, employment or training |
| Approximate NEET | Local proxy when recent training cannot be identified |
| Skills mismatch | Education differing from occupation-reference mode |
| Association | Statistical relationship represented in data |
| Causation | Demonstrated cause-and-effect relationship |

---

## 23. Limitations

- The model covers youth in the labour force, not all youth.
- The model evaluation is unweighted.
- The model can encode historical sex and geographic associations.
- Enrolment may be affected by labour-force selection.
- Small subgroup estimates may be unstable.
- Survey weights do not capture the complete test-design uncertainty.
- Rare profiles have greater uncertainty.
- The future-starter approximation cannot verify the ILO start-date condition.
- Skills mismatch is a statistical occupation comparison, not a skill test.
- Probability estimates must not determine employment, benefits, admissions or legal eligibility.

---

## 24. Viva Summary

A concise explanation is:

> HunarLens predicts unemployment among Pakistani youth aged 15–24 who are in the labour force. It creates a household-aware 70/15/15 split, uses an approved feature allowlist, combines feature engineering and preprocessing with a scikit-learn pipeline, tunes only with training data, chooses thresholds using validation data and evaluates the frozen HistGradientBoosting model once on the test set. On test data it achieved 0.360 F1, 0.273 precision, 0.530 recall and 0.303 PR-AUC. The stratified dummy achieved 0.123 F1 and 0.127 PR-AUC.

The key interpretation is:

> The model represents associations in the survey data. It does not establish causation and should not be used to make decisions about individuals.
