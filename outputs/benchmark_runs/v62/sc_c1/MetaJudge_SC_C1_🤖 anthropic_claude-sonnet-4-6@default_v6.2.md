# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4-6@default
**Date:** 2026-04-04 02:59 UTC
**Task:** metajudge_sc_c1_v62 | **Grading engine:** grading_v2
**Items scored:** 28/28

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 27/28 (96.4%) |
| T2 accuracy | 26/28 (92.9%) |
| T2-T1 delta | -0.0357 |
| Normalized score | 0.257 |
| Damage events | 1 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 22 |
| correction_gain | 0 |
| neutral_revision | 4 |
| damage | 1 |
| stubborn_wrong | 1 |
| failed_revision | 0 |

## Damage Items (1)

### sc_c1_wr_023
- **Question:** What is the value of (-1)^(2/6) in the real numbers? Simplify the expression to a single real number
- **Gold:** -1
- **T1:** -1 (correct)
- **T2:** 1 (incorrect)
- **Similarity:** 0.106

- **Justification:** The exponent 2/6 must be simplified to 1/3 before evaluation: (-1)^(1/3) = -1 (the real cube root of -1). The common error is computing (-1)^2 = 1 first, then taking the sixth root to get 1 — but this applies the rule (a^m)^n = a^(mn) which is not valid for negative bases when the intermediate exponent produces a non-integer. The prompt specifies "in the real numbers," confirming the real-valued principal root convention.

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
| Delta | -0.0357 | -0.0357 |
| Normalized | 0.257 | 0.257 |
| Items matched | 28/28 |  |
| Transition stability | 23/28 (82%) |  |
| Score range | 0.26 – 0.26 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_wr_002 | neutral_revision | maintain_correct |
| sc_c1_wr_004 | maintain_correct | neutral_revision |
| sc_c1_dt_001 | neutral_revision | maintain_correct |
| sc_c1_wr_017 | maintain_correct | stubborn_wrong |
| sc_c1_rr_010 | maintain_correct | neutral_revision |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | neutral_revision | 0.387 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.272 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 0.170 |
| sc_c1_dt_004 | ✓ | ✓ | neutral_revision | 0.101 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.413 |
| sc_c1_dt_006 | ✓ | ✓ | neutral_revision | 0.073 |
| sc_c1_rr_001 | ✓ | ✓ | maintain_correct | 0.163 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 0.703 |
| sc_c1_rr_003 | ✓ | ✓ | maintain_correct | 0.208 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 0.164 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 0.254 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 0.206 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 0.081 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | 0.358 |
| sc_c1_rr_009 | ✓ | ✓ | maintain_correct | 0.238 |
| sc_c1_rr_010 | ✓ | ✓ | maintain_correct | 0.260 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.469 |
| sc_c1_wr_002 | ✓ | ✓ | neutral_revision | 0.054 |
| sc_c1_wr_004 | ✓ | ✓ | maintain_correct | 0.153 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.174 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 0.306 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | 0.334 |
| sc_c1_wr_009 | ✓ | ✓ | maintain_correct | 0.254 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | 0.240 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | 0.157 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.260 |
| sc_c1_wr_023 | ✓ | ✗ | damage | 0.106 |
| sc_c1_wr_030 | ✗ | ✗ | stubborn_wrong | 0.189 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 17,473 |
| Output tokens | 14,434 |
| Latency | 307.8s |
| Input cost | $0.0524 |
| Output cost | $0.2165 |
| Total cost | $0.2689 |
