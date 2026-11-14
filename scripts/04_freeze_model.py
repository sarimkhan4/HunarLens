# What: fits and freezes the approved model using training and validation only.
# Why: calibration and thresholds need a held-out set; the test set stays sealed.
# Viva: the classifier is fitted on train, while validation chooses calibration and cut-offs.
from pathlib import Path
import importlib.metadata
import json
import runpy
import sys
from datetime import date

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_recall_curve, precision_score, recall_score,
                             roc_auc_score)
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import (CATEGORICAL_FEATURES, FEATURES, MODELS_DIR, NUMERIC_FEATURES,
                              RANDOM_STATE, REPORT_FIGURES, REPORT_TABLES, TARGET)
from hunarlens.pipeline import build_model_pipeline

PARAMS = dict(max_iter=200, learning_rate=0.06, max_depth=None, max_leaf_nodes=15,
              min_samples_leaf=50, l2_regularization=10, early_stopping=False,
              class_weight=None, random_state=RANDOM_STATE)
MIN_BRIER_IMPROVEMENT = 0.02
F1_TOLERANCE = 0.005
MIN_SCREEN_RECALL = 0.60


def expected_calibration_error(y: np.ndarray, scores: np.ndarray) -> float:
    """Summarise the weighted absolute error in ten fixed probability bins."""
    bins = np.minimum((scores * 10).astype(int), 9)
    return float(sum(np.mean(bins == i) * abs(y[bins == i].mean() - scores[bins == i].mean())
                     for i in range(10) if np.any(bins == i)))


def select_thresholds(y: np.ndarray, scores: np.ndarray) -> dict:
    """Use the midpoint of the near-optimal range and the strictest recall threshold."""
    precision, recall, thresholds = precision_recall_curve(y, scores)
    f1 = np.divide(2 * precision[:-1] * recall[:-1], precision[:-1] + recall[:-1],
                   out=np.zeros_like(thresholds), where=(precision[:-1] + recall[:-1]) != 0)
    eligible = thresholds[f1 >= f1.max() - F1_TOLERANCE]
    screening = thresholds[recall[:-1] >= MIN_SCREEN_RECALL]
    return {"f1": float((eligible.min() + eligible.max()) / 2),
            "f1_range": [float(eligible.min()), float(eligible.max())],
            "maximum_f1": float(f1.max()), "screening": float(screening.max())}


def validation_metrics(y: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    """Report classification and ranking measures on validation labels."""
    predicted = scores >= threshold
    order = np.random.default_rng(RANDOM_STATE).permutation(len(scores))
    order = order[np.argsort(-scores[order], kind="stable")]
    n = int(np.ceil(len(y) * 0.1))
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {"precision": float(precision_score(y, predicted, zero_division=0)),
            "recall": float(recall_score(y, predicted, zero_division=0)),
            "f1": float(f1_score(y, predicted, zero_division=0)),
            "pr_auc": float(average_precision_score(y, scores)),
            "roc_auc": float(roc_auc_score(y, scores)),
            "lift_at_10_percent": float(y[order[:n]].mean() / y.mean()),
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}


def compare_calibration(y: np.ndarray, raw: np.ndarray, sigmoid: np.ndarray) -> tuple[pd.DataFrame, bool]:
    """Require both a 2% relative Brier reduction and a lower fixed-bin error."""
    rows = [{"method": name, "brier": brier_score_loss(y, scores),
             "ece_10_fixed_bins": expected_calibration_error(y, scores)}
            for name, scores in [("raw", raw), ("sigmoid", sigmoid)]]
    table = pd.DataFrame(rows)
    improve = (rows[1]["brier"] <= rows[0]["brier"] * (1 - MIN_BRIER_IMPROVEMENT)
               and rows[1]["ece_10_fixed_bins"] < rows[0]["ece_10_fixed_bins"])
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, scores in [("Raw", raw), ("Sigmoid", sigmoid)]:
        observed, predicted = calibration_curve(y, scores, n_bins=10, strategy="quantile")
        ax.plot(predicted, observed, marker="o", label=name)
    ax.plot([0, 1], [0, 1], "--", color="black", label="Perfect calibration")
    ax.set(xlabel="Mean predicted probability", ylabel="Observed unemployed fraction",
           title="Validation calibration (sigmoid fitted on these labels)", xlim=(0, 1), ylim=(0, 1))
    ax.legend(); fig.tight_layout()
    fig.savefig(REPORT_FIGURES / "validation_calibration.png", dpi=200); plt.close(fig)
    return table, bool(improve)


def training_metadata(train: pd.DataFrame, pipeline: object) -> dict:
    """Record observed input ranges and the fitted encoder's actual categories."""
    transformer = pipeline.named_steps["preprocess"]
    encoder = transformer.named_transformers_["categorical"].named_steps["encode"]
    columns = transformer.transformers_[1][2]
    categories = {name: [x.item() if isinstance(x, np.generic) else x for x in values]
                  for name, values in zip(columns, encoder.categories_)}
    return {"numeric": {c: [float(train[c].min()), float(train[c].max())] for c in NUMERIC_FEATURES},
            "categorical": {c: categories[c] for c in CATEGORICAL_FEATURES},
            "encoder_categories": categories}


def main() -> None:
    """Fit once on train, select validation-only calibration and freeze artifacts."""
    for path in [MODELS_DIR, REPORT_FIGURES, REPORT_TABLES]:
        path.mkdir(parents=True, exist_ok=True)
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    train, val = loader["load_train_validation"]()
    y = val[TARGET].to_numpy()
    model = build_model_pipeline(HistGradientBoostingClassifier(**PARAMS))
    with threadpool_limits(limits=1):
        model.fit(train[FEATURES], train[TARGET])
        raw = model.predict_proba(val[FEATURES])[:, 1]
        calibrated = CalibratedClassifierCV(estimator=FrozenEstimator(model), method="sigmoid")
        calibrated.fit(val[FEATURES], y)
        sigmoid = calibrated.predict_proba(val[FEATURES])[:, 1]
    table, use_sigmoid = compare_calibration(y, raw, sigmoid)
    table.to_csv(REPORT_TABLES / "calibration_validation.csv", index=False)
    scores = sigmoid if use_sigmoid else raw
    if average_precision_score(y, scores) > 0.4:
        raise ValueError("Validation PR-AUC exceeds 0.4: investigate possible leakage before freezing.")
    thresholds = select_thresholds(y, scores)
    metrics = {name: validation_metrics(y, scores, thresholds[name]) for name in ["f1", "screening"]}
    results = pd.DataFrame([{"threshold_type": name, "threshold": thresholds[name],
                             "interpretation": "optimistic: threshold chosen on the same labels",
                             "prevalence": float(y.mean()), **metrics[name]} for name in metrics])
    results.to_csv(REPORT_TABLES / "stage6_thresholds.csv", index=False)
    bands = {"high_min": float(np.quantile(scores, 0.9)),
             "elevated_min": float(np.quantile(scores, 0.7)),
             "definition": "High >= high_min; Elevated >= elevated_min; Lower otherwise; ties may alter proportions"}
    features = training_metadata(train, model)
    versions = {p: importlib.metadata.version(p) for p in ["numpy", "pandas", "scikit-learn", "joblib", "streamlit"]}
    versions["python"] = sys.version.split()[0]
    metadata = {"model": "HistGradientBoostingClassifier", "model_parameters": PARAMS,
                "model_name": "HistGradientBoostingClassifier", "trained_on": date.today().isoformat(),
                "python_version": versions["python"], "sklearn_version": versions["scikit-learn"],
                "random_state": RANDOM_STATE, "threshold_f1": thresholds["f1"],
                "threshold_screening": thresholds["screening"], "metrics_val": metrics["f1"],
                "census_lookup": "data/processed/census_lookup.csv",
                "feature_names": FEATURES, "features": features, "province_values": features["categorical"]["province"],
                "area_values": features["categorical"]["area"], "prevalence_train": float(train[TARGET].mean()),
                "prevalence_validation": float(y.mean()), "calibration": "sigmoid" if use_sigmoid else "raw",
                "calibration_comparison": table.to_dict(orient="records"), "thresholds": thresholds,
                "validation_metrics_optimistic": metrics, "risk_bands": bands, "versions": versions}
    output = MODELS_DIR / "final_pipeline.joblib"
    joblib.dump(calibrated if use_sigmoid else model, output, compress=3)
    if output.stat().st_size >= 25_000_000:
        raise ValueError("Frozen model exceeds 25 MB.")
    (MODELS_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2, allow_nan=False), encoding="utf-8")
    print("Calibration (validation, sigmoid fitted on these labels):\n", table.to_string(index=False))
    print("Selected:", metadata["calibration"], "\nThresholds:\n", results.to_string(index=False))
    print("Near-optimal F1 range:", thresholds["f1_range"], "max F1:", thresholds["maximum_f1"])
    print("Risk bands:", bands, "\nModel bytes:", output.stat().st_size)


if __name__ == "__main__":
    main()
