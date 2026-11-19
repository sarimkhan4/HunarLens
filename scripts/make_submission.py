# What: checks a clean checkout, runs tests and previews the submission file list.
# Why: a reviewer can inspect exclusions before any archive is created.
# Viva: the dry run enforces privacy paths and a size limit without deleting files.
import re
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 5_000_000
MANIFEST = "SUBMISSION_MANIFEST.md"
ALLOWED_PROCESSED = {"data/processed/.gitkeep", "data/processed/census_lookup.csv", "data/processed/rare_combinations.csv"}


def removed_paths(text):
    """Read explicitly reviewed tracked REMOVE candidates from the cleanup table."""
    return set(re.findall(r"\|\s*REMOVE\s*\|\s*`([^`]+)`\s*\|", text))


def validate_file(path, size):
    """Refuse raw, intermediate, person-level processed or oversized files."""
    normalized = path.replace("\\", "/")
    if normalized.startswith(("data/raw/", "data/interim/")):
        raise ValueError(f"Refusing private or intermediate path: {normalized}")
    if normalized.startswith("data/processed/") and normalized not in ALLOWED_PROCESSED:
        raise ValueError(f"Refusing person-level processed path: {normalized}")
    if size > MAX_BYTES:
        raise ValueError(f"Refusing file over {MAX_BYTES} bytes: {normalized}")


def clean():
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT, check=True, capture_output=True, text=True)
    if result.stdout.strip():
        raise RuntimeError("Working tree is not clean; commit or otherwise resolve changes before the dry run.\n" + result.stdout)


def build_manifest(files):
    """Compute a stable manifest including its own byte count and the total."""
    own_size = 0
    for _ in range(20):
        entries = sorted([*files, (MANIFEST, own_size)])
        total = sum(size for _, size in entries)
        text = "# Submission dry-run manifest\n\nNo archive was created. Files listed below are tracked, apart from this generated manifest on its first run. REMOVE candidates are excluded.\n\n"
        text += f"Files: {len(entries)}; total: {total:,} bytes; maximum per file: {MAX_BYTES:,} bytes.\n\n```text\n"
        text += "\n".join(f"{name}  ({size:,} bytes)" for name, size in entries) + "\n```\n"
        actual = len(text.encode("utf-8"))
        if actual == own_size:
            return text
        own_size = actual
    raise RuntimeError("Manifest size did not converge")


def main():
    clean()
    print("Running default pytest suite...", flush=True)
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True)
    clean()
    output = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
    tracked = [part.decode("utf-8") for part in output.split(b"\0") if part]
    removed = removed_paths((ROOT / "docs/cleanup_candidates.md").read_text(encoding="utf-8"))
    files = []
    for path in tracked:
        if path in removed or path == MANIFEST:
            continue
        absolute = ROOT / path
        if not absolute.is_file():
            raise RuntimeError(f"Tracked file is unavailable: {path}")
        size = absolute.stat().st_size
        validate_file(path, size)
        files.append((path, size))
    text = build_manifest(files)
    validate_file(MANIFEST, len(text.encode("utf-8")))
    (ROOT / MANIFEST).write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print("Dry run only: no zip was created.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Submission dry run refused: {error}", file=sys.stderr)
        sys.exit(1)
