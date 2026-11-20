# What: creates occupation-level tolerance and severe mismatch comparisons.
# Why: dashboard choices must use saved aggregates rather than person-level data.
# Viva: the same occupation modes are re-estimated in each cluster resample.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports/tables"


def load(name, path):
    spec = spec_from_file_location(name, ROOT / "scripts" / path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    analysis = load("skills_analysis_variants", "analyze_skills_gap.py")
    refine = load("skills_refine_variants", "compute_skills_refinements.py")
    data, workers, youth = analysis.prepare()
    boot = analysis.Bootstrap(data)
    modes = analysis.bootstrap_modes(boot, workers.loc[workers.age.ge(15)])
    stability = pd.read_csv(TABLES / "skills_mode_stability.csv")
    employed = youth.loc[youth.employed & youth.occupation.between(1, 9) & youth.band.gt(0)]
    rows = []
    for code, frame in employed.groupby("occupation"):
        diff = frame.band - frame.all_15_plus
        for name, mask, lower, upper in [
            ("within one band", diff.abs().le(1), -1, 1),
            ("two or more bands above", diff.ge(2), 2, 5),
        ]:
            impossible = name == "two or more bands above" and int(frame.all_15_plus.iloc[0]) >= 4
            row = analysis.result_row(boot, frame, mask, name, f"occupation {int(code)}", structural=impossible)
            analysis.replace_interval(row, refine.dynamic_shares(boot, frame, modes, lower, upper))
            mode = stability.loc[stability.norm.eq("all_15_plus") & stability.occupation.eq(code)].iloc[0]
            try:
                wide = float(row["ci_high"]) - float(row["ci_low"]) > .30
            except (ValueError, TypeError):
                wide = False
            row["reliability"] = "mode unstable" if mode.change_share > .1 or wide else ""
            rows.append(row)
    analysis.save("mismatch_occupation_variants", rows)


if __name__ == "__main__":
    main()
