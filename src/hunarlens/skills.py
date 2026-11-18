# What: disclosure-safe helpers for the skills variable audit.
# Why: audit tables must not expose small survey cells or drift from documentation.
# Viva: weighted totals estimate population counts; unweighted counts show sample size.
from pathlib import Path

import pandas as pd


def safe_cell(count: int, weighted: float) -> tuple[str, str, str]:
    """Suppress small cells and flag estimates with small sample sizes."""
    if count < 30:
        return "suppressed", "suppressed", "suppressed: n < 30"
    return str(count), f"{weighted:.0f}", "unreliable: n < 50" if count < 50 else ""


def render_audit_totals(table: pd.DataFrame) -> str:
    """Render document counts directly from the generated audit table."""
    rows = table.loc[table["category"].eq("ALL")]
    result = ["| Population / variable | Unweighted n | Weighted total |", "|---|---:|---:|"]
    for row in rows.itertuples(index=False):
        result.append(f"| {row.scope}: {row.variable} | {row.n} | {row.weighted_n} |")
    return "\n".join(result)


def audit_document_matches(path: Path, table: pd.DataFrame) -> bool:
    """Catch stale numeric summaries after the generated audit table changes."""
    text = path.read_text(encoding="utf-8")
    start, end = "<!-- AUDIT TOTALS START -->", "<!-- AUDIT TOTALS END -->"
    return start in text and end in text and text.split(start, 1)[1].split(end, 1)[0].strip() == render_audit_totals(table)
