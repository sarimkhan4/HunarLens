# Skills-gap analysis summary

**Status:** Last recorded full pytest run: 72 passed, 0 failed, 0 errors. Evidence: [audit](skills_gap_data_audit.md),
[methods](skills_gap_methods.md), [findings](skills_gap_findings.md) and the linked aggregate tables.

**Decisions:** approved one-digit occupations; armed forces excluded; all-employed, age 25–44, youth-only
and normative comparisons; approximate NEET; approved absence exclusions; frequency-averaged education
scenario and training scenario. Industry, detailed field of study and unemployment barriers are excluded.
The PBS occupation-version discrepancy and bootstrap design are documented in the audit and methods.

| Reproduction comparison | Maximum absolute difference (percentage points) | Status |
|---|---:|---|
| Occupation groups | 0.055 | Pass |
| Education/literacy | 0.032 | Pass |
| Unemployment by education (age 10+) | 0.046 | Pass |

| Indicator | n | Our share (%) | PBS share (%) | Difference (pp) | Status |
|---|---:|---:|---:|---:|---|
| occupation_1 | 2133 | 2.31 | 2.3 | 0.012 | PASS |
| occupation_2 | 5932 | 6.05 | 6.1 | 0.046 | PASS |
| occupation_3 | 4157 | 4.41 | 4.4 | 0.014 | PASS |
| occupation_4 | 1664 | 1.76 | 1.8 | 0.039 | PASS |
| occupation_5 | 16560 | 17.24 | 17.2 | 0.037 | PASS |
| occupation_6 | 30313 | 27.95 | 27.9 | 0.055 | PASS |
| occupation_7 | 12547 | 13.67 | 13.7 | 0.029 | PASS |
| occupation_8 | 8062 | 8.33 | 8.3 | 0.028 | PASS |
| occupation_9 | 18405 | 18.27 | 18.3 | 0.031 | PASS |
| illiterate | 37241 | 15.11 | 15.1 | 0.008 | PASS |
| literate | 62532 | 27.90 | 27.9 | 0.005 | PASS |
| literate_never | 1704 | 0.52 | 0.5 | 0.024 | PASS |
| literate_below_matric | 30131 | 13.53 | 13.5 | 0.025 | PASS |
| literate_matric | 14231 | 6.41 | 6.4 | 0.007 | PASS |
| literate_intermediate | 7943 | 3.57 | 3.6 | 0.032 | PASS |
| literate_degree | 8523 | 3.87 | 3.9 | 0.029 | PASS |
| unemployment_education_no_education | 1740 | 4.65 | 4.7 | 0.046 | PASS |
| unemployment_education_below_matric | 2175 | 6.17 | 6.2 | 0.035 | PASS |
| unemployment_education_matric | 1328 | 8.60 | 8.6 | 0.005 | PASS |
| unemployment_education_intermediate | 1125 | 12.61 | 12.6 | 0.013 | PASS |
| unemployment_education_degree | 680 | 10.94 | 10.9 | 0.038 | PASS |
| unemployment_education_masters_mphil_phd | 374 | 11.72 | 11.7 | 0.022 | PASS |

[Full reproduction table](../reports/tables/skills_reproduction.csv) and
[waterfall](../reports/tables/skills_row_waterfall.csv).

**Occupation modes and reference sample sizes**

| Occupation | All employed mode (n) | Age 25–44 mode (n) | Youth mode (n) |
|---:|---|---|---|
| 1 | Degree or above (2133) | Degree or above (1049) | Below matric (239) |
| 2 | Degree or above (5932) | Degree or above (3209) | Intermediate (1248) |
| 3 | Degree or above (4151) | Degree or above (2212) | Intermediate (710) |
| 4 | Degree or above (1664) | Degree or above (960) | Intermediate (269) |
| 5 | Below matric (16244) | Below matric (7611) | Below matric (4201) |
| 6 | No formal (28878) | No formal (12599) | No formal (6811) |
| 7 | Below matric (12194) | Below matric (5968) | Below matric (3511) |
| 8 | Below matric (7935) | Below matric (4228) | Below matric (1600) |
| 9 | No formal (17987) | No formal (8859) | Below matric (4681) |

**Five headline findings**

- Unemployment by education, from the lowest to the highest band: no formal: 8.2% (n=617; 95% CI 7.3%–9.0%), labour-force n=7094; below matric: 11.4% (n=1080; 95% CI 10.6%–12.2%), labour-force n=9629; matric: 14.8% (n=679; 95% CI 13.7%–16.0%), labour-force n=4574; intermediate: 17.5% (n=664; 95% CI 16.1%–19.1%), labour-force n=3849; degree or above: 22.6% (n=343; 95% CI 20.3%–25.0%), labour-force n=1507.
- Among degree-level labour-force youth (n=1507), employed: groups 1–4: 42.0% (n=624; 95% CI 39.3%–44.7%); employed: groups 5–9: 35.4% (n=540; 95% CI 33.0%–37.9%); unemployed: 22.6% (n=343; 95% CI 20.3%–25.0%).
- Strict above-mode shares across statistical norms: 41.0% (overall; norm=youth; n=23270; 95% CI 31.1%–41.6%) to 46.0% (overall; norm=all_15_plus; n=23270; 95% CI 45.0%–47.2%). Within-one-band matched shares across norms: 75.7% (all_15_plus; n=23270; 95% CI 74.8%–76.5%) to 80.3% (youth; n=23270; 95% CI 79.6%–84.5%). Severe shares, at least two bands above mode, across norms: 17.4% (youth; n=23270; 95% CI 12.9%–17.9%) to 19.8% (all_15_plus; n=23270; 95% CI 19.1%–20.8%). Normative ISCO above-level share: 10.6% (n=2378; 95% CI 10.1%–11.1%) (denominator n=23270). These are different definitions; low-education occupations make above-mode shares large, and this is not a count of wasted degrees.
- The share with training was 8.9 percentage points lower among unemployed than employed youth (n=3383 unemployed, 23270 employed; 95% CI -10.3 to -7.5 percentage points).
- Not employed and not enrolled (approximate NEET) described 29.3% of youth (n=59486; 95% CI 28.7%–29.8%); PBS reported 28.4% for its separate NEET measure (n and CI not reported). The definitions differ because our approximation cannot identify recent training.

**Unemployment by education, sex and area**

| Group | Education band | Labour-force n | Unemployed n | Unemployment rate (95% CI) | Flag |
|---|---|---:|---:|---|---|
| All | No formal | 7094 | 617 | 8.2% (n=617; 95% CI 7.3%–9.0%) | Not flagged |
| All | Below matric | 9629 | 1080 | 11.4% (n=1080; 95% CI 10.6%–12.2%) | Not flagged |
| All | Matric | 4574 | 679 | 14.8% (n=679; 95% CI 13.7%–16.0%) | Not flagged |
| All | Intermediate | 3849 | 664 | 17.5% (n=664; 95% CI 16.1%–19.1%) | Not flagged |
| All | Degree or above | 1507 | 343 | 22.6% (n=343; 95% CI 20.3%–25.0%) | Not flagged |
| Male | No formal | 4669 | 468 | 9.2% (n=468; 95% CI 8.1%–10.3%) | Not flagged |
| Male | Below matric | 8076 | 925 | 11.7% (n=925; 95% CI 10.8%–12.6%) | Not flagged |
| Male | Matric | 3856 | 529 | 13.9% (n=529; 95% CI 12.6%–15.3%) | Not flagged |
| Male | Intermediate | 2916 | 439 | 15.4% (n=439; 95% CI 13.9%–16.9%) | Not flagged |
| Male | Degree or above | 913 | 176 | 18.6% (n=176; 95% CI 15.8%–21.4%) | Not flagged |
| Female | No formal | 2425 | 149 | 6.1% (n=149; 95% CI 4.9%–7.6%) | Not flagged |
| Female | Below matric | 1553 | 155 | 10.1% (n=155; 95% CI 8.5%–11.9%) | Not flagged |
| Female | Matric | 718 | 150 | 19.5% (n=150; 95% CI 16.3%–22.8%) | Not flagged |
| Female | Intermediate | 933 | 225 | 23.5% (n=225; 95% CI 20.3%–26.7%) | Not flagged |
| Female | Degree or above | 594 | 167 | 28.4% (n=167; 95% CI 24.5%–32.0%) | Not flagged |
| Rural | No formal | 5986 | 494 | 7.4% (n=494; 95% CI 6.4%–8.4%) | Not flagged |
| Rural | Below matric | 7212 | 719 | 9.8% (n=719; 95% CI 8.9%–10.6%) | Not flagged |
| Rural | Matric | 3129 | 456 | 14.6% (n=456; 95% CI 13.1%–16.1%) | Not flagged |
| Rural | Intermediate | 2505 | 413 | 17.0% (n=413; 95% CI 15.2%–18.8%) | Not flagged |
| Rural | Degree or above | 837 | 198 | 24.1% (n=198; 95% CI 20.9%–27.2%) | Not flagged |
| Urban | No formal | 1108 | 123 | 11.3% (n=123; 95% CI 8.9%–13.7%) | Not flagged |
| Urban | Below matric | 2417 | 361 | 15.2% (n=361; 95% CI 13.5%–16.9%) | Not flagged |
| Urban | Matric | 1445 | 223 | 15.3% (n=223; 95% CI 13.1%–17.6%) | Not flagged |
| Urban | Intermediate | 1344 | 251 | 18.2% (n=251; 95% CI 15.6%–20.9%) | Not flagged |
| Urban | Degree or above | 670 | 145 | 21.2% (n=145; 95% CI 17.6%–24.6%) | Not flagged |

**Degree-level labour-force outcomes**

| Degree-level labour-force outcome | Share (n; 95% CI) |
|---|---|
| Employed: groups 1–4 | 42.0% (n=624; 95% CI 39.3%–44.7%) |
| Employed: groups 5–9 | 35.4% (n=540; 95% CI 33.0%–37.9%) |
| Unemployed | 22.6% (n=343; 95% CI 20.3%–25.0%) |

**Mismatch definitions and samples**

| Norm | Definition | Denominator n | Share (cell n; 95% CI; bootstrap median and bias) |
|---|---|---:|---|
| all_15_plus | Strict over | 23270 | 46.0% (n=10516; 95% CI 45.0%–47.2%); bootstrap median 46.0%, median minus estimate +0.0 pp |
| all_15_plus | Strict under | 23270 | 16.0% (n=3672; 95% CI 15.0%–16.7%); bootstrap median 16.1%, median minus estimate +0.0 pp |
| all_15_plus | within one band | 23270 | 75.7% (n=17696; 95% CI 74.8%–76.5%); bootstrap median 75.7%, median minus estimate +0.0 pp |
| all_15_plus | two or more bands above | 23270 | 19.8% (n=4545; 95% CI 19.1%–20.8%); bootstrap median 19.8%, median minus estimate +0.0 pp |
| age_25_44 | Strict over | 23270 | 46.0% (n=10516; 95% CI 44.8%–46.9%); bootstrap median 46.0%, median minus estimate +0.0 pp |
| age_25_44 | Strict under | 23270 | 16.0% (n=3672; 95% CI 15.4%–16.8%); bootstrap median 16.1%, median minus estimate +0.0 pp |
| age_25_44 | within one band | 23270 | 75.7% (n=17696; 95% CI 74.8%–76.7%); bootstrap median 75.7%, median minus estimate +0.0 pp |
| age_25_44 | two or more bands above | 23270 | 19.8% (n=4545; 95% CI 18.8%–20.6%); bootstrap median 19.8%, median minus estimate -0.0 pp |
| youth | Strict over | 23270 | 41.0% (n=9364; 95% CI 31.1%–41.6%); bootstrap median 40.6%, median minus estimate -0.4 pp |
| youth | Strict under | 23270 | 18.5% (n=4405; 95% CI 17.9%–28.3%); bootstrap median 18.8%, median minus estimate +0.3 pp |
| youth | within one band | 23270 | 80.3% (n=18741; 95% CI 79.6%–84.5%); bootstrap median 80.4%, median minus estimate +0.1 pp |
| youth | two or more bands above | 23270 | 17.4% (n=3991; 95% CI 12.9%–17.9%); bootstrap median 17.0%, median minus estimate -0.3 pp |
| ISCO | Normative above level | 23270 | 10.6% (n=2378; 95% CI 10.1%–11.1%) |

The age 25–44 reference and all-employed reference have the same occupation modes and identical point
shares; the age 25–44 norm is not an independent sensitivity. Bootstrap ranges can differ.

The youth-only strict estimate is 41.0% (n=23270; 95% CI 31.1%–41.6%; bootstrap median 40.6%, median minus estimate -0.4 percentage points). In the youth reference, occupation groups 1, 6 are mode-sensitive: their modal band changes in more than one tenth of resamples. The resampled modes can change the classification of many workers together. In particular, the agricultural group's youth mode switches from no formal education to below matric in 13.9% of resamples (reference n=6811). That switch moves the comparison threshold upward and can place fewer workers above the mode. This produces a lower tail in the bootstrap distribution, leaving the point estimate near the upper interval endpoint.

**Over-education by occupation**

| Norm | Occupation | Denominator n | Above mode (cell n; bootstrap range or CI; median and bias) | Reliability |
|---|---|---:|---|---|
| all_15_plus | occupation 1 | 239 | — (n=0) | Not flagged |
| all_15_plus | occupation 2 | 1248 | — (n=0) | Not flagged |
| all_15_plus | occupation 3 | 710 | — (n=0) | Not flagged |
| all_15_plus | occupation 4 | 269 | — (n=0) | Not flagged |
| all_15_plus | occupation 5 | 4201 | 46.1% (n=1910; 95% CI 44.2%–48.1%); bootstrap median 46.1%, median minus estimate -0.0 pp | Not flagged |
| all_15_plus | occupation 6 | 6811 | 63.4% (n=4058; 95% CI 61.2%–65.6%); bootstrap median 63.5%, median minus estimate +0.1 pp | Not flagged |
| all_15_plus | occupation 7 | 3511 | 29.0% (n=996; 95% CI 27.2%–31.0%); bootstrap median 29.0%, median minus estimate -0.0 pp | Not flagged |
| all_15_plus | occupation 8 | 1600 | 32.1% (n=514; 95% CI 29.5%–34.8%); bootstrap median 32.0%, median minus estimate -0.1 pp | Not flagged |
| all_15_plus | occupation 9 | 4681 | 66.7% (n=3038; 95% CI 65.0%–68.7%); bootstrap median 66.8%, median minus estimate +0.1 pp | Not flagged |
| age_25_44 | occupation 1 | 239 | — (n=0) | Not flagged |
| age_25_44 | occupation 2 | 1248 | — (n=0) | Not flagged |
| age_25_44 | occupation 3 | 710 | — (n=0) | Not flagged |
| age_25_44 | occupation 4 | 269 | — (n=0) | Not flagged |
| age_25_44 | occupation 5 | 4201 | 46.1% (n=1910; 95% CI 44.2%–48.1%); bootstrap median 46.1%, median minus estimate -0.0 pp | Not flagged |
| age_25_44 | occupation 6 | 6811 | 63.4% (n=4058; 95% CI 61.2%–65.6%); bootstrap median 63.5%, median minus estimate +0.1 pp | Not flagged |
| age_25_44 | occupation 7 | 3511 | 29.0% (n=996; 95% CI 27.2%–31.0%); bootstrap median 29.0%, median minus estimate -0.0 pp | Not flagged |
| age_25_44 | occupation 8 | 1600 | 32.1% (n=514; 95% CI 29.5%–34.8%); bootstrap median 32.0%, median minus estimate -0.1 pp | Not flagged |
| age_25_44 | occupation 9 | 4681 | 66.7% (n=3038; 95% CI 64.5%–68.6%); bootstrap median 66.8%, median minus estimate +0.0 pp | Not flagged |
| youth | occupation 1 | 239 | 61.9% (n=143; mode unstable; 95% bootstrap range 0.0%–63.8%); bootstrap median 37.2%, median minus estimate -24.7 pp | mode unstable |
| youth | occupation 2 | 1248 | 31.3% (n=386; 95% CI 28.3%–34.0%); bootstrap median 31.3%, median minus estimate +0.0 pp | Not flagged |
| youth | occupation 3 | 710 | 18.3% (n=130; 95% CI 15.3%–21.4%); bootstrap median 18.2%, median minus estimate -0.0 pp | Not flagged |
| youth | occupation 4 | 269 | 23.2% (n=60; 95% CI 17.8%–28.4%); bootstrap median 23.3%, median minus estimate +0.1 pp | Not flagged |
| youth | occupation 5 | 4201 | 46.1% (n=1910; 95% CI 44.2%–48.1%); bootstrap median 46.1%, median minus estimate -0.0 pp | Not flagged |
| youth | occupation 6 | 6811 | 63.4% (n=4058; mode unstable; 95% bootstrap range 28.6%–64.7%); bootstrap median 63.1%, median minus estimate -0.3 pp | mode unstable |
| youth | occupation 7 | 3511 | 29.0% (n=996; 95% CI 27.2%–31.0%); bootstrap median 29.0%, median minus estimate -0.0 pp | Not flagged |
| youth | occupation 8 | 1600 | 32.1% (n=514; 95% CI 29.5%–34.8%); bootstrap median 32.0%, median minus estimate -0.1 pp | Not flagged |
| youth | occupation 9 | 4681 | 25.7% (n=1167; 95% CI 24.2%–27.5%); bootstrap median 25.7%, median minus estimate +0.0 pp | Not flagged |
| ISCO | occupation 1 | 239 | — (n=0) | Not flagged |
| ISCO | occupation 2 | 1248 | — (n=0) | Not flagged |
| ISCO | occupation 3 | 710 | — (n=0) | Not flagged |
| ISCO | occupation 4 | 269 | 23.2% (n=60; 95% CI 18.0%–28.4%) | Not flagged |
| ISCO | occupation 5 | 4201 | 4.4% (n=187; 95% CI 3.7%–5.2%) | Not flagged |
| ISCO | occupation 6 | 6811 | 2.5% (n=141; 95% CI 2.1%–3.0%) | Not flagged |
| ISCO | occupation 7 | 3511 | 1.9% (n=66; 95% CI 1.4%–2.4%) | Not flagged |
| ISCO | occupation 8 | 1600 | 2.4% (n=40; 95% CI 1.6%–3.3%) | Not flagged |
| ISCO | occupation 9 | 4681 | 41.5% (n=1884; 95% CI 39.7%–43.4%) | Not flagged |

**Education outcomes**

| Education band | n | Employed: matched | Employed: above mode | Employed: below mode | Unemployed |
|---|---:|---|---|---|---|
| No formal | 7094 | 60.1% (n=4396; 95% CI 58.3%–62.1%); bootstrap median 60.1%, median minus estimate -0.0 pp | — (n=0) | 31.7% (n=2081; 95% CI 30.0%–33.5%); bootstrap median 31.8%, median minus estimate +0.1 pp | 8.2% (n=617; 95% CI 7.3%–9.0%) |
| Below matric | 9629 | 43.6% (n=4062; 95% CI 42.3%–45.2%); bootstrap median 43.6%, median minus estimate +0.0 pp | 41.0% (n=4104; 95% CI 39.5%–42.3%); bootstrap median 40.9%, median minus estimate -0.0 pp | 4.0% (n=383; 95% CI 3.4%–4.5%); bootstrap median 4.0%, median minus estimate -0.0 pp | 11.4% (n=1080; 95% CI 10.6%–12.2%) |
| Matric | 4574 | — (n=0) | 76.3% (n=3500; 95% CI 74.8%–78.3%); bootstrap median 76.3%, median minus estimate -0.0 pp | 8.9% (n=395; 95% CI 7.3%–9.9%); bootstrap median 8.9%, median minus estimate -0.0 pp | 14.8% (n=679; 95% CI 13.7%–16.0%) |
| Intermediate | 3849 | — (n=0) | 60.4% (n=2372; 95% CI 58.5%–63.9%); bootstrap median 60.5%, median minus estimate +0.0 pp | 22.0% (n=813; 95% CI 19.6%–23.6%); bootstrap median 22.0%, median minus estimate -0.0 pp | 17.5% (n=664; 95% CI 16.1%–19.1%) |
| Degree or above | 1507 | 42.0% (n=624; 95% CI 37.5%–44.7%); bootstrap median 42.0%, median minus estimate +0.0 pp | 35.4% (n=540; 95% CI 33.0%–39.8%); bootstrap median 35.4%, median minus estimate +0.1 pp | — (n=0) | 22.6% (n=343; 95% CI 20.3%–25.0%) |

Some intervals are asymmetric because re-estimated modes change classifications in some resamples.

The model-estimated education-profile difference averaged +3.6 percentage points (95% CI +3.3 to +3.8) among covered profiles (n=3268); weighted coverage was 82.1%. This is a model-estimated difference between profiles within the labour-force sample, not a causal effect. Selection matters: less-educated workers are concentrated in agriculture and elementary jobs, and many less-educated women are outside the labour force. The comparison does not establish that education changes unemployment.

**Flagged items**

- Youth occupation groups 1, 6 are mode-sensitive; see the
  [mode-stability table](../reports/tables/skills_mode_stability.csv).
- The PSU bootstrap ignores stratification; future-starter timing cannot be verified.
- Approximate NEET differs from PBS NEET; model-shift estimates are affected by labour-force selection.
- Cells marked n<30 are suppressed; a dash is a structural zero. Results show association, and do not
  measure vacancies, employer demand or individual skills.
