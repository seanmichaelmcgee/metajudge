# Statistical Review & Update — Agent Prompt

## Objective

Review, update, and extend the MetaJudge statistical analysis to cover all
three active families (A, B, C). Produce a unified stats backgrounder and
concrete weight recommendations for the composite MetaScore.

## Read first (in order)

1. `SOUL.md` — principles (behavioral evidence, two-axis framework)
2. `docs/stats/stats_backgrounder_families_ab.md` — existing A+B methodology
3. `docs/stats/power_analysis_family_c.md` — Family C power analysis (v0.6.2, 45 items)
4. `docs/stats/stats_reproducibility_log.md` — seeds, versions, checksums
5. `metajudge/scoring/statistics.py` — implementation (bootstrap, McNemar, Holm, Spearman)
6. `config/family_c_scoring.yaml` — FC scoring parameters
7. `outputs/family_c/sweep_v2_phase5/phase6_full_analysis.md` — latest FC results (56 items x 4 models)
8. `outputs/family_c/sweep_v2/sweep_v2_analysis.md` — validation sweep (5 models x 45 items)
9. `planning/family_c_sprint/03_scoring_blueprint.md` — FC transition scoring design

## Deliverables

### D1: Updated stats backgrounder (`docs/stats/stats_backgrounder_v3.md`)

Extend the existing A+B backgrounder to cover Family C. Address:

- **Transition-based scoring distribution properties**: Family C scores are
  bounded, discrete-ish (6 transition classes), and asymmetric (damage > gain).
  What are the implications for bootstrap CIs and pairwise tests?
- **Paired structure**: All families share the paired-items design, but FC has
  two observations per item (T1, T2). How does within-item dependency affect
  inference? Is McNemar still appropriate for T1-vs-T2 within a model?
- **Multiple testing**: With 3 families and 4+ subscores, the comparison space
  grows. Update the Holm correction scope.
- **Power update**: The A+B backgrounder was written for n=117/84. FC has n=55.
  What effect sizes are detectable? What is the minimum FC item count for
  defensible SC rate comparisons (the v0.6.2 analysis estimated 75-150)?
- **Confidence ceiling problem**: All models report 92-99% confidence on FC
  items. Discuss implications for confidence-based discrimination and the
  confidence adjustment component of the transition score.
- **B0 baseline interpretation**: The re-answering baseline (B0) tests whether
  the review protocol adds value beyond re-sampling. What is the right
  statistical test for C1-B0 delta significance?

### D2: Cross-family correlation analysis

- Spearman rank correlations between family-level scores across models
  (extend the existing bridge analysis from A+B to A+B+C)
- Are the three families measuring distinguishable constructs? If two families
  correlate at rho > 0.9 across models, one may be redundant.
- Report with CIs. Small model panel (4-5 models) means rank correlations
  have very wide CIs — flag this limitation explicitly.

### D3: Weight recommendations (`docs/stats/weight_recommendations.md`)

Using the statistical evidence from D1 and D2, recommend composite weights.
Consider:

- **Reliability**: families with tighter CIs deserve more weight
- **Discriminative power**: families that separate models more should be
  weighted higher (use effect sizes from pairwise comparisons)
- **Independence**: highly correlated families should not both receive large
  weights (double-counting the same construct)
- **Theoretical priors**: SOUL.md specifies monitoring-heavy weighting;
  any deviation must be justified
- **Current defaults**: `config/benchmark_config.yaml` and
  `metajudge/scoring/composite_score.py` (DEFAULT_WEIGHTS)

Provide 2-3 candidate weight vectors with rationale, plus a recommended
default. Format as a YAML snippet ready to drop into config.

## Constraints

- All statistical methods must be non-parametric (bootstrap, permutation,
  exact tests). No normality assumptions — the backgrounder explains why.
- Seeds must be reproducible: `seed=42`, `n_boot=10000` throughout.
- Do not modify scoring logic or item data. This is analysis only.
- Results should be in markdown tables, not just prose.
- Flag any finding that contradicts SOUL.md principles.

## Data sources for computation

Run scripts or write new analysis code as needed. Key data:

| Family | Items | Models | Data location |
|--------|-------|--------|--------------|
| A (Cal) | 105 clean | 5 | `outputs/calibration_item_audit.csv` or re-run from `kaggle-dataset-v3/` |
| B (Abs) | 72 clean | 5 | `outputs/family_b_item_audit.csv` or re-run from `kaggle-dataset-v3/` |
| C (SC) | 55 clean | 4-5 | `outputs/family_c/sweep_v2_phase5/` JSONL files |

If audit CSVs are stale or missing, regenerate from the JSONL sweep files.

## Output format

- All deliverables as markdown in `docs/stats/`
- Commit after each deliverable (D1, D2, D3 separately)
- Final commit message should summarize the recommended weights
