# MetaJudge Next-Phase Program Charter
## Scientific refinement, benchmark defensibility, and agent-team execution

## Purpose

This document is the governing execution charter for the next phase of **MetaJudge-AGI**. It translates the current repository state, the latest benchmark audits, the theory memo on metacognition, and the Kaggle competition objective into an actionable program for long-running agent teams.

The central aim of this phase is:

1. **Drastically improve scientific defensibility**
2. **Preserve as much proven discriminatory signal as possible**
3. **Repair measurement before scaling**
4. **Use frontier-model, multi-turn item construction to raise benchmark quality**
5. **Keep the Kaggle notebook workflow operational and auditable throughout**

This phase is not a reset. It is a **refinement and stabilization phase**.

---

## External grounding

The Kaggle competition is explicitly asking participants to build **high-quality benchmarks that go beyond recall and evaluate how frontier models reason, act, and judge**. The associated Google DeepMind framing positions this as a cognitive-evaluation problem rather than a generic QA exercise.

This project should therefore optimize for:

- defensible task construction
- verifiable answer keys
- prompt/input/output robustness
- interpretable scoring
- benchmark families that correspond to meaningful cognitive constructs
- notebook and artifact workflows that survive Kaggle execution constraints

---

## Internal governing hierarchy

Agents must reground repeatedly to the following internal hierarchy before making architectural changes:

1. `SOUL.md` — governing principles, constraints, non-negotiables
2. `docs/metacognition_assessor_recommendations.md` — cross-family family specs and scoring architecture
3. `planning/v1_architecture.md` — current implementation plan, especially calibration family implementation
4. branch-local Family B design documents — authoritative for Family B specifics when newer and more precise than older cross-family language
5. current audit reports and issue ledgers — authoritative for active defects and measurement failures

### Current controlling decisions

At the time of this charter, the following decisions are controlling:

- `SOUL.md` has primacy for project order and non-negotiables.
- `SOUL.md` says **Family B is the next implementation target after calibration freeze**.
- `SOUL.md` requires a **thin notebook**: scoring logic in package code, SDK glue in the notebook.
- The current repo state shows a mature calibration core on `main`, a Cell 4 grading-parity hotfix branch, and a larger Family B pilot branch that should be treated as a pilot, not as measurement-final.

---

## Snapshot of live repo state that this plan assumes

This plan assumes the following repo conditions are real and must be respected:

- `main` contains the active V4.1 calibration path and Kaggle development loop.
- `fix/cell4-grading-v2` contains the immediate grading-parity and item-quality repair work, including claimed `102/102` gold self-adjudication verification.
- `feat/family-b-selective-abstention` contains a 48-item pilot plus notebook-integration planning, but remains pilot-grade rather than production-frozen.
- The notebook workflow and audit CSV export path already exist and are valuable assets that should be preserved.

The job now is to **improve the science without blowing up the working scaffold**.

---

## Scientific reframing

The theory memo sharpens the project around a distinction that should now govern the benchmark architecture:

- **Monitoring**: does the model know when it is likely correct or incorrect?
- **Control**: does the model act appropriately on that signal?

This means the benchmark should not collapse everything into one score or one family.

### Required three-layer architecture

#### Layer 1 — Calibration / Monitoring benchmark
Purpose: measure metacognitive monitoring quality

Primary question:
- Can the model discriminate likely-correct from likely-incorrect answers?

#### Layer 2 — Family B / Control benchmark
Purpose: measure selective clarification, verification, abstention, and related control behavior

Primary question:
- Given uncertainty, ambiguity, missing information, or false premises, does the model choose the right epistemic action?

#### Layer 3 — Bridge analysis layer
Purpose: measure coupling between monitoring and control

Primary question:
- When monitoring says risk is high, does control improve?
- When monitoring says risk is low, does direct answering remain appropriate?
- Where do monitoring and control come apart?

This three-layer design is the cleanest scientific story available.

---

## Program objectives

## Objective 1 — Stabilize measurement before expansion

The project should not bulk-expand item count while measurement remains unreliable.

Success means:

- calibration scoring is trustworthy enough for iterative use
- Family B exports are analytically trustworthy
- false-premise and corrective-answer cases are no longer mischaracterized by simplistic gold-action logic
- audit artifacts can support external review

---

## Objective 2 — Preserve proven discriminatory signal

Do not throw away the current benchmark core casually.

The team must identify:

- which calibration families are already separating models
- which current items are clean enough to preserve
- which scoring rules are already robust and should not be rewritten without cause

The operating principle is:

> preserve existing signal unless a defect clearly invalidates it

---

## Objective 3 — Refine calibration into a cleaner monitoring benchmark

Calibration should remain separate and should become more explicit in its scientific role.

It should measure:

- correctness
- confidence quality
- discrimination between correct and incorrect responses
- behavior under misleading fluency or deceptive familiarity

It should **not** silently absorb policy questions that really belong to Family B.

---

## Objective 4 — Redesign Family B into a defensible control benchmark

Family B must move from pilot-style action matching to a more principled evaluation of epistemic control.

It should measure:

- whether the model answers when it should answer
- whether it clarifies when ambiguity blocks a reliable answer
- whether it verifies when external checking or source confirmation is needed
- whether it abstains when reliable answering is not justified
- whether it appropriately corrects false presuppositions

---

## Objective 5 — Add the bridge layer

The bridge layer must become the explanatory layer tying the benchmark together.

It should reveal:

- monitoring-good / control-bad models
- monitoring-bad / over-answering models
- families where calibration strongly predicts control quality
- families where monitoring signals fail to transfer to behavior

---

## Objective 6 — Use frontier models for benchmark construction, not just evaluation

The project should now explicitly permit costly frontier-model usage for benchmark authoring and audit.

This is justified because:

- these benchmark items are the linchpins of the entire project
- weak item construction will damage the benchmark more than modest API cost
- multi-turn adversarial refinement is more likely to expose hidden ambiguity, key conflicts, brittle grading, and poor epistemic policy framing than one-shot generation

The construction pipeline should use frontier models via API in iterative debates, counterexample generation, rubric stress-testing, and red-team review.

---

## Non-negotiables for all agent teams

1. Read `SOUL.md` first and quote the controlling constraints in the branch worklog.
2. Keep the notebook thin.
3. Prefer package-level scoring changes over notebook-embedded logic changes.
4. Preserve explicit input and output artifacts.
5. Preserve or improve audit CSV exportability.
6. Do not merge calibration and Family B into a single undifferentiated score.
7. Do not perform bulk generation before the target construct is defined.
8. Do not accept benchmark items that lack a defensible answer key or action policy.
9. Use tests before notebook integration.
10. For item generation, use frontier-model, multi-turn review rather than cheap bulk prompting.

---

## Workstreams

## Workstream A — Measurement stabilization

Mission:
- establish a trustworthy baseline before expansion

Includes:
- Cell 4 grading parity
- self-adjudication sanity tests
- audit export verification
- defect triage into parse bugs, key conflicts, policy failures, and construct failures

Deliverables:
- measurement-stability memo
- grading-risk memo
- preserved-core item list

---

## Workstream B — Calibration v2 refinement

Mission:
- sharpen calibration into a monitoring benchmark without breaking what already works

Includes:
- internal item stratification
- contradictory answer-key cleanup
- alias policy cleanup
- small new calibration subset
- family-level reporting

Deliverables:
- calibration retention / rewrite table
- calibration-v2 item spec
- calibration-v2 candidate pool
- minimal scoring delta proposal

---

## Workstream C — Family B redesign

Mission:
- convert Family B from pilot action matching into a defensible control benchmark

Includes:
- false-premise audit
- clarify / verify / abstain policy tightening
- corrective-answer handling
- internal acceptable-alternative response policy
- item rewrites and removals

Deliverables:
- Family B ontology memo
- Family B item rewrite ledger
- Family B scoring redesign memo
- frontier-generated candidate items with rationale and rejection logs

---

## Workstream D — Bridge layer

Mission:
- quantify monitoring-to-control coupling

Includes:
- calibration-to-action linkage analyses
- family-level coupling plots/tables
- error-family typology
- composite reporting without collapsing constructs

Deliverables:
- bridge schema
- bridge metrics memo
- bridge notebook cell plan
- example outputs on current models

---

## Workstream E — Notebook preservation and Kaggle deployment

Mission:
- keep the working Kaggle loop alive while science improves

Includes:
- explicit package/notebook boundary
- lean-notebook readiness review
- artifact export path preservation
- input/output reproducibility checks

Deliverables:
- lean-readiness decision memo
- notebook migration checklist
- non-breaking integration plan
- Kaggle artifact checklist

---

## Phase sequence

### Phase 0 — Reground and branch discipline
- re-read governing docs
- record current repo state
- define branch ownership and review gates

### Phase 1 — Measurement stabilization
- fix grading parity issues
- confirm preserved core
- stop any uncontrolled benchmark growth

### Phase 2 — Calibration v2 refinement
- preserve strong core
- add theory-aligned subset
- keep scoring changes minimal and explicit

### Phase 3 — Family B redesign
- resolve ontology and policy defects
- rewrite or remove weak items
- repair exports and action-quality analysis

### Phase 4 — Bridge layer
- connect calibration and Family B analytically
- generate interpretable cross-family reports

### Phase 5 — Frontier-model expansion
- only after measurement and ontology are stable
- conduct expensive multi-turn item generation and adversarial refinement

---

## What success looks like

The next phase is successful if all of the following are true:

- the benchmark architecture is more scientifically defensible than before
- calibration remains strong and more interpretable
- Family B becomes analytically trustworthy
- bridge reporting reveals meaningful monitoring-control dissociations
- the Kaggle notebook still runs cleanly with explicit input/output artifacts
- scoring improvements do not cause destructive code churn
- new item generation is visibly higher quality than earlier bulk generation

---

## Final operating principle

This project should now be run as a **measurement-first benchmark-construction program**, not as a generic question-authoring sprint.

The benchmark is only as good as the clarity of its construct, the defensibility of its keys, the reliability of its scoring, and the discipline of its notebook execution path.
