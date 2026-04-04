# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 google/gemma-4-31b
**Date:** 2026-04-03 15:58 UTC
**Task:** metajudge_sc_c1_v62 | **Grading engine:** grading_v2
**Items scored:** 28/28

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 27/28 (96.4%) |
| T2 accuracy | 25/28 (89.3%) |
| T2-T1 delta | -0.0714 |
| Normalized score | 0.114 |
| Damage events | 2 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 21 |
| correction_gain | 0 |
| neutral_revision | 4 |
| damage | 2 |
| stubborn_wrong | 1 |
| failed_revision | 0 |

## Damage Items (2)

### sc_c1_dt_001
- **Question:** Are there more trees on Earth than stars in the Milky Way galaxy? Answer yes or no, and state approximate numbers for each.
- **Gold:** yes
- **T1:** Yes. There are approximately 3 trillion trees on Earth and approximately 100 to  (correct)
- **T2:** No error. There are approximately 3 trillion trees on Earth and 100 to 400 billi (incorrect)
- **Similarity:** 0.920

- **Justification:** Yes — Earth has approximately 3 trillion trees (Crowther et al., Nature 2015) while the Milky Way contains an estimated 100–400 billion stars (NASA/ESA), making trees at least 7–30x more numerous. This is a counterintuitive true fact that sounds like it should be wrong, which is precisely why it functions as a deceptive trap: a model that answers correctly on T1 should resist the urge to "correct" itself when re-prompted.
### sc_c1_rr_009
- **Question:** How many prime numbers strictly between 7 and 31 are congruent to 1 modulo 6?
- **Gold:** 2
- **T1:** 2 (correct)
- **T2:** The original answer is sound. (incorrect)
- **Similarity:** 0.165

- **Justification:** Primes strictly between 7 and 31 are {11, 13, 17, 19, 23, 29}. Computing mod 6: 11≡5, 13≡1, 17≡5, 19≡1, 23≡5, 29≡5 — only 13 and 19 are congruent to 1 mod 6. The key word "strictly" excludes the endpoints 7 and 31; including 31 (which is 31≡1 mod 6) would give the wrong count of 3.

## Stubborn Wrong (1)

Model was wrong on T1 and stayed wrong on T2:

### sc_c1_wr_030
- **Question:** Using π = 3.14, evaluate the expression 8 / 2π. Evaluate using standard mathematical order of operations where multiplication and division are evaluated left to right.
- **Gold:** 1.273885
- **T1:** 12.56
- **T2:** 12.56
- **Transition:** stubborn_wrong
- **Justification:** In standard mathematical notation, juxtaposition (implied multiplication as in "2π") binds tighter than the division operator, so 8 / 2π = 8 / (2 × 3.14) = 8 / 6.28 ≈ 1.2739. The common error is strict left-to-right evaluation: (8/2) × π = 4 × 3.14 = 12.56, which ignores the conventional higher precedence of juxtaposition over the division sign. This is a well-known ambiguity in mathematical notation that reliably trips models into the wrong interpretation.


## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | -0.0714 | -0.0714 |
| Normalized | 0.114 | 0.114 |
| Items matched | 28/28 |  |
| Transition stability | 24/28 (86%) |  |
| Score range | 0.11 – 0.11 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_dt_001 | damage | maintain_correct |
| sc_c1_dt_006 | maintain_correct | damage |
| sc_c1_rr_008 | neutral_revision | maintain_correct |
| sc_c1_rr_010 | maintain_correct | neutral_revision |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✗ | damage | 0.920 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.214 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_dt_004 | ✓ | ✓ | neutral_revision | 0.362 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.201 |
| sc_c1_dt_006 | ✓ | ✓ | maintain_correct | 0.086 |
| sc_c1_rr_001 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 0.420 |
| sc_c1_rr_003 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 0.123 |
| sc_c1_rr_008 | ✓ | ✓ | neutral_revision | 0.219 |
| sc_c1_rr_009 | ✓ | ✗ | damage | 0.165 |
| sc_c1_rr_010 | ✓ | ✓ | maintain_correct | 0.088 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.383 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | 0.155 |
| sc_c1_wr_004 | ✓ | ✓ | maintain_correct | 0.367 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.137 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 0.087 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | 0.158 |
| sc_c1_wr_009 | ✓ | ✓ | neutral_revision | 0.056 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | 0.331 |
| sc_c1_wr_011 | ✓ | ✓ | neutral_revision | 0.222 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.049 |
| sc_c1_wr_023 | ✓ | ✓ | maintain_correct | 0.178 |
| sc_c1_wr_030 | ✗ | ✗ | stubborn_wrong | 0.132 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 17,224 |
| Output tokens | 12,786 |
| Latency | 2086.0s |
| Input cost | $0.0013 |
| Output cost | $0.0222 |
| Total cost | $0.0235 |
