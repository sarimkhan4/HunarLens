# What: records training-only rare age/enrolment and age/education combinations.
# Why: the app should warn for combinations with fewer than 20 training records.
# Viva: only boolean flags, not person records or group counts, leave the script.
from pathlib import Path
import json
import runpy
import sys

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, FEATURES, MODELS_DIR


def main() -> None:
    """Generate every supported combination, including absent ones, as a flag."""
    loader = runpy.run_path(str(ROOT / "scripts" / "compute_baselines.py"))
    train, _ = loader["load_train_validation"]()
    metadata = json.loads((MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))
    builder = joblib.load(MODELS_DIR / "final_pipeline.joblib").named_steps["features"]
    band = builder.transform(train[FEATURES])["age_band"]
    band_counts = train.assign(age_band=band).groupby(["age_band", "currently_enrolled"], observed=True).size()
    age_counts = train.groupby(["age", "education_level"], observed=True).size()
    rows = []
    for value in metadata["features"]["encoder_categories"]["age_band"]:
        for category in metadata["features"]["categorical"]["currently_enrolled"]:
            rows.append({"kind": "age_band_enrolment", "age_key": value, "category": category,
                         "rare": bool(band_counts.get((value, category), 0) < 20)})
    low, high = metadata["features"]["numeric"]["age"]
    for age in range(int(low), int(high) + 1):
        for category in metadata["features"]["categorical"]["education_level"]:
            rows.append({"kind": "age_education", "age_key": str(age), "category": category,
                         "rare": bool(age_counts.get((age, category), 0) < 20)})
    pd.DataFrame(rows).to_csv(DATA_PROCESSED / "rare_combinations.csv", index=False)
    print(f"Saved {len(rows)} boolean combination flags from training rows.")


if __name__ == "__main__":
    main()
