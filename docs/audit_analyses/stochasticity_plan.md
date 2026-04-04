# Stochasticity Deep Analysis — Plan

## Mission

> Evaluate the reproducibility of MetaJudge v6.2 scores using dual-run data
> across all available models. Determine whether score differences between
> models represent genuine capability differences or measurement noise.
> Identify which items and tasks are most volatile, and whether the volatility
> is genuine response variance, parsing artifacts, or grading artifacts.

---

## Gap Assessment

**What exists:** Gemini Pro has one detailed per-item stochasticity analysis.
Synthesis reports mention stochasticity at headline level (0.29 swing, 57% C1 stability).

**What's missing:** Systematic analysis across ALL 19 model×task dual-run
combinations. No cross-model comparison, no per-item volatility analysis,
no assessment of change validity, no leaderboard impact analysis.

**Data available:** 19 model×task combinations with R1+R2 data.
Rich enough for comprehensive analysis.

---

## Analysis Structure

### Level 1: Per-Model Stochasticity Profile
For each model with dual-run data:
- **Score delta:** R1 normalized vs R2 normalized (per task)
- **Item flip rate:** % of items that changed outcome between runs
- **Flip direction:** Did flips improve or worsen the score?
- **Stability class:** Stable (<5% flips), Moderate (5-15%), Volatile (>15%)

### Level 2: Per-Item Volatility (across models)
For each item in each task:
- How many models flipped on this item?
- Is this item inherently volatile or model-specific?
- Items that flip for ALL models → item design issue
- Items that flip for ONE model → model-specific variance

### Level 3: Change Validity Assessment
For each flip, categorize:
- **Genuine variance:** Model gives different but equally reasonable answers
- **Parsing artifact:** Same answer, different extraction/formatting
- **Grading artifact:** Same answer, grading engine inconsistency
- **Confirmation detection:** T2 confirms T1 but phrased differently → different grade

### Level 4: Leaderboard Impact
- Compute MetaScore using R2 data instead of R1
- Do rankings change?
- Compute score ± stochasticity range per model
- Can we confidently separate any model pairs?

### Level 5: Recommendations
- Which tasks need multi-run aggregation?
- Which items should be flagged as volatile?
- What stochasticity threshold should trigger concern?

---

## Agent Hierarchy

```
ORCHESTRATOR
│
├── PHASE 1: Data extraction (orchestrator inline)
│   Parse all 19 dual-run JSONs into structured stochasticity dataset
│   Compute all R1 vs R2 deltas, flip counts, score differences
│   Output: stochasticity_dataset.json
│
├── PHASE 2: Per-model + per-item analysis (opus, background)
│   Reads stochasticity_dataset.json
│   Produces Level 1 (model profiles) + Level 2 (item volatility)
│   Output: stochasticity_model_item_analysis.md
│
├── PHASE 3: Change validity + leaderboard impact (opus, background)
│   Reads stochasticity_dataset.json + canonical_dataset.json
│   Produces Level 3 (validity) + Level 4 (leaderboard)
│   Requires reading actual answer strings from JSONs for validity
│   Output: stochasticity_validity_impact.md
│
└── PHASE 4: Synthesis (orchestrator inline)
    Combines all into stochasticity_deep_analysis.md
    Level 5 recommendations
    Integration into v62_synthesis_report.md
```

---

## Execution

Phase 1 is data extraction (orchestrator, fast).
Phases 2 and 3 can run in parallel (both opus, background).
Phase 4 assembles after both return.

Each phase: commit, stop for user if needed.
