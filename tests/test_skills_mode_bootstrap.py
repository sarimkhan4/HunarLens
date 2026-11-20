# What: checks mode re-estimation in clustered mismatch bootstrap samples.
# Why: intervals should include uncertainty in the occupation-specific norms.
# Viva: resampling clusters can change the most common education band.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_modes_change_and_bootstrap_shares_sum_to_one():
    spec = spec_from_file_location("skills_modes", ROOT / "scripts/analyze_skills_gap.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = []
    for psu in range(8):
        for occupation in (1, 2):
            for _ in range(10):
                rows.append({"psu": str(psu), "occupation": occupation,
                             "band": 1 if psu < 5 else 2, "weight": 1.0})
    frame = pd.DataFrame(rows)
    first = module.Bootstrap(frame)
    second = module.Bootstrap(frame)
    modes = module.bootstrap_modes(first, frame)
    assert np.array_equal(first.draws, second.draws)
    assert np.array_equal(modes, module.bootstrap_modes(second, frame))
    full = module.modes(frame)
    assert np.any(modes[:, 0] != full.loc[1])
    shares = module.mismatch_bootstrap(first, frame, modes)
    assert np.allclose(shares.sum(axis=1), 1, atol=1e-9, rtol=0)
