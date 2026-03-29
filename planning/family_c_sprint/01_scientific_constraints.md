# Family C Sprint: Scientific Constraints Memo

**Purpose:** Non-negotiable design principles for Family C, grounded in the
repo's governing documents and metacognition literature.

---

## 1. Core Theoretical Frame

### 1.1 Nelson & Narens (1990): Monitoring → Control

Family C operationalizes the **monitoring-to-control link**:
- Turn 1 produces a monitoring signal (initial answer + confidence)
- Turn 2 tests whether that signal is used to regulate behavior (revise, maintain, or mark unresolved)

A model with good metacognitive control should:
- Revise when initial confidence was low AND the answer was wrong
- Maintain when initial confidence was high AND the answer was correct
- Lower confidence or mark unresolved when review reveals uncertainty but not a clear fix

A model with poor metacognitive control will:
- Flip answers indiscriminately under challenge
- Stubbornly persist on errors despite low initial confidence
- Increase confidence after review regardless of outcome

### 1.2 Huang et al. (ICLR 2024): The C1/C2 Separation Is Non-Negotiable

Huang et al. demonstrate that **apparent self-correction collapses** when oracle
feedback is removed. This means:

- **C1 (intrinsic):** The model gets NO new information. Any correction must come
  from the model's own re-examination. This is the hardest test and most likely
  to show near-zero performance for many models. That's fine — it's a floor.
- **C2 (evidence-assisted):** The model gets a WEAK signal (not the answer).
  This tests whether the model can integrate evidence without blind flipping.

Mixing C1 and C2 would **inflate scores** by crediting evidence-assisted corrections
as if they were intrinsic. This is the primary measurement trap the benchmark
must avoid.

### 1.3 Kadavath et al. (2022): Models Have Some Self-Knowledge

LLMs show some ability to track their own correctness. This justifies Family C
as a meaningful benchmark — we are not testing an impossible capability. But
the literature also shows this ability is:
- Prompt-sensitive (Xiong et al., ICLR 2024)
- Overconfident in aggregate
- Better at detecting uncertainty than at acting on it

Family C should expect **partial** self-correction, not perfect performance.

---

## 2. Non-Negotiable Design Principles

### Principle 1: Behavior Over Self-Report

**Source:** SOUL.md §1, Recommendations memo

Score only behavioral evidence:
- `revised_answer` (did the answer change? is it now correct?)
- `revised_confidence` (did confidence move appropriately?)
- `revise_decision` / `is_likely_wrong` (did the model flag an error?)

Never score narrative fields:
- `what_changed` — diagnostic only
- `suspected_error_type` — diagnostic only
- Any chain-of-thought or explanation

Models are unreliable narrators. A model that says "I found an arithmetic error"
but doesn't actually fix the answer has demonstrated nothing.

### Principle 2: The Maintain/Revise/Unresolved Triad

**Source:** Recommendations memo, v1_architecture.md

Three normative outcomes exist for every item:

| Outcome | When appropriate | Behavioral evidence |
|---------|-----------------|---------------------|
| **Maintain** | Original answer was correct | Answer unchanged, confidence stable or slightly up |
| **Revise** | Original answer was wrong, correction available | Answer changed to correct, confidence rises |
| **Unresolved** | Error detected but fix unclear | Answer may or may not change, confidence drops |

Reducing Family C to binary "changed / didn't change" would destroy the
benchmark's ability to measure nuanced metacognitive control.

### Principle 3: Damage Must Be Visible and Consequential

**Source:** Recommendations memo §4.C, scoring_plan.md

"Damage" = a previously correct answer is made incorrect during revision.

Design requirements:
- Damage must be **explicitly tracked** in audit outputs (`damage_flag`)
- Damage must be **penalized more than the gain from a successful correction**
  (asymmetric penalty prevents "always revise" gaming)
- Damage in C1 (no evidence) should be penalized **more harshly** than in C2
  (weak evidence), because C1 revision is purely self-generated
- Right-to-right robustness items must be included to measure damage rate

### Principle 4: Confidence Must Remain Integrated

**Source:** v1_architecture.md, benchmark_config.yaml

MetaJudge's identity is built on confidence. Family C must not drop it.

Required confidence dynamics:
- Turn 1: Initial confidence (same as Family A format)
- Turn 2: Revised confidence (must be elicited explicitly)

Scoring uses confidence appropriateness:
- Correct revision → confidence should rise
- Correct maintenance → confidence stable or slight rise
- Unresolved / uncertain → confidence should drop
- Damaging revision → confidence should drop (penalize if it doesn't)

### Principle 5: No Credit for Obedience to Criticism

**Source:** Recommendations memo, Framework §5.3.5

The benchmark must not degenerate into "did the model change its answer when
asked to reconsider?" This would measure **compliance**, not **metacognition**.

Safeguards:
- Include items where the correct action is to **maintain** the original answer
- Include items with **weak or misleading** challenges that should be resisted
- Score revision quality, not revision frequency
- Anti-gaming: vary challenge types (generic, contradiction, weak challenge, inspect)

### Principle 6: Clean-Set Discipline

**Source:** SOUL.md, emerging repo practice

New Family C items must follow:
1. **Audit first:** Every item gets a damage_flag, confidence_repair_score, review_type
2. **Quarantine suspects:** Items with ambiguous gold answers, inconsistent grading,
   or edge-case answer formats go to quarantine
3. **Promote only clean items:** Only audited, unambiguous items enter the reporting subset
4. **Track provenance:** Each item records its source, review status, and any exclusion reason

### Principle 7: Same-Budget Fairness

**Source:** Recommendations memo

C1 and C2 must be reported separately. Do not claim "self-correction capability"
based on C2 alone — C2 provides extra information that C1 does not.

Within C2, the evidence provided must be:
- **Weak, not conclusive** — hints and contradictions, not answers
- **Consistent across models** — same evidence for all models on same item
- **Not trivially revealing** — if the evidence is effectively "the answer is X",
  the test measures reading comprehension, not metacognition

---

## 3. What Family C Must NOT Be

| Anti-pattern | Why it fails | How to avoid |
|-------------|-------------|--------------|
| "Are you sure?" test | Measures compliance, not metacognition | Include maintain-correct items, penalize blind flipping |
| Second-chance reasoning | Gives credit for more compute, not self-monitoring | C1 uses generic prompt, not targeted hints |
| Oracle-assisted correction | Inflates scores (Huang et al.) | C2 evidence must be weak/suggestive only |
| Likert-rubric benchmark | Subjective, fragile, unreproducible | Score behavioral outcomes deterministically |
| Reasoning depth test | Already covered by other benchmarks | Focus on revision behavior, not reasoning quality |

---

## 4. Theoretical Predictions

Based on the literature and existing MetaJudge data:

1. **C1 scores will be low across all models** — intrinsic self-correction is
   empirically weak (Huang et al.). Expect mean scores of 0.3-0.5.
2. **C2 will show more spread** — evidence integration varies by model.
   Expect mean scores of 0.4-0.7 with meaningful variance.
3. **Damage rates will vary** — some models (especially instruction-tuned ones)
   may overcorrect at higher rates. This is a key discriminating signal.
4. **Confidence repair quality will correlate with Family A calibration** —
   models that calibrate well should also adjust confidence appropriately.
   But the correlation should not be perfect (Family C measures something new).
5. **Model ordering may differ from A/B** — a model that calibrates well may
   still overcorrect or stubbornly persist. This is the scientific value of
   opening the control axis.
