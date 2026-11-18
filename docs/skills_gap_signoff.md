# Skills-gap sign-off — stopped before S3

**Status: not ready for approval.** S2's generated comparisons passed, but S3
was stopped at the requested uncovered-definition condition. There are no S3
headline findings or confidence intervals to approve.

The team approved one-digit occupation grouping, the stated mismatch norms,
the approximate NEET definition, and the absence exclusions. The audit records
the questionnaire/Stata evidence and unresolved source limitations in
[`skills_gap_data_audit.md`](skills_gap_data_audit.md). Optional industry,
detailed field of study and unemployment-barrier lenses are excluded for the
reasons in [`DECISIONS.md`](DECISIONS.md).

The full [reproduction table](../reports/tables/skills_reproduction.csv)
compares each occupation and education/literacy cell with its PBS source.
The two source tables use different denominators, described in the decisions.
The [row waterfall](../reports/tables/skills_row_waterfall.csv) records the
approved exclusions. All survey output cells follow the disclosure rule.

**Decision required:** for the validation model-shift analysis, specify the
actual `education_level` code to use when moving a profile to a higher band
with multiple categories, or remove that lens. For example, the below-matric
band spans nursery, kindergarten, primary and middle; the degree band includes
several subjects and qualifications. A band alone does not uniquely identify a
valid input to the frozen model.
