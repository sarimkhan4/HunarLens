# What: summarizes the downloaded survey schema and Census workbook shapes.
# Why: reviewers need evidence before choosing a label or features.
# Viva: this reads metadata and worksheet shapes, not individual responses.
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def audit() -> None:
    """Document observed field labels without exporting personal records."""
    source = RAW / "LFS 2024-25.sav web.dta"
    with pd.read_stata(source, iterator=True) as reader:
        labels = reader.variable_labels()
        value_labels = reader.value_labels()
        sample = reader.read(1)
        count = reader._nobs
    lines = ["# LFS raw data dictionary (preliminary)", "",
             f"Source: PBS Stata file, {count:,} records and {len(labels)} fields.",
             "Labels and codes below are embedded in the Stata file; the separate PBS coding scheme describes sampling codes. Missing codes and questionnaire routing are not yet verified.", "",
             "| Field | Stata variable label | Read type | Value labels |",
             "|---|---|---|---|"]
    for name, label in labels.items():
        codes = value_labels.get(name, {})
        if len(codes) > 20:
            coding = f"{len(codes)} labelled codes; see source"
        else:
            coding = "; ".join(f"{key}: {value}" for key, value in codes.items()) or "Not labelled"
        clean = lambda value: str(value).replace("|", "/").replace("\n", " ")
        lines.append(f"| {name} | {clean(label)} | {sample[name].dtype} | {clean(coding)} |")
    (ROOT / "docs" / "data_dictionary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"LFS: {count:,} rows; {len(labels)} columns")
    for path in sorted(RAW.glob("*.xlsx")):
        workbook = pd.ExcelFile(path)
        for sheet in workbook.sheet_names:
            rows, columns = pd.read_excel(workbook, sheet_name=sheet, header=None).shape
            print(f"{path.name}: {sheet}, {rows} rows x {columns} columns")


if __name__ == "__main__":
    audit()
