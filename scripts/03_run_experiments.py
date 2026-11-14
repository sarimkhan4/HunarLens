# What: runs Stage 5 training-fold experiments and validation comparisons.
# Why: grouped CV provides a fair, reproducible selection basis.
# Viva: validation sets a threshold; the test partition is never evaluated here.
from pathlib import Path
import json
import os
import runpy
import sys
import time

for thread_env in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[thread_env] = "1"

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedGroupKFold, cross_validate
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, FEATURES, GROUP, N_CV_FOLDS, RANDOM_STATE, REPORT_FIGURES, REPORT_TABLES, TARGET
from hunarlens.pipeline import build_model_pipeline
from hunarlens.splits import file_hash

CHECKPOINTS = ROOT / "data" / "interim" / "stage5"
RESULTS = REPORT_TABLES / "experiments.csv"
JOBS = 2
N_ITER_RF = 15
N_ITER_HGB = 15
SCORING = {"ap": "average_precision", "roc_auc": "roc_auc"}
MODELS = ["logistic_regression", "random_forest", "hist_gradient_boosting"]
HOUSEHOLD = {"household_size", "children_under_15", "other_youth_15_24", "head_sex", "head_education"}
CENSUS = {"census_density", "census_urban_proportion", "census_household_size"}


def make_model(name: str, weighted: bool = False):
    """Use one worker per forest; parallelism is controlled by CV."""
    if name == "logistic_regression":
        return LogisticRegression(max_iter=1000, class_weight="balanced" if weighted else None, random_state=RANDOM_STATE)
    if name == "random_forest":
        return RandomForestClassifier(class_weight="balanced_subsample" if weighted else None, n_jobs=1, random_state=RANDOM_STATE)
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(class_weight="balanced" if weighted else None, early_stopping=False, random_state=RANDOM_STATE)
    return DummyClassifier(strategy="stratified", random_state=RANDOM_STATE)


def search_space(name: str) -> dict:
    """Use the plan's specified search spaces inside the whole pipeline."""
    if name == "logistic_regression":
        return {"model__C": [0.01, 0.1, 1, 10], "model__class_weight": [None, "balanced"]}
    if name == "random_forest":
        return {"model__n_estimators": [200, 400], "model__max_depth": [6, 10, 16, None],
                "model__min_samples_leaf": [5, 20, 50], "model__max_features": ["sqrt", 0.3],
                "model__class_weight": [None, "balanced_subsample"]}
    return {"model__learning_rate": [0.03, 0.06, 0.1], "model__max_depth": [3, 5, None],
            "model__max_leaf_nodes": [15, 31], "model__min_samples_leaf": [20, 50, 100],
            "model__l2_regularization": [0, 1, 10], "model__max_iter": [200, 400],
            "model__class_weight": [None, "balanced"]}


def write_row(path: Path, row: dict, keys: list[str]) -> None:
    """Replace a checkpoint row atomically so interrupted runs can resume."""
    old = pd.read_csv(path) if path.exists() else pd.DataFrame()
    if not old.empty:
        match = pd.Series(True, index=old.index)
        for key in keys:
            match &= old[key].astype(str).eq(str(row[key]))
        old = old.loc[~match]
    tmp = path.with_suffix(".tmp")
    pd.concat([old, pd.DataFrame([row])], ignore_index=True).to_csv(tmp, index=False)
    tmp.replace(path)


def guard_run() -> None:
    """Never reuse checkpoints from a different dataset or split file."""
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    REPORT_TABLES.mkdir(parents=True, exist_ok=True)
    REPORT_FIGURES.mkdir(parents=True, exist_ok=True)
    state = {"data": file_hash(DATA_PROCESSED / "hunarlens_youth.csv"),
             "split": file_hash(DATA_PROCESSED / "split_assignments.csv"), "rf_iter": N_ITER_RF, "hgb_iter": N_ITER_HGB}
    path = CHECKPOINTS / "run.json"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        if old["data"] != state["data"] or old["split"] != state["split"]:
            raise ValueError("Stage 5 checkpoints belong to a different dataset or split.")
        for key, model in [("rf_iter", "random_forest"), ("hgb_iter", "hist_gradient_boosting")]:
            if old[key] != state[key] and (is_done("E3", model) or (CHECKPOINTS / f"{model}.joblib").exists()):
                raise ValueError(f"Cannot change {key} after tuning {model}.")
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def val_metrics(model, val: pd.DataFrame, threshold: float = 0.5) -> dict:
    """Check the validation tripwire before returning comparison metrics."""
    truth = val[TARGET]
    scores = model.predict_proba(val[FEATURES])[:, 1]
    ap = average_precision_score(truth, scores)
    if ap > 0.4:
        raise ValueError(f"Validation PR-AUC {ap:.4f} exceeds 0.4; stop and investigate leakage.")
    pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(truth, pred, labels=[0, 1]).ravel()
    order = np.random.default_rng(RANDOM_STATE).permutation(len(scores))
    ranked = order[np.argsort(-scores[order], kind="stable")]
    top = max(1, int(np.ceil(len(scores) * 0.1)))
    return {"val_ap": ap, "val_roc_auc": roc_auc_score(truth, scores),
            "val_precision": precision_score(truth, pred, zero_division=0),
            "val_recall": recall_score(truth, pred, zero_division=0),
            "val_f1": f1_score(truth, pred, zero_division=0), "val_prevalence": truth.mean(),
            "val_lift_at_10_percent": truth.iloc[ranked[:top]].mean() / truth.mean(),
            "val_tn": tn, "val_fp": fp, "val_fn": fn, "val_tp": tp}


def optimal_threshold(model, val: pd.DataFrame) -> tuple[float, float]:
    """Choose F1's threshold using validation only; ties use the first threshold."""
    truth = val[TARGET]
    probabilities = model.predict_proba(val[FEATURES])[:, 1]
    precision, recall, thresholds = precision_recall_curve(truth, probabilities)
    f1 = np.divide(2 * precision[:-1] * recall[:-1], precision[:-1] + recall[:-1],
                   out=np.zeros_like(thresholds), where=(precision[:-1] + recall[:-1]) != 0)
    index = int(np.argmax(f1))
    return float(thresholds[index]), float(f1[index])


def record(exp: str, name: str, fitted, val: pd.DataFrame, params: dict, mean: float, std: float, seconds: float, threshold: float = 0.5) -> None:
    """Save metrics, positive-class context and fitted choices as each step finishes."""
    metrics = val_metrics(fitted, val, threshold)
    default_f1 = val_metrics(fitted, val, 0.5)["val_f1"]
    best = metrics["val_f1"] if exp == "E4" else np.nan
    weight = params.get("model__class_weight")
    strategy = "stratified" if name == "dummy" else weight if weight is not None else "unweighted"
    row = {"exp_id": exp, "model": name, "imbalance_strategy": strategy,
           "best_params": json.dumps(params, sort_keys=True), "cv_ap_mean": mean, "cv_ap_std": std,
           "val_f1_at_0.5": default_f1, "val_f1_best": best, "threshold": threshold, "fit_seconds": seconds, **metrics}
    write_row(RESULTS, row, ["exp_id", "model"])
    print(f"Saved {exp} {name}: CV AP={mean:.4f}, validation AP={metrics['val_ap']:.4f}", flush=True)


def is_done(exp: str, name: str) -> bool:
    if not RESULTS.exists():
        return False
    rows = pd.read_csv(RESULTS)
    return bool((rows.exp_id.eq(exp) & rows.model.eq(name)).any())


def normalize_dummy_metadata() -> None:
    """Describe the saved baseline by its actual sampling strategy."""
    rows = pd.read_csv(RESULTS)
    mask = rows.exp_id.eq("E0") & rows.model.eq("dummy")
    if mask.sum() != 1:
        raise ValueError("Expected exactly one stratified dummy baseline.")
    rows.loc[mask, "imbalance_strategy"] = "stratified"
    rows.loc[mask, "best_params"] = json.dumps({"model__strategy": "stratified"})
    rows["imbalance_strategy"] = rows["imbalance_strategy"].fillna("unweighted")
    rows.to_csv(RESULTS, index=False)


def run_simple(exp: str, name: str, train: pd.DataFrame, val: pd.DataFrame, folds: list) -> None:
    """Measure an untuned estimator using the exact same grouped folds."""
    if is_done(exp, name):
        return
    weighted = exp == "E2"
    model = build_model_pipeline(make_model(name, weighted))
    start = time.perf_counter()
    scores = cross_validate(model, train[FEATURES], train[TARGET], groups=train[GROUP], cv=folds, scoring=SCORING, n_jobs=JOBS)
    model.fit(train[FEATURES], train[TARGET])
    params = ({"model__strategy": "stratified"} if name == "dummy" else
              {"model__class_weight": "balanced_subsample" if weighted and name == "random_forest" else "balanced" if weighted else None})
    record(exp, name, model, val, params, scores["test_ap"].mean(), scores["test_ap"].std(), time.perf_counter() - start)


def tune(name: str, train: pd.DataFrame, val: pd.DataFrame, folds: list) -> None:
    """Tune on training groups, checkpoint the refitted model and validation rows."""
    checkpoint = CHECKPOINTS / f"{name}.joblib"
    gap_path = REPORT_TABLES / "generalization_gap.csv"
    gap_done = gap_path.exists() and pd.read_csv(gap_path).model.eq(name).any()
    if is_done("E3", name) and is_done("E4", name) and checkpoint.exists() and gap_done:
        return
    if checkpoint.exists():
        saved = joblib.load(checkpoint)
    else:
        pipe = build_model_pipeline(make_model(name))
        common = dict(estimator=pipe, scoring=SCORING, refit="ap", cv=folds, n_jobs=JOBS, return_train_score=True, error_score="raise")
        if name == "logistic_regression":
            search = GridSearchCV(param_grid=search_space(name), **common)
        else:
            iterations = N_ITER_RF if name == "random_forest" else N_ITER_HGB
            search = RandomizedSearchCV(param_distributions=search_space(name), n_iter=iterations, random_state=RANDOM_STATE, **common)
        start = time.perf_counter()
        search.fit(train[FEATURES], train[TARGET], groups=train[GROUP])
        saved = {"model": search.best_estimator_, "params": search.best_params_, "cv_ap": float(search.best_score_),
                 "cv_std": float(search.cv_results_["std_test_ap"][search.best_index_]), "fit_seconds": time.perf_counter() - start}
        val_metrics(saved["model"], val)
        joblib.dump(saved, checkpoint)
    fitted, mean, std, seconds, params = saved["model"], saved["cv_ap"], saved["cv_std"], saved["fit_seconds"], saved["params"]
    metrics = val_metrics(fitted, val)
    record("E3", name, fitted, val, params, mean, std, seconds)
    threshold, _ = optimal_threshold(fitted, val)
    record("E4", name, fitted, val, params, mean, std, seconds, threshold)
    write_row(gap_path, {"model": name,
              "train_ap": average_precision_score(train[TARGET], fitted.predict_proba(train[FEATURES])[:, 1]),
              "cv_ap": mean, "validation_ap": metrics["val_ap"]}, ["model"])


def choose_leader() -> str:
    """Within 0.01 of the best CV score, prefer logistic, then forest, then HGB."""
    rows = pd.read_csv(RESULTS).query("exp_id == 'E3'")
    best = rows.cv_ap_mean.max()
    eligible = set(rows.loc[rows.cv_ap_mean >= best - 0.01, "model"])
    return next(name for name in MODELS if name in eligible)


def precision_recall_figure(val: pd.DataFrame) -> None:
    """Plot validation curves with a prevalence reference and dummy baseline."""
    fig, ax = plt.subplots(figsize=(7, 5))
    for name in MODELS:
        model = joblib.load(CHECKPOINTS / f"{name}.joblib")["model"]
        prob = model.predict_proba(val[FEATURES])[:, 1]
        if average_precision_score(val[TARGET], prob) > 0.4:
            raise ValueError(f"Validation PR-AUC exceeds 0.4 for {name}.")
        precision, recall, _ = precision_recall_curve(val[TARGET], prob)
        ax.plot(recall, precision, label=name)
    ax.axhline(val[TARGET].mean(), color="black", linestyle="--", label="Prevalence / dummy no-skill")
    ax.set(title="Validation precision–recall curves", xlabel="Recall", ylabel="Precision", xlim=(0, 1), ylim=(0, 1))
    ax.legend()
    fig.tight_layout()
    fig.savefig(REPORT_FIGURES / "validation_pr_curves.png", dpi=200)
    plt.close(fig)


def group_learning_curve(name: str, train: pd.DataFrame, folds: list) -> None:
    """Subsample whole training households within each held-out grouped fold."""
    target = REPORT_TABLES / "grouped_learning_curve.csv"
    model = joblib.load(CHECKPOINTS / f"{name}.joblib")["model"]
    for fraction in [0.2, 0.5, 1.0]:
        scores = []
        for number, (fit_index, hold_index) in enumerate(folds):
            group_ids = train.iloc[fit_index][GROUP].unique()
            group_ids = np.random.default_rng(RANDOM_STATE + number).permutation(group_ids)
            keep = group_ids[:max(1, int(np.ceil(len(group_ids) * fraction)))]
            subset = train.iloc[fit_index].loc[lambda frame: frame[GROUP].isin(keep)]
            fitted = clone(model).fit(subset[FEATURES], subset[TARGET])
            hold = train.iloc[hold_index]
            scores.append(average_precision_score(hold[TARGET], fitted.predict_proba(hold[FEATURES])[:, 1]))
        write_row(target, {"fraction_of_training_groups": fraction, "cv_ap_mean": np.mean(scores), "cv_ap_std": np.std(scores), "model": name}, ["fraction_of_training_groups"])
        print(f"Learning curve {fraction:.0%} complete", flush=True)
    table = pd.read_csv(target).sort_values("fraction_of_training_groups")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.errorbar(table.fraction_of_training_groups * 100, table.cv_ap_mean, yerr=table.cv_ap_std, marker="o")
    ax.axhline(train[TARGET].mean(), color="black", linestyle="--", label="Training prevalence")
    ax.set(title=f"Grouped learning curve: {name}", xlabel="Training groups used per fold (%)", ylabel="Held-out fold average precision")
    ax.legend(); fig.tight_layout(); fig.savefig(REPORT_FIGURES / "grouped_learning_curve.png", dpi=200); plt.close(fig)


def complexity_curve(train: pd.DataFrame, folds: list) -> None:
    """Compare forest depths using only grouped training folds."""
    saved = joblib.load(CHECKPOINTS / "random_forest.joblib")["model"]
    target = REPORT_TABLES / "validation_curve.csv"
    for depth in [6, 10, 16, None]:
        model = clone(saved).set_params(model__max_depth=depth)
        scores = cross_validate(model, train[FEATURES], train[TARGET], groups=train[GROUP], cv=folds, scoring="average_precision", n_jobs=JOBS, return_train_score=True)
        write_row(target, {"max_depth": str(depth), "train_ap": scores["train_score"].mean(), "cv_ap": scores["test_score"].mean()}, ["max_depth"])
        print(f"Complexity depth {depth} complete", flush=True)
    table = pd.read_csv(target, keep_default_na=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(table.max_depth.astype(str), table.train_ap, marker="o", label="Fold training")
    ax.plot(table.max_depth.astype(str), table.cv_ap, marker="o", label="Held-out fold")
    ax.axhline(train[TARGET].mean(), color="black", linestyle="--", label="Prevalence")
    ax.set(title="Random Forest complexity curve", xlabel="Maximum tree depth", ylabel="Average precision")
    ax.legend(); fig.tight_layout(); fig.savefig(REPORT_FIGURES / "forest_validation_curve.png", dpi=200); plt.close(fig)


def ablation(name: str, train: pd.DataFrame, folds: list) -> None:
    """Remove feature groups only in the pipeline's preprocessor, within CV."""
    saved = joblib.load(CHECKPOINTS / f"{name}.joblib")["model"]
    options = [("individual_only", HOUSEHOLD | CENSUS), ("individual_household", CENSUS),
               ("all_features", set()), ("full_without_census", CENSUS)]
    for label, excluded in options:
        pipe = clone(saved)
        if name == "hist_gradient_boosting":
            # Removing columns can make ColumnTransformer emit sparse output;
            # HistGradientBoosting requires a dense matrix.
            pipe.named_steps["preprocess"].sparse_threshold = 0
        numeric, categorical = pipe.named_steps["preprocess"].transformers
        extended = set(excluded)
        if "household_size" in excluded:
            extended |= {"household_size_clipped", "children_share"}
        pipe.named_steps["preprocess"].transformers = [(numeric[0], numeric[1], [x for x in numeric[2] if x not in extended]),
                                                       (categorical[0], categorical[1], [x for x in categorical[2] if x not in extended])]
        score = cross_validate(pipe, train[FEATURES], train[TARGET], groups=train[GROUP], cv=folds, scoring="average_precision", n_jobs=JOBS)
        write_row(REPORT_TABLES / "feature_group_ablation.csv", {"model": name, "ablation": label, "cv_ap_mean": score["test_score"].mean(), "cv_ap_std": score["test_score"].std()}, ["model", "ablation"])
        print(f"Ablation {label} complete", flush=True)


def add_baseline_context(train: pd.DataFrame, val: pd.DataFrame) -> None:
    """Place dummy and prevalence references beside gap and ablation results."""
    experiments = pd.read_csv(RESULTS)
    dummy = experiments.loc[experiments.exp_id.eq("E0") & experiments.model.eq("dummy")].iloc[0]
    for name in ["generalization_gap.csv", "feature_group_ablation.csv", "grouped_learning_curve.csv", "validation_curve.csv"]:
        path = REPORT_TABLES / name
        table = pd.read_csv(path, keep_default_na=False)
        table["train_prevalence"] = train[TARGET].mean()
        table["val_prevalence"] = val[TARGET].mean()
        table["dummy_cv_ap"] = dummy.cv_ap_mean
        table["dummy_val_ap"] = dummy.val_ap
        table.to_csv(path, index=False)


def main() -> None:
    """Checkpoint every experiment and run diagnostics after all models pass."""
    guard_run()
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    train, val = loader["load_train_validation"]()
    cv = StratifiedGroupKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    folds = list(cv.split(train[FEATURES], train[TARGET], groups=train[GROUP]))
    for fit, hold in folds:
        if set(train.iloc[fit][GROUP]) & set(train.iloc[hold][GROUP]):
            raise ValueError("Households overlap a CV fold.")
    with threadpool_limits(limits=1):
        run_simple("E0", "dummy", train, val, folds)
        normalize_dummy_metadata()
        for name in MODELS:
            run_simple("E1", name, train, val, folds)
            run_simple("E2", name, train, val, folds)
            tune(name, train, val, folds)
        leader = choose_leader()
        print(f"CV-selected leader: {leader}", flush=True)
        precision_recall_figure(val)
        group_learning_curve(leader, train, folds)
        complexity_curve(train, folds)
        ablation(leader, train, folds)
        add_baseline_context(train, val)


if __name__ == "__main__":
    main()
