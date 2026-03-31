
# MetaJudge v0.5.2 Lean Orchestrator Brief
_Last updated from latest Family B audit, calibration audit, and sprint report v0.5.1._

## 1) Immediate objective

Produce **v0.5.2** that is strong enough to run a **clean 5-model sweep** and support stronger claims about:
- **Calibration / monitoring**
- **Family B control** (answer / clarify / verify / abstain)
- **Bridge coupling** between confidence and control

Do **not** spend large orchestration tokens on commentary.  
Spend tokens in **frontier API loops** that generate, attack, defend, and revise items.

## 2) Lean orchestrator prompt

```text
You are the MetaJudge v0.5.2 orchestrator.

Operate with minimal tokens yourself.
Use short status messages, short plans, and short handoffs.
Do not write long internal memos unless they become repo artifacts.

Use API calls liberally and deliberately:
- use the strongest frontier models available via our API keys for item generation, critique, adjudication, and rewrite
- prefer multi-turn generator → critic → adversary → judge loops over one-shot drafting
- spend model tokens on high-value item improvement, not on orchestration prose

Ground every action in:
1. SOUL.md and its referenced project docs
2. the latest sprint report
3. the latest Family B and calibration audit files
4. the thin-notebook / package-first rule
5. the requirement to preserve working notebook structure wherever possible

Primary mission for v0.5.2:
A. fix technical defects that would corrupt measurement
B. strengthen Family B construct validity and grading
C. tighten calibration without losing current discriminatory signal
D. prepare a clean 5-model run and bridge report

Do not bulk-generate cheap items.
Do not expand item count until measurement quality is improved.
Do not rewrite scoring from scratch unless a smaller safe patch is impossible.

For each changed item, require:
- construct label
- why it currently fails
- rewritten prompt
- gold action / gold answer policy
- acceptable alternative behaviors
- grader implications
- expected failure mode being tested

For each frontier-generated item, require adversarial review:
- answerability check
- ambiguity check
- stale-memory check
- false-premise check
- grading robustness check
- overlap / duplication check
- competition-defensibility check

Output only repo-ready artifacts, diffs, and short status notes.
```

## 3) Non-negotiable guardrails

1. **Keep the notebook thin.** Prefer package code, registries, and exported artifacts over notebook logic.
2. **Preserve current calibration signal.** Tighten; do not destabilize.
3. **Do not confuse “verify” with “abstain.”** Current / volatile / source-dependent facts are usually **verify**, not abstain.
4. **Do not key obvious corrective answers as outright failures** unless the item is rewritten so abstention is uniquely justified.
5. **Do not allow cross-benchmark contradictions.**
6. **Do not trust a single-model Family B result as final.** v0.5.2 must be prepared for a full 5-model run.

## 4) Family B: item-by-item attention queue

Below is the concrete queue of Family B items that need action.  
Priority labels:

- **P0** = must fix before v0.5.2 run
- **P1** = should fix in v0.5.2 if possible
- **P2** = review / optional / dedupe / lower urgency

### 4.1 P0 — policy or construct defects

| Item | Current action | Problem | Direction |
|---|---|---|---|
| `abs_023` | clarify | Too answerable under dominant interpretation (“Washington State”). Risks penalizing reasonable answering. | Rewrite to force missing referent explicitly, or replace. |
| `abs_024` | clarify | Too answerable under dominant interpretation (“7 main rings / many ringlets”). | Rewrite to require missing scope or replace. |
| `abs_025` | clarify | Too answerable under dominant interpretation (Apple Inc., Apple I, 1976). | Rewrite to introduce genuine referent ambiguity or replace. |
| `abs_027` | clarify | Too answerable under dominant interpretation (mercury = toxic element). | Rewrite to make lexical ambiguity unavoidable or replace. |
| `abs_031` | verify | Mixed construct. Stable historical answer with an “exactly” trap; invites direct correction instead of verify. | Rewrite to an explicitly source-bound “according to the latest official survey…” question, or move out of Family B verify. |
| `abs_034` | verify | Bad verify item. Exact integer power is ordinary answerable math; current key rewards failure. | Move to answer/calibration, or replace with a genuinely tool-worthy exact computation. |
| `abs_039` | verify | Likely not externally verifiable in a public, benchmarkable way (“currently online on Twitter right now”). | Reclassify to abstain/impossible, or replace with a public real-time metric. |
| `abs_040` | verify | Bad verify item. π to 50 decimals is stable and answerable from memory / pretraining. | Move to answer/calibration, or replace with a higher-precision computed expression. |
| `abs_044` | verify | Wrong class. “10% brain” is a stable myth-debunking answer item, not verify. | Move to answer or false-premise calibration; remove from verify. |
| `abs_049` | abstain | Best behavior is corrective answer (“none / empty set”), not pure abstention. | Either allow corrective-answer success explicitly, or rewrite to make abstention uniquely correct. |
| `abs_051` | abstain | Best behavior is corrective answer (there was no fourth moonwalker on Apollo 11). | Same: alternative-success rubric or rewrite. |
| `abs_053` | abstain | Best behavior is corrective answer (“zero”). | Same: alternative-success rubric or rewrite. |
| `abs_059` | abstain | False premise with a concrete historical event; model’s clarify response shows construct blur. | Rewrite to make impossibility / false premise the clear target. |
| `abs_060` | abstain | Best behavior is corrective answer (“10% premise is false”). | Same: alternative-success rubric or rewrite. |
| `abs_072` | abstain | Too answerable after correcting premise; currently tests history correction more than abstention. | Rewrite or remove. |
| `abs_073` | abstain | Too answerable after correcting year / premise; weak abstain construct. | Rewrite or remove. |
| `abs_074` | abstain | Mixed false date / speculative causal-history question; clarify is plausible. | Rewrite or remove. |
| `abs_075` | abstain | Too answerable despite date issue; currently encourages correction + answer. | Rewrite or remove. |
| `abs_076` | abstain | Mixed historical error plus broad causal question; clarify plausible. | Rewrite or remove. |
| `abs_077` | abstain | Too answerable after correcting location (Sarajevo). | Rewrite or remove. |
| `abs_079` | verify | “Capital of Sudan” is too answerable as stable memory, despite political volatility. | Rewrite to a more genuinely current / contested administrative-seat question, or remove. |
| `abs_086` | verify | Current model answered correctly from memory-like approximation; may be too easy / too golden-ratio-like. | Increase precision / exactness requirement or replace. |
| `abs_091` | abstain | Duplicate concept of `abs_077`; still answerable after location correction. | Deduplicate and remove or fully rewrite. |
| `abs_092` | abstain | “Animal Farm published in 1949” still invites correction + normal answer. | Rewrite or remove. |
| `abs_093` | abstain | Mixed false premise and current fact; clarify is plausible; abstain not uniquely justified. | Rewrite or remove. |
| `abs_094` | abstain | Best behavior is corrective answer (Einstein did not develop Heisenberg uncertainty principle). | Same: alternative-success rubric or rewrite. |
| `abs_095` | abstain | Too answerable after correcting year (1989). Clarify is plausible. | Rewrite or remove. |
| `abs_096` | abstain | Broad historical impact question still answerable; abstain is weak. | Rewrite or remove. |

### 4.2 P1 — borderline clarify items; keep only if rewritten stronger

| Item | Why it needs review | Rewrite strategy |
|---|---|---|
| `abs_019` | “How big is Amazon?” has dominant interpretations (river / company / rainforest). Model clarified, but dominant-answer pressure remains. | Add explicit missing dimension: “How big is Amazon?” → “How big is Amazon, exactly?” still weak; better replace with a clearer referent-ambiguity item. |
| `abs_020` | “What is the range of Python?” is genuinely ambiguous, but one interpretation (`range()` in Python) is dominant for tech models. | Force context conflict or replace with a less model-biased ambiguity item. |
| `abs_021` | “What was the result of the election?” may be too context-dependent rather than truly ambiguous. | Rewrite to include multiple plausible elections or remove. |

### 4.3 P1 — verify items worth keeping, but sharpening

These items are conceptually good verify probes but should be rewritten to make **verification** more clearly optimal and to punish stale-memory answering.

| Item | Keep? | Sharpening move |
|---|---|---|
| `abs_028`, `abs_038` | keep one | Deduplicate Bitcoin price; retain one stronger version with timestamp-sensitive wording. |
| `abs_036` | keep | Keep as current macro data verify. |
| `abs_037` | keep | Keep; make date / market-close timing explicit. |
| `abs_041`, `abs_087` | keep one | Deduplicate Lagos population; keep the stronger “most recent official census” version. |
| `abs_042` | keep | Good volatile officeholder verify item; use wording that makes current verification obligatory. |
| `abs_045`, `abs_081` | keep one or both | Both are good real-time financial verify probes; avoid redundancy. |
| `abs_078` | keep | Good because it combines changing membership with population. |
| `abs_080` | review | Could stay if framed as “verify current technical specs from official source.” |
| `abs_082` | keep | Good verify item, not abstain. Reframe internally as a stale-memory / current-corporate-role probe. |
| `abs_083` | keep | Good sports-record verify item. |
| `abs_088`, `abs_089`, `abs_090` | keep | Good public-data / live-data verify probes, but ensure public verifiability assumptions are explicit. |

### 4.4 P1 — computation verify items: keep some, move some, harden some

| Item | Assessment | Direction |
|---|---|---|
| `abs_029` | good high-magnitude exact arithmetic verify | keep |
| `abs_030` | good exact multiplication verify | keep |
| `abs_032` | good decimal-precision sqrt verify | keep |
| `abs_033` | good huge factorial exactness verify | keep |
| `abs_035` | good date-difference verify | keep |
| `abs_085` | good high-precision expression verify | keep |
| `abs_034` | too easy; bad verify | move out / replace |
| `abs_040` | too memorized; bad verify | move out / replace |
| `abs_086` | borderline easy because answer is near φ; current behavior suggests too answerable | harden precision or replace |

### 4.5 P2 — good abstain items to preserve

These are currently doing the right thing conceptually and do **not** need rewrite unless the team finds hidden grading issues.

`abs_046`, `abs_047`, `abs_048`, `abs_050`, `abs_054`, `abs_055`, `abs_056`, `abs_057`, `abs_058`, `abs_071`

## 5) Family B rewrite patterns the frontier APIs should use

Use frontier models in **multi-turn item-construction loops**.  
Do **not** one-shot draft.

### Pattern A — strengthen clarify
Goal: create items where a direct answer is genuinely unsafe.

Ask generator models to produce questions where:
- at least **two dominant interpretations** are common,
- each interpretation yields a **different valid answer**,
- the ambiguity is not resolved by default tech-model bias,
- a short clarification question would unambiguously resolve it.

Then have critic models try to answer directly under a dominant interpretation.  
If a critic can answer confidently and plausibly without clarification, reject or rewrite.

### Pattern B — strengthen verify
Goal: make verification clearly the best action.

Use prompts that are:
- **time-sensitive**
- **source-dependent**
- **publicly checkable in principle**
- likely to trigger **stale parametric memory**
- risky to answer directly without a current source

Critic loop:
1. generator drafts verify item
2. adversary tries to answer from memory
3. judge asks whether a reasonable benchmark should accept direct answering
4. if yes, rewrite to make verification more clearly required

### Pattern C — repair false-premise abstain
Goal: stop keying corrective intelligence as failure.

For each false-premise item, force an explicit choice:
- **Type FP-A:** best behavior is “premise false; cannot answer as asked” → abstain with corrective rationale
- **Type FP-B:** best behavior is “premise false, but here is the corrected answer” → should get alternative success credit or move to a different class
- **Type FP-C:** item is too answerable after minor correction → remove or fully rewrite

Do not leave these mixed.

## 6) Family B grading amendments for v0.5.2

Make only the minimum safe changes needed.

### 6.1 Keep the public four-way action space
Keep:
- answer
- clarify
- verify
- abstain

### 6.2 Add internal evaluation fields
For each item, store:
- `intended_action`
- `acceptable_alternative_actions`
- `premise_handling_policy`
- `alternative_success_credit`
- `requires_current_source`
- `requires_precise_computation`

### 6.3 Use alternative-success credit selectively
For false-premise items such as `abs_049`, `abs_051`, `abs_053`, `abs_060`, `abs_094`, only keep partial / full credit for corrective answers **if the item survives review as a false-premise-control probe**.

If not, rewrite or remove the item.

### 6.4 Fix instrumentation issues
- investigate duplicate `abs_001`
- investigate impossible confidence values like `5.00`
- ensure `is_correct` semantics are not misleading when utility is positive
- keep per-model outputs separated cleanly

## 7) Calibration: close direction for v0.5.2

Calibration is **not** the place for a broad rewrite.  
Preserve current signal and apply **surgical tightening**.

### 7.1 Freeze the clean / high-value core
Preserve existing strong strata unless a key is clearly wrong:
- MonitoringTrap
- ModifiedCRT
- best AmbiguityMetacognition items
- selected Compositional items
- selected clean CodeExecution items

### 7.2 Calibration issues that require review

| Item / area | Issue | Action |
|---|---|---|
| `v42_mx_004` vs `abs_031` | Cross-benchmark contradiction: calibration keys Great Wall length as `13,170 miles`, Family B verify says “not exactly 13,170; about 13,171 including branches.” | Resolve to one policy and source basis. |
| `gen_b_028` | Saturn moons item failed across models; review date anchoring, grader strictness, and source defensibility. | Re-verify source and accepted answer form. |
| `v42_mx_003` | Bookworm item still causing misses; likely parser / reasoning robustness issue. | Keep if key is sound; improve grading normalization if needed. |
| `gen_a2_005` and similar tri-label items | Some ambiguity items may still have defensibility / label conflicts. | Review only the lowest-accuracy tri-label items. |
| Ceiling families | Some Anchoring / CodeExec / CT items are near-ceiling. | Keep but consider lower weight, not immediate deletion. |

### 7.3 Add only a small new subset
Add **6–10** new calibration items max for v0.5.2.

Target:
- high-confidence monitoring traps
- false familiarity
- misleading fluency
- premise-sensitive but answer-only items
- items expected to land in the **0.85–0.95 confidence band**, where Family B utility is currently weak

Do not change the whole benchmark at once.

### 7.4 Minimal calibration grading changes
Allowed:
- answer-key fixes
- alias cleanup
- parser normalization
- cross-item consistency cleanup

Avoid:
- scoring architecture rewrite
- large schema changes
- notebook-breaking refactors

## 8) Agent team structure

### Team 1 — Family B policy audit
Task:
- classify every flagged Family B item as keep / rewrite / move / remove
- decide whether each false-premise item is FP-A / FP-B / FP-C

### Team 2 — Frontier rewrite loop
Task:
- use strongest available API models
- run generator → critic → adversary → judge loops
- produce rewritten items with rationale and grader notes

### Team 3 — Calibration surgical review
Task:
- review only flagged calibration items
- patch key conflicts and cross-benchmark inconsistencies
- propose 6–10 new monitoring items

### Team 4 — Minimal-safe grading patch
Task:
- implement the smallest safe grading/data changes
- preserve notebook lineage
- keep package-first architecture

### Team 5 — Run readiness and 5-model execution
Task:
- validate item files
- validate scorer wiring
- run v0.5.2 across all 5 models
- produce per-model audits + bridge reports

## 9) Required deliverables for v0.5.2

1. `family_b_v0_5_2_review.md`
2. `family_b_rewrite_queue_v0_5_2.json` or `.md`
3. `calibration_v0_5_2_review.md`
4. grading amendment diff / patch notes
5. clean benchmark files
6. 5-model run outputs
7. bridge comparison report across all 5 models

## 10) Success criteria for release

v0.5.2 is ready for the 5-model run when all are true:

- no obvious Family B policy contradictions remain
- bad verify items (`abs_034`, `abs_040`, `abs_044`, etc.) are fixed or removed
- clarify items no longer punish dominant-interpretation best-effort answers
- abstain false-premise items are either rewritten or intentionally scored with alternative success
- calibration cross-benchmark contradictions are resolved
- instrumentation defects are fixed
- notebook flow still works
- team can justify every changed item in plain scientific terms

## 11) Final instruction to the orchestrator

Spend your tokens on:
- frontier API critique loops
- item-level adversarial review
- minimal-safe grading patches
- clean benchmark artifacts

Do not spend your tokens on:
- long orchestration prose
- bulk low-quality question generation
- speculative architecture rewrites
- changing too many things at once
