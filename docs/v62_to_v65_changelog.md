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

### CJ-001: C1/C2 Scoring Contract — Delta vs Transition-Based

**Status:** PLANNING
**Priority:** P0 — benchmark validity issue
**Category:** 1 (C1/C2 Scoring)
**Files:**
- `notebooks/metajudge_sc_c1.ipynb` — production scoring, uses delta
- `notebooks/metajudge_sc_c2.ipynb` — same delta-only issue
- `metajudge/scoring/self_correction_v2.py` — transition scoring exists but unused
- `config/family_c_scoring.yaml` — asymmetric weights defined but unused
- `METHODOLOGY.md`, `docs/scoring_overview.md`, `README.md` — claim transition-based

**Problem:** Public docs describe transition-based scoring with asymmetric damage
penalties and confidence adjustments. Both C1 AND C2 production notebooks compute
simple accuracy delta `(t2_correct - t1_correct) / n`. Example discrepancy:
Sonnet C1 scores 0.400 (delta) vs 0.890 (transition-weighted).

The code for transition scoring exists (`score_item()`, `compute_family_c_headline()`
in `self_correction_v2.py`) but is never called. The YAML config exists but is
never loaded (hardcoded defaults in the .py module take precedence).

**Decision needed:** Wire up existing transition code, or update docs to match
delta approach? See DN-001.

**CJ-001-NOTE: Interaction with C1 stochasticity**
The 53% C1 flip concentration (maintain_correct ↔ neutral_revision boundary)
currently has ZERO score impact under delta scoring because both transitions
have t2_correct=true. Switching to transition-based scoring would make these
flips score-relevant (0.60 vs 0.40 per item), potentially INCREASING instability.
Must fix CJ-002 BEFORE wiring up transition scoring.

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

### CJ-004: Abstention Payoff Matrix Audit

**Status:** PLANNING
**Priority:** P1
**Category:** 2 (Abstention)
**Files:**
- `metajudge/scoring/abstention_metrics.py:38-64` — global payoff matrix
- `metajudge/scoring/abstention_metrics.py:325-346` — v2 embedded matrix (DIFFERENT!)
- `docs/family_b_scoring_spec.md` — documented rationale
- `docs/scoring_overview.md:61-99` — public matrix documentation

**Problem:** TWO undocumented issues found:

**Issue A: Dual matrix discrepancy.** The global matrix and the `score_family_b_item_v2()`
embedded matrix disagree on cautious-action penalties for answer items:

| Cell | Global matrix | v2 embedded | Docs |
|------|--------------|-------------|------|
| clarify × answer | -0.2 | **-0.5** | -0.2 |
| verify × answer | -0.2 | **-0.5** | -0.2 |
| abstain × answer | -0.3 | **-0.5** | -0.3 |

Which matrix is actually used in production? If v2, then models are penalized
2.5x more than documented for cautious behavior on answerable items.

**Issue B: +0.3 off-diagonal credit.** The +0.3 partial credit for any non-answer
action on any non-answer gold compresses score range and rewards "cautious
disposition" over action discrimination. Models that answer less score better.
Verify may be structurally disadvantaged vs abstain.

**v6.5 action:** Run sensitivity analysis on +0.3 vs smaller values (0.1, 0.15,
0.2). Check how much model ordering is driven by answer rate vs action accuracy
vs verify suppression.

---

### CJ-005: Abstention Scoring — Verify/Abstain Asymmetry

**Status:** PLANNING
**Priority:** P2
**Category:** 2 (Abstention)
**Files:**
- `metajudge/scoring/abstention_metrics.py`
- `notebooks/metajudge_abstention.ipynb`

**Problem:** Verify and abstain are treated nearly identically in scoring (+0.3
partial credit for each on non-matching non-answer items), but they represent
different metacognitive strategies. The current matrix may not discriminate
between a model that knows it needs more info (verify) vs one that gives up
(abstain). Check whether separating these signals improves discrimination.

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

### DN-001: Will transition-based scoring fix the C1 53% flip problem?

**Short answer: No. It would likely make it worse.**

The 53% figure refers to 19 of 36 C1 flips concentrated in 5 items, primarily
driven by maintain_correct ↔ neutral_revision classification ambiguity.

Under CURRENT delta scoring:
- maintain_correct: t2_correct=true → delta contribution = 0
- neutral_revision: t2_correct=true → delta contribution = 0
- A flip between them has **zero score impact**
- The 0.286 score swings come from the OTHER 47% of flips (damage-related,
  where t2_correct actually changes)

Under TRANSITION-BASED scoring:
- maintain_correct: weight = 0.60
- neutral_revision: weight = 0.40
- A flip between them changes the item score by ±0.20
- At n=28 items, each such flip moves the headline by ~0.007
- With 5+ items flipping simultaneously, this adds ~0.035 of NEW noise

**Conclusion:** Transition scoring adds a new source of instability for the
exact boundary that's already the most volatile. The delta approach is
accidentally more robust to this specific failure mode.

**Implication for v6.5:** Before switching to transition scoring, FIRST fix the
classification boundary (CJ-002). Otherwise you're amplifying noise.

### DN-002: Recommended sequencing for C1 fixes

1. Tighten maintain_correct vs neutral_revision boundary (CJ-002)
2. Verify the 5 volatile items are stable under new boundary
3. THEN decide delta vs transition scoring (CJ-001) with clean data
4. Fix item quality issues (CJ-003) in parallel
5. Update docs to match whichever approach is chosen

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
