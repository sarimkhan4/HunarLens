# What: builds de-identified roster features and the regional Census lookup.
# Why: shared households must be grouped before selecting youth.
# Viva: no survey identifier is retained in the resulting feature table.
from pathlib import Path

import numpy as np
import pandas as pd

from hunarlens.config import AGE_MAX, AGE_MIN

KEYS = ["PCode", "EBCode", "HHNo"]
PROVINCES = {1: ("kp", "KHYBER PAKHTUNKHWA"), 2: ("punjab", "PUNJAB"),
             3: ("sindh", "SINDH"), 4: ("balochistan", "BALOCHISTAN")}


def roster_features(data: pd.DataFrame) -> pd.DataFrame:
    """Count all roster members and attach their head's demographic fields."""
    if data[KEYS + ["SNo"]].isna().any().any():
        raise ValueError("A household or roster key is missing; grouping cannot be trusted.")
    if data.duplicated(KEYS + ["SNo"]).any():
        raise ValueError("Duplicate person keys require investigation; no rows were dropped.")
    keys = pd.MultiIndex.from_frame(data[KEYS])
    group_id, _ = pd.factorize(keys, sort=True)
    roster = pd.DataFrame({"group_id": group_id + 1, "age": data.S4C6.to_numpy(),
                           "head": data.S4C3.eq(1).to_numpy(),
                           "sex": data.S4C5.to_numpy(), "education": data.S4C9.to_numpy()})
    grouped = roster.groupby("group_id", sort=False)
    sizes = grouped.size().rename("household_size")
    children = roster.age.lt(AGE_MIN).groupby(roster.group_id).sum().rename("children_under_15")
    youth = roster.age.between(AGE_MIN, AGE_MAX).groupby(roster.group_id).sum().rename("youth_count")
    heads = roster.loc[roster["head"], ["group_id", "sex", "education"]]
    if len(heads) != len(sizes) or heads.group_id.duplicated().any():
        raise ValueError("Each household must have exactly one identified head.")
    heads = heads.set_index("group_id").rename(columns={"sex": "head_sex", "education": "head_education"})
    features = sizes.to_frame().join([children, youth, heads])
    result = features.loc[group_id + 1].reset_index()
    result["other_youth_15_24"] = result.pop("youth_count") - roster.age.between(AGE_MIN, AGE_MAX).astype(int).to_numpy()
    return result


def census_lookup(raw: Path) -> pd.DataFrame:
    """Use province-level density and urban share with area-specific household size."""
    rows = []
    for code, (filename, name) in PROVINCES.items():
        sheet = pd.read_excel(raw / f"table_1_{filename}_province.xlsx", header=None)
        matches = sheet.index[sheet[0].astype(str).str.strip().str.upper().eq(name)].tolist()
        if len(matches) != 1:
            raise ValueError(f"Census province row not uniquely found: {name}")
        base = sheet.loc[matches[0]]
        for area_code, area_name in [(1, "RURAL"), (2, "URBAN")]:
            row = sheet.loc[matches[0] + area_code]
            if str(row[0]).strip().upper() != area_name:
                raise ValueError(f"Census {area_name} row missing for {name}")
            rows.append({"province": code, "area": area_code, "census_density": float(base[7]),
                         "census_urban_proportion": float(base[8]) / 100,
                         "census_household_size": float(row[9])})
    lookup = pd.DataFrame(rows)
    if not np.isfinite(lookup[["census_density", "census_urban_proportion", "census_household_size"]]).all().all():
        raise ValueError("Census lookup contains invalid numeric values.")
    return lookup
