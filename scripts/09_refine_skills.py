# What: generates tolerance, occupation and graduate-absorption tables.
# Why: broad education mismatch figures need occupation and sensitivity context.
# Viva: weighted shares describe groups, not a person's abilities.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"
SPEC = spec_from_file_location("skills_analysis", ROOT / "scripts/09_analyze_skills.py")
analysis = module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def dynamic_shares(boot, frame, norms, minimum, maximum):
    """Use replicate-specific modes for a range of band differences."""
    values = (boot.draws @ analysis.occupation_band_weights(boot, frame)).reshape(-1, 9, 5)
    differences = np.arange(1, 6)[None, None, :] - norms[:, :, None]
    if (((norms == 0) & (values.sum(axis=2) > 0))).any():
        raise RuntimeError("STOP: resample has no norm for an occupied group.")
    denominator = boot.draws @ boot.vector(frame)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.sum(values * ((differences >= minimum) & (differences <= maximum)), axis=(1, 2)) / denominator


def make():
    data, workers, youth = analysis.prepare()
    boot = analysis.Bootstrap(data)
    reference = {"all_15_plus": workers.loc[workers.age.ge(15)],
                 "age_25_44": workers.loc[workers.age.between(25, 44)],
                 "youth": workers.loc[workers.age.between(15, 24)]}
    replicate = {key: analysis.bootstrap_modes(boot, frame) for key, frame in reference.items()}
    employed = youth.loc[youth.employed & youth.occupation.between(1, 9) & youth.band.gt(0)]
    labour = youth.loc[(youth.employed | youth.unemployed) & youth.band.eq(5)]
    variants, occupation, absorption = [], [], []
    for name, modes in replicate.items():
        diff = employed.band - employed[name]
        for label, condition, low, high in [("within one band", diff.abs().le(1), -1, 1),
                                            ("two or more bands above", diff.ge(2), 2, 5)]:
            row = analysis.result_row(boot, employed, condition, name, label)
            analysis.replace_interval(row, dynamic_shares(boot, employed, modes, low, high))
            variants.append(row)
        for code, frame in employed.groupby("occupation"):
            row = analysis.result_row(boot, frame, frame.band.gt(frame[name]), name, f"occupation {int(code)}")
            analysis.replace_interval(row, dynamic_shares(boot, frame, modes, 1, 5))
            occupation.append(row)
    for code, frame in employed.groupby("occupation"):
        observed = np.select([frame.education.between(1, 4), frame.education.between(5, 7),
                              frame.education.between(8, 16)], [1, 2, 3], default=0)
        expected = 1 if code == 9 else 2 if 4 <= code <= 8 else 3
        occupation.append(analysis.result_row(boot, frame, observed > expected, "ISCO", f"occupation {int(code)}"))
    for group, frame in analysis.strata(labour):
        if not (group == "overall" or group.startswith("sex=") and ", " not in group or group.startswith("area=")):
            continue
        masks = [("Employed: groups 1–4", frame.employed & frame.occupation.between(1, 4)),
                 ("Employed: groups 5–9", frame.employed & frame.occupation.between(5, 9)),
                 ("Unemployed", frame.unemployed)]
        if not np.allclose(sum(mask.astype(int) for _, mask in masks), 1):
            raise RuntimeError("STOP: graduate absorption categories do not sum to 100%.")
        for label, mask in masks:
            row = analysis.result_row(boot, frame, mask, group, label)
            if len(frame.loc[frame.unemployed]) < 50:
                prefix = f"{row['flag']}; " if row["flag"] else ""
                row["flag"] = prefix + "unreliable: fewer than 50 unemployed"
            absorption.append(row)
    analysis.secondary_suppress(absorption, lambda row: True)
    analysis.save("mismatch_variants", variants)
    analysis.save("mismatch_by_occupation", occupation)
    analysis.save("graduate_absorption", absorption)
    pd.DataFrame([{"indicator": "PBS NEET youth 2024-25, all areas", "estimate": .284,
                   "n": "not reported in table", "ci_low": "not reported", "ci_high": "not reported",
                   "source_url": "https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf",
                   "source": "PBS Annual Report, Table 8.8"}]).to_csv(TABLES / "skills_neet_external.csv", index=False)
    print("Refined aggregate tables generated.")


if __name__ == "__main__":
    make()
