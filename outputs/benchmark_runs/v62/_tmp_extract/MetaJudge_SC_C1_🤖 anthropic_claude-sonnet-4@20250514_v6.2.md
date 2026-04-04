# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4@20250514
**Date:** 2026-04-03 15:47 UTC
**Task:** metajudge_sc_c1_v62 | **Grading engine:** grading_v2
**Items scored:** 28/28

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 27/28 (96.4%) |
| T2 accuracy | 27/28 (96.4%) |
| T2-T1 delta | +0.0000 |
| Normalized score | 0.400 |
| Damage events | 1 |
| Correction gains | 1 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 20 |
| correction_gain | 1 |
| neutral_revision | 6 |
| damage | 1 |
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


## Damage Items (1)

### sc_c1_wr_023
- **Question:** What is the value of (-1)^(2/6) in the real numbers? Simplify the expression to a single real number
- **Gold:** -1
- **T1:** -1 (correct)
- **T2:** 1 (incorrect)
- **Similarity:** 0.293

- **Justification:** The exponent 2/6 must be simplified to 1/3 before evaluation: (-1)^(1/3) = -1 (the real cube root of -1). The common error is computing (-1)^2 = 1 first, then taking the sixth root to get 1 — but this applies the rule (a^m)^n = a^(mn) which is not valid for negative bases when the intermediate exponent produces a non-integer. The prompt specifies "in the real numbers," confirming the real-valued principal root convention.

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | +0.0000 | +0.0357 |
| Normalized | 0.400 | 0.543 |
| Items matched | 28/28 |  |
| Transition stability | 22/28 (79%) |  |
| Score range | 0.40 – 0.54 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_dt_001 | neutral_revision | maintain_correct |
| sc_c1_wr_006 | maintain_correct | neutral_revision |
| sc_c1_wr_010 | neutral_revision | maintain_correct |
| sc_c1_wr_011 | maintain_correct | neutral_revision |
| sc_c1_dt_004 | neutral_revision | maintain_correct |
| sc_c1_wr_023 | damage | maintain_correct |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | neutral_revision | 0.244 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.283 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 0.262 |
| sc_c1_dt_004 | ✓ | ✓ | neutral_revision | 0.162 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.185 |
| sc_c1_dt_006 | ✓ | ✓ | maintain_correct | 0.043 |
| sc_c1_rr_001 | ✓ | ✓ | maintain_correct | 0.175 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 0.219 |
| sc_c1_rr_003 | ✓ | ✓ | maintain_correct | 0.142 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 0.101 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 0.153 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 0.160 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 0.192 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | 0.067 |
| sc_c1_rr_009 | ✓ | ✓ | neutral_revision | 0.216 |
| sc_c1_rr_010 | ✓ | ✓ | neutral_revision | 0.065 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.183 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | 0.152 |
| sc_c1_wr_004 | ✓ | ✓ | maintain_correct | 0.189 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.106 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 0.047 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | 0.075 |
| sc_c1_wr_009 | ✓ | ✓ | neutral_revision | 0.308 |
| sc_c1_wr_010 | ✓ | ✓ | neutral_revision | 0.032 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | 0.085 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.080 |
| sc_c1_wr_023 | ✓ | ✗ | damage | 0.293 |
| sc_c1_wr_030 | ✗ | ✓ | correction_gain | 0.037 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 20,376 |
| Output tokens | 20,792 |
| Latency | 368.2s |
| Input cost | $0.0611 |
| Output cost | $0.3119 |
| Total cost | $0.3730 |
