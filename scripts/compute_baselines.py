# What: evaluates validation baselines and a training-only leakage tripwire.
# Why: we need an honest reference and a warning about unusually predictive fields.
# Viva: grouped folds keep household members together during the scan.
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, FEATURES, GROUP, LEAKAGE_TREE_MAX_DEPTH, N_CV_FOLDS, RANDOM_STATE, REPORT_TABLES, TARGET
from hunarlens.pipeline import build_model_pipeline
from hunarlens.splits import load_assignments


def load_train_validation() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Skip test rows while reading; reject stale or incomplete assignments."""
    path = DATA_PROCESSED / "hunarlens_youth.csv"
    assignments = load_assignments(DATA_PROCESSED / "split_assignments.csv", path)
    labels = assignments.split.to_numpy()
    if not set(labels) <= {"train", "val", "test"}:
        raise ValueError("Unexpected split label.")
    rows = pd.read_csv(path, usecols=[*FEATURES, GROUP, TARGET],
                       skiprows=lambda line: line > 0 and (line > len(labels) or labels[line - 1] == "test"))
    selected = labels[labels != "test"]
    if len(rows) != len(selected):
        raise ValueError("Assignment and dataset row counts differ.")
    return rows.loc[selected == "train"].copy(), rows.loc[selected == "val"].copy()


def evaluate_baselines(train: pd.DataFrame, val: pd.DataFrame) -> pd.DataFrame:
    """Compare both simple models on validation, including class imbalance context."""
    rows = []
    for strategy in ["stratified", "most_frequent"]:
        pipeline = build_model_pipeline(DummyClassifier(strategy=strategy, random_state=RANDOM_STATE))
        pipeline.fit(train[FEATURES], train[TARGET])
        prediction = pipeline.predict(val[FEATURES])
        scores = pipeline.predict_proba(val[FEATURES])[:, 1]
        truth = val[TARGET]
        tn, fp, fn, tp = confusion_matrix(truth, prediction, labels=[0, 1]).ravel()
        order = np.random.default_rng(RANDOM_STATE).permutation(len(scores))
        ranked = order[np.argsort(-scores[order], kind="stable")]
        top = max(1, int(np.ceil(0.1 * len(scores))))
        rows.append({"model": strategy, "f1": f1_score(truth, prediction, zero_division=0),
                     "precision": precision_score(truth, prediction, zero_division=0),
                     "recall": recall_score(truth, prediction, zero_division=0),
                     "pr_auc": average_precision_score(truth, scores), "roc_auc": roc_auc_score(truth, scores),
                     "accuracy": accuracy_score(truth, prediction), "prevalence": truth.mean(),
                     "lift_at_10_percent": truth.iloc[ranked[:top]].mean() / truth.mean(),
                     "tn": tn, "fp": fp, "fn": fn, "tp": tp})
    return pd.DataFrame(rows)


def scan_features(train: pd.DataFrame) -> pd.DataFrame:
    """Use one raw column per grouped CV tree; stop on suspicious performance."""
    y = train[TARGET]
    cv = StratifiedGroupKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    folds = list(cv.split(train[FEATURES], y, groups=train[GROUP]))
    for fitting, held_out in folds:
        if set(train.iloc[fitting][GROUP]) & set(train.iloc[held_out][GROUP]):
            raise ValueError("A household appears in both sides of a CV fold.")
    rows = []
    for feature in FEATURES:
        tree = make_pipeline(SimpleImputer(strategy="most_frequent"),
                             DecisionTreeClassifier(max_depth=LEAKAGE_TREE_MAX_DEPTH, random_state=RANDOM_STATE))
        scores = cross_val_score(tree, train[[feature]], y, cv=folds, scoring="average_precision")
        row = {"feature": feature, "mean_pr_auc": scores.mean(), "std_pr_auc": scores.std(),
               "train_prevalence": y.mean(), "flag_over_3x": scores.mean() > 3 * y.mean()}
        rows.append(row)
        pd.DataFrame(rows).to_csv(REPORT_TABLES / "single_feature_scan.csv", index=False)
        if row["flag_over_3x"]:
            raise ValueError(f"Leakage tripwire triggered for {feature}; stop and investigate.")
    return pd.DataFrame(rows)


def main() -> None:
    """Run the training-only scan before reporting validation baselines."""
    REPORT_TABLES.mkdir(parents=True, exist_ok=True)
    train, val = load_train_validation()
    scan = scan_features(train)
    baselines = evaluate_baselines(train, val)
    baselines.to_csv(REPORT_TABLES / "baseline_validation.csv", index=False)
    print("Maximum single-feature PR-AUC:", scan.mean_pr_auc.max())
    print(baselines.to_string(index=False))


if __name__ == "__main__":
    main()
