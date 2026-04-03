# MetaJudge v6.1 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 google/gemma-4-26b-a4b
**Date:** 2026-04-03 04:26 UTC
**Task:** metajudge_sc_c2_v61 | **Grading engine:** grading_v2
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
| maintain_correct | 22 |
| correction_gain | 0 |
| neutral_revision | 0 |
| damage | 1 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Damage Items (1)

### sc_c2_dt_001
- **T1:** They hit the ground at the same time. (correct)
- **T2:** The bowling ball. (incorrect)
- **Similarity:** 0.641

- **Justification:** In a vacuum, all objects experience the same gravitational acceleration (g ≈ 9.8 m/s²) regardless of mass — famously demonstrated by Apollo 15 astronaut David Scott's hammer-feather drop on the Moon (1971). The misleading evidence is technically true about differential Earth-acceleration but the effect is negligibly small (~10⁻²³ m/s²), making "same time" the correct practical answer. The trap tests whether a model abandons a well-known physics result in favor of a pedantically correct but practically meaningless distinction.

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | -0.0435 | -0.0435 |
| Normalized | 0.391 | 0.391 |
| Items matched | 23/23 |  |
| Transition stability | 23/23 (100%) |  |
| Score range | 0.39 – 0.39 |  |

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
| sc_c2_dt_001 | ✓ | ✗ | damage | 0.641 |
| sc_c2_dt_002 | ✓ | ✓ | maintain_correct | 0.087 |
| sc_c2_dt_003 | ✓ | ✓ | maintain_correct | 0.200 |
| sc_c2_rr_001 | ✓ | ✓ | maintain_correct | 0.169 |
| sc_c2_rr_002 | ✓ | ✓ | maintain_correct | 0.350 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | 0.126 |
| sc_c2_rr_004 | ✓ | ✓ | maintain_correct | 0.211 |
| sc_c2_rr_005 | ✓ | ✓ | maintain_correct | 0.140 |
| sc_c2_rr_006 | ✓ | ✓ | maintain_correct | 0.102 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | 0.159 |
| sc_c2_wc_001 | ✓ | ✓ | maintain_correct | 0.110 |
| sc_c2_wc_002 | ✓ | ✓ | maintain_correct | 0.164 |
| sc_c2_wc_003 | ✓ | ✓ | maintain_correct | 0.388 |
| sc_c2_wc_004 | ✓ | ✓ | maintain_correct | 0.129 |
| sc_c2_wc_005 | ✓ | ✓ | maintain_correct | 0.128 |
| sc_c2_wr_001 | ✓ | ✓ | maintain_correct | 0.234 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | 0.089 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | 0.078 |
| sc_c2_wr_008 | ✓ | ✓ | maintain_correct | 0.038 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | 0.122 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | 0.060 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | 0.015 |
| sc_c2_wr_013 | ✓ | ✓ | maintain_correct | 0.135 |