# MetaJudge v6.2 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 google/gemini-3-flash-preview
**Date:** 2026-04-04 03:15 UTC
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
| maintain_correct | 18 |
| correction_gain | 0 |
| neutral_revision | 5 |
| damage | 0 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | +0.0000 | +0.0000 |
| Normalized | 0.500 | 0.500 |
| Items matched | 23/23 |  |
| Transition stability | 22/23 (96%) |  |
| Score range | 0.50 – 0.50 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_wr_013 | neutral_revision | maintain_correct |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c2_dt_001 | ✓ | ✓ | neutral_revision | 0.373 |
| sc_c2_dt_002 | ✓ | ✓ | maintain_correct | 0.070 |
| sc_c2_dt_003 | ✓ | ✓ | neutral_revision | 0.252 |
| sc_c2_rr_001 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_002 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_rr_004 | ✓ | ✓ | maintain_correct | 0.135 |
| sc_c2_rr_005 | ✓ | ✓ | neutral_revision | 0.203 |
| sc_c2_rr_006 | ✓ | ✓ | maintain_correct | 0.372 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | 0.232 |
| sc_c2_wc_001 | ✓ | ✓ | maintain_correct | 0.112 |
| sc_c2_wc_002 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c2_wc_003 | ✓ | ✓ | neutral_revision | 0.126 |
| sc_c2_wc_004 | ✓ | ✓ | maintain_correct | 0.130 |
| sc_c2_wc_005 | ✓ | ✓ | maintain_correct | 0.041 |
| sc_c2_wr_001 | ✓ | ✓ | maintain_correct | 0.078 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | 0.087 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | 0.139 |
| sc_c2_wr_008 | ✓ | ✓ | maintain_correct | 0.102 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | 0.100 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | 0.058 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | 0.097 |
| sc_c2_wr_013 | ✓ | ✓ | neutral_revision | 0.254 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 16,253 |
| Output tokens | 12,292 |
| Latency | 843.0s |
| Input cost | $0.0081 |
| Output cost | $0.4227 |
| Total cost | $0.4309 |
