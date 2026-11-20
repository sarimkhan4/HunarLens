# What: creates the approved group-aware train/validation/test assignments.
# Why: every experiment must reuse the same household split.
# Viva: the test partition receives only row counts and class counts here.
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, REPORT_TABLES
from hunarlens.splits import file_hash, make_assignments


def main() -> None:
    """Save assignments and an aggregate class-balance report."""
    path = DATA_PROCESSED / "hunarlens_youth.csv"
    data = pd.read_csv(path, usecols=["group_id", "is_unemployed"])
    assignments = make_assignments(data, file_hash(path))
    summary = data.assign(split=assignments.split).groupby("split").is_unemployed.agg(rows="size", positives="sum", prevalence="mean")
    if (summary.prevalence - data.is_unemployed.mean()).abs().max() > 0.01:
        raise ValueError("Split prevalence differs by more than one percentage point.")
    assignments.to_csv(DATA_PROCESSED / "split_assignments.csv", index=False)
    REPORT_TABLES.mkdir(parents=True, exist_ok=True)
    summary.to_csv(REPORT_TABLES / "split_summary.csv")
    print(summary.to_string())
    print("Top 10 eligible youth per group:", data.groupby("group_id").size().nlargest(10).tolist())
    print("Top 10 household sizes:", pd.read_csv(path, usecols=["household_size"]).household_size.nlargest(10).tolist())


if __name__ == "__main__":
    main()
