# Intensive Cross-Model Item Audit — Plan

## Purpose

Select a focused sample of items and analyze them deeply across all 6 complete
models. This demonstrates the benchmark's interpretability and grading robustness
at the individual item level. The methodology is codified for reproducibility on
different item samples or future benchmark versions.

---

## Item Selection

### Set 1: Correctly Graded Items (5 per task = 20 items)

**Criteria:**
- Data available from all 6 complete models
- Graded correctly by all models (consensus correct) OR discriminating
  (some correct, some wrong) — prefer a mix
- Avoid items with known grading bugs (tri_label: gen_a4_022/024, gen_b_040, gen_a2_007)
- Avoid items with known encoding issues (abs_006)
- Select from diverse categories/mechanisms within each task

**Mix per task:**
- 2 items where ALL models are correct (consensus — shows baseline)
- 3 items where models DISAGREE (discriminating — shows what the benchmark measures)

### Set 2: Problematic Items (5 additional items, cross-task)

**Criteria:**
- Items where grading is sometimes wrong across models
- Bugs whose solution is UNCLEAR (not the known tri_label fix)
- Include items flagged in deep audits: abs_002 (false positive), abs_006 (Unicode)
- Cross-model comparison will help locate the bug pattern

---

## Per-Item Analysis Structure

### (a) Key Data Table

```markdown
### [item_id] — [task] — [category/mechanism]

**Question:** [full question text]
**Gold Answer:** [gold answer]
**Justification:** [from justifications file]

| Model | Answer | Correct | Confidence | Score | Cost |
|-------|--------|---------|-----------|-------|------|
| flash | ... | ✓ | 0.95 | 0.998 | $0.003 |
| pro | ... | ✓ | 0.90 | 0.990 | $0.010 |
| ... | | | | | |
```

### (b) Deep Analysis

1. **Grading accuracy explanation:** How the grading engine processes this item.
   Which rule applies, what accepted_forms exist, why the grade is correct.

2. **Scoring effect:** How this item's score contributes to each model's task
   score. Compute with-item vs without-item to show marginal contribution.

3. **Leaderboard effect:** If this item were removed, would any model change rank?

4. **Validity assessment:** Is the gold answer defensible? Is the question
   unambiguous? Any concerns about the item design?

### (c) Cross-Model Patterns

For each item: what does the pattern of model responses reveal about
metacognitive differences? (e.g., "all models confident and correct — no
discrimination" vs "frontier models correct, smaller models wrong at
high confidence — overconfidence signal")

---

## Execution

### Phase B1: Item Selection (orchestrator, inline)
- Query canonical_dataset.json for items meeting criteria
- Select 20 + 5 items
- Commit selection with rationale

### Phase B2: Per-Task Deep Analysis (4 admin agents, sequential)
- Each admin agent processes 5 items × 6 models for one task
- Calibration + Abstention: sonnet (grading is mechanical)
- C1 + C2: opus (transition reasoning needs depth)

### Phase B3: Problematic Item Analysis (1 opus agent)
- 5 items with known grading issues
- Cross-model comparison to isolate bug patterns

### Phase B4: Synthesis (orchestrator, inline)
- Combine all analyses into `intensive_cross_model_audit.md`
- Extract patterns, findings, recommendations

---

## Output

```
docs/audit_analyses/
  intensive_cross_model_audit.md    — the final report
  intensive_audit_plan.md           — this plan (methodology)
  intensive_audit_items.json        — selected items with rationale
```

## Reuse

To run this on a different sample:
1. Modify selection criteria in Phase B1
2. Re-run the same agent pipeline
3. Compare findings across samples
