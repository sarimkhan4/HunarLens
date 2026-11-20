# What: computes validation-only changes between model input profiles.
# Why: multiple education codes can belong to the same next band.
# Viva: these predictions describe model associations, not causal effects.
from pathlib import Path
import json
import sys

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.app_utils import build_input, is_rare_combination, validate_inputs
from hunarlens.config import FEATURES

BANDS = {1: range(1, 2), 2: range(2, 6), 3: range(6, 7), 4: range(7, 8), 5: range(8, 17)}
REPEATS = 1000


def average_codes(probabilities, frequencies):
    """Average candidate predictions with training-code frequencies."""
    p = np.asarray(probabilities, dtype=float)
    w = np.asarray(frequencies, dtype=float)
    low, high = float(p.min()), float(p.max())
    return float(np.clip(np.average(p, weights=w), low, high)), low, high


def selected_input(values, metadata, flags, census):
    """Construct only valid, non-rare scenarios through the app's builder."""
    if validate_inputs(values, metadata) or is_rare_combination(values, flags):
        return None
    return build_input(values, metadata, census)


def sample_profiles():
    data = pd.read_csv(ROOT / "data/processed/hunarlens_youth.csv")
    split = pd.read_csv(ROOT / "data/processed/split_assignments.csv")
    survey = pd.read_csv(ROOT / "data/interim/skills_audit_dataset.csv")
    survey = survey.loc[survey.age.between(15, 24) & (survey.employed | survey.unemployed)].reset_index(drop=True)
    if len(survey) != len(data) or not np.array_equal(split.row_id.to_numpy(), np.arange(len(data))):
        raise RuntimeError("STOP: survey/model row alignment is not verified.")
    indexes = split.index[split.split.isin(["train", "val"])]
    columns = [("age", "age"), ("sex", "sex"), ("education", "education_level"),
               ("enrolment", "currently_enrolled"), ("area", "area"), ("province", "province")]
    if not all(np.array_equal(survey.loc[indexes, a], data.loc[indexes, b]) for a, b in columns):
        raise RuntimeError("STOP: survey/model profiles do not align.")
    train = data.loc[split.split.eq("train"), "education_level"]
    validation = data.loc[split.split.eq("val")].copy()
    validation["weight"] = survey.loc[validation.index, "weight"]
    validation["psu"] = survey.loc[validation.index, "psu"]
    return train.value_counts().to_dict(), validation


def predictions(model, validation, frequencies, metadata, census, flags):
    rows, references = [], []
    for index, profile in validation.iterrows():
        values = profile[FEATURES].to_dict()
        base = selected_input(values, metadata, flags, census)
        if base is None:
            continue
        rows.append(base)
        references.append((index, "base", None, 1))
        trained = {**values, "has_training": 1}
        row = selected_input(trained, metadata, flags, census)
        if row is not None:
            rows.append(row)
            references.append((index, "training", 1, 1))
        current = int(values["education_level"])
        band = next((number for number, codes in BANDS.items() if current in codes), None)
        if band is None or band == 5:
            continue
        for code in BANDS[band + 1]:
            if frequencies.get(float(code), 0) == 0:
                continue
            row = selected_input({**values, "education_level": code}, metadata, flags, census)
            if row is not None:
                rows.append(row)
                references.append((index, "education", code, frequencies[float(code)]))
    probabilities = model.predict_proba(pd.concat(rows, ignore_index=True)[FEATURES])[:, 1]
    result = pd.DataFrame(references, columns=["index", "scenario", "code", "frequency"])
    result["probability"] = probabilities
    return result


def profile_changes(predicted, validation):
    base = predicted.loc[predicted.scenario.eq("base")].set_index("index").probability
    rows = []
    for index, group in predicted.loc[~predicted.scenario.eq("base")].groupby(["index", "scenario"]):
        i, scenario = index
        mean, low, high = average_codes(group.probability, group.frequency)
        rows.append({"index": i, "scenario": scenario, "difference": mean - base.loc[i],
                     "min": low - base.loc[i], "max": high - base.loc[i]})
    return pd.DataFrame(rows).join(validation[["weight", "psu", "sex", "area", "education_level"]], on="index")


def main():
    frequencies, validation = sample_profiles()
    metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    census = pd.read_csv(ROOT / "data/processed/census_lookup.csv")
    flags = pd.read_csv(ROOT / "data/processed/rare_combinations.csv", dtype={"age_key": str, "rare": bool})
    model = joblib.load(ROOT / "models/final_pipeline.joblib")
    predicted = predictions(model, validation, frequencies, metadata, census, flags)
    changes = profile_changes(predicted, validation)
    # Aggregate-only output: PSU identifiers and individual profiles never leave memory.
    rows = []
    for scenario in ["education", "training"]:
        scenario_rows = changes.loc[changes.scenario.eq(scenario)]
        for key in ["overall", "sex_area", "education_band"]:
            val = validation.copy()
            val["group"] = "overall" if key == "overall" else (
                val.sex.astype(str) + "/" + val.area.astype(str) if key == "sex_area" else
                val.education_level.map(lambda x: next((str(b) for b, codes in BANDS.items() if int(x) in codes), "unknown")))
            for group, denominator in val.groupby("group"):
                selected = scenario_rows.loc[scenario_rows["index"].isin(denominator.index)]
                n = len(selected)
                if n == 0:
                    rows.append({"scenario": scenario, "grouping": key, "group": group, "n": 0,
                                 "coverage": 0, "mean": "—", "minimum": "—", "maximum": "—",
                                 "ci_low": "—", "ci_high": "—", "flag": "no valid scenario"})
                    continue
                if n < 30:
                    rows.append({"scenario": scenario, "grouping": key, "group": group, "n": "n<30",
                                 "coverage": "n<30", "mean": "n<30", "minimum": "n<30", "maximum": "n<30",
                                 "ci_low": "n<30", "ci_high": "n<30", "flag": "suppressed: n<30"})
                    continue
                psus = selected.psu.unique()
                rng = np.random.default_rng(42)
                clusters = selected.groupby("psu").apply(lambda x: pd.Series({"w": x.weight.sum(), "v": (x.weight*x.difference).sum()}), include_groups=False)
                draw = rng.multinomial(len(psus), np.full(len(psus), 1 / len(psus)), size=REPEATS)
                draws = (draw @ clusters.v.to_numpy()) / (draw @ clusters.w.to_numpy())
                rows.append({"scenario": scenario, "grouping": key, "group": group, "n": n,
                             "coverage": selected.weight.sum()/denominator.weight.sum(),
                             "mean": np.average(selected.difference, weights=selected.weight),
                             "minimum": np.average(selected["min"], weights=selected.weight),
                             "maximum": np.average(selected["max"], weights=selected.weight),
                             "ci_low": np.quantile(draws, .025), "ci_high": np.quantile(draws, .975),
                             "flag": "unreliable: n < 50" if n < 50 else ""})
    pd.DataFrame(rows).to_csv(ROOT / "reports/tables/skills_model_shift.csv", index=False)
    print("Validation model-shift table generated; inputs were not saved.")


if __name__ == "__main__":
    main()
