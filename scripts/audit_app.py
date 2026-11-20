# What: prints the requested train/validation and interface audit.
# Why: compare model behaviour without opening the test split or saving person rows.
# Viva: partial profiles, observed subgroup rates and individual predictions differ.
from pathlib import Path
import json
import runpy
import sys

import joblib
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.app_utils import LABELS, build_input, predict_probability, risk_label
from hunarlens.config import FEATURES, TARGET


def print_sex_area(model, metadata, census):
    """Use canonical metadata choices for the sex-by-area comparisons."""
    base = metadata["reference_values"]
    categories = metadata["features"]["categorical"]
    rows = []
    for age in [base["age"], 18, 24]:
        for sex in categories["sex"]:
            for area in categories["area"]:
                row = build_input({**base, "age": age, "sex": sex, "area": area}, metadata, census)
                rows.append({"age": int(age), "sex": LABELS["sex"][int(sex)], "sex_value": repr(row.sex.iloc[0]),
                             "area": LABELS["area"][int(area)], "area_value": repr(row.area.iloc[0]),
                             "probability": f"{predict_probability(model, row):.4f}"})
    print("SEX AREA", pd.DataFrame(rows).to_string(index=False), sep="\n", flush=True)


def print_enrolment(model, metadata, census, train, validation):
    """Show training rates, observed validation predictions and plausible profiles."""
    categories = metadata["features"]["categorical"]["currently_enrolled"]
    profiles = {1: (20, 1), 4: (15, 3), 5: (15, 4), 6: (16, 5), 7: (18, 6),
                8: (22, 7), 9: (22, 7), 10: (22, 7), 11: (22, 7), 12: (22, 7),
                13: (22, 7), 14: (24, 13), 15: (24, 14), 16: (24, 14)}
    validation = validation.copy()
    validation["predicted_probability"] = model.predict_proba(validation[FEATURES])[:, 1]
    rows = []
    for code in categories:
        training = train.loc[train.currently_enrolled.eq(code)]
        held = validation.loc[validation.currently_enrolled.eq(code)]
        age, education = profiles[int(code)]
        row = build_input({**metadata["reference_values"], "currently_enrolled": code,
                           "age": age, "education_level": education}, metadata, census)
        rows.append({"code": int(code), "category": LABELS["currently_enrolled"][int(code)],
                     "train_n": len(training), "train_rate": f"{training[TARGET].mean():.4f}" if len(training) else "—",
                     "val_n": len(held), "val_mean": f"{held.predicted_probability.mean():.4f}" if len(held) else "—",
                     "profile_age": age, "profile_education": education,
                     "profile_probability": f"{predict_probability(model, row):.4f}"})
    print("ENROLMENT", pd.DataFrame(rows).to_string(index=False), sep="\n", flush=True)


def print_insights():
    """Compare the actual rendered dataframes against their saved sources."""
    app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=60).run()
    app.sidebar.radio[0].set_value("Insights").run()
    experiments = pd.read_csv(ROOT / "reports/tables/experiments.csv")
    expected = experiments.loc[experiments.exp_id.eq("E4"), ["model", "cv_ap_mean", "val_f1_best", "threshold"]].rename(
        columns={"model": "Model", "cv_ap_mean": "Grouped CV PR-AUC", "val_f1_best": "Validation F1", "threshold": "Tuned threshold"})
    sources = [expected, pd.read_csv(ROOT / "reports/tables/test_metrics.csv"),
               pd.read_csv(ROOT / "reports/tables/test_bootstrap_ci.csv"), pd.read_csv(ROOT / "reports/tables/test_subgroups.csv")]
    names = ["Model comparison", "Test metrics and dummy", "95% intervals", "Subgroups"]
    checks = [{"check": name, "result": "PASS" if app.dataframe[i].value.reset_index(drop=True).equals(source.reset_index(drop=True)) else "FAIL"}
              for i, (name, source) in enumerate(zip(names, sources))]
    doc = (ROOT / "docs/test_findings.md").read_text(encoding="utf-8")
    for value in ["0.360", "0.303", "0.123", "0.127", "2.81", "0.87", "0.328–0.393"]:
        checks.append({"check": f"Findings value {value}", "result": "PASS" if value in doc else "FAIL"})
    print("INSIGHTS CHECKS", pd.DataFrame(checks).to_string(index=False), sep="\n")
    print("INSIGHTS MODELS", app.dataframe[0].value.to_string(index=False), sep="\n")
    print("INSIGHTS TEST METRICS", app.dataframe[1].value.to_string(index=False), sep="\n")
    print("INSIGHTS F1 CI", app.dataframe[2].value.query("metric == 'f1'").to_string(index=False), sep="\n")
    app.sidebar.radio[0].set_value("About and limits").run()
    print("ABOUT FULL TEXT", "\n".join(item.value for item in app.markdown), sep="\n", flush=True)


def print_fixtures(model, metadata, census):
    """Print synthetic complete app inputs and their frozen outputs."""
    base = metadata["reference_values"]
    fixtures = {"Low": {"age": 18, "education_level": 6, "currently_enrolled": 7},
                "Typical": {},
                "High": {"age": 22, "sex": 2, "area": 2, "education_level": 13, "currently_enrolled": 1}}
    for name, changes in fixtures.items():
        row = build_input({**base, **changes}, metadata, census)
        probability = predict_probability(model, row)
        print(f"FIXTURE {name}: probability={probability:.6f}, band={risk_label(probability, metadata)}, "
              f"flagged={probability >= metadata['threshold_f1']}")
        values = {name: row[name].iloc[0].item() for name in row.columns}
        print(json.dumps(values, sort_keys=True), flush=True)


def main():
    metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    model = joblib.load(ROOT / "models/final_pipeline.joblib")
    census = pd.read_csv(ROOT / "data/processed/census_lookup.csv")
    loader = runpy.run_path(str(ROOT / "scripts/compute_baselines.py"))
    train, validation = loader["load_train_validation"]()
    with threadpool_limits(limits=1):
        print_sex_area(model, metadata, census)
        print_enrolment(model, metadata, census, train, validation)
        print_insights()
        print_fixtures(model, metadata, census)


if __name__ == "__main__":
    main()
