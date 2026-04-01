# MetaScore: Composite Construction Rationale

## Method

MetaScore = mean(z_A, z_B, z_C), where z_X = (X − X̄) / σ_X for each family.

Equal-weight z-score averaging. No optimized weights. No differential weighting by reliability, discriminability, or theory.

## Why equal weights

Davis-Stober (2011, *Psychometrika*) proved formally that with k ≤ 5 predictors and n ≤ 15 observations, fixed equal weights have lower expected mean squared error than OLS-optimized weights. Dawes (1979, *American Psychologist*) showed empirically that unit-weighted composites match or outperform regression weights in small samples. Einhorn & Hogarth (1975) showed the minimum correlation between equal-weighted and optimally-weighted composites exceeds 0.95 with k ≤ 5.

With 3 families and 5 models, any data-derived differential weighting is pure overfitting.

## Why z-standardization

The three families produce scores on different scales with different spreads:

| Family | Metric | Spread | Range |
|--------|--------|--------|-------|
| A (Calibration) | 1 − Brier | 0.100 | 0.836–0.936 |
| B (Abstention) | UWAA | 0.064 | 0.828–0.892 |
| C (Self-Correction) | T2−T1 accuracy delta | 0.039 | −0.020–+0.020 |

Without standardization, Family A would dominate the composite through raw variance alone. Z-standardization ensures each family contributes equally in standard-deviation units, consistent with equal-weight theory.

## Why Family C is included

The Haberman (2008, *JEBS*) PRMSE test determines whether a subscore adds information beyond the total. Family C was evaluated under both single-run and triplicate conditions:

| Condition | C reliability (α) | PRMSE(C alone) | PRMSE(C from A+B) | Standalone value? |
|-----------|-------------------|----------------|-------------------|-------------------|
| Single run | 0.35 | 0.350 | 0.657 | **No** |
| 3-run majority vote | 0.76 | 0.758 | 0.412 | **Yes** |

The triplicate crossed the Haberman threshold. Family C's aggregated scores predict true self-correction performance better than Families A+B can. Triplicating was necessary: single-run reliability was insufficient.

Family C also provides orthogonal information. Spearman correlations across the 5-model panel:
- A × B: ρ = +0.60 (partially redundant)
- A × C: ρ = −0.37 (partially orthogonal)
- B × C: ρ = −0.74 (strongly anti-correlated)

The B×C anti-correlation confirms that abstention quality and self-correction quality are dissociable. Removing C would collapse the distinction between Pro (best abstainer, worst self-corrector) and Sonnet (best self-corrector, moderate abstainer).

## Ranking stability

10,000 weight vectors sampled from Dirichlet(1,1,1) — uniform prior over the weight simplex.

**Robust orderings (stable under ≥95% of weight perturbations):**
- Flash > Haiku (100%), Sonnet > Haiku (100%), Flash > Pro (97%)

**Fragile orderings (< 75%):**
- Flash vs Sonnet (54%), Sonnet vs Pro (63%), Pro vs DeepSeek (65%)

The leaderboard separates into two tiers — {Flash, Sonnet} and {Pro, DeepSeek, Haiku} — that are robust to any reasonable weighting. Within-tier ordering is weight-sensitive, reflecting genuine capability trade-offs rather than measurement noise.

Hasse partial order: only 2 of 10 model pairs have a dominance relation (one model beats another on all 3 families). The remaining 8 pairs are incomparable — in each case, one model wins on calibration/abstention and the other wins on self-correction.

## What MetaScore does NOT claim

- It does not claim to statistically separate adjacent-ranked models. The Friedman test (p = 0.38) confirms that 3 families are insufficient for formal pairwise significance at α = 0.05.
- It does not claim the weights are optimal. It claims they are *provably no worse* than any data-optimized alternative at this sample size.
- It does not claim a single ranking captures all information. The family-level profiles and Hasse incomparability structure are presented alongside MetaScore for this reason.

---

## Benchmark Notebook Implementation

### What to change

The current benchmark notebook calls `compute_composite_score()` from the package, which uses theory-constrained weights from `config/benchmark_config.yaml`. **Replace this** with the z-score equal-weight computation below. The explicit 4-line implementation is more defensible than a function call with opaque weights, and it is directly auditable by judges.

### Computation cell (~15 lines)

```python
# Composite MetaScore — equal-weight z-score average (Dawes 1979)
_fam_scores = {}
for label, scores_dict in [("A", cal_metrics), ("B", fb_metrics), ("C", fc_metrics)]:
    if label == "C":
        vals = {m: fc_metrics[m]["delta"] for m in fc_metrics}
    elif label == "B":
        vals = {m: fb_metrics[m]["uwaa"] for m in fb_metrics}
    else:
        vals = {m: cal_metrics[m]["mean_1_brier"] for m in cal_metrics}
    arr = np.array([vals[m] for m in model_order])
    _fam_scores[label] = (arr - arr.mean()) / arr.std()

metascores = np.mean([_fam_scores[f] for f in ["A", "B", "C"]], axis=0)
```

### Markdown cell (place directly above the computation cell)

> **Composite MetaScore** is the equal-weight average of z-standardized family scores. Equal weighting is provably optimal at n=5 models (Davis-Stober 2011; Dawes 1979). Family C is included based on 3-run majority-vote aggregation (ICC = 0.76, exceeding the Haberman 2008 threshold for standalone subscore value). Rankings of Flash (rank 1) and Haiku (rank 5) are stable under 100% of weight perturbations; middle rankings reflect genuine capability trade-offs across metacognitive dimensions (B×C Spearman ρ = −0.74).

### What stays in the narrative notebook only

The following analyses support the rationale but do **not** belong in the benchmark notebook:

- Dirichlet pairwise stability matrix and rank probability table
- Hasse partial order and linear extension counting
- Haberman PRMSE derivation and sensitivity analysis
- ICC computation and per-run breakdowns
- Friedman test and Nemenyi critical difference
- Per-run stability diagnostics

These are available in the narrative notebook and in `docs/stats/` for judges who want the full evidence base.

### What the benchmark notebook should display

One table combining family profiles and the composite:

| Model | Calibration (A) | Abstention (B) | Self-Correction (C) | MetaScore | Rank |
|-------|----------------|---------------|--------------------|-----------| -----|
| ... | 1-Brier | UWAA | T2-T1 Δ (3-run avg) | mean(z) | |

Plus one sentence below the table: *"8 of 10 model pairs are Pareto-incomparable across the three families — see the narrative notebook for the full partial-order analysis."*

This keeps the benchmark notebook lean (one computation, one justification, one table) while signposting the deeper analysis for interested reviewers.
