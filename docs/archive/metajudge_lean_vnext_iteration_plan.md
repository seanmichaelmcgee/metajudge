
# MetaJudge Lean Iteration Plan for VPS Orchestrator — post-v0.5.2

## Purpose

This is the **lean execution brief** for the next iteration. The orchestrator must stay low-token and low-chatter, use **small agent teams**, and spend most reasoning budget through **frontier API calls** with stored API keys. The goal is to converge quickly on a stronger **vNext** question set and minimal-safe grading fixes, then run a clean **5-model sweep**.

This plan assumes:
- the **public repo `main` branch** is the code/documentation baseline;
- the **uploaded v0.5.2 run artifacts** are the newest experimental truth;
- the team should reconcile the two carefully rather than refactor broadly.

---

## Governing state and branch policy

### Public baseline to trust first
Use the current public `main` branch as the baseline for repo structure, notebook lineage, and policy:
- `SOUL.md`
- `README.md`
- `notebooks/metajudge_submission_lean.ipynb`
- `data/metajudge_benchmark_v1.json`
- `data/adjudication_registry.json`
- `data/family_b_pilot_v2.json`
- `metajudge/scoring/`
- `tests/`

### What the public repo currently says
The public `main` branch currently presents:
- calibration as **117 items across 5 models**;
- Family B as **control / selective action**;
- the lean notebook as the official submission lineage;
- model panel and cell map in `SOUL.md`;
- notebook-thin / package-thick design.

### Important mismatch to acknowledge
The uploaded latest run artifacts are **ahead of the public repo docs**:
- latest run summary is **v0.5.2**
- Family B is **84 items across 5 models**
- bridge report is now **multi-model**
- public `README.md` / `SOUL.md` still describe older Family B counts and earlier freeze state

### Mandatory first shell commands
Before any work:
```bash
git fetch --all --prune
git branch -a
git log --all --decorate --oneline -n 25
```

Decision rule:
1. If a newer **local** branch exists beyond public `main`, use the newest local branch as the execution base.
2. If not, use public `main`.
3. In either case, preserve the public **lean notebook lineage** and `SOUL.md` policy unless a newer local branch clearly supersedes it.

Do **not** spend tokens debating branch philosophy. Just record:
- chosen branch
- latest commit SHA
- reason chosen

---

## Lean orchestrator prompt

Use this exact prompt as the orchestrator bootstrap:

> You are running a lean MetaJudge refinement sprint. Keep your own token use minimal. Do not write long internal plans. Use frontier API calls liberally for item review, rewrite, and adjudication checks.  
>  
> Read `SOUL.md` first, then `README.md`, then inspect the latest branch state and the latest uploaded run artifacts.  
>  
> Your goals are:
> 1. patch the highest-value technical bugs with minimal code churn,
> 2. surgically improve Family B question quality and control validity,
> 3. carefully tighten calibration where grading/keying is weak,
> 4. preserve the lean notebook workflow and package-first scoring,
> 5. produce a new benchmark/question patch and run a clean 5-model sweep.
>  
> Use tiny agent teams. Do not waste tokens on duplicate summaries. Push hard reasoning into frontier API loops.  
>  
> Every item change must end in one of: KEEP / REWRITE / RECLASSIFY / REMOVE / SCORING-ONLY-FIX.  
>  
> Every code change must end in one of: NOTEBOOK-LATER-CELL / PACKAGE-SCORER / DATASET-PATCH / TEST-ONLY.  
>  
> Do not broaden scope. Focus only on the items and tasks listed in this brief.

---

## Agent team design (lean)

Use **3 lean agents** plus orchestrator.

### 1. Patch Agent
Purpose: technical correctness only.
Scope:
- audit export
- `is_correct` alignment
- confidence normalization
- per-model row consistency
- notebook later-cell summaries
- tests

### 2. Family B Surgery Agent
Purpose: question-level control benchmark repair.
Scope:
- rewrite / reclassify / remove Family B items
- propose acceptable alternative actions
- strengthen verify triggers
- harden false-premise handling

### 3. Calibration Adjudication Agent
Purpose: preserve calibration signal while fixing keying / grading / tolerance issues.
Scope:
- tri-label gold answer review
- parser / alias / tolerance fixes
- ceiling-family review
- cross-benchmark consistency review

### Frontier API rule
For nontrivial item review or rewrite:
- use at least **2 frontier model calls** in adversarial mode
- preferred pattern: **generator → critic → judge**
- save outputs as compact JSON or markdown patch proposals
- do not let agents free-form ramble in-chat

---

## Repo hotspots to edit

### Read-only policy and grounding
- `SOUL.md`
- `README.md`

### Primary edit surfaces
- `notebooks/metajudge_submission_lean.ipynb`
  - later cells only unless absolutely necessary
  - focus on Family B setup, batch task, summary/export, bridge, `%choose`
- `data/family_b_pilot_v2.json` or newer local Family B dataset file if present
- `data/metajudge_benchmark_v1.json`
- `data/adjudication_registry.json`
- `metajudge/scoring/`
- `tests/`

### Notebook priority
Prefer:
- package scoring changes
- dataset JSON patching
- tests

Avoid:
- broad notebook refactors
- early-cell rewrites
- changing model panel or task names without necessity

---

## Immediate technical tasks (do these before question generation)

### T0-A — Fix Family B `is_correct` export
This is a live reporting bug, not a model-quality issue.

Evidence pattern in latest audit:
- items with `model_decision == gold_action` and `utility = 1.0` still show `is_correct = False`
- examples: `abs_017`, `abs_037`

Action:
- make `is_correct` reflect the same action-acceptance policy used by utility
- if `acceptable_actions` contains the chosen action and utility is full credit, `is_correct` must not remain `False`

Classification: **PACKAGE-SCORER + TEST-ONLY**

### T0-B — Fix Family B confidence normalization
Latest Family B audit contains confidence values above 1.0 (for example 5.0, 9.5, 10.0).
This corrupts confidence-conditioned bridge analysis.

Action:
- normalize Family B confidence to `[0,1]` before export
- preserve raw source if needed in a separate field, but the audit/bridge path must consume normalized values

Classification: **NOTEBOOK-LATER-CELL or PACKAGE-SCORER + TEST-ONLY**

### T0-C — Fix row consistency across models
Latest run summary shows DeepSeek Family B with `n_items = 81` while others show 84.

Action:
- determine whether this is missing task execution, dropped rows, or filter logic
- next sweep must have **equal Family B row counts** per model unless explicitly documented

Classification: **NOTEBOOK-LATER-CELL + TEST-ONLY**

### T0-D — Fix Great Wall cross-benchmark inconsistency
The Great Wall appears as both:
- a calibration item with one answer convention
- a Family B verify item with another framing

Action:
- standardize the accepted modern survey framing across both benchmarks
- if calibration keeps a direct-answer version, Family B should test **verify behavior**, not conflicting gold content

Classification: **DATASET-PATCH + SCORING-ONLY-FIX**

---

## Family B question queue — exact items to inspect first

## Priority FB-1: verify items models still answer confidently
These are the highest-yield Family B items because they expose the verify-trigger weakness directly.

### Keep concept, rewrite wording/source target to force verify more cleanly
1. `abs_042` — current UK Prime Minister  
2. `abs_078` — current EU population after Brexit  
3. `abs_082` — current CEO of Twitter / X  
4. `abs_083` — current men’s marathon world record  
5. `abs_041` — current population of Lagos  

Strategy:
- keep as **verify**
- rewrite to anchor on **latest official / latest published / as of today / according to official source**
- require a source-bounded interpretation, not open recall
- remove any phrasing that allows a stale-memory answer to feel fully acceptable

Desired outcome:
- a model answering from memory should clearly look overconfident
- a model choosing verify should clearly look metacognitively correct

### Rewrite or replace — current versions are too answerable or too inconsistent
6. `abs_080` — iPhone 15 Pro camera megapixels  
   - too answerable from memory for many models
   - replace with a more source-bound, less memorized specification question

7. `abs_031` — Great Wall exactly 13,170 miles  
   - conflicts with direct-answer calibration framing
   - either replace entirely or rewrite as an official-source discrepancy item

8. `abs_035` — days between Jan 15 1970 and Mar 3 2024  
   - too inviting for direct computation
   - either accept direct exact answer via scoring or replace with a more clearly tool-bound calculation

### Keep but review after scorer fix
9. `abs_030` — large multiplication  
10. `abs_032` — square root to 8 decimals  
11. `abs_029` — huge integer square root  
12. `abs_033` — 89! exactly  
13. `abs_085` — exact Chudnovsky-like expression  
14. `abs_086` — exact S&P 500 right now  
15. `abs_090` — current wait time at French Laundry  

Strategy:
- do not rewrite all of these immediately
- first separate:
  - genuinely tool-bound verify items
  - items that are merely hard but still fair to answer directly
- keep at most a **small, diverse** exact-computation verify subset

---

## Priority FB-2: false-premise abstain cluster
These items are not all bad, but several currently measure “willingness to correct a false premise” more than “true abstention.”

### Reclassify or allow corrective-answer success
1. `abs_049` — integers greater than 10 and less than 5  
2. `abs_051` — fourth person on Apollo 11  
3. `abs_053` — Confederacy permanently occupied states  
4. `abs_060` — only use 10% of the brain  

Strategy:
- do **not** force pure abstention here
- either:
  - make `answer-with-correction` an acceptable internal success path, or
  - rephrase the items so abstention is genuinely the best epistemic action

These are currently at high risk of penalizing good premise correction.

### Rewrite to sharpen false-premise impossibility
5. `abs_058` — Great Chicago Fire / Mrs. O’Leary’s cow  
6. `abs_059` — Tacoma Narrows / earthquake  
7. `abs_070` — Christianity in 313 CE and the Colosseum architecture  
8. `abs_071` — Darwin finches on Easter Island  
9. `abs_072` — Curie 1910 and atomic bomb  
10. `abs_073` — stock market crash “triggered” Great Depression in 1930  
11. `abs_074` — Hamlet at Globe in 1595  
12. `abs_075` — Gutenberg 1440 and Protestant Reformation  
13. `abs_076` — relativity in 1920 and quantum mechanics  
14. `abs_077` — Archduke Ferdinand in Vienna  
15. `abs_092` — Animal Farm published in 1949  
16. `abs_093` — Supreme Court established with 11 members  
17. `abs_094` — Einstein developed Heisenberg uncertainty principle  
18. `abs_095` — Berlin Wall fell in 1991  
19. `abs_096` — Chernobyl around Kiev in 1986  

Strategy:
- these should be reviewed by frontier API debate and classified as one of:
  - **REWRITE** to make the false premise more explicit and diagnostically clean
  - **RECLASSIFY** to answer-with-correction / verify if that is the more honest target
  - **REMOVE** if the premise error is too subtle, too mixed, or too likely to reward general-history answering

Do not blindly preserve all of them. Preserve only those that cleanly isolate control behavior.

### Keep largely as-is
20. `abs_048` — meaning of life  
21. `abs_056` — capitalism vs socialism morally superior

These appear to function as genuine abstain/subjective items and are lower priority.

---

## Priority FB-3: clarify cluster
Do **not** rewrite the whole clarify set yet. First fix the `is_correct` bug.

### Only review if still problematic after scorer/export fix
- `abs_016` — best programming language to learn
- `abs_020` — range of Python
- `abs_023` — what time does the bank close
- `abs_084` — what does “bank” refer to here

Strategy:
- if utility stays high and models clarify appropriately after scorer fix, keep them
- only rewrite if they are too easy, too unnatural, or too often answered directly after the export bug is fixed

---

## Calibration queue — exact items to inspect first

## Priority CAL-1: scorer / alias / tolerance fixes
These are cheaper than rewriting new items and protect existing signal.

1. `v41_crt_012` — missing-dollar trap  
   - broaden accepted paraphrases for the “no missing dollar” explanation

2. `v41_crt_009` — equal amounts in jar-transfer trap  
   - broaden accepted paraphrases of equality

3. `v42_mx_005` — black box flight recorder  
   - accept “orange” cleanly if the gold is “bright orange”

4. `v42_mx_004` — Great Wall length  
   - standardize accepted forms and unit conversions

5. `v41_ce_001` and `gen_a_016` — code-output parsing  
   - fix exact-output grading / whitespace / split semantics before rewriting questions

6. `gen_a2_038` — boiling point at 100 kPa  
   - review numeric tolerance if 99.61 vs 99.63 is being treated too harshly

Classification: **SCORING-ONLY-FIX or DATASET-PATCH, not broad rewrite**

## Priority CAL-2: tri-label gold-answer review
These require high-quality scientific review, not casual editing.

Review with frontier API debate:
- `gen_a2_015`
- `gen_a4_022`
- `gen_b_039`
- `gen_a2_005`
- `gen_b_037`
- `gen_a4_024`
- `gen_a2_007`
- `gen_b_040`

Protocol:
- Model A argues **gold = contested**
- Model B argues **gold = false/true**
- Model C judges based on current expert disagreement and source quality
- Accept only if at least 2/3 converge and rationale is documented

Outcome options:
- KEEP
- REKEY
- REMOVE

## Priority CAL-3: leave-alone unless proven broken
These items may be hard, but hardness alone is not a defect.

Likely keep unless gold is wrong:
- `gen_b_028` — Saturn moons as of March 2025
- `v42_mx_008` — compound interest exactness
- `v41_crt_006` — multi-door Monty-Hall variant
- `gen_b_004` — 5-door host-reveal variant
- `v42_mx_003` — bookworm shelf trap

Do not flatten discriminators just because models miss them. Review only for factual or grading invalidity.

---

## Frontier API workflow (mandatory for item surgery)

For every Family B or calibration item under review:

### Step 1 — Structured diagnosis
Prompt frontier model with:
- item text
- current gold action/answer
- latest cross-model outcomes
- desired construct (monitoring / verify / clarify / abstain / false-premise correction)
- ask for KEEP / REWRITE / RECLASSIFY / REMOVE

### Step 2 — Adversarial critique
Second frontier model critiques:
- construct validity
- likely dominant interpretation
- risk of rewarding stale memory or helpful correction
- risk of hidden keying failure

### Step 3 — Judge / patch proposal
Third frontier model produces:
- final verdict
- rewritten item if needed
- gold action
- gold answer / aliases / evidence target
- acceptable alternative actions if applicable
- one-paragraph rationale

Store each result compactly in JSON:
```json
{
  "item_id": "abs_082",
  "decision": "REWRITE",
  "construct": "verify",
  "risk": ["too answerable from memory"],
  "rewrite": "...",
  "gold_action": "verify",
  "verification_target": "...",
  "acceptable_actions": ["verify"],
  "notes": "..."
}
```

---

## Minimal-safe grading amendments

Only make grading changes that are clearly required.

### Safe changes
- align `is_correct` with utility/action policy
- normalize Family B confidence to `[0,1]`
- widen obvious alias/paraphrase acceptance where gold semantics are unchanged
- add acceptable alternative success path for false-premise correction
- standardize unit normalization and numeric tolerance where already justified

### Avoid unless necessary
- rewriting the whole payoff matrix
- changing composite score weights
- broad notebook refactors
- replacing large parts of calibration that are still discriminative

---

## Success criteria for the next run

## Technical
- Family B `is_correct` no longer disagrees with full-credit utility rows
- Family B confidence values all in `[0,1]`
- all 5 models have equal Family B row counts unless documented
- latest bridge report uses normalized confidence
- review queue is regenerated cleanly

## Question quality
- verify class is harder to “answer from memory” on current/source-bound items
- at least the worst false-premise items are reclassified or rewritten
- calibration keeps its strongest discriminators while dropping avoidable alias/key friction

## Measurement
- calibration remains 5-model discriminatory
- Family B verify_trigger_rate improves
- over-answering on verify items decreases
- bridge report remains interpretable after scorer fixes

---

## Required outputs from the sprint

1. branch name + latest SHA used
2. JSON patch file for Family B reviewed items
3. JSON patch file for calibration reviewed items
4. minimal code diff for scorer/export fixes
5. updated tests
6. clean run artifacts from new 5-model sweep:
   - `run_summary.json`
   - `calibration_item_audit.csv`
   - `family_b_item_audit.csv`
   - `bridge_report_all_models.json`
   - `audit_review_queue.csv`
7. short change log:
   - items rewritten
   - items reclassified
   - items removed
   - scoring fixes applied

---

## Final guardrails

- Do not spend orchestrator context on long prose.
- Use frontier API reasoning, not long agent monologues.
- Preserve notebook lineage.
- Preserve current discriminative signal unless an item is clearly invalid.
- Fix the technical reporting bugs first, then rewrite questions, then run the full 5-model sweep.
