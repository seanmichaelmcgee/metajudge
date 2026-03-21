# Bridge Layer and Minimal-Safe Scoring / Notebook Plan
## Linking monitoring to control without breaking the Kaggle workflow

## Mission

Add a third reporting layer that reveals the relationship between calibration and Family B, while making the smallest scoring and notebook changes necessary to improve scientific defensibility.

This document exists to prevent two bad outcomes:

1. overcomplicated scoring rewrites that destabilize the repo
2. scientifically weak reporting that collapses distinct constructs into one number

---

## Why the bridge layer exists

A benchmark that measures only calibration cannot show whether monitoring affects behavior.

A benchmark that measures only Family B actions cannot show whether the model's action policy is coupled to internal uncertainty in a meaningful way.

The bridge layer exists to answer:

- when monitoring says risk is high, does the model behave more cautiously?
- when monitoring says risk is low, does the model answer directly and correctly?
- where do monitoring and control diverge?
- which families expose a monitoring-control gap?

This is where the scientific framing becomes strongest.

---

## Required outputs of the bridge layer

The bridge layer must produce reports that are understandable to both internal developers and external reviewers.

### Minimum required outputs
1. model-level monitoring vs control summary
2. family-level coupling summary
3. failure-mode clusters
4. calibration-confidence to Family B action mapping
5. overconfidence-to-bad-control exemplars
6. cautious-but-inefficient exemplars

### Recommended outputs
1. monitoring-good / control-bad quadrant table
2. monitoring-bad / over-answering quadrant table
3. action utility by confidence band
4. item-family heatmap
5. exemplar casebook

---

## Scoring strategy: minimal-safe change

### Core principle
Do not rewrite working scoring logic unless the current logic is invalid or incapable of representing the construct.

### Implication
- Calibration gets a light-to-moderate scoring update.
- Family B gets the larger redesign.
- The bridge layer should mostly consume outputs from those two families, not force both families into a totally new shared scorer.

---

## Scoring decomposition required

### Calibration side
Need:
- correctness
- confidence
- family / stratum tag
- cue type
- failure type

### Family B side
Need:
- task answer correctness
- action correctness
- premise handling quality
- utility
- acceptable-alternative path classification

### Bridge side
Need derived features such as:
- confidence band
- risk group
- action aggressiveness
- control appropriateness
- monitoring-control alignment flag

---

## Minimal schema delta approach

To avoid breaking the current notebook and package stack, prefer **additive schema changes** rather than destructive refactors.

### Add fields instead of renaming unless necessary
Recommended:
- add new columns / keys
- preserve old columns until compatibility window closes
- introduce translation helpers inside package code
- keep notebook wrappers simple

### Package-first implementation
All new scoring logic should live in package or scoring modules, not the notebook.

The notebook should:
- load embedded or explicit benchmark data
- call scoring utilities
- emit auditable outputs
- remain readable and execution-stable on Kaggle

---

## Lean notebook decision rule

The repo already contains work toward a leaner notebook flow. Do not migrate merely because a lean version exists.

### Lean migration should happen only when:
- Cell 4 grading parity is proven
- package/notebook boundary is stable
- answer-key integration is verified
- audit export remains intact
- Family B additions do not force fragile notebook logic

### Lean migration should be deferred if:
- notebook parity is uncertain
- the new bridge layer is still moving rapidly
- Family B scoring is still changing weekly
- migration would duplicate debugging burden

---

## Notebook integration philosophy

### Preserve
- the current multi-cell development flow
- explicit input packages or embedded benchmark state
- explicit output artifacts
- audit CSV export
- model discovery and evaluation loop already verified on Kaggle

### Add carefully
- new calibration metadata
- Family B richer output fields
- bridge reporting cells or bridge export stage
- diagnostics that help decide freeze / replace / rewrite

### Avoid
- notebook-only business logic
- hidden state
- destructive restructuring while the science is still moving

---

## Proposed reporting structure

### Report A — Calibration monitoring report
Questions answered:
- How well does the model know when it is right or wrong?
- Which item strata are hardest?
- Where is overconfidence concentrated?

### Report B — Family B control report
Questions answered:
- Does the model choose the right epistemic action?
- Does it correct false premises?
- Does it over-answer or over-abstain?

### Report C — Bridge report
Questions answered:
- Does calibration predict control?
- Which models show a monitoring-control gap?
- Which item families best reveal dissociation?

These can all be produced from one notebook run if the schema is structured correctly.

---

## Failure modes to explicitly guard against

1. **Metric collapse**
   - one aggregate score hides which construct failed

2. **Ontology overfitting**
   - model is punished for a good corrective answer because it did not match the hand-authored action label

3. **Notebook fragility**
   - scoring improvements break the Kaggle execution path

4. **Schema churn**
   - repeated renaming or reformatting makes audits incomparable

5. **Pseudo-precision**
   - more scores are added without real construct clarity

---

## Recommended implementation sequence

### Step 1
Lock the preserved notebook path and current outputs

### Step 2
Add calibration metadata and reporting without changing its basic evaluation loop

### Step 3
Refactor Family B exports so they can carry richer scoring decomposition

### Step 4
Add bridge derivations as a reporting layer, not as a new core benchmark family

### Step 5
Only after stable outputs exist, consider lean-notebook migration

---

## Deliverables

1. `bridge_layer_schema.md`
2. `bridge_metrics_and_views.md`
3. `minimal_safe_scoring_delta.md`
4. `lean_notebook_decision_memo.md`
5. `notebook_integration_non_breaking_plan.md`
6. `artifact_export_checklist.md`

---

## Review questions before merge

- Does this change improve scientific defensibility?
- Does it preserve or improve notebook operability?
- Is the scoring change additive where possible?
- Would an external reviewer understand the distinction between monitoring and control after reading the outputs?
- Are we preserving current discriminatory signal?

---

## Final directive

Treat the bridge layer as an **analytic overlay**, not a reason to destabilize the working repo.

The scoring job is to reveal constructs more clearly with the least destructive engineering change possible.
