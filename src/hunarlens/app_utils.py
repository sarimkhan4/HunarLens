# What: validates form inputs and calls the approved prediction pipeline.
# Why: the interface and tests must use the same input checks and prediction path.
# Viva: Census values are looked up, while preprocessing stays inside the pipeline.
from typing import Any

import math
import pandas as pd

from hunarlens.config import FEATURES

EDUCATION = {1: "No formal education", 2: "Nursery but below kindergarten", 3: "Kindergarten but below primary",
             4: "Primary but below middle", 5: "Middle but below matric", 6: "Matric but below intermediate",
             7: "Intermediate but below degree", 8: "Degree in engineering", 9: "Degree in medicine",
             10: "Degree in computer science", 11: "Degree in agriculture", 12: "Degree in other subject",
             13: "BS/BE (4 years)", 14: "MA/MSc", 15: "MPhil/MS", 16: "PhD"}
ENROLMENT = {1: "Not currently enrolled", 2: "Nursery", 3: "Kindergarten", 4: "Primary", 5: "Middle",
             6: "Matric", 7: "Intermediate", 8: "Engineering degree", 9: "Medicine degree",
             10: "Computer degree", 11: "Agriculture degree", 12: "Other degree", 13: "BS/BE (4 years)",
             14: "MA/MSc", 15: "MPhil/MS", 16: "PhD"}
LABELS = {"sex": {1: "Male", 2: "Female"}, "head_sex": {1: "Male", 2: "Female"},
          "marital_status": {1: "Never married", 2: "Married", 3: "Widowed", 4: "Divorced"},
          "relationship_to_head": {1: "Head of household", 2: "Spouse", 3: "Son or daughter (unmarried)",
                                   4: "Son or daughter (married)", 5: "Parent", 6: "Sibling", 7: "Other relative",
                                   8: "Household employee", 9: "Non-relative"},
          "can_read": {1: "Yes", 2: "No"}, "can_write": {1: "Yes", 2: "No"},
          "education_level": EDUCATION, "head_education": EDUCATION, "currently_enrolled": ENROLMENT,
          "has_training": {0: "No", 1: "Yes"}, "province": {1: "Khyber Pakhtunkhwa", 2: "Punjab", 3: "Sindh", 4: "Balochistan"},
          "area": {1: "Rural", 2: "Urban"}}

COUNT_FIELDS = {"household_size", "children_under_15", "other_youth_15_24"}


def normalize_inputs(values: dict, metadata: dict) -> dict:
    """Resolve codes to the exact typed metadata values used by the encoder."""
    result = {}
    for name, choices in metadata["features"]["categorical"].items():
        try:
            number = float(values[name])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"Choose a supported value for {name.replace('_', ' ')}.") from None
        matches = [choice for choice in choices if number == choice]
        if not matches:
            raise ValueError(f"Choose a supported value for {name.replace('_', ' ')}.")
        result[name] = matches[0]
    for name in metadata["features"]["numeric"]:
        if name.startswith("census_"):
            continue
        try:
            value = float(values[name])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"Enter a valid number for {name.replace('_', ' ')}.") from None
        if not math.isfinite(value) or not value.is_integer():
            raise ValueError(f"Enter a whole number for {name.replace('_', ' ')}.")
        result[name] = int(value) if name in COUNT_FIELDS else value
    return result


def validate_inputs(values: dict, metadata: dict) -> list[str]:
    """Check training ranges, logical household counts and literacy consistency."""
    try:
        values = normalize_inputs(values, metadata)
    except ValueError as error:
        return [str(error)]
    errors = []
    for name, bounds in metadata["features"]["numeric"].items():
        if name.startswith("census_"):
            continue
        if name not in values or not bounds[0] <= values[name] <= bounds[1]:
            errors.append(f"{name.replace('_', ' ').title()} must be between {bounds[0]:g} and {bounds[1]:g}.")
    if values.get("household_size", 0) < 1 + values.get("children_under_15", 0) + values.get("other_youth_15_24", 0):
        errors.append("Household size must include this person, the children and the other youth counted.")
    if values.get("can_read") == 2 and values.get("can_write") == 1:
        errors.append("Someone marked as unable to read cannot also be marked as able to write.")
    if values.get("relationship_to_head") == 1:
        if values.get("head_sex") != values.get("sex") or values.get("head_education") != values.get("education_level"):
            errors.append("For a household head, head sex and education must match the person's answers.")
    return errors


def build_input(values: dict, metadata: dict, census: pd.DataFrame) -> pd.DataFrame:
    """Construct the approved raw model row after validating and joining Census."""
    errors = validate_inputs(values, metadata)
    if errors:
        raise ValueError(" ".join(errors))
    values = normalize_inputs(values, metadata)
    match = census.loc[census.province.eq(values["province"]) & census.area.eq(values["area"])]
    if len(match) != 1:
        raise ValueError("Census information is unavailable for this location.")
    row = dict(values)
    for name in ["census_density", "census_urban_proportion", "census_household_size"]:
        row[name] = float(match.iloc[0][name])
    return pd.DataFrame([row], columns=FEATURES)


def is_rare_combination(values: dict, rare_flags: pd.DataFrame) -> bool:
    """Read training-derived flags without retaining counts or individual rows."""
    age = int(values["age"])
    bands = rare_flags.loc[rare_flags.kind == "age_band_enrolment", "age_key"].unique()
    matches = [band for band in bands if int(band.split("-")[0]) <= age <= int(band.split("-")[1])]
    if len(matches) != 1:
        raise ValueError("Rare-combination age band is unavailable for this age.")
    band = matches[0]
    enrolled = rare_flags.loc[(rare_flags.kind == "age_band_enrolment") &
                              (rare_flags.age_key == band) & (rare_flags.category == float(values["currently_enrolled"]))]
    educated = rare_flags.loc[(rare_flags.kind == "age_education") &
                              (rare_flags.age_key == str(age)) & (rare_flags.category == float(values["education_level"]))]
    if len(enrolled) != 1 or len(educated) != 1:
        raise ValueError("Rare-combination information is unavailable for these inputs.")
    return bool(enrolled.rare.iloc[0] or educated.rare.iloc[0])


def predict_probability(model: Any, row: pd.DataFrame) -> float:
    """Return the frozen pipeline's probability for a single validated row."""
    return float(model.predict_proba(row[FEATURES])[0, 1])


def risk_label(probability: float, metadata: dict) -> str:
    """Apply the saved validation-derived band cut-offs without re-estimation."""
    bands = metadata["risk_bands"]
    if probability >= bands["high_min"]:
        return "High"
    if probability >= bands["elevated_min"]:
        return "Elevated"
    return "Lower than most"
