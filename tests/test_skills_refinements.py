# What: checks the refined reporting and education-outcome partitions.
# Why: the written findings must follow generated tables and avoid causal claims.
# Viva: the four outcome groups describe the whole labour-force education band.
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


def test_findings_avoid_causal_phrases():
    text = (ROOT / "docs/skills_gap_findings.md").read_text(encoding="utf-8").lower()
    for phrase in ["causes", "because of", "leads to", "reduces unemployment", "raises unemployment"]:
        assert phrase not in text


def test_docs_match_regeneration_from_tables(tmp_path):
    report = load("skills_report_refinements", "09_skills_report.py")
    report.ROOT = tmp_path
    report.DOCS = tmp_path / "docs"
    report.DOCS.mkdir()
    (tmp_path / "notebooks").mkdir()
    report.write()
    for name in ["skills_gap_findings.md", "skills_gap_signoff.md"]:
        actual = (ROOT / "docs" / name).read_text(encoding="utf-8")
        expected = (report.DOCS / name).read_text(encoding="utf-8")
        assert actual == expected
        assert actual + "\n999999\n" != expected


def test_outcome_shares_partition_each_education_band():
    analysis = load("skills_outcomes_refinements", "09_analyze_skills.py")
    _, _, youth = analysis.prepare()
    labour = youth.loc[(youth.employed | youth.unemployed) & youth.band.gt(0)]
    table = pd.read_csv(ROOT / "reports/tables/skills_outcomes_by_education.csv", keep_default_na=False)
    for band, frame in labour.groupby("band"):
        masks = {"unemployed": frame.unemployed,
                 "employed matched": frame.employed & frame.band.eq(frame.all_15_plus),
                 "employed over": frame.employed & frame.band.gt(frame.all_15_plus),
                 "employed under": frame.employed & frame.band.lt(frame.all_15_plus)}
        shares = {name: frame.loc[mask, "weight"].sum() / frame.weight.sum() for name, mask in masks.items()}
        assert np.isclose(sum(shares.values()), 1, atol=1e-9, rtol=0)
        for category, share in shares.items():
            row = table.loc[table.group.eq(analysis.BANDS[int(band)]) & table.category.eq(category)].iloc[0]
            if row["estimate"] != "suppressed":
                assert np.isclose(float(row["estimate"]), share, atol=1e-9, rtol=0)


def test_degree_absorption_and_mismatch_tables_include_expected_groups():
    absorption = pd.read_csv(ROOT / "reports/tables/skills_graduate_absorption.csv")
    assert set(absorption.group) == {"overall", "sex=1.0", "sex=2.0", "area=1.0", "area=2.0"}
    assert len(absorption) == 15
    occupation = pd.read_csv(ROOT / "reports/tables/skills_mismatch_by_occupation.csv")
    assert set(occupation.group) == {"all_15_plus", "age_25_44", "youth", "ISCO"}
