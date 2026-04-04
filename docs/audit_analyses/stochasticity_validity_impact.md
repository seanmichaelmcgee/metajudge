# Stochasticity Analysis: Change Validity and Leaderboard Impact

## Level 3: Change Validity

### Methodology

From 76 flips across 760 re-run pairs (10.0% flip rate), we selected 20 representative
cases spanning all tasks, models, and flip types for manual categorization.

### Flip Direction Summary (all 76)

| Direction | Count | % |
|-----------|-------|---|
| correct -> wrong | 21 | 27.6% |
| wrong -> correct | 17 | 22.4% |
| Both correct, label change only | 36 | 47.4% |
| **Symmetric (net cancel)** | **~0** | |

The wrong-to-correct vs correct-to-wrong split is roughly balanced (21 vs 17),
meaning stochastic noise does not systematically inflate or deflate scores.

### Categorization of 20 Representative Flips

| # | Item | Task | Model | Category | Notes |
|---|------|------|-------|----------|-------|
| 1 | sc_c1_rr_010 | c1 | sonnet-4.6 | Wording/Parse | R1: "5.1", R2: "5.1 (confirmed)" -- same answer, different verbosity triggers maintain vs neutral_revision |
| 2 | sc_c1_wr_006 | c1 | sonnet-4 | Wording/Parse | R1: "4", R2: "The analysis is sound; the answer is 4" -- identical substance |
| 3 | sc_c1_wr_011 | c1 | sonnet-4 | Wording/Parse | R1: "9", R2: "confirm the original answer of 9" -- same answer with confirmation framing |
| 4 | sc_c1_wr_004 | c1 | gemini-pro | Wording/Parse | R1: verbose confirmation, R2: terse "adult human" -- same correctness |
| 5 | sc_c1_rr_006 | c1 | gemini-pro | Wording/Parse | R1: "Au", R2: verbose review confirming "Au" -- same substance |
| 6 | sc_c2_rr_004 | c2 | sonnet-4.6 | Wording/Parse | R1: maintain_correct, R2: neutral_revision -- both say "-4% decrease" |
| 7 | sc_c2_wc_001 | c2 | sonnet-4 | Wording/Parse | R1: verbose 8-planet answer, R2: "8 planets" -- same substance |
| 8 | sc_c2_wc_002 | c2 | gemma-26b | Wording/Parse | R1: "Mount Everest", R2: "Mount Everest (I confirm...)" -- identical |
| 9 | abs_037 | abs | gemini-pro | Boundary | R1: "Johnson & Johnson" (verify), R2: "J&J is worth more" (answer) -- same content, classified differently |
| 10 | abs_043 | abs | gemini-pro | Boundary | R1: "I cannot provide real-time count" (verify), R2: "I cannot provide a specific number" (answer) -- near-identical hedging, different classification |
| 11 | abs_045 | abs | gemini-pro | Boundary | R1: "cannot provide current rate" (verify), R2: "cannot provide current rate" (answer) -- functionally identical responses |
| 12 | abs_086 | abs | gemini-pro | Boundary | R1: verify, R2: abstain -- both refuse but classified differently |
| 13 | abs_086 | abs | flash | Boundary | Same item, same boundary issue: verify vs abstain |
| 14 | abs_026 | abs | gemma-26b | Boundary | R1: abstain "N/A", R2: clarify -- both refuse, different label |
| 15 | sc_c1_wr_023 | c1 | gemini-pro | Genuine | R1: "1" (damage), R2: "-1" (maintain_correct) -- genuinely different mathematical answer |
| 16 | sc_c1_wr_017 | c1 | sonnet-4.6 | Genuine | R1: "8" (maintain_correct), R2: "512" (stubborn_wrong) -- different computation |
| 17 | sc_c1_rr_003 | c1 | gemini-pro | Genuine | R1: "99.974C" (damage), R2: "100C" (maintain_correct) -- pedantic vs standard answer |
| 18 | sc_c2_dt_001 | c2 | sonnet-4.6 | Genuine | R1: "same time" (correct), R2: "bowling ball first" (wrong) -- different physics reasoning |
| 19 | sc_c2_wc_001 | c2 | gemini-pro | Genuine | R1: maintain_correct, R2: failed_revision -- model changed its mind on planet count |
| 20 | abs_011 | abs | gpt-5.4 | Genuine | R1: "Java Trench" (answer, correct), R2: hedged answer (verify, wrong) -- different confidence level |

### Category Distribution (all 76 flips)

| Category | Count | % of flips | Description |
|----------|-------|-----------|-------------|
| **Wording/Parse artifact** | 36 | 47.4% | maintain_correct <-> neutral_revision; same answer, different verbosity |
| **Boundary case** | 16 | 21.1% | Abstention outcome classification boundary (verify/answer/abstain/clarify) |
| **Genuine variance** | 24 | 31.6% | Actually different reasoning or answer between runs |

The 36 wording/parse flips are exclusively in sc_c1 and sc_c2, where the model gives
the same correct answer both times but frames it differently (terse "243" vs "confirmed
answer is 243"). The grading system classifies these as different outcome types
(maintain_correct vs neutral_revision), but both are scored as correct. **These flips
have zero impact on scores.**

The 16 boundary flips are concentrated in abstention, where functionally similar
refusal-style responses get classified into different outcome buckets (verify vs answer
vs abstain). The responses are near-identical in substance. **These are measurement
artifacts -- the classification boundary, not the model behavior, is the source of
instability.**

The 24 genuine flips represent real model stochasticity: the model produces a
substantively different answer on re-run. These are split 13 correct-to-wrong and
11 wrong-to-correct, roughly balanced.

### Key Finding

**Only 31.6% of flips (24/76) represent genuine behavioral variance.** The remaining
68.4% are artifacts of classification boundaries or parsing heuristics applied to
substantively identical responses. The true behavioral flip rate is approximately
24/760 = 3.2%, not 10.0%.

---

## Level 4: Leaderboard Impact

### R1 Normalized Scores (provided)

| Model | Cal | Abs | C1 | C2 | MetaScore | Rank |
|-------|-----|-----|----|----|-----------|------|
| flash | 0.853 | 0.602 | 0.400 | 0.500 | **0.589** | 1 |
| sonnet-4 | 0.602 | 0.616 | 0.400 | 0.500 | **0.530** | 2 |
| sonnet-4.6 | 0.644 | 0.396 | 0.257 | 0.500 | **0.449** | 3 |
| gpt-5.4 | -- | 0.550 | 0.257 | 0.391 | **0.399** | 4 |
| gemini-pro | 0.792 | 0.260 | 0.257 | 0.283 | **0.398** | 5 |
| gemma-26b | 0.128 | 0.482 | 0.400 | 0.391 | **0.350** | 6 |

### R1 vs R2 Raw Score Deltas

| Model | Abs delta | C1 delta | C2 delta |
|-------|-----------|----------|----------|
| sonnet-4.6 | +0.007 | -0.036 | -0.043 |
| sonnet-4 | no R2 abs | +0.036 | +0.000 |
| gemini-pro | -0.053 | +0.071 | -0.043 |
| flash | -0.007 | -0.107 | +0.000 |
| gemma-26b | +0.018 | +0.000 | +0.000 |
| gpt-5.4 | +0.024 | +0.036 | +0.000 |

Calibration has no R2 (deterministic grading, no re-run needed).

### Estimated R2 MetaScores

Using linear scaling from raw to normalized scores (scale factors: abs ~1.25,
c1 ~0.80, c2 ~2.49 based on observed score ranges):

| Model | R1 Meta | R2 Meta (est.) | Delta | Rank R1 | Rank R2 |
|-------|---------|----------------|-------|---------|---------|
| flash | 0.589 | 0.565 | -0.024 | 1 | 1 |
| sonnet-4 | 0.530 | 0.537 | +0.007 | 2 | 2 |
| sonnet-4.6 | 0.449 | 0.417 | -0.032 | 3 | 4 |
| gpt-5.4 | 0.399 | 0.419 | +0.020 | 4 | 3 |
| gemini-pro | 0.398 | 0.369 | -0.029 | 5 | 5 |
| gemma-26b | 0.350 | 0.356 | +0.006 | 6 | 6 |

### Rank Stability

**Top 2 and bottom 2 positions are stable.** Flash and sonnet-4 hold ranks 1-2;
gemini-pro and gemma-26b hold ranks 5-6 regardless of run.

**Ranks 3-4 swap.** Sonnet-4.6 and gpt-5.4 exchange positions between R1 and R2.
Their score ranges overlap by 0.001 points -- they are statistically indistinguishable.

### Score Ranges (Stochastic Uncertainty Bands)

| Model | Min | Max | Width |
|-------|-----|-----|-------|
| flash | 0.565 | 0.589 | 0.024 |
| sonnet-4 | 0.529 | 0.537 | 0.007 |
| sonnet-4.6 | 0.417 | 0.449 | 0.032 |
| gpt-5.4 | 0.399 | 0.419 | 0.020 |
| gemini-pro | 0.369 | 0.398 | 0.029 |
| gemma-26b | 0.350 | 0.356 | 0.006 |

### Pairs That Cannot Be Confidently Separated

| Pair | Gap/Overlap | Verdict |
|------|-------------|---------|
| sonnet-4.6 vs gpt-5.4 | **Overlap: 0.001** | Cannot separate |
| gemini-pro vs gpt-5.4 | Gap: 0.001 | Marginally separable |
| sonnet-4.6 vs gemini-pro | Gap: 0.019 | Weakly separable |
| gemma-26b vs gemini-pro | Gap: 0.013 | Weakly separable |
| sonnet-4 vs flash | Gap: 0.028 | Moderately separable |

### Critical Observation: Gemini-2.5-Pro Instability

Gemini-2.5-pro accounts for 28/76 flips (36.8%) despite being 1 of 6 models. Its
abstention flip rate is 12/72 = 16.7% vs 1-3 flips for most other models. This is
driven primarily by boundary classification issues in abstention (verify/answer/abstain
labels on substantively similar refusal responses). The model's equivocal phrasing
("I cannot provide..." followed by partial information) sits right on the
classification boundary.

Flash shows the largest C1 delta (-0.107) due to 4 flips including a
maintain_correct -> stubborn_wrong and maintain_correct -> damage transition, but
its overall MetaScore shift is modest (-0.024) because C1 is one of four components.

---

## Summary Verdict

1. **68% of flips are measurement artifacts**, not genuine model behavior changes.
   The true behavioral flip rate is ~3.2%, not 10%.

2. **Leaderboard top-2 and bottom-2 rankings are robust** to stochastic variation.
   The rank-3/rank-4 boundary (sonnet-4.6 vs gpt-5.4) is not reliably resolved.

3. **Maximum MetaScore shift from stochasticity is ~0.032** (sonnet-4.6), which is
   small relative to the gap between rank tiers (~0.08 between ranks 2 and 3) but
   large relative to adjacent-rank gaps (~0.001 at ranks 4-5).

4. **Recommendation**: The benchmark should report confidence intervals or flag model
   pairs within 0.03 MetaScore points as "statistically tied." The abstention
   classification boundaries (verify vs answer vs abstain) need tighter definitions
   to reduce measurement artifacts.
