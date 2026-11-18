# What: compares weighted survey indicators with the published PBS rates.
# Why: the dashboard should display only rates that reproduce official values.
# Viva: participation uses the whole age group; unemployment uses the labour force.
import importlib.util
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dataset_builder", ROOT / "scripts/01_build_dataset.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
SOURCE = ROOT / "data/pbs_table15_excerpt.txt"
TABLE_URL = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-15.pdf"
REPORT_URL = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf"


def pbs_age_rates() -> dict[str, float]:
    """Read the verified PBS all-area rows and their published column order."""
    result = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"(15-19|20-24) Years ((?:\d+\.\d+\s*){6})", line)
        if not match:
            continue
        age = match.group(1).replace("-", "_")
        values = [float(value) / 100 for value in match.group(2).split()]
        for key, value in zip((f"{kind}_{age}_{sex}" for kind in ("participation", "unemployment")
                               for sex in ("total", "male", "female")), values):
            result[key] = value
    if len(result) != 12:
        raise ValueError("The PBS Table 15 excerpt does not contain the expected age and sex rows.")
    return result


def main() -> None:
    """Apply the approved label, exclusions and weights before aggregating."""
    data = pd.read_stata(builder.RAW, columns=builder.COLS, convert_categoricals=False)
    valid = ~data.S5C5.eq(14) & ~(data.S5C4.eq(1) & data.S5C5.isna()) & data.S4C6.ge(10)
    data = data.loc[valid].copy()
    employed, unemployed = builder.provisional_status(data)
    labour = employed | unemployed
    published = pd.read_csv(builder.TABLES / "label_reproduction.csv").set_index("group")
    groups = {"all_ages": data.S4C6.ge(10), "youth_all": data.S4C6.between(15, 24),
              "youth_male": data.S4C6.between(15, 24) & data.S4C5.eq(1),
              "youth_female": data.S4C6.between(15, 24) & data.S4C5.eq(2),
              "youth_rural": data.S4C6.between(15, 24) & data.Region.eq(1),
              "youth_urban": data.S4C6.between(15, 24) & data.Region.eq(2)}
    age_pbs = pbs_age_rates()
    rows = []
    def add(name, mask, denominator, target, url):
        numerator = data.loc[mask & (labour if name.startswith("participation_") else unemployed), "Weights"].sum()
        total = data.loc[mask & denominator, "Weights"].sum()
        value = numerator / total
        difference = value - target
        rows.append({"indicator": name, "our_value": value, "pbs_value": target, "source_url": url,
                     "difference": difference, "status": "verified" if abs(difference) <= 0.003 else "discrepancy"})
    for name, mask in groups.items():
        add(name, mask, labour, published.loc[name, "pbs_unemployment_rate"], REPORT_URL)
    for start, end in [(15, 19), (20, 24)]:
        for sex, condition in [("total", data.S4C5.notna()), ("male", data.S4C5.eq(1)), ("female", data.S4C5.eq(2))]:
            mask = data.S4C6.between(start, end) & condition
            for kind, denominator in [("participation", data.S4C6.notna()), ("unemployment", labour)]:
                name = f"{kind}_{start}_{end}_{sex}"
                add(name, mask, denominator, age_pbs[name], TABLE_URL)
    output = pd.DataFrame(rows)
    output.to_csv(builder.TABLES / "overview_indicators.csv", index=False)
    print(output.to_string(index=False))


if __name__ == "__main__":
    main()
