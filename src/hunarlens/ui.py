# What: maps a probability to its aggregate validation percentile.
# Why: the display must share a stable, testable ruler scale.
# Viva: interpolation locates a score within validation quantiles.
import numpy as np


def score_percentile(probability: float, quantiles: list[float]) -> float:
    """Interpolate a bounded percentile, tolerating repeated quantile values."""
    if len(quantiles) != 101 or np.any(np.diff(quantiles) < 0):
        raise ValueError("Expected 101 ordered validation quantiles.")
    return float(np.interp(probability, quantiles, np.arange(101), left=0, right=100))
