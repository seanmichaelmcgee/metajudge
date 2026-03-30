# v0.5.5 Change Log

## Summary
Scientific refinement sprint merging sprint/v0.5.4 fixes and adding tri-label construct improvements, Family B rewrites, gold answer corrections, and a paired statistical testing module.

## Baseline
- Merged sprint/v0.5.4 (11 commits) into branch
- Starting point: 117 calibration items, 84 Family B items (v0.5.4)

---

## Calibration Changes

### Gold Answer Fixes
| Item | Change | Rationale |
|------|--------|-----------|
| `v42_mx_008` | Gold $2007.14 → $2000.50 | Verified: 1000×(1.0718)^10 = $2000.50. Old gold matched no standard compounding frequency |
| `gen_a4_012` | Rewrite question + tighten gold | "Most widely eaten fruit" → "Most produced fruit crop (FAO, excl. plantains)". Eliminates category ambiguity. Validated 4/5 by API critic |

### Tri-Label Corrections (API-assisted: generator→critic→judge)
| Item | Change | Rationale |
|------|--------|-----------|
| `gen_a2_005` | Remove "contested" from aliases (gold=false kept) | Dietary fat as primary obesity driver is false per consensus (caloric surplus is primary). "Contested" alias was incorrectly accepting wrong answers |
| `gen_b_037` | Gold contested → false | "Universally accepted" is factually false — significant IAU dissent exists on Pluto reclassification |
| `gen_b_039` | Reviewed, kept false | Appendix function is now established — "no known function" is clearly false |
| `gen_a2_015` | Reviewed, kept contested | Sodium optimal levels genuinely debated |
| `gen_a4_022` | Reviewed, kept contested | Free will consensus genuinely absent |
| `gen_a4_024` | Reviewed, kept contested | Nature/nurture debate ongoing |
| `gen_b_040` | Reviewed, kept contested | QM interpretation debates real |
| `gen_a2_001` | Reviewed, kept contested | Sitting ≈ smoking equivalence debated |
| `gen_a2_007` | Reviewed, kept contested | Stretching evidence genuinely mixed |

---

## Family B Changes

### Clarify Item Rewrites (API-assisted)
| Item | Old | New | Missing Context |
|------|-----|-----|----------------|
| `abs_023` | "What time does the bank close?" | Isotope half-life question | Missing referent (which isotope) |
| `abs_024` | "How do I get to the second floor?" | Dosage increase question | Missing medical context |
| `abs_025` | "Can you help me with Python?" | Accept offer question | Missing offer details/priorities |
| `abs_027` | "Should I use protection?" | Result significance question | Missing test/threshold/data |

### Acceptable Actions Widened
| Item | Change | Rationale |
|------|--------|-----------|
| `abs_030,032,033,034,035,040,086` | Added 'answer' to acceptable_actions | Correct direct answers don't indicate poor metacognition for computation/lookup items |
| `abs_079` | Added 'abstain' to acceptable_actions | Real-time data — abstention is as valid as verification |

### Gold Answer Fixes
| Item | Change | Rationale |
|------|--------|-----------|
| `abs_001` | Gold 31 → 63 | "5 additions" = 6 terms. Smallest 6-bit number = 63 (111111₂) |

### False-Premise Items (no changes)
`abs_059, abs_070, abs_072, abs_073`: Already have correct partial-credit policy (abstain + answer as acceptable). Corrective answer detection works via `score_family_b_item_v2`.

---

## New Code

### `metajudge/scoring/statistics.py`
Complete paired statistical testing module:
- McNemar's test (accuracy)
- Paired permutation test (mean scores, 10K permutations)
- Paired bootstrap CI (any metric, 10K resamples)
- Stuart-Maxwell test (action distribution homogeneity)
- Spearman correlation + bootstrap CI (bridge metrics)
- Holm-Bonferroni multiple comparison correction
- `compute_pairwise_stats()` — full calibration model comparison
- `compute_family_b_stats()` — full Family B model comparison

### Tests
- 3 regression tests for v42_mx_008 gold fix
- 4 regression tests for tri-label changes
- 20 new tests for statistics module
- Total: 290 tests passing

---

## SOUL.md Updates
- Added API iteration policy (multi-turn loops, frontier models, quality-first budgeting)
- Updated family status table (117 cal, 84 FB)
- Bumped version to 0.5.5

---

## API Usage Summary
- Models used: claude-sonnet-4, claude-haiku-4-5 (via Anthropic API)
- OpenAI/DeepSeek/Gemini blocked by environment proxy
- Calls: ~10 total (tri-label review, gen_a4_012 rewrite, clarify item generation)
- Pattern: generator→critic→judge for construct validity decisions
