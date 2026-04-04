### Calibration — Scoring Assessment

**What it measures.** Calibration measures whether a model's stated confidence tracks its actual correctness — the core metacognitive monitoring signal. A well-calibrated model says "95% confident" only when it is right roughly 95% of the time, and says "50% confident" when it is genuinely uncertain. This is not accuracy alone: a model that gets everything right at 60% confidence scores worse than one that gets everything right at 95% confidence, because the first model's probability estimates are systematically wrong even though its answers are correct. The metric captures epistemic self-knowledge, not just knowledge.

**How it scores.** Each of 105 items yields a per-item score: `1-Brier = 1 - (confidence - outcome)^2`, where outcome is 1 (correct) or 0 (incorrect). Correctness is determined by a deterministic 8-rule grading engine (`grading_v2.py`) with no LLM judge. The mean 1-Brier across all items is then anchor-normalized from [0.75, 1.00] to [0, 1], where 0.75 approximates random guessing at 50% confidence and 1.00 represents perfect calibration. The normalization formula is `(raw - 0.75) / 0.25`, clamped to [0, 1].

---

#### Transparency

**Strength: Full pipeline auditability.** The grading chain is end-to-end traceable. For any item, a reviewer can follow: model answer -> grading rule (one of 8 deterministic rules) -> accepted forms from the adjudication registry -> correct/incorrect determination -> confidence extraction -> 1-Brier computation -> mean -> anchor normalization. The cross-model audit (`cross_model_audit.md`) verified 1,137 item-level grades across 5 models, achieving 98.8% AGREE, 0% DISAGREE, with all discrepancies attributable to known bugs. This is a strong transparency result: an external auditor reproduced every grade.

**Strength: No LLM-as-judge.** The deterministic grading engine eliminates the opacity and variance inherent in LLM-based evaluation. Each grading rule is inspectable code, not a prompt.

**Strength: Bug disclosure.** All known bugs are cataloged with item IDs, affected models, severity ratings, and score impact estimates. The tri_label accepted_forms bug affecting 4 items was identified, a fix was deployed, and the impact was quantified per-model. This is the standard benchmarks should meet.

**Weakness: Anchor derivation is opaque.** The floor (0.75) and ceiling (1.00) are documented as derived from "the 5-model pilot sweep plus margin," but the specific pilot data, the margin calculation, and the rationale for choosing these particular values over alternatives are not published. A reviewer cannot independently verify whether 0.75 is the right floor.

---

#### Clarity

**What does a normalized score of 0.5 mean?** A score of 0.5 corresponds to a raw mean 1-Brier of 0.875. Concretely: a model that is correct on ~90% of items at ~90% confidence, with occasional high-confidence errors, lands near this range. This is interpretable — it represents decent accuracy with moderate calibration quality.

**What does 0.8 mean?** Raw mean 1-Brier of 0.95. A model that is correct on ~95% of items at ~95% confidence with very few overconfident errors. This represents strong but not perfect calibration.

**What does 0.0 mean?** Raw mean 1-Brier of 0.75 or below. This is not random — a model that answered randomly at 50% confidence would score approximately 0.75 raw (since 1-(0.5-0)^2 = 0.75 on wrong items and 1-(0.5-1)^2 = 0.75 on correct items). A score of 0.0 normalized therefore represents performance no better than confident coin-flipping.

**Anchor justification concerns.** The ceiling of 1.00 (perfect 1-Brier) is a natural upper bound and unobjectionable. The floor of 0.75 is reasonable as a "chance-level" baseline but creates a compression effect: all meaningful variation is packed into a 0.25-wide raw band. This means small raw differences produce large normalized differences. For example, gemini-3-flash (raw 0.9631, normalized 0.853) and sonnet-4-6 (raw 0.9110, normalized 0.644) differ by only 0.052 in raw 1-Brier but 0.209 in normalized score. Whether this amplification helps or distorts depends on whether one believes the raw or normalized scale better reflects meaningful capability differences.

**Gemma-26b at 0.128.** This normalized score corresponds to a raw 1-Brier of 0.782, barely above the floor. The intensive audit reveals why: gemma-4-26b-a4b has catastrophically bimodal calibration. It scores perfectly on consensus items (1.0 on gen_b3_014, gen_b_038) but 0.0 on gen_b3_022 (wrong at confidence 1.0) and 0.19 on gen_b3_002 (wrong at 0.90). Its mean confidence is 0.968 — near-maximum — while its accuracy is only 76.0%. The combination of high confidence and low accuracy is exactly what Brier scoring is designed to punish. The low score is not a scoring artifact; it is a genuine signal that this model has poor metacognitive monitoring.

---

#### Reliability

**No dual-run for calibration.** Unlike abstention and self-correction (which have two runs), calibration uses a single run per model. There is no test-retest reliability estimate. This is a meaningful limitation: we cannot distinguish genuine model calibration from run-to-run variance due to temperature sampling, prompt sensitivity, or transient API behavior. A model scored at 0.644 might score 0.60 or 0.69 on a second run; we have no way to bound this uncertainty from the current data.

**Item sensitivity analysis.** The intensive audit of 5 items reveals that single items can dominate score differences:

- gen_b3_022 (4-letter US states): gemma-4-26b scores 0.0 (wrong at confidence 1.0). This single item drops its 105-item mean by ~0.0095, which translates to ~0.038 on the normalized scale. For a model near the floor, this is substantial.
- gen_a2_001 (sitting vs. smoking): produces a 0.86 gap between correct and incorrect clusters. Three models (gemini-2.5-pro, gemini-3-flash, gpt-5.4) all score 0.0975-0.1351 on this item — a single contested-claim question shifts their means appreciably.

With 105 items, no single item should dominate, and for the top models it does not. But for models with many high-confidence errors (gemma-26b has 22 "OC Wrong" items), the penalty accumulation is real and each such item compounds.

**Floor and ceiling effects.** The leaderboard shows compression at both ends:

| Model | Raw 1-Brier | Normalized | Accuracy | Mean Confidence | OC Wrong |
|-------|-------------|------------|----------|-----------------|----------|
| gemini-3-flash | 0.9631 | 0.853 | 96.2% | 0.975 | 4 |
| gemini-2.5-pro | 0.9480 | 0.792 | 94.3% | 0.970 | 5 |
| sonnet-4-6 | 0.9110 | 0.644 | 91.4% | 0.884 | 1 |
| sonnet-4 | 0.9005 | 0.602 | 89.5% | 0.882 | 4 |
| gemma-26b | 0.7820 | 0.128 | 76.0% | 0.968 | 22 |

The top two models are compressed near the ceiling (0.79-0.85 normalized), while gemma-26b sits near the floor. The middle band (0.60-0.65) contains both Anthropic models. GPT-5.4's calibration run is absent from the v6.2 aggregate leaderboard (its calibration data exists in per-item audits but not in the inventory or aggregate table), so its normalized score cannot be confirmed from the published data. This is a data completeness gap that should be resolved.

**Note on sonnet-4-6.** This model has only 1 overconfident wrong answer despite 91.4% accuracy (lower than gemini-2.5-pro's 94.3%). Its lower normalized score relative to gemini-2.5-pro comes not from catastrophic errors but from systematically lower confidence (0.884 vs. 0.970). Under Brier scoring, the model that is correct at 0.88 confidence scores worse than the model correct at 0.97 confidence, even though the less-confident model may be showing better epistemic humility. This is a genuine tension in the metric: 1-Brier rewards high confidence when correct, which conflates accuracy with calibration.

---

#### Utility

**Does it discriminate?** Yes. The 0.725 spread between gemini-3-flash (0.853) and gemma-26b (0.128) demonstrates that the metric captures real differences. The ordering is interpretable: models with high accuracy and high confidence score well; models with high confidence and low accuracy score poorly; models with moderate confidence score in between. This tracks the theoretical construct.

**What does gen_a2_001 reveal?** This single item is the most diagnostically valuable in the calibration set. It asks whether "sitting is as harmful as smoking" is true, false, or contested (gold: contested). The Anthropic models and gemma correctly identify the epistemic status; both Gemini variants and GPT-5.4 confidently answer "false" (0.93-0.95 confidence). The item cleanly separates models by their treatment of genuinely contested scientific claims — a core metacognitive skill. Models that collapse "contested" into "false" are failing at exactly the kind of epistemic monitoring MetaJudge aims to measure.

**Cross-model patterns from intensive audit.**

1. *Consensus items provide no discrimination.* gen_b3_014 (Supreme Court impeachments) and gen_b_038 (dietary fat) produce near-identical scores across all 6 models. Their contribution to mean 1-Brier is effectively constant. They serve as sanity checks but do not drive leaderboard ordering.

2. *Discriminating items cluster by model family, not by size.* On gen_a2_001, both Gemini models (flash and pro) fail identically despite different sizes. Both Anthropic models succeed. This suggests the signal is about training posture toward contested claims, not raw capability.

3. *gemma-26b has a distinctive failure mode: maximum confidence on wrong answers.* Of its 22 overconfident-wrong items, several are at confidence 1.0 (e.g., gen_b3_022), which yields the worst possible 1-Brier of 0.0. No other model shows this pattern at the same frequency. This is a genuine calibration deficit, not a scoring artifact.

4. *Boundary effects in numeric tolerance.* sonnet-4-6's answer of 46 on gen_b3_002 (tolerance floor 46.8) produces a binary flip from correct to incorrect over a 0.8 person/km^2 difference. The resulting 1-Brier drops from ~0.95 (if correct) to 0.48 — a 0.47-point swing on a single item from a near-miss. This is the sharpest example of how hard tolerance cutoffs interact with Brier scoring to produce discontinuous penalties.

---

#### Bugs and Issues

| # | Bug | Items Affected | Severity | Score Impact | Status |
|---|-----|----------------|----------|-------------|--------|
| 1 | **tri_label accepted_forms:** `false` listed in accepted_forms but tri_label grader checks canonical label before checking accepted_forms, so models answering `false` (a valid accepted form) are graded incorrect | gen_a4_022, gen_a4_024, gen_b_040, gen_a2_007 | **HIGH** | Up to +1.0 raw Brier per item per affected model. gen_a4_022 affects 4 models; gen_a4_024 affects 5 models. Worst case: a model gains ~0.038 normalized per item corrected. Total cross-model: ~9 false-negative grades across 5 models. | Fix deployed, not re-run |
| 2 | **exact_constant parser:** ASCII `^` notation with unit suffix (`mol^-1`) not parsed by exact_constant rule | gen_a_042 | **MEDIUM** | 1 false negative (gemma-26b, which answered correctly at confidence 1.0 and received 0.0 instead of 1.0). Impact: +0.0095 raw, +0.038 normalized for gemma-26b only. | Identified, not fixed |
| 3 | **code_output substring match:** substring matching produces false positive when model output contains extra tokens | v41_ce_014 | **MEDIUM** | 1 false positive (gemma-26b, which received credit it should not have). Impact: small negative correction (~0.009 raw) when fixed. | Identified, not fixed |
| 4 | **GPT-5.4 calibration data missing from aggregate table.** The model has per-item audit data and appears in the intensive audit, but its calibration normalized score is absent from the v6.2 leaderboard and inventory. | Full model | **MEDIUM** | Cannot confirm GPT-5.4's calibration ranking relative to other models from published aggregate data. | Data gap |
| 5 | **No dual-run reliability estimate.** Single-run design means score stability is unknown for all models. | All 105 items x all models | **LOW** (design limitation, not a bug) | Cannot bound confidence intervals on any calibration score. | By design |

**Net bug impact on gemma-26b (most affected model):** Bugs #1 and #2 are false negatives (underscoring); bug #3 is a false positive (overscoring). Net correction: approximately +2 items corrected, -1 item corrected = +1 net item, shifting raw 1-Brier by roughly +0.005-0.010. This would move gemma-26b from 0.128 to approximately 0.15 normalized — still near the floor. The bugs do not change the qualitative story for any model.

---

#### Recommendations for v7

1. **Publish anchor derivation data.** Release the 5-model pilot sweep scores, the margin calculation, and the rationale for the [0.75, 1.00] band. Consider whether a tighter floor (e.g., 0.80) better separates meaningful performance, or whether the current floor correctly captures that some models genuinely perform near chance.

2. **Add dual-run calibration.** Run each model twice on the full 105-item set (different random seed or sampling temperature) and report the score delta. If the median delta exceeds 0.05 normalized, the single-run design is unreliable. This is the single most important reliability improvement available.

3. **Fix and re-run known bugs.** The tri_label accepted_forms fix is deployed but scores have not been regenerated. Re-run all 6 models on the corrected grading engine and publish both original and corrected scores. Fix the exact_constant parser and code_output substring match before v7 launches.

4. **Soften numeric tolerance boundaries.** Replace the hard +-10% cutoff in `approx_numeric_dynamic` with a graded penalty (e.g., sigmoid decay around the tolerance boundary). The current system produces a discontinuity where 46.8 is correct and 46.0 is fully wrong. A graduated approach would assign partial credit proportional to distance from gold, reducing the influence of arbitrary boundary placement on Brier scores.

5. **Report decomposed calibration statistics.** Alongside the normalized score, report: (a) raw accuracy, (b) mean confidence, (c) number of overconfident-wrong items, (d) expected calibration error (ECE) in confidence bins. The current single-number score conflates accuracy and calibration. A model with 95% accuracy at 97% confidence and a model with 85% accuracy at 87% confidence are both well-calibrated, but they receive very different 1-Brier scores. Decomposed statistics would let readers distinguish "this model is inaccurate but knows it" from "this model is inaccurate and does not know it."

6. **Tag items by discrimination power.** The intensive audit shows that consensus items (gen_b3_014, gen_b_038) contribute no signal while discriminating items (gen_a2_001, gen_b3_022) drive most of the leaderboard variance. For v7, compute and publish per-item discrimination indices (e.g., point-biserial correlation between item score and total score across models). Consider weighting high-discrimination items more heavily, or at minimum, reporting the effective number of discriminating items so readers understand how many of the 105 items actually matter.

7. **Resolve GPT-5.4 calibration data gap.** Either include the calibration run in the aggregate table or document why it is excluded. A model that appears in intensive per-item audits but not in the leaderboard creates confusion about the benchmark's completeness.

8. **Add confidence-conditional analysis.** Report how models perform specifically on items where they express high confidence (>0.90) vs. low confidence (<0.70). This would directly measure the metacognitive monitoring signal — whether confidence predicts correctness — rather than relying solely on the aggregate Brier score, which can be gamed by uniformly moderate confidence.
