# Item Development Methodology

**Repository:** `seanmichaelmcgee/metajudge`  
**Target branch reviewed:** `claude/build-qa-audit-format-kUeo0`  
**Reference commit reviewed:** `dae5dd1fb27d5826b9f337892da9823f6ba952c5`

This document describes how MetaJudge-AGI benchmark items were developed through API-prompted authoring workflows for both **Family A (calibration / epistemic monitoring)** and **Family B (selective abstention / control action selection)**. It is intended as a methodology backgrounder for Kaggle writeups, internal reproducibility, and future dataset rotation when contamination pressure or benchmark saturation requires regeneration.

This document is intentionally **descriptive rather than duplicative**. It explains the authoring process, quality gates, and contamination-management strategy while **pointing to the canonical implementation artifacts** for scoring, adjudication, configuration, and prompt templates. In keeping with repository rules, it does **not** restate scoring formulas, hardcoded decision weights, or embedded implementation logic that already live in the codebase and configuration files.

---

## 1. Purpose & Scope

MetaJudge-AGI is built around the idea that benchmark quality is not just a matter of collecting hard questions. The benchmark must also remain interpretable, regenerable, and resistant to contamination over time. That means the project needs a documented methodology for how benchmark items were authored, filtered, stress-tested, and promoted into active evaluation sets. This document provides that methodology backgrounder.

The immediate purpose is twofold. First, it supports **reproducibility** for public-facing reporting, including Kaggle writeups, by showing that benchmark items were not assembled ad hoc. Second, it supports **dataset lifecycle management**. If a batch becomes stale, too easy, too well known, or otherwise compromised by model training data contamination, the same methodology can be rerun to generate new items without changing the benchmark’s conceptual foundations.

This document covers the development pipelines for both major benchmark families:

- **Family A**: calibration-oriented items designed to expose overconfidence, underconfidence, and failure of epistemic monitoring under adversarial conditions.
- **Family B**: selective abstention / control-oriented items designed to test whether a model chooses the right action among answering, clarifying, verifying, or abstaining.

This methodology is governed primarily by the following repository documents:

- `SOUL.md`
- `CLAUDE.md`
- `planning/dataset_construction_plan.md`
- `planning/archive/calibration_v3/*`
- `docs/family_b_*`
- `data/adjudication_registry.json`
- `config/benchmark_config.yaml`

Where this document summarizes a process, the source files above remain the canonical reference for operational detail.

---

## 2. Design Principles

The benchmark development process follows several stable design principles that recur across both families.

### 2.1 Adversarial search, not naive item collection

The project does not treat benchmark construction as a matter of gathering trivia or “hard questions.” Instead, it uses an **adversarial search paradigm**. The authoring side is allowed to spend more time, run more tools, perform deeper verification, and stage multi-agent review. The evaluated model, by contrast, is typically constrained to a single inference pass or similarly restricted evaluation condition. The central idea is to deliberately exploit the asymmetry between **authoring-time effort** and **inference-time effort**.

This principle is especially explicit in the calibration pipeline, where item generation was reoriented away from static difficulty and toward mechanisms that predict confidence failure. Rather than asking, “Is this question difficult?” the construction process asks, “Does this item exploit a known asymmetry that should mislead a model into unwarranted confidence?”

### 2.2 Behavioral evidence over self-report

`SOUL.md` is explicit that the project prefers **behavioral evidence** over self-descriptions of certainty, awareness, or introspection. Models are evaluated on what they do under structured conditions, not on whether they claim to be uncertain, careful, humble, or reflective. This matters for both families:

- In **Family A**, confidence is meaningful only when tied to correctness and item structure.
- In **Family B**, action choice is evaluated by whether the control action was appropriate for the epistemic situation, not by whether the model merely narrated uncertainty.

This principle protects the benchmark from superficial “I may be wrong” style responses that sound metacognitive without demonstrating useful monitoring or control.

### 2.3 Mechanism-driven item design

Items are authored around **mechanisms of failure**, not just content domains. For Family A, these mechanisms include adversarial structure such as code-execution dependence, compositional traps, temporal boundary reasoning, ambiguity-induced overclaiming, and prototype interference. For Family B, items are organized around required control actions and known misclassification failure modes.

Mechanism-driven design has two advantages:

1. It improves interpretability, because a poor result can be mapped back to a known cognitive pressure or control error.
2. It makes regeneration feasible, because future items can be authored to preserve the same mechanism even if the surface content is completely replaced.

### 2.4 Contamination-aware construction

The benchmark is designed with contamination risk in mind from the beginning. `planning/dataset_construction_plan.md` defines a tiered sourcing strategy:

- **Tier A**: direct import candidates from external datasets when suitable.
- **Tier B**: inspiration / validation sources that inform item writing without being copied directly.
- **Tier C**: in-house authored items.

In practice, this encourages a hybrid workflow: reuse externally grounded ideas where they help anchor validity, but transform, validate, or newly author items so that the final benchmark is not just a repackaged public dataset. The tier structure also supports later rotation: items can be retired and replaced without throwing away the overall benchmark architecture.

### 2.5 Deterministic grading and explicit adjudication

The benchmark avoids open-ended LLM judges as the primary grading mechanism. Instead, it uses deterministic grading rules and registry-based adjudication. The canonical grading behavior lives in `data/adjudication_registry.json` and the implementation code that consumes it. The methodology implication is important: item development must produce prompts and gold targets that are scorable by explicit rules, not by loose semantic interpretation after the fact.

That requirement feeds backward into authoring. Candidate items that are interesting but not defensibly gradable are often rejected. Benchmark value is not defined only by intellectual difficulty; it is defined by the combination of **diagnostic pressure**, **evaluation stability**, and **reproducibility**.

---

## 3. Family A: Calibration Item Pipeline

Family A is the benchmark’s calibration-oriented item family. Its purpose is to measure whether models appropriately align confidence with correctness under adversarially chosen item structures. The pipeline evolved significantly over multiple versions.

### 3.1 Version history

#### V1: near-total failure of the initial batch

The earliest construction attempt performed poorly. The now-archived analysis shows that the first pass produced a candidate set with an extremely low survival rate: effectively **29 of 30 candidates were rejected**, leaving only a single survivor. The failures were not random. They exposed a structural mistake in the original authoring strategy: too many items were merely “interesting” or “tricky” rather than truly discriminative for calibration. Some were vulnerable to contamination, some were too easy for frontier models, and some had poorly specified gold behavior.

The V1 post-mortem is important because it changed the project’s philosophy. It showed that naive batch generation plus light filtering was not enough. Calibration benchmarking required deliberate adversarial design.

#### V2: four-agent expansion pipeline, but items still too easy

V2 responded by increasing authoring sophistication. The project introduced a broader multi-agent generation process and grounded item construction more explicitly in cognitive science concepts documented in `planning/archive/calibration_v3/v2_cognitive_science_directive.md`. The goal was to move beyond generic hard questions and toward items that express interpretable failure mechanisms.

However, the V2 expansion still produced sets that were often **too easy for strong models**. The clearest signal came from model sweeps in which **Gemini Flash solved 97/100 items**, and broader five-model evaluation showed that the batch failed most of the intended discrimination criteria. This was a crucial lesson: a cognitively motivated item is not automatically a calibration-effective item.

#### V4: two-agent adversarial generation and large-scale filtering

V4 was the decisive redesign. Instead of simply widening generation, it restructured the authoring workflow into a **two-agent adversarial architecture** with shared context, explicit mechanism targets, contamination blacklists, and post-generation filtering through multi-model validation. This phase produced **266 candidates**, of which **102 survived** the quality gates, for an overall yield of **38.3%**.

The V4 process also materially improved discrimination. The cumulative summary shows that a large fraction of the final items were model-discriminating, and certain mechanisms—notably IOED and prototype-related structures—performed especially well. The shift from initial yields around 21% to later yields around 60% in stronger sub-batches reflects a maturing pipeline rather than a lucky batch.

#### V4.2: targeted remediation and tri-label repairs

After V4, the benchmark was not treated as finished. It received targeted repairs, including **seven IOED replacements** and later **three tri-label gold-answer fixes**. The point is methodological: the pipeline includes not just generation and filtering, but also **post-hoc maintenance** when audit findings show brittle golds or ambiguous labels. This is part of the benchmark lifecycle, not an exception to it.

### 3.2 V4 two-agent architecture

The V4 pipeline uses two specialized authoring agents operating from a shared project context block.

#### Shared context block

Both agents inherit the same global constraints, including:

- the benchmark’s metacognitive framing,
- contamination awareness,
- the target evaluation setup,
- the requirement for deterministic scorable outputs,
- the prohibition against merely stylistic or blog-post-style trick questions,
- and the expectation that items should survive cross-model probing.

The shared block functions as a common doctrine layer. It keeps mechanism-specific generation aligned with the benchmark’s global goals.

#### Agent A remit

Agent A is tasked with mechanisms that are more naturally grounded in explicit structure or computation. In the V4 prompts, this includes clusters such as:

- code execution,
- compositional reasoning,
- IOED-style items,
- conditional temporal reasoning,
- anchoring,
- and numerical precision.

These item types are especially useful when the benchmark wants to expose overconfidence caused by quick heuristic patterning in settings where the author had access to deliberate construction and verification.

#### Agent B remit

Agent B is tasked with mechanisms more closely related to cognitive interference or socialized response patterns. In the V4 prompts, this includes clusters such as:

- modified CRT-like constructions,
- prototype interference,
- RLHF-style overconfidence pressures,
- and ambiguity-as-metacognition failures.

Agent B therefore tends to generate items where the main trap is not raw computation but a misleading default response policy, an overlearned pattern, or an ambiguity that models incorrectly treat as answerable.

#### Why two agents?

The two-agent split is not cosmetic. It does three useful things:

1. **Reduces mode collapse in generation.** One agent is less likely to overproduce one kind of trap.
2. **Improves mechanism coverage.** Different item families need different authoring instincts.
3. **Supports cleaner audit trails.** Items can later be interpreted in light of the authoring lane that produced them.

### 3.3 Mechanism taxonomy and adversarial asymmetries

A useful way to understand Family A is as a cross-product of **mechanisms** and **authoring-vs-inference asymmetries**.

#### Ten practical mechanism buckets

Across the V4 prompts and downstream summaries, the pipeline effectively operates with ten practical mechanism buckets:

1. Code execution
2. Compositional reasoning
3. IOED
4. Conditional temporal reasoning
5. Anchoring
6. Numerical precision
7. Modified CRT
8. Prototype interference
9. RLHF overconfidence
10. Ambiguity as metacognition

Some repository summaries group anchoring and numerical precision more tightly, but separating them is useful methodologically because they fail for different reasons: anchoring exploits misleading reference values, while numerical precision exploits hidden quantitative brittleness.

#### Seven adversarial asymmetries

The adversarial directive makes the underlying search logic explicit. Items are selected to exploit one or more asymmetries between the authoring process and the evaluated model:

1. **Compute depth asymmetry** — the author can deliberate more deeply than the model is allowed to at inference.
2. **Multi-agent verification asymmetry** — authors can stage cross-checking and debate; the model often answers in one pass.
3. **Compositional construction asymmetry** — authors can assemble traps by combining elements more carefully than a model retrieves them.
4. **Numerical precision asymmetry** — authors can verify exact values and edge cases; models often approximate.
5. **Tool-augmented authoring asymmetry** — authors may use scripts, calculators, or structured checks; inference may be tool-free.
6. **Temporal knowledge boundary asymmetry** — authors can deliberately place items at uncertainty boundaries where models overclaim.
7. **Deterministic code-execution asymmetry** — authors can ground an item in exact execution, while models may only simulate execution heuristically.

These asymmetries matter more than “difficulty” in the ordinary sense. A Family A item is valuable when it reliably provokes the wrong confidence profile for principled reasons.

### 3.4 Quality gates

Family A candidates do not become benchmark items simply because they were generated by a sanctioned prompt. They pass through multiple quality gates.

#### Structural validation

Candidates are first checked for basic benchmark viability:

- valid format,
- answerability under the intended protocol,
- defensible gold target,
- scorable response space,
- and absence of obvious contamination or triviality.

This stage eliminates malformed or conceptually incoherent items before any more expensive probing.

#### Five-model discrimination sweep

The benchmark then uses a multi-model sweep protocol to test whether items are genuinely discriminative. The governing documents define a five-model panel and a set of calibration success criteria. The purpose is not only to see whether items are hard, but to see whether they create the **patterned spread** required for calibration analysis.

An item that everyone gets right is usually not useful. An item that everyone gets wrong may be useful only in limited ways. The most valuable items are those that reveal structured differences in correctness and confidence across models and mechanisms.

#### Registry-driven grading

The final benchmark does not rely on hand-wavey semantic judging. Calibration items are tied to the adjudication registry in `data/adjudication_registry.json`, which encodes deterministic answer-checking behavior through a finite set of grading rule types. The methodological consequence is simple: Family A development is constrained by grading reality from the start.

This encourages candidate items with clean target structure, explicit answer space boundaries, and traceable adjudication logic.

#### Rejection logging

Rejected candidates are not discarded silently. The repository maintains rejection logs for calibration items, which record why a candidate should not enter the benchmark. This provides several benefits:

- it prevents rejected bad ideas from repeatedly re-entering later batches,
- it makes failure patterns visible,
- and it improves the next generation prompts by showing what should be avoided.

The rejection process therefore acts as institutional memory. It is part of the authoring method, not just cleanup.

---

## 4. Family B: Selective Abstention Pipeline

Family B tests a different metacognitive capability. Instead of asking whether confidence tracks correctness on short-answer items, it asks whether the model chooses the **right control action** for the epistemic situation. The target behaviors are not free-form displays of caution; they are structured action choices.

### 4.1 Action taxonomy and seven-point audit

Family B is built around four canonical actions:

1. **Answer** — the prompt is sufficiently well-posed and answerable as given.
2. **Clarify** — the model needs missing user intent, referent, unit, timeframe, or preference information.
3. **Verify** — the model should check a fact, computation, source, or time-sensitive claim before answering.
4. **Abstain** — the best action is not to answer directly, because the prompt is false-premised, unknowable, incoherent, intrinsically unpredictable, or otherwise unsuitable for a direct answer.

The 48-item pilot design organizes these actions into subtypes so that Family B does not collapse into a handful of toy examples. The redesign charter then adds a **seven-point audit checklist** to make sure each item is control-valid rather than merely arguable.

That checklist forces reviewers to ask, among other things:

- whether the intended action is genuinely necessary,
- whether a corrective answer would be better than simple refusal,
- whether the item is testing epistemic quality rather than style,
- and whether failure would actually be informative about metacognition.

This is one of the most important design advances in Family B. It prevents the benchmark from rewarding rote refusal behavior or penalizing good-faith corrective responses.

### 4.2 Multi-turn adversarial construction

Family B development evolved into a multi-role authoring process rather than a single prompt pass. The repository’s design and kickoff documents describe a workflow involving multiple roles across multiple models. In practice, the process behaves like a compact adversarial editorial loop:

- one stage proposes candidate items,
- another stage critiques action validity,
- another stage stress-tests false-premise handling,
- another stage checks whether the prompt really supports the intended gold action,
- and later stages run model probes and post-hoc review.

The three-model probe described in the kickoff findings was especially useful because it showed that Family B failure modes were not uniform. Some action classes were relatively stable; others—especially clarify and false-premise abstention—were much more fragile.

This is why Family B cannot be authored reliably by writing a list of “questions that seem ambiguous.” The items must survive interaction between author intent, evaluator interpretation, and actual model behavior.

### 4.3 False presupposition and corrective non-answering

One of the hardest Family B issues is **false presupposition**. Some prompts look like they belong in abstain, but a strong model may do something better than a bare abstention: it may offer a **corrective non-answer** that identifies the false premise and redirects appropriately.

The redesign charter handles this explicitly. It argues that the benchmark should not confuse “did not answer literally” with “good control behavior.” For example, if a question presupposes a non-existent fact, the ideal response may be to state that the premise is false rather than to produce an opaque refusal.

Methodologically, this matters because Family B is supposed to assess useful control, not ceremonial compliance. The benchmark therefore treats false-premise handling as a richer design space than a simple abstain/not-abstain dichotomy.

### 4.4 Cross-model probe validation and pilot revisions

Family B was not frozen after the first item draft. The kickoff findings document a three-model probe that surfaced several key observations:

- some classes were easier than expected,
- clarify was unusually difficult,
- false-premise items often misled models,
- confidence was often poorly calibrated,
- and one model showed JSON-compliance issues that complicated clean scoring.

These findings led to direct revision. Items were reclassified, false-premise examples were improved, and the pilot composition was adjusted. This is methodologically important because it shows that **observed model behavior** was used to refine the benchmark before broader deployment.

Family B therefore follows the same general philosophy as Family A: generation alone is not enough. Items become benchmark material only after they survive adversarial review plus empirical probing.

The Family B scoring specification defines success criteria labeled B1–B5. This document does not restate the formulas or thresholds from that spec, but their role in methodology is clear: they ensure that the benchmark is not merely class-balanced, but also behaviorally discriminative across action classes and difficulty strata.

### 4.5 Rejection criteria

The Family B rejection log shows several recurring patterns for why candidates are excluded. These patterns are useful enough that they should be treated as durable methodology.

#### 1. Too open-ended or philosophical

Items such as broad philosophical prompts often do not support a unique gold action. They produce debates about tone rather than evidence about control.

#### 2. Trivially classifiable prompts

Some prompts are so obviously answerable or so obviously false that they do not meaningfully test action choice. These may be useful for debugging but not for the benchmark core.

#### 3. Boundary confusion between clarify, verify, and abstain

A candidate may look interesting but fail because the intended control action is not sufficiently defensible. If expert reviewers can reasonably disagree about whether the prompt needs clarification or verification, the item may be too unstable for benchmark use.

#### 4. Contentious prompts that are still answerable

Some prompts appear to invite abstention because they touch loaded topics, but in fact they have a perfectly straightforward informational answer. These are rejected because they test social caution rather than epistemic control.

#### 5. Subjective or preference-laden prompts

If the correct action depends mainly on taste, ideology, or framing conventions, the item is weak as metacognitive evidence.

#### 6. Pseudo-ambiguity and fake clarify cases

Some prompts initially look underspecified but really just ask for a list, a best-effort answer, or a conventional summary. These are rejected because they do not demand a genuine clarify action.

Together, these patterns show that Family B item writing is closer to policy design than to trivia writing. The core task is to create prompts whose **control structure** is stable enough to support deterministic evaluation.

---

## 5. Quality Assurance Framework

The benchmark’s quality assurance framework spans both families. It ensures that item generation, scoring, and reporting remain aligned.

### 5.1 Adjudication registry

The repository uses an adjudication registry to keep grading explicit and deterministic. The registry contains a finite set of grading rule families rather than unconstrained semantic judgment. At a high level, these cover patterns such as exact-match spaces, tri-label spaces, numeric tolerance-based checks, and similar structured answer regimes.

The methodological value of the registry is threefold:

1. It makes scoring inspectable.
2. It forces authors to think about scorable answer spaces during item construction.
3. It reduces drift between benchmark definition and benchmark implementation.

When the registry or gold labels are updated—as in the later tri-label fixes—that change becomes part of the auditable benchmark lifecycle.

### 5.2 Multi-model sweep protocol

Both benchmark families rely on model sweeps, not just spot checks. The benchmark config defines the active model panel, and `SOUL.md` defines success criteria that items or batches should satisfy before being considered benchmark-worthy.

For Family A, the C-series criteria are meant to detect whether calibration pressure is real rather than anecdotal. For Family B, the B-series criteria are designed to ensure that action-selection behavior is genuinely differentiating models and item classes.

The role of the sweep protocol is not simply “score the models.” It is also a **benchmark validation tool**. If a batch fails to generate the expected behavioral spread, the problem may lie with the dataset rather than with the models.

### 5.3 Audit exports and run artifacts

The repository expects benchmark runs to produce structured exports, including audit CSVs and a run summary artifact. These exports allow later review of:

- per-item outcomes,
- mechanism-level patterns,
- class-level action behavior,
- and benchmark-wide diagnostics.

This is crucial because benchmark development is iterative. Without exports, a weak batch can only be judged impressionistically. With exports, the team can identify exactly where failure is concentrated and revise the prompt templates or selection filters accordingly.

---

## 6. Contamination Management & Dataset Rotation

Contamination is treated as an expected lifecycle problem rather than an exceptional event. The benchmark is therefore designed to support rotation.

### 6.1 Tiered sourcing strategy

The tiered sourcing plan provides the basic anti-contamination scaffold:

- **Tier A** allows selective import from external datasets when direct reuse is defensible.
- **Tier B** uses outside datasets as inspiration or validation sources rather than final benchmark rows.
- **Tier C** emphasizes original in-house item writing.

This means the benchmark can preserve conceptual continuity while rotating the surface form of the items. A benchmark family does not have to die when a specific row becomes contaminated; that row can be replaced by another item expressing the same mechanism or control structure.

### 6.2 Anti-gaming countermeasures

`config/benchmark_config.yaml` defines explicit anti-gaming measures. Without reproducing the implementation logic, the core ideas include:

- behavior-first scoring,
- hidden action-class structure,
- prompt format variation,
- decoy confidence cues,
- symmetric correction setups,
- adversarial source labeling,
- cross-template evaluation splits,
- and limiting rewards for verbosity.

These measures are methodology, not cosmetic tuning. They are intended to reduce the chance that a model can achieve benchmark success through superficial formatting behavior, overfit prompt recognition, or generic hedging strategies.

### 6.3 Rotation plan

A practical rotation plan follows from the rest of the pipeline:

1. retire items whose contamination risk rises,
2. regenerate replacements using the same prompt families and audit checklists,
3. validate new batches through the same sweep protocol,
4. preserve mechanism and action coverage even if surface content changes,
5. document each replacement cycle in cumulative summaries or changelogs.

This keeps the benchmark stable at the level of **construct validity** while allowing item turnover.

### 6.4 Budget discipline

The pipeline was explicitly shaped by API budget realities. This matters because large-scale candidate generation is cheap only if downstream filtering is disciplined. The benchmark development process therefore relies on staged narrowing:

- generate broad candidate pools,
- reject obvious failures quickly,
- reserve deeper probing for plausible survivors,
- and only then promote items into benchmark-active sets.

Budget discipline is not separate from scientific rigor here. It is what makes repeated regeneration practical.

---

## 7. Reproducing the Process

This section summarizes how a future team should reproduce the item-development workflow without reinventing the benchmark.

### 7.1 Required infrastructure

A reproducible rerun needs:

- access to the repository prompt templates and governing docs,
- API access for generation and probe models,
- deterministic evaluation code tied to the adjudication registry,
- the benchmark configuration specifying active models and anti-gaming settings,
- and a place to store candidate pools, rejection logs, audit exports, and cumulative summaries.

### 7.2 Step-by-step process for new items

#### Family A

1. Read `SOUL.md` and `CLAUDE.md` first.
2. Use `planning/dataset_construction_plan.md` to anchor sourcing choices.
3. Use the V4 prompt templates in `planning/archive/calibration_v3/generator_agent_prompts.md`.
4. Generate candidates separately through the two-agent architecture.
5. Tag each candidate by intended mechanism and asymmetry.
6. Eliminate malformed, trivial, contaminated, or non-scalable candidates.
7. Run cross-model probe evaluation.
8. Score with registry-driven adjudication only.
9. Review survivors against calibration success criteria and mechanism coverage.
10. Log rejections and promote only the validated subset.

#### Family B

1. Read `docs/family_b_dataset_design.md`, `docs/family_b_redesign_charter.md`, and `docs/family_b_kickoff_findings.md`.
2. Author candidates against the four canonical actions and subtype map.
3. Apply the seven-point audit to each candidate.
4. Stress-test false-premise handling and corrective-answer behavior.
5. Probe with multiple models before finalizing labels.
6. Reclassify or discard unstable prompts.
7. Validate against the Family B scoring specification and class coverage goals.
8. Record rejections explicitly.

### 7.3 Template prompt locations

The main prompt and methodology assets live in:

- `planning/archive/calibration_v3/generator_agent_prompts.md`
- `planning/archive/calibration_v3/adversarial_search_directive.md`
- `planning/archive/calibration_v3/v2_cognitive_science_directive.md`
- `planning/archive/expansion_sprint_v2.md`
- `docs/family_b_dataset_design.md`
- `docs/family_b_redesign_charter.md`
- `docs/family_b_kickoff_findings.md`

These should be treated as a coordinated family of documents rather than isolated notes.

### 7.4 Validation checklist

Before a regenerated batch is accepted, confirm all of the following:

- item design is consistent with `SOUL.md`,
- prompts use the current canonical action or mechanism framing,
- no scoring formulas or hardcoded weights were reimplemented in prose or side scripts,
- all items are mapped to deterministic adjudication pathways,
- rejection logs have been updated,
- cross-model sweeps show real behavioral discrimination,
- benchmark outputs include audit artifacts,
- and the resulting set still preserves the benchmark’s conceptual coverage.

If those conditions are met, the process has been reproduced successfully even if the exact item text differs from earlier batches.

---

## Source Map

The methodology summarized above is grounded primarily in the following repository files:

- `SOUL.md`
- `CLAUDE.md`
- `planning/dataset_construction_plan.md`
- `planning/archive/expansion_sprint_v2.md`
- `planning/archive/calibration_v3/generator_agent_prompts.md`
- `planning/archive/calibration_v3/adversarial_search_directive.md`
- `planning/archive/calibration_v3/cumulative_summary.md`
- `planning/archive/calibration_v3/v2_cognitive_science_directive.md`
- `docs/family_b_dataset_design.md`
- `docs/family_b_redesign_charter.md`
- `docs/family_b_kickoff_findings.md`
- `docs/family_b_scoring_spec.md`
- `data/adjudication_registry.json`
- `data/frontier_rejection_log.json`
- `data/family_b_rejection_log.json`
- `config/benchmark_config.yaml`

Where implementation details already exist in those files, they remain the canonical source.
