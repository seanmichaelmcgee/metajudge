# Phase Plan — MetaJudge-AGI

## Timeline: 14-21 Days (Source: Implementation Plan)

---

## Phase 0: Bootstrap (Day 0) ✅ COMPLETE

**Goal:** Project infrastructure ready for development.

**Deliverables:**
- [x] Git repository initialized
- [x] Python virtual environment
- [x] Directory structure
- [x] Dependency manifest
- [x] Configuration files
- [x] Placeholder Python modules
- [x] README stub
- [x] Agent team plan
- [x] Phase plan
- [x] Prototype dataset
- [x] Source documents copied to project

**Critical path:** Unblocks all subsequent work.

---

## Phase 1: Specification & Schema (Days 1-3)

**Source:** Implementation Plan §Phase 1, Framework §2-6

**Goal:** Freeze all schemas, finalize task taxonomy, document scoring rules.

**Subtasks:**
1. Review and finalize operational definition of metacognition (Framework §2)
2. Finalize five sub-benchmark specifications
3. Freeze response schemas (all five families + metadata)
4. Define scoring weights and document rationale
5. Define where deterministic grading ends and judge-model grading begins (Framework §13)
6. Write benchmark charter document
7. Validate schemas with Pydantic tests

**Deliverables:**
- Frozen `metajudge/schemas/response_schemas.py`
- `docs/benchmark_charter.md`
- `docs/scoring_explanation.md`
- `tests/unit/test_schemas.py`
- Decision record: scoring boundaries

**Agents:** Schema Agent (lead), Scoring Agent (consult), Orchestrator

**Dependencies:** Phase 0 complete
**Parallelizable with:** Nothing (foundational)

---

## Phase 2: Dataset Construction (Days 3-7)

**Source:** Implementation Plan §Phase 2, Framework §5.1-5.5 (data design)

**Goal:** Author 500-1500 task items across all five families.

**Subtasks:**
1. Create task authoring guide with rules per family
2. Author calibration items (easy/medium/hard/deceptive)
3. Author abstention items (answerable/underspecified/unreliable)
4. Author self-correction items (wrong-first AND correct-first)
5. Author source-awareness items (mixed provenance)
6. Author strategy-adaptation items (multi-strategy problems)
7. Assign hidden metadata (difficulty, optimal action, source type, etc.)
8. Create family/variant linkages for anti-gaming
9. Validate item counts and tier distributions
10. Create public/private/pilot splits

**Deliverables:**
- `data/raw_tasks/*.json` — all five families
- `data/splits/` — public, private, pilot
- `docs/task_authoring_guide.md`
- Item distribution report

**Agents:** Dataset Agent (lead), Schema Agent (validation), Anti-Gaming Agent (variant design)

**Dependencies:** Phase 1 (frozen schemas)
**Parallelizable with:** Phase 3 (can start scoring stubs during dataset authoring)

---

## Phase 3: Task Implementation (Days 5-10)

**Source:** Implementation Plan §Phase 3, Framework §9.2

**Goal:** Implement task functions, prompt builders, and evaluation logic.

**Subtasks:**
1. Implement task runners for each family (calibration, abstention, self-correction, source, strategy)
2. Implement prompt builders with anti-gaming variation support
3. Implement response parsing and validation
4. Implement single-item runners
5. Implement batch evaluation over DataFrames
6. Add multi-turn interaction for self-correction and strategy tasks
7. Write integration tests with prototype data

**Deliverables:**
- Complete `metajudge/tasks/*.py`
- `metajudge/evaluation/runner.py`
- `tests/integration/test_runner.py`

**Agents:** Scoring Agent (lead), Schema Agent (schema enforcement), Integration Agent (Kaggle patterns)

**Dependencies:** Phase 1 (schemas), Phase 2 (partial — prototype data sufficient)
**Parallelizable with:** Phase 2 (dataset authoring)

---

## Phase 4: Scoring System (Days 7-12)

**Source:** Implementation Plan §Phase 4, Framework §7

**Goal:** Complete scoring implementation for all dimensions and composite.

**Subtasks:**
1. Finalize calibration metrics (Brier, ECE, overconfidence, accuracy-by-bucket)
2. Finalize abstention metrics (utility matrix, risk-coverage, abstention precision)
3. Finalize self-correction metrics (revision quality, confidence direction, efficiency)
4. Finalize source-awareness metrics (label accuracy, span alignment, unsupported penalty)
5. Finalize strategy metrics (selection accuracy, diversity, consistency)
6. Implement composite score aggregation with design principle verification
7. Write comprehensive unit tests for all scoring functions
8. Validate four composite design principles (Framework §7.3)

**Deliverables:**
- Complete `metajudge/scoring/*.py`
- `tests/unit/test_scoring.py`
- Composite score validation report

**Agents:** Scoring Agent (lead), QA Agent (testing)

**Dependencies:** Phase 1 (schemas), Phase 2 (test data)
**Parallelizable with:** Phase 3 (task implementation)

---

## Phase 5: Anti-Gaming Hardening (Days 9-14)

**Source:** Implementation Plan §Phase 5, Framework §8

**Goal:** Implement all eight anti-gaming countermeasures.

**Subtasks:**
1. Generate prompt paraphrase variants (§8.2.3)
2. Add decoy difficulty cues (§8.2.4)
3. Verify symmetric correction setup (§8.2.5)
4. Design source-label adversarial items (§8.2.6)
5. Create cross-template evaluation splits (§8.2.7)
6. Implement verbosity independence check (§8.2.8)
7. Verify hidden optimal-action class distribution (§8.2.2)
8. Run anti-gaming validation suite
9. Generate hardened dataset variants

**Deliverables:**
- Complete `metajudge/anti_gaming/perturbations.py`
- `data/processed_tasks/*_hardened.json`
- `planning/verification/anti_gaming_report.md`

**Agents:** Anti-Gaming Agent (lead), Dataset Agent (variant generation), QA Agent (validation)

**Dependencies:** Phase 2 (datasets), Phase 4 (scoring)
**Parallelizable with:** Phase 4 (scoring), Phase 6 (Kaggle integration start)

---

## Phase 6: Kaggle Integration (Days 12-16)

**Source:** Implementation Plan §Phase 6, Framework §9, Notebook Sketch

**Goal:** Build submission-ready Kaggle notebook.

**Subtasks:**
1. Verify kaggle_benchmarks SDK in live environment
2. Wrap all five task families in @kbench.task decorators
3. Implement .evaluate() dataset evaluation
4. Implement structured output support
5. Implement multi-turn interaction for self-correction and strategy tasks
6. Add assertion logic per task
7. Implement aggregate metrics computation
8. Implement result export
9. Verify benchmark registration/export mechanism
10. Verify model availability in competition environment

**Deliverables:**
- `notebooks/kaggle_submission.py`
- `planning/verification/kaggle_sdk_verification.md`
- Updated `metajudge/evaluation/kaggle_integration.py`

**Agents:** Integration Agent (lead), Schema Agent (consult), Scoring Agent (consult)

**Dependencies:** Phases 3-5 (task implementation, scoring, anti-gaming)
**Parallelizable with:** Phase 5 (anti-gaming) — can start notebook structure early

**CRITICAL UNKNOWNS:** (See verification log)
- Exact SDK API surface
- Model list
- Export/selection mechanism
- Notebook magics

---

## Phase 7: Validation & Pilot (Days 14-18)

**Source:** Implementation Plan §Phase 7, Framework §14

**Goal:** Validate benchmark on multiple models, verify all four validation axes.

**Subtasks:**
1. Run benchmark on multiple models via Kaggle
2. Check construct validity (§14.1): does it measure metacognition, not reasoning/verbosity?
3. Check discriminative validity (§14.2): do models separate meaningfully?
4. Check robustness (§14.3): do prompt variations preserve ranking?
5. Check anti-gaming robustness (§14.4): do cheap strategies fail?
6. Inspect subscore variation across models
7. Identify poorly discriminating modules
8. Tune scoring weights based on empirical results
9. Conduct ablation analysis

**Deliverables:**
- Pilot analysis notebook
- Validation report (all four axes)
- Refined benchmark v1.1 (if needed)
- Weight tuning rationale

**Agents:** QA Agent (lead), Scoring Agent (analysis), Integration Agent (model runs)

**Dependencies:** Phase 6 (working Kaggle notebook)
**Parallelizable with:** Phase 8 (documentation can start during pilot)

---

## Phase 8: Final Submission (Days 18-21)

**Source:** Implementation Plan §Phase 8, Framework §10-11

**Goal:** Polish and submit competition entry.

**Subtasks:**
1. Write competition writeup (Framework §10, Task 9)
2. Document anti-gaming measures
3. Show illustrative examples
4. Discuss limitations honestly (Framework §15)
5. Final notebook cleanup
6. Final dataset freeze
7. Confirm runtime and reproducibility
8. Submit to Kaggle

**Deliverables:**
- `docs/competition_writeup.md`
- Final `notebooks/kaggle_submission.py`
- `docs/limitations.md`
- Submission confirmation

**Agents:** Documentation Agent (lead), Integration Agent (submission), QA Agent (final check)

**Dependencies:** Phase 7 (validation complete)
**Parallelizable with:** Nothing (final phase)

---

## Critical Path

```
Phase 0 → Phase 1 → Phase 2 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
                          ↘ Phase 3 ↗
```

The critical path runs through dataset construction (Phase 2) because most downstream work depends on having task items. Phase 3 (task implementation) can partially overlap with Phase 2 using prototype data.

## Key Milestones

| Day | Milestone |
|-----|-----------|
| 0   | Repository bootstrapped, agent team defined |
| 3   | Schemas frozen, benchmark charter written |
| 7   | Initial dataset (500+ items) complete |
| 10  | Task runners and scoring working locally |
| 14  | Anti-gaming hardened, Kaggle notebook draft |
| 18  | Pilot validation complete, v1.1 refined |
| 21  | Submission ready |
