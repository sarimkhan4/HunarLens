# Skills-gap findings

Skills gap, as measurable from the LFS: the difference in education and vocational-training attainment between unemployed and employed youth, the education mismatch of employed youth relative to the occupations they hold, and what happens to youth at each education level in the labour market. Education and training are proxies for skills. Vacancies and employer demand are not measured in the LFS; employer surveys (NAVTTC/NSIS) are cited as context only.

The weighted survey estimates describe associations and do not establish causation. Education and training are skills proxies;
they do not describe an individual's abilities.

- The share with training was 8.9 percentage points lower among unemployed than employed youth (n=3383 unemployed, 23270 employed; 95% CI -10.3 to -7.5 percentage points).
- Using the all-employed norm, 46.0% of employed youth were above their occupation group's modal education band (n=23270; 95% CI 45.0%–47.2%).
- Using the youth-only norm, the corresponding share was 41.0% (n=23270; 95% CI 31.1%–41.6%).
- Not employed and not enrolled (approximate NEET) described 29.3% of youth (n=59486; 95% CI 28.7%–29.8%).
- The education-outcome table below shows four mutually exclusive shares for each education band; together the underlying shares sum to the whole band.

| Education band | n | Employed: matched | Employed: above mode | Employed: below mode | Unemployed |
|---|---:|---|---|---|---|
| No formal | 7094 | 60.1% (95% CI 58.3%–62.1%) | Suppressed | 31.7% (95% CI 30.0%–33.5%) | Suppressed |
| Below matric | 9629 | 43.6% (95% CI 42.3%–45.2%) | 41.0% (95% CI 39.5%–42.3%) | 4.0% (95% CI 3.4%–4.5%) | 11.4% (95% CI 10.6%–12.2%) |
| Matric | 4574 | Suppressed | 76.3% (95% CI 74.8%–78.3%) | Suppressed | 14.8% (95% CI 13.7%–16.0%) |
| Intermediate | 3849 | Suppressed | 60.4% (95% CI 58.5%–63.9%) | 22.0% (95% CI 19.6%–23.6%) | Suppressed |
| Degree or above | 1507 | 42.0% (95% CI 37.5%–44.7%) | 35.4% (95% CI 33.0%–39.8%) | Suppressed | Suppressed |

The four underlying outcome shares sum to the whole education band before rounding. Suppressed cells
are withheld to protect small groups. See [graduate absorption](../reports/tables/skills_graduate_absorption.csv)
for the division between occupations and unemployment, including sex and area.

The mismatch results depend on the coarse five-band scheme and the occupation structure: agriculture and
elementary occupations have low modal education. The strict figure must not be read as “wasted degrees”.
The [tolerance and severe variants](../reports/tables/skills_mismatch_variants.csv) and
[occupation comparisons](../reports/tables/skills_mismatch_by_occupation.csv) show the sensitivity.

The model-estimated education-profile difference averaged +3.6 percentage points (95% CI +3.3 to +3.8) among covered profiles (n=3268); weighted coverage was 82.1%. This is a model-estimated difference between profiles within the labour-force sample, not a causal effect. Selection matters: less-educated workers are concentrated in agriculture and elementary jobs, and many less-educated women are outside the labour force. The comparison does not establish that education changes unemployment.

| Validation group | n | Mean difference (95% CI), pp | Code sensitivity range, pp |
|---|---:|---|---|
| Male, rural | 1800 | +3.4 (+3.1 to +3.6) | +3.0 to +3.6 |
| Male, urban | 689 | +4.3 (+3.8 to +4.7) | +3.9 to +4.5 |
| Female, rural | 678 | +3.4 (+3.0 to +3.8) | +2.9 to +3.7 |
| Female, urban | 101 | +2.7 (+1.2 to +4.2) | +2.2 to +3.0 |
| No formal | 978 | +0.8 (+0.8 to +0.9) | -0.3 to +1.5 |
| Below matric | 1357 | +4.3 (+4.1 to +4.5) | +4.3 to +4.3 |
| Matric | 583 | +9.0 (+8.5 to +9.6) | +9.0 to +9.0 |
| Intermediate | 350 | -1.6 (-1.9 to -1.2) | -2.4 to -0.9 |
| Degree or above | Suppressed | Suppressed | Suppressed |

Not employed and not enrolled (approximate NEET) is not the SDG 8.6.1 indicator: recent training cannot be
identified from the available questions.

| Group | n | Approximate NEET (95% CI) |
|---|---:|---|
| All youth | 59486 | 29.3% (95% CI 28.7%–29.8%) |
| Male | 31418 | 13.7% (95% CI 13.1%–14.2%) |
| Female | 28068 | 46.5% (95% CI 45.5%–47.3%) |
| Rural | 39904 | 29.5% (95% CI 28.8%–30.3%) |
| Urban | 19582 | 29.0% (95% CI 27.9%–29.9%) |

The [PBS annual report](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf) separately reports a national NEET estimate of 28.4%
(sample count and interval not reported in the table). Its definition differs from our approximation.
The external figure is recorded in [skills_neet_external.csv](../reports/tables/skills_neet_external.csv).

See the aggregate skills tables for sample counts, 95% intervals, sensitivity ranges and suppressed cells.
The approximate NEET measure means not employed and not enrolled; it does not establish that a youth is
outside all non-formal training. Degree types are only identifiable for the explicitly labelled codes;
other degree-level codes have no recorded field. The questionnaire's “other” category refers specifically to
a two-year degree in other subjects; the [degree-type table](../reports/tables/skills_degree_type.csv)
shows n and reliability flags:

| Reported degree type | n | Unemployment (95% CI) | Reliability |
|---|---:|---|---|
| Engineering | 81 | Suppressed | suppressed: small cell |
| Medicine | 35 | Suppressed | suppressed: small cell |
| Computer | 34 | Suppressed | suppressed: small cell |
| Agriculture | suppressed | Suppressed | suppressed: small cell |
| Other two-year degree | 479 | 25.1% (95% CI 21.0%–29.3%) | Not flagged |

Industry, detailed field of study and unemployment barriers
were excluded and remain future work. The survey has no vacancy or employer-demand measure.
Comparisons between norm populations are affected by cohort composition, and the model was trained without
survey weights. Small groups are suppressed or marked unreliable.
