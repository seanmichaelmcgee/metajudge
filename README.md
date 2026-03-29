# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v0.5.5.1
**Deadline:** April 16, 2026
**Submission:** Kaggle Community Benchmark + Writeup (1,500 words)

---

## What This Measures

MetaJudge evaluates whether language models can **track the reliability of their own outputs** (monitoring) and **act appropriately on that information** (control). This maps directly to the two-component model of metacognition established in cognitive psychology (Nelson & Narens, 1990; Flavell, 1979).

### Axis I — Confidence Calibration (Monitoring)
*Does the model know when it is likely correct or incorrect?*

- 105 clean items (12 excluded) across 10 adversarial mechanisms
- Stratified into three tiers: clean objective (Stratum A), objective-but-brittle (B), and metacognitive traps (C)
- Scored via **Brier rule** — strictly proper: `1 - (confidence - outcome)²`
- Correctness graded by deterministic 8-rule engine (no LLM judge)

### Axis II — Selective Abstention (Control)
*Given uncertainty, does the model choose the right epistemic action?*

- 72 clean items (12 excluded) testing four control actions: **answer**, **clarify**, **verify**, **abstain**
- 22 false-presupposition items testing corrective non-answer behavior
- Scored via **UWAA** (Utility-Weighted Action Accuracy) with 5×4 payoff matrix
- Corrective answers on false-premise items credited; acceptable alternatives awarded partial credit

### Composite MetaScore

**MetaScore = 0.60 × Calibration + 0.40 × UWAA**

The 60/40 weighting reflects the monitoring-control hierarchy (Nelson & Narens, 1990): accurate self-assessment is prerequisite to appropriate action selection.

---

## Repository Structure

```
SOUL.md                           # Governing principles (read first)
CLAUDE.md                         # Development instructions

metajudge/                        # Python package — scoring, grading, schemas
  scoring/
    grading_v2.py                 #   8-rule deterministic adjudication engine
    calibration_metrics.py        #   Brier, ECE, overconfidence rate
    abstention_metrics.py         #   UWAA, utility matrix, score_family_b_item_v2
    statistics.py                 #   Bootstrap CIs, Holm, McNemar, Spearman
  schemas/                        #   Response dataclasses
  tasks/                          #   Task implementations

data/                             # Production datasets
  metajudge_benchmark_v1.json     #   117-item calibration set (V4.2)
  family_b_pilot_v2.json          #   84-item Family B set
  adjudication_registry.json      #   132 grading rules (117 cal + 15 FB)
  clean_subset_manifest.json      #   Exclusion lists for clean subset

notebooks/
  metajudge_benchmark.ipynb       #   Official benchmark (Kaggle submission)
  metajudge_narrative.ipynb       #   5-model analysis with figures + stats

kaggle-dataset/                   #   → Upload as Kaggle Dataset "metajudge-data"
kaggle-package/                   #   → Upload as Kaggle Dataset "metajudge-package"

tests/                            #   Unit and integration tests (290+)
docs/                             #   Scientific documentation
planning/                         #   Architecture plans and fix plans
outputs/                          #   Run artifacts (audit CSVs, figures)
```

---

## Notebooks

### Benchmark Notebook (`metajudge_benchmark.ipynb`)
The official Kaggle submission. Runs both axes against one model via the Benchmarks SDK.

**Requires two Kaggle Dataset inputs:**
- `metajudge-data` — benchmark items, registry, clean manifest (from `kaggle-dataset/`)
- `metajudge-package` — metajudge Python package (from `kaggle-package/`)

**Produces:**
- `MetaScore` (float) → Kaggle leaderboard via `%choose metajudge_metacognition_v1`
- `calibration_item_audit.csv` — per-item: model_answer, confidence, is_correct, brier_score
- `family_b_item_audit.csv` — per-item: model_decision, model_answer, is_correct, utility
- `benchmark_run_summary.json` — aggregate metrics + per-axis breakdown

**Architecture:** Brier formula and composite weighting are inlined for judge transparency. Family B utility scoring and answer grading use the metajudge package (identical to narrative notebook).

### Narrative Notebook (`metajudge_narrative.ipynb`)
The full 5-model analysis. Runs all models, produces figures and statistical tests.

**Produces:**
- Same audit CSVs (across all 5 models)
- 4 figures saved to disk: reliability diagram, action distribution, Brier forest plot, mechanism heatmap
- Leaderboards, bootstrap CIs with Holm correction, Spearman bridge analysis

---

## Scoring

### Calibration (Axis I)
Per-item: `1 − (confidence − outcome)²` (Brier 1950, strictly proper).
Grading: 8-rule registry-driven engine (`grading_v2.py`) with tolerance-aware numeric, alias, tri-label, code-output, and fraction grading. No LLM judge.

### Selective Abstention (Axis II)
Primary metric: UWAA = `(mean_utility + 1) / 2`, normalised to [0, 1].
Utility matrix maps (model action × gold action) → [-1, +1].
Corrective non-answers on false-presupposition items receive +0.5.
Acceptable alternative actions receive at least +0.3 partial credit.

### Composite
`MetaScore = 0.60 × mean(1-Brier) + 0.40 × UWAA`

---

## 5-Model Sweep

| Model | 1-Brier | Accuracy | UWAA | MetaScore |
|-------|---------|----------|------|-----------|
| Gemini 2.5 Pro | 0.885 | 87% | — | — |
| Gemini 2.5 Flash | 0.882 | 87% | 0.744 | — |
| DeepSeek V3.1 | 0.832 | 75% | — | — |
| Claude Sonnet 4 | 0.816 | 78% | — | — |
| Claude Haiku 4.5 | 0.781 | 72% | — | — |

*Calibration from v0.5.1. Family B UWAA only available for Flash (others pending re-run with corrected grading). Full 5-model results will be produced on Kaggle.*

---

## Start Here

1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`docs/metacognition_assessor_recommendations.md`** — Cross-family architecture
3. **`docs/metacognition_literature_report.md`** — 80+ paper annotated bibliography
4. **`planning/v1_architecture.md`** — Implementation plan

---

## Theoretical Grounding

MetaJudge is grounded in the distinction between metacognitive monitoring and control (Nelson & Narens, 1990), operationalized through the report/withhold paradigm (Koriat & Goldsmith, 1996). The benchmark tests whether LLMs exhibit the selective reporting behavior that characterizes metacognitive competence in humans.

### Key References
- **Nelson & Narens (1990)** — Monitoring vs. control architecture
- **Koriat & Goldsmith (1996)** — Report/withhold paradigm for strategic accuracy regulation
- **Burnell et al. (2026)** — DeepMind cognitive taxonomy identifying metacognition as a key evaluation gap
- **Brier (1950)** — Strictly proper scoring rule for probabilistic forecasts
- **Gneiting & Raftery (2007)** — Theory of strictly proper scoring rules

For the full bibliography, see `docs/metacognition_literature_report.md`.

---

## Dev Commands

```bash
pip install -e ".[dev]"       # Install
pytest tests/ --tb=short      # Test (290+)
ruff check .                  # Lint
black .                       # Format
mypy metajudge/ --ignore-missing-imports  # Type check
```

---

## Competition Context

Built for the [Kaggle Measuring Progress Toward AGI](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon. The companion paper (Burnell et al., 2026) identifies metacognition as one of five cognitive abilities where the evaluation gap is largest.

**Rubric:** 50% dataset quality, 30% novelty/insight/discriminatory power, 20% writeup.

---

## License

MIT
