# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v0.7.1 (v3.1 post-audit — 51 clean FC items, tolerance + parsing fixes)
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

- 51 clean items (4 excluded post-audit) across two subfamilies:
  - **C1 — Intrinsic** (28 clean): Model prompted to reconsider with no new evidence
  - **C2 — Evidence-assisted** (23 clean): Model given a weak/suggestive evidence snippet
- 4 strata (post-audit): wrong-to-right (20), right-to-right (17), deceptive-trap (9), weak-challenge (5)
- 4 unresolved/contested items excluded (0% T2 accuracy floor effect across all models)
- Scored via **transition-based scoring** with inverted damage:gain penalties (damage > gain) and confidence adjustment
- Config-driven scoring via `config/family_c_scoring.yaml`
- Grounded in Huang et al. (ICLR 2024): intrinsic self-correction fails without external evidence

**Status:** v3.1 post-audit. Kaggle v3.1 packaging done. Audit fixes: numeric tolerance for 2 items, confirmation-without-restatement detection for T2 parsing, 4 unresolved items excluded. See `outputs/audit_family_c_summary.md` for full audit.

### Composite MetaScore

**Current (Families A+B+C):** `compute_composite_score()` with auto-renormalized default weights:

```python
# Effective weights with A+B+C active (D+E absent, auto-excluded):
# Calibration (A):        40.0%
# Abstention (B):         26.7%
# Intrinsic SC (C1):      13.3%
# Evidence SC (C2):       20.0%
```

Weight optimization is a separate pending task — see `docs/stats/stats_review_prompt.md`.

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
  metajudge_benchmark_v3.ipynb    #   Official benchmark v3.1 (A+B+C, post-audit)
  metajudge_narrative_v3.ipynb    #   Narrative analysis v3.1 (A+B+C, post-audit)
  metajudge_benchmark_v2.ipynb    #   V2 benchmark (A+B only, archived)
  metajudge_narrative_v2.ipynb    #   V2 narrative (A+B only, archived)
  metajudge_benchmark.ipynb       #   V1 benchmark (archived)
  metajudge_narrative.ipynb       #   V1 narrative (archived)
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

kaggle-dataset-v3/                #   -> Upload as Kaggle Dataset "metajudge-data" (v3.1 post-audit)
kaggle-package-v3/                #   -> Upload as Kaggle Dataset "metajudge-package" (v3.1 post-audit)

tests/                            #   Unit and integration tests
outputs/                          #   Run artifacts (audit CSVs, figures)
  audit_family_ab_summary.md      #     Family A/B validity audit
  audit_family_c_summary.md       #     Family C validity audit (v0.7.1)
  family_c/                       #     Sweep results, power analysis, pilot data
    sweep_v2/                     #       V2 validation sweep (5 models x 45 items)
    sweep_v2_phase5/              #       Phase 5+6 integrated sweep (56 items x 4 models)
docs/                             #   Scientific documentation
  stats/                          #     Statistical backgrounders + power analysis
planning/                         #   Architecture and sprint plans
  family_c_sprint/                #     Sprint planning docs + v2 checkpoint
```

---

## Notebooks

### Benchmark Notebook (`metajudge_benchmark_v3.ipynb`)
The official Kaggle submission (v3.1 post-audit). Runs all three axes against one model via the Benchmarks SDK.

**Requires two Kaggle Dataset inputs:**
- `metajudge-data-v3` — benchmark items, Family C items, registry (187 entries), clean manifest (from `kaggle-dataset-v3/`)
- `metajudge-package-v3` — metajudge Python package with Family C scoring + confirmation detection (from `kaggle-package-v3/`)

**Produces:**
- `MetaScore` (float) -> Kaggle leaderboard via `%choose metajudge_metacognition_v1`
- `calibration_item_audit.csv` — per-item: model_answer, confidence, is_correct, brier_score
- `family_b_item_audit.csv` — per-item: model_decision, model_answer, is_correct, utility
- `family_c_item_audit.csv` — per-item: t1/t2 answers, correctness, transition, edit similarity
- `benchmark_run_summary.json` — aggregate metrics + per-axis breakdown

**Architecture:** Brier formula inlined for judge transparency. Family B utility scoring, Family C transition scoring, and composite weighting use the metajudge package. T2 answers processed through `resolve_t2_answer()` for confirmation-without-restatement handling.

### Narrative Notebook (`metajudge_narrative_v3.ipynb`)
The full multi-model analysis (v3.1 post-audit). Runs all models across all three families, produces figures and statistical tests.

**Produces:**
- Audit CSVs for all three families (across all models)
- 6 figures: reliability diagram, action distribution, Brier forest plot, mechanism heatmap, FC delta bar chart, FC stratum heatmap
- Leaderboards for each family, composite MetaScore, bootstrap CIs with Holm correction, Spearman bridge analysis

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
`compute_composite_score()` with auto-renormalized default weights over available families. With A+B+C: Calibration 40%, Abstention 27%, C1 13%, C2 20%. Weight optimization pending — see `docs/stats/stats_review_prompt.md`.

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

### Family C — v0.7.0 Kaggle run (55 items x 5 models, pre-audit)

| Model | T1 Acc | T2 Acc | Delta | W→R | R→W | Profile |
|-------|--------|--------|-------|-----|-----|---------|
| Gemini 2.5 Pro | 92.7% | 81.8% | **-10.9%** | 0 | 6 | Heavy damage* |
| Gemini 2.5 Flash | 87.3% | 83.6% | -3.6% | 0 | 2 | Net damage |
| Claude Haiku 4.5 | 87.3% | 83.6% | -3.6% | 2 | 4 | Net damage |
| Claude Sonnet 4 | 83.6% | 81.8% | -1.8% | 0 | 1 | Slight damage |
| DeepSeek V3.1 | 80.0% | 83.6% | **+3.6%** | 3 | 1 | Self-corrector |

*\*Gemini Pro's -10.9% delta is partially inflated by confirmation-without-restatement parsing failures (5/6 FLIP_TO_WRONG cases). See `outputs/audit_family_c_summary.md`.*

**Key findings (v0.7.0, subject to v3.1 audit fixes):**
- Only DeepSeek shows net positive self-correction (+3.6%, 3 W→R, 1 R→W)
- Self-correction ability is highly model-dependent — different model panels produce different rankings (cf. Sprint v2 where Gemini Flash led)
- Deceptive trap items show expected net damage (T1=95.6% → T2=84.4%), validating item design
- Confidence ceiling persists: all models 92-99% with <5pp correct/incorrect gap

**Audit findings (v3.1 fixes applied to dataset/package, re-run pending):**
- 2 items had missing numeric tolerance — 10 forced-wrong gradings corrected
- 4 unresolved items excluded (0% T2, ungradeable) — 55 → 51 clean items
- Confirmation-without-restatement detection added to T2 parsing

### Family C — Sprint v2 (56 items x 4 models, v2 protocol, historical)

| Model | T1 Acc | T2 Acc | Delta | SC Rate | Damage Rate | Profile |
|-------|--------|--------|-------|---------|-------------|---------|
| Gemini 2.5 Flash | 78.6% | 85.7% | **+7.1%** [-2, 18] | 50% (6/12) | 4.5% (2/44) | Self-corrector |
| Claude Sonnet 4.6 | 83.9% | 85.7% | +1.8% [-4, 9] | 22% (2/9) | 2.1% (1/47) | Cautious corrector |
| GPT-5.2 | 87.5% | 85.7% | -1.8% [-7, 4] | 14% (1/7) | 4.1% (2/49) | Slight damage |
| GPT-5 Mini | 85.7% | 83.9% | -1.8% [-5, 0] | 0% (0/8) | 2.1% (1/48) | Net damage |

---

## Start Here

### For day-to-day work
1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`CLAUDE.md`** — Development instructions and hard rules
3. **`outputs/audit_family_c_summary.md`** — Family C validity audit (v0.7.1)
4. **`outputs/audit_family_ab_summary.md`** — Family A/B validity audit
5. **`docs/stats/stats_review_prompt.md`** — Statistical review + weight optimization prompt
6. **`config/family_c_scoring.yaml`** — Scoring weights and thresholds

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
