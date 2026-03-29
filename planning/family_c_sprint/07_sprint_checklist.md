# Family C Sprint: Execution Checklist

**Purpose:** Step-by-step execution plan for the Family C sprint.
Each step has a clear deliverable and dependencies.

---

## Day 1: Foundation

### Step 1: Schema and Scoring Updates
**Dependencies:** None
**Deliverable:** Updated Python modules

- [ ] Update `SelfCorrectionResponse` in `response_schemas.py`:
  - Add optional `revise_decision: Literal["maintain", "revise", "unresolved"]` field
  - Keep backward compatibility with existing fields
- [ ] Update `self_correction_metrics.py`:
  - Add `score_self_correction_item_v2()` per scoring blueprint
  - Add `compute_family_c_headline()` aggregation function
  - Add `build_audit_row()` helper
  - Adjust base scores: damage 0.1→0.05, maintain_correct 0.6→0.70
  - Widen confidence adjustment range to [-0.15, +0.10]
- [ ] Add Family C scoring config to `benchmark_config.yaml`
- [ ] Write tests for new scoring functions in `tests/`

### Step 2: Task Module Refactor
**Dependencies:** Step 1 (schemas)
**Deliverable:** Updated task module with C1/C2 split

- [ ] Refactor `tasks/self_correction.py`:
  - Split `build_correction_prompt()` into `build_c1_turn2_prompt()` and `build_c2_turn2_prompt()`
  - Add challenge template pools for C1 (generic, inspect, reconsider)
  - Add challenge template pools for C2 (contradiction, weak_challenge, peer_hint)
  - Add `score_self_correction_item_v2()` integration
- [ ] Write tests for prompt builders

### Step 3: Seed Dataset Authoring
**Dependencies:** None (parallel with Steps 1-2)
**Deliverable:** `data/family_c/family_c_seed_v1.json`

- [ ] Create `data/family_c/` directory
- [ ] Author 15 C1 items:
  - 5 wrong-to-right (arithmetic, factual, reasoning mix)
  - 5 right-to-right (factual recall, well-known facts)
  - 3 unresolved (genuinely ambiguous or definition-dependent)
  - 2 deceptive-trap (plausible but incorrect challenge)
- [ ] Author 20 C2 items:
  - 5 wrong-to-right (with suggestive evidence)
  - 5 right-to-right (with irrelevant or neutral evidence)
  - 5 weak-challenge (with misleading evidence)
  - 3 unresolved (with ambiguous evidence)
  - 2 deceptive-trap (with plausible but wrong evidence)
- [ ] Verify all gold answers are unambiguous and machine-gradeable
- [ ] Create `data/family_c/family_c_manifest.json`

---

## Day 2: Integration and Dry Run

### Step 4: Notebook Scaffolding
**Dependencies:** Steps 1-3
**Deliverable:** `notebooks/family_c_analysis.ipynb`

- [ ] Create analysis notebook with cell structure per `04_task_architecture.md`
- [ ] Implement C1 task function (decorated, with `chats.new()` and two turns)
- [ ] Implement C2 task function (decorated, with evidence in turn 2)
- [ ] Add data loading with manifest filtering
- [ ] Add audit DataFrame builder
- [ ] Add headline score computation cells
- [ ] Add diagnostic output cells (correction rate, damage rate, confidence dynamics)

### Step 5: Dry Run (Gate 0)
**Dependencies:** Step 4
**Deliverable:** Gate 0 pass/fail

- [ ] Run 3-5 items against gemini-2.5-flash
- [ ] Verify: structured output valid on both turns
- [ ] Verify: grading produces correct results
- [ ] Verify: scoring pipeline produces expected values
- [ ] Verify: audit row is complete and correct
- [ ] Fix any issues found
- [ ] **Gate 0 decision: proceed or fix**

### Step 6: Smoke Test (Phase 1)
**Dependencies:** Gate 0 pass
**Deliverable:** Smoke test audit CSV

- [ ] Run full seed set (35 items) against gemini-2.5-flash
- [ ] Review audit CSV for anomalies
- [ ] Identify grading ambiguities → quarantine
- [ ] Check score distribution — not all 0 or all 1
- [ ] Update manifest with any quarantined items
- [ ] **Gate 0.5 decision: proceed to full panel or fix items**

---

## Day 3: Full Evaluation

### Step 7: 5-Model Panel Run (Phase 2)
**Dependencies:** Step 6 pass
**Deliverable:** 10 audit CSVs (C1 + C2 × 5 models)

- [ ] Run clean C1 items against all 5 models
- [ ] Run clean C2 items against all 5 models
- [ ] Collect audit CSVs
- [ ] Monitor budget (should be well within limits)

### Step 8: Analysis and Validation
**Dependencies:** Step 7
**Deliverable:** Validation report

- [ ] Compute headline scores per model per subfamily
- [ ] Compute diagnostic submetrics (correction rate, damage rate, etc.)
- [ ] Run bootstrap CIs for pairwise model comparisons
- [ ] Compute rank correlation with A/B scores
- [ ] Run item discrimination analysis
- [ ] Run bridge analysis (monitoring → control coupling)
- [ ] Produce stratum-level breakdowns
- [ ] Flag suspect items for quarantine review

### Step 9: Audit and Clean-Set Update
**Dependencies:** Step 8
**Deliverable:** Updated manifest, quarantine decisions

- [ ] Review flagged items
- [ ] Update `family_c_manifest.json` with exclusions/quarantines
- [ ] Verify ≥ 25 items remain in clean set (12+ C1, 15+ C2)
- [ ] **Gate 1 decision: does Family C discriminate?**

### Step 10: Documentation
**Dependencies:** Step 9
**Deliverable:** Summary findings

- [ ] Document headline findings in analysis notebook summary cell
- [ ] Record what worked, what didn't, what surprised
- [ ] List items that need replacement or improvement
- [ ] Produce expansion recommendations

---

## Post-Sprint: Decision Points

### If Gate 1 passes:
- Proceed to expansion sprint (author 25-45 additional items)
- Target: 60-80 total items, 50+ clean
- Follow adversarial expansion strategy from `02_item_design.md`

### If Gate 1 fails:
- Diagnose root cause (see `06_risks_and_gates.md` failure modes)
- Consider:
  - Redesigning items (if grading/design issues)
  - Reducing scope to C2-only (if C1 shows zero variance)
  - Deferring Family C (if fundamental measurement problems)

### If Gate 1 is ambiguous:
- Run a second evaluation with revised items
- Do not promote to benchmark surface until clear

---

## Quick Reference: File Checklist

| File | New/Update | Sprint Day |
|------|-----------|------------|
| `metajudge/schemas/response_schemas.py` | Update | Day 1 |
| `metajudge/scoring/self_correction_metrics.py` | Update | Day 1 |
| `metajudge/tasks/self_correction.py` | Update | Day 1 |
| `config/benchmark_config.yaml` | Update | Day 1 |
| `tests/test_self_correction_scoring.py` | New | Day 1 |
| `data/family_c/family_c_seed_v1.json` | New | Day 1 |
| `data/family_c/family_c_manifest.json` | New | Day 1 |
| `notebooks/family_c_analysis.ipynb` | New | Day 2 |
| Audit CSVs in outputs/ | New | Day 3 |
| Manifest updates | Update | Day 3 |
