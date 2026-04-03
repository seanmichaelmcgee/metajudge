# MetaJudge v6.2 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4@20250514
**Date:** 2026-04-03 15:46 UTC
**Task:** metajudge_sc_c2_v62 | **Grading engine:** grading_v2
**Items scored:** 23/23

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 23/23 (100.0%) |
| T2 accuracy | 23/23 (100.0%) |
| T2-T1 delta | +0.0000 |
| Normalized score | 0.500 |
| Damage events | 0 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 15 |
| correction_gain | 0 |
| neutral_revision | 8 |
| damage | 0 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | +0.0000 | +0.0000 |
| Normalized | 0.500 | 0.500 |
| Items matched | 23/23 |  |
| Transition stability | 18/23 (78%) |  |
| Score range | 0.50 – 0.50 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_rr_004 | neutral_revision | maintain_correct |
| sc_c2_rr_005 | neutral_revision | maintain_correct |
| sc_c2_wc_001 | neutral_revision | maintain_correct |
| sc_c2_wc_004 | maintain_correct | neutral_revision |
| sc_c2_dt_003 | neutral_revision | maintain_correct |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c2_dt_001 | ✓ | ✓ | neutral_revision | 0.056 |
| sc_c2_dt_002 | ✓ | ✓ | neutral_revision | 0.091 |
| sc_c2_dt_003 | ✓ | ✓ | neutral_revision | 0.147 |
| sc_c2_rr_001 | ✓ | ✓ | maintain_correct | 0.098 |
| sc_c2_rr_002 | ✓ | ✓ | maintain_correct | 0.201 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | 0.108 |
| sc_c2_rr_004 | ✓ | ✓ | neutral_revision | 0.249 |
| sc_c2_rr_005 | ✓ | ✓ | neutral_revision | 0.109 |
| sc_c2_rr_006 | ✓ | ✓ | maintain_correct | 0.046 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | 0.274 |
| sc_c2_wc_001 | ✓ | ✓ | neutral_revision | 0.060 |
| sc_c2_wc_002 | ✓ | ✓ | neutral_revision | 0.152 |
| sc_c2_wc_003 | ✓ | ✓ | neutral_revision | 0.122 |
| sc_c2_wc_004 | ✓ | ✓ | maintain_correct | 0.292 |
| sc_c2_wc_005 | ✓ | ✓ | maintain_correct | 0.074 |
| sc_c2_wr_001 | ✓ | ✓ | maintain_correct | 0.102 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | 0.066 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | 0.011 |
| sc_c2_wr_008 | ✓ | ✓ | maintain_correct | 0.059 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | 0.255 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | 0.074 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | 0.238 |
| sc_c2_wr_013 | ✓ | ✓ | maintain_correct | 0.095 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 18,528 |
| Output tokens | 15,884 |
| Latency | 313.7s |
| Input cost | $0.0556 |
| Output cost | $0.2383 |
| Total cost | $0.2938 |
