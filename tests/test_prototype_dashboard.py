# What: checks the prototype bridge uses the approved model and validation.
# Why: a custom interface must not introduce another scoring rule.
# Viva: the visual layer sends inputs to the same frozen pipeline.
import json
from pathlib import Path
import sys
import subprocess
import shutil

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


def test_browser_values_are_validated_and_normalized():
    metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    model = joblib.load(ROOT / "models/final_pipeline.joblib")
    with threadpool_limits(limits=1):
        _, missing = view_data(metadata, model, {"household_size": None})
        assert missing["errors"] == ["Enter a number for household size."]
        _, bad = view_data(metadata, model, {"sex": 999})
        assert bad["errors"] == ["Check your inputs."]
        _, extra = view_data(metadata, model, {"unexpected": 1})
        assert extra["errors"] == ["Check your inputs."]
        _, int_result = view_data(metadata, model, {"sex": 2})
        _, float_result = view_data(metadata, model, {"sex": 2.0})
        _, string_result = view_data(metadata, model, {"sex": "2"})
        assert int_result["probability"] == float_result["probability"] == string_result["probability"]


def test_no_invented_static_dashboard_values():
    forbidden = ["Prototype", "Illustrative", "14.9", "13.6", "32.8", "59.3", "sent to a server", "scoring logic", "Drop in accuracy"]
    for name in ["prototype.html", "prototype.css", "prototype.js", "streamlit_app.py"]:
        text = (ROOT / "app" / name).read_text(encoding="utf-8")
        assert not any(value in text for value in forbidden), name


def test_dashboard_uses_only_verified_aggregates():
    metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    model = joblib.load(ROOT / "models/final_pipeline.joblib")
    with threadpool_limits(limits=1):
        data = dashboard_data(metadata, model, {}, "overview")
    indicators = pd.read_csv(ROOT / "reports/tables/overview_indicators.csv")
    valid = indicators[indicators.status.eq("verified")].set_index("indicator")
    for name, value in data["survey"].items():
        assert value == pytest.approx(valid.loc[name, "pbs_value"])
    metrics = pd.read_csv(ROOT / "reports/tables/test_metrics.csv").set_index("model_threshold")
    for model_name, row in data["metrics"].items():
        for key, value in row.items():
            assert value == pytest.approx(metrics.loc[model_name, key])


def test_prototype_app_loads():
    with threadpool_limits(limits=1):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90).run()
    assert not app.exception and not app.error


def test_replacement_delta_is_reversed_for_plain_language():
    if not shutil.which("node"):
        pytest.skip("Node is unavailable for the JavaScript semantics check")
    source = (ROOT / "app/prototype.js").read_text(encoding="utf-8-sig")
    script = "const m=await import('data:text/javascript;base64,'+Buffer.from(process.argv[1]).toString('base64'));if(m.relativeChange(-0.05)!==0.05||m.relativeChange(0.05)!==-0.05)process.exit(1)"
    subprocess.run(["node", "--input-type=module", "-e", script, source], check=True)


def test_indicator_download_uses_real_newlines():
    if not shutil.which("node"):
        pytest.skip("Node is unavailable for the JavaScript semantics check")
    source = (ROOT / "app/prototype.js").read_text(encoding="utf-8-sig")
    script = "const m=await import('data:text/javascript;base64,'+Buffer.from(process.argv[1]).toString('base64'));const s=m.indicatorCsv([{indicator:'x',our_value:1,pbs_value:1,source_url:'url',difference:0,status:'verified'}]);if(s.split('\\n').length!==2||s.includes('\\\\n'))process.exit(1)"
    subprocess.run(["node", "--input-type=module", "-e", script, source], check=True)


def test_component_unavailable_renders_classic(monkeypatch):
    import streamlit as st
    monkeypatch.delattr(st.components, "v2")
    with threadpool_limits(limits=1):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90).run()
    assert not app.exception
    assert any("classic view" in warning.value for warning in app.warning)
    assert any(metric.label == "Youth unemployment" for metric in app.metric)
