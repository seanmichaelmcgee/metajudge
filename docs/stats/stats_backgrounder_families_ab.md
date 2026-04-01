# MetaJudge v0.5.5.1 — Statistical Testing Backgrounder

## 1. Introduction

MetaJudge is a benchmark measuring metacognitive behavior in large language models.
Statistical comparisons between models must account for three structural features
of the data: (a) observations are **paired** — the same items are administered to
every model, creating natural within-item dependencies; (b) sample sizes are
**moderate** (n = 117 calibration items, n = 84 selective-abstention items),
placing the analysis in a regime where large-sample approximations are not always
reliable; and (c) the primary scoring metrics (Brier scores, utility payoffs) have
**non-normal, bounded distributions** that discourage parametric assumptions.

For these reasons, MetaJudge's statistical framework is **non-parametric by
default**, relying on exact tests, permutation procedures, and bootstrap
resampling rather than t-tests or ANOVA. All pairwise comparisons are corrected
for multiple testing using familywise error-rate control.

---

## 2. Statistical Tests

### 2.1 McNemar's Test

McNemar's test (McNemar, 1947) is the standard method for comparing two
classifiers evaluated on the same test set when the outcome is binary
(correct / incorrect). It considers only the **discordant pairs** — items where
one model is correct and the other is wrong — and tests whether the two
directions of disagreement are equally likely under the null hypothesis.

**Why chosen for MetaJudge:** Each calibration item yields a binary correctness
judgment per model, and all models see the same items. McNemar's test is the
natural paired test for this structure, recommended by Dietterich (1998) as the
preferred statistical test for comparing supervised classifiers.

**Implementation detail:** For small discordant counts (n < 25), the exact
binomial test is used; for larger counts, the chi-squared approximation with
continuity correction is applied.

**Leading alternatives considered:**
- *Cochran's Q test* — extends McNemar's to simultaneous comparison of k > 2
  classifiers (Cochran, 1950). Rejected because it provides only an omnibus
  "any difference" verdict, losing pairwise granularity. It may be added as a
  gatekeeper test when the model count exceeds 8.
- *Exact conditional test (Edwards, 1948)* — provides exact p-values without
  continuity correction but is computationally heavier and unnecessary given
  the binomial fallback already implemented.

### 2.2 Paired Permutation Test

The paired permutation test (Good, 2005; Pesarin & Salmaso, 2010) is a
distribution-free hypothesis test for the difference in means of two paired
samples. Under the null hypothesis that the two score distributions are
exchangeable, the test randomly flips the sign of each paired difference and
recomputes the test statistic across many iterations, constructing an empirical
null distribution.

**Why chosen for MetaJudge:** Brier scores and utility values are continuous but
bounded on [0, 1] and [-1, 1] respectively, with distributions that are
typically skewed and zero-inflated. The permutation test makes no distributional
assumptions beyond exchangeability under the null, making it strictly more
general than the Wilcoxon signed-rank test.

**Implementation detail:** 10,000 permutations are used with a fixed random
seed (42) for reproducibility. The two-sided p-value is computed as
(count + 1) / (n_perm + 1), following the recommendation of Phipson and Smyth
(2010) to avoid zero p-values.

**Leading alternatives considered:**
- *Wilcoxon signed-rank test* — a classical non-parametric paired test
  (Wilcoxon, 1945). Rejected because it assumes a symmetric distribution of
  differences, which Brier score differences often violate.
- *Paired t-test* — parametric, assumes normal differences. Rejected due to
  bounded, skewed score distributions.

### 2.3 Bootstrap Confidence Intervals

The percentile bootstrap (Efron, 1979; Efron & Tibshirani, 1993) constructs
confidence intervals by resampling with replacement from the observed data.
For paired comparisons, the item-level differences are resampled; for
single-sample estimates, the raw scores are resampled. The α/2 and
1 − α/2 percentiles of the bootstrap distribution define the interval.

**Why chosen for MetaJudge:** Bootstrap CIs complement hypothesis tests by
quantifying the **magnitude and uncertainty** of effects, not just statistical
significance. They require no distributional assumptions and are straightforward
to implement for any summary statistic.

**Implementation detail:** 10,000 bootstrap resamples, seed = 42, percentile
method. Both paired-difference CIs and single-sample CIs are provided.

**Leading alternatives considered:**
- *BCa (bias-corrected and accelerated) bootstrap* — provides higher-order
  accuracy for skewed distributions (Efron, 1987). Rejected because the added
  complexity yields marginal benefit at n = 117, and the percentile method is
  more transparent.
- *Bayesian credible intervals* — would require specifying priors for Brier
  scores. Rejected to maintain a frequentist framework consistent with the
  other tests.

### 2.4 Stuart-Maxwell Test

The Stuart-Maxwell test (Stuart, 1955; Maxwell, 1970) is an extension of
McNemar's test to square contingency tables with k > 2 categories. It tests
marginal homogeneity — whether the row and column marginals of a paired
k × k table are equal — which corresponds to asking whether two models have
the same distribution of predicted actions.

**Why chosen for MetaJudge:** Family B items require models to choose among
four actions (answer, clarify, verify, abstain). Comparing the action
distributions of two models on the same items requires a paired multi-category
test. The Stuart-Maxwell test is the standard choice.

**Implementation detail:** The test statistic follows a chi-squared distribution
with k − 1 degrees of freedom under the null. For singular or near-singular
variance matrices, the Moore-Penrose pseudoinverse is used.

**Leading alternatives considered:**
- *Bhapkar test* — asymptotically equivalent to Stuart-Maxwell but uses a
  different variance estimator (Bhapkar, 1966). Less widely known; rejected
  for familiarity and interpretability.
- *McNemar-Bowker test of symmetry* — tests whether the off-diagonal cells
  are symmetric, which is a stronger hypothesis than marginal homogeneity.
  Rejected because we specifically want to compare marginals, not symmetry.

### 2.5 Spearman Rank Correlation

Spearman's rank correlation coefficient (Spearman, 1904) measures the monotonic
association between two variables by computing the Pearson correlation on their
ranks. It is non-parametric and robust to outliers and non-linear relationships.

**Why chosen for MetaJudge:** The bridge analysis examines whether higher model
confidence is associated with higher accuracy. This is a monotonic relationship
question (not necessarily linear), making Spearman's ρ the natural choice.
Bootstrap CIs are provided for inferential precision.

**Leading alternatives considered:**
- *Kendall's τ* — another rank correlation that is more robust to ties and has
  a simpler variance formula (Kendall, 1938). Rejected because Spearman's ρ
  has greater statistical power for continuous data without excessive ties.
- *Pearson's r* — assumes linear relationship and bivariate normality. Rejected
  because confidence-accuracy relationships are typically non-linear.

### 2.6 Holm-Bonferroni Correction

The Holm-Bonferroni procedure (Holm, 1979) is a sequentially rejective method
for controlling the familywise error rate (FWER) when conducting multiple
hypothesis tests. It orders p-values from smallest to largest and compares each
to α / (m − rank + 1), stopping at the first non-rejection.

**Why chosen for MetaJudge:** With 5 models producing 10 pairwise comparisons
and multiple test types per pair, the raw number of hypothesis tests ranges from
20 to 40+. Without correction, the probability of at least one false positive
becomes unacceptably high. Holm-Bonferroni is uniformly more powerful than the
classical Bonferroni correction while maintaining strong FWER control.

**Leading alternatives considered:**
- *Benjamini-Hochberg (BH) procedure* — controls the false discovery rate
  (FDR), which is less conservative than FWER (Benjamini & Hochberg, 1995).
  Rejected for the current 5-model analysis because FWER control is preferred
  for benchmark validation claims. BH may be adopted when model count exceeds
  8, as Holm becomes overly conservative at 100+ comparisons.
- *Bonferroni correction* — the simplest FWER method. Rejected because Holm
  is uniformly more powerful with no added complexity.

---

## 3. Scoring Metrics

### 3.1 Brier Score

The Brier score (Brier, 1950) is a strictly proper scoring rule that measures
the accuracy of probabilistic predictions. For a single item with stated
confidence c and binary outcome y ∈ {0, 1}:

    Brier = (c − y)²

A strictly proper scoring rule has the unique property that the expected score
is minimized (for lower-is-better formulations) when the stated confidence
equals the true probability of being correct (Gneiting & Raftery, 2007). This
makes it impossible to systematically improve one's Brier score by misreporting
confidence — the optimal strategy is honest calibration.

MetaJudge reports the affine transform 1 − Brier (higher-is-better, range
[0, 1]) in leaderboards, but statistical tests operate on the raw Brier loss.

### 3.2 Expected Calibration Error (ECE)

Expected Calibration Error (Naeini, Cooper, & Hauskrecht, 2015) partitions
predictions into bins by confidence level and measures the weighted average
gap between confidence and accuracy within each bin:

    ECE = Σ (|B_k| / N) · |acc(B_k) − conf(B_k)|

ECE is used as a **diagnostic metric** in MetaJudge (not in scoring) because
it captures a complementary aspect of calibration quality that Brier scores
can obscure — specifically, the systematic direction and pattern of
miscalibration across the confidence spectrum.

### 3.3 Utility-Weighted Action Accuracy (UWAA)

UWAA is a project-specific metric for Family B (selective abstention) that
normalizes the mean per-item utility to [0, 1]:

    UWAA = (mean_utility + 1.0) / 2.0

The utility for each item is determined by a 5 × 4 payoff matrix that maps
(model_decision × gold_action) pairs to scalar rewards in [-1, +1]. The
matrix is designed so that correct answers to answerable questions yield +1.0,
incorrect answers to answerable questions yield -1.0, and appropriate
deferral actions (clarify, verify, abstain) yield partial credit.

---

## 4. Effect Size Measures

### 4.1 Cohen's d (Paired)

For continuous paired differences (Brier scores, utility):

    d = mean(A − B) / sd(A − B)

Conventional thresholds: |d| < 0.2 negligible, 0.2–0.5 small, 0.5–0.8
medium, > 0.8 large (Cohen, 1988). These thresholds are guidelines, not
absolute cutoffs.

### 4.2 McNemar Odds Ratio

For binary accuracy comparisons, the odds ratio of discordant cells:

    OR = (A correct, B wrong) / (B correct, A wrong)

An OR > 1 indicates model A is more accurate; OR < 1 favors model B.

---

## 5. Power and Limitations

**Sample sizes:** n = 117 calibration items, n = 84 Family B items. With
5 models, there are 10 pairwise comparisons for calibration and 6 for
Family B (Gemini Flash excluded due to n = 1 in Family B).

**Power considerations:**
- McNemar's test: power depends on the number of discordant pairs, not total n.
  With 117 items, typical discordant counts range from 15-40 pairs, which
  provides adequate power for detecting accuracy differences of ~10 percentage
  points.
- Permutation tests at n = 117: sufficient to detect Brier score differences
  with Cohen's d ≥ 0.3 at 80% power.
- Per-mechanism subgroups (n = 2 to n = 20) are reported as **descriptive
  only** — formal hypothesis testing within mechanisms is underpowered.

**Sensitivity analysis:** All pairwise tests are run on both the full item set
and a clean subset excluding ~48 items flagged in the audit review queue. This
characterizes the robustness of findings to potential item quality concerns.

**Multiple comparisons:** With 10 pairwise comparisons × 2 tests per pair
(accuracy + Brier) = 20 tests, Holm-Bonferroni correction is applied. The
effective significance threshold for the most significant test is
α / 20 = 0.0025.

---

## 6. References

Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate:
A practical and powerful approach to multiple testing. *Journal of the Royal
Statistical Society: Series B*, 57(1), 289–300.

Bhapkar, V. P. (1966). A note on the equivalence of two test criteria for
hypotheses in categorical data. *Journal of the American Statistical
Association*, 61(313), 228–235.

Brier, G. W. (1950). Verification of forecasts expressed in terms of
probability. *Monthly Weather Review*, 78(1), 1–3.

Cochran, W. G. (1950). The comparison of percentages in matched samples.
*Biometrika*, 37(3/4), 256–266.

Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*
(2nd ed.). Lawrence Erlbaum Associates.

Dietterich, T. G. (1998). Approximate statistical tests for comparing
supervised classification learning algorithms. *Neural Computation*, 10(7),
1895–1923.

Efron, B. (1979). Bootstrap methods: Another look at the jackknife.
*The Annals of Statistics*, 7(1), 1–26.

Efron, B. (1987). Better bootstrap confidence intervals. *Journal of the
American Statistical Association*, 82(397), 171–185.

Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*.
Chapman & Hall/CRC.

Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules,
prediction, and estimation. *Journal of the American Statistical Association*,
102(477), 359–378.

Good, P. I. (2005). *Permutation, Parametric, and Bootstrap Tests of
Hypotheses* (3rd ed.). Springer.

Holm, S. (1979). A simple sequentially rejective multiple test procedure.
*Scandinavian Journal of Statistics*, 6(2), 65–70.

Kendall, M. G. (1938). A new measure of rank correlation. *Biometrika*,
30(1/2), 81–93.

Maxwell, A. E. (1970). Comparing the classification of subjects by two
independent judges. *British Journal of Psychiatry*, 116(535), 651–655.

McNemar, Q. (1947). Note on the sampling error of the difference between
correlated proportions or percentages. *Psychometrika*, 12(2), 153–157.

Naeini, M. P., Cooper, G., & Hauskrecht, M. (2015). Obtaining well-calibrated
probabilities using Bayesian binning. *Proceedings of the AAAI Conference on
Artificial Intelligence*, 29(1), 2901–2907.

Pesarin, F., & Salmaso, L. (2010). *Permutation Tests for Complex Data*.
Wiley.

Phipson, B., & Smyth, G. K. (2010). Permutation P-values should never be
zero. *Statistical Applications in Genetics and Molecular Biology*, 9(1).

Spearman, C. (1904). The proof and measurement of association between two
things. *American Journal of Psychology*, 15(1), 72–101.

Stuart, A. (1955). A test for homogeneity of the marginal distributions in a
two-way classification. *Biometrika*, 42(3/4), 412–416.

Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics
Bulletin*, 1(6), 80–83.
