# File naming map

This map records the previous and current names of the application, analysis, and documentation files.

| Current name | Purposeful name |
|---|---|
| `app/prototype_dashboard.py` | `app/dashboard_component.py` |
| `app/prototype.html` | `app/dashboard.html` |
| `app/prototype.css` | `app/dashboard.css` |
| `app/prototype.js` | `app/dashboard.js` |
| `docs/skills_gap_signoff.md` | `docs/skills_gap_summary.md` |
| `docs/report_draft.md` | `docs/project_report.md` |
| `docs/cleanup_candidates.md` | `docs/submission_file_review.md` |
| `docs/IMPLEMENTATION_PLAN.md` | `docs/process/project_plan.md` |
| `docs/SKILLS_GAP_PLAN.md` | `docs/process/skills_gap_plan.md` |
| `reports/tables/stage6_thresholds.csv` | `reports/tables/validation_thresholds.csv` |
| `reports/tables/skills_signoff_test_status.csv` | `reports/tables/skills_summary_test_status.csv` |
| `reports/tables/skills_pres5_test_status.csv` | `reports/tables/skills_dashboard_test_status.csv` |
| `reports/tables/skills_s1_field_values.csv` | `reports/tables/skills_audit_field_values.csv` |
| `notebooks/01_data_audit.ipynb` | `notebooks/data_audit.ipynb` |
| `notebooks/02_eda.ipynb` | `notebooks/exploratory_analysis.ipynb` |
| `notebooks/03_baseline_pipeline.ipynb` | `notebooks/baseline_and_pipeline.ipynb` |
| `notebooks/04_model_experiments.ipynb` | `notebooks/model_comparison.ipynb` |
| `notebooks/06_test_evaluation.ipynb` | `notebooks/test_set_evaluation.ipynb` |
| `notebooks/07_skills_gap.ipynb` | `notebooks/skills_gap_analysis.ipynb` |
| `scripts/00_download_data.py` | `scripts/download_data.py` |
| `scripts/01_audit_raw.py` | `scripts/audit_raw_data.py` |
| `scripts/01_build_dataset.py` | `scripts/build_modeling_dataset.py` |
| `scripts/02_make_splits.py` | `scripts/make_splits.py` |
| `scripts/03_g5_review.py` | `scripts/review_model_comparison.py` |
| `scripts/03_run_experiments.py` | `scripts/compare_models.py` |
| `scripts/03_stage4_baselines.py` | `scripts/compute_baselines.py` |
| `scripts/04_freeze_model.py` | `scripts/save_final_model.py` |
| `scripts/05_enrolment_ablation.py` | `scripts/analyze_enrolment_ablation.py` |
| `scripts/05_explain.py` | `scripts/explain_model.py` |
| `scripts/06_final_test_eval.py` | `scripts/evaluate_on_test_set.py` |
| `scripts/07_audit_app.py` | `scripts/audit_app.py` |
| `scripts/07_build_rare_flags.py` | `scripts/build_rare_flags.py` |
| `scripts/08_overview_indicators.py` | `scripts/compute_survey_indicators.py` |
| `scripts/08_runtime_app_check.py` | `scripts/check_app_runtime.py` |
| `scripts/08_validation_calibration.py` | `scripts/analyze_validation_calibration.py` |
| `scripts/09_analyze_skills.py` | `scripts/analyze_skills_gap.py` |
| `scripts/09_capture_screenshots.py` | `scripts/capture_screenshots.py` |
| `scripts/09_complete_audit.py` | `scripts/complete_skills_audit.py` |
| `scripts/09_model_shift.py` | `scripts/analyze_model_shift.py` |
| `scripts/09_refine_skills.py` | `scripts/compute_skills_refinements.py` |
| `scripts/09_score_quantiles.py` | `scripts/compute_score_quantiles.py` |
| `scripts/09_skills_audit.py` | `scripts/audit_skills_data.py` |
| `scripts/09_skills_gap.py` | `scripts/build_skills_dataset.py` |
| `scripts/09_skills_occupation_variants.py` | `scripts/analyze_occupation_variants.py` |
| `scripts/09_skills_report.py` | `scripts/write_skills_report.py` |
| `scripts/09_verify_skills.py` | `scripts/verify_skills_analysis.py` |
| `scripts/10_capture_skills_screenshots.py` | `scripts/capture_skills_screenshots.py` |
| `scripts/10_stage9e_screenshots.py` | `scripts/capture_dashboard_screenshots.py` |
| `scripts/11_prepare_display_curve.py` | `scripts/prepare_display_curve.py` |
| `scripts/12_check_submission_links.py` | `scripts/check_submission_links.py` |
| `scripts/12_cleanup_inventory.py` | `scripts/inventory_submission_files.py` |
| `scripts/12_generate_submission_report.py` | `scripts/compile_report_numbers.py` |
| `scripts/12_generate_submission_sources.py` | `scripts/generate_data_sources.py` |
| `tests/test_prototype_dashboard.py` | `tests/test_dashboard_component.py` |
| `tests/test_skills_dashboard_s5.py` | `tests/test_skills_dashboard.py` |
| `tests/test_skills_pres5.py` | `tests/test_skills_dashboard_readiness.py` |
| `tests/test_skills_shift_s3.py` | `tests/test_skills_model_shift.py` |
| `tests/test_skills_signoff.py` | `tests/test_skills_summary.py` |
| `tests/test_stage4.py` | `tests/test_pipeline_and_splits.py` |
| `tests/test_stage5.py` | `tests/test_model_comparison.py` |
| `tests/test_stage6.py` | `tests/test_model_freeze.py` |
| `tests/test_stage7.py` | `tests/test_model_explanations.py` |
| `tests/test_stage8.py` | `tests/test_test_evaluation.py` |
| `tests/test_stage9.py` | `tests/test_streamlit_app.py` |

Current screenshots have descriptive page and viewport names directly inside `docs/screenshots/`.
