# MetaJudge v6.1 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 google/gemma-4-26b-a4b
**Date:** 2026-04-03 04:30 UTC
**Task:** metajudge_sc_c1_v61 | **Grading engine:** grading_v2
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
| maintain_correct | 27 |
| correction_gain | 0 |
| neutral_revision | 0 |
| damage | 0 |
| stubborn_wrong | 1 |
| failed_revision | 0 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | +0.0000 | -0.0357 |
| Normalized | 0.400 | 0.257 |
| Items matched | 28/28 |  |
| Transition stability | 27/28 (96%) |  |
| Score range | 0.26 – 0.40 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_dt_006 | maintain_correct | damage |

## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 0 |
| Output tokens | 0 |
| Latency | 0.0s |
| Input cost | $0.0000 |
| Output cost | $0.0000 |
| Total cost | $0.0000 |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | maintain_correct | 0.258 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | 0.173 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 0.158 |
| sc_c1_dt_004 | ✓ | ✓ | maintain_correct | 0.899 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | 0.076 |
| sc_c1_dt_006 | ✓ | ✓ | maintain_correct | 0.084 |
| sc_c1_rr_001 | ✓ | ✓ | maintain_correct | 0.257 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | 0.089 |
| sc_c1_rr_003 | ✓ | ✓ | maintain_correct | 0.107 |
| sc_c1_rr_004 | ✓ | ✓ | maintain_correct | 0.391 |
| sc_c1_rr_005 | ✓ | ✓ | maintain_correct | 0.185 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | 0.309 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 0.180 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | 0.236 |
| sc_c1_rr_009 | ✓ | ✓ | maintain_correct | 0.174 |
| sc_c1_rr_010 | ✓ | ✓ | maintain_correct | 0.164 |
| sc_c1_wr_001 | ✓ | ✓ | maintain_correct | 0.172 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | 0.098 |
| sc_c1_wr_004 | ✓ | ✓ | maintain_correct | 0.347 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 0.124 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 0.135 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | 0.138 |
| sc_c1_wr_009 | ✓ | ✓ | maintain_correct | 0.094 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | 0.137 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | 0.079 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | 0.154 |
| sc_c1_wr_023 | ✓ | ✓ | maintain_correct | 0.180 |
| sc_c1_wr_030 | ✗ | ✗ | stubborn_wrong | 0.211 |