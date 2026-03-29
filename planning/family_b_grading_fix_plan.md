# Family B Answer Grading Fix Plan

**Status:** Registry + fallback fix applied to benchmark notebook and grading engine.
**Remaining:** Narrative notebook needs the same fix applied.

---

## Problem Summary

Family B "answer" items (`abs_001`–`abs_015`) were not in the adjudication
registry. When a model chose `decision == "answer"`, the grading engine
returned `is_correct = False` for every item, regardless of answer quality.
This silently corrupted all UWAA scores — the entire Axis II (Control) metric.

### Root Cause

- The adjudication registry was built for calibration items only (117 entries)
- Family B items use `abs_*` IDs, which had no registry entries
- `grade_item()` returned `{"correct": False, "method": "unknown"}` for missing items
- No fallback existed in grading_v2.py

### Prior State by Notebook

| Notebook | Family B Grading | Bug Present? |
|----------|-----------------|-------------|
| **Lean** (`metajudge_submission_lean.ipynb`) | 5-level heuristic fallback (exact → word → numeric → last-word → substring) | Partial — heuristic worked but was imprecise |
| **Narrative** (`metajudge_narrative.ipynb`) | `grade_item()` only, no fallback | **YES — all answers graded incorrect** |
| **Benchmark** (`metajudge_benchmark.ipynb`) | `grade_item()` only, no fallback | **YES — all answers graded incorrect** |

---

## Fix Applied (2026-03-29)

### 1. Registry entries (15 items)

Added `abs_001`–`abs_015` to `data/adjudication_registry.json` with:
- Proper `grader_rule` (alias_plus_normalization or approx_numeric_small)
- `accepted_forms` with aliases (e.g., Li/Lithium, Sunda Trench/Java Trench)
- Numeric tolerances where appropriate (e.g., C-14 half-life ±10 years)

### 2. Fallback in `grade_item()`

Added optional `gold_answer` parameter to `grade_item()`. When an item is
not in the registry and `gold_answer` is provided, uses:
- Normalised string comparison (lowercase, collapsed whitespace)
- Numeric comparison with `rel_tol=1e-6`

Conservative — no substring or containment matching.

### 3. Benchmark notebook updated

Cell 6 now passes `gold_answer=gold_answer` to `grade_item()`.

### 4. Tests added

- `TestFamilyBRegistry`: Verifies 15 entries present, grading works (Lithium/Li, 5730/5,730, Floyd-Warshall)
- `TestGradeItemFallback`: Verifies fallback exact, numeric, miss, and no-gold-answer cases
- All 118 grading tests pass

---

## Remaining Work: Narrative Notebook

### What to fix

`notebooks/metajudge_narrative.ipynb` Cell 6 — Family B sweep:

```python
# CURRENT (buggy for items not in registry):
if iid in REGISTRY:
    is_correct = grade_item(iid, str(resp.answer), REGISTRY).get("correct", False)

# FIXED (uses registry + fallback):
is_correct = grade_item(iid, str(resp.answer), REGISTRY,
                        gold_answer=item["gold_answer"]).get("correct", False)
```

The `if iid in REGISTRY` guard is no longer needed since:
1. All 15 answer items are now in the registry
2. The fallback handles any future items not yet registered

### Impact on prior results

All narrative notebook Family B results need to be re-run. The prior
results (from the 5-model sweep) have corrupted `is_correct` values,
meaning UWAA scores are wrong. This affects:
- Family B leaderboard (cell 11)
- Composite MetaScore (cell 13)
- Mechanism heatmap (cell 16)
- Any exported audit CSVs

### Verification steps after fix

1. Run a smoke test on 2-3 items with known answers to confirm grading
2. Re-run full 5-model sweep on Kaggle
3. Compare UWAA scores before/after — expect improvement for models that
   correctly answered "answer" items
4. Verify the 57 non-answer items (clarify/verify/abstain) are unaffected
   (is_correct should remain False for all, which is correct behaviour
   since correctness only matters when decision == "answer")

---

## Theoretical Note

Family B grading only affects the `answer_correct` vs `answer_incorrect`
row selection in the utility matrix. For the 57 items where `gold_action`
is clarify/verify/abstain, the model's decision (not its answer) determines
the utility. The grading fix therefore only impacts the 15 "answer" items
— but these are critical because they carry the highest utility swing
(+1.0 correct vs -1.0 incorrect, a 2.0 spread).
