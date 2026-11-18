# Decisions

## 2026-11-15 — Stage 0 skeleton

- Leave the feature lists empty until the team approves them after the data audit. This avoids guessing predictors before inspecting the real data.
- Keep raw and interim data out of Git because microdata redistribution and privacy must be checked first.
- The initial dependency files were partial because installation had not completed. This was superseded by the version and dependency decision below.

## 2026-11-15 — Python 3.12 and installed dependency pins

- The team chose Python 3.12 instead of 3.11 to match the available project environment. Use Python 3.12 locally and for Streamlit deployment.
- Pin the six direct runtime libraries and the two development tools to the versions installed in `.venv`. This keeps development tools out of the runtime requirements while recording the tested direct dependencies.

## 2026-11-15 — Stage 1 acquisition and preliminary audit

- Add `openpyxl` with human approval because pandas needs it to read the official Census Excel files.
- Keep the feature allowlist, label and household-grouping rule unapproved. Source labels alone do not establish the PBS headline classification or a reliable current-district join.
- Retain the raw extract under ignored `data/raw/`: its schema includes a name-labelled field and survey identifiers, and file-specific redistribution terms are unresolved.

## 2026-11-15 — Gate G1 approval and Stage 2 pause

- The team approved the proposed label, features, grouping and geographic approach subject to weighted reproduction. No implementation was authorized to override a contradiction in source documentation.
- Stage 2 was paused before constructing labels because `S5C5` numeric value labels conflict between the questionnaire and the downloaded Stata file. Resolve the correct coding with the PBS documentation or PBS before implementing the absence rules.
- Exclude `S4C11`: its question's response labels explicitly mention training during and before a job. `S4C12` remains unapproved pending verification of its codes and leakage risk.

## 2026-11-15 — Absence-code fallback and reproduction check

- The team instructed an empirical comparison and a 67-record exclusion if inconclusive. Questionnaire 5.5 has 15 options; Stata labels 1–13 are shifted one option relative to the questionnaire, while Stata code 15 matches option 15 and 14 is unlabelled. The sex check cannot validate either mapping: Stata maternity code 4 has three male and one female, and questionnaire maternity code 5 has no records. Exclude codes 1 and 14 for `S5C4=1`, as instructed, without assuming the remaining mapping is proven.
- A provisional 10+ weighted calculation failed the pre-agreed 2% unemployed-count tolerance: 5,779,758 versus 5,900,000 (2.038% below). The population estimates and grouped route diagnostics are generated in `reports/tables/`; no youth dataset was created. Inspect PBS's coding and routing and confirm how rounding and future starters affect the published totals before selecting a label.
- The user superseded the earlier `S4C11` exclusion by authorizing an ever/current versus never collapse if supported by the question. The question supports that wording, but no feature was implemented while the label gate is open. `S4C12` has no attached Stata value labels; inspect Annex C before approving its categories.
- The requested raw grouping diagnostic found 53,974 `PCode` + `EBCode` + `HHNo` groups, mean 6.03 records and maximum 54. Since the maximum exceeds 30, the instructed fallback is `PCode` + `EBCode`; this produces 3,759 groups with mean 86.58 and maximum 189. Neither grouping has been used to build a dataset. The large fallback groups are a limitation to inspect when splitting.

## 2026-11-15 — Revised Stage 2 decisions and gate

- The team chose the questionnaire coding for `S5C5`, treating the Stata labels as misaligned; code 1's median age is 21 and code 2's is 51. This age pattern supports their decision but is not proof of the source coding. Exclude code 14 and missing `S5C5` among `S5C4=1`; the user clarified that `S4C4` was a typo. The prior 67-record exclusion is superseded.
- The team retained `PCode + EBCode + HHNo` without quarter, replacing the prior fallback decision despite the observed maximum of 54 records. No group ID has been built yet.
- The report's definition requires active job search, availability and no work; no explicit future-starter exception was found. Do not add people who did not search without PBS support. The team authorized collapsing `S4C11` to ever/current versus never and excluding `S4C12` if its codes cannot be verified; neither has been implemented while reproduction fails.
- The revised provisional check returned 5,800,161 unemployed and 6.985%, below the required 5.85–5.95 million and 7.05–7.15%. The label gate remains open; do not adjust the label merely to hit the published numbers.

## 2026-11-15 — Future starters and Stage 2 dataset

- The team approved inclusion of available non-searchers with `S9C5=1`, subject to documentation. The ILO 19th ICLS guide explicitly includes qualifying future starters. PBS records a job starting in the near future but no verified start date, so the ILO's generally three-month limit cannot be checked; this is an approximation. The reproduced PBS totals corroborate the rule but do not prove that all records meet the limit.
- Use the team-approved `PCode + EBCode + HHNo` as an integer group, calculated on the full roster before youth filtering. No crosswalk is exported. The 54-record maximum and potential reuse of identifiers remain limitations for grouped splits.
- Use Census province-level density and urban proportion, because those cells are blank in the rural/urban rows; use area-specific average household size. The fixed lookup therefore joins on province and area, with eight matching combinations.
- Keep Census density in its original unit in the analysis dataset; the requested log transformation belongs in the single fitted scikit-learn pipeline in Stage 4, avoiding feature engineering outside the pipeline. Use only numeric codes for survey categories; invalid codes are mapped to missing and no undocumented value is interpreted as a missing code.
- Exclude `S4C12`: training type lacks Stata value labels and the available PBS sampling coding scheme has no verified training-category annex. Convert `S4C11` categories 1–3 to yes and 4 to no, dropping job timing.
- Do not remove identical feature rows as duplicates: the verified household-plus-person keys are unique, and two different people can legitimately share all model features. Abort rather than silently dropping a duplicated source person key.

## 2026-11-15 — Gate G2 and Stage 3 audit

- The team approved Gate G2. The Stage 2 value audit found no retained 97, 98 or 99 codes, and no documented missing code requiring conversion; existing valid-code checks convert unexpected categorical codes to missing. Education code 1 means no formal education and enrolment code 1 means currently not enrolled; both are meaningful responses, not missing. `has_training=0` means not received or receiving training, not a missing category. Training type is excluded.
- `census_density` and `census_urban_proportion` are constant within province and add no information beyond province. `census_household_size` varies by area within every province, so it is constant within province × area, not province alone; it adds no information beyond that joint key. Stage 5 must include a comparison with and without all Census features. Stage 7 must permute province, area and all Census features together, preserving valid province × area combinations; interpret this as joint importance for the entire geographic group.
- Treat `can_read`, `can_write`, and `education_level` as a correlated group when interpreting later importance results. Their relationship can dilute the apparent contribution of any one variable.

## 2026-11-15 — Gate G3 and Stage 4 preprocessing

- The team approved five engineered outputs: the numeric education code alongside categorical education, age bands 15–17/18–20/21–24, children under 15 divided by household size, household size clipped at the training-fold 99th percentile, and a categorical sex × area interaction. No Census density log or other engineered output is added. The clipped size replaces the original size in the numeric branch.
- The EDA shows a substantial area difference for females (24.5% urban versus 11.1% rural), compared with 14.1% versus 11.8% for males, so the interaction was selected. These descriptive rates are not causal evidence.
- The education codes include distinct degree subjects and do not form an unquestionable progression; using the raw code as ordinal is an approved modelling assumption, and the categorical representation is retained. No code or category is learned from validation or test rows.
- Use the approved 20-fold household-grouped split, persist a dataset hash with row assignments, and derive the five-fold scan on training rows only. Thresholds, calibration, model selection and test metrics are deferred.

## 2026-11-15 — Stage 5 experiment protocol

- The team approved dropping E5 undersampling; class weighting and validation threshold tuning are tested instead, avoiding a new dependency.
- Reduce the Random Forest randomized search from 25 to 15 iterations. The default 100-tree forest required approximately 15 seconds for grouped CV and refit on this machine, so the original 25 iterations at 200–400 trees were projected to take many minutes; the user authorized a reduction to 15 when runtime is too long.
- Reduce the HistGradientBoosting search from 30 to 15 iterations as well. Its default 100-iteration grouped CV and refit took approximately 11 seconds, and each planned candidate uses 200 or 400 iterations; the full search would substantially extend runtime.
- The Stage 5 CV rule nominates Random Forest: mean grouped CV average precision is 0.3076, versus 0.2977 for HistGradientBoosting and 0.2811 for Logistic Regression. The forest is also the simpler of the two models within 0.01 of the best score. This is a candidate for Gate G5, not a final model choice or freeze.
- Tuned forest train/CV/validation average precision is 0.4732/0.3076/0.3277, indicating a substantial training-to-held-out gap. Threshold-optimized validation F1 is optimistic because the same validation labels select and assess the threshold; final evaluation remains untouched.
- Grouped CV forest ablation scores are 0.3009 for individual features, 0.3061 with household features, and 0.3076 with all features. The requested full-without-Census and individual-plus-household comparisons are identical feature sets and both score 0.3061; the small difference is not evidence of a causal Census effect.

## 2026-11-15 — Gate G5 and Stage 6

- The team approved HistGradientBoosting with the E3 parameters and no class weight as the final model. Random Forest scored highest on every held-out metric but its 0.0099 CV average-precision advantage was inside the 0.01 tie band. The team selected HGB for its smaller train-to-CV gap (0.1037 versus 0.1655), much smaller file and faster predictions.
- Gate G6 approved the raw-probability HGB freeze under the pre-agreed tie-break: RF was marginally ahead on every held-out metric, but RF minus HGB CV average precision was 0.0099, below 0.01. HGB was selected for its smaller train–CV gap, file size and prediction time. The approved F1 and screening thresholds are 0.182931 and 0.154107; high and elevated band cut-offs are 0.268655 and 0.158568 (displayed rounded values; metadata retains the full calculated precision).
- Paired CV differences use identical grouped folds; their population standard deviations describe fold variation, not independent uncertainty estimates. The HGB individual/household/Census ablation uses the same folds and tuned parameters. Force dense preprocessing for HGB ablation because dropping columns can otherwise produce a sparse matrix unsupported by HGB.
- Compare sigmoid and raw scores on validation; retain sigmoid only if its validation Brier score improves by at least 2% relative and its fixed-bin calibration error decreases. Raw Brier is 0.100341 versus sigmoid 0.100335, so retain raw. Sigmoid was fitted and evaluated on the same validation labels, so this comparison is optimistic and does not establish external calibration.
- Choose the F1 threshold as the midpoint of all thresholds within 0.005 of maximum validation F1. The qualifying endpoints are 0.175638 and 0.190225; their midpoint is 0.182931. Because F1 is discontinuous and the qualifying set need not be contiguous, the midpoint's F1 (0.353569) is slightly more than 0.005 below the maximum (0.358974). The screening threshold is the highest validation threshold reaching recall 0.60. Both validation results are optimistic because the same labels select and assess them.
- Risk bands use the validation 90th and 70th probability percentiles; ties at cutoffs may change exact band proportions. The chosen pipeline remains trained on train only. Test observations remain sealed. Do not create the frozen-v1 tag until the team's approval.

## 2026-11-15 — Gate G6 and Stage 7

- Gate G6 approved the freeze. The `frozen-v1` tag points to the approved HGB model commit; Stage 7 adds training-derived reference values to metadata without refitting or changing the frozen model.
- The team accepted Stage 7. The SHA-256 of `models/final_pipeline.joblib` is `6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3`; the working file matches the binary retrieved directly from `frozen-v1` byte for byte. The tag remains unchanged.
- On the same five grouped training folds and HGB hyperparameters, removing `currently_enrolled` lowers mean CV average precision from 0.297705 to 0.250015 (difference -0.047690). The frozen estimator and feature list are unchanged.
- Add Geography (province, area, and all three Census features) and Sex as separate joint-permutation groups. Keep the earlier Region and Sex and area rows for reference; display the geographically consistent grouping in the chart.
- Use 20 validation permutations through the complete pipeline, individually and in the requested groups. Education and enrolment lead. Their source fields S4C9 and S4C10 are approved roster inputs and are not used in the Section 5/9 label; no direct label input was found in this review.
- The requested Region group excludes area because area is grouped with sex. As Census household size varies by province × area, these separate permutations can create inconsistent geographic combinations. Interpret the resulting sensitivities cautiously; the prior province + area + Census grouped-importance recommendation remains relevant for a future supplementary analysis.

## Stage 8 — first test opening

- Test split first opened at 2026-11-15T17:52:25+05:00; frozen model SHA-256 `6778affc93d96a6d38044c406e7829f2827addbc0b75bdcafcd4106ff4cf35f3`. The opening is recorded before parsing test rows; the saved predictions are the sole source for later test analyses.

## 2026-11-15 — Stage 9 app

- The app passes validated raw inputs to the frozen pipeline and looks up Census indicators by province and area; it does not fit, alter or replace the model. All UI category choices and ranges come from training metadata, with questionnaire labels for display.
- The roster defines other youth as household members aged 15–24 excluding the subject. Household size must include the subject, children under 15 and other youth. A subject who is the household head supplies the head's sex and education directly; reading and writing answers must be consistent.
- Move `openpyxl` to development dependencies: the data-building scripts need it, but the app consumes the committed Census CSV. Runtime requirements retain only the six libraries needed by the app.
- The grouped importance chart uses the geographically consistent group and the local what-if chart shows changes in model predictions only. Model inputs are not intentionally saved or logged by application code. Deployment is deferred for team approval.

## 2026-11-15 — App audit follow-up

- Metadata stores category codes and encoder values, but not questionnaire labels or numeric input dtypes. The form continues to use the verified questionnaire label mapping. The input builder resolves supplied categorical codes to the exact typed metadata values and uses the training-verified numeric dtypes; unknown categories are rejected. This preserves the model's existing float-string sex × area interaction rather than changing it.
- A non-blocking warning flags an unmarried son/daughter paired with any other marital status. A separate warning uses a training-only file containing boolean flags for age-band × enrolment and age × education combinations with fewer than 20 records. No per-combination counts or personal rows are stored in the flag file; the metadata and frozen estimator are unchanged.

## 2026-11-15 — App audit accepted

- Describe enrolment results as associations in the labour-force sample; selection and the availability/search rules are hypotheses, not established explanations. The enrolment tooltip, the unweighted test summary and the privacy and non-affiliation statements provide context without changing prediction behavior.
- Report validation calibration for enrolment × sex × area only when a cell has at least 30 records. Flag an absolute mean-prediction versus observed-rate gap over 0.05. These descriptive cells do not establish individual calibration and do not replace the frozen test evaluation.

## 2026-11-15 — Stage 9b interface

- Replace the submit form with live widget updates and a named Streamlit result fragment. Widget state is session-scoped; application code does not persist or log user-entered values. Validation and prediction continue through the existing functions and unchanged frozen pipeline.
- Generate the risk ruler from 101 aggregate validation-score quantiles; the saved metadata continues to define the bands and thresholds. The ruler is a relative position among validation youth in the labour force, not a population percentile or an individual diagnosis.
- Pin the already-installed Altair version for the interactive charts. Keep the Streamlit default font: no Atkinson Hyperlegible font file is included. Configure pytest to discover only the project's `tests` directory, so ignored local clone checks are not collected as duplicate tests.
# 2026-11-16 — Prototype-inspired Streamlit dashboard

The dashboard adopts the supplied HTML prototype's navigation and visual direction while using the saved PBS reproduction and held-out evaluation tables, and the existing frozen model and input-validation path. The HTML's illustrative scoring formula is not used. Survey rates are labelled weighted; model results are labelled unweighted. Profile inputs are not saved, including for the prototype's optional profile-comparison feature. The download contains aggregate survey indicators only.

Input changes rerun the page so that the full form remains available after repeated edits. The model, thresholds and validation rules are unchanged.

The next layout revision follows the supplied prototype's two-card profile explorer, 100-square result visual, paired dashboard panels and data-source/definition cards. Existing approved model inputs and explanatory content remain available; all result visuals derive from the frozen pipeline and saved reports.

## 2026-11-16 — Original prototype integration

Use the supplied HTML and CSS in a Streamlit custom component to reproduce its layout, instead of approximating it with native widgets. The prototype's illustrative JavaScript scoring formula is removed. Component selections are transient session state and are validated by the existing Python input builder before the unchanged frozen pipeline is called. Saved survey and evaluation tables supply dashboard results. The prior native interface remains accessible with `?classic=1` and its existing AppTests continue to run against that route.

## 2026-11-18 — Dashboard verification and accessibility

The overview uses weighted estimates from the approved label and only displays PBS values whose difference is at most 0.3 percentage points. The verified Table 15 excerpt records the source used for age-group comparisons. Results and uncertainty on the model page come from saved evaluation tables. User selections remain transient; client-side comparison retains only the previous model score until cleared or the session ends. Public aggregate reference files are cached, while user selections and profile results are never cached or logged.
