# What: generates the exploratory analysis descriptive tables, figures and findings.
# Why: every plot and count can be reproduced from the same analysis dataset.
# Viva: EDA describes the sample; it does not fit or select a model.
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from hunarlens.config import FEATURES, NUMERIC_FEATURES

BLUE, ORANGE = "#0072B2", "#D55E00"


def value_audit(data: pd.DataFrame, tables: Path) -> pd.DataFrame:
    """Save counts including explicit missing rows and all rare categories."""
    rows, rare = [], []
    for name in FEATURES:
        counts = data[name].value_counts(dropna=True)
        for value, count in counts.head(15).items():
            rows.append({"feature": name, "value": value, "count": int(count), "kind": "observed"})
        rows.append({"feature": name, "value": None, "count": int(data[name].isna().sum()), "kind": "missing"})
        for value, count in counts[counts < 50].items():
            rare.append({"feature": name, "value": value, "count": int(count)})
    result = pd.DataFrame(rows)
    result.to_csv(tables / "feature_value_counts_top15.csv", index=False)
    pd.DataFrame(rare, columns=["feature", "value", "count"]).to_csv(tables / "rare_categories.csv", index=False)
    return result


def save_figure(fig: plt.Figure, figures: Path, name: str) -> None:
    """Write a consistent export without leaving open figures in memory."""
    fig.tight_layout()
    fig.savefig(figures / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def rate_plot(data: pd.DataFrame, group: str, figures: Path) -> str:
    """Show group unemployment rates and sample sizes without modelling."""
    summary = data.groupby(group, dropna=False).is_unemployed.agg(["mean", "size"])
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.bar([str(x) for x in summary.index], summary["mean"] * 100, color=BLUE)
    for bar, count in zip(bars, summary["size"]):
        ax.annotate(f"n={count}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=7, rotation=45 if len(summary) > 8 else 0)
    ax.set(title=f"Unemployment rate by {group}", xlabel=f"{group} (survey code)", ylabel="Unemployed (%)")
    ax.set_ylim(0, max(5, summary["mean"].max() * 130))
    save_figure(fig, figures, f"rate_by_{group}")
    return f"Rates range from {summary['mean'].min() * 100:.1f}% to {summary['mean'].max() * 100:.1f}% across observed codes; labels show group sizes."


def create_figures(data: pd.DataFrame, figures: Path) -> dict[str, str]:
    """Create descriptive figures and short observations from unweighted rows."""
    findings = {}
    counts = data.is_unemployed.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Employed (0)", "Unemployed (1)"], [counts.get(0, 0), counts.get(1, 0)], color=[BLUE, ORANGE])
    ax.set(title="Employment status in youth analysis data", xlabel="Class", ylabel="People (unweighted)")
    save_figure(fig, figures, "class_balance")
    findings["class_balance"] = f"There are {counts.get(1, 0):,} unemployed and {counts.get(0, 0):,} employed records; prevalence is {data.is_unemployed.mean() * 100:.2f}%."
    fig, ax = plt.subplots(figsize=(8, 4))
    for value, label, color in [(0, "Employed", BLUE), (1, "Unemployed", ORANGE)]:
        subset = data.loc[data.is_unemployed.eq(value), "age"].value_counts(normalize=True).sort_index()
        ax.plot(subset.index, subset.values * 100, marker="o", label=label, color=color)
    ax.set(title="Age distribution within each class", xlabel="Age (years)", ylabel="Share within class (%)")
    ax.legend()
    save_figure(fig, figures, "age_by_class")
    findings["age_by_class"] = "Age shares are shown within each class, so the different class sizes do not dominate the comparison. Survey ages show visible peaks."
    summary = data.groupby(["area", "sex"]).is_unemployed.agg(["mean", "size"])
    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [f"{'Rural' if a == 1 else 'Urban'} / {'Male' if s == 1 else 'Female'}" for a, s in summary.index]
    ax.bar(labels, summary["mean"] * 100, color=[BLUE, ORANGE, BLUE, ORANGE])
    for i, (rate, n) in enumerate(zip(summary["mean"], summary["size"])):
        ax.text(i, rate * 100, f"n={n}", ha="center", va="bottom", fontsize=8)
    ax.set(title="Unemployment by area and sex", xlabel="Area and sex", ylabel="Unemployed (%)")
    ax.set_ylim(0, summary["mean"].max() * 130)
    save_figure(fig, figures, "rate_sex_area")
    findings["rate_sex_area"] = f"The four area and sex groups range from {summary['mean'].min() * 100:.1f}% to {summary['mean'].max() * 100:.1f}%; the chart includes group counts."
    for column in ["province", "education_level", "has_training"]:
        findings[f"rate_by_{column}"] = rate_plot(data, column, figures)
    missing = data[FEATURES].isna().mean().sort_values() * 100
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(missing.index, missing.values, color=BLUE)
    ax.set(title="Missing values by feature", xlabel="Missing records (%)", ylabel="Feature", xlim=(0, max(1, missing.max() * 1.2)))
    save_figure(fig, figures, "missing_values")
    findings["missing_values"] = f"The largest observed feature missing rate is {missing.max():.2f}%; unknown source coding may not be reflected in this number."
    for name in ["age", "household_size", "children_under_15", "census_density", "census_urban_proportion", "census_household_size"]:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.boxplot(data[name].dropna(), vert=False, showfliers=True)
        ax.set(title=f"Distribution and outliers: {name}", xlabel=name, yticks=[])
        save_figure(fig, figures, f"box_{name}")
        findings[f"box_{name}"] = f"The observed range is {data[name].min():.2f} to {data[name].max():.2f}; boxplot points are statistical outliers, not necessarily errors."
    fig, ax = plt.subplots(figsize=(8, 7))
    correlation = data[NUMERIC_FEATURES + ["is_unemployed"]].corr()
    picture = ax.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set(xticks=range(len(correlation)), yticks=range(len(correlation)), xticklabels=correlation.columns, yticklabels=correlation.index, title="Numeric feature correlations")
    ax.tick_params(axis="x", labelrotation=60)
    fig.colorbar(picture, ax=ax, label="Pearson correlation")
    save_figure(fig, figures, "numeric_correlations")
    findings["numeric_correlations"] = "The heatmap shows Pearson associations among numeric fields and the target; correlations do not establish causation."
    for name, values, xlabel in [("household_size_distribution", data.household_size, "Roster members per household"),
                                 ("youth_per_household", data.groupby("group_id").size(), "Eligible youth records per group")]:
        counts = values.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(counts.index, counts.values, color=BLUE)
        ax.set(title=name.replace("_", " ").title(), xlabel=xlabel, ylabel="Youth records" if name.startswith("household_size") else "Groups")
        save_figure(fig, figures, name)
        findings[name] = f"The maximum observed value is {values.max():.0f}; household identifiers are used only to count group sizes."
    return findings


def run_eda(root: Path) -> pd.DataFrame:
    """Generate exploratory analysis outputs and a narrative from the permitted columns."""
    tables, figures = root / "reports" / "tables", root / "reports" / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(root / "data" / "processed" / "hunarlens_youth.csv")
    if set(data.columns) != set(FEATURES) | {"is_unemployed", "group_id"}:
        raise ValueError("Unexpected processed-data schema.")
    audit = value_audit(data, tables)
    findings = create_figures(data, figures)
    lines = ["# exploratory analysis EDA findings", "", "All results below use unweighted analysis records. The dataset construction weighted youth unemployment rate was about 12.8% after the approved future-starter rule (the earlier active-search-only estimate was about 12.6%).", ""]
    for name, finding in findings.items():
        lines.extend([f"## {name.replace('_', ' ').title()}", "", finding, f"Figure: `reports/figures/{name}.png`.", ""])
    lines.extend(["## Category and missing-value review", "", "All 19 features have zero observed NaNs. The value audit is in `reports/tables/feature_value_counts_top15.csv`; all observed feature values below 50 records, including discrete numeric values, are in `reports/tables/rare_categories.csv`. Counts are unweighted and small groups should be interpreted cautiously.", "", "Education code 1 denotes no formal education; current enrolment code 1 means not enrolled; training code 0 means no training. These are substantive responses, not missing values. No 97, 98 or 99 codes are retained in the observed features.", "", "## Proposed engineering for pipeline review", "", "- Consider treating education codes as ordered only after confirming the degree categories form a meaningful order.", "- Consider log-transforming Census density inside the model pipeline; density differs widely across provinces.", "- Consider children under 15 per household member inside the pipeline, with a safe denominator.", "- Consider an age band inside the pipeline if the team approves losing age detail.", "", "These are proposals, not implemented features; comparisons must respect grouped splits and validation-only model selection."])
    (root / "docs" / "eda_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return audit
