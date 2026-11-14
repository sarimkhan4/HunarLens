# Stage 1 proposal for human review

## 2026-11-15: approved future-starter approximation

The [ILO derivation guide for the 19th ICLS, paragraphs 47–48](https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf) includes available future starters who did not search because they had arranged to start a job within a “short subsequent period”, “generally not greater than three months”. The PBS questionnaire asks: “What is the main reason why (Name) did not try to find a paid job or start a business in the last 4 weeks?” Option 01 is “Already has a job or business to start in the near future”.

The questionnaire and Stata variable labels were inspected for a job-start date or duration; no such field was identified. `S5C6` concerns returning to an existing job and `S9C6` asks availability within two weeks, neither establishes the future job's start date. Thus a three-month limit cannot be applied or compared using an observed start date. The approved `S9C5=1` rule uses “near future” as a proxy, and may include starts outside the ILO's generally three-month reference. Published totals provide corroboration, not proof that every selected individual satisfies it. The earlier active-search-only rule below is superseded.

The team approved Gate G1 on 2026-11-15 subject to the Stage 2 reproduction test. The user subsequently chose questionnaire coding for `S5C5` and the original three-field group key. The latest reproduction failed the revised tolerance; no analysis dataset or grouping rule has been implemented.

## Previous reproduction (before future starters were approved)

The team chose questionnaire codes for `S5C5`, citing median ages 21 for code 1 and 51 for code 2. This pattern is consistent with, but does not prove, the questionnaire mapping. Code 1 is not treated as an existing job; code 14 and missing `S5C5` where `S5C4=1` are excluded. The earlier 67-record exclusion below is superseded.

The [PBS annual report](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf), chapter 3, describes the unemployed as “without work, currently available to work, and taking active steps to find/seek work.” Its chapter 9 also specifies job search in the previous four weeks and availability within two weeks. The report text located does not describe a future-starter exception; the provisional rule therefore retains the active-search requirement rather than assuming such an exception. Questionnaire `S9C5=1` identifies people who have a job or business to start soon, but does not on its own establish their inclusion in PBS unemployment.

The current provisional totals are 77,233,161 employed, 5,800,161 unemployed, and 83,033,322 in the labour force, giving 6.985%. The requested acceptance bounds are 5.85–5.95 million and 7.05–7.15%; both fail. The report's 19th ICLS youth comparisons and rural/urban rates appear alongside provisional estimates in `reports/tables/label_reproduction.csv` (PBS counts are blank where no comparable figure was located). The future-starter diagnostic and grouped route crosstabs are also generated in `reports/tables/`.

The approved group key is `PCode + EBCode + HHNo`, despite its observed maximum of 54 roster records. The team explicitly rejected the earlier fallback; potential cross-quarter household reuse remains a limitation to assess. `S4C11` is approved only as an ever/current-versus-never collapse. `S4C12` is excluded unless its categories can be verified against official documentation; the available two-page sampling coding scheme does not contain Annex C training categories.

The revised rule includes `S9C1=2`, `S9C5=1`, `S9C6=1` when not employed. The estimate is 5,896,967 unemployed, labour force 83,130,128 and rate 7.094%, within the team-approved reproduction bounds. Without that addition the corresponding unemployed estimate is 5,800,161. The data do not provide a verified start-date variable, so counts with and without the ILO's generally three-month limit cannot be determined. Among 50 `S5C4=1`, `S5C5=1` records (weighted 41,977), none is classified employed; 27 (weighted 21,809) are classified unemployed and 23 are outside the labour force under the approved rule.

## Feature coding and missingness

Questionnaire codes `S4C81` and `S4C82` are 1 yes, 2 no; `S4C81` has a malformed Stata value-label entry, so the questionnaire codes are used. Sex permits 1–2, marital status 1–4, relationship 1–9, and education and enrolment 1–16; values outside those ranges become missing. `S4C11` values 1–3 map to yes and 4 to no; other values become missing. Original Stata system missing values are read as missing. The available PBS sampling coding scheme does not document per-feature missing codes, so special missing-code assumptions are not made. Census values and full-roster household counts are derived from source records. Observed feature missing rates are generated in `reports/tables/feature_missingness.csv`.

## Historical: discrepancy discovered during Stage 2

In the [PBS questionnaire](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Questionnaire-of-LFS-2024-25-Final.pdf), question 5.5 code 1 is “Waiting to start new job or business” and code 2 is “Illness or injury”. The downloaded Stata file labels code 1 as illness or injury and code 2 as shift work/flexitime. Its label for code 14 is absent, although 17 records have that numeric code; 50 records have code 1. The dataset alone does not establish whether the numeric values follow the questionnaire or the attached labels. The file also contains 327 zero values in `S5C5` where `S5C4` is missing, so zero must not be assumed to be a valid absence reason without documentation.

The questionnaire lists 15 reasons; the Stata file has 14 labels (1–13 and 15). Labels 1–13 correspond to questionnaire items 2–14; Stata label 15 corresponds to questionnaire item 15. The female-share check is inconclusive: code 4 (maternity under Stata labels) has one female and three male records, while code 5 (maternity under questionnaire labels) has no records. The fallback removes 67 `S5C4=1` records coded 1 or 14, recorded in the row waterfall. It does not establish the true mapping for the other codes.

The questionnaire asks whether an absent worker will return within three months and whether they continue to receive income. It routes a yes answer on either relevant question to the employment section. The annual report text searched did not state the detailed absence rule, so an exact report quotation cannot be supplied. The provisional check follows these questionnaire routes; it does not establish that this is PBS's complete production algorithm.

PBS's published 19th ICLS population covers ages 10 and over. The provisional weighted check estimates 83.013 million in the labour force and 5.780 million unemployed (6.962%), against the rounded report values 83.1 million, 5.9 million and 7.1%. The unemployed total differs by 2.038%, narrowly outside the required 2% tolerance. The gate therefore fails; do not create the youth dataset from this provisional rule.

Among age-10+ records outside the 67 exclusions, 129 report no search, a job to start in the near future (`S9C5=1`), and availability; 65 are aged 15–24. These are potential future starters, not confirmed additions to the PBS unemployment definition. They are not included in the provisional result. The annual report's unemployment description mentions search and availability but did not resolve the future-starter exception.

Question 4.11 asks whether the person has ever completed or is currently receiving technical, vocational or educational training. Its response labels are 1 during a job, 2 before a job, 3 currently receiving, and 4 not received/receiving. The user has authorized a collapsed ever/current training indicator with timing discarded, but it has not been implemented while the reproduction gate fails. Question 4.12 asks for type of training and refers to Annex C; the Stata file has no attached value labels. The question itself does not mention a job or employer, but its category descriptions must be checked before inclusion. Question 4.13 records training duration in weeks, without Stata value labels; 4.14 asks for the provider, coded 1 public technical/vocational institute, 2 private institute, 3 informal apprentice. The user has forbidden both fields. None has been added to `config.FEATURES`.

## Label evidence

The Stata labels identify `S5C1` (work for pay), `S5C2` (business or farm), `S5C3` (family farm/business help), `S5C4` (job or business while absent), `S5C5`–`S5C7` (absence details), `S5C8`–`S5C10` (agricultural work and intended use), `S9C1` (job search in the last four weeks), and `S9C6` (availability within two weeks). Stata value labels for `S5C1`–`S5C4`, `S9C1`, and `S9C6` say 1 = yes and 2 = no. Questionnaire skips, missing values, exceptions for future starters, the headline framework, and the full employed classification remain unverified. These fields are forbidden predictors.

The intended population is age 15–24 (`S4C6`), employed or unemployed under the team-approved PBS headline rule. Do not infer the exact rule from field labels alone. Compare resulting weighted estimates with PBS published totals in Stage 2 after approval.

## Grouping and geographic join evidence

`PCode` is labelled processing code; `EBCode` is labelled block; `HHNo` is present without a Stata variable label. PBS describes a 10-digit code with PSU and household positions, but the document has an inconsistent quarter-position description. Verify actual formatting, uniqueness and repeats across quarters before approving any combination; do not use identifiers as features.

`Province` and `Region` exist; `S4C16` is **previous** district, not current district. The coding scheme says processing-code strata can refer to divisions or districts, which does not establish a consistent current-district field. A province × urban/rural join is a provisional fallback pending verification of `PCode` and Census workbook geography. No join has been built or approved.

## Candidate predictor review

The table below records the Stage 1 assessments that preceded the team's conditional Gate G1 approval. The approved list still requires the explicit exclusions and verification recorded above. Census candidates must be constructed from non-outcome aggregate tables only.

| Field | Assessment | Reason |
|---|---|---|
| `S4C6` | ALLOWED candidate | Age; defines the target population but is not employment status. |
| `S4C5`, `S4C7` | ALLOWED candidates | Sex and marital status. |
| `S4C3` | ALLOWED candidate | Relationship to household head. |
| `S4C82`, `S4C9` | ALLOWED candidates | Writing ability and education level. |
| `Province`, `Region` | ALLOWED candidates | Province and rural/urban area. |
| `S4C81` | UNSURE | Literacy label appears malformed in the Stata value labels; verify questionnaire and codes. |
| `S4C10` | UNSURE | Current enrolment may relate to present activity and must be reviewed. |
| `S4C11`–`S4C14` | UNSURE | Training timing includes training during a job; responses may reveal employment. |
| `S4C15`–`S4C17` | UNSURE | Residence history and routing need review; `S4C16` is previous district. |
| `S4C18` | FORBIDDEN | Migration reasons include job search, finding work and job transfer. |
| `S5C1`–`S10C10_14b` | FORBIDDEN | Employment, search, availability, earnings or work/activity questions can reveal the label. |
| `PCode`, `EBCode`, `HHNo`, `SNo`, `Weights`, `Quarter`, `Fstatus` | FORBIDDEN | Identifiers, survey design, or unverified administrative status. |
| `S4C2` | FORBIDDEN | Household member name field. |
| Census density, urban proportion, average household size | UNSURE | Confirm geographic alignment and absence of outcome-derived measures. |

The candidate list does not establish 15 approved raw predictors. Household size must be investigated without exposing identifiers.
