# What: checks grouped splits, allowlists and training-only preprocessing.
# Why: prevents validation or test information entering fitted transformations.
# Viva: each test checks a potential route for leakage.
from pathlib import Path
import runpy
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, FEATURES, GROUP, TARGET
from hunarlens.pipeline import build_model_pipeline
from hunarlens.splits import load_assignments


@pytest.fixture
def split_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    data_path = DATA_PROCESSED / "hunarlens_youth.csv"
    split_path = DATA_PROCESSED / "split_assignments.csv"
    if not data_path.exists() or not split_path.exists():
        pytest.skip("Local processed data and split assignments are required.")
    data = pd.read_csv(data_path, usecols=[GROUP, TARGET])
    return data, load_assignments(split_path, data_path)


@pytest.mark.full_data
def test_no_group_overlap(split_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    data, assignments = split_data
    assert data.assign(split=assignments.split).groupby(GROUP).split.nunique().max() == 1


@pytest.mark.full_data
def test_split_fractions_and_prevalence(split_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    data, assignments = split_data
    summary = data.assign(split=assignments.split).groupby("split")[TARGET].agg(["size", "mean"])
    for name, fraction in {"train": 0.70, "val": 0.15, "test": 0.15}.items():
        assert abs(summary.loc[name, "size"] / len(data) - fraction) < 0.02
        assert abs(summary.loc[name, "mean"] - data[TARGET].mean()) < 0.01


@pytest.mark.full_data
def test_features_allowlist_and_label(split_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    columns = pd.read_csv(DATA_PROCESSED / "hunarlens_youth.csv", nrows=0).columns
    assert set(columns) == set(FEATURES) | {GROUP, TARGET}
    assert GROUP not in FEATURES and TARGET not in FEATURES
    data, _ = split_data
    assert data[TARGET].notna().all() and set(data[TARGET].unique()) <= {0, 1}


def test_fit_on_training_only() -> None:
    train = pd.DataFrame({name: [1.0, 2.0, 3.0, 4.0] for name in FEATURES})
    train["age"] = [15, 18, 21, 24]
    train["household_size"] = [2, 4, 6, 8]
    train["children_under_15"] = [0, 1, 2, 3]
    train.loc[0, "census_density"] = np.nan
    validation = train.copy()
    validation["household_size"] = 10000
    validation["census_density"] = 10000
    pipe = build_model_pipeline(DummyClassifier(strategy="stratified", random_state=42))
    pipe.fit(train, [0, 1, 0, 1])
    cutoff = pipe.named_steps["features"].household_upper_
    median = pipe.named_steps["preprocess"].named_transformers_["numeric"].named_steps["impute"].statistics_[3]
    scaler = pipe.named_steps["preprocess"].named_transformers_["numeric"].named_steps["scale"]
    pipe.predict(validation)
    assert cutoff == pytest.approx(train.household_size.quantile(0.99))
    assert median == pytest.approx(train.census_density.median())
    assert scaler.mean_[0] == pytest.approx(train.age.mean())
    assert pipe.named_steps["features"].household_upper_ == cutoff


@pytest.mark.full_data
def test_test_rows_skipped_in_evaluation(monkeypatch: pytest.MonkeyPatch, split_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, assignments = split_data
    original = pd.read_csv
    inspected = []
    def inspect(*args: object, **kwargs: object) -> pd.DataFrame:
        if Path(str(args[0])).name == "hunarlens_youth.csv":
            skip = kwargs.get("skiprows")
            assert callable(skip)
            assert all(skip(int(i) + 1) for i in assignments.index[assignments.split.eq("test")])
            inspected.append(True)
        return original(*args, **kwargs)
    monkeypatch.setattr(pd, "read_csv", inspect)
    script = runpy.run_path(str(ROOT / "scripts" / "compute_baselines.py"))
    script["load_train_validation"]()
    assert inspected


def test_requirements_pinned() -> None:
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            assert "==" in line
