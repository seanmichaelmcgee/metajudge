# Frontier Agent Team Operating Manual and Kickoff Prompt
## Long-running orchestrator guidance for benchmark refinement and high-quality item construction

## Purpose

This document is the operating brief for the VPS orchestrator and its agent teams.

The job is not merely to generate more questions. The job is to **refine the scientific benchmark architecture**, preserve proven signal, and use frontier models through API-based multi-turn engagements to produce benchmark items and scoring proposals of substantially higher quality than earlier bulk-generation approaches.

---

## Governing instruction

Before doing any work, the orchestrator must reground on:

- `SOUL.md`
- `docs/metacognition_assessor_recommendations.md`
- `planning/v1_architecture.md`
- current benchmark audit reports
- latest theory memo on metacognition, monitoring, control, selective reporting, and LLM abstention / verification

When these documents conflict:
- `SOUL.md` governs sequencing, constraints, and non-negotiables
- the recommendations memo governs cross-family family specs and scoring direction
- newer, more specific Family B design documents govern Family B implementation details
- active audit evidence governs defect priority

The orchestrator must record its interpretation of this hierarchy in its initial worklog.

---

## Core mission

Build the next scientifically defensible version of the MetaJudge benchmark by executing five coordinated tracks:

1. stabilize current measurement
2. refine calibration into a cleaner monitoring benchmark
3. redesign Family B into a defensible control benchmark
4. create the bridge layer linking monitoring to control
5. preserve Kaggle notebook operability and auditability throughout

---

## Team structure

The orchestrator should spawn specialized agent teams with explicit ownership.

### Team 1 — Repo and policy grounding
Responsibilities:
- inspect repo state
- read governing docs
- map current branches, notebooks, schemas, and scoring paths
- identify what must not be broken

Outputs:
- grounding memo
- repo-state memo
- non-negotiables memo

---

### Team 2 — Calibration v2
Responsibilities:
- preserve strong calibration core
- stratify current items
- propose retention/rewrite/remove decisions
- author small new monitoring subset
- propose minimal-safe scoring changes

Outputs:
- calibration retention matrix
- new calibration subset candidates
- calibration scoring delta memo

---

### Team 3 — Family B redesign
Responsibilities:
- audit current pilot ontology
- rewrite weak items
- separate true abstention from corrective non-answer behavior
- propose richer internal scoring
- produce high-quality new items

Outputs:
- Family B ontology memo
- false-premise policy memo
- item rewrite ledger
- candidate item pack

---

### Team 4 — Bridge analytics
Responsibilities:
- define monitoring-to-control reporting
- design bridge schema and derived metrics
- specify exemplar reports and artifact outputs

Outputs:
- bridge schema
- bridge metrics memo
- reporting prototypes

---

### Team 5 — Notebook and integration safety
Responsibilities:
- preserve notebook execution path
- review Cell 4 / grading parity status
- advise on lean-notebook readiness
- produce non-breaking integration steps

Outputs:
- integration risk memo
- lean migration decision memo
- explicit artifact checklist

---

### Team 6 — Frontier-model item construction and red-team review
Responsibilities:
- use frontier APIs to generate, attack, revise, and grade candidate items
- maintain rejection logs and rationale
- surface hidden ambiguity and grading fragility
- run adversarial multi-turn item refinement

Outputs:
- accepted candidate packs
- rejection logs
- adversarial review transcripts or summaries
- grading-risk notes

---

## Frontier-model policy

This phase explicitly permits the use of **frontier models via API** for benchmark construction.

### Why
Because these benchmark items are the linchpins of the project, quality matters more than cheap generation.

### Required standard
No serious candidate item should be accepted after a single one-shot prompt.

### Minimum multi-turn process
1. construct
2. critique
3. adversarial response generation
4. key and rubric drafting
5. counterexample challenge
6. rewrite
7. independent review
8. human/orchestrator acceptance decision

---

## Required frontier-model roles

The orchestrator should ensure these functional roles are played, whether by separate agents or rotating API calls:

- Constructor
- Skeptic
- Counterexample generator
- Rubric auditor
- Premise auditor
- Integration editor

Each accepted item should survive this gauntlet.

---

## Benchmark construction principles

### Principle 1 — Construct before quantity
Do not bulk-generate until the target construct is explicit.

### Principle 2 — Defensibility over cleverness
A flashy question with a brittle key is worse than a simpler question with strong measurement value.

### Principle 3 — Preserve existing signal
Do not replace strong current items without evidence.

### Principle 4 — Rejection logging is a feature
Keep records of why items were rejected. This improves quality and avoids reintroducing the same defects.

### Principle 5 — Use adversarial review
Assume the first version of any item is worse than it looks.

---

## Specific directives by workstream

## A. Measurement stabilization
- inspect current scoring and exports
- confirm which outputs are trustworthy
- identify minimal necessary fixes
- do not begin large item expansion until this memo is complete

## B. Calibration v2
- keep calibration separate
- stratify the benchmark
- preserve the anchor core
- add a theory-aligned monitoring subset
- minimize destructive scoring churn

## C. Family B
- redesign around epistemic control
- stop collapsing corrective premise rejection into generic abstention failure
- define acceptable alternative success paths
- use frontier-model debate for every nontrivial rewrite

## D. Bridge layer
- specify analytic outputs only after family schemas are stable enough
- avoid creating a giant new scorer if a reporting layer will do

## E. Notebook / Kaggle
- keep notebook thin
- preserve explicit outputs
- avoid breaking the current verified Kaggle workflow
- defer lean-notebook migration unless parity is proven

---

## Required artifacts and work discipline

Each team must produce:

- a branch-level worklog
- a decision log
- a rejection log where applicable
- explicit open questions
- a merge-risk summary
- references back to the governing docs that justify the team's decisions

The orchestrator must maintain a central oversight memo synthesizing:
- what was changed
- why it changed
- what evidence justified it
- what remains risky
- whether the work preserved project objectives

---

## Hard review gates

No merge-ready proposal should advance without clearing these questions:

1. Does this improve scientific defensibility?
2. Does this preserve or strengthen discriminatory power?
3. Is the answer/action key defendable?
4. Is the grading change minimal-safe where possible?
5. Does this preserve Kaggle notebook operability?
6. Is the item or scoring logic consistent with monitoring vs control framing?
7. Was the proposal stress-tested by frontier-model adversarial review?

---

## Kickoff prompt for the VPS orchestrator

Copy the following prompt into the VPS orchestration system.

---

# VPS / Orchestrator Kickoff Prompt

You are the lead orchestrator for the `metajudge` repository, a Kaggle Community Benchmarks project for the **Measuring Progress Toward AGI** competition on the **Metacognition** track.

Your job is to run a long-horizon, multi-agent benchmark-refinement program that improves the scientific defensibility of the project without destroying its existing working notebook and scoring infrastructure.

## First principles

This project is not a generic QA dataset project. It is a metacognitive benchmark project organized around two major constructs:

- **Monitoring**: whether a model knows when it is likely correct or incorrect
- **Control**: whether a model acts appropriately on that signal

Your benchmark work must therefore separate:

1. **Calibration / monitoring benchmark**
2. **Family B / control benchmark**
3. **Bridge reporting layer between monitoring and control**

Do not collapse these into a single undifferentiated score or family.

## Governing documents

Read and follow, in this order:

1. `SOUL.md`
2. `docs/metacognition_assessor_recommendations.md`
3. `planning/v1_architecture.md`
4. newer Family B design documents where they are more specific than older global language
5. the latest audit reports and issue ledgers
6. the latest theory memo connecting Hart, Nelson & Narens, Koriat & Goldsmith, meta-d', and recent LLM calibration / abstention literature

In your first oversight memo, state explicitly how you resolved any conflict between documents.

## Live repo assumptions to verify immediately

- `main` contains the active calibration benchmark path and Kaggle loop
- `fix/cell4-grading-v2` contains the near-term grading parity work and claimed 102/102 self-adjudication verification
- `feat/family-b-selective-abstention` contains the Family B pilot and notebook integration planning
- the current notebook and audit artifact pipeline are valuable and should be preserved

Verify these assumptions directly in the repo before planning deeper work.

## Program objectives

1. stabilize current measurement
2. preserve proven discriminatory signal
3. refine calibration into a cleaner monitoring benchmark
4. redesign Family B into a defensible control benchmark
5. build a bridge layer linking monitoring and control
6. preserve Kaggle notebook operability and auditability throughout
7. use frontier models via API in multi-turn adversarial construction to produce higher-quality items, answer keys, and scoring proposals

## Agent teams to spawn

Spawn at least the following teams:

- Repo/policy grounding team
- Calibration v2 team
- Family B redesign team
- Bridge analytics team
- Notebook/integration safety team
- Frontier-model item construction and red-team team

Require each team to maintain:
- worklog
- decisions
- rejection log where applicable
- open questions
- risk summary

## Mandatory operating rules

- Keep the notebook thin; scoring logic belongs in package code.
- Do not bulk-generate items before construct definitions and acceptance criteria are explicit.
- Do not replace strong existing items casually.
- Do not treat false-premise correction as automatic Family B failure.
- Do not migrate to the lean notebook unless parity and artifact preservation are demonstrated.
- Use frontier-model APIs for multi-turn item construction and adversarial critique; avoid one-shot cheap generation for important items.

## Required immediate outputs

Produce, in order:

1. a repo-grounding memo
2. a measurement-stability memo
3. a calibration-v2 retention/rewrite plan
4. a Family B ontology and false-premise policy memo
5. a minimal-safe scoring delta memo
6. a bridge-layer design memo
7. a notebook integration and artifact-preservation plan
8. a frontier-model generation protocol with rejection logging rules

## Construction quality bar

Every serious candidate item must go through:
- construction
- skeptical critique
- plausible wrong-answer generation
- answer-key and alias drafting
- counterexample testing
- rewrite
- independent rubric review
- accept / reject / revise decision

Prefer fewer, stronger items over many weak ones.

## Final outcome

The target outcome is a benchmark system that is more scientifically defensible, more clearly aligned to metacognition theory, more robust in grading, and still executable in Kaggle notebooks with explicit inputs and auditable outputs.

Begin by grounding yourself in the repo and producing the repo-grounding memo.
