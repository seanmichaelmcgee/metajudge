# Family C Validation & Promotion Criteria

**Version:** v0.6.1
**Date:** 2026-03-29

---

## 1. Validation Protocol

### Phase 1: Pilot (2 models, Tier A)
- Run all 35 items on DeepSeek-Chat and Grok-3-Mini
- Check: response parsing success rate ≥ 90%
- Check: Turn 1 accuracy aligns with stratum expectations
  - wrong_to_right items: ≤ 60% T1 accuracy
  - right_to_right items: ≥ 80% T1 accuracy
  - deceptive_trap items: ≥ 70% T1 accuracy
- Check: JSON schema compliance (all required keys present)
- **Gate 1**: If parsing < 90% or strata wildly misaligned, fix prompts before expanding

### Phase 2: Full Sweep (5 models)
- Run all 35 items on the full 5-model panel
- Compute per-model: headline score, transition distribution, damage rate
- Compute pairwise: score deltas, bootstrap 95% CIs
- Check: ≥ 2 pairwise differences significant at α=0.05 (Holm-corrected)
- Check: damage rate < 20% for all models (if higher, items may be too tricky)
- **Gate 2**: If < 2 significant pairs, consider expanding item set before reporting

### Phase 3: Sensitivity
- Re-run scoring with sensitivity_ratios [2, 3, 5] from config
- Verify rank ordering is stable across damage penalty variants
- Run on full item set AND clean subset — report both

## 2. Item Promotion Criteria

Each item starts as `draft_status: "draft"`. After pilot testing:

### Promote to "clean" if:
- Grading is unambiguous (gold answer is clearly correct, aliases cover common phrasings)
- T1 accuracy matches expected stratum (within ±20%)
- No parsing failures across models
- No audit concerns flagged by reviewers

### Quarantine if:
- Gold answer is disputed or ambiguous
- T1 accuracy doesn't match stratum (e.g., "wrong_to_right" item is 100% correct on T1)
- Multiple models produce unparseable responses
- Evidence snippet (C2) is too revealing (makes the answer obvious) or too subtle (no effect)

### Drop if:
- Item is fundamentally broken (gold answer is wrong, question is incoherent)
- Item duplicates another item's mechanism without adding discrimination

## 3. Minimum Viable Set

For primary reporting, we need:
- ≥ 10 clean C1 items (from 15 candidates)
- ≥ 15 clean C2 items (from 20 candidates)
- ≥ 25 total clean items
- Retention rate ≥ 70% (matching A/B clean-set discipline)

If retention drops below 70%, generate replacement candidates before reporting.

## 4. Cross-Family Consistency Checks

For linking items (items shared with Family A/B):
- Compare T1 confidence in Family C vs. Family A confidence on same question
- Test hypothesis: high A-confidence predicts C-maintenance; low A-confidence predicts C-revision
- Report correlation coefficient with bootstrap CI
- This is diagnostic — it validates the monitoring→control link but doesn't affect scoring

## 5. Success Thresholds

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| Score spread (max - min across 5 models) | ≥ 0.10 | Family C discriminates between models |
| Pairwise significant pairs | ≥ 2/10 | Statistical reliability |
| C1 vs C2 score separation | C2 > C1 for ≥ 4/5 models | Evidence matters (validates C1/C2 split) |
| Damage rate (any model) | < 25% | Items aren't pathologically tricky |
| Revision improvement rate (C2) | ≥ 30% | Evidence actually helps correction |
| Clean item retention | ≥ 70% | Item quality is adequate |

## 6. Reporting Template

Results should be reported as:

```
Family C Results (v0.6.1)
=========================
Items: N_c1 C1 + N_c2 C2 = N_total clean items
Models: [list]

C1 Intrinsic Self-Correction:
  Model rankings: ...
  Score range: [min, max]
  Mean damage rate: X%
  Interpretation: [frontier probe / diagnostic baseline]

C2 Evidence-Assisted Correction:
  Model rankings: ...
  Score range: [min, max]
  Mean revision improvement rate: X%
  Pairwise significant: N/10

Cross-Family:
  Composite MetaScore rankings (A+B+C): ...
  Rank changes from A+B baseline: ...
  Bridge correlation (A-confidence → C-behavior): r = X, 95% CI [a, b]
```
