# MetaJudge v6.2 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4-6@default
**Date:** 2026-04-04 02:59 UTC
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
| maintain_correct | 19 |
| correction_gain | 0 |
| neutral_revision | 4 |
| damage | 0 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | +0.0000 | -0.0435 |
| Normalized | 0.500 | 0.391 |
| Items matched | 23/23 |  |
| Transition stability | 21/23 (91%) |  |
| Score range | 0.39 – 0.50 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_rr_004 | maintain_correct | neutral_revision |
| sc_c2_dt_001 | neutral_revision | damage |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c2_dt_001 | ✓ | ✓ | neutral_revision | 0.063 |
| sc_c2_dt_002 | ✓ | ✓ | maintain_correct | 0.111 |
| sc_c2_dt_003 | ✓ | ✓ | maintain_correct | 0.083 |
| sc_c2_rr_001 | ✓ | ✓ | maintain_correct | 0.093 |
| sc_c2_rr_002 | ✓ | ✓ | neutral_revision | 0.113 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | 0.081 |
| sc_c2_rr_004 | ✓ | ✓ | maintain_correct | 0.269 |
| sc_c2_rr_005 | ✓ | ✓ | maintain_correct | 0.103 |
| sc_c2_rr_006 | ✓ | ✓ | maintain_correct | 0.085 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | 0.191 |
| sc_c2_wc_001 | ✓ | ✓ | maintain_correct | 0.086 |
| sc_c2_wc_002 | ✓ | ✓ | maintain_correct | 0.113 |
| sc_c2_wc_003 | ✓ | ✓ | neutral_revision | 0.079 |
| sc_c2_wc_004 | ✓ | ✓ | maintain_correct | 0.038 |
| sc_c2_wc_005 | ✓ | ✓ | neutral_revision | 0.035 |
| sc_c2_wr_001 | ✓ | ✓ | maintain_correct | 0.220 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | 0.099 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | 0.120 |
| sc_c2_wr_008 | ✓ | ✓ | maintain_correct | 0.091 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | 0.199 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | 0.212 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | 0.265 |
| sc_c2_wr_013 | ✓ | ✓ | maintain_correct | 0.043 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 16,993 |
| Output tokens | 12,819 |
| Latency | 325.6s |
| Input cost | $0.0510 |
| Output cost | $0.1923 |
| Total cost | $0.2433 |
