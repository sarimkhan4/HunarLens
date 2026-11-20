# HunarLens: Youth Unemployment Vulnerability and Skills-Gap Analysis in Pakistan

**CT-378 Machine Learning · AlphaDevs**  
Sarim Khan (CT-24266), Muhammad Saraib (CT-24255), Danish Meraj (CT-24268)  
Date and instructor: [TEAM TO COMPLETE]

## 1. Abstract

HunarLens combines an explainable unemployment classifier with weighted survey analysis for Pakistan. The modelling sample contains 26,653 labour-force youth and 12.7% unemployment. A frozen histogram gradient boosting pipeline achieves test F1 0.360, average precision 0.303 and ROC-AUC 0.752, compared with stratified-Dummy F1 0.123 and AP 0.127. Household-grouped development and a protected test evaluation support a credible comparison. The separate skills analysis finds weighted unemployment increasing from 8.2% without formal education to 22.6% with a degree or above. Occupational mismatch varies with its reference definition. A Streamlit dashboard displays evidence, uncertainty and illustrative profiles. These associations are conditional on survey definitions and labour-force membership, and are unsuitable for individual employment decisions.

## 2. Problem, importance and data

The questions are whether permitted demographic and household inputs distinguish unemployed from employed youth, and how education and training relate to outcomes and occupational placement. Unemployment is conditional on labour-force membership; many students and carers without employment are outside that denominator. The classifier therefore does not estimate an outcome for all youth without work.

PBS reports youth unemployment 12.8% compared with national unemployment 7.1%, and youth NEET 28.4% (PBS, n.d.). The project uses the Labour Force Survey and Census regional context, with questionnaire audits preceding analysis. Skills are not directly tested: education and vocational training are proxies, occupations describe current placement, and vacancies and employer demand are absent. ILO and ETF guidance support distinguishing educational mismatch from direct skill measurement (ILO, 2021; ETF, 2019).

The audited modelling dataset contains demographic, education, household-roster and Census inputs. Labour-market outcome fields, occupation, weights and identifiers are excluded as predictors. Household features are constructed before youth filtering. Raw and person-level files stay outside the submission; the dashboard reads the protected model and small aggregate artefacts. Source links and reuse-status details are in [DATA_SOURCES.md](../DATA_SOURCES.md).

\newpage

## 3. Design and methodological decisions

**Table 1. Choices, alternatives and evidence.**

| Decision | Alternatives considered | Choice and reason | Evidence |
| --- | --- | --- | --- |
| Labour-force label | Search alone; reported status; audited routes | Work, absence, search and availability routes with an explicit future-starter approximation | Label reproduction and future-starter diagnostics |
| Study population | All youth; labour-force youth | Labour-force youth for prediction; all youth for approximate NEET | Row waterfall and population definitions |
| Predictors | Broad survey fields; explicit allowlist | Demographic, education, roster and Census inputs; exclude outcome information | Feature audit and single-feature scan |
| Partitioning | Individual random split; household grouping | Keep related youth together in partitions and CV folds | Saved split summary and overlap tests |
| Geography | District linkage; province context | Verified province join; recognise constant Census features | Census lookup and feature ablation |
| Imbalance | Resampling; class weights; threshold adjustment | Compare weights, retain unweighted HGB and validation thresholds | Experiment comparison |
| Model selection | Largest CV score; pre-agreed simplicity tie rule | HGB within the tie band, with smaller train–CV gap and compact deployment | CV fold scores and gap table |
| Probability calibration | Raw probabilities; sigmoid mapping | Raw probabilities; validation Brier improvement was negligible | Calibration comparison |
| Operating points | Default cutoff; isolated F1 maximum; plateau midpoint | Validation midpoint plus recall-oriented alternative | Threshold table and documented midpoint limitation |
| Evaluation | Repeated test comparisons; frozen evaluation | Score the frozen pipeline once; reuse stored summaries | Test metrics and bootstrap intervals |
| Explanation | Individual importance alone; grouped information | Whole-pipeline permutations, correlated groups and ablation | Permutation and enrolment-ablation tables |
| Interface | Personal verdict; contextual exploration | Plain language, frequencies, uncertainty and non-decision wording | Dashboard, fallback and parity tests |
| Skills analysis | Direct skill claims; education proxies | Weighted attainment and occupational mismatch with resampled norms | Skills methods, reproduction and sensitivity tables |


Grouped cross-validation fits the complete preprocessing pipeline inside each training fold. AP selects candidates; validation supports threshold and calibration decisions. Random Forest leads CV AP, but its advantage over HGB lies within the pre-agreed tie margin. HGB has a smaller train–CV gap and a compact deployment artefact. Sigmoid calibration offers negligible Brier improvement, so probabilities remain raw. The midpoint threshold's F1 is slightly below the intended near-maximum band because F1 is discontinuous; this limitation is recorded rather than concealed.

The survey path uses weights and PSU-cluster bootstrap intervals. Occupational modes are re-estimated in every statistical mismatch replicate, and normative definitions remain separate. Structural zeros are shown as dashes; small nonzero cells are suppressed and unstable modes are labelled. The adult and mid-age norms share the same point modes, so they are not independent point-estimate sensitivities.

\newpage

## 4. Key results

**Table 2. Test performance with household-bootstrap intervals.**

| Model / operating point | F1 [95% CI] | Precision [95% CI] | Recall [95% CI] | AP [95% CI] | ROC-AUC [95% CI] | Top-decile lift [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| HGB F1 | 0.360 [0.328, 0.393] | 0.273 [0.245, 0.303] | 0.530 [0.485, 0.576] | 0.303 [0.267, 0.343] | 0.752 [0.731, 0.774] | 2.814 [2.450, 3.129] |
| HGB screening | 0.354 [0.326, 0.382] | 0.247 [0.223, 0.271] | 0.628 [0.584, 0.675] | 0.303 [0.267, 0.343] | 0.752 [0.731, 0.774] | 2.814 [2.450, 3.129] |
| Stratified Dummy | 0.123 [0.097, 0.154] | 0.125 [0.098, 0.156] | 0.122 [0.094, 0.152] | 0.127 [0.116, 0.139] | 0.499 [0.484, 0.515] | 0.866 [0.747, 1.240] |

The test denominator is 3,999, including 508 unemployed observations and prevalence 12.7%. At the primary cutoff, HGB finds 269 unemployed people, misses 239, and flags 716 employed people. Its top-decile lift is 2.814. The screening cutoff finds 319 unemployed people but flags 975 employed people. These trade-offs prevent the apparent improvement over random prediction from being interpreted as reliable individual classification.

Subgroup coverage is uneven. Recall is 17.9% for people without formal education, with 95 positives among 1,038 records, compared with 94.1% for intermediate education, with 101 positives among 617 records. Degree-or-higher estimates use only 46 positives and are unreliable. A common threshold produces different recalls across sex groups because their score distributions differ; this is not evidence of a causal sex effect.

**Table 3. Weighted youth unemployment by education.**

| Population / norm | Outcome / education | Denominator n | Cell n | Weighted share | Lower bound | Upper bound | Disclosure / reliability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Overall | No formal | 7,094 | 617 | 8.2% | 7.3% | 9.0% |  |
| Overall | Below matric | 9,629 | 1,080 | 11.4% | 10.6% | 12.2% |  |
| Overall | Matric | 4,574 | 679 | 14.8% | 13.7% | 16.0% |  |
| Overall | Intermediate | 3,849 | 664 | 17.5% | 16.1% | 19.1% |  |
| Overall | Degree or above | 1,507 | 343 | 22.6% | 20.3% | 25.0% |  |

Training attainment is 8.9 percentage points lower among unemployed than employed youth, with interval 7.5–10.3 percentage points for the magnitude. Strict above-mode mismatch ranges from 41.0% to 46.0% across statistical reference populations. The normative above-level share is separately 10.6%. These comparisons depend on occupational composition and do not measure unusable qualifications. Approximate NEET is 29.3%, with interval 28.7%–29.8%, beside PBS's 28.4%; recent training cannot be identified in the approximation.

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
