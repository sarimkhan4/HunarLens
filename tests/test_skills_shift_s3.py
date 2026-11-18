# What: checks skill-shift averaging and saved aggregate protections.
# Why: scenario averages must agree with a direct calculation and hide small cells.
# Viva: weighted averages fall between the smallest and largest scenarios.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_shift():
    spec = spec_from_file_location("skills_shift", ROOT / "scripts/09_model_shift.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_five_validation_profiles_match_manual_weighted_average():
    shift = load_shift()
    frequencies, validation = shift.sample_profiles()
    metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
    census = pd.read_csv(ROOT / "data/processed/census_lookup.csv")
    flags = pd.read_csv(ROOT / "data/processed/rare_combinations.csv", dtype={"age_key": str, "rare": bool})
    model = joblib.load(ROOT / "models/final_pipeline.joblib")
    predicted = shift.predictions(model, validation.head(30), frequencies, metadata, census, flags)
    changes = shift.profile_changes(predicted, validation)
    groups = predicted.loc[predicted.scenario.eq("education")].groupby("index")
    indices = list(groups.groups)[:5]
    assert len(indices) == 5
    for index in indices:
        group = groups.get_group(index)
        manual = np.sum(group.probability.to_numpy() * group.frequency.to_numpy()) / group.frequency.sum()
        base = predicted.loc[(predicted["index"] == index) & predicted.scenario.eq("base"), "probability"].iloc[0]
        row = changes.loc[(changes["index"] == index) & changes.scenario.eq("education")].iloc[0]
        assert np.isclose(row["difference"], manual - base, rtol=0, atol=1e-12)
        assert row["min"] <= row["difference"] <= row["max"]


def test_shift_coverage_and_suppression_are_reported():
    table = pd.read_csv(ROOT / "reports/tables/skills_model_shift.csv", keep_default_na=False)
    assert {"coverage", "n", "minimum", "mean", "maximum"} <= set(table.columns)
    for row in table.itertuples(index=False):
        if row.n == "suppressed":
            assert row.mean == "suppressed" and row.coverage == "suppressed"
        else:
            assert int(row.n) >= 30
            assert 0 <= float(row.coverage) <= 1
            assert float(row.minimum) <= float(row.mean) <= float(row.maximum)


def test_independent_weighted_mean_agrees_for_five_examples():
    shift = load_shift()
    for values, weights in [([.1, .3], [1, 2]), ([.05, .1, .2], [4, 2, 1]),
                            ([.1], [1]), ([.2, .2], [3, 1]), ([.4, .1], [5, 3])]:
        mean, low, high = shift.average_codes(values, weights)
        manual = sum(v * w for v, w in zip(values, weights)) / sum(weights)
        assert abs(mean - manual) < 1e-12
        assert low <= mean <= high


def test_survey_outputs_respect_disclosure_and_required_sanity():
    for name in ["attainment_gap", "education_occupation_matrix", "outcomes_by_education",
                 "training_by_occupation", "mismatch", "mismatch_sensitivity", "neet", "degree_type"]:
        table = pd.read_csv(ROOT / "reports/tables" / f"skills_{name}.csv", keep_default_na=False)
        for row in table.itertuples(index=False):
            if row.estimate == "suppressed":
                assert row.ci_low == "suppressed" and row.ci_high == "suppressed"
            else:
                assert int(row.n) >= 30 and int(row.positive_n) >= 30
                assert 0 <= float(row.estimate) <= 1
    modes = pd.read_csv(ROOT / "reports/tables/skills_occupation_modes.csv")
    primary = modes.loc[modes.norm.eq("all_15_plus")].set_index("occupation")
    assert primary.loc[9, "mode_band"] != 5 and primary.loc[2, "mode_band"] != 1
    mismatch = pd.read_csv(ROOT / "reports/tables/skills_mismatch.csv")
    over = mismatch.loc[mismatch.group.eq("overall; norm=all_15_plus") & mismatch.category.eq("over"), "estimate"].iloc[0]
    assert float(over) < .6


def test_report_headlines_match_generated_tables(tmp_path):
    spec = spec_from_file_location("skills_report", ROOT / "scripts/09_skills_report.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    findings, _, _, _ = module.content()
    for name in ["skills_gap_findings.md", "skills_gap_signoff.md"]:
        document = (ROOT / "docs" / name).read_text(encoding="utf-8")
        assert all(line in document for line in findings)
    module.ROOT = tmp_path
    module.DOCS = tmp_path / "docs"
    module.DOCS.mkdir()
    (tmp_path / "notebooks").mkdir()
    module.write()
    for name in ["skills_gap_findings.md", "skills_gap_signoff.md", "skills_gap_methods.md"]:
        assert (module.DOCS / name).read_text(encoding="utf-8") == (ROOT / "docs" / name).read_text(encoding="utf-8")
    assert (tmp_path / "notebooks/07_skills_gap.ipynb").read_text(encoding="utf-8") == (ROOT / "notebooks/07_skills_gap.ipynb").read_text(encoding="utf-8")


def test_cluster_bootstrap_is_reproducible():
    spec = spec_from_file_location("skills_analysis", ROOT / "scripts/09_analyze_skills.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    frame = pd.DataFrame({"psu": ["a"] * 30 + ["b"] * 30, "weight": [1.0] * 60})
    first, second = module.Bootstrap(frame), module.Bootstrap(frame)
    assert np.array_equal(first.draws, second.draws)
    condition = pd.Series([True] * 30 + [False] * 30)
    row = module.result_row(first, frame, condition, "example", "share")
    assert abs(row["estimate"] - np.sum(frame.weight.to_numpy() * condition.to_numpy()) / frame.weight.sum()) < 1e-9


def test_s1_document_has_every_generated_field_count():
    table = pd.read_csv(ROOT / "reports/tables/skills_s1_field_values.csv", keep_default_na=False, dtype=str)
    document = (ROOT / "docs/skills_gap_data_audit.md").read_text(encoding="utf-8")
    for row in table.itertuples(index=False):
        assert f"`{row.variable}`" in document
        assert f"{row.code}: {row.n}" in document
        if row.n == "suppressed":
            assert row.weighted_n == "suppressed"
        else:
            assert int(row.n) >= 30
