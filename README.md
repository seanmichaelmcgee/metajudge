# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v6.1 (4-task Kaggle Benchmark, dual-run stochasticity, resilient evaluation)
**Deadline:** April 16, 2026
**Submission:** Kaggle Community Benchmark + Writeup (1,500 words)

---

## What This Measures

MetaJudge evaluates whether language models can **track the reliability of their own outputs** (monitoring) and **act appropriately on that information** (control). This maps directly to the two-process model of metacognition established by Nelson & Narens (1990).

### Confidence Calibration — Monitoring
*Does the model know when it is likely correct or incorrect?*

- 105 clean items (12 excluded) across 10 adversarial mechanisms
- Scored via **Brier rule** — strictly proper: `1 - (confidence - outcome)²`
- Correctness graded by deterministic 8-rule engine (no LLM judge)

### Selective Abstention — Control
*Given uncertainty, does the model choose the right epistemic action?*

- 72 clean items (12 excluded) testing four control actions: **answer**, **clarify**, **verify**, **abstain**
- 22 false-presupposition items testing corrective non-answer behavior
- Scored via **UWAA** (Utility-Weighted Action Accuracy) with 5×4 payoff matrix
- Dual-run stochasticity check (Run 2 independent, display only)

### Intrinsic Self-Correction C1 — Control
*Can the model detect and repair its own errors without external evidence?*

- 28 clean items: model answers, then receives a neutral third-person review prompt
- 4 strata: wrong-to-right, right-to-right, deceptive-trap, weak-challenge
- Grounded in Huang et al. (ICLR 2024) and Tyen et al. (2024)
- Dual-run stochasticity check

### Evidence-Assisted Self-Correction C2 — Control
*Does external evidence help or damage the model's performance?*

- 23 clean items: model answers, then receives a reviewer's note with evidence that may be accurate, misleading, or irrelevant
- Same transition-based scoring as C1 with config-driven asymmetric damage penalties
- Dual-run stochasticity check

**Scoring:** Transition-based scoring classifies each item as correction_gain, maintain_correct, neutral_revision, damage, stubborn_wrong, or failed_revision. Damage costs more than correction gains (config via `config/family_c_scoring.yaml`).

### Composite MetaScore

**MetaScore = mean(norm_A, norm_B, norm_C1, norm_C2)** — platform-averaged anchor-normalized scores.

Each task notebook returns one anchor-normalized float. The Kaggle platform averages the 4 scores into the leaderboard MetaScore. Equal weighting justified by Dawes (1979) and Davis-Stober (2011). Anchor normalization follows BIG-Bench (Srivastava et al., 2023).

See `docs/benchmark/v5_theoretical_backgrounder.md` for the full two-process framework, task mapping, and statistical methodology.

---

## Repository Structure

```
SOUL.md                           # Governing principles (read first)
CLAUDE.md                         # Development instructions

metajudge/                        # Python package — 7 modules, clean
  __init__.py                     #   Package root, version 6.1
  scoring/
    __init__.py
    grading_v2.py                 #   8-rule deterministic adjudication engine
    abstention_metrics.py         #   UWAA, utility matrix, score_family_b_item_v2
    self_correction_v2.py         #   Family C transition scoring, confidence adjustment
  tasks/
    __init__.py
    self_correction_v2.py         #   Family C task definitions (C1/C2 prompts, grading)

data/                             # Production datasets
  metajudge_benchmark_v1.json     #   117-item calibration set
  family_b_pilot_v2.json          #   84-item Family B set
  adjudication_registry.json      #   132 grading rules (117 cal + 15 FB)
  clean_subset_manifest.json      #   Exclusion lists for clean subset
  family_c/                       #   Family C item bundles
    family_c_c1_candidates.json   #     35 C1 candidates (28 clean)
    family_c_c2_candidates.json   #     30 C2 candidates (23 clean)
    SCHEMA.md                     #     Item bundle specification

config/
  benchmark_config.yaml           #   Overall benchmark weights
  family_c_scoring.yaml           #   Family C base scores, damage penalties, ranges

notebooks/                        #   v6.1 task notebooks (Kaggle Benchmark)
  metajudge_calibration.ipynb     #   Calibration — Monitoring, returns anchor-normalized Brier
  metajudge_abstention.ipynb      #   Abstention — Control, dual-run, returns normalized UWAA
  metajudge_sc_c1.ipynb           #   SC C1 — Control, dual-run, returns normalized SC delta
  metajudge_sc_c2.ipynb           #   SC C2 — Control, dual-run, returns normalized SC delta
  archive/                        #   Prior versions (v4.1, v5.1, v1–v3.2)

scripts/
  generate_audit_docx.py          #   Per-model .docx audit report generator (v6.1)
  generate_qa_audit_docx.py       #   Legacy multi-model QA audit report (v0.5.5.1)
  gold_answer_justification_prompt.md  # Prompt for generating gold answer justifications
  audit_benchmark_v32.py          #   Unified benchmark audit (re-grade + composite validation)
  extract_wrong_for_llm_audit.py  #   Extract wrong-graded items for LLM semantic audit
  pilot_family_c.py               #   Family C model sweep runner (v0.6.x)
  openrouter/client.py            #   OpenRouter API client for multi-model execution

kaggle-dataset-v3/                #   -> Upload as Kaggle Dataset "metajudge-data-v6-1"
kaggle-package-v3/                #   -> Upload as Kaggle Dataset "metajudge-package-v6-1" (7 modules + metadata)

tests/                            #   Unit and integration tests
outputs/                          #   Run artifacts (audit CSVs, figures, justifications)
  metajudge_v51_gold_answer_justifications.md  # 266 item justifications (A+B+C)
docs/                             #   Scientific documentation
  benchmark/                      #     v5 theoretical backgrounder, LLM audit prompt
  audit/                          #     Audit framework (two-layer: automated + LLM semantic)
  stats/                          #     Statistical backgrounders, composite methodology
planning/                         #   Architecture and sprint plans
  family_c_sprint/                #     Sprint planning docs + v2 checkpoint
```

---

## Notebooks

### v6.1 Task Notebooks (Kaggle Benchmark)

4 independent task notebooks. Each evaluates one model via `kbench.llm` and returns one anchor-normalized `float`. The Kaggle platform averages the 4 scores into the leaderboard MetaScore.

| # | Notebook | Task | Process | Items | Returns |
|---|----------|------|---------|-------|---------|
| 1 | `metajudge_calibration.ipynb` | `metajudge_calibration_v61` | Monitoring | 105 | normalized 1-Brier |
| 2 | `metajudge_abstention.ipynb` | `metajudge_abstention_v61` | Control | 72 | normalized UWAA |
| 3 | `metajudge_sc_c1.ipynb` | `metajudge_sc_c1_v61` | Control | 28 | normalized SC delta |
| 4 | `metajudge_sc_c2.ipynb` | `metajudge_sc_c2_v61` | Control | 23 | normalized SC delta |

**Requires two Kaggle Dataset inputs:**
- `metajudge-data-v6-1` — benchmark items, Family C items, registry, clean manifest
- `metajudge-package-v6-1` — clean 7-module scoring package

**Each notebook produces:**
- Per-item audit CSV with model slug in filename
- Full responses JSON with metadata header (model, version, timestamp, items_scored/attempted)
- One `float` score → Kaggle leaderboard

**v6.1 features:**
- Dual-run stochasticity check (B, C1, C2): Run 1 cached/scored, Run 2 independent/display-only
- Resilient evaluation: Run 2 wrapped in try/except, item_id matching (not positional), 80% gate on stochasticity display
- Run 1 failure warning: transparent reporting when items fail (runaway token generation)
- Damage item listing (C1, C2): names each damaged item in notebook output
- Score range interpretation line across independent runs

**Audit reports:** `scripts/generate_audit_docx.py` produces per-model .docx audit reports from notebook outputs. Shows summary tables, stochasticity comparison, and item-by-item detail with gold answer justifications, accepted forms, and transition coloring. Failed items (evaluation errors) displayed transparently.

### Archived Notebooks (`notebooks/archive/`)
Prior versions (v4.1, v5.1, v1–v3.2). Kept for fallback and historical reference.

---

## Scoring

### Calibration (Monitoring)
Per-item: `1 - (confidence - outcome)^2` (Brier 1950, strictly proper).
Grading: 8-rule registry-driven engine (`grading_v2.py`) with tolerance-aware numeric, alias, tri-label, code-output, and fraction grading. No LLM judge.

### Selective Abstention (Control)
Primary metric: UWAA = `(mean_utility + 1) / 2`, normalised to [0, 1].
Utility matrix maps (model action × gold action) → [−1, +1].
Corrective non-answers on false-presupposition items receive +0.5.
Acceptable alternative actions receive at least +0.3 partial credit.

### Self-Correction (Control)
Transition-based scoring classifies each item into one of six outcomes: `correction_gain`, `maintain_correct`, `neutral_revision`, `damage`, `stubborn_wrong`, `failed_revision`. Base scores differ between C1 (harsh on damage: −0.40) and C2 (more forgiving: −0.25, but −0.40 for misleading evidence). Confidence adjustment in [−0.15, +0.10] applied per transition. See `planning/family_c_sprint/03_scoring_blueprint.md` for worked examples.

### Composite
`MetaScore = mean(norm_A, norm_B, norm_C1, norm_C2)` — platform-averaged anchor-normalized scores. Equal weighting justified by Dawes (1979) and Davis-Stober (2011). See `docs/stats/composite_construction_step2.md`.

---

## Audit Framework

MetaJudge uses a **two-layer audit** to ensure grading accuracy. See `docs/audit/README.md`.

**Layer 1 — Automated re-grading** (`scripts/audit_benchmark_v32.py`): Re-grades every item using the production grading engine, flags correctness flips, validates anchor normalization.

**Layer 2 — LLM semantic audit** (`docs/benchmark/llm_grading_audit_prompt.md`): Long-context LLM reviews all items marked wrong, evaluating whether the model's answer is semantically correct despite failing the automated grader.

**Layer 3 — Per-model audit reports** (`scripts/generate_audit_docx.py`): Professional .docx reports with summary tables, stochasticity comparison, runtime/cost, and item-by-item detail including gold answer justifications (266 items justified in `outputs/metajudge_v51_gold_answer_justifications.md`).

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

### Family C — v0.7.0 Kaggle run (55 items × 5 models, pre-audit)

| Model | T1 Acc | T2 Acc | Delta | W→R | R→W | Profile |
|-------|--------|--------|-------|-----|-----|---------|
| Gemini 2.5 Pro | 92.7% | 81.8% | **−10.9%** | 0 | 6 | Heavy damage* |
| Gemini 2.5 Flash | 87.3% | 83.6% | −3.6% | 0 | 2 | Net damage |
| Claude Haiku 4.5 | 87.3% | 83.6% | −3.6% | 2 | 4 | Net damage |
| Claude Sonnet 4 | 83.6% | 81.8% | −1.8% | 0 | 1 | Slight damage |
| DeepSeek V3.1 | 80.0% | 83.6% | **+3.6%** | 3 | 1 | Self-corrector |

*\*Gemini Pro's −10.9% delta is partially inflated by confirmation-without-restatement parsing failures.*

---

## Start Here

### For day-to-day work
1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`CLAUDE.md`** — Development instructions and hard rules
3. **`docs/benchmark/v5_theoretical_backgrounder.md`** — Two-process framework, task mapping, scoring methodology
4. **`config/family_c_scoring.yaml`** — Scoring weights and thresholds

### For theoretical background
5. **`docs/metacognition_assessor_recommendations.md`** — Cross-family architecture rationale
6. **`docs/metacognition_literature_report.md`** — 80+ paper annotated bibliography
7. **`planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md`** — Family C theoretical analysis

---

## Theoretical Grounding

MetaJudge is grounded in the distinction between metacognitive monitoring and control (Nelson & Narens, 1990), operationalized through the report/withhold paradigm (Koriat & Goldsmith, 1996). The benchmark tests whether LLMs exhibit the selective reporting behavior that characterizes metacognitive competence in humans. Family C extends this to the control axis, testing whether models can detect and repair errors — a capacity that Huang et al. (ICLR 2024) showed rarely occurs without external evidence. Tyen et al. (2024) demonstrated that the bottleneck is error detection (monitoring), not repair (control).

### Key References
- **Nelson & Narens (1990)** — Monitoring vs. control architecture
- **Koriat & Goldsmith (1996)** — Report/withhold paradigm for strategic accuracy regulation
- **Huang et al. (ICLR 2024)** — Intrinsic self-correction often fails without external evidence
- **Tyen et al. (2024)** — LLMs Cannot Find Reasoning Errors, but Can Correct Them
- **Burnell et al. (2026)** — DeepMind cognitive taxonomy identifying metacognition as a key evaluation gap
- **Brier (1950)** — Strictly proper scoring rule for probabilistic forecasts
- **Dawes (1979)** — Equal weights outperform optimized weights in small-n composites
- **Davis-Stober (2011)** — Formal proof: equal weights minimize MSE when p ≥ n
- **Srivastava et al. (2023)** — BIG-Bench: anchor normalization precedent

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
