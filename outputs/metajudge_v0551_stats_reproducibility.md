# MetaJudge v0.5.5.1 — Statistical Analysis Reproducibility Log

## Environment

- **Python**: 3.11.14
- **Platform**: Linux-6.18.5-x86_64-with-glibc2.39
- **Architecture**: x86_64

## Package Versions

| Package | Version |
|---------|---------|
| numpy | 2.4.3 |
| scipy | 1.17.1 |
| matplotlib | 3.10.8 |
| seaborn | 0.13.2 |
| python-docx | 1.2.0 |
| pandas | 3.0.1 |

## Random Seeds

All bootstrap and permutation procedures use a fixed seed for reproducibility:

- **Bootstrap CI**: seed = 42 (via `np.random.default_rng(42)`)
- **Permutation test**: seed = 42 (via `np.random.default_rng(42)`)
- **Bootstrap resamples**: n = 10,000
- **Permutation iterations**: n = 10,000

Seeds are hardcoded in `metajudge/scoring/statistics.py` and not configurable
at runtime, ensuring identical results across runs.

## Data Checksums (SHA-256)

| File | SHA-256 |
|------|---------|
| calibration_item_audit (8).csv | `7ba8a465456cdb34cb8a7a52d279b3c8649e8b00953d1a095f297635d0be6f39` |
| family_b_item_audit (8).csv | `e52d4edb5a7a632e2fa45f77516629ba329cb16621e5c87cd90b94b016f14272` |
| run_summary (7).json | `eb3002a6d42db9fb0db752d8c650f176c2bd184bcd9a8c9ecbe340d021ef5609` |
| audit_review_queue (2).csv | `0448301e3b926ad0cd3993cd5ee11303bd12825b593dfc61ed0fa7ed0aac1fc3` |

## Script Invocation

```bash
# From project root
pip install -e ".[dev]"
pip install matplotlib seaborn scipy

python scripts/generate_stats_report.py
```

**Prerequisites**: Data files must be extracted to `/tmp/v0551/v0.5.5.1 - results/`.

## Output Manifest

### Reports

| File | Description |
|------|-------------|
| `outputs/metajudge_v0551_stats_backgrounder.md` | Statistical testing rationale and references |
| `outputs/metajudge_v0551_stats_report.docx` | Polished results report with embedded figures |
| `outputs/metajudge_v0551_stats_reproducibility.md` | This file |

### Figures (11 PNGs)

| File | Description |
|------|-------------|
| `bridge_confidence_accuracy.png` | Confidence vs accuracy per model with Spearman ρ |
| `bridge_confidence_violins.png` | Confidence distribution violin plots by model |
| `cal_brier_forest_plot.png` | Pairwise Brier score differences with 95% bootstrap CIs |
| `cal_mechanism_brier_bars.png` | Mean Brier score by mechanism × model |
| `cal_mechanism_heatmap.png` | Accuracy heatmap: mechanisms × models |
| `cal_pvalue_heatmap.png` | Calibration p-value heatmap (McNemar + permutation) |
| `cal_reliability_diagram.png` | Calibration reliability diagram (all models overlaid) |
| `fb_action_confusion.png` | Action confusion matrices per model (Family B) |
| `fb_action_distribution.png` | Action distribution stacked bar chart (Family B) |
| `fb_utility_forest_plot.png` | Pairwise utility differences with 95% bootstrap CIs |
| `significance_master_heatmap.png` | Master significance heatmap (all tests × all pairs) |

## Reproduction Steps

1. Clone the repository and check out the analysis branch
2. Extract v0.5.5.1 data to `/tmp/v0551/`
3. Install dependencies: `pip install -e ".[dev]" && pip install matplotlib seaborn scipy`
4. Run: `python scripts/generate_stats_report.py`
5. Verify outputs match checksums and figure count

## Statistical Tests Summary

| Test | Function | Source |
|------|----------|--------|
| McNemar's test | `mcnemar_test()` | `metajudge/scoring/statistics.py` |
| Paired permutation test | `paired_permutation_test()` | `metajudge/scoring/statistics.py` |
| Paired bootstrap CI | `paired_bootstrap_ci()` | `metajudge/scoring/statistics.py` |
| Single-sample bootstrap CI | `bootstrap_ci_single()` | `metajudge/scoring/statistics.py` |
| Stuart-Maxwell test | `stuart_maxwell_test()` | `metajudge/scoring/statistics.py` |
| Spearman + bootstrap CI | `spearman_with_ci()` | `metajudge/scoring/statistics.py` |
| Holm-Bonferroni correction | `holm_correction()` | `metajudge/scoring/statistics.py` |
| Cohen's d (effect size) | `compute_effect_sizes()` | `scripts/generate_stats_report.py` |
| Odds ratio (McNemar) | `compute_odds_ratio()` | `scripts/generate_stats_report.py` |
