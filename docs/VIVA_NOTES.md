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
