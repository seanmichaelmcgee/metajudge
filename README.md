# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v0.6.1 (Family C pilot)
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

### Axis III — Self-Correction (Control) *[current sprint]*
*Can the model detect and repair its own errors?*

- 35 seed items (28 clean after 2-model pilot triage) across two subfamilies:
  - **C1 — Intrinsic:** Model prompted to reconsider with no new evidence (neutral or metacognitive challenge)
  - **C2 — Evidence-assisted:** Model given a weak/suggestive evidence snippet and asked to reconsider
- 5 strata: wrong-to-right, right-to-right, weak-challenge, unresolved, deceptive-trap
- Scored via **transition-based scoring** with inverted damage:gain penalties (damage > gain) and confidence adjustment
- Config-driven scoring via `config/family_c_scoring.yaml`
- Grounded in Huang et al. (ICLR 2024): intrinsic self-correction fails without external evidence

**Status:** 2-model pilot complete (deepseek-chat, grok-3-mini). 5-model panel run pending. See `outputs/family_c/pilot_report_v061.md` for pilot results.

### Composite MetaScore

**Current (Families A+B):** `MetaScore = 0.60 x Calibration + 0.40 x UWAA`

**Provisional (with Family C):** Weights will be rebalanced after Family C validation:

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
    family_c_c1_candidates.json   #     15 C1 items (13 clean)
    family_c_c2_candidates.json   #     20 C2 items (15 clean)
    SCHEMA.md                     #     Item bundle specification

config/
  benchmark_config.yaml           #   Overall benchmark weights
  family_c_scoring.yaml           #   Family C base scores, damage penalties, ranges

notebooks/
  metajudge_benchmark.ipynb       #   Official benchmark (Kaggle submission)
  metajudge_narrative.ipynb       #   5-model analysis with figures + stats

scripts/
  pilot_family_c.py               #   Family C model sweep runner
  openrouter/client.py            #   OpenRouter API client for multi-model execution

kaggle-dataset/                   #   -> Upload as Kaggle Dataset "metajudge-data"
kaggle-package/                   #   -> Upload as Kaggle Dataset "metajudge-package"

tests/                            #   Unit and integration tests (290+)
outputs/                          #   Run artifacts (audit CSVs, figures)
  family_c/                       #     Family C pilot outputs (JSONL, CSV, report)
docs/                             #   Scientific documentation (see docs/README.md)
planning/                         #   Architecture and sprint plans (see planning/README.md)
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

### Self-Correction (Axis III) *[current sprint]*
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

### Family C Pilot (v0.6.1 — 2-model, 35 items)

| Model | Parse Rate | Mean Scaled Score | Damage Rate | Revision Rate |
|-------|-----------|-------------------|-------------|---------------|
| deepseek-chat | 35/35 | 0.9203 | 2.9% | 11.4% |
| grok-3-mini | 35/35 | 0.9849 | 0.0% | 0.0% |

Key finding: Grok never revised (0% revision rate), validating the "stubborn baseline" from Huang et al. DeepSeek showed 1 damage event on a deceptive-trap item, validating that construct. Full 5-model results pending.

---

## Start Here

### For day-to-day work
1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`CLAUDE.md`** — Development instructions and hard rules
3. **`planning/family_c_sprint/07_sprint_checklist.md`** — Current sprint execution plan
4. **`data/family_c/SCHEMA.md`** — Item bundle specification for Family C
5. **`config/family_c_scoring.yaml`** — Scoring weights and thresholds

### For theoretical background (not needed for task execution)
6. **`docs/metacognition_assessor_recommendations.md`** — Cross-family architecture rationale
7. **`docs/metacognition_literature_report.md`** — 80+ paper annotated bibliography
8. **`planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md`** — Family C theoretical analysis
9. **`docs/references.bib`** — Full reference database

### For historical context (read only if needed)
10. **`planning/archive/v1_architecture.md`** — Original Family A implementation plan
11. **`docs/archive/`** — Superseded design docs, sprint reports, orchestrator briefs

See `docs/README.md` and `planning/README.md` for complete document indexes.

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
