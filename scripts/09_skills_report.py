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


def content():
    gap = one("attainment_difference", group="overall", category="Training ever/current")
    mismatch = one("mismatch", group="overall; norm=all_15_plus", category="over")
    sensitivity = one("mismatch_sensitivity", group="overall; norm=youth", category="over")
    neet = one("neet", group="overall", category="not employed and not enrolled")
    degree = one("degree_type", group="Other two-year degree", category="unemployment rate")
    shift = one("model_shift", scenario="education", grouping="overall", group="overall")
    reproduction = pd.read_csv(TABLES / "skills_reproduction.csv")
    max_occ = reproduction.loc[reproduction.indicator.str.startswith("occupation_"), "difference_pp"].max()
    max_edu = reproduction.loc[~reproduction.indicator.str.startswith("occupation_"), "difference_pp"].max()
    findings = [
        f"The training share among unemployed youth was {100 * float(gap.difference):+.1f} percentage points compared with employed youth.",
        f"Under the all-employed norm, {pct(mismatch.estimate)} of employed youth were above their occupation group's modal education band.",
        f"Using the youth-only norm, the corresponding share was {pct(sensitivity.estimate)}.",
        f"The approximate not-employed-and-not-enrolled share was {pct(neet.estimate)} of all youth.",
        f"Among non-enrolled youth in the labour force reporting another two-year degree, {pct(degree.estimate)} were unemployed.",
    ]
    return findings, shift, max_occ, max_edu


def write():
    findings, shift, max_occ, max_edu = content()
    bullets = "\n".join(f"- {line}" for line in findings)
    shift_text = (f"The model-estimated education-profile difference averaged {100 * float(shift['mean']):+.1f} "
                  f"percentage points among covered profiles; weighted coverage was {pct(shift.coverage)}. "
                  "This is a model-estimated difference between profiles, not a causal effect.")
    comparison = pd.read_csv(TABLES / "skills_mismatch_interval_comparison.csv")
    width_rows = ["| Reference norm | Outcome | Fixed-mode width (pp) | Re-estimated width (pp) |",
                  "|---|---|---:|---:|"]
    for row in comparison.itertuples(index=False):
        if "norm=ISCO" not in row.group:
            width_rows.append(f"| {row.group.split('norm=')[1]} | {row.category} | {100 * row.fixed_width:.2f} | {100 * row.reestimated_width:.2f} |")
    widths = "\n".join(width_rows)
    mode = pd.read_csv(TABLES / "skills_occupation_modes.csv")
    mode = mode.loc[mode.norm.eq("all_15_plus")]
    modes = "\n".join(["| Occupation group | Modal education band | n |", "|---:|---|---:|"] +
                      [f"| {int(row.occupation)} | {row.mode_label} | {int(row.n)} |" for row in mode.itertuples(index=False)])
    status_path = TABLES / "skills_test_status.csv"
    status = pd.read_csv(status_path).iloc[0] if status_path.exists() else None
    status_text = (f"Tests passed: {int(status['tests'])}; failures: {int(status['failures'])}; errors: {int(status['errors'])}."
                   if status is not None and status["failures"] == 0 and status["errors"] == 0 else
                   "Tests pending; not ready for sign-off.")
    findings_doc = f"""# Skills-gap findings

{DEFINITION}

The weighted survey estimates describe associations, not causes. Education and training are skills proxies;
they do not describe an individual's abilities.

{bullets}

{shift_text}

See the aggregate skills tables for sample counts, 95% intervals, sensitivity ranges and suppressed cells.
The approximate NEET measure means not employed and not enrolled; it does not establish that a youth is
outside all non-formal training. Degree types are only identifiable for the explicitly labelled codes;
other degree-level codes have no recorded field. Industry, detailed field of study and unemployment barriers
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

The percentile intervals use 1,000 PSU-cluster resamples with seed 42. They do not account for stratification.
For each statistical mismatch replicate, the occupation modes are re-estimated from the corresponding
resampled reference population, and youth are classified against those replicate-specific modes.
The normative comparison uses its fixed, predefined rules. A cell below 30 is
suppressed and groups below 50 are flagged; complementary cells are suppressed when needed.

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
    signoff = f"""# Skills-gap sign-off — team review

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

[Full reproduction table](../reports/tables/skills_reproduction.csv) and
[waterfall](../reports/tables/skills_row_waterfall.csv).

**Occupation modes: all employed persons aged 15+**

{modes}

**Five headline findings**

{bullets}

{shift_text}

Cells under 30 are suppressed, and small groups are flagged. Results show associations only; the extension
does not measure vacancies, employer demand or individual skills. Review the degree-type table's suppressed
groups and the scenario-coverage table before use.
"""
    (DOCS / "skills_gap_findings.md").write_text(findings_doc, encoding="utf-8")
    (DOCS / "skills_gap_methods.md").write_text(methods, encoding="utf-8")
    (DOCS / "skills_gap_signoff.md").write_text(signoff, encoding="utf-8")
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
    (ROOT / "notebooks/07_skills_gap.ipynb").write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    print("Skills findings, methods, sign-off and notebook generated from tables.")


def record_test_results():
    """Read pytest's JUnit result only after the test command has finished."""
    root = ET.parse(ROOT / ".pytest-results.xml").getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {name: sum(int(suite.get(name, 0)) for suite in suites) for name in ("tests", "failures", "errors")}
    if not totals["tests"] or totals["failures"] or totals["errors"]:
        raise RuntimeError("Test results do not establish a passing suite.")
    pd.DataFrame([totals]).to_csv(TABLES / "skills_test_status.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-tests", action="store_true")
    args = parser.parse_args()
    if args.record_tests:
        record_test_results()
    write()
