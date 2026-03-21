# MetaJudge Kaggle I/O Contract

## Inputs (from /kaggle/input/)
All serious Kaggle runs consume:

| Input | File | Format | Required |
|-------|------|--------|----------|
| Benchmark dataset | metajudge_benchmark_v1.json | JSON array (102 items) | Yes |
| Adjudication registry | adjudication_registry.json | JSON array (102 specs) | Yes |
| metajudge package | metajudge/ directory | Python package | Yes |

### Kaggle Dataset Slug
Upload as a single Kaggle Dataset: `metajudge-benchmark`
Expected paths:
- `/kaggle/input/metajudge-benchmark/metajudge_benchmark_v1.json`
- `/kaggle/input/metajudge-benchmark/adjudication_registry.json`
- `/kaggle/input/metajudge-benchmark/metajudge/` (package directory)

### Fallback
When running locally, the notebook falls back to `data/` for datasets and assumes the package is installed.

## Outputs (to /kaggle/working/)
Every serious run writes:

| Output | File | Format | Purpose |
|--------|------|--------|---------|
| Run summary | run_summary.json | JSON | Benchmark version, item count, grading engine, rules |
| Model scores | model_scores.csv | CSV | Per-model headline scores (when sweep runs) |
| Item audit | item_audit.csv | CSV | Per-item per-model: answer, confidence, correct, score |
| Diagnostics | diagnostics.json | JSON | C1-C5 success criteria, mechanism breakdowns |

### Minimum required output
For any submission run: `run_summary.json`
For sweep/audit runs: all four files

### Family B Outputs
When Family B (selective abstention) cells are enabled, run_summary includes:
```json
{
  "families": {
    "calibration": {"items": 102, "version": "V4.2"},
    "abstention": {"items": 48, "version": "pilot_v2"}
  }
}
```

## Notebook Cell Contract

| Cell | Input | Output | Side Effects |
|------|-------|--------|-------------|
| 0 | — | — | Markdown only |
| 1 | Kaggle SDK | SDK handle, grading_v2 imports | Print env info |
| 2 | — | CalibrationResponse schema | — |
| 3 | JSON files from /kaggle/input/ | dataset DataFrame, ANSWER_KEY, REGISTRY | — |
| 4 | REGISTRY | — | Assert 102/102 gold self-adj, 17 per-rule tests |
| 5 | dataset, REGISTRY | Single-item task result | Smoke test print |
| 6 | dataset | Batch task result, headline score | Print results |
| 7 | dataset | Sweep DataFrames | Print per-model results |
| 8 | — | run_summary.json | Write to /kaggle/working/ |
| 9 | — | — | Markdown separator: Family B section |
| 10 | metajudge package | abstention_metrics imports, Family B dataset | Print env info |
| 11 | — | AbstentionResponse schema | — |
| 12 | UWAA scoring, action F1 | — | Assert scoring self-tests |
| 13 | Family B dataset | Single-item abstention result | Smoke test print |
| 14 | Family B dataset | Batch abstention results | Print results |
| 15 | Calibration + abstention scores | Composite score | Print composite |
| 16 | — | — | %choose metacog_calibration_v1_batch |
