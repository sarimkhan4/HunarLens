# What: checks the final evaluation on synthetic records only.
# Why: validate ranking metrics and the freeze guard before opening the test split.
# Viva: a rejected hash must prevent any use of test records.
from pathlib import Path
import runpy
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def stage8():
    return runpy.run_path(str(ROOT / "scripts" / "06_final_test_eval.py"))


def test_synthetic_metrics(stage8):
    y = np.array([1, 0, 1, 0])
    scores = np.array([.9, .8, .7, .1])
    result = stage8["metrics"](y, scores, .75)
    assert (result["tp"], result["fp"], result["fn"], result["tn"]) == (1, 1, 1, 1)
    assert result["precision"] == pytest.approx(.5)
    assert result["recall"] == pytest.approx(.5)
    assert result["lift_10"] == pytest.approx(2)


def test_hash_guard_and_no_second_open(stage8, monkeypatch):
    digest = "a" * 64
    decisions = SimpleNamespace(read_text=lambda **kwargs: f"The SHA-256 of `models/final_pipeline.joblib` is `{digest}`")
    namespace = stage8["verify_frozen_model"].__globals__
    monkeypatch.setitem(namespace, "DECISIONS", decisions)
    monkeypatch.setitem(namespace, "sha256", lambda path: digest)
    assert stage8["verify_frozen_model"]() == digest
    monkeypatch.setitem(namespace, "sha256", lambda path: "b" * 64)
    with pytest.raises(ValueError, match="does not match"):
        stage8["verify_frozen_model"]()
    monkeypatch.setitem(namespace, "RECEIPT", SimpleNamespace(exists=lambda: False))
    monkeypatch.setitem(namespace, "PREDICTIONS", SimpleNamespace(exists=lambda: False))
    monkeypatch.setitem(namespace, "DECISIONS", SimpleNamespace(read_text=lambda **kwargs: "## Stage 8 — first test opening"))
    with pytest.raises(RuntimeError, match="previous test opening"):
        stage8["save_test_predictions"](digest, {})


def test_bootstrap_is_grouped_and_reproducible(stage8):
    data = pd.DataFrame({"group_id": ["a", "a", "b", "b", "c", "c"],
                         "is_unemployed": [1, 0, 1, 0, 1, 0],
                         "probability": [.8, .3, .6, .4, .7, .2],
                         "dummy_probability": [1, 0, 0, 1, 1, 0]})
    thresholds = {"f1": .5, "screening": .4}
    one = stage8["bootstrap"](data, thresholds, repeats=4)
    two = stage8["bootstrap"](data, thresholds, repeats=4)
    pd.testing.assert_frame_equal(one, two)
    assert set(one.valid_repeats) == {4}
    assert set(one.metric) == {"f1", "precision", "recall", "pr_auc", "roc_auc", "lift_10"}
