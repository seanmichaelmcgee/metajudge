# MetaJudge v6.2 → v6.5 Change Journal

**Branch:** `submission/v6.5` (branched from `submission/v6.1`)
**Rollback:** `submission/v6.1` (frozen)
**Started:** 2026-04-05

---

## Change Log

Each entry: what changed, why, what files, verification status.

### CJ-001: C1 Scoring Contract — Delta vs Transition-Based

**Status:** PLANNING
**Priority:** P0 — benchmark validity issue
**Files:**
- `notebooks/metajudge_sc_c1.ipynb` (production scoring — uses delta)
- `metajudge/scoring/self_correction_v2.py` (transition scoring — exists but unused)
- `config/family_c_scoring.yaml` (asymmetric weights — defined but unused)
- `METHODOLOGY.md`, `docs/scoring_overview.md`, `README.md` (claim transition-based)

**Problem:** Public docs describe transition-based scoring with asymmetric damage
penalties and confidence adjustments. Production notebook computes simple accuracy
delta `(t2_correct - t1_correct) / n`. Example discrepancy: Sonnet C1 scores
0.400 (delta) vs 0.890 (transition-weighted). This is a 0.490 point gap.

**Decision needed:** Wire up existing transition code, or update docs to match
delta approach? See CJ-001-NOTE below.

**CJ-001-NOTE: Interaction with C1 stochasticity**
The 53% C1 flip concentration (maintain_correct ↔ neutral_revision boundary)
currently has ZERO score impact under delta scoring because both transitions
have t2_correct=true. Switching to transition-based scoring would make these
flips score-relevant (0.60 vs 0.40 per item), potentially INCREASING instability.
See analysis in "Decision Notes" section below.

---

### CJ-002: (reserved — next change)

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
classification boundary (tighten maintain_correct vs neutral_revision definition).
Otherwise you're amplifying noise.

### DN-002: Recommended sequencing for C1 fixes

1. Tighten maintain_correct vs neutral_revision classification boundary
2. Verify the 5 volatile items (sc_c1_rr_010, dt_001, wr_023, wr_004, wr_011)
   are stable under new boundary
3. THEN decide delta vs transition scoring with clean classification data
4. Update docs to match whichever approach is chosen

---

## Verification Checklist

| CJ # | Change | Verified? | Method |
|-------|--------|-----------|--------|
| 001 | C1 scoring contract | ☐ | Re-run C1 with both approaches, compare stability |

---

## Files Modified (running index)

_No files modified yet — planning phase._
