# HunarLens: Implementation Plan (CT-378 Machine Learning)

Group **AlphaDevs** · Explainable ML for youth unemployment vulnerability in Pakistan · Deployment: **Streamlit Community Cloud**

> Put this file at `docs/IMPLEMENTATION_PLAN.md`. `AGENTS.md` (repo root) holds the hard rules; this file holds the build order.

---

## 0. How to use this plan

**Working loop, per stage**
1. Give Codex the prompt below with the stage number.
2. Codex builds, runs the tests, prints a **STAGE REPORT**, and stops.
3. The stage owner reads **every line**, re-runs it, and checks the acceptance criteria.
4. At each **GATE**, the team agrees and records the decision in `docs/DECISIONS.md`. Only then start the next stage.

**Prompt template for Codex**
```
Read AGENTS.md and docs/IMPLEMENTATION_PLAN.md.
Implement Stage N only. Inspect the real files before coding; never invent column names.
Meet every acceptance criterion, run pytest, print the STAGE REPORT, then stop.
```

**Priorities:** **P0** = needed for marks, **P1** = strong quality boost, **P2** = nice to have (cut these first if time runs out).

**Definition of done for the project:** every P0 item complete, the Streamlit app live on a public URL, report (PDF, 3–4 pages) written, and each member able to explain any stage in the viva.

---

## 1. Project at a glance

| Item | Value |
|---|---|
| Problem | Which Pakistani youth (15–24, in the labour force) are most at risk of being unemployed, and which factors drive that? |
| Users | Students/researchers/policy analysts exploring patterns (an **aggregate screening and insight tool, not a tool for deciding about individuals**) |
| Data | LFS 2024–25 (individual) + Census 2023 (regional). About 26,000 records, 15+ predictors |
| Target | `is_unemployed` (1 = unemployed, 0 = employed) |
| Models | Stratified Dummy baseline, Logistic Regression, Random Forest, HistGradientBoosting |
| Primary metric | F1 (unemployed class). Also precision, recall, PR-AUC, ROC-AUC, top-10% lift |
| Deliverables | GitHub repo, 3–4 page PDF report, 10-min demo, individual viva, one live Streamlit URL |

**How the plan maps to the marking scheme (10 marks)**

| Marks | Component | Where it is earned |
|---|---|---|
| 2 | ML lifecycle quality | Stages 2–8 (EDA, pipeline, split, baseline + 3 models, CV tuning, test-once evaluation, joblib) |
| 2 | Deployment live | Stage 9 (Streamlit URL working during the demo) |
| 3 | Report | Stage 10 |
| 3 | Viva (individual) | `docs/VIVA_NOTES.md`, rotation rule in section 7 |

> **Confirm with your instructor in writing:** the guideline text still says "all three deployments" in the overview and marking scheme, but you were told one site is enough. Get that in writing.

---

## 2. Key design decisions (already made; change only with team approval)

| Decision | Choice | Why |
|---|---|---|
| Positive class | Unemployed = 1 | The metric is F1 of that class |
| Population | Labour force only (employed + unemployed) aged 15–24 | People outside the labour force are neither employed nor unemployed; mixing them in makes the label noisy |
| Feature selection | **Allowlist** in `config.py` | Safer than a blocklist against label leakage |
| Split | 70/15/15, grouped by household, stratified, seed 42 | Guideline split + no household leakage |
| Split method | `StratifiedGroupKFold(n_splits=20)`: 14 folds → train, 3 → val, 3 → test | Gives exactly 70/15/15 with stratification and groups |
| Tuning | 5-fold `StratifiedGroupKFold` on train, refit on `average_precision` | Threshold-free and suited to imbalance |
| Imbalance handling | Class weights + threshold tuning (+ optional undersampling experiment) | Features are mostly categorical, which makes SMOTE awkward |
| Gradient boosting | `HistGradientBoostingClassifier` | Fast, supports `class_weight`; same algorithm family as classic gradient boosting (state this in the report). Use classic `GradientBoostingClassifier` + sample weights only if your instructor requires it |
| Probabilities | Calibrated (sigmoid) on validation | Class weighting inflates raw probabilities; the app must not overstate risk |
| Threshold | F1-optimal on validation (primary) + recall-oriented screening threshold (secondary) | F1 is the stated metric |
| Explainability | Permutation importance (global) + one-at-a-time "what changes the risk" (local, P1) | Model-agnostic, no extra dependency |
| Data format | CSV (no parquet) | Avoids an extra dependency |
| Python | 3.11, exact pins | Same version locally and on Streamlit Cloud |

---

## 3. Environment and repository

Layout is in `AGENTS.md` §3. Setup:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

**Pinning versions:** install the libraries first, then freeze the exact versions into `requirements.txt` (runtime libraries only) and record the Python version in `README.md`. Do not type version numbers from memory. After any library change, re-freeze and re-run all tests.

**Custom-transformer caveat:** if the pipeline contains a custom class from `src/hunarlens/features.py`, the app can only load it if `src/` is importable. The app therefore starts with `sys.path.insert(0, <repo>/src)`. Keep custom transformers few and simple.

---

## 4. Stages

### Stage 0: Setup and hello-world deployment (P0)

**Goal:** a working skeleton and a proven deployment path before any modelling.

**Tasks**
- Create the repo, folders, `.gitignore`, `config.py` (Appendix A), empty modules, `tests/` with one passing test.
- Create `requirements.txt` / `requirements-dev.txt`.
- Create a minimal `app/streamlit_app.py` ("HunarLens: coming soon") and **deploy it on Streamlit Community Cloud now** (connect GitHub, set the Python version to 3.11 in Advanced settings).
- Create `docs/DECISIONS.md` and `docs/VIVA_NOTES.md`.

**Acceptance**
- [ ] `pytest -q` passes in a clean virtual environment.
- [ ] The placeholder app opens from a public URL in an incognito window.
- [ ] All three members can clone, install and run the repo.

**GATE G0:** URL works for everyone. This removes the biggest late-stage risk.

---

### Stage 1: Data acquisition and audit (P0)

**Goal:** get the official raw data **by script**, then know exactly what it is, where it came from, and what it is allowed to be used for. (You start with no data, so Codex downloads it.)

**Sources (all from the Pakistan Bureau of Statistics, PBS)**

| Dataset | Where | What to take |
|---|---|---|
| LFS 2024-25 microdata | PBS "Labour Force Statistics" page (`https://www.pbs.gov.pk/labour-force-statistics/`) | The microdata file (Stata preferred; SPSS is also listed), the **2024-25 coding scheme** and the **2024-25 questionnaire** |
| LFS 2024-25 Annual Report and tables | Same page | Used to **check your label** (Stage 2 gate) |
| Census 2023 Table-1, district-wise (area, population, density, urban proportion, household size) | PBS census detailed-results page (`https://pbs.gov.pk/result-excel/`) | The Excel tables for each province and Islamabad |

Download links change over time, so Codex must **discover them from these landing pages** instead of trusting a remembered URL. (A third-party project reports the Stata file as a small zip at `https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-STATA.zip`, while PBS's own page describes a RAR file. Whatever you get, record the exact URL.)

**Download task (`scripts/00_download_data.py`)**
- Fetch files from the official PBS pages only, save them in `data/raw/`, and write `data/raw/MANIFEST.json` (URL, access date, file name, size, SHA-256).
- Extract archives (zip/RAR) with a tool available on the machine (7-Zip or unrar). If the sandbox has no internet access or no extractor, **stop and ask the humans**: download the files in a browser, drop them into `data/raw/`, and Codex continues from there (about five minutes of work).
- Read the Stata file with `pandas.read_stata` (keep value labels so categories are readable) and the Census Excel tables with `pandas.read_excel`.
- Record the PBS terms of use / data policy text and the access date in `data/README.md`. If the terms are unclear, say so there.

**Tasks**
- List every file (format, rows, columns, size). Write `docs/data_dictionary.md` from the LFS codebook/questionnaire: variable name, meaning, type, coding, missing codes.
- Write `data/README.md`: for **each dataset** the source, collection method, licence/terms of use, access date, and what was done to remove personal identifiers (course requirement).
- Identify the variables for: age, sex, marital status, education, vocational training, province, district, urban/rural, household size, relationship to head, and the **variables that define the label** (employment, job search, availability).
- Classify every candidate predictor as **ALLOWED / FORBIDDEN (label-derived) / UNSURE**, with a reason. Aim for 18–25 allowed candidates; the final list needs **at least 15** raw features.
- Decide how a **household ID** is built from the survey's identifying fields. If no household ID exists, use the PSU/cluster as a conservative grouping and state this as a limitation.
- Check whether the LFS 2024-25 microdata has **district codes**. If yes, join Census at district level and resolve naming mismatches. If it only has province and urban/rural, join at **province × urban/rural**. In that case the Census features take only a handful of distinct values and add little beyond province and urban/rural, so say so in the report instead of overselling them.

**Outputs:** `docs/data_dictionary.md`, `data/README.md`, `docs/label_definition.md` (draft), `notebooks/01_data_audit.ipynb`.

**Acceptance**
- [ ] Every dataset documented with source, method, licence, date.
- [ ] A table of candidate features with the ALLOWED/FORBIDDEN/UNSURE classification.
- [ ] Household-ID rule and Census join key written down.

**GATE G1 (critical, all three members; about 30 minutes):**
Codex does the work, but it must write a one-page **proposal** with evidence, and the humans approve it.
1. **Label rule.** Codex proposes the exact variables and codes in `docs/label_definition.md`: unemployed = in the labour force, without work, available and seeking work; employed = employed in the same reference period; everyone else excluded. The 2024-25 LFS moved to the newer international labour-statistics standard (19th ICLS), and PBS also reports figures under the older framework, so the file may carry variables for both. Use PBS's **headline definition** unless your instructor says otherwise, and have Codex state which one it used. Humans open the coding scheme and questionnaire PDFs and confirm the variable names really exist and mean what Codex says.
2. **Final feature allowlist** (≥ 15 raw features), with every UNSURE column resolved. Survey weights, identifiers and design variables are never features.
3. **Grouping rule** (household ID, or PSU/cluster fallback) approved.

---

### Stage 2: Build the analysis dataset (P0)

**Goal:** one clean, documented, de-identified modelling table, produced by a script.

**Tasks** (`src/hunarlens/data.py`, `scripts/01_build_dataset.py`)
- Load raw data → keep ages 15–24 → keep labour-force members → build `is_unemployed` per `label_definition.md`.
- Create `group_id` (integer code, never a predictor) and drop all identifiers.
- Standardise categories (spelling, codes, missing codes → NaN) and fix types.
- Join Census features on the agreed key. Save the small regional table as `data/processed/census_lookup.csv`. List any unmatched keys and how they were resolved.
- Remove duplicates; check impossible values.
- Write the **row waterfall** to `reports/tables/row_waterfall.csv` (rows at every filter).
- Save `data/processed/hunarlens_youth.csv`.

**Acceptance**
- [ ] ≥ 5,000 rows (expected ~26,000) and ≥ 15 features.
- [ ] `is_unemployed` has only 0/1 and no missing values; prevalence printed.
- [ ] `group_id` present; **no direct identifiers** anywhere.
- [ ] No column outside the allowlist is marked as a feature.
- [ ] Waterfall explains every dropped row.

**GATE G2: reproduce PBS's published numbers (objective check, no domain expertise needed).**
Before the youth filter, using the survey weight variable on **all** ages the report covers, Codex computes the weighted labour force, weighted number of unemployed and the unemployment rate, and saves them to `reports/tables/label_reproduction.csv` next to the published values. The headline targets from the press coverage are an unemployment rate of about **7.1%**, a labour force of about **83.1 million** and about **5.9 million** unemployed. Codex must confirm in the Annual Report which definition each published figure follows. Accept if the rate is within about 0.2 percentage points and the counts within about 2%. Then compute the weighted 15–24 rate and compare it with the youth table in the Annual Report.

A mismatch means the label, the filters or the weight variable is wrong. Fix it **now**, before any modelling. The weight is used only for this check, never as a feature.

---

### Stage 3: EDA (P0)

**Goal:** understand the data and justify preprocessing choices (guideline: **at least 5 plots**).

**Plots (aim for 8; each with a 1–2 sentence finding in `docs/eda_findings.md`)**
1. Class balance (counts + prevalence).
2. Age distribution by class.
3. Unemployment rate by sex × urban/rural.
4. Unemployment rate by province (or district group).
5. Unemployment rate by education level (with counts, so small groups are visible).
6. Unemployment rate by vocational training (yes/no).
7. Missing values per feature.
8. Numeric distributions + outliers (box plots: age, household size, Census density) and a correlation heatmap for numeric features including the target.

**Also:** household size distribution (explains why grouping matters) and a note on any rare categories.

**Outputs:** `notebooks/02_eda.ipynb`, figures in `reports/figures/`, `docs/eda_findings.md`.

**Acceptance**
- [ ] ≥ 5 clear, labelled plots, each with a written finding.
- [ ] Missing-value, outlier and class-balance sections present.
- [ ] A short list of preprocessing and feature-engineering decisions.

**GATE G3:** approve the engineering list. Keep it small (≤ 5 engineered features), for example: age band, education as ordinal, binary vocational-training flag, log of population density, household-size bucket. Add sex × urban only if EDA supports it.

---

### Stage 4: Splits, pipeline, baseline, leakage tests (P0)

**Goal:** a leak-proof foundation that every later experiment reuses.

**Tasks**
- `splits.py` / `02_make_splits.py`: `StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=42)`. Assign 14 folds to train, 3 to val, 3 to test. Save `split_assignments.csv` (row id, `split`).
- `pipeline.py`: `build_preprocessor()` = `ColumnTransformer` with numeric → `SimpleImputer(median)` + `StandardScaler`; categorical → `SimpleImputer(most_frequent)` + `OneHotEncoder(handle_unknown="ignore", min_frequency=…)`; plus engineered features from `features.py`. `build_model_pipeline(model)` wraps it.
- Baselines: `DummyClassifier(strategy="stratified")` (headline baseline) and `most_frequent` (shows why accuracy is misleading), evaluated on validation.
- **Single-feature leakage scan:** for each feature, cross-validated PR-AUC of a depth-limited tree on that feature alone → `reports/tables/single_feature_scan.csv`. Flag anything above 3× prevalence.
- Write the tests in Appendix C.

**Outputs:** `notebooks/03_baseline_pipeline.ipynb`, split file, baseline table.

**Acceptance**
- [ ] Split sizes ≈ 70/15/15; **prevalence in each split within 1 percentage point of overall**.
- [ ] Test proves **no `group_id` in more than one split**.
- [ ] Test proves `X` columns equal the allowlist exactly.
- [ ] Test proves scaler/imputer statistics come from **training rows only**.
- [ ] Dummy stratified F1 ≈ prevalence (sanity check).
- [ ] Single-feature scan shows no suspicious feature (or it is investigated).

**GATE G4:** read the leakage scan and the tests together. This is the most important review in the project.

---

### Stage 5: Model experiments and tuning (P0)

**Goal:** a fair, logged comparison of three algorithms and several imbalance strategies.

**Experiment ladder** (all on the same pipeline and the same splits; results appended to `reports/tables/experiments.csv`)

| ID | Experiment | Priority |
|---|---|---|
| E0 | Stratified Dummy | P0 |
| E1 | Each model, default settings, no class weights | P0 |
| E2 | Each model with class weights | P0 |
| E3 | E2 tuned (5-fold grouped CV, `refit="average_precision"`) | P0 |
| E4 | E3 + threshold tuned on validation (F1-optimal) | P0 |
| E5 | Random undersampling inside the CV pipeline (needs `imbalanced-learn`; ask first) | P2 |

**Search spaces (starting points; Codex may adjust sensibly and must log changes)**
- **Logistic Regression** (grid): `C` ∈ {0.01, 0.1, 1, 10}, `class_weight` ∈ {None, "balanced"}, `max_iter=1000`.
- **Random Forest** (randomised, `n_iter≈25`): `n_estimators` ∈ {200, 400}; `max_depth` ∈ {6, 10, 16, None}; `min_samples_leaf` ∈ {5, 20, 50}; `max_features` ∈ {"sqrt", 0.3}; `class_weight` ∈ {None, "balanced_subsample"}.
- **HistGradientBoosting** (randomised, `n_iter≈30`): `learning_rate` ∈ {0.03, 0.06, 0.1}; `max_depth` ∈ {3, 5, None}; `max_leaf_nodes` ∈ {15, 31}; `min_samples_leaf` ∈ {20, 50, 100}; `l2_regularization` ∈ {0, 1, 10}; `max_iter` ∈ {200, 400}; `class_weight` ∈ {None, "balanced"}; `early_stopping=False` (the built-in early-stopping split is not household-aware).

**Search mechanics:** `cv=StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` and `search.fit(X_train, y_train, groups=group_train)`. Record `average_precision` and `roc_auc`; `refit="average_precision"`.

**Columns in `experiments.csv`:** `exp_id, model, imbalance_strategy, best_params, cv_ap_mean, cv_ap_std, val_ap, val_roc_auc, val_f1_at_0.5, val_f1_best, threshold, val_precision, val_recall, fit_seconds`.

**Over/under-fitting analysis (guideline requires discussion; P0):**
- Train vs CV vs validation PR-AUC per tuned model (a gap table).
- A grouped learning curve for the leading model.
- One validation curve for a key complexity parameter (for example RF `max_depth` or HGB `max_leaf_nodes`).

**Model selection rule:** highest mean CV `average_precision`; if two models are within 0.01, prefer the simpler/more interpretable one. Write the reasoning in `docs/DECISIONS.md`.

**Outputs:** `notebooks/04_model_experiments.ipynb`, `experiments.csv`, PR-curve figure (all models + no-skill line), learning/validation curves.

**Acceptance**
- [ ] Each of the three algorithms is tuned with 5-fold grouped CV on **train only**.
- [ ] The test split was never loaded in this stage (tests check that `split == "test"` rows are not used).
- [ ] The experiment table is complete and reproducible by `scripts/03_run_experiments.py`.

**GATE G5:** the team picks the final model and freezes its hyperparameters (not Codex).

---

### Stage 6: Calibrate, choose threshold, freeze (P0)

**Goal:** turn the chosen model into the exact object the app and the test evaluation will use.

**Tasks** (`scripts/04_freeze_model.py`)
- Fit the chosen pipeline on the **training split**.
- Calibrate probabilities with the **sigmoid** method on the **validation split**, using the API supported by the pinned scikit-learn version (no deprecated calls). Compare calibration (Brier score and a calibration curve) before vs after.
- Choose thresholds on validation: **F1-optimal** (primary) and a **screening threshold** with recall ≥ 0.60 (secondary; the team may change the target).
- Compute **risk bands** from validation scores: for example "High" = top 10% of scores, "Elevated" = next 20%, "Lower" = rest. Save the cut-offs.
- Save `models/final_pipeline.joblib` and `models/metadata.json` (schema in Appendix B).
- Tag the commit `frozen-v1`.

**Acceptance**
- [ ] The joblib file loads in a fresh process and predicts a probability for a sample row.
- [ ] `metadata.json` records the thresholds, risk bands, prevalence, features and categories, and library versions.
- [ ] The test split has still not been used.

**GATE G6:** after this tag, nothing about the model changes before Stage 8.

---

### Stage 7: Explainability on validation data (P0 global, P1 local)

**Goal:** the "explainable" part of the project title.

**Tasks** (`explain.py`, `scripts/05_explain.py`)
- **Global (P0):** `permutation_importance` on the **validation** split, scoring `average_precision`, `n_repeats=10`, using the **whole pipeline on raw columns** so one-hot columns are grouped back to their original feature. Save `reports/tables/permutation_importance.csv` and a bar chart.
- **Direction of effect (P1):** partial-dependence-style plots for the top 3–4 features (for example risk vs age, vs education level).
- **Local what-if (P1):** for one input, replace each of the top-k features with a typical (mode/median) value and report the change in calibrated risk. This powers the app's per-person explanation.
- Write plain-language interpretation in `docs/eda_findings.md` (or a new `docs/model_findings.md`) with a caveat that **association is not causation**.

**Acceptance**
- [ ] Importance computed on validation only; the chart is saved.
- [ ] A short written interpretation per top feature.
- [ ] The importance ranking looks plausible (if a surprising feature dominates, check for leakage before continuing).

---

### Stage 8: Final test evaluation (**once**) (P0)

**Goal:** the unbiased result that goes into the report.

**Tasks** (`scripts/06_final_test_eval.py`, `notebooks/06_test_evaluation.ipynb`)
- Load the frozen model and `metadata.json`. Predict on the test split **once**, at the frozen threshold.
- Report: F1, precision, recall, PR-AUC, ROC-AUC, confusion matrix, top-10% and top-20% lift, next to the stratified Dummy on the same test set and the prevalence.
- **Grouped bootstrap** (resample households, 1,000 repeats) for 95% confidence intervals on F1, PR-AUC and recall (P1).
- **Subgroup analysis** (P1): precision/recall/positive-rate by sex, urban/rural and province, with sample sizes; flag groups with few positives.
- **Error analysis** (P1): what kinds of records are missed (false negatives) or over-flagged (false positives)?
- Figures: PR curve with the no-skill line, confusion matrix, lift/gain chart.
- Write the interpretation honestly: how much better than the baseline, and what that means in practice.

**Acceptance**
- [ ] The test set was evaluated exactly once; the log in `docs/DECISIONS.md` says so.
- [ ] Every number in the report comes from a generated table.
- [ ] Limitations are stated (see Stage 10).

---

### Stage 9: Streamlit app and deployment (P0)

**Goal:** a robust public app meeting the guideline: **input form, prediction with probability, one explanatory chart.**

**Page spec (`app/streamlit_app.py`)**
- Header: project title and a one-line purpose. Sidebar navigation with three pages.
- **Page 1: Risk estimator**
  - Form built from `metadata.json` (categories and ranges come from there, so the app can never disagree with the model). Age slider 15–24; selectboxes for sex, province → district (cascading), urban/rural, education, vocational training, marital status, household size, and the other allowlisted features.
  - Census features are looked up automatically from `census_lookup.csv` using the chosen district.
  - Output: calibrated probability, the **population base rate** next to it, a **risk band** (Lower / Elevated / High), and whether it crosses the model's operating threshold.
  - **Explanation chart:** the global permutation-importance bar chart (required). P1: a second chart showing how the risk would change if key inputs were set to typical values.
  - Input validation and friendly errors (`try/except`, never a raw traceback).
- **Page 2: Insights** (P1): model comparison table, PR curve, key EDA findings.
- **Page 3: About and limits** (P0): data sources and licences, how the label is defined, the headline limitations, and the disclaimer: *"A statistical pattern tool built on survey data. It is not a decision tool for individuals."*
- Technical: `@st.cache_resource` for model loading, `Path(__file__).resolve().parents[1]` for paths, `sys.path.insert` for `src/`, **no logging of user input**.

**Deployment steps**
1. Push the repo to GitHub (public, or connect a private repo).
2. In Streamlit Community Cloud: select repo, branch `main`, main file `app/streamlit_app.py`, Python 3.11 in Advanced settings.
3. Confirm the build uses the pinned `requirements.txt`.
4. Test in incognito. Wake the app before every demo (idle apps sleep).

**Tests:** `streamlit.testing.v1.AppTest` smoke test; a **parity test** (the same input gives the same probability in the app and in a plain Python call, to 6 decimals).

**Acceptance**
- [ ] Public URL works in incognito on a phone and a laptop.
- [ ] Form, probability, base rate and the explanation chart all present.
- [ ] Invalid input shows a clear message; nothing crashes.
- [ ] Model file is small enough for GitHub (aim for under ~25 MB; reduce trees/depth or use compressed joblib if needed).
- [ ] Parity and smoke tests pass.

**GATE G9:** one member who did *not* build the app uses it end to end.

---

### Stage 10: Report, README, demo, viva (P0)

**README.md**
- What it is (3 lines), live Streamlit link, setup steps (Python 3.11, install, `pytest`, run scripts, run app), data-access note (where to get raw data; licence), repo tour, results summary, team table.

**Report (PDF, 3–4 pages)** with the guideline's sections and a page budget:

| Section | Pages | Content |
|---|---|---|
| Abstract | 0.15 | Problem, data, method, headline result with CI, one limitation |
| Problem and motivation | 0.3 | Why youth unemployment, who uses the tool |
| Data collection | 0.5 | Both sources, licences, dates, de-identification, label definition, final row/feature counts |
| EDA | 0.6 | 3–4 key plots, class imbalance, main findings |
| Methodology | 0.7 | Pipeline figure, grouped split, models, tuning, imbalance handling, threshold, calibration |
| Results | 0.9 | Experiments table, final test table with CIs vs baseline, PR curve, importance chart, lift |
| Deployment | 0.3 | Screenshots and URL |
| Limitations and future work | 0.3 | See below |
| References + contribution table | 0.35 | Citations; per-member contributions |

**Limitations to state honestly:** demographics explain only part of unemployment (no labour-demand, network or job-search information); survey sampling weights not used (records treated as unweighted); the household grouping is approximate if built from survey identifiers; one survey year; the label depends on the official definition; subgroup performance differs; correlation is not causation; the tool is not for decisions about individuals.

**References:** PBS LFS 2024–25; PBS Population and Housing Census 2023; scikit-learn (Pedregosa et al., 2011); Streamlit documentation; any method papers you actually cite. **Cite everything used or adapted**; uncited copied material scores zero for the whole project.

**Demo (10 minutes): rehearse twice**
- **0:00–3:00** problem, the two data sources, the imbalance, and the leakage/household safeguards.
- **3:00–7:00** live app: pick a profile, show probability vs base rate, the chart, and the "About" page. Because only one deployment is required, you have time to show the **model-comparison insight** too. Have screenshots as a fallback.
- **7:00–10:00** results: baseline vs final model, PR curve, lift, honest limitations.
- Keep the app warm and have the local copy ready as a backup.

**Viva preparation:** see Appendix D; every member rehearses answering about any stage.

---

## 5. Realistic expectations

- Expect modest gains over the dummy baseline (F1 well below 0.6). That is a legitimate finding about how predictable unemployment is from demographics.
- The honest story for the report: *"Unemployment is only partly predictable from demographic, educational and regional factors; the best model improves PR-AUC by about N× over chance and flags the highest-risk 10% of youth at about N× the base rate."* Fill N from your own results.
- Do not chase the score with leaked features. If a result jumps, suspect leakage.

---

## 6. Timeline (compress to your real deadline; keep ≥ 2 days of buffer)

Late submission costs **1 mark per day**.

| Days | Stages | Notes |
|---|---|---|
| 1–2 | 0, 1 | G0, G1 are critical |
| 3–4 | 2, 3 | G2 label sanity check |
| 5 | 4 | G4 leakage review |
| 6–8 | 5 | Heaviest compute; start the report outline in parallel |
| 9 | 6, 7 | Freeze, then explain |
| 10 | 8 | Test once |
| 11–12 | 9 | App + deployment |
| 13–14 | 10 | Report, README, rehearsal, buffer |

**If time runs short, cut in this order:** E5 undersampling (P2) → local what-if chart → Insights page → partial-dependence plots → subgroup/error analysis → bootstrap CIs. **Never cut:** leakage tests, grouped splits, the baseline, tuning, test-once, calibration or threshold, the About page, the report, the viva notes.

---

## 7. Team organisation

| Member | Owns | Also writes |
|---|---|---|
| A | Stages 1–3 (data, label, EDA) | Report: Data, EDA |
| B | Stages 4–6 (splits, pipeline, models, freeze) | Report: Methodology |
| C | Stages 7–9 (explainability, test evaluation, app) | Report: Results, Deployment |
| All | Stage 0, Stage 10, gates, README | Limitations, references, contribution table |

**Viva rotation rule:** each member must **explain a stage they did not own** to the group, and each must have personally run and modified at least one script (for example change a hyperparameter and re-run). Examiners can ask any member about any part.

---

## 8. Risk register

| Risk | Mitigation |
|---|---|
| Wrong label rule (noisy positives) | G1 sign-off + G2 comparison with the PBS published rate |
| No household ID | Group by PSU/cluster; state the limitation |
| Label leakage via forbidden columns | Allowlist, keyword tripwire test, single-feature scan, R9 |
| Very low scores | Frame honestly (Section 5); focus on lifecycle quality, PR-AUC and lift |
| Codex invents variables or APIs | AGENTS.md rule "inspect real files first"; human review at every stage |
| Streamlit build fails or sklearn version mismatch | Stage 0 hello-world deploy; pinned requirements; parity test |
| Model file too large | Limit trees/depth, compressed joblib |
| Census and LFS regions do not match | Mapping table; fallback to province level; document |
| LFS file has no district codes | Join Census at province × urban/rural; Census features then add little signal; say so in the report |
| Codex sandbox has no internet or cannot extract RAR | Humans download in a browser into `data/raw/`; Codex continues |
| Label does not match PBS published totals | Weighted reproduction test at Gate G2 |
| Data licence restricts sharing | Keep raw data out of git; include a download note |
| Time overrun | Priorities P0/P1/P2 and the cut list |
| App asleep or offline during the demo | Wake it before the demo; local backup; screenshots |
| Test set accidentally peeked at | R4, log it in `DECISIONS.md`, disclose |

---

## 9. Final submission checklist

**Problem and data**
- [ ] Real problem with a clear user · no forbidden or duplicate dataset
- [ ] Two public sources combined · ≥ 5,000 rows · ≥ 15 features
- [ ] Source, method, licence and date documented for each dataset · identifiers removed

**ML lifecycle**
- [ ] EDA with ≥ 5 plots (distributions, missing values, outliers, correlations, class balance)
- [ ] Preprocessing in one scikit-learn `Pipeline`, fitted on training data only
- [ ] Train/val/test split (70/15/15), grouped and stratified
- [ ] Baseline + three algorithms
- [ ] 5-fold CV with `GridSearchCV`/`RandomizedSearchCV`
- [ ] Metrics reported once on the held-out test set · over/under-fitting and errors discussed
- [ ] Final pipeline saved with `joblib` · versions pinned in `requirements.txt`

**Deployment (Streamlit)**
- [ ] Input form · probability/confidence · one explanatory chart
- [ ] Public URL working live and tested in incognito
- [ ] Instructor confirmation that one deployment is sufficient

**Deliverables**
- [ ] GitHub repo with `data/` (or download script), `notebooks/`, `app/`, `models/`, `requirements.txt`, README with setup steps and the deployment link
- [ ] Report PDF (3–4 pages) with all required sections, citations and the individual contribution table
- [ ] 10-minute demo rehearsed · all three members ready for the viva
- [ ] Submitted before the deadline

---

## Appendix A: `config.py` skeleton

```python
# src/hunarlens/config.py
# What: central constants. Why: one source of truth. Viva: "where do feature lists live?"
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = ROOT / "data" / "processed"
REPORT_TABLES = ROOT / "reports" / "tables"
REPORT_FIGURES = ROOT / "reports" / "figures"
MODELS_DIR = ROOT / "models"

RANDOM_STATE = 42
TARGET = "is_unemployed"
GROUP = "group_id"
SPLIT = "split"
AGE_MIN, AGE_MAX = 15, 24
SPLIT_FRACTIONS = {"train": 0.70, "val": 0.15, "test": 0.15}
SPLIT_FOLDS = 20            # 14 train / 3 val / 3 test
N_CV_FOLDS = 5

# --- Filled in by the HUMANS at Gate G1/G3. Codex must not guess these. ---
NUMERIC_FEATURES: list[str] = []
CATEGORICAL_FEATURES: list[str] = []
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES   # must be >= 15 raw features

# Tripwire (a warning, not proof): flag feature names that look labour-market related.
LABEL_KEYWORDS = ["employ", "job", "work", "occupation", "industry",
                  "wage", "hours", "seek", "avail", "activity"]
ALLOWED_DESPITE_KEYWORD: list[str] = []   # human-approved exceptions only
```

## Appendix B: `models/metadata.json` schema

```json
{
  "model_name": "string",
  "trained_on": "YYYY-MM-DD",
  "python_version": "string",
  "sklearn_version": "string",
  "random_state": 42,
  "calibration": "sigmoid",
  "features": {
    "numeric": {"age": [15, 24]},
    "categorical": {"sex": ["..."], "province": ["..."]}
  },
  "district_by_province": {"Province": ["District", "..."]},
  "prevalence_train": 0.0,
  "threshold_f1": 0.0,
  "threshold_screening": 0.0,
  "risk_bands": {"high_min": 0.0, "elevated_min": 0.0},
  "metrics_val": {"f1": 0.0, "precision": 0.0, "recall": 0.0, "pr_auc": 0.0, "roc_auc": 0.0},
  "census_lookup": "data/processed/census_lookup.csv",
  "importance_file": "reports/tables/permutation_importance.csv"
}
```

## Appendix C: tests to write (pytest)

| Test | Checks |
|---|---|
| `test_no_group_overlap` | No `group_id` appears in two splits |
| `test_split_fractions` | Sizes ≈ 70/15/15; prevalence per split within 1 point of overall |
| `test_features_allowlist` | `X.columns == config.FEATURES`; target and group not in `X` |
| `test_keyword_tripwire` | No feature name contains a `LABEL_KEYWORDS` term unless approved |
| `test_label_binary` | `is_unemployed` ∈ {0, 1}, no NaN; ages within 15–24 |
| `test_fit_on_train_only` | Scaler/imputer statistics equal those computed on train rows only |
| `test_test_split_untouched` | Stage 5–7 code never selects `split == "test"` rows |
| `test_model_roundtrip` | joblib load → predict probability in [0, 1] |
| `test_metadata_consistent` | `metadata.json` categories match the pipeline's encoder categories |
| `test_requirements_pinned` | Every `requirements.txt` line uses `==` |
| `test_app_smoke` | `AppTest` runs the app without exceptions |
| `test_app_parity` | App probability equals plain-Python probability (6 decimals) |

## Appendix D: viva question bank (rehearse answers)

1. Why F1 for the positive class rather than accuracy? What would a majority-class model score?
2. What does prevalence tell you, and why is it the no-skill PR-AUC?
3. What is data leakage? Name two ways it could have happened here and how you prevented them.
4. Why split by household? What would go wrong with a random split?
5. Why is every preprocessing step inside the pipeline, and what does "fit on train only" mean?
6. Why did you tune on PR-AUC but report F1? Where did the threshold come from?
7. What does class weighting do? Why did you also calibrate probabilities?
8. Walk through how Random Forest and Gradient Boosting differ. Why does Logistic Regression need scaling?
9. Is the model over-fitting? Show the evidence (train vs CV vs validation, learning curve).
10. What does permutation importance measure, and what does it not tell you?
11. What is lift in the top 10%, and why is it useful for an imbalanced problem?
12. Why can't you use the "job search" variable as a feature?
13. How is the label defined, and who is excluded from the data?
14. What are the main limitations, and who should not use this app, or for what?
15. Show me where in the code the threshold is applied, and where the test set is first used.
