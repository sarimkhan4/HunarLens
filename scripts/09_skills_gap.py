# What: builds and checks an isolated survey dataset for the skills extension.
# Why: the published distributions must be reproduced before any analysis.
# Viva: the survey weight estimates population proportions, not model predictions.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.skills import safe_cell

RAW = ROOT / "data/raw/LFS 2024-25.sav web.dta"
INTERIM = ROOT / "data/interim/skills_audit_dataset.csv"
TABLES = ROOT / "reports/tables"
OCC_SOURCE = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-17.pdf"
EDU_SOURCE = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-7-3.pdf"
PBS_OCC = {1: 2.3, 2: 6.1, 3: 4.4, 4: 1.8, 5: 17.2, 6: 27.9, 7: 13.7, 8: 8.3, 9: 18.3}
# Table 7 expresses each employed/literacy/education cell as a percentage of
# the entire population age 10+, not as a percentage of employed persons.
PBS_EDU = {"illiterate": 15.1, "literate": 27.9, "literate_never": 0.5,
           "literate_below_matric": 13.5, "literate_matric": 6.4,
           "literate_intermediate": 3.6, "literate_degree": 3.9}


def load_builder():
    spec = spec_from_file_location("dataset_builder", ROOT / "scripts/01_build_dataset.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_waterfall(rows, step, frame):
    n, weighted, flag = safe_cell(len(frame), frame.Weights.sum())
    rows.append({"step": step, "n": n, "weighted_n": weighted, "flag": flag})


def build():
    builder = load_builder()
    columns = list(dict.fromkeys(builder.COLS + ["S4C9", "S4C10", "S4C11", "S4C81", "S4C82", "S5C12", "Province", "PCode", "EBCode"]))
    data = pd.read_stata(RAW, columns=columns, convert_categoricals=False)
    steps = []
    add_waterfall(steps, "all survey records", data)
    data = data.loc[~data.S5C5.eq(14)].copy()
    add_waterfall(steps, "after ambiguous absence code 14", data)
    data = data.loc[~(data.S5C4.eq(1) & data.S5C5.isna())].copy()
    add_waterfall(steps, "after absent worker with missing reason", data)
    data = data.loc[data.S4C6.ge(10)].copy()
    add_waterfall(steps, "age 10 and above", data)
    employed, unemployed = builder.provisional_status(data)
    add_waterfall(steps, "youth 15–24", data.loc[data.S4C6.between(15, 24)])
    add_waterfall(steps, "youth employed", data.loc[data.S4C6.between(15, 24) & employed])
    add_waterfall(steps, "youth unemployed", data.loc[data.S4C6.between(15, 24) & unemployed])
    pd.DataFrame(steps).to_csv(TABLES / "skills_row_waterfall.csv", index=False)
    result = pd.DataFrame({
        "age": data.S4C6, "sex": data.S4C5, "area": data.Region,
        "province": data.Province, "education": data.S4C9, "enrolment": data.S4C10,
        "training": data.S4C11, "can_read": data.S4C81, "can_write": data.S4C82,
        "employed": employed, "unemployed": unemployed, "weight": data.Weights,
        "occupation": (data.S5C12 // 1000).where(employed & data.S5C12.notna()),
        "psu": data.PCode.astype(str) + ":" + data.EBCode.astype("Int64").astype(str),
    })
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(INTERIM, index=False)
    return result


def reproduce(data):
    employed = data.loc[data.employed]
    rows = []
    for group, official in PBS_OCC.items():
        group_rows = employed.loc[employed.occupation.eq(group)]
        add_reproduction(rows, f"occupation_{group}", group_rows, employed.weight.sum(), official, OCC_SOURCE)
    literate = employed.can_read.eq(1) & employed.can_write.eq(1)
    masks = {"illiterate": ~literate, "literate": literate, "literate_never": literate & employed.education.eq(1),
             "literate_below_matric": literate & employed.education.between(2, 5),
             "literate_matric": literate & employed.education.eq(6),
             "literate_intermediate": literate & employed.education.eq(7),
             "literate_degree": literate & employed.education.between(8, 16)}
    for name, mask in masks.items():
        add_reproduction(rows, name, employed.loc[mask], data.weight.sum(), PBS_EDU[name], EDU_SOURCE)
    table = pd.DataFrame(rows)
    table.to_csv(TABLES / "skills_reproduction.csv", index=False)
    print(table.to_string(index=False))
    if table.status.eq("STOP").any():
        raise SystemExit("STOP: a reproduction difference exceeds one percentage point.")


def add_reproduction(rows, indicator, frame, denominator, official, url):
    n, _, flag = safe_cell(len(frame), frame.weight.sum())
    if n == "suppressed":
        rows.append({"indicator": indicator, "n": n, "our_value": "suppressed", "pbs_value": official,
                     "source_url": url, "difference_pp": "suppressed", "status": "STOP"})
        return
    value = 100 * frame.weight.sum() / denominator
    difference = abs(value - official)
    status = "STOP" if difference > 1 else "FLAG" if difference > 0.5 else "PASS"
    rows.append({"indicator": indicator, "n": n, "our_value": value, "pbs_value": official,
                 "source_url": url, "difference_pp": difference, "status": status, "flag": flag})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", required=True)
    parser.parse_args()
    TABLES.mkdir(parents=True, exist_ok=True)
    reproduce(build())


if __name__ == "__main__":
    main()
