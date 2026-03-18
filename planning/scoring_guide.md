# Scoring Guide — MetaJudge-AGI V1 Calibration

**Date:** 2026-03-18  
**Scope:** Family A (Confidence Calibration) per-item and aggregate scoring  
**Governing docs:** `SOUL.md`, `planning/v1_architecture.md`  
**Status:** Pending implementation — `calibration_aware_score` requires replacement

---

## 1. The Scoring Problem

The `@kbench.task` function must return a single `float` per dataset item. This float populates the `result` column when `.evaluate()` runs across the dataset, and its mean becomes the benchmark's headline score on the Kaggle leaderboard.

The question: what should that float represent?

For a calibration benchmark, the per-item score must satisfy two properties:

1. **Higher scores for better-calibrated responses.** A model that is correct and appropriately confident should outscore one that is correct but uncertain, and both should outscore a model that is wrong and overconfident.
2. **Properness.** The scoring rule should be *strictly proper* — meaning the only strategy that maximizes expected score is reporting one's true probability of being correct. Without this property, the benchmark can be gamed or, worse, can fail to distinguish calibrated from uncalibrated models.

---

## 2. Current Implementation and Its Defect

### The function

```python
# metajudge/scoring/calibration_metrics.py (current)
def calibration_aware_score(is_correct: bool, confidence: float) -> float:
    if is_correct:
        return 0.5 + 0.5 * confidence   # Range: [0.5, 1.0]
    else:
        return 0.5 * (1.0 - confidence)  # Range: [0.0, 0.5]
```

### Why it fails

The expected score under this function is:

```
E[S(c)] = c × (p − 0.5) + 0.5
```

where `p` is the true probability of correctness and `c` is the stated confidence.

This is **linear in c**. The derivative `dE/dc = p − 0.5` is constant, which means:

- If `p > 0.5`: expected score is maximized at `c = 1.0`, not `c = p`
- If `p < 0.5`: expected score is maximized at `c = 0.0`, not `c = p`
- If `p = 0.5`: expected score is flat — any confidence is equally good

**This is not a proper scoring rule.** It incentivizes extreme confidence reporting, not honest probability estimation. A rational agent would always report 0 or 1.

### Practical impact

With a simulated 100-item dataset at 70% model accuracy:

| Model behavior | Our current score | 1 − Brier² |
|----------------|-------------------|-------------|
| Well-calibrated (~0.85 conf when right, ~0.35 when wrong) | 0.746 | **0.944** |
| Always reports 1.0 (maximally overconfident) | 0.700 | 0.700 |
| Always reports 0.95 (chronically overconfident) | 0.690 | 0.728 |
| Always reports 0.5 (hedging) | 0.600 | 0.750 |

The current function separates the well-calibrated model from the overconfident model by only **0.046 points**. Under 1 − Brier², that gap is **0.244 points** — over five times more discriminating.

Under the current function, the always-1.0 model (C) ranks above the hedging model (D). Under Brier, the hedger correctly ranks above the overconfident model — because at least the hedger isn't claiming false certainty on 30% of items.

---

## 3. Recommended Replacement: Per-Item Brier Score

### The function

```python
def calibration_aware_score(is_correct: bool, confidence: float) -> float:
    """Per-item calibration score based on the Brier scoring rule.

    Returns 1 - (confidence - outcome)^2, an affine transform of the
    Brier score that is higher-is-better and ranges [0, 1].

    This is a strictly proper scoring rule: the expected score is
    uniquely maximized when stated confidence equals true probability
    of correctness (Brier 1950; Gneiting & Raftery 2007).
    """
    y = 1.0 if is_correct else 0.0
    return 1.0 - (confidence - y) ** 2
```

### Properties

| Property | Value |
|----------|-------|
| Range | [0, 1] |
| Direction | Higher is better |
| Strictly proper | Yes — optimal strategy is `c = P(correct)` |
| Per-item computable | Yes — requires only `confidence` and `is_correct` |
| SDK compatible | Yes — returns `float`, matches `@kbench.task -> float` |

### Behavior across scenarios

| Scenario | Confidence | Correct? | Score |
|----------|------------|----------|-------|
| Correct + highly confident | 0.95 | Yes | 0.998 |
| Correct + moderately confident | 0.70 | Yes | 0.910 |
| Correct + uncertain | 0.30 | Yes | 0.510 |
| Wrong + appropriately uncertain | 0.20 | No | 0.960 |
| Wrong + moderately confident | 0.50 | No | 0.750 |
| Wrong + overconfident | 0.90 | No | 0.190 |
| Wrong + maximally overconfident | 1.00 | No | 0.000 |

The quadratic penalty means going from 0.5 to 0.9 confidence on a wrong answer drops the score by 0.56 points — far more punishing than the current linear function's 0.20-point drop.

### Why Brier and not something else

| Alternative | Why not |
|-------------|---------|
| Raw Brier score | Lower-is-better; awkward for SDK convention where higher `result` = better |
| Log score (cross-entropy) | Undefined at `c = 0` or `c = 1`; requires clipping; harsher than necessary |
| ECE | Aggregate metric — cannot be computed per-item |
| AUROC | Aggregate metric — requires the full run to compute |
| Spherical score | Less interpretable; no practical advantage over Brier for binary outcomes |

1 − Brier² is the simplest strictly proper scoring rule that is higher-is-better and bounded in [0, 1]. It is the most widely used calibration metric in the literature (Brier 1950; Guo et al. 2017; Naeini et al. 2015). It can be cited without explanation.

### Mathematical justification for properness

Let `p` = true probability of correctness, `c` = stated confidence:

```
E[S(c)] = p × [1 - (c-1)²] + (1-p) × [1 - c²]
        = p × (2c - c²) + (1-p) × (1 - c²)
        = 2pc - pc² + 1 - c² - p + pc²
        = 1 - p + 2pc - c²

dE/dc = 2p - 2c = 0  ⟹  c* = p
d²E/dc² = -2 < 0  (concave, so c* = p is a maximum)
```

The unique optimum is `c = p`: report your true probability. This is strict properness.

---

## 4. Aggregate Diagnostics

The per-item score (§3) goes into the `result` column and produces the headline benchmark number. The following aggregate metrics are computed after the run for diagnostic purposes — they are reported in the writeup and analysis but do not feed into the Kaggle leaderboard score.

### 4.1 Brier Score (aggregate)

```python
def brier_score(confidences, correctness) -> float:
    # Already implemented in calibration_metrics.py
    return mean((c - y)² for c, y in zip(confidences, correctness))
```

- Range: [0, 1], lower is better
- Relationship to per-item score: `mean(per_item_scores) = 1 - brier_score`
- Standard reference metric; enables direct comparison with published results

### 4.2 Expected Calibration Error (ECE)

```python
def expected_calibration_error(confidences, correctness, n_bins=10) -> float:
    # Already implemented in calibration_metrics.py
```

- Bins predictions by confidence, measures weighted average |accuracy − confidence| per bin
- Captures *systematic* miscalibration that Brier may miss (see Misconception #3 in Kumar et al. 2019)
- Important complement: a model can have a decent Brier score but poor ECE if it's overconfident in some bins and underconfident in others

### 4.3 Overconfidence Rate

```python
def overconfidence_rate(confidences, correctness, threshold=0.8) -> float:
    # Already implemented in calibration_metrics.py
```

- Fraction of wrong answers where confidence exceeded the threshold
- Direct behavioral measure: "how often does this model confidently assert wrong answers?"
- The single most important diagnostic for the metacognition track — high overconfidence rate is the failure mode judges will care about

### 4.4 Accuracy-by-Confidence Bucket

```python
def accuracy_by_confidence_bucket(confidences, correctness, n_bins=10):
    # Already implemented in calibration_metrics.py
```

- Returns (mean_confidence, mean_accuracy, count) per bucket
- The raw data for reliability diagrams (calibration curves)
- Enables visual inspection: a well-calibrated model produces a diagonal line

### 4.5 AUROC (not yet implemented)

```
from sklearn.metrics import roc_auc_score
auroc = roc_auc_score(correctness, confidences)
```

- Measures whether confidence scores discriminate correct from incorrect answers
- A model that assigns higher confidence to correct answers than incorrect ones gets high AUROC regardless of absolute calibration
- Captures *discrimination* — complementary to ECE which captures *calibration*
- Listed in v1_architecture.md as a V1 deliverable; implementation is one line

---

## 5. Anti-Gaming Analysis

### 5.1 Constant-confidence strategies

A key concern for any calibration benchmark: can a model game the score by adopting a constant confidence regardless of the question?

At 70% accuracy with `1 − (c − y)²`:

| Constant confidence | Expected score |
|--------------------|---------------|
| c = 0.0 | 0.300 |
| c = 0.3 | 0.630 |
| c = 0.5 | 0.750 |
| c = 0.7 | **0.790** |
| c = 0.9 | 0.750 |
| c = 1.0 | 0.700 |

The optimal constant-confidence strategy is `c = 0.7` — which equals the model's actual accuracy. This is correct behavior for a proper scoring rule: the best you can do without per-item information is report your base rate. Score: 0.790.

A well-calibrated model (varying confidence per item) scores **0.944** — a 0.154-point gap over the best constant strategy. This gap is the benchmark's discriminating power, and it's large enough to be meaningful.

### 5.2 Overconfidence strategy

A model that always says `c = 0.95` at 70% accuracy scores 0.728 — worse than the constant-0.7 strategy (0.790) and far worse than honest calibration (0.944). Overconfidence is not rewarded.

### 5.3 Underconfidence strategy

A model that always says `c = 0.3` at 70% accuracy scores 0.630 — also substantially worse. The quadratic penalty works symmetrically: being too uncertain about correct answers also costs points.

### 5.4 Remaining concern: difficulty-dependent gaming

A model that reports `c = 1.0` on easy items (which it knows it'll get right) and `c = 0.5` on hard items (hedging) partially mimics calibration. This is actually desirable behavior — it means the model is doing coarse-grained uncertainty tracking. The benchmark should reward this, and 1 − Brier² does: such a model scores higher than a constant-confidence model but lower than one with fine-grained per-item calibration.

---

## 6. What Changes in the Codebase

### Must change

| File | Change |
|------|--------|
| `metajudge/scoring/calibration_metrics.py` | Replace body of `calibration_aware_score()` |

Three lines. The function signature and all call sites remain identical.

### No change needed

| File | Why |
|------|-----|
| `metajudge/tasks/calibration.py` | Calls `calibration_aware_score()` — signature unchanged |
| `metajudge/scoring/composite_score.py` | Operates on family-level scores — unaffected |
| `tests/unit/test_scoring.py` | Test expectations will need updating for new score values |
| All aggregate diagnostic functions | Remain as-is; they compute different metrics |

### Should add

| Item | Description |
|------|-------------|
| AUROC computation | One-line `sklearn` call in diagnostics or a thin wrapper |
| `tests/unit/test_scoring.py` updates | Adjust expected values for the new per-item function |

---

## 7. Impact on Dataset Design

The per-item scoring function influences dataset authoring in one important way:

**Difficulty distribution matters more under Brier.** Because Brier penalizes overconfidence quadratically, deceptive items (where models are confidently wrong) produce dramatically low scores. A dataset with too many deceptive items would depress all models' scores uniformly, reducing discriminatory power. The planned distribution (20% easy, 35% medium, 25% hard, 15% deceptive, 5% adversarial) should provide a healthy spread.

The dataset team should be aware of this: the per-item score now ranges more widely (a wrong-and-confident answer can score 0.000 vs. the old floor of ~0.025), which means individual items have more leverage on the aggregate. Outlier items should be reviewed for whether their gold answers are unambiguous.

---

## 8. What Judges Will See

Per the [Kaggle competition rubric](https://www.kaggle.com/competitions/kaggle-measuring-agi/overview), dataset quality and task construction are weighted at 50%. Scoring is part of task construction. Our writeup should include:

1. **Per-item metric:** 1 − Brier², citing Brier (1950) and Gneiting & Raftery (2007) on strictly proper scoring rules
2. **Why proper scoring matters:** A benchmark that can be gamed by trivial strategies has no discriminatory power — and discriminatory power is 15% of the judging rubric
3. **Diagnostic suite:** ECE, overconfidence rate, AUROC, reliability diagrams — showing we don't just produce a number, we produce an interpretable calibration profile
4. **Anti-gaming analysis:** Demonstrate that constant-confidence strategies score substantially below honest calibration

---

## References

- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3.
- Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *ICML 2017*.
- Naeini, M. P., Cooper, G., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using Bayesian binning into quantiles. *AAAI 2015*.
- Xiong, M., et al. (2024). Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. *ICLR 2024*.
- Kumar, A., Liang, P. S., & Ma, T. (2019). Verified uncertainty calibration. *NeurIPS 2019*.
