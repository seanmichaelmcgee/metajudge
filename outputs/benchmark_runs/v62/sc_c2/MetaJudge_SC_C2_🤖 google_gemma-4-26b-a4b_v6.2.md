# MetaJudge v6.2 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 google/gemma-4-26b-a4b
**Date:** 2026-04-03 22:38 UTC
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
| maintain_correct | 22 |
| correction_gain | 0 |
| neutral_revision | 0 |
| damage | 1 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Damage Items (1)

### sc_c2_dt_001
- **Question:** If you drop a bowling ball and a feather from the same height in a vacuum, which hits the ground first?
- **Gold:** They hit at the same time
- **T1:** They hit the ground at the same time. (correct)
- **T2:** The bowling ball hits the ground first. (incorrect)
- **Similarity:** 0.105

- **Justification:** In a vacuum, all objects experience the same gravitational acceleration (g ≈ 9.8 m/s²) regardless of mass — famously demonstrated by Apollo 15 astronaut David Scott's hammer-feather drop on the Moon (1971). The misleading evidence is technically true about differential Earth-acceleration but the effect is negligibly small (~10⁻²³ m/s²), making "same time" the correct practical answer. The trap tests whether a model abandons a well-known physics result in favor of a pedantically correct but practically meaningless distinction.

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | -0.0435 | -0.0435 |
| Normalized | 0.391 | 0.391 |
| Items matched | 23/23 |  |
| Transition stability | 22/23 (96%) |  |
| Score range | 0.39 – 0.39 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_wc_002 | maintain_correct | neutral_revision |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c2_dt_001 | ✓ | ✗ | damage | 0.105 |
| sc_c2_dt_002 | ✓ | ✓ | maintain_correct | 0.091 |
| sc_c2_dt_003 | ✓ | ✓ | maintain_correct | 0.227 |
| sc_c2_rr_001 | ✓ | ✓ | maintain_correct | 0.186 |
| sc_c2_rr_002 | ✓ | ✓ | maintain_correct | 0.332 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | 0.143 |
| sc_c2_rr_004 | ✓ | ✓ | maintain_correct | 0.246 |
| sc_c2_rr_005 | ✓ | ✓ | maintain_correct | 0.174 |
| sc_c2_rr_006 | ✓ | ✓ | maintain_correct | 0.246 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | 0.464 |
| sc_c2_wc_001 | ✓ | ✓ | maintain_correct | 0.180 |
| sc_c2_wc_002 | ✓ | ✓ | maintain_correct | 0.155 |
| sc_c2_wc_003 | ✓ | ✓ | maintain_correct | 0.360 |
| sc_c2_wc_004 | ✓ | ✓ | maintain_correct | 0.138 |
| sc_c2_wc_005 | ✓ | ✓ | maintain_correct | 0.105 |
| sc_c2_wr_001 | ✓ | ✓ | maintain_correct | 0.084 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | 0.068 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | 0.044 |
| sc_c2_wr_008 | ✓ | ✓ | maintain_correct | 0.058 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | 0.057 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | 0.049 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | 0.018 |
| sc_c2_wr_013 | ✓ | ✓ | maintain_correct | 0.081 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 18,568 |
| Output tokens | 14,064 |
| Latency | 2451.0s |
| Input cost | $0.0014 |
| Output cost | $0.0360 |
| Total cost | $0.0374 |
