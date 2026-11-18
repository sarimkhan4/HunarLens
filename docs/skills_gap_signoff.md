# Skills-gap sign-off — team review

**Status:** Tests passed: 60; failures: 0; errors: 0. Evidence: [audit](skills_gap_data_audit.md),
[methods](skills_gap_methods.md), [findings](skills_gap_findings.md) and the linked aggregate tables.

**Decisions:** approved one-digit occupations; armed forces excluded; all-employed, age 25–44, youth-only
and normative comparisons; approximate NEET; approved absence exclusions; frequency-averaged education
scenario and training scenario. Industry, detailed field of study and unemployment barriers are excluded.
The PBS occupation-version discrepancy and bootstrap design are documented in the audit and methods.

| Reproduction comparison | Maximum absolute difference (percentage points) | Status |
|---|---:|---|
| Occupation groups | 0.055 | Pass |
| Education/literacy | 0.032 | Pass |

[Full reproduction table](../reports/tables/skills_reproduction.csv) and
[waterfall](../reports/tables/skills_row_waterfall.csv).

**Occupation modes: all employed persons aged 15+**

| Occupation group | Modal education band | n |
|---:|---|---:|
| 1 | Degree or above | 2133 |
| 2 | Degree or above | 5932 |
| 3 | Degree or above | 4151 |
| 4 | Degree or above | 1664 |
| 5 | Below matric | 16244 |
| 6 | No formal | 28878 |
| 7 | Below matric | 12194 |
| 8 | Below matric | 7935 |
| 9 | No formal | 17987 |

**Five headline findings**

- The training share among unemployed youth was -8.9 percentage points compared with employed youth.
- Under the all-employed norm, 46.0% of employed youth were above their occupation group's modal education band.
- Using the youth-only norm, the corresponding share was 41.0%.
- The approximate not-employed-and-not-enrolled share was 29.3% of all youth.
- Among non-enrolled youth in the labour force reporting another two-year degree, 25.1% were unemployed.

The model-estimated education-profile difference averaged +3.6 percentage points among covered profiles; weighted coverage was 82.1%. This is a model-estimated difference between profiles, not a causal effect.

Cells under 30 are suppressed, and small groups are flagged. Results show associations only; the extension
does not measure vacancies, employer demand or individual skills. Review the degree-type table's suppressed
groups and the scenario-coverage table before use.
