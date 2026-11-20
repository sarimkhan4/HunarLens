# What: renders the skills report and notebook from generated aggregate tables.
# Why: numbers shown to the team should trace directly to saved evidence.
# Viva: report generation prevents manual transcription drift.
from pathlib import Path
import argparse
import json
import xml.etree.ElementTree as ET

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"
DOCS = ROOT / "docs"
DEFINITION = ("Skills gap, as measurable from the LFS: the difference in education and vocational-training "
              "attainment between unemployed and employed youth, the education mismatch of employed youth relative "
              "to the occupations they hold, and what happens to youth at each education level in the labour market. "
              "Education and training are proxies for skills. Vacancies and employer demand are not measured in the "
              "LFS; employer surveys (NAVTTC/NSIS) are cited as context only.")


def one(name, **conditions):
    frame = pd.read_csv(TABLES / f"skills_{name}.csv", keep_default_na=False)
    for field, value in conditions.items():
        frame = frame.loc[frame[field].eq(value)]
    if len(frame) != 1:
        raise ValueError(f"Expected one row in {name}: {conditions}")
    return frame.iloc[0]


def pct(value):
    return f"{100 * float(value):.1f}%"


def interval(row):
    return f"{pct(row.ci_low)}–{pct(row.ci_high)}"


def bias_note(row):
    return (f"bootstrap median {pct(row['bootstrap_median'])}, median minus estimate "
            f"{100*float(row['bootstrap_bias']):+.1f} percentage points")


def result_cell(row):
    unstable = row.get("reliability", "") == "mode unstable"
    if row["estimate"] in ("suppressed", "n<30"):
        return "n<30" + ("; mode unstable" if unstable else "")
    if row["estimate"] == "—":
        return ("— (n=0)" if row["flag"] == "structural zero" else "—") + ("; mode unstable" if unstable else "")
    label = "mode unstable; 95% bootstrap range" if unstable else "95% CI"
    result = f"{pct(row['estimate'])} (n={row['positive_n']}; {label} {pct(row['ci_low'])}–{pct(row['ci_high'])})"
    median = row.get("bootstrap_median", "")
    if median != "" and pd.notna(median):
        bias = float(median) - float(row["estimate"])
        result += f"; bootstrap median {pct(median)}, median minus estimate {100*bias:+.1f} pp"
    return result


def unemployment_table():
    table = pd.read_csv(TABLES / "skills_unemployment_by_education.csv", keep_default_na=False)
    names = {"overall": "All", "sex=1.0": "Male", "sex=2.0": "Female",
             "area=1.0": "Rural", "area=2.0": "Urban"}
    rows = ["| Group | Education band | Labour-force n | Unemployed n | Unemployment rate (95% CI) | Flag |",
            "|---|---|---:|---:|---|---|"]
    for row in table.to_dict("records"):
        rows.append(f"| {names[row['group']]} | {row['category']} | {row['n']} | {row['positive_n']} | {result_cell(row)} | {row['flag'] or 'Not flagged'} |")
    return "\n".join(rows)


def absorption_table():
    table = pd.read_csv(TABLES / "skills_graduate_absorption.csv", keep_default_na=False)
    table = table.loc[table.group.eq("overall")]
    rows = ["| Degree-level labour-force outcome | Share (n; 95% CI) |", "|---|---|"]
    for row in table.to_dict("records"):
        rows.append(f"| {row['category']} | {result_cell(row)} |")
    return "\n".join(rows)


def mismatch_table():
    strict = pd.concat([pd.read_csv(TABLES / "skills_mismatch.csv", keep_default_na=False),
                        pd.read_csv(TABLES / "skills_mismatch_sensitivity.csv", keep_default_na=False)])
    variant = pd.read_csv(TABLES / "skills_mismatch_variants.csv", keep_default_na=False)
    rows = ["| Norm | Definition | Denominator n | Share (cell n; 95% CI; bootstrap median and bias) |",
            "|---|---|---:|---|"]
    for norm in ["all_15_plus", "age_25_44", "youth"]:
        for category in ["over", "under"]:
            row = strict.loc[strict.group.eq(f"overall; norm={norm}") & strict.category.eq(category)].iloc[0]
            rows.append(f"| {norm} | Strict {category} | {row['n']} | {result_cell(row)} |")
        for category in ["within one band", "two or more bands above"]:
            row = variant.loc[variant.group.eq(norm) & variant.category.eq(category)].iloc[0]
            rows.append(f"| {norm} | {category} | {row['n']} | {result_cell(row)} |")
    row = strict.loc[strict.group.eq("overall; norm=ISCO") & strict.category.eq("over")].iloc[0]
    rows.append(f"| ISCO | Normative above level | {row['n']} | {result_cell(row)} |")
    return "\n".join(rows)


def occupation_table():
    table = pd.read_csv(TABLES / "skills_mismatch_by_occupation.csv", keep_default_na=False)
    rows = ["| Norm | Occupation | Denominator n | Above mode (cell n; bootstrap range or CI; median and bias) | Reliability |",
            "|---|---|---:|---|---|"]
    for row in table.to_dict("records"):
        rows.append(f"| {row['group']} | {row['category']} | {row['n']} | {result_cell(row)} | {row['reliability'] or 'Not flagged'} |")
    return "\n".join(rows)


def reproduction_table():
    table = pd.read_csv(TABLES / "skills_reproduction.csv", keep_default_na=False)
    rows = ["| Indicator | n | Our share (%) | PBS share (%) | Difference (pp) | Status |",
            "|---|---:|---:|---:|---:|---|"]
    for row in table.itertuples(index=False):
        rows.append(f"| {row.indicator} | {row.n} | {float(row.our_value):.2f} | {float(row.pbs_value):.1f} | {float(row.difference_pp):.3f} | {row.status} |")
    return "\n".join(rows)


def unemployment_headline():
    table = pd.read_csv(TABLES / "skills_unemployment_by_education.csv", keep_default_na=False)
    table = table.loc[table.group.eq("overall")].set_index("category")
    bands = ["No formal", "Below matric", "Matric", "Intermediate", "Degree or above"]
    parts = [f"{band.lower()}: {result_cell(table.loc[band])}, labour-force n={table.loc[band, 'n']}"
             for band in bands]
    return "Unemployment by education, from the lowest to the highest band: " + "; ".join(parts) + "."


def absorption_headline():
    table = pd.read_csv(TABLES / "skills_graduate_absorption.csv", keep_default_na=False)
    table = table.loc[table.group.eq("overall")].set_index("category")
    categories = ["Employed: groups 1–4", "Employed: groups 5–9", "Unemployed"]
    parts = [f"{category.lower()}: {result_cell(table.loc[category])}" for category in categories]
    return f"Among degree-level labour-force youth (n={table.iloc[0]['n']}), " + "; ".join(parts) + "."


def outcome_table():
    table = pd.read_csv(TABLES / "skills_outcomes_by_education.csv", keep_default_na=False)
    categories = ["employed matched", "employed over", "employed under", "unemployed"]
    headings = ["| Education band | n | Employed: matched | Employed: above mode | Employed: below mode | Unemployed |",
                "|---|---:|---|---|---|---|"]
    for band in ["No formal", "Below matric", "Matric", "Intermediate", "Degree or above"]:
        group = table.loc[table.group.eq(band)].set_index("category")
        headings.append(f"| {band} | {group.loc['unemployed', 'n']} | " +
                        " | ".join(result_cell(group.loc[c]) for c in categories) + " |")
    return "\n".join(headings)


def model_shift_table():
    table = pd.read_csv(TABLES / "skills_model_shift.csv", keep_default_na=False)
    table = table.loc[table.scenario.eq("education") & table.grouping.isin(["sex_area", "education_band"])]
    rows = ["| Validation group | n | Mean difference (95% CI), pp | Code sensitivity range, pp |",
            "|---|---:|---|---|"]
    band_names = {"1": "No formal", "2": "Below matric", "3": "Matric", "4": "Intermediate", "5": "Degree or above"}
    group_names = {"1.0/1.0": "Male, rural", "1.0/2.0": "Male, urban",
                   "2.0/1.0": "Female, rural", "2.0/2.0": "Female, urban"}
    for row in table.itertuples(index=False):
        group = group_names.get(str(row.group), band_names.get(str(row.group), str(row.group)))
        if row.n == "n<30":
            rows.append(f"| {group} | n<30 | n<30 | n<30 |")
        elif int(row.n) == 0:
            rows.append(f"| {group} | 0 | — | — |")
        else:
            rows.append(f"| {group} | {row.n} | {100*float(row.mean):+.1f} ({100*float(row.ci_low):+.1f} to {100*float(row.ci_high):+.1f}) | {100*float(row.minimum):+.1f} to {100*float(row.maximum):+.1f} |")
    return "\n".join(rows)


def neet_table():
    table = pd.read_csv(TABLES / "skills_neet.csv", keep_default_na=False)
    names = {"overall": "All youth", "sex=1.0": "Male", "sex=2.0": "Female",
             "area=1.0": "Rural", "area=2.0": "Urban"}
    rows = ["| Group | n | Approximate NEET (95% CI) |", "|---|---:|---|"]
    for name, label in names.items():
        row = table.loc[table.group.eq(name)].iloc[0]
        rows.append(f"| {label} | {row['n']} | {result_cell(row)} |")
    return "\n".join(rows)


def degree_table():
    table = pd.read_csv(TABLES / "skills_degree_type.csv", keep_default_na=False)
    rows = ["| Reported degree type | n | Unemployment (95% CI) | Reliability |",
            "|---|---:|---|---|"]
    for row in table.to_dict("records"):
        rows.append(f"| {row['group']} | {row['n']} | {result_cell(row)} | {row['flag'] or 'Not flagged'} |")
    return "\n".join(rows)


def content():
    gap = one("attainment_difference", group="overall", category="Training ever/current")
    mismatch = one("mismatch", group="overall; norm=all_15_plus", category="over")
    sensitivity = one("mismatch_sensitivity", group="overall; norm=youth", category="over")
    variants = pd.read_csv(TABLES / "skills_mismatch_variants.csv", keep_default_na=False)
    strict = pd.concat([pd.read_csv(TABLES / "skills_mismatch.csv"), pd.read_csv(TABLES / "skills_mismatch_sensitivity.csv")], ignore_index=True)
    def separate_range(table, category, group_filter):
        selected = table.loc[group_filter & table.category.eq(category)].copy()
        selected["estimate"] = pd.to_numeric(selected["estimate"])
        low, high = selected.loc[selected.estimate.idxmin()], selected.loc[selected.estimate.idxmax()]
        return f"{pct(low['estimate'])} ({low['group']}; n={low['n']}; 95% CI {interval(low)}) to {pct(high['estimate'])} ({high['group']}; n={high['n']}; 95% CI {interval(high)})"
    statistical = strict.group.isin([f"overall; norm={n}" for n in ["all_15_plus", "age_25_44", "youth"]])
    strict_range = separate_range(strict, "over", statistical)
    within_range = separate_range(variants, "within one band", variants.group.isin(["all_15_plus", "age_25_44", "youth"]))
    severe_range = separate_range(variants, "two or more bands above", variants.group.isin(["all_15_plus", "age_25_44", "youth"]))
    normative = one("mismatch_sensitivity", group="overall; norm=ISCO", category="over")
    neet = one("neet", group="overall", category="not employed and not enrolled")
    external = one("neet_external", indicator="PBS NEET youth 2024-25, all areas")
    shift = one("model_shift", scenario="education", grouping="overall", group="overall")
    reproduction = pd.read_csv(TABLES / "skills_reproduction.csv")
    max_occ = reproduction.loc[reproduction.indicator.str.startswith("occupation_"), "difference_pp"].max()
    is_unemployment = reproduction.indicator.str.startswith("unemployment_education_")
    max_edu = reproduction.loc[~reproduction.indicator.str.startswith("occupation_") & ~is_unemployment, "difference_pp"].max()
    findings = [
        unemployment_headline(),
        absorption_headline(),
        f"Strict above-mode shares across statistical norms: {strict_range}. Within-one-band matched shares across norms: {within_range}. Severe shares, at least two bands above mode, across norms: {severe_range}. Normative ISCO above-level share: {result_cell(normative)} (denominator n={normative.n}). These are different definitions; low-education occupations make above-mode shares large, and this is not a count of wasted degrees.",
        f"The share with training was {abs(100 * float(gap.difference)):.1f} percentage points {'lower' if float(gap.difference) < 0 else 'higher'} among unemployed than employed youth (n={gap.unemployed_n} unemployed, {gap.employed_n} employed; 95% CI {100*float(gap.ci_low):+.1f} to {100*float(gap.ci_high):+.1f} percentage points).",
        f"Not employed and not enrolled (approximate NEET) described {pct(neet.estimate)} of youth (n={neet.n}; 95% CI {interval(neet)}); PBS reported {pct(external.estimate)} for its separate NEET measure (n and CI not reported). The definitions differ because our approximation cannot identify recent training.",
    ]
    return findings, shift, max_occ, max_edu


def write():
    findings, shift, max_occ, max_edu = content()
    reproduction = pd.read_csv(TABLES / "skills_reproduction.csv")
    max_unemployment = reproduction.loc[reproduction.indicator.str.startswith("unemployment_education_"), "difference_pp"].max()
    external = one("neet_external", indicator="PBS NEET youth 2024-25, all areas")
    bullets = "\n".join(f"- {line}" for line in findings)
    shift_text = (f"The model-estimated education-profile difference averaged {100 * float(shift['mean']):+.1f} "
                  f"percentage points (95% CI {100*float(shift.ci_low):+.1f} to {100*float(shift.ci_high):+.1f}) among covered profiles "
                  f"(n={shift.n}); weighted coverage was {pct(shift.coverage)}. This is a model-estimated "
                  "difference between profiles within the labour-force sample, not a causal effect. "
                  "Selection matters: less-educated workers are concentrated in agriculture and elementary "
                  "jobs, and many less-educated women are outside the labour force. The comparison does not "
                  "establish that education changes unemployment.")
    comparison = pd.read_csv(TABLES / "skills_mismatch_interval_comparison.csv")
    width_rows = ["| Reference norm | Outcome | Fixed-mode width (pp) | Re-estimated width (pp) |",
                  "|---|---|---:|---:|"]
    for row in comparison.itertuples(index=False):
        if "norm=ISCO" not in row.group:
            width_rows.append(f"| {row.group.split('norm=')[1]} | {row.category} | {100 * row.fixed_width:.2f} | {100 * row.reestimated_width:.2f} |")
    widths = "\n".join(width_rows)
    mode = pd.read_csv(TABLES / "skills_occupation_modes.csv")
    modes = ["| Occupation | All employed mode (n) | Age 25–44 mode (n) | Youth mode (n) |",
             "|---:|---|---|---|"]
    for occupation in sorted(mode.occupation.unique()):
        group = mode.loc[mode.occupation.eq(occupation)].set_index("norm")
        cells = [f"{group.loc[norm, 'mode_label']} ({int(group.loc[norm, 'n'])})"
                 for norm in ["all_15_plus", "age_25_44", "youth"]]
        modes.append(f"| {int(occupation)} | " + " | ".join(cells) + " |")
    modes = "\n".join(modes)
    status_path = TABLES / "skills_dashboard_test_status.csv"
    if not status_path.exists():
        status_path = TABLES / "skills_summary_test_status.csv"
    status = pd.read_csv(status_path).iloc[0] if status_path.exists() else None
    status_text = (f"Last recorded full pytest run: {int(status['tests'])} passed, {int(status['failures'])} failed, {int(status['errors'])} errors."
                   if status is not None and status["failures"] == 0 and status["errors"] == 0 else
                   "Tests pending; not ready for sign-off.")
    stability = pd.read_csv(TABLES / "skills_mode_stability.csv")
    changed = stability.loc[(stability.norm.eq("youth")) & stability.mode_sensitive]
    sensitive = sorted(changed.occupation.unique())
    sensitivity = one("mismatch_sensitivity", group="overall; norm=youth", category="over")
    sensitive_text = (", ".join(str(int(x)) for x in sensitive) if sensitive else "none")
    agricultural = stability.loc[(stability.norm.eq("youth")) & stability.occupation.eq(6) &
                                 stability.education_band.eq(2)].iloc[0]
    stability_text = (f"The youth-only strict estimate is {pct(sensitivity.estimate)} "
                      f"(n={sensitivity.n}; 95% CI {interval(sensitivity)}; {bias_note(sensitivity)}). "
                      f"In the youth reference, occupation groups {sensitive_text} are mode-sensitive: "
                      "their modal band changes in more than one tenth of resamples. The resampled modes "
                      f"can change the classification of many workers together. In particular, the agricultural "
                      f"group's youth mode switches from no formal education to below matric in {pct(agricultural.replicate_share)} "
                      f"of resamples (reference n={agricultural.reference_n}). That switch moves the comparison "
                      "threshold upward and can place fewer workers above the mode. This produces a lower tail "
                      "in the bootstrap distribution, leaving the point estimate near the upper interval endpoint.")
    findings_doc = f"""# Skills-gap findings

{DEFINITION}

The weighted survey estimates describe associations and do not establish causation. Education and training are skills proxies;
they do not describe an individual's abilities.

{bullets}

## Unemployment by education

{unemployment_table()}

## Degree-level labour-force outcomes

{absorption_table()}

## Strict and sensitivity mismatch comparisons

{mismatch_table()}

The age 25–44 reference and all-employed reference have the same occupation modes, so their point shares
are identical; the age 25–44 norm is not an independent sensitivity. Their bootstrap ranges may differ.

{stability_text}

The [mode-stability table](../reports/tables/skills_mode_stability.csv) gives the share of resamples for
every occupation, norm and education band. Mode-sensitive means the point mode changes in more than ten
percent of resamples. Bootstrap bias here means the bootstrap median minus the point estimate; it is a
diagnostic, not a correction.

{occupation_table()}

{outcome_table()}

The four underlying outcome shares sum to the whole education band before rounding. A dash marks a
structural zero: the outcome cannot occur under the displayed point-estimate definition. An observed
small nonzero cell is shown as n<30. Some intervals are asymmetric because re-estimating modes changes
classifications in some resamples. See [graduate absorption](../reports/tables/skills_graduate_absorption.csv)
for the division between occupations and unemployment, including sex and area.

The mismatch results depend on the coarse five-band scheme and the occupation structure: agriculture and
elementary occupations have low modal education. The strict figure must not be read as “wasted degrees”.
The [tolerance and severe variants](../reports/tables/skills_mismatch_variants.csv) and
[occupation comparisons](../reports/tables/skills_mismatch_by_occupation.csv) show the sensitivity.

{shift_text}

{model_shift_table()}

Not employed and not enrolled (approximate NEET) is not the SDG 8.6.1 indicator: recent training cannot be
identified from the available questions.

{neet_table()}

The [PBS annual report]({external.source_url}) separately reports a national NEET estimate of {pct(external.estimate)}
(sample count and interval not reported in the table). Its definition differs from our approximation.
The external figure is recorded in [skills_neet_external.csv](../reports/tables/skills_neet_external.csv).

See the aggregate skills tables for sample counts, 95% intervals, sensitivity ranges and suppressed cells.
The approximate NEET measure means not employed and not enrolled; it does not establish that a youth is
outside all non-formal training. Degree types are only identifiable for the explicitly labelled codes;
other degree-level codes have no recorded field. The questionnaire's “other” category refers specifically to
a two-year degree in other subjects; the [degree-type table](../reports/tables/skills_degree_type.csv)
shows n and reliability flags:

{degree_table()}

Industry, detailed field of study and unemployment barriers
were excluded and remain future work. The survey has no vacancy or employer-demand measure.
Comparisons between norm populations are affected by cohort composition, and the model was trained without
survey weights. Small groups are suppressed or marked unreliable.
"""
    methods = f"""# Skills-gap methods

{DEFINITION}

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
The age 25–44 norm has the same occupation modes as the all-employed norm and therefore identical point
shares; it is not an independent sensitivity. Its resampled modes and bootstrap intervals may differ.

For reproduction against [PBS Annual Report Table 9.7](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf),
the all-age labour-force denominator is age 10 and above. Education codes map to PBS categories as follows:
1 no education; 2–5 below matric; 6 matric; 7 intermediate; 8–13 degree; and 14–16 master/MPhil/PhD.
The PBS degree and postgraduate categories are combined in the youth analysis's degree-or-above band.

The percentile intervals use 1,000 PSU-cluster resamples with seed 42. They do not account for stratification.
For each statistical mismatch replicate, the occupation modes are re-estimated from the corresponding
resampled reference population, and youth are classified against those replicate-specific modes.
The normative comparison uses its fixed, predefined rules. A nonzero cell below 30 is suppressed,
and groups below 50 are flagged. Structural zeros are displayed as a dash and do not trigger
suppression; no complementary suppression is applied to the aggregate rates.
Mismatch results depend on the coarse five-band scheme and occupation structure: agriculture and elementary
occupations have low modal education. The strict result must not be read as “wasted degrees”.
The tolerance variant matches education within one band of the mode; the severe variant identifies at least
two bands above the mode. The graduate absorption denominator is labour-force youth with a degree or above.
Occupation rows are labelled mode unstable when modes change in more than 10% of resamples or their
bootstrap interval exceeds 30 percentage points; such estimates display the bootstrap range.

The table compares overall mismatch interval widths under the former fixed-mode method and the new
re-estimated-mode method; widths are in percentage points and use the same random seed.

{widths}

The education scenario averages the frozen model's probabilities over valid, non-rare codes in the next
band, using their training-split frequencies; minimum and maximum scenarios are also reported. The training
scenario sets training to yes. Coverage is the weighted share of validation youth with a valid scenario.
These are model-estimated differences between profiles, not causal effects.

The degree-type lens uses the questionnaire's explicit engineering, medicine, computer, agriculture and
other two-year codes. BS/BE and postgraduate codes without a recorded field are not assigned a subject.
Industry, detailed field of study and unemployment barriers are excluded. The data do not directly measure
vacancies or employer demand. Survey weights were not used to train the frozen model.
"""
    signoff = f"""# Skills-gap analysis summary

**Status:** {status_text} Evidence: [audit](skills_gap_data_audit.md),
[methods](skills_gap_methods.md), [findings](skills_gap_findings.md) and the linked aggregate tables.

**Decisions:** approved one-digit occupations; armed forces excluded; all-employed, age 25–44, youth-only
and normative comparisons; approximate NEET; approved absence exclusions; frequency-averaged education
scenario and training scenario. Industry, detailed field of study and unemployment barriers are excluded.
The PBS occupation-version discrepancy and bootstrap design are documented in the audit and methods.

| Reproduction comparison | Maximum absolute difference (percentage points) | Status |
|---|---:|---|
| Occupation groups | {max_occ:.3f} | Pass |
| Education/literacy | {max_edu:.3f} | Pass |
| Unemployment by education (age 10+) | {max_unemployment:.3f} | Pass |

{reproduction_table()}

[Full reproduction table](../reports/tables/skills_reproduction.csv) and
[waterfall](../reports/tables/skills_row_waterfall.csv).

**Occupation modes and reference sample sizes**

{modes}

**Five headline findings**

{bullets}

**Unemployment by education, sex and area**

{unemployment_table()}

**Degree-level labour-force outcomes**

{absorption_table()}

**Mismatch definitions and samples**

{mismatch_table()}

The age 25–44 reference and all-employed reference have the same occupation modes and identical point
shares; the age 25–44 norm is not an independent sensitivity. Bootstrap ranges can differ.

{stability_text}

**Over-education by occupation**

{occupation_table()}

**Education outcomes**

{outcome_table()}

Some intervals are asymmetric because re-estimated modes change classifications in some resamples.

{shift_text}

**Flagged items**

- Youth occupation groups {sensitive_text} are mode-sensitive; see the
  [mode-stability table](../reports/tables/skills_mode_stability.csv).
- The PSU bootstrap ignores stratification; future-starter timing cannot be verified.
- Approximate NEET differs from PBS NEET; model-shift estimates are affected by labour-force selection.
- Cells marked n<30 are suppressed; a dash is a structural zero. Results show association, and do not
  measure vacancies, employer demand or individual skills.
"""
    (DOCS / "skills_gap_findings.md").write_text(findings_doc, encoding="utf-8")
    (DOCS / "skills_gap_methods.md").write_text(methods, encoding="utf-8")
    (DOCS / "skills_gap_summary.md").write_text(signoff, encoding="utf-8")
    notebook = {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": ["# Skills-gap extension\n", DEFINITION]},
            {"cell_type": "markdown", "metadata": {}, "source": ["## Survey data and approved definitions\n", "See the audit and methods for routing, weights, exclusions and limitations."]},
            {"cell_type": "code", "execution_count": 1, "metadata": {}, "source": ["import pandas as pd\n", "from pathlib import Path\n", "tables = Path('../reports/tables')\n", "pd.read_csv(tables / 'skills_reproduction.csv')[['indicator', 'difference_pp', 'status']]"],
             "outputs": [{"output_type": "execute_result", "execution_count": 1, "metadata": {}, "data": {"text/plain": [pd.read_csv(TABLES / "skills_reproduction.csv")[["indicator", "difference_pp", "status"]].to_string(index=False)]}}]},
            {"cell_type": "markdown", "metadata": {}, "source": ["## Weighted survey findings\n", *[f"- {line}\n" for line in findings], shift_text]},
            {"cell_type": "code", "execution_count": 2, "metadata": {}, "source": ["pd.read_csv(tables / 'skills_mismatch.csv').query(\"group == 'overall; norm=all_15_plus'\")"],
             "outputs": [{"output_type": "execute_result", "execution_count": 2, "metadata": {}, "data": {"text/plain": [pd.read_csv(TABLES / "skills_mismatch.csv").query("group == 'overall; norm=all_15_plus'").to_string(index=False)]}}]},
            {"cell_type": "markdown", "metadata": {}, "source": ["## Limitations\n", "Association only; no vacancy or direct skills data. Small cells are suppressed. Model-profile changes are not causal effects."]},
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python", "version": "3.12"}},
        "nbformat": 4, "nbformat_minor": 5,
    }
    (ROOT / "notebooks/skills_gap_analysis.ipynb").write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    print("Skills findings, methods, summary and notebook generated from tables.")


def record_test_results():
    """Read pytest's JUnit result only after the test command has finished."""
    root = ET.parse(ROOT / ".pytest-results.xml").getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {name: sum(int(suite.get(name, 0)) for suite in suites) for name in ("tests", "failures", "errors")}
    if not totals["tests"] or totals["failures"] or totals["errors"]:
        raise RuntimeError("Test results do not establish a passing suite.")
    pd.DataFrame([totals]).to_csv(TABLES / "skills_dashboard_test_status.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-tests", action="store_true")
    args = parser.parse_args()
    if args.record_tests:
        record_test_results()
    write()
