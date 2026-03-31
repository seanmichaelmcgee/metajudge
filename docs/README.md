# docs/ — Document Index

Classification of all documents in this directory. Use this to find the right
document without reading everything.

**Classifications:**
- **Operational** — active reference for current work
- **Background** — useful context and rationale, not execution guidance
- **Historical** — superseded or completed; read only for project history (moved to `archive/`)

---

## Operational

| Document | Purpose |
|----------|---------|
| `family_b_scoring_spec.md` | Canonical Family B scoring reference (UWAA, utility matrix, action F1, AUARC) |
| `family_b_notebook_integration.md` | Family B notebook cell design (Cells 9-15) |
| `item_development_methodology.md` | Item authoring guide for all families |
| `dataset_cleaning_notes.md` | Clean-subset discipline and exclusion criteria |
| `notebook_architecture_memo.md` | Notebook design rationale (A/B surface; will need Family C update) |
| `kaggle_import_guide.md` | How to import datasets into Kaggle |
| `kaggle_upload_guide.md` | How to upload datasets to Kaggle |
| `kaggle_upload_runbook.md` | Step-by-step Kaggle upload procedure |

## Background

These documents provide theoretical grounding and architectural rationale.
They are valuable for understanding *why* decisions were made but should not
be treated as execution instructions for the current sprint.

| Document | Purpose |
|----------|---------|
| `metacognition_assessor_recommendations.md` | Cross-family architecture and two-axis framework rationale |
| `metacognition_literature_report.md` | 80+ paper annotated bibliography |
| `references.bib` | Full reference database |
| `metajudge_program_charter.md` | Overall program goals and scope |
| `family_b_dataset_design.md` | Family B item design rationale |
| `family_b_literature_review.md` | Family B literature survey (68K) |

## Historical (archived)

These documents have been moved to `archive/`. They are superseded by current
code, later planning docs, or completed work. Preserved for project history.

| Document | Why archived |
|----------|-------------|
| `archive/source_framework.md` | Original conceptual foundation; superseded by recommendations memo |
| `archive/bridge_layer_and_minimal_safe_plan.md` | Early bridge layer plan; completed |
| `archive/calibration_v2_refinement_charter.md` | V2 calibration refinement; completed |
| `archive/frontier_agent_team_operating_manual.md` | Agent team manual from earlier sprint; superseded |
| `archive/metacognition_assessor_change_prompt.md` | Family A implementation checklist; completed |
| `archive/metajudge_lean_vnext_iteration_plan.md` | vNext iteration plan; superseded by current code |
| `archive/metajudge_v0_5_2_congruence_review.md` | v0.5.2 congruence review; superseded |
| `archive/metajudge_vnext_orchestrator_brief.md` | Orchestrator brief; superseded |
| `archive/sprint_report_v0.5.1.md` | v0.5.1 sprint report; completed |
| `archive/v0_5_2_lean_orchestrator_brief.md` | v0.5.2 orchestrator brief; superseded |
| `archive/v0_5_5_change_log.md` | v0.5.5 change log; historical |
| `archive/v0_5_5_open_questions.md` | v0.5.5 open questions; resolved |
| `archive/v0_5_5_state_reconciliation.md` | v0.5.5 state reconciliation; resolved |
| `archive/family_b_kickoff_findings.md` | Family B kickoff; completed |
| `archive/family_b_redesign_charter.md` | Family B redesign; completed |

---

## Notes for agents

- For Family C sprint work, the primary planning docs are in `planning/family_c_sprint/`.
- For Family C scoring details, see `config/family_c_scoring.yaml` and `metajudge/scoring/self_correction_v2.py`.
- Do not treat background documents as authoritative for the current sprint without cross-checking against current code and artifacts.
