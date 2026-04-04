# MetaJudge v6.2 Stochasticity Synthesis

**Audit finding** | 760 dual-run pairs | 7 models | 3 tasks | April 2026

---

## 1. Executive Summary

MetaJudge v6.2 produces a headline stochastic flip rate of 10.0% (76/760 item pairs change classification between runs). This number is misleading. Manual review shows 68.4% of flips are measurement artifacts -- wording/parse sensitivity (47.4%) and classification boundary ambiguity (21.1%) -- not genuine behavioral variance. The true behavioral flip rate is approximately 3.2%. However, the instability that does exist is not uniformly distributed: it concentrates overwhelmingly in the Self-Correction C1 task, where 68% of items are unstable across models and score swings of 0.286 occur between runs. The leaderboard resolves into 3 stable tiers rather than 6 ranked positions, with ranks 3-4 indistinguishable within stochastic noise. The benchmark's top-level rankings are defensible; its C1 scores are not.

---

## 2. The 10% Illusion

The 10.0% raw flip rate decomposes as follows:

| Category | Flips | % of total | Score impact |
|----------|-------|-----------|--------------|
| Wording/parse artifact | 36 | 47.4% | Zero -- same answer, different verbosity |
| Boundary classification | 16 | 21.1% | Minimal -- near-identical refusals labeled differently |
| Genuine behavioral variance | 24 | 31.6% | Real -- different reasoning or answer |

The 36 wording/parse flips are exclusively in SC tasks. A model answering "243" vs "confirmed answer is 243" gets classified as maintain_correct vs neutral_revision. Both are scored correct. These flips change labels but not scores.

The 16 boundary flips are concentrated in abstention, where equivocal refusals ("I cannot provide real-time data" followed by partial information) sit on the verify/answer/abstain boundary. The responses are functionally identical; the classification system lacks the resolution to handle them consistently.

The 24 genuine flips split 13 correct-to-wrong and 11 wrong-to-correct -- roughly balanced, meaning stochasticity introduces noise without systematic bias. **The true behavioral flip rate is 24/760 = 3.2%.** At this level, MetaJudge is comparable to typical inter-rater reliability for human evaluators on subjective tasks.

---

## 3. Task Reliability Hierarchy

| Task | Items | Perfectly stable | Any flip | Multi-model volatile | Flip rate |
|------|-------|-----------------|----------|---------------------|-----------|
| Abstention | 72 | 70.8% | 29.2% | 4.2% (3 items) | 24/426 = 5.6% |
| SC C2 | 23 | 52.2% | 47.8% | 17.4% (4 items) | 16/138 = 11.6% |
| SC C1 | 28 | 32.1% | 67.9% | 28.6% (8 items) | 36/196 = 18.4% |

**Abstention** is well-behaved. The 3 multi-model volatile items all involve Gemini-2.5-Pro, so even apparent cross-model instability traces to one outlier model. Aggregate scores move less than 0.01 between runs for 5 of 6 models.

**SC C2** has hidden instability: nearly half its items flip for at least one model, but flips are predominantly offsetting. Four of six models show zero net C2 score change between runs. The instability is real at item level but washes out in aggregation -- a fortunate accident, not a design guarantee.

**SC C1** is fundamentally unreliable. Only 9 of 28 items are perfectly stable. Three independent models (Gemini-2.5-Pro, GPT-5.4, Gemini-3-Flash) show identical absolute score swings of 0.286 between runs -- a structural signature, not model-specific noise.

---

## 4. The C1 Problem

### Root cause

The dominant flip pattern is **maintain_correct <-> neutral_revision** (accounting for the majority of C1 flips). The rubric distinction between "maintaining the correct answer" and "performing a neutral revision that preserves correctness" is insufficiently sharp. When a model says "5.1" on one run and "5.1 (confirmed)" on another, the classification system sees a categorical difference where none exists behaviorally.

### The worst items

| Item | Models flipped | Rate | Dominant pattern |
|------|---------------|------|-----------------|
| sc_c1_rr_010 | 5/7 | 71% | maintain_correct <-> neutral_revision |
| sc_c1_dt_001 | 4/7 | 57% | maintain_correct <-> neutral_revision |
| sc_c1_wr_023 | 4/7 | 57% | damage <-> maintain_correct |
| sc_c1_wr_004 | 3/7 | 43% | maintain_correct <-> neutral_revision |
| sc_c1_wr_011 | 3/7 | 43% | maintain_correct <-> neutral_revision |

These 5 items (18% of C1) account for 19 of 36 C1 flips (53%). Item sc_c1_rr_010 is effectively unmeasurable -- 5 of 7 models classify it differently between runs.

### Which models suffer most

Every model tested on C1 shows instability, but it manifests differently:

- **Score-shifting** (Gemini-Pro, GPT-5.4, Flash): C1 scores swing by 0.286 between runs, enough to move a model from worst to best on that task.
- **Score-neutral but noisy** (Sonnet-4.6, Gemma-31b): Flips cancel in aggregate (score unchanged) but item-level measurement is unreliable.
- **Consistently volatile** (Sonnet-4, Gemini-Pro): 21%+ flip rates across all SC tasks.

The fact that C1 is bimodal -- containing both the most volatile AND some perfectly stable items -- means the instability is item-specific, not task-wide randomness. This is fixable.

---

## 5. Leaderboard Confidence Intervals

### Three tiers, not six ranks

| Tier | Models | MetaScore range (R1-R2) | Internal gap |
|------|--------|------------------------|--------------|
| Top | Flash, Sonnet-4 | 0.530-0.589 | 0.028-0.059 |
| Middle | Sonnet-4.6, GPT-5.4 | 0.399-0.449 | **Overlap: 0.001** |
| Bottom | Gemini-Pro, Gemma-26b | 0.350-0.398 | 0.013-0.048 |

The maximum MetaScore shift from stochasticity is 0.032 (Sonnet-4.6). The gap between tiers (~0.08 between tier 1 and tier 2) exceeds this comfortably. The gap within the middle tier (0.001 at the overlap point) does not.

### What is robust

- Flash holds rank 1 in both runs. Its uncertainty band (0.565-0.589) never overlaps with rank 2.
- Sonnet-4 holds rank 2. Band: 0.529-0.537.
- Gemma-26b holds rank 6. Band: 0.350-0.356.

### What is not robust

- **Sonnet-4.6 vs GPT-5.4**: R1 says Sonnet-4.6 by 0.050. R2 says GPT-5.4 by 0.002. These models are tied.
- **Gemini-Pro vs GPT-5.4**: Separated by 0.001 in R1. Gemini-Pro's high instability (uncertainty width: 0.029) means this ranking is noise.

---

## 6. Recommendations for v7

### Immediate (rubric fixes)

1. **Tighten the maintain_correct / neutral_revision boundary.** Define operationally: if the final answer is lexically identical (modulo formatting), classify as maintain_correct regardless of surrounding commentary. This alone would eliminate ~47% of all flips.

2. **Drop or rework the 5 most volatile C1 items** (sc_c1_rr_010, dt_001, wr_023, wr_004, wr_011). Removing them eliminates 53% of C1 instability. If retained, they need unambiguous gold labels.

3. **Sharpen abstention classification boundaries.** The verify/answer/abstain distinction fails on equivocal refusals. Define a "partial refusal" category or operationalize the boundary with lexical heuristics.

### Structural (methodology fixes)

4. **Expand the C1 item set.** 28 items is too few -- each flip moves the normalized score by ~0.036. At 56+ items, per-flip impact halves and scores become robust to the residual 3.2% genuine flip rate.

5. **Report confidence intervals.** Flag model pairs within 0.03 MetaScore as "statistically tied." Present tier membership rather than precise rankings.

6. **Run triple (not dual) evaluation** for SC tasks. Two runs provide a flip/no-flip binary; three runs identify the majority classification and reduce noise by ~40%.

### Reporting (transparency fixes)

7. **Decompose flip rates** into artifact vs genuine in all stochasticity reporting. The raw 10% number is misleading without context.

8. **Report per-task reliability** alongside aggregate MetaScores. Users should know that C1 scores carry wide error bars.

---

## 7. Honest Assessment

**What v6.2 gets right:** The leaderboard's tier structure is real. Flash and Sonnet-4 are genuinely better meta-judges than the bottom tier. The 3.2% true behavioral flip rate is acceptable for a benchmark of this complexity. Abstention measurement is solid. The stochastic noise is not systematically biased in either direction.

**What v6.2 gets wrong:** C1 scores are not reliable enough to contribute meaningfully to model differentiation. With 68% of items unstable and 0.286-point swings between runs, C1 functions as a noise injector in the MetaScore composite. The benchmark presents 6 ranked positions when it can only resolve 3 tiers. Adjacent-rank differences (0.001-0.013) fall well within the stochastic uncertainty band (up to 0.032).

**What this means practically:** If you are using MetaJudge v6.2 to choose between Flash and Gemma-26b, the benchmark gives you a clear answer. If you are using it to choose between Sonnet-4.6 and GPT-5.4, you are reading noise. The overall validity of the benchmark is moderate -- the tier structure holds, the fine-grained ranking does not. For a v6.2 benchmark with novel task designs, this is a reasonable but improvable outcome.

**Bottom line:** MetaJudge v6.2 is more stable than it first appears (3.2% true flip rate, not 10%), but less precise than it claims (3 tiers, not 6 ranks). The C1 task is the clear weak point and should be the primary target for v7 methodology improvements.
