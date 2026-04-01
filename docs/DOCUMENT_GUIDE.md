# MetaJudge-AGI: Document Guide

> **Purpose:** Single entry-point for agents and contributors to navigate 100+ documents.
> **Read time:** ~10 minutes. **Last updated:** 2026-04-01 (v0.7.2)

---

## How to use this guide

Documents are classified into five tiers:

| Tier | Label | Meaning | Agent action |
|------|-------|---------|-------------|
| **G** | Governance | Non-negotiable principles; wins all conflicts | Must follow |
| **A** | Authoritative | Currently governs decisions in its scope | Must follow within scope |
| **R** | Reference | Valuable context, not binding | Read for understanding |
| **H** | Historical | Superseded or completed | Read only if tracing prior decisions |
| **O** | Operational | Runbooks, checklists, execution prompts | Follow when executing that task |

When documents conflict, Tier G > A > R. Within the same tier, SOUL.md's priority table (§ Governing design documents) breaks ties.

---

## 1. Governance & Project Identity (G)

| Document | Path | Purpose |
|----------|------|---------|
| **SOUL.md** | `SOUL.md` | Non-negotiable principles, two-axis framework, priority table for all other docs |
| **CLAUDE.md** | `CLAUDE.md` | Dev instructions, hard rules, package structure, dev commands |
| **README.md** | `README.md` | Public-facing overview: version, item counts, sweep results, composite method |

**Read order:** SOUL.md → CLAUDE.md → this guide → task-specific docs.

---

## 2. Theoretical Foundations (A/R)

These documents establish *why* MetaJudge measures what it measures, grounded in cognitive psychology and LLM evaluation literature.

| Tier | Document | Path | Scope |
|------|----------|------|-------|
| **A** | Metacognition assessor recommendations | `docs/metacognition_assessor_recommendations.md` | Cross-family: two-axis framework, family specs, architectural guidance |
| **A** | Scientific constraints (FC) | `planning/family_c_sprint/01_scientific_constraints.md` | Family C non-negotiable design principles from theory |
| **A** | Theoretical grounding (FC) | `planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md` | Theory→design translation: damage:gain ratio, detection as bottleneck, 7 research questions |
| **R** | Literature report (metacognition) | `docs/metacognition_literature_report.md` | 80+ paper annotated bibliography across all families |
| **R** | Literature report (FC) | `planning/family_c_sprint/20_family_c_literature_report.md` | 6 decades of self-correction literature: neural roots → LLM frontier |
| **R** | Reference database | `docs/references.bib` | BibTeX entries for all cited works |

**Theory → Implementation:** Nelson & Narens (1990) → `docs/metacognition_assessor_recommendations.md` → `planning/family_c_sprint/01_scientific_constraints.md` → `planning/family_c_sprint/02_item_design.md` → `data/family_c/SCHEMA.md` → items built.

---

## 3. Composite & Statistical Methodology (A/R)

These documents establish *how* family-level scores combine into MetaScore and how to quantify uncertainty.

| Tier | Document | Path | Scope |
|------|----------|------|-------|
| **A** | Composite construction (step 2) | `docs/stats/composite_construction_step2.md` | Equal-weight z-score method, Dirichlet stability, Hasse partial order, Haberman PRMSE, Friedman test — with implementation code |
| **R** | Composite methods survey | `docs/stats/Composite Rankings from Heterogeneous Sub-Metrics_ An Annotated Methods Survey for MetaJudge.md` | Theoretical foundations: Dawes 1979, Davis-Stober 2011, OECD handbook, 8 candidate methods evaluated |
| **A** | Stats backgrounder (A+B) | `docs/stats/stats_backgrounder_families_ab.md` | Paired bootstrap CIs, McNemar, permutation tests, Holm correction — methodology for Families A+B |
| **R** | Power analysis (FC) | `docs/stats/power_analysis_family_c.md` | SC rate CIs, T2-T1 bootstrap, McNemar pairwise — statistical power assessment |
| **O** | Reproducibility log | `docs/stats/stats_reproducibility_log.md` | Seeds (42), package versions, data checksums for reproducibility |
| **R** | Stats review prompt | `docs/stats/stats_review_prompt.md` | Research agent prompt that produced the composite methodology (historical context) |

**Key finding:** MetaScore = mean(z_A, z_B, z_C). Family C α ≈ 0.35 < 0.55 Haberman threshold — no standalone subscore value, but reshuffles composite ranking.

---

## 4. Family Design & Scoring Specs (A, per family)

### Family A — Confidence Calibration

| Tier | Document | Path |
|------|----------|------|
| **A** | Scoring plan | `planning/scoring_plan.md` |
| **A** | Benchmark config | `config/benchmark_config.yaml` |

**Implements:** `metajudge/scoring/calibration_metrics.py`, `metajudge/scoring/grading_v2.py`

### Family B — Selective Abstention

| Tier | Document | Path |
|------|----------|------|
| **A** | Scoring spec | `docs/family_b_scoring_spec.md` |
| **R** | Dataset design | `docs/family_b_dataset_design.md` |
| **R** | Notebook integration | `docs/family_b_notebook_integration.md` |

**Implements:** `metajudge/scoring/abstention_metrics.py`

### Family C — Self-Correction

| Tier | Document | Path |
|------|----------|------|
| **A** | Scoring blueprint | `planning/family_c_sprint/03_scoring_blueprint.md` |
| **A** | Item design | `planning/family_c_sprint/02_item_design.md` |
| **A** | Item schema | `data/family_c/SCHEMA.md` |
| **A** | Scoring config | `config/family_c_scoring.yaml` |
| **A** | Design review v2 | `planning/family_c_sprint/21_family_c_design_review_v2.md` |

**Implements:** `metajudge/scoring/self_correction_v2.py`, `metajudge/tasks/self_correction_v2.py`

**Design → Build trace:** `03_scoring_blueprint.md` → `config/family_c_scoring.yaml` → `metajudge/scoring/self_correction_v2.py` (classify_transition, score_item, build_audit_row) → `metajudge/tasks/self_correction_v2.py` (prompts, parse_answer_confidence, resolve_t2_answer) → notebooks.

---

## 5. Item Development Methodology (R)

| Tier | Document | Path | Scope |
|------|----------|------|-------|
| **R** | Item development methodology | `docs/item_development_methodology.md` | A+B authoring workflows: adversarial search, quality gates, contamination mgmt |
| **A** | FC design review v2 | `planning/family_c_sprint/21_family_c_design_review_v2.md` | Theory→engineering translation for Family C |
| **R** | FC executive roadmap | `planning/family_c_sprint/00_executive_roadmap.md` | Decision rationale for building Family C next |
| **R** | FC risks & gates | `planning/family_c_sprint/06_risks_and_gates.md` | Failure modes, decision gates framework |

**Build → Validate trace:** `02_item_design.md` → `scripts/generate_item_v2.py` (author→adversary→canary→frontier) → `data/family_c/family_c_c1_candidates.json` → `scripts/sweep_v2.py` → `outputs/audit_family_c_summary.md`.

---

## 6. Agent Architecture & Orchestration (O/R)

| Tier | Document | Path | Scope |
|------|----------|------|-------|
| **O** | Orchestrator grounding | `orchestrator/GROUNDING.md` | Session startup protocol, decision framework, anti-drift rules, recovery protocol |
| **O** | Agent roster | `orchestrator/AGENTS.md` | Permanent and ad-hoc agent roles, dispatch patterns |
| **R** | Decision log | `orchestrator/DECISION_LOG.md` | Chronological record of orchestrator decisions with rationale |
| **H** | Pilot orchestrator instructions | `planning/family_c_sprint/13_pilot_orchestrator_instructions.md` | Agent team instructions for v0.6.1 pilot (completed) |
| **H** | Resume-safe hardening prompt | `planning/family_c_sprint/15_resume_safe_hardening_orchestrator_prompt.md` | Orchestrator prompt for v0.6.2 hardening (completed) |
| **H** | Next-phase orchestrator prompt | `planning/family_c_sprint/16_next_phase_orchestrator_prompt.md` | Post-correction hardening orchestrator (completed) |

**Key pattern:** The orchestrator reads `GROUNDING.md` → checks `STATE.json` → reads `SOUL.md` → checks `git log` → dispatches work to agents defined in `AGENTS.md`.

---

## 7. Validation & Audit Trail (A/R)

| Tier | Document | Path | Scope |
|------|----------|------|-------|
| **A** | Family C audit | `outputs/audit_family_c_summary.md` | v0.7.1 audit: 6 FLIP_TO_WRONG, 2 tolerance issues, 4 exclusions |
| **A** | Family A+B audit | `outputs/audit_family_ab_summary.md` | 968 rows: 66 FLIP_TO_CORRECT, verbose-answer adjudication, gold drift |
| **A** | Gold answer justifications | `outputs/metajudge_v0551_gold_answer_justifications.md` | Per-item defensibility for 201 items (117 Cal + 84 Abs) |
| **R** | FC Phase 6 analysis | `outputs/family_c/sweep_v2_phase5/phase6_full_analysis.md` | Bootstrap CIs, transition matrices, confidence dynamics (56 items x 4 models) |
| **R** | FC sweep analysis (v0.6.2) | `outputs/family_c/sweep_analysis_v062.md` | Original 5-model sweep with grading corrections |
| **R** | FC hardening report | `outputs/family_c/hardening_report_v062.md` | Item generation batches, validation, evidence calibration |
| **R** | V2 validation report | `outputs/audit_v2_validation_report.md` | Comprehensive v2 validation across families |
| **H** | FC pilot report | `outputs/family_c/pilot_report_v061.md` | v0.6.1 pilot (superseded by v0.6.2+) |

**Validate → Score trace:** `outputs/audit_family_c_summary.md` → tolerance fixes in `kaggle-dataset-v3/adjudication_registry.json` → confirmation detection in `metajudge/tasks/self_correction_v2.py` → exclusions in `kaggle-dataset-v3/clean_subset_manifest.json` → re-run notebooks.

---

## 8. Notebook & Kaggle Integration (O)

| Tier | Document | Path | Scope |
|------|----------|------|-------|
| **O** | Kaggle upload runbook | `docs/kaggle_upload_runbook.md` | Step-by-step upload and submission process |
| **R** | Notebook architecture | `docs/notebook_architecture_memo.md` | Two-notebook split decision and cell architecture |
| **R** | Program charter | `docs/metajudge_program_charter.md` | Governing execution charter for long-running agent teams |
| **H** | FC notebook integration plan | `planning/family_c_sprint/24_notebook_integration_v3_plan.md` | v3 notebook build plan (completed — 9 sub-phases) |
| **H** | FC notebook integration prompt | `planning/family_c_sprint/23_family_c_notebook_integration_prompt.md` | Original FC-only notebook plan (superseded by plan 24) |

**Current notebooks:**
- `notebooks/metajudge_narrative_v3.ipynb` — v3.2, 25 cells, all 3 families + z-score composite
- `notebooks/metajudge_benchmark_v3.ipynb` — v3.1, 13 cells, official Kaggle submission

---

## 9. Sprint Execution & Checkpoints (H)

These documents tracked sprint execution and are now completed. Read only for understanding the development history.

| Document | Path | Status |
|----------|------|--------|
| Sprint checklist | `planning/family_c_sprint/07_sprint_checklist.md` | Completed |
| Sprint v2 checkpoint | `planning/family_c_sprint/checkpoint_sprint_v2_phase6.md` | All 6 phases done |
| Hardening checkpoint | `planning/family_c_sprint/checkpoint_status_v062.md` | Phase 2 complete |
| Grading freeze note | `planning/family_c_sprint/grading_freeze_note_phase1.md` | Locked |
| v0.5.5.1 revalidation | `planning/family_c_sprint/10_v0551_revalidation.md` | Completed |
| Validation promotion | `planning/family_c_sprint/12_validation_promotion.md` | Completed |
| Integration notes | `planning/family_c_sprint/11_integration_notes.md` | Completed |
| Sprint v2 state memo | `planning/family_c_sprint/sprint_v2_state_memo.md` | Recovery reference |
| Hardening state memo | `planning/family_c_sprint/state_memo_next_phase.md` | Recovery reference |
| Results-grounded amendments | `planning/family_c_sprint/08_results_grounded_amendments.md` | Applied |
| Family B grading fix | `planning/family_b_grading_fix_plan.md` | Applied |
| SDK verification | `planning/verification/kaggle_sdk_verification.md` | Complete |
| Research prompts | `planning/family_c_sprint/09_*, 17_*, 18_*, 19_*` | Completed — produced literature reports |

---

## 10. Historical & Superseded

`planning/archive/` contains 11 documents from early architecture, scoring guides, and expansion sprints (v0.1–v0.4 era). `planning/archive/calibration_v3/` contains 18 documents from the Family A item generation pipeline (adversarial search, batch summaries, generator prompts, verification protocols). `docs/archive/` contains superseded Family B literature and early design docs.

These trace the evolution of ideas but should not be followed by current agents. All have been superseded by the documents listed above.

---

## The Intellectual Pipeline

```
THEORY                          DESIGN                          BUILD
─────                           ──────                          ─────
Nelson & Narens (1990)    →  metacognition_assessor_         →  metajudge/scoring/
Koriat & Goldsmith (1996)    recommendations.md                 calibration_metrics.py
Huang et al. (ICLR 2024) →  01_scientific_constraints.md    →  abstention_metrics.py
Burnell et al. (2026)     →  02_item_design.md               →  self_correction_v2.py
                          →  03_scoring_blueprint.md          →  tasks/self_correction_v2.py
                          →  family_b_scoring_spec.md         →  grading_v2.py
                          →  scoring_plan.md

VALIDATE                        SCORE                           COMPOSITE
────────                        ─────                           ─────────
scripts/sweep_v2.py       →  audit_family_c_summary.md      →  composite_construction_
scripts/audit_v2_*.py     →  audit_family_ab_summary.md        step2.md
generate_item_v2.py       →  gold_answer_justifications.md  →  MetaScore = mean(z_A,
                          →  tolerance/exclusion fixes          z_B, z_C)
                                                             →  notebooks/narrative_v3
                                                             →  notebooks/benchmark_v3
```

### Three end-to-end traces

**Family A (Calibration):**
`docs/metacognition_assessor_recommendations.md` → `planning/scoring_plan.md` → `metajudge/scoring/calibration_metrics.py` + `grading_v2.py` → `data/metajudge_benchmark_v1.json` (117 items) → `outputs/audit_family_ab_summary.md` → notebook Cell 5 (sweep) → Cell 11 (leaderboard)

**Family B (Abstention):**
`docs/metacognition_assessor_recommendations.md` → `docs/family_b_scoring_spec.md` → `metajudge/scoring/abstention_metrics.py` → `data/family_b_pilot_v2.json` (84 items) → `outputs/audit_family_ab_summary.md` → notebook Cell 6 (sweep) → Cell 13 (leaderboard)

**Family C (Self-Correction):**
`planning/family_c_sprint/01_scientific_constraints.md` → `03_scoring_blueprint.md` → `metajudge/scoring/self_correction_v2.py` + `tasks/self_correction_v2.py` → `data/family_c/` (55 items, 51 clean) → `outputs/audit_family_c_summary.md` → notebook Cell 8 (sweep) → Cell 15 (leaderboard) → Cell 20 (composite analysis)

---

## Quick Reference: What to Read for Common Tasks

| Task | Read these |
|------|-----------|
| **Understand the project** | SOUL.md → README.md → this guide |
| **Add/modify items** | `02_item_design.md` → `data/family_c/SCHEMA.md` → `docs/item_development_methodology.md` |
| **Change scoring** | `03_scoring_blueprint.md` → `config/family_c_scoring.yaml` → `metajudge/scoring/self_correction_v2.py` |
| **Update composite** | `docs/stats/composite_construction_step2.md` → notebook Cell 19-20 |
| **Run on Kaggle** | `docs/kaggle_upload_runbook.md` → `kaggle-dataset-v3/` + `kaggle-package-v3/` |
| **Audit results** | `outputs/audit_family_c_summary.md` → `outputs/audit_family_ab_summary.md` |
| **Understand statistics** | `docs/stats/stats_backgrounder_families_ab.md` → `docs/stats/composite_construction_step2.md` |
| **Orchestrate agents** | `orchestrator/GROUNDING.md` → `orchestrator/AGENTS.md` |
| **Trace a design decision** | `orchestrator/DECISION_LOG.md` → relevant sprint checkpoint |
