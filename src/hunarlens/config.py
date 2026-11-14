# What: central project constants.
# Why: shared settings have one source. Viva: the feature allowlist lives here.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = ROOT / "data" / "processed"
REPORT_TABLES = ROOT / "reports" / "tables"
REPORT_FIGURES = ROOT / "reports" / "figures"
MODELS_DIR = ROOT / "models"

RANDOM_STATE = 42
TARGET = "is_unemployed"
GROUP = "group_id"
SPLIT = "split"
AGE_MIN, AGE_MAX = 15, 24
SPLIT_FRACTIONS = {"train": 0.70, "val": 0.15, "test": 0.15}
SPLIT_FOLDS = 20
N_CV_FOLDS = 5

# The team must approve features after inspecting the data.
NUMERIC_FEATURES: list[str] = []
CATEGORICAL_FEATURES: list[str] = []
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

LABEL_KEYWORDS = [
    "employ", "job", "work", "occupation", "industry", "wage", "hours",
    "seek", "avail", "activity",
]
ALLOWED_DESPITE_KEYWORD: list[str] = []
