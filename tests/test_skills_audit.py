# What: checks disclosure and consistency in the skills variable audit.
# Why: generated counts and documentation must agree without exposing small cells.
# Viva: the unweighted count determines whether an estimate is suppressed.
from pathlib import Path

import pandas as pd

from hunarlens.skills import audit_document_matches, safe_cell

ROOT = Path(__file__).resolve().parents[1]


def test_small_cells_are_suppressed_and_small_groups_flagged():
    assert safe_cell(29, 1000) == ("suppressed", "suppressed", "suppressed: n < 30")
    assert "unreliable" in safe_cell(30, 1000)[2]
    assert safe_cell(50, 1000)[2] == ""


def test_audit_tables_never_publish_small_counts():
    for name in ("skills_audit_counts.csv", "skills_audit_occupation_groups.csv"):
        table = pd.read_csv(ROOT / "reports/tables" / name, keep_default_na=False)
        for row in table.itertuples(index=False):
            if row.n == "suppressed":
                assert row.weighted_n == "suppressed"
            else:
                assert int(row.n) >= 30
                assert ("unreliable" in row.flag) == (int(row.n) < 50)


def test_document_summary_matches_generated_counts():
    table = pd.read_csv(ROOT / "reports/tables/skills_audit_counts.csv", keep_default_na=False, dtype=str)
    assert audit_document_matches(ROOT / "docs/skills_gap_data_audit.md", table)
    changed = table.copy()
    changed.loc[0, "n"] = "999999999"
    assert not audit_document_matches(ROOT / "docs/skills_gap_data_audit.md", changed)
