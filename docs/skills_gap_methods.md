# Skills-gap methods

Skills gap, as measurable from the LFS: the difference in education and vocational-training attainment between unemployed and employed youth, the education mismatch of employed youth relative to the occupations they hold, and what happens to youth at each education level in the labour market. Education and training are proxies for skills. Vacancies and employer demand are not measured in the LFS; employer surveys (NAVTTC/NSIS) are cited as context only.

The survey analyses use LFS weights, with unweighted sample counts. The labour-force lenses use the approved
employment/unemployment definition among youth aged 15–24; approximate NEET uses all youth and means not
employed and not enrolled. The model-shift lens uses validation profiles only, with training-split code
frequencies and survey weights; it never changes or refits the model.

Education bands are no formal (1), below matric (2–5), matric (6), intermediate (7), and degree or above
(8–16). Occupations use one-digit major groups; armed forces are excluded. The modal education band in each
occupation is estimated in all employed persons aged 15+, in employed persons aged 25–44, and in employed
youth for the respective norms. A worker above, below or equal to that norm is called over-, under- or
matched in this statistical sense. The normative sensitivity compares codes 1–4 with level 1, 5–7 with
level 2, and 8–16 with levels 3–4. This is an occupation-level proxy rather than a measure of a person's skills.

The percentile intervals use 1,000 PSU-cluster resamples with seed 42. They do not account for stratification.
For each statistical mismatch replicate, the occupation modes are re-estimated from the corresponding
resampled reference population, and youth are classified against those replicate-specific modes.
The normative comparison uses its fixed, predefined rules. A cell below 30 is
suppressed and groups below 50 are flagged; complementary cells are suppressed when needed.
Mismatch results depend on the coarse five-band scheme and occupation structure: agriculture and elementary
occupations have low modal education. The strict result must not be read as “wasted degrees”.
The tolerance variant matches education within one band of the mode; the severe variant identifies at least
two bands above the mode. The graduate absorption denominator is labour-force youth with a degree or above.

The table compares overall mismatch interval widths under the former fixed-mode method and the new
re-estimated-mode method; widths are in percentage points and use the same random seed.

| Reference norm | Outcome | Fixed-mode width (pp) | Re-estimated width (pp) |
|---|---|---:|---:|
| all_15_plus | matched | 1.73 | 1.73 |
| all_15_plus | over | 1.93 | 2.25 |
| all_15_plus | under | 1.31 | 1.68 |
| age_25_44 | matched | 1.73 | 1.84 |
| age_25_44 | over | 1.93 | 2.05 |
| age_25_44 | under | 1.31 | 1.40 |
| youth | matched | 1.79 | 1.71 |
| youth | over | 2.05 | 10.50 |
| youth | under | 1.52 | 10.46 |

The education scenario averages the frozen model's probabilities over valid, non-rare codes in the next
band, using their training-split frequencies; minimum and maximum scenarios are also reported. The training
scenario sets training to yes. Coverage is the weighted share of validation youth with a valid scenario.
These are model-estimated differences between profiles, not causal effects.

The degree-type lens uses the questionnaire's explicit engineering, medicine, computer, agriculture and
other two-year codes. BS/BE and postgraduate codes without a recorded field are not assigned a subject.
Industry, detailed field of study and unemployment barriers are excluded. The data do not directly measure
vacancies or employer demand. Survey weights were not used to train the frozen model.
