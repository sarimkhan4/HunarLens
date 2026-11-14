# What: checks a provisional label against published PBS totals.
# Why: the analysis dataset must not be built if the label does not reproduce PBS.
# Viva: survey weights estimate population totals; they are never predictors.
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import DATA_PROCESSED, FEATURES
from hunarlens.data import census_lookup, roster_features

RAW = ROOT / "data" / "raw" / "LFS 2024-25.sav web.dta"
TABLES = ROOT / "reports" / "tables"
COLS = ["Weights", "Region", "S4C4", "S4C5", "S4C6", "S5C1", "S5C2", "S5C3", "S5C4", "S5C5", "S5C6", "S5C7", "S5C8", "S5C9", "S5C10", "S9C1", "S9C5", "S9C6"]
ROSTER_COLS = ["PCode", "EBCode", "HHNo", "SNo", "Province", "Region", "S4C3", "S4C5", "S4C6", "S4C7", "S4C81", "S4C82", "S4C9", "S4C10", "S4C11"]


def provisional_status(data: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Follow the questionnaire routes conservatively for the reproduction check."""
    paid = data.S5C1.eq(1)
    sale_work = data.S5C10.isin([1, 2])
    business = (data.S5C2.eq(1) | data.S5C3.eq(1)) & (data.S5C9.eq(4) | (data.S5C9.isin([1, 2, 3]) & sale_work))
    absent = data.S5C4.eq(1) & ~data.S5C5.eq(1) & (data.S5C6.eq(1) | data.S5C7.eq(1))
    farming = data.S5C8.isin([1, 2, 3]) & sale_work
    employed = paid | business | absent | farming
    seeking = data.S9C1.eq(1)
    future_starter = data.S9C1.eq(2) & data.S9C5.eq(1)
    unemployed = ~employed & (seeking | future_starter) & data.S9C6.eq(1)
    return employed, unemployed


def save_absence_tables(data: pd.DataFrame) -> None:
    """Save grouped counts only; never export household or person identifiers."""
    absent = data.loc[data.S5C4.eq(1)].copy()
    absent["age_band"] = pd.cut(absent.S4C6, [0, 14, 24, 34, 44, 54, 64, float("inf")], labels=["0-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65+"])
    for field, name in [("S4C5", "sex"), ("age_band", "age")]:
        table = pd.crosstab(absent.S5C5.fillna(-1), absent[field], dropna=False)
        table.index.name = "absence_code_minus_1_is_missing"
        table.to_csv(TABLES / f"absence_code_by_{name}.csv")
    data.groupby(["S5C4", "S5C5", "S5C6", "S5C7"], dropna=False).size().rename("count").reset_index().to_csv(TABLES / "label_input_absence_crosstab.csv", index=False)
    data.groupby(["S5C1", "S5C2", "S5C3", "S5C8", "S5C9", "S5C10", "S9C1", "S9C6"], dropna=False).size().rename("count").reset_index().to_csv(TABLES / "label_input_routes_crosstab.csv", index=False)


def reproduction(data: pd.DataFrame, employed: pd.Series, unemployed: pd.Series) -> pd.DataFrame:
    """Compare survey-weighted estimates with report tables 3.3, 9.4 and 8.5.2."""
    youth = data.S4C6.between(15, 24)
    groups = [("all_ages", data.S4C6.ge(10), 0.071), ("youth_all", youth, 0.128),
              ("youth_male", youth & data.S4C5.eq(1), 0.125),
              ("youth_female", youth & data.S4C5.eq(2), 0.140),
              ("youth_rural", youth & data.Region.eq(1), 0.115),
              ("youth_urban", youth & data.Region.eq(2), 0.158)]
    rows = []
    for name, mask, rate in groups:
        emp = data.loc[mask & employed, "Weights"].sum()
        unemp = data.loc[mask & unemployed, "Weights"].sum()
        published = {"all_ages": (77200000, 5900000, 83100000),
                     "youth_all": (17900000, 2600000, 20600000),
                     "youth_male": (13700000, 2000000, 15700000),
                     "youth_female": (4200000, 700000, 4900000)}.get(name, (None, None, None))
        rows.append({"group": name, "employed": emp, "unemployed": unemp,
                     "labour_force": emp + unemp, "unemployment_rate": unemp / (emp + unemp),
                     "pbs_employed": published[0], "pbs_unemployed": published[1],
                     "pbs_labour_force": published[2],
                     "pbs_unemployment_rate": rate})
    return pd.DataFrame(rows)


def build_youth(keep: pd.Series, employed: pd.Series, unemployed: pd.Series) -> None:
    """Build roster summaries first, then keep only approved de-identified features."""
    roster = pd.read_stata(RAW, columns=ROSTER_COLS, convert_categoricals=False)
    household = roster_features(roster)
    selected = keep & roster.S4C6.between(15, 24) & (employed | unemployed)
    names = {"S4C6": "age", "S4C5": "sex", "S4C7": "marital_status", "S4C3": "relationship_to_head",
             "S4C81": "can_read", "S4C82": "can_write", "S4C9": "education_level",
             "S4C10": "currently_enrolled", "Province": "province", "Region": "area"}
    youth = roster.loc[selected, list(names)].rename(columns=names).copy()
    youth = youth.join(household.loc[selected].set_axis(youth.index))
    youth["has_training"] = roster.loc[selected, "S4C11"].map({1: 1, 2: 1, 3: 1, 4: 0})
    valid_codes = {"sex": range(1, 3), "marital_status": range(1, 5), "relationship_to_head": range(1, 10),
                   "can_read": range(1, 3), "can_write": range(1, 3), "education_level": range(1, 17),
                   "currently_enrolled": range(1, 17), "head_sex": range(1, 3), "head_education": range(1, 17)}
    for column, codes in valid_codes.items():
        youth[column] = youth[column].where(youth[column].isin(codes))
    lookup = census_lookup(RAW.parent)
    youth = youth.merge(lookup, how="left", on=["province", "area"], validate="many_to_one", indicator=True)
    if not youth["_merge"].eq("both").all():
        raise ValueError("Some youth records have no matching Census region.")
    youth["is_unemployed"] = unemployed.loc[selected].astype(int).to_numpy()
    youth = youth[["group_id", *FEATURES, "is_unemployed"]]
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    lookup.to_csv(DATA_PROCESSED / "census_lookup.csv", index=False)
    youth.to_csv(DATA_PROCESSED / "hunarlens_youth.csv", index=False)
    missing = youth[FEATURES].isna().mean().rename("missing_rate").rename_axis("feature").reset_index()
    missing.to_csv(TABLES / "feature_missingness.csv", index=False)
    print(f"Youth records: {len(youth)}; prevalence: {youth.is_unemployed.mean():.4f}; groups: {youth.group_id.nunique()}")


def main() -> int:
    """Stop before building youth data when the all-age gate fails."""
    TABLES.mkdir(parents=True, exist_ok=True)
    data = pd.read_stata(RAW, columns=COLS, convert_categoricals=False)
    save_absence_tables(data)
    code14 = data.S5C5.eq(14)
    missing = data.S5C4.eq(1) & data.S5C5.isna()
    keep = ~(code14 | missing)
    pd.DataFrame([{"step": "all survey records", "rows": len(data)}, {"step": "ambiguous absence code: after excluding S5C5=14", "rows": int((~code14).sum())}, {"step": "ambiguous absence code: after missing S5C5 where S5C4=1", "rows": int(keep.sum())}, {"step": "age 10 and over", "rows": int((keep & data.S4C6.ge(10)).sum())}]).to_csv(TABLES / "row_waterfall.csv", index=False)
    raw_keep = keep.copy()
    data = data.loc[keep & data.S4C6.ge(10)].copy()
    employed, unemployed = provisional_status(data)
    starter = data.S9C1.eq(2) & data.S9C5.eq(1) & data.S9C6.eq(1) & ~employed
    code1 = data.S5C4.eq(1) & data.S5C5.eq(1)
    pd.DataFrame([{"group": "all_ages", "records": int(starter.sum()),
                   "weighted_count": data.loc[starter, "Weights"].sum()},
                  {"group": "youth_15_24", "records": int((starter & data.S4C6.between(15, 24)).sum()),
                   "weighted_count": data.loc[starter & data.S4C6.between(15, 24), "Weights"].sum()},
                  {"group": "S5C5_1_available", "records": int((data.S5C4.eq(1) & data.S5C5.eq(1) & data.S9C6.eq(1)).sum()),
                   "weighted_count": data.loc[data.S5C4.eq(1) & data.S5C5.eq(1) & data.S9C6.eq(1), "Weights"].sum()},
                  {"group": "S5C5_1_all", "records": int(code1.sum()), "weighted_count": data.loc[code1, "Weights"].sum()},
                  {"group": "S5C5_1_unemployed", "records": int((code1 & unemployed).sum()),
                   "weighted_count": data.loc[code1 & unemployed, "Weights"].sum()}]).to_csv(TABLES / "future_starters_diagnostic.csv", index=False)
    result = reproduction(data, employed, unemployed)
    result.to_csv(TABLES / "label_reproduction.csv", index=False)
    print(result.to_string(index=False))
    total = result.iloc[0]
    passed = 5850000 <= total.unemployed <= 5950000 and 0.0705 <= total.unemployment_rate <= 0.0715
    if not passed:
        print("Reproduction gate failed; no youth dataset was built.")
        return 1
    all_employed = pd.Series(False, index=raw_keep.index)
    all_unemployed = pd.Series(False, index=raw_keep.index)
    all_employed.loc[data.index] = employed
    all_unemployed.loc[data.index] = unemployed
    youth_filter = raw_keep & pd.read_stata(RAW, columns=["S4C6"], convert_categoricals=False).S4C6.between(15, 24)
    waterfall = pd.read_csv(TABLES / "row_waterfall.csv")
    additions = pd.DataFrame([{"step": "age 15-24 after exclusions", "rows": int(youth_filter.sum())},
                              {"step": "eligible employed or unemployed youth", "rows": int((youth_filter & (all_employed | all_unemployed)).sum())}])
    pd.concat([waterfall, additions], ignore_index=True).to_csv(TABLES / "row_waterfall.csv", index=False)
    build_youth(raw_keep, all_employed, all_unemployed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
