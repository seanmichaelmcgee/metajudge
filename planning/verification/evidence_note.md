# Evidence Note — Minimal Kaggle Notebook Test

**Date:** 2026-03-18  
**Status:** AWAITING EXECUTION (notebook prepared, requires user's Kaggle session)

---

## Questions & Expected Answers

### 1. Did this run in a real Kaggle competition notebook?

**Expected:** YES — the notebook is created via the competition's Code tab → "+ New Notebook", which links it to the competition environment where `kaggle_benchmarks` is available as a pre-installed package.

**Evidence to confirm:** Notebook URL contains `/competitions/kaggle-measuring-agi/`, SDK imports succeed, `kbench.llm` returns a model name.

**Actual:** _(fill after execution)_

---

### 2. Did the wrapper-task pattern work?

**Expected:** YES — Cell 4 defines `metacognition_suite` as a `@kbench.task(name="metacognition_suite")` that:
- Calls `mini_calibration.evaluate()` on a 2-row DataFrame internally
- Aggregates sub-task scores via `.mean()`
- Returns a single `float` composite score
- Cell 5 selects it via `%choose metacognition_suite`

This proves the production pattern: one top-level task wraps N sub-benchmark families, each run via `.evaluate()`, and returns the composite score that the leaderboard uses.

**Evidence to confirm:** Cell 4 prints sub-results list + composite score without errors. Cell 5's `%choose` accepts the task name.

**Actual:** _(fill after execution)_

---

### 3. Did anything unexpected appear in execution?

**Expected items to watch for:**
- `schema=` dataclass: Does the model reliably return typed objects? (Confirmed via cookbook, but live run may reveal edge cases)
- `results_df["result"]` column: Is this the correct column name for task return values? (Confirmed from starter notebook's `.as_dataframe()`)
- `%choose` behavior: Does it produce visible output, or just silently register?
- Quota usage: How much did 6 LLM calls cost?

**Actual:** _(fill after execution)_

---

### 4. Is there any remaining submission-path blocker?

**Expected:** NO — if all 5 cells succeed, the entire submission pipeline is proven:
1. Import SDK ✓
2. Define subtask with structured output ✓
3. Run subtask on dataset via `.evaluate()` ✓
4. Wrap in top-level task returning composite float ✓
5. Select via `%choose` for leaderboard ✓

**Known non-blockers (documented, mitigated):**
- Single task per notebook → wrapper pattern handles this
- $500 total quota → caching + small pilot first
- Notebook runtime limits → configurable subset size

**Actual:** _(fill after execution)_

---

## Decision

**If all cells pass:** Stop verification. Move to implementation sprint:
1. Repository refactor to SDK-native `@dataclass` schemas
2. Top-level `metacognition_suite` wrapper task
3. Per-family `@kbench.task` functions (A–E)
4. Dataset authoring (calibration first)
5. Scoring integration

**If any cell fails:** Document the specific error. Determine if it's:
- A code bug (fix and retry)
- An SDK limitation (assess severity, check workaround)
- A fundamental architecture problem (reassess Path 1)
