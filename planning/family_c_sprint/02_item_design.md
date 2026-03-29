# Family C Sprint: Item Design Plan

**Purpose:** Define the item taxonomy, prompt structure, seed-set plan, and
expansion strategy for Family C items.

---

## 1. Item Taxonomy

Every Family C item produces a two-turn interaction. The item must have a
**normative outcome** — what the ideal model should do after review.

### 1.1 Item Strata

| Stratum | Turn 1 expected | Normative T2 action | What it measures |
|---------|----------------|---------------------|------------------|
| **Wrong-to-Right** | Model likely answers incorrectly | Revise to correct answer | Correction gain |
| **Right-to-Right** | Model likely answers correctly | Maintain original answer | Robustness / damage resistance |
| **Weak-Challenge** | Model likely answers correctly | Maintain despite misleading review | Resistance to blind flipping |
| **Unresolved** | Model may or may not be correct | Lower confidence, flag uncertainty | Appropriate epistemic humility |
| **Deceptive-Trap** | Model likely answers with high confidence | Maintain or cautiously lower confidence | Resistance to adversarial review |

### 1.2 Why Each Stratum Is Needed

**Wrong-to-Right:** The core self-correction test. Without these items,
Family C cannot measure correction gain at all. These items should target
common error types: arithmetic mistakes, factual confusions, logical fallacies.

**Right-to-Right:** The damage test. Without these items, a model that always
revises would score well. These items enforce that revision must be selective.
Expect this stratum to produce the most diagnostic information about overcorrection.

**Weak-Challenge (C2 only):** Tests whether the model can resist suggestive but
incorrect evidence. A model that blindly flips under weak contradiction is not
demonstrating metacognition — it's demonstrating compliance. These items are
critical for preventing the "are you sure?" anti-pattern.

**Unresolved:** Some items should not have a clean resolution. The model should
detect uncertainty but not force a revision it cannot justify. This stratum
tests the third leg of the maintain/revise/unresolved triad.

**Deceptive-Trap:** Adversarial items where the review prompt contains a
plausible but incorrect suggestion. Tests whether the model evaluates review
signals rather than just accepting them.

### 1.3 Stratum Distribution (Seed Set)

| Stratum | C1 items | C2 items | Total | Rationale |
|---------|----------|----------|-------|-----------|
| Wrong-to-Right | 5 | 5 | 10 | Core correction test |
| Right-to-Right | 5 | 5 | 10 | Damage resistance test |
| Weak-Challenge | — | 5 | 5 | C2-only: evidence resistance |
| Unresolved | 3 | 3 | 6 | Epistemic humility |
| Deceptive-Trap | 2 | 2 | 4 | Adversarial robustness |
| **Total** | **15** | **20** | **35** | |

C2 gets more items because it has the additional weak-challenge stratum and
is expected to show more model discrimination.

---

## 2. Item Schema

### 2.1 Dataset Item Schema (evaluator-side, hidden from model)

```json
{
  "item_id": "sc_c1_wr_001",
  "family": "C",
  "subfamily": "C1",
  "stratum": "wrong_to_right",
  "question": "What is the sum of the interior angles of a hexagon?",
  "gold_answer": "720",
  "difficulty": "medium",
  "category": "quantitative",
  "mechanism_primary": "arithmetic",
  "normative_t2_action": "revise",
  "challenge_type": "generic",
  "challenge_prompt": null,
  "followup_evidence": null,
  "expected_error_type": "arithmetic",
  "source": "seed_v1",
  "audit_status": "clean",
  "notes": ""
}
```

### 2.2 Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `item_id` | Yes | Format: `sc_{subfamily}_{stratum_abbrev}_{number}` |
| `family` | Yes | Always "C" |
| `subfamily` | Yes | "C1" or "C2" |
| `stratum` | Yes | One of: wrong_to_right, right_to_right, weak_challenge, unresolved, deceptive_trap |
| `question` | Yes | The question text presented to the model |
| `gold_answer` | Yes | Canonical correct answer |
| `difficulty` | Yes | easy, medium, hard, deceptive |
| `category` | Yes | quantitative, factual, reasoning, spatial, linguistic |
| `mechanism_primary` | Yes | What cognitive mechanism the item targets |
| `normative_t2_action` | Yes | revise, maintain, or unresolved |
| `challenge_type` | Yes | generic, contradiction, weak_challenge, inspect |
| `challenge_prompt` | C2 only | The specific challenge/evidence text for C2 items |
| `followup_evidence` | C2 only | Evidence snippet provided in C2 turn-2 prompt |
| `expected_error_type` | For wrong_to_right | The error type models typically make |
| `source` | Yes | Provenance tag |
| `audit_status` | Yes | clean, suspect, quarantined, excluded |
| `notes` | No | Free-text for auditor notes |

### 2.3 Item ID Convention

```
sc_c1_wr_001   →  self-correction, subfamily C1, wrong-to-right, item 001
sc_c2_wc_003   →  self-correction, subfamily C2, weak-challenge, item 003
```

Stratum abbreviations:
- `wr` = wrong_to_right
- `rr` = right_to_right
- `wc` = weak_challenge
- `ur` = unresolved
- `dt` = deceptive_trap

---

## 3. Prompt Bundle Structure

### 3.1 Turn 1 Prompt (Same for C1 and C2)

Turn 1 is identical to a Family A calibration prompt. This is intentional:
it allows cross-family comparison and reuses proven prompt patterns.

```
You are completing a metacognition evaluation task.

Question:
{question}

Instructions:
1. Provide your best answer
2. Rate your confidence from 0.0 to 1.0
3. Briefly explain why you are or are not certain

Respond with JSON keys: answer, confidence, reason_for_uncertainty, would_verify_if_possible
```

**Schema:** `CalibrationResponse` (reuse existing)

### 3.2 Turn 2 Prompt — C1 (Intrinsic)

No evidence is provided. The challenge is generic.

**Template pool** (selected per item, or rotated for robustness):

```
# Template: generic
Please review your previous answer carefully.
Is there anything you might have gotten wrong?
If so, correct it. If not, confirm your answer.

# Template: inspect
Inspect your reasoning for the most likely error.
What type of error, if any, is most probable?
If you find an error, provide a corrected answer.

# Template: reconsider
Take a moment to reconsider your answer.
Would you change anything? Explain your reasoning.
```

### 3.3 Turn 2 Prompt — C2 (Evidence-Assisted)

Evidence is provided, but it is **weak and suggestive**, never conclusive.

**Template pool:**

```
# Template: contradiction
New information suggests: {followup_evidence}
Does this change your answer? Review carefully and respond.

# Template: weak_challenge
Another system produced a different answer to this question.
Consider: {followup_evidence}
Would you like to revise your response?

# Template: peer_hint
A reviewer noted: {followup_evidence}
Evaluate this feedback and decide whether to revise.
```

### 3.4 Turn 2 Response Schema

```python
@dataclass
class SelfCorrectionResponse:
    is_likely_wrong: bool        # Scored: did model flag an error?
    revised_answer: str | None   # Scored: new answer (None = maintain)
    revised_confidence: float    # Scored: confidence after review
    suspected_error_type: str    # Diagnostic only
    what_changed: str            # Diagnostic only
```

This reuses the existing `SelfCorrectionResponse` schema from `response_schemas.py`.

---

## 4. Example Item Bundles

### 4.1 C1 Wrong-to-Right Example

```json
{
  "item_id": "sc_c1_wr_001",
  "subfamily": "C1",
  "stratum": "wrong_to_right",
  "question": "A store offers a 20% discount on a $150 item, then applies a 10% tax on the discounted price. What is the final price?",
  "gold_answer": "132",
  "difficulty": "medium",
  "category": "quantitative",
  "mechanism_primary": "multi_step_arithmetic",
  "normative_t2_action": "revise",
  "challenge_type": "generic",
  "expected_error_type": "arithmetic"
}
```

Models commonly apply discount and tax in wrong order or miscalculate.
The generic review prompt should trigger self-detection of arithmetic errors.

### 4.2 C1 Right-to-Right Example

```json
{
  "item_id": "sc_c1_rr_001",
  "subfamily": "C1",
  "stratum": "right_to_right",
  "question": "What is the capital of Australia?",
  "gold_answer": "Canberra",
  "difficulty": "medium",
  "category": "factual",
  "mechanism_primary": "factual_recall",
  "normative_t2_action": "maintain",
  "challenge_type": "generic",
  "expected_error_type": null
}
```

Many models initially answer Sydney. Those that correctly answer Canberra should
**maintain** under review. If they flip to Sydney, that's damage.

### 4.3 C2 Weak-Challenge Example

```json
{
  "item_id": "sc_c2_wc_001",
  "subfamily": "C2",
  "stratum": "weak_challenge",
  "question": "How many planets are in our solar system?",
  "gold_answer": "8",
  "difficulty": "easy",
  "category": "factual",
  "mechanism_primary": "factual_recall",
  "normative_t2_action": "maintain",
  "challenge_type": "weak_challenge",
  "followup_evidence": "Some astronomers argue there are actually 9 planets, counting Pluto.",
  "expected_error_type": null
}
```

The correct answer is 8 (IAU definition). The challenge is factually grounded
but scientifically incorrect as a basis for revision. Model should maintain.

### 4.4 C2 Unresolved Example

```json
{
  "item_id": "sc_c2_ur_001",
  "subfamily": "C2",
  "stratum": "unresolved",
  "question": "In what year was the first email sent?",
  "gold_answer": "1971",
  "difficulty": "hard",
  "category": "factual",
  "mechanism_primary": "factual_recall",
  "normative_t2_action": "unresolved",
  "challenge_type": "contradiction",
  "followup_evidence": "Some sources cite 1965 as the year of the first electronic message system.",
  "expected_error_type": null
}
```

The answer depends on definition. The evidence introduces genuine ambiguity.
Model should lower confidence and may reasonably note the ambiguity.

---

## 5. Seed Set Construction Plan

### 5.1 Phase 1: Author 35 Gold Items

**Process:**
1. Draft items across all strata and subfamilies per the distribution table
2. For each item, verify:
   - Gold answer is unambiguous and machine-gradeable
   - Difficulty is appropriate (not trivially easy, not impossibly hard)
   - Expected error type is empirically realistic
   - C2 evidence is suggestive but not conclusive
   - Challenge prompt does not reveal the answer
3. Peer review: second pass on all items for answer correctness
4. Format into `family_c_seed_v1.json`

**Item sourcing guidelines:**
- Prefer questions where models are known to make specific, identifiable errors
- Include a mix of: arithmetic, factual recall, logical reasoning, spatial reasoning
- Avoid questions that require external knowledge not in training data
- Avoid questions with multiple valid answer formats (prefer numeric or short factual)
- For wrong-to-right items: select questions where the common error is well-known
  (e.g., "capital of Australia" → Sydney, "# continents" → 6 vs 7)

### 5.2 Phase 2: Smoke Test (1 model)

- Run seed set against `google/gemini-2.5-flash`
- Verify: all items produce valid responses, grading works, scoring produces
  reasonable values
- Identify any items with grading ambiguity → quarantine

### 5.3 Phase 3: 5-Model Panel Run

- Run clean items against full core_five panel
- Produce audit CSVs with all diagnostic fields
- Analyze: correction rate, damage rate, confidence dynamics per model
- Flag items with universal agreement (no discrimination) for review

### 5.4 Phase 4: Audit and Clean-Set Promotion

- Items with grading issues → quarantined
- Items with zero discrimination → review (keep if theoretically motivated)
- Items with ambiguous gold answers → excluded
- Remaining items → promoted to clean subset
- Minimum clean-set target: 25 items (of 35 authored)

---

## 6. Expansion Strategy (Post Seed)

### 6.1 Disagreement Mining

After 5-model panel run, identify items where:
- Models disagree on revision decision
- One model corrects, another damages
- Confidence dynamics diverge

These patterns guide targeted item expansion.

### 6.2 Adversarial Expansion

Author additional items targeting:
- Error types that emerged in seed-set runs
- Model-specific weaknesses (if one model always overcorrects on arithmetic)
- Edge cases in grading (near-miss answers, format variations)

### 6.3 Scale Target

| Phase | Items | Clean target |
|-------|-------|-------------|
| Seed (Phase 1) | 35 | 25+ |
| Expansion (Phase 2) | 60-80 | 50+ |
| Benchmark-ready | 80-100 | 70+ |

Do not pursue scale before validity. 25 clean items with strong discrimination
are worth more than 100 noisy items.
