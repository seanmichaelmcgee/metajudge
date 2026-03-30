# MetaJudge vNext Orchestrator Brief — Calibration Strengthening, Family B Repair, and Bridge-Layer Advancement

## Status

**Purpose of this document:** drive a long-running VPS orchestration sprint that improves the benchmark scientifically **without destabilizing the working Kaggle notebook stack**.

This brief is written for:
- the VPS orchestrator,
- sub-agent teams,
- repo maintainers working in branches,
- item-construction agents using frontier-model APIs,
- audit agents validating scoring and benchmark defensibility.

This sprint is **not** a reset. It is a **measurement-hardening and benchmark-quality sprint**.

---

## Governing objective

Build the next MetaJudge iteration so that it:
1. **Preserves and improves calibration as a monitoring benchmark**.
2. **Substantially improves Family B as a control benchmark**.
3. **Adds a bridge layer** showing where monitoring and control align or dissociate.
4. **Fixes the known technical defects from the current sprint report** before further scale-up.
5. **Uses frontier-model API calls in multi-turn adversarial and constructive loops** to improve items, keys, and grading with higher scientific defensibility than cheap one-shot generation.

---

## Source hierarchy and regrounding rules

The team must repeatedly reground to the following sources, in this order:

1. **`SOUL.md` and the files it references**  
   Treat this as the repo’s governing implementation/priority document unless a newer branch-specific implementation memo clearly supersedes it for that branch’s narrow scope.

2. **Competition framing**
   - `kaggle_measuring_agi.md`
   - official Kaggle competition materials
   - official Google DeepMind paper / blog framing

3. **Most recent audit evidence**
   - `sprint_report.md`
   - latest `calibration_item_audit*.csv`
   - latest `family_b_item_audit*.csv`
   - any bridge report JSON or run summary artifacts

4. **Existing strategy docs already produced for the project**
   - program charter
   - calibration refinement charter
   - Family B redesign charter
   - bridge/minimal-safe plan
   - frontier agent operating manual
   - theory-aligned update docs

### Mandatory regrounding cadence

The orchestrator must re-check and restate alignment to project objectives:
- at sprint start,
- after every major branch merge,
- after every benchmark regeneration pass,
- after every scoring change,
- before every Kaggle run,
- before declaring any family “ready.”

Each regrounding note must answer:
- Are we still measuring the intended construct?
- Did we preserve existing discriminatory signal?
- Did we introduce grader fragility?
- Did we violate thin-notebook discipline?
- Are we making the scientific story more defensible, not merely larger?

---

## Competition-aligned interpretation of success

The project exists within a benchmark-design hackathon, not a model-building contest. The core evaluation goal is to design **high-quality tasks** that go beyond recall and test how frontier systems **reason, act, and judge**. The metacognition track specifically maps to:
- **monitoring**: confidence calibration, error monitoring, source judgment;
- **control**: error correction, strategic action selection under uncertainty.

Therefore, success is **not**:
- adding many items quickly,
- making the benchmark merely harder,
- maximizing branch activity,
- adding complex scoring that breaks notebooks.

Success **is**:
- sharper construct validity,
- better answer-key defensibility,
- preserved or improved model discrimination,
- clearer monitoring vs control separation,
- auditable grading,
- repeatable Kaggle runs with explicit artifacts.

---

## Current state summary

### What appears strong already
- The project has a strong scientific direction around **monitoring vs control**.
- Calibration has a meaningful discriminatory core.
- Monitoring-trap style items are contributing real signal.
- The bridge idea is scientifically valuable and likely competition-relevant.
- The notebook workflow has already undergone significant iterative stabilization and must be protected.

### What is still broken or fragile
From the latest sprint evidence and audits, the immediate defects are:

#### P0 / fix before new scientific expansion
1. **IOED block needs review**  
   It is producing pathological performance and may contain answer-key or item-quality problems.

2. **Family B scorer wiring is incomplete**  
   `score_family_b_item_v2` exists but is not fully wired into the notebook task function. This means corrective-answer logic and improved scoring are not consistently reaching the actual run path.

3. **Per-model summary leakage / blended run stats**  
   Current summary reporting appears to blend across models, reducing interpretability.

4. **Known grading/keying issues in answer-class Family B items**
   - `abs_001`
   - `abs_004`
   These weaken the answer-family signal and must be fixed or replaced.

#### P1 / high priority scientific repair
5. **Family B still over-penalizes some correct epistemic behavior**
   Especially where a false or impossible premise should be handled by corrective negation rather than blind abstention.

6. **Family B action measurement remains less trustworthy than its conceptual design**
   Utility can be right while `is_correct` remains wrong or under-informative.

7. **Calibration still has localized grading fragility**
   Especially parser/keying disputes and mechanism blocks that may look discriminative but are partly artifact-driven.

#### P2 / next phase once instrumentation is fixed
8. **Need a better frontier-model item generation loop**
   Item authoring must become more rigorous, adversarial, and evidence-backed.

9. **Need multi-model bridge reporting**
   Current bridge narrative is strong, but it needs a more robust comparative layer.

---

## Core scientific direction for this sprint

## A. Calibration remains a separate benchmark family
Treat calibration as the **monitoring benchmark**.

Its job is to measure:
- correctness,
- confidence,
- discrimination of correct vs incorrect,
- metacognitive vulnerability to misleading fluency / false familiarity / ambiguity,
- robustness across mechanisms.

Calibration is **not** where selective clarify/verify/abstain policy should be tested directly.

### Calibration vNext principles
- Preserve the strongest existing signal.
- Avoid gratuitous rewrite.
- Remove contradictory or weakly grounded keys.
- Split internally into more interpretable strata.
- Add a limited new subset rather than replacing the benchmark wholesale.

### Calibration strata to maintain or sharpen
1. **Clean objective**
   - Code execution
   - exact arithmetic / exact program output
   - tightly verifiable temporal or numeric items

2. **Objective but brittle**
   - anchored facts requiring alias discipline
   - temporal items needing explicit date anchoring
   - compositional lookups where stale or multiple conventions can exist

3. **Metacognitive diagnostic traps**
   - misleading fluency
   - false familiarity
   - CRT-style intuition traps
   - ambiguity-sensitive answering

### High-yield calibration mechanisms
Protect and refine:
- `MonitoringTrap`
- `ModifiedCRT`
- `AmbiguityMetacognition`
- `CodeExecution`

Review and repair:
- `IOED`
- any parser-sensitive or alias-fragile items
- any item where “correctness” depends on controversial ontology

### Calibration scoring amendments — minimum safe scope
Allow only targeted changes:
- clearer alias / normalization rules,
- parser hardening,
- exact-vs-acceptable-answer policy cleanup,
- family-level reporting,
- unambiguous Brier / calibration metric naming.

Do **not** rewrite calibration scoring from scratch unless current logic is provably invalid.

---

## B. Family B is the control benchmark
Treat Family B as the benchmark for **metacognitive control**:
- answer when answerable and reliable,
- clarify when ambiguity or missing constraints blocks safe answering,
- verify when computation, real-time data, or external evidence is required,
- abstain when the question is genuinely unknowable, incoherent, or ungroundable.

### Family B must measure control, not generic refusal
This is crucial. The question is not “can the model refuse?”  
The question is “does the model choose the right control action based on its epistemic state?”

### Family B current problems that must be fixed
1. **Action scoring remains under-specified**
   Matching `gold_action` alone is not enough.

2. **Corrective-answer cases are not fully handled**
   Example class: false premise or impossible-set questions where the best answer is a corrective statement rather than a vacuous abstention.

3. **Some answer items still have broken or debatable keys**
   These contaminate the “answer” class and must not remain as-is.

4. **Verify items vary in quality**
   Some truly require verification, some only require ordinary knowledge or correction.

5. **Clarify items must be genuine ambiguity / missing-information cases**
   Not merely awkwardly worded answerable questions.

### Family B scoring model to target
Maintain the public 4-action space if needed for Kaggle simplicity:
- `answer`
- `clarify`
- `verify`
- `abstain`

But internally, add decomposed scoring fields:

1. `action_correct_primary`
2. `action_acceptable_alternative`
3. `answer_correct_if_answered`
4. `premise_handling_quality`
5. `utility`
6. `harmfulness` or `epistemic_risk`
7. `notes_for_audit`

### Internal handling of corrective-answer cases
Do **not** rush to add a fifth public Kaggle label unless notebook and leaderboard complexity clearly justify it.

Preferred approach:
- keep 4 public actions,
- allow internally that some items accept a **corrective answer path** as a valid or near-valid success mode.

Examples:
- impossible-set questions,
- false historical presuppositions,
- malformed requests whose safest response is “none / that premise is false.”

### Family B target subdomains
Maintain and sharpen:
- clarify: missing preference, missing referent, missing unit, scope ambiguity, lexical ambiguity
- verify: real-time facts, high-precision calculation, source-dependent claims, current officeholders, current prices / rates
- abstain: unknowable future, subjective value questions, incoherent prompts, impossible premises, unsupported hidden-state questions
- false-presupposition handling: must explicitly test whether the model exits the false frame instead of answering inside it

---

## C. Bridge layer becomes a first-class reporting layer
The bridge layer asks:

- If the model appears uncertain, does it choose a safer control action?
- If the model is overconfident, does it over-answer?
- Where do monitoring and control dissociate?
- Which models have good calibration but poor control?
- Which models are poor calibrators but sometimes conservative controllers?
- Which mechanisms create the strongest monitoring-control gaps?

This layer is the scientific glue between the monitoring benchmark and the control benchmark.

### Bridge outputs to produce
At minimum:
- monitoring vs control quadrant classification,
- overconfidence-to-overanswer correlation,
- confidence bin vs utility curves,
- per-model bridge tables,
- per-mechanism bridge summaries,
- one writeup-ready visualization.

---

## Fixed work order

The orchestrator must enforce this order.

### Phase 0 — Repo and notebook preservation
Before any major question-generation sprint:
- confirm working branch strategy,
- preserve notebook lineage,
- preserve explicit input/output package behavior,
- confirm thin-notebook discipline,
- document current task-entry points and scoring hooks.

### Phase 1 — Immediate technical fixes
Must be completed first:

1. Review and repair or replace IOED items.
2. Wire `score_family_b_item_v2` into the active notebook task path.
3. Fix per-model summary blending.
4. Review/fix answer-family defects in Family B (`abs_001`, `abs_004`, and any newly identified peers).
5. Re-run a narrow validation pass to verify the fixes actually changed outputs.

### Phase 2 — Calibration vNext refinement
- preserve current discriminatory core,
- split by internal strata,
- repair keying and parser fragility,
- add small theory-aligned monitoring subset,
- produce revised calibration package + audit evidence.

### Phase 3 — Family B redesign
- audit every item for construct validity,
- reclassify problematic items,
- define acceptable alternative response modes,
- repair scoring schema,
- add stronger clarify / verify / false-premise items,
- produce revised Family B package + audit evidence.

### Phase 4 — Bridge layer expansion
- multi-model bridge sweep,
- report generation,
- failure-mode mapping,
- writeup-oriented scientific narrative.

### Phase 5 — Frontier-model item expansion
Only after scoring and instrumentation are stable:
- frontier multi-turn item generation,
- adversarial challenge / critique loops,
- evidence-grounded rewrites,
- benchmark inclusion only after strict audit.

---

## Agent-team architecture

## 1. Orchestrator
Responsibilities:
- maintain project context,
- enforce phase order,
- prevent premature benchmark expansion,
- coordinate merges,
- require regrounding memos,
- ensure branch outputs are explicit and auditable.

The orchestrator must never delegate away the final decision on:
- benchmark inclusion,
- scoring changes,
- notebook integration,
- merge readiness.

## 2. Repo / notebook integrity team
Responsibilities:
- map active notebook task functions,
- identify scoring entry points,
- patch minimal-safe code changes,
- preserve explicit imports/exports,
- maintain run reproducibility.

Primary deliverables:
- patch plan,
- integration diffs,
- rollback notes,
- notebook parity validation.

## 3. Calibration refinement team
Responsibilities:
- review existing families,
- preserve discriminatory items,
- identify brittle keys,
- draft calibration-vNext subset,
- propose only minimal-safe grading amendments.

Primary deliverables:
- item audit table,
- keep/repair/replace decisions,
- revised benchmark JSON / package artifacts,
- family-level analysis.

## 4. Family B redesign team
Responsibilities:
- rewrite ambiguous or wrongly keyed items,
- define corrective-answer policy,
- refine clarify/verify/abstain boundaries,
- produce action-policy memo,
- create high-quality replacements and expansions.

Primary deliverables:
- revised item inventory,
- policy memo,
- scoring schema proposal,
- audited Family B vNext.

## 5. Scoring and analysis team
Responsibilities:
- design decomposed Family B scoring,
- keep calibration scoring changes minimal,
- fix summary leakage,
- produce bridge metrics and reports.

Primary deliverables:
- scoring amendment memo,
- tests,
- bridge tables,
- run-summary fixes.

## 6. Frontier-model item-construction team
Responsibilities:
- use frontier APIs in multi-turn constructive and adversarial sessions,
- generate, critique, rewrite, and evidence-check items,
- never add raw generated items directly to the benchmark.

Primary deliverables:
- candidate item packs,
- evidence notes,
- judge memos,
- final promoted items only after audit approval.

## 7. Audit and adjudication board
Responsibilities:
- final human-in-the-loop or top-level AI review,
- resolve key disputes,
- reject fragile items,
- check contamination risk heuristically,
- sign off on promotion to benchmark.

Primary deliverables:
- audit ledger,
- accept / revise / reject log,
- release recommendation.

---

## Frontier-model API usage policy

The next high-value item generation sprint should use **frontier models**, not small cheap models, for candidate generation and critique.

### Why
This sprint is building the benchmark’s scientific linchpins:
- higher-quality ambiguity cases,
- better false-premise items,
- stronger verify items,
- cleaner monitoring traps,
- better wording and clearer gold behavior,
- higher confidence in adversarial review.

This is a justified place to spend more per call.

### Required generation pattern
Every new or heavily revised item must go through a multi-turn loop:

1. **Generator turn**
   - propose item
   - propose construct label
   - propose gold behavior
   - explain why the item measures the target construct

2. **Adversary turn**
   - attack construct validity
   - identify alternate interpretations
   - identify stale / disputable keys
   - identify parser or alias risks
   - propose model-cheat paths

3. **Judge turn**
   - decide if the item survives
   - require rewrites
   - assign risk level

4. **Evidence turn**
   - where needed, provide supporting evidence or computation path
   - for verify items, define the external target/source precisely
   - for exact answer items, define canonical answer and acceptable aliases

5. **Rewrite turn**
   - sharpen wording
   - reduce ambiguity if answer-item
   - increase ambiguity if clarify-item
   - tighten real-time or computation necessity if verify-item
   - sharpen impossible or unknowable status if abstain-item

6. **Final audit turn**
   - approve, revise, or reject

### Required roles in multi-turn item construction
Use at least:
- **generator**
- **critic**
- **epistemic auditor**
- **grader/rubric designer**
- **final judge**

Optional additional role:
- **red-team solver** trying to answer incorrectly yet plausibly, to test robustness.

### Hard rule
No item enters the benchmark directly from a one-shot generation.

---

## Item-quality standards

Every candidate item must be judged on:

1. **Construct validity**
   - Does it actually test the intended mechanism?

2. **Answer-key defensibility**
   - Is the gold answer or gold action justified and stable?

3. **Interpretation control**
   - Are alternate interpretations handled explicitly?

4. **Grader tractability**
   - Can the item be graded reliably in the current architecture?

5. **Contamination / memorization concern**
   - Is the item so common that it mostly tests recall or contamination?

6. **Difficulty placement**
   - Is the item in the intended stratum?

7. **Discriminatory potential**
   - Is there reason to believe models will separate on this item?

8. **Metacognitive relevance**
   - Does failure reflect monitoring/control weakness rather than arbitrary obscurity?

---

## Specific recommendations by benchmark area

## Calibration — recommended focus
### Keep and sharpen
- monitoring traps with plausible-but-wrong intuitive pulls,
- ambiguity metacognition items where correct behavior is to recognize instability in interpretation,
- code execution with exact outputs and strong grading,
- select modified CRT items with unambiguous keys.

### Review carefully
- IOED,
- any question with controversy-heavy knowledge claims,
- any item relying on fragile parser behavior,
- any item where alias range is wide enough to hide the gold target.

### Add in limited number
New calibration subset should include:
- misleading fluency,
- false familiarity,
- premise-sensitive answer-only items,
- slight reflection-sensitive items where confidence should change if the model really monitors.

This remains an **answer-only** subset.

## Family B — recommended focus
### Clarify
Add or improve items where:
- a key referent is absent,
- a unit or measurement basis is missing,
- scope or granularity is underspecified,
- lexical ambiguity creates two incompatible but plausible meanings,
- user preference is necessary to proceed.

### Verify
Add or improve items where:
- the answer genuinely requires real-time retrieval,
- the answer genuinely requires code or exact arithmetic,
- the answer genuinely requires a live authoritative source,
- the model should not answer from static parametric memory.

### Abstain
Add or improve items where:
- the future is genuinely unknowable,
- the prompt is subjective in a way that blocks objective truth conditions,
- the request is incoherent or impossible,
- the premise is false and must be explicitly recognized as such.

### False-premise / corrective-answer zone
This must be treated as a special review lane.
For each such item decide:
- should best behavior be abstain?
- should best behavior be corrective answer?
- should both be allowed?
- how will that be reflected in scoring?

---

## Minimal-safe grading amendment plan

The project must avoid scoring work that breaks the notebook unless there is no alternative.

### Calibration
Allowed:
- parser fixes,
- alias cleanup,
- exact-vs-acceptable-answer hardening,
- mechanism-level metric cleanup,
- report naming/clarity fixes.

Avoid:
- new complex judge loops in the notebook,
- heavy external adjudication that threatens run reliability.

### Family B
Required:
- wire v2 scorer into active task path,
- split correctness dimensions,
- support acceptable alternative metacognitive responses where justified,
- preserve utility as a central signal.

Avoid:
- introducing public action complexity that the notebook cannot support,
- creating opaque scoring no one can audit.

### Bridge layer
Encouraged:
- derived analytics in post-processing,
- plots/tables based on exported artifacts,
- no need to complicate the notebook task path unless essential.

---

## Deliverables required from this sprint

## 1. Technical-fix packet
- wiring fix for Family B v2 scorer
- per-model summary fix
- IOED review memo
- answer-item defect review memo
- validation run notes

## 2. Calibration vNext packet
- keep/repair/replace table
- revised item pack
- parser/alias policy memo
- audit CSV from new run
- summary report

## 3. Family B vNext packet
- action-policy memo
- revised item pack
- decomposed scoring schema
- audit CSV from new run
- false-premise handling memo

## 4. Bridge packet
- multi-model bridge report
- confidence-to-utility analysis
- figure/table assets
- writeup-ready summary

## 5. Frontier generation packet
- prompt set for generation
- critic prompt set
- judge prompt set
- item candidate logs
- evidence logs
- promoted-item ledger

## 6. Merge recommendation packet
- branch summary
- risk assessment
- rollback plan
- recommended next Kaggle run state

---

## Acceptance criteria

The orchestrator should not declare this sprint successful unless:

### Technical
- Family B v2 scorer is confirmed active in the notebook run path.
- Per-model summaries are no longer blended.
- Known P0 item defects are resolved or removed.

### Scientific
- Calibration remains discriminative after fixes.
- Family B scoring is more faithful to true control behavior.
- At least one bridge analysis is clean enough for writeup use.
- New or revised items are supported by explicit audit notes.

### Operational
- Notebook remains runnable.
- Input/output artifacts remain explicit and reviewable.
- Changes are documented and branch-contained.
- No major scoring rewrite has broken previous working paths.

---

## Stop conditions and escalation

Stop and escalate to the orchestrator if:
- a proposed scoring change forces large notebook rewrites,
- a new item family adds complexity without improving construct validity,
- frontier generation produces many items but weak defensibility,
- Family B policy disagreement cannot be resolved,
- calibration signal drops sharply after “cleanup,”
- branches diverge so far that merge risk becomes high.

When escalation occurs, produce:
- concise problem statement,
- options,
- estimated code churn,
- scientific tradeoff,
- recommended decision.

---

## Suggested autonomous operating loop

1. Reground to `SOUL.md`, competition brief, sprint report.
2. Patch P0 technical defects.
3. Validate with narrow rerun.
4. Audit calibration keep/repair/replace.
5. Audit Family B keep/repair/replace.
6. Run frontier-model generation loop for highest-yield missing or weak areas.
7. Review candidates adversarially.
8. Promote only audited items.
9. Run multi-model benchmark sweep.
10. Produce calibration, Family B, and bridge reports.
11. Reground and decide next merge/run.

Repeat until:
- measurement quality meaningfully improves,
- scientific story becomes cleaner,
- notebook stability remains intact.

---

## Direct kickoff prompt for the VPS orchestrator

Copy the block below into the orchestrator bootstrap if needed.

---

You are the orchestrator for the MetaJudge vNext sprint. Your job is to coordinate long-running agent teams that improve the scientific defensibility, grading reliability, and benchmark usefulness of the MetaJudge metacognition project for the Kaggle “Measuring Progress Toward AGI” benchmark-design hackathon.

Operate under these rules:

1. Reground first to `SOUL.md`, the competition brief, the sprint report, and the latest audit CSVs.
2. Protect the notebook stack. Keep notebooks thin. Prefer package-side fixes.
3. Do not expand benchmark scope before fixing the current P0 defects.
4. Treat calibration as the monitoring benchmark and Family B as the control benchmark.
5. Build the bridge layer that explains monitoring-control dissociation.
6. Use frontier-model APIs for item generation, critique, rewrite, and adjudication.
7. Do not accept one-shot generated items into the benchmark.
8. Preserve existing discriminatory signal wherever possible.
9. Favor minimal-safe grading amendments over scoring rewrites that threaten notebook stability.
10. Produce explicit artifacts at every stage: memos, JSON/CSV outputs, audit ledgers, branch summaries, and merge recommendations.

Your required first actions:
- map the current notebook scoring path and confirm whether Family B v2 scoring is active;
- inspect and resolve IOED issues;
- fix blended per-model summaries;
- review known Family B answer-item failures;
- run a narrow validation pass;
- then launch separate Calibration, Family B, Scoring, and Frontier Generation teams.

Each team must return:
- objective,
- current findings,
- proposed changes,
- risk level,
- required code changes,
- artifacts produced,
- whether the work is ready to merge.

Do not confuse benchmark size with benchmark quality. The goal is a smaller number of more defensible, more interpretable, more discriminative tasks with auditable grading and a clear scientific narrative.

---

## Final instruction

This sprint should make the project:
- **more scientifically defensible,**
- **more metacognitively targeted,**
- **more analytically interpretable,**
- **more robust in scoring,**
- **and still runnable on Kaggle without destabilizing the working notebook structure.**
