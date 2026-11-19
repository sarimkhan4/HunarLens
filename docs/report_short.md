# HunarLens — short report draft

**Draft:** target four pages excluding the decision appendix; verify pagination after formatting. Contributions and AI disclosure remain team placeholders.

## Abstract

HunarLens examines unemployment among youth in the labour force using the Pakistan Labour Force Survey and contextual Census aggregates. A frozen histogram gradient boosting pipeline is evaluated against a stratified baseline. On the held-out sample, the primary F1 is 0.360 versus 0.123 for the baseline; average precision is 0.303 versus 0.127. A separate weighted skills-gap extension compares education and training as proxies and reports uncertainty. Results are associative, conditional on survey definitions and selection, and unsuitable for individual decisions.

## Problem and importance

The project studies survey patterns for unemployed youth within the labour force, not all youth without employment. PBS provides the household survey and contextual Census tables; the ILO provides labour-force definitions. Education and training are skills proxies and the survey does not measure vacancies. Results are associations and must not be used to make decisions about individuals. [Sources and terms](../DATA_SOURCES.md).

## Design and data

Audited survey routes define employment and unemployment; future-starter timing is not verifiable. The model uses a demographic, education, roster and coarse regional allowlist. Household groups keep related records together. A single training-fitted scikit-learn pipeline handles missing values, encoding and model estimation. The skills path instead uses survey weights and PSU-cluster bootstrap intervals, with statistical and normative occupation comparisons kept separate. Raw microdata and person-level files are excluded from the submission.

## Method and results

Grouped cross-validation selects model candidates; validation determines operating thresholds and calibration. The final pipeline and thresholds were frozen before the one-time test evaluation. Results on the unweighted test partition are:

| model_threshold | n | positives | prevalence | f1 | precision | recall | pr_auc | roc_auc | lift_10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HGB F1 | 3999 | 508 | 0.127 | 0.360 | 0.273 | 0.530 | 0.303 | 0.752 | 2.814 |
| HGB screening | 3999 | 508 | 0.127 | 0.354 | 0.247 | 0.628 | 0.303 | 0.752 | 2.814 |
| Stratified Dummy | 3999 | 508 | 0.127 | 0.123 | 0.125 | 0.122 | 0.127 | 0.499 | 0.866 |

Primary F1 has a household-bootstrap interval of 0.328–0.393. The weighted youth unemployment estimate is 12.8%; this is a different denominator and weighting scheme from the model test prevalence. Education-group unemployment comparisons appear below:

| category | n | positive_n | estimate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- |
| No formal | 7094 | 617 | 8.2% | 7.3% | 9.0% |
| Below matric | 9629 | 1080 | 11.4% | 10.6% | 12.2% |
| Matric | 4574 | 679 | 14.8% | 13.7% | 16.0% |
| Intermediate | 3849 | 664 | 17.5% | 16.1% | 19.1% |
| Degree or above | 1507 | 343 | 22.6% | 20.3% | 25.0% |

Patterns vary across subgroups and can reflect labour-force selection; some subgroup results are unreliable. Occupation modes can change across bootstrap samples. The approximate NEET calculation omits recent-training information. Full findings, intervals, comparison tables and definitions are in [test_findings.md](test_findings.md) and [skills_gap_signoff.md](skills_gap_signoff.md).

## Deployment, limitations and future work

The Streamlit dashboard reads tracked aggregates and the frozen model, with a native fallback. Its profile tool is exploratory, not a decision tool. Model training and test evaluation are unweighted; the PSU bootstrap does not capture the complete design; Census features are geographically coarse; and the model has not been independently validated. Future work should examine external validity, subgroup fairness and independently measured employer demand. See the [figure index](report_figures.md) for screenshots and results.

## References and contributions

PBS, ILO, ILOSTAT, ETF and NAVTTC/NSIS sources and access flags are listed in [DATA_SOURCES.md](../DATA_SOURCES.md). ILOSTAT and NSIS automated access require **VERIFY**. Team members, individual contributions and the AI-assistance statement: **[COMPLETE]**.

## Appendix: decision log

| Decision | Choice | Alternative | Why | Evidence / file |
| --- | --- | --- | --- | --- |
| Label | Published headline concept with audited questionnaire routes; future starters use the available near-future proxy | Self-declared status or search alone | Reproduction and routing evidence | label_definition.md; label_reproduction.csv |
| Population | Youth in the labour force | All youth as model targets | Target is unemployment conditional on labour-force membership | label_definition.md |
| Predictors | Explicit demographic, education, household and Census allowlist | Outcome-related and identifier fields | Prevent leakage and protect privacy | ../src/hunarlens/config.py |
| Split | Stratified household groups | Random individual split | Avoid related records crossing partitions | ../reports/tables/split_summary.csv |
| Census join | Province with area where available | District matching | Verified geography; no unsupported district linkage | DECISIONS.md |
| Imbalance | Compare class weights; choose threshold on validation | Undersampling dependency | Avoid added dependency and report operating trade-offs | ../reports/tables/experiments.csv |
| Selection | HistGradientBoosting within the pre-agreed CV tie band | Highest-scoring random forest | Smaller train–CV gap, model size and prediction time; forest led held-out metrics | ../reports/tables/generalization_gap.csv |
| Calibration | Use raw probabilities | Sigmoid calibration | Validation calibration did not clearly improve | ../reports/tables/calibration_validation.csv |
| Threshold | Validation F1 plateau midpoint and separate screening threshold | A single noisy F1 peak | Improve stability and show recall trade-off | ../reports/tables/stage6_thresholds.csv |
| Test policy | Freeze before one test scoring | Repeated test-driven selection | Protect held-out evaluation | test_findings.md |
| Explanation | Grouped and individual permutation importance | Unapproved explanatory dependencies | Model-agnostic association and correlated-group interpretation | model_findings.md |
| Interface | Population context, uncertainty and non-decision wording | Individual verdict | Clarify sample and avoid prescriptive use | ../app/prototype.html |
| Skills gap | Weighted education/training proxies, mode norms and PSU intervals | Claiming direct skill demand | Survey records occupations, not vacancies or individual skills | skills_gap_methods.md |
