# Cleanup candidates — review only

No files have been deleted. REMOVE means exclude from a submission package; KEEP preserves needed artefacts; ASK requires human review. The complete path-by-path, byte-sized inventory (including ignored local files) is [submission_cleanup_inventory.csv.gz](../reports/submission_cleanup_inventory.csv.gz). Raw or private file contents were not scanned.

## Counts and bytes

| Action | Scope | Files | Total bytes |
|---|---|---:|---:|
| KEEP | tracked | 221 | 5363726 |
| REMOVE | tracked | 41 | 3110820 |
| REMOVE | untracked/ignored | 111703 | 4746984553 |

## Tracked screenshots not referenced by the report or README

| Action | Path | Bytes | Reason |
|---|---|---:|---|
| REMOVE | `docs/screenshots/estimate-1280.png` | 84919 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/estimate-390-result.png` | 51169 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/estimate-390.png` | 39780 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/explorer-1280x900.png` | 84756 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/explorer-1440x900.png` | 79538 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/explorer-lower-1280x900.png` | 84207 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/explorer-lower-1440x900.png` | 85516 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/methodology-1280x900.png` | 87352 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/methodology-1440x900.png` | 87579 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/overview-1280x900.png` | 87117 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/overview-1440x900.png` | 160055 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/performance-1280x900.png` | 101927 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/performance-1440x900.png` | 110053 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/precision-recall-1280x900.png` | 101927 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/precision-recall-1440x900.png` | 110053 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/desktop-polish/profile-information-1440x900.png` | 73613 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/explorer-1024x768.png` | 77427 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/explorer-390x844.png` | 31886 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/methodology-1024x768.png` | 63753 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/methodology-1440x900.png` | 97999 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/overview-1024x768.png` | 131539 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/overview-1440x900.png` | 160766 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/final/performance-1024x768.png` | 66042 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/explorer-360x844.png` | 32867 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/explorer-390x844.png` | 33007 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/explorer-430x844.png` | 32980 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/explorer-760x844.png` | 40354 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/methodology-360x844.png` | 39810 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/methodology-390x844.png` | 40043 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/methodology-430x844.png` | 39395 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/methodology-760x844.png` | 47831 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/overview-360x844.png` | 98632 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/overview-390x844.png` | 104737 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/overview-430x844.png` | 105526 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/overview-760x844.png` | 126804 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/performance-360x844.png` | 41849 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/performance-390x844.png` | 41963 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/performance-430x844.png` | 42636 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/mobile/performance-760x844.png` | 48830 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/skills/skills-1024x768.png` | 82142 | Screenshot not referenced in the report figure index or README |
| REMOVE | `docs/screenshots/skills/skills-390x844.png` | 52441 | Screenshot not referenced in the report figure index or README |

## Tracked application and references

- KEEP `app/prototype.html`, `app/prototype.js`, `app/prototype.css`: despite their names they are the active dashboard, not disposable prototypes.
- KEEP the model, metadata, score quantiles, tracked aggregate tables, the two processed aggregate lookups, requirements, source, tests and referenced screenshots.
- ASK before removing any tracked script or documentation: scripts can be entry points or imported dynamically; historical decisions may be assessment evidence.

## Import and reference scan

- No project helper was identified as unreferenced by both the Python AST import graph and `git grep`; this does not prove the absence of dead code.

## Potential secrets or identifiers

A pattern scan of tracked text checked private-key headers, AWS-style keys, CNIC-like and Pakistan mobile-number formats. This is not a complete secret or personal-identifier audit. Matches below name files only and may be false positives; ignored raw/intermediate content was deliberately not opened.
- No matches in the scanned tracked text. Names and contextual identifiers still require human review.

## Files over 5 MB

These are local files, not a recommendation to delete them. The packaging dry run rejects selected files above 5,000,000 bytes.

| Path | Bytes | Action |
|---|---:|---|
| `.venv/Lib/site-packages/PIL/_avif.cp312-win_amd64.pyd` | 7893504 | REMOVE |
| `.venv/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/inject_dll_amd64.pdb` | 5779456 | REMOVE |
| `.venv/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/inject_dll_x86.pdb` | 5902336 | REMOVE |
| `.venv/Lib/site-packages/numpy.libs/libscipy_openblas64_-63c857e738469261263c764a36be9436.dll` | 20415488 | REMOVE |
| `.venv/Lib/site-packages/pyarrow/arrow.dll` | 19269120 | REMOVE |
| `.venv/Lib/site-packages/pyarrow/arrow_compute.dll` | 10125312 | REMOVE |
| `.venv/Lib/site-packages/pyarrow/arrow_flight.dll` | 15127040 | REMOVE |
| `.venv/Lib/site-packages/pyarrow/parquet.dll` | 7191552 | REMOVE |
| `.venv/Lib/site-packages/pydeck/nbextension/static/index.js.map` | 19408921 | REMOVE |
| `.venv/Lib/site-packages/scipy.libs/libscipy_openblas-197ee2fc9b4d071f7e048078cac74115.dll` | 20262912 | REMOVE |
| `.venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp312-win_amd64.pyd` | 6709248 | REMOVE |
| `.venv/share/jupyter/nbextensions/pydeck/index.js.map` | 19408921 | REMOVE |
| `data/interim/balanced_profile_browser/OnDeviceHeadSuggestModel/20251024.824731831.14/cr_en-us_500000_index.bin` | 7928141 | REMOVE |
| `data/interim/balanced_profile_browser/component_crx_cache/23759e3f6d0119a00038b963cec9fb7abafd7b65a35a7e83c7697511db59e6e7` | 7932363 | REMOVE |
| `data/interim/balanced_profile_browser/optimization_guide_model_store/43/E6DC4029A1E4B4C1/7F43D2EF5B5F0E09/model.tflite` | 36778224 | REMOVE |
| `data/interim/curve_profile_browser/OnDeviceHeadSuggestModel/20251024.824731831.14/cr_en-us_500000_index.bin` | 7928141 | REMOVE |
| `data/interim/curve_profile_browser/component_crx_cache/23759e3f6d0119a00038b963cec9fb7abafd7b65a35a7e83c7697511db59e6e7` | 7932363 | REMOVE |
| `data/interim/curve_profile_browser/optimization_guide_model_store/43/E6DC4029A1E4B4C1/B72F9FFC38E53EDE/model.tflite` | 36778224 | REMOVE |
| `data/interim/desktop_polish_browser/optimization_guide_model_store/43/E6DC4029A1E4B4C1/CB66E752F9FE0F36/model.tflite` | 36778224 | REMOVE |
| `data/interim/live_diagnose_profile/optimization_guide_model_store/43/E6DC4029A1E4B4C1/B4244AFDB032A5E8/model.tflite` | 36778224 | REMOVE |
| `data/interim/mobile_style_browser/Default/Download Service/Files/Unconfirmed 44848.crdownload` | 10190032 | REMOVE |
| `data/interim/mobile_style_browser/Default/Download Service/Files/Unconfirmed 623814.crdownload` | 10147821 | REMOVE |
| `data/interim/skills_audit_dataset.csv` | 20504318 | REMOVE |
| `data/interim/skills_browser_profile/optimization_guide_model_store/43/E6DC4029A1E4B4C1/03878DB212CF826D/model.tflite` | 36778224 | REMOVE |
| `data/interim/stage5/random_forest.joblib` | 8295186 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/PIL/_avif.cp312-win_amd64.pyd` | 7893504 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/numpy.libs/libscipy_openblas64_-63c857e738469261263c764a36be9436.dll` | 20415488 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/pyarrow/arrow.dll` | 19269120 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/pyarrow/arrow_compute.dll` | 10125312 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/pyarrow/arrow_flight.dll` | 15127040 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/pyarrow/parquet.dll` | 7191552 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/pydeck/nbextension/static/index.js.map` | 19408921 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/scipy.libs/libscipy_openblas-197ee2fc9b4d071f7e048078cac74115.dll` | 20262912 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp312-win_amd64.pyd` | 6709248 | REMOVE |
| `data/interim/stage9_fresh_clone/.venv/share/jupyter/nbextensions/pydeck/index.js.map` | 19408921 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/PIL/_avif.cp312-win_amd64.pyd` | 7893504 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/numpy.libs/libscipy_openblas64_-63c857e738469261263c764a36be9436.dll` | 20415488 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/pyarrow/arrow.dll` | 19269120 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/pyarrow/arrow_compute.dll` | 10125312 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/pyarrow/arrow_flight.dll` | 15127040 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/pyarrow/parquet.dll` | 7191552 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/pydeck/nbextension/static/index.js.map` | 19408921 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/scipy.libs/libscipy_openblas-197ee2fc9b4d071f7e048078cac74115.dll` | 20262912 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp312-win_amd64.pyd` | 6709248 | REMOVE |
| `data/interim/stage9b_fresh_clone/.venv/share/jupyter/nbextensions/pydeck/index.js.map` | 19408921 | REMOVE |
| `data/interim/stage9e_browser/OnDeviceHeadSuggestModel/20251024.824731831.14/cr_en-us_500000_index.bin` | 7928141 | REMOVE |
| `data/interim/stage9e_browser/component_crx_cache/23759e3f6d0119a00038b963cec9fb7abafd7b65a35a7e83c7697511db59e6e7` | 7932363 | REMOVE |
| `data/interim/stage9e_browser/optimization_guide_model_store/43/E6DC4029A1E4B4C1/50C8DD7BEBE7E064/model.tflite` | 36778224 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/PIL/_avif.cp312-win_amd64.pyd` | 7893504 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/numpy.libs/libscipy_openblas64_-63c857e738469261263c764a36be9436.dll` | 20415488 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/pyarrow/arrow.dll` | 19269120 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/pyarrow/arrow_compute.dll` | 10125312 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/pyarrow/arrow_flight.dll` | 15127040 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/pyarrow/parquet.dll` | 7191552 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/pydeck/nbextension/static/index.js.map` | 19408921 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/scipy.libs/libscipy_openblas-197ee2fc9b4d071f7e048078cac74115.dll` | 20262912 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp312-win_amd64.pyd` | 6709248 | REMOVE |
| `data/interim/stage9e_runtime_clone/.venv/share/jupyter/nbextensions/pydeck/index.js.map` | 19408921 | REMOVE |
| `data/interim/ui_compare/curve_check_profile/Default/Download Service/Files/Unconfirmed 831927.crdownload` | 30555237 | REMOVE |
| `data/interim/ui_compare/curve_check_profile/Default/Download Service/Files/Unconfirmed 918361.crdownload` | 29899878 | REMOVE |
| `data/interim/ui_compare/profile/Default/Download Service/Files/Unconfirmed 625747.crdownload` | 20757639 | REMOVE |
| `data/interim/ui_compare/profile/Default/Download Service/Files/Unconfirmed 823211.crdownload` | 20315270 | REMOVE |
| `data/raw/LFS 2024-25.sav web.dta` | 436276656 | REMOVE |
| `data/raw/LFS-2024-25-Annual-Report.pdf` | 9425530 | REMOVE |
| `data/raw/LFS-2024-25-STATA.zip` | 9243553 | REMOVE |

## Duplicated content

Exact duplicate tracked text files were checked by SHA-256; similarly named lifecycle documents and screenshots are not assumed to be duplicates.
- No exact duplicates among tracked text files.
