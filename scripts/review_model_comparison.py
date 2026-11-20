# What: produces the team's requested paired CV, HGB ablation and lift review.
# Why: reviewers need fold-level variation before freezing the chosen model.
# Viva: the same household folds make paired differences meaningful.
from pathlib import Path
import os
import runpy
import sys

for thread_env in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[thread_env] = "1"

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES, GROUP, N_CV_FOLDS, RANDOM_STATE, REPORT_TABLES, TARGET


def main() -> None:
    """Evaluate the frozen-in-CV parameter choices without opening test rows."""
    stage5 = runpy.run_path(str(ROOT / "scripts" / "compare_models.py"))
    loader = runpy.run_path(str(ROOT / "scripts" / "compute_baselines.py"))
    train, val = loader["load_train_validation"]()
    cv = StratifiedGroupKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    folds = list(cv.split(train[FEATURES], train[TARGET], groups=train[GROUP]))
    if "--ablation-only" in sys.argv:
        with threadpool_limits(limits=1):
            stage5["ablation"]("hist_gradient_boosting", train, folds)
            stage5["add_baseline_context"](train, val)
        return
    results = {"fold": list(range(1, N_CV_FOLDS + 1))}
    lift = []
    with threadpool_limits(limits=1):
        for name in stage5["MODELS"]:
            model = joblib.load(stage5["CHECKPOINTS"] / f"{name}.joblib")["model"]
            scores = cross_val_score(clone(model), train[FEATURES], train[TARGET], groups=train[GROUP], cv=folds, scoring="average_precision", n_jobs=stage5["JOBS"])
            results[name] = scores
            probability = model.predict_proba(val[FEATURES])[:, 1]
            if average_precision_score(val[TARGET], probability) > 0.4:
                raise ValueError(f"Validation leakage tripwire exceeded by {name}.")
            order = np.random.default_rng(RANDOM_STATE).permutation(len(probability))
            order = order[np.argsort(-probability[order], kind="stable")]
            item = {"model": name, "prevalence": val[TARGET].mean()}
            for fraction in [0.1, 0.2]:
                count = int(np.ceil(fraction * len(order)))
                item[f"lift_top_{int(fraction * 100)}_pct"] = val[TARGET].iloc[order[:count]].mean() / val[TARGET].mean()
            lift.append(item)
            print(f"Fold and lift review complete: {name}", flush=True)
        table = pd.DataFrame(results)
        table["rf_minus_hgb"] = table.random_forest - table.hist_gradient_boosting
        table["hgb_minus_lr"] = table.hist_gradient_boosting - table.logistic_regression
        summary = pd.DataFrame([{"fold": label, **table.drop(columns="fold").agg(operation).to_dict()}
                                for label, operation in [("mean", "mean"), ("std_population", "std")]])
        # Use population standard deviation, matching RandomizedSearchCV's cv_results_.
        summary.loc[summary.fold.eq("std_population"), table.columns[1:]] = table.drop(columns="fold").std(ddof=0).to_numpy()
        pd.concat([table, summary], ignore_index=True).to_csv(REPORT_TABLES / "cv_fold_scores.csv", index=False)
        pd.DataFrame(lift).to_csv(REPORT_TABLES / "validation_lift.csv", index=False)
        stage5["ablation"]("hist_gradient_boosting", train, folds)
        stage5["add_baseline_context"](train, val)


if __name__ == "__main__":
    main()
