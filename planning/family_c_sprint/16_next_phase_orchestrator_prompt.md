# MetaJudge Family C — Next-Phase Orchestrator Prompt (post-corrected sweep)

## Purpose

You are restarting the **Family C question-hardening and dataset-development loop** after a corrected 5-model sweep materially changed the interpretation of the pilot results.

Your job is **not** to do another broad planning sprint.
Your job is to run a **phased, commit-gated, API-heavy hardening program** that:

1. treats the corrected sweep as the new baseline reality,
2. uses OpenRouter much more heavily for question generation and audit,
3. focuses specifically on **harder wrong-to-right (WR) items** for Family C,
4. preserves clean, benchmark-compatible grading semantics,
5. forces durable checkpoints, pushes, and user stops,
6. outputs a stronger Family C clean set for later narrative-notebook and benchmark-notebook integration.

This is a **benchmark dataset construction sprint**, not a memo-writing sprint.

---

## New baseline assumptions you must adopt

Treat the corrected sweep as the active truth unless directly disproven by repo artifacts from the current working branch/PR.

Key implications from the corrected sweep summary provided by the user:

- a prior grading bug materially distorted the earlier results,
- most of the previously reported damage was grading artifact,
- 3 of 4 non-rigid models showed positive Turn-2 improvement,
- Grok appears rigid and useful as a canary for “never revise” behavior,
- many WR items are too easy and are not generating enough discernibility,
- Family C now needs **harder WR items targeting roughly 40–60% Turn-1 accuracy**,
- current priority is **item generation, hardening, grading robustness, and dataset iteration**, not further broad repo planning.

You must act on those implications.

---

## Repo orientation and source-of-truth rule

Before doing anything else, orient yourself to the repo, but do not be fooled by stale prose.

### Source-of-truth order
When sources conflict, trust them in this order:

1. current working branch / current PR artifacts
2. latest sprint-specific commits and hardening artifacts
3. current dataset JSONs and task/scoring code
4. current checkpoint and hardening reports
5. broad planning docs
6. README
7. older planning/history docs

The public `main` branch appears to lag the current Family C push; its latest visible public commits are still around the Mar 21–22 v0.5.1/refinement sprint and README updates, so do **not** treat public-main prose as the current execution truth if the active PR/branch says otherwise. citeturn134477view0

### Files to read first
Read these before making changes:

1. current working branch status (`git status`, `git branch`, `git log --oneline -25`)
2. current PR / branch diff versus base
3. `planning/family_c_sprint/14_hardening_orchestrator_prompt.md`
4. `planning/family_c_sprint/15_resume_safe_hardening_orchestrator_prompt.md`
5. latest Family C checkpoint/status file
6. latest hardening report(s)
7. `data/family_c/SCHEMA.md`
8. current Family C candidate JSONs
9. `metajudge/tasks/self_correction_v2.py`
10. current Family C scoring code/config
11. `scripts/openrouter/client.py`
12. latest validation / sweep artifacts

Then produce a brief **state-recovery memo** in-repo before proceeding.

---

## Competition and benchmark framing

Remember what this project is building:

- This Kaggle / DeepMind event is a **benchmark-design hackathon**, not a standard prediction competition.
- The benchmark must stay targeted, held-out, interpretable, and reproducible.
- Family C is meant to improve metacognitive **discernibility** across models, not merely create clever prompts.
- The later architecture remains:
  - **clean Family C dataset** →
  - **5-model narrative notebook sweep** →
  - **thin official benchmark notebook integration**.

That competition framing still matters, so avoid techniques that make scoring opaque, non-reproducible, or notebook-incompatible. fileciteturn17file13 fileciteturn17file14

---

## Scientific frame you must preserve

You must stay aligned with the recent Family C research grounding:

- Intrinsic self-correction often fails mainly because **error detection** is the bottleneck, not repair. fileciteturn17file3
- Compute-equivalent baselines matter; a second attempt alone can mimic “self-correction.” fileciteturn17file0
- Generic “are you sure?” prompting can induce sycophantic flipping rather than genuine metacognitive correction. fileciteturn17file3
- The benchmark should measure **correction decision quality**, not just raw task improvement. fileciteturn17file5
- Damage should matter more than indiscriminate revision, but exact weighting should be calibrated after stable item generation and reliable grading, not guessed early. fileciteturn17file9turn17file10

Academic anchors for this sprint (last ~24 months where possible):

1. **Kamoi et al., TACL 2024** — intrinsic self-correction is weak and fairness / compute-equivalent baselines matter. fileciteturn17file3
2. **Tyen et al., ACL Findings 2024** — error detection is the primary bottleneck. fileciteturn17file3
3. **Kumar et al., ICLR 2025 (SCoRe)** — stronger self-correction is achievable under specialized training, which implies generic prompting should not be overcredited. fileciteturn17file10
4. **Zhang et al., ACL 2025** — review prompts can induce sycophantic / capitulatory behavior. fileciteturn17file10
5. **CorrectBench / Self-Correction Bench 2025 landscape** — existing self-correction benchmarks still do not combine metacognitive framing, C1/C2 split, and decision-quality focus the way MetaJudge aims to. fileciteturn17file5

Use these to constrain behavior, not to trigger another literature-only loop.

---

## Primary strategic shift for this sprint

The main bottleneck is now **question development quality and difficulty**, especially WR items.

Therefore, you must explicitly shift from:

- one-shot item drafting,
- low-iteration generation,
- underpowered API use,
- and broad, brittle batch runs,

toward:

- **multi-turn item-authoring dialogues** with frontier models,
- **adversarial / red-team generation loops**,
- **iterative refinement of single items or tiny batches**,
- **heavier OpenRouter usage** for high-value item development,
- and small, durable, commit-gated progress.

The return on paid API calls is expected to be high here. Underuse of OpenRouter is considered a failure mode.

---

## OpenRouter usage policy — much heavier use required

This sprint is explicitly authorized to use OpenRouter much more heavily than prior runs.

### Required stance
- Use OpenRouter as a **core generation and audit engine**, not a light convenience tool.
- Expect generation to be **10x or more more API-intensive** than the earlier underpowered runs if needed.
- Use frontier models for high-value generation, adversarial critique, and final audit.
- Use cheaper models for screening, rejection, and simple canary checks.

### Security rules
- never print API keys,
- never commit API keys,
- read from environment only,
- if `OPENROUTER_API_KEY` is missing, stop and say so clearly.

### Required logging
Every model call batch must produce auditable outputs containing at least:
- timestamp,
- task name,
- model,
- prompt or prompt hash,
- parsed output if any,
- raw output,
- latency,
- usage/tokens if available,
- error text if any,
- item IDs touched.

Do not let expensive exploration live only in terminal output.

---
## Model routing and API usage policy (OpenRouter)

Family C hardening must use OpenRouter **much more heavily** than prior runs, especially for **wrong-to-right (WR)** item development. The previous level of API usage was insufficient for the difficulty target.

The goal is **not** to use expensive models everywhere.  
The goal is to use frontier models **strategically and repeatedly** for the hardest parts of item generation, adversarial hardening, and final acceptance.

### Core principle

Use a **3-tier routing strategy**:

- **Tier 1: cheap screening models** for schema checks, fast canary validation, easy rejection, and bulk filtering
- **Tier 2: strong workhorse frontier models** for routine drafting, medium-cost refinement, and evidence calibration
- **Tier 3: max frontier models** for high-value WR item generation, adversarial multi-turn loops, and final acceptance audit

Do not waste frontier budget on trivial screening.  
Do not rely on cheap models for final WR item authoring.

---

### Tier 1 — cheap screeners

Use for:
- schema/JSON compliance checks
- first-pass candidate rejection
- “too easy” detection
- fast canary validation
- bulk screening of generated candidates
- quick format robustness checks

Preferred models:
- `google/gemini-2.5-flash-lite`
- `openai/gpt-5-mini`
- `x-ai/grok-3-mini`

Optional fallback:
- `mistralai/mistral-small-3.2-24b-instruct-2506`

Do **not** use Tier 1 models as final authors for accepted WR items.

---

### Tier 2 — workhorse frontier

Use for:
- routine candidate drafting
- medium-cost refinement
- evidence snippet calibration
- structured critique
- routine adversarial review
- C2 snippet tuning
- clarification of borderline grading cases

Preferred models:
- `anthropic/claude-sonnet-4.6`
- `openai/gpt-5.2`
- `google/gemini-3-pro-preview`
- `x-ai/grok-4.1-fast`

Use Tier 2 heavily for day-to-day progress.

---

### Tier 3 — max frontier

Use for:
- high-value WR candidate generation
- multi-turn adversarial/red-team loops
- hardest C1 intrinsic-review items
- hardest C2 evidence-assisted items
- final refinement of shortlisted items
- final independent audit on accepted candidates

Preferred models:
- `anthropic/claude-opus-4.6`
- `openai/gpt-5.2-pro`
- `google/gemini-3.1-pro-preview`
- `x-ai/grok-4`
- `moonshotai/kimi-k2-thinking`
- `deepseek/deepseek-r1`

These models should be used more often than in prior runs for the hardest item-development work.

---

## Default role assignments

### Primary author models
Use one of these for serious WR authoring:
- `anthropic/claude-opus-4.6`
- `openai/gpt-5.2-pro`

Fallback:
- `anthropic/claude-sonnet-4.6`
- `openai/gpt-5.2`

### Adversarial red-team critic
Use a **different model family** than the author whenever possible.

Preferred:
- `x-ai/grok-4`
- `deepseek/deepseek-r1`
- `moonshotai/kimi-k2-thinking`
- `google/gemini-3.1-pro-preview`

Fallback:
- `x-ai/grok-4.1-fast`
- `google/gemini-3-pro-preview`

### Final independent acceptance auditor
Use a third model family where possible.

Preferred:
- `openai/gpt-5.2-pro`
- `google/gemini-3.1-pro-preview`
- `anthropic/claude-opus-4.6`

Fallback:
- `openai/gpt-5.2`
- `anthropic/claude-sonnet-4.6`

### Cheap canary validators
Use these aggressively:
- `google/gemini-2.5-flash-lite`
- `x-ai/grok-3-mini`
- `openai/gpt-5-mini`

If cheap canaries solve the item immediately and reliably, the item is too easy, badly framed, or belongs in a different stratum.

---

## Required multi-turn WR hardening loop

For **high-value WR items**, do not use one-shot generation.

Use the following loop:

1. **Author pass**
   - frontier author generates one candidate item bundle
   - output must include prompt, gold answer, intended failure mechanism, expected T1 profile, and explanation of why revision should be possible but non-trivial

2. **Adversarial critique pass**
   - different frontier model attacks the candidate
   - it must identify:
     - why the item may be too easy
     - whether the item resembles famous benchmark/trick questions
     - whether the reasoning path is too obvious
     - whether the gold answer or evidence makes revision too easy
     - whether the item is ambiguous or grading-hostile

3. **Revision pass**
   - author revises the item using the critique

4. **Second adversarial pass**
   - adversarial model attacks again
   - must explicitly try to break the item as a Family C WR candidate

5. **Optional third-model critique**
   - use a third frontier model for especially promising or expensive items

6. **Cheap canary test**
   - run Tier 1 canaries
   - if canaries succeed too easily, reject, reclassify, or revise

7. **Acceptance audit**
   - independent frontier auditor decides:
     - accept
     - revise again
     - quarantine
     - reject

For the hardest/highest-value WR items, allow **up to 5–7 iterations** of this loop.

Do **not** apply 5–7 iterations to every candidate.
Reserve long loops for:
- shortlisted WR items,
- items intended to improve model separation,
- difficult C1 intrinsic items,
- difficult C2 items with promising but imperfect evidence structure.

---

## Cost policy

The previous API utilization was too low.

You are explicitly allowed to spend **substantially more** on API calls for item development if quality improves materially.

Default budget priority:
- **50–60%** of generation budget: frontier author + adversarial hardening loops
- **20–25%**: evidence calibration and cross-model critique
- **15–20%**: cheap canary screening
- **5–10%**: final audit / acceptance checks

If budget pressure emerges, scale back in this order:
1. reduce optional third-model critique
2. reduce iteration depth on mediocre candidates
3. reduce Tier 3 usage for mid-value items
4. keep Tier 3 for only the best WR candidates

Do **not** solve budget pressure by reverting to one-shot cheap-model generation for difficult WR items.

---

## Preferred concrete routing patterns

### High-cost / maximum quality pattern
- **Author:** `anthropic/claude-opus-4.6`
- **Adversary:** `x-ai/grok-4` or `deepseek/deepseek-r1`
- **Final auditor:** `openai/gpt-5.2-pro` or `google/gemini-3.1-pro-preview`
- **Cheap canaries:** `google/gemini-2.5-flash-lite`, `x-ai/grok-3-mini`

### Balanced pattern
- **Author:** `anthropic/claude-sonnet-4.6`
- **Adversary:** `deepseek/deepseek-r1` or `x-ai/grok-4.1-fast`
- **Final auditor:** `openai/gpt-5.2` or `google/gemini-3-pro-preview`
- **Cheap canaries:** `google/gemini-2.5-flash-lite`, `openai/gpt-5-mini`

### C2 evidence-calibration pattern
- **Snippet drafter/refiner:** `google/gemini-3.1-pro-preview` or `anthropic/claude-sonnet-4.6`
- **Adversarial pressure check:** `deepseek/deepseek-r1` or `x-ai/grok-4`
- **Cheap canary sensitivity test:** `google/gemini-2.5-flash-lite`

---

## Substitution rule

If any listed model is unavailable or performs poorly in practice:
- substitute the nearest current equivalent,
- document the substitution,
- and continue.

Model substitutions must be logged in the checkpoint file and hardening report.

---

## Hard rules for model use

1. Do not use the same model family for author, adversary, and final auditor when avoidable.
2. Do not let cheap models dominate high-value WR development.
3. Do not rely on a single frontier model’s judgment for final acceptance.
4. Do not use one-shot generation for difficult WR candidates.
5. Do not continue iterating mediocre items past their value threshold.
6. Do not overspend frontier budget on trivial schema or formatting checks.
7. Every accepted high-value WR item must have gone through:
   - frontier authoring,
   - adversarial critique,
   - cheap canary validation,
   - independent acceptance audit.

---

## Success criterion for model routing

The routing policy is working if:
- accepted WR items are materially harder than prior batches,
- classic/famous too-easy traps are being rejected early,
- the item pipeline produces better model separation,
- frontier usage is concentrated on the hardest/highest-yield items,
- and overall item quality improves enough to justify the added API cost.

---

## The required item-generation method

### The core method is not one-shot generation.
For high-value WR items, you must use a **multi-turn iterative authoring loop**.

For each candidate item or tiny batch:

1. **Initial authoring pass**
   - Ask a frontier model to propose an item bundle.
   - The item must be framed for Family C, not as a generic puzzle.

2. **Adversarial / red-team critique pass**
   - Ask the same or another strong model to attack the item.
   - Required attack questions:
     - Is this too famous / too memetic?
     - Is this too easy for current frontier or even mid-tier models?
     - Is the gold answer ambiguous?
     - Could the evidence snippet accidentally reveal the answer too directly?
     - Is the intended WR behavior actually plausible?
     - Is there any grading ambiguity?

3. **Revision pass**
   - Feed critique back into generation.
   - Ask for a revised harder version, not just cosmetic edits.

4. **Repeat**
   - Continue the author → red-team → revise loop until success criteria are met.
   - Default ceiling: **5 iterations**.
   - For especially valuable items, you may go to **7 iterations**.

5. **Canary validation**
   - Run cheap models first.
   - If both cheap canaries solve it easily, reject or revise.

6. **Frontier sanity check**
   - For accepted candidates, do at least one frontier check to ensure the item is hard but not broken.

7. **Durable write + checkpoint**
   - Save candidate, audit note, and validation result.
   - Update checkpoint.
   - Micro-commit.

This loop is mandatory for WR hardening.

---

## Success criteria for WR candidates

The target for new WR items is roughly:

- **Turn-1 accuracy around 40–60%** on the intended validation panel,
- non-trivial room for revision,
- clean gold answer,
- clean grading path,
- not obviously famous,
- not obviously impossible,
- compatible with Family C C1 or C2 structure,
- reproducible in the later narrative and benchmark notebook workflows.

Reject items that are:
- obvious,
- famous internet traps,
- impossible to grade cleanly,
- too dependent on hidden assumptions,
- too tool-dependent,
- too evidence-revealed,
- or too narrow in a way that causes unstable model behavior unrelated to self-correction.

---

## C1 and C2 behavior constraints

### C1
- intrinsic review,
- no substantive new evidence,
- must not collapse into “you are wrong, fix it,”
- should probe whether the model can reconsider appropriately without external support.

### C2
- bounded external intervention,
- for this sprint, prefer **fixed short evidence snippets**,
- evidence must create revision pressure without trivially giving away the answer,
- no live retrieval or tool-dependent runtime paths in this sprint.

Keep C1 and C2 separate from the outset.

---

## Unresolved policy for this sprint

Keep unresolved in scope, but do not let it dominate.

- Maintain a **small tagged unresolved subset**.
- Do not let unresolved become the main target of this hardening sprint.
- Use unresolved only where it clearly supports metacognitive interpretation and clean scoring.
- Do not build a judge-heavy prose-scoring subsystem here.

This remains a secondary edge-case track, not the main engine of progress. fileciteturn17file5

---

## Phased execution plan

# Phase 0 — state recovery and freeze on current truths

### Tasks
- inspect current branch / PR state,
- inspect latest hardening artifacts,
- confirm corrected sweep outputs are present and understood,
- confirm grading bug is resolved or isolate what remains,
- produce a one-page state memo,
- create/update checkpoint file,
- micro-commit.

### Stop
Stop for user confirmation before new generation begins.

### Required commit
`Family C next-phase: checkpoint phase 0 state recovery after corrected sweep`

---

# Phase 1 — scoring and grading freeze for generation

### Goal
Before generating more items, lock the **core grading semantics** that will be used during this sprint.

### Tasks
- confirm corrected grading path,
- identify any remaining brittle grading cases,
- freeze current per-item grading semantics for generation-time evaluation,
- write a short grading note,
- micro-commit.

### Rule
Do not keep changing grading rules mid-generation unless a genuine bug is found.

### Stop
Stop for user confirmation before high-cost item generation begins.

### Required commit
`Family C next-phase: checkpoint phase 1 grading semantics frozen for WR hardening`

---

# Phase 2 — high-cost WR hardening batches

This is the main expensive phase.

### Batch size
Work in **tiny batches**:
- preferred: 1–3 candidate items per batch,
- only enlarge if a stable productive pattern emerges.

### Required behavior
For each batch:
1. author with frontier model,
2. red-team with frontier model,
3. revise,
4. repeat 3–5 times, up to 7 if the item is promising,
5. canary-test with cheap models,
6. optionally frontier-check,
7. save outputs,
8. update checkpoint,
9. micro-commit,
10. stop and summarize.

### Deliverables per batch
- candidate JSON/JSONL,
- audit log,
- validation output,
- acceptance or rejection note,
- updated checkpoint.

### Stop cadence
You must stop after **every batch** for a brief user-facing summary.
If the batch was expensive or materially changed direction, explicitly request continuation before proceeding.

### Required commit pattern
Examples:
- `Family C next-phase: checkpoint C1 WR hardening batch 1`
- `Family C next-phase: checkpoint C2 WR hardening batch 1`
- `Family C next-phase: checkpoint WR hardening batch 2 accepted candidates`

---

# Phase 3 — C2 snippet calibration and edge-case cleanup

### Tasks
- tune or replace weak evidence snippets,
- verify they induce revision pressure without giving away the answer,
- validate against at least one cheap and one frontier model,
- keep unresolved subset small and clean,
- micro-commit after each meaningful snippet batch.

### Stop
Stop after the first recalibration batch and present:
- what got stronger,
- what still looks weak,
- what should be deferred.

---

# Phase 4 — integrated narrative-sweep preparation

### Goal
Produce the Family C clean set and grading package ready for the next 5-model narrative sweep.

### Tasks
- merge accepted items,
- quarantine weak/ambiguous items,
- verify clean counts,
- verify WR counts,
- write prep note for narrative sweep,
- micro-commit.

### Stop
Stop and request confirmation before any full narrative sweep is launched.

### Required commit
`Family C next-phase: checkpoint narrative-sweep-ready clean set`

---

# Phase 5 — post-sweep interpretation and benchmark-path recommendation

### Goal
After the next narrative sweep, decide what is benchmark-worthy.

### Tasks
- evaluate discernibility,
- check whether Family C is now strong enough for later benchmark integration,
- recommend reclassification of too-easy WR items,
- state what still needs iteration,
- micro-commit report updates.

Do not push Family C into the benchmark notebook unless the narrative sweep actually supports it.

---

## Commit, push, and checkpoint rules

### Micro-commit rule
Commit after any of the following:
- new script,
- changed script,
- candidate batch saved,
- validation batch saved,
- checkpoint updated,
- grading note saved,
- snippet recalibration saved,
- any meaningful 15–20 minute unit of work.

### Push rule
Push to remote after:
- every completed phase,
- every expensive batch with accepted artifacts,
- any point where loss of local state would be painful.

### Checkpoint file
Maintain a checkpoint file at all times, containing:
- branch,
- latest commit,
- current phase,
- artifacts written,
- accepted candidates,
- quarantined candidates,
- exact next action,
- whether user confirmation is required before proceeding.

If a timeout occurs, the next VPS must be able to resume from this file and the committed repo state.

---

## Hard rules

1. Do not start with a giant generation run.
2. Do not trust famous trap questions.
3. Do not underuse OpenRouter.
4. Do not overspend frontier calls on trivial screening.
5. Do not let expensive work live only in logs.
6. Do not skip user stops.
7. Do not skip micro-commits.
8. Do not silently change grading semantics once Phase 1 is frozen.
9. Do not merge ambiguous items into clean.
10. Do not let narrative and future benchmark workflows diverge in core grading meaning.

---

## Primary deliverables

By the end of this next-phase run, you should aim to produce:

1. updated checkpoint/status file,
2. grading freeze note,
3. new WR candidate batches with audit logs,
4. C2 snippet calibration outputs,
5. updated candidate / quarantine / clean dataset artifacts,
6. a short narrative-sweep readiness memo,
7. durable commits and pushes after every meaningful checkpoint.

---

## Final success condition

Success is **not** a huge amount of activity.
Success is:
- harder WR items,
- better discriminability,
- heavier and smarter OpenRouter usage,
- clean grading semantics,
- small-batch adversarial iteration,
- and a repo state that can survive another timeout without losing meaningful work.
