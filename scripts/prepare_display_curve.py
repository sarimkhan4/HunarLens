# What: draws a landscape PR chart from the sealed prediction cache.
# Why: a wide desktop chart needs a different layout, not a stretched image.
# Viva: it reads saved scores; it never loads or rescores the model or test split.
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import precision_recall_curve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hunarlens.config import TARGET, REPORT_FIGURES, REPORT_TABLES, DATA_PROCESSED


def main() -> None:
    """Reformat existing curve coordinates without changing evaluation results."""
    cached = pd.read_csv(DATA_PROCESSED / "test_predictions.csv",
                         usecols=[TARGET, "probability", "dummy_probability"])
    metrics = pd.read_csv(REPORT_TABLES / "test_metrics.csv").set_index("model_threshold")
    fig, ax = plt.subplots(figsize=(11, 4.4), layout="constrained")
    for label, column, result_name, style in [
        ("HGB", "probability", "HGB F1", "-"),
        ("Stratified Dummy", "dummy_probability", "Stratified Dummy", "-.")
    ]:
        precision, recall, _ = precision_recall_curve(cached[TARGET], cached[column])
        ap = metrics.loc[result_name, "pr_auc"]
        ax.plot(recall, precision, style, linewidth=1.8, label=f"{label}: AP={ap:.3f}")
    prevalence = metrics.loc["HGB F1", "prevalence"]
    ax.axhline(prevalence, linestyle="--", color="#45546c", label=f"Prevalence={prevalence:.3f}")
    ax.set(xlabel="Recall", ylabel="Precision", xlim=(-.02, 1.02), ylim=(-.02, 1.04))
    ax.grid(axis="y", alpha=.15)
    ax.legend(loc="upper right", frameon=True)
    path = REPORT_FIGURES / "test_pr_curve_wide.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"Saved {path.relative_to(ROOT)} from cached predictions; no rescoring.")


if __name__ == "__main__":
    main()
