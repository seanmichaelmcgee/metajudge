# Calibration v2 Refinement Charter
## Preserving signal while sharpening the monitoring benchmark

## Mission

Refine the calibration benchmark into a more scientifically explicit **monitoring** benchmark while preserving the strongest existing discriminatory signal and minimizing unnecessary scoring churn.

Calibration is not being replaced. It is being **clarified, tightened, and stratified**.

---

## Why calibration stays separate

Calibration is currently the cleanest mechanism in the repo for measuring whether a model can distinguish likely-correct from likely-incorrect outputs.

Under the new theoretical framing, calibration is the benchmark family that most directly measures:

- metacognitive monitoring
- confidence discrimination
- overconfidence / underconfidence
- item-family-specific monitoring failure

It should remain separate from Family B because mixing monitoring and control too early will weaken interpretability.

---

## What calibration should measure

Calibration should measure:

1. **Answer correctness**
2. **Confidence quality**
3. **Discrimination between correct and incorrect outcomes**
4. **Failure under misleading cues**
5. **Family-level variation in metacognitive monitoring**

Calibration should not become a disguised control-policy benchmark.

---

## What calibration should not measure

Calibration should not be used to silently score:

- whether the model asked a clarification question
- whether the model should have verified externally
- whether the model handled false presuppositions optimally under a multi-action policy
- whether the model selected the best behavior among several control options

Those belong to Family B or the bridge layer.

---

## Required internal split

Calibration must now be divided internally into three strata.

## Stratum A — Clean objective items
These are the anchor core and should be protected.

Definition:
- exact or tightly gradable answers
- stable answer key
- low alias ambiguity
- low temporal brittleness
- low controversy

Examples:
- exact arithmetic
- exact code execution
- strongly constrained symbolic or numerical outputs

Purpose:
- provide low-noise monitoring signal
- anchor confidence metrics
- preserve existing discriminatory power

Policy:
- retain aggressively unless evidence shows low value or hidden ambiguity

---

## Stratum B — Objective but brittle items
These are allowed, but must be explicitly tagged and more carefully governed.

Definition:
- answerable, but more vulnerable to:
  - temporal drift
  - alias ambiguity
  - wording sensitivity
  - historical controversy
  - acceptable alternate phrasings

Examples:
- conditional temporal facts
- some knowledge questions with naming disputes
- items requiring carefully managed aliases or date anchoring

Purpose:
- test monitoring under realistic factual brittleness
- support family-level analyses of confidence under instability

Policy:
- keep only if answer key is defendable and notes are explicit

---

## Stratum C — Metacognitively diagnostic traps
These are high-value if well designed.

Definition:
- items whose primary value is not factual difficulty but metacognitive stress:
  - misleading fluency
  - false familiarity
  - intuitive-but-wrong reasoning
  - deceptive premise structure
  - seemingly obvious but invalid shortcut cues

Examples:
- modified CRT-style items
- fluency traps
- plausible-but-false cue patterns

Purpose:
- reveal monitoring failures that do not reduce to raw knowledge

Policy:
- include selectively and only with strong grading robustness

---

## New calibration subset required

A **new calibration subset** should be added, not as a replacement family but as a targeted enhancement.

### Proposed name
`Calibration-MX` or `Calibration-v2-monitoring-traps`

### Purpose
Capture theory-aligned monitoring failure under deceptive cues while preserving answer-only format.

### Target constructs
- misleading fluency
- cue familiarity without reliable knowledge
- false familiarity
- plausible but invalid premise processing
- confidence after a lightweight self-check or reflect step
- hard-easy effect under controlled family design

### Format constraints
- still answer-only
- still confidence-bearing
- no explicit action selection
- must be gradable with high confidence
- every item must have a rationale for why it is metacognitively diagnostic

---

## Scoring philosophy

Calibration scoring should receive a **light-to-moderate rework**, not a rewrite.

### Preserve
- correctness logic that is already robust
- current notebook structure
- current audit export pathway
- family-level discrimination analyses that are already working

### Improve
- contradictory answer keys
- alias over-permissiveness or inconsistency
- metric naming clarity
- internal family tagging
- family-level and stratum-level reporting

### Add
- reporting by calibration stratum
- overconfidence concentration analysis by family
- monitoring-failure map by cue type
- optional check-pass delta for special subset items

---

## Minimal-safe scoring changes

The team should prefer the smallest changes that increase interpretability.

### Mandatory changes
1. Remove contradictory or self-undermining answer keys.
2. Enforce a canonical alias policy.
3. Distinguish raw Brier loss from transformed or inverted score labels.
4. Add metadata fields for:
   - stratum
   - cue type
   - temporal brittleness
   - controversy risk
   - grading risk

### Optional but recommended
1. Add family-conditioned calibration plots or tables.
2. Add failure-type clusters:
   - knowledge gap
   - reasoning trap
   - false familiarity
   - wording / alias issue
   - temporal brittleness
3. Add reflect-pass deltas for the new monitoring subset.

---

## Item acceptance rules

No calibration item should enter or remain in the production set unless it satisfies all of the following:

- answer key is defendable
- aliases are bounded and intentional
- prompt wording is stable
- grading rule is explicit
- item purpose is identifiable
- the item fits one of the three strata
- reviewers can explain why confidence on this item should be informative

---

## Frontier-model generation protocol

New calibration items should be created using frontier models via API, in multi-turn workflows.

### Required pipeline
1. Propose candidate item
2. Attack the item for ambiguity, answer-key conflict, shortcut leakage, and grading brittleness
3. Rewrite the item
4. Stress-test candidate responses and likely alternates
5. Draft answer key and alias set
6. Independent model critiques the key
7. Human/lead-agent acceptance decision
8. Add to rejection log if rejected

### Required adversarial prompts
The team must explicitly ask frontier models to:
- produce plausible wrong but fluent answers
- identify alternate valid phrasings
- detect controversy or naming disputes
- challenge whether confidence on the item would actually be diagnostic
- suggest minimal wording changes that preserve construct but improve grading reliability

---

## Deliverables

1. `calibration_v2_retention_matrix.md`
2. `calibration_v2_candidate_spec.md`
3. `calibration_v2_rejection_log.json`
4. `calibration_v2_scoring_delta.md`
5. `calibration_v2_notebook_integration_plan.md`

---

## Review questions agents must answer before merge

- Does this item really measure monitoring?
- Is this answer key defensible?
- Is this family already providing signal we risk damaging?
- Can this scoring change be made without destabilizing the notebook?
- Is this item better than the weakest preserved item it would replace?

---

## Final directive

Calibration v2 should be pursued as a **precision refinement program**, not as an expansion sprint.

Protect the anchor core, remove hidden landmines, and add a small, theory-aligned monitoring subset that materially improves scientific defensibility.
