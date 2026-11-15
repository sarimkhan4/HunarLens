# What: checks the app and fixed parity fixtures with runtime requirements only.
# Why: a clean clone must run without the development test packages or raw data.
# Viva: the same inputs should produce the same probability after a fresh install.
from pathlib import Path
import builtins
import io
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import joblib
import pandas as pd
from streamlit.testing.v1 import AppTest
from threadpoolctl import threadpool_limits
from hunarlens.app_utils import LABELS, build_input, predict_probability

FIXTURES = {"Low": ({"age": 18, "education_level": 6.0, "currently_enrolled": 7.0}, 0.006704),
            "Typical": ({}, 0.092567),
            "High": ({"age": 22, "sex": 2.0, "area": 2.0, "education_level": 13.0, "currently_enrolled": 1.0}, 0.339528)}


def project_open_tracker():
    """Capture repository files opened during actual AppTest requests."""
    opened = set()
    original_open, original_io_open = builtins.open, io.open
    def record(path):
        if isinstance(path, (str, bytes, Path)):
            try:
                relative = Path(path).resolve().relative_to(ROOT)
                if not any(part in {".venv", ".git", "__pycache__"} for part in relative.parts):
                    opened.add(relative.as_posix())
            except (OSError, ValueError):
                pass
    def tracked_open(file, *args, **kwargs):
        record(file)
        return original_open(file, *args, **kwargs)
    def tracked_io_open(file, *args, **kwargs):
        record(file)
        return original_io_open(file, *args, **kwargs)
    return opened, original_open, original_io_open, tracked_open, tracked_io_open


def check_fixture(name, changes, expected, model, metadata, census):
    """Compare a real submitted form and the app builder against a fixed fixture."""
    values = {**metadata["reference_values"], **changes}
    row = build_input(values, metadata, census)
    probability = predict_probability(model, row)
    if abs(probability - expected) > 0.0000005:
        raise AssertionError(f"{name}: six-decimal probability differs from the approved fixture")
    app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90).run()
    app.slider[0].set_value(int(values["age"]))
    for field in ["sex", "area", "education_level", "currently_enrolled"]:
        app.selectbox(key=field).select(values[field])
    app.button[0].click().run()
    if app.exception or app.error or not app.metric or app.metric[0].value != f"{probability:.1%}":
        raise AssertionError(f"{name}: app submission and prediction function differ")
    print(f"{name}: PASS, probability={probability:.6f}, displayed={app.metric[0].value}")
    labels = {field: LABELS[field][int(values[field])] for field in LABELS}
    labels.update({key: int(values[key]) for key in ["age", "household_size", "children_under_15", "other_youth_15_24"]})
    print(json.dumps(labels, ensure_ascii=True, sort_keys=True))


def main():
    opened, original_open, original_io_open, tracked_open, tracked_io_open = project_open_tracker()
    builtins.open, io.open = tracked_open, tracked_io_open
    try:
        metadata = json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))
        model = joblib.load(ROOT / "models/final_pipeline.joblib")
        census = pd.read_csv(ROOT / "data/processed/census_lookup.csv")
        with threadpool_limits(limits=1):
            for name, (changes, expected) in FIXTURES.items():
                check_fixture(name, changes, expected, model, metadata, census)
            app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90).run()
            for page in ["Insights", "About and limits"]:
                app.sidebar.radio[0].set_value(page).run()
                if app.exception or app.error:
                    raise AssertionError(f"{page} page did not load")
    finally:
        builtins.open, io.open = original_open, original_io_open
    opened.add("app/streamlit_app.py")
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path:
            try:
                relative = Path(path).resolve().relative_to(ROOT)
                if relative.parts[:2] == ("src", "hunarlens") and relative.suffix == ".py":
                    opened.add(relative.as_posix())
            except (OSError, ValueError):
                pass
    for path in sorted(opened):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", path], cwd=ROOT,
                                 capture_output=True, text=True).returncode == 0
        print(f"{'PASS' if tracked else 'FAIL'} tracked: {path}")
        if not tracked:
            raise AssertionError(f"App opened an untracked repository file: {path}")
    if "src/hunarlens/app_utils.py" not in opened:
        raise AssertionError("The category-label mapping was not found in tracked application code")


if __name__ == "__main__":
    main()
