# What: checks model comparison selection and validation leakage tripwire.
# Why: validation cannot select the leading model or silently hide a high PR-AUC.
# Viva: the selection rule uses CV scores and prefers simpler nearby models.
from pathlib import Path
import runpy

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_leader_uses_cv_and_simplicity(monkeypatch: pytest.MonkeyPatch) -> None:
    module = runpy.run_path(str(ROOT / "scripts" / "compare_models.py"))
    rows = pd.DataFrame([{"exp_id": "E3", "model": "logistic_regression", "cv_ap_mean": 0.30, "val_ap": 0.10},
                  {"exp_id": "E3", "model": "random_forest", "cv_ap_mean": 0.309, "val_ap": 0.50},
                  {"exp_id": "E3", "model": "hist_gradient_boosting", "cv_ap_mean": 0.305, "val_ap": 0.70}])
    monkeypatch.setattr(module["pd"], "read_csv", lambda path: rows)
    assert module["choose_leader"]() == "logistic_regression"


def test_high_validation_ap_stops() -> None:
    module = runpy.run_path(str(ROOT / "scripts" / "compare_models.py"))
    val = pd.DataFrame({name: [0, 1, 2, 3] for name in module["FEATURES"]})
    val["is_unemployed"] = [0, 0, 1, 1]
    class LeakyModel:
        def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
            return np.array([[1, 0], [1, 0], [0, 1], [0, 1]])
    with pytest.raises(ValueError, match="stop and investigate leakage"):
        module["val_metrics"](LeakyModel(), val)
