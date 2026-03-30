# Calibration Dataset Construction Plan for Kaggle “Measuring Progress Toward AGI” — Metacognition Track

**Date:** 2026-03-18  
**Scope:** Family A / confidence calibration only  
**Target artifact:** `data/calibration.csv`  
**Objective:** maximize **dataset quality & task construction** under the Kaggle rubric while staying fully compatible with the current code path, schema, and revised calibration scoring plan.

---

## 1) Executive recommendation

Build the V1 benchmark as a **hybrid static short-answer calibration set**:

1. **Backbone factual layer** from **SimpleQA** and **SimpleQA Verified**
2. **Deception layer** from **TruthfulQA-inspired misconception items**, rewritten into exact-match form
3. **Calibration-specific inspiration layer** from **GRACE**, used mainly for difficulty shaping and validation philosophy rather than direct row import
4. **Small authored adversarial layer** created in-house and validated empirically against at least two public/open models before Kaggle submission

This remains the best fit because there is **no single mature public metacognition dataset** that naturally satisfies all of the current hard constraints:
- exact string matching only
- short canonical gold answers
- five fixed difficulty labels
- broad domain coverage
- strong penalties for confident errors
- no dependence on current events or open-ended grading

The revised scoring plan strengthens this recommendation rather than changing it. Because the headline score is now a **proper calibration score** based on per-item Brier-style scoring, the benchmark should prioritize:
- **unambiguous ground truth**
- **clean canonical answers**
- **enough items per bucket for stable calibration diagnostics**
- **deceptive/adversarial items that induce genuine overconfidence rather than annotation noise**

So the correct design principle is still: optimize for **defensibility, static ground truth, domain breadth, and discriminative calibration behavior** rather than trying to force a more complex academic benchmark into an incompatible CSV schema.

---

## 2) Non-negotiable technical constraints carried forward from the wishlist

This plan **does not depart from** the hard requirements in `dataset_wishlist.md`.

### Required row schema
Each row must provide:

- `prompt`
- `gold_answer`
- `difficulty` ∈ {`easy`, `medium`, `hard`, `deceptive`, `adversarial`}
- `example_id`

Recommended retained analysis metadata outside the submission CSV:

- `item_family`
- `evaluation_axis = monitoring`
- `risk_class`
- `damage_sensitive`
- `source_dataset`
- `rewrite_status`
- `accepted_aliases_internal`

### Exact-match constraint
Because scoring uses normalized exact string equality only, every item must obey these authoring rules:

- gold answer should be **1–5 tokens**
- one **canonical spelling only** in the final CSV
- no punctuation dependence
- no symbols unless unavoidable
- numeric answers should be **digits**
- prompt should explicitly request **bare answer only**
- avoid any item with multiple equally natural renderings unless the prompt can be rewritten to force one rendering

### Important clarification after the scoring review
The final submission CSV should still contain **one canonical `gold_answer` only**.  
However, because the scoring function now penalizes confident wrong answers much more sharply, the build process should maintain an **internal alias ledger** for every item where alternate renderings are plausible.

That means:
- **competition artifact:** one canonical `gold_answer`
- **internal QC artifact:** accepted aliases, spelling variants, and rewrite rationale

This preserves the hard schema while reducing the risk that item ambiguity masquerades as model miscalibration.

---

## 3) Scoring alignment and why it matters for dataset construction

The updated scoring plan uses a **strictly proper confidence score** of the form:

`1 - (confidence - outcome)^2`

where `outcome = 1` for correct and `0` for incorrect.

This has three direct dataset implications.

### 3.1 Gold-answer ambiguity matters more than before
Under the previous linear score, mislabeled or ambiguous items were harmful but less catastrophic. Under the revised score, a model can be heavily penalized for a high-confidence answer that is semantically right but string-mismatched. So dataset quality must now be treated as part of scoring validity.

### 3.2 The deceptive and adversarial tiers must expose overconfidence, not annotation noise
A deceptive item is useful only if:
- its correct answer is genuinely unambiguous
- common wrong answers are psychologically plausible
- failure arises from misconception or overreach rather than wording defects

### 3.3 Calibration diagnostics require enough data per slice
The headline leaderboard score can be computed on any item count, but secondary diagnostics such as reliability buckets and ECE become noisy on very small subsets. The dataset should therefore be large enough, and balanced enough, to make post-hoc calibration analysis interpretable.

**Conclusion:** the scoring revision does **not** require a new dataset philosophy, but it does require stricter item hygiene and more explicit pilot validation.

---

## 4) Competition alignment

Kaggle’s judging criteria put **Dataset quality & task construction at 50%**, explicitly emphasizing defensible data, unambiguous correct answers, statistical sufficiency, and task quality. This plan is designed around that rubric first.

The competition framework also emphasizes held-out cognitive tasks, human-comparable evaluation, and under-measured cognitive abilities such as **metacognition**. This supports building a benchmark that is narrow, rigorous, and auditable rather than broad but weakly grounded.

The scoring revision strengthens this alignment because proper scoring means the benchmark now genuinely rewards **honest uncertainty tracking** rather than just a mixture of accuracy and aggressive confidence.

---

## 5) Source strategy: what to pull, and how to use it

## 5.1 Tier A — direct import candidates

### A. SimpleQA
**Use:** primary source for `easy`, `medium`, and part of `hard` factual items  
**Why:** short fact-seeking questions, strong fit to exact grading, broad topic coverage  
**How to use:**
- filter for rows whose answer can be converted to a single canonical string
- exclude any item with punctuation, aliases, unit ambiguity, or time-sensitive facts
- rewrite prompts to request **numeric-only** or **single-token** answers where needed
- record any rejected near-miss items in the provenance sheet so selection decisions are auditable

**Role in final set:** factual backbone and baseline calibration anchor

### B. SimpleQA Verified
**Use:** preferred replacement or audit layer for SimpleQA-derived rows when overlap exists  
**Why:** improves label reliability, reduces redundancy and noise  
**How to use:**
- prioritize Verified rows for high-stakes `easy` and `medium` buckets
- use as a source of cleaner, more defensible gold answers
- if both SimpleQA and SimpleQA Verified cover the same topic, prefer Verified

**Role in final set:** label quality upgrade and provenance-strengthening source

### C. TruthfulQA
**Use:** source of **deceptive misconception seeds**, not direct final rows  
**Why:** built specifically to trigger human-like falsehoods and misconceptions  
**How to use:**
- do **not** import free-form rows unchanged
- convert selected items to exact-match form with one canonical answer
- keep only items where the gold answer can be reduced to a short string like `no`, `0`, `black`, `venus`
- exclude items whose grading depends on nuanced free-response truthfulness
- document the intended misconception for every retained item

**Role in final set:** primary seed source for `deceptive`

---

## 5.2 Tier B — design inspiration and validation references

### D. GRACE
**Use:** calibration benchmark reference for **difficulty shaping and validation**, not as the main row source  
**Why:** GRACE is explicitly about calibration and introduces clue-structured difficulty plus calibration-sensitive evaluation  
**How to use:**
- use GRACE to justify the idea that calibration should be measured across **graduated uncertainty**
- borrow the principle that the benchmark should distinguish early confident correctness from confident guessing
- optionally adapt a small number of clue-based items into one-shot short-answer prompts if they survive exact-match constraints

**Role in final set:** academic justification for calibration-specific construction

### E. MetaMedQA
**Use:** reference only  
**Why:** genuine metacognition benchmark with abstention/confidence design, but domain-specific and multiple-choice  
**How to use:** cite as evidence that explicit metacognitive task design exists, while noting it is **not** a fit for this general-domain V1 CSV

---

## 5.3 Tier C — in-house authored rows

These are required because public datasets alone will not satisfy the full wishlist.

### F. Authored arithmetic / numeric items
**Use:** `easy`, `medium`, `hard`  
**Why:** easiest class to make exact-match-safe and contamination-resistant  
**Examples:** square roots, percentages, ratios, date arithmetic, exact counts from static world knowledge  
**Rule:** prompt must force one numeric output only

### G. Authored semantic-illusion / misconception variants
**Use:** `deceptive`  
**Why:** canonical literature items are likely memorized; modified variants are needed  
**Method:** preserve the cognitive trap but alter surface form, story frame, or object names while keeping one exact answer

### H. Authored adversarial items
**Use:** `adversarial`  
**Why:** needed for shelf life and overconfidence stress testing  
**Method:** use static, verifiable but low-frequency facts or near-unknowable exact-count items with one correct answer, then pre-test for confabulation tendency

---

## 6) Recommended 100-item composition

This preserves the wishlist distribution and makes each difficulty tier do distinct work.

| Difficulty | Count | Primary source mix | Purpose |
|---|---:|---|---|
| easy | 20 | SimpleQA / SimpleQA Verified + authored arithmetic | baseline confident correctness |
| medium | 35 | SimpleQA Verified + authored numeric / science / geography | spread confidence over moderately hard known items |
| hard | 25 | harder verified factual items + obscure but static authored facts | separate strong from average models |
| deceptive | 15 | TruthfulQA-inspired + modified CRT / semantic illusions | expose confident false beliefs |
| adversarial | 5 | fully authored, static, validation-tested | stress-test confabulation |

### Recommended family distribution
Use **7 families** plus a small cross-domain buffer:

- arithmetic / numeric
- science
- geography
- history
- language / linguistics
- misconception / semantic illusion
- numeric count / estimation with exact answer
- cross-domain adversarial buffer

This still matches the wishlist’s concern that too few domains measures knowledge specialization, while too many domains create noise.

### Pilot guardrail on bucket sizes
Do not reduce any bucket below a size that makes the post-hoc diagnostics meaningless.

Recommended minimums:
- `easy`: 15+
- `medium`: 25+
- `hard`: 20+
- `deceptive`: 10+
- `adversarial`: 5+

If pilot results show that the deceptive/adversarial buckets are too punishing or too noisy, adjust **item quality first**, not just counts.

---

## 7) Construction pipeline

## Phase 1 — candidate harvest
Create a candidate pool of **250–350 items**:
- 80–100 from SimpleQA / SimpleQA Verified
- 40–60 misconception candidates from TruthfulQA
- 80–100 authored arithmetic / numeric / static fact rows
- 20–30 authored deceptive and adversarial rows
- optional 10–20 GRACE-inspired candidates

## Phase 2 — exact-match canonicalization filter
Reject any candidate with:
- multiple valid surface forms
- punctuation-sensitive gold answer
- unit ambiguity
- synonym ambiguity
- culturally dependent naming
- recent/current knowledge dependence

Each retained item gets:
- canonical `gold_answer`
- rewritten prompt requesting bare answer only
- source provenance tag
- initial difficulty hypothesis
- rationale note
- internal alias list if needed

## Phase 3 — ambiguity and contamination review
For every deceptive/adversarial item:
- document plausible wrong answer
- record why the item should induce overconfidence
- flag whether the item is a direct literature item or modified variant
- verify that the gold answer can be rendered in one stable form

For every factual item:
- attach one authoritative verification note in an internal provenance sheet
- document rejected aliases or alternate phrasings if they were considered

## Phase 4 — pre-pilot screening
Run candidates through at least **two accessible models** before Kaggle:
- one stronger frontier-style API or open proxy if available
- one smaller/open model

Use pre-pilot results to estimate:
- item accuracy
- confidence spread
- overconfidence frequency
- ambiguity flags
- prompt-following failure rate

**Cull rules:**
- remove items that almost all models miss with low confidence and no informative spread
- remove items that almost all models answer correctly with identical confidence unless needed for the `easy` anchor
- remove items where semantically correct responses frequently miss exact-match because of predictable formatting alternatives
- flag deceptive items that do not actually induce overconfidence

## Phase 5 — bucket assignment
Assign final difficulty labels using **observed behavior**, not just intuition.

Suggested practical definition:
- `easy`: high correctness, high confidence, low disagreement
- `medium`: moderate correctness, moderate confidence spread
- `hard`: lower correctness among weaker models, some success among stronger models, uncertainty present
- `deceptive`: wrong answers common with moderate/high confidence and a small set of recurrent traps
- `adversarial`: deliberately stress confabulation or brittle certainty, but still static and objectively verifiable

## Phase 6 — 20-item Kaggle pilot
Construct the competition pilot to sample all five labels.

Recommended pilot distribution:
- 4 easy
- 7 medium
- 5 hard
- 3 deceptive
- 1 adversarial

Pilot goals:
- validate score spread under the revised scoring rule
- check that deceptive/adversarial items do not create floor effects
- confirm that exact-match failures are not dominating the signal
- inspect reliability curves and wrong-at-high-confidence patterns

## Phase 7 — final 100-item freeze
After pilot review:
- relabel if needed
- replace ambiguous rows
- confirm provenance completeness
- freeze `example_id`
- export final `calibration.csv`
- export support docs

---

## 8) Hard rules for item writing and rewriting

### 8.1 Prompt format rule
Every prompt should end with a forcing instruction such as:

> “Answer with a single word or number only.”

Use stronger wording where needed:
- “Give digits only.”
- “Give the country name only.”
- “Answer yes or no only.”

### 8.2 Gold-answer form rule
Use **bare numeric gold answers** whenever possible.  
Example: prefer `0.05` over `$0.05`.

### 8.3 Difficulty validation rule
Do **not** rely only on author intuition.  
Use:
1. source prior
2. two-model pre-pilot
3. Kaggle pilot confirmation

### 8.4 Deception robustness rule
Do not use classic CRT items unchanged as the backbone of the deceptive tier.  
Use:
- modified CRT templates
- misconception variants
- semantic illusion rewrites
- pilot validation for actual overconfidence effects

### 8.5 Shelf-life rule
Preserve a small authored adversarial tier and keep provenance metadata so later versions can rotate saturated items out without changing the benchmark design philosophy.

### 8.6 Canonicalization and alias rule
For every item, the authoring team must explicitly answer:
- What exact string is the intended `gold_answer`?
- What near-miss strings are plausible from a competent model?
- Can the prompt be rewritten to collapse those variants into one canonical output?
- If not, should the item be dropped?

This rule is mandatory under the revised scoring regime.

---

## 9) Deliverables to build alongside `calibration.csv`

To maximize defensibility for the 50% dataset/task-construction score, ship five supporting artifacts:

1. **`data/calibration.csv`** — final benchmark
2. **`data/calibration_provenance.csv`** — one row per item with source, verification note, author, rewrite status
3. **`data/calibration_alias_audit.csv`** — internal-only ledger of acceptable variants considered during authoring and why each was collapsed or rejected
4. **`docs/calibration_authoring_policy.md`** — canonical answer rules, exclusion rules, prompt format rules
5. **`docs/calibration_pilot_report.md`** — pilot results, relabeling decisions, rejected-item summary, calibration diagnostics

These are what make the dataset auditable.

---

## 10) What not to do

- Do not use long-form QA datasets requiring semantic grading
- Do not use current-events questions
- Do not rely on GPT-judge style grading for V1
- Do not let deceptive and adversarial tiers collapse into trivia difficulty
- Do not change `normalize_text` for V1 unless the pilot proves a systemic failure
- Do not import multiple-choice-only metacognition datasets directly and pretend they are equivalent to your short-answer task
- Do not keep ambiguous items just because they are theoretically elegant or literature-famous

---

## 11) Recommended academic references

These four remain the strongest justification set for the current plan:

1. **Wei et al. (2024), _Measuring short-form factuality in large language models_**  
   Justifies using short, fact-seeking, objectively gradable questions as the backbone.

2. **Lin, Hilton, and Evans (2022), _TruthfulQA: Measuring How Models Mimic Human Falsehoods_**  
   Justifies a deceptive tier based on misconceptions and human-like false beliefs.

3. **Sung et al. (2025), _GRACE: A Granular Benchmark for Evaluating Model Calibration against Human Calibration_**  
   Justifies calibration-specific benchmark construction and the need to distinguish confident correctness from confident guessing.

4. **Kadavath et al. (2022), _Language Models (Mostly) Know What They Know_**  
   Justifies calibration/self-evaluation as a meaningful metacognitive signal rather than mere task accuracy.

Useful secondary references:

5. **Geng et al. (2024), _A Survey of Confidence Estimation and Calibration in Large Language Models_**  
   Supports metric choices and clarifies current calibration methodology.

6. **Wang et al. (2025), _Decoupling Metacognition from Cognition: A Framework for Quantifying Metacognitive Ability in LLMs_**  
   Helps frame the limits of pure accuracy-based evaluation and explains why the benchmark should isolate monitoring behavior.

7. **Haas et al. (2025), _SimpleQA Verified: A Reliable Factuality Benchmark to Measure Parametric Knowledge_**  
   Supports preferring cleaned, de-duplicated, and audited factual items over raw benchmark reuse.

8. **Brier (1950), _Verification of forecasts expressed in terms of probability_**  
   Foundational justification for using proper scoring rules and for preferring a Brier-style headline score.

---

## 12) Final recommendation

For V1, the benchmark should be presented as:

> **a static, exact-match, calibration-sensitive metacognition benchmark built from a hybrid of public factual QA, public misconception QA, and empirically validated authored items, scored with a proper per-item calibration rule**

That framing is honest, technically compatible with the codebase, aligned with the competition rubric, and defensible in a writeup.

The best immediate next move is:

1. harvest candidate pools from SimpleQA / SimpleQA Verified / TruthfulQA
2. canonicalize into exact-match-safe forms
3. author 20–30 deceptive/adversarial variants in-house
4. build the alias/provenance audit alongside authoring rather than after the fact
5. run the two-model pre-pilot
6. finalize the 20-item Kaggle pilot
7. only then scale to the full 100-item benchmark

---

## Reference list

- Jason Wei et al. **Measuring short-form factuality in large language models.** 2024.
- Stephanie Lin, Jacob Hilton, Owain Evans. **TruthfulQA: Measuring How Models Mimic Human Falsehoods.** ACL 2022.
- Yoo Yeon Sung et al. **GRACE: A Granular Benchmark for Evaluating Model Calibration against Human Calibration.** ACL 2025.
- Saurav Kadavath et al. **Language Models (Mostly) Know What They Know.** 2022.
- Jiahui Geng et al. **A Survey of Confidence Estimation and Calibration in Large Language Models.** NAACL 2024.
- Guoqing Wang et al. **Decoupling Metacognition from Cognition: A Framework for Quantifying Metacognitive Ability in LLMs.** AAAI 2025.
- Lukas Haas et al. **SimpleQA Verified: A Reliable Factuality Benchmark to Measure Parametric Knowledge.** 2025.
- Glenn W. Brier. **Verification of forecasts expressed in terms of probability.** 1950.
