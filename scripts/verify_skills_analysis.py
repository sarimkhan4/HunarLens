# What: audits routes, categories and plausible ages for the skills extension.
# Why: survey labels must be checked before they support a new analysis.
# Viva: a routed question is not expected to have an answer for everyone.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.skills import safe_cell

RAW = ROOT / "data/raw/LFS 2024-25.sav web.dta"
OUT = ROOT / "reports/tables"


def builder():
    spec = spec_from_file_location("dataset_builder", ROOT / "scripts/build_modeling_dataset.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_check(rows, name, population, selected):
    n, weight, flag = safe_cell(len(selected), selected.Weights.sum())
    rows.append({"check": name, "population": population, "n": n, "weighted_n": weight, "flag": flag})


def main():
    module = builder()
    cols = list(dict.fromkeys(module.COLS + ["S4C9", "S4C10", "S4C11", "S4C12", "S4C14", "S5C12", "Province"]))
    data = pd.read_stata(RAW, columns=cols, convert_categoricals=False)
    youth = data.loc[data.S4C6.between(15, 24)].copy()
    employed, _ = module.provisional_status(youth)
    valid = ~youth.S5C5.eq(14) & ~(youth.S5C4.eq(1) & youth.S5C5.isna())
    rows = []
    checks = [
        ("occupation recorded for employed", valid & employed & youth.S5C12.notna()),
        ("occupation missing for employed", valid & employed & youth.S5C12.isna()),
        ("occupation recorded outside employment", valid & ~employed & youth.S5C12.notna()),
        ("training course recorded for trainees", youth.S4C11.isin([1, 2, 3]) & youth.S4C12.notna()),
        ("training course missing for trainees", youth.S4C11.isin([1, 2, 3]) & youth.S4C12.isna()),
        ("training course recorded for non-trainees", youth.S4C11.eq(4) & youth.S4C12.notna()),
        ("training provider missing for trainees", youth.S4C11.isin([1, 2, 3]) & youth.S4C14.isna()),
        ("enrolment missing or invalid", ~youth.S4C10.isin(range(1, 17))),
        ("education missing or invalid", ~youth.S4C9.isin(range(1, 17))),
        ("training missing or invalid", ~youth.S4C11.isin(range(1, 5))),
        ("youth excluded: absence code 14", youth.S5C5.eq(14)),
        ("youth excluded: absent with missing reason", youth.S5C4.eq(1) & youth.S5C5.isna()),
    ]
    for name, mask in checks:
        add_check(rows, name, "youth 15–24", youth.loc[mask])
    pd.DataFrame(rows).to_csv(OUT / "skills_audit_routing.csv", index=False)
    ages = []
    for code, frame in youth.groupby("S4C9", dropna=False):
        n, weight, flag = safe_cell(len(frame), frame.Weights.sum())
        ages.append({"education_code": code, "n": n, "weighted_n": weight,
                     "median_age": frame.S4C6.median() if len(frame) >= 30 else "suppressed",
                     "flag": flag})
    pd.DataFrame(ages).to_csv(OUT / "skills_audit_education_ages.csv", index=False)
    counts = pd.read_csv(OUT / "skills_audit_counts.csv", keep_default_na=False)
    totals = counts.loc[counts.category.eq("ALL"), ["scope", "variable", "n", "weighted_n"]].rename(
        columns={"n": "total_n", "weighted_n": "total_weight"})
    shares = counts.merge(totals, on=["scope", "variable"], how="left")
    for col, total, output in [("n", "total_n", "sample_share"), ("weighted_n", "total_weight", "weighted_share")]:
        numerator = pd.to_numeric(shares[col], errors="coerce")
        denominator = pd.to_numeric(shares[total], errors="coerce")
        shares[output] = (numerator / denominator).round(6)
    shares.to_csv(OUT / "skills_audit_code_shares.csv", index=False)
    print("Disclosure-safe routing, age-plausibility and category-share tables written.")


if __name__ == "__main__":
    main()
