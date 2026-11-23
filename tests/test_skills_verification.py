# What: checks generated skills-audit and reproduction evidence.
# Why: published cells must obey disclosure rules and the pre-agreed gate.
# Viva: a reproduction gate checks definitions against external statistics.
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"


def test_reproduction_matches_gate():
    table = pd.read_csv(TABLES / "skills_reproduction.csv")
    assert set(table.status) <= {"PASS", "FLAG"}
    assert (table.difference_pp <= 1).all()


def test_routing_table_suppresses_small_cells():
    table = pd.read_csv(TABLES / "skills_audit_routing.csv", keep_default_na=False)
    for row in table.itertuples(index=False):
        if row.n == "suppressed":
            assert row.weighted_n == "suppressed"
        else:
            assert int(row.n) >= 30


def test_category_shares_do_not_expose_suppressed_cells():
    table = pd.read_csv(TABLES / "skills_audit_code_shares.csv", keep_default_na=False)
    suppressed = table.loc[table.n.eq("suppressed")]
    assert suppressed.sample_share.eq("").all()
    assert suppressed.weighted_share.eq("").all()
