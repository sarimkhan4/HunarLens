# exploratory analysis EDA findings

All results below use unweighted analysis records. The dataset construction weighted youth unemployment rate was about 12.8% after the approved future-starter rule (the earlier active-search-only estimate was about 12.6%).

## Class Balance

There are 3,383 unemployed and 23,270 employed records; prevalence is 12.69%.
Figure: `reports/figures/class_balance.png`.

## Age By Class

Age shares are shown within each class, so the different class sizes do not dominate the comparison. Survey ages show visible peaks.
Figure: `reports/figures/age_by_class.png`.

## Rate Sex Area

The four area and sex groups range from 11.1% to 24.5%; the chart includes group counts.
Figure: `reports/figures/rate_sex_area.png`.

## Rate By Province

Rates range from 10.8% to 15.7% across observed codes; labels show group sizes.
Figure: `reports/figures/rate_by_province.png`.

## Rate By Education Level

Rates range from 5.3% to 33.3% across observed codes; labels show group sizes.
Figure: `reports/figures/rate_by_education_level.png`.

## Rate By Has Training

Rates range from 6.9% to 13.9% across observed codes; labels show group sizes.
Figure: `reports/figures/rate_by_has_training.png`.

## Missing Values

The largest observed feature missing rate is 0.00%; unknown source coding may not be reflected in this number.
Figure: `reports/figures/missing_values.png`.

## Box Age

The observed range is 15.00 to 24.00; boxplot points are statistical outliers, not necessarily errors.
Figure: `reports/figures/box_age.png`.

## Box Household Size

The observed range is 1.00 to 54.00; boxplot points are statistical outliers, not necessarily errors.
Figure: `reports/figures/box_household_size.png`.

## Box Children Under 15

The observed range is 0.00 to 23.00; boxplot points are statistical outliers, not necessarily errors.
Figure: `reports/figures/box_children_under_15.png`.

## Box Census Density

The observed range is 42.90 to 621.83; boxplot points are statistical outliers, not necessarily errors.
Figure: `reports/figures/box_census_density.png`.

## Box Census Urban Proportion

The observed range is 0.15 to 0.54; boxplot points are statistical outliers, not necessarily errors.
Figure: `reports/figures/box_census_urban_proportion.png`.

## Box Census Household Size

The observed range is 5.40 to 7.00; boxplot points are statistical outliers, not necessarily errors.
Figure: `reports/figures/box_census_household_size.png`.

## Numeric Correlations

The heatmap shows Pearson associations among numeric fields and the target; correlations do not establish causation.
Figure: `reports/figures/numeric_correlations.png`.

## Household Size Distribution

The maximum observed value is 54; household identifiers are used only to count group sizes.
Figure: `reports/figures/household_size_distribution.png`.

## Youth Per Household

The maximum observed value is 10; household identifiers are used only to count group sizes.
Figure: `reports/figures/youth_per_household.png`.

## Category and missing-value review

All 19 features have zero observed NaNs. The value audit is in `reports/tables/feature_value_counts_top15.csv`; all observed feature values below 50 records, including discrete numeric values, are in `reports/tables/rare_categories.csv`. Counts are unweighted and small groups should be interpreted cautiously.

Education code 1 denotes no formal education; current enrolment code 1 means not enrolled; training code 0 means no training. These are substantive responses, not missing values. No 97, 98 or 99 codes are retained in the observed features.

## Proposed engineering for team approval

- Consider treating education codes as ordered only after confirming the degree categories form a meaningful order.
- Consider log-transforming Census density inside the model pipeline; density differs widely across provinces.
- Consider children under 15 per household member inside the pipeline, with a safe denominator.
- Consider an age band inside the pipeline if the team approves losing age detail.

These are proposals, not implemented features; comparisons must respect grouped splits and validation-only model selection.
