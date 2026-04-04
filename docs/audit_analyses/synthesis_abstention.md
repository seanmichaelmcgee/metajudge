# Synthesis: Abstention Scoring Assessment

**Benchmark:** MetaJudge v6.2 | **Task:** Abstention (Family B)
**Date:** 2026-04-04 | **Items:** 72 | **Models:** 6

---

## Model Summary

| Model | UWAA | Normalized | Action Accuracy | Answer Rate |
|-------|------|------------|-----------------|-------------|
| sonnet-4 | 0.847 | 0.616 | 62.5% | moderate |
| flash | 0.841 | 0.602 | 59.7% | moderate |
| gpt-5.4 | 0.820 | 0.550 | 59.7% | moderate |
| gemma-26b | 0.793 | 0.482 | 60.6% | moderate |
| sonnet-4.6 | 0.758 | 0.396 | 41.7% | high |
| gemini-pro | 0.704 | 0.260 | 38.9% | 73.6% |

---

## 1. Transparency

**Rating: Adequate with caveats**

The payoff matrix is fully documented in `docs/scoring_overview.md` and the intensive audit traces each cell lookup explicitly. A reader can reconstruct any model's utility score from the matrix and the action/correctness labels. The 5x4 matrix structure, anchor normalization formula (floor=0.60, ceiling=1.00), and UWAA transform are all public.

However, two transparency gaps exist:

**The `is_correct` column is misleading.** For non-answer gold items, `is_correct` conflates action correctness with content-answer matching. The GPT-5.4 audit found 28 items with `utility=1.0` but `is_correct=False` because the model chose the correct non-answer action (clarify/verify/abstain) but the column checked content against a gold answer that does not exist for these items. The CSV-level action accuracy (15/72) undercounts the MD-report figure (43/72) by exactly these 28 items. A downstream analyst using only the CSV would draw wrong conclusions about GPT-5.4's performance.

**Partial credit rationale is unstated in the matrix.** The +0.3 value for off-diagonal non-answer actions is described as rewarding "epistemic caution" but the document does not justify why 0.3 rather than 0.1 or 0.5. The choice matters: it is the single parameter most responsible for compressing the score range (see Reliability below).

---

## 2. Clarity

**Rating: Good**

The four-action taxonomy (answer/clarify/verify/abstain) is well-defined and the gold-action assignments are generally defensible. The intensive audit items demonstrate that the action boundaries carry real semantic weight: abs_026 ("How long is the race?") cleanly separates clarify (+1.0) from abstain (+0.3) from answer (-0.5), producing three distinct score tiers that map to meaningfully different model behaviors.

Two clarity weaknesses:

**The verify/abstain boundary is underspecified.** Item abs_028 (Bitcoin price) reveals that the distinction between "I cannot help" (abstain) and "here is how to get the answer" (verify) depends on subtle framing rather than categorical differences. Three models that correctly identified the knowledge-cutoff limitation chose abstain over verify, receiving +0.3 instead of +1.0. The 0.7-point penalty for this distinction is steep given that the behavioral difference is a single redirecting sentence. The scoring spec does not provide clear decision rules for when a question requires verify versus abstain.

**Salient-referent bias inflates item difficulty artificially.** Item abs_019 ("How big is Amazon?") penalizes models that resolve the ambiguity toward the dominant referent (the company). Three of six models answered with company metrics. The question is genuinely ambiguous, but the 3/6 split may reflect training-data salience rather than metacognitive failure. A model that provides a correct, useful answer about the company receives -0.5, which is arguably harsh when the referent bias is an item-design property rather than a model deficiency.

---

## 3. Reliability

**Rating: Concerning**

This is the weakest dimension. Three specific problems:

### 3a. Partial credit compresses the score range

The +0.3 partial credit for off-diagonal non-answer actions is the dominant feature of the scoring system. Consider Gemini Pro: 38.9% action accuracy but UWAA = 0.704, which normalizes to 0.260. The partial credit system converts a model that gets the specific action wrong nearly two-thirds of the time into one that still scores above the random-action floor. The mechanism:

- When gold=clarify and model=abstain: +0.3 instead of the "correct" +1.0
- When gold=verify and model=abstain: +0.3 instead of +1.0
- When gold=abstain and model=clarify: +0.3 instead of +1.0

A model that always abstains on every non-answer item would collect +0.3 on every clarify, verify, and abstain item (losing only the 0.7 differential on clarify and verify golds, gaining full +1.0 on abstain golds). Combined with correct answers on answerable items, this "always abstain on uncertain items" strategy produces a competitive UWAA without any genuine action discrimination.

The practical consequence: the 6-model spread on normalized abstention is only 0.356 (0.260 to 0.616), compared to 0.725 for calibration. The partial credit system reduces the task's discriminative power.

### 3b. The abs_002 and abs_006 grading errors are confirmed

**abs_002 (false positive):** Gold=Lithium, model (sonnet-4.6) answered Helium, graded `is_correct=True` with utility +1.0. This is a factual grading error — Lithium has the highest second ionization energy (7298 kJ/mol), not Helium (5250 kJ/mol). The grader incorrectly accepted the wrong answer.

**abs_006 (Unicode minus):** Gold="3n - 6", model (sonnet-4.6) answered "3n - 6" verbatim but was graded `is_correct=False` with utility -1.0. The mismatch is likely U+2212 (minus sign) versus U+002D (hyphen-minus) in the extraction step. This is a grading extraction bug that costs the model 2.0 utility points on a single item.

These two errors partially cancel for sonnet-4.6 (+1.0 undeserved on abs_002, -2.0 undeserved on abs_006, net -1.0 error) but they demonstrate that the grading pipeline has both false-positive and false-negative failure modes on the same model.

### 3c. The "verify" action is structurally disadvantaged

Across all audited models, verify is the least-selected action. The Gemini Pro audit shows only 5/72 verify selections (6.9%). This is not because verify items are rare in the dataset but because models' RLHF training rewards refusal (abstain) over redirection (verify). The payoff matrix correctly values verify at +1.0 for verify-gold items, but the +0.3 partial credit for abstain-when-gold-is-verify means models pay only a 0.7 penalty for collapsing verify into abstain. Given that verify requires a specific behavioral pattern (redirecting the user to an external source) that few models have been trained to produce, the task may be measuring RLHF training choices rather than metacognitive control.

---

## 4. Utility

**Rating: Mixed**

The abstention task measures something real. The intensive audit confirms that models differ meaningfully in their ability to detect ambiguity (abs_019, abs_026) and knowledge-boundary awareness (abs_028). The 3/6 splits on discriminating items are not noise — they reflect genuine capability differences traceable to specific model behaviors.

However, the task's utility is undermined by a central tension:

**Does the scoring reward metacognitive control or cautious disposition?** The data suggest the latter dominates. The final evaluation report notes that "models that answer less score better on abstention." This is expected given the payoff structure: the worst outcomes (-1.0, -0.5) all come from answering, while the worst non-answer outcome is -0.3 (clarifying when you should answer) or -0.2 (verifying/clarifying when you should answer). A risk-averse model that defaults to non-answer actions faces a much smaller downside than a model that defaults to answering.

The sonnet-4.6 case is instructive: 41.7% action accuracy but UWAA = 0.758. The model does not discriminate well between action types, but its tendency to choose non-answer actions (abstain on abs_026, abstain on abs_028) collects enough partial credit to maintain a moderate score. Meanwhile, Gemini Pro at 38.9% action accuracy but with a 73.6% answer rate scores UWAA = 0.704. The difference between these two models is primarily answer rate, not action discrimination quality.

The cross-model audit provides some reassurance: 98.8% agreement rate across 1137 items, with only 5 flags and 0 disagreements in the abstention task specifically. The pipeline is mechanically reliable even where the scoring design choices are debatable.

---

## 5. Confirmed Bugs

| ID | Item | Description | Impact | Status |
|----|------|-------------|--------|--------|
| B1 | abs_002 | False positive: Helium accepted as correct when gold is Lithium | +1.0 undeserved utility for affected models | Open |
| B2 | abs_006 | Unicode minus (U+2212) vs hyphen (U+002D) causes extraction failure | -2.0 utility swing (from +1.0 to -1.0) for sonnet-4.6 | Open |
| B3 | CSV export | `is_correct` column conflates action correctness with content match | Undercounts action accuracy for models choosing correct non-answer actions (GPT-5.4: 15 vs 43) | Open |

---

## 6. Recommendations for v7

### R1. Re-examine partial credit value (+0.3)

The +0.3 off-diagonal partial credit is the most consequential design parameter in the scoring system and it lacks empirical justification. Consider:
- **Option A:** Reduce to +0.1, increasing the penalty for wrong-but-cautious actions and widening the score range.
- **Option B:** Make partial credit asymmetric — e.g., abstain-when-gold-is-clarify gets +0.1 (lost opportunity to help) while clarify-when-gold-is-abstain gets +0.3 (overcautious but interactive).
- **Option C:** Empirically calibrate the value by testing what partial-credit level maximizes rank-order stability across dual runs.

### R2. Split the `is_correct` column

Replace with two columns: `action_correct` (boolean: model action matches gold action or is in acceptable alternatives) and `content_correct` (boolean: answer content matches gold, NA for non-answer actions). This eliminates the CSV/MD discrepancy found in the GPT-5.4 audit.

### R3. Tighten the verify/abstain boundary

Provide explicit decision rules in the gold-action justifications: verify applies when the question is answerable in principle but requires a source the model cannot access (real-time data, personal records, behind-paywall content). Abstain applies when the question is genuinely unanswerable even with external resources (incoherent premise, undefined terms). This would reduce the verify/abstain conflation pattern observed in abs_028.

### R4. Add answer-rate controls to the scoring

The current system does not directly penalize over-answering as a disposition. Consider adding a calibration penalty: if a model's answer rate exceeds the base rate of answer-gold items by more than a threshold (e.g., 15 percentage points), apply a small UWAA discount. This would separate models that score well through action discrimination from those that score well through cautious blanket non-answering.

### R5. Fix known grading bugs before v7

- Add U+2212 to the character normalization step in the grading pipeline (abs_006).
- Audit abs_002 gold answer across all models and correct the grader's accepted-forms list.
- Both fixes are mechanical and should not require re-running the full benchmark.

### R6. Address salient-referent bias in item design

Items like abs_019 ("How big is Amazon?") penalize models for resolving ambiguity toward the dominant referent. For v7, either (a) ensure clarify-gold items have genuinely balanced referents (no single interpretation dominates), or (b) add accepted-alternative credit for answers that acknowledge the ambiguity even while choosing one interpretation.

---

## Summary Judgment

The abstention scoring system is mechanically sound — the cross-model audit confirms 98.8% agreement and the payoff matrix is applied consistently. The core design (4-action taxonomy, utility matrix, UWAA normalization) is defensible as a framework for measuring metacognitive control.

However, the partial credit system (+0.3) compresses the score range enough that the task's discriminative power is substantially reduced. A model with ~40% action accuracy can score a normalized 0.26-0.40, which is closer to the middle of the range than the action accuracy alone would suggest. The scoring rewards cautious disposition (low answer rate) almost as much as it rewards genuine action discrimination, making it difficult to distinguish between a model that understands when to clarify versus verify versus abstain and a model that simply defaults to non-answer actions when uncertain.

The two grading bugs (abs_002 false positive, abs_006 Unicode minus) are individually small but collectively demonstrate that the grading pipeline needs character-normalization hardening and gold-answer validation. The `is_correct` column ambiguity is a data-export problem that could mislead downstream analysts.

For v7, the highest-priority change is reconsidering the +0.3 partial credit value with empirical evidence rather than intuition. The second priority is splitting the verify/abstain decision boundary with explicit, documented criteria.
