# What: compares approved HGB grouped CV with and without enrolment.
# Why: assess whether this leading input materially affects model ranking.
# Viva: removing a column happens within each training-fold pipeline.
from pathlib import Path
import os
import runpy
import sys

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES, GROUP, MODELS_DIR, N_CV_FOLDS, RANDOM_STATE, REPORT_TABLES, TARGET


def main() -> None:
    """Run the same household folds and add one reproducible ablation row."""
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    train, val = loader["load_train_validation"]()
    model = clone(joblib.load(MODELS_DIR / "final_pipeline.joblib"))
    preprocessor = model.named_steps["preprocess"]
    preprocessor.sparse_threshold = 0
    preprocessor.transformers = [(name, branch, [c for c in columns if c != "currently_enrolled"])
                                 for name, branch, columns in preprocessor.transformers]
    splitter = StratifiedGroupKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    folds = list(splitter.split(train[FEATURES], train[TARGET], groups=train[GROUP]))
    with threadpool_limits(limits=1):
        scores = cross_val_score(model, train[FEATURES], train[TARGET], cv=folds,
                                 groups=train[GROUP], scoring="average_precision", n_jobs=1)
    path = REPORT_TABLES / "feature_group_ablation.csv"
    table = pd.read_csv(path)
    baseline = table.loc[(table.model == "hist_gradient_boosting") & (table.ablation == "all_features")].iloc[0]
    row = {**baseline.to_dict(), "ablation": "full_without_currently_enrolled",
           "cv_ap_mean": scores.mean(), "cv_ap_std": scores.std()}
    table = table.loc[~((table.model == "hist_gradient_boosting") & (table.ablation == row["ablation"]))]
    pd.concat([table, pd.DataFrame([row])], ignore_index=True).to_csv(path, index=False)
    print("Full CV AP:", baseline.cv_ap_mean, "Without enrolment:", scores.mean(),
          "Change:", scores.mean() - baseline.cv_ap_mean, "fold scores:", scores, flush=True)


if __name__ == "__main__":
    main()
