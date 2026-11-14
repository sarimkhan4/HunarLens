# Decisions

## 2026-11-15 — Stage 0 skeleton

- Leave the feature lists empty until the team approves them after the data audit. This avoids guessing predictors before inspecting the real data.
- Keep raw and interim data out of Git because microdata redistribution and privacy must be checked first.
- The initial dependency files are partial: the available interpreter was Python 3.12 and installation did not complete. Finish the installation and verify the pins in a clean Python 3.11 environment before deployment.
