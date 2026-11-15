# What: generates validation-only explanations for the frozen model.
# Why: report model reliance and prediction patterns without touching test observations.
# Viva: all permutations operate on raw features through the full fitted pipeline.
from pathlib import Path
import json
import runpy
import sys

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES, MODELS_DIR, REPORT_FIGURES, REPORT_TABLES, TARGET
from hunarlens.explain import average_predictions, feature_importance, group_importance, reference_values


def importance_plot(table: pd.DataFrame, label: str, filename: str, title: str) -> None:
    """Draw mean validation AP loss with permutation standard deviations."""
    table = table.iloc[:15].iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, max(4, len(table) * .35)))
    ax.barh(table[label], table.importance_mean, xerr=table.importance_std, color="#277da1", capsize=3)
    ax.axvline(0, color="black", linewidth=.8)
    ax.set(title=title, xlabel="Decrease in validation average precision", ylabel=label.title())
    fig.tight_layout(); fig.savefig(REPORT_FIGURES / filename, dpi=200); plt.close(fig)


def partial_plots(model: object, val: pd.DataFrame, metadata: dict) -> None:
    """Plot average predictions after setting a raw input across validation rows."""
    inputs = val[FEATURES]
    scenarios = {"age": [{"age": x} for x in range(15, 25)],
                 "education_level": [{"education_level": x} for x in metadata["features"]["categorical"]["education_level"]],
                 "currently_enrolled": [{"currently_enrolled": x} for x in metadata["features"]["categorical"]["currently_enrolled"]],
                 "sex_area": [{"sex": s, "area": a} for s in metadata["sex_values"] for a in metadata["area_values"]]}
    for name, changes in scenarios.items():
        result = average_predictions(model, inputs, changes)
        result.to_csv(REPORT_TABLES / f"partial_{name}.csv", index=False)
        labels = (result.sex.astype(str) + " / " + result.area.astype(str)) if name == "sex_area" else result[name].astype(str)
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(range(len(result)), result.mean_probability, marker="o", color="#277da1")
        ax.axhline(val[TARGET].mean(), color="#b64b39", linestyle="--", label="Validation prevalence")
        ax.set_xticks(range(len(result)), labels, rotation=45 if name != "age" else 0, ha="right" if name != "age" else "center")
        ax.set(xlabel="Sex / area (survey codes)" if name == "sex_area" else name.replace("_", " "),
               ylabel="Mean predicted unemployment probability", title=f"Validation prediction profile: {name.replace('_', ' ')}")
        ax.legend(); fig.tight_layout(); fig.savefig(REPORT_FIGURES / f"partial_{name}.png", dpi=200); plt.close(fig)


def main() -> None:
    """Explain a frozen estimator using train references and validation labels only."""
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    train, val = loader["load_train_validation"]()
    model = joblib.load(MODELS_DIR / "final_pipeline.joblib")
    path = MODELS_DIR / "metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["reference_values"] = reference_values(train)
    metadata["sex_values"] = metadata["features"]["categorical"]["sex"]
    path.write_text(json.dumps(metadata, indent=2, allow_nan=False), encoding="utf-8")
    with threadpool_limits(limits=1):
        base = average_precision_score(val[TARGET], model.predict_proba(val[FEATURES])[:, 1])
        individual = feature_importance(model, val[FEATURES], val[TARGET])
        individual["baseline_ap"] = base
        individual["validation_prevalence"] = val[TARGET].mean()
        individual.to_csv(REPORT_TABLES / "permutation_importance.csv", index=False)
        print("Individual permutation importance complete", flush=True)
        groups = group_importance(model, val[FEATURES], val[TARGET])
        groups["validation_prevalence"] = val[TARGET].mean()
        groups.to_csv(REPORT_TABLES / "grouped_permutation_importance.csv", index=False)
        importance_plot(individual, "feature", "permutation_importance.png", "Validation feature permutation importance")
        consistent = groups[~groups["group"].isin(["Region", "Sex and area"])]
        importance_plot(consistent, "group", "grouped_permutation_importance.png", "Validation grouped permutation importance")
        partial_plots(model, val, metadata)
    print("Validation AP:", base, "prevalence:", val[TARGET].mean())
    print(individual.to_string(index=False)); print(groups.to_string(index=False))


if __name__ == "__main__":
    main()
