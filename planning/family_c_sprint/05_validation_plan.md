# Family C Sprint: Validation Plan

**Purpose:** Define the evaluation protocol, statistical analyses, and promotion
criteria for Family C.

---

## 1. Evaluation Protocol

### 1.1 Model Panel

Use the `core_five` panel from `benchmark_config.yaml`:

| Model | Role |
|-------|------|
| google/gemini-2.5-flash | Fast, cheap — smoke test and baseline |
| google/gemini-2.5-pro | Strong frontier model |
| anthropic/claude-sonnet-4@20250514 | Strong frontier model |
| anthropic/claude-haiku-4-5@20251001 | Smaller/faster model |
| deepseek-ai/deepseek-v3.1 | Open-weight frontier model |

### 1.2 Evaluation Phases

**Phase 0: Dry Run (pre-evaluation)**
- Run 3-5 items against gemini-2.5-flash only
- Verify: prompts produce valid structured output on both turns
- Verify: grading and scoring pipeline produces expected values
- Fix any parsing, schema, or grading issues

**Phase 1: Smoke Test (1 model, full seed set)**
- Run all 35 seed items against gemini-2.5-flash
- Verify: all items produce valid responses
- Verify: score distribution is reasonable (not all 0 or all 1)
- Identify grading ambiguities → quarantine
- Expected time: ~5 minutes with caching

**Phase 2: Full Panel Run (5 models, clean seed set)**
- Run clean items against all 5 models
- Collect audit CSVs per model
- Expected time: ~20-30 minutes total with caching and parallelism

**Phase 3: Analysis and Audit**
- Compute all metrics from scoring blueprint
- Run statistical comparisons
- Flag suspect items
- Produce validation report

---

## 2. What to Measure

### 2.1 Primary Questions

| Question | How to answer | Minimum bar |
|----------|--------------|-------------|
| Does Family C discriminate between models? | Score variance across 5 models | Range ≥ 0.10 for at least one subfamily |
| Do C1 and C2 produce different rankings? | Compare model orderings | At least one rank swap |
| Is damage measurable? | Damage rate > 0 for at least 2 models | Mean damage rate > 0.05 |
| Does correction rate vary? | Correction gain rate across models | Range ≥ 0.15 |
| Are confidence dynamics informative? | Appropriate confidence rate varies | Range ≥ 0.10 |

### 2.2 Headline Statistics Per Model

For each model, compute:

```
C1_score:  mean item score across C1 clean items
C2_score:  mean item score across C2 clean items
correction_gain_rate:  #(wrong→right) / #(wrong at T1)
damage_rate:  #(right→wrong) / #(right at T1)
net_correction:  correction_gain_rate - damage_rate
revision_rate:  #(revised) / #(total)
mean_confidence_shift:  mean(conf_2 - conf_1)
appropriate_confidence_rate:  #(appropriate direction) / #(total)
```

### 2.3 Per-Stratum Breakdown

For each stratum × subfamily, report:
- Mean item score
- N items
- Most common outcome
- Damage count (if applicable)

---

## 3. Statistical Analysis

### 3.1 Score Distributions

- Report mean, median, std, min, max for C1_score and C2_score per model
- Histogram of item scores per model (5 histograms, overlay or faceted)
- Box plots comparing models on C1 and C2

### 3.2 Model Comparison

**Pairwise differences:**
- For each model pair, compute: mean_score_difference ± bootstrap 95% CI
- Use bootstrap (B=1000, seed=42) for confidence intervals
  (matches existing `statistics.py` patterns)

**Rank correlation with A/B:**
- Compute Spearman rank correlation between:
  - C1 ranking and A (calibration) ranking
  - C2 ranking and A (calibration) ranking
  - C1 ranking and B (abstention) ranking
  - C2 ranking and B (abstention) ranking
- If C perfectly correlates with A, its incremental value is lower
- Expect moderate but imperfect correlation (ρ ≈ 0.4-0.7)

### 3.3 Discrimination Analysis

**Item discrimination:**
- For each item, compute score variance across 5 models
- Flag items with zero variance (all models same score) as low-discrimination
- Flag items where all models score < 0.2 (floor effects) or > 0.9 (ceiling effects)

**Subfamily discrimination:**
- Does C1 show any meaningful spread, or do all models effectively score ~0?
  If C1 has near-zero variance, it may need to be deferred or redesigned.

### 3.4 Damage Analysis

- Per-model damage rates with 95% CIs
- Item-level damage patterns: which items trigger overcorrection?
- Cross-model damage agreement: do the same items cause damage across models?
- Damage severity: when damage occurs, how much does confidence change?

### 3.5 Bridge Analysis

Extend the existing `bridge_metrics.py` analysis:

**Monitoring → Control coupling for Family C:**
- Plot: T1 confidence × T1 correctness → T2 outcome
- Expected pattern: low T1 confidence + wrong → more likely to revise
- Failure pattern: high T1 confidence + correct → still revises (overcorrection)

**Cross-family bridge:**
- Models that calibrate well (Family A) should show better confidence dynamics in C
- Models with good abstention (Family B) should show less overcorrection
- Test these predictions empirically

---

## 4. Suspect-Item Handling

### 4.1 Quarantine Criteria

An item should be quarantined if:
1. **Grading ambiguity:** Multiple valid answer formats, or gold answer is debatable
2. **Universal floor:** All 5 models score ≤ 0.2 (item may be too hard or poorly designed)
3. **Universal ceiling:** All 5 models score ≥ 0.9 (item may be trivial)
4. **Inconsistent grading:** Model answer is arguably correct but grader marks wrong
5. **Schema failure:** Model fails to produce valid structured output

### 4.2 Quarantine Process

1. Flag item in audit CSV with reason
2. Add to `family_c_manifest.json` quarantined list
3. Remove from clean subset
4. Review at end of Phase 3 — fix or permanently exclude

### 4.3 Minimum Clean-Set Threshold

- Must retain ≥ 12 C1 items and ≥ 15 C2 items after quarantine
- If below threshold, author replacement items and re-run
- Do not lower the threshold; add items instead

---

## 5. Simple Claims After Seed-Set Evaluation

After the seed-set evaluation, the following claims should be assessable
(listed from strongest to weakest):

### 5.1 Claims we expect to support
- "Family C produces measurable score variation across frontier models"
- "C2 (evidence-assisted) discriminates more than C1 (intrinsic)"
- "Overcorrection (damage) is a real and measurable failure mode"
- "Model rankings on Family C differ from Family A rankings"

### 5.2 Claims that require more data
- "Family C adds incremental prediction value beyond A+B"
- "C1 intrinsic self-correction is a stable, discriminating measure"
- "Damage rate is a reliable individual-difference signal"

### 5.3 Claims we should not make yet
- "MetaJudge measures the full metacognition construct" (need D and E)
- "Family C scores are stable across prompt variations" (need robustness testing)
- "Family C generalizes beyond the tested item domains" (need broader items)

---

## 6. Promotion Decision Criteria

### 6.1 Gate 1: Seed-Set Approval

Family C seed set is approved for expansion if:
- [ ] ≥ 25 items pass clean-set audit
- [ ] Score range across 5 models ≥ 0.10 for at least one subfamily
- [ ] Damage rate > 0 for at least 2 models
- [ ] No systematic grading failures
- [ ] Cost is within budget

### 6.2 Gate 2: Clean-Set Promotion

Family C clean set is promoted to reporting status if:
- [ ] ≥ 50 clean items across C1 + C2
- [ ] Bootstrap CIs show at least one significant pairwise model difference
- [ ] Rank correlation with A is < 0.9 (C measures something new)
- [ ] Damage rate patterns are stable across two evaluation runs
- [ ] Scoring produces values in a useful range (not all clustered)

### 6.3 Gate 3: Official Benchmark Inclusion

Family C enters the official `%choose` benchmark if:
- [ ] Gates 1 and 2 passed
- [ ] Composite score with C included does not degrade A/B discrimination
- [ ] No unresolved grading ambiguities in clean set
- [ ] Narrative notebook documents all validation evidence
- [ ] Scoring weights confirmed (C1: 0.10, C2: 0.15)

---

## 7. Validation Outputs

The validation process should produce:

| Output | Format | Purpose |
|--------|--------|---------|
| `family_c_audit_c1_{model}.csv` | CSV | Per-item C1 audit per model |
| `family_c_audit_c2_{model}.csv` | CSV | Per-item C2 audit per model |
| `family_c_summary.json` | JSON | Headline scores and diagnostic metrics |
| `family_c_discrimination.json` | JSON | Item discrimination and ranking analysis |
| `family_c_manifest.json` | JSON | Updated clean-set manifest |
| Analysis cells in notebook | Notebook | Visualization and statistical tests |
