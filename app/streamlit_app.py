# What: presents the frozen youth-unemployment model and its limitations.
# Why: make aggregate survey patterns understandable without saving user input.
# Viva: the form supplies raw fields to the same fitted pipeline used in evaluation.
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json
import logging
import textwrap
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
LOGGER = logging.getLogger(__name__)
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


@st.cache_data(show_spinner=False)
def load_reference_tables():
    """Reuse non-personal regional and rare-combination reference data."""
    return (pd.read_csv(ROOT / "data/processed/census_lookup.csv"),
            pd.read_csv(ROOT / "data/processed/rare_combinations.csv", dtype={"age_key": str, "rare": bool}))


def category(name, metadata, label):
    """Offer only training-observed categories, with the training mode selected."""
    choices = metadata["features"]["categorical"][name]
    default = metadata["reference_values"][name]
    if name not in st.session_state:
        st.session_state[name] = default if default in choices else choices[0]
    return st.selectbox(label, choices, index=None,
                        format_func=lambda value: LABELS[name].get(int(value), f"Code {value:g}"), key=name,
                        help=HELP[name])


def number(name, metadata, label):
    """Use observed training bounds and the training median as the initial value."""
    low, high = metadata["features"]["numeric"][name]
    default = int(metadata["reference_values"][name])
    if name not in st.session_state:
        st.session_state[name] = default
    return st.number_input(label, min_value=int(low), max_value=int(high), value=None, step=1, key=name,
                           help=HELP[name])


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
                '</div><div class="ruler-labels"><span>Lower than most</span><span>Elevated</span><span>High</span></div></div>', unsafe_allow_html=True)
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
    st.subheader("What the survey pattern suggests")
    st.caption("Estimated unemployment probability · youth in the labour force")
    for name in ("household_size", "children_under_15", "other_youth_15_24", "age"):
        if values[name] is None:
            st.error(f"Enter a number for {name.replace('_', ' ')}.")
            return
    for error in validate_inputs(values, metadata):
        st.error(error)
    if validate_inputs(values, metadata):
        return
    if values["age"] <= 17 and values["education_level"] >= 8:
        st.warning("A university degree at this age is unusual. Please check the education selection.")
    if values["relationship_to_head"] == 3 and values["marital_status"] != 1:
        st.warning("The relationship says son or daughter (unmarried), but the marital status is not never married. Please check the selections.")
    try:
        census, flags = load_reference_tables()
        row = build_input(values, metadata, census)
        if is_rare_combination(values, flags):
            st.warning("This combination is rare in the survey data, so the estimate is less reliable.")
        probability = predict_probability(model, row)
        left, right = st.columns(2)
        left.metric("Estimated unemployment probability", f"{probability:.1%}")
        right.metric("Training sample base rate", f"{metadata['prevalence_train']:.1%}")
        st.write(f"**Relative band:** {risk_label(probability, metadata)}")
        count = round(probability * 100)
        squares = ''.join('<i class="on"></i>' if i < count else '<i></i>' for i in range(100))
        st.markdown(f'<div class="dot-grid" role="img" aria-label="{count} of 100 squares highlighted">{squares}</div>',
                    unsafe_allow_html=True)
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
    except Exception as error:
        LOGGER.error("Estimate unavailable (%s)", type(error).__name__)
        st.error("The estimate is temporarily unavailable. Please check the inputs and try again.")


def estimator(model, metadata):
    """Collect approved fields in four groups and show the live result beside them."""
    st.markdown('<div class="page-eyebrow">INTERACTIVE TOOL</div>', unsafe_allow_html=True)
    st.title("Profile explorer")
    st.caption("Explore the frozen model for youth aged 15–24 in the labour force. Inputs are not stored.")
    inputs, result = st.columns([.85, 1.35], gap="medium")
    with inputs.container(border=True):
        st.subheader("Build a profile")
        st.caption("Select characteristics to update the estimate.")
        sex_col, area_col = st.columns(2)
        with sex_col:
            category("sex", metadata, "Sex")
        with area_col:
            category("area", metadata, "Area")
        age_min, age_max = metadata["features"]["numeric"]["age"]
        if "age" not in st.session_state:
            st.session_state["age"] = int(metadata["reference_values"]["age"])
        st.slider("Age (years)", int(age_min), int(age_max), value=None,
                  key="age", help=HELP["age"])
        edu_col, enrol_col = st.columns(2)
        with edu_col:
            category("education_level", metadata, "Education level")
        with enrol_col:
            category("currently_enrolled", metadata, "Current enrolment")
        st.caption("Additional details used by the model")
        person_col, location_col = st.columns(2)
        with person_col:
            category("marital_status", metadata, "Marital status")
            relationship = category("relationship_to_head", metadata, "Relationship to household head")
            category("can_read", metadata, "Can read")
            category("can_write", metadata, "Can write")
        with location_col:
            category("province", metadata, "Province")
            category("has_training", metadata, "Ever received or currently receiving training")
        st.caption("Household")
        for name, label in [("household_size", "Household size, including this person"),
                            ("children_under_15", "Children under 15 in the household"),
                            ("other_youth_15_24", "Other youth aged 15–24 in the household")]:
            number(name, metadata, label)
        if relationship == 1:
            st.caption("As the household head, this person's sex and education are used for the head fields.")
        else:
            category("head_sex", metadata, "Household head's sex")
            category("head_education", metadata, "Household head's education")
        st.write("Try an example")
        for column, (name, changes) in zip(st.columns(3), EXAMPLES.items()):
            column.button(name, on_click=apply_example, args=(metadata, changes), width="stretch", help="Fill the form with this synthetic example.")
        st.caption("Inputs are not stored. Census information is filled automatically.")
    with result.container(border=True):
        result_panel(model, metadata)


def overview():
    """Present published survey rates separately from model-sample estimates."""
    survey = pd.read_csv(TABLES / "overview_indicators.csv").query('status == "verified"').set_index("indicator")
    heading, actions = st.columns([3, 1])
    with heading:
        st.markdown('<div class="page-eyebrow">PAKISTAN LABOUR MARKET · 2024–25</div>', unsafe_allow_html=True)
        st.title("Youth employment at a glance")
        st.caption("A clearer view of the opportunities and barriers shaping young people's transition into work.")
    with actions:
        st.button("Explore a profile →", on_click=lambda: st.session_state.update(navigation="Profile explorer"), type="primary")
    st.markdown('<div class="dashboard-hero"><div><strong>Understand the youth employment landscape</strong><br>'
                'Explore official survey indicators alongside an experimental profile estimator. '
                'Use the insights to ask better questions, not to make decisions about individuals.</div>'
                '<div class="hero-age"><b>15–24</b><br>Survey youth age group</div></div>', unsafe_allow_html=True)
    groups = [("Youth unemployment", "youth_all"), ("National unemployment", "all_ages"),
              ("Youth · male", "youth_male"), ("Youth · female", "youth_female")]
    for column, (label, group) in zip(st.columns(4), groups):
        with column.container(border=True):
            if group in survey.index:
                st.metric(label, f"{survey.loc[group, 'pbs_value']:.1%}")
            st.caption("PBS · ages 15–24" if group != "all_ages" else "PBS · ages 10+")
    st.caption("Official weighted rates, rounded as reported by PBS. Model evaluation uses unweighted records.")
    st.markdown("[PBS Labour Force Survey annual report](https://www.pbs.gov.pk/labour-force-statistics/) · "
                "[Age and sex table](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-15.pdf)")
    left, right = st.columns([1.45, 1])
    with left.container(border=True):
        st.subheader("Youth unemployment by sex and area")
        selected = [("Male", "youth_male"), ("Female", "youth_female"),
                    ("Rural", "youth_rural"), ("Urban", "youth_urban")]
        rates = pd.DataFrame([{"Group": name, "Rate": survey.loc[key, "pbs_value"]}
                              for name, key in selected if key in survey.index])
        chart = alt.Chart(rates).mark_bar(color="#087e8b", cornerRadiusEnd=4).encode(
            x=alt.X("Rate:Q", title="Unemployment rate", axis=alt.Axis(format="%")),
            y=alt.Y("Group:N", sort=None, title=None),
            tooltip=["Group:N", alt.Tooltip("Rate:Q", format=".1%")])
        st.altair_chart(chart, width="stretch")
        st.caption("Sex and area are separate comparisons, not mutually exclusive groups.")
    left, right = st.columns([1.45, 1])
    with left.container(border=True):
        st.subheader("Youth group comparison")
        st.caption("Official weighted rates for selected groups")
        st.dataframe(rates.rename(columns={"Rate": "Unemployment rate"}), hide_index=True,
                     column_config={"Unemployment rate": st.column_config.NumberColumn(format="percent")})
    with right.container(border=True):
        st.subheader("How to read this dashboard")
        st.markdown("**01 · Start with the population**  \nCheck the age group, year and denominator.\n\n"
                    "**02 · Compare like with like**  \nUnemployment is a share of the labour force, not all youth.\n\n"
                    "**03 · Separate data from estimates**  \nSurvey statistics and model predictions are different evidence.")
        st.info("Students and other youth outside the labour force are not represented by the model.")
    st.download_button("Download survey indicators", rates.to_csv(index=False),
                       file_name="hunarlens_survey_indicators.csv", mime="text/csv")


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
    outcome_col, metric_col = st.columns([1.45, 1])
    with outcome_col.container(border=True):
        st.subheader("What happens at the follow-up threshold?")
        st.caption("Observed outcomes in the held-out test sample")
        for label, value in [("Flagged youth", (final['tp'] + final['fp']) / final['n']),
                             ("Unemployed among flagged", final['precision']),
                             ("Unemployed detected", final['recall'])]:
            st.write(f"{label}: **{value:.1%}**")
            st.progress(float(value))
        st.write(f"Of unemployed youth, **{final['recall']:.1%}** were flagged; "
                 f"**{1 - final['recall']:.1%}** were missed. Of those flagged, **{final['precision']:.1%}** were unemployed.")
    with metric_col.container(border=True):
        st.subheader("Core evaluation metrics")
        st.caption("Reported on the held-out test sample")
        for label, value in [("F1 score", final['f1']), ("PR-AUC", final['pr_auc']), ("ROC-AUC", final['roc_auc'])]:
            st.write(f"{label}: **{value:.3f}**")
            st.progress(float(value))
        st.caption(f"F1: {final['f1']:.3f} · Dummy F1: {dummy['f1']:.3f} · "
                   f"PR-AUC: {final['pr_auc']:.3f} · No-skill prevalence: {final['prevalence']:.3f}")
    importance_col, subgroup_col = st.columns([1.45, 1])
    with importance_col.container(border=True):
        st.subheader("Input groups associated with predictions")
        importance_chart()
    with subgroup_col.container(border=True):
        st.subheader("Performance differs by education")
        groups = pd.read_csv(TABLES / "test_subgroups.csv")
        education = groups[(groups.subgroup == "education group") & (groups.threshold == "f1")]
        if education.empty:
            education = groups[(groups.subgroup.str.contains("education", case=False)) & (groups.threshold == "f1")]
        st.dataframe(education[["value", "n", "positives", "recall"]], hide_index=True)
        st.caption("Recall is detection among unemployed youth. Groups with fewer than 50 positives are unreliable.")
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
    test_metrics = pd.read_csv(TABLES / "test_metrics.csv")
    display_columns = ["model_threshold", "f1", "precision", "recall", "pr_auc", "roc_auc", "lift_10", "prevalence"]
    st.dataframe(test_metrics[display_columns].rename(columns={"model_threshold": "Model and threshold", "f1": "F1", "precision": "Precision", "recall": "Recall", "pr_auc": "PR-AUC", "roc_auc": "ROC-AUC", "lift_10": "Top 10% lift", "prevalence": "Prevalence"}), hide_index=True)
    st.write("95% household-grouped bootstrap intervals")
    st.dataframe(pd.read_csv(TABLES / "test_bootstrap_ci.csv"), hide_index=True)
    st.image(str(FIGURES / "test_pr_curve_wide.png"), caption="Test precision–recall curve; dashed line is prevalence.")
    st.subheader("Subgroup caveats")
    groups = pd.read_csv(TABLES / "test_subgroups.csv")
    st.dataframe(groups, hide_index=True)
    with st.expander("Show full tables"):
        st.dataframe(test_metrics, hide_index=True)
        st.dataframe(experiment, hide_index=True)
    st.warning("Subgroups with fewer than 50 unemployed people are flagged as unreliable; larger groups may still have substantial uncertainty. Performance differs across education, sex and area.")
    st.caption(NOTE)


def about():
    """Explain data sources, the label and limitations using saved results."""
    st.title("Data and methodology")
    st.subheader("Official data sources")
    st.markdown(textwrap.dedent("""
        - [PBS Labour Force Statistics](https://www.pbs.gov.pk/labour-force-statistics/)
        - [PBS Census 2023](https://www.pbs.gov.pk/result-excel/)
        - [LFS Annual Report](https://www.pbs.gov.pk/labour-force-statistics/)
        - [LFS Table 15](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-15.pdf)
        Sources accessed 15 November 2026.
    """))
    st.subheader("Definitions and limitations")
    st.markdown("""Skills-gap sources: [ILOSTAT mismatch methods](https://ilostat.ilo.org/blog/only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education/), [ETF measurement guidance](https://www.etf.europa.eu/en/publications-and-resources/publications/skills-mismatch-measurement-etf-partner-countries), [NAVTTC / NSIS employer skill survey, 2024](https://www.skillingpakistan.gov.pk/), and [PBS Annual Report, Table 9.7](https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf).""")
    st.markdown(textwrap.dedent("""
        The model covers youth aged 15?24 in the labour force. Unemployed people were not
        employed, were available within two weeks and either searched in the previous four
        weeks or had a job or business to start. The file does not record the start date,
        so the three-month future-starter condition cannot be verified.

        Results use unweighted records and describe associations, not causal effects. Census features
        are constant within province or province and area. Enrolment associations partly
        reflect selection into the labour-force sample. Students outside the labour force
        are not included. Inputs are not stored. HunarLens is not affiliated with or endorsed by PBS.
        It is not a decision tool for individuals.
    """))
    metrics = pd.read_csv(TABLES / "test_metrics.csv").set_index("model_threshold").loc["HGB F1"]
    groups = pd.read_csv(TABLES / "test_subgroups.csv")
    no_formal = groups[(groups.subgroup.str.contains("education", case=False)) &
                       (groups.value == "No formal education") & (groups.threshold == "f1")]
    st.write(f"On the unweighted test set, F1 was **{metrics.f1:.3f}**, PR-AUC **{metrics.pr_auc:.3f}** and ROC-AUC **{metrics.roc_auc:.3f}**.")
    if not no_formal.empty:
        st.write(f"Recall for people with no formal education was **{no_formal.iloc[0].recall:.1%}**.")


def skills_gap():
    """Show the cached survey aggregates in the accessible classic view."""
    from dashboard_component import static_data
    data = static_data()
    st.title("Skills gap")
    st.write("Skills gap, as measurable from the LFS: the difference in education and vocational-training attainment between unemployed and employed youth, the education mismatch of employed youth relative to the occupations they hold, and what happens to youth at each education level in the labour market. Education and training are proxies for skills. Vacancies and employer demand are not measured in the LFS; employer surveys (NAVTTC/NSIS) are cited as context only.")
    st.caption("Our analysis · weighted estimates and unweighted sample counts")
    unemployment = data["skills_unemployment_by_education"]
    overall = unemployment.loc[unemployment.group.eq("overall")].set_index("category")
    for band in ["No formal", "Degree or above"]:
        row = overall.loc[band]
        st.metric(f"Unemployment · {band}", f"{row['estimate']:.1%}", help=f"Labour-force n={row['n']}")
    training = data["skills_attainment_gap"]
    st.subheader("Training · unemployed and employed")
    st.dataframe(training.loc[training.group.isin(["overall; employed", "overall; unemployed"]) & training.category.eq("Training ever/current")], hide_index=True)
    st.dataframe(data["skills_attainment_difference"].query("group == 'overall' and category == 'Training ever/current'"), hide_index=True)
    comparisons = pd.concat([data["skills_mismatch"], data["skills_mismatch_sensitivity"]])
    norm_names = ["overall; norm=all_15_plus", "overall; norm=age_25_44", "overall; norm=youth"]
    strict = comparisons.loc[comparisons.group.isin(norm_names) & comparisons.category.eq("over")]
    st.metric("Strict above-typical range across statistical norms", f"{strict.estimate.min():.1%}–{strict.estimate.max():.1%}", help=f"Employed youth n={strict.iloc[0]['n']}")
    neet = data["skills_neet"].query("group == 'overall'").iloc[0]
    official = data["skills_neet_external"].iloc[0]
    st.metric("Approximate NEET / PBS NEET", f"{neet['estimate']:.1%} / {official['estimate']:.1%}", help=f"Our survey n={neet['n']}; definitions differ")
    st.subheader("What happens at each education level")
    st.dataframe(data["skills_outcomes_by_education"], hide_index=True)
    groups = {"All youth": "overall", "Male": "sex=1.0", "Female": "sex=2.0", "Rural": "area=1.0", "Urban": "area=2.0"}
    group = groups[st.selectbox("Survey subgroup", list(groups), key="skills_classic_group")]
    st.subheader("Unemployment by education")
    st.dataframe(unemployment.loc[unemployment.group.eq(group)], hide_index=True)
    st.subheader("Where do graduates work?")
    graduates = data["skills_graduate_absorption"]
    st.dataframe(graduates.loc[graduates.group.eq(group)], hide_index=True)
    st.subheader("Education and training attainment gap")
    gaps = data["skills_attainment_difference"]
    gap_group = st.selectbox("Attainment subgroup", list(gaps.group.unique()), key="skills_classic_attainment")
    st.dataframe(gaps.loc[gaps.group.eq(gap_group)], hide_index=True)
    st.subheader("Education mismatch depends on the definition")
    definitions = {"Strict: all employed": ("all_15_plus", "over"), "Strict: youth only": ("youth", "over"),
                   "Within one band: all employed": ("all_15_plus", "within one band"),
                   "Two or more bands above: all employed": ("all_15_plus", "two or more bands above"),
                   "Normative ISCO": ("ISCO", "over")}
    norm, category = definitions[st.selectbox("Mismatch definition", list(definitions), key="skills_classic_definition")]
    if category == "over":
        overall_mismatch = pd.concat([data["skills_mismatch"], data["skills_mismatch_sensitivity"]])
        selected = overall_mismatch.loc[overall_mismatch.group.eq(f"overall; norm={norm}") & overall_mismatch.category.eq(category)]
        occupation = data["skills_mismatch_by_occupation"].query("group == @norm")
    else:
        selected = data["skills_mismatch_variants"].query("group == @norm and category == @category")
        occupation = data["skills_mismatch_occupation_variants"].query("group == @category")
    st.dataframe(selected, hide_index=True)
    st.caption("Mode unstable rows show their full bootstrap range in the lower and upper columns.")
    st.dataframe(occupation, hide_index=True)
    st.write("Above the typical level compares education bands with an occupation's mode; it does not assess the usefulness of a degree.")
    st.subheader("Education to occupation")
    st.dataframe(data["skills_education_occupation_matrix"], hide_index=True)
    st.subheader("Not employed and not enrolled")
    st.dataframe(data["skills_neet"].loc[lambda x: x.group.isin(groups.values())], hide_index=True)
    st.dataframe(data["skills_neet_external"], hide_index=True)
    st.write("Approximate NEET differs from the PBS measure: recent training cannot be identified.")
    st.subheader("How to read this page")
    st.write("Education and training are proxies for skills, not measures of individual ability. No vacancy or employer-demand data are measured. These are associations only; labour-force sample selection affects comparisons. Survey analyses use weights and cluster bootstrap intervals; the model does not. The age 25–44 reference has the same occupation modes as the all-employed reference and is not an independent sensitivity.")


def main():
    st.set_page_config(page_title="HunarLens", page_icon="🌱", layout="wide")
    try:
        st.markdown(f"<style>{(ROOT / 'app' / 'style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    except OSError as error:
        LOGGER.error("Styles unavailable (%s)", type(error).__name__)
    try:
        metadata = load_metadata()
    except Exception as error:
        LOGGER.error("Model details unavailable (%s)", type(error).__name__)
        st.error("The model details are temporarily unavailable. Please try again later.")
        return
    if sklearn.__version__ != metadata.get("sklearn_version"):
        st.warning("The installed scikit-learn version differs from the model's saved version; predictions may be unreliable.")
    try:
        model = load_model()
    except Exception as error:
        LOGGER.error("Model unavailable (%s)", type(error).__name__)
        st.error("The model is temporarily unavailable. Please try again later.")
        return
    # Add ?classic=1 to the URL to use the native Streamlit interface.
    if st.query_params.get("classic") != "1":
        try:
            if not hasattr(st.components, "v2"):
                raise RuntimeError("Streamlit custom components are unavailable")
            from dashboard_component import show_dashboard
            show_dashboard(metadata, model)
            st.markdown('<style>[data-testid="stMainBlockContainer"] {padding:0!important;max-width:none!important;width:100%!important;} '
                        'header[data-testid="stHeader"] {visibility:hidden;}</style>', unsafe_allow_html=True)
            return
        except Exception as error:
            LOGGER.error("Dashboard component unavailable (%s)", type(error).__name__)
            st.warning("The interactive dashboard is unavailable; showing the classic view.")
    try:
        with st.sidebar:
            st.markdown('<div class="sidebar-brand"><span>H</span> HunarLens</div>'
                        '<div class="sidebar-sub">YOUTH INTELLIGENCE</div>', unsafe_allow_html=True)
            page = st.radio("Workspace", ["Overview", "Skills gap", "Profile explorer", "Model performance", "Data & methodology"],
                            key="navigation")
            st.caption("PBS Labour Force Survey 2024–25 · Independent research project")
        st.markdown(f'<div class="dashboard-topbar"><span>Workspace&nbsp; / &nbsp;<strong>{page}</strong></span>'
                    '<span class="location-pill">Pakistan · National view</span></div>', unsafe_allow_html=True)
        if page == "Overview":
            overview()
        elif page == "Skills gap":
            skills_gap()
        elif page == "Profile explorer":
            estimator(model, metadata)
        elif page == "Model performance":
            insights()
        else:
            about()
    except Exception as error:
        LOGGER.error("Page unavailable (%s)", type(error).__name__)
        st.error("This page is temporarily unavailable. Please try again later.")


if __name__ == "__main__":
    main()
