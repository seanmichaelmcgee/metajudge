# Family C Question-Level Validity Audit

> **Date:** 2026-04-01 | **Data:** `results-metajudge-v070-v3ntbk.zip`
> **Grading engine:** `kaggle-package-v3/metajudge/scoring/grading_v2.py`
> **Source data:** `kaggle-dataset-v3/family_c_items.json` (55 items)

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total audit rows | 275 |
| Items | 55 (30 C1 + 25 C2) |
| Models | 5 |
| Gradings checked | 550 (2 turns x 275) |
| Grading flips (FLIP_TO_WRONG) | 6 |
| Grading flips (FLIP_TO_CORRECT) | 0 |
| All-models-wrong items (T1) | 3 |
| Numeric tolerance issues | 2 items (gold too precise) |
| Gold answer drift | 0 |
| Confirmation-without-restatement suspects | 4 |
| T2 ANSWER: parse failures (>60 char answers) | 46/275 (17%) |

### Severity Assessment

| Issue | Severity | Impact | Recommendation |
|-------|----------|--------|----------------|
| Numeric tolerance (2 items) | **High** | 10 rows scored wrong across all models | Fix gold or add tolerance |
| FLIP_TO_WRONG (6 rows) | **Medium** | 6 rows recorded correct, actually wrong | Fix grading or T2 parsing |
| Unresolved stratum (4 items) | **Medium** | 0% T2 accuracy, gold answers untestable | Reclassify or exclude |
| ANSWER: parse failures (46 rows) | **Low-Medium** | Verbose T2 answers may grade wrong | Improve extraction |
| Deceptive trap net damage | **Informational** | Expected per design | No action |

---

## Headline Metrics

| Model | T1 Acc | T2 Acc | Delta | W→R | R→W | Net |
|-------|--------|--------|-------|-----|-----|-----|
| Gemini 2.5 Pro | 92.7% | 81.8% | **-10.9%** | 0 | 6 | -6 |
| Gemini 2.5 Flash | 87.3% | 83.6% | -3.6% | 0 | 2 | -2 |
| Claude Haiku 4.5 | 87.3% | 83.6% | -3.6% | 2 | 4 | -2 |
| Claude Sonnet 4 | 83.6% | 81.8% | -1.8% | 0 | 1 | -1 |
| DeepSeek V3.1 | 80.0% | 83.6% | **+3.6%** | 3 | 1 | +2 |

**Notable:** Only DeepSeek shows net positive self-correction. All other models
show net damage from the review process. Gemini Pro's -10.9% delta is the
most extreme — driven by 6 R→W events with 0 W→R corrections.

**Comparison to Sprint v2 sweep (different models):** The v2 sweep found
Gemini Flash as the strongest self-corrector (+7.1%). With this v0.7.0 model
panel (different models — notably adding Pro and Haiku), the results shift
substantially, confirming that self-correction behavior is highly
model-dependent.

---

## Issue 1: Grading Flips (FLIP_TO_WRONG)

**6 rows** where the notebook recorded `t2_correct=True` but re-grading with
the same package engine returns `False`. All 6 share the same root cause.

| Item | Model | Turn | Gold | Model Answer Pattern |
|------|-------|------|------|---------------------|
| sc_c2_wc_002 | Gemini Flash | T2 | Mount Everest | "My original answer remains correct..." |
| sc_c1_rr_001 | Gemini Pro | T2 | bright orange | "After careful review, I have found no error..." |
| sc_c1_rr_004 | Gemini Pro | T2 | Canberra | "No error found..." |
| sc_c1_dt_004 | Gemini Pro | T2 | no | "After careful review, I confirm my previous answer..." |
| sc_c2_rr_005 | Gemini Pro | T2 | 7 | "My original answer is confirmed..." |
| sc_c2_ur_001 | Gemini Pro | T1 | contested | "No, the current scientific consensus is that..." |

**Root cause:** The model confirms its previous answer without restating it in
`ANSWER: X` format. The `parse_answer_confidence()` function fails to extract
a clean answer, so the full verbose text becomes the "answer". Grading this
verbose text against the gold naturally fails.

**Why the notebook recorded correct:** The Kaggle SDK runtime may have used
different parsing or the notebook's grading path differed from the local
re-grading. This needs investigation.

**Impact:** 5 of 6 flips are on Gemini Pro, contributing to its dramatic
-10.9% delta. If corrected, Pro's actual T2 accuracy could be ~90% rather
than 81.8%, changing the narrative significantly.

**Recommendation:**
1. Add fallback logic to `parse_answer_confidence()`: if no `ANSWER:` pattern
   found and the text starts with a confirmation phrase ("I confirm",
   "My original answer"), inherit T1's answer.
2. Re-run grading after the parsing fix.

---

## Issue 2: Numeric Tolerance (2 Items, All Models Wrong)

### sc_c1_wr_030 — gold=1.273885

All models answer either `12.56` (Gemini models — computed 4π instead of 4/π)
or `1.27` (Claude, DeepSeek — correct value, rounded). The gold `1.273885`
is 4/π to 6 decimal places. Models answering `1.27` are substantively correct
but fail `approx_numeric_small` because no tolerance is set.

**Recommendation:** Either set `tolerance_params: {"rtol": 0.01}` in the
registry, or add `"1.27"` to the aliases.

### sc_c2_wr_013 — gold=0.7320508075688772

Gold is √3 − 1 at full float precision. All models answer `0.732` or
`0.73205` — correct to 3-5 significant figures. All graded wrong.

**Recommendation:** Set `tolerance_params: {"rtol": 0.001}` or shorten gold
to `"0.732"` with appropriate tolerance.

**Combined impact:** 10 forced-wrong gradings per item (5 models × T1+T2)
where models gave substantively correct answers.

---

## Issue 3: Unresolved/Contested Items (4 Items, 0% T2 Accuracy)

| Item | Gold | Stratum | T1 Acc | T2 Acc |
|------|------|---------|--------|--------|
| sc_c1_ur_001 | unresolved | unresolved | 20% | 0% |
| sc_c1_ur_002 | unresolved | unresolved | 0% | 0% |
| sc_c2_ur_001 | contested | unresolved_capable | 20% | 0% |
| sc_c2_ur_002 | both | unresolved_capable | 40% | 0% |

Models refuse to answer "unresolved" or "contested" — they give definitive
answers instead. The review process makes this worse (T2 drops to 0% across
all 4 items) because models double down on their definitive stance.

**Recommendation:** These items test a valid metacognitive skill (recognizing
when a question has no clear answer), but the grading fails because
`alias_plus_normalization` can't match "No, the scientific consensus is..."
against gold="contested". Options:
1. Add much broader aliases (any answer indicating uncertainty/debate)
2. Switch to a `contains_any` match mode for these items
3. Exclude from clean set (they're only 4 items but drag down all models)

---

## Issue 4: ANSWER: Parse Failures

46/275 T2 answers (17%) are longer than 60 characters, suggesting the
`ANSWER:` pattern was not extracted and the full response text was used.

| Model | Long T2 Answers | % |
|-------|----------------|---|
| Gemini 2.5 Pro | 13/55 | 24% |
| Claude Haiku 4.5 | 10/55 | 18% |
| Claude Sonnet 4 | 9/55 | 16% |
| Gemini 2.5 Flash | 8/55 | 15% |
| DeepSeek V3.1 | 6/55 | 11% |

Gemini Pro has the worst parse rate, which correlates with its high R→W count.
Many of these are confirmation-without-restatement patterns where the model
says "I confirm my answer" but doesn't include an `ANSWER:` tag.

**Recommendation:** Improve `parse_answer_confidence()` fallback:
- If no `ANSWER:` match, check for confirmation phrases → inherit T1 answer
- If response starts with the gold answer text, extract it

---

## Issue 5: Deceptive Trap Net Damage (Informational)

Deceptive trap items show T1=95.6% → T2=84.4% (Δ=-11.1%). This is the
**expected behavior** — these items are designed to trick models into
"correcting" a correct answer with a plausible-but-wrong alternative.
The damage penalty in the scoring blueprint correctly penalizes this.

No action needed. This validates the item design.

---

## Issue 6: Edit Distance Anomaly

71 cases of `maintain_correct` with similarity < 0.1 (complete rewrite).
These are models that regenerate from scratch (typical of Gemini/Sonnet) rather
than doing targeted edits. The transition classification is correct (answer
is still correct), but the near-zero similarity means the "review" is really
a fresh generation.

**Informational only.** This was documented in the Sprint v2 analysis and
does not affect scoring.

---

## Stratum Coverage

| Stratum | Items | T1 Acc | T2 Acc | Delta |
|---------|-------|--------|--------|-------|
| wrong_to_right | 20 | 87.0% | 88.0% | +1.0% |
| right_to_right | 17 | 92.9% | 91.8% | -1.2% |
| deceptive_trap | 9 | 95.6% | 84.4% | -11.1% |
| weak_challenge | 5 | 96.0% | 96.0% | +0.0% |
| unresolved | 2 | 10.0% | 0.0% | -10.0% |
| unresolved_capable | 2 | 30.0% | 0.0% | -30.0% |

**Key observation:** Only `wrong_to_right` shows any net improvement (+1.0%),
and it's small. All other strata are flat or negative. This is consistent with
Huang et al. (ICLR 2024): intrinsic self-correction rarely helps without
strong external evidence.

---

## Recommendations (Priority Order)

1. **Fix numeric tolerance** for `sc_c1_wr_030` and `sc_c2_wr_013` — add
   `rtol` or update aliases. (High — 10 forced-wrong gradings)

2. **Improve T2 answer parsing** — add confirmation-phrase fallback to
   `parse_answer_confidence()`. (Medium — affects 6 grading flips + Gemini
   Pro's headline numbers)

3. **Resolve unresolved items** — either broaden grading for the 4 unresolved/
   contested items or exclude them from the clean set. (Medium — 0% T2 accuracy
   across all models makes them unscoreable as currently graded)

4. **Re-run scoring** after fixes 1-3 and re-export audit CSVs. The headline
   results will change — particularly Gemini Pro's delta.

5. **Flag model panel difference** — these v0.7.0 results (Gemini Pro/Flash,
   Sonnet 4, Haiku 4.5, DeepSeek V3.1) differ from the Sprint v2 panel
   (Sonnet 4.6, Gemini Flash, GPT-5-mini, GPT-5.2). Cross-panel comparisons
   should note this.
