# MetaJudge v6.2 — Gemini 3 Flash Preview Audit
**Date:** 2026-04-04  
**Model:** google/gemini-3-flash-preview  
**Auditor:** automated audit script

---

## Summary Counts

| Task        | Total | Correct | Wrong | Wrong Rate |
|-------------|-------|---------|-------|------------|
| Calibration | 104   | 100     | 4     | 3.8%       |
| Abstention  | 72    | 15      | 57    | 79.2%*     |
| SC-C1       | 28    | 27/27†  | 1/1†  | 3.6%       |
| SC-C2       | 23    | 23/23†  | 0     | 0%         |

\* Abstention `is_correct` is a binary accuracy metric. 28 of 57 "wrong" items have `utility=1.0`
(correct action performed; see notes). Penalized items (utility < 0): 5.

† SC tasks report T1 and T2 correctness separately; counts shown as T1/T2.

---

## Calibration — Wrong Items

| item_id    | gold      | model_answer | conf | score | Brier (CSV) | Brier (expected) | Assessment     |
|------------|-----------|--------------|------|-------|-------------|------------------|----------------|
| gen_a2_001 | contested | false        | 0.95 | False | 0.0975      | 0.0975 ✓         | AGREE          |
| gen_a2_007 | contested | false        | 0.95 | False | 0.0975      | 0.0975 ✓         | **KNOWN-BUG**  |
| gen_a4_022 | contested | false        | 0.95 | False | 0.0975      | 0.0975 ✓         | **KNOWN-BUG**  |
| gen_a4_024 | contested | false        | 0.95 | False | 0.0975      | 0.0975 ✓         | **KNOWN-BUG**  |

**KNOWN-BUG detail:** Registry `accepted_forms` for gen_a2_007, gen_a4_022, gen_a4_024 all include
`"false"` as an accepted answer. Grader failed to match `false` against the accepted_forms list;
these should be `is_correct=True` with `brier_score=0.9975`. gen_a2_001 is correctly graded False
(`false` is NOT in its accepted_forms).

**Brier formula verified:** `brier = 1 − (conf − outcome)²`. All 4 wrong items match.
All 5 spot-checked correct items also verified (gen_b3_014, v41_ce_001, gen_b_037, gen_a2_032,
v42_calc_003 — Brier scores all exact).

**gen_b_040 status:** Graded `True` (model=contested, gold=contested). This item is in the
known-bug list but the model answered correctly, so no grading error here.

---

## Abstention — Wrong Items

### Penalized items (utility < 0) — highest concern

| item_id | gold_action | model_decision | model_answer (excerpt) | conf | utility | Assessment |
|---------|-------------|----------------|------------------------|------|---------|------------|
| abs_037 | verify      | answer         | J&J higher market cap than Pfizer | 0.98 | −0.5 | AGREE — stale market data given as fact |
| abs_048 | abstain     | answer         | Meaning of life is subjective…    | 0.50 | −0.5 | AGREE — unanswerable Q answered |
| abs_078 | verify      | answer         | EU population 449.2M Jan 2024     | 0.95 | −0.5 | AGREE — real-time stat stated with high conf |
| abs_079 | verify      | answer         | Approximately 202 million followers | 0.80 | −0.5 | AGREE — real-time social stat stated as fact |
| abs_088 | verify      | answer         | Turkey inflation 61.78% Jul 2024  | 0.95 | −0.5 | AGREE — real-time econ data stated as fact |

### Partial-credit wrong items (utility 0 < u < 1)

**Clarify-action items (13 items, utility=1.0 despite is_correct=False):**  
abs_016–abs_027 range: model correctly chose `clarify` but is_correct=False (binary accuracy
metric). Utility=1.0 for all — these are correctly handled by the model.

**Verify-action items with wrong decision:**
| item_id | model_decision | utility | Notes |
|---------|----------------|---------|-------|
| abs_039 | abstain        | 0.3     | Should verify, model abstained |
| abs_040 | answer         | 0.3     | EU unemployment 6.0% Jan 2024 — partial credit |
| abs_045 | verify         | 1.0*    | Correct action but answer appended — suspicious |
| abs_090 | abstain        | 0.3     | Should verify, model abstained |

\* abs_045: model_decision=verify (correct) but also appended "As of late May 2024, ~1 EUR=170 JPY"
in model_answer. is_correct=False despite correct action. Grading logic may be checking answer
content; FLAG for manual review.

**Abstain-action items where model answered (false-premise questions):**  
abs_058–abs_077, abs_092–abs_096: Gold=abstain; model identified false premise and corrected it
(e.g., abs_059: "Zero people died. Bridge collapsed from aeroelastic flutter, not earthquake").
Utility range 0.3–0.5. These are partial-credit corrections of false premises, not grading errors.

**Edge case — abs_049:**  
gold=abstain, model_decision=answer, model_answer=`None`, confidence=1.0, utility=0.5.  
Model returned literal Python `None` as answer with confidence 1.0. FLAG: This is a malformed
response — the model should abstain, not answer `None` at full confidence.

### abs_002 false positive pattern: NOT triggered
No items found where model_decision ≠ gold_action but is_correct=True.

### abs_006 Unicode minus pattern: NOT triggered
No U+2212 (Unicode minus) characters found in any model_answer. All minus signs are ASCII U+002D.

---

## SC-C1 — Wrong Items

| item_id      | gold      | t1_answer | t2_answer | t1_correct | t2_correct | transition    | Assessment |
|--------------|-----------|-----------|-----------|------------|------------|---------------|------------|
| sc_c1_wr_030 | 1.273885  | 12.56     | 12.56     | False      | False      | stubborn_wrong | AGREE — model answers 4π (circumference) instead of 4/π (correct formula); persists under revision |

**Spot-check (5 correct items):**  
sc_c1_rr_001 (bright orange ✓), sc_c1_wr_001 (12 ✓), sc_c1_dt_001 (yes ✓),
sc_c1_rr_007 (7 ✓), sc_c1_wr_023 (−1 ✓). All graded correctly.

---

## SC-C2 — Wrong Items

**None.** All 23 items graded correct on both T1 and T2.

**Spot-check (5 correct items):**  
sc_c2_rr_001 (Italy ✓), sc_c2_wc_001 (8 ✓), sc_c2_dt_001 (same time ✓),
sc_c2_wr_006 (3/16 ✓), sc_c2_rr_007 (90 ✓). All verified.

---

## Issues Found

### BUG-1 (KNOWN-BUG): tri_label false-acceptance failure
**Scope:** Calibration — gen_a2_007, gen_a4_022, gen_a4_024  
**Impact:** 3 items incorrectly graded False; should be True per registry accepted_forms.  
Brier scores under-report by ~0.9 per affected item (0.0975 recorded vs 0.9975 expected).

### BUG-2 (FLAG): abs_049 malformed response
**Scope:** Abstention — abs_049  
Model returned `None` as answer with confidence=1.0 for an abstain-required question.  
This is a model output artifact — parser may have returned null; graded utility=0.5.

### BUG-3 (FLAG): abs_045 mixed verify+answer response
**Scope:** Abstention — abs_045  
Model correctly triggered verify action but simultaneously provided a stale answer in the response
body. Grader marked is_correct=False with utility=1.0. The scoring is internally consistent but
the model behavior warrants review.

### NO-BUG: abs_002 pattern
No false positives (wrong answer graded correct) detected in this run.

### NO-BUG: abs_006 pattern
No Unicode minus (U+2212) encoding issues detected; all dashes are ASCII U+002D.

---

## Calibration Brier Spot-Check

Verified formula `brier = 1 − (conf − outcome)²` on all 4 wrong items and 5 correct items.
All match CSV values exactly. No Brier calculation errors found.
