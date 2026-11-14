# What: creates and validates reproducible household-aware split assignments.
# Why: household members must not leak between datasets.
# Viva: 20 grouped stratified folds are allocated 14, 3 and 3.
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from hunarlens.config import GROUP, RANDOM_STATE, SPLIT_FOLDS, TARGET


def file_hash(path: Path) -> str:
    """Tie row positions to the exact dataset that was split."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_assignments(data: pd.DataFrame, digest: str) -> pd.DataFrame:
    """Allocate groups without fitting a model or opening test metrics."""
    splitter = StratifiedGroupKFold(n_splits=SPLIT_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    labels = np.full(len(data), "", dtype=object)
    for fold, (_, indices) in enumerate(splitter.split(data, data[TARGET], groups=data[GROUP])):
        labels[indices] = "train" if fold < 14 else "val" if fold < 17 else "test"
    if (labels == "").any():
        raise ValueError("Some rows have no split assignment.")
    return pd.DataFrame({"row_id": np.arange(len(data)), "split": labels, "dataset_sha256": digest})


def load_assignments(path: Path, data_path: Path) -> pd.DataFrame:
    """Reject stale assignments if the underlying row order changed."""
    assignments = pd.read_csv(path)
    if assignments.dataset_sha256.nunique() != 1 or assignments.dataset_sha256.iloc[0] != file_hash(data_path):
        raise ValueError("Split assignments do not match the current dataset.")
    if not np.array_equal(assignments.row_id.to_numpy(), np.arange(len(assignments))):
        raise ValueError("Split row identifiers are not in order.")
    return assignments
