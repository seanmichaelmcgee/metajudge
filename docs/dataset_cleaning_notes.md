# MetaJudge v0.5.5.1 — Dataset Cleaning Notes

## Summary

The clean benchmark subset excludes 24 items (12 calibration + 12 Family B) from
the full 201-item benchmark, producing a 177-item primary reporting set.

## Exclusion Criteria

### Calibration (12 items excluded, 105 remaining)

**Criterion**: Items where >= 3 of 5 models answered incorrectly.

**Rationale**: When the majority of frontier models fail an item, it suggests
a potential problem with the item itself (ambiguous wording, disputed answer,
temporal brittleness, or excessive difficulty that measures knowledge rather
than metacognition). Individual model failures are not grounds for exclusion —
only systematic failures across the model panel.

**Coverage impact**: All 10 mechanisms retained. Minimum retention: RLHF at
67% (2/3 items). Eight mechanisms retain >= 80% of items.

| Mechanism | Total | Clean | % Kept |
|-----------|-------|-------|--------|
| AmbiguityMetacognition | 14 | 12 | 86% |
| Anchoring | 10 | 9 | 90% |
| CodeExecution | 16 | 15 | 94% |
| Compositional | 17 | 17 | 100% |
| ConditionalTemporal | 7 | 6 | 86% |
| IOED | 2 | 2 | 100% |
| ModifiedCRT | 18 | 15 | 83% |
| MonitoringTrap | 20 | 17 | 85% |
| Prototype | 10 | 10 | 100% |
| RLHF | 3 | 2 | 67% |

### Family B (12 items excluded, 72 remaining)

**Criterion**: Items flagged as "verify_but_answered" in the audit review queue.

**Rationale**: These items have a gold action of "verify" but multiple models chose
to answer directly. This suggests the verify/answer boundary may be ambiguous for
these items, making utility scoring less reliable.

**Coverage impact**: Only the "verify" action is affected (reduced from 27 to 15).
Answer, clarify, and abstain are fully retained.

| Gold Action | Total | Clean | % Kept |
|-------------|-------|-------|--------|
| answer | 15 | 15 | 100% |
| clarify | 13 | 13 | 100% |
| verify | 27 | 15 | 56% |
| abstain | 29 | 29 | 100% |

## Warnings

1. **RLHF mechanism**: Only 2 items remain — treat as exploratory/descriptive only
2. **Verify action**: 56% retention is adequate but at the lower bound; monitor if
   further items are excluded
3. **Full dataset required**: All analyses must also be run on the full 117/84 set
   as sensitivity checks

## Manifest Location

Machine-readable: `data/clean_subset_manifest.json`

## Sensitivity Analysis Policy

Primary claims use the clean subset. Full-set results are reported in:
- Sensitivity analysis section of the stats report
- Appendix tables in the public narrative notebook
- Reproducibility log references both runs
