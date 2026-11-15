# What: generates aggregate percentiles of frozen-model validation probabilities.
# Why: the app's relative position must use validation, never test or live input.
# Viva: percentiles summarise saved-model scores without saving individual rows.
from pathlib import Path
import json
import runpy
import sys

import joblib
import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import FEATURES, MODELS_DIR


def main() -> None:
    loader = runpy.run_path(str(ROOT / "scripts" / "03_stage4_baselines.py"))
    _, validation = loader["load_train_validation"]()
    model = joblib.load(MODELS_DIR / "final_pipeline.joblib")
    with threadpool_limits(limits=1):
        scores = model.predict_proba(validation[FEATURES])[:, 1]
    output = {"source": "validation", "n": len(scores),
              "quantiles": np.quantile(scores, np.linspace(0, 1, 101)).tolist()}
    (MODELS_DIR / "score_quantiles.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Saved {len(output['quantiles'])} validation percentiles from {len(scores)} rows.")


if __name__ == "__main__":
    main()
