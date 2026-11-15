# What: checks local explanation output and complete approved feature groups.
# Why: what-if changes must be valid probabilities and cannot expose test data.
# Viva: replacing a value with itself must leave the prediction unchanged.
import json
from pathlib import Path
import sys

import joblib
import pandas as pd
import pytest
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES
from hunarlens.explain import GROUPS, local_what_if


def test_groups_cover_allowlist_exactly_once():
    members = [name for key, group in GROUPS.items() if key not in {"Region", "Sex and area"} for name in group]
    assert sorted(members) == sorted(FEATURES)
    assert set(GROUPS["Geography"]) == {"province", "area", "census_density", "census_urban_proportion", "census_household_size"}
    assert GROUPS["Sex"] == ["sex"]


def test_what_if_probabilities_and_identity():
    metadata_path = ROOT / "models" / "metadata.json"
    if not metadata_path.exists() or "reference_values" not in json.loads(metadata_path.read_text(encoding="utf-8")):
        pytest.skip("Run the Stage 7 explanation script first.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    row = pd.DataFrame([metadata["reference_values"]], columns=FEATURES)
    model = joblib.load(ROOT / "models" / "final_pipeline.joblib")
    with threadpool_limits(limits=1):
        result = local_what_if(model, row, metadata["reference_values"], FEATURES)
    assert result.original_probability.between(0, 1).all()
    assert result.new_probability.between(0, 1).all()
    assert result.change.abs().max() == pytest.approx(0.0, abs=1e-12)
    changed = row.copy()
    changed.loc[0, "age"] = 15 if row.loc[0, "age"] != 15 else 24
    with threadpool_limits(limits=1):
        result = local_what_if(model, changed, metadata["reference_values"], ["age"])
    assert result.new_probability.between(0, 1).all()
