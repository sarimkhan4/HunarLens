# What: produces aggregate-only availability and routing tables for the S1 audit.
# Why: evidence for the skills extension must be checked before analysis.
# Viva: each weighted total is paired with its survey sample count.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.skills import render_audit_totals, safe_cell

RAW = ROOT / "data/raw/LFS 2024-25.sav web.dta"
TABLES = ROOT / "reports/tables"
GENERAL = ["S4C5", "S4C6", "Region", "S4C9", "S4C10", "S4C11", "S4C12", "S4C13", "S4C14"]
EMPLOYED = ["S5C11", "S5C12", "S5C13", "S5C15", "S5C16", "S5C17", "S5C18", "S5C19", "S5C20", "Fstatus"]
NONEMPLOYED = ["S9C1", *[f"S9C2{i}" for i in range(1, 14)], "S9C3", "S9C4", "S9C5", "S9C6", "S9C7", "S9C9", "S9C10", "S9C11", "S9C12", "S9C13", "S9C14", "S9C15", "S9C16"]
LABEL = ["S5C1", "S5C2", "S5C3", "S5C4", "S5C5", "S5C6", "S5C7", "S5C8", "S5C9", "S5C10"]


def add_cell(rows: list, scope: str, variable: str, category: str, frame: pd.DataFrame) -> None:
    """Publish only sample and weighted aggregate counts."""
    n, weighted, flag = safe_cell(len(frame), frame.Weights.sum())
    rows.append(dict(scope=scope, variable=variable, category=category, n=n, weighted_n=weighted, flag=flag))


def tabulate(rows: list, scope: str, variable: str, frame: pd.DataFrame) -> None:
    """Keep missing separate from values; avoid hundreds of sparse detail codes."""
    add_cell(rows, scope, variable, "ALL", frame)
    values = frame[variable]
    if variable in {"S5C12", "S5C13", "S9C12", "S9C13", "S4C13", "S5C18", "S9C15", "S4C6"}:
        add_cell(rows, scope, variable, "recorded", frame.loc[values.notna()])
        add_cell(rows, scope, variable, "missing / not asked", frame.loc[values.isna()])
        return
    for value in sorted(values.dropna().unique()):
        add_cell(rows, scope, variable, str(value), frame.loc[values.eq(value)])
    add_cell(rows, scope, variable, "missing / not asked", frame.loc[values.isna()])


def main() -> None:
    spec = spec_from_file_location("dataset_builder", ROOT / "scripts/01_build_dataset.py")
    builder = module_from_spec(spec)
    spec.loader.exec_module(builder)
    columns = list(dict.fromkeys(["Weights", *GENERAL, *EMPLOYED, *NONEMPLOYED, *LABEL]))
    data = pd.read_stata(RAW, columns=columns, convert_categoricals=False)
    data = data.loc[data.S4C6.between(15, 24)].copy()
    employed, unemployed = builder.provisional_status(data)
    valid = ~data.S5C5.eq(14) & ~(data.S5C4.eq(1) & data.S5C5.isna())
    groups = [("all youth", data, GENERAL), ("employed youth", data.loc[valid & employed], EMPLOYED),
              ("unemployed youth", data.loc[valid & unemployed], NONEMPLOYED)]
    rows = []
    for scope, frame, fields in groups:
        for field in fields:
            tabulate(rows, scope, field, frame)
    add_cell(rows, "all youth", "Weights", "missing / not asked", data.loc[data.Weights.isna()])
    add_cell(rows, "all youth", "employment classification", "ambiguous absence excluded", data.loc[~valid])
    # Empirically check the questionnaire's previous-work routing against its mislabeled Stata field.
    for code in (1, 2):
        frame = data.loc[valid & unemployed & data.S9C10.eq(code)]
        add_cell(rows, "unemployed youth", "S9C10 routing", f"{code}: previous occupation recorded", frame.loc[frame.S9C12.notna()])
        add_cell(rows, "unemployed youth", "S9C10 routing", f"{code}: previous occupation missing", frame.loc[frame.S9C12.isna()])
    counts = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    counts.to_csv(TABLES / "skills_audit_counts.csv", index=False)
    reader = pd.read_stata(RAW, iterator=True)
    labels = reader.variable_labels()
    values = reader.value_labels()
    codebook = []
    for field in [*GENERAL, *EMPLOYED, *NONEMPLOYED, "Weights"]:
        for code, label in (values.get(field) or {"": "No Stata value labels"}).items():
            codebook.append({"variable": field, "stata_variable_label": labels.get(field, ""), "code": code, "stata_value_label": label})
    pd.DataFrame(codebook).to_csv(TABLES / "skills_audit_stata_codebook.csv", index=False)
    workers = data.loc[valid & employed].copy()
    workers["major"] = (workers.S5C12 // 1000).where(workers.S5C12.notna())
    occupation = []
    for (major, sex, area), frame in workers.groupby(["major", "S4C5", "Region"], dropna=False):
        add_cell(occupation, "employed youth", "occupation major / sex / area", f"{major} / {sex} / {area}", frame)
    pd.DataFrame(occupation).to_csv(TABLES / "skills_audit_occupation_groups.csv", index=False)
    doc = ROOT / "docs/skills_gap_data_audit.md"
    if doc.exists():
        contents = doc.read_text(encoding="utf-8")
        start, end = "<!-- AUDIT TOTALS START -->", "<!-- AUDIT TOTALS END -->"
        if start in contents and end in contents:
            prefix, tail = contents.split(start, 1)
            _, suffix = tail.split(end, 1)
            doc.write_text(prefix + start + "\n\n" + render_audit_totals(counts) + "\n\n" + end + suffix, encoding="utf-8")
    print("Aggregate audit tables written; all cells below 30 suppressed.")


if __name__ == "__main__":
    main()
