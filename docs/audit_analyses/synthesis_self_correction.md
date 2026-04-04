# Self-Correction (C1 + C2) -- Scoring Assessment

> Part of the MetaJudge v6.2 Synthesis Audit. Evaluates whether C1/C2 scoring
> is transparent, clear, reliable, and useful -- and identifies concrete
> improvements for v7.

---

## What It Measures / How It Scores

Self-correction tasks test whether a model can detect and repair its own errors
(C1, no evidence) or integrate reviewer evidence to improve (C2, with evidence).
Each item follows a two-turn protocol: T1 answer, then T2 revision opportunity.

The scoring system has two layers that do not fully align:

1. **Transition scores** (defined in `self_correction_v2.py` and
   `family_c_scoring.yaml`): Six transition types with asymmetric base scores
   (e.g., maintain_correct=+0.60, damage=-0.40/-0.50) plus a confidence
   adjustment in [-0.15, +0.10]. These are rescaled from [-0.65, +0.65] to
   [0, 1].

2. **Accuracy delta** (used in production notebooks for the submitted score):
   `(T2_correct - T1_correct) / n`, anchor-normalized with C1 anchors
   [-0.10, +0.15] and C2 anchors [-0.20, +0.20].

The production notebook (`metajudge_sc_c1.ipynb`) computes and returns the
accuracy-delta normalized score. The transition-based scoring module is imported
only for `classify_transition` -- the `score_item` and `compute_family_c_headline`
functions are never called. The confidence adjustment, the asymmetric base-score
weights, and the rescaling logic in `self_correction_v2.py` have no effect on
the submitted score. This is the single most important finding in this
assessment: documented scoring mechanics and production scoring diverge.

---

## Transparency

**Can you trace T1 -> T2 -> transition -> score?**

Partially. The audit trail from T1 answer through T2 answer to transition
classification is clean and fully traceable. Each item's `classify_transition`
call is deterministic given `correct_before`, `correct_after`, and `revised`.
The six transition labels are well-defined and mutually exclusive.

The break occurs at the scoring step. A reader of `scoring_overview.md` would
expect transition base scores and confidence adjustments to determine the
headline number. Instead, the headline score collapses to a simple accuracy
delta: how many items flipped from wrong to right minus how many flipped from
right to wrong, divided by item count, then anchor-normalized. The transition
labels, base scores, and confidence adjustments appear in audit CSVs and
diagnostic reports but do not affect the returned score.

This means the documented damage:gain asymmetry (damage penalty exceeds
correction reward) is not operative. Under accuracy delta, one damage event
exactly cancels one correction gain. A model that damages two correct answers
and corrects two wrong ones scores delta=0, which normalizes to 0.40 for C1.
Under the transition system, that model would score substantially below 0.40
because damage=-0.40 is not offset by correction_gain=+0.20.

**Verdict:** Transition classification is transparent. The gap between documented
scoring and production scoring is a transparency failure.

---

## Clarity

**What does normalized 0.400 mean? What does 0.257 mean?**

Under the production metric (accuracy delta with C1 anchors [-0.10, +0.15]):

- **0.400** means delta = 0, i.e., zero net change in accuracy between T1 and
  T2. The model neither improved nor degraded. With 28 C1 items, 0.400 = (0 -
  (-0.10)) / (0.15 - (-0.10)) = 0.10/0.25 = 0.40. This is the "did nothing"
  baseline.

- **0.257** means delta = -1/28 = -0.0357, i.e., one net item flipped from
  correct to incorrect. Normalized: (-0.0357 - (-0.10)) / 0.25 = 0.0643/0.25
  = 0.257.

The clustering is severe. Flash, Sonnet 4, Gemma-26b, and GPT-5.4 all land at
0.400 (zero delta). Sonnet 4.6 and Gemini Pro land at 0.257 (one net damage).
With n=28, the metric has only about 6-7 distinguishable levels in the range
models actually occupy. The resolution is roughly 1/28 = 0.036 raw, which maps
to 0.143 normalized. Two models cannot be separated unless they differ by at
least one net item flip.

For C2 (n=23, anchors [-0.20, +0.20]):

- **0.500** means delta=0 (zero net change). This is also the "did nothing"
  baseline for C2.
- **0.283** (Gemini Pro) and **0.391** (Gemma-26b) reflect one or two net
  damage events.

**Verdict:** The scores are interpretable once you know the production metric,
but the fact that 0.400 means "no change" rather than "moderate self-correction
ability" is counterintuitive. A normalized score of 0.40 sounds mediocre; it
actually means the model held steady, which is arguably good behavior given that
damage dominates correction in the audit data. The scoring frame penalizes
stability by placing it below the midpoint.

---

## Reliability

**n=28 (C1) / n=23 (C2), stochasticity, item sensitivity, clustering**

### Sample size

With n=28, a single item flip moves the C1 score by 0.143 normalized. The
effective resolution is about 7 distinguishable bins across [0, 1]. For C2
(n=23), each item flip moves the score by approximately 0.109 normalized. These
are coarse instruments. Any claim about rank ordering between models separated
by less than one item flip is noise, not signal.

### Stochasticity

The intensive audit reports C1 run-to-run swing up to 0.29 normalized. This
means the same model on the same items can shift by roughly two item-flips
between independent runs. A model scoring 0.400 on one run could score 0.257 or
0.543 on the next. The 90% confidence interval around any single C1 score spans
approximately half the observed model range.

The dual-run protocol in the notebook is a valuable diagnostic but does not
solve the problem -- it only reveals the magnitude of instability for a single
model-run pair.

### Item sensitivity

The audit identified 4/10 sampled items (40%) that showed 6/6 correct at both
T1 and T2, contributing only `maintain_correct` transitions. These items
contribute delta=0 and add no discriminating information. They consume budget
without producing signal. In a 28-item set, if a similar proportion (~11 items)
are consensus-correct, the effective discriminating item count drops to roughly
17, worsening resolution further.

### Clustering

The observed score distribution is:
- C1: {0.257, 0.400} -- two distinct values across six models
- C2: {0.283, 0.391, 0.500} -- three distinct values

This is a near-total collapse of the scoring distribution. The metric cannot
differentiate Flash from Sonnet 4 from Gemma-26b (all at C1=0.400) despite
these models having visibly different self-correction behaviors in the item-level
audit. The transition-level data shows meaningful differences (e.g., Flash
produces identical T1/T2 text with similarity=1.0 on multiple items; Sonnet 4
shows genuine reconsideration). None of this appears in the headline score.

**Verdict:** Reliability is poor. Small n, high stochasticity, and coarse
resolution combine to produce a metric that cannot reliably distinguish models
that behave differently.

---

## Utility

**Does the C1/C2 split add value? Deceptive traps vs. other items?**

### C1/C2 split

The split is conceptually well-motivated: C1 tests intrinsic error detection,
C2 tests evidence integration. In practice:

- C1 and C2 scores are moderately correlated across models (both penalize Gemini
  Pro most heavily; both assign "did nothing" scores to the same cluster).
- The C2 evidence types create genuinely different challenges: deceptive traps
  and weak challenges produce damage; right-to-right items with irrelevant
  evidence produce nothing. The split has value, but it is currently obscured by
  the accuracy-delta metric that collapses evidence-type effects into a single
  number.

The C2 evidence types should be broken out as diagnostic sub-scores rather than
averaged together.

### Deceptive traps vs. other items

The audit's strongest finding is that deceptive traps (dt_001, wc_005) are the
best discriminators. They produced the only clear model separations in C2:
Gemini Pro failed both, Gemma-26b failed dt_001, all others survived. These
items have a fundamentally different character from wrong-to-right or
right-to-right items -- they test epistemic robustness under social/authority
pressure rather than error detection.

The current scoring treats a deceptive-trap damage event identically to any
other damage event under the accuracy-delta metric. Under the transition system,
C2 misleading items use a reduced damage penalty (-0.40 instead of -0.50), which
partially addresses this -- but as noted, this logic is not active in production.

### Audit-level richness vs. headline poverty

The item-level audit data (transition types, similarity scores, confidence
deltas, per-model patterns) is far richer than what the headline score captures.
The audit identified that damage dominates correction 9:3 across 60 pairs, that
wr_023 functions as a right-to-wrong trap, that Gemini Pro is uniquely
susceptible to authority pressure, and that gpt-5.4 has an answer-extraction
vulnerability. None of these findings are visible in the headline scores.

**Verdict:** The C1/C2 split adds conceptual value but the headline metric
discards most of the information that makes the split useful. The real utility
is in the audit trail, not the number.

---

## Bugs

### 1. Scoring pipeline divergence (Critical)

`scoring_overview.md` documents transition-based scoring with asymmetric
damage:gain weights and confidence adjustments. The production notebook computes
accuracy delta. The transition scoring module (`self_correction_v2.py`) is
imported but its scoring functions are unused. This is not a minor documentation
gap -- it means the stated scoring philosophy (damage costs more than correction
helps) is not implemented in production.

### 2. sc_c1_wr_023 stratum misclassification (High)

Item wr_023 ((-1)^(2/6)) is labeled `wrong_to_right` with normative T2 action
`revise`. In practice, all 6 models answered T1 correctly. The item functions as
a right-to-wrong trap with a 4/6 damage rate. The stratum label is empirically
wrong, which means:
- Transition scoring logic that conditions on stratum will misinterpret this item
- Diagnostic sub-metrics (e.g., "wrong-to-right correction rate") are polluted
- The item cannot fulfill its designed purpose (testing error correction) because
  there is no T1 error to correct

### 3. Confirmation detection gaps (Medium)

Items rr_008, rr_009, and wc_005 have reported confirmation detection failures.
The `resolve_t2_answer` function is designed to handle cases where the model
confirms without restating, but edge cases slip through. When a model says
"I confirm my answer" without restating it, the T2 answer may be extracted as
empty or default, potentially causing false damage or failed-revision
classifications.

### 4. Answer extraction vulnerability -- gpt-5.4 (Medium)

gpt-5.4's verbose T2 format ("No error -- [full explanation]") caused a likely
false negative on wr_001 (model stated the correct answer "12" but was graded
incorrect) and a genuine arithmetic slip on wr_008. The answer extraction
pipeline does not robustly handle this model's output format, introducing
systematic bias against verbose responders.

### 5. Similarity metric anomaly (Low)

gpt-5.4 on wr_008 shows similarity=0.99 despite changing its answer from 110
to 11. The edit-distance similarity captures text-level overlap but not semantic
change. A model that changes one digit in a long response gets high similarity
despite being wrong. The similarity metric is diagnostic-only but could mislead
auditors.

---

## Recommendations for v7

### 1. Align production scoring with documented scoring

Either (a) activate the transition-based scoring in production notebooks, using
`score_item` and `compute_family_c_headline` from `self_correction_v2.py`, or
(b) update `scoring_overview.md` to accurately describe the accuracy-delta
metric. Option (a) is preferred because the transition system captures
meaningful distinctions (maintain_correct vs. neutral_revision, damage vs.
failed_revision) that accuracy delta discards.

### 2. Increase item count to n >= 50 per subfamily

With n=28 (C1) and n=23 (C2), the metric cannot distinguish models separated by
less than one item flip. Doubling the item count to 50+ would halve the
per-item-flip impact and narrow the stochasticity window. Priority should be on
adding discriminating items (see below), not more consensus-correct items.

### 3. Replace consensus-correct items

The 4 items identified as 6/6 correct at both T1 and T2 (wr_004, rr_001,
c2_wr_001, c2_rr_001) should be replaced with items that produce genuine
wrong-to-right opportunities or, failing that, deceptive traps that test
epistemic robustness. Each consensus item replaced with a discriminating item
improves effective resolution more than adding two new consensus items.

### 4. Reclassify or redesign wr_023

Either relabel wr_023 as a deceptive-trap item (its empirical function) or
redesign it so that T1 errors are common. The current mismatch between design
intent and empirical behavior corrupts stratum-level analytics.

### 5. Add multi-run aggregation

Require 3+ independent runs per model and report the median score with
interquartile range. The current dual-run protocol reveals stochasticity but
does not mitigate it. With run-to-run swings of 0.29, a single run score is
not a reliable estimate.

### 6. Break out C2 evidence-type sub-scores

Report separate sub-scores for C2 evidence types: deceptive trap, weak
challenge, supportive evidence, irrelevant context. The deceptive-trap items
are measuring something fundamentally different (authority resistance) from
supportive-evidence items (evidence integration). Averaging them together
obscures the most informative signal in C2.

### 7. Harden answer extraction

The gpt-5.4 extraction failures and confirmation detection gaps indicate that
the parsing pipeline needs additional robustness testing against verbose and
terse response formats. Specific fixes:
- Handle "No error -- [answer]" format explicitly
- Improve confirmation-without-restatement detection for rr_008, rr_009, wc_005
- Add extraction regression tests using observed failure cases from the audit

### 8. Report effective item count alongside headline score

Publish the number of items that actually produced non-trivial transitions
(anything other than 6/6 maintain_correct) as a quality indicator. If 40% of
items are non-discriminating, users should know the effective n is 17, not 28.
