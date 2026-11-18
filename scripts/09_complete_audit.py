# What: generates the field-by-field S1 evidence from survey metadata and counts.
# Why: every variable used to define the study population needs an audit trail.
# Viva: missing routed answers are different from a recorded answer of no.
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.skills import safe_cell

RAW = ROOT / "data/raw/LFS 2024-25.sav web.dta"
TABLE = ROOT / "reports/tables/skills_s1_field_values.csv"
DOC = ROOT / "docs/skills_gap_data_audit.md"

# Extracted question stems from the PBS questionnaire; line wrapping is joined.
QUESTIONS = {
    "S4C5": "Gender",
    "S4C6": "How old was (Name) at (his/her) last birthday?",
    "S4C81": "Can…… read a simple statement with understanding in any language?",
    "S4C82": "Can…… write a simple statement with understanding in any language?",
    "S4C9": "Level of Education",
    "S4C10": "Current Enrollment",
    "S4C11": "Has…… ever completed/currently receiving any technical, vocational and educational training/courses such as auto or engine mechanics, carpentry, typing, computer, tailoring etc.",
    "S5C1": "Did…. do any work for pay/wage (Cash/Kind), for someone else during last week, at least for one hour on any day?",
    "S5C2": "Did …. Run / do any kind of business, farming or other activity to generate income in last week?",
    "S5C3": "Did…help to work for family gain in a family business or family farm during last week?",
    "S5C4": "Even though (you/NAME) did not work last week did (you/he/she) have a paid job or a business/ agriculture/ Poultry/ Livestock/Fishery farm?",
    "S5C5": "Why did … not work last week?",
    "S5C6": "When will (you/Name) return to the same job/ business/own enterprise",
    "S5C7": "Do/Does you/Name continue to receive an income from (you/his/her job/ business/ own agriculture farm during the absence?",
    "S5C8": "Last week did (you/name) do any work in …?",
    "S5C9": "Was this work that you mentioned in…?",
    "S5C10": "Thinking about the work in (farming, rearing animals and/or fishing) …. (do/does) are the products intended ….?",
    "S5C12": "What was…..main occupation, e.g. what was the nature of work that ….did?",
    "S9C1": "Was (Name) looking for work during the last four week? (as employee, employer or independent worker to establish his/her own business)",
    "S9C5": "What is the main reason why (Name) did not try to find a paid job or start a business in the last 4 weeks?",
    "S9C6": "Could (you/NAME) start working within the next two weeks",
    "Province": "1. Province:",
    "Region": "Area is coded in the sampling scheme, not an individual question.",
    "Weights": "Not a questionnaire question; survey weight in the Stata data.",
    "PCode": "Section 1: Identification Processing Code:",
    "EBCode": "6. Enumeration Block Code:",
}


def main():
    reader = pd.read_stata(RAW, iterator=True)
    labels = reader.variable_labels()
    columns = list(QUESTIONS)
    data = pd.read_stata(RAW, columns=columns, convert_categoricals=False)
    youth = data.loc[data.S4C6.between(15, 24)]
    records, lines = [], []
    allowed = {"S4C5": range(1, 4), "S4C81": [1, 2], "S4C82": [1, 2],
               "S4C9": range(1, 17), "S4C10": range(1, 17), "S4C11": range(1, 5),
               "S5C1": [1, 2], "S5C2": [1, 2], "S5C3": [1, 2], "S5C4": [1, 2],
               "S5C5": range(1, 16), "S5C6": range(1, 4), "S5C7": [1, 2],
               "S5C8": range(1, 5), "S5C9": range(1, 5), "S5C10": range(1, 5),
               "S9C1": [1, 2], "S9C5": range(1, 15), "S9C6": [1, 2],
               "Region": [1, 2], "Province": [1, 2, 3, 4]}
    for field, question in QUESTIONS.items():
        frame = youth[[field, "Weights"]].copy() if field != "Weights" else youth[["Weights"]].copy()
        if field in {"Weights", "PCode", "EBCode"}:
            n, weight, flag = safe_cell(len(frame.loc[frame[field].notna()]), frame.loc[frame[field].notna(), "Weights"].sum())
            records.append({"variable": field, "code": "nonmissing; values withheld", "n": n, "weighted_n": weight, "flag": flag})
        else:
            for code, group in frame.groupby(field, dropna=False, sort=True):
                n, weight, flag = safe_cell(len(group), group.Weights.sum())
                records.append({"variable": field, "code": "missing" if pd.isna(code) else str(code), "n": n, "weighted_n": weight, "flag": flag})
        values = [r for r in records if r["variable"] == field]
        cells = "; ".join(f"{r['code']}: {r['n']}" for r in values)
        evidence = "Observed codes and sample counts at left; age and training routes checked in skills_audit_routing.csv and skills_audit_education_ages.csv."
        if field.startswith(("S5", "S9")):
            evidence = "Observed codes and sample counts at left; questionnaire routes compared with approved label. Routed cells may be missing."
        if field in {"S5C5", "S5C6", "S5C7", "S5C8"}:
            evidence += " Zeroes occur outside the relevant absence/no-work routes; not interpreted as an answer."
        if field == "S5C5":
            evidence += " Stata label shift: team-approved questionnaire mapping; ambiguous codes excluded."
        if field == "S4C81":
            evidence += " Stata value-label text is malformed; questionnaire 1/2 coding applies."
        if field == "S9C5":
            evidence += " No reason was recorded on the searched route." if not (youth.S9C5.notna() & youth.S9C1.eq(1)).any() else " Reason is also recorded on the searched route; investigate."
        if field == "S4C11":
            evidence += " Trainee and non-trainee routes were checked against course recording."
        if field == "S5C12":
            evidence += " Non-employed records are excluded from the occupation lens; group-by-sex/area table checks observed major groups."
        if field in allowed:
            relevant = youth[field].notna()
            if field in {"S5C5", "S5C6", "S5C7"}:
                relevant &= youth.S5C4.eq(1)
            if field == "S5C8":
                relevant &= ~youth[field].eq(0)
                if (youth[field].eq(0) & youth.S5C4.eq(2)).any():
                    evidence += " Zero appeared on the no-job route; verification incomplete."
            unexpected = relevant & ~youth[field].isin(allowed[field])
            evidence += " Observed routed codes conform to the questionnaire." if not unexpected.any() else " Unexpected routed code: verification incomplete."
        if field in {"PCode", "EBCode"}:
            evidence = "Composite cluster checked against household counts; identifier values withheld."
        lines.append(f"| `{field}` | {question} | {labels.get(field, '') or '(none)'} | {cells} | {evidence} |")
    pd.DataFrame(records).to_csv(TABLE, index=False)
    text = DOC.read_text(encoding="utf-8")
    start, end = "<!-- S1 FIELDS START -->", "<!-- S1 FIELDS END -->"
    block = ("\n\n| Variable | Exact questionnaire wording / source | Stata variable label | Observed youth codes: unweighted n | Empirical evidence |\n"
             "|---|---|---|---|---|\n" + "\n".join(lines) + "\n\n")
    if start in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + start + block + end + after
    else:
        text += "\n\n## Field-by-field S1 evidence\n\n" + start + block + end + "\n"
    DOC.write_text(text, encoding="utf-8")
    print("Field-level S1 audit generated; small counts suppressed.")


if __name__ == "__main__":
    main()
