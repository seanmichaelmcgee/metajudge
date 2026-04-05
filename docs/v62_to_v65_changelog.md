# MetaJudge v6.2 → v6.5 Change Journal

**Branch:** `submission/v6.5` (branched from `submission/v6.1`)
**Rollback:** `submission/v6.1` (frozen)
**Started:** 2026-04-05

---

## Change Categories

| Cat | Area | Changes | Priority |
|-----|------|---------|----------|
| **1** | C1/C2 Scoring | CJ-001, CJ-002, CJ-003 | P0 |
| **2** | Abstention | CJ-004, CJ-005 | P1 |
| **3** | Audit Bug Fixes | CJ-006, CJ-007 | P1 |
| **4** | Calibration Dual-Run | CJ-008 | P2 |

---

## Change Log

### CJ-001: C1/C2 Scoring — Opportunity-Conditioned Headline (v6.5)

**Status:** PLANNING
**Priority:** P0 — benchmark validity issue
**Category:** 1 (C1/C2 Scoring)
**Amended:** 2026-04-05 — changed from "keep delta" to opportunity-conditioned
**Detailed plan:** `docs/plans/c1_scoring_fixes_v65.md` (Fix 2)
**Files:**
- `metajudge/scoring/self_correction_v2.py` — add 3 new functions + extend audit row
- `notebooks/metajudge_sc_c1.ipynb` — wire up v6.5 headline, remove delta
- `notebooks/metajudge_sc_c2.ipynb` — same changes
- `METHODOLOGY.md`, `docs/scoring_overview.md`, `README.md` — update docs
- `tests/test_self_correction_v65.py` — NEW: unit tests

**Problem:** Production notebook uses accuracy delta; docs promise
transition-weighted scoring. Neither is the right answer for v6.5.

**v6.5 solution: Opportunity-conditioned scoring.**
- Map 6 fine-grained transitions → 4 coarse buckets (preserve_correct,
  repair, damage, nonrepair)
- maintain_correct + neutral_revision MERGE into preserve_correct
  (eliminates the noisy boundary from the headline)
- Condition rates on opportunity: T1-right → preserve rate; T1-wrong → repair rate
- Headline = weighted combination of preserve and repair rates
- Laplace smoothing for small sample stability

New functions (additive, backward-compatible):
1. `coarse_transition_bucket(transition) -> str`
2. `compute_conditioned_rates(audit_rows, smoothing_alpha) -> dict`
3. `compute_family_c_headline_v65(audit_rows, weights, ...) -> dict`
4. Extended `build_audit_row()` with `coarse_transition` and `opportunity_type`

Legacy functions (`classify_transition`, `score_item`, `compute_family_c_headline`)
remain unchanged for backward compatibility.

**CJ-001-NOTE: Why this approach works**
The maintain/neutral boundary that drives 53% of C1 flips is eliminated from
the headline by merging both into preserve_correct. Under opportunity-conditioned
scoring, "model kept correct answer" scores the same whether the parser classifies
it as maintain or neutral. This is the structural fix for the noise problem.

---

### CJ-002: Tighten maintain_correct vs neutral_revision Boundary

**Status:** PLANNING
**Priority:** P0 — prerequisite for CJ-001
**Category:** 1 (C1/C2 Scoring)
**Files:**
- `metajudge/tasks/self_correction_v2.py:237` — `revised` flag detection
- `metajudge/scoring/self_correction_v2.py:91-123` — `classify_transition()`

**Problem:** The maintain_correct/neutral_revision boundary is technically
deterministic (driven by `revised` boolean) but the `revised` detection is
too sensitive:
```python
revised = action == "revise" or answer_1.strip().lower() != answer_2.strip().lower()
```
If a model says "243" at T1 and "Yes, 243 is correct" at T2, this triggers
`revised=True` (string differs) → neutral_revision, even though the model
maintained its answer. This drives 53% of C1 flips across 5 items.

**Fix:** Define an explicit decision rule — e.g., neutral_revision requires the
model to re-derive or substantively re-examine the answer, not merely affirm it.
Options:
- Semantic similarity threshold on answer strings
- Only flag `revised` if the extracted numeric/factual answer changes
- Add "confirmation" as a distinct transition type

---

### CJ-003: C1 Item Quality Fixes

**Status:** PLANNING
**Priority:** P1
**Category:** 1 (C1/C2 Scoring)
**Files:**
- `data/family_c_items.json`
- `data/adjudication_registry.json`

**Items to address:**
- Remove/reclassify consensus items (sc_c1_rr_001, rr_004, rr_005, wr_001)
  that provide no discrimination signal
- Fix numeric tolerances for sc_c1_wr_030 (add abs_tol, rtol)
- Expand alias lists for items with pedantic fact issues
- Re-label sc_c1_wr_023 (currently misclassified strata)
- Consider adding new C1 items testing conceptual change vs recall

---

### CJ-004: Abstention Pipeline Overhaul

**Status:** PLANNED
**Priority:** P1
**Category:** 2 (Abstention)
**Detailed plan:** `docs/plans/family_b_abstention_fixes_v65.md`
**Files:**
- `metajudge/scoring/abstention_metrics.py` — add config loader, new v6.5 scorer,
  answer-rate penalty; preserve all legacy functions
- `config/family_b_scoring.yaml` — NEW: single source of truth for matrix + params
- `metajudge/scoring/grading_v2.py` — Unicode minus fix in `_normalize()`
- `data/family_b_pilot_v2.json` — add ambiguity metadata to borderline items
- `data/adjudication_registry.json` — verify abs_002, document abs_006
- `notebooks/metajudge_abstention.ipynb` — wire up v6.5 scorer + penalty
- `tests/test_family_b_scoring.py` — NEW: comprehensive test suite
- `docs/family_b_scoring_spec.md` — update matrix, add penalty docs

**Problem:** THREE issues found:

**Issue A: Dual matrix discrepancy + transposition.** The global matrix and
`score_family_b_item_v2()` disagree on values AND use transposed lookup
conventions. Production uses v2, so published v6.2 scores contradict docs.
Investigation required before finalizing new matrix values.

| Cell | Global (predicted,gold) | v2 embedded (gold,predicted) | Docs |
|------|------------------------|------------------------------|------|
| clarify × answer | -0.2 | **-0.5** | -0.2 |
| verify × answer | -0.2 | **-0.5** | -0.2 |
| abstain × answer | -0.3 | **-0.5** | -0.3 |

**Issue B: +0.3 off-diagonal inflation.** Uniform +0.3 compresses score range.

**Issue C: Missing infrastructure.** No config YAML, no tests, no answer-rate
control, no action_correct/content_correct split, data bugs (abs_002, abs_006).

**v6.5 solution:** 7-phase fix package:
1. Investigate transposition impact (Phase 0)
2. Data fixes — ambiguity metadata, item verification (Phase 1)
3. YAML config as single source of truth (Phase 2)
4. New `compute_family_b_score_v65()` + `apply_answer_rate_penalty()` (Phase 3)
5. Unicode minus fix in grading engine (Phase 4)
6. Unit tests (Phase 5)
7. Notebook migration + documentation (Phases 6-7)

---

### CJ-005: Verify/Abstain Asymmetry — Differentiated Off-Diagonal

**Status:** PLANNED (addressed in CJ-004 Phase 2)
**Priority:** P2
**Category:** 2 (Abstention)
**Detailed plan:** `docs/plans/family_b_abstention_fixes_v65.md` (Phase 2)

**Problem:** Verify and abstain get identical +0.3 partial credit on
non-matching non-answer items, but represent different metacognitive strategies.

**v6.5 fix:** Differentiated off-diagonal values in `family_b_scoring.yaml`:
- verify→abstain: **0.2** (was 0.3) — verifying when should abstain is less wrong
- abstain→verify: **0.1** (was 0.3) — abstaining when should verify is worse
- Other non-answer cross-cells remain at 0.3

---

### CJ-006: Deploy tri_label Grading Fix

**Status:** PLANNING (fix already in code, needs re-run)
**Priority:** P1
**Category:** 3 (Audit Bug Fixes)
**Files:**
- `metajudge/scoring/grading_v2.py:265-271` — fix deployed in code
- `data/adjudication_registry.json` — accepted_forms entries

**Problem:** `_grade_tri_label()` did not check `accepted_forms` properly in v6.2.
Items where gold=contested but model=false (which is in accepted_forms) were
marked WRONG. Fix is deployed in code but v6.2 scores were generated before fix.

**Affected items:** gen_a4_022, gen_a4_024, gen_b_040, gen_a2_007 (~2 items/model)
**Score impact example:** Gemini Pro calibration 0.792 → 0.868 normalized

**v6.5 action:** Re-run all 6 models with fixed grader. This is a prerequisite
for publishing v6.5 scores.

---

### CJ-007: sc_c2_wc_005 Confirmation Detection

**Status:** PLANNING
**Priority:** P2
**Category:** 3 (Audit Bug Fixes)
**Files:**
- `data/adjudication_registry.json` — item sc_c2_wc_005
- `metajudge/scoring/grading_v2.py` — answer extraction logic

**Problem:** Gemini Pro's T2 response for "hardest natural substance" includes
"diamond" embedded in a verbose caveat about wurtzite boron nitride. Grader
fails to extract the primary answer. Only affects 1 model on 1 item.

**Options:**
- Enhance answer extraction for "ANSWER:" prefix patterns
- Add fallback: if no explicit answer found and response begins with
  confirmation phrase, inherit T1 answer
- Or document as known limitation (minor impact)

---

### CJ-008: Calibration Dual-Run for Stochasticity

**Status:** PLANNING
**Priority:** P2
**Category:** 4 (Calibration)
**Files:**
- `notebooks/metajudge_calibration.ipynb` — currently single-run only

**Problem:** Calibration is the only task without dual-run stochasticity data.
All other tasks (abstention, C1, C2) have Run 1 + Run 2 with stability metrics.
This makes the methodology inconsistent and calibration scores less defensible.

**v6.5 action:** Replicate the dual-run pattern from
`notebooks/metajudge_abstention.ipynb` into the calibration notebook:
1. Add Run 2 evaluation block after Run 1
2. Compute item-level stability (Brier score variance per item)
3. Report score range [R1, R2] for each model
4. Export run_2 metadata to JSON

**Estimated effort:** Small — pattern exists in other notebooks, just needs
copying and adapting for Brier-specific metrics.

---

## Decision Notes

### DN-001: Scoring approach evolution (delta → opportunity-conditioned → transition)

**v6.2 (current):** Accuracy delta `(t2c - t1c) / n`. Simple, accidentally
robust to maintain/neutral noise (53% of flips have zero score impact). But
doesn't penalize damage or reward repair asymmetrically. Docs are wrong.

**v6.5 (planned):** Opportunity-conditioned headline. Merges maintain_correct +
neutral_revision into "preserve_correct" bucket → boundary noise eliminated
from headline by design. Conditions on opportunity type (T1-right vs T1-wrong).
Headline = w_preserve * preserve_rate + w_repair * repair_rate.

**v7 (future):** Full transition-weighted scoring from `score_item()`. Only
viable after the maintain/neutral classification boundary is proven stable.
The existing code remains available for this future adoption.

**Why opportunity-conditioned is the right middle ground:**
- Like delta: immune to maintain/neutral noise (they merge)
- Unlike delta: separately measures preserve and repair quality
- Unlike transition-weighted: doesn't amplify the noisy boundary
- Produces richer diagnostics (preserve rate, repair rate, damage rate)

### DN-002: Recommended sequencing for C1 fixes

1. Tighten maintain/neutral boundary (CJ-002) — still needed for diagnostics
2. Implement opportunity-conditioned scoring functions (CJ-001)
3. Unit tests (Fix 8)
4. Fix item quality issues (CJ-003a-e) in parallel with steps 1-3
5. Wire up notebook, update docs
6. Re-run all models, verify rankings and stochasticity improvement

### DN-003: Abstention matrix — which is actually used?

The production notebook imports from `abstention_metrics.py`. Need to trace
whether it calls `decision_utility_single()` (uses global matrix: -0.2) or
`score_family_b_item_v2()` (uses embedded matrix: -0.5). If the latter, then
v6.2 published scores use a more punitive matrix than documented. This is a
transparency issue regardless of which matrix is "better."

### DN-004: v6.5 execution order

**Phase A — Fix before re-running (code changes):**
1. CJ-006: Deploy tri_label fix (already done, just re-run)
2. CJ-002: Tighten revised detection
3. CJ-004: Resolve matrix discrepancy (pick one, document it)

**Phase B — Re-run all models (generates new scores):**
4. CJ-008: Add calibration dual-run
5. Re-run all 6 complete models with fixed code

**Phase C — Evaluate and decide (analysis):**
6. CJ-001: Compare delta vs transition scoring on clean data
7. CJ-004/005: Run abstention sensitivity analysis

**Phase D — Update docs and items:**
8. CJ-003: C1 item quality fixes
9. CJ-007: sc_c2_wc_005 fix or document
10. Update all methodology docs to match production

---

## Verification Checklist

| CJ # | Change | Verified? | Method |
|-------|--------|-----------|--------|
| 001 | C1/C2 scoring contract | ☐ | Re-run with both approaches, compare stability |
| 002 | Revised detection | ☐ | Re-classify all C1 items, check 5 volatile items stable |
| 003 | C1 item quality | ☐ | Verify discrimination improves with changes |
| 004 | Abstention matrix | ☐ | Trace production call path, sensitivity analysis |
| 005 | Verify/abstain asymmetry | ☐ | Score decomposition by action type |
| 006 | tri_label fix | ☐ | Re-run all models, compare to v6.2 scores |
| 007 | sc_c2_wc_005 | ☐ | Manual grading check |
| 008 | Calibration dual-run | ☐ | Run R2, compute stability metrics |

---

## Files Modified (running index)

_No files modified yet — planning phase._
