# What: checks the pre-dashboard mismatch and reproduction reporting.
# Why: each sensitivity has a different meaning and unstable modes need a warning.
# Viva: survey estimates should be traceable to tables and their uncertainty visible.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"


def report_module():
    spec = spec_from_file_location("pres5_report", ROOT / "scripts/09_skills_report.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_definitions_are_separated_and_normative_row_present():
    report = report_module()
    headline = report.content()[0][2]
    assert "Strict above-mode shares across statistical norms:" in headline
    assert "Within-one-band matched shares across norms:" in headline
    assert "Severe shares, at least two bands above mode, across norms:" in headline
    assert "Normative ISCO above-level share:" in headline
    assert "Across the displayed definitions and samples" not in headline
    assert "| ISCO | Normative above level |" in report.mismatch_table()
    modes = pd.read_csv(TABLES / "skills_occupation_modes.csv")
    left = modes.loc[modes.norm.eq("all_15_plus")].set_index("occupation").mode_band
    right = modes.loc[modes.norm.eq("age_25_44")].set_index("occupation").mode_band
    assert left.equals(right)


def test_mode_unstable_rule_and_display():
    report = report_module()
    stability = pd.read_csv(TABLES / "skills_mode_stability.csv", keep_default_na=False)
    occupations = pd.read_csv(TABLES / "skills_mismatch_by_occupation.csv", keep_default_na=False)
    for row in occupations.to_dict("records"):
        code = int(row["category"].split()[-1])
        group = stability.loc[stability.norm.eq(row["group"]) & stability.occupation.eq(code)]
        changed = not group.empty and float(group.iloc[0].change_share) > .1
        try:
            wide = float(row["ci_high"]) - float(row["ci_low"]) > .30
        except ValueError:
            wide = False
        assert (row["reliability"] == "mode unstable") == (changed or wide)
        if not group.empty:
            assert group.reliability.eq(row["reliability"]).all()
        if row["reliability"] == "mode unstable":
            display = report.result_cell(row)
            assert "mode unstable" in display and "bootstrap range" in display
            assert display in report.occupation_table()


def test_education_reproduction_and_report_traceability():
    report = report_module()
    data = pd.read_csv(TABLES / "skills_reproduction.csv")
    rows = data.loc[data.indicator.str.startswith("unemployment_education_")]
    assert len(rows) == 6 and rows.status.eq("PASS").all()
    assert np.all(rows.difference_pp <= .5)
    assert rows.labour_force_n.notna().all()
    findings = (ROOT / "docs/skills_gap_findings.md").read_text(encoding="utf-8")
    signoff = (ROOT / "docs/skills_gap_signoff.md").read_text(encoding="utf-8")
    assert all(line in findings and line in signoff for line in report.content()[0])
    assert report.reproduction_table() in signoff
    assert report.mismatch_table() in signoff
    assert report.occupation_table() in findings and report.occupation_table() in signoff
