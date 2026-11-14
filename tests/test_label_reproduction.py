# What: checks key provisional employment routes with synthetic responses.
# Why: the PBS reproduction check must not count own-use farming as employment.
# Viva: the test checks example questionnaire paths, not real survey records.
from pathlib import Path
import runpy

import pandas as pd


def test_provisional_routes() -> None:
    module = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "01_build_dataset.py"))
    empty = {name: float("nan") for name in module["COLS"]}
    rows = [
        {**empty, "S5C1": 1},
        {**empty, "S5C2": 1, "S5C9": 1, "S5C10": 4, "S9C1": 1, "S9C6": 1},
        {**empty, "S5C3": 1, "S5C9": 1, "S5C10": 2},
        {**empty, "S5C4": 1, "S5C6": 1},
        {**empty, "S9C1": 2, "S9C5": 1, "S9C6": 1},
        {**empty, "S9C1": 2, "S9C5": 1, "S9C6": 2},
    ]
    employed, unemployed = module["provisional_status"](pd.DataFrame(rows))
    assert employed.tolist() == [True, False, True, True, False, False]
    assert unemployed.tolist() == [False, True, False, False, True, False]
