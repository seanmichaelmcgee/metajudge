# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 google/gemini-3-flash-preview
**Date:** 2026-04-04 03:19 UTC
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
| maintain_correct | 25 |
| correction_gain | 0 |
| neutral_revision | 2 |
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
| Delta | +0.0000 | -0.0714 |
| Normalized | 0.400 | 0.114 |
| Items matched | 28/28 |  |
| Transition stability | 24/28 (86%) |  |
| Score range | 0.11 – 0.40 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_wr_004 | maintain_correct | neutral_revision |
| sc_c1_rr_003 | maintain_correct | damage |
| sc_c1_dt_006 | maintain_correct | stubborn_wrong |
| sc_c1_wr_023 | maintain_correct | damage |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | neutral_revision | 0.510 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.152 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 0.013 |
| sc_c1_dt_004 | ✓ | ✓ | neutral_revision | 0.282 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.192 |
| sc_c1_dt_006 | ✓ | ✓ | maintain_correct | 0.133 |
| sc_c1_rr_001 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_003 | ✓ | ✓ | maintain_correct | 0.097 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_009 | ✓ | ✓ | maintain_correct | 0.305 |
| sc_c1_rr_010 | ✓ | ✓ | maintain_correct | 0.060 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.089 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | 0.169 |
| sc_c1_wr_004 | ✓ | ✓ | maintain_correct | 0.623 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.081 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_wr_009 | ✓ | ✓ | maintain_correct | 0.073 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | 0.521 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | 0.053 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.299 |
| sc_c1_wr_023 | ✓ | ✓ | maintain_correct | 0.113 |
| sc_c1_wr_030 | ✗ | ✗ | stubborn_wrong | 1.000 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 15,636 |
| Output tokens | 12,553 |
| Latency | 1326.5s |
| Input cost | $0.0078 |
| Output cost | $0.6667 |
| Total cost | $0.6746 |
