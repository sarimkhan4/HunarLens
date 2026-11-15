# What: tests the interface, approved input checks and pipeline parity.
# Why: the app must use the exact saved model and reject inconsistent households.
# Viva: identical inputs must give identical probabilities in the app and pipeline.
import json
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
import pytest
import sklearn
from streamlit.testing.v1 import AppTest
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.app_utils import build_input, is_rare_combination, predict_probability, validate_inputs
from hunarlens.config import FEATURES
from hunarlens.ui import score_percentile


@pytest.fixture(scope="module")
def artifacts():
    metadata = json.loads((ROOT / "models" / "metadata.json").read_text(encoding="utf-8"))
    census = pd.read_csv(ROOT / "data" / "processed" / "census_lookup.csv")
    model = joblib.load(ROOT / "models" / "final_pipeline.joblib")
    return model, metadata, census


def test_app_smoke_and_navigation():
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60).run()
    assert not app.exception and not app.error
    assert any(box.label == "Relationship to household head" for box in app.selectbox)
    assert "most are working" in app.selectbox(key="currently_enrolled").help
    assert [tab.label for tab in app.tabs] == ["Estimate", "Insights", "About"]
    assert len(app.dataframe) >= 3
    about = " ".join(item.value for item in app.markdown)
    assert "not affiliated with or endorsed by PBS" in about
    assert "Inputs are not stored" in about


def test_head_display_and_form_validation():
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60).run()
    app.selectbox(key="relationship_to_head").select(1.0).run()
    assert not any(box.label == "Household head's sex" for box in app.selectbox)
    app.number_input(key="household_size").set_value(1)
    app.number_input(key="children_under_15").set_value(2)
    app.run()
    assert any("Household size must include" in error.value for error in app.error)
    assert not app.metric
    assert not app.exception


def test_app_submission_matches_pipeline(artifacts):
    model, metadata, census = artifacts
    expected_row = build_input(dict(metadata["reference_values"]), metadata, census)
    with threadpool_limits(limits=1):
        expected = predict_probability(model, expected_row)
        app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60).run()
    assert not app.exception and not app.error
    assert app.metric[0].value == f"{expected:.1%}"


def test_version_mismatch_warns(monkeypatch):
    monkeypatch.setattr(sklearn, "__version__", "different")
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60).run()
    assert any("scikit-learn version differs" in warning.value for warning in app.warning)


def test_household_and_head_consistency(artifacts):
    _, metadata, census = artifacts
    values = dict(metadata["reference_values"])
    values.update(household_size=2, children_under_15=2, other_youth_15_24=0)
    assert any("Household size must include" in error for error in validate_inputs(values, metadata))
    values.update(household_size=3, relationship_to_head=1, sex=2, head_sex=1)
    assert any("must match" in error for error in validate_inputs(values, metadata))
    values.update(head_sex=values["sex"], head_education=values["education_level"], can_read=2, can_write=1)
    assert any("unable to read" in error for error in validate_inputs(values, metadata))
    with pytest.raises(ValueError):
        build_input(values, metadata, census)


def test_app_pipeline_parity_20_random_valid_rows(artifacts):
    model, metadata, census = artifacts
    rng = np.random.default_rng(42)
    with threadpool_limits(limits=1):
        for _ in range(20):
            values = dict(metadata["reference_values"])
            for name, options in metadata["features"]["categorical"].items():
                values[name] = rng.choice(options).item()
            values["age"] = int(rng.integers(15, 25))
            values["children_under_15"] = int(rng.integers(0, 4))
            values["other_youth_15_24"] = int(rng.integers(0, 3))
            values["household_size"] = 1 + values["children_under_15"] + values["other_youth_15_24"]
            if values["can_read"] == 2:
                values["can_write"] = 2
            if values["relationship_to_head"] == 1:
                values["head_sex"] = values["sex"]
                values["head_education"] = values["education_level"]
            row = build_input(values, metadata, census)
            assert list(row.columns) == FEATURES
            assert predict_probability(model, row) == pytest.approx(model.predict_proba(row)[0, 1], abs=1e-6)


def test_metadata_and_tracked_input_schema(artifacts):
    model, metadata, census = artifacts
    assert set(metadata["reference_values"]) == set(FEATURES)
    assert set(metadata["features"]["numeric"]) | set(metadata["features"]["categorical"]) == set(FEATURES)
    assert not census.duplicated(["province", "area"]).any()
    assert model.named_steps["model"].__class__.__name__ == metadata["model_name"]


def test_category_encodings_are_normalized_and_unknown_rejected(artifacts):
    model, metadata, census = artifacts
    baseline = dict(metadata["reference_values"])
    baseline.update(sex=2, area=2, education_level=7, currently_enrolled=7)
    categorical = metadata["features"]["categorical"]
    raw_fields = set(categorical) | {"age", "household_size", "children_under_15", "other_youth_15_24"}
    variants = [{**baseline, **{name: cast(baseline[name]) for name in raw_fields}}
                for cast in [int, float, str]]
    with threadpool_limits(limits=1):
        rows = [build_input(variant, metadata, census) for variant in variants]
        probabilities = [predict_probability(model, row) for row in rows]
    assert probabilities == pytest.approx([probabilities[0]] * 3, abs=1e-12)
    assert all(row.sex.dtype == "float64" and row.area.dtype == "float64" for row in rows)
    assert all(row.household_size.dtype == "int64" and row.has_training.dtype == "int64" for row in rows)
    with pytest.raises(ValueError, match="supported value for sex"):
        build_input({**baseline, "sex": "999"}, metadata, census)


def test_rare_flags_and_warnings(artifacts):
    _, metadata, _ = artifacts
    flags = pd.read_csv(ROOT / "data/processed/rare_combinations.csv", dtype={"age_key": str, "rare": bool})
    assert set(flags.columns) == {"kind", "age_key", "category", "rare"}
    assert not flags.duplicated(["kind", "age_key", "category"]).any()
    assert is_rare_combination({**metadata["reference_values"], "age": 15, "education_level": 8}, flags)
    with threadpool_limits(limits=1):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=60).run()
        app.slider[0].set_value(15)
        app.selectbox(key="education_level").select(8.0)
        app.run()
    assert app.metric and any("combination is rare" in warning.value for warning in app.warning)


def test_marital_relationship_warning_does_not_block():
    with threadpool_limits(limits=1):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=60).run()
        app.selectbox(key="relationship_to_head").select(3.0).run()
        app.selectbox(key="marital_status").select(2.0)
        app.run()
    assert app.metric and any("relationship says" in warning.value for warning in app.warning)


def test_live_examples_and_ruler():
    with threadpool_limits(limits=1):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=60).run()
        assert app.metric[0].value == "9.3%"
        app.button[0].click().run()
        assert app.metric[0].value == "0.7%"
        app.button[2].click().run()
        assert app.metric[0].value == "34.0%"
        assert app.selectbox(key="area").value == 2.0
        app.number_input(key="household_size").set_value(1).run()
        assert not app.metric and any("Household size" in error.value for error in app.error)
    quantiles = json.loads((ROOT / "models/score_quantiles.json").read_text(encoding="utf-8"))["quantiles"]
    positions = [score_percentile(value, quantiles) for value in [0, .01, .1, .3, 1]]
    assert positions == sorted(positions) and positions[0] == 0 and positions[-1] == 100
