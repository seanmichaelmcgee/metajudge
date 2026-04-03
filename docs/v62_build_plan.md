# MetaJudge v6.2 — Build Plan

## Context

v6.1 runs revealed three categories of issues:

1. **try/except catches fatal errors silently.** Quota exhaustion (`PermissionDeniedError: 403`) is caught as a per-item failure. Once quota is gone, every subsequent item fails too — producing a partial score (58/105) that looks like the model performed badly when it actually ran out of money. 47 items silently dropped.

2. **Markdown audit reports are incomplete.** Missing question text on flagged items. Abstention has no action-error section. C1/C2 reports are sparse — only damage items shown, no corrections or stubborn_wrong. Judges need to see the questions to evaluate grading quality.

3. **Cost data missing for non-Flash models.** run.json glob pattern fails on model slugs with emoji (`🤖`) and `@` characters. Costs display in Kaggle UI but not in the markdown report.

## Workstreams

### WS1: Error handling — distinguish recoverable vs fatal

**Problem:** `except Exception` catches everything equally. Quota errors cascade — once one fires, all remaining items fail too, burning through the parallel job queue with 403s.

**Fix:** Re-raise fatal errors, only catch per-item recoverable errors.

```python
try:
    response = llm.prompt(prompt, schema=CalibrationResponse)
    # ... grading ...
    return {...}
except Exception as e:
    err_str = str(e).lower()
    if "403" in err_str or "quota" in err_str or "permission" in err_str:
        raise  # Fatal — quota gone, crash immediately
    print(f"  ITEM FAILED: {item_id}: {type(e).__name__}: {str(e)[:120]}")
    return None
```

**Apply to:** All 4 helper tasks (calibration, abstention, sc_c1/c2).

**Alternative considered:** Remove try/except entirely and let runs fail. Rejected because genuine per-item failures (LengthFinishReasonError, parsing errors) are real and should be handled gracefully. The fix is to distinguish error types, not to remove the safety net.

### WS2: Markdown report improvements

#### 2a. Add question text to all flagged items (all 4 notebooks)

Currently wrong/negative/damage items show gold answer, model answer, and justification but NOT the question. The question is in the items JSON but not in the audit CSV. Need to load items JSON and join by item_id.

For calibration: already loads `all_cal_items` in the data cell. Build a lookup dict `{item_id: question}` and include in wrong items section.

For abstention: same pattern with `all_fb_items`.

For C1/C2: items are in `c1_df`/`c2_df` which already have the question column from the data load.

#### 2b. Abstention — add action errors section

Current: only "Negative Utility Items" section (utility < 0).
Problem: a model can get negative utility from answering wrong on an answerable item (gold=answer, model=answer, wrong) — that's an accuracy failure, not a metacognitive failure. Meanwhile, a model choosing "answer" when gold is "abstain" IS a metacognitive failure but might get utility = -1.0 (caught) or utility = 0.5 if it happened to answer correctly (missed).

Better structure:
- **Action Errors** — items where `model_decision != gold_action`. These are the metacognitive failures.
- **Negative Utility Items** — keep as supplementary section for completeness.

Both sections include: item_id, question, gold_action, model_decision, model_answer, utility, justification.

#### 2c. C1/C2 — full transition breakdown

Current: only "Damage Items" section.
Add:
- **Correction Gains** — wrong→right transitions (the wins). Show question, T1/T2 answers, justification.
- **Stubborn Wrong** — wrong on T1, still wrong on T2. Show what the model persisted with.
- **Damage Items** — right→wrong (already exists, add question text).
- Keep item detail table at the bottom.

Group by transition type. Each item: item_id, question (truncated), gold, T1 answer, T2 answer, justification.

### WS3: Fix cost data extraction

**Problem:** run.json glob `*calibration*.run.json` doesn't match filenames like:
`metajudge_calibration_v61-run_id_Run_1_anthropic_claude-haiku-4-520251001.run.json`

The emoji `🤖` in the model slug may also be an issue, though the Haiku filename shown in the error doesn't have emoji.

**Fix:** Use `*.run.json` as the glob pattern (match any run.json in OUTPUT_DIR) instead of task-specific patterns. There's only one task per notebook, so there's only one run.json.

**Also check:** Whether the run.json for non-Flash models has the same `subruns[].conversations[].metrics` structure with `inputTokens`, `outputTokens`, etc. The Haiku run said "run.json not found" — might be a glob issue or might be that the run.json wasn't saved (the `Kept:` line appeared in calibration but check if it appears for all models).

## Execution phases

### Phase 0: Archive v6.1 notebooks, bump version refs to v6.2

### Phase 1: Fix try/except — re-raise quota/permission errors
- All 4 helper tasks
- Keep try/except for LengthFinishReasonError, TypeError, parsing errors
- **Commit, stop, wait**

### Phase 2: Fix run.json glob pattern
- Change from `*calibration*` / `*abstention*` / `*sc_c1*` / `*sc_c2*` to `*.run.json`
- All 4 notebooks
- **Commit, stop, wait**

### Phase 3: Add question text to flagged items
- Build item_id→question lookup in each notebook
- Add question to wrong items (cal), action errors + negative utility (abs), all transition detail (C1/C2)
- **Commit, stop, wait** (may split into sub-phases per notebook)

### Phase 4: Abstention — action errors section
- New section: items where model_decision != gold_action
- Each item: question, gold_action, model_decision, answer, utility, justification
- **Commit, stop, wait**

### Phase 5: C1/C2 — full transition breakdown
- Add correction_gain and stubborn_wrong sections
- Each section: items with question, T1/T2 answers, justification
- **Commit, stop, wait**

### Phase 6: Sync to submission branch
- Copy updated notebooks to submission/v6.1 (or create submission/v6.2)
- **Commit, stop, wait**

## What NOT to change
- Task names (platform-registered)
- Anchor values
- Scoring logic
- Prompt text (except conciseness instruction already added)
- The `%choose` targets
- Stochasticity resilience (Run 2 try/except, item_id matching, 80% gate)
