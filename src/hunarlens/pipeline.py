# What: assembles preprocessing and an estimator into a single pipeline.
# Why: preprocessing must learn from training rows only.
# Viva: the same fitted transformations are reused for validation and prediction.
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from hunarlens.config import CATEGORICAL_FEATURES, MIN_CATEGORY_FREQUENCY, NUMERIC_FEATURES
from hunarlens.features import ApprovedFeatures


def build_preprocessor() -> ColumnTransformer:
    """Impute and scale numeric fields; impute and one-hot encode categories."""
    numeric = [x for x in NUMERIC_FEATURES if x != "household_size"] + ["household_size_clipped", "education_ordinal", "children_share"]
    categorical = CATEGORICAL_FEATURES + ["age_band", "sex_area"]
    return ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                  ("encode", OneHotEncoder(handle_unknown="ignore", min_frequency=MIN_CATEGORY_FREQUENCY))]), categorical),
    ])


def build_model_pipeline(model: object) -> Pipeline:
    """Keep feature construction, preprocessing and the estimator together."""
    return Pipeline([("features", ApprovedFeatures()), ("preprocess", build_preprocessor()), ("model", model)])
