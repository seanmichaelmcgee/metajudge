# planning/ — Planning Document Index

Classification of planning documents. The Family C sprint directory is the
current operational focus.

**Classifications:**
- **Operational** — active reference for current sprint
- **Background** — useful context, not execution guidance
- **Historical** — superseded; moved to `archive/`

---

## Operational

### `family_c_sprint/` — Current sprint (start here)

| Document | Purpose | Priority |
|----------|---------|----------|
| `07_sprint_checklist.md` | Step-by-step execution plan (Days 1-3) | **Read first** |
| `03_scoring_blueprint.md` | Scoring design with worked examples | High |
| `02_item_design.md` | Item taxonomy, schema, 35-item seed plan | High |
| `04_task_architecture.md` | SDK patterns, C1/C2 prompt templates | High |
| `00_executive_roadmap.md` | Strategic recommendation + open questions | Medium |
| `01_scientific_constraints.md` | Non-negotiable design principles from literature | Medium |
| `05_validation_plan.md` | 5-model evaluation protocol and promotion criteria | Medium |
| `06_risks_and_gates.md` | Failure modes and decision gates | Medium |
| `08_results_grounded_amendments.md` | Post-v0.5.5.1 amendments | Reference |
| `10_v0551_revalidation.md` | Baseline update to v0.5.5.1.1 clean-subset | Reference |
| `11_integration_notes.md` | Integration notes for v2 modules | Reference |
| `12_validation_promotion.md` | Validation and promotion criteria | Reference |
| `13_pilot_orchestrator_instructions.md` | Instructions for pilot orchestrator agent | Reference |
| `15_resume_safe_hardening_orchestrator_prompt.md` | Hardening prompt for production orchestrator | Reference |
| `09_deep_research_prompt.md` | Research prompt for adversarial item expansion | Background |
| `Theoretical_grounding_MetaJudge_Family_C.md` | Deep theoretical analysis (41K) | Background |

### Other operational docs

| Document | Purpose |
|----------|---------|
| `family_b_grading_fix_plan.md` | Family B grading fix (completed but still relevant reference) |

## Background

| Document | Purpose |
|----------|---------|
| `scoring_plan.md` | Family A Brier scoring and adjudication — still valid for Family A |
| `verification/` | SDK verification records |

## Historical (archived)

| Document | Why archived |
|----------|-------------|
| `archive/v1_architecture.md` | Original Family A architecture; superseded by current code |
| `archive/dataset_construction_plan.md` | Original item sourcing plan; completed |
| `archive/calibration_research_brief.md` | Early calibration research |
| `archive/calibration_research_directive.md` | Early calibration directive |
| `archive/calibration_v3/` | V3 calibration plans; superseded by V4.2 |
| `archive/dataset_wishlist_v0.md` | Original dataset wishlist |
| `archive/expansion_sprint_context.md` | V2 expansion sprint context |
| `archive/expansion_sprint_v2.md` | V2 expansion sprint plan |
| `archive/merge_review_checklist.md` | Merge review checklist |
| `archive/multi_agent_coordination.md` | Multi-agent coordination plan |
| `archive/progress_report_sprint2.md` | Sprint 2 progress report |
| `archive/scoring_guide_v0.md` | Original scoring guide |

---

## Python files needing attention after Family C sprint

These files are **not being moved** because the Family C sprint team may
depend on them. They should be addressed after the current sprint completes.

| File | Issue |
|------|-------|
| `metajudge/tasks/self_correction.py` | v1 task module, superseded by `self_correction_v2.py`. Needs deprecation header or consolidation. |
| `metajudge/scoring/self_correction_metrics.py` | v1 scoring with outdated damage penalty (0.1 vs current config-driven values). Superseded by `self_correction_v2.py`. |
| `kaggle-package/metajudge/scoring/self_correction_metrics.py` | v1 copy in Kaggle package. Needs v2 replacement before Kaggle submission. |
| `kaggle-package/metajudge/tasks/self_correction.py` | v1 copy in Kaggle package. Same issue. |
