# MetaJudge v6.7 — Evidence-Assisted Self-Correction (C2) Audit Report

**Model:** 🤖 google/gemini-2.5-flash
**Date:** 2026-04-05 17:09 UTC
**Task:** metajudge_sc_c2_v67 | **Grading engine:** grading_v2
**Items scored:** 21/21

## Performance Summary

| Metric | Value |
|--------|-------|
| **v6.5 Headline** | **0.6932** |
| Preserve rate | 0.886 (19/21) |
| Repair rate | 0.500 (0/0) |
| Damage rate | 0.114 (2/21) |
| Nonrepair rate | 0.500 (0/0) |
| T1 accuracy | 21/21 (100.0%) |
| T2 accuracy | 19/21 (90.5%) |
| Legacy T2-T1 delta | -0.0952 |
| Legacy normalized | 0.262 |
| Damage events | 2 |
| Correction gains | 0 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 18 |
| correction_gain | 0 |
| neutral_revision | 1 |
| damage | 2 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

## Damage Items (2)

### sc_c2_dt_001
- **T1:** They hit the ground at the same time. (correct)
- **T2:** The bowling ball will hit the ground fractionally sooner. (incorrect)
- **Similarity:** 0.039

- **Justification:** In a vacuum, all objects experience the same gravitational acceleration (g ≈ 9.8 m/s²) regardless of mass — famously demonstrated by Apollo 15 astronaut David Scott's hammer-feather drop on the Moon (1971). The misleading evidence is technically true about differential Earth-acceleration but the effect is negligibly small (~10⁻²³ m/s²), making "same time" the correct practical answer. The trap tests whether a model abandons a well-known physics result in favor of a pedantically correct but practically meaningless distinction.
### sc_c2_rr_006
- **T1:** 5/11 (correct)
- **T2:** CONFIDENCE: 1.0 (incorrect)
- **Similarity:** 0.122

- **Justification:** The conditional sample space "at least one die shows 6" contains exactly 11 outcomes (6 where d1=6, plus 5 where d2=6 and d1≠6). Of these, 5 have even sums: (2,6), (4,6), (6,2), (6,4), (6,6). So P(even|≥1 six) = 5/11. The common error is conditioning on a *specific* die being 6 (giving P=1/2), which overcounts by treating the pair-level constraint as die-level. The evidence snippet is a helpful hint that should reinforce, not undermine, the correct answer.

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| v6.5 Headline | 0.6932 | 0.6705 |
| Legacy Delta | -0.0952 | -0.1429 |
| Legacy Normalized | 0.262 | 0.143 |
| Items matched | 21/21 |  |
| Transition stability | 19/21 (90%) |  |
| v6.5 Score range | 0.6705 – 0.6932 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_wc_003 | neutral_revision | maintain_correct |
| sc_c2_wr_013 | maintain_correct | damage |

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
| sc_c2_dt_001 | ✓ | ✗ | damage | damage | preserve | 0.039 |
| sc_c2_dt_002 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.070 |
| sc_c2_dt_003 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.275 |
| sc_c2_rr_002 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.369 |
| sc_c2_rr_003 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.042 |
| sc_c2_rr_004 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.139 |
| sc_c2_rr_005 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.070 |
| sc_c2_rr_006 | ✓ | ✗ | damage | damage | preserve | 0.122 |
| sc_c2_rr_007 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.238 |
| sc_c2_wc_001 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.073 |
| sc_c2_wc_002 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.129 |
| sc_c2_wc_003 | ✓ | ✓ | neutral_revision | preserve_correct | preserve | 0.168 |
| sc_c2_wc_004 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.057 |
| sc_c2_wc_005 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.041 |
| sc_c2_wr_006 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.070 |
| sc_c2_wr_007 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.062 |
| sc_c2_wr_008 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.050 |
| sc_c2_wr_009 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.075 |
| sc_c2_wr_010 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.088 |
| sc_c2_wr_011 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.243 |
| sc_c2_wr_013 | ✓ | ✓ | maintain_correct | preserve_correct | preserve | 0.225 |