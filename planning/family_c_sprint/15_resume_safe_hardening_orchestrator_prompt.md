# Family C Hardening Sprint — Resume-Safe Orchestrator Prompt (v0.6.2)

## Purpose

This document is the **resume-safe** orchestrator prompt for the next Family C hardening sprint.

It exists because the prior VPS run produced real progress but lost additional work due to long-running execution, insufficient commit frequency, and overly large execution chunks between durable checkpoints.

This prompt is for a **brand new VPS / brand new orchestrator / brand new agent team** that must:

1. re-contextualize itself with the **MetaJudge repo**,
2. re-contextualize itself with the **Kaggle Measuring AGI benchmark-design competition**,
3. recover and preserve the real lessons learned from the prior hardening run,
4. execute the remaining hardening work in **small resumable phases**, and
5. **micro-commit constantly** so that partial progress is never lost again.

This is not a free-form exploration prompt.
This is a **durable execution prompt**.

---

## Primary operating principle

**Do work in small restartable chunks, commit immediately, write a checkpoint note, and stop at explicit gates for continuation.**

If you do not follow that rule, you are failing the assignment.

---

## What this sprint is trying to accomplish

The immediate goal is to harden **Family C** so that it becomes suitable for:

- internal narrative-notebook 5-model sweeps,
- later benchmark-notebook integration,
- eventual contribution to a single leaderboard-facing composite score,
- and broader public interpretation inside the Kaggle competition framework.

The current problem is that the Family C pilot was too easy and too high-scoring to produce enough model separation.

This sprint exists to:

- harden wrong-to-right items,
- audit and stabilize grading,
- calibrate C2 evidence snippets,
- expand the item set in the right strata,
- preserve clean versus quarantined item states,
- and leave behind a clean resumable repo state after every meaningful step.

---

## Competition context you must internalize first

This project is being built for the Kaggle / DeepMind **Measuring Progress Toward AGI — Cognitive Abilities** benchmark-design competition.

That means:

- this is **not** a standard train-and-submit prediction competition,
- the project is a **benchmark design and evaluation** project,
- interpretability and scientific grounding matter,
- tasks must be reproducible and explainable,
- the final benchmark surface must stay clean enough for Kaggle Benchmarks mechanics,
- and the repo should continue to support both:
  - a **thin official benchmark notebook**, and
  - a **richer public narrative notebook** with multi-model analysis.

Family C is part of the broader metacognition axis, specifically the **control / regulation** side of the benchmark.

Do not lose sight of the fact that Family C exists to improve **metacognitive discernibility** across models, not to create a clever local prompt trick.

---

## Repo context you must internalize first

Before doing anything else, read the current repo materials in this order:

1. `README.md`
2. `planning/family_c_sprint/13_pilot_orchestrator_instructions.md`
3. `planning/family_c_sprint/14_hardening_orchestrator_prompt.md`
4. `docs/metacognition_assessor_recommendations.md`
5. `docs/metacognition_literature_report.md`
6. `data/family_c/SCHEMA.md`
7. `config/family_c_scoring.yaml`
8. `metajudge/tasks/self_correction_v2.py`
9. `metajudge/scoring/self_correction_v2.py`
10. `scripts/openrouter/client.py`
11. current Family C candidate JSON files
12. current `outputs/family_c/` hardening artifacts from the previous run

You are expected to work from the real repo state, not your memory.

---

## Security instruction — critical

A prior run log captured an OpenRouter API key in plaintext.
Treat that key as compromised.

Rules:

- never echo keys,
- never print keys,
- never write keys into repo files,
- never commit keys,
- never paste them into markdown,
- read keys from environment only,
- stop immediately and report the required env var if it is missing.

The required variable is:

- `OPENROUTER_API_KEY`

If you need to validate it, do a minimal smoke test only.

---

## What the previous VPS run already accomplished

The prior hardening run was **not** a failure. It produced real progress.
That progress must be preserved and used as the starting point.

At minimum, the log shows the following happened before timeout:

### Phase A / setup work completed

- hardening branch setup was initiated,
- environment verification was performed,
- a smoke test across 5 models was run,
- quarantine manifest was locked,
- `sc_c2_dt_001` was promoted to clean,
- hardening prompt `14_hardening_orchestrator_prompt.md` was copied into the repo,
- Phase A was committed.

### Grading audit work completed

- a grading robustness audit found issues,
- aliases and normalization-related fixes were applied,
- `self_correction_v2.py` JSON parsing was made more robust to preamble text / fenced output,
- grading audit artifacts were written.

### Evidence calibration work completed

- existing C2 snippets were analyzed,
- three flagged items underwent evidence recalibration,
- recalibration artifacts were written.

### Generation lessons were learned

- generation of wrong-to-right items was the main bottleneck,
- generic classic trap questions were too easy,
- examples like bat-and-ball / snail-in-the-well style items were not useful,
- the canary validation logic correctly rejected too-easy items,
- a second-generation script direction (`hardening_generate_v2.py`) began emerging.

### Process failure was identified

- background processes were too long-running and fragile,
- sandbox/VPS resets killed in-flight work,
- commits were too sparse,
- too much value existed only in logs and temp files rather than committed repo state,
- large combined execution steps were too risky.

This prompt hardcodes protections against repeating those failures.

---

## Hard lessons from the prior run

### Lesson 1 — micro-commit or lose work

This is the most important lesson.

The orchestrator must micro-commit after every meaningful checkpoint.
Not “commit often” in a vague sense.
**Micro-commit concretely and repeatedly.**

### Lesson 2 — background jobs are dangerous unless restartable

Long-running generation processes can disappear.
No important work should exist only in a background job or temp log.

### Lesson 3 — wrong-to-right generation needs a harder generation strategy

Question authoring must explicitly avoid famous benchmark/trick problems that frontier models already know.

### Lesson 4 — grading and parsing robustness matter almost as much as question quality

The audit work was valuable and must be retained as first-class hardening work, not treated as cleanup.

### Lesson 5 — phased stopping points are mandatory

The orchestrator must pause at pre-defined human checkpoints even if more work could theoretically continue.

---

## Hard rule: micro-commit policy

You must **micro-commit throughout the sprint**.

A micro-commit is required whenever **any** of the following happens:

1. a new script is created,
2. a script is materially edited,
3. a candidate JSON is updated,
4. a quarantine manifest changes,
5. a recalibration artifact is written,
6. a validation artifact is written,
7. a report section is completed,
8. a phase is completed,
9. 15–20 minutes of meaningful work has passed,
10. a restart would otherwise lose non-trivial work.

### Commit message style

Use short explicit commit messages like:

- `Hardening v0.6.2: checkpoint Phase 0 bootstrap and state recovery`
- `Hardening v0.6.2: checkpoint grading audit fixes batch 1`
- `Hardening v0.6.2: checkpoint evidence recalibration batch 1`
- `Hardening v0.6.2: checkpoint C1 WR generation accepted items batch 1`
- `Hardening v0.6.2: checkpoint C2 WR generation accepted items batch 1`
- `Hardening v0.6.2: checkpoint full canary validation artifacts`
- `Hardening v0.6.2: checkpoint final triage and report draft`

### Checkpoint note rule

After every micro-commit, write or update:

- `planning/family_c_sprint/checkpoint_status_v062.md`

That file must include:

- current branch,
- latest commit hash,
- phase completed,
- files changed,
- artifacts produced,
- exact next step,
- blockers if any,
- whether it is safe to resume from here.

This file is mandatory.

---

## Human continuation gates — mandatory

The orchestrator must stop and request continuation at the following gates:

### Gate 1 — after Phase 0 bootstrap/state recovery
Stop and present:
- what prior work is already in repo,
- what is still missing,
- the exact plan for active hardening.

### Gate 2 — after wrong-to-right generation batch 1
Stop and present:
- candidate items accepted,
- candidate items quarantined,
- why the new generation strategy is or is not working.

### Gate 3 — after full canary validation and triage draft
Stop and present:
- current clean counts,
- current WR clean counts,
- whether targets look reachable,
- any grading or snippet failures that remain.

### Gate 4 — before final benchmark-facing recommendations
Stop and present:
- what is benchmark-ready,
- what still belongs only in the narrative notebook,
- what remains deferred.

Do not bulldoze through these gates.

---

## Goal state for this sprint

Target the following end state:

- **18 C1 items** total,
- **25 C2 items** total,
- **43 Family C items** total,
- **at least 35 clean items** after triage,
- **at least 8 clean wrong-to-right items total**, with:
  - at least **4 clean C1 WR**,
  - at least **4 clean C2 WR**,
- all grading rules validated against actual model output formats,
- evidence snippets calibrated for meaningful revision pressure,
- all work represented by committed repo artifacts,
- and a final hardening report plus checkpoint file that would let a fresh VPS resume immediately.

---

## Work philosophy for this sprint

The orchestrator should use **small parallel agent teams**, but must keep the work phaseable and resumable.

That means:

- parallelize where useful,
- but never so much that the state becomes too diffuse to checkpoint,
- prefer small batches of candidate items,
- prefer deterministic artifacts over ephemeral logs,
- and prefer stop-and-resume safety over raw speed.

This sprint is allowed to be long-running and compute-expensive, but it must remain **restart-safe**.

---

## Recommended agent structure

Use 5 core agents maximum, with optional short-lived micro-agents for narrow tasks.

### Agent A — State Recovery + Repo Context Agent
Responsibilities:
- verify current branch and recent commits,
- inventory prior hardening artifacts,
- confirm what work from the earlier run is already committed,
- update `checkpoint_status_v062.md` after bootstrap.

### Agent B — Wrong-to-Right Question Authoring Agent
Responsibilities:
- generate harder C1 and C2 WR candidates,
- avoid famous benchmark/trick problems,
- work in small batches,
- immediately write candidate outputs to repo artifacts.

### Agent C — Difficulty Canary / Validator Agent
Responsibilities:
- test candidate WR items against cheap canaries first,
- reject too-easy items quickly,
- escalate only viable items,
- write validation artifacts continuously.

### Agent D — Grading + Evidence Calibration Agent
Responsibilities:
- continue grading robustness work,
- audit actual output formats,
- recalibrate C2 snippets where needed,
- preserve clean scoring semantics.

### Agent E — Triage + Report + Commit Agent
Responsibilities:
- merge accepted items,
- update clean/quarantine states,
- maintain checkpoint file,
- write hardening report,
- enforce micro-commit policy,
- stop at human gates.

Optional micro-agents are allowed only for:
- individual high-value item bundles,
- narrow snippet recalibration,
- one-off grading edge cases,
- or small-scale candidate cleanup.

Do not create research-only memo agents.

---

## Model routing policy

Use multiple models through OpenRouter, but route them intelligently for cost.

### General principle

Use cheaper models for:
- screening,
- canary validation,
- format checking,
- first-pass audits,
- and high-volume rejection work.

Use stronger frontier models for:
- final candidate generation,
- final item refinement,
- difficult snippet calibration,
- and final audit of accepted items.

### Suggested routing

#### Cheap / screening tier
Use these first when possible:
- `deepseek/deepseek-chat`
- `x-ai/grok-3-mini`

#### Strong mid / frontier tier
Use these selectively:
- `openai/gpt-4.1`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-2.5-pro`

### Allowed substitutions

If exact OpenRouter model IDs differ, substitute the nearest current equivalent and document the substitution clearly in:

- `planning/family_c_sprint/checkpoint_status_v062.md`

### Hard routing rule

Do not waste frontier-model budget on trivial screening.
Do not trust cheap-model generation alone for final accepted items.

---

## Phase plan

# Phase 0 — Bootstrap and state recovery

This phase must happen first.

### Tasks

1. verify branch and repo status,
2. confirm the current Family C counts,
3. inventory prior hardening artifacts,
4. identify exactly what is already committed from the prior run,
5. verify that `14_hardening_orchestrator_prompt.md` is present,
6. create or refresh `checkpoint_status_v062.md`,
7. perform a minimal API smoke test if the key is present,
8. commit the bootstrap state.

### Deliverables

- updated `checkpoint_status_v062.md`
- a brief state recovery section inside the checkpoint file
- a micro-commit for Phase 0

### Stop condition

Pause at **Gate 1**.

---

# Phase 1 — Recover and preserve prior hardening outputs

This phase converts prior progress into stable repo state.

### Tasks

1. verify grading audit artifacts exist and are readable,
2. verify evidence recalibration artifacts exist and are readable,
3. verify whether `hardening_generate_v2.py` exists and whether it is usable,
4. if useful work only exists in temp/log space, convert it into repo files immediately,
5. commit the recovered state.

### Deliverables

- any recovered scripts placed in repo,
- any recovered artifacts written into `outputs/family_c/`,
- checkpoint update,
- micro-commit.

### Rule

Do not move into large-scale generation if prior work is still sitting only in logs or temp files.

---

# Phase 2 — Wrong-to-right hardening in small batches

This is the core bottleneck phase.

### Core problem

Many wrong-to-right items were too easy, and generic famous problems were not useful.

### Required generation strategy

Generate **small batches** only.

For each batch:

1. generate candidate WR items,
2. validate against cheap canaries,
3. reject too-easy items immediately,
4. preserve accepted candidates in durable files,
5. commit,
6. update checkpoint,
7. optionally continue to next batch.

### Hard generation rules

- avoid famous internet-famous benchmark puzzles,
- avoid bat-and-ball,
- avoid snail-in-the-well,
- avoid heavily memorized textbook traps,
- favor less canonical but still clean reasoning tasks,
- target known LLM weaknesses without becoming ambiguous.

### Suggested weakness categories

- multi-step reasoning with clean arithmetic structure,
- base-rate neglect,
- temporal confusion,
- spatial relation reasoning,
- order-of-operations edge cases,
- counterintuitive but checkable math,
- controlled commonsense traps not famous online,
- comparison and quantity reasoning where first-pass intuition is often wrong.

### Batch size

Keep each generation batch small:

- 2–4 candidate C1 WR items per batch,
- 2–4 candidate C2 WR items per batch,
- no large monolithic generation jobs.

### Candidate state files

Persist all outputs into repo files such as:

- `outputs/family_c/hardening_c1_wr_batch_*.json`
- `outputs/family_c/hardening_c2_wr_batch_*.json`

Do not rely on nohup logs as the main state.

### Commit rule

Commit after every accepted batch or every 15–20 minutes, whichever comes first.

### Stop condition

Pause at **Gate 2** after batch 1.

---

# Phase 3 — Grading robustness hardening

This phase continues the valuable work already started.

### Tasks

1. audit actual model outputs against grading rules,
2. expand aliases where appropriate,
3. confirm parsing robustness for fenced and preamble JSON,
4. flag any item whose grading semantics are brittle,
5. write a grading audit delta file,
6. commit the changes.

### Rule

Do not change core scoring semantics casually.
This phase is about robustness and correctness, not re-theorizing the benchmark.

### Deliverables

- updated candidate JSONs if aliases / grading rules are safely improved,
- `outputs/family_c/hardening_grading_audit_delta_v062.json`,
- checkpoint update,
- micro-commit.

---

# Phase 4 — Evidence snippet calibration

This phase should remain bounded and item-specific.

### Tasks

1. identify flagged C2 items with weak, too-strong, or borderline evidence snippets,
2. calibrate in small targeted item batches,
3. verify revised snippets produce appropriate pressure,
4. write recalibration artifacts,
5. commit.

### Rule

Do not turn this into open-ended prompt experimentation.
Each recalibration should be tied to a specific item and artifact.

### Deliverables

- updated C2 items,
- `outputs/family_c/hardening_evidence_recalibration_v062.json`,
- checkpoint update,
- micro-commit.

---

# Phase 5 — Full canary validation

Only run this once enough new material is in place.

### Tasks

1. validate all new and changed items,
2. confirm clean/quarantine status,
3. verify WR clean counts,
4. verify total clean counts,
5. capture failures clearly,
6. write a full validation artifact,
7. commit.

### Deliverables

- `outputs/family_c/hardening_validation_summary_v062.csv`
- `outputs/family_c/hardening_validation_details_v062.json`
- updated checkpoint file
- micro-commit

### Stop condition

Pause at **Gate 3**.

---

# Phase 6 — Final triage and report

This phase is where clean state is consolidated.

### Tasks

1. merge accepted candidate items into canonical Family C candidate files,
2. update clean / quarantine statuses,
3. confirm target counts,
4. write the hardening report,
5. write final checkpoint file,
6. commit.

### Deliverables

- updated candidate JSONs
- `outputs/family_c/hardening_report_v062.md`
- final `planning/family_c_sprint/checkpoint_status_v062.md`
- final micro-commit

### Stop condition

Pause at **Gate 4**.

---

## Non-negotiable rules

1. **Micro-commit constantly.**
2. **Update checkpoint file after every commit.**
3. **Stop at human gates.**
4. **Do not store important work only in nohup logs or /tmp.**
5. **Do not run giant background jobs without incremental durable outputs.**
6. **Do not expose secrets.**
7. **Do not use only one model for all tasks.**
8. **Do not trust famous benchmark traps as hard items.**
9. **Do not silently change benchmark-defining semantics.**
10. **Do not overrun the sprint into benchmark-notebook design work unless explicitly instructed.**

---

## Recommended commit cadence examples

Examples of acceptable frequent commit points:

- bootstrap done
- quarantine manifest verified
- grading fixes batch done
- parser robustness fix committed
- evidence recalibration for 2 items done
- first C1 WR accepted batch written
- first C2 WR accepted batch written
- canary validation artifact written
- triage update done
- report draft saved

If you think “I’ll commit later,” you are probably about to repeat the same failure mode.

---

## Deliverables table

| Deliverable | Path | Required |
|---|---|---|
| Checkpoint file | `planning/family_c_sprint/checkpoint_status_v062.md` | Yes |
| Recovery notes | embedded in checkpoint file | Yes |
| Phase 0 smoke / state verification | `outputs/family_c/` artifacts as needed | Yes |
| WR generation batch outputs | `outputs/family_c/hardening_c1_wr_batch_*.json`, `outputs/family_c/hardening_c2_wr_batch_*.json` | Yes |
| Grading audit delta | `outputs/family_c/hardening_grading_audit_delta_v062.json` | Yes |
| Evidence recalibration delta | `outputs/family_c/hardening_evidence_recalibration_v062.json` | Yes |
| Validation summary | `outputs/family_c/hardening_validation_summary_v062.csv` | Yes |
| Validation details | `outputs/family_c/hardening_validation_details_v062.json` | Yes |
| Final report | `outputs/family_c/hardening_report_v062.md` | Yes |
| Updated candidate files | `data/family_c/*.json` | Yes |

---

## Required report structure for `hardening_report_v062.md`

The final report should include:

1. current branch and commit hash,
2. what was recovered from prior hardening work,
3. what was newly generated,
4. how many WR candidates were generated and accepted,
5. how many items remain quarantined,
6. grading issues fixed,
7. evidence snippets recalibrated,
8. final clean counts,
9. final WR clean counts,
10. whether targets were met,
11. what remains for the next sprint,
12. exact repo state from which to resume.

Keep it concrete.

---

## Required structure for `checkpoint_status_v062.md`

At minimum include:

```markdown
# Family C Hardening Checkpoint Status v0.6.2

## Current state
- Branch:
- Latest commit:
- Current phase:
- Safe to resume from here: yes/no

## What is done
- ...

## Files changed since last checkpoint
- ...

## Artifacts produced
- ...

## Exact next step
- ...

## Blockers / user decisions needed
- ...
```

Update it every time.

---

## Resume-safe execution style

When running commands:

- prefer deterministic scripts over ad hoc shell pipelines,
- write outputs into repo paths immediately,
- checkpoint after each meaningful batch,
- avoid orphan processes,
- if you must background something, ensure it writes incremental durable outputs,
- do not launch broad parallelism unless each branch of work is independently checkpointable.

---

## Final instruction to the orchestrator

Your job is **not** just to push hard.
Your job is to push hard **without losing work**.

A sprint that produces fewer items but leaves behind a clean resumable repo with 8 strong commits is better than a sprint that produces more ephemeral work and times out.

If in doubt:

- narrow the batch,
- write the artifact,
- commit,
- update checkpoint,
- ask to continue.

That is the correct operating behavior for this VPS hardening sprint.
