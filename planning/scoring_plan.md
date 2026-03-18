# Scoring Plan Rewrite — Calibration Track (V1 to Frontier-Ready)

**Date:** 2026-03-18  
**Scope:** Family A (Confidence Calibration)  
**Purpose:** Final rewrite of the scoring plan so it is mathematically correct, operationally robust, compatible with the current dataset constraints, and scalable from flash-model debugging runs to stronger frontier-model evaluation.

---

## 1. Executive Decision

The core scoring choice remains correct:

- **Keep a Brier-derived per-item score as the official leaderboard metric.**
- **Do not use an LLM judge as the primary scorer.**
- **Upgrade the scoring plan to include a deterministic adjudication layer keyed by `example_id`.**
- **Keep the current calibration dataset construction plan largely intact, but require stronger answer governance and pilot gates.**

The current guide is directionally strong, but it needs four changes before it should be treated as final:

1. **Correct the metric naming.** The proposed function is `1 - (confidence - outcome)^2`, which is **1 minus the per-item Brier loss**, not “1 − Brier².”
2. **Separate scoring from adjudication.** Brier needs a binary correctness label, but correctness must itself be determined by a robust deterministic grader.
3. **Add an answer-key specification.** This is necessary to support non-identical but equivalent answers without turning the benchmark into a fragile string-match exercise.
4. **Add frontier-readiness rules.** The benchmark must be able to scale beyond flash models without immediate ceiling effects.

---

## 2. Official Headline Metric

### 2.1 Per-item score

For each item:

```python
y = 1.0 if is_correct else 0.0
score = 1.0 - (confidence - y) ** 2
```

### 2.2 Official interpretation

This is the benchmark’s **official per-item score**. The benchmark headline score is the mean across all items:

```python
headline_score = mean(score_i for score_i in item_scores)
```

### 2.3 Correct terminology

Use one of these names consistently in the codebase and writeup:

- **Brier-derived per-item score**
- **Affine transform of per-item Brier loss**
- **1 − per-item Brier loss**

Do **not** call it “1 − Brier².” That phrase is mathematically inaccurate.

### 2.4 Why this remains the right choice

This metric remains the correct official choice because it is:

- **strictly proper**
- **bounded in [0, 1]**
- **higher-is-better**
- **per-item computable**
- **SDK compatible**
- **well aligned with calibration as epistemic monitoring**

It also preserves the strongest part of the current guide: a model cannot maximize score through trivial overconfidence, and a constant-confidence hedging strategy is dominated by truthful per-item uncertainty reporting.

---

## 3. Critical Distinction: Scoring vs Correctness Adjudication

The scoring rule is now settled. The real source of benchmark fragility is **not** the Brier formula. It is **how `is_correct` is decided**.

That distinction must be explicit:

- **Scoring rule** answers: how should confidence and correctness combine?
- **Adjudication rule** answers: was the answer correct?

For a calibration benchmark, the adjudication rule matters even more once Brier is used, because a false negative on a high-confidence correct answer is severely punished.

### 3.1 Final policy

- **Official scoring uses deterministic adjudication.**
- **LLM judges are not used in the official scoring loop.**
- **LLM or human review may be used only during dataset authoring, audit, or disputed-item review.**

This preserves reproducibility, avoids hidden evaluator drift, and fits the benchmark’s need for defensible task construction.

---

## 4. Final Adjudication Standard

### 4.1 Required item-level answer spec

For every item, maintain an internal answer key keyed by `example_id` with the following fields:

| Field | Purpose |
|---|---|
| `canonical_answer` | The single preferred gold answer |
| `accepted_aliases` | Deterministic list of equivalent accepted strings |
| `answer_type` | `integer`, `decimal`, `yes_no`, `entity`, `single_word`, etc. |
| `format_instruction` | The expected response format, e.g. `digits_only` |
| `grader_rule` | Which deterministic grading rule to apply |
| `notes` | Author-side justification and edge-case warnings |

### 4.2 Important compatibility decision

The CSV schema does **not** need to change.

Keep:

- `prompt`
- `gold_answer`
- `difficulty`
- `example_id`

Store richer adjudication metadata in a separate deterministic registry, for example:

- `data/calibration_answer_key.json`
- or `data/calibration_answer_key.csv`

with lookup by `example_id`.

This preserves the hard codebase requirements while allowing adjudication to become more robust.

### 4.3 Official grading hierarchy

The grader should apply the following deterministic hierarchy:

1. **Exact normalized canonical match**
2. **Exact normalized alias match**
3. **Type-specific deterministic rule** where predeclared
   - numeric equivalence for numeric items
   - yes/no normalization for binary items
   - controlled entity alias list for named entities
4. **Otherwise incorrect**

No free-form semantic judging in the live evaluation loop.

### 4.4 What this changes operationally

This means the benchmark is no longer hostage to a single fragile `gold_answer` string, while still remaining deterministic and reproducible.

It also means you can safely import or adapt public question sets that have semantically stable but format-variable answers, as long as you normalize them into this answer-key system during dataset construction.

---

## 5. Minimal Code Changes Required

The earlier guide understates the implementation work. The final scoring plan requires more than replacing three lines.

### 5.1 Must change now

| File / area | Change |
|---|---|
| `metajudge/scoring/calibration_metrics.py` | Replace current function with Brier-derived per-item score |
| `metajudge/tasks/calibration.py` | Route correctness adjudication through a deterministic grader, not direct raw string equality only |
| scorer utilities | Add answer-key lookup by `example_id` |
| tests | Add adjudication tests and score tests |

### 5.2 Can remain unchanged in spirit

| File / area | Status |
|---|---|
| composite score logic | Conceptually unchanged |
| aggregate diagnostics | Keep, but expand |
| CSV task schema | Keep as-is |

### 5.3 New helper layer to add

Implement a deterministic grader such as:

```python
def adjudicate_answer(example_id: str, raw_answer: str) -> bool:
    spec = ANSWER_KEY[example_id]
    # canonical / alias / type-specific deterministic checks
    ...
```

Then:

```python
is_correct = adjudicate_answer(example_id, parsed.answer)
score = calibration_aware_score(is_correct, confidence)
```

This is the cleanest way to make scoring robust without changing the external benchmark schema.

---

## 6. Aggregate Diagnostic Suite

The existing diagnostic suite is good, but the final rewrite should make the structure explicit.

### 6.1 Official leaderboard metric

- **Mean Brier-derived per-item score**

### 6.2 Required diagnostics for every run

- **Aggregate Brier score**
- **Expected Calibration Error (ECE)**
- **Overconfidence rate**
- **Accuracy by confidence bucket / reliability diagram data**
- **AUROC**

### 6.3 Recommended additional diagnostics

These are not required for V1 launch but are highly desirable before frontier-model comparison:

- **Per-difficulty Brier score**
- **Per-difficulty overconfidence rate**
- **Per-domain Brier score**
- **Risk-weighted overconfidence analysis** using `risk_class` and `damage_sensitive`
- **Coverage-style summary** if abstention or defer-to-unknown is introduced later

### 6.4 Interpretation policy

Use the metrics this way:

- **Headline score** = overall calibration performance
- **Brier** = canonical calibration reference
- **ECE** = systematic miscalibration pattern
- **AUROC** = discrimination between correct and incorrect answers
- **Overconfidence rate** = most important failure mode metric
- **Bucket plots** = human-readable diagnostic evidence

---

## 7. Dataset Implications

The current dataset construction plan remains broadly compatible, but the final scoring plan imposes three concrete requirements.

### 7.1 Requirement 1: stronger canonicalization

Every imported or authored item must be curated into a format that supports deterministic adjudication.

That means:

- one stable canonical answer
- short answer span
- explicit accepted aliases if needed
- clear answer type
- prompt wording that pushes the model toward the intended form

### 7.2 Requirement 2: keep the current difficulty mix, but add pilot gates

The planned distribution remains acceptable:

- `easy`: 20
- `medium`: 35
- `hard`: 25
- `deceptive`: 15
- `adversarial`: 5

But this mix should now be treated as a **starting design**, not an immutable law.

Pilot runs should trigger review if any of the following occur:

- `deceptive` or `adversarial` items cause broad floor effects
- a large fraction of low scores are due to answer-format failures rather than real calibration failure
- `hard` items are effectively random or ambiguous
- `easy` items are not actually easy across the tested model band

### 7.3 Requirement 3: build for stronger models now

Even if V1 is debugged on flash models, the item bank should be authored with stronger models in mind.

That means:

- avoid well-known memorized traps when possible
- rewrite or perturb classic deceptive items rather than copying them verbatim
- reserve some harder items that are unlikely to saturate immediately
- maintain an unpublished reserve pool for later swaps

---

## 8. Frontier-Readiness Policy

The benchmark does not need to start at frontier scale, but the scoring plan should be explicitly designed so scaling up does not force another redesign.

### 8.1 What will break first as models improve

The scoring rule itself will not break. The likely failure points are:

1. **ceiling effects** on easy and medium items
2. **memorization of classic deceptive items**
3. **format sensitivity** becoming the main error source rather than epistemic error
4. **insufficient discrimination among strong models**

### 8.2 Final policy for scaling to stronger models

Adopt a two-layer item-bank strategy:

#### Stable anchor set

A fixed subset that remains constant across runs to preserve comparability over time.

#### Rotating challenge set

A reserved pool of harder, less saturated items that can be swapped in when stronger models compress the score range.

### 8.3 Retirement and refresh triggers

An item should be reviewed for retirement or rotation if, across strong-model pilot runs:

- accuracy is near ceiling
- confidence is near ceiling
- it no longer contributes to discrimination
- it behaves like a format test rather than a knowledge-or-monitoring test

### 8.4 What to log during stronger-model pilots

For each item, store:

- correctness rate
- mean confidence
- mean score
- overconfidence frequency
- mismatch reason category
  - true knowledge error
  - deceptive trap success/failure
  - answer-format failure
  - alias miss
  - ambiguity or item defect

This is the minimum information needed to know whether an item should remain in the frontier-capable pool.

---

## 9. LLM-as-Judge Policy

This needs to be explicit because it is a natural temptation once answers become more language-like.

### 9.1 Official stance

- **No LLM judge in the primary scoring loop**

### 9.2 Allowed uses

- dataset authoring support
- alias discovery during offline curation
- dispute analysis on flagged items
- rubric validation against humans during benchmark development

### 9.3 Why this is the right choice

For a calibration benchmark, using an LLM judge in the official scoring loop introduces a second model’s uncertainty into the benchmark itself. That weakens reproducibility and makes the task construction less defensible.

If a free-form semantic judge is required for many items, the dataset is drifting away from a calibration benchmark optimized for robust correctness labels and toward a broader QA benchmark.

---

## 10. Stepwise Implementation Plan

### Phase 1 — immediate scoring fix

1. Replace the old linear `calibration_aware_score()` with the Brier-derived version.
2. Correct all prose and comments from “1 − Brier²” to “1 − per-item Brier loss” or equivalent.
3. Add unit tests proving proper behavior on correct/incorrect confidence edge cases.

### Phase 2 — deterministic adjudication layer

1. Create `calibration_answer_key` keyed by `example_id`.
2. Add `canonical_answer`, `accepted_aliases`, `answer_type`, `format_instruction`, `grader_rule`, `notes`.
3. Implement deterministic adjudication function.
4. Add unit tests for alias, numeric, and yes/no grading.

### Phase 3 — pilot validation on flash models

1. Run the 20-item pilot.
2. Audit all misses by category.
3. Separate calibration failures from adjudication failures.
4. Revise prompts, aliases, and defective items before full-set authoring.

### Phase 4 — full V1 benchmark

1. Freeze the first stable 100-item benchmark.
2. Report headline score plus full diagnostics.
3. Include explicit writeup on anti-gaming and deterministic adjudication.

### Phase 5 — stronger-model scaling

1. Run the benchmark on stronger models.
2. Measure ceiling compression and item-level discrimination.
3. Refresh only the rotating challenge subset as needed.
4. Preserve anchor items for comparability.

---

## 11. Final Recommendation

The final recommendation is:

- **Keep the Brier-derived scoring rule.**
- **Treat deterministic correctness adjudication as first-class infrastructure, not an afterthought.**
- **Do not use an LLM judge as the official grader.**
- **Keep the current dataset plan, but require answer-key metadata and pilot-based item review.**
- **Build the item bank now in a way that can scale to frontier models without changing the scoring philosophy.**

That gives you a calibration benchmark that is:

- mathematically principled
- operationally reproducible
- robust to answer-form variance
- compatible with the current project structure
- scalable from flash-model debugging to stronger-model evaluation

---

## 12. Core References

- Brier, G. W. (1950). *Verification of forecasts expressed in terms of probability.*
- Gneiting, T., & Raftery, A. E. (2007). *Strictly proper scoring rules, prediction, and estimation.*
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). *On calibration of modern neural networks.*
- Kumar, A., Liang, P. S., & Ma, T. (2019). *Verified uncertainty calibration.*
- Xiong, M., et al. (2024). *Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs.*

