# What: scores the approved model once and evaluates saved test predictions.
# Why: a locked holdout needs a permanent, auditable prediction record.
# Viva: later metrics and figures read the same saved probabilities, never refit HGB.
from datetime import datetime
from pathlib import Path
import hashlib
import json
import os
import re
import runpy
import sys

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, FEATURES, GROUP, MODELS_DIR, RANDOM_STATE, REPORT_FIGURES, REPORT_TABLES, TARGET
from hunarlens.pipeline import build_model_pipeline
from hunarlens.splits import load_assignments

PREDICTIONS = DATA_PROCESSED / "test_predictions.csv"
RECEIPT = DATA_PROCESSED / "test_evaluation_receipt.json"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
BOOTSTRAP_REPEATS = 1000


def sha256(path: Path) -> str:
    """Hash file bytes for the model and saved prediction record."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_model() -> str:
    """Refuse to use an artifact that differs from the recorded approved hash."""
    text = DECISIONS.read_text(encoding="utf-8")
    matches = re.findall(r"SHA-256 of `models/final_pipeline\.joblib` is `([0-9a-f]{64})`", text)
    if len(set(matches)) != 1:
        raise ValueError("Expected exactly one approved model SHA-256 in DECISIONS.md.")
    actual = sha256(MODELS_DIR / "final_pipeline.joblib")
    if actual != matches[0]:
        raise ValueError("Frozen model SHA-256 does not match DECISIONS.md; test remains sealed.")
    return actual


def save_test_predictions(model_hash: str, metadata: dict) -> None:
    """Open test once, after creating a durable receipt and logging the opening."""
    if RECEIPT.exists() or PREDICTIONS.exists():
        raise RuntimeError("A test opening or prediction file already exists; refusing to score again.")
    if "## test evaluation — first test opening" in DECISIONS.read_text(encoding="utf-8"):
        raise RuntimeError("The decisions log records a previous test opening; refusing to score again.")
    model = joblib.load(MODELS_DIR / "final_pipeline.joblib")
    loader = runpy.run_path(str(ROOT / "scripts" / "compute_baselines.py"))
    train, _ = loader["load_train_validation"]()
    dummy = build_model_pipeline(DummyClassifier(strategy="stratified", random_state=RANDOM_STATE))
    with threadpool_limits(limits=1):
        dummy.fit(train[FEATURES], train[TARGET])
    data_path = DATA_PROCESSED / "hunarlens_youth.csv"
    assignments = load_assignments(DATA_PROCESSED / "split_assignments.csv", data_path)
    splits = assignments.split.to_numpy()
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    receipt = {"opened_at": started, "model_sha256": model_hash, "status": "opening_started"}
    with RECEIPT.open("x", encoding="utf-8") as target:
        json.dump(receipt, target, indent=2)
    with DECISIONS.open("a", encoding="utf-8") as target:
        target.write(f"\n## test evaluation — first test opening\n\n- Test split first opened at {started}; "
                     f"frozen model SHA-256 `{model_hash}`. The opening is recorded before parsing test rows; "
                     "the saved predictions are the sole source for later test analyses.\n")
    test = pd.read_csv(data_path, usecols=[*FEATURES, GROUP, TARGET],
                       skiprows=lambda line: line > 0 and (line > len(splits) or splits[line - 1] != "test"))
    if len(test) != int((splits == "test").sum()):
        raise ValueError("Test row count does not match assignments. The test was opened; do not rescore.")
    with threadpool_limits(limits=1):
        test["probability"] = model.predict_proba(test[FEATURES])[:, 1]
        test["dummy_probability"] = dummy.predict_proba(test[FEATURES])[:, 1]
    high = metadata["risk_bands"]["high_min"]
    elevated = metadata["risk_bands"]["elevated_min"]
    test["risk_band"] = np.select([test.probability >= high, test.probability >= elevated],
                                  ["High", "Elevated"], default="Lower")
    temporary = PREDICTIONS.with_suffix(".tmp")
    test.to_csv(temporary, index=False)
    os.replace(temporary, PREDICTIONS)
    receipt.update(status="complete", predictions_sha256=sha256(PREDICTIONS), rows=len(test))
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


def load_predictions(model_hash: str) -> pd.DataFrame:
    """On reruns use only the saved, hash-checked predictions; never rescore."""
    if not RECEIPT.exists() or not PREDICTIONS.exists():
        raise RuntimeError("Incomplete test receipt or predictions. Do not reopen test automatically.")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if receipt.get("status") != "complete" or receipt.get("model_sha256") != model_hash:
        raise RuntimeError("Test receipt is incomplete or belongs to a different model.")
    if sha256(PREDICTIONS) != receipt.get("predictions_sha256"):
        raise RuntimeError("Saved test predictions do not match the receipt.")
    return pd.read_csv(PREDICTIONS)


def top_lift(y: np.ndarray, scores: np.ndarray, fraction: float) -> float:
    """Break equal-score ties reproducibly before computing top-fraction lift."""
    order = np.random.default_rng(RANDOM_STATE).permutation(len(y))
    order = order[np.argsort(-scores[order], kind="stable")]
    size = max(1, int(np.ceil(fraction * len(y))))
    return float(y[order[:size]].mean() / y.mean()) if y.mean() else np.nan


def metrics(y: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    """Compute positive-class metrics and the confusion matrix on saved scores."""
    pred = scores >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    two_classes = len(np.unique(y)) == 2
    return {"n": len(y), "positives": int(y.sum()), "prevalence": float(y.mean()),
            "f1": f1_score(y, pred, zero_division=0), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred, zero_division=0),
            "pr_auc": average_precision_score(y, scores) if two_classes else np.nan,
            "roc_auc": roc_auc_score(y, scores) if two_classes else np.nan,
            "accuracy": accuracy_score(y, pred), "lift_10": top_lift(y, scores, .1),
            "lift_20": top_lift(y, scores, .2), "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}


def metric_table(data: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Evaluate both approved thresholds and the single stratified dummy."""
    y = data[TARGET].to_numpy()
    results = []
    for name, column, threshold in [("HGB F1", "probability", thresholds["f1"]),
                                    ("HGB screening", "probability", thresholds["screening"]),
                                    ("Stratified Dummy", "dummy_probability", .5)]:
        results.append({"model_threshold": name, "threshold": threshold,
                        **metrics(y, data[column].to_numpy(), threshold)})
    return pd.DataFrame(results)


def bootstrap(data: pd.DataFrame, thresholds: dict, repeats: int = BOOTSTRAP_REPEATS) -> pd.DataFrame:
    """Resample entire households, preserving repeated households and their members."""
    groups = data.groupby(GROUP, sort=False).indices
    positions = list(groups.values())
    rng = np.random.default_rng(RANDOM_STATE)
    values = {name: [] for name in ["HGB F1", "HGB screening", "Stratified Dummy"]}
    y = data[TARGET].to_numpy()
    prob = data.probability.to_numpy(); dummy = data.dummy_probability.to_numpy()
    for _ in range(repeats):
        idx = np.concatenate([positions[i] for i in rng.integers(0, len(positions), size=len(positions))])
        for name, scores, cut in [("HGB F1", prob, thresholds["f1"]),
                                  ("HGB screening", prob, thresholds["screening"]),
                                  ("Stratified Dummy", dummy, .5)]:
            values[name].append(metrics(y[idx], scores[idx], cut))
    rows = []
    for name, samples in values.items():
        frame = pd.DataFrame(samples)
        for measure in ["f1", "precision", "recall", "pr_auc", "roc_auc", "lift_10"]:
            valid = frame[measure].dropna()
            rows.append({"model_threshold": name, "metric": measure, "lower_95": valid.quantile(.025),
                         "upper_95": valid.quantile(.975), "valid_repeats": len(valid), "repeats": repeats})
    return pd.DataFrame(rows)


def education_group(series: pd.Series) -> pd.Series:
    """Group documented schooling codes into interpretable broad categories."""
    return pd.Series(np.select([series.eq(1), series.between(2, 5), series.eq(6), series.eq(7), series.between(8, 16)],
                               ["No formal education", "Below matric", "Matric", "Intermediate", "Degree or higher"],
                               default="Unknown"), index=series.index)


def subgroup_table(data: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Describe flags and positive-class performance within approved subgroups."""
    frame = data.copy()
    frame["sex"] = frame.sex.map({1: "Male", 2: "Female"}).fillna("Unknown")
    frame["area"] = frame.area.map({1: "Rural", 2: "Urban"}).fillna("Unknown")
    frame["province"] = frame.province.map({1: "Khyber Pakhtunkhwa", 2: "Punjab", 3: "Sindh", 4: "Balochistan"}).fillna("Unknown")
    frame["sex_area"] = frame.sex + " / " + frame.area
    frame["education_group"] = education_group(frame.education_level)
    rows = []
    for field in ["sex", "area", "sex_area", "province", "education_group"]:
        for value, sub in frame.groupby(field, dropna=False, sort=True):
            for name, cut in thresholds.items():
                y = sub[TARGET].to_numpy(); pred = sub.probability.to_numpy() >= cut
                rows.append({"subgroup": field, "value": value, "threshold": name, "n": len(sub),
                             "positives": int(y.sum()), "unreliable_fewer_than_50_positives": int(y.sum()) < 50,
                             "flag_rate": pred.mean(), "precision": precision_score(y, pred, zero_division=0),
                             "recall": recall_score(y, pred, zero_division=0)})
    return pd.DataFrame(rows)


def error_distributions(data: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Count feature values by TP, FN, FP and TN; do not export identifiers."""
    frame = data.copy()
    positive = frame.probability >= threshold
    frame["outcome"] = np.select([positive & frame[TARGET].eq(1), ~positive & frame[TARGET].eq(1),
                                  positive & frame[TARGET].eq(0)], ["TP", "FN", "FP"], default="TN")
    parts = []
    for name in FEATURES:
        counts = frame.groupby(["outcome", name], dropna=False).size().reset_index(name="count")
        counts = counts.rename(columns={name: "value"}); counts.insert(1, "feature", name)
        parts.append(counts)
    return pd.concat(parts, ignore_index=True)


def comparison_table(test: pd.DataFrame) -> pd.DataFrame:
    """Combine previously saved validation results with the untouched test results."""
    val = pd.read_csv(REPORT_TABLES / "validation_thresholds.csv")
    rows = []
    for _, item in val.iterrows():
        rows.append({"split": "validation", "model_threshold": "HGB F1" if item.threshold_type == "f1" else "HGB screening",
                     "f1": item.f1, "precision": item.precision, "recall": item.recall,
                     "pr_auc": item.pr_auc, "roc_auc": item.roc_auc, "prevalence": item.prevalence,
                     "lift_10": item.lift_at_10_percent, "note": "threshold chosen on validation labels"})
    dummy = pd.read_csv(REPORT_TABLES / "baseline_validation.csv").query("model == 'stratified'").iloc[0]
    rows.append({"split": "validation", "model_threshold": "Stratified Dummy", "f1": dummy.f1,
                 "precision": dummy.precision, "recall": dummy.recall, "pr_auc": dummy.pr_auc,
                 "roc_auc": dummy.roc_auc, "prevalence": dummy.prevalence, "lift_10": dummy.lift_at_10_percent,
                 "note": "training-fitted dummy"})
    rows.extend({"split": "test", **{key: item[key] for key in ["model_threshold", "f1", "precision", "recall", "pr_auc", "roc_auc", "prevalence", "lift_10"]},
                 "note": "frozen before test"} for _, item in test.iterrows())
    return pd.DataFrame(rows)


def figures(data: pd.DataFrame, threshold: float) -> None:
    """Create four test figures directly from the saved prediction file."""
    y = data[TARGET].to_numpy(); p = data.probability.to_numpy(); d = data.dummy_probability.to_numpy()
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, scores in [("HGB", p), ("Stratified Dummy", d)]:
        precision, recall, _ = precision_recall_curve(y, scores)
        ax.plot(recall, precision, label=f"{name}: AP={average_precision_score(y, scores):.3f}")
    ax.axhline(y.mean(), linestyle="--", color="black", label=f"Prevalence={y.mean():.3f}")
    ax.set(xlabel="Recall", ylabel="Precision", title="Test precision–recall curve"); ax.legend()
    fig.tight_layout(); fig.savefig(REPORT_FIGURES / "test_pr_curve.png", dpi=200); plt.close(fig)
    matrix = confusion_matrix(y, p >= threshold, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5, 4)); ax.imshow(matrix, cmap="Blues")
    for (i, j), value in np.ndenumerate(matrix): ax.text(j, i, str(value), ha="center", va="center")
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Employed", "Unemployed"],
           yticklabels=["Employed", "Unemployed"], xlabel="Predicted class", ylabel="Actual class",
           title="Test confusion matrix: F1 threshold")
    fig.tight_layout(); fig.savefig(REPORT_FIGURES / "test_confusion_matrix.png", dpi=200); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fractions = np.arange(.05, 1.001, .05)
    for name, scores in [("HGB", p), ("Stratified Dummy", d)]:
        lift = np.array([top_lift(y, scores, f) for f in fractions])
        actual_fractions = np.ceil(fractions * len(y)) / len(y)
        axes[0].plot(actual_fractions, actual_fractions * lift, label=name); axes[1].plot(actual_fractions, lift, label=name)
    axes[0].plot([0, 1], [0, 1], "k--", label="No skill"); axes[1].axhline(1, color="black", linestyle="--")
    axes[0].set(xlabel="Fraction of people ranked", ylabel="Fraction of positives captured", title="Cumulative gain")
    axes[1].set(xlabel="Fraction of people ranked", ylabel="Lift over prevalence", title="Cumulative lift")
    axes[0].legend(); axes[1].legend(); fig.tight_layout()
    fig.savefig(REPORT_FIGURES / "test_gain_lift.png", dpi=200); plt.close(fig)
    observed, predicted = calibration_curve(y, p, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(6, 5)); ax.plot(predicted, observed, "o-", label="HGB")
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.set(xlabel="Mean predicted probability", ylabel="Observed unemployed fraction",
           title=f"Test calibration (Brier={brier_score_loss(y, p):.3f})", xlim=(0, 1), ylim=(0, 1))
    ax.legend(); fig.tight_layout(); fig.savefig(REPORT_FIGURES / "test_calibration.png", dpi=200); plt.close(fig)


def main() -> None:
    """Verify the freeze, score at most once, then analyse only saved predictions."""
    model_hash = verify_frozen_model()
    metadata = json.loads((MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))
    thresholds = {"f1": metadata["threshold_f1"], "screening": metadata["threshold_screening"]}
    if not RECEIPT.exists() and not PREDICTIONS.exists():
        save_test_predictions(model_hash, metadata)
    data = load_predictions(model_hash)
    result = metric_table(data, thresholds)
    result.to_csv(REPORT_TABLES / "test_metrics.csv", index=False)
    bands = data.groupby("risk_band")[TARGET].agg(n="size", positives="sum", prevalence="mean").reset_index()
    bands.to_csv(REPORT_TABLES / "test_risk_bands.csv", index=False)
    pd.DataFrame([{"model": label, "brier": brier_score_loss(data[TARGET], data[column])}
                  for label, column in [("HGB", "probability"), ("Stratified Dummy", "dummy_probability")]]).to_csv(
                      REPORT_TABLES / "test_brier_scores.csv", index=False)
    comparison_table(result).to_csv(REPORT_TABLES / "validation_test_comparison.csv", index=False)
    subgroup_table(data, thresholds).to_csv(REPORT_TABLES / "test_subgroups.csv", index=False)
    error_distributions(data, thresholds["f1"]).to_csv(REPORT_TABLES / "test_error_distributions.csv", index=False)
    figures(data, thresholds["f1"])
    print("Saved predictions and deterministic tables; running grouped bootstrap.", flush=True)
    bootstrap(data, thresholds).to_csv(REPORT_TABLES / "test_bootstrap_ci.csv", index=False)
    print(result.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
