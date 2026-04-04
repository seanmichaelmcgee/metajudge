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

### WS3: Scoring explainability + submission readiness

**Problem:** The current notebook methodology markdowns are terse (5-8 lines) and don't clearly explain how raw metrics become normalized scores, how the composite MetaScore is formed, or what the numbers actually mean. The theoretical backgrounder covers the framework but not the step-by-step scoring logic a judge needs to interpret results. The Kaggle benchmark description (visible to all judges) needs a clear introduction and scoring methodology summary.

**Deliverables:**

#### 3a. Scoring overview document — `docs/scoring_overview.md`

A single reference document that explains scoring end-to-end. NOT a duplicate of the backgrounder — this is the *how*, not the *why*. Structure:

1. **How a raw score becomes a normalized score** — the anchor normalization formula, what the anchors are, where they came from (pilot sweep), worked example per task.

2. **Calibration scoring explained** — Brier rule formula, what 1-Brier means intuitively (1.0 = perfect, 0.75 = random guessing at 50%), how the 8-rule grading engine determines correctness, what "overconfident wrong" means.

3. **Abstention scoring explained** — The 5×4 payoff matrix (full table), what each cell means, how corrective answers on false-presupposition items get +0.5, how acceptable alternatives work, what UWAA is and why it's normalized to [0,1]. This is the hardest scoring to explain clearly.

4. **Self-correction scoring explained** — The six transition types with definitions, the damage:gain asymmetry with the actual config values, how confidence adjustment works, how C1 and C2 differ in their anchor ranges and why.

5. **Composite MetaScore** — How the platform averages the 4 task scores, why equal weights, what the final number means.

#### 3b. Improved notebook methodology markdowns

Expand the current 5-8 line methodology cells to ~10-15 lines each. Add:
- One sentence explaining what the normalized score means intuitively
- The anchor values and what they represent
- A pointer to `docs/scoring_overview.md` for full details

#### 3c. Benchmark description text

Short text for the Kaggle benchmark description field (visible to judges on the benchmark page):
- Three-sentence introduction: what MetaJudge measures, the two-process framework, why behavioral evidence matters
- Five bullet points on scoring methodology: one per task + composite
- This will be drafted after we have clean v6.2 runs to confirm the methodology is final

### WS4: Fix cost data extraction (was WS3)

**Problem:** run.json glob `*calibration*.run.json` doesn't match filenames like:
`metajudge_calibration_v61-run_id_Run_1_anthropic_claude-haiku-4-520251001.run.json`

The emoji `🤖` in the model slug may also be an issue, though the Haiku filename shown in the error doesn't have emoji.

**Fix:** Use `*.run.json` as the glob pattern (match any run.json in OUTPUT_DIR) instead of task-specific patterns. There's only one task per notebook, so there's only one run.json.

**Also check:** Whether the run.json for non-Flash models has the same `subruns[].conversations[].metrics` structure with `inputTokens`, `outputTokens`, etc. The Haiku run said "run.json not found" — might be a glob issue or might be that the run.json wasn't saved (the `Kept:` line appeared in calibration but check if it appears for all models).

## Execution phases

### Phase 0: Archive v6.1 notebooks, bump version refs to v6.2 ✅ DONE

### Phase 1: Fix try/except — re-raise quota/permission errors (WS1)
- All 4 helper tasks
- Keep try/except for LengthFinishReasonError, TypeError, parsing errors
- Re-raise if "403", "quota", or "permission" in error message
- **Commit, stop, wait**

### Phase 2: Fix run.json glob pattern (WS4)
- Change from `*calibration*` / `*abstention*` / `*sc_c1*` / `*sc_c2*` to `*.run.json`
- All 4 notebooks
- **Commit, stop, wait**

### Phase 3: Calibration report — add question text to wrong items (WS2a)
- Build `_questions` lookup from `all_cal_items`
- Add question to each wrong item in the markdown report
- **Commit, stop, wait**

### Phase 4: Abstention report — action errors section + question text (WS2a + WS2b)
- Build `_questions` lookup from `all_fb_items`
- New section: "Action Errors" (model_decision != gold_action)
- Add question to action errors + negative utility items
- **Commit, stop, wait**

### Phase 5: C1/C2 reports — full transition breakdown (WS2c)
- Add correction_gain and stubborn_wrong sections
- Add question text to all flagged items (damage, corrections, stubborn)
- **Commit, stop, wait** (may split C1 and C2)

### Phase 6: Write scoring overview document (WS3a)
- `docs/scoring_overview.md` — end-to-end scoring explainer
- Anchor normalization, Brier, UWAA payoff matrix, transition types, composite
- **Commit, stop, wait**

### Phase 7: Improve notebook methodology markdowns (WS3b)
- Expand from 5-8 lines to 10-15 lines per notebook
- Add intuitive score interpretation, anchor values, pointer to scoring_overview.md
- **Commit, stop, wait**

### Phase 8: Benchmark description text (WS3c)
- Draft after clean v6.2 runs available
- 3-sentence intro + 5 scoring bullets for Kaggle benchmark page
- **Commit, stop, wait**

### Phase 9: Sync to submission branch
- Copy updated notebooks + new docs to submission/v6.2
- **Commit, stop, wait**

## What NOT to change
- Task names (platform-registered)
- Anchor values
- Scoring logic
- Prompt text (except conciseness instruction already added)
- The `%choose` targets
- Stochasticity resilience (Run 2 try/except, item_id matching, 80% gate)
