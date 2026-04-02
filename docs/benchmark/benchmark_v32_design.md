# Benchmark v3.2 — Composite Scoring Design

**Notebook:** `metajudge_benchmark_v3_2.ipynb`
**Date:** April 2026
**Status:** Production

---

## Problem

The Kaggle Benchmarks SDK runs tasks per-model (`kbench.llm` = one model at a
time). Z-standardization requires all models' scores simultaneously, which is
impossible in the per-model execution model. The v3.1 notebook's composite
cell computed z-scores that depended on the full 5-model panel — this breaks
when Kaggle runs the task for a single new model.

## Solution: Anchor-Based Normalization

Each family score is rescaled to [0, 1] using fixed theoretical floor/ceiling
constants. No reference to other models required. This follows the BIG-Bench
approach (Srivastava et al. 2023) and Open LLM Leaderboard v2 (Beeching et
al. 2024).

### Anchor Constants

| Family | Metric | Floor | Ceiling | Floor Rationale | Validation |
|--------|--------|-------|---------|-----------------|------------|
| A (Calibration) | 1-Brier | 0.75 | 1.00 | Random guessing at 50% confidence: 1-(0.5-p)² = 0.75 regardless of accuracy | Mathematical proof |
| B (Abstention) | UWAA | 0.60 | 1.00 | Random uniform action selection on this item set | Monte Carlo: 72K trials, seed=42 |
| C (Self-Correction) | T2-T1 Δ | -1.00 | +1.00 | Worst/best case theoretical bounds | Theoretical |

**Important:** B floor is 0.60, not 0.50. The item distribution is
abstain-heavy (40.3% of gold actions) and abstaining randomly gets partial
credit against verify/clarify gold actions. The empirical random baseline
was validated via Monte Carlo simulation (72,000 trials across all 72 clean
items with uniform random action selection).

### Normalization Formula

```python
def normalize(score, floor, ceil):
    return max(0.0, min(1.0, (score - floor) / (ceil - floor)))
```

### Composite MetaScore

```python
MetaScore = (norm_A + norm_B + norm_C) / 3
```

Equal weighting is provably optimal at n=5 models with k=3 families:
- Dawes (1979): equal weights outperform OLS-optimized weights empirically
- Davis-Stober (2011): formal proof that equal weights minimize MSE when p ≥ n
- Einhorn & Hogarth (1975): minimum correlation between equal-weight and
  OLS-weight composites exceeds 0.95 with k ≤ 5

### Two-Axis Decomposition

```python
Monitoring = (norm_A + norm_B) / 2   # Epistemic self-assessment quality
Control    = norm_C                   # Ability to correct errors
```

The `%choose` task returns `MetaScore` (single float). Monitoring and Control
are displayed in the notebook for profile analysis but not submitted separately.

---

## Notebook Architecture (16 cells)

| Cell | Type | Content | Changes from v3.1 |
|------|------|---------|-------------------|
| 0 | md | Title + intro | Version → v3.2, two-axis description |
| 1 | code | Imports + pip install | Added scipy/matplotlib/seaborn install |
| 2 | code | Scoring formulas | Replaced weighted composite with anchor constants + `normalize()` + `composite_metascore()` |
| 3 | code | Response schemas | Unchanged |
| 4 | code | Load datasets | Unchanged |
| 5 | code | Task: Calibration | Unchanged |
| 6 | code | Task: Abstention | Unchanged |
| 7 | code | Task: Self-Correction | Fixed `import numpy as np as _np_fc` syntax error |
| 8 | code | Composite task | **Rewritten**: runs A+B+C, anchor normalization, returns MetaScore |
| 9 | code | Run benchmark | Passes `fc_df` to composite task |
| 10 | md | MetaScore explanation | Anchor normalization + BIG-Bench reference |
| 11 | code | Results display | Raw + normalized + monitoring/control table |
| 12 | code | Scatter plot | Monitoring × Control, axes [0, 1] |
| 13 | code | Audit export | CSVs + composite_analysis.csv + summary JSON |
| 14 | md | Scoring methodology | Anchor table + 7 references |
| 15 | code | `%choose` | `metajudge_metacognition_v3_2` |

### Figures (3 total)

1. Reliability diagram (from calibration task)
2. Action distribution (from abstention task)
3. Monitoring × Control scatter (Cell 12)

### Tables (4 total)

1. Calibration leaderboard (from task output)
2. Abstention leaderboard (from task output)
3. Self-correction leaderboard (from task output)
4. MetaScore results (Cell 11): raw scores, normalized, monitoring, control

### Exports

- `calibration_item_audit.csv` — per-item calibration results
- `family_b_item_audit.csv` — per-item abstention results
- `family_c_item_audit.csv` — per-item self-correction results
- `composite_analysis.csv` — normalized scores, axes, MetaScore
- `benchmark_run_summary.json` — version, method, anchors, file manifest

---

## What the Leaderboard Shows

Each model evaluated by the benchmark gets one number:

| Output | Formula | Range | Higher is better? |
|--------|---------|-------|-------------------|
| MetaScore | mean(norm_A, norm_B, norm_C) | [0, 1] | Yes |

The notebook also displays (but does not submit):

| Display | Formula | Interpretation |
|---------|---------|----------------|
| Monitoring | mean(norm_A, norm_B) | Epistemic self-assessment quality |
| Control | norm_C | Error correction ability |

Models in the upper-right of the Monitoring × Control scatter have strong
metacognition on both axes. Quadrant separation reveals capability
dissociations (e.g., high monitoring but low control).

---

## Relationship to Narrative Notebook

The narrative notebook (`metajudge_narrative_v3.ipynb`) retains z-standardized
composite analysis for cross-model comparison where all models are evaluated
together. The z-score MetaScore, Dirichlet stability analysis, Hasse partial
order, and Haberman PRMSE test are analytical tools that require the full model
panel — they are not per-model scoring functions.

| Feature | Benchmark v3.2 | Narrative v3.2 |
|---------|---------------|----------------|
| Normalization | Anchor-based (per-model) | Z-score (cross-model) |
| Models per run | 1 (Kaggle SDK) | 5 (full panel) |
| Composite | MetaScore = mean(norm_A, norm_B, norm_C) | MetaScore = mean(z_A, z_B, z_C) |
| Uncertainty | Not computed (single model) | Dirichlet, Hasse, Friedman |
| Family C caveat | Reported via damage rate | Haberman PRMSE test |
| Purpose | Leaderboard submission | Scientific analysis |

---

## Bugfixes Included

1. **`import numpy as np as _np_fc`** — invalid Python syntax (double alias).
   Removed from Cell 7 in both v3 and v3.2 notebooks. `np` already imported
   in Cell 1.

2. **Missing scipy install** — Cell 9 (z-score version) used `scipy.stats`
   but the benchmark notebook never pip-installed it. Added to Cell 1.

3. **Missing orchestrator task** — The initial v3.2 draft removed the old
   composite task (Cell 8 in v3) which orchestrated all three sub-task sweeps.
   Without it, `CAL_AUDIT`/`FB_AUDIT`/`FC_AUDIT` were never populated.
   Restored with anchor normalization.

4. **`cal_results` undefined** — The benchmark notebook uses `@kbench.task`
   functions that produce audit DataFrames, not the `cal_results`/`fb_results`
   dicts from the narrative notebook. MetaScore display rewritten to compute
   from `CAL_AUDIT`/`FB_AUDIT`/`FC_AUDIT`.

---

## References

- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability.
- Dawes, R. M. (1979). The robust beauty of improper linear models in decision making.
- Davis-Stober, C. P. (2011). A geometric proof of the decision-theoretic optimality of unit weights.
- Einhorn, H. J., & Hogarth, R. M. (1975). Unit weighting schemes for decision making.
- Srivastava, A., et al. (2023). Beyond the imitation game: BIG-Bench.
- Beeching, E., et al. (2024). Open LLM Leaderboard v2.
- Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework.
- Huang, J., et al. (2024). Large language models cannot self-correct reasoning yet.
- Burnell, R., et al. (2026). Measuring progress toward AGI.
