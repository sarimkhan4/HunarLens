# What: connects the extracted HTML dashboard to the approved survey model.
# Why: preserve the prototype's layout while using the same validation and predictions.
# Viva: the browser sends raw choices; Python validates and calls the frozen pipeline.
import json
import base64
from pathlib import Path
import pandas as pd
import streamlit as st
from hunarlens.app_utils import LABELS, build_input, is_rare_combination, predict_probability, risk_label, validate_inputs
from hunarlens.explain import local_what_if
from hunarlens.ui import score_percentile

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"
INPUT_NAMES = ["sex", "area", "age", "education_level", "currently_enrolled", "marital_status",
               "relationship_to_head", "can_read", "can_write", "has_training", "province",
               "household_size", "children_under_15", "other_youth_15_24", "head_sex", "head_education"]
NAMES = {"age":"Age (years)", "sex":"Sex", "area":"Area", "education_level":"Highest education completed",
         "currently_enrolled":"Current enrolment", "marital_status":"Marital status",
         "relationship_to_head":"Relationship to household head", "can_read":"Can read",
         "can_write":"Can write", "has_training":"Ever or currently receiving training",
         "province":"Province", "household_size":"Household size (including this person)",
         "children_under_15":"Children under 15", "other_youth_15_24":"Other youth aged 15–24",
         "head_sex":"Household head's sex", "head_education":"Household head's education"}
HELP = {"currently_enrolled":"Enrolled youth in the labour-force sample are mostly working; students outside the labour force are not included.",
        "other_youth_15_24":"Do not count this person.", "household_size":"Include everyone in the household, including this person.",
        "age":"Age in completed years.", "sex":"Sex recorded in the survey.", "area":"Rural or urban location.",
        "education_level":"Highest level completed.", "marital_status":"Current marital status.",
        "relationship_to_head":"This person's relationship to the household head.",
        "can_read":"Can read a simple statement with understanding.", "can_write":"Can write a simple statement with understanding.",
        "has_training":"Ever received or currently receiving training.", "province":"Province where the household lives.",
        "children_under_15":"Household members younger than 15.", "head_sex":"Sex of the household head.",
        "head_education":"Highest education level completed by the household head."}

def view_data(metadata, model, profile, explore="age"):
    """Build a view from the same validation and prediction functions as the app."""
    values = {name: profile.get(name, metadata["reference_values"][name]) for name in INPUT_NAMES}
    if values["relationship_to_head"] == 1:
        values["head_sex"], values["head_education"] = values["sex"], values["education_level"]
    errors = validate_inputs(values, metadata)
    result = {"errors": errors, "warnings": []}
    if errors:
        return values, result
    if values["age"] <= 17 and values["education_level"] >= 8:
        result["warnings"].append("A university degree at this age is unusual. Please check the education selection.")
    if values["relationship_to_head"] == 3 and values["marital_status"] != 1:
        result["warnings"].append("The relationship says son or daughter (unmarried), but marital status is not never married.")
    census = pd.read_csv(ROOT / "data/processed/census_lookup.csv")
    flags = pd.read_csv(ROOT / "data/processed/rare_combinations.csv", dtype={"age_key": str, "rare": bool})
    if is_rare_combination(values, flags):
        result["warnings"].append("This combination is rare in the survey data, so the estimate is less reliable.")
    row = build_input(values, metadata, census)
    probability = predict_probability(model, row)
    ranking = pd.read_csv(TABLES / "permutation_importance.csv").feature.head(5).tolist()
    changes = local_what_if(model, row, metadata["reference_values"], ranking, top_k=5)
    result.update(probability=probability, band=risk_label(probability, metadata),
                  flagged=probability >= metadata["threshold_f1"],
                  changes=changes[["feature","change"]].to_dict(orient="records"))
    quantiles = json.loads((ROOT / "models/score_quantiles.json").read_text(encoding="utf-8"))["quantiles"]
    result["percentile"] = score_percentile(probability, quantiles)
    if explore not in INPUT_NAMES:
        explore = "age"
    if explore in metadata["features"]["categorical"]:
        choices = metadata["features"]["categorical"][explore]
    else:
        bounds = metadata["features"]["numeric"][explore]
        choices = range(int(bounds[0]), int(bounds[1]) + 1)
    alternatives = []
    for choice in choices:
        candidate = {**values, explore: choice}
        if validate_inputs(candidate, metadata):
            continue
        alternative = build_input(candidate, metadata, census)
        alternatives.append({"label": LABELS.get(explore, {}).get(int(choice), str(int(choice))),
                             "probability": predict_probability(model, alternative),
                             "current": choice == values[explore],
                             "rare": is_rare_combination(candidate, flags)})
    result["alternatives"] = alternatives
    return values, result

def dashboard_data(metadata, model, profile, page, explore="age"):
    """Supply only aggregates, schema and this session's transient selections."""
    values, result = view_data(metadata, model, profile, explore)
    fields = []
    for name in INPUT_NAMES:
        field = {"name": name, "label": NAMES[name], "help": HELP.get(name, "")}
        if name in metadata["features"]["categorical"]:
            field["options"] = [{"value": value, "label": LABELS[name].get(int(value), f"Code {value:g}")}
                                for value in metadata["features"]["categorical"][name]]
        else:
            field["range"] = metadata["features"]["numeric"][name]
        fields.append(field)
    survey = pd.read_csv(TABLES / "label_reproduction.csv").set_index("group")["pbs_unemployment_rate"]
    metrics = pd.read_csv(TABLES / "test_metrics.csv").set_index("model_threshold")
    importance = pd.read_csv(TABLES / "grouped_permutation_importance.csv")
    importance = importance[~importance["group"].isin(["Region", "Sex and area"])]
    return {"fields": fields, "values": values, "result": result, "page": page, "explore": explore,
            "defaults": {name: metadata["reference_values"][name] for name in INPUT_NAMES},
            "base_rate": metadata["prevalence_train"], "threshold": metadata["threshold_f1"],
            "survey": survey.to_dict(), "metrics": metrics.to_dict(orient="index"),
            "importance": importance[["group","importance_mean","importance_std"]].to_dict(orient="records"),
            "test_table": pd.read_csv(TABLES / "test_metrics.csv").to_dict(orient="records"),
            "confidence": pd.read_csv(TABLES / "test_bootstrap_ci.csv").to_dict(orient="records"),
            "subgroups": pd.read_csv(TABLES / "test_subgroups.csv").to_dict(orient="records"),
            "experiments": pd.read_csv(TABLES / "experiments.csv").query('exp_id == "E4"')
                [["model", "cv_ap_mean", "val_f1_best", "threshold"]].to_dict(orient="records"),
            "pr_curve": base64.b64encode((ROOT / "reports/figures/test_pr_curve.png").read_bytes()).decode("ascii")}

@st.cache_resource
def dashboard_component():
    """Register the component once for all sessions."""
    return st.components.v2.component("hunarlens.prototype",
        html=(ROOT / "app/prototype.html").read_text(encoding="utf-8"),
        css=(ROOT / "app/prototype.css").read_text(encoding="utf-8"),
        js=(ROOT / "app/prototype.js").read_text(encoding="utf-8"))


def show_dashboard(metadata, model):
    """Mount the original HTML as a Streamlit component."""
    component = dashboard_component()
    state = st.session_state.get("prototype_ui", {})
    profile = state.get("profile", {}) or {}
    page = state.get("page", "overview") or "overview"
    explore = state.get("explore", "age") or "age"
    try:
        data = dashboard_data(metadata, model, profile, page, explore)
    except Exception:
        st.error("The estimate is temporarily unavailable. Please check the inputs and try again.")
        return
    component(key="prototype_ui", data=data, on_profile_change=lambda: None, on_page_change=lambda: None,
              on_explore_change=lambda: None)
