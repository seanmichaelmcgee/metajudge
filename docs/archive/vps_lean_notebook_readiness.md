# Lean Notebook Readiness Assessment

## Verdict: GO_LEAN

The lean notebook is ready for submission use with grading_v2 registry-driven adjudication.

## What Was Patched

### Cell 0 (Markdown Header)
- Updated dataset version: V4.1 → V4.2
- Updated scoring logic reference: adjudication.py → grading_v2.py

### Cell 1 (Imports)
- Removed: `adjudicate`, `set_answer_key` from `metajudge.scoring.adjudication`
- Added: `grade_item`, `load_registry` from `metajudge.scoring.grading_v2`
- Kept: `brier_item_score` (still from adjudication.py — it's a pure math function)

### Cell 3 (Data Loading)
- Added: Registry loading (`load_registry()`) with Kaggle/local path detection
- Added: Registry count assertion (102 entries)
- Kept: ANSWER_KEY construction for backward compatibility

### Cell 4 (Self-Tests)
- Replaced: 9 `adjudicate()`-based assertions
- Added: 17 `grade_item()`-based assertions covering all 7 active grader rules
- Added: Gold self-adjudication loop (102/102 PASS)

### Cell 5 (Task Definition)
- Replaced: `adjudicate(item_id, response.answer, gold_answer)` → `grade_item(item_id, response.answer, REGISTRY)["correct"]`

### Cell 8 (New — I/O Contract)
- Added: Structured `run_summary.json` output with benchmark version, item count, grading engine, and rule list

## What the Lean Notebook Now Does

1. **10 cells** (was 9): markdown header + 8 code cells + 1 new I/O contract cell + %choose
2. **Grading**: Registry-driven via `grading_v2.grade_item()` (8 supported rules, 7 active)
3. **Dataset**: V4.2 (102 items, 7 IOED replacements)
4. **Self-tests**: 17 per-rule assertions + 102/102 gold self-adjudication
5. **Output**: `run_summary.json` with benchmark metadata

## Test Results

- `python -m pytest tests/ -v`: **212/212 PASS**
- Gold self-adjudication: **102/102 PASS**
- Per-rule self-tests: **17/17 PASS** (7 active rules)

## Remaining Gaps

- **yes_no rule**: Supported in grading_v2.py but no items in V4.2 use it (0/102). Not a gap — the code is tested in `test_grading_v2.py::TestYesNo`.
- **Family B integration**: Not in scope for this branch. Tracked separately.
- **Diagnostics cell (C1-C5 analysis)**: Deferred to a later phase.
