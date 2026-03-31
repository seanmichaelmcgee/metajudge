# Sprint v2 Phase 6 Checkpoint

**Date:** 2026-03-31
**Branch:** `sprint/family-c-v2`
**Status:** Sprint v2 complete. All 6 phases done.

## Branch State

- Base: `main` (commit 2e4d195)
- Branch: `sprint/family-c-v2`
- All changes committed and pushed

## Sprint v2 Commits

| Phase | Commit | Summary |
|-------|--------|---------|
| Phase 1a | 973ff22 | Scoring rescale fix + C2 damage ratio + grading rule fixes |
| Phase 1b | 59934d6 | Grading improvements + test updates — all 66 tests green |
| Phase 2a | 02bbc8e | New sweep_v2.py — redesigned protocol (C1 third-person, C2 reviewer's note, B0, confidence, edit-distance) |
| Phase 2b | 380e8ff | Smoke test passed — 3 items x 1 model, all fields populated |
| Phase 3 | 3674784 | Validation sweep — 5 models x 45 items + paired protocol comparison |
| Phase 3 helper | a7e7ecb | Single-model sweep helper for parallel execution |
| Phase 4 | 776c2f5 | Item generation pipeline (author -> adversary -> canary -> frontier) |
| Phase 4 batch 1 | b32d02d | 8 accepted from 16 generated (50% accept rate) |
| Phase 4 batch 2-3 | 1d35510 | 11 total accepted items across all batches |
| Phase 5 merge | 1f793b5 | Merge 11 new items into candidates + expand B0 diagnostic subset |
| Phase 5 sweep | 098353e | Integrated sweep — 56 items x 4 models, new protocol |
| Phase 6 | (this) | Full analysis with bootstrap CIs + writeup draft + checkpoint |

## Dataset Counts

| Category | Count | Details |
|----------|-------|---------|
| **Clean items** | 45 | Original v0.6.2 set (C1: 23, C2: 22) |
| **Draft items (Phase 4)** | 11 | Accepted via author -> adversary -> canary -> frontier pipeline |
| **Total swept** | 56 | 45 clean + 11 draft |
| **Quarantined** | 6 | From v0.6.2 Phase 2 (too easy for frontier) |
| **Models swept** | 4 | Sonnet 4.6, Gemini Flash, GPT-5-mini, GPT-5.2 |
| **Total trials** | 224 | 56 items x 4 models |
| **B0 diagnostic subset** | 25 | WR items with re-answering baseline |

## Key Metrics Summary

### Headline (Bootstrap 95% CIs)

| Model | T1 Acc | T2 Acc | T2-T1 Delta | SC Rate | Damage Rate |
|-------|--------|--------|-------------|---------|-------------|
| Sonnet 4.6 | 83.9% | 85.7% | +1.8% [-4, 9] | 22% (2/9) | 2.1% (1/47) |
| Gemini Flash | 78.6% | 85.7% | +7.1% [-2, 18] | 50% (6/12) | 4.5% (2/44) |
| GPT-5-mini | 85.7% | 83.9% | -1.8% [-5, 0] | 0% (0/8) | 2.1% (1/48) |
| GPT-5.2 | 87.5% | 85.7% | -1.8% [-7, 4] | 14% (1/7) | 4.1% (2/49) |

### B0 Baseline (WR subset)

| Model | T2 Acc | B0 Acc | C1-B0 Delta |
|-------|--------|--------|-------------|
| Gemini Flash | 84% | 64% | **+20%** |
| Others | 84% | 84-88% | 0% to -4% |

### Key Finding

Gemini-flash is the only model showing genuine metacognitive correction: +20% C1-B0 delta on the WR subset, meaning the review protocol adds substantial value beyond re-sampling.

## Phase Completion Status

- [x] Phase 1: Scoring + grading fixes (rescale, C2 damage ratio, rule fixes, tests green)
- [x] Phase 2: New sweep protocol (third-person C1, reviewer's note C2, B0, confidence, edit-distance)
- [x] Phase 3: Validation sweep (5 models x 45 items, paired protocol comparison)
- [x] Phase 4: Item generation (11 accepted via 4-stage pipeline)
- [x] Phase 5: Integrated sweep (56 items x 4 models = 224 trials)
- [x] Phase 6: Full analysis + writeup draft + checkpoint

## Artifacts Produced This Sprint

| Artifact | Path |
|----------|------|
| Sweep script | `scripts/sweep_v2.py` |
| Phase 6 analysis script | `scripts/phase6_analysis.py` |
| Phase 5 JSONL (4 files) | `outputs/family_c/sweep_v2_phase5/` |
| Phase 5 summary | `outputs/family_c/sweep_v2_phase5/phase5_analysis.md` |
| Phase 6 full analysis | `outputs/family_c/sweep_v2_phase5/phase6_full_analysis.md` |
| Writeup draft | `outputs/family_c/family_c_writeup_draft.md` |
| This checkpoint | `planning/family_c_sprint/checkpoint_sprint_v2_phase6.md` |

## What's Remaining (Post-Sprint)

1. **Merge to main** — PR from `sprint/family-c-v2` into `main`
2. **Promote draft items** — 11 Phase 4 items need formal promotion from draft to clean after additional validation
3. **DeepSeek-R1 retry** — Timed out during Phase 5; retry with longer timeout or API workaround
4. **Expand model panel** — Add 2-3 more models for broader coverage
5. **Confidence discrimination** — Investigate alternative confidence elicitation to break the 92-99% ceiling
6. **Integration with Families A/B** — Compute composite MetaJudge scores across all three families
