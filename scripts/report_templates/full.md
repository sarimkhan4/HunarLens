# HunarLens: Youth Unemployment Vulnerability and Skills-Gap Analysis in Pakistan

**Course:** CT-378 Machine Learning  
**Group:** AlphaDevs  
**Members:** Sarim Khan (CT-24266); Muhammad Saraib (CT-24255); Danish Meraj (CT-24268)  
**Submission date:** [TEAM TO COMPLETE]  
**Instructor:** [TEAM TO COMPLETE]

\newpage

## Abstract

HunarLens examines youth unemployment in Pakistan through complementary prediction and survey-analysis tools. The modelling sample contains {{sample_n}} labour-force youth, of whom {{sample_prevalence}} are unemployed, drawn from the Pakistan Bureau of Statistics Labour Force Survey and linked to Census context. Household-grouped cross-validation compares demographic and education-based classifiers while keeping outcome information outside the predictor allowlist. The frozen histogram gradient boosting model achieves test F1 {{test_f1}}, average precision {{test_pr_auc}} and ROC-AUC {{test_roc_auc}}, compared with stratified-baseline F1 {{dummy_f1}} and average precision {{dummy_pr_auc}}. Its primary F1 interval is {{f1_lower_95}}–{{f1_upper_95}} under household bootstrap resampling. A separate weighted analysis finds unemployment of {{lowedu_estimate}} among youth without formal education and {{degree_estimate}} among those with a degree or above. Education mismatch varies substantially with its definition and occupational reference population. A Streamlit dashboard presents aggregate patterns, uncertainty, model performance and illustrative profiles. These associations are conditional on labour-force membership; they neither measure individual skills nor establish educational or training effects. The tool supports research interpretation and is unsuitable for individual employment decisions.

## 1. Problem and motivation

### 1.1 Questions and intended users

The project asks how well permitted personal and household characteristics distinguish unemployed from employed youth, and how education and training relate to labour-market outcomes and occupational placement. These questions share a survey source but require different analytical designs. Prediction evaluates whether patterns generalise to held-out households. Survey analysis describes weighted population patterns with uncertainty. Neither question asks whether education, sex, place of residence or training determines a person's future.

The intended users are students, researchers and readers of labour-market statistics who need an accessible account of the evidence. A user may want to compare unemployment across education groups, understand where graduates work, or see which information an experimental model uses. HunarLens therefore combines a reproducible analytical workflow with an interface that explains denominators and limitations beside the results. Its contribution is a transparent connection between data preparation, evaluation and interpretation, rather than an unusually high predictive score.

### 1.2 The denominator matters

Unemployment is measured among people in the labour force. A young person without paid work is not automatically unemployed under the survey definition: search, availability and recognised exceptions matter. Many students, carers and other people outside the labour force are outside the classifier's target population. Treating them as unemployed would change the question, inflate the outcome pool and give apparently useful predictions of school attendance or inactivity instead of the intended outcome.

This distinction also affects how readers interpret education. People with different qualifications enter the observed labour-force sample in different proportions and circumstances. A comparison within this sample is not a comparison of all young Pakistanis. The interface therefore describes probabilities as conditional survey associations. The broader approximate NEET analysis uses all youth and explicitly changes the denominator. Comparing these indicators without noting that change would obscure rather than clarify youth disadvantage.

### 1.3 Operational skills-gap definition

> {{definition}}

This definition limits what the project claims. Attainment, occupational placement and employment status are observable proxies. Practical competence, job quality, employer recruitment requirements and unfilled vacancies are not directly measured. The educational mode of an occupation describes existing workers; it does not establish what every job requires. The report consequently uses separate statistical and normative definitions and presents their disagreement as substantive information about measurement.

## 2. Importance

PBS reports youth unemployment of {{youth_all_pbs_unemployment_rate}}, compared with the headline national rate of {{all_ages_pbs_unemployment_rate}}. The published youth rates are {{youth_male_pbs_unemployment_rate}} for males and {{youth_female_pbs_unemployment_rate}} for females, and {{youth_rural_pbs_unemployment_rate}} in rural areas compared with {{youth_urban_pbs_unemployment_rate}} in urban areas (PBS, n.d.-a). These are weighted official statistics, not the classifier's unweighted prevalence. Their differences motivate subgroup analysis while leaving open which mechanisms, institutions or selection processes underlie them.

Our weighted youth estimates show unemployment increasing from {{lowedu_estimate}} among people without formal education to {{degree_estimate}} among those with a degree or above. Among women with a degree or above it is {{degree_female}}. These results are calculated from the audited microdata and appear in the education table; they are not presented as verbatim PBS youth education estimates. Education can coexist with employment difficulties, but these cross-sectional comparisons cannot establish the effect of acquiring a qualification.

PBS's national youth NEET reference is {{neet_pbs}}, whereas our not-employed-and-not-enrolled approximation is {{neet_estimate}}. The former comes from the Annual Report's NEET table; the latter cannot account adequately for recent training. Their proximity is useful context, not evidence that the definitions are interchangeable. A person undertaking training may meet our approximation while being outside a properly measured NEET population. The distinction remains visible wherever the figures appear.

International guidance also distinguishes qualification mismatch from directly measured skill mismatch (ILO, 2021; ETF, 2019). This supports a restrained use of survey education and occupation fields. NAVTTC and NSIS materials provide employer-side context, but their scope and reference periods differ from the household survey. HunarLens does not splice demand estimates from these sources into its survey tables. Such a combination would require an explicit design for geography, timing, occupation definitions and sampling differences.

A screening-style display can help readers explore concentration of survey outcomes or understand a threshold trade-off. It must not become a personal decision service. The observed precision means many flagged people are employed, and the recall means many unemployed people are missed. Using such a flag for admission, recruitment, benefit allocation or exclusion would go beyond both the evidence and the project's purpose. Aggregate planning questions require additional institutional and demand-side evidence, not a direct conversion of model ranks into individual recommendations.

## 3. Solution design

### 3.1 Separate analytical paths

The architecture separates prediction from weighted survey analysis after a shared acquisition and audit process. Official files are downloaded, documented and inspected against questionnaires and coding information. The modelling path builds labels and allowed predictors, assigns households to partitions, compares training-fitted pipelines and freezes the selected model. The survey path uses additional labour-market variables to construct weighted attainment and occupational summaries. These descriptive fields never enter the classifier.

![Figure 1. Architecture with distinct modelling and weighted survey-analysis paths.](../reports/figures/report_architecture.png)

Figure 1 shows how both paths reach the dashboard through stored artefacts. The app loads the frozen pipeline and metadata for profile predictions, while the survey and performance pages read tracked aggregate tables. The presentation layer does not refit the model or perform a fresh test evaluation. This design makes the app small enough for straightforward deployment and keeps expensive research computations separate from interactive use.

The separation also makes evidence easier to audit. A chart about education mismatch can be traced to its survey table and bootstrap method; a probability can be traced to the saved preprocessing pipeline and model. A display correction should not change either analytical result. Keeping tables, presentation and inference distinct therefore supports reproducibility and gives the team a clear explanation of which component is responsible when an output looks unexpected.

### 3.2 Dashboard design and user needs

The Overview page introduces the population and official context. Skills gap supports comparisons of education outcomes, occupational placement and approximate NEET. Profile explorer illustrates the frozen model for a coherent set of allowed inputs. Model performance shows the baseline, uncertainty and subgroup errors. Data and methodology explains definitions, sources and responsible use. The navigation follows the questions a reader is likely to ask rather than exposing the order in which the code was written.

The profile display pairs the probability with the training base rate, a frequency description and a grid representing a hundred comparable observations. These representations offer alternatives to an isolated decimal. They remain illustrations of the same estimate, not additional observations or a promise about a particular person. The ruler's percentile is relative to validation scores, whereas the displayed probability describes the model's estimate; these are different quantities and need different labels.

Input controls use readable survey labels, grouped personal, education, location and household fields, and explanatory help text. Invalid household relationships or incompatible literacy answers block an estimate. Plausible but rare combinations produce a warning. Reference profiles and an input explorer reduce the effort needed to understand the interface, while explicit messages make clear when a hypothetical comparison may be poorly supported by the sample.

Accessibility includes labelled controls, visible focus, readable contrast, text alongside colours and a native Streamlit fallback. The design is informed by WCAG guidance (W3C, 2024), but the project does not claim formal conformance certification. The application does not persist or log profile inputs. Statistical counts shown elsewhere are aggregate evidence from the source survey, not records of visitors' use.

## 4. Design decisions and reasons

Table 1 summarises the main choices. The following subsections explain their consequences for validity and interpretation.

**Table 1. Decisions, alternatives and supporting evidence.**

{{decisions}}

### 4.1 Label definition and future starters

The label follows the approved employment and unemployment derivation rather than a single reported-status field. Paid or profit-oriented work and qualifying family work count as employment; own-use-only agricultural production does not. Temporary absence requires the audited return-to-work or continued-income routes. Unemployment normally requires no employment, recent search and current availability. This avoids treating every person without observed work as unemployed (PBS, n.d.-a, n.d.-b).

The future-starter exception includes available people who did not search because a job or business was arranged to begin soon. ILO guidance recognises such an exception but limits it to a short subsequent period, generally no more than three months (ILO, 2013, 2019). The survey does not supply a verified start date. The implementation therefore uses the questionnaire's near-future response as an approximation and states that timing compliance cannot be established for each person.

The future-starter diagnostic records {{future_records}} additional observations with weighted count {{future_weighted_count}}. People waiting to start a new job are not classified as already employed. Among {{waiting_records}} such absence responses, weighted {{waiting_weighted_count}}, the approved unemployment routes classify {{waiting_unemployed_records}} as unemployed, weighted {{waiting_unemployed_weighted_count}}. These counts document the consequence of the rule; the rule was justified from the definition before numerical agreement was considered.

### 4.2 Questionnaire and file-label disagreement

The absence-reason variable S5C5 contains a disagreement between questionnaire categories and attached Stata labels. Several labels appear shifted, and an observed category lacks a reliable label. Blindly trusting the file would misinterpret waiting to start a new job as a reason for absence from an existing job. That would affect both employment status and the unemployment denominator.

The audit compared the category lists and inspected age and sex distributions among temporarily absent workers. The suspected maternity comparison was too sparse to resolve the mapping alone. The waiting-to-start code included {{waiting_young}} youth, compared with {{illness_young}} in the next category, consistent with the questionnaire's distinction between new starters and illness-related absence. The team retained questionnaire coding and removed ambiguous absence responses. This is empirical support for a documented decision, not proof that every questionnaire route is measured without error.

### 4.3 Reproduction before modelling

The approved derivation yields weighted employed, unemployed and labour-force totals of {{national_employed}}, {{national_unemployed}} and {{national_labour_force}} million respectively, with unemployment {{all_ages_unemployment_rate}}. These agree with the rounded PBS headline figures within the approved tolerances. The youth reproduction gives {{youth_all_unemployment_rate}} and also checks sex and area comparisons. Reproduction is important because a classifier could otherwise learn a consistent but incorrectly constructed outcome.

The reproduction checks do not establish that the survey's complete production algorithm has been recovered. Rounded published totals can conceal small routing differences, and the future-starter timing limitation remains. The report consequently treats agreement as corroboration. It does not tune absence rules or exceptional categories to obtain a preferred total, and it distinguishes historical diagnostic attempts from the approved rule used in the current dataset.

### 4.4 Feature allowlist and leakage review

The predictor set is an explicit allowlist of {{feature_count}} fields. Employment, occupation, industry, wages, search and availability variables are excluded even when they might produce strong prediction. The outcome is derived from such information, so including it would partly ask the model to rediscover the label rule. Identifiers, weights, survey timing and administrative status fields are also excluded as predictors.

A training-only grouped single-feature scan fits a shallow decision tree separately for each input. Its highest average precision is {{max_scan}}, and no input exceeds the specified multiple-of-prevalence warning threshold. This check complements schema tests and source review; it cannot certify the absence of every possible information shortcut. Enrolment receives additional scrutiny because its predictive association is strong despite being a roster field rather than a label input.

### 4.5 Household grouping and Census context

The full-roster household key combines processing code, enumeration block and household number, without quarter. The audited {{households}} groups match the published household count (PBS, n.d.-a). Individual random splitting was rejected because related young people share household circumstances. A household must remain wholly within a partition and within a cross-validation holdout. The unusually large observed roster groups remain a documented caveat about possible identifier reuse.

Census linkage uses verified province-level context with the app lookup retaining the province and area keys. It does not infer districts from unrelated residence fields. In this build, density, urban proportion and average household size are constant within province. They therefore add no new geographic information beyond province, although alternative numeric representations can affect a fitted estimator. Ablation and joint geographic permutation examine this redundancy rather than treating the indicators as independent local measurements.

### 4.6 Class weights and operating thresholds

Class weights were compared with unweighted fitting. For HGB, default grouped-CV AP is {{hgb_E1_cv_ap_mean}} without weights and {{hgb_E2_cv_ap_mean}} with balanced weights. The logistic and forest comparisons likewise do not justify class weighting as a universal improvement. Weights can alter ranking and calibration; a better F1 at the default cutoff does not necessarily mean a better probability model.

The chosen approach retains unweighted fitting and adjusts the operating threshold using validation data. This separates ranking quality from the decision rule used to calculate precision and recall. Undersampling was omitted because the approved comparisons already address imbalance without a new dependency or discarded majority records. The consequence is a simpler reproducible pipeline, accompanied by explicit trade-offs rather than a claim that class imbalance has been solved.

### 4.7 Model choice within the tie rule

Random Forest has the highest mean CV AP, {{rf_E3_cv_ap_mean}}, compared with HGB {{hgb_E3_cv_ap_mean}}. Their unrounded difference lies just below the pre-agreed one-hundredth tie margin; the displayed difference rounds to {{cv_difference}}. The team selected HGB within that margin, citing its smaller training-to-CV gap, compact model file and practical prediction speed. The gaps are {{hgb_gap}} for HGB and {{rf_gap}} for the forest.

The selected compressed artefact measures {{model_kib}} KiB. A comparable saved forest size and controlled latency benchmark are not available in the aggregate evidence, so no numeric size or speed ratio is claimed. Random Forest was marginally ahead on the reported validation metrics, but it was never evaluated on test. The tie-break is thus a documented engineering judgement supported by CV proximity, not a claim that HGB won every metric.

### 4.8 Calibration, thresholds and risk bands

Raw validation probabilities have Brier score {{raw_brier}}, while sigmoid calibration has {{sigmoid_brier}} at report precision. The unrounded improvement is negligible; both values round alike. The fixed-bin calibration error changes from {{raw_ece_10_fixed_bins}} to {{sigmoid_ece_10_fixed_bins}}. The team kept raw probabilities because the comparison did not clearly justify a calibration layer fitted to the same validation labels.

The primary threshold is the midpoint between the outer thresholds whose validation F1 is near its maximum. The stored primary and screening cutoffs display as {{test_threshold}} and {{screen_threshold}}. A discontinuous F1 curve means the midpoint need not itself remain in the qualifying set: its validation F1 is {{val_f1}}, compared with the original maximum {{hgb_E4_val_f1}}. This limitation is retained rather than obscured by calling the midpoint exactly optimal.

High and Elevated bands begin at displayed probabilities {{high_min}} and {{elevated_min}}. They derive from validation score quantiles, with High representing the upper decile and Elevated the next portion. Equal scores may change realised band sizes. The app uses full stored precision and calls the remaining band Lower than most. A relative band is not a guarantee of safety, and a follow-up flag is not a verdict.

### 4.9 Evaluation, explanation and application

The model, calibration choice and operating thresholds were frozen before test scoring. Only the frozen HGB and stratified Dummy were evaluated on test. Later performance views consume saved summaries, preserving the distinction between development evidence and final evaluation. This policy prevents repeated comparisons from turning the nominally held-out partition into another tuning sample.

Explanations use validation permutation importance through the whole pipeline, with correlated columns also permuted jointly. Geography is moved as one internally consistent tuple, while sex is separately reported. Education combines qualification and literacy. This reduces misleading interpretations of redundant fields, although permutation can still create unusual combinations with other inputs. The enrolment ablation provides complementary evidence about performance when a field is absent during fitting.

Application decisions follow the same caution. The profile tool validates coherent input combinations, warns about rare survey support, reports the population base rate and keeps non-decision wording close to the estimate. The native fallback provides the same conceptual content if the custom interface fails. These choices make the analysis easier to inspect without adding a new prediction method inside the UI.

### 4.10 Skills-gap estimation

Statistical mismatch compares each employed youth's education band with the weighted modal band in the occupation group. Reference populations include all employed adults, mid-age employed adults and employed youth. The mid-age norm happens to have the same point modes as the all-adult norm, so it is not an independent point-estimate sensitivity. A normative occupation-to-education mapping answers a different question and is reported separately.

PSU-cluster resampling re-estimates occupational modes inside every statistical mismatch replicate. Holding modes fixed would ignore uncertainty about the reference classification, particularly where education categories are nearly tied. The normative comparison keeps its rules fixed because those rules are definitions rather than estimated modes. Reproduction checks compare weighted occupation shares, education distribution and age-eligible education unemployment rates against published PBS tables. The largest recorded absolute difference is {{reproduction_max}} percentage points.

## 5. Data and preparation

### 5.1 Sources and analytical populations

The source inventory in [DATA_SOURCES.md](../DATA_SOURCES.md) identifies the official LFS microdata, questionnaire, coding scheme and Annual Report, together with Census workbooks and methodological references. The questionnaire provides wording and routing; the coding scheme supports category interpretation; the Annual Report supplies definitions and published checks. Census context supplies geographic aggregates. None of these roles is interchangeable: a convenient variable label is not by itself a verified statistical definition.

The modelling population is youth aged fifteen through twenty-four classified as employed or unemployed. The broader survey-analysis dataset retains other eligible ages for occupational reference norms and all youth for approximate NEET. Counts are unweighted sample sizes unless explicitly described as weighted totals. This separation matters because survey weights expand observations to different population totals and because an occupational denominator excludes unemployed people.

### 5.2 Row waterfall and privacy

The raw roster contains {{waterfall_0}} records. After excluding the ambiguous absence category, {{waterfall_1}} remain; after excluding temporarily absent workers without a recorded reason, {{waterfall_2}} remain. The age-eligible national reproduction population contains {{waterfall_3}} records. Youth filtering retains {{waterfall_4}}, and restricting those youth to the labour force gives {{waterfall_5}} modelling records. This sequence records losses explicitly rather than silently dropping inconsistent rows.

Household size, children and other youth are calculated before the youth restriction. Otherwise a household would appear to contain only its selected young workers. Head's characteristics likewise come from the household roster. The source name field and address, phone or identity fields are removed from analytical exports. Group keys are retained only where grouping is required and are never displayed as predictors or as notebook examples.

Raw and person-level files remain local and ignored by version control. The application needs only the frozen model, metadata, small geographic lookup, rarity flags, score quantiles and aggregate results. Redistribution permission is not inferred from download availability. This boundary helps protect survey respondents and reduces the risk that the deployed interface or submission package exposes records irrelevant to its purpose.

## 6. Exploratory data analysis

The EDA describes the unweighted modelling records. It is intended to reveal imbalance, uneven support, coding problems and plausible feature relationships before model comparison. It should not be read as an alternative official population release. The weighted survey path answers population questions separately, and its uncertainty estimates cannot simply be attached to unweighted charts.

![Figure 2. Class balance in the unweighted modelling sample.](../reports/figures/class_balance.png)

The positive class contains {{sample_positive}} observations, or {{sample_prevalence}} of {{sample_n}} records. This explains why majority-class accuracy is an inadequate success criterion: a classifier can appear accurate while finding almost no unemployed youth. Average precision, recall and the Dummy baseline make that problem visible. The absolute number of positives also limits how finely subgroup performance can be estimated.

![Figure 3. Unweighted unemployment by sex and area, with sample counts.](../reports/figures/rate_sex_area.png)

Urban women have the highest unemployment share in this descriptive comparison, while the rural female group is much closer to the male groups. The pattern motivates the sex–area interaction and a fairness review, but does not identify a causal effect of location or sex. Group counts and labour-force selection are essential context; the women included here are a selected subset of all young women.

![Figure 4. Unemployment by recorded education category, including category counts.](../reports/figures/rate_by_education_level.png)

Education categories differ substantially in observed unemployment and in sample support. Fine qualification labels should not be interpreted as a smooth ladder with equally spaced distances. Some categories are rare and some degree labels describe course type rather than a higher attainment level. The broad-band skills analysis and the detailed model inputs therefore serve different purposes, and neither establishes the return to an additional qualification.

![Figure 5. Age distributions within the employed and unemployed classes.](../reports/figures/age_by_class.png)

The age chart normalises within class so that the larger employed group does not dominate the comparison. Visible peaks may reflect reported ages and the composition of the labour-force sample. Age is retained numerically and also represented by broad bands inside the pipeline. A cross-sectional age pattern is not a trajectory showing how the same young people progress through employment.

![Figure 6. Recorded missingness for the allowed modelling inputs.](../reports/figures/missing_values.png)

The largest observed feature missing rate is {{max_missing}}. This refers to recognised missing values after the approved conversion rules, not proof that the underlying questionnaire is error-free. Substantive responses such as no formal education or not enrolled remain meaningful categories. Training timing is collapsed, and the unverified training-type field is excluded. Imputation remains in the production pipeline to give consistent behaviour for valid missing values in later input.

## 7. Methodology

### 7.1 Inputs and preprocessing

**Table 2. The {{feature_count}} allowed raw input features, grouped by purpose.**

{{features}}

The pipeline begins with approved feature engineering and then applies a column transformer. Numeric features receive median imputation and standard scaling; categorical features receive most-frequent imputation and unknown-safe one-hot encoding. Infrequent categories are grouped according to the configured minimum frequency. All learned transformations are fitted only to the relevant training fold and reused for its holdout. The app calls this same fitted pipeline rather than reproducing preprocessing independently.

Engineered inputs include the education-code representation alongside the categorical qualification, broad age bands, children as a share of household size, a household-size upper clip learned from training, and a sex–area interaction. The education-code representation is a pragmatic ordering, not a claim that all qualifications have equal spacing or that adjacent degree types imply a strict skill ranking. Keeping the categorical input allows additional distinctions. The learned clipping limit is recalculated within training folds, preventing full-dataset distribution information from entering preprocessing.

### 7.2 Household partitions and cross-validation

**Table 3. Saved household-grouped partitions.**

{{splits_table}}

The partition procedure uses shuffled stratified household folds with a fixed random seed, allocating most folds to training and equal smaller sets to validation and test. The saved assignments are reused by experiments. Stratification balances the outcome as far as household grouping allows; exact equality is neither necessary nor guaranteed. Household membership, rather than each individual record, is the unit that must stay intact.

Model selection uses five-fold stratified grouped cross-validation within training. Average precision is the refit metric and ROC-AUC is also recorded. Every fold fits the complete pipeline, including feature engineering and encoding. Validation is then used for reported model comparisons, threshold selection and calibration review. The final test partition is not used to choose inputs, hyperparameters, explanatory groups or application behaviour.

### 7.3 Models, search and generalisation

The stratified Dummy supplies a random-prediction reference aligned with training class balance. Logistic regression provides a comparatively simple linear predictor, Random Forest represents interactions through bagged trees, and histogram gradient boosting builds additive tree corrections. Default, weighted and tuned variants separate the effects of model family, imbalance handling and hyperparameters. The experiment table retains these comparisons rather than reporting only the best-looking validation result.

The logistic grid crosses regularisation strength with class-weight options. Forest search varies tree count, depth, minimum leaf size, feature subsampling and weights. HGB search varies learning rate, depth, leaf count, minimum leaf size, regularisation, iteration count and weights, with early stopping disabled. The implemented random searches use {{n_iter_rf}} forest candidates and {{n_iter_hgb}} HGB candidates, fewer than the larger planned budgets, to keep grouped fitting practical on the available laptop. Appendix B records the exact search values and selected HGB parameters.

**Table 4. Tuned-model average precision and the training–CV gap.**

{{gap_table}}

The forest and HGB fit training data more strongly than their held-out folds; the logistic gap is smaller but its CV ranking quality is lower. A larger training score alone is therefore not evidence of a better generalising model. Fold variability also matters: the models are compared on the same grouped folds, allowing paired comparisons rather than treating different resamples as equivalent experiments.

![Figure 7. Grouped learning curve for Random Forest, the initial CV leader.](../reports/figures/grouped_learning_curve.png)

The saved learning curve belongs to Random Forest, not the eventual HGB selection. Its mean CV AP increases from {{learning_0}} at the smallest training fraction to {{learning_2}} at the largest. This suggests that additional training information may still help that model under this resampling design. It does not establish the learning curve of HGB or guarantee improvement with future survey data. The separate forest complexity curve examines sensitivity to maximum depth.

### 7.4 Evaluation and uncertainty

F1 balances precision and recall at an operating point, whereas AP summarises ranking across recall levels. ROC-AUC measures ranking over positive–negative pairs, and top-decile lift compares the concentration of unemployed observations in the highest-scored group with prevalence. Accuracy is retained for completeness but does not guide model selection. All model metrics are unweighted, reflecting the experimental record-based task.

Household bootstrap intervals resample test households with replacement, preserving within-household dependence. The saved calculation uses {{bootstrap_repeats}} repetitions. Percentile bounds describe variation under that resampling scheme; they do not represent uncertainty from retraining, the complete complex survey design or future economic conditions. Subgroup tables add denominators and positive counts, because a seemingly impressive recall based on very few unemployed observations can be highly unstable.

### 7.5 Explanation and survey estimation

Whole-pipeline permutation importance measures the AP decrease after an input or group is shuffled on validation. Error bars describe variation across permutations, not confidence intervals for a causal quantity. Correlated information may be shared across features, so small differences in importance are not treated as a ranking of social importance. Partial-dependence-style substitutions average predictions after setting a field to a common value and may create uncommon combinations.

The skills analysis instead uses LFS weights and PSU-cluster bootstrap intervals. Education is collapsed into broad bands, armed forces are excluded from the major-occupation comparison, and any unsupported lens is omitted rather than inferred. Industry, detailed field of study and unemployment barriers are not part of the final extension. The degree-type lens uses only explicitly identifiable questionnaire degree categories and retains its small-cell limitations.

Nonzero cells below the disclosure minimum are suppressed; structural impossibilities are marked with a dash. Unreliable groups carry a visible flag. When occupational modes frequently change across resamples or ranges become very wide, rows are labelled mode unstable and shown with their bootstrap range. An independent calculation checks headline agreement, while composition checks confirm that mutually exclusive outcomes sum to the full denominator before display rounding.

## 8. Results

### 8.1 Model comparison and final evaluation

**Table 5. Grouped CV and validation comparison; validation F1 uses each experimental tuned cutoff.**

{{comparison_table}}

These validation thresholds were selected on the same labels used to report F1, so their F1 values are optimistic. The HGB experimental maximum is also distinct from the subsequently frozen midpoint. The forest leads the reported validation metrics; HGB is selected through the documented tie rule. The test table evaluates only the frozen choice and the baseline, preserving the original distinction between selection and assessment.

**Table 6. Test metrics and household-bootstrap intervals at frozen operating points.**

{{test_table}}

The test sample contains {{test_n}} records and {{test_positives}} unemployed observations, giving prevalence {{test_prevalence_pct}}. HGB's AP {{test_pr_auc}} is meaningfully above Dummy AP {{dummy_pr_auc}}, while its F1 {{test_f1}} exceeds Dummy F1 {{dummy_f1}}. The F1 interval is {{f1_lower_95}}–{{f1_upper_95}} and the AP interval is {{pr_auc_lower_95}}–{{pr_auc_upper_95}}. These results show useful concentration of survey outcomes, alongside substantial errors and uncertainty.

![Figure 8. Test precision–recall curve with the no-skill prevalence line.](../reports/figures/test_pr_curve_wide.png)

At the primary cutoff the model correctly flags {{test_tp}} unemployed people and misses {{test_fn}}. It flags {{test_fp}} employed people, while {{test_tn}} employed people remain unflagged. Precision {{test_precision_pct}} means that most flags are not unemployed observations in this sample. Recall {{test_recall_pct}} means that a substantial share of unemployed people are missed. These counts make the limitations more concrete than a summary score alone.

The screening cutoff finds {{screen_tp}} unemployed people, with recall {{screen_recall_pct}}, but flags {{screen_fp}} employed people and has precision {{screen_precision_pct}}. This is an operating trade-off rather than a universally preferable setting. Top-decile lift is {{test_lift_10}}, compared with {{dummy_lift_10}} for the Dummy; top-fifth lift is {{test_lift_20}}. Ranking enriches the selected group, but enrichment does not justify using the group for individual decisions.

### 8.2 Subgroup errors and fairness

Primary recall is {{female_test_recall}} among females and {{male_test_recall}} among males, with {{female_test_positives}} and {{male_test_positives}} unemployed observations respectively. Their flagged shares are {{female_test_flag_rate}} and {{male_test_flag_rate}}. A common threshold intersects different group score distributions, so equal cutoffs do not imply equal recall. This describes a threshold-dependent performance difference; it is not a causal explanation of sex differences in unemployment or a demonstration of fairness.

Recall is {{noformal_test_recall}} for people without formal education, based on {{noformal_test_positives}} unemployed people among {{noformal_test_n}} records. For intermediate education it is {{intermediate_test_recall}}, based on {{intermediate_test_positives}} unemployed people among {{intermediate_test_n}} records. The contrast shows how a model with acceptable overall ranking can systematically miss an important subgroup. Degree-or-higher performance rests on only {{degree_test_positives}} positives among {{degree_test_n}} records and is flagged as unreliable.

The error analysis compares feature distributions for false negatives with true positives and false positives with true negatives. These are counts, so large groups can dominate even when their error rate is moderate. Both rate and count perspectives are needed: one describes unequal performance, the other the number of affected observations. The complete subgroup table in Appendix A supports examination beyond the selected examples in this narrative.

### 8.3 Importance, enrolment and ablation

Grouped AP importance is {{importance_Education}} for education, {{importance_Enrolment}} for enrolment, {{importance_Geography}} for geography and {{importance_Sex}} for sex. These are model-reliance measures under permutation. They do not imply that changing a person's category would produce a corresponding change in employment. Removing enrolment during grouped HGB fitting changes CV AP from {{hgb_E3_cv_ap_mean}} to {{without_enrolment}}, demonstrating substantial predictive reliance on that field.

Among training records, {{enrolled_unemployed}} of {{enrolled_n}} enrolled youth are unemployed, a rate of {{enrolled_unemployment_rate}}, compared with {{not_enrolled_unemployed}} of {{not_enrolled_n}} not-enrolled youth, or {{not_enrolled_unemployment_rate}}. The average substituted model profile also gives lower probabilities to enrolled categories. A plausible hypothesis involves labour-force selection and the search and availability rules: enrolled people who appear in this sample are largely working. The association must not be generalised to students outside the sample.

### 8.4 Education outcomes and graduate placement

**Table 7. Weighted youth unemployment within the labour force, with sample counts and PSU-bootstrap bounds.**

{{education_table}}

The gradient across the broad education bands persists as a descriptive pattern, but the same denominators also support employed-at-mode, employed-above-mode, employed-below-mode and unemployed shares. Those mutually exclusive outcomes are reproduced in Appendix A. Some mismatch-related intervals are asymmetric because resampled occupational modes alter the classification; ordinary unemployment rates do not depend on those modes. The distinction prevents a single uncertainty explanation from being incorrectly applied to every column.

Graduate absorption separates employment in managerial, professional, technical and clerical groups ({{graduate_upper}}) from employment in the remaining major groups ({{graduate_other}}) and unemployment ({{graduate_unemployed}}). These categories describe placement among degree-level labour-force youth, not the availability of graduate vacancies. Their full weighted shares, sample counts and intervals appear in Appendix A, alongside sex and area comparisons. A graduate in a lower major group is not automatically shown to have unusable skills or a poor-quality job.

### 8.5 Mismatch depends on definition

Strict above-mode shares range from {{strict_youth_estimate}} under the youth reference to {{strict_adult_estimate}} under the all-adult reference. The adult estimate has interval {{strict_adult_ci_low}}–{{strict_adult_ci_high}} with denominator {{strict_adult_n}}. The youth estimate has interval {{strict_youth_ci_low}}–{{strict_youth_ci_high}} with the same denominator. Its point estimate lies near the upper end because some bootstrap samples select alternative occupational modes, moving many youth into different mismatch categories.

Under the within-one-band definition, {{tolerance_estimate}} are matched within tolerance, with interval {{tolerance_ci_low}}–{{tolerance_ci_high}}. The severe above-mode definition gives {{severe_estimate}}, with interval {{severe_ci_low}}–{{severe_ci_high}}. The normative above-level share is {{normative_estimate}}, with interval {{normative_ci_low}}–{{normative_ci_high}} and denominator {{normative_n}}. These definitions are deliberately kept separate; combining them into a single range would disguise the questions being compared.

Agricultural and elementary occupations have low modal education, making the strict above-mode share sensitive to occupational composition and the coarse band scheme. This result is not a count of wasted degrees or proof of deficient workers. The by-occupation tables label mode unstable rows and show the bootstrap range. The accompanying stability table records how often each band is selected, making uncertainty in the reference classification visible rather than burying it inside a narrow-looking interval.

### 8.6 Training, approximate NEET and illustrative shifts

Training ever/current is reported by {{training_unemployed}} of unemployed youth and {{training_employed}} of employed youth. It is {{training_difference}} percentage points lower among unemployed than employed youth, with a difference magnitude interval of {{training_ci_high}}–{{training_ci_low}} percentage points. The comparison cannot isolate a training effect: training can occur during employment, and timing categories were deliberately discarded to form the permitted indicator.

The not-employed-and-not-enrolled approximation is {{neet_estimate}}, with interval {{neet_ci_low}}–{{neet_ci_high}}, denominator {{neet_n}} and cell count {{neet_positive_n}}. PBS reports {{neet_pbs}} for national youth NEET. Our approximation is not the complete SDG indicator because recent training cannot be identified. Sex and area results appear in Appendix A; they describe broader exclusion from work and enrolment than the labour-force-only unemployment classifier.

The education-profile substitution covers {{shift_n}} validation records, corresponding to {{shift_coverage}} weighted coverage. Its average model-estimated difference is {{shift_mean}} percentage points, with code-choice sensitivity {{shift_minimum}}–{{shift_maximum}}. The calculation averages valid next-band codes using training frequencies and excludes invalid or rare combinations. This is a model-estimated difference within the labour-force sample, affected by selection, not an educational intervention effect. Low-education employment is concentrated in agricultural and elementary occupations, and many low-educated women are outside the labour force.

## 9. Deployment and verification

**Live application:** [TEAM TO INSERT SUBMISSION URL]

Streamlit hosts the interface and caches the model and metadata resources. The entry point resolves repository-relative paths and imports the package containing the custom transformer before unpickling. Tracked assets supply category labels, geographic context, rarity flags, quantiles and displayed result tables. The custom dashboard component communicates with the Python application for prediction; the native fallback retains usable tables and controls if that component cannot render (Streamlit, n.d.).

Application testing checks loading, navigation, invalid-input handling and the agreement of app predictions with pipeline probabilities for valid profiles. It also checks category coercion so equivalent coded values produce the same input representation, and unknown categories raise a clear error. Household-head consistency and rarity warnings are tested separately. These checks complement model tests; a statistically frozen artefact does not by itself prevent a UI mapping or input-type bug.

The report uses the saved screenshots below to document the desktop pages and representative phone layouts. They illustrate navigation and presentation rather than serving as the source of statistical values. Tables and report prose draw from saved numerical evidence. Responsive presentation keeps the same definitions across screen sizes; it should not introduce different calculations for mobile visitors.

![Figure 9. Overview, desktop layout.](screenshots/overview-1440x900.png)

![Figure 10. Skills gap, desktop layout.](screenshots/skills-1440x900.png)

![Figure 11. Profile explorer, desktop layout.](screenshots/explorer-1440x900.png)

![Figure 12. Model performance, desktop layout.](screenshots/performance-1440x900.png)

![Figure 13. Data and methodology, desktop layout.](screenshots/methodology-1440x900.png)

![Figure 14. Overview, phone layout.](screenshots/overview-390x844.png)

![Figure 15. Skills gap, phone layout.](screenshots/skills-390x844.png)

![Figure 16. Profile explorer, phone layout.](screenshots/explorer-390x844.png)

## 10. Limitations and future work

The modelling analysis is unweighted and limited to the labour force. Its probabilities describe the fitted sample relationship rather than a representative risk for every young person in Pakistan. The future-starter timing condition cannot be checked. Household grouping reduces related-record leakage but depends on the approved key, whose unusual large groups deserve further validation. An external survey or later observation period would provide stronger evidence of transportability than further reuse of the held-out sample.

Census indicators are coarse and constant within province. They cannot represent neighbourhood opportunities or changes between the Census and survey periods. Education bands and major occupations also compress important variation. The ordinal education-code feature is a modelling convenience, and the statistical mode is a description of workers, not a direct requirement imposed by employers. Vacancy data, skill assessments and job-quality measures would be needed for stronger claims about labour-market matching.

PSU bootstrap intervals acknowledge clustering but omit stratification and other elements of the complete survey design. Re-estimating modes captures classification uncertainty within this approximation, yet unstable occupational modes remain sensitive to sample composition. Disclosure suppression protects small observed cells but also limits the specificity of conclusions. Point estimates and their intervals should be read with the reference population, reliability flag and weighting method together.

Fairness remains an empirical and normative question. Sex and geography are inputs, subgroup recall differs markedly, and calibration can vary across combinations. Future work should assess external calibration, subgroup error uncertainty and intended-use harms with domain stakeholders. Removing a sensitive input alone would not guarantee fairness because correlated information remains. No individual decision use is justified by the current evaluation, even if aggregate predictive scores improve.

## 11. Use of AI assistance

**TEAM TO COMPLETE ACCORDING TO COURSE POLICY:** Describe the AI tools used, the tasks for which assistance was received, the material independently checked, and how each member verified and understood the submitted work. Include the course's required disclosure wording and any restrictions that applied. The team remains responsible for the correctness, originality, interpretation and defensibility of the submission.

## 12. Individual contributions

**Table 8. Individual contributions for completion by the team.**

| Member | Student identifier | Implementation and analysis | Writing and verification |
| --- | --- | --- | --- |
| Sarim Khan | CT-24266 | [TEAM TO COMPLETE] | [TEAM TO COMPLETE] |
| Muhammad Saraib | CT-24255 | [TEAM TO COMPLETE] | [TEAM TO COMPLETE] |
| Danish Meraj | CT-24268 | [TEAM TO COMPLETE] | [TEAM TO COMPLETE] |

## References

{{references}}

## Appendix A. Full results and uncertainty

{{skills_appendices}}

### Table A12. Complete test subgroups at both operating points

{{subgroup_table}}

Source: [test_subgroups.csv](../reports/tables/test_subgroups.csv). True in the final column indicates fewer than fifty unemployed observations; it is a reliability flag, not an exclusion.

### Table A13. Occupation modes for every statistical reference population

{{modes_table}}

Source: [skills_occupation_modes.csv](../reports/tables/skills_occupation_modes.csv).

### Table A14. Reproduction against published PBS tables

{{reproduction_table}}

Source: [skills_reproduction.csv](../reports/tables/skills_reproduction.csv). Occupation and literacy distributions use their published reference populations; education unemployment uses all eligible ages. These are not youth-only denominators.

### Table A15. Bootstrap modal-band frequencies for mode-unstable occupations

{{stability_table}}

Source: [skills_mode_stability.csv](../reports/tables/skills_mode_stability.csv). Frequent alternative modes explain asymmetric mismatch ranges; no individual respondent is identified.

### Table A16. Validation-only model substitutions and coverage

{{shift_table}}

Source: [skills_model_shift.csv](../reports/tables/skills_model_shift.csv). Changes are percentage points; code minima and maxima are sensitivity summaries, not confidence bounds. Counts are unweighted, coverage and shift summaries use the recorded survey weighting. Subgroup codes retain the table's keys: sex and area refer respectively to male/female and rural/urban in the audited coding.

## Appendix B. Hyperparameters and search specification

**Table B1. Selected HGB parameters from the saved tuned experiment.**

{{parameters_table}}

Early stopping is disabled. The random seed is fixed consistently across the analytical workflow. The model's full machine-readable settings remain in the protected metadata.

**Table B2. Implemented search spaces, read from the experiment script.**

{{search_table}}

Logistic evaluates the full grid. The random searches draw {{n_iter_rf}} forest candidates and {{n_iter_hgb}} HGB candidates. The spaces come from `scripts/compare_models.py`; values are shown at report precision, with None meaning the relevant limit or class weighting is absent.

## Appendix C. Test inventory

The inventory below names the repository checks by subject. It documents coverage rather than implying that automated checks prove statistical validity. Data-dependent checks require the local ignored datasets; application parity checks use the same protected pipeline as deployment.

{{test_inventory}}

## Appendix D. Dashboard glossary

- **Labour force:** employed people plus people meeting the unemployment definition.
- **Prevalence:** the share of the specified sample classified as unemployed.
- **Probability:** the frozen model's conditional estimate for a supplied profile.
- **Percentile:** the proportion of validation scores below a profile's position; distinct from probability.
- **Flagged for follow-up:** the score crosses the stored illustrative threshold, without establishing an individual verdict.
- **Precision:** the unemployed share among flagged observations.
- **Recall:** the share of unemployed observations that are flagged.
- **F1:** the harmonic mean of precision and recall.
- **Average precision:** a summary of precision across recall levels, shown as PR-AUC in the dashboard.
- **ROC-AUC:** ranking discrimination across positive–negative pairs.
- **Lift:** concentration of unemployed observations in a high-score group relative to prevalence.
- **Calibration:** agreement between predicted probabilities and observed frequencies.
- **Survey weight:** the contribution of a record to a population estimate.
- **PSU:** primary sampling unit, the cluster resampled for survey uncertainty.
- **Bootstrap range:** percentile bounds across resamples; mode-unstable estimates require particular caution.
- **Structural zero:** an outcome impossible under the definition; shown as a dash rather than suppressed.
- **Mode unstable:** the reference education category changes often across resamples or the resulting range is exceptionally wide.
- **Education mismatch:** an occupation-based comparison using education as a skills proxy.
- **Approximate NEET:** not employed and not enrolled, without a verified recent-training condition.

## Publication details requiring team verification

- [VERIFY] Exact publication year of the PBS Annual Report, questionnaire and coding/microdata release; the survey reference period is established.
- [VERIFY] Release date of the Census detailed-results workbooks; the Census reference year is established.
- [VERIFY] Publication date and constituent survey reference periods of NAVTTC's *Skills trend analysis: National & international*. It supplies context only; no employer-demand statistic from it enters the results.
