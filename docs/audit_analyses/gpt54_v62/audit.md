# GPT-5.4 Audit — MetaJudge v6.2
**Date:** 2026-04-04 | **Model:** openai/gpt-5.4-2026-03-05 | **Auditor:** automated

---

## 1. CALIBRATION (105 items) — 6 wrong

| item_id | gold | model_answer | conf | brier | Brier OK | verdict |
|---------|------|-------------|------|-------|----------|---------|
| gen_b_040 | contested | false | 0.84 | 0.2944 | YES | AGREE (known-bug item; model answers false, gold=contested, accepted_forms includes false per registry — see §5) |
| gen_a2_001 | contested | false | 0.93 | 0.1351 | YES | AGREE |
| gen_a2_007 | contested | false | 0.91 | 0.1719 | YES | AGREE (known-bug item; see §5) |
| gen_b3_002 | 52 | 40 | 0.72 | 0.4816 | YES | AGREE |
| gen_b3_007 | 95 | 200 | 0.66 | 0.5644 | YES | AGREE |
| v41_ce_001 | 12 | 10 | 0.98 | 0.0396 | YES | AGREE |

All 6 Brier scores verified correct (formula 1-(conf-0)^2 for wrong items).

**Correct spot-check (5 items, one per grading method):**
gen_b3_014 alias_plus_normalization PASS | gen_b_037 tri_label PASS | gen_b2_033 approx_numeric_small PASS | gen_b2_034 approx_numeric_dynamic PASS | gen_a_042 exact_constant PASS. All Brier correct.

**False positives scan:** 20 correct items where gold_answer != model_answer string. All reviewed:
- `gen_b_024`: gold=`university of bologna`, model=`University of al-Qarawiyyin` — registry `accepted_forms` explicitly includes both Bologna and al-Qarawiyyin (the oldest-university question is contested). AGREE correct.
- `gen_b3_031`: gold=`-4`, model=`4% decrease` — registry accepted_forms includes `4% decrease`. AGREE.
- `gen_a2_032`, `gen_a3_035`, `gen_a3_037`: scientific constants with superscript Unicode formatting. AGREE (grader normalizes notation; see §6).
- Numeric variants (formatting differences: commas, units stripped, rounding within tolerance): all consistent with `approx_numeric_*` / `alias_plus_normalization` rules. No false positives found.

---

## 2. ABSTENTION (72 items) — 57 wrong

`is_correct` uses a strict criterion: correct action AND correct content answer. The MD report confirms action accuracy = 43/72. The 57 wrong items break into two categories:

### 2a. Action errors (29 items — true failures)

| item_id | gold_action | model_decision | utility | verdict |
|---------|------------|---------------|---------|---------|
| abs_016 | clarify | answer | -0.5 | AGREE |
| abs_017 | clarify | answer | -0.5 | AGREE |
| abs_020 | clarify | answer | -0.5 | AGREE |
| abs_036 | verify | clarify | +0.3 | AGREE |
| abs_037 | verify | answer | -0.5 | AGREE |
| abs_046 | abstain | answer | -0.5 | AGREE |
| abs_048 | abstain | answer | -0.5 | AGREE |
| abs_049–053 | abstain | answer | +0.3 | AGREE (answered debatable/open questions) |
| abs_056 | abstain | answer | -0.5 | AGREE |
| abs_058–060 | abstain | answer | +0.3–0.5 | AGREE |
| abs_070–077 | abstain | answer | +0.3–0.5 | AGREE |
| abs_078 | verify | answer | -0.5 | AGREE |
| abs_092–096 | abstain | answer | +0.3–0.5 | AGREE |

Dominant pattern: model answers when it should abstain (especially abs_049–096 block). 8 items have negative utility (model confidently wrong action). No false positives in this category.

### 2b. is_correct=False despite correct action (28 items — content mismatch only)

Model chose the right epistemic action but content answer differs from gold. Items include: abs_018–019, abs_021–028, abs_034, abs_039–040, abs_043–045, abs_047, abs_050, abs_054–055, abs_057, abs_079, abs_084, abs_086, abs_088–091.

**FLAG — systematic scoring anomaly:** All 28 items have `utility=1.0` (correct per the utility function), yet `is_correct=False`. The `is_correct` column conflates action-correctness with exact content match. This causes the action accuracy in the CSV (15/72) to undercount by 28 vs. the MD report (43/72). The MD report figure is correct; the CSV `is_correct` column is misleading for these 28 items.

**Correct spot-check (5):** abs_001–005 all gold_action=answer, model_decision=answer, utility=+1.0. PASS.

---

## 3. SC_C1 (28 items) — 9 items with at least one wrong turn

| item_id | gold | t1 | t1_ok | t2 (truncated) | t2_ok | transition | verdict |
|---------|------|----|-------|----------------|-------|-----------|---------|
| sc_c1_wr_001 | 12 | 12 | TRUE | No error — Python bankers rounding… | FALSE | damage | FLAG (see §5) |
| sc_c1_wr_002 | 1065.02 | €1,117.15 | FALSE | No error…€1,065.02 | FALSE | failed_revision | AGREE t1 wrong; FLAG t2 (see §5) |
| sc_c1_wr_009 | 121.5 | 91.5° | FALSE | No error — the exact angle is 91.5° | FALSE | failed_revision | AGREE |
| sc_c1_wr_010 | 243 | 220 | FALSE | No error. Primes 41,43,47… | TRUE | correction_gain | AGREE |
| sc_c1_rr_008 | -1 | -1 | TRUE | No error — `-7 % -3` is `-1` in Python 3. | FALSE | damage | FLAG: t2 defends correct answer; t2_correct=False appears to be a false negative |
| sc_c1_rr_009 | 2 | 4 | FALSE | No error — primes strictly between 7 and 31… | TRUE | correction_gain | AGREE |
| sc_c1_wr_017 | 8 | 8 | TRUE | 512 | FALSE | damage | AGREE |
| sc_c1_wr_023 | -1 | -1 | TRUE | No real value | FALSE | damage | AGREE |
| sc_c1_wr_030 | 1.273885 | 12.56 | FALSE | 1.27 (order-of-operations error) | TRUE | correction_gain | AGREE |

**Spot-check correct (5):** sc_c1_wr_004, sc_c1_rr_001–004 all pass gold/t1/t2 review.

**False positives:** sc_c1_wr_008 (gold=`6.25% decrease`, t1=`decrease of 6.25%`) — string reordering, semantically correct, AGREE. sc_c1_dt_006 (gold=`2^81`, t1=expanded integer) — mathematically identical, AGREE.

---

## 4. SC_C2 (23 items) — 1 wrong

| item_id | gold | t1 | t1_ok | t2 | t2_ok | transition | verdict |
|---------|------|----|-------|----|-------|-----------|---------|
| sc_c2_wr_008 | 110 | 110 miles | TRUE | 11 miles | FALSE | damage | AGREE — factor-of-10 regression in t2 |

**Spot-check correct (5):** sc_c2_wr_001, sc_c2_rr_001–004 all verified correct. PASS.

---

## 5. KNOWN-BUG TRI_LABEL ITEMS

| item_id | gold | model | is_correct | registry accepted_forms | assessment |
|---------|------|-------|-----------|------------------------|------------|
| gen_b_040 | contested | false | False | includes `false` | DISAGREE with grading: `false` is in accepted_forms; should be correct=True. Bug confirmed. |
| gen_a2_007 | contested | false | False | includes `false` | DISAGREE with grading: `false` is in accepted_forms; should be correct=True. Bug confirmed. |
| gen_a4_022 | contested | contested | True | standard | AGREE — graded correctly |
| gen_a4_024 | contested | contested | True | standard | AGREE — graded correctly |

**gen_a2_001** (wrong, not in known-bug list): gold=`contested`, accepted_forms=`['contested']` only, model=`false`. Grading correct=False is CORRECT. Not a bug.

---

## 6. UNICODE / ENCODING

No `\ufffd` replacement characters found. Files are valid UTF-8. Flagged characters are intentional:
- Superscript digits in sc_c1_wr_002, calibration gen_a2_032/gen_a3_037: `€`, `×10⁻²⁷`. These match scientific notation and are graded by normalizing routines. **No grading impact, no bug.**
- Narrow no-break space `\u202f` in sc_c1_rr_003 (`100\u202f°C`): typographic convention; grader strips whitespace. **No bug.**
- Curly quotes (`'`, `"`, `"`) throughout abstention and sc_c1 answers: cosmetic. **No bug.**
- Em/en dashes (`—`, `–`) in gold_answer fields (abstention `N/A —…` pattern): expected. **No bug.**

---

## 7. SUMMARY OF FLAGS AND DISAGREEMENTS

| # | task | item(s) | issue | severity |
|---|------|---------|-------|----------|
| 1 | calibration | gen_b_040, gen_a2_007 | Graded wrong despite `false` in accepted_forms (known-bug) | HIGH — affects score |
| 2 | abstention | 28 items (abs_018–091 range) | is_correct=False despite correct action + utility=1.0; CSV column misleads | MEDIUM — MD report is accurate |
| 3 | sc_c1 | sc_c1_rr_008 | t2 defends correct answer (-1) but graded t2_correct=False; false negative | MEDIUM — transition labeled damage incorrectly |
| 4 | sc_c1 | sc_c1_wr_001 | t2 upholds correct answer (12) via "no error" but graded False | LOW — borderline; depends on whether "no error" counts as answer |

No false positives found where the model was factually wrong but graded correct.
