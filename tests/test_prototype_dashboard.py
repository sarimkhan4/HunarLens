# What: checks the prototype bridge uses the approved model and validation.
# Why: a custom interface must not introduce another scoring rule.
# Viva: the visual layer sends inputs to the same frozen pipeline.
import json
from pathlib import Path
import sys

import joblib
import pandas as pd
import pytest
from threadpoolctl import threadpool_limits
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
from hunarlens.app_utils import build_input, predict_probability
from prototype_dashboard import INPUT_NAMES, dashboard_data, view_data


def test_prototype_uses_frozen_pipeline_and_rejects_invalid_inputs():
    metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    model = joblib.load(ROOT / "models/final_pipeline.joblib")
    census = pd.read_csv(ROOT / "data/processed/census_lookup.csv")
    with threadpool_limits(limits=1):
        for changes in [{}, {"age": 18, "education_level": 6, "currently_enrolled": 7},
                        {"age": 22, "sex": 2, "area": 2, "education_level": 13, "currently_enrolled": 1}]:
            values, result = view_data(metadata, model, changes)
            assert not result["errors"]
            assert result["probability"] == pytest.approx(predict_probability(model, build_input(values, metadata, census)))
        values, result = view_data(metadata, model, {"household_size": 1, "children_under_15": 2})
        assert result["errors"] and "probability" not in result
        data = dashboard_data(metadata, model, {}, "overview")
    assert {field["name"] for field in data["fields"]} == set(INPUT_NAMES)
    assert data["metrics"]["HGB F1"]["f1"] == pytest.approx(0.360348292)


def test_prototype_app_loads():
    with threadpool_limits(limits=1):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90).run()
    assert not app.exception and not app.error
