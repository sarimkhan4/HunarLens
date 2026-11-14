# What: constructs the approved features and learns a household-size clip.
# Why: the training fold alone must determine the percentile threshold.
# Viva: transform applies the same threshold to every later row.
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

from hunarlens.config import HOUSEHOLD_CLIP_QUANTILE


class ApprovedFeatures(BaseEstimator, TransformerMixin):
    """Create simple demographic features without changing the input columns."""

    def fit(self, X: pd.DataFrame, y: object = None) -> "ApprovedFeatures":
        self.household_upper_ = float(X["household_size"].quantile(HOUSEHOLD_CLIP_QUANTILE))
        if not np.isfinite(self.household_upper_):
            raise ValueError("Cannot learn a household-size cutoff from missing values.")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        check_is_fitted(self, "household_upper_")
        data = X.copy()
        data["education_ordinal"] = data["education_level"]
        data["age_band"] = pd.cut(data["age"], bins=[14, 17, 20, 24], labels=["15-17", "18-20", "21-24"]).astype(object)
        data["children_share"] = data["children_under_15"] / data["household_size"].where(data["household_size"] > 0)
        data["household_size_clipped"] = data["household_size"].clip(upper=self.household_upper_)
        interaction = data["sex"].astype(str) + "_" + data["area"].astype(str)
        data["sex_area"] = interaction.where(data["sex"].notna() & data["area"].notna(), np.nan)
        return data
