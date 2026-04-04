# Pipeline Evaluation — Aggregate Analysis

**Model:** Gemini 2.5 Pro | **Version:** v6.2
**Scope:** All 228 item responses across 4 tasks + 123 stochasticity records

---

## 1. Score Summary

| Task | Items | Raw Metric | Normalized | Notes |
|------|-------|-----------|------------|-------|
| Calibration | 105 | 1-Brier = 0.9480 | 0.792 | 2 grading errors found |
| Calibration (corrected) | 105 | 1-Brier = 0.9670 | **0.868** | After tri_label fix |
| Abstention | 72 | UWAA = 0.7042 | 0.260 | |
| SC C1 | 28 | Delta = -0.0357 | 0.257 | |
| SC C2 | 23 | Delta = -0.0870 | 0.283 | |
| **MetaScore** | **228** | | **0.398** | |
| **MetaScore (corrected)** | **228** | | **0.417** | After grading fix |

## 2. Grading Pipeline Assessment

### Findings

| Check | Result | Impact |
|-------|--------|--------|
| Brier computation (105 items) | ✅ 0 errors | None |
| Numeric tolerance grading | ✅ All borderline cases correct | None |
| Case/format normalization | ✅ Working | None |
| tri_label accepted_forms | ❌ Bug: not checked | +0.0190 Brier, +0.076 normalized |
| Abstention utility computation | ✅ All 72 verified | None |
| Corrective-answer detection | ✅ Working | None |
| SC transition classification | ✅ Consistent with (t1,t2,revised) | None |
| Confirmation detection | ⚠️ 1 gap (sc_c2_wc_005) | Minor — may affect 1 item |

**Overall grading accuracy:** 226/228 items correctly graded (99.1%).
2 errors from tri_label bug (now fixed). 1 borderline case (sc_c2_wc_005).

## 3. Stochasticity Assessment

| Task | Run 1 Norm | Run 2 Norm | Δ | Stability | Concern |
|------|-----------|-----------|---|-----------|---------|
| Calibration | 0.792 | — | — | N/A (single run) | None |
| Abstention | 0.260 | 0.194 | 0.066 | 60/72 | ⚠️ Moderate |
| SC C1 | 0.257 | 0.543 | 0.286 | see audit | 🔴 High |
| SC C2 | 0.283 | 0.283 | 0.000 | see audit | ✅ Low |

## 4. Score Validity Assessment

### Calibration: VALID ✅
- Brier rule correctly implemented, 0 computation errors
- Meaningful spread: 6 wrong items across diverse categories
- Overconfidence penalty working (5 items at conf≥0.9 wrong)
- **Fix needed:** tri_label accepted_forms (applied, re-upload pending)
- Corrected score: 0.792 → 0.868

### Abstention: VALID WITH CAVEATS ⚠️
- All utility scores verified correct
- Action accuracy only 38.9% but UWAA = 0.704 — partial credit system is generous
- Model over-answers (53/72 = 73.6%): prefers answering over epistemic actions
- 17 negative utility items — penalties are justified
- **Caveat:** Low action accuracy producing moderate UWAA suggests the scoring
  may not discriminate well between models that over-answer vs models with
  genuinely poor action selection. Need multi-model comparison to confirm.

### SC C1: VALID BUT LOW PRECISION ⚠️
- Transition classification correct for all 28 items
- Net damage (-0.0357) consistent with Huang et al. prediction
- **High stochasticity:** Run 1→Run 2 swing of 0.286 normalized
- n=28 produces coarse delta resolution: each item flip = 0.0357 delta change
- Score of 0.257 is one of multiple models scoring exactly 0.257 (-1/28 delta)
- **Implication:** C1 scores should not be used for fine-grained ranking

### SC C2: VALID WITH CEILING EFFECT ⚠️
- 100% T1 accuracy leaves nothing to correct — only tests damage resistance
- Both damage events are deceptive traps working as designed
- Model susceptible to authoritative-sounding misleading evidence
- **Ceiling effect:** Strong models cluster at ~0.5 (no delta)
- **Implication:** C2 only discriminates in the lower performance range

## 5. Composite MetaScore Assessment

**MetaScore: 0.417** (corrected)

The MetaScore captures a real phenomenon: Gemini 2.5 Pro has a
**monitoring-control gap**. Strong calibration (0.868) paired with
weak control (0.260, 0.257, 0.283) means the model knows
when it's right but doesn't act on that knowledge.

### Equal-weight validity
Equal weighting gives calibration 25% influence. If calibration were weighted
higher (e.g., 40%), the MetaScore would be 0.507.
If control tasks were weighted higher (10% cal, 30% each control),
it would be 0.327.
The equal-weight score (0.417) sits between these extremes.

## 6. Pipeline Recommendations

1. **Deploy tri_label fix** — re-upload package, re-run models (done in code, pending upload)
2. **Add sc_c2_wc_005 confirmation phrase** if pattern recurs across models
3. **Report C1 scores with CI** — n=28 is too small for precision; report score ± stochasticity range
4. **Multi-model comparison needed** — single-model audit validates the pipeline mechanics but cannot assess discrimination. Need 5+ models to evaluate whether score differences are meaningful.
5. **Consider abstention scoring calibration** — 38.9% action accuracy → 0.260 normalized may be overly compressed by the anchor range. Compare across models before adjusting.