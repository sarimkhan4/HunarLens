# What: generates submission report drafts from the saved aggregate evidence.
# Why: results should remain traceable and not require model or test rescoring.
# Viva: published and derived statistics come from recorded tables, not memory.
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"
DOCS = ROOT / "docs"


def load(name):
    return pd.read_csv(TABLES / f"{name}.csv", keep_default_na=False)


def md_table(frame):
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for values in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value).replace("|", "/") for value in values) + " |")
    return "\n".join(lines)


def main():
    metrics = load("test_metrics")
    interval = load("test_bootstrap_ci")
    splits = load("split_summary")
    waterfall = load("row_waterfall")
    comparison = load("generalization_gap")
    subgroups = load("test_subgroups")
    education = load("skills_unemployment_by_education")
    mismatch = load("skills_mismatch_variants")
    neet = load("skills_neet")
    params = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    hgb = metrics.loc[metrics.model_threshold.eq("HGB F1")].iloc[0]
    dummy = metrics.loc[metrics.model_threshold.eq("Stratified Dummy")].iloc[0]
    f1_ci = interval.loc[interval.model_threshold.eq("HGB F1") & interval.metric.eq("f1")].iloc[0]
    weighted_youth = load("label_reproduction").query("group == 'youth_all'").iloc[0]
    key_metrics = metrics[["model_threshold", "n", "positives", "prevalence", "f1", "precision", "recall", "pr_auc", "roc_auc", "lift_10"]].copy()
    for column in key_metrics.columns[3:]:
        key_metrics[column] = key_metrics[column].map(lambda x: f"{float(x):.3f}")
    group_table = subgroups.loc[(subgroups.threshold.eq("f1")) & subgroups.subgroup.isin(["sex", "area"])][["subgroup", "value", "n", "positives", "precision", "recall"]].copy()
    for column in ["precision", "recall"]:
        group_table[column] = group_table[column].map(lambda x: f"{float(x):.3f}")
    skills_table = education.loc[education.group.eq("overall"), ["category", "n", "positive_n", "estimate", "ci_low", "ci_high"]].copy()
    for column in ["estimate", "ci_low", "ci_high"]:
        skills_table[column] = skills_table[column].map(lambda x: f"{100*float(x):.1f}%")
    strict = pd.concat([load("skills_mismatch"), load("skills_mismatch_sensitivity")])
    strict = strict.loc[strict.group.isin(["overall; norm=all_15_plus", "overall; norm=age_25_44", "overall; norm=youth", "overall; norm=ISCO"]) & strict.category.eq("over"), ["group", "category", "n", "positive_n", "estimate", "ci_low", "ci_high"]]
    variants = mismatch[["group", "category", "n", "positive_n", "estimate", "ci_low", "ci_high"]]
    absorption = load("skills_graduate_absorption").query("group == 'overall'")[["category", "n", "positive_n", "estimate", "ci_low", "ci_high"]]
    training = load("skills_attainment_difference").query("group == 'overall' and category == 'Training ever/current'")
    neet_overall = neet.query("group == 'overall'")
    pbs_neet = load("skills_neet_external")
    figures = [
        ("Class balance in the modelling sample", "../reports/figures/class_balance.png"),
        ("Unemployment by education, with counts", "../reports/figures/rate_by_education_level.png"),
        ("Grouped learning curve", "../reports/figures/grouped_learning_curve.png"),
        ("Validation precision–recall curves", "../reports/figures/validation_pr_curves.png"),
        ("Grouped permutation importance on validation", "../reports/figures/grouped_permutation_importance.png"),
        ("Frozen model precision–recall curve on the test split", "../reports/figures/test_pr_curve_wide.png"),
        ("Test confusion matrix", "../reports/figures/test_confusion_matrix.png"),
        ("Profile explorer desktop screenshot", "screenshots/final/explorer-1440x900.png"),
        ("Skills-gap dashboard desktop screenshot", "screenshots/skills/skills-1440x900.png"),
        ("Model performance dashboard desktop screenshot", "screenshots/final/performance-1440x900.png"),
    ]
    for _, path in figures:
        if not (DOCS / path).exists():
            raise FileNotFoundError(path)
    (DOCS / "report_figures.md").write_text("# Report figure index\n\n" + "\n".join(f"- [{caption}]({path})" for caption, path in figures) + "\n", encoding="utf-8")
    decisions = [
        ("Label", "Published headline concept with audited questionnaire routes; future starters use the available near-future proxy", "Self-declared status or search alone", "Reproduction and routing evidence", "label_definition.md; label_reproduction.csv"),
        ("Population", "Youth in the labour force", "All youth as model targets", "Target is unemployment conditional on labour-force membership", "label_definition.md"),
        ("Predictors", "Explicit demographic, education, household and Census allowlist", "Outcome-related and identifier fields", "Prevent leakage and protect privacy", "../src/hunarlens/config.py"),
        ("Split", "Stratified household groups", "Random individual split", "Avoid related records crossing partitions", "../reports/tables/split_summary.csv"),
        ("Census join", "Province with area where available", "District matching", "Verified geography; no unsupported district linkage", "DECISIONS.md"),
        ("Imbalance", "Compare class weights; choose threshold on validation", "Undersampling dependency", "Avoid added dependency and report operating trade-offs", "../reports/tables/experiments.csv"),
        ("Selection", "HistGradientBoosting within the pre-agreed CV tie band", "Highest-scoring random forest", "Smaller train–CV gap, model size and prediction time; forest led held-out metrics", "../reports/tables/generalization_gap.csv"),
        ("Calibration", "Use raw probabilities", "Sigmoid calibration", "Validation calibration did not clearly improve", "../reports/tables/calibration_validation.csv"),
        ("Threshold", "Validation F1 plateau midpoint and separate screening threshold", "A single noisy F1 peak", "Improve stability and show recall trade-off", "../reports/tables/stage6_thresholds.csv"),
        ("Test policy", "Freeze before one test scoring", "Repeated test-driven selection", "Protect held-out evaluation", "test_findings.md"),
        ("Explanation", "Grouped and individual permutation importance", "Unapproved explanatory dependencies", "Model-agnostic association and correlated-group interpretation", "model_findings.md"),
        ("Interface", "Population context, uncertainty and non-decision wording", "Individual verdict", "Clarify sample and avoid prescriptive use", "../app/prototype.html"),
        ("Skills gap", "Weighted education/training proxies, mode norms and PSU intervals", "Claiming direct skill demand", "Survey records occupations, not vacancies or individual skills", "skills_gap_methods.md"),
    ]
    decision_table = md_table(pd.DataFrame(decisions, columns=["Decision", "Choice", "Alternative", "Why", "Evidence / file"]))
    abstract = (f"HunarLens examines unemployment among youth in the labour force using the Pakistan Labour Force Survey and contextual Census aggregates. "
                f"A frozen histogram gradient boosting pipeline is evaluated against a stratified baseline. On the held-out sample, the primary F1 is {hgb.f1:.3f} "
                f"versus {dummy.f1:.3f} for the baseline; average precision is {hgb.pr_auc:.3f} versus {dummy.pr_auc:.3f}. "
                "A separate weighted skills-gap extension compares education and training as proxies and reports uncertainty. Results are associative, conditional on survey definitions and selection, and unsuitable for individual decisions.")
    full = f"""# HunarLens — submission report draft

**Draft for team review.** Pagination depends on typography, figure placement and appendices; verify the required length after export. Author names, contributions and AI-assistance disclosure are placeholders.

## Abstract

{abstract}

## 1. Problem and motivation

Youth unemployment is a public-policy concern, but the unemployment rate is not the proportion of all young people without a job. It is conditioned on labour-force membership. People outside the labour force, including many students and unpaid carers, are not modelled as unemployed. HunarLens makes this denominator explicit and supports exploration of survey patterns and the performance of an experimental classifier.

The project asks two related but distinct questions. First, how well can permitted characteristics rank unemployment among labour-force youth? Second, how do education and vocational-training proxies vary with employment status and occupations? The second question is descriptive; the labour-force survey does not observe vacancies or direct employer requirements. Combining these questions on one dashboard requires visible separation between survey estimates, model output and official figures.

## 2. Importance and evidence

The [PBS Labour Force Statistics page](https://www.pbs.gov.pk/labour-force-statistics/) supplies the survey, questionnaire, methods and publications. The [ILO derivation guide](https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf) supplies international labour-force definitions. PBS reports unemployment with a specific reference period for search and availability. We reproduce published aggregates before modelling and present divergence where it exists.

Education mismatch can be described by an empirical occupational mode or by a normative occupation-to-education mapping. These answer different questions. The [ILOSTAT methodology](https://ilostat.ilo.org/blog/only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education/) and [ETF guidance](https://www.etf.europa.eu/en/publications-and-resources/publications/skills-mismatch-measurement-etf-partner-countries) explain alternative approaches. The automated ILOSTAT link check returned a non-success status; **VERIFY** browser access and source attribution before submission. NAVTTC/NSIS employer material is contextual, not a measurement of vacancies in this dataset; its link also requires **VERIFY**.

## 3. Solution design

### Architecture

PBS files are downloaded into an ignored raw directory and audited. The build script constructs the approved label, household roster features and regional lookup, and applies an explicit feature allowlist. Household-aware split assignments isolate the training, validation and test partitions. One scikit-learn pipeline performs feature engineering, missing-value handling, encoding and estimation. Validation supports threshold selection and explanations. The frozen artefact and metadata supply the Streamlit interface; tables and plots are precomputed rather than recomputed from test rows in the app.

The skills-gap path is separate. It uses audited survey variables, weights and PSU-cluster resampling for descriptive aggregates. The interface consumes only generated tables. Occupation and labour-force variables are never model predictors. A suitable architecture figure is a left-to-right flow from PBS data and audit to the separate model and skills paths, then to stored artefacts and the dashboard.

### Audiences and use

The dashboard supports students and researchers comparing aggregate patterns. The profile explorer illustrates how the frozen model responds to allowed inputs. It is not a screening service, a measure of personal ability or an employment decision tool. Counts, uncertainty and sample conditions must accompany comparisons; the interface is not evidence of causal effects.

## 4. Design decisions and rationale

{decision_table}

Further detail, including gate approvals and alternatives, is recorded in [DECISIONS.md](DECISIONS.md). The future-starter timing requirement cannot be verified from the available survey fields, so the approved proxy is a documented approximation rather than proof of exact compliance for every case.

## 5. Data collection and preparation

The download manifest records source URLs, retrieval dates, bytes and SHA-256 checksums. [DATA_SOURCES.md](../DATA_SOURCES.md) lists every downloaded item and its status. PBS survey data are household-based; the Census tables supply aggregate regional context. Raw survey files remain outside version control. The approved label uses audited work, absence, job-search and availability fields, including an approved future-starter proxy. Ambiguous absence records are excluded in the recorded waterfall rather than silently discarded.

{md_table(waterfall)}

The published all-age and youth reproduction comparisons are in [label_reproduction.csv](../reports/tables/label_reproduction.csv). The weighted youth unemployment estimate is {weighted_youth.unemployment_rate:.1%}; it is not the same quantity as unweighted model prevalence. Household counts are assembled from roster fields before filtering youth. Only the final allowlist enters the model. Sensitive identifiers, household keys and labour-market outcome variables are not predictors. The census lookup is geographically coarse and adds no within-province variation in this build.

## 6. Exploratory data analysis

The EDA notebook examines class balance, age and household distributions, education and training categories, missingness, and numeric correlation. Group sizes are shown alongside descriptive rates. Plots use the modelling sample without survey weights, so they describe the records used for modelling rather than a population estimate. Patterns involving enrolment, sex and area are associations and can reflect selection into the labour force. Rare categories and missing-value codes are reviewed in the audit tables.

![Unweighted modelling-sample class balance](../reports/figures/class_balance.png)

The chosen engineered fields include an ordered education representation alongside the original category, an age band, a household child share and clipping fitted on training rows. These transformations remain inside the pipeline. Grouped permutation and ablation results are used to interpret related education and geographic fields together, not as independent causal effects.

## 7. Methodology

### Splitting and preprocessing

Households are assigned to a single partition; grouped cross-validation prevents related youth from crossing folds. The modelling dataset uses an allowlist, median imputation and scaling for numeric features, and categorical imputation and unknown-safe one-hot encoding for categorical features. Transformations are fitted on training rows only. The saved partition sizes and prevalence are:

{md_table(splits)}

### Model development

The baseline is a stratified dummy classifier. Logistic regression, random forest and histogram gradient boosting are compared under grouped cross-validation using average precision. Validation is reserved for comparison, threshold selection and calibration review. A pre-agreed simplicity tie band permits the final model to be chosen for generalization gap, file size and prediction speed even when another candidate has a marginally higher CV score. The tuned train, CV and validation average-precision evidence is:

{md_table(comparison)}

Calibration review retained raw probabilities. The primary operating point is selected on validation from a near-optimal F1 range, while the secondary screening point seeks higher recall. Both thresholds were fixed before test scoring. Model-specific explanations use permutation importance on validation; correlated inputs are also permuted as groups. The approach measures how much the model relies on information under the chosen evaluation scheme, not a causal effect.

### Skills-gap estimates

Survey descriptions use weights and PSU-cluster bootstrap intervals; they do not reproduce the full stratified survey design. Occupation modes are recomputed in bootstrap resamples for statistical mismatch estimates. The strict, within-one-band, severe and normative definitions are reported separately. Unstable modes and wide ranges are flagged. Small cells are suppressed according to the approved disclosure rule; structural zeros are distinguished from observed small counts.

## 8. Results

### Final test and baseline

The sealed evaluation reports the following metrics. Values are unweighted and the two model thresholds use the same frozen probabilities. The test predictions are not regenerated for this document.

{md_table(key_metrics)}

The household-bootstrap interval for primary F1 is {f1_ci.lower_95:.3f}–{f1_ci.upper_95:.3f}. It expresses sampling variability under this resampling design, not a guarantee of performance elsewhere. The precision–recall baseline is the test prevalence. The associated curve and confusion matrix are in the [figure index](report_figures.md). See [test_findings.md](test_findings.md) for precision, recall, lift, errors and caveats.

![Frozen-model test precision–recall curve](../reports/figures/test_pr_curve_wide.png)

### Subgroup performance

{md_table(group_table)}

Subgroup results are descriptive. Sample size and the number of positive cases affect stability; some education and geography groups have fewer positive cases than the reliability threshold. Differences do not establish that an attribute caused an outcome. The classifier uses sex and location, so model use and group error rates require explicit fairness review.

![Validation grouped permutation importance](../reports/figures/grouped_permutation_importance.png)

### Skills-gap results

The weighted unemployment comparison below is conditional on labour-force membership and should not be compared directly with unweighted model metrics:

{md_table(skills_table)}

Degree-level labour-force outcomes, weighted shares:

{md_table(absorption)}

Strict above-mode or above-norm shares, with denominator and cell counts:

{md_table(strict)}

Tolerance and severe variants use different definitions and should not be combined into a single range:

{md_table(variants)}

The training comparison below is the unemployed-minus-employed difference in weighted shares:

{md_table(training)}

The approximate not-employed-and-not-enrolled measure and the separate PBS reference are:

{md_table(neet_overall)}

{md_table(pbs_neet)}

Our approximation cannot identify recent training and is not the complete SDG NEET indicator. The occupation-mode estimates depend on the education-band scheme and composition of occupations. The age-specific adult norm happens to produce the same point modes as the all-employed norm, so it is not an independent point-estimate sensitivity. [Skills-gap findings](skills_gap_findings.md) and [sign-off](skills_gap_signoff.md) contain the complete results, counts, bootstrap ranges, sensitivity definitions and caveats.

## 9. Deployment and interface

The application runs as a Streamlit service and reads a frozen model, metadata and tracked aggregate artefacts. It contains overview, skills-gap, profile, performance and methodology views. A native Streamlit fallback is available when the custom component is unavailable. Inputs are transient and are not intentionally stored. Screenshots of the desktop interface and skills page are linked in [report_figures.md](report_figures.md). **VERIFY** the deployed branch, URL and live rendering with the team before submission.

![Profile explorer on desktop](screenshots/final/explorer-1440x900.png)

![Skills-gap dashboard on desktop](screenshots/skills/skills-1440x900.png)

![Model performance dashboard on desktop](screenshots/final/performance-1440x900.png)

## 10. Limitations and future work

The model is conditional on labour-force membership, uses unweighted survey records and is not externally validated. Future-starter timing cannot be verified. Census information is aggregate and geographically coarse. Education and training proxy skills only imperfectly; a worker's qualification does not establish task proficiency. Occupation information exists for employed youth and employer demand is absent. PSU bootstrap intervals ignore stratification; model bootstrap intervals describe a different sampling procedure. Group comparisons may be imprecise or unstable, and repeated development decisions can affect generalization.

Future work includes independent temporal or external validation, an explicit survey-design analysis, fairness assessment with adequate subgroup sizes, independently sourced employer demand, and confirmation of licences and report references. The current artefact is for exploratory aggregate research rather than individual decisions.

## References

- Pakistan Bureau of Statistics. Labour Force Survey, questionnaire, coding scheme, annual report and Census tables. See [DATA_SOURCES.md](../DATA_SOURCES.md) for source URLs, dates and checksums.
- International Labour Organization. Labour-force variable derivation guide. [Guide](https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf).
- ILOSTAT. Educational mismatch methods. [Methodology](https://ilostat.ilo.org/blog/only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education/) — **VERIFY** automated access.
- European Training Foundation. [Skills mismatch measurement](https://www.etf.europa.eu/en/publications-and-resources/publications/skills-mismatch-measurement-etf-partner-countries).
- NAVTTC / NSIS. [Skills information](https://www.skillingpakistan.gov.pk/) — **VERIFY** automated access and survey-year attribution.
- NAVTTC / NSIS. [Skills Trend Analysis](https://tevtreform.jobs.gov.pk/wp-content/uploads/downloads/governance/Skills%20Trend%20Analysis.pdf), n.d. — external context; **VERIFY** publication year and access.

## Individual contributions — placeholders

| Team member | Contribution | Evidence / review |
|---|---|---|
| [NAME — COMPLETE] | [COMPLETE] | [COMPLETE] |
| [NAME — COMPLETE] | [COMPLETE] | [COMPLETE] |
| [NAME — COMPLETE] | [COMPLETE] | [COMPLETE] |

## Appendix A. Tables and uncertainty

Full aggregate CSVs are under `reports/tables/`; the [skills sign-off](skills_gap_signoff.md), [test findings](test_findings.md), and [source catalogue](../DATA_SOURCES.md) link the tables to definitions. The source workbook and raw microdata are not included. The figures list identifies the approved report images.

### Unemployment by education and available sex and area groups

{md_table(education)}

### Mismatch by occupation and reference norm

{md_table(load('skills_mismatch_by_occupation'))}

### Test subgroup table

{md_table(subgroups)}

## Appendix B. Frozen hyperparameters

```json
{json.dumps(params['model_parameters'], indent=2)}
```

The saved thresholds and versions are in [metadata.json](../models/metadata.json). The trained artefact is not regenerated to write this report.

## Appendix C. Test inventory

The `tests/` directory covers data and label reproduction, grouping, pipeline leakage, experiments, freeze, explainability, sealed test artefacts, application parity, the skills audit, disclosure, bootstrap and dashboard. Run `python -m pytest -q` for the default suite and `python -m pytest -q -m full_data` for full-data checks when the ignored local data are available. Tests are not evidence of future live-service performance.
"""
    short = f"""# HunarLens — short report draft

**Draft:** target four pages excluding the decision appendix; verify pagination after formatting. Contributions and AI disclosure remain team placeholders.

## Abstract

{abstract}

## Problem and importance

The project studies survey patterns for unemployed youth within the labour force, not all youth without employment. PBS provides the household survey and contextual Census tables; the ILO provides labour-force definitions. Education and training are skills proxies and the survey does not measure vacancies. Results are associations and must not be used to make decisions about individuals. [Sources and terms](../DATA_SOURCES.md).

## Design and data

Audited survey routes define employment and unemployment; future-starter timing is not verifiable. The model uses a demographic, education, roster and coarse regional allowlist. Household groups keep related records together. A single training-fitted scikit-learn pipeline handles missing values, encoding and model estimation. The skills path instead uses survey weights and PSU-cluster bootstrap intervals, with statistical and normative occupation comparisons kept separate. Raw microdata and person-level files are excluded from the submission.

## Method and results

Grouped cross-validation selects model candidates; validation determines operating thresholds and calibration. The final pipeline and thresholds were frozen before the one-time test evaluation. Results on the unweighted test partition are:

{md_table(key_metrics)}

Primary F1 has a household-bootstrap interval of {f1_ci.lower_95:.3f}–{f1_ci.upper_95:.3f}. The weighted youth unemployment estimate is {weighted_youth.unemployment_rate:.1%}; this is a different denominator and weighting scheme from the model test prevalence. Education-group unemployment comparisons appear below:

{md_table(skills_table)}

Patterns vary across subgroups and can reflect labour-force selection; some subgroup results are unreliable. Occupation modes can change across bootstrap samples. The approximate NEET calculation omits recent-training information. Full findings, intervals, comparison tables and definitions are in [test_findings.md](test_findings.md) and [skills_gap_signoff.md](skills_gap_signoff.md).

## Deployment, limitations and future work

The Streamlit dashboard reads tracked aggregates and the frozen model, with a native fallback. Its profile tool is exploratory, not a decision tool. Model training and test evaluation are unweighted; the PSU bootstrap does not capture the complete design; Census features are geographically coarse; and the model has not been independently validated. Future work should examine external validity, subgroup fairness and independently measured employer demand. See the [figure index](report_figures.md) for screenshots and results.

## References and contributions

PBS, ILO, ILOSTAT, ETF and NAVTTC/NSIS sources and access flags are listed in [DATA_SOURCES.md](../DATA_SOURCES.md). ILOSTAT and NSIS automated access require **VERIFY**. Team members, individual contributions and the AI-assistance statement: **[COMPLETE]**.

## Appendix: decision log

{decision_table}
"""
    (DOCS / "report_draft.md").write_text(full, encoding="utf-8")
    (DOCS / "report_short.md").write_text(short, encoding="utf-8")
    print("Generated report drafts and figure index from saved aggregate tables.")


if __name__ == "__main__":
    main()
