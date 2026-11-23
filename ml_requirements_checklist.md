# ML lifecycle and platform requirements checklist

The repository covers all seven ML lifecycle requirements and the Streamlit application requirements. The public deployment URL is documented, but the browser tool could not access it during this review, so current live availability remains unverified.

This is a review of existing code and saved outputs, not a fresh execution of training, evaluation or automated tests.

| Requirement | Status | Implementation and evidence |
|---|---|---|
| **1. EDA: distributions, missing values, outliers, correlations, class balance; at least five plots** | Covered | [Exploratory analysis notebook](../notebooks/exploratory_analysis.ipynb) contains **16 embedded plots**, covering class balance, age distributions, missing values, outlier boxplots, correlations, household distributions and unemployment by demographic group. Plot implementation: [eda.py](../src/hunarlens/eda.py). Interpretation: [EDA findings](eda_findings.md). |
| **2. Imputation, encoding, scaling and feature engineering inside a training-only scikit-learn Pipeline** | Covered | [pipeline.py](../src/hunarlens/pipeline.py) combines median imputation and standard scaling for numeric features with most-frequent imputation and one-hot encoding for categorical features. [features.py](../src/hunarlens/features.py) constructs age bands, education ordinal, children's household share, household-size clipping and sex–area interaction. Model-fitting code uses training rows, and cross-validation fits preprocessing within each training fold. |
| **3. Train/validation/test split** | Covered | Household-grouped, stratified approximately **70/15/15**: **18,657 training / 3,997 validation / 3,999 test** rows. Implementation: [splits.py](../src/hunarlens/splits.py) and [make_splits.py](../scripts/make_splits.py). Saved evidence: [split_summary.csv](../reports/tables/split_summary.csv). This is cross-sectional classification; a time-series split is not required. |
| **4. Simple baseline plus at least three course algorithms** | Covered | Stratified Dummy baseline, **Logistic Regression, Random Forest and HistGradientBoosting**. Implementation: [compare_models.py](../scripts/compare_models.py). Narrative: [model comparison notebook](../notebooks/model_comparison.ipynb). Results: [experiments.csv](../reports/tables/experiments.csv). |
| **5. Five-fold GridSearchCV or RandomizedSearchCV tuning** | Covered | **Five-fold StratifiedGroupKFold** on training households. Logistic Regression uses GridSearchCV; Random Forest and HGB use RandomizedSearchCV. Selection uses cross-validation average precision. Evidence: [compare_models.py](../scripts/compare_models.py) and [cv_fold_scores.csv](../reports/tables/cv_fold_scores.csv). |
| **6. Appropriate held-out metrics, once-only test evaluation, fitting gaps and error discussion** | Covered, with an archive limitation | Saved test metrics include F1, precision, recall, PR-AUC, ROC-AUC and confusion-matrix counts, alongside the Dummy. [evaluate_on_test_set.py](../scripts/evaluate_on_test_set.py) implements model-hash checks and a score-once receipt. Evidence: [test evaluation notebook](../notebooks/test_set_evaluation.ipynb), [test findings](test_findings.md), [test_metrics.csv](../reports/tables/test_metrics.csv), [bootstrap intervals](../reports/tables/test_bootstrap_ci.csv), [subgroup results](../reports/tables/test_subgroups.csv) and [error distributions](../reports/tables/test_error_distributions.csv). Fitting analysis: [generalization_gap.csv](../reports/tables/generalization_gap.csv), [grouped learning curve](../reports/figures/grouped_learning_curve.png) and [validation curve](../reports/figures/forest_validation_curve.png). |
| **7. Save final pipeline with joblib and pin package versions** | Covered | [final_pipeline.joblib](../models/final_pipeline.joblib) exists. Saving implementation: [save_final_model.py](../scripts/save_final_model.py). [requirements.txt](../requirements.txt) contains exact `==` pins; scikit-learn **1.9.1** matches [metadata.json](../models/metadata.json). |
| **Streamlit input form** | Covered | Profile explorer in [streamlit_app.py](../app/streamlit_app.py) and the dashboard component files. Input preparation and checks: [app_utils.py](../src/hunarlens/app_utils.py). |
| **Prediction with confidence/probability** | Covered | The app displays predicted unemployment probability, the training base rate, a risk band and a threshold flag. The displayed probability is a model estimate, not a confidence interval. |
| **At least one explanatory chart** | Covered | Grouped permutation importance and local what-if explanations. Implementation: [explain.py](../src/hunarlens/explain.py) and the app. Saved evidence: [grouped permutation importance](../reports/tables/grouped_permutation_importance.csv). |
| **Public Streamlit Community Cloud deployment** | Documented; live check inconclusive | [README](../README.md) records [hunar-lens.streamlit.app](https://hunar-lens.streamlit.app/). The automated browser check could not access the URL. Confirm public access in an incognito browser without signing in. |

## Saved test results

Source: [test_metrics.csv](../reports/tables/test_metrics.csv). HGB values below use the frozen primary F1 threshold; displayed values are rounded to four decimal places.

| Metric | Frozen HGB | Stratified Dummy |
|---|---:|---:|
| F1 | 0.3603 | 0.1234 |
| Precision | 0.2731 | 0.1247 |
| Recall | 0.5295 | 0.1220 |
| PR-AUC | 0.3031 | 0.1268 |
| ROC-AUC | 0.7520 | 0.4987 |

## Remaining evidence gaps

- The `tests/` directory is absent after cleanup. The earlier automated leakage and application checks therefore cannot currently be rerun from this directory.
- The original `data/processed/test_predictions.csv` cache is unavailable. Aggregate test tables, figures and the evaluation receipt remain, but the original row-level predictions cannot currently be independently checked. **Do not rescore the test set to replace the cache.**
- Current public deployment availability needs a manual browser check.

## Model integrity

The review did not change the model or its results. The model file hash matched the recorded SHA-256:

```text
6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3
```
