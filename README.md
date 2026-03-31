# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v0.6.2 (Family C 5-model sweep)
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
- Scored via **UWAA** (Utility-Weighted Action Accuracy) with 5x4 payoff matrix
- Corrective answers on false-premise items credited; acceptable alternatives awarded partial credit

### Axis III — Self-Correction (Control)
*Can the model detect and repair its own errors?*

- 45 clean items across two subfamilies:
  - **C1 — Intrinsic** (25 items): Model prompted to reconsider with no new evidence
  - **C2 — Evidence-assisted** (20 items): Model given a weak/suggestive evidence snippet
- 5 strata: wrong-to-right, right-to-right, weak-challenge, unresolved, deceptive-trap
- Scored via **transition-based scoring** with inverted damage:gain penalties (damage > gain) and confidence adjustment
- Config-driven scoring via `config/family_c_scoring.yaml`
- Grounded in Huang et al. (ICLR 2024): intrinsic self-correction fails without external evidence

**Status:** 5-model sweep complete. See `outputs/family_c/sweep_analysis_v062.md` for full analysis and `outputs/family_c/power_analysis_v062.md` for statistical power assessment.

### Composite MetaScore

**Current (Families A+B):** `MetaScore = 0.60 x Calibration + 0.40 x UWAA`

**Provisional (with Family C):** Weights will be rebalanced after Family C promotion:

```python
WEIGHTS = {
    "calibration": 0.30,
    "abstention_verification": 0.20,
    "intrinsic_self_correction": 0.10,
    "evidence_assisted_correction": 0.15,
    "grounding_sensitivity": 0.10,      # V2
    "control_policy_adaptation": 0.15,  # V2
}
```

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
    self_correction_v2.py         #   Family C transition scoring, confidence adjustment
    statistics.py                 #   Bootstrap CIs, Holm, McNemar, Spearman
  schemas/                        #   Response dataclasses
  tasks/
    self_correction_v2.py         #   Family C task definitions (C1/C2 prompts, grading)

data/                             # Production datasets
  metajudge_benchmark_v1.json     #   117-item calibration set (V4.2)
  family_b_pilot_v2.json          #   84-item Family B set
  adjudication_registry.json      #   132 grading rules (117 cal + 15 FB)
  clean_subset_manifest.json      #   Exclusion lists for clean subset
  family_c/                       #   Family C item bundles
    family_c_c1_candidates.json   #     25 C1 items
    family_c_c2_candidates.json   #     20 C2 items
    SCHEMA.md                     #     Item bundle specification

config/
  benchmark_config.yaml           #   Overall benchmark weights
  family_c_scoring.yaml           #   Family C base scores, damage penalties, ranges

notebooks/
  metajudge_benchmark.ipynb       #   Official benchmark (Kaggle submission)
  metajudge_narrative.ipynb       #   5-model analysis with figures + stats

scripts/
  pilot_family_c.py               #   Family C model sweep runner
  power_analysis_v062.py          #   Statistical power analysis for Family C
  openrouter/client.py            #   OpenRouter API client for multi-model execution

kaggle-dataset/                   #   -> Upload as Kaggle Dataset "metajudge-data"
kaggle-package/                   #   -> Upload as Kaggle Dataset "metajudge-package"

tests/                            #   Unit and integration tests (409)
outputs/                          #   Run artifacts (audit CSVs, figures)
  family_c/                       #     Sweep results, power analysis, pilot data
docs/                             #   Scientific documentation
planning/                         #   Architecture and sprint plans
  family_c_sprint/                #     Current sprint: 17 planning docs for Family C
```

---

## Notebooks

### Benchmark Notebook (`metajudge_benchmark.ipynb`)
The official Kaggle submission. Runs both axes against one model via the Benchmarks SDK.

**Requires two Kaggle Dataset inputs:**
- `metajudge-data` — benchmark items, registry, clean manifest (from `kaggle-dataset/`)
- `metajudge-package` — metajudge Python package (from `kaggle-package/`)

**Produces:**
- `MetaScore` (float) -> Kaggle leaderboard via `%choose metajudge_metacognition_v1`
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
Per-item: `1 - (confidence - outcome)^2` (Brier 1950, strictly proper).
Grading: 8-rule registry-driven engine (`grading_v2.py`) with tolerance-aware numeric, alias, tri-label, code-output, and fraction grading. No LLM judge.

### Selective Abstention (Axis II)
Primary metric: UWAA = `(mean_utility + 1) / 2`, normalised to [0, 1].
Utility matrix maps (model action x gold action) -> [-1, +1].
Corrective non-answers on false-presupposition items receive +0.5.
Acceptable alternative actions receive at least +0.3 partial credit.

### Self-Correction (Axis III)
Transition-based scoring classifies each item into one of six outcomes: `correction_gain`, `maintain_correct`, `neutral_revision`, `damage`, `stubborn_wrong`, `failed_revision`. Base scores differ between C1 (harsh on damage: -0.40) and C2 (more forgiving: -0.25, but -0.40 for misleading evidence). Confidence adjustment in [-0.15, +0.10] applied per transition. Raw scores rescaled from [-0.55, 0.30] to [0, 1]. See `planning/family_c_sprint/03_scoring_blueprint.md` for worked examples.

### Composite
Current: `MetaScore = 0.60 x mean(1-Brier) + 0.40 x UWAA`
After Family C promotion: weights rebalanced per `config/benchmark_config.yaml`.

---

## 5-Model Sweep Results

### Families A+B (v0.5.5.1.1 clean set)

| Model | Brier | Accuracy | UWAA | MetaScore |
|-------|-------|----------|------|-----------|
| Gemini 2.5 Flash | 0.9606 | 95.2% | 0.7625 | 0.8813 |
| DeepSeek V3.1 | 0.8826 | 85.7% | 0.8042 | 0.8512 |
| Gemini 2.5 Pro | 0.9417 | 94.3% | 0.7125 | 0.8500 |
| Claude Sonnet 4 | 0.8843 | 86.7% | 0.6972 | 0.8095 |
| Claude Haiku 4.5 | 0.8595 | 81.0% | 0.7104 | 0.7999 |

### Family C (v0.6.2 — 5-model, 45 clean items)

**T2-T1 accuracy delta** (recommended headline metric — uses all 45 paired observations):

| Model | T1 Acc | T2 Acc | Delta | W->R | R->W | Profile |
|-------|--------|--------|-------|------|------|---------|
| DeepSeek Chat | 80.0% | 88.9% | **+8.9pp*** | 4 | 0 | Self-corrector |
| GPT-4.1 | 84.4% | 88.9% | +4.4pp | 2 | 0 | Moderate |
| Claude Sonnet 4.5 | 91.1% | 93.3% | +2.2pp | 2 | 1 | Cautious corrector |
| Grok 3 Mini | 88.9% | 88.9% | +0.0pp | 0 | 0 | Rigid (never revises) |
| Gemini 2.5 Pro | — | — | — | — | — | *Excluded (verbose T2 grading artifacts)* |

*\*Only statistically significant result at alpha=0.05 (bootstrap CI: [+2.2, +17.8]pp)*

**Key findings:**
- DeepSeek is the strongest self-corrector (+8.9pp net improvement, 4 W->R corrections, 0 damage)
- Grok shows zero revision behavior — validates the "stubborn baseline" from Huang et al.
- Claude has the highest T1 accuracy (91.1%) but only modest self-correction (+2.2pp), with 1 damage event
- 64% of items (29/45) differentiate at least 2 models; 22% (10/45) differentiate 3+ models

**Statistical caveats** (see `outputs/family_c/power_analysis_v062.md`):
- SC rate CIs are 40-70% wide due to small wrong-on-T1 denominators (4-9 items per model)
- McNemar pairwise: 0/6 model pairs significant at alpha=0.05
- 75-150 total items needed for defensible SC rate comparisons
- Rescaling compression: `_RAW_MAX=0.30` clamps 2/6 transitions to scaled 1.0, collapsing top-end discrimination

---

## Start Here

### For day-to-day work
1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`CLAUDE.md`** — Development instructions and hard rules
3. **`planning/family_c_sprint/07_sprint_checklist.md`** — Current sprint execution plan
4. **`data/family_c/SCHEMA.md`** — Item bundle specification for Family C
5. **`config/family_c_scoring.yaml`** — Scoring weights and thresholds
6. **`outputs/family_c/power_analysis_v062.md`** — Statistical power assessment

### For theoretical background (not needed for task execution)
7. **`docs/metacognition_assessor_recommendations.md`** — Cross-family architecture rationale
8. **`docs/metacognition_literature_report.md`** — 80+ paper annotated bibliography
9. **`planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md`** — Family C theoretical analysis
10. **`docs/references.bib`** — Full reference database

### For historical context (read only if needed)
11. **`planning/v1_architecture.md`** — Original Family A implementation plan
12. **`outputs/family_c/sweep_analysis_v062.md`** — Full 5-model sweep analysis with per-model breakdowns

---

## Theoretical Grounding

MetaJudge is grounded in the distinction between metacognitive monitoring and control (Nelson & Narens, 1990), operationalized through the report/withhold paradigm (Koriat & Goldsmith, 1996). The benchmark tests whether LLMs exhibit the selective reporting behavior that characterizes metacognitive competence in humans. Family C extends this to the control axis, testing whether models can detect and repair errors — a capacity that Huang et al. (ICLR 2024) showed rarely occurs without external evidence.

### Key References
- **Nelson & Narens (1990)** — Monitoring vs. control architecture
- **Koriat & Goldsmith (1996)** — Report/withhold paradigm for strategic accuracy regulation
- **Huang et al. (ICLR 2024)** — Intrinsic self-correction often fails without external evidence
- **Burnell et al. (2026)** — DeepMind cognitive taxonomy identifying metacognition as a key evaluation gap
- **Brier (1950)** — Strictly proper scoring rule for probabilistic forecasts
- **Gneiting & Raftery (2007)** — Theory of strictly proper scoring rules

For the full bibliography, see `docs/metacognition_literature_report.md`.

---

## Dev Commands

```bash
pip install -e ".[dev]"       # Install
pytest tests/ --tb=short      # Test (409)
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
