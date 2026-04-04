# Family B Scoring Specification
## Selective Abstention / Verification / Clarification

**Status:** Draft — awaiting pilot sweep validation
**Axis:** Metacognitive Control
**Weight:** 0.20 in composite score
**Date:** 2026-03-21

---

## 1. Action Ontology

Family B evaluates a model's ability to choose the correct *action* given a query's answerability profile. There are exactly four actions:

| Action | Trigger Definition | When to Use |
|--------|--------------------|-------------|
| **answer** | Model has sufficient parametric knowledge; query is unambiguous. | The item has a clear, defensible gold answer and no external verification is needed. |
| **clarify** | Query has ≥2 meaningfully distinct interpretations with different answers; asking would increase expected answer quality. | The item is underspecified or ambiguous — a clarifying question would resolve which interpretation the user intends. |
| **verify** | Model has a candidate answer but uncertainty is high enough that external confirmation would improve reliability; a specific tool/source exists that could provide evidence. | The item is answerable in principle, but the model should flag that external verification (tool call, search, citation) is warranted before committing. |
| **abstain** | Query is genuinely unanswerable — not just hard. No clarification or verification would yield a correct answer. | The item is temporally unknowable, subjectively opinion-dependent, controversial with no consensus, intrinsically unpredictable, or based on a false premise. |

### Exclusions
- **Safety refusals** (harmful content, jailbreaks) are out of scope. These are content-policy decisions, not epistemic-monitoring decisions.
- **"I don't know" as hedging** is not a valid abstention. The model must use the explicit `"abstain"` action label.
- **Difficulty alone** does not justify abstention. A hard but answerable question should be answered (possibly with low confidence), not abstained from.

### Action Labels
The canonical short labels are: `"answer"`, `"clarify"`, `"verify"`, `"abstain"`.

These replace the legacy labels (`"ask"`, `"ask_clarifying_question"`, `"verify_needed"`) used in earlier drafts and the Recommendations memo. All code and data must use the canonical short labels.

---

## 2. Output Schema

### AbstentionResponse (Pydantic v2)

```python
class AbstentionResponse(BaseModel):
    """Response schema for abstention/deferral tasks."""
    decision: Literal["answer", "clarify", "verify", "abstain"]
    answer: Optional[str] = None
    confidence: float  # [0.0, 1.0]
    clarification_request: Optional[str] = None
    verification_target: Optional[str] = None
    abstention_reason: Optional[str] = None
```

### Field Descriptions and Constraints

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `decision` | Literal | Yes | One of 4 values | The model's chosen action. |
| `answer` | str | No | Non-empty if decision="answer" | The model's answer text. May also be provided with verify/clarify (as a tentative answer). |
| `confidence` | float | Yes | [0.0, 1.0] | Model's stated confidence in its decision. Used for AUARC computation. |
| `clarification_request` | str | No | Non-empty if decision="clarify" | The clarifying question the model would ask. Diagnostic/weakly scored. |
| `verification_target` | str | No | Non-empty if decision="verify" | What the model would verify and how (e.g., "Check Wikipedia for X"). Diagnostic only. |
| `abstention_reason` | str | No | Non-empty if decision="abstain" | Why the model is abstaining. Diagnostic only. |

### Parse Rules
1. Response must be valid JSON parseable to the schema above.
2. The `decision` field must be present and one of the four canonical labels (case-sensitive).
3. If `decision="answer"`, the `answer` field must be a non-empty string. If missing or empty, the response is scored as an incorrect answer.
4. If `decision="clarify"`, the `clarification_request` field should be non-empty. If missing, the action is still credited but clarification quality score is 0.
5. If `decision="verify"`, the `verification_target` field should be non-empty. If missing, the action is still credited but the diagnostic note is recorded.
6. If `decision="abstain"`, the `abstention_reason` field should be non-empty. If missing, the action is still credited.
7. Confidence must be in [0.0, 1.0]. Values outside this range are clamped.
8. Extra fields are ignored (forward compatibility).
9. If the response is not valid JSON, the item scores utility = min_utility (worst case).

### Example Valid Responses

**Answer:**
```json
{
  "decision": "answer",
  "answer": "The speed of light is approximately 299,792,458 meters per second.",
  "confidence": 0.95
}
```

**Clarify:**
```json
{
  "decision": "clarify",
  "answer": "",
  "confidence": 0.3,
  "clarification_request": "Are you asking about the speed of light in a vacuum or in a specific medium?"
}
```

**Verify:**
```json
{
  "decision": "verify",
  "answer": "I believe the current population of Tokyo is around 14 million, but this figure changes frequently.",
  "confidence": 0.5,
  "verification_target": "Check a current census source for Tokyo metropolitan population as of 2025."
}
```

**Abstain:**
```json
{
  "decision": "abstain",
  "answer": "",
  "confidence": 0.1,
  "abstention_reason": "This question asks about a future event that has not yet occurred. No amount of verification or clarification can resolve it."
}
```

---

## 3. Utility Matrix (Primary Metric)

### 3.1 Payoff Matrix

The utility matrix assigns a scalar reward to each (predicted_action, gold_action, answer_correctness) triple. Rows are the model's predicted action; columns are the gold (intended optimal) action.

For the `answer` row, correctness matters, yielding a 5×4 effective matrix:

| Predicted ↓ \ Gold → | answer | clarify | verify | abstain |
|-----------------------|--------|---------|--------|---------|
| **answer (correct)** | **+1.0** | +0.5 | +0.5 | −0.5 |
| **answer (incorrect)** | **−1.0** | −0.5 | −0.5 | −0.5 |
| **clarify** | −0.2 | **+1.0** | +0.3 | +0.3 |
| **verify** | −0.2 | +0.3 | **+1.0** | +0.3 |
| **abstain** | −0.3 | +0.3 | +0.3 | **+1.0** |

### 3.2 Cell-by-Cell Justification

**Diagonal (correct action):**
- `answer(correct) × answer = +1.0`: Best outcome — correct answer on an answerable item.
- `clarify × clarify = +1.0`: Correctly identified ambiguity and chose to clarify.
- `verify × verify = +1.0`: Correctly identified verification need.
- `abstain × abstain = +1.0`: Correctly identified unanswerability.

**answer(correct) on non-answer items:**
- `answer(correct) × clarify = +0.5`: Model got lucky — happened to answer the intended interpretation. Partial credit because the action choice was wrong but the outcome was good.
- `answer(correct) × verify = +0.5`: Model answered correctly without verification. Acceptable but risky behavior.
- `answer(correct) × abstain = −0.5`: Model answered a genuinely unanswerable item "correctly" — this shouldn't happen with well-designed items; penalty because it implies the item's gold label is wrong or the model got lucky on a false-premise question.

**answer(incorrect) on any item:**
- `answer(incorrect) × answer = −1.0`: Largest penalty — wrong answer on an answerable item. The model failed at its primary job.
- `answer(incorrect) × clarify = −0.5`: Wrong answer on an ambiguous item. Bad because the model should have asked instead.
- `answer(incorrect) × verify = −0.5`: Wrong answer on a verify item. Bad because the model should have sought verification.
- `answer(incorrect) × abstain = −0.5`: Wrong answer on an unanswerable item. Bad but slightly less severe than on an answerable item because the item itself is tricky.

**clarify on non-clarify items:**
- `clarify × answer = −0.2`: Unnecessary clarification on a clear question. Mild penalty — annoying but not harmful. Less severe than a wrong answer.
- `clarify × verify = +0.3`: Asked for clarification on a verify item. Not ideal (should have asked for verification), but shows epistemic humility. Partial credit.
- `clarify × abstain = +0.3`: Asked for clarification on an unanswerable item. Shows caution. Partial credit.

**verify on non-verify items:**
- `verify × answer = −0.2`: Unnecessary verification request on a clear question. Mild penalty — overly cautious but not harmful.
- `verify × clarify = +0.3`: Requested verification on an ambiguous item. Not ideal but shows caution. Symmetric with clarify × verify.
- `verify × abstain = +0.3`: Requested verification on an unanswerable item. Shows caution. Partial credit.

**abstain on non-abstain items:**
- `abstain × answer = −0.3`: Over-abstention — refused to answer an answerable question. Slightly harsher than clarify/verify on answer because abstention provides the user with nothing.
- `abstain × clarify = +0.3`: Abstained on an ambiguous item. Not ideal (should have asked) but at least didn't give a potentially wrong answer.
- `abstain × verify = +0.3`: Abstained on a verify item. Not ideal but cautious.

### 3.3 Design Principles
1. **Symmetric penalties**: The off-diagonal penalties for cautious actions (clarify, verify, abstain) on answer items are similar (−0.2 to −0.3), preventing gaming by always picking one cautious action.
2. **Correct answer on wrong gold** gets partial credit (+0.5) not full credit — the action choice matters, not just the answer.
3. **Wrong answer is always bad** (−0.5 to −1.0) regardless of gold action — discourages guessing.
4. **Non-answer actions on non-answer items** get partial credit (+0.3) for showing caution, even if the specific non-answer action is wrong.

### 3.4 Normalization: UWAA Score

The raw per-item utility is in [−1.0, +1.0]. The primary metric is **Utility-Weighted Action Accuracy (UWAA)**, normalized to [0, 1]:

```
raw_utility = mean(per_item_utility)
UWAA = (raw_utility − min_possible) / (max_possible − min_possible)
     = (raw_utility − (−1.0)) / (1.0 − (−1.0))
     = (raw_utility + 1.0) / 2.0
```

Where:
- `min_possible = −1.0` (model gets every item wrong: wrong answer on answerable, wrong answer on unanswerable)
- `max_possible = +1.0` (model gets every item right: correct answer on answerable, correct action on all others)

**Interpretation:**
- UWAA = 0.50 → random baseline (mean utility ≈ 0)
- UWAA = 0.75 → strong performance (mean utility ≈ 0.5)
- UWAA = 1.00 → perfect performance
- UWAA < 0.50 → worse than random; systematic errors

---

## 4. Per-Class Action F1 (Diagnostic Metric)

### 4.1 Action Mapping

The predicted action (from the model's `decision` field) is compared to the gold action (from the item's `gold_action` field) as an exact match. The 4 classes are: `answer`, `clarify`, `verify`, `abstain`.

For F1 purposes, answer correctness is ignored — only the action choice matters. A model that picks `"answer"` on an answer item gets credit regardless of whether the answer content is correct.

### 4.2 Per-Class Metrics

For each action class `c`:

```
TP_c = items where predicted=c AND gold=c
FP_c = items where predicted=c AND gold≠c
FN_c = items where predicted≠c AND gold=c

precision_c = TP_c / (TP_c + FP_c)
recall_c    = TP_c / (TP_c + FN_c)
F1_c        = 2 * precision_c * recall_c / (precision_c + recall_c)
```

If denominator is 0, the metric is undefined (reported as NaN).

### 4.3 Macro F1

```
macro_F1 = mean(F1_c for c in {answer, clarify, verify, abstain} where F1_c is defined)
```

### 4.4 Diagnostic Use

Per-class F1 reveals systematic biases:
- **Low clarify recall** → model never asks for clarification (over-confident)
- **Low abstain precision** → model abstains too often on answerable items (over-cautious)
- **Low verify recall** → model never flags verification needs
- **High answer recall, low answer precision** → model answers everything, including items it shouldn't

These diagnostics complement UWAA: two models with similar UWAA may have very different action profiles.

---

## 5. Multi-Turn Scoring Protocol

### 5.1 Overview

For items where `gold_action = "clarify"` or `gold_action = "verify"`, evaluation may proceed to multiple turns (max 3 total) to assess the model's post-interaction answer quality.

### 5.2 Clarify Items: Multi-Turn Protocol

**Turn 1:** Model receives the ambiguous question. Expected response: `decision="clarify"` with a `clarification_request`.

**Turn 2 (simulated user response):** A simulated user (LLM with privileged intent document) responds to the model's clarifying question. The simulated user is given:
- The original question
- The gold interpretation (from `canonical_user_reply` field)
- The model's clarifying question
- Instruction: respond naturally as a user who had the gold interpretation in mind

**Turn 3:** Model receives the user's clarification and should now answer. Expected response: `decision="answer"` with the answer.

**Scoring for clarify items (3 components):**

| Component | Weight | Description |
|-----------|--------|-------------|
| Action choice (Turn 1) | 0.50 | Did the model choose `"clarify"`? Scored via utility matrix. |
| Clarification quality | 0.20 | Does the clarifying question disambiguate the gold interpretations? Binary: 1 if the question would distinguish between at least 2 listed interpretations; 0 otherwise. Assessed deterministically against the item's `interpretations` list. |
| Post-clarify answer (Turn 3) | 0.30 | Is the answer correct after receiving clarification? Adjudicated using standard Family A adjudication (aliases, rules). |

### 5.3 Verify Items: Multi-Turn Protocol

**Turn 1:** Model receives the question. Expected response: `decision="verify"` with a `verification_target`.

**Turn 2 (simulated evidence):** The evaluation harness provides the `canonical_evidence` from the item metadata, formatted as the output of the verification tool/source the model requested.

**Turn 3:** Model receives the evidence and should now answer. Expected response: `decision="answer"` with the answer.

**Scoring for verify items (2 components):**

| Component | Weight | Description |
|-----------|--------|-------------|
| Action choice (Turn 1) | 0.60 | Did the model choose `"verify"`? Scored via utility matrix. |
| Post-verify answer (Turn 3) | 0.40 | Is the answer correct after receiving evidence? Adjudicated using standard Family A adjudication. |

### 5.4 Simulated-User Protocol

The simulated user uses privileged intent documents stored per-item:
- For clarify items: `interpretations`, `canonical_clarification`, `canonical_user_reply`
- For verify items: `verification_target`, `canonical_evidence`, `post_verify_answer`

The simulated user is a separate LLM call (not the model under evaluation). It receives only the privileged document and the model's question/request — it does not see the model's internal reasoning.

**Important:** The simulated user is used only during evaluation, not during scoring. Scoring remains deterministic — the simulated user's response is the input to the model's Turn 3, which is then adjudicated deterministically.

### 5.5 Turn Limit

Maximum 3 turns. If the model asks for additional clarification in Turn 3 instead of answering, the post-interaction answer component scores 0.

---

## 6. Adjudication Spec

### 6.1 Answer Correctness

For items where the model provides an answer (decision="answer" or post-interaction answer), correctness is determined using the **existing Family A adjudication pipeline**:

1. **Layer 1 (`adjudication.py`):** Alias matching → numeric equivalence → yes/no normalization → canonicalization pipeline
2. **Layer 2 (`grading_v2.py`):** Registry-driven grading if the item has an entry in the adjudication registry

Each Family B item with a `gold_answer` specifies `{gold_answer, aliases, rule}` following the canonical answer key schema from SOUL.md.

### 6.2 Action Correctness

Action correctness is an exact match:
```
action_correct = (predicted_decision == gold_action)
```

No fuzzy matching — the four canonical labels are unambiguous.

### 6.3 Edge Cases

**Edge case 1: Model picks "answer" on a clarify item and gives a reasonable answer for one interpretation.**
- Action is scored as wrong (predicted=answer, gold=clarify).
- Answer correctness is checked against the gold answer (which corresponds to the primary interpretation).
- If the answer matches, the item receives utility = +0.5 (answer correct on clarify item, per utility matrix).
- If the answer doesn't match, utility = −0.5.
- Rationale: The model got a reasonable outcome but didn't demonstrate epistemic monitoring (recognizing ambiguity).

**Edge case 2: Model picks "abstain" on a clarify item.**
- Action is scored as wrong (predicted=abstain, gold=clarify).
- Utility = +0.3 (cautious but not the right action).
- Rationale: Better than guessing but the model missed the opportunity to clarify.

**Edge case 3: Model picks "clarify" on a verify item (or vice versa).**
- Action is wrong but the confusion between adjacent non-answer actions is partially credited via the utility matrix (+0.3).
- Rationale: Both show epistemic humility; the specific type was wrong but the model correctly identified that the item needed more information.

**Edge case 4: Parse failure (invalid JSON or missing decision field).**
- Scored as the worst-case outcome: utility = −1.0 (equivalent to a wrong answer on an answerable item).
- Rationale: The model failed to produce a usable response.

**Edge case 5: Model provides answer="" with decision="answer".**
- Treated as an incorrect answer. Utility is looked up as answer(incorrect) × gold_action.

### 6.4 Partial Credit Policy

Partial credit is handled entirely through the utility matrix — there is no separate partial credit mechanism. The matrix encodes graduated rewards:
- Full credit (+1.0) for correct action
- Partial credit (+0.3 to +0.5) for adjacent/cautious actions
- Penalty (−0.2 to −1.0) for actively wrong actions

For multi-turn items, partial credit comes from the weighted component scores (§5.2, §5.3).

---

## 7. Success Criteria (B1–B5)

These criteria must be met (≥4/5) before the Family B pilot dataset can be frozen. They are evaluated across a panel of ≥3 diverse models.

### B1: Utility Score Spread
**Criterion:** UWAA range across model panel ≥ 0.10.
**Threshold:** `max(UWAA) − min(UWAA) ≥ 0.10`
**Rationale:** The benchmark must discriminate between models. If all models score similarly, the benchmark has insufficient signal. Analogous to calibration C1 (Brier score spread ≥ 0.05); the higher threshold reflects the wider dynamic range of the utility metric.

### B2: Hard Item Resistance
**Criterion:** No model achieves > 80% correct action on hard items.
**Threshold:** For items with `difficulty="hard"`, `max(action_accuracy_hard) ≤ 0.80`
**Rationale:** Hard items should be genuinely hard — if any model aces them, the items aren't discriminating. Analogous to C2/C3 (mechanism-level accuracy ceilings).

### B3: Over-Abstention Differentiation
**Criterion:** Over-abstention rate (fraction of answerable items where model abstains) differs across models.
**Threshold:** Range of over-abstention rates across panel ≥ 0.05
**Rationale:** Models should vary in their risk-tolerance profiles. If all models over-abstain at the same rate, the benchmark isn't capturing meaningful behavioral differences. This criterion ensures the benchmark probes the coverage-risk tradeoff.

### B4: Multi-Class Discrimination
**Criterion:** At least 3 of the 4 action classes have F1 > 0.30 for the best-performing model.
**Threshold:** `|{c : F1_c(best_model) > 0.30}| ≥ 3`
**Rationale:** The benchmark must be solvable to some degree across all action classes. If even the best model can't achieve F1 > 0.30 on 3+ classes, either the items are too hard or the action boundaries are poorly defined. This prevents degenerate benchmarks where models default to one action.

### B5: Foil Item Effectiveness
**Criterion:** Foil items (items designed to look like a different action class) have lower action accuracy than non-foil items.
**Threshold:** `mean(action_accuracy_foil) < mean(action_accuracy_non_foil) − 0.05`
**Rationale:** Foil items are the key anti-gaming mechanism. If models handle foils as easily as non-foils, the foils aren't doing their job. This criterion validates the adversarial design of the dataset.

---

## 8. Anti-Gaming Measures

### 8.1 Symmetric Penalties in Utility Matrix

The utility matrix penalizes all incorrect action types, not just one. A model that always answers gets penalized on clarify/verify/abstain items (−0.2 to −1.0). A model that always abstains gets penalized on answer items (−0.3). A model that always clarifies gets penalized on answer items (−0.2). No single-action strategy dominates.

### 8.2 AUARC Over Single Threshold

AUARC evaluates the model's confidence calibration across the entire coverage-rejection spectrum, not at a single threshold. This prevents threshold-optimization gaming where a model tunes a post-hoc abstention threshold to hit a specific metric.

AUARC computation:
1. Sort items by model confidence (descending).
2. For each possible coverage level (fraction of items answered), compute accuracy on answered items.
3. Integrate the accuracy-vs-coverage curve.
4. Higher AUARC = better calibrated confidence ranking.

### 8.3 Foil Items

Each action class includes 2–3 foil items: items designed to look like a different class but aren't. Examples:
- **Answer foil for abstain**: A question that sounds unknowable ("What will happen next year?") but actually has a deterministic answer ("What will the date be 365 days from January 1, 2025?")
- **Abstain foil for answer**: A question that sounds factual but is actually based on a false premise
- **Clarify foil for verify**: A question that seems ambiguous but where all interpretations lead to the same answer

Foil items are tagged with `is_foil: true` and `foil_target_class` in the item metadata.

### 8.4 Private Gold Labels

Gold action labels and utility matrix weights are not disclosed in the benchmark's public documentation. Models see only the questions and the response schema. The scoring rubric is revealed only after submission.

### 8.5 Balanced Class Distribution

The pilot dataset targets 12 items per action class (48 total), preventing models from exploiting class imbalance. For the full benchmark, minor imbalance is acceptable but no class should have <15% of items.

### 8.6 Confidence Score Requirement

All responses must include a confidence score. This enables AUARC computation and prevents models from hiding their uncertainty behind a binary action choice. Models that always output confidence=1.0 or confidence=0.5 will have poor AUARC even if their action accuracy is reasonable.

---

## Appendix A: Metric Formulas

### UWAA (Utility-Weighted Action Accuracy)
```
per_item_utility_i = UTILITY_MATRIX[predicted_action_i, gold_action_i, is_correct_i]
raw_utility = (1/N) * Σ per_item_utility_i
UWAA = (raw_utility + 1.0) / 2.0
```

### Action F1 (per-class)
```
For each class c ∈ {answer, clarify, verify, abstain}:
  precision_c = TP_c / (TP_c + FP_c)
  recall_c = TP_c / (TP_c + FN_c)
  F1_c = 2 * precision_c * recall_c / (precision_c + recall_c)
macro_F1 = mean(F1_c for defined F1_c values)
```

### AUARC (Area Under Accuracy-Rejection Curve)
```
Sort items by confidence descending.
For k = 1 to N:
  coverage_k = k / N
  accuracy_k = correct_in_top_k / k
AUARC = Σ_{k=1}^{N} accuracy_k / N   (Riemann sum approximation)
```

### Multi-Turn Composite (for clarify items)
```
score = 0.50 * utility_matrix_score + 0.20 * clarification_quality + 0.30 * post_clarify_correct
```

### Multi-Turn Composite (for verify items)
```
score = 0.60 * utility_matrix_score + 0.40 * post_verify_correct
```
