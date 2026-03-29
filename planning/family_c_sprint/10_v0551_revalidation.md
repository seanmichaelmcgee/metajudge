# Family C Sprint: v0.5.5.1.1 Revalidation Note

**Status:** Revalidation of sprint plans against v0.5.5.1.1 clean-subset results
**Date:** 2026-03-29
**Source:** outputs/results-narrative-v0.5.5.1.1.zip (merged from main dd877e7)

---

## 1. What Changed from v0.5.1 to v0.5.5.1.1

The v0.5.5.1.1 results use the **clean subset** (105 calibration items, 72 Family B items)
after excluding 12+12 suspect items via `clean_subset_manifest.json`.

| Metric | v0.5.1 (full set) | v0.5.5.1.1 (clean set) | Delta |
|--------|-------------------|------------------------|-------|
| Cal items | 117 | 105 | -12 excluded |
| FB items | 87 (1 model) | 72 (5 models) | -15 excluded, +4 models |
| Top accuracy | Flash 87.2% | Flash 95.2% | +8% (harder items removed) |
| MetaScore range | N/A (single model FB) | 0.80-0.88 | Now computable |

**Family B is now a full 5-model comparison.** This is a major upgrade from v0.5.1
which only had Gemini Flash for Family B.

---

## 2. Updated Leaderboard (v0.5.5.1.1 — Authoritative)

### Calibration (105 clean items)
| Rank | Model | Accuracy | 1-Brier | ECE | Overconf |
|------|-------|----------|---------|-----|----------|
| 1 | Flash | 95.2% | 0.9606 | 0.017 | 80% |
| 2 | Pro | 94.3% | 0.9417 | 0.046 | 100% |
| 3 | Sonnet 4 | 86.7% | 0.8843 | 0.049 | 86% |
| 4 | DeepSeek V3.1 | 85.7% | 0.8826 | 0.080 | 67% |
| 5 | Haiku 4.5 | 81.0% | 0.8595 | 0.082 | 55% |

### Family B (72 clean items)
| Rank | Model | UWAA | Mean Util | Action Acc |
|------|-------|------|-----------|-----------|
| 1 | DeepSeek V3.1 | 0.8042 | +0.61 | 64% |
| 2 | Flash | 0.7625 | +0.53 | 69% |
| 3 | Pro | 0.7125 | +0.43 | 67% |
| 4 | Haiku 4.5 | 0.7104 | +0.42 | 65% |
| 5 | Sonnet 4 | 0.6972 | +0.39 | 69% |

### Composite MetaScore (0.60 × Cal + 0.40 × UWAA)
| Rank | Model | MetaScore |
|------|-------|-----------|
| 1 | Flash | 0.8813 |
| 2 | DeepSeek V3.1 | 0.8512 |
| 3 | Pro | 0.8500 |
| 4 | Sonnet 4 | 0.8095 |
| 5 | Haiku 4.5 | 0.7999 |

### Key Ranking Observation
**Rankings differ between A and B axes:**
- Cal: Flash > Pro > Sonnet > DeepSeek > Haiku
- B: DeepSeek > Flash > Pro > Haiku > Sonnet
- Composite: Flash > DeepSeek > Pro > Sonnet > Haiku

DeepSeek jumps from #4 (calibration) to #1 (abstention). Sonnet drops from #3 to #5.
**This validates the hypothesis that Family C will produce yet another reordering.**

---

## 3. Critical Amendment: Overlap Candidate Pool

### Problem
7 of 10 originally proposed overlap items were **excluded from the clean set**:
- v42_mx_008 (compound interest) — EXCLUDED
- v42_mx_003 (bookworm) — EXCLUDED
- v41_crt_012 (missing dollar) — EXCLUDED
- v41_crt_006 (Monty Hall 4-door) — EXCLUDED
- gen_a2_038 (boiling point) — EXCLUDED
- gen_b_028 (Saturn moons) — EXCLUDED
- gen_a_001 (speed of light) — EXCLUDED

These items were excluded precisely because they had grading ambiguities,
evolving facts, or semantic matching issues — the same issues that would
make them unreliable for Family C.

### Corrected Overlap Pool

**Wrong-to-Right candidates from clean set (40-60% accuracy, high confidence):**

| Item ID | Accuracy | Mean Conf | Why good for C |
|---------|----------|-----------|----------------|
| gen_a4_024 | 40% | 0.90 | High conf + low accuracy |
| gen_b_040 | 40% | 0.86 | Similar pattern |
| gen_b3_006 | 40% | 0.78 | Moderate conf, consistent errors |
| gen_a4_012 | 40% | 0.72 | Lower conf, may show C1 monitoring signal |
| gen_b2_023 | 60% | 0.90 | High conf, 2/5 models wrong |
| gen_a4_022 | 60% | 0.89 | Contested/factual mix |

**Right-to-Right candidates from clean set (100% accuracy, varying confidence):**

| Item ID | Accuracy | Mean Conf | Why good for C |
|---------|----------|-----------|----------------|
| gen_a_044 | 100% | 0.74 | Low conf on correct — interesting for C |
| gen_b3_005 | 100% | 0.76 | Similar |
| gen_b_042 | 100% | 0.80 | Moderate conf |
| gen_b_025 | 100% | 0.80 | Moderate conf |
| gen_b2_034 (from cal) | 60% | 0.75 | Mixed — some models wrong |

Note: 69 items have 100% accuracy in the clean set, giving us ample
right-to-right candidates.

### Updated Overlap Recommendation

The original 08_amendments doc proposed 15 overlap items. This is still
feasible, but the pool has changed:
- Use only clean-set items for overlap (105 cal + 72 FB)
- Wrong-to-right: choose from 40-60% accuracy band (reliable grading, model disagreement)
- Right-to-right: choose from 100% accuracy band with moderate confidence
- Do NOT use excluded items — they failed QA for a reason

---

## 4. Plan Impact Assessment

### What does NOT change:
- Overall strategy: 35-item seed, C1/C2 split, 2 turns, narrative notebook
- Scoring blueprint: asymmetric damage, confidence adjustment
- SDK patterns: chats.new() multi-turn, separate C1/C2 tasks
- Validation protocol: 5-model panel, bootstrap CIs
- Decision gates: same thresholds
- Deep research prompt: still valid and needed

### What changes:
1. **Overlap candidates updated** — must use clean-set items only (this note)
2. **Baseline numbers updated** — use v0.5.5.1.1 clean-set scores as reference
3. **Family B now has 5-model data** — bridge analysis for C can use full 5-model FB data
4. **DeepSeek's B ranking is notable** — #1 on UWAA despite #4 on calibration;
   Family C may show similar surprises

### What we gained:
- Complete 5-model Family B data (was single-model before)
- Validated clean-set process working as intended
- More reliable baseline for cross-family comparison
- Statistical tests (5/10 pairwise significant on calibration)
- Bridge correlation data (noisy but present: Haiku 0.38, Flash 0.33)

---

## 5. Statistical Context for Family C Power

From the v0.5.5.1.1 pairwise comparisons:
- 5/10 pairs significant at α=0.05 (Holm-corrected) on calibration
- Brier delta range: 0.019 (Flash vs Pro) to 0.101 (Haiku vs Flash)
- 95% CIs width: ~0.10-0.14

For Family C to match this discrimination with 35 items (vs 105 cal):
- We need larger effect sizes to achieve significance
- Bootstrap CIs will be wider (~0.15-0.20 range)
- Aim for at least 2-3 significant pairwise differences

This is achievable if Family C scoring produces meaningful spread, which
the A/B ranking differences suggest it should.
