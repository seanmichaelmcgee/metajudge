# Family B Redesign Charter
## Selective clarification, verification, abstention, and corrective non-answer behavior

## Mission

Redesign Family B so that it becomes a defensible **control benchmark** rather than a brittle pilot of gold-action matching.

Family B should test whether models act appropriately on uncertainty, ambiguity, missing information, and false premises.

The key transition is this:

> Family B must move from simplistic action matching toward principled epistemic control evaluation.

---

## Family B's scientific role

Family B is the benchmark family most directly responsible for testing:

- selective clarification
- selective verification
- strategic abstention
- premise correction when a direct answer would validate a false assumption
- behavioral consequences of monitoring quality

This makes Family B the main control benchmark and the best bridge from monitoring into action.

---

## Core problem to fix

Earlier audits and the new theoretical framing imply that Family B is vulnerable to four major failure modes:

1. **Export / correctness instability**
2. **Ontology errors**
3. **False-premise mis-scoring**
4. **Action over-rigidity**

If these are not fixed, Family B remains a pilot artifact rather than a scientific benchmark.

---

## The ontology question

The current public action space is useful but incomplete.

Existing public classes:
- `answer`
- `clarify`
- `verify`
- `abstain`

These can remain the public Kaggle-facing ontology for simplicity.

However, internal scoring must now acknowledge that the space of **successful metacognitive behavior** is richer than those four labels.

### Internal success paths that must be handled
- direct correct answer
- clarify before answering
- verify before answering
- abstain
- **corrective answer / corrective non-answer**:
  - rejecting a false premise
  - answering with “none,” “not applicable,” or “the premise is false”
  - refusing to accept the task framing when the framing is the problem

This does not necessarily require a fifth public label, but it does require more nuanced scoring.

---

## Policy decision required

### Recommended approach
Keep four public actions, but add **internal acceptable-alternative response logic**.

This means each item should specify:

- intended gold action
- acceptable alternative success paths
- harmful response patterns
- rationale for each

This avoids overfitting the benchmark to a rigid ontology when the construct is epistemic quality, not taxonomic obedience.

---

## Item categories Family B must support

## Category 1 — Clarification-required items
Definition:
- the prompt is underspecified or ambiguous enough that a reliable answer cannot yet be produced

Success behavior:
- asks a targeted clarification question
- does not hallucinate a fully specific answer

Failure behavior:
- guesses a specific answer prematurely
- asks irrelevant or performative clarification

Acceptance rule:
- ambiguity must be real, not cosmetic

---

## Category 2 — Verification-required items
Definition:
- the prompt is answerable in principle, but reliable answering requires checking a source, current state, or external computation

Success behavior:
- signals need for verification
- identifies what to verify
- does not present an unverified answer as settled fact

Failure behavior:
- answers confidently without basis
- performs fake verification language without identifying verifiable target

Acceptance rule:
- verification need must be genuine and explainable

---

## Category 3 — True abstention items
Definition:
- the question lacks a justified answer path even with ordinary clarification or verification, or it asks for unsupported speculation beyond epistemic warrant

Success behavior:
- abstains or explicitly states insufficient basis

Failure behavior:
- invents answer
- masks ignorance as style

Acceptance rule:
- abstention must be the genuinely appropriate policy, not just a convenience label

---

## Category 4 — Corrective non-answer items
Definition:
- the prompt contains a false presupposition or impossible set-up, and the best behavior is to reject or correct the premise

Success behavior:
- explicitly corrects the premise
- gives “none,” “not applicable,” or equivalent where appropriate
- avoids validating the false frame

Failure behavior:
- treats the false premise as valid and answers within it
- abstains vaguely without premise correction when correction is available and informative

Acceptance rule:
- must be distinguished from true abstention

This category is especially important and should no longer be hidden inside the abstain bucket.

---

## Item audit protocol

Every Family B item must now pass the following audit:

1. What exactly makes this a control item rather than a calibration item?
2. Is the intended action genuinely necessary?
3. Could a high-quality corrective answer be better than abstention?
4. Is the item evaluating epistemic quality or merely stylistic compliance?
5. Is the answer/action key defensible to an external reviewer?
6. Can the item be explained in monitoring-control language?
7. Is failure on this item informative about metacognition rather than just task knowledge?

If the answer to any of these is weak, the item should be rewritten or rejected.

---

## Scoring redesign

Family B scoring needs a deeper rework than calibration.

### Minimum decomposition required

Every scored row should separate at least:

1. **Task answer correctness**
2. **Action correctness**
3. **Premise handling quality**
4. **Control utility**
5. **Alternative-success classification**

### Recommended schema additions
- `intended_action`
- `acceptable_actions`
- `acceptable_alternative_resolution`
- `premise_type`
- `requires_clarification`
- `requires_verification`
- `is_false_presupposition`
- `harmful_response_patterns`
- `utility_rationale`

---

## Corrective-answer policy

This is the most important conceptual change.

For false-premise items, the benchmark must stop treating all non-abstain behavior as failure.

Examples of acceptable corrective resolution may include:
- “There are no such integers.”
- “That did not happen.”
- “The premise is false.”
- “This cannot be answered as stated because the assumption is incorrect.”

This behavior should often count as a success path, not a miss.

---

## Frontier-model generation protocol

Family B item generation must use frontier models via API in **multi-turn adversarial construction**, not single-pass prompting.

### Required workflow
1. Generate candidate item
2. Ask a second frontier model to argue why the item is weak, ambiguous, or misclassified
3. Ask another model to propose the strongest possible incorrect but plausible model response
4. Stress-test whether the gold action still seems right
5. Rewrite item and ontology notes
6. Generate draft acceptable alternatives
7. Generate harmful-response examples
8. Re-run critique
9. Only then decide accept / reject / revise

### Required conversation roles
- Constructor
- Skeptical reviewer
- Grader/rubric reviewer
- Counterexample generator
- Epistemic-policy reviewer
- Integrator

These may be separate agents or role-switched frontier calls.

---

## What high-quality Family B items look like

A high-quality Family B item has:

- a clearly justified control demand
- a stable rationale for the intended behavior
- an explicit explanation of why direct answering would be epistemically bad
- a bounded set of acceptable alternative responses
- a clear harmful-response pattern
- a plausible real-world analogue
- grading that can survive variation in wording

---

## Deliverables

1. `family_b_ontology_revision.md`
2. `family_b_false_premise_policy.md`
3. `family_b_item_rewrite_ledger.csv`
4. `family_b_scoring_redesign.md`
5. `family_b_frontier_generation_protocol.md`
6. `family_b_acceptance_checklist.md`

---

## Review questions before merge

- Is this a genuine control task?
- Is the intended action truly necessary?
- Would a corrective answer be better than abstention?
- Can the item be robustly scored without overfitting to wording?
- Does this item advance the two-axis project objective?

---

## Final directive

Family B should be rebuilt as a **behaviorally defensible epistemic-control benchmark**.

Do not optimize for action-label neatness. Optimize for whether the benchmark truly detects when a model acts wisely or unwisely under uncertainty.
