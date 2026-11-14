# What: checks the initial configuration.
# Why: gives the project a small setup test. Viva: pytest checks an expected constant.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hunarlens.config import RANDOM_STATE


def test_random_state() -> None:
    assert RANDOM_STATE == 42
