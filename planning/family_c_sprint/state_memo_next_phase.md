# Family C Next-Phase State Recovery Memo

## Branch and Commit State
- Branch: `hardening/family-c-v0.6.2`
- Latest commit: `050ca04` — "Hardening v0.6.2: corrected sweep analysis + Gemini rerun + WR item audit"
- Total commits since main: 15
- PR: #16

## Current Baseline (corrected sweep)
- Grading bug: **RESOLVED** (`extract_first_number` fixed in `scripts/regrade_sweep_v062.py`)
- 61/225 grades corrected (27% error rate in original grader)
- Original grader systematically under-counted correct answers by ~30 percentage points

### Corrected Model Performance (45 clean items)
| Model | T1 Acc | T2 Acc | W→R | R→W | SC Rate | Damage Rate |
|-------|--------|--------|-----|-----|---------|-------------|
| **Claude Sonnet 4.5** | **91.1%** | **93.3%** | 2 | 1 | **50.0%** (2/4) | 2.4% |
| Grok 3 Mini | 88.9% | 88.9% | 0 | 0 | 0.0% (0/5) | 0.0% |
| GPT-4.1 | 84.4% | 88.9% | 2 | 0 | 28.6% (2/7) | 0.0% |
| DeepSeek Chat | 80.0% | 88.9% | 4 | 0 | 44.4% (4/9) | 0.0% |
| Gemini 2.5 Pro (rerun) | 86.7% | 82.2% | 0 | 2† | 0.0% (0/6) | 5.1%† |

†Gemini R→W items are truncation artifacts (empty T2 responses), not genuine model errors. True damage rate likely 0%.

## Current Item Inventory
| Metric | Count |
|--------|-------|
| C1 total | 35 |
| C1 clean | 33 |
| C1 quarantine | 2 |
| C1 WR clean | 15 |
| C2 total | 32 |
| C2 clean | 28 |
| C2 quarantine | 4 |
| C2 WR clean | 13 |
| **Total items** | **67** |
| **Total clean** | **61** |
| Total quarantine | 6 |
| Total WR clean | 28 |
| Items in 5-model sweep | 45 |
| Items with T1 acc > 80% | 27 / 45 (60%) |

## WR Item Problem
- 16 WR-stratum items tested in the 5-model sweep
- **12 of 16 WR items have T1 accuracy ≥ 80%** — models rarely get them wrong on T1, so there is no "wrong" to self-correct from
- **0 WR items show genuine WR transition across ≥ 2 reliable models**
- 1 WR item (sc_c1_wr_004) is R→R across all 5 models (100% T1, completely trivial)
- Only 3 items (sc_c1_wr_001, sc_c1_wr_009, sc_c1_wr_010) have T1 accuracy ≤ 60% — approaching the 40-60% sweet spot
- **Core issue:** Items designed as "wrong_to_right" are too easy at T1 — need new items targeting 40-60% T1 accuracy
- Must use multi-turn adversarial generation loops, not one-shot item creation

### WR Item Detail
| Item ID | T1 Acc | Actual WR Count | Status |
|---------|--------|-----------------|--------|
| sc_c1_wr_004 | 100% | 0/5 | Too easy — quarantine candidate |
| sc_c1_wr_002 | 80% | 0/5 | Too easy |
| sc_c1_wr_006 | 80% | 0/5 | Too easy |
| sc_c1_wr_007 | 80% | 1/5 | Marginal |
| sc_c1_wr_008 | 100% | 0/5 | Too easy |
| sc_c1_wr_011 | 100% | 0/5 | Too easy |
| sc_c1_wr_001 | 60% | 1/5 | Viable — needs harder evidence |
| sc_c1_wr_009 | 60% | 1/5 | Viable |
| sc_c1_wr_010 | 60% | 1/5 | Viable |
| sc_c2_wr_001 | 100% | 0/5 | Too easy |
| sc_c2_wr_006 | 40% | 0/5 | Hard but no WR |
| sc_c2_wr_007 | 80% | 1/5 | Too easy |
| sc_c2_wr_008 | 100% | 0/5 | Too easy |
| sc_c2_wr_009 | 80% | 0/5 | Too easy |
| sc_c2_wr_010 | 100% | 0/5 | Too easy |
| sc_c2_wr_011 | 100% | 0/5 | Too easy |

## Remaining Grading Edge Cases
1. **Gemini truncation:** Even with max_tokens=4096 rerun, 2 items still produce near-empty T2 responses. Need to set max_tokens=8192 or use `thinking` budget separation for Gemini specifically.
2. **"No" in yes/no grading:** `grade_yes_no_v2` checks `has_no and not has_yes`, but "No, actually..." could appear in a yes-answer context. Edge case is low-frequency but real.
3. **Fraction equivalence:** `grade_fraction_or_decimal_v2` handles `a/b` format but not LaTeX fractions (`\frac{a}{b}`).
4. **Multi-answer items:** Current grader assumes single gold answer per item. Items with multiple valid forms (e.g., "1081" vs "1,081" vs "one thousand eighty-one") rely on aliases list being complete.
5. **Unit handling:** Grader does not parse units — "1081 km" vs "1081 miles" would both match the number 1081. Not currently an issue but could become one with physics/chemistry items.

## Corrected Sweep Output Files
| File | Lines | Size | Status |
|------|-------|------|--------|
| `outputs/family_c/sweep_regraded_v062.jsonl` | 225 | 232K | ✓ Parseable |
| `outputs/family_c/sweep_regrade_changes_v062.json` | 1160 | 84K | ✓ 61 changes |
| `outputs/family_c/sweep_analysis_v062.md` | 354 | 20K | ✓ Complete |
| `outputs/family_c/sweep_cross_model_v062.csv` | 46 | 4K | ✓ 45 items × 5 models |
| `outputs/family_c/sweep_raw_gemini-2-5-pro-rerun.jsonl` | 45 | 48K | ✓ Parseable |
| `scripts/regrade_sweep_v062.py` | 788 | 32K | ✓ Improved grader |

## Exact Next Step
**Phase 1: Freeze grading semantics for generation sprint**
- Lock down grader behavior with unit tests before generating new items
- Define target T1 accuracy range (40-60%) for WR items
- Design adversarial generation pipeline for items that are genuinely hard at T1
