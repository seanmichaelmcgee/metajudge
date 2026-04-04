# MetaJudge v6.2 Stochasticity: Per-Model and Per-Item Analysis

**Dataset:** 760 dual-run item pairs | 7 models | 3 tasks | 76 total flips (10.0%)

---

## Level 1: Model Stochasticity Profiles

### Gemini-2.5-Pro

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| Abstention | 0.260 | 0.194 | -0.066 | 12/72 = 16.7% | Volatile |
| SC C1 | 0.257 | 0.543 | +0.286 | 12/28 = 42.9% | Volatile |
| SC C2 | 0.283 | 0.283 | +0.000 | 4/23 = 17.4% | Volatile |
| **Overall** | | | | **28/123 = 22.8%** | **Volatile** |

The worst performer by stability. Nearly 1-in-4 items flip between runs. The C1 flip rate of 42.9% means the score is essentially coin-flip noise. The +0.286 delta swing in C1 between runs is the largest in the dataset -- the model went from 0.257 to 0.543, a complete ranking reversal that would move it from worst to best on that task.

### Claude-Sonnet-4 (20250514)

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| SC C1 | 0.400 | 0.543 | +0.143 | 6/28 = 21.4% | Volatile |
| SC C2 | 0.500 | 0.500 | +0.000 | 5/23 = 21.7% | Volatile |
| **Overall** | | | | **11/51 = 21.6%** | **Volatile** |

Only tested on SC tasks (no abstention). Both tasks show ~21% flip rates. The C2 flips are score-neutral (symmetric), but C1 shows net improvement on R2 -- raising the question of whether R1 was unlucky or R2 was.

### GPT-5.4

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| Abstention | 0.550 | 0.580 | +0.030 | 3/72 = 4.2% | Stable |
| SC C1 | 0.257 | 0.543 | +0.286 | 4/28 = 14.3% | Moderate |
| SC C2 | 0.391 | 0.500 | +0.109 | 3/23 = 13.0% | Moderate |
| **Overall** | | | | **10/123 = 8.1%** | **Moderate** |

Stable on abstention, moderate on SC. Like Gemini-2.5-Pro, shows a massive +0.286 C1 swing between runs. Two independent models producing an identical delta swing on the same task is suspicious -- it suggests the instability is task-structural, not model-specific.

### Gemma-4-26b-a4b

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| Abstention | 0.482 | 0.505 | +0.023 | 7/71 = 9.9% | Moderate |
| SC C1 | 0.400 | 0.400 | +0.000 | 1/28 = 3.6% | Stable |
| SC C2 | 0.391 | 0.391 | +0.000 | 1/23 = 4.3% | Stable |
| **Overall** | | | | **9/122 = 7.4%** | **Moderate** |

Mostly stable on SC tasks with flips concentrated in abstention. Notably, the one C1 flip is on sc_c1_rr_010 -- the most volatile item in the entire dataset.

### Claude-Sonnet-4-6 (Default)

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| Abstention | 0.396 | 0.405 | +0.009 | 1/72 = 1.4% | Stable |
| SC C1 | 0.257 | 0.257 | +0.000 | 5/28 = 17.9% | Volatile |
| SC C2 | 0.500 | 0.391 | -0.109 | 2/23 = 8.7% | Moderate |
| **Overall** | | | | **8/123 = 6.5%** | **Moderate** |

Extremely stable on abstention (1 flip in 72), but volatile on C1. The 5 C1 flips cancel out in aggregate (score unchanged at 0.257), which is score-neutral but still indicates noisy item-level measurement.

### Gemini-3-Flash-Preview

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| Abstention | 0.602 | 0.594 | -0.009 | 1/72 = 1.4% | Stable |
| SC C1 | 0.400 | 0.114 | -0.286 | 4/28 = 14.3% | Moderate |
| SC C2 | 0.500 | 0.500 | +0.000 | 1/23 = 4.3% | Stable |
| **Overall** | | | | **6/123 = 4.9%** | **Stable** |

Lowest aggregate flip rate among models tested on all 3 tasks. But the -0.286 C1 swing (mirror image of Gemini-2.5-Pro and GPT-5.4's +0.286) reinforces the pattern: C1 scores are fundamentally unreliable with 28 items.

### Gemma-4-31b

| Task | R1 Norm | R2 Norm | Delta | Flip Rate | Stability |
|------|---------|---------|-------|-----------|-----------|
| Abstention | 0.506 | 0.506 | +0.000 | 0/67 = 0.0% | Stable |
| SC C1 | 0.114 | 0.114 | +0.000 | 4/28 = 14.3% | Moderate |
| **Overall** | | | | **4/95 = 4.2%** | **Stable** |

Perfectly stable on abstention (zero flips across 67 items). C1 flips cancel out. Not tested on C2.

### Cross-Model Stability Ranking

| Rank | Model | Flip Rate | Assessment |
|------|-------|-----------|------------|
| 1 | gemma-4-31b | 4.2% (4/95) | Stable |
| 2 | gemini-3-flash-preview | 4.9% (6/123) | Stable |
| 3 | claude-sonnet-4-6 | 6.5% (8/123) | Moderate |
| 4 | gemma-4-26b-a4b | 7.4% (9/122) | Moderate |
| 5 | gpt-5.4 | 8.1% (10/123) | Moderate |
| 6 | claude-sonnet-4 (0514) | 21.6% (11/51) | Volatile |
| 7 | gemini-2.5-pro | 22.8% (28/123) | Volatile |

### Is Stability Correlated with MetaScore?

Using Run 1 MetaScores from the aggregate report (4 complete models):

| Model | MetaScore | Flip Rate | Stable? |
|-------|-----------|-----------|---------|
| gemini-3-flash-preview | 0.589 | 4.9% | Yes |
| claude-sonnet-4-6 | 0.449 | 6.5% | Somewhat |
| gemini-2.5-pro | 0.398 | 22.8% | No |
| gemma-4-26b-a4b | 0.350 | 7.4% | Somewhat |

**Weak positive correlation** -- the highest-scoring model is the most stable, and the most volatile model (Gemini-2.5-Pro) scores below average. But Gemma-4-26b-a4b breaks the pattern: lowest MetaScore yet reasonably stable. The correlation is driven primarily by Gemini-2.5-Pro being both unstable and mediocre. With n=4 complete models, no statistical conclusion is warranted.

**Honest assessment:** Gemini-2.5-Pro's instability is a genuine concern. Its MetaScore could plausibly range from ~0.30 to ~0.50 depending on run luck. The other models are stable enough that their rankings are likely robust, with the caveat that C1 scores are unreliable for all models.

---

## Level 2: Item Volatility Map

### Per-Task Breakdown

**Abstention (72 items, 6 models tested)**

| Flip Count | Items | Percentage |
|------------|-------|-----------|
| 0 (perfectly stable) | 51 | 70.8% |
| 1 (model-specific) | 18 | 25.0% |
| 2 (multi-model volatile) | 3 | 4.2% |

Abstention is well-behaved. The 3 items flipping for 2 models (abs_026, abs_034, abs_086) involve Gemini-2.5-Pro in every case, so even the "multi-model" volatility is partly Gemini-Pro's instability leaking through.

**SC C1 (28 items, 7 models tested)**

| Flip Count | Items | Percentage |
|------------|-------|-----------|
| 0 (perfectly stable) | 9 | 32.1% |
| 1 (model-specific) | 11 | 39.3% |
| 2 (multi-model) | 3 | 10.7% |
| 3 (multi-model) | 2 | 7.1% |
| 4 (multi-model) | 2 | 7.1% |
| 5 (inherently volatile) | 1 | 3.6% |

Only 32% of C1 items are perfectly stable -- compared to 71% for abstention. 28% of items flip for 2+ models, confirming the instability is task-structural. With only 28 items and 68% showing any instability, C1 normalized scores are dominated by noise.

**SC C2 (23 items, 6 models tested)**

| Flip Count | Items | Percentage |
|------------|-------|-----------|
| 0 (perfectly stable) | 12 | 52.2% |
| 1 (model-specific) | 7 | 30.4% |
| 2 (multi-model) | 3 | 13.0% |
| 3 (multi-model) | 1 | 4.3% |

C2 falls between abstention and C1. Half the items are stable, but with only 23 items total, each flip moves the normalized score by ~0.04 points.

### 10 Most Volatile Items

| Rank | Item | Task | Flipped By | Models Tested | Rate |
|------|------|------|-----------|---------------|------|
| 1 | sc_c1_rr_010 | C1 | 5 | 7 | 71% |
| 2 | sc_c1_dt_001 | C1 | 4 | 7 | 57% |
| 3 | sc_c1_wr_023 | C1 | 4 | 7 | 57% |
| 4 | sc_c1_wr_004 | C1 | 3 | 7 | 43% |
| 5 | sc_c1_wr_011 | C1 | 3 | 7 | 43% |
| 6 | sc_c2_wc_002 | C2 | 3 | 6 | 50% |
| 7 | abs_026 | Abs | 2 | 6 | 33% |
| 8 | abs_034 | Abs | 2 | 6 | 33% |
| 9 | abs_086 | Abs | 2 | 6 | 33% |
| 10 | sc_c1_dt_006 | C1 | 2 | 7 | 29% |

**All top 5 are C1 items.** The single most volatile item (sc_c1_rr_010) flips for 5 of 7 models -- this item is essentially unmeasurable by current methodology.

### 10 Most Stable Items

| Rank | Item | Task | Flipped By | Models Tested |
|------|------|------|-----------|---------------|
| 1-9 | sc_c1_dt_002, dt_003, dt_005, rr_002, rr_005, rr_007, wr_001, wr_007, wr_030 | C1 | 0 | 7 |
| 10 | abs_001 | Abs | 0 | 6 |

Nine C1 items and one abstention item achieved perfect stability across all models. This means C1 has both the most volatile AND some of the most stable items -- it is a bimodal task where specific items are either rock-solid or highly unstable.

### C1 Deep Dive: What Drives the Instability?

C1 accounts for 36 of 76 total flips (47%) despite having only 28 of 123 unique items (23%). The instability is concentrated:

**The top 5 volatile C1 items account for 19 flips** -- more than half of all C1 instability comes from 5 items (18% of C1 items).

Examining the flip patterns:

| Item | Dominant Flip Pattern | Interpretation |
|------|----------------------|----------------|
| sc_c1_rr_010 | maintain_correct <-> neutral_revision (4x), neutral_revision -> damage (1x) | Borderline correct -- models waver on whether to revise |
| sc_c1_dt_001 | neutral_revision <-> maintain_correct (4x) | Same borderline pattern |
| sc_c1_wr_023 | damage -> maintain_correct (3x), maintain_correct -> damage (1x) | Unstable damage classification |
| sc_c1_wr_004 | maintain_correct <-> neutral_revision (3x) | Borderline revision detection |
| sc_c1_wr_011 | maintain_correct <-> neutral_revision (3x) | Same pattern |

The dominant flip pattern is **maintain_correct <-> neutral_revision**: models inconsistently decide whether a self-correction response constitutes a "revision" or "maintaining" the original answer. This is a classification boundary problem -- these items sit at the edge of what counts as a revision, and stochastic variation pushes models across that boundary.

The second pattern involves **damage** classifications flipping, which is more concerning since damage directly affects the normalized score.

### Critical Finding

**Removing the 5 most volatile C1 items (sc_c1_rr_010, dt_001, wr_023, wr_004, wr_011) would eliminate 19 of 36 C1 flips (53%).** If MetaJudge v6.3 aims to reduce stochasticity, these items should be reviewed for ambiguous classification boundaries. The underlying issue is that the maintain_correct / neutral_revision distinction is not sharp enough for these items, and models resolve the ambiguity differently on each run.

---

## Summary Judgment

1. **Abstention is stable.** 71% of items never flip; aggregate scores move less than 0.01 between runs for most models.
2. **C1 is unreliable.** 68% of items flip for at least one model; aggregate scores can swing by 0.286 between runs. C1 normalized scores should be interpreted as approximate ordinal rankings, not precise measurements.
3. **C2 is marginal.** Half the items are stable, but the small item count (23) amplifies each flip.
4. **Gemini-2.5-Pro is the outlier.** Its instability (22.8% flip rate) is 3-5x worse than the median model, driven by both abstention and C1 volatility.
5. **Item-level instability is concentrated.** 5 C1 items generate half of all C1 flips. These are classification boundary cases, not random noise -- they represent genuine ambiguity in the scoring rubric.
