# What: presents the frozen youth-unemployment model and its limitations.
# Why: make aggregate survey patterns understandable without saving user input.
# Viva: the form supplies raw fields to the same fitted pipeline used in evaluation.
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json
import altair as alt
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import sklearn
import streamlit as st

from hunarlens.app_utils import LABELS, build_input, is_rare_combination, predict_probability, risk_label, validate_inputs
from hunarlens.explain import local_what_if
from hunarlens.ui import score_percentile

TABLES = ROOT / "reports" / "tables"
FIGURES = ROOT / "reports" / "figures"
NOTE = "Association from survey data, not a cause. Not a decision tool for individuals."
HELP = {"age": "Age in completed years.", "sex": "Sex recorded in the survey.",
        "marital_status": "Current marital status.", "relationship_to_head": "This person's relationship to the household head.",
        "education_level": "Highest education level completed.", "can_read": "Can read a simple statement with understanding.",
        "can_write": "Can write a simple statement with understanding.",
        "currently_enrolled": "Among enrolled youth in the labour-force sample, most are working; the model estimates lower unemployment for them.",
        "has_training": "Whether this person has ever received or is currently receiving training.",
        "province": "Province where this person lives.", "area": "Whether the household is in a rural or urban area.",
        "household_size": "All people in the household, including this person.",
        "children_under_15": "Household members younger than 15.",
        "other_youth_15_24": "Other household members aged 15–24, excluding this person.",
        "head_sex": "Sex of the household head.", "head_education": "Highest education level of the household head."}
EXAMPLES = {"Rural, enrolled": {"age": 18, "education_level": 6.0, "currently_enrolled": 7.0},
            "Rural, not enrolled": {},
            "Urban graduate": {"age": 22, "sex": 2.0, "area": 2.0, "education_level": 13.0, "currently_enrolled": 1.0}}


def refresh_result():
    """Refresh the page so form controls remain available after each change."""
    st.rerun()


def apply_example(metadata, changes):
    """Fill widget state with a synthetic example, not a saved person record."""
    for name, value in {**metadata["reference_values"], **changes}.items():
        if not name.startswith("census_"):
            st.session_state[name] = int(value) if name in {"age", "household_size", "children_under_15", "other_youth_15_24"} else value


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
    if name not in st.session_state:
        st.session_state[name] = default if default in choices else choices[0]
    return st.selectbox(label, choices, index=None,
                        format_func=lambda value: LABELS[name].get(int(value), f"Code {value:g}"), key=name,
                        help=HELP[name], on_change=None if name == "relationship_to_head" else refresh_result)


def number(name, metadata, label):
    """Use observed training bounds and the training median as the initial value."""
    low, high = metadata["features"]["numeric"][name]
    default = int(metadata["reference_values"][name])
    if name not in st.session_state:
        st.session_state[name] = default
    return st.number_input(label, min_value=int(low), max_value=int(high), value=None, step=1, key=name,
                           help=HELP[name], on_change=refresh_result)


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
    changes["feature"] = changes.feature.str.replace("_", " ")
    if changes.change.abs().max() < 0.0005:
        st.info("Every displayed change is below 0.0005 in probability.")
        return
    chart = alt.Chart(changes).mark_bar(color="#1D2B64").encode(
        x=alt.X("change:Q", title="Change in predicted probability"),
        y=alt.Y("feature:N", sort="-x", title="Input replaced"),
        tooltip=[alt.Tooltip("feature:N", title="Input"), alt.Tooltip("change:Q", format="+.4f", title="Change"),
                 alt.Tooltip("new_probability:Q", format=".4f", title="New probability")])
    st.altair_chart(chart, width="stretch")
    st.caption("Each comparison changes one field at a time; some combinations may be uncommon. These are model associations.")


def ruler(probability, metadata):
    """Show an accessible validation-percentile position on the three bands."""
    quantiles = json.loads((ROOT / "models" / "score_quantiles.json").read_text(encoding="utf-8"))["quantiles"]
    percentile = score_percentile(probability, quantiles)
    band = risk_label(probability, metadata)
    summary = f"{band} band; higher than about {round(percentile)} percent of youth in the survey sample"
    st.markdown(f'<div class="ruler-wrap" role="img" aria-label="{summary}"><div class="ruler">'
                '<div class="ruler-band ruler-lower">Lower than most</div>'
                '<div class="ruler-band ruler-elevated">Elevated</div>'
                '<div class="ruler-band ruler-high">High</div>'
                f'<span class="ruler-marker" style="left: {min(percentile, 99.5):.2f}%"></span>'
                '</div></div>', unsafe_allow_html=True)
    st.write(f"Higher than about **{round(percentile)}%** of youth in the survey sample")
    st.caption("Position is relative to validation scores for youth in the labour force.")


def explore_input(model, values, metadata, census, flags):
    """Evaluate valid alternatives through the same input builder and predictor."""
    options = ["age", "sex", "area", "province", "education_level", "currently_enrolled", "has_training",
               "household_size", "children_under_15", "other_youth_15_24", "marital_status", "relationship_to_head",
               "can_read", "can_write", "head_sex", "head_education"]
    field = st.selectbox("Input to explore", options, format_func=lambda x: x.replace("_", " ").title(),
                         help="Change one input at a time while keeping the other answers fixed.", key="explore_input")
    if field in metadata["features"]["categorical"]:
        choices = metadata["features"]["categorical"][field]
    else:
        lo, hi = metadata["features"]["numeric"][field]
        choices = range(int(lo), int(hi) + 1)
    rows = []
    for value in choices:
        candidate = {**values, field: value}
        if validate_inputs(candidate, metadata):
            continue
        row = build_input(candidate, metadata, census)
        rows.append({"value": LABELS.get(field, {}).get(int(value), str(int(value))),
                     "probability": predict_probability(model, row), "current": value == values[field],
                     "rare": is_rare_combination(candidate, flags)})
    if not rows:
        st.info("No alternative values fit the current answers.")
        return
    frame = pd.DataFrame(rows)
    st.caption("Only combinations that pass the input checks are shown.")
    chart = alt.Chart(frame).mark_point(size=95, filled=True).encode(
        x=alt.X("value:N", sort=None, title=field.replace("_", " ").title()),
        y=alt.Y("probability:Q", title="Predicted probability", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("current:N", scale=alt.Scale(domain=[True, False], range=["#7A1F5C", "#1D2B64"]),
                        legend=alt.Legend(title="Current value")),
        shape=alt.Shape("current:N", title="Current value"),
        tooltip=["value:N", alt.Tooltip("probability:Q", format=".4f"), alt.Tooltip("rare:N", title="Rare combination")])
    st.altair_chart(chart, width="stretch")
    if frame.rare.any():
        st.caption("Some alternatives are rare in the survey data, so their estimates are less reliable.")


@st.fragment(key="live_result")
def result_panel(model, metadata):
    """Display live results without rerunning the other tabs."""
    names = [name for name in HELP if name not in {"head_sex", "head_education"}]
    values = {name: st.session_state[name] for name in names}
    if values["relationship_to_head"] == 1:
        values["head_sex"], values["head_education"] = values["sex"], values["education_level"]
    else:
        values["head_sex"], values["head_education"] = st.session_state["head_sex"], st.session_state["head_education"]
    st.subheader("Your estimate")
    for error in validate_inputs(values, metadata):
        st.error(error)
    if validate_inputs(values, metadata):
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
        st.caption(f"About {round(probability * 100)} in 100 similar modelled profiles; "
                   f"{probability / metadata['prevalence_train']:.1f}× the training-sample rate. "
                   "These are model estimates, not guaranteed outcomes.")
        ruler(probability, metadata)
        st.write("**Flagged for follow-up** at the validation-selected threshold." if probability >= metadata["threshold_f1"]
                 else "Not flagged for follow-up at the validation-selected threshold.")
        st.info(NOTE)
        st.caption("Do not use this estimate for hiring, eligibility, benefits, admissions or decisions about a person.")
        st.subheader("What changes this estimate")
        what_if_chart(model, row, metadata)
        st.subheader("Explore one input")
        explore_input(model, values, metadata, census, flags)
        with st.expander("How the model uses information"):
            importance_chart()
    except Exception:
        st.error("The estimate is temporarily unavailable. Please check the inputs and try again.")


def estimator(model, metadata):
    """Collect approved fields in four groups and show the live result beside them."""
    st.markdown('<div class="page-eyebrow">INTERACTIVE TOOL</div>', unsafe_allow_html=True)
    st.title("Profile explorer")
    st.caption("Explore the frozen model for youth aged 15–24 in the labour force. Inputs are not stored.")
    st.write("Try an example")
    for column, (name, changes) in zip(st.columns(3), EXAMPLES.items()):
        column.button(name, on_click=apply_example, args=(metadata, changes), width="stretch", help="Fill the form with this synthetic example.")
    inputs, result = st.columns([1, 1], gap="large")
    with inputs:
        st.subheader("Build a profile")
        st.subheader("About the person")
        age_min, age_max = metadata["features"]["numeric"]["age"]
        if "age" not in st.session_state:
            st.session_state["age"] = int(metadata["reference_values"]["age"])
        st.slider("Age (years)", int(age_min), int(age_max), value=None,
                  key="age", help=HELP["age"], on_change=refresh_result)
        category("sex", metadata, "Sex")
        category("marital_status", metadata, "Marital status")
        relationship = category("relationship_to_head", metadata, "Relationship to household head")
        st.subheader("Education and training")
        for name, label in [("education_level", "Education level"), ("can_read", "Can read"), ("can_write", "Can write"),
                            ("currently_enrolled", "Current enrolment"), ("has_training", "Ever received or currently receiving training")]:
            category(name, metadata, label)
        st.subheader("Location")
        category("province", metadata, "Province"); category("area", metadata, "Area")
        st.subheader("Household")
        for name, label in [("household_size", "Household size, including this person"),
                            ("children_under_15", "Children under 15 in the household"),
                            ("other_youth_15_24", "Other youth aged 15–24 in the household")]:
            number(name, metadata, label)
        if relationship == 1:
            st.caption("As the household head, this person's sex and education are used for the head fields.")
        else:
            category("head_sex", metadata, "Household head's sex")
            category("head_education", metadata, "Household head's education")
    with result:
        result_panel(model, metadata)


def overview():
    """Present published survey rates separately from model-sample estimates."""
    survey = pd.read_csv(TABLES / "label_reproduction.csv").set_index("group")
    st.markdown('<div class="page-eyebrow">PAKISTAN LABOUR MARKET · 2024–25</div>', unsafe_allow_html=True)
    st.title("Youth employment at a glance")
    st.caption("A clearer view of the opportunities and barriers shaping young people's transition into work.")
    st.markdown('<div class="dashboard-hero"><strong>Understand the youth employment landscape</strong><br>'
                'Explore official survey indicators alongside an experimental profile estimator. '
                'Use the insights to ask better questions, not to make decisions about individuals.</div>', unsafe_allow_html=True)
    groups = [("Youth unemployment", "youth_all"), ("National unemployment", "all_ages"),
              ("Youth · male", "youth_male"), ("Youth · female", "youth_female")]
    for column, (label, group) in zip(st.columns(4), groups):
        with column.container(border=True):
            st.metric(label, f"{survey.loc[group, 'pbs_unemployment_rate']:.1%}")
            st.caption("PBS · ages 15–24" if group != "all_ages" else "PBS · ages 10+")
    st.caption("Official weighted rates, rounded as reported by PBS. Model evaluation uses unweighted records.")
    st.markdown("[PBS Labour Force Survey annual report](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf) · "
                "[Age and sex table](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-15.pdf)")
    left, right = st.columns([1.45, 1])
    with left.container(border=True):
        st.subheader("Youth unemployment by sex and area")
        selected = [("Male", "youth_male"), ("Female", "youth_female"),
                    ("Rural", "youth_rural"), ("Urban", "youth_urban")]
        rates = pd.DataFrame([{"Group": name, "Rate": survey.loc[key, "pbs_unemployment_rate"]}
                              for name, key in selected])
        chart = alt.Chart(rates).mark_bar(color="#087e8b", cornerRadiusEnd=4).encode(
            x=alt.X("Rate:Q", title="Unemployment rate", axis=alt.Axis(format="%")),
            y=alt.Y("Group:N", sort=None, title=None),
            tooltip=["Group:N", alt.Tooltip("Rate:Q", format=".1%")])
        st.altair_chart(chart, width="stretch")
        st.caption("Sex and area are separate comparisons, not mutually exclusive groups.")
    with right.container(border=True):
        st.subheader("How to read this dashboard")
        st.markdown("**01 · Start with the population**  \nCheck the age group, year and denominator.\n\n"
                    "**02 · Compare like with like**  \nUnemployment is a share of the labour force, not all youth.\n\n"
                    "**03 · Separate data from estimates**  \nSurvey statistics and model predictions are different evidence.")
        st.info("Students and other youth outside the labour force are not represented by the model.")
    st.download_button("Download survey indicators", rates.to_csv(index=False),
                       file_name="hunarlens_survey_indicators.csv", mime="text/csv")
    st.button("Explore a profile →", on_click=lambda: st.session_state.update(navigation="Profile explorer"), type="primary")


def insights():
    """Display saved comparisons and the single final test evaluation."""
    st.markdown('<div class="page-eyebrow">EVALUATION & RELIABILITY</div>', unsafe_allow_html=True)
    st.title("Model performance")
    st.caption("Understand what the experimental model can—and cannot—identify in its held-out evaluation sample.")
    metrics = pd.read_csv(TABLES / "test_metrics.csv").set_index("model_threshold")
    final = metrics.loc["HGB F1"]
    dummy = metrics.loc["Stratified Dummy"]
    for column, (label, value, caption) in zip(st.columns(4), [
        ("Test sample", f"{int(final['n']):,}", "Unseen youth records"),
        ("Unemployed in test", f"{final['prevalence']:.1%}", f"{int(final['positives'])} records"),
        ("Flagged for follow-up", f"{(final['tp'] + final['fp']) / final['n']:.1%}", "At the primary threshold"),
        ("ROC-AUC", f"{final['roc_auc']:.3f}", "Ranking metric")]):
        with column.container(border=True):
            st.metric(label, value)
            st.caption(caption)
    with st.container(border=True):
        st.subheader("What happens at the follow-up threshold?")
        st.write(f"Of unemployed youth, **{final['recall']:.1%}** were flagged; "
                 f"**{1 - final['recall']:.1%}** were missed. Of those flagged, **{final['precision']:.1%}** were unemployed.")
        st.caption(f"F1: {final['f1']:.3f} · Dummy F1: {dummy['f1']:.3f} · "
                   f"PR-AUC: {final['pr_auc']:.3f} · No-skill prevalence: {final['prevalence']:.3f}")
    with st.container(border=True):
        st.subheader("Input groups associated with predictions")
        importance_chart()
    st.subheader("Model experiments")
    experiment = pd.read_csv(TABLES / "experiments.csv")
    chosen = experiment.loc[experiment.exp_id.eq("E4"), ["model", "cv_ap_mean", "val_f1_best", "threshold"]]
    comparison = alt.Chart(chosen).mark_bar(color="#1D2B64").encode(
        x=alt.X("cv_ap_mean:Q", title="Grouped CV average precision"),
        y=alt.Y("model:N", sort="-x", title="Model"),
        tooltip=[alt.Tooltip("model:N", title="Model"), alt.Tooltip("cv_ap_mean:Q", format=".4f", title="CV PR-AUC"),
                 alt.Tooltip("val_f1_best:Q", format=".4f", title="Validation F1"),
                 alt.Tooltip("threshold:Q", format=".4f", title="Tuned threshold")])
    st.altair_chart(comparison, width="stretch")
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
    st.markdown('<div class="page-eyebrow">EVIDENCE & GOVERNANCE</div>', unsafe_allow_html=True)
    st.title("Data and methodology")
    st.markdown("""HunarLens describes patterns in Pakistan's **Labour Force Survey 2024–25** and **Population and Housing Census 2023**. Sources: [Pakistan Bureau of Statistics labour-force statistics](https://www.pbs.gov.pk/labour-force-statistics/) and [Census detailed results](https://pbs.gov.pk/result-excel/), accessed **15 November 2026**.

    The model uses youth aged **15–24 in the labour force**. Employed people worked for pay or profit, did qualifying family or sale-oriented farm work, or were temporarily absent under the survey rules. Unemployed people were not employed, were available within two weeks and either searched in the previous four weeks or had a job or business to start in the near future. The data do not record the start date, so the [ILO's generally three-month future-starter condition](https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf) could not be verified. See the [PBS annual report](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf) for the survey's definitions.

    Results are **unweighted** and describe survey associations, not causes. Census density and urban share are constant within province; Census household size is constant within province and area. Enrolment is a strong correlate partly reflecting selection into the labour-force-only sample. Performance and errors vary by subgroup, and small groups are uncertain.

    Inputs are not stored by this app. HunarLens is not affiliated with or endorsed by PBS. On the unweighted test set, the frozen model had F1 **0.360**, PR-AUC **0.303** and ROC-AUC **0.752**. Performance was weaker for some groups: recall for people with no formal education was **17.9%** at the primary threshold. Students outside the labour force are not included in the sample, so these results do not describe them.

    **Association from survey data, not a cause. Not a decision tool for individuals.**""")


def main():
    st.set_page_config(page_title="HunarLens", page_icon="🌱", layout="wide")
    try:
        st.markdown(f"<style>{(ROOT / 'app' / 'style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    except OSError:
        pass
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
    try:
        with st.sidebar:
            st.markdown('<div class="sidebar-brand"><span>H</span> HunarLens</div>'
                        '<div class="sidebar-sub">YOUTH INTELLIGENCE</div>', unsafe_allow_html=True)
            page = st.radio("Workspace", ["Overview", "Profile explorer", "Model performance", "Data & methodology"],
                            key="navigation")
            st.caption("PBS Labour Force Survey 2024–25 · Independent research project")
        if page == "Overview":
            overview()
        elif page == "Profile explorer":
            estimator(model, metadata)
        elif page == "Model performance":
            insights()
        else:
            about()
    except Exception:
        st.error("This page is temporarily unavailable. Please try again later.")


if __name__ == "__main__":
    main()
