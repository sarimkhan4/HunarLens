# What: creates a course-focused ML guide using the project's saved evidence.
# Why: students need to explain the concepts and the exact implementation in a viva.
# Viva: this generator reads only aggregate tables and never refits or scores a model.
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import build_project_guide as layout

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'reports/tables'


def rows(name):
    with (TABLES / f'{name}.csv').open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def find(name, **conditions):
    matches = [row for row in rows(name) if all(row.get(key) == str(value) for key, value in conditions.items())]
    if len(matches) != 1:
        raise ValueError(f'Expected one {name} row for {conditions}; got {len(matches)}')
    return matches[0]


def num(row, key):
    return float(row[key])


def pct(row, key):
    return f'{100 * num(row, key):.1f}%'


def value(row, key):
    return f'{num(row, key):.3f}'


def add(guide, heading, paragraphs):
    guide.section(heading)
    for item in paragraphs:
        if isinstance(item, tuple):
            guide.add(item[1], item[0])
        else:
            guide.add(item)


def build():
    guide = layout.Guide()
    train = find('split_summary', split='train')
    val = find('split_summary', split='val')
    test = find('split_summary', split='test')
    hgb = find('experiments', exp_id='E3', model='hist_gradient_boosting')
    rf = find('experiments', exp_id='E3', model='random_forest')
    lr = find('experiments', exp_id='E3', model='logistic_regression')
    hgb_default = find('experiments', exp_id='E1', model='hist_gradient_boosting')
    hgb_weighted = find('experiments', exp_id='E2', model='hist_gradient_boosting')
    metrics = find('test_metrics', model_threshold='HGB F1')
    screening = find('test_metrics', model_threshold='HGB screening')
    dummy = find('test_metrics', model_threshold='Stratified Dummy')
    frequent = find('baseline_validation', model='most_frequent')
    hgb_gap = find('generalization_gap', model='hist_gradient_boosting')
    rf_gap = find('generalization_gap', model='random_forest')
    raw = find('calibration_validation', method='raw')
    sigmoid = find('calibration_validation', method='sigmoid')
    val_threshold = find('validation_thresholds', threshold_type='f1')
    f1ci = find('test_bootstrap_ci', model_threshold='HGB F1', metric='f1')
    education = find('grouped_permutation_importance', group='Education')
    enrolment = find('grouped_permutation_importance', group='Enrolment')
    no_enrolment = find('feature_group_ablation', model='hist_gradient_boosting', ablation='full_without_currently_enrolled')
    no_formal = find('test_subgroups', value='No formal education', threshold='f1')
    intermediate = find('test_subgroups', value='Intermediate', threshold='f1')
    metadata = json.loads((ROOT / 'models/metadata.json').read_text(encoding='utf-8'))
    params = metadata['model_parameters']

    add(guide, 'How to study with this guide', [
        'This guide is written for the machine-learning course and individual viva. Each section explains a concept, the concrete HunarLens implementation, the reason for the choice and the limitations. The numbers come from the saved aggregate experiment and evaluation tables.',
        'The prediction task is conditional on belonging to the labour force. The model estimates survey associations, not a person’s abilities or a causal effect. It is an educational research tool, not an employment or benefits decision system.',
        'The guide uses stored evidence only. It does not retrain a model or score the test split. Source files are identified so that each student can open them and trace the implementation independently.'
    ])
    add(guide, '1. Framing the machine-learning problem', [
        ('h2', 'Supervised learning and binary classification'),
        'Supervised learning uses examples with known outcomes to learn a function from inputs X to a target y. In this project each eligible survey record is one example. The target is is_unemployed: 1 means unemployed and 0 means employed. The model returns an estimated probability for class 1.',
        'This is binary classification, not regression on a continuous outcome, clustering, or prediction of every person without work. The modelled population consists of youth aged 15–24 who are classified as employed or unemployed. Students or carers outside the labour force do not become negative or positive training examples simply because they are not employed.',
        ('h2', 'Training examples versus population estimates'),
        f'The analysis dataset contains {int(train["rows"])+int(val["rows"])+int(test["rows"]):,} examples. The model-development and test metrics are unweighted. Weighted survey analyses and label reproduction are separate; their rates answer population-estimation questions and should not be confused with model-sample prevalence.',
        'The positive class is a minority. An apparently high accuracy could be achieved by labelling nearly everyone employed. That makes positive-class precision, recall, F1 and average precision essential.',
        'Trace: src/hunarlens/config.py defines TARGET, GROUP and FEATURES; scripts/build_modeling_dataset.py constructs the outcome.'
    ])
    add(guide, '2. Data, labels and the danger of leakage', [
        ('h2', 'Ground truth is an operational definition'),
        'A target must be defined before model fitting. The project uses audited survey responses about work, temporary absence, search and availability. Some qualifying future starters are included using the near-future response, but the available file does not establish the precise job-start date. A weighted comparison with published PBS totals checks consistency; a match does not prove that every individual is perfectly classified.',
        'The S5C5 absence-reason value labels conflict with the questionnaire. The team used the questionnaire interpretation after empirical review and excluded documented ambiguous records. A model can learn a target only as well as that target is measured: label error, missing timing and survey routing all affect the meaning of performance.',
        ('h2', 'Leakage: using information unavailable or too close to the answer'),
        'Leakage occurs when fitting or evaluation gains information that would not be legitimately available for the intended prediction. Employment, job search, availability, occupation, wages and hours are excluded from X because they describe the labour-market outcome or directly participate in its derivation. Names, identifiers, survey weights and household group IDs are also excluded as predictors.',
        'The project uses an explicit allowlist rather than dropping a few known bad columns from the full survey. A grouped single-feature scan and input-schema tests are additional checks. They can reveal suspicious signals but cannot prove the complete absence of leakage. A very predictive feature should prompt a substantive investigation, not an automatic claim of cheating or validity.',
        'Trace: src/hunarlens/config.py, scripts/build_modeling_dataset.py, reports/tables/single_feature_scan.csv and tests/test_dataset.py.'
    ])
    add(guide, '3. Exploratory data analysis and imbalance', [
        ('h2', 'What EDA does'),
        'Exploratory data analysis checks class balance, data ranges, missing values, category frequencies and associations before modelling. It reveals problems such as rare values, implausible household sizes or a category that may be a missing-value code. It does not establish why an association exists.',
        f'The training split has {int(train["positives"]):,} unemployed examples among {int(train["rows"]):,} rows, or {pct(train,"prevalence")}. In validation the most-frequent baseline predicts the majority class, giving accuracy {pct(frequent,"accuracy")} but unemployed-class F1 {value(frequent,"f1")}. This shows why accuracy alone would conceal failure to identify the positive class.',
        'The sex–area and education plots motivated closer examination and the sex-by-area engineered interaction. EDA charts are unweighted modelling-sample descriptions. The weighted skills-gap tables are a different analysis and use survey weights.',
        'Trace: notebooks/exploratory_analysis.ipynb, src/hunarlens/eda.py, docs/eda_findings.md and reports/figures/.'
    ])
    add(guide, '4. Train, validation and test data', [
        ('h2', 'Why three roles?'),
        'Training data fit the model and support grouped cross-validation. Validation data compare selected models, inspect calibration, choose thresholds and create explanations. Test data estimate performance after these decisions are frozen. Reusing test outcomes to change the model would turn test into another development set.',
        f'The saved split has train {int(train["rows"]):,} rows ({int(train["positives"]):,} positives; {pct(train,"prevalence")}), validation {int(val["rows"]):,} rows ({int(val["positives"]):,}; {pct(val,"prevalence")}), and test {int(test["rows"]):,} rows ({int(test["positives"]):,}; {pct(test,"prevalence")}). Exact fractions are approximate because entire households stay together.',
        ('h2', 'Why group by household?'),
        'Young people in the same household share context and may be similar. A row-level random split could put relatives in both training and test, producing an overly optimistic estimate of performance for unseen households. The group key combines the recorded processing code, enumeration block and household number. It is used for splitting, never as a predictor.',
        'The implementation uses StratifiedGroupKFold with 20 folds, shuffling and seed 42. Fourteen folds form training, three validation and three test. Stratification seeks similar class proportions; grouping takes priority over exact percentages. The assignment file carries a hash of the source dataset so a changed row order is detected.',
        'Trace: src/hunarlens/splits.py, scripts/make_splits.py, reports/tables/split_summary.csv and tests/test_pipeline_and_splits.py.'
    ])
    add(guide, '5. Cross-validation and model selection', [
        ('h2', 'The five-fold idea'),
        'Grouped cross-validation partitions the training households into five folds. For each run, the pipeline fits on four folds and scores the fifth; each fold takes a turn as holdout. A mean and standard deviation summarise the fold scores. The groups are passed to search.fit so a household cannot straddle the fitting and holdout parts of a fold.',
        'All learned preprocessing must be fitted within each fold. Computing an imputation median, a clipping percentile or category frequencies on the entire dataset before cross-validation leaks information from the holdout. A single sklearn Pipeline makes the correct fit/transform sequence reproducible.',
        f'The selection score is average precision (AP). The tuned grouped-CV means are logistic regression {value(lr,"cv_ap_mean")}, Random Forest {value(rf,"cv_ap_mean")} and histogram gradient boosting {value(hgb,"cv_ap_mean")}. AP and ROC-AUC are both recorded, but AP is the refit score.',
        'These scores support model selection, not a final performance claim. The validation set is used for thresholds and reported comparison, while the sealed test scores come only after the model and operating points are fixed.',
        'Trace: scripts/compare_models.py, reports/tables/cv_fold_scores.csv and reports/tables/experiments.csv.'
    ])
    add(guide, '6. Feature engineering inside a pipeline', [
        ('h2', 'Raw inputs and engineered inputs'),
        'The 19 allowed raw fields describe a person, their education and training, household roster and broad Census context. Examples include age, sex, education, current enrolment, household size, province and area. The group identifier and outcome-related responses are not part of this feature set.',
        'ApprovedFeatures constructs: an education-code numeric representation alongside the categorical education field; age bands 15–17, 18–20 and 21–24; children under 15 divided by household size; household size clipped at the training 99th percentile; and a sex-by-area interaction. The unchanged raw household-size input is not sent directly to the preprocessor: its clipped version is used.',
        'Why fit the clip? The cutoff is learned from the training fold, then applied unchanged to its holdout and future examples. This prevents a validation or test distribution from choosing the boundary. The ordinal education field is a pragmatic coding representation, not proof that every qualification is evenly spaced or causally ordered.',
        ('h2', 'The pipeline'),
        'build_model_pipeline constructs Pipeline(features, preprocess, model). First, ApprovedFeatures.fit learns the household-size cutoff; transform creates derived columns. Next, a ColumnTransformer sends numeric and categorical columns through separate processing branches. Finally, the fitted estimator receives the transformed matrix.',
        'This design also keeps deployment consistent: the app passes approved raw features to the same saved pipeline, rather than manually recreating training transformations.',
        'Trace: src/hunarlens/features.py and src/hunarlens/pipeline.py.'
    ])
    add(guide, '7. Missing values, scaling and encoding', [
        ('h2', 'Numeric branch'),
        'SimpleImputer(strategy="median") learns medians on the fitting fold and replaces missing numeric values. StandardScaler then learns a mean and standard deviation for each numeric column and applies the same transformation later. Scaling helps models such as logistic regression compare coefficients under regularisation. Tree models are generally less sensitive to monotonic rescaling, but a shared pipeline keeps the comparison consistent.',
        'The current modelling data audit reports no observed missing values in the allowed fields after approved coding. The imputer is still useful for a compatible later input. It is not a justification for treating an unknown survey code as a real category: the questionnaire and coding scheme must be audited first.',
        ('h2', 'Categorical branch'),
        'Categorical missing values use the training-fold most-frequent category. OneHotEncoder turns categories into indicator columns. It uses handle_unknown="ignore" and min_frequency=50: rare categories can be grouped, and an unseen category does not crash the fitted encoder. The app separately validates allowed values so an unknown category is not silently accepted as an estimate.',
        'Alternative approaches include ordinal encoding, explicit missing categories or model-specific native category handling. They need documented assumptions and cross-validation. A categorical numeric code is not automatically a meaningful magnitude.',
        'Trace: src/hunarlens/pipeline.py, src/hunarlens/config.py and src/hunarlens/app_utils.py.'
    ])
    add(guide, '8. Baselines and model families', [
        ('h2', 'Dummy classifiers'),
        'The most-frequent dummy always predicts the majority label; the stratified dummy draws labels according to the fitted class proportions. They provide a reference: a complex model should demonstrate value beyond a simple rule. Their scores are not a substitute for the no-skill precision–recall prevalence line.',
        ('h2', 'Logistic regression'),
        'Logistic regression models log-odds as a linear combination of the transformed inputs and maps them through a sigmoid to a probability. One-hot encoding and feature interactions give it some nonlinear input representations, but its fitted relationship remains linear in those transformed columns. Regularisation constrains coefficient size; C is the inverse regularisation strength in the search.',
        ('h2', 'Random Forest'),
        'A forest averages predictions from many decision trees. Trees make sequences of splits and can learn interactions without specifying their exact mathematical form. Randomness in bootstrap samples and considered features reduces correlation between trees. Deep trees or small leaves can fit training noise, so depth and minimum leaf size are tuned.',
        ('h2', 'Histogram gradient boosting'),
        'Histogram gradient boosting builds an additive ensemble of trees sequentially, improving the loss by fitting corrections to the current model. Histogram bins make split search efficient on numeric representations. Learning rate, leaf count, minimum leaf size and regularisation control flexibility. Unlike a forest, trees are added as a sequence of corrections rather than averaged as mostly independent learners.',
        'Trace: scripts/compare_models.py make_model() and search_space(); the selected estimator is stored in models/final_pipeline.joblib.'
    ])
    add(guide, '9. Tuning, class weights and experiments', [
        ('h2', 'Hyperparameters versus learned parameters'),
        'A hyperparameter is set before fitting, such as tree depth or logistic C. Learned parameters include fitted coefficients, tree splits, imputation medians and encoder categories. Cross-validation compares hyperparameter choices using training folds; it does not guarantee that the chosen setting is globally optimal.',
        'The project compares a dummy, defaults without class weights, defaults with class weights, tuned variants and validation threshold variants. Logistic uses a grid over C and class weight. Random Forest searches tree count, depth, minimum leaf, feature sampling and weight choices. HGB searches learning rate, depth, leaves, minimum leaf, L2 regularisation, iterations and weight choices. Each tree-family random search uses 15 candidates to keep runtime manageable.',
        f'For default HGB, grouped-CV AP is {value(hgb_default,"cv_ap_mean")} without class weights and {value(hgb_weighted,"cv_ap_mean")} with balanced weights. A weight can improve recall at a fixed cutoff while worsening ranking or calibration; one metric alone should not be used to claim universal improvement.',
        'Undersampling the majority class was not included in the final experiment sequence. It could reduce computation or change the loss balance, but would discard majority examples and add design choices. The chosen approach keeps all training examples and sets thresholds on validation.'
    ])
    add(guide, '10. Selection, overfitting and generalisation', [
        ('h2', 'Underfitting and overfitting'),
        'Underfitting occurs when a model cannot represent useful structure; training and held-out performance may both be weak. Overfitting occurs when training performance is much stronger than performance on new data. A train–CV gap is a warning sign, not a complete diagnosis: noise, sample composition and metric variability also matter.',
        f'Random Forest AP is {value(rf_gap,"train_ap")} on training and {value(rf_gap,"cv_ap")} in grouped CV, a gap of {num(rf_gap,"train_ap")-num(rf_gap,"cv_ap"):.3f}. HGB gives {value(hgb_gap,"train_ap")} and {value(hgb_gap,"cv_ap")}, a gap of {num(hgb_gap,"train_ap")-num(hgb_gap,"cv_ap"):.3f}. These values are not test scores.',
        f'The forest CV AP exceeds HGB by {num(rf,"cv_ap_mean")-num(hgb,"cv_ap_mean"):.4f}, within the pre-agreed 0.01 tie band. The team chose HGB for its smaller gap and deployment properties; the forest was ahead on the reported validation metrics. The final test set was not used to compare the forest and HGB.',
        'The saved grouped learning curve is for Random Forest, the initial CV leader; it is not an HGB learning curve. Learning curves compare held-out performance as the fitting sample grows. A complexity curve compares holdout performance across a chosen complexity parameter.',
        'Trace: reports/tables/generalization_gap.csv, grouped_learning_curve.csv and docs/DECISIONS.md.'
    ])
    add(guide, '11. Final HGB and model persistence', [
        ('h2', 'Saved settings'),
        f'The final model is HistGradientBoostingClassifier with max_iter={params["max_iter"]}, learning_rate={params["learning_rate"]}, max_depth={params["max_depth"]}, max_leaf_nodes={params["max_leaf_nodes"]}, min_samples_leaf={params["min_samples_leaf"]}, l2_regularization={params["l2_regularization"]}, early_stopping={params["early_stopping"]} and class_weight={params["class_weight"]}. The chosen pipeline was fit on the training split only.',
        'A smaller learning rate makes individual boosting updates less aggressive; a limited number of leaves and a minimum leaf size restrict how finely a tree can partition the data. L2 regularisation penalises overly large leaf effects. These controls can reduce overfitting but do not guarantee fairness, calibration or external validity.',
        'Joblib serialises the whole fitted pipeline, including the custom feature transformer, preprocessors and estimator. Metadata records feature names, allowed inputs, thresholds, training reference values and library versions. The app imports the project package before loading the file so the custom transformer can be located. Matching the pinned scikit-learn version is important for reproducibility.',
        'Trace: scripts/save_final_model.py, models/final_pipeline.joblib, models/metadata.json and tests/test_model_freeze.py.'
    ])
    add(guide, '12. Probabilities, calibration and thresholds', [
        ('h2', 'Ranking versus probability calibration'),
        'A model can rank people reasonably well while its numeric probabilities are too high or too low. Calibration asks whether cases assigned a given probability have comparable observed outcome frequencies. A calibration curve compares grouped average predicted probabilities with observed rates; bins with few records are unstable.',
        f'The validation Brier score is {num(raw,"brier"):.6f} for raw HGB and {num(sigmoid,"brier"):.6f} after sigmoid calibration. Brier score is the mean squared difference between predicted probability and binary outcome; smaller is better, but it combines calibration and discrimination. Because the change was tiny and calibration used validation labels, the team retained raw probabilities.',
        ('h2', 'Operating points'),
        f'The stored primary threshold is {num(metrics,"threshold"):.6f} and the screening threshold is {num(screening,"threshold"):.6f}. A score at or above a threshold is flagged. Lowering a threshold usually increases recall and can reduce precision; it changes labels, not the probability ranking or AP.',
        f'The primary rule uses the midpoint of the range of validation thresholds whose F1 is within 0.005 of the maximum. F1 is discontinuous, so this midpoint need not itself lie within the qualifying F1 band: its validation F1 is {value(val_threshold,"f1")}. Both threshold selection and assessment on validation use the same labels and are optimistic.',
        'High and Elevated bands are based on validation score quantiles. These are relative group labels, not guarantees about individuals. Their exact cutoffs remain in metadata; the model and thresholds must not be changed to improve the reported test result.'
    ])
    add(guide, '13. Confusion matrix and classification metrics', [
        ('h2', 'Read the counts before the score'),
        f'At the frozen primary threshold, the test confusion counts are: true positives {metrics["tp"]}, false positives {metrics["fp"]}, false negatives {metrics["fn"]}, true negatives {metrics["tn"]}. True positive means an unemployed record was flagged; false positive means an employed record was flagged.',
        f'Precision = TP / (TP + FP) = {metrics["tp"]} / ({metrics["tp"]} + {metrics["fp"]}) = {value(metrics,"precision")}. Among flagged records, about {pct(metrics,"precision")} are unemployed. The remainder are false positives in this test sample.',
        f'Recall = TP / (TP + FN) = {metrics["tp"]} / ({metrics["tp"]} + {metrics["fn"]}) = {value(metrics,"recall")}. The model flags about {pct(metrics,"recall")} of the unemployed observations and misses the others.',
        f'F1 = 2 × precision × recall / (precision + recall) = {value(metrics,"f1")}. F1 is a harmonic mean: a very low precision or recall pulls it down. Accuracy = (TP + TN) / all = {value(metrics,"accuracy")}, but majority-class accuracy is not the project’s selection criterion.',
        f'At the secondary threshold, recall is {value(screening,"recall")} and precision is {value(screening,"precision")}; it detects {screening["tp"]} unemployed records while flagging {screening["fp"]} employed records. This is a trade-off, not a recommendation to use individual flags.'
    ])
    add(guide, '14. PR-AUC, ROC-AUC and lift', [
        ('h2', 'Average precision and the PR curve'),
        f'Precision–recall curves show precision and recall as the threshold moves. Average precision (AP) summarises the curve using changes in recall as weights. The test HGB AP is {value(metrics,"pr_auc")}, compared with test prevalence {value(metrics,"prevalence")} and stratified Dummy AP {value(dummy,"pr_auc")}. For a no-skill reference, prevalence is the horizontal PR line.',
        'AP is useful with a rare positive class because precision directly exposes false-positive burden. It depends on prevalence, so AP values from populations with different positive-class rates must be compared carefully. AP summarises a ranking over thresholds and is not the F1 at the chosen threshold.',
        ('h2', 'ROC-AUC'),
        f'ROC curves compare true-positive rate against false-positive rate over thresholds. ROC-AUC has the interpretation that a randomly chosen positive is ranked above a randomly chosen negative, with ties handled appropriately. HGB test ROC-AUC is {value(metrics,"roc_auc")}; the dummy is {value(dummy,"roc_auc")}. ROC-AUC alone does not state the precision a user will experience.',
        ('h2', 'Lift'),
        f'Top-10% lift compares the positive share among the highest-scored decile with overall prevalence. HGB lift is {value(metrics,"lift_10")} on test; the stratified Dummy is {value(dummy,"lift_10")}. Lift is a concentration measure, not the probability that a flagged person is unemployed and not a causal effect.'
    ])
    add(guide, '15. Bootstrap uncertainty and subgroup fairness', [
        ('h2', 'Cluster bootstrap'),
        f'The test evaluation resamples households with replacement for 1,000 repetitions and computes percentile intervals. HGB primary F1 is {value(metrics,"f1")} with a 95% interval {float(f1ci["lower_95"]):.3f}–{float(f1ci["upper_95"]):.3f}. The interval describes variation under this resampling procedure for the evaluated sample; it does not include all retraining, design or future-population uncertainty.',
        'Resampling individual records would ignore dependence between members of a household. The survey-oriented skills analysis instead resamples PSUs and uses survey weights, but it still does not capture the full stratified survey design. These two bootstrap procedures answer different questions.',
        ('h2', 'Disaggregated performance'),
        f'At the primary threshold, recall for the no-formal-education group is {pct(no_formal,"recall")} with {no_formal["positives"]} unemployed observations; intermediate-education recall is {pct(intermediate,"recall")} with {intermediate["positives"]} positives. A common threshold can produce different group recalls when score distributions differ.',
        'Sex is a model input, and geography and education may be correlated with sensitive attributes. Group metrics are descriptive and some groups have too few positives for reliable comparisons. Fairness cannot be reduced to one overall F1 or fixed simply by deleting one column.',
        'Trace: reports/tables/test_bootstrap_ci.csv, test_subgroups.csv and scripts/evaluate_on_test_set.py. Do not rerun test scoring.'
    ])
    add(guide, '16. Explainable ML and ablation', [
        ('h2', 'Permutation importance'),
        'Permutation importance measures how much a model’s score changes when a feature is shuffled on validation. The original fitted pipeline scores raw columns before and after shuffling; it is not refit for each permutation. A larger mean AP drop indicates greater reliance under this perturbation. Repeats show shuffle variability, not a causal confidence interval.',
        f'The saved Education group has mean AP importance {value(education,"importance_mean")}; Enrolment has {value(enrolment,"importance_mean")}. Correlated variables can share or mask importance. The grouped method applies one shared row permutation to all columns in a group, preserving their internal combinations.',
        ('h2', 'Ablation versus permutation'),
        f'An ablation retrains without a feature or group under the same evaluation procedure. Without current enrolment, HGB grouped-CV AP is {value(no_enrolment,"cv_ap_mean")}, versus {value(hgb,"cv_ap_mean")} with all features. Permutation instead disrupts information after fitting. The approaches answer related but different questions.',
        ('h2', 'Partial dependence and local what-if'),
        'Partial-dependence-style plots replace one value across validation rows and average predictions. Local what-if compares one profile with a version in which a field is replaced by a training median or mode. These substitutions can create uncommon combinations. Their output is a change in the model score, not evidence that changing the person would change their employment outcome.',
        'Enrolment associations are affected by conditioning on labour-force membership: many students outside the labour force are absent from the modelling sample. Interpret all explanations as associations represented by the fitted model.'
    ])
    add(guide, '17. Skills analysis versus supervised modelling', [
        'The skills-gap extension is descriptive, not a second classifier. It uses education and vocational-training attainment as proxies for skills and compares employed and unemployed youth, occupational education modes and outcomes by education. The LFS does not directly measure employer vacancies or a person’s full capabilities.',
        'Weighted population shares and PSU-cluster bootstrap intervals describe survey patterns. For statistical mismatch, a reference population’s modal education band is computed within occupation; a youth’s band can be above, at or below it. Modes are re-estimated within bootstrap replicates. A normative mapping and alternative reference populations give sensitivity analyses, not interchangeable definitions.',
        'This distinction matters in a machine-learning viva: a weighted descriptive association is not a feature-importance value, a model-estimated profile substitution is not a causal treatment effect, and the model’s unweighted test metrics are not an official population unemployment rate.',
        'Trace: src/hunarlens/skills.py, scripts/analyze_skills_gap.py, docs/skills_gap_methods.md and reports/tables/skills_*.csv.'
    ])
    add(guide, '18. Deployment, tests and reproducibility', [
        'The Streamlit app loads the frozen joblib pipeline, metadata and tracked aggregate artefacts. User selections are translated into the approved input schema; household and literacy rules reject invalid combinations, while rare combinations produce warnings. Inputs are not stored. The browser interface and native fallback use the same analytical artefacts.',
        'Tests cover the allowlist, grouped splits, binary label, train-only fitting, model loading in a fresh process, metadata compatibility, app/pipeline prediction parity, privacy, dashboard rendering and skills-analysis suppression. Tests are evidence about specified behaviours; passing them does not prove absence of every bug or that the model will work in a new population.',
        'The frozen model hash detects a file change, not statistical quality. The previously saved individual test-prediction file was removed during an earlier cleanup; aggregate test results remain. Do not regenerate predictions, tune thresholds, or evaluate other models on test during a viva or report review.',
        'Use python -m pytest -q for the suite and streamlit run app/streamlit_app.py to run the app. See README.md for setup, the native fallback and prerequisites.'
    ])
    add(guide, '19. Viva questions with model answers', [
        ('h2', 'Q1. What is X and what is y?'),
        'X is the approved collection of demographic, education, household and Census input fields. y is the binary unemployment label for labour-force youth. Household IDs are used for grouping and are excluded from X.',
        ('h2', 'Q2. Why is the split grouped and stratified?'),
        'Grouping keeps household members together. Stratification attempts to preserve the positive-class proportion. The exact row percentages may vary because whole groups must stay intact.',
        ('h2', 'Q3. What fits inside cross-validation?'),
        'The feature transformer, imputation, scaling, encoding and estimator fit separately on each training fold. The held-out fold receives transform and predict only.',
        ('h2', 'Q4. Why not choose accuracy?'),
        'Unemployment is the minority class. A majority-only classifier can obtain high accuracy while failing to identify unemployed people; precision, recall, F1, AP and baseline comparisons expose this.',
        ('h2', 'Q5. Why did the team choose HGB over the forest?'),
        'The forest had higher CV AP, but the advantage was inside the agreed tie margin. HGB had a smaller train–CV gap and practical deployment advantages. This was a documented choice, not an HGB victory on every validation metric.',
        ('h2', 'Q6. What is the difference between AP and F1?'),
        'AP summarises ranking across thresholds. F1 combines precision and recall at one threshold. Adjusting the threshold changes F1 but does not change the underlying ranking.',
        ('h2', 'Q7. Is the primary cutoff exactly the best validation F1?'),
        'No. It is a midpoint selected from a near-optimal threshold range. Since F1 changes discontinuously, that midpoint is not guaranteed to achieve the original maximum or remain within the requested tolerance.',
        ('h2', 'Q8. What does a permutation-importance score prove?'),
        'It shows how much the fitted model’s evaluation score depends on an input under a specified shuffling experiment. It does not establish that changing that feature causes unemployment.',
        ('h2', 'Q9. What are the main limitations?'),
        'Unweighted modelling, selection into the labour force, unverifiable future-starter timing, coarse geographic context, subgroup differences, non-causal explanations and lack of independent external validation.',
        ('h2', 'Q10. Can the app decide who gets a job or support?'),
        'No. It is a research and educational tool with substantial false positives and false negatives. The output is not a decision about an individual.'
    ])
    guide.section('Illustrations')
    guide.illustration('reports/figures/report_architecture.png', 'The project’s modelling and survey-analysis paths')
    guide.illustration('reports/figures/class_balance.png', 'Class balance in the modelling dataset')
    guide.illustration('reports/figures/test_confusion_matrix.png', 'Saved test confusion matrix')
    guide.illustration('reports/figures/test_pr_curve_wide.png', 'Saved test precision–recall curve')
    guide.illustration('reports/figures/grouped_permutation_importance.png', 'Validation grouped permutation importance')
    guide.flush()
    layout.OUTPUT = ROOT / 'HunarLens_Machine_Learning_Concepts_Guide.pdf'
    layout.render(guide, subtitle='Machine learning concepts and implementation',
                  strapline='Concepts  ·  Project code  ·  Results  ·  Viva questions')


if __name__ == '__main__':
    build()
