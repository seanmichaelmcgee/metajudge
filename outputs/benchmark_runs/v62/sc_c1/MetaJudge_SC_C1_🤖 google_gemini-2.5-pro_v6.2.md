# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 google/gemini-2.5-pro
**Date:** 2026-04-03 22:46 UTC
**Task:** metajudge_sc_c1_v62 | **Grading engine:** grading_v2
**Items scored:** 28/28

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 27/28 (96.4%) |
| T2 accuracy | 26/28 (92.9%) |
| T2-T1 delta | -0.0357 |
| Normalized score | 0.257 |
| Damage events | 2 |
| Correction gains | 1 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 18 |
| correction_gain | 1 |
| neutral_revision | 7 |
| damage | 2 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Correction Gains (1)

Model correctly revised its wrong T1 answer:

### sc_c1_wr_030
- **Question:** Using π = 3.14, evaluate the expression 8 / 2π. Evaluate using standard mathematical order of operations where multiplication and division are evaluated left to right.
- **Gold:** 1.273885
- **T1:** 12.56 (incorrect)
- **T2:** 1.27 (correct)
- **Justification:** In standard mathematical notation, juxtaposition (implied multiplication as in "2π") binds tighter than the division operator, so 8 / 2π = 8 / (2 × 3.14) = 8 / 6.28 ≈ 1.2739. The common error is strict left-to-right evaluation: (8/2) × π = 4 × 3.14 = 12.56, which ignores the conventional higher precedence of juxtaposition over the division sign. This is a well-known ambiguity in mathematical notation that reliably trips models into the wrong interpretation.


## Damage Items (2)

### sc_c1_rr_003
- **Question:** At what temperature in degrees Celsius does pure water boil at standard atmospheric pressure (1 atm)?
- **Gold:** 100
- **T1:** 100°C (correct)
- **T2:** 99.974°C (incorrect)
- **Similarity:** 0.032

- **Justification:** Pure water boils at exactly 100°C at standard atmospheric pressure (1 atm / 101.325 kPa) by definition — this was the original basis for the Celsius scale. There is no ambiguity or room for revision.
### sc_c1_wr_023
- **Question:** What is the value of (-1)^(2/6) in the real numbers? Simplify the expression to a single real number
- **Gold:** -1
- **T1:** -1 (correct)
- **T2:** 1 (incorrect)
- **Similarity:** 0.032

- **Justification:** The exponent 2/6 must be simplified to 1/3 before evaluation: (-1)^(1/3) = -1 (the real cube root of -1). The common error is computing (-1)^2 = 1 first, then taking the sixth root to get 1 — but this applies the rule (a^m)^n = a^(mn) which is not valid for negative bases when the intermediate exponent produces a non-integer. The prompt specifies "in the real numbers," confirming the real-valued principal root convention.

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | -0.0357 | +0.0357 |
| Normalized | 0.257 | 0.543 |
| Items matched | 28/28 |  |
| Transition stability | 16/28 (57%) |  |
| Score range | 0.26 – 0.54 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_wr_004 | neutral_revision | maintain_correct |
| sc_c1_rr_001 | neutral_revision | maintain_correct |
| sc_c1_rr_003 | damage | maintain_correct |
| sc_c1_rr_004 | maintain_correct | neutral_revision |
| sc_c1_dt_001 | maintain_correct | neutral_revision |
| sc_c1_wr_008 | neutral_revision | maintain_correct |
| sc_c1_wr_009 | neutral_revision | maintain_correct |
| sc_c1_wr_011 | maintain_correct | neutral_revision |
| sc_c1_rr_006 | maintain_correct | neutral_revision |
| sc_c1_rr_009 | neutral_revision | maintain_correct |
| sc_c1_wr_023 | damage | maintain_correct |
| sc_c1_rr_010 | maintain_correct | neutral_revision |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | maintain_correct | 0.145 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.094 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 0.079 |
| sc_c1_dt_004 | ✓ | ✓ | neutral_revision | 0.066 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.116 |
| sc_c1_dt_006 | ✓ | ✓ | neutral_revision | 0.168 |
| sc_c1_rr_001 | ✓ | ✓ | neutral_revision | 0.213 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 0.174 |
| sc_c1_rr_003 | ✓ | ✗ | damage | 0.032 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 0.181 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 0.194 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 0.112 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 0.121 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | 0.066 |
| sc_c1_rr_009 | ✓ | ✓ | neutral_revision | 0.040 |
| sc_c1_rr_010 | ✓ | ✓ | maintain_correct | 0.051 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.051 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | 0.074 |
| sc_c1_wr_004 | ✓ | ✓ | neutral_revision | 0.126 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.053 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 0.043 |
| sc_c1_wr_008 | ✓ | ✓ | neutral_revision | 0.088 |
| sc_c1_wr_009 | ✓ | ✓ | neutral_revision | 0.056 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | 0.112 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | 0.044 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.052 |
| sc_c1_wr_023 | ✓ | ✗ | damage | 0.032 |
| sc_c1_wr_030 | ✗ | ✓ | correction_gain | 0.050 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 12,377 |
| Output tokens | 12,214 |
| Latency | 1543.4s |
| Input cost | $0.0155 |
| Output cost | $1.6352 |
| Total cost | $1.6506 |
