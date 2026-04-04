# MetaJudge Scoring Audit — Initial Findings (v6.2)

**Date:** 2026-04-03
**Data:** 4 tasks × 1 model each (mismatched — extraction limitation)
**Status:** Preliminary — needs full panel data for discrimination analysis

---

## Data Inventory

| Version | Task | Model | Items Scored | Expected |
|---------|------|-------|-------------|----------|
| v62 | Calibration | Claude Sonnet 4 | 105 | 105 ✓ |
| v62 | Abstention | Gemma 4 31b | 68 | 72 (4 failed) |
| v62 | SC C1 | Gemma 4 31b | 28 | 28 ✓ |
| v62 | SC C2 | Claude Sonnet 4 | 23 | 23 ✓ |
| v61 | Calibration | GPT-5.4 | 32 | 105 (quota hit) |
| v61 | Abstention | Gemma 4 26b | 72 | 72 ✓ |
| v61 | SC C1 | Gemma 4 26b | 28 | 28 ✓ |
| v61 | SC C2 | Gemma 4 26b | 23 | 23 ✓ |

---

## Findings by Task

### 1. Calibration (Sonnet 4, v62) — VALID

| Metric | Value |
|--------|-------|
| Accuracy | 94/105 (89.5%) |
| Mean 1-Brier | 0.9005 |
| Normalized | 0.602 |
| Overconfident wrong | 4 |

**11 wrong items** spanning calculation errors (v42_calc_002, v41_ct_002), contested-knowledge misclassification (gen_a4_022, gen_a4_024), and prototype violations (gen_b2_019: gold=Sweden, model=Finland).

**Assessment:** Scoring mechanics correct. Item spread exists (wrong items across multiple categories). Overconfidence penalty working (4 items at conf≥0.9 incur high Brier cost). Need multi-model data to assess discrimination.

### 2. Abstention (Gemma 31b, v62) — VALID BUT LENIENT

| Metric | Value |
|--------|-------|
| Items scored | 68/72 |
| UWAA | 0.805 |
| Normalized | 0.513 |
| Action accuracy | 48.5% |
| Negative utility | 3 |

**Key concern:** Model achieves normalized 0.513 despite getting the action wrong 51.5% of the time. The partial credit system (+0.3 for cautious non-answer actions) is generous — the model never selects "verify" (0 predictions), routing all verify-gold items to "abstain" for +0.3 each.

**Action distribution reveals a pattern:**
- Model uses only 3 of 4 actions (never "verify")
- 16 items where gold=abstain but model=answer (confident on unanswerable questions)
- Despite 35 action errors, only 3 produce negative utility

**Question for review:** Is the scoring too lenient? A model with random action selection scores ~0.50 UWAA. This model at 48.5% action accuracy scores 0.513 normalized — barely above the floor. The partial credit may be masking poor metacognitive control, but it also correctly rewards "safe" failures (abstaining instead of verifying is less harmful than answering incorrectly).

### 3. SC C1 (Gemma 31b, v62) — VALID, GRADING ISSUE FLAGGED

| Metric | Value |
|--------|-------|
| T1 accuracy | 27/28 (96.4%) |
| T2 accuracy | 25/28 (89.3%) |
| Delta | -0.071 |
| Normalized | 0.114 |
| Damage events | 2 |

**Net damage** — model hurts itself by reconsidering. Consistent with Huang et al. (ICLR 2024): intrinsic self-correction rarely improves.

**Damage item sc_c1_dt_001:** Model correctly answered "Yes" (trees > stars) then changed after review prompt. Classic deceptive trap — working as designed.

**Damage item sc_c1_rr_009:** T2 answer = "The original answer is sound." Grading engine treats this as a new answer that doesn't match gold="2". This is a **confirmation-without-restatement** issue — the model is maintaining its answer but not restating it. `resolve_t2_answer()` should handle this but may not be matching this phrasing pattern.

**Action needed:** Investigate whether "The original answer is sound" is caught by `resolve_t2_answer()`. If not, this is a grading bug affecting all models on this item.

### 4. SC C2 (Sonnet 4, v62) — CEILING EFFECT

| Metric | Value |
|--------|-------|
| T1 accuracy | 23/23 (100%) |
| T2 accuracy | 23/23 (100%) |
| Delta | 0.000 |
| Normalized | 0.500 |
| Damage events | 0 |

Sonnet 4 gets 100% on T1, leaving nothing to correct. C2 degenerates into a pure damage-resistance test. The 8 neutral revisions show the model engaging with the evidence but not breaking anything.

**Implication:** C2 discrimination requires models that err on T1. Strong models will all cluster at normalized ~0.5 (no delta). This is a known limitation — the Family C reliability caveat (α ≈ 0.35) reflects this.

---

## Cross-Cutting Issues

1. **Confirmation-without-restatement (C1):** The rr_009 grading needs investigation. If `resolve_t2_answer()` doesn't catch "The original answer is sound," it's a systematic grading bug.

2. **Abstention leniency:** The +0.3 partial credit for cautious non-answer actions may be too generous. A model that always abstains would score better than one that tries to answer and gets some wrong. This is by design (rewarding epistemic humility) but may reduce discrimination.

3. **C2 ceiling effect:** Expected and documented, but means C2 only separates models in the lower performance range. The composite is robust to this (equal weights, 4 tasks).

4. **Missing "verify" action:** Gemma never selects verify. This could be a model-specific issue or a prompt design issue. Need multi-model data to determine if any model uses verify.

---

## Next Steps

1. **Investigate resolve_t2_answer** for "The original answer is sound" phrasing
2. **Extract more model data** — need 5+ models to assess discrimination
3. **v61 vs v62 comparison** for overlapping models (once data extracted)
4. **Item discrimination analysis** (which items separate models?) requires full panel
