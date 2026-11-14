# What: checks frozen model portability, metadata and validation-only loading.
# Why: the saved model must work independently without examining test observations.
# Viva: a new Python process makes sure the saved pipeline is self-contained.
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

import joblib
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES


@pytest.fixture
def artifacts():
    model_path = ROOT / "models" / "final_pipeline.joblib"
    metadata_path = ROOT / "models" / "metadata.json"
    if not model_path.exists() or not metadata_path.exists():
        pytest.skip("Run Stage 6 to generate the local model and metadata.")
    return model_path, json.loads(metadata_path.read_text(encoding="utf-8"))


def test_model_roundtrip_fresh_process(artifacts):
    model_path, metadata = artifacts
    row = {name: values[0] for section in ["numeric", "categorical"]
           for name, values in metadata["features"][section].items()}
    assert set(row) == set(FEATURES)
    code = ("import json,joblib,pandas as pd,sys; "
            "row=json.loads(sys.argv[2]); model=joblib.load(sys.argv[1]); "
            "p=model.predict_proba(pd.DataFrame([row]))[0,1]; assert 0 <= p <= 1")
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), OMP_NUM_THREADS="1")
    subprocess.run([sys.executable, "-c", code, str(model_path), json.dumps(row)],
                   cwd=ROOT, env=env, check=True, capture_output=True, text=True, timeout=60)
    assert model_path.stat().st_size < 25_000_000


def test_metadata_matches_fitted_encoder(artifacts):
    model_path, metadata = artifacts
    model = joblib.load(model_path)
    if metadata["calibration"] == "sigmoid":
        model = model.calibrated_classifiers_[0].estimator.estimator
    transformer = model.named_steps["preprocess"]
    encoder = transformer.named_transformers_["categorical"].named_steps["encode"]
    for name, categories in zip(transformer.transformers_[1][2], encoder.categories_):
        assert metadata["features"]["encoder_categories"][name] == categories.tolist()
    assert set(metadata["features"]["numeric"]) | set(metadata["features"]["categorical"]) == set(FEATURES)


def test_pinned_sklearn_matches_metadata(artifacts):
    _, metadata = artifacts
    pins = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    versions = [line.split("==", 1)[1] for line in pins if line.startswith("scikit-learn==")]
    assert versions == [metadata["sklearn_version"]]


def test_stage6_uses_skip_test_loader(monkeypatch):
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    assignments = pd.DataFrame({"split": ["train", "test", "val"]})
    monkeypatch.setitem(loader["load_train_validation"].__globals__, "load_assignments", lambda *args: assignments)
    def fake_read(path, usecols, skiprows):
        assert not skiprows(0) and not skiprows(1) and skiprows(2) and not skiprows(3)
        return pd.DataFrame([{column: 1 for column in usecols}, {column: 2 for column in usecols}])
    monkeypatch.setattr(pd, "read_csv", fake_read)
    train, val = loader["load_train_validation"]()
    assert len(train) == len(val) == 1
    source = (ROOT / "scripts" / "04_freeze_model.py").read_text(encoding="utf-8")
    assert 'loader["load_train_validation"]()' in source


def test_threshold_range_midpoint():
    module = runpy.run_path(str(ROOT / "scripts" / "04_freeze_model.py"))
    result = module["select_thresholds"](np.array([0, 1, 0, 1]), np.array([.1, .3, .4, .8]))
    assert result["f1"] == pytest.approx(sum(result["f1_range"]) / 2)
