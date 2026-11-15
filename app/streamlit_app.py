# What: presents the frozen youth-unemployment model and its limitations.
# Why: make aggregate survey patterns understandable without saving user input.
# Viva: the form supplies raw fields to the same fitted pipeline used in evaluation.
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import sklearn
import streamlit as st

from hunarlens.app_utils import LABELS, build_input, is_rare_combination, predict_probability, risk_label, validate_inputs
from hunarlens.explain import local_what_if

TABLES = ROOT / "reports" / "tables"
FIGURES = ROOT / "reports" / "figures"
NOTE = "Association from survey data, not a cause. Not a decision tool for individuals."


@st.cache_resource
def load_metadata():
    """Reuse training metadata without caching any form input."""
    return json.loads((ROOT / "models" / "metadata.json").read_text(encoding="utf-8"))


@st.cache_resource
def load_model():
    """Reuse the frozen fitted pipeline between requests."""
    return joblib.load(ROOT / "models" / "final_pipeline.joblib")


def category(name, metadata, label):
    """Offer only training-observed categories, with the training mode selected."""
    choices = metadata["features"]["categorical"][name]
    default = metadata["reference_values"][name]
    help_text = ("Among enrolled youth in the labour-force sample, most are working; "
                 "the model estimates lower unemployment for them.") if name == "currently_enrolled" else None
    return st.selectbox(label, choices, index=choices.index(default) if default in choices else 0,
                        format_func=lambda value: LABELS[name].get(int(value), f"Code {value:g}"), key=name,
                        help=help_text)


def number(name, metadata, label):
    """Use observed training bounds and the training median as the initial value."""
    low, high = metadata["features"]["numeric"][name]
    default = int(metadata["reference_values"][name])
    return st.number_input(label, min_value=int(low), max_value=int(high), value=default, step=1, key=name)


def importance_chart():
    """Draw the precomputed, geographically consistent grouped importance."""
    table = pd.read_csv(TABLES / "grouped_permutation_importance.csv")
    table = table.loc[~table["group"].isin(["Region", "Sex and area"])].sort_values("importance_mean")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(table["group"], table.importance_mean, xerr=table.importance_std, color="#277da1", capsize=3)
    ax.axvline(0, color="black", linewidth=.8)
    ax.set(xlabel="Decrease in validation average precision", ylabel="Feature group", title="Model reliance on feature groups")
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption("Error bars show variation across 20 permutations, not confidence intervals. Correlated inputs can share importance.")


def what_if_chart(model, row, metadata):
    """Compare predictions after individual inputs are replaced by training references."""
    ranking = pd.read_csv(TABLES / "permutation_importance.csv").feature.head(5).tolist()
    changes = local_what_if(model, row, metadata["reference_values"], ranking, top_k=5)
    changes = changes.sort_values("change")
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.barh(changes.feature.str.replace("_", " "), changes.change, color="#277da1")
    ax.axvline(0, color="black", linewidth=.8)
    ax.set(xlabel="Change in predicted probability", ylabel="Input replaced", title="Compared with typical training values")
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption("Each comparison changes one field at a time; some combinations may be uncommon. These are model associations.")


def estimator(model, metadata):
    """Collect approved fields, look up Census data and display the frozen prediction."""
    st.header("Risk estimator")
    st.caption("For a person aged 15–24 in the labour force: employed, or unemployed and available for work.")
    st.subheader("About the person")
    relationship = category("relationship_to_head", metadata, "Relationship to household head")
    with st.form("estimator"):
        values = {"relationship_to_head": relationship}
        age_min, age_max = metadata["features"]["numeric"]["age"]
        values["age"] = st.slider("Age (years)", int(age_min), int(age_max), int(metadata["reference_values"]["age"]))
        values["sex"] = category("sex", metadata, "Sex")
        values["marital_status"] = category("marital_status", metadata, "Marital status")
        st.subheader("Education and training")
        for name, label in [("education_level", "Education level"), ("can_read", "Can read"),
                            ("can_write", "Can write"), ("currently_enrolled", "Current enrolment"),
                            ("has_training", "Ever received or currently receiving training")]:
            values[name] = category(name, metadata, label)
        st.subheader("Location")
        values["province"] = category("province", metadata, "Province")
        values["area"] = category("area", metadata, "Area")
        st.subheader("Household")
        for name, label in [("household_size", "Household size, including this person"),
                            ("children_under_15", "Children under 15 in the household"),
                            ("other_youth_15_24", "Other youth aged 15–24 in the household")]:
            values[name] = number(name, metadata, label)
        if relationship == 1:
            values["head_sex"] = values["sex"]
            values["head_education"] = values["education_level"]
            st.caption("As the household head, this person's sex and education are used for the head fields.")
        else:
            values["head_sex"] = category("head_sex", metadata, "Household head's sex")
            values["head_education"] = category("head_education", metadata, "Household head's education")
        submitted = st.form_submit_button("Estimate")
    st.caption(NOTE)
    if not submitted:
        return
    errors = validate_inputs(values, metadata)
    if errors:
        for error in errors:
            st.error(error)
        return
    if values["age"] <= 17 and values["education_level"] >= 8:
        st.warning("A university degree at this age is unusual. Please check the education selection.")
    if values["relationship_to_head"] == 3 and values["marital_status"] != 1:
        st.warning("The relationship says son or daughter (unmarried), but the marital status is not never married. Please check the selections.")
    try:
        census = pd.read_csv(ROOT / "data" / "processed" / "census_lookup.csv")
        row = build_input(values, metadata, census)
        flags = pd.read_csv(ROOT / "data" / "processed" / "rare_combinations.csv", dtype={"age_key": str, "rare": bool})
        if is_rare_combination(values, flags):
            st.warning("This combination is rare in the survey data, so the estimate is less reliable.")
        probability = predict_probability(model, row)
        left, right = st.columns(2)
        left.metric("Estimated unemployment probability", f"{probability:.1%}")
        right.metric("Training sample base rate", f"{metadata['prevalence_train']:.1%}")
        st.write(f"**Relative band:** {risk_label(probability, metadata)}")
        if probability >= metadata["threshold_f1"]:
            st.write("**Flagged for follow-up** at the validation-selected threshold.")
        else:
            st.write("Not flagged for follow-up at the validation-selected threshold.")
        st.subheader("How the model uses information")
        importance_chart()
        st.subheader("What changes this estimate")
        what_if_chart(model, row, metadata)
    except Exception:
        st.error("The estimate is temporarily unavailable. Please check the inputs and try again.")


def insights():
    """Display saved comparisons and the single final test evaluation."""
    st.header("Insights")
    st.subheader("Model experiments")
    experiment = pd.read_csv(TABLES / "experiments.csv")
    chosen = experiment.loc[experiment.exp_id.eq("E4"), ["model", "cv_ap_mean", "val_f1_best", "threshold"]]
    st.dataframe(chosen.rename(columns={"model": "Model", "cv_ap_mean": "Grouped CV PR-AUC",
                                        "val_f1_best": "Validation F1", "threshold": "Tuned threshold"}), hide_index=True)
    st.caption("Validation F1 is optimistic: thresholds were chosen on the same validation labels. The final HGB threshold uses the approved near-optimal midpoint rule.")
    st.subheader("Final test results")
    st.dataframe(pd.read_csv(TABLES / "test_metrics.csv"), hide_index=True)
    st.write("95% household-grouped bootstrap intervals")
    st.dataframe(pd.read_csv(TABLES / "test_bootstrap_ci.csv"), hide_index=True)
    st.image(str(FIGURES / "test_pr_curve.png"), caption="Test precision–recall curve; dashed line is prevalence.")
    st.subheader("Subgroup caveats")
    groups = pd.read_csv(TABLES / "test_subgroups.csv")
    st.dataframe(groups, hide_index=True)
    st.warning("Subgroups with fewer than 50 unemployed people are flagged as unreliable; larger groups may still have substantial uncertainty. Performance differs across education, sex and area.")
    st.caption(NOTE)


def about():
    """Explain the approved label, public sources and limitations in plain language."""
    st.header("About and limits")
    st.markdown("""HunarLens describes patterns in Pakistan's **Labour Force Survey 2024–25** and **Population and Housing Census 2023**. Sources: [Pakistan Bureau of Statistics labour-force statistics](https://www.pbs.gov.pk/labour-force-statistics/) and [Census detailed results](https://pbs.gov.pk/result-excel/), accessed **15 November 2026**.

    The model uses youth aged **15–24 in the labour force**. Employed people worked for pay or profit, did qualifying family or sale-oriented farm work, or were temporarily absent under the survey rules. Unemployed people were not employed, were available within two weeks and either searched in the previous four weeks or had a job or business to start in the near future. The data do not record the start date, so the [ILO's generally three-month future-starter condition](https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf) could not be verified. See the [PBS annual report](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf) for the survey's definitions.

    Results are **unweighted** and describe survey associations, not causes. Census density and urban share are constant within province; Census household size is constant within province and area. Enrolment is a strong correlate partly reflecting selection into the labour-force-only sample. Performance and errors vary by subgroup, and small groups are uncertain.

    Inputs are not stored by this app. HunarLens is not affiliated with or endorsed by PBS. On the unweighted test set, the frozen model had F1 **0.360**, PR-AUC **0.303** and ROC-AUC **0.752**. Performance was weaker for some groups: recall for people with no formal education was **17.9%** at the primary threshold. Students outside the labour force are not included in the sample, so these results do not describe them.

    **Association from survey data, not a cause. Not a decision tool for individuals.**""")


def main():
    st.set_page_config(page_title="HunarLens", page_icon="🌱", layout="wide")
    st.title("HunarLens")
    try:
        metadata = load_metadata()
    except Exception:
        st.error("The model details are temporarily unavailable. Please try again later.")
        return
    if sklearn.__version__ != metadata.get("sklearn_version"):
        st.warning("The installed scikit-learn version differs from the model's saved version; predictions may be unreliable.")
    try:
        model = load_model()
    except Exception:
        st.error("The model is temporarily unavailable. Please try again later.")
        return
    page = st.sidebar.radio("Explore", ["Risk estimator", "Insights", "About and limits"])
    try:
        if page == "Risk estimator":
            estimator(model, metadata)
        elif page == "Insights":
            insights()
        else:
            about()
    except Exception:
        st.error("This page is temporarily unavailable. Please try again later.")


if __name__ == "__main__":
    main()
