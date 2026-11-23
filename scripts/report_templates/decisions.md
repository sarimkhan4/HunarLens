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
