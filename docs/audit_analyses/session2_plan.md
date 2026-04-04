# Audit Execution Plan — Session 2

## Status entering this session

**Completed:**
- Cross-model automated audit: 1137 items, 99.2% accuracy, 0 DISAGREE
- Gemini 2.5 Pro deep audit: 228 items (4 files)
- Sonnet 4.6 deep audit: 228 items (5 DISAGREE found — new bugs)
- Final evaluation report with 5-model leaderboard

**Now available: 6 complete models**
1. claude-sonnet-4.6 (deep audit ✅)
2. claude-sonnet-4 (cross-model only)
3. gemini-2.5-pro (deep audit ✅)
4. gemini-3-flash (needs deep audit)
5. gemma-4-26b (needs deep audit)
6. gpt-5.4 (needs deep audit)

---

## Task A: Deep Per-Model Audits (3 remaining models)

**What:** Same item-by-item LLM audit as Sonnet 4.6 and Pro. Each agent:
- Reads all 4 CSVs for that model
- Checks every item's grading against the registry
- Flags DISAGREE (grading wrong), FLAG (borderline), KNOWN-BUG (tri_label)
- Writes `docs/audit_analyses/{model}_v62/audit.md`

**Models:** Flash (227 items), Gemma-26b (226 items), GPT-5.4 (228 items)

**Timeout mitigation:** Previous agents timed out at ~30 min. Fix:
- Use `model=sonnet` for speed (not opus)
- Reduce scope: focus on WRONG items + spot-check 10 CORRECT items per task
- Don't enumerate all 100+ correct calibration items in detail

**Agent hierarchy:**
- 3 worker agents (one per model), launched in parallel
- Main thread monitors, commits results as they arrive

---

## Task B: Intensive Cross-Model Item Audit (after Task A)

**What:** Select 5 items PER TASK (20 total) that are graded correctly across
all models, and do a deep analysis showing the benchmark's interpretability.

**Item selection criteria:**
- Must have data from all 6 complete models
- Graded correctly (is_correct=True for calibration, etc.)
- Prefer items that DISCRIMINATE (some models confident, others uncertain)
- 5 per task: mix of easy consensus + harder discriminating items

**Per item, the report shows:**

### (a) Key Data Table
| Model | Answer | Correct | Confidence | Brier/Utility/Transition | Cost (if available) |
With the question text, gold answer, justification from the justifications file.

### (b) Deep Analysis (per item)
1. Why the grading is accurate — specific explanation referencing the grading rule and registry
2. Effect on scoring — how this item contributes to each model's task score
3. Effect on leaderboard — which models gain/lose from this item
4. Validity assessment — any concerns about the item, gold answer, or grading

### (c) Cross-model patterns
What does this item reveal about model differences in metacognition?

**Agent hierarchy for Task B:**
- 1 selector agent: picks the 20 items based on criteria
- 4 analyst agents (one per task): produce deep analysis for 5 items × 6 models
- 1 synthesizer agent: combines into final report

**Output:** `docs/audit_analyses/intensive_cross_model_audit.md`
- Reusable methodology (can run on different item samples)
- Codified selection criteria
- Per-item deep analysis
- Aggregate findings

---

## Execution Sequence

1. **Commit plan** ← this file
2. **Launch Task A** — 3 deep audit agents in parallel (sonnet model, focused scope)
3. **While Task A runs:** Select 20 items for Task B (can do this inline)
4. **Commit Task A results** as they arrive
5. **Launch Task B** — analyst agents with the selected items
6. **Commit Task B results**
7. **Update leaderboard** with any corrections from new audits
8. **Update final_evaluation_report.md** with expanded findings

---

## Commit strategy

After each agent completes:
```
"Deep audit [{model}]: {items} items, {AGREE}/{DISAGREE}/{FLAG}. 
Key findings: {1-sentence summary}. 
NEXT: {what's pending}"
```

If session approaches timeout:
```
"Session checkpoint: {what's done}, {what's running}, {what's next}.
All results in docs/audit_analyses/. Canonical dataset at
docs/audit_analyses/canonical_dataset.json."
```
