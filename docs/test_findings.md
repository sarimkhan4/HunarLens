# test evaluation: final test findings

The frozen HGB model was evaluated once on 3,999 labour-force youth, including 508 unemployed people (12.7%). At the frozen F1 threshold, its F1 was 0.360, precision 0.273, recall 0.530, average precision 0.303, and ROC-AUC 0.7520. The stratified Dummy scored 0.123 F1 and 0.127 average precision. HGB's top-10% lift was 2.81, compared with 0.87 for the Dummy. These are unweighted test results.

At the primary threshold, HGB correctly flagged 269 unemployed people and missed 239; it also flagged 716 employed people. The screening threshold improved recall to 0.628 (319 of 508), with precision 0.247 and 975 employed people flagged. These are different operating trade-offs, fixed before test evaluation, not recommendations to make individual decisions.

The 1,000 household-grouped bootstrap resamples give a 95% percentile interval of 0.328–0.393 for primary-threshold F1 and 0.267–0.343 for average precision. These intervals summarise variation under household resampling of this test sample; they do not incorporate survey weights or the full survey design, and do not guarantee performance in another population.

At the primary threshold, recall was 0.480 for men and 0.680 for women, and 0.498 in rural areas and 0.583 in urban areas. Recall was 0.179 among those with no formal education and 0.941 in the intermediate-education group; precision in those groups was 0.215 and 0.311 respectively. These differences are descriptive and warrant a fairness discussion. The Balochistan subgroup has only 35 positives and the degree-or-higher group has 46, so their subgroup estimates are flagged as unreliable. Even groups above 50 positives may have considerable uncertainty.

The error counts illustrate the uneven coverage: of the 95 unemployed people with no formal education, 78 were false negatives and 17 were true positives. Among all test records, the 716 false positives and 2,775 true negatives are described by feature-value counts in `reports/tables/test_error_distributions.csv`; these counts reflect group sizes as well as performance.

The High, Elevated and Lower bands contain 433, 813 and 2,753 people, with observed unemployment shares of 0.349, 0.194 and 0.072 respectively. The test Brier score was 0.100. These summaries assess the frozen validation-derived cut-offs; they do not establish calibration for other populations.

The analysis uses no survey weights and the sample is limited to youth classified as in the labour force. For future starters, the available data do not verify when the arranged job or business begins, so the standard's timing condition cannot be checked. Subgroup results can be small and unstable, and the model encodes historical associations, including sex and geography. HunarLens is an aggregate pattern tool for exploration, not a decision tool for individuals.
