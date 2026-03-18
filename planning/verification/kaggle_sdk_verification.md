# Kaggle SDK Verification Report — MetaJudge-AGI

**Date:** 2026-03-18
**Sprint:** API Verification
**Status:** COMPLETE — All critical unknowns resolved

---

## 1. Notebook Environment Summary

### SDK
- **Package:** `kaggle_benchmarks` (aliased as `kbench`)
- **License:** Apache 2.0
- **Source:** https://github.com/Kaggle/kaggle-benchmarks (branch: `ci`)
- **Import pattern:** `import kaggle_benchmarks as kbench`
- **Alternative imports:** `from kaggle_benchmarks import assertions, chats, judge_llm, llm, llms, system, task`

### Default Model
- **Access:** `kbench.llm` — pre-loaded default model
- **Default observed:** `google/gemini-2.0-flash`
- **Model call method:** `llm.prompt(text, schema=None, image=None, tools=None)`

### Model Enumeration
- **Pattern:** `kbench.llms["model/name"]` (dictionary-style access)
- **Examples:** `kbench.llms["google/gemini-2.5-flash"]`, `kbench.llms["meta/llama-3.1-70b"]`
- **Core set includes:** Claude 3.5/3.7/Opus 4, Gemini, GPT-4o-mini/o1, Grok-2, Gemma, Llama, and more
- **Judge model:** `kbench.judge_llm` — separate pre-loaded judge

### Competition Context
- **Competition:** Measuring Progress Toward AGI — Cognitive Abilities
- **Deadline:** April 16, 2026 (29 days from now)
- **Submission format:** Kaggle Writeup (≤1,500 words) + attached Kaggle Benchmark
- **Evaluation:** 50% dataset quality, 20% writeup, 15% discriminatory power, 15% community votes
- **Metacognition track prize:** 2 × $10,000 + eligible for $25,000 grand prize
- **Quota:** $50/day, $500 total for benchmark runs

---

## 2. Capability Matrix

| # | Capability | Status | Confidence | Evidence Source |
|---|-----------|--------|------------|----------------|
| 1 | `import kaggle_benchmarks as kbench` | **PASS** | HIGH | Starter notebook Cell 1, Cookbook, all examples |
| 2 | `kbench.llm` default model | **PASS** | HIGH | Starter notebook Cell 2, Cookbook |
| 3 | Model enumeration (`kbench.llms[...]`) | **PASS** | HIGH | Cookbook dataset evaluation recipe, docs model list |
| 4 | Structured outputs (`schema=` parameter) | **PASS** | HIGH | Cookbook structured output notebook: int, bool, dict, dataclass, Pydantic all work |
| 5 | `@kbench.task(name=...)` decorator | **PASS** | HIGH | Starter notebook Cell 2, all Cookbook examples |
| 6 | `.run(llm=..., **kwargs)` | **PASS** | HIGH | Starter notebook Cell 2, Cookbook |
| 7 | `kbench.assertions.assert_true()` | **PASS** | HIGH | Starter notebook Cell 2, Cookbook |
| 8 | `kbench.assertions.assert_contains_regex()` | **PASS** | HIGH | Cookbook check_capital example |
| 9 | `kbench.assertions.assert_equal()` | **PASS** | HIGH | Structured output notebook Cells 2-5 |
| 10 | `kbench.assertions.assert_fail()` | **PASS** | HIGH | Cookbook critique example |
| 11 | Custom assertions (`@assertion_handler()`) | **PASS** | HIGH | Cookbook custom assertions recipe |
| 12 | `.evaluate()` dataset evaluation | **PASS** | HIGH | Starter notebook Cell 3, Cookbook dataset recipe |
| 13 | `runs.as_dataframe()` | **PASS** | HIGH | Starter notebook Cell 3 |
| 14 | Multi-turn (automatic history) | **PASS** | HIGH | Conversations notebook: llm.prompt() maintains history across calls |
| 15 | Isolated conversations (`chats.new()`) | **PASS** | HIGH | Conversations notebook: with chats.new(): creates clean slate |
| 16 | Multi-agent conversations | **PASS** | HIGH | Conversations notebook (20 Questions), Cookbook dungeon adventure |
| 17 | Judge helper (`assess_response_with_judge`) | **PASS** | HIGH | Cookbook haiku/critique recipes with full examples |
| 18 | Judge LLM (`kbench.judge_llm`) | **PASS** | HIGH | Cookbook, Conversations notebook |
| 19 | Custom judge prompt/schema | **PASS** | HIGH | Cookbook StoryCritique example |
| 20 | `%choose task_name` export | **PASS** | HIGH | Starter notebook Cell 5, Cookbook |
| 21 | Return types (bool, float, int, tuple) | **PASS** | HIGH | Cookbook return types recipe |
| 22 | Tool use (`tools=[...]`) | **PASS** | MEDIUM | Cookbook recipe (marked "experimental") |
| 23 | Python code execution | **PASS** | MEDIUM | Cookbook script_runner recipe |
| 24 | Image/multimodal support | **PASS** | MEDIUM | Cookbook images recipe |
| 25 | Caching (`kbench.client.enable_cache()`) | **PASS** | HIGH | Starter notebook Cell 3 |
| 26 | Parallel execution (`n_jobs`) | **PASS** | HIGH | Starter notebook Cell 3 |

**Summary: 26/26 capabilities PASS. No blockers identified.**

---

## 3. Evidence Log

### E-001: Imports
- **Cell:** Starter notebook Cell 1
- **Result:** `import kaggle_benchmarks as kbench` works. Also: `from kaggle_benchmarks import assertions, chats, judge_llm, llm, llms, system, task`
- **Unblocks:** All downstream work

### E-002: Default LLM
- **Cell:** Starter notebook Cell 2
- **Result:** `kbench.llm` available, used as `llm.prompt("text")`
- **Observed model:** `google/gemini-2.0-flash`
- **Unblocks:** All task implementations

### E-003: Structured Output
- **Cell:** Structured output notebook Cells 2-6
- **Result:** `llm.prompt(text, schema=X)` works with:
  - `schema=int` → returns `int`
  - `schema=bool` → returns `bool`
  - `schema={"key": type}` → returns Pydantic-like object
  - `schema=MyDataclass` → returns dataclass instance
  - `schema=MyPydanticModel` → returns Pydantic instance
- **Key detail:** Schema-enforced output returns the *typed object*, not a string
- **Unblocks:** All five task families. Our CalibrationResponse, AbstentionResponse, etc. can be passed directly as `schema=` parameter.

### E-004: @kbench.task Decorator
- **Cell:** Starter notebook Cell 2
- **Result:** `@kbench.task(name="solve_riddle")` works. Task function signature: `def task_fn(llm, **params) -> return_type`
- **Key detail:** First parameter must be `llm`. Additional parameters map to dataset columns in `.evaluate()`.
- **Unblocks:** Task registration for all five families

### E-005: Task Execution (.run)
- **Cell:** Starter notebook Cell 2
- **Result:** `solve_riddle.run(llm=kbench.llm, riddle=..., answer=...)` works
- **Unblocks:** Single-item testing

### E-006: Dataset Evaluation (.evaluate)
- **Cell:** Starter notebook Cell 3
- **Result:** `solve_riddle.evaluate(llm=[kbench.llm], evaluation_data=df, n_jobs=3, stop_condition=..., max_attempts=1)` works
- **Key detail:** Returns runs object with `.as_dataframe()` method. DataFrame columns accessible via `result` column.
- **Pattern:** Define a scoring task that calls `.evaluate()` on a sub-task and returns aggregate metric
- **Unblocks:** Batch evaluation over 500+ task items

### E-007: Multi-Turn Interaction
- **Cell:** Conversations notebook
- **Result:** `llm.prompt()` called multiple times on the same `llm` object automatically preserves conversation history
- **Key detail:** This is NOT message-list-based. Just call `llm.prompt()` repeatedly and it remembers.
- **Example:** Turn 1: `llm.prompt(rules)`, Turn 2: `llm.prompt(answer)` — model sees full history
- **Unblocks:** Self-correction (Task C) and Strategy Adaptation (Task E) — BOTH viable

### E-008: Isolated Conversations
- **Cell:** Conversations notebook
- **Result:** `with chats.new():` creates isolated context. Judge calls inside don't leak to main conversation.
- **Unblocks:** Judge-model evaluation can run alongside main task without contamination

### E-009: Judge Helper
- **Cell:** Cookbook haiku and critique examples
- **Result:** `kbench.assertions.assess_response_with_judge(criteria=[...], response_text=..., judge_llm=...)` works
- **Supports:** Custom prompt function via `prompt_fn=`, custom output schema via `output_schema=`
- **Returns:** Assessment object with `.results` list of `{passed, criterion, reason}`
- **Unblocks:** Limited judge usage for strategy-explanation matching and abstention-reason quality checks

### E-010: Export Mechanism
- **Cell:** Starter notebook Cell 5
- **Result:** `%choose batch_riddle_solver` — notebook magic in the final cell
- **Key detail:** Currently only supports a single task per notebook for leaderboard
- **Design implication:** Our benchmark must have a single top-level scoring task that wraps sub-tasks
- **Unblocks:** Submission pipeline

### E-011: Return Types
- **Cell:** Cookbook
- **Result:** Tasks can return `None` (pass/fail on assertions), `bool`, `float`, `int`, `tuple[int,int]` (count), `tuple[float,float]` (value + confidence interval), or `dict`
- **Design implication:** Our composite score should return `float`. Sub-tasks can return `dict` for detailed metrics.
- **Unblocks:** Scoring architecture

### E-012: Caching & Parallelism
- **Cell:** Starter notebook Cell 3
- **Result:** `with kbench.client.enable_cache():` avoids re-running identical queries. `n_jobs=3` runs examples in parallel.
- **Design implication:** Critical for running 500+ items within quota limits
- **Unblocks:** Efficient evaluation at scale

---

## 4. Blocking vs Non-Blocking Unknowns

### All Previously-Critical Unknowns: RESOLVED

| ID | Unknown | Resolution | Status |
|----|---------|------------|--------|
| V-001 | SDK API surface | Fully documented via cookbook + starter + examples | **RESOLVED** |
| V-002 | Export mechanism | `%choose task_name` in final cell | **RESOLVED** |
| V-003 | Model availability | Core set documented; `kbench.llms[...]` for enumeration | **RESOLVED** |
| V-004 | Multi-turn support | Automatic history on `llm.prompt()` calls | **RESOLVED** |
| V-005 | Judge model API | `assess_response_with_judge()` with custom prompt/schema | **RESOLVED** |
| V-006 | Structured output | `schema=` parameter accepts int/bool/dict/dataclass/Pydantic | **RESOLVED** |

### Remaining Non-Blocking Unknowns

| ID | Unknown | Impact | Mitigation |
|----|---------|--------|------------|
| V-007 | Competition deadline | April 16, 2026 (29 days) | Known — timeline is tight but feasible |
| V-008 | Scoring weight tuning | Quality concern, not blocker | Pilot evaluation in Phase 7 |
| V-009 | Dataset size vs quota | $500 total quota, 500+ items × multiple models | Use caching, n_jobs parallelism, pilot on small set first |
| V-013 | Notebook runtime limits | May need subset evaluation | Design for configurable subset size |
| V-015 | Reproducibility | Model nondeterminism | Document, use seed where possible |

### New Constraint Identified

**SINGLE TASK PER NOTEBOOK:** The `%choose` mechanism only supports one task per notebook for leaderboard. This means our architecture must be:
- One top-level `@kbench.task` that wraps all five sub-benchmarks
- Sub-tasks called via `.evaluate()` inside the top-level task
- Top-level task returns the composite `float` score

This is architecturally important but not blocking — it just means we need a wrapper pattern.

---

## 5. Recommended Benchmark-Scope Decision

### **Path 1: Full Original Plan Remains Viable** ✅

**Justification:**

Every capability our benchmark needs is confirmed available:

1. **Structured outputs** — `schema=` parameter directly accepts our Pydantic schemas (CalibrationResponse, AbstentionResponse, etc.). Models return typed objects, not strings. This is *better* than what we planned — no JSON parsing needed.

2. **Multi-turn interaction** — Automatic conversation history means self-correction and strategy-adaptation tasks work naturally. Call `llm.prompt()` for turn 1, then `llm.prompt()` again for turn 2, and the model sees both turns.

3. **Judge model** — `assess_response_with_judge()` is available with custom prompts and custom schemas, exactly as Framework §13 specifies for limited rubric checks.

4. **Dataset evaluation** — `.evaluate()` runs our task over DataFrame rows with parallel execution and caching. This handles the 500-1500 item evaluation efficiently.

5. **Assertions** — `assert_true`, `assert_equal`, `assert_contains_regex`, `assert_fail`, and custom assertions via `@assertion_handler()`.

6. **Export** — `%choose` works but is limited to one task. Solvable with a wrapper task.

**All five sub-benchmarks are fully implementable as designed:**
- A. Confidence Calibration — single-turn, structured output, deterministic scoring
- B. Selective Abstention — single-turn, structured output, utility matrix scoring
- C. Error Detection & Self-Correction — multi-turn (automatic history), structured output both turns
- D. Source Awareness — single-turn, structured output, deterministic scoring
- E. Strategy Adaptation — multi-turn (automatic history), structured output both turns

### Design Adaptations Required (Minor)

1. **Schema format:** Use `dataclass` or `Pydantic` models as `schema=` parameter instead of JSON prompting + manual parsing. This is an *upgrade* from the notebook sketch approach.

2. **Architecture:** Wrap all five sub-benchmarks in a single top-level `@kbench.task` that calls sub-task `.evaluate()` methods and returns composite `float`.

3. **Judge usage:** Use `assess_response_with_judge()` with custom criteria for strategy-explanation consistency checks and abstention-reason quality — exactly as Framework §13 recommends.

4. **Multi-turn pattern for Task C (Self-Correction):**
   ```python
   # Turn 1: Initial answer
   response1 = llm.prompt(initial_prompt, schema=CalibrationResponse)
   # Turn 2: Correction challenge (model sees turn 1 automatically)
   response2 = llm.prompt(correction_prompt, schema=SelfCorrectionResponse)
   ```

5. **Multi-turn pattern for Task E (Strategy Adaptation):**
   ```python
   # Turn 1: Initial strategy + answer
   response1 = llm.prompt(strategy_prompt, schema=StrategyAdaptationResponse)
   # Turn 2: Feedback + retry (model sees turn 1 automatically)
   response2 = llm.prompt(feedback_prompt, schema=StrategyAdaptationResponse)
   ```

---

## 6. Immediate Next Coding Steps

### Priority 1: Update repository schemas to use SDK patterns (Day 1)

- Convert all `MetaResponse` / family-specific schemas to `@dataclass` format (better SDK compatibility than Pydantic, based on cookbook examples)
- Add `schema=` parameter usage to all task modules
- Remove JSON parsing code (no longer needed)

### Priority 2: Build the top-level wrapper task (Day 1-2)

```python
@kbench.task(name="metacognition_behavioral_suite")
def metacognition_suite(llm, df) -> float:
    with kbench.client.enable_cache():
        cal_runs = calibration_task.evaluate(llm=[llm], evaluation_data=cal_df, n_jobs=3)
        abs_runs = abstention_task.evaluate(llm=[llm], evaluation_data=abs_df, n_jobs=3)
        # ... etc for all 5 families
    return compute_composite_score(...)
```

### Priority 3: Implement per-family @kbench.task functions (Days 2-4)

Each family becomes a task with proper `schema=` usage:
```python
@kbench.task(name="metacog_calibration")
def metacog_calibration(llm, prompt: str, gold_answer: str, ...) -> dict:
    response = llm.prompt(prompt, schema=CalibrationResponse)
    score = score_calibration_item(response, gold_answer)
    kbench.assertions.assert_true(0.0 <= response.confidence <= 1.0, ...)
    return score
```

### Priority 4: Begin dataset authoring (Days 2-7)

Start with calibration items (simplest to author and validate).

### Priority 5: Kaggle notebook draft (Days 3-5)

Create first-pass notebook that imports metajudge, runs prototype data, and tests `%choose`.

### Priority 6: Pilot on 2-3 models (Days 7-10)

Use `kbench.llms[...]` to run across multiple models and verify discriminatory power.

---

## Appendix: Key SDK Code Patterns for Implementation

### Structured Output
```python
from dataclasses import dataclass

@dataclass
class CalibrationResponse:
    answer: str
    confidence: float
    reason_for_uncertainty: str
    would_verify_if_possible: bool

response = llm.prompt("Your question here", schema=CalibrationResponse)
# response.confidence is a float, response.answer is a str — no parsing needed
```

### Multi-Turn Self-Correction
```python
@kbench.task(name="metacog_self_correction")
def self_correction_task(llm, prompt, challenge, gold_answer, ...):
    # Turn 1 — model answers
    r1 = llm.prompt(f"Answer this: {prompt}", schema=CalibrationResponse)
    
    # Turn 2 — model sees turn 1 automatically, gets challenge
    r2 = llm.prompt(f"{challenge}\nRevise if needed.", schema=SelfCorrectionResponse)
    
    # Score both turns
    return score_correction(r1, r2, gold_answer)
```

### Isolated Judge Evaluation
```python
with chats.new():
    assessment = kbench.assertions.assess_response_with_judge(
        criteria=["Strategy explanation matches chosen strategy"],
        response_text=response.why_this_strategy,
        judge_llm=kbench.judge_llm,
    )
```

### Dataset Evaluation with Caching
```python
with kbench.client.enable_cache():
    runs = my_task.evaluate(
        llm=[kbench.llm],
        evaluation_data=df,
        n_jobs=3,
        max_attempts=1,
    )
eval_df = runs.as_dataframe()
```

### Export
```python
# Final cell of notebook:
%choose metacognition_behavioral_suite
```
