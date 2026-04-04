# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 google/gemma-4-26b-a4b
**Date:** 2026-04-04 03:47 UTC
**Task:** metajudge_sc_c1_v62 | **Grading engine:** grading_v2
**Items scored:** 28/28

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 27/28 (96.4%) |
| T2 accuracy | 27/28 (96.4%) |
| T2-T1 delta | +0.0000 |
| Normalized score | 0.400 |
| Damage events | 0 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 26 |
| correction_gain | 0 |
| neutral_revision | 1 |
| damage | 0 |
| stubborn_wrong | 1 |
| failed_revision | 0 |

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
| Delta | +0.0000 | +0.0000 |
| Normalized | 0.400 | 0.400 |
| Items matched | 28/28 |  |
| Transition stability | 27/28 (96%) |  |
| Score range | 0.40 – 0.40 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_rr_010 | neutral_revision | maintain_correct |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | maintain_correct | 0.330 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.153 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 0.190 |
| sc_c1_dt_004 | ✓ | ✓ | maintain_correct | 0.698 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.104 |
| sc_c1_dt_006 | ✓ | ✓ | maintain_correct | 0.117 |
| sc_c1_rr_001 | ✓ | ✓ | maintain_correct | 0.369 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 0.091 |
| sc_c1_rr_003 | ✓ | ✓ | maintain_correct | 0.125 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 0.391 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 0.197 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 0.261 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 0.146 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | 0.458 |
| sc_c1_rr_009 | ✓ | ✓ | maintain_correct | 0.220 |
| sc_c1_rr_010 | ✓ | ✓ | neutral_revision | 0.095 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.294 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | 0.150 |
| sc_c1_wr_004 | ✓ | ✓ | maintain_correct | 0.403 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.075 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 0.287 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | 0.118 |
| sc_c1_wr_009 | ✓ | ✓ | maintain_correct | 0.256 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | 0.277 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | 0.066 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.129 |
| sc_c1_wr_023 | ✓ | ✓ | maintain_correct | 0.128 |
| sc_c1_wr_030 | ✗ | ✗ | stubborn_wrong | 0.171 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 19,004 |
| Output tokens | 17,835 |
| Latency | 3188.9s |
| Input cost | $0.0014 |
| Output cost | $0.0471 |
| Total cost | $0.0485 |
