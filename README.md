# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v0.7.0 (Family C 55-item expansion + v2 sweep + Kaggle v3 packaging)
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

- 55 clean items across two subfamilies:
  - **C1 — Intrinsic** (30 items): Model prompted to reconsider with no new evidence
  - **C2 — Evidence-assisted** (25 items): Model given a weak/suggestive evidence snippet
- 6 strata: wrong-to-right (20), right-to-right (17), deceptive-trap (9), weak-challenge (5), unresolved (2), unresolved-capable (2)
- Scored via **transition-based scoring** with inverted damage:gain penalties (damage > gain) and confidence adjustment
- Config-driven scoring via `config/family_c_scoring.yaml`
- Grounded in Huang et al. (ICLR 2024): intrinsic self-correction fails without external evidence

**Status:** Sprint v2 complete — 55 clean items, v2 sweep protocol (third-person C1, reviewer's note C2, B0 baseline, confidence, edit-distance), Kaggle v3 packaging done. See `outputs/family_c/sweep_v2_phase5/phase6_full_analysis.md` for full analysis and `planning/family_c_sprint/checkpoint_sprint_v2_phase6.md` for sprint checkpoint.

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
    family_c_c1_candidates.json   #     35 C1 candidates (30 clean)
    family_c_c2_candidates.json   #     30 C2 candidates (25 clean)
    SCHEMA.md                     #     Item bundle specification

config/
  benchmark_config.yaml           #   Overall benchmark weights
  family_c_scoring.yaml           #   Family C base scores, damage penalties, ranges

notebooks/
  metajudge_benchmark.ipynb       #   Official benchmark (Kaggle submission)
  metajudge_benchmark_v2.ipynb    #   V2 benchmark with Family C
  metajudge_narrative.ipynb       #   5-model analysis with figures + stats
  metajudge_narrative_v2.ipynb    #   V2 narrative with Family C analysis
  metajudge_submission_lean.ipynb #   Lean submission notebook

scripts/
  pilot_family_c.py               #   Family C model sweep runner (v0.6.x)
  sweep_v2.py                     #   V2 sweep protocol (C1/C2/B0/confidence/edit-distance)
  sweep_v2_single_model.py        #   Single-model sweep helper for parallel execution
  generate_item_v2.py             #   Item generation pipeline (author→adversary→canary→frontier)
  phase6_analysis.py              #   Phase 6 full analysis with bootstrap CIs
  analyze_sweep_v2.py             #   V2 sweep analysis script
  build_kaggle_dataset_v3.py      #   Build kaggle-dataset-v3 from source data
  power_analysis_v062.py          #   Statistical power analysis for Family C
  openrouter/client.py            #   OpenRouter API client for multi-model execution

kaggle-dataset-v3/                #   -> Upload as Kaggle Dataset "metajudge-data" (v3 with Family C)
kaggle-package-v3/                #   -> Upload as Kaggle Dataset "metajudge-package" (v3 with FC scoring)

tests/                            #   Unit and integration tests
outputs/                          #   Run artifacts (audit CSVs, figures)
  family_c/                       #     Sweep results, power analysis, pilot data
    sweep_v2/                     #       V2 validation sweep (5 models x 45 items)
    sweep_v2_phase5/              #       Phase 5+6 integrated sweep (56 items x 4 models)
docs/                             #   Scientific documentation
planning/                         #   Architecture and sprint plans
  family_c_sprint/                #     Sprint planning docs + v2 checkpoint
```

---

## Notebooks

### Benchmark Notebook (`metajudge_benchmark.ipynb` / `metajudge_benchmark_v2.ipynb`)
The official Kaggle submission. Runs all axes against one model via the Benchmarks SDK. V2 adds Family C scoring.

**Requires two Kaggle Dataset inputs:**
- `metajudge-data` — benchmark items, registry, clean manifest, Family C items (from `kaggle-dataset-v3/`)
- `metajudge-package` — metajudge Python package with Family C scoring (from `kaggle-package-v3/`)

**Produces:**
- `MetaScore` (float) -> Kaggle leaderboard via `%choose metajudge_metacognition_v1`
- `calibration_item_audit.csv` — per-item: model_answer, confidence, is_correct, brier_score
- `family_b_item_audit.csv` — per-item: model_decision, model_answer, is_correct, utility
- `benchmark_run_summary.json` — aggregate metrics + per-axis breakdown

**Architecture:** Brier formula and composite weighting are inlined for judge transparency. Family B utility scoring and answer grading use the metajudge package (identical to narrative notebook).

### Narrative Notebook (`metajudge_narrative.ipynb` / `metajudge_narrative_v2.ipynb`)
The full multi-model analysis. Runs all models, produces figures and statistical tests. V2 adds Family C analysis.

**Produces:**
- Same audit CSVs (across all models)
- 4 figures saved to disk: reliability diagram, action distribution, Brier forest plot, mechanism heatmap
- Leaderboards, bootstrap CIs with Holm correction, Spearman bridge analysis

### Lean Submission Notebook (`metajudge_submission_lean.ipynb`)
Minimal submission notebook — scoring logic lives in the metajudge package.

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
Transition-based scoring classifies each item into one of six outcomes: `correction_gain`, `maintain_correct`, `neutral_revision`, `damage`, `stubborn_wrong`, `failed_revision`. Base scores differ between C1 (harsh on damage: -0.40) and C2 (more forgiving: -0.25, but -0.40 for misleading evidence). Confidence adjustment in [-0.15, +0.10] applied per transition. Raw scores rescaled from [-0.55, 0.30] to [0, 1]. V2 protocol uses third-person framing for C1 and reviewer's note framing for C2, with B0 re-answering baseline to separate genuine correction from re-sampling. See `planning/family_c_sprint/03_scoring_blueprint.md` for worked examples.

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

### Family C — Sprint v2 (56 items x 4 models, v2 protocol)

**T2-T1 accuracy delta** with bootstrap 95% CIs (10,000 resamples):

| Model | T1 Acc | T2 Acc | Delta | SC Rate | Damage Rate | Profile |
|-------|--------|--------|-------|---------|-------------|---------|
| Gemini 2.5 Flash | 78.6% | 85.7% | **+7.1%** [-2, 18] | 50% (6/12) | 4.5% (2/44) | Self-corrector |
| Claude Sonnet 4.6 | 83.9% | 85.7% | +1.8% [-4, 9] | 22% (2/9) | 2.1% (1/47) | Cautious corrector |
| GPT-5.2 | 87.5% | 85.7% | -1.8% [-7, 4] | 14% (1/7) | 4.1% (2/49) | Slight damage |
| GPT-5 Mini | 85.7% | 83.9% | -1.8% [-5, 0] | 0% (0/8) | 2.1% (1/48) | Net damage |

**B0 re-answering baseline** (WR items only — tests whether the review protocol adds value beyond re-sampling):

| Model | T2 Acc | B0 Acc | C1-B0 Delta |
|-------|--------|--------|-------------|
| Gemini 2.5 Flash | 84% | 64% | **+20%** |
| Others | 84% | 84-88% | 0% to -4% |

**Key findings:**
- Gemini Flash is the strongest self-corrector: +7.1% delta with +20% C1-B0 — genuine metacognitive correction beyond re-sampling
- GPT-5 Mini shows net damage: -1.8% delta, 0% SC rate — the review protocol introduces R->W errors without any W->R corrections
- Edit-distance reveals revision strategies: Sonnet/Gemini do near-complete rewrites (mean sim 0.18-0.20); GPT-5 Mini does targeted edits (38% in 0.4-0.9 range)
- Confidence is uniformly high (92-99%) with <5pp correct/incorrect gap across all models — consistent with Mei et al. (2025) on reasoning model overconfidence

**Statistical caveats:**
- No individual T2-T1 delta reaches significance at alpha=0.05 (CIs all cross zero)
- SC rate CIs remain wide (32-75%) due to small wrong-on-T1 denominators (7-12 items per model)
- 75-150 total items needed for defensible SC rate comparisons

---

## Start Here

### For day-to-day work
1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`CLAUDE.md`** — Development instructions and hard rules
3. **`planning/family_c_sprint/checkpoint_sprint_v2_phase6.md`** — Sprint v2 checkpoint (current state)
4. **`data/family_c/SCHEMA.md`** — Item bundle specification for Family C
5. **`config/family_c_scoring.yaml`** — Scoring weights and thresholds
6. **`outputs/family_c/sweep_v2_phase5/phase6_full_analysis.md`** — Full Phase 6 analysis with bootstrap CIs

### For theoretical background (not needed for task execution)
7. **`docs/metacognition_assessor_recommendations.md`** — Cross-family architecture rationale
8. **`docs/metacognition_literature_report.md`** — 80+ paper annotated bibliography
9. **`planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md`** — Family C theoretical analysis
10. **`docs/references.bib`** — Full reference database

### For historical context (read only if needed)
11. **`planning/v1_architecture.md`** — Original Family A implementation plan
12. **`outputs/family_c/sweep_analysis_v062.md`** — Original v0.6.2 5-model sweep analysis

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
pytest tests/ --tb=short      # Test
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
