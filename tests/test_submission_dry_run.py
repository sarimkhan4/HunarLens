# What: checks the dry-run packaging privacy and size guardrails.
# Why: ignored survey records must not enter a submission archive by accident.
# Viva: explicit allowlists protect processed aggregates while blocking person records.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("submission_dry_run", ROOT / "scripts/make_submission.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)


def test_private_paths_and_large_files_are_rejected():
    for path, size in [("data/raw/survey.dta", 1), ("DATA/RAW/survey.dta", 1), ("data/interim/file.csv", 1),
                       ("data/processed/person.csv", 1), ("data/../data/raw/file.csv", 1),
                       ("models/large.bin", module.MAX_BYTES + 1)]:
        with pytest.raises(ValueError):
            module.validate_file(path, size)
    module.validate_file("data/processed/census_lookup.csv", module.MAX_BYTES)
    module.validate_file("data/processed/rare_combinations.csv", 1)


def test_reviewed_removals_and_manifest_size():
    assert module.removed_paths("| REMOVE | `docs/old.png` | 22 | unused |") == {"docs/old.png"}
    result = module.build_manifest([("app/example.py", 12)])
    assert "app/example.py" in result and module.MANIFEST in result
    assert f"{len(result.encode('utf-8')):,} bytes" in result
