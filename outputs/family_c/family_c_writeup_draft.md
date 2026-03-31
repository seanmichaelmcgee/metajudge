# Family C: Self-Correction Under Metacognitive Review

## Construct

Family C measures whether models can detect and correct their own errors when given a structured review opportunity. It operationalizes the *detection-revision asymmetry* identified by Tyen et al. (ACL Findings 2024): the finding that error detection, not error correction, is the bottleneck for model self-improvement. Where Families A and B assess calibration and abstention on first-pass responses, Family C asks whether a second pass — with metacognitive scaffolding — produces genuine improvement or merely regeneration.

## Protocol

Each item follows a two-turn protocol:

**Turn 1 (T1):** The model answers a closed-form question with a structured `ANSWER: <answer> | CONFIDENCE: <0-100>` format. No review prompt is given; this establishes the baseline response.

**Turn 2 (T2):** The model receives a review prompt in one of three conditions:

- **C1 (Intrinsic review):** A third-person review prompt asks the model to examine "the student's work" for errors, adopting a reviewer role rather than defending its own answer. This framing draws on Hong et al. (EMNLP 2025), who showed that third-person framing reduces sycophantic self-confirmation. The prompt uses a detect-only instruction ("identify whether an error exists before attempting any correction") following Tyen et al.'s finding that decoupling detection from correction improves both. A "Wait" activation (Tsui, 2025) encourages deliberation before committing.

- **C2 (Evidence-assisted review):** Like C1, but the prompt includes a "Reviewer's Note" — a short factual snippet (a formula, a definition, a constraint) that bears on the item without directly revealing the answer. C2 measures whether models can leverage external evidence when their intrinsic detection fails.

- **B0 (Re-answering baseline):** The model simply re-answers the same question from scratch, without any review prompt. B0 isolates the re-sampling baseline: any improvement in C1/C2 beyond B0 represents genuine metacognitive value.

## Item Design

The dataset comprises 56 items across two subfamilies (C1: 31, C2: 25) and five strata:

- **wrong_to_right (26 items):** Items designed so a capable model can get the right answer but is likely to make a specific, predictable error on first pass. These target CoT-resistant error types: convention traps (e.g., Python's banker's rounding), specification boundaries (e.g., custom unit definitions that override real-world values), and semantic override errors (e.g., juxtaposition-as-multiplication in formal notation).

- **right_to_right (12 items):** Items that models should answer correctly on both passes. These measure the *damage rate* — whether the review process causes models to second-guess correct answers.

- **deceptive_trap (9 items):** Items with plausible-but-wrong lures designed to test whether models resist surface-level pattern matching during review.

- **weak_challenge (5 items, C2 only):** Items where the C2 evidence snippet provides a moderate nudge rather than a strong signal.

- **unresolved (4 items):** Items with genuine ambiguity, testing whether models appropriately acknowledge uncertainty rather than committing to a specific answer.

The 11 Phase 4 items were generated through a four-stage pipeline: author (generate candidate with mechanism annotation), adversary (verify the intended error is elicited), canary (pre-test on 2 cheap models), and frontier (pre-test on 4 frontier models, requiring at least one failure). This pipeline addresses the lesson from earlier phases that canary accuracy does not predict frontier difficulty.

## Results

Across 224 trials (56 items x 4 models), the headline metrics with bootstrap 95% CIs are:

| Model | T1 Acc | T2 Acc | T2-T1 Delta | SC Rate (W->R) | Damage Rate (R->W) |
|-------|--------|--------|-------------|-----------------|---------------------|
| Sonnet 4.6 | 83.9% [73, 93] | 85.7% [77, 95] | +1.8% [-4, 9] | 22% [6, 55] (2/9) | 2.1% [0, 11] (1/47) |
| Gemini Flash | 78.6% [68, 89] | 85.7% [77, 95] | +7.1% [-2, 18] | 50% [25, 75] (6/12) | 4.5% [1, 15] (2/44) |
| GPT-5-mini | 85.7% [77, 95] | 83.9% [73, 93] | -1.8% [-5, 0] | 0% [0, 32] (0/8) | 2.1% [0, 11] (1/48) |
| GPT-5.2 | 87.5% [79, 95] | 85.7% [77, 95] | -1.8% [-7, 4] | 14% [3, 51] (1/7) | 4.1% [1, 14] (2/49) |

**Gemini-flash shows genuine metacognitive correction.** Its +7.1% T2-T1 delta is backed by a +20% C1-B0 delta on the WR item subset (C1 T2 accuracy 84% vs. B0 accuracy 64%), meaning the review protocol adds substantial value beyond re-sampling. No other model shows a positive C1-B0 delta — Sonnet and GPT-5-mini show C1-B0 = 0% (re-sampling equivalent), and GPT-5.2 shows -4% (re-sampling is slightly better).

**Edit-distance analysis reveals divergent revision strategies.** Sonnet rewrites 93% of its responses entirely (mean similarity 0.18), while GPT-5-mini makes targeted edits 38% of the time (mean similarity 0.61). This aligns with Kumar et al.'s (ICLR 2025) SCoRe finding that targeted revision signals genuine correction, while complete rewriting signals re-generation. Notably, Gemini-flash also rewrites heavily (86%) but achieves the highest SC rate, suggesting that rewriting and correction are not mutually exclusive.

**Phase 4 items add discriminative power.** The item sc_c2_wr_016 (a custom unit definition trap) achieves 0% T1 accuracy across all 4 models — every model imports the real-world mile-to-kilometer conversion instead of the stated custom definition. Three additional items (wr_017, wr_023, wr_030) sit at 75% T1, each failing on exactly one model.

## Scoring

Family C scoring reflects the asymmetric costs of self-correction errors:

- **C1 and C2 are scored separately** and never aggregated, since C2's external evidence fundamentally changes the task.
- **Damage:gain inversion:** A 2:1 penalty ratio weights R->W transitions (damage) twice as heavily as W->R transitions (gain), following prospect theory's loss aversion and the practical reality that a model that damages correct answers is worse than one that fails to correct errors.
- **Confidence adjustment:** The raw transition score is modulated by a confidence delta term. Appropriate confidence changes (dropping confidence when switching to a wrong answer) receive a small bonus; inappropriate confidence rigidity receives a penalty.
- **Rescaling:** Raw scores on the theoretical range [-0.65, 0.65] are linearly rescaled to [0, 1] for aggregation with Families A and B.

## Limitations

- **Small sample size:** n=56 items yields wide bootstrap CIs (e.g., Gemini's T2-T1 delta CI spans [-2%, +18%]). Statistical significance at the conventional alpha=0.05 level is not achievable for most pairwise comparisons.
- **Four models only:** DeepSeek-R1 timed out during the sweep and could not be included. The model panel, while covering major providers, is not exhaustive.
- **Item saturation:** 5 of 11 Phase 4 items show 100% T1 accuracy across all 4 models, providing no discriminative power. The item generation pipeline's frontier pre-test gate helps but does not fully solve this.
- **Confidence ceiling:** All models report 92-99% mean confidence regardless of correctness, yielding minimal discrimination from the confidence component. This is consistent with Mei et al. (2025) but limits the scoring system's ability to reward appropriate calibration.
- **Re-generation confound:** Models that completely rewrite their T2 response (Sonnet: 93%, Gemini: 86%) may be re-generating rather than reviewing. The B0 baseline partially controls for this, but only on WR items.
