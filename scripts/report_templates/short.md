# HunarLens: Youth Unemployment Vulnerability and Skills-Gap Analysis in Pakistan

**CT-378 Machine Learning · AlphaDevs**  
Sarim Khan (CT-24266), Muhammad Saraib (CT-24255), Danish Meraj (CT-24268)  
Date and instructor: [TEAM TO COMPLETE]

## 1. Abstract

HunarLens combines an explainable unemployment classifier with weighted survey analysis for Pakistan. The modelling sample contains {{sample_n}} labour-force youth and {{sample_prevalence}} unemployment. A frozen histogram gradient boosting pipeline achieves test F1 {{test_f1}}, average precision {{test_pr_auc}} and ROC-AUC {{test_roc_auc}}, compared with stratified-Dummy F1 {{dummy_f1}} and AP {{dummy_pr_auc}}. Household-grouped development and a protected test evaluation support a credible comparison. The separate skills analysis finds weighted unemployment increasing from {{lowedu_estimate}} without formal education to {{degree_estimate}} with a degree or above. Occupational mismatch varies with its reference definition. A Streamlit dashboard displays evidence, uncertainty and illustrative profiles. These associations are conditional on survey definitions and labour-force membership, and are unsuitable for individual employment decisions.

## 2. Problem, importance and data

The questions are whether permitted demographic and household inputs distinguish unemployed from employed youth, and how education and training relate to outcomes and occupational placement. Unemployment is conditional on labour-force membership; many students and carers without employment are outside that denominator. The classifier therefore does not estimate an outcome for all youth without work.

PBS reports youth unemployment {{youth_all_pbs_unemployment_rate}} compared with national unemployment {{all_ages_pbs_unemployment_rate}}, and youth NEET {{neet_pbs}} (PBS, n.d.). The project uses the Labour Force Survey and Census regional context, with questionnaire audits preceding analysis. Skills are not directly tested: education and vocational training are proxies, occupations describe current placement, and vacancies and employer demand are absent. ILO and ETF guidance support distinguishing educational mismatch from direct skill measurement (ILO, 2021; ETF, 2019).

The audited modelling dataset contains demographic, education, household-roster and Census inputs. Labour-market outcome fields, occupation, weights and identifiers are excluded as predictors. Household features are constructed before youth filtering. Raw and person-level files stay outside the submission; the dashboard reads the protected model and small aggregate artefacts. Source links and reuse-status details are in [DATA_SOURCES.md](../DATA_SOURCES.md).

\newpage

## 3. Design and methodological decisions

**Table 1. Choices, alternatives and evidence.**

{{decisions}}

Grouped cross-validation fits the complete preprocessing pipeline inside each training fold. AP selects candidates; validation supports threshold and calibration decisions. Random Forest leads CV AP, but its advantage over HGB lies within the pre-agreed tie margin. HGB has a smaller train–CV gap and a compact deployment artefact. Sigmoid calibration offers negligible Brier improvement, so probabilities remain raw. The midpoint threshold's F1 is slightly below the intended near-maximum band because F1 is discontinuous; this limitation is recorded rather than concealed.

The survey path uses weights and PSU-cluster bootstrap intervals. Occupational modes are re-estimated in every statistical mismatch replicate, and normative definitions remain separate. Structural zeros are shown as dashes; small nonzero cells are suppressed and unstable modes are labelled. The adult and mid-age norms share the same point modes, so they are not independent point-estimate sensitivities.

\newpage

## 4. Key results

**Table 2. Test performance with household-bootstrap intervals.**

{{test_table}}

The test denominator is {{test_n}}, including {{test_positives}} unemployed observations and prevalence {{test_prevalence_pct}}. At the primary cutoff, HGB finds {{test_tp}} unemployed people, misses {{test_fn}}, and flags {{test_fp}} employed people. Its top-decile lift is {{test_lift_10}}. The screening cutoff finds {{screen_tp}} unemployed people but flags {{screen_fp}} employed people. These trade-offs prevent the apparent improvement over random prediction from being interpreted as reliable individual classification.

Subgroup coverage is uneven. Recall is {{noformal_test_recall}} for people without formal education, with {{noformal_test_positives}} positives among {{noformal_test_n}} records, compared with {{intermediate_test_recall}} for intermediate education, with {{intermediate_test_positives}} positives among {{intermediate_test_n}} records. Degree-or-higher estimates use only {{degree_test_positives}} positives and are unreliable. A common threshold produces different recalls across sex groups because their score distributions differ; this is not evidence of a causal sex effect.

**Table 3. Weighted youth unemployment by education.**

{{education_table}}

Training attainment is {{training_difference}} percentage points lower among unemployed than employed youth, with interval {{training_ci_high}}–{{training_ci_low}} percentage points for the magnitude. Strict above-mode mismatch ranges from {{strict_youth_estimate}} to {{strict_adult_estimate}} across statistical reference populations. The normative above-level share is separately {{normative_estimate}}. These comparisons depend on occupational composition and do not measure unusable qualifications. Approximate NEET is {{neet_estimate}}, with interval {{neet_ci_low}}–{{neet_ci_high}}, beside PBS's {{neet_pbs}}; recent training cannot be identified in the approximation.

\newpage

## 5. Deployment, limitations and future work

The dashboard provides Overview, Skills gap, Profile explorer, Model performance, and Data and methodology. It combines readable categories, probabilities alongside frequencies and a base rate, uncertainty displays, explicit non-decision wording and a native fallback. Profile inputs are validated without being stored. App-to-pipeline parity tests and rendering checks complement statistical tests. Live URL: [TEAM TO INSERT SUBMISSION URL].

Prediction is unweighted, conditional on labour-force participation and tied to the observed survey period. Enrolment is a strong correlate partly reflecting selection: enrolled members of the labour force are mostly working, while many students are outside the sample. The future-starter job-start limit is unverifiable. Census context is constant within province and cannot represent local demand. Education and occupations are coarse proxies, and the PSU bootstrap omits stratification. Mode instability and suppressed cells limit detailed conclusions.

Future work should prioritise external validation, calibration across groups, better geographic information and independent employer-demand evidence. A higher score would not itself authorise individual use. Decisions about employment or services require evidence and safeguards outside this project's scope. The complete report provides the architecture, screenshots, full uncertainty tables, hyperparameters, test inventory and glossary.

## 6. Team declarations

**AI assistance — TEAM TO COMPLETE:** Explain assistance received, independent checks, authorship responsibilities and the course-policy disclosure.

**Individual contributions — TEAM TO COMPLETE:** Record each member's implementation, analysis, writing and verification responsibilities.

## References

- European Training Foundation. (2019). *Skills mismatch measurement in ETF partner countries*. https://www.etf.europa.eu/en/publications-and-resources/publications/skills-mismatch-measurement-etf-partner-countries (accessed November 20, 2026).
- International Labour Organization. (2013). *Resolution concerning statistics of work, employment and labour underutilization*. https://www.ilo.org/resource/resolution-concerning-statistics-work-employment-and-labour-0 (accessed November 20, 2026).
- International Labour Organization. (2021). *Only half of workers worldwide hold jobs corresponding to their level of education*. https://ilostat.ilo.org/blog/only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education/ (accessed November 20, 2026).
- Pakistan Bureau of Statistics. (n.d.). *Labour Force Survey 2024–25: Annual report*. https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf (accessed November 20, 2026). [VERIFY: publication year.]
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html
- Streamlit. (n.d.). *Streamlit documentation*. https://docs.streamlit.io/ (accessed November 20, 2026).

**Publication detail requiring team verification:** [VERIFY] The PBS report's publication year, distinct from its confirmed survey reference period.
