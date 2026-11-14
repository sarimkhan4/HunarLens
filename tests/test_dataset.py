# What: verifies the processed schema and synthetic household calculations.
# Why: identifiers must not leak and household features use the full roster.
# Viva: tests check what reaches the modelling table, not private records.
from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES
from hunarlens.data import roster_features


def test_household_features_include_children_and_head() -> None:
    roster = pd.DataFrame({"PCode": ["a", "a", "a"], "EBCode": [1, 1, 1], "HHNo": [1, 1, 1],
                           "SNo": [1, 2, 3], "S4C3": [1, 3, 3], "S4C6": [40, 20, 9],
                           "S4C5": [2, 1, 2], "S4C9": [6, 5, 3]})
    result = roster_features(roster)
    assert result.loc[1, "household_size"] == 3
    assert result.loc[1, "children_under_15"] == 1
    assert result.loc[1, "other_youth_15_24"] == 0
    assert result.loc[1, "head_sex"] == 2
    assert result.loc[1, "head_education"] == 6


@pytest.mark.full_data
def test_processed_schema_and_privacy() -> None:
    path = ROOT / "data" / "processed" / "hunarlens_youth.csv"
    if not path.exists():
        pytest.skip("Processed microdata is not distributed; run the dataset build first.")
    data = pd.read_csv(path)
    assert set(data.columns) == set(FEATURES) | {"is_unemployed", "group_id"}
    assert list(data.columns) == ["group_id", *FEATURES, "is_unemployed"]
    assert len(FEATURES) >= 15
    assert set(data.is_unemployed.unique()) <= {0, 1}
    assert data.is_unemployed.notna().all()
    assert data.age.between(15, 24).all()
    assert data.group_id.notna().all()
    forbidden = {"pcode", "ebcode", "hhno", "sno", "s4c2", "weights", "quarter", "fstatus"}
    assert forbidden.isdisjoint(name.lower() for name in data.columns)
    assert not any(word in name.lower() for name in data.columns for word in ("name", "address", "phone", "cnic"))


def test_no_person_identifiers_in_other_processed_csvs() -> None:
    for path in (ROOT / "data" / "processed").glob("*.csv"):
        columns = pd.read_csv(path, nrows=0).columns.str.lower()
        assert not any(name in {"pcode", "ebcode", "hhno", "sno", "s4c2"} for name in columns)
        assert not any(word in name for name in columns for word in ("name", "address", "phone", "cnic"))
