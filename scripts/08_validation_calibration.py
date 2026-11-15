# What: summarises training enrolment and validation calibration by subgroup.
# Why: explain an enrolment association and identify large observed score gaps.
# Viva: these are unweighted group averages, not individual predictions or causes.
from pathlib import Path
import runpy
import sys

import joblib
import pandas as pd
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES, MODELS_DIR, REPORT_TABLES, TARGET


def main() -> None:
    """Read training and validation only; save aggregate tables without person rows."""
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    train, val = loader["load_train_validation"]()
    train = train.copy(); val = val.copy()
    if train.currently_enrolled.isna().any() or val.currently_enrolled.isna().any():
        raise ValueError("Missing enrolment needs a separate category before computing group rates.")
    train["enrolment"] = train.currently_enrolled.map(lambda x: "Not enrolled" if x == 1 else "Enrolled")
    summary = train.groupby("enrolment")[TARGET].agg(n="size", unemployed="sum", unemployment_rate="mean").reset_index()
    summary.to_csv(REPORT_TABLES / "enrolment_train_summary.csv", index=False)
    model = joblib.load(MODELS_DIR / "final_pipeline.joblib")
    with threadpool_limits(limits=1):
        val["probability"] = model.predict_proba(val[FEATURES])[:, 1]
    val["enrolment"] = val.currently_enrolled.map(lambda x: "Not enrolled" if x == 1 else "Enrolled")
    val["sex"] = val.sex.map({1: "Male", 2: "Female"})
    val["area"] = val.area.map({1: "Rural", 2: "Urban"})
    cells = val.groupby(["enrolment", "sex", "area"], dropna=False).agg(
        n=(TARGET, "size"), mean_probability=("probability", "mean"), observed_rate=(TARGET, "mean")).reset_index()
    cells = cells.loc[cells.n >= 30].copy()
    cells["gap"] = cells.mean_probability - cells.observed_rate
    cells["absolute_gap_over_0_05"] = cells.gap.abs() > .05
    cells.to_csv(REPORT_TABLES / "validation_calibration_cells.csv", index=False)
    print("TRAINING ENROLMENT", summary.to_string(index=False), sep="\n")
    print("VALIDATION CALIBRATION", cells.to_string(index=False), sep="\n")


if __name__ == "__main__":
    main()
