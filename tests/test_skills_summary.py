# What: checks structural-zero reporting and the sign-off diagnostics.
# Why: impossible outcomes must remain distinct from small observed cells.
# Viva: a structural zero follows from the definition, not a small sample.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = spec_from_file_location(name, ROOT / "scripts" / filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structural_zero_and_primary_suppression():
    analysis = load("skills_signoff_analysis", "analyze_skills_gap.py")
    frame = pd.DataFrame({"psu": ["a"] * 30 + ["b"] * 30, "weight": [1.0] * 60})
    boot = analysis.Bootstrap(frame)
    structural = analysis.result_row(boot, frame, pd.Series([False] * 60), "x", "zero", structural=True)
    assert structural["estimate"] == "—" and structural["positive_n"] == 0
    small = pd.Series([True] * 5 + [False] * 55)
    assert analysis.result_row(boot, frame, small, "x", "small")["estimate"] == "n<30"
    assert "unreliable" in analysis.result_row(boot, frame, small, "x", "small", reliability="positive")["flag"]
    assert analysis.result_row(boot, frame, ~small, "x", "complement")["estimate"] != "n<30"


def test_mode_stability_and_bootstrap_median():
    table = pd.read_csv(ROOT / "reports/tables/skills_mode_stability.csv")
    totals = table.groupby(["norm", "occupation"]).replicate_share.sum()
    assert np.allclose(totals, 1, atol=1e-9)
    assert (table.mode_sensitive == (table.change_share > .1)).all()
    for name in ["skills_mismatch.csv", "skills_mismatch_variants.csv"]:
        values = pd.read_csv(ROOT / "reports/tables" / name, keep_default_na=False)
        shown = values.loc[values.bootstrap_median.ne("") & values.estimate.ne("n<30") & values.estimate.ne("—")]
        assert len(shown) > 0
        for row in shown.itertuples(index=False):
            assert np.isclose(float(row.bootstrap_bias), float(row.bootstrap_median) - float(row.estimate), atol=1e-9)


def test_unemployment_and_employment_sum_for_each_band():
    analysis = load("skills_signoff_outcomes", "analyze_skills_gap.py")
    _, _, youth = analysis.prepare()
    labour = youth.loc[(youth.employed | youth.unemployed) & youth.band.gt(0)]
    table = pd.read_csv(ROOT / "reports/tables/skills_unemployment_by_education.csv")
    for band, group in labour.groupby("band"):
        unemployed = group.loc[group.unemployed, "weight"].sum() / group.weight.sum()
        employed = group.loc[group.employed, "weight"].sum() / group.weight.sum()
        assert np.isclose(unemployed + employed, 1, atol=1e-9)
        recorded = table.loc[table.group.eq("overall") & table.category.eq(analysis.BANDS[int(band)])].iloc[0]
        assert np.isclose(float(recorded["estimate"]), unemployed, atol=1e-9)


def test_every_visible_rate_cell_includes_unweighted_n():
    report = load("skills_signoff_report", "write_skills_report.py")
    for table_name in ["skills_unemployment_by_education.csv", "skills_outcomes_by_education.csv",
                       "skills_mismatch.csv", "skills_mismatch_variants.csv"]:
        table = pd.read_csv(ROOT / "reports/tables" / table_name, keep_default_na=False)
        for row in table.to_dict("records"):
            text = report.result_cell(row)
            if text not in ("n<30", "—"):
                assert "n=" in text


def test_findings_and_signoff_are_generated_from_tables(tmp_path):
    report = load("skills_signoff_generation", "write_skills_report.py")
    report.ROOT = tmp_path
    report.DOCS = tmp_path / "docs"
    report.DOCS.mkdir()
    (tmp_path / "notebooks").mkdir()
    report.write()
    for name in ["skills_gap_findings.md", "skills_gap_summary.md"]:
        actual = (ROOT / "docs" / name).read_text(encoding="utf-8")
        assert actual == (report.DOCS / name).read_text(encoding="utf-8")
        assert actual != actual + " 999999"
    findings = (report.DOCS / "skills_gap_findings.md").read_text(encoding="utf-8").lower()
    assert not any(term in findings for term in ["causes", "because of", "leads to", "reduces unemployment", "raises unemployment"])
