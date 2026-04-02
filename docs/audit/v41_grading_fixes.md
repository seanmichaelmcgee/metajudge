# MetaJudge v4.1 — Grading Fixes

**Date:** April 2026
**Source:** Independent LLM audits of v3.2 benchmark results (4 models × 228 items)
**Status:** Implementing

---

## Summary

| Fix | Type | Item(s) | Error | Severity |
|-----|------|---------|-------|----------|
| 1.1 | Registry | v41_crt_009 | "The amounts are the same" rejected for gold "They are equal" | HIGH |
| 1.2 | Registry | gen_b_024 | French transliteration "Al-Karaouine" rejected | HIGH |
| 1.3 | Registry | sc_c2_wc_005 | `contains_any` credits contradictory answer | HIGH |
| 2.1 | Code | v41_ce_015 | Double quotes vs single quotes in code output | MEDIUM |
| 2.2 | Code | sc_c2_wc_001 | "Eight" not recognized as "8" | MEDIUM |
| 2.3 | Code | sc_c2_rr_004 | "4% decrease" not recognized as "-4%" | MEDIUM |
| 2.4 | Code | sc_c2_wc_004 | "France spans the most..." rejected for gold "France" | MEDIUM |

---

## Part 1: Registry Fixes

### Fix 1.1 — v41_crt_009: Equality phrasing
- Add: `"the same amount"`, `"the amounts are the same"`, `"identical"`, `"same amount"` to accepted_forms
- Merge with existing aliases (already has `"equal"`, `"the same"`, `"they are equal"`)
- Already has `match_mode: "contains_any"` from prior fix

### Fix 1.2 — gen_b_024: Al-Qarawiyyin transliterations
- Add: `"al-karaouine"`, `"al karaouine"`, `"quaraouiyine"`, `"al-karaouiyine"`, `"karaouine"` to accepted_forms

### Fix 1.3 — sc_c2_wc_005: Disable contains_any (false positive)
- Change `match_mode` from `"contains_any"` to `null`
- Keep `accepted_forms: ["diamond"]`
- Prevents crediting "Wurtzite boron nitride is harder than diamond"

---

## Part 2: Grading Engine Fixes

### Fix 2.1 — Quote normalization in code_output
- Treat `"` and `'` as equivalent in `_grade_code_output()`
- 3-line addition after initial exact match

### Fix 2.2 — Number-word-to-digit conversion
- `_normalize_number_words()`: "Eight" → "8", "Eight planets" → "8 planets"
- Single word or leading word only (no prose conversion)
- Integrate into `_preprocess_answer()`

### Fix 2.3 — Signed percentage normalization
- `_normalize_sign_language()`: "4% decrease" → "-4%", "4% increase" → "+4%"
- Fallback in `_grade_approx_numeric_small()` after existing extraction fails

### Fix 2.4 — Leading-token match for short gold answers
- If gold ≤ 3 words and answer starts with gold, accept
- Fallback in `_grade_alias_plus_normalization()` before final return-False
- Handles "France spans the most time zones..." for gold "France"

---

## Verification

Each fix has specific regression tests. After all fixes:
1. All 11 confirmed false negatives grade correctly
2. The sc_c2_wc_005 false positive grades correctly
3. No previously-correct items flip to wrong

---

## Deferred

- `gen_a_042`: Avogadro's constant 8th sig fig — needs strict_precision mode
- `gen_a2_032`: CODATA proton mass 10th sig fig — same
- `gen_a_044`: Body temperature study-specific dispute
- `sc_c1_wr_002`: Compound interest exact-cent tolerance
