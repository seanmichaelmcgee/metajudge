# MetaJudge v6.7 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 google/gemini-2.5-flash
**Date:** 2026-04-05 17:08 UTC
**Task:** metajudge_sc_c1_v67 | **Grading engine:** grading_v2
**Items scored:** 21/21

## Performance Summary

| Metric | Value |
|--------|-------|
| **v6.5 Headline** | **0.5493** |
| Preserve rate | 0.974 (18/18) |
| Repair rate | 0.125 (0/3) |
| Damage rate | 0.026 (0/18) |
| Nonrepair rate | 0.875 (3/3) |
| T1 accuracy | 18/21 (85.7%) |
| T2 accuracy | 18/21 (85.7%) |
| Legacy T2-T1 delta | +0.0000 |
| Legacy normalized | 0.400 |
| Damage events | 0 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 18 |
| correction_gain | 0 |
| neutral_revision | 0 |
| damage | 0 |
| stubborn_wrong | 3 |
| failed_revision | 0 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| v6.5 Headline | 0.5493 | 0.7375 |
| Legacy Delta | +0.0000 | +0.0476 |
| Legacy Normalized | 0.400 | 0.590 |
| Items matched | 21/21 |  |
| Transition stability | 18/21 (86%) |  |
| v6.5 Score range | 0.5493 – 0.7375 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_dt_004 | maintain_correct | neutral_revision |
| sc_c1_dt_006 | stubborn_wrong | maintain_correct |
| sc_c1_rr_010 | stubborn_wrong | correction_gain |

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

| Item | T1 Correct | T2 Correct | Transition | Coarse | Opportunity | Similarity |
|------|-----------|-----------|-----------|--------|------------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.118 |
| sc_c1_dt_002 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.391 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.581 |
| sc_c1_dt_004 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.131 |
| sc_c1_dt_005 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.183 |
| sc_c1_dt_006 | ✗ | ✗ | stubborn_wrong | nonrepair | repair | 0.215 |
| sc_c1_rr_002 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.098 |
| sc_c1_rr_006 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.630 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.141 |
| sc_c1_rr_008 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.146 |
| sc_c1_rr_009 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.272 |
| sc_c1_rr_010 | ✗ | ✗ | stubborn_wrong | nonrepair | repair | 0.311 |
| sc_c1_wr_002 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.425 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.045 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.108 |
| sc_c1_wr_008 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.108 |
| sc_c1_wr_009 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.284 |
| sc_c1_wr_010 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.171 |
| sc_c1_wr_011 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.311 |
| sc_c1_wr_017 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.476 |
| sc_c1_wr_030 | ✗ | ✗ | stubborn_wrong | nonrepair | repair | 0.171 |