# What: inventories local submission candidates without deleting or opening private data.
# Why: review must distinguish tracked artefacts from local caches and raw files.
# Viva: REMOVE means exclude from the package, not delete from the workspace.
import ast
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/submission_cleanup_inventory.csv.gz"


def tracked_paths():
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    return {p.decode("utf-8") for p in result.stdout.split(b"\0") if p}


def classify(path, tracked, referenced):
    name = path.as_posix()
    if name.startswith((".venv/", ".pytest_cache/", ".pytest_tmp/", "data/raw/", "data/interim/")) or "/__pycache__/" in f"/{name}" or ".ipynb_checkpoints/" in name or name.endswith(".pyc") or name == ".pytest-results.xml":
        return "REMOVE", "Local environment, cache, raw survey, intermediate or temporary output; exclude from package"
    if name.startswith("data/processed/") and name not in {"data/processed/.gitkeep", "data/processed/census_lookup.csv", "data/processed/rare_combinations.csv"}:
        return "REMOVE", "Ignored person-level or non-submission processed file"
    if name.startswith("docs/screenshots/") and name not in referenced:
        return "REMOVE", "Screenshot not referenced in the report figure index or README"
    if name not in tracked:
        return "ASK", "Untracked file: review before packaging"
    return "KEEP", "Tracked project or explicitly referenced submission evidence"


def import_findings(tracked):
    files = [ROOT / p for p in tracked if p.endswith(".py")]
    names = {p.stem: p.relative_to(ROOT).as_posix() for p in files if p.parent.name == "hunarlens" and p.stem != "__init__"}
    counts = Counter()
    for file in files:
        try:
            tree = ast.parse(file.read_text(encoding="utf-8-sig"))
        except (OSError, SyntaxError, UnicodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                counts.update(alias.name.split(".")[-1] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                counts[node.module.split(".")[-1]] += 1
    lines = []
    for name, path in sorted(names.items()):
        grep = subprocess.run(["git", "grep", "-l", "-F", name, "--", "*.py", "*.ipynb", "*.md"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        refs = len([line for line in grep.stdout.splitlines() if line != path])
        if not counts[name] and not refs:
            lines.append(f"- ASK `{path}`: no static import or `git grep` reference found; dynamic imports may exist.")
    return lines or ["- No project helper was identified as unreferenced by both the Python AST import graph and `git grep`; this does not prove the absence of dead code."]


def main():
    tracked = tracked_paths()
    references = (ROOT / "docs/report_figures.md").read_text(encoding="utf-8") + (ROOT / "README.md").read_text(encoding="utf-8")
    referenced = {p for p in tracked if p.startswith("docs/screenshots/") and (p in references or p.removeprefix("docs/") in references)}
    rows, totals, large = [], defaultdict(lambda: [0, 0]), []
    skipped = {".git", ".agents", ".codex", ".aws"}
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skipped]
        for filename in files:
            absolute = Path(directory) / filename
            if absolute == INVENTORY:
                continue
            try:
                rel, size = absolute.relative_to(ROOT), absolute.stat().st_size
            except OSError:
                continue
            action, reason = classify(rel, tracked, referenced)
            scope = "tracked" if rel.as_posix() in tracked else "untracked/ignored"
            rows.append((action, scope, rel.as_posix(), size, reason))
            totals[(action, scope)][0] += 1
            totals[(action, scope)][1] += size
            if size > 5_000_000:
                large.append((rel.as_posix(), size, action))
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(INVENTORY, "wt", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["action", "git_scope", "path", "size_bytes", "reason"])
        writer.writerows(sorted(rows, key=lambda row: row[2]))
    screenshots = [row for row in rows if row[0] == "REMOVE" and row[1] == "tracked"]
    text_files = [ROOT / p for p in tracked if Path(p).suffix.lower() in {".py", ".md", ".json", ".toml", ".txt", ".html", ".js", ".css", ".csv"}]
    patterns = [re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), re.compile(r"\bAKIA[0-9A-Z]{16}\b"), re.compile(r"\b\d{5}-\d{7}-\d\b"), re.compile(r"\b(?:\+92|0)3\d{2}[- ]?\d{7}\b")]
    flagged = []
    for file in text_files:
        try:
            if any(pattern.search(file.read_text(encoding="utf-8")) for pattern in patterns):
                flagged.append(file.relative_to(ROOT).as_posix())
        except (OSError, UnicodeError):
            continue
    lines = ["# Cleanup candidates — review only", "", "No files have been deleted. REMOVE means exclude from a submission package; KEEP preserves needed artefacts; ASK requires human review. The complete path-by-path, byte-sized inventory (including ignored local files) is [submission_cleanup_inventory.csv.gz](../reports/submission_cleanup_inventory.csv.gz). Raw or private file contents were not scanned.", "", "## Counts and bytes", "", "| Action | Scope | Files | Total bytes |", "|---|---|---:|---:|"]
    for (action, scope), (count, size) in sorted(totals.items()):
        lines.append(f"| {action} | {scope} | {count} | {size} |")
    lines += ["", "## Tracked screenshots not referenced by the report or README", "", "| Action | Path | Bytes | Reason |", "|---|---|---:|---|"]
    for action, _, name, size, reason in screenshots:
        lines.append(f"| {action} | `{name}` | {size} | {reason} |")
    lines += ["", "## Tracked application and references", "", "- KEEP `app/prototype.html`, `app/prototype.js`, `app/prototype.css`: despite their names they are the active dashboard, not disposable prototypes.", "- KEEP the model, metadata, score quantiles, tracked aggregate tables, the two processed aggregate lookups, requirements, source, tests and referenced screenshots.", "- ASK before removing any tracked script or documentation: scripts can be entry points or imported dynamically; historical decisions may be assessment evidence.", "", "## Import and reference scan", "", *import_findings(tracked), "", "## Potential secrets or identifiers", "", "A pattern scan of tracked text checked private-key headers, AWS-style keys, CNIC-like and Pakistan mobile-number formats. This is not a complete secret or personal-identifier audit. Matches below name files only and may be false positives; ignored raw/intermediate content was deliberately not opened."]
    lines.extend([f"- ASK `{name}`: pattern match; manually review without publishing sensitive values." for name in flagged] or ["- No matches in the scanned tracked text. Names and contextual identifiers still require human review."])
    lines += ["", "## Files over 5 MB", "", "These are local files, not a recommendation to delete them. The packaging dry run rejects selected files above 5,000,000 bytes.", "", "| Path | Bytes | Action |", "|---|---:|---|"]
    for name, size, action in sorted(large):
        lines.append(f"| `{name}` | {size} | {action} |")
    lines += ["", "## Duplicated content", "", "Exact duplicate tracked text files were checked by SHA-256; similarly named lifecycle documents and screenshots are not assumed to be duplicates."]
    hashes = defaultdict(list)
    for file in text_files:
        if file.exists():
            hashes[hashlib.sha256(file.read_bytes()).hexdigest()].append(file.relative_to(ROOT).as_posix())
    duplicate_groups = [group for group in hashes.values() if len(group) > 1]
    lines.extend(["- ASK " + ", ".join(f"`{p}`" for p in group) for group in duplicate_groups] or ["- No exact duplicates among tracked text files."])
    (ROOT / "docs/cleanup_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Inventoried {len(rows)} files; {len(screenshots)} tracked screenshots are removal candidates; {len(flagged)} tracked-text paths need pattern review.")


if __name__ == "__main__":
    main()
