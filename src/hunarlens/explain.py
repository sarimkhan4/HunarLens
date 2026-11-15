# What: computes validation permutation importance and individual what-if changes.
# Why: explain the fitted model without exposing household identifiers.
# Viva: shuffling breaks association with the outcome, not a causal effect.
from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score

from hunarlens.config import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, RANDOM_STATE

GROUPS = {
    "Age": ["age"], "Sex and area": ["sex", "area"],
    "Education": ["education_level", "can_read", "can_write"],
    "Enrolment": ["currently_enrolled"], "Training": ["has_training"],
    "Marital and relationship": ["marital_status", "relationship_to_head"],
    "Household": ["household_size", "children_under_15", "other_youth_15_24", "head_sex", "head_education"],
    "Region": ["province", "census_density", "census_urban_proportion", "census_household_size"],
    "Geography": ["province", "area", "census_density", "census_urban_proportion", "census_household_size"],
    "Sex": ["sex"],
}


def reference_values(train: pd.DataFrame) -> dict[str, Any]:
    """Use only training medians and modes, with deterministic mode tie-breaking."""
    values = {name: float(train[name].median()) for name in NUMERIC_FEATURES}
    for name in CATEGORICAL_FEATURES:
        value = train[name].mode(dropna=True).iloc[0]
        values[name] = value.item() if isinstance(value, np.generic) else value
    return values


def local_what_if(model: Any, row: pd.DataFrame, references: dict, features: list[str],
                  top_k: int | None = None) -> pd.DataFrame:
    """Replace the first k ranked raw inputs, reporting new risk minus original risk."""
    if len(row) != 1 or not set(features) <= set(FEATURES) or (top_k is not None and top_k < 1):
        raise ValueError("Provide one row and approved features only.")
    original = float(model.predict_proba(row[FEATURES])[0, 1])
    results = []
    for name in features[:top_k]:
        altered = row[FEATURES].copy()
        altered.loc[altered.index[0], name] = references[name]
        probability = float(model.predict_proba(altered)[0, 1])
        results.append({"feature": name, "reference_value": references[name],
                        "original_probability": original, "new_probability": probability,
                        "change": probability - original})
    return pd.DataFrame(results)


def feature_importance(model: Any, X: pd.DataFrame, y: pd.Series, repeats: int = 20) -> pd.DataFrame:
    """Shuffle each raw field while scoring the full fitted pipeline."""
    result = permutation_importance(model, X[FEATURES], y, scoring="average_precision",
                                    n_repeats=repeats, random_state=RANDOM_STATE, n_jobs=1)
    return pd.DataFrame({"feature": FEATURES, "importance_mean": result.importances_mean,
                         "importance_std": result.importances_std}).sort_values("importance_mean", ascending=False)


def group_importance(model: Any, X: pd.DataFrame, y: pd.Series, repeats: int = 20) -> pd.DataFrame:
    """Shuffle all fields in each group with the same row permutation."""
    X = X[FEATURES].reset_index(drop=True)
    baseline = average_precision_score(y, model.predict_proba(X)[:, 1])
    rng = np.random.default_rng(RANDOM_STATE)
    rows = []
    for name, columns in GROUPS.items():
        drops = []
        for _ in range(repeats):
            permuted = X.copy()
            permuted[columns] = X.iloc[rng.permutation(len(X))][columns].to_numpy()
            drops.append(baseline - average_precision_score(y, model.predict_proba(permuted)[:, 1]))
        rows.append({"group": name, "features": ", ".join(columns), "importance_mean": np.mean(drops),
                     "importance_std": np.std(drops), "baseline_ap": baseline})
        print(f"Group importance complete: {name}", flush=True)
    return pd.DataFrame(rows).sort_values("importance_mean", ascending=False)


def average_predictions(model: Any, X: pd.DataFrame, scenarios: list[dict]) -> pd.DataFrame:
    """Change named raw fields for all validation rows and average predictions."""
    results = []
    for scenario in scenarios:
        altered = X[FEATURES].copy()
        for name, value in scenario.items():
            altered[name] = value
        results.append({**scenario, "mean_probability": model.predict_proba(altered)[:, 1].mean()})
    return pd.DataFrame(results)
