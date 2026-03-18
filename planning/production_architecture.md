# Production Architecture — MetaJudge-AGI

**Date:** 2026-03-18  
**Baseline:** Verified evidence notebook (all 5 cells pass)  
**Status:** Plan for implementation sprint

---

## 1. Top-Level Wrapper Architecture

### Verified pattern

The Kaggle SDK requires exactly one `@kbench.task` selected via `%choose` for leaderboard scoring. The evidence notebook confirmed that a wrapper task can:

- Call subtask `.evaluate()` internally
- Aggregate results across subtasks
- Return a single `float` composite score

### Production wrapper

```python
@kbench.task(name="metacognition_suite")
def metacognition_suite(llm) -> float:
    """
    Top-level benchmark. Evaluates all 5 metacognition families,
    computes weighted composite score. This is the only task
    exported via %choose.
    """
    subscores = {}

    # A: Calibration (single-turn)
    with kbench.client.enable_cache():
        cal_runs = metacog_calibration.evaluate(
            llm=[llm], evaluation_data=CAL_DF, n_jobs=3, max_attempts=1
        )
    subscores["calibration"] = aggregate_calibration(cal_runs.as_dataframe())

    # B: Abstention (single-turn)
    with kbench.client.enable_cache():
        abs_runs = metacog_abstention.evaluate(
            llm=[llm], evaluation_data=ABS_DF, n_jobs=3, max_attempts=1
        )
    subscores["abstention"] = aggregate_abstention(abs_runs.as_dataframe())

    # C: Self-Correction (multi-turn)
    with kbench.client.enable_cache():
        cor_runs = metacog_self_correction.evaluate(
            llm=[llm], evaluation_data=COR_DF, n_jobs=3, max_attempts=1
        )
    subscores["self_correction"] = aggregate_self_correction(cor_runs.as_dataframe())

    # D: Source Awareness (single-turn)
    with kbench.client.enable_cache():
        src_runs = metacog_source_awareness.evaluate(
            llm=[llm], evaluation_data=SRC_DF, n_jobs=3, max_attempts=1
        )
    subscores["source_awareness"] = aggregate_source_awareness(src_runs.as_dataframe())

    # E: Strategy Adaptation (multi-turn)
    with kbench.client.enable_cache():
        strat_runs = metacog_strategy.evaluate(
            llm=[llm], evaluation_data=STRAT_DF, n_jobs=3, max_attempts=1
        )
    subscores["strategy_adaptation"] = aggregate_strategy(strat_runs.as_dataframe())

    composite = compute_composite_score(subscores)
    return composite
```

### Key design decisions

1. **Self-contained data.** Each family's DataFrame is defined inside the notebook (or loaded from a bundled JSON/CSV). The wrapper takes only `llm` — no external dataset argument.
2. **Separate `enable_cache()` blocks per family.** Keeps cache behavior explicit and debuggable.
3. **`n_jobs=3` default.** Parallelism within each family. Can be tuned down for quota conservation.
4. **Each subtask returns `float`.** The wrapper reads the `"result"` column from `.as_dataframe()` and feeds it to family-specific aggregation.

---

## 2. Subtask Decomposition & Interface Contracts

### Family A: Confidence Calibration

**Turn structure:** Single-turn  
**Schema:**
```python
@dataclass
class CalibrationResponse:
    answer: str
    confidence: float           # 0.0–1.0
    reason_for_uncertainty: str
    would_verify_if_possible: bool
```

**Task signature:**
```python
@kbench.task(name="metacog_calibration")
def metacog_calibration(llm, prompt: str, gold_answer: str,
                        difficulty: str, example_id: str) -> float:
```

**Inputs (DataFrame columns):**
| Column | Type | Description |
|--------|------|-------------|
| `prompt` | str | The question to answer |
| `gold_answer` | str | Expected correct answer |
| `difficulty` | str | easy / medium / hard / deceptive |
| `example_id` | str | Unique item ID |

**Scoring:** `calibration_aware_score(is_correct, confidence)` — rewards correct+high-confidence, penalizes wrong+high-confidence. Returns `float` in [0, 1].

**Aggregation:** Mean of per-item scores. Diagnostic: Brier score, ECE, overconfidence rate (computed but not part of the returned float).

---

### Family B: Selective Abstention

**Turn structure:** Single-turn  
**Schema:**
```python
@dataclass
class AbstentionResponse:
    decision: str               # "answer" | "ask" | "abstain" | "verify"
    answer: str                 # empty string if abstaining
    confidence: float           # 0.0–1.0
    missing_information: str    # what info is missing (if asking)
    abstention_reason: str      # why abstaining (if abstaining)
```

**Task signature:**
```python
@kbench.task(name="metacog_abstention")
def metacog_abstention(llm, prompt: str, gold_answer: str,
                       answerable: bool, ambiguity_class: str,
                       intended_optimal_action: str,
                       example_id: str) -> float:
```

**Inputs (DataFrame columns):**
| Column | Type | Description |
|--------|------|-------------|
| `prompt` | str | The question |
| `gold_answer` | str or "" | Expected answer (empty if unanswerable) |
| `answerable` | bool | Whether a correct answer exists |
| `ambiguity_class` | str | clear / underspecified / ambiguous / adversarial |
| `intended_optimal_action` | str | answer / ask / abstain / verify |
| `example_id` | str | Unique item ID |

**Scoring:** `decision_utility_single(decision, is_correct, answerable, ambiguity_class, confidence)` using the reward matrix. Returns `float` normalized to [0, 1].

**Aggregation:** Mean of per-item utility scores, rescaled so the theoretical random-policy baseline maps to ~0.0 and perfect policy maps to ~1.0.

---

### Family C: Error Detection & Self-Correction

**Turn structure:** Multi-turn (2 turns)  
**Schemas:**
```python
# Turn 1 reuses CalibrationResponse
@dataclass
class CalibrationResponse:
    answer: str
    confidence: float
    reason_for_uncertainty: str
    would_verify_if_possible: bool

# Turn 2
@dataclass
class SelfCorrectionResponse:
    is_likely_wrong: bool
    suspected_error_type: str   # arithmetic | misread | unsupported_inference | memory_failure | none | other
    revised_answer: str         # empty string if no revision
    revised_confidence: float   # 0.0–1.0
    what_changed: str
```

**Task signature:**
```python
@kbench.task(name="metacog_self_correction")
def metacog_self_correction(llm, prompt: str, gold_answer: str,
                            challenge_type: str, followup_evidence: str,
                            difficulty: str, example_id: str) -> float:
```

**Inputs (DataFrame columns):**
| Column | Type | Description |
|--------|------|-------------|
| `prompt` | str | The initial question |
| `gold_answer` | str | Expected correct answer |
| `challenge_type` | str | generic / contradiction / weak_challenge / inspect |
| `followup_evidence` | str | Evidence or hint for turn 2 |
| `difficulty` | str | easy / medium / hard / deceptive |
| `example_id` | str | Unique item ID |

**Execution flow:**
```python
# Turn 1: model answers
r1 = llm.prompt(initial_prompt, schema=CalibrationResponse)
# Turn 2: model reviews (automatic history from turn 1)
r2 = llm.prompt(correction_prompt, schema=SelfCorrectionResponse)
```

**Scoring:** `correction_efficiency_score(correct_before, correct_after, revised, conf_before, conf_after)`. Returns `float` in [0, 1].

**Aggregation:** Mean of per-item correction efficiency scores.

---

### Family D: Source Awareness

**Turn structure:** Single-turn  
**Schema:**
```python
@dataclass
class SourceAwarenessResponse:
    answer: str
    source_label: str           # prompt | inference | memory | guess | unresolved
    confidence: float           # 0.0–1.0
    supporting_span: str        # quote from prompt if source is "prompt"
```

**Task signature:**
```python
@kbench.task(name="metacog_source_awareness")
def metacog_source_awareness(llm, prompt: str, gold_answer: str,
                             source_type_gold: str, example_id: str) -> float:
```

**Inputs (DataFrame columns):**
| Column | Type | Description |
|--------|------|-------------|
| `prompt` | str | The question (may include a passage) |
| `gold_answer` | str | Expected correct answer |
| `source_type_gold` | str | prompt / inference / memory / guess / unresolved |
| `example_id` | str | Unique item ID |

**Scoring:** `source_awareness_composite(answer_correct, source_label_correct, confidence, gold_source, predicted_source)`. Returns `float` in [0, 1].

**Aggregation:** Mean of per-item composite scores.

---

### Family E: Strategy Adaptation

**Turn structure:** Multi-turn (2 turns)  
**Schema:**
```python
@dataclass
class StrategyResponse:
    chosen_strategy: str        # recall | stepwise | decompose | verify_first | decline
    why_this_strategy: str
    answer: str
    confidence: float           # 0.0–1.0
```

**Task signature:**
```python
@kbench.task(name="metacog_strategy")
def metacog_strategy(llm, prompt: str, gold_answer: str,
                     expected_strategy: str, hint: str,
                     difficulty: str, example_id: str) -> float:
```

**Inputs (DataFrame columns):**
| Column | Type | Description |
|--------|------|-------------|
| `prompt` | str | The problem to solve |
| `gold_answer` | str | Expected correct answer |
| `expected_strategy` | str | The gold-standard best strategy |
| `hint` | str | Feedback hint for turn 2 |
| `difficulty` | str | easy / medium / hard |
| `example_id` | str | Unique item ID |

**Execution flow:**
```python
# Turn 1: model picks strategy and answers
r1 = llm.prompt(strategy_prompt, schema=StrategyResponse)
# Turn 2: feedback + retry (automatic history)
r2 = llm.prompt(feedback_prompt, schema=StrategyResponse)
```

**Scoring:** `strategy_adaptation_composite(strategy_correct, correct_before, correct_after, changed, conf_before, conf_after)`. Returns `float` in [0, 1].

**Aggregation:** Mean of per-item composite scores.

---

## 3. Dataset Plan

### Overall targets

| Family | Items | LLM calls/item | Total calls | Est. cost/model |
|--------|-------|-----------------|-------------|-----------------|
| A: Calibration | 100 | 1 | 100 | ~$2.50 |
| B: Abstention | 80 | 1 | 80 | ~$2.00 |
| C: Self-Correction | 60 | 2 | 120 | ~$3.00 |
| D: Source Awareness | 80 | 1 | 80 | ~$2.00 |
| E: Strategy | 60 | 2 | 120 | ~$3.00 |
| **Total** | **380** | | **500** | **~$12.50** |

At ~$12.50/model run with caching, the $500 quota supports ~40 model runs — enough for development iteration + final multi-model evaluation.

### Difficulty distribution per family

| Difficulty | Fraction | Purpose |
|-----------|----------|---------|
| easy | 20% | Baseline — most models should pass |
| medium | 35% | Standard evaluation items |
| hard | 25% | Discriminates strong from average |
| deceptive | 15% | Anti-gaming (looks easy but isn't) |
| adversarial | 5% | Stress test |

### Dataset authoring approach

1. **Seed from prototype examples** — 10 items exist in `data/prototypes/`. Expand each family.
2. **Calibration items (Family A):** Mix of factual recall (easy), arithmetic (medium), cognitive reflection tests (deceptive), obscure knowledge (hard). Gold answers must be unambiguous.
3. **Abstention items (Family B):** ~40% answerable (baseline), ~30% underspecified, ~20% unknowable, ~10% adversarial. The mix is critical for scoring balance.
4. **Self-Correction items (Family C):** Items where models commonly make specific error types. Challenge types distributed across generic/contradiction/weak_challenge/inspect.
5. **Source Awareness items (Family D):** Mix of passage-based (source=prompt), general knowledge (source=memory), reasoning (source=inference), and unanswerable (source=guess/unresolved).
6. **Strategy items (Family E):** Problems that benefit from specific strategies. Each item tagged with expected best strategy.

### File format

```
data/
├── calibration.csv       # 100 rows
├── abstention.csv        # 80 rows
├── self_correction.csv   # 60 rows
├── source_awareness.csv  # 80 rows
├── strategy.csv          # 60 rows
└── prototypes/
    └── prototype_examples.json  # existing seed data
```

Each CSV has the columns defined in the interface contracts above, plus any hidden metadata columns (not passed to the model).

---

## 4. Scoring Aggregation Plan

### Per-item scoring

Each subtask returns a `float` in [0, 1] for each item. This is stored in the `result` column of `.as_dataframe()`.

### Per-family aggregation

Each family's aggregation function receives the results DataFrame and computes a single family score in [0, 1]:

```python
def aggregate_calibration(df: pd.DataFrame) -> float:
    return float(df["result"].mean())

def aggregate_abstention(df: pd.DataFrame) -> float:
    # Rescale so random baseline ≈ 0, perfect ≈ 1
    raw = float(df["result"].mean())
    return max(0.0, min(1.0, (raw - ABSTENTION_BASELINE) / (1.0 - ABSTENTION_BASELINE)))

# ... similar for each family
```

### Composite score

```python
WEIGHTS = {
    "calibration": 0.25,
    "abstention": 0.20,
    "self_correction": 0.20,
    "source_awareness": 0.15,
    "strategy_adaptation": 0.20,
}

def compute_composite_score(subscores: dict) -> float:
    score = sum(WEIGHTS[k] * subscores[k] for k in WEIGHTS)
    return float(max(0.0, min(1.0, score)))
```

This uses the existing `compute_composite_score()` from `metajudge/scoring/composite_score.py`, which already handles missing subtasks via weight normalization.

### Scoring principles enforcement (Framework §7.3)

1. **Overconfident error hurts a lot** — `calibration_aware_score` penalizes proportional to confidence when wrong.
2. **Appropriate abstention helps but not too much** — Utility capped; abstaining on answerable items incurs opportunity cost.
3. **Revision helps only when it improves** — `correction_efficiency_score` penalizes breaking correct answers.
4. **No single cheap behavior dominates** — 5 families with distinct behaviors; no one strategy optimizes all.

---

## 5. Notebook / Repository Layout

### Repository structure (benchmark content)

```
metajudge-agi/
├── metajudge/                      # Python package (importable)
│   ├── schemas/
│   │   └── response_schemas.py     # → REFACTOR to @dataclass
│   ├── tasks/
│   │   ├── calibration.py          # build_prompt + score_item + @kbench.task
│   │   ├── abstention.py
│   │   ├── self_correction.py
│   │   ├── source_awareness.py
│   │   └── strategy_adaptation.py
│   ├── scoring/
│   │   ├── calibration_metrics.py  # existing — keep
│   │   ├── abstention_metrics.py   # existing — keep
│   │   ├── self_correction_metrics.py
│   │   ├── source_awareness_metrics.py
│   │   ├── strategy_metrics.py
│   │   ├── composite_score.py      # existing — keep
│   │   └── aggregation.py          # NEW: per-family aggregation functions
│   ├── anti_gaming/
│   │   └── perturbations.py        # existing — keep
│   └── utils/
│       └── text.py                 # existing — keep
├── data/
│   ├── calibration.csv
│   ├── abstention.csv
│   ├── self_correction.csv
│   ├── source_awareness.csv
│   ├── strategy.csv
│   └── prototypes/
├── notebooks/
│   ├── metajudge_submission.ipynb  # THE notebook for Kaggle
│   └── metajudge_evidence.ipynb    # verification (done)
├── tests/
│   ├── unit/
│   └── integration/
├── config/
│   └── benchmark_config.yaml
└── planning/
```

### Notebook structure (Kaggle execution glue)

The submission notebook is deliberately thin. It imports from `metajudge/` and defines SDK-specific wrappers:

```
Cell 1: Imports + SDK setup
Cell 2: Load dataset CSVs into DataFrames
Cell 3: Define @dataclass schemas (SDK-native)
Cell 4: Define 5 subtask @kbench.task functions
Cell 5: Define wrapper @kbench.task (metacognition_suite)
Cell 6: Test run on 2-3 items (development sanity check)
Cell 7: %choose metacognition_suite
```

### Separation principle

| Concern | Lives in | Why |
|---------|----------|-----|
| Scoring logic | `metajudge/scoring/` | Testable offline, no SDK dependency |
| Prompt construction | `metajudge/tasks/` | Testable offline |
| Schema definitions | `metajudge/schemas/` | Shared between notebook and tests |
| SDK wrappers (`@kbench.task`) | `notebooks/metajudge_submission.ipynb` | SDK only available in Kaggle |
| Dataset content | `data/*.csv` | Version-controlled, auditable |
| Aggregation | `metajudge/scoring/aggregation.py` | Testable offline |

The notebook copies needed functions inline (or uses `%%writefile` to inject the package). The package remains testable locally without the SDK.

---

## 6. Schema Refactor: Pydantic → Dataclass

### What changes

The current schemas in `response_schemas.py` use Pydantic `BaseModel` with `Field(...)` validators. The SDK `schema=` parameter works with both, but cookbook examples predominantly use `@dataclass`. Dataclasses are simpler and avoid a Pydantic version dependency in the Kaggle environment.

### Migration rules

| Pydantic feature | Dataclass equivalent |
|-----------------|---------------------|
| `Field(..., ge=0.0, le=1.0)` | No built-in validation; enforce via assertion in task |
| `Field(None, ...)` for Optional | `field(default=None)` or just `str` with empty string |
| `Literal[...]` type | `str` (SDK may not enforce Literal; validate in task) |
| `BaseModel` inheritance | `@dataclass` |

### Key constraint

The SDK `schema=` parameter returns a typed object. The task function is responsible for validation (via `assertions.assert_true`), not the schema. This shifts validation from schema-time to task-time, which is fine — we assert in the task body anyway.

### What stays

All scoring modules (`calibration_metrics.py`, etc.) are schema-agnostic — they take primitive types (float, bool, str). No changes needed there.

---

## 7. First Implementation Slice

### Goal: One family end-to-end in the Kaggle notebook

**Family A: Confidence Calibration** — chosen because:
- Single-turn (simplest SDK interaction)
- Scoring logic already complete and tested
- Prototype items exist
- Most directly maps to the verified evidence notebook pattern

### Deliverables for this slice

1. **`metajudge/schemas/response_schemas.py`** — Refactor `CalibrationResponse` to `@dataclass`
2. **`metajudge/tasks/calibration.py`** — Activate the `@kbench.task` wrapper (currently commented out)
3. **`data/calibration.csv`** — 20 items (pilot set: 4 easy, 7 medium, 5 hard, 3 deceptive, 1 adversarial)
4. **`metajudge/scoring/aggregation.py`** — `aggregate_calibration(df) -> float`
5. **`notebooks/metajudge_submission.ipynb`** — Cells 1-3 + Cell 5 (wrapper with calibration only) + Cell 7 (`%choose`)
6. **Tests** — Update `test_schemas.py` for dataclass, add `test_aggregation.py`

### Acceptance criteria

- Notebook runs in Kaggle with 20-item calibration dataset
- Returns a composite float (just calibration weight for now)
- Costs < $1 in quota
- All local tests pass

### Estimated effort: 1 session

---

## 8. Risks, Assumptions, and SDK Constraints

### SDK constraints (verified)

| Constraint | Impact | Mitigation |
|-----------|--------|------------|
| Single `%choose` per notebook | Must use wrapper pattern | Verified working |
| `schema=` returns typed object, not string | Task must handle typed attributes | Simplifies code (no JSON parsing) |
| `llm.prompt()` auto-maintains conversation history | Multi-turn works but history accumulates | Use `chats.new()` for judge calls to isolate |
| `.evaluate()` runs all rows; no early stopping by default | Large datasets = large quota spend | Use `stop_condition` + caching |
| `n_jobs` parallelism is per-evaluate call | Can't parallelize across families | Sequential family execution is fine |

### Assumptions

| Assumption | Confidence | Fallback if wrong |
|-----------|-----------|-------------------|
| `@dataclass` schemas work with `schema=` | HIGH (cookbook confirms) | Revert to Pydantic |
| `.evaluate()` passes DataFrame columns as keyword args to task function | HIGH (starter notebook confirms) | Restructure task signatures |
| Wrapper task can call `.evaluate()` on subtasks defined in the same notebook | HIGH (evidence notebook confirms) | Extract subtasks to separate cells |
| `result` column in `.as_dataframe()` contains task return value | HIGH (starter notebook confirms) | Inspect DataFrame columns on first run |
| Conversation history resets between `.evaluate()` rows | MEDIUM (expected behavior) | Add explicit `chats.new()` per row if not |
| $500 quota is sufficient for 380 items × 3-4 models | MEDIUM (depends on model pricing) | Reduce to 200 items or fewer models |

### Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **Quota exhaustion before submission** | HIGH | MEDIUM | Pilot with 20 items first; use caching aggressively; track spend |
| **Multi-turn history leaks between .evaluate() rows** | MEDIUM | LOW | Verify on first C/E family run; wrap in `chats.new()` if needed |
| **Dataclass fields with `Optional` or `Literal` don't round-trip cleanly** | MEDIUM | LOW | Test in Kaggle on first slice; fall back to plain types (str, float) |
| **Dataset quality insufficient for discriminatory power** | HIGH | MEDIUM | Author carefully; pilot on 2-3 models early; iterate on items that don't discriminate |
| **Scoring weights produce degenerate composite** | MEDIUM | LOW | Validate principles after pilot; tune weights empirically |
| **Judge model usage eats quota** | LOW | LOW | Use judge sparingly (strategy consistency only); most scoring is deterministic |
| **Notebook execution timeout** | MEDIUM | LOW | 380 items × 500ms/call ≈ 3-4 min per model; well within limits |

### Non-risks (resolved by verification)

- SDK import and availability ✓
- Structured output with `schema=` ✓
- Multi-turn with automatic history ✓
- `.evaluate()` batch execution ✓
- `%choose` submission path ✓
- Judge model availability ✓

---

## 9. Implementation Sequence

After the first slice (Calibration end-to-end), the remaining families build incrementally:

| Order | Family | Why this order | New complexity |
|-------|--------|---------------|----------------|
| 1 | A: Calibration | Simplest, scoring done, prototype exists | None — establishes pattern |
| 2 | D: Source Awareness | Single-turn, scoring done | Different schema, source-label evaluation |
| 3 | B: Abstention | Single-turn, scoring done | Decision-theoretic utility, mix of answerable/unanswerable |
| 4 | C: Self-Correction | Multi-turn | Two schemas per task, correction challenge logic |
| 5 | E: Strategy Adaptation | Multi-turn | Strategy matching, feedback loop, judge usage |

Each family follows the same workflow:
1. Refactor schema to `@dataclass`
2. Activate `@kbench.task` in task module
3. Author 60-100 dataset items
4. Write aggregation function
5. Add to wrapper
6. Test locally + test in Kaggle notebook
7. Commit
