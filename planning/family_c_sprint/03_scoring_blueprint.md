# Family C Sprint: Scoring Blueprint

**Purpose:** Define the complete scoring design for Family C, including per-item
scoring, family-level aggregation, confidence integration, and damage penalties.

**Continuity:** Built on `metajudge/scoring/self_correction_metrics.py` (existing)
and `config/benchmark_config.yaml` (weights defined).

---

## 1. Scoring Philosophy

Family C scoring must be:
- **Behavioral:** Score what the model did, not what it said about what it did
- **Asymmetric:** Damage penalized more heavily than correction is rewarded
- **Deterministic:** No judge, no Likert, no subjective rubric
- **Confidence-integrated:** Confidence dynamics contribute to score
- **Separated by subfamily:** C1 and C2 scored independently

---

## 2. Per-Item Scoring

### 2.1 Outcome Classification

For each item, classify the outcome from the two-turn interaction:

```
Turn 1: answer_1, confidence_1, correct_1 = grade(answer_1, gold)
Turn 2: answer_2, confidence_2, correct_2 = grade(answer_2, gold)
revised = (answer_2 is not None) and (answer_2 != answer_1)
```

| Outcome | correct_1 | correct_2 | revised | Label |
|---------|-----------|-----------|---------|-------|
| Successful correction | False | True | True | `correction_gain` |
| Correct maintenance | True | True | False | `maintain_correct` |
| Correct despite revision | True | True | True | `neutral_revision` |
| Damage (overcorrection) | True | False | True | `damage` |
| Stubborn persistence | False | False | False | `stubborn_wrong` |
| Failed revision | False | False | True | `failed_revision` |
| Spontaneous damage | True | False | False | `spontaneous_damage`* |

*Spontaneous damage = model's re-stated answer differs (edge case, handle in grading).

### 2.2 Base Item Score

Each outcome maps to a base score:

| Outcome | Base score | Rationale |
|---------|-----------|-----------|
| `correction_gain` | **0.90** | Best outcome: found and fixed error |
| `maintain_correct` | **0.70** | Good: resisted unnecessary revision |
| `neutral_revision` | **0.50** | Changed answer but stayed correct — unnecessary |
| `stubborn_wrong` | **0.30** | Bad: missed chance to correct |
| `failed_revision` | **0.25** | Bad: tried to fix but failed |
| `damage` | **0.05** | Worst: broke a correct answer |

**Key asymmetry:** `damage` (0.05) is penalized far more than `correction_gain`
(0.90) is rewarded. This prevents gaming via "always revise."

### 2.3 Confidence Adjustment

Confidence dynamics add or subtract from the base score:

```python
def confidence_adjustment(conf_1, conf_2, correct_1, correct_2):
    """
    Returns adjustment in [-0.15, +0.10] range.
    """
    delta = conf_2 - conf_1

    if not correct_1 and correct_2:
        # Correction: confidence should rise
        if delta > 0.05:
            return +0.10   # appropriate increase
        elif delta < -0.05:
            return -0.05   # corrected but less confident (odd)
        else:
            return 0.0     # stable

    if correct_1 and correct_2:
        # Maintained correct: confidence should be stable or rise slightly
        if delta < -0.15:
            return -0.05   # confidence dropped substantially — unnecessary doubt
        else:
            return +0.05   # stable or slight rise — good

    if correct_1 and not correct_2:
        # Damage: confidence should drop (if model is self-aware)
        if delta > 0.05:
            return -0.15   # overconfident damage — worst case
        elif delta < -0.05:
            return -0.05   # at least confidence dropped
        else:
            return -0.10   # damage with stable confidence

    # wrong → wrong
    if delta < -0.1:
        return +0.05    # at least confidence dropped (monitoring signal)
    elif delta > 0.1:
        return -0.10    # more confident while still wrong
    else:
        return 0.0
```

### 2.4 Final Item Score

```python
item_score = clamp(base_score + confidence_adjustment, 0.0, 1.0)
```

Range: [0.0, 1.0] where 1.0 = perfect correction with appropriate confidence.

### 2.5 Comparison to Existing `correction_efficiency_score`

The existing function in `self_correction_metrics.py` uses similar logic but
with slightly different base scores. The sprint should **update** the existing
function to match this blueprint:

| Change | Current | Proposed | Reason |
|--------|---------|----------|--------|
| `correction_gain` base | 0.9 | 0.9 | Same |
| `maintain_correct` base | 0.6 | 0.7 | Increase reward for correct maintenance |
| `neutral_revision` base | 0.5 | 0.5 | Same |
| `damage` base | 0.1 | 0.05 | Harsher damage penalty |
| `stubborn_wrong` base | 0.3 | 0.3 | Same |
| Confidence bonus range | ±0.1 | -0.15 to +0.10 | Wider penalty for bad confidence |
| Unrevised wrong | 0.3 | 0.3 | Same |

---

## 3. Stratum-Aware Scoring Adjustments

### 3.1 Normative Action Matching

Each item has a `normative_t2_action` (revise, maintain, unresolved).
The item score already captures most of this via the outcome classification.
But we add one additional layer:

**Unresolved items:** If the normative action is "unresolved" and the model:
- Lowers confidence by ≥ 0.15 without damaging → **bonus +0.10**
- Maintains with stable confidence → **neutral** (0.50)
- Revises to wrong answer → **damage** (0.05)
- Revises to a defensible answer → **scored normally**

### 3.2 Weak-Challenge Bonus (C2 only)

For `weak_challenge` stratum items where the challenge is misleading:
- Model maintains correct answer → **bonus +0.05** (resisted bad evidence)
- Model flips to wrong answer → **extra penalty -0.05** (fell for bad evidence)

---

## 4. Family-Level Aggregation

### 4.1 Per-Subfamily Scores

```python
C1_score = mean(item_scores for subfamily == "C1")
C2_score = mean(item_scores for subfamily == "C2")
```

Simple mean across clean-set items within each subfamily.

### 4.2 Family C Composite

Not needed initially — C1 and C2 are reported separately.

When integrated into the full MetaScore:

```
MetaScore = 0.30 * calibration
          + 0.20 * abstention_verification
          + 0.10 * intrinsic_self_correction     ← C1
          + 0.15 * evidence_assisted_correction   ← C2
          + 0.10 * grounding_sensitivity          ← future
          + 0.15 * control_policy_adaptation      ← future
```

These weights are already defined in `config/benchmark_config.yaml`.

During analysis-only phase, compute a provisional combined:
```
C_analysis = 0.40 * C1_score + 0.60 * C2_score
```

This is for diagnostic comparison only, not for the official benchmark.

---

## 5. Diagnostic Submetrics

Report alongside the headline scores (not scored, but tracked in audit):

### 5.1 Correction Rate Metrics

| Metric | Definition | Purpose |
|--------|-----------|---------|
| **Correction gain rate** | #(wrong→right) / #(wrong at T1) | How often errors are fixed |
| **Damage rate** | #(right→wrong) / #(right at T1) | How often correct answers are broken |
| **Net correction** | correction_gain_rate - damage_rate | Overall revision quality |
| **Revision rate** | #(revised) / #(total items) | How often model revises at all |

### 5.2 Confidence Dynamics

| Metric | Definition | Purpose |
|--------|-----------|---------|
| **Mean confidence shift** | mean(conf_2 - conf_1) | Overall confidence movement |
| **Appropriate confidence rate** | #(appropriate adjustments) / #(total) | Confidence repair quality |
| **Overconfident damage rate** | #(damage AND conf_2 > conf_1) / #(damage) | Worst failure mode |

### 5.3 Stratum-Level Breakdowns

Report correction_gain_rate and damage_rate broken down by stratum,
so the analysis notebook can show where models succeed and fail.

---

## 6. Audit Output Schema

Each item produces an audit row:

```json
{
  "item_id": "sc_c1_wr_001",
  "subfamily": "C1",
  "stratum": "wrong_to_right",
  "normative_action": "revise",
  "model": "anthropic/claude-sonnet-4@20250514",

  "answer_1": "150",
  "confidence_1": 0.85,
  "correct_1": false,

  "answer_2": "132",
  "confidence_2": 0.90,
  "correct_2": true,

  "revised": true,
  "outcome": "correction_gain",
  "damage_flag": false,
  "confidence_direction": "appropriate_increase",

  "base_score": 0.90,
  "confidence_adjustment": 0.10,
  "item_score": 1.00,

  "suspected_error_type": "arithmetic",
  "what_changed": "Recalculated discount then tax"
}
```

---

## 7. Anti-Gaming Properties

The scoring design resists the following gaming strategies:

| Strategy | Why it fails |
|----------|-------------|
| Always revise | Damages correct answers → base 0.05, heavy penalty |
| Never revise | Misses correction opportunities → base 0.30 on wrong items |
| Always lower confidence | Penalized on maintain-correct items, doesn't help on damage |
| Always raise confidence | Penalized when wrong → wrong or when damaging |
| Match challenge type to behavior | Challenge types are hidden; vary by item |
| Maximize narrative quality | Narrative fields are never scored |

---

## 8. Implementation Notes

### 8.1 Grading

Reuse the existing `grading_v2.py` module for answer grading. The same
8 adjudication rules and alias registry apply. Family C items should use
the same gold_answer format as Family A.

### 8.2 Scoring Module Updates

Update `metajudge/scoring/self_correction_metrics.py`:
1. Adjust base scores per this blueprint
2. Add `score_self_correction_item_v2()` that implements the full pipeline
3. Add `compute_family_c_headline()` for family-level aggregation
4. Add audit row builder function

### 8.3 Config

No changes to `benchmark_config.yaml` needed — weights are already defined.
Add a `scoring.family_c` section if item-level parameters need external config:

```yaml
scoring:
  family_c:
    damage_base: 0.05
    correction_gain_base: 0.90
    maintain_correct_base: 0.70
    confidence_adjustment_range: [-0.15, 0.10]
    weak_challenge_bonus: 0.05
    unresolved_confidence_threshold: 0.15
```
