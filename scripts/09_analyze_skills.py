# What: makes weighted skills-gap survey tables with cluster bootstrap intervals.
# Why: the descriptive extension must quantify uncertainty and disclose small cells.
# Viva: a bootstrap resamples survey clusters, not individual records.
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.skills import safe_cell

DATA = ROOT / "data/interim/skills_audit_dataset.csv"
TABLES = ROOT / "reports/tables"
BANDS = {1: "No formal", 2: "Below matric", 3: "Matric", 4: "Intermediate", 5: "Degree or above"}
N_BOOT = 1000


def education_band(code):
    return np.select([code.eq(1), code.between(2, 5), code.eq(6), code.eq(7), code.between(8, 16)],
                     [1, 2, 3, 4, 5], default=0)


def modes(frame):
    weights = frame.groupby(["occupation", "band"], observed=True).weight.sum()
    return weights.groupby(level=0).idxmax().map(lambda key: key[1])


def prepare():
    data = pd.read_csv(DATA)
    data["band"] = education_band(data.education)
    workers = data.loc[data.employed & data.occupation.between(1, 9) & data.band.gt(0)].copy()
    youth = data.loc[data.age.between(15, 24)].copy()
    for name, population in [("all_15_plus", workers.loc[workers.age.ge(15)]),
                             ("age_25_44", workers.loc[workers.age.between(25, 44)]),
                             ("youth", workers.loc[workers.age.between(15, 24)])]:
        norm = modes(population)
        youth[name] = youth.occupation.map(norm)
    youth["age_band"] = np.where(youth.age.le(19), "15–19", "20–24")
    return data, workers, youth


class Bootstrap:
    def __init__(self, frame):
        psu = pd.Index(frame.psu.unique())
        self.codes = pd.Series(np.arange(len(psu)), index=psu)
        self.draws = np.random.default_rng(42).multinomial(len(psu), np.full(len(psu), 1 / len(psu)), size=N_BOOT)

    def vector(self, frame):
        ids = self.codes.loc[frame.psu].to_numpy()
        return np.bincount(ids, weights=frame.weight.to_numpy(), minlength=len(self.codes))

    def interval(self, frame, condition):
        denominator = self.draws @ self.vector(frame)
        numerator = self.draws @ self.vector(frame.loc[condition])
        with np.errstate(divide="ignore", invalid="ignore"):
            values = numerator / denominator
        finite = values[np.isfinite(values)]
        return np.quantile(finite, [0.025, 0.975]) if len(finite) else (np.nan, np.nan)


def occupation_band_weights(bootstrap, frame):
    """Aggregate weighted records by PSU, occupation and education band."""
    selected = frame.loc[frame.occupation.between(1, 9) & frame.band.between(1, 5)]
    cluster = bootstrap.codes.loc[selected.psu].to_numpy()
    cell = ((selected.occupation.to_numpy(dtype=int) - 1) * 5 +
            selected.band.to_numpy(dtype=int) - 1)
    sums = np.bincount(cluster * 45 + cell, weights=selected.weight.to_numpy(),
                       minlength=len(bootstrap.codes) * 45)
    return sums.reshape(len(bootstrap.codes), 45)


def bootstrap_modes(bootstrap, reference):
    """Re-estimate weighted occupation modes in every PSU resample."""
    values = (bootstrap.draws @ occupation_band_weights(bootstrap, reference)).reshape(-1, 9, 5)
    result = np.argmax(values, axis=2) + 1
    result[values.sum(axis=2) == 0] = 0
    return result


def mismatch_bootstrap(bootstrap, frame, replicate_modes, denominator=None):
    """Compute matched/over/under shares using each replicate's own modes."""
    values = (bootstrap.draws @ occupation_band_weights(bootstrap, frame)).reshape(-1, 9, 5)
    denom = bootstrap.draws @ bootstrap.vector(frame if denominator is None else denominator)
    education = np.arange(1, 6)[None, None, :]
    expected = replicate_modes[:, :, None]
    valid = (expected > 0) | (values.sum(axis=2, keepdims=True) == 0)
    if not valid.all():
        raise RuntimeError("STOP: a bootstrap replicate lacks a required occupation norm.")
    with np.errstate(divide="ignore", invalid="ignore"):
        shares = np.column_stack([np.sum(values * comparison, axis=(1, 2)) / denom
                                  for comparison in (education == expected, education > expected,
                                                     education < expected)])
    return shares


def replace_interval(row, samples):
    """Replace the fixed-mode interval only for a publishable cell."""
    if row["estimate"] not in ("n<30", "—"):
        finite = samples[np.isfinite(samples)]
        if not len(finite):
            raise RuntimeError("STOP: no valid bootstrap intervals.")
        row["ci_low"], row["ci_high"] = np.quantile(finite, [.025, .975])
        row["bootstrap_median"] = float(np.median(finite))
        row["bootstrap_bias"] = row["bootstrap_median"] - row["estimate"]


def result_row(bootstrap, frame, condition, group, category, reliability="denominator", structural=False):
    subset = frame.loc[condition]
    n = len(frame)
    positive = len(subset)
    count = "n<30" if 0 < n < 30 else n
    flag = "unreliable: n < 50" if n < 50 else ""
    if n == 0:
        return {"group": group, "category": category, "n": 0, "positive_n": 0,
                "estimate": "—", "ci_low": "—", "ci_high": "—", "flag": "no observations"}
    if structural:
        if positive:
            raise RuntimeError("STOP: a structural zero has observed cases.")
        return {"group": group, "category": category, "n": n, "positive_n": 0,
                "estimate": "—", "ci_low": "—", "ci_high": "—", "flag": "structural zero"}
    small = 0 < n < 30 or 0 < positive < 30
    if small:
        reason = "suppressed: n<30"
        if reliability == "positive" and positive < 50:
            reason += "; unreliable: fewer than 50 positives"
        return {"group": group, "category": category, "n": count, "positive_n": "n<30",
                "estimate": "n<30", "ci_low": "n<30", "ci_high": "n<30",
                "flag": reason}
    total = frame.weight.sum()
    value = subset.weight.sum() / total
    independent = np.sum(frame.weight.to_numpy() * np.asarray(condition, dtype=float)) / np.sum(frame.weight.to_numpy())
    if not np.isclose(value, independent, atol=1e-9, rtol=0):
        raise RuntimeError("STOP: independent estimate disagrees.")
    low, high = bootstrap.interval(frame, condition)
    if reliability == "positive" and positive < 50:
        flag = "unreliable: fewer than 50 positives"
    return {"group": group, "category": category, "n": n, "positive_n": positive,
            "estimate": value, "ci_low": low, "ci_high": high, "flag": flag}


def strata(frame):
    yield "overall", frame
    for key in ["sex", "area", "province", "age_band"]:
        for value, group in frame.groupby(key, dropna=False):
            yield f"{key}={value}", group
    for (sex, area), group in frame.groupby(["sex", "area"], dropna=False):
        yield f"sex={sex}, area={area}", group


def save(name, rows):
    pd.DataFrame(rows).to_csv(TABLES / f"skills_{name}.csv", index=False)


def difference_row(boot, employed, unemployed, predicate, group, category):
    first = result_row(boot, employed, predicate(employed), group, category)
    second = result_row(boot, unemployed, predicate(unemployed), group, category)
    if first["estimate"] == "n<30" or second["estimate"] == "n<30":
        return {"group": group, "category": category, "employed_n": first["n"], "unemployed_n": second["n"],
                "difference": "n<30", "ci_low": "n<30", "ci_high": "n<30",
                "flag": "suppressed: small cell"}
    def draws(frame):
        den = boot.draws @ boot.vector(frame)
        num = boot.draws @ boot.vector(frame.loc[predicate(frame)])
        with np.errstate(divide="ignore", invalid="ignore"):
            return num / den
    samples = draws(unemployed) - draws(employed)
    samples = samples[np.isfinite(samples)]
    return {"group": group, "category": category, "employed_n": first["n"], "unemployed_n": second["n"],
            "difference": second["estimate"] - first["estimate"], "ci_low": np.quantile(samples, .025),
            "ci_high": np.quantile(samples, .975),
            "flag": "unreliable: n < 50" if len(employed) < 50 or len(unemployed) < 50 else ""}


def analysis():
    data, workers, youth = prepare()
    boot = Bootstrap(data)
    prior = {}
    for file in ["skills_mismatch.csv", "skills_mismatch_sensitivity.csv"]:
        path = TABLES / file
        if path.exists():
            previous = pd.read_csv(path, keep_default_na=False)
            for row in previous.itertuples(index=False):
                if row.group.startswith("overall; norm=") and row.ci_low not in ("suppressed", "n<30", "—"):
                    prior[(row.group, row.category)] = float(row.ci_high) - float(row.ci_low)
    comparison_path = TABLES / "skills_mismatch_interval_comparison.csv"
    if comparison_path.exists():
        previous = pd.read_csv(comparison_path)
        prior.update({(row.group, row.category): row.fixed_width for row in previous.itertuples(index=False)})
    labour = youth.loc[(youth.employed | youth.unemployed) & youth.band.gt(0)].copy()
    employed = youth.loc[youth.employed & youth.occupation.between(1, 9) & youth.band.gt(0)].copy()
    group_n = employed.groupby("occupation").size()
    if (group_n < 50).any():
        raise RuntimeError("STOP: a small occupation group requires nearest-neighbour merge handling.")
    norm = modes(workers.loc[workers.age.ge(15)])
    references = {"all_15_plus": workers.loc[workers.age.ge(15)],
                  "age_25_44": workers.loc[workers.age.between(25, 44)],
                  "youth": workers.loc[workers.age.between(15, 24)]}
    replicate_modes = {name: bootstrap_modes(boot, frame) for name, frame in references.items()}
    stability = []
    for name, replicated in replicate_modes.items():
        point = modes(references[name])
        for occupation in range(1, 10):
            current = int(point.loc[occupation])
            changed = float(np.mean(replicated[:, occupation - 1] != current))
            for band in BANDS:
                stability.append({"norm": name, "occupation": occupation, "education_band": band,
                                  "band_label": BANDS[band], "point_mode": current,
                                  "reference_n": len(references[name].loc[references[name].occupation.eq(occupation)]),
                                  "replicate_share": np.mean(replicated[:, occupation - 1] == band),
                                  "change_share": changed, "mode_sensitive": changed > .1,
                                  "reliability": "mode unstable" if changed > .1 else ""})
    save("mode_stability", stability)
    if norm.get(9) == 5 or norm.get(2) == 1:
        raise RuntimeError("STOP: occupational education modes fail plausibility check.")
    over = employed.band.gt(employed.all_15_plus)
    if employed.loc[over, "weight"].sum() / employed.weight.sum() >= .6:
        raise RuntimeError("STOP: overall over-education is at least 60%.")
    mode_rows = []
    for norm_name, reference in [("all_15_plus", workers.loc[workers.age.ge(15)]),
                                 ("age_25_44", workers.loc[workers.age.between(25, 44)]),
                                 ("youth", workers.loc[workers.age.between(15, 24)])]:
        for key, value in modes(reference).items():
            mode_rows.append({"norm": norm_name, "occupation": key, "mode_band": int(value),
                              "mode_label": BANDS[int(value)], "n": len(reference.loc[reference.occupation.eq(key)])})
    save("occupation_modes", mode_rows)
    attainment, attainment_difference, outcomes, matrix, training, neet, mismatch, degrees = [], [], [], [], [], [], [], []
    for group, frame in strata(labour):
        if not np.isclose(sum(frame.loc[frame.band.eq(b), "weight"].sum() for b in BANDS) / frame.weight.sum(), 1, atol=1e-9, rtol=0):
            raise RuntimeError("STOP: education shares do not sum to 100%.")
        for status, subset in [("employed", frame.loc[frame.employed]), ("unemployed", frame.loc[frame.unemployed])]:
            if subset.empty:
                continue
            for band, name in BANDS.items():
                attainment.append(result_row(boot, subset, subset.band.eq(band), f"{group}; {status}", name))
            attainment.append(result_row(boot, subset, subset.training.isin([1, 2, 3]), f"{group}; {status}", "Training ever/current"))
        employed_group, unemployed_group = frame.loc[frame.employed], frame.loc[frame.unemployed]
        if len(employed_group) and len(unemployed_group):
            for band, name in BANDS.items():
                attainment_difference.append(difference_row(boot, employed_group, unemployed_group, lambda f, b=band: f.band.eq(b), group, name))
            attainment_difference.append(difference_row(boot, employed_group, unemployed_group,
                                                       lambda f: f.training.isin([1, 2, 3]), group, "Training ever/current"))
    for band, frame in labour.groupby("band"):
        categories = {"unemployed": frame.unemployed, "employed matched": frame.employed & frame.band.eq(frame.all_15_plus),
                      "employed over": frame.employed & frame.band.gt(frame.all_15_plus),
                      "employed under": frame.employed & frame.band.lt(frame.all_15_plus)}
        if not np.allclose(sum(mask.astype(int) for mask in categories.values()), 1):
            raise RuntimeError("STOP: outcomes do not partition the labour force.")
        for category, mask in categories.items():
            structural = ((category == "employed over" and band == min(BANDS)) or
                          (category == "employed under" and band == max(BANDS)) or
                          (category == "employed matched" and band not in norm.values))
            row = result_row(boot, frame, mask, BANDS[int(band)], category, structural=structural)
            if category.startswith("employed "):
                samples = mismatch_bootstrap(boot, frame.loc[frame.employed], replicate_modes["all_15_plus"], denominator=frame)
                replace_interval(row, samples[:, {"employed matched": 0, "employed over": 1, "employed under": 2}[category]])
            outcomes.append(row)
        for training_code, subgroup in frame.groupby(frame.training.isin([1, 2, 3])):
            outcomes.append(result_row(boot, subgroup, subgroup.unemployed, BANDS[int(band)], f"unemployed; training={training_code}"))
    for band, frame in employed.groupby("band"):
        if not np.isclose(sum(frame.loc[frame.occupation.eq(o), "weight"].sum() for o in frame.occupation.unique()) / frame.weight.sum(), 1, atol=1e-9, rtol=0):
            raise RuntimeError("STOP: occupation shares do not sum to 100%.")
        for occupation in sorted(frame.occupation.unique()):
            matrix.append(result_row(boot, frame, frame.occupation.eq(occupation), BANDS[int(band)], f"occupation {int(occupation)}"))
        if band == 5:
            matrix.append(result_row(boot, frame, frame.occupation.between(1, 3), BANDS[int(band)], "occupations 1–3"))
    for group, frame in strata(employed):
        for name in ["all_15_plus", "age_25_44", "youth"]:
            comparisons = [("matched", frame.band.eq(frame[name])), ("over", frame.band.gt(frame[name])), ("under", frame.band.lt(frame[name]))]
            if not np.allclose(sum(mask.astype(int) for _, mask in comparisons), 1):
                raise RuntimeError("STOP: mismatch categories do not partition employed youth.")
            samples = mismatch_bootstrap(boot, frame, replicate_modes[name])
            finite = samples[np.isfinite(samples).all(axis=1)]
            if not np.allclose(finite.sum(axis=1), 1, atol=1e-9, rtol=0):
                raise RuntimeError("STOP: bootstrap mismatch shares do not sum to 100%.")
            for column, (label, condition) in enumerate(comparisons):
                row = result_row(boot, frame, condition, f"{group}; norm={name}", label)
                replace_interval(row, samples[:, column])
                mismatch.append(row)
        observed_level = np.select([frame.education.between(1, 4), frame.education.between(5, 7),
                                    frame.education.between(8, 16)], [1, 2, 3], default=0)
        expected_level = np.select([frame.occupation.eq(9), frame.occupation.between(4, 8),
                                    frame.occupation.between(1, 3)], [1, 2, 3], default=0)
        for label, condition in [("matched", observed_level == expected_level), ("over", observed_level > expected_level),
                                 ("under", observed_level < expected_level)]:
            mismatch.append(result_row(boot, frame, condition, f"{group}; norm=ISCO", label))
    for occupation, frame in employed.groupby("occupation"):
        training.append(result_row(boot, frame, frame.training.isin([1, 2, 3]), f"occupation {int(occupation)}", "training ever/current"))
    for group, frame in strata(youth):
        neet.append(result_row(boot, frame, ~frame.employed & frame.enrolment.eq(1), group, "not employed and not enrolled"))
    for band, frame in youth.groupby("band"):
        neet.append(result_row(boot, frame, ~frame.employed & frame.enrolment.eq(1), BANDS.get(int(band), "Unknown"), "not employed and not enrolled"))
    for code, label in [(8, "Engineering"), (9, "Medicine"), (10, "Computer"), (11, "Agriculture"), (12, "Other two-year degree")]:
        frame = labour.loc[labour.enrolment.eq(1) & labour.education.eq(code)]
        degrees.append(result_row(boot, frame, frame.unemployed, label, "unemployment rate", reliability="positive"))
    for name, rows in [("attainment_gap", attainment), ("attainment_difference", attainment_difference), ("outcomes_by_education", outcomes),
                       ("education_occupation_matrix", matrix), ("training_by_occupation", training),
                       ("mismatch", [row for row in mismatch if "norm=all_15_plus" in row["group"]]),
                       ("mismatch_sensitivity", [row for row in mismatch if "norm=all_15_plus" not in row["group"]]),
                       ("neet", neet), ("degree_type", degrees)]:
        save(name, rows)
    comparisons = []
    for row in mismatch:
        key = (row["group"], row["category"])
        if key in prior and row["ci_low"] not in ("suppressed", "n<30", "—"):
            comparisons.append({"group": key[0], "category": key[1], "fixed_width": prior[key],
                                "reestimated_width": row["ci_high"] - row["ci_low"]})
    save("mismatch_interval_comparison", comparisons)
    print("Core aggregate tables generated.")


if __name__ == "__main__":
    analysis()
