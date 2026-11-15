# Viva notes

## Stage 0

**What does the placeholder app do?** It displays the project name and a coming-soon message so the deployment path can be checked early.

**Why are the feature lists empty?** The team must inspect the real data and approve a safe allowlist before any predictors are chosen.

**Why keep raw data out of Git?** Survey microdata may have privacy or redistribution restrictions; its licence must be checked before sharing.

**Why pin dependencies and use Python 3.12?** A consistent environment makes local runs and the eventual cloud deployment easier to reproduce.

## Stage 1

**Why discover files from PBS landing pages?** Links can change, and discovery ties downloads to the official source.

**What does a SHA-256 hash do?** It detects file changes; it does not prove the source is correct.

**Why not use `S4C16` as the current district?** Its Stata label describes the previous district of residence.

**Why is training not automatically a safe feature?** `S4C11` distinguishes training received during a job, which may reveal employment status.

**Why is the household rule still pending?** The identifier structure and repeats must be checked and approved before grouping.

## Stage 2 reproduction check

**Why compare the weighted totals with PBS?** It checks whether the proposed classification and survey weights approximately reproduce the published population estimates.

**Why did the sex check not resolve the absence codes?** The candidate maternity categories had too few or no female observations to establish either coding scheme.

**Why remove 67 records?** The team specified that fallback for the two ambiguous absence codes if the check was inconclusive; the waterfall records it.

**Why was the youth dataset initially delayed?** The earlier provisional unemployed estimate missed the team's tolerance, so the team reviewed the future-starter rule before continuing.

## Stage 2 completed dataset

**Why count the full roster before selecting youth?** Otherwise children and older household heads would disappear from household summaries.

**Why are future starters included?** The ILO standard includes qualifying available people with an arranged job, even without a recent search. Our survey lacks a verified start date, so the short-period condition cannot be checked.

**Why is Census density not yet logged?** The eventual modelling pipeline must perform transformations; the dataset retains density in its source units.

**How are identifiers protected?** Raw identifiers are used only to calculate an integer group and household summaries; they are not included in the output table, which is ignored by Git.

## Stage 3 EDA

**Why use unweighted counts here?** These plots describe the records that later models will see; survey-weighted population estimates answer a different question.

**Does a low count in an education category make its rate reliable?** No. A few people can make its percentage change sharply, so the chart shows sample sizes.

**Why investigate household sizes as high as 54?** The group key could combine records across survey periods; an extreme size is a reason to inspect grouping, not proof of an error.

**What does a correlation heatmap prove?** It shows linear associations in these data; it does not establish causation or feature importance.

**Why compare models with and without Census fields?** The fields repeat information already determined by province or province and area, so an ablation can show whether they change validation performance.

## Stage 4 pipeline and baseline

**Why group by household?** Similar people in the same household could make validation artificially optimistic if their records appeared on both sides.

**Where is the household-size clipping limit learned?** The pipeline computes its 99th percentile on the rows passed to `fit`, so each cross-validation fold learns its own limit.

**Why keep both numeric and categorical education?** Numeric coding gives a simple ordered signal, while the categorical version allows subject-specific differences; the ordering is an assumption, not a fact about all degree subjects.

**What does the single-feature scan prove?** It is a warning for unusually strong predictors, not proof that the entire feature set is free of leakage.

**Why compare the dummy models?** They show what a simple non-informative strategy achieves on the same validation data and prevalence.

## Stage 5 model experiments

**Why tune with grouped cross-validation on training data?** It keeps households apart in every fold and preserves validation data for a separate comparison.

**Why is Random Forest the candidate leader?** It has the highest mean grouped CV average precision; validation results did not determine the ranking.

**What does its training-to-CV gap suggest?** The forest fits the training records more strongly than unseen households, so overfitting is a concern.

**Why is the threshold-optimized validation F1 optimistic?** The same validation labels were used to select the threshold and report its F1.

**Why omit random undersampling?** The team chose class weights and threshold tuning for imbalance experiments without adding another dependency.

## Stage 6: calibration and freeze

**Why choose HGB when Random Forest scored higher?** The team used the approved 0.01 CV tie band and preferred HGB's smaller overfitting gap, file size and prediction time.

**Why keep raw probabilities?** Sigmoid calibration barely changed the validation Brier score, so it did not meet the stated improvement rule.

**Why are the validation threshold scores optimistic?** The same labels choose the thresholds and measure their scores; final performance needs the still-sealed test data.

**Why can the midpoint have F1 below the near-optimal range?** F1 changes discontinuously, so the qualifying thresholds can have gaps even when their endpoints are near-optimal.

**What do the risk bands mean?** They divide validation scores at their 70th and 90th percentiles; they are relative rankings and do not establish individual causation.

## Stage 7: explanations

**What does permutation importance measure?** The decrease in validation average precision after values are shuffled; it measures reliance of this fitted model, not causation.

**Why shuffle education fields together?** Education, reading and writing are correlated, so separate shuffles can hide or split their shared contribution.

**What do the error bars mean?** They show variation across 20 random permutations, not a confidence interval or evidence that small differences are meaningful.

**What does a local what-if compare?** It replaces one input with its training median or mode and reports the change in predicted probability, leaving the other inputs fixed.

**Why discuss sex and fairness?** Sex is an input to this model, and predictive importance alone cannot establish whether its errors and use are fair across groups.

## Stage 8: final test evaluation

**Why verify the model hash first?** It checks that the model file is the one approved before opening the test split.

**Why save test probabilities?** Every later table and figure can use the same one-time predictions without scoring the holdout again.

**What does grouped bootstrap resample?** Whole households are sampled with replacement, keeping members of a sampled household together.

**Why compare with the Dummy and prevalence?** They show how much predictive ranking and classification improve over a non-informative reference.

**Why inspect subgroups?** Overall performance can hide unequal recall and precision; small positive counts make subgroup estimates less stable.

## Stage 9: Streamlit app

**Why does the app pass raw inputs to the saved pipeline?** The same fitted imputation, feature construction and encoding are used in training, testing and the app.

**Why is a household head's information filled automatically?** The roster defines head characteristics from that same person, so conflicting answers would be inconsistent.

**Why show the sample base rate beside the estimate?** It gives context for a probability when unemployment is a minority outcome in the training sample.

**What does the local what-if chart show?** It compares the prediction with one field replaced by a typical training value; it describes the model's response, not a causal effect.

**Why is the app not an individual decision tool?** The survey sample, unweighted model, possible subgroup differences and uncertainty limit what a single estimate can support.

## Stage 9b: live interface

**What does the risk ruler compare?** It locates a score among aggregate validation predictions for youth in the labour force.

**Why use a Streamlit fragment?** An input change can update the result area without rerunning the Insights and About tabs.

**Do interactive charts refit the model?** No. They use the same frozen pipeline and approved input checks to compare predictions.

**Why can a rare-combination warning appear?** The training split contained fewer than 20 rows for at least one relevant age and education or enrolment combination.
## Prototype-inspired dashboard

**Why are the survey rates and model scores shown separately?** PBS rates use survey weights, while the saved model evaluation uses unweighted records; they describe different quantities.

**Does the profile explorer use the HTML prototype's formula?** No. The explorer validates the inputs and calls the same frozen pipeline as before.

**Why is the survey download safe to share?** It contains aggregate rates only, not information entered into the profile explorer.
