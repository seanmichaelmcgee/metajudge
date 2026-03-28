# MetaJudge Notebook Architecture Memo

*Status: Complete*
*Branch: claude/build-qa-audit-format-kUeo0*

## Architectural Decision: Two-Notebook Split

The sprint notebook (`metajudge_submission_lean.ipynb`, 21 cells) mixed benchmark
definition, 5-model sweeps, Family B experimentation, composite reporting, audit
exports, bridge analysis, and diagnostics in one stateful notebook.

This has been split into two purpose-built notebooks:

### Notebook 1: `metajudge_benchmark.ipynb` (Official Benchmark)
- **6 cells** — imports, schema, dataset, single-item task, batch task, `%choose`
- Uses `kbench.llm` for model selection via Kaggle Task Detail UI
- Runs on the **clean 105-item calibration set**
- Returns a single scalar: mean(1 − Brier)
- No hardcoded model lists, no sweep, no narrative
- `%choose metacog_calibration_clean_v1` in the final cell

### Notebook 2: `metajudge_narrative.ipynb` (Public Narrative)
- **13 cells** with rich markdown narrative
- Loads pre-computed v0.5.5.1 5-model sweep results
- Calibration leaderboard, reliability diagram, per-mechanism heatmap
- Family B leaderboard, action distribution plot
- Pairwise statistical comparisons with Holm-Bonferroni correction
- Brier score forest plot with 95% bootstrap CIs
- Bridge analysis (Spearman confidence-accuracy correlations)
- Confidence distribution violin plots
- Interpretive narrative on what the benchmark reveals

## Official Score Decision

**Calibration-only** (not composite). Rationale:
- Family B has the Gemini Flash gap (n=1) making a fair composite impossible
- Families C-E are designed but not yet instrumented
- The composite score module exists in the package but requires all families
- Calibration-only is clean, defensible, and properly scored with a strictly proper rule

Family B results are prominently featured in the narrative notebook.

## Clean Dataset Decision

**Conservative exclusion** (24 items: 12 cal + 12 FB). See `docs/dataset_cleaning_notes.md`.
- Cal: items where ≥3/5 models wrong (item-level problems)
- FB: items flagged as verify_but_answered (ambiguous action boundaries)
- All mechanisms and actions preserved
- Full-set sensitivity analysis available

## Package Utilities Added

`metajudge/notebook_helpers.py` provides:
- `resolve_data_root()` / `resolve_output_dir()` — cross-environment path resolution
- `load_benchmark_dataset()` / `load_family_b_dataset()` — JSON dataset loaders
- `load_clean_manifest()` / `get_excluded_item_ids()` / `filter_clean_subset()` — clean subset filtering
- `short_model_name()` / `SWEEP_MODELS` — model name utilities
- `format_leaderboard_cal()` / `format_leaderboard_fb()` — result formatting
- `build_answer_key()` — answer key construction

## Gemini Flash / Family B Status

Gemini Flash has only 1 Family B item in v0.5.5.1 data. This is **not** a code bug —
it reflects the model's behavior during the sweep (likely schema compliance issues
with the Family B structured response format).

**Resolution**: Excluded from Family B pairwise comparisons. Noted transparently
in the narrative notebook. Fix will require investigation of Gemini's structured
output behavior with the AbstentionResponse schema (potential Team E follow-up).

## File Manifest

| File | Role |
|------|------|
| `notebooks/metajudge_benchmark.ipynb` | Official benchmark notebook |
| `notebooks/metajudge_narrative.ipynb` | Public narrative notebook |
| `notebooks/metajudge_submission_lean.ipynb` | Sprint notebook (retained as reference) |
| `metajudge/notebook_helpers.py` | Shared utility module |
| `data/clean_subset_manifest.json` | Machine-readable exclusion manifest |
| `docs/dataset_cleaning_notes.md` | Cleaning rationale and coverage tables |
| `docs/notebook_architecture_memo.md` | This document |

## Regeneration Instructions

```bash
# Official benchmark (runs on Kaggle Benchmarks)
# Upload metajudge_benchmark.ipynb, select model via Task Detail UI

# Narrative notebook (local or Kaggle regular)
# Requires v0.5.5.1 results in /tmp/v0551/ or data/results/
jupyter notebook notebooks/metajudge_narrative.ipynb

# Stats report (produces .docx + figures + backgrounder)
python scripts/generate_stats_report.py
```
