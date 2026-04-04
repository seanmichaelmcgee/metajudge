# MetaJudge v6.2 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 openai/gpt-5.4-2026-03-05
**Date:** 2026-04-04 03:25 UTC
**Task:** metajudge_sc_c2_v62 | **Grading engine:** grading_v2
**Items scored:** 23/23

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 23/23 (100.0%) |
| T2 accuracy | 22/23 (95.7%) |
| T2-T1 delta | -0.0435 |
| Normalized score | 0.391 |
| Damage events | 1 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 16 |
| correction_gain | 0 |
| neutral_revision | 6 |
| damage | 1 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Damage Items (1)

### sc_c2_wr_008
- **Question:** A car's odometer reads 15951 miles, which is a palindrome. What is the minimum number of miles the car must drive before the odometer shows the next palindrome?
- **Gold:** 110
- **T1:** 110 miles (correct)
- **T2:** 11 miles (incorrect)
- **Similarity:** 0.986

- **Justification:** 15951 is the palindrome 1-5-9-5-1. Since C=9 is maxed, incrementing requires a carry: B goes from 5 to 6, C resets to 0, giving 1-6-0-6-1 = 16061. The gap is 16061 - 15951 = 110. The common error is answering 10 (claiming 15961 is next, but 15961 reversed is 16951, not a palindrome). The evidence snippet explicitly describes the carry-propagation rule, providing the key insight for self-correction.

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | -0.0435 | +0.0000 |
| Normalized | 0.391 | 0.500 |
| Items matched | 23/23 |  |
| Transition stability | 20/23 (87%) |  |
| Score range | 0.39 – 0.50 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_wc_002 | neutral_revision | maintain_correct |
| sc_c2_wr_008 | damage | maintain_correct |
| sc_c2_rr_006 | maintain_correct | failed_revision |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c2_dt_001 | ✓ | ✓ | neutral_revision | 0.163 |
| sc_c2_dt_002 | ✓ | ✓ | maintain_correct | 0.912 |
| sc_c2_dt_003 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_001 | ✓ | ✓ | maintain_correct | 0.933 |
| sc_c2_rr_002 | ✓ | ✓ | neutral_revision | 0.911 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_004 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_005 | ✓ | ✓ | maintain_correct | 0.973 |
| sc_c2_rr_006 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wc_001 | ✓ | ✓ | maintain_correct | 0.927 |
| sc_c2_wc_002 | ✓ | ✓ | neutral_revision | 0.353 |
| sc_c2_wc_003 | ✓ | ✓ | neutral_revision | 0.142 |
| sc_c2_wc_004 | ✓ | ✓ | neutral_revision | 0.408 |
| sc_c2_wc_005 | ✓ | ✓ | neutral_revision | 0.203 |
| sc_c2_wr_001 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wr_008 | ✓ | ✗ | damage | 0.986 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wr_013 | ✓ | ✓ | maintain_correct | 1.000 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 12,416 |
| Output tokens | 1,869 |
| Latency | 62.0s |
| Input cost | $0.0310 |
| Output cost | $0.0280 |
| Total cost | $0.0591 |
