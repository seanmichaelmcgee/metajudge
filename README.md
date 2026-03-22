# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models, built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

**Current version:** v0.5.1
**Deadline:** April 16, 2026
**Submission:** Kaggle Community Benchmark + Writeup (1500 words)

---

## What This Measures

MetaJudge evaluates whether language models can **track the reliability of their own outputs** (monitoring) and **act appropriately on that information** (control). This maps directly to the two-component model of metacognition established in cognitive psychology (Nelson & Narens, 1990; Flavell, 1979).

The benchmark is organized around three layers:

### Layer 1 — Calibration (Monitoring)
*Does the model know when it is likely correct or incorrect?*

- 117-item benchmark across 10 adversarial mechanisms
- Stratified into three tiers: clean objective (Stratum A), objective-but-brittle (B), and metacognitive traps (C)
- Scored via Brier-derived calibration metric (strictly proper)
- Stratum C includes CRT-style reasoning traps, misleading fluency items, and false familiarity probes

### Layer 2 — Family B: Selective Abstention (Control)
*Given uncertainty, does the model choose the right epistemic action?*

- 87-item benchmark testing four control actions: **answer**, **clarify**, **verify**, **abstain**
- 23 false-presupposition items testing corrective non-answer behavior
- Scored via Utility-Weighted Action Accuracy (UWAA) with a 5×4 payoff matrix
- Acceptable alternative responses credited (e.g., corrective premise rejection on false-premise items)

### Layer 3 — Bridge Analysis
*Does monitoring quality predict control quality?*

- Quantifies monitoring-control coupling per model
- Classifies models into quadrants (good/bad monitoring × good/bad control)
- Maps confidence bands to control utility — revealing where monitoring and control dissociate

---

## Key Finding (v0.5.1)

There is a clear monotonic relationship between expressed confidence and control quality:

| Confidence Band | Items | Mean Utility | Interpretation |
|----------------|-------|-------------|----------------|
| Very low (0–0.3) | 24 | **+0.91** | When uncertain, models act wisely |
| Very high (0.85–0.95) | 11 | +0.40 | Mixed behavior |
| Extreme (0.95+) | 47 | **+0.30** | When confident, models over-answer |

Models that express uncertainty make dramatically better control decisions than models that are confidently wrong. This is the monitoring-control dissociation the benchmark is designed to reveal.

---

## 5-Model Leaderboard (v0.5.1)

| Model | Calibration (1-Brier) | Accuracy | Family B UWAA |
|-------|----------------------|----------|---------------|
| Gemini 2.5 Pro | 0.885 | 87% | — |
| Gemini 2.5 Flash | 0.882 | 87% | 0.744 |
| DeepSeek V3.1 | 0.832 | 75% | — |
| Claude Sonnet 4 | 0.816 | 78% | — |
| Claude Haiku 4.5 | 0.781 | 72% | — |

Success criteria: C1 (Brier spread ≥ 0.05) ✓, C4 (conf-acc gap ≥ 10 items) ✓, C5 (ECE range ≥ 0.03) ✓

---

## Repository Structure

```
SOUL.md                    # Governing principles (read first)
metajudge/                 # Python package — scoring, schemas, metrics
  scoring/                 #   adjudication, grading_v2, calibration, bridge
  schemas/                 #   response dataclasses
  tasks/                   #   task implementations
data/                      # Production datasets
  metajudge_benchmark_v1.json    # 117-item calibration set (V4.2)
  adjudication_registry.json     # Grading registry (8 rules)
  family_b_pilot_v2.json         # 87-item Family B set
notebooks/
  metajudge_submission_lean.ipynb # Production Kaggle notebook
kaggle-upload/             # Ready-to-upload Kaggle dataset
docs/                      # Scientific documentation and charters
  metacognition_literature_report.md  # 80+ paper annotated bibliography
  references.bib                      # BibTeX references
  sprint_report_v0.5.1.md            # Latest run report
tests/                     # Unit and integration tests (246+)
outputs/                   # Run artifacts (audit CSVs, bridge reports)
```

---

## Start Here

1. **`SOUL.md`** — Governing principles, constraints, non-negotiables
2. **`docs/metacognition_assessor_recommendations.md`** — Cross-family architecture and theoretical grounding
3. **`docs/metacognition_literature_report.md`** — Annotated bibliography tracing the theoretical lineage
4. **`planning/v1_architecture.md`** — Implementation plan

---

## Theoretical Grounding

MetaJudge is grounded in the distinction between metacognitive monitoring and metacognitive control, established by Nelson and Narens (1990) and operationalized through the report/withhold paradigm of Koriat and Goldsmith (1996). The benchmark directly tests whether LLMs exhibit the selective reporting behavior that characterizes metacognitive competence in humans.

### Foundational Psychology
- **Flavell (1979)** — Defined metacognition as knowledge and cognition about cognitive phenomena
- **Nelson & Narens (1990)** — Monitoring vs. control architecture; the object-level/meta-level distinction
- **Koriat & Goldsmith (1996)** — Report/withhold paradigm: metacognition enables strategic control over memory output accuracy
- **Fleming & Lau (2014)** — Signal-detection framework (meta-d') for measuring metacognitive sensitivity

### LLM Calibration and Abstention
- **Kadavath et al. (2022)** — LLMs can produce useful self-evaluation under the right conditions
- **Xiong et al. (ICLR 2024)** — Verbalized confidence is systematically overconfident and prompt-sensitive
- **Huang et al. (ICLR 2024)** — Intrinsic self-correction often fails without external evidence
- **Yang et al. (TACL 2025)** — "Know Your Limits" survey of abstention methods in LLMs
- **RiskEval (2026)** — Models maintain calibrated confidence but fail to convert it into strategic abstention, producing utility collapse under risk

### Bridging Psychology and AI
- **Steyvers & Peters (2025)** — Directly applying psychological metacognition theory to evaluate LLM self-knowledge
- **Steyvers et al. (2025)** — Metacognition and uncertainty communication in humans and LLMs
- **Burnell et al. (2025)** — Google DeepMind cognitive taxonomy for measuring progress toward AGI

For the full 80+ paper annotated bibliography, see `docs/metacognition_literature_report.md` and `docs/references.bib`.

---

## Scoring

### Calibration
Per-item score: `1 − (confidence − outcome)²` (Brier-derived, strictly proper).
Grading: 8-rule registry-driven engine (`grading_v2.py`) with tolerance-aware numeric, alias, tri-label, code-output, and fraction grading.

### Family B
Primary metric: UWAA (Utility-Weighted Action Accuracy) with 5×4 payoff matrix.
Corrective non-answers on false-presupposition items receive partial credit (+0.5).
Action F1 and AUARC as diagnostic metrics.

### Bridge
Derived analytics consuming both families. Confidence-band utility mapping, quadrant classification, failure-mode clustering.

---

## Competition Context

This benchmark was designed for the [Kaggle Measuring Progress Toward AGI](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon, organized by Google DeepMind. The competition invites participants to design high-quality benchmarks that evaluate how frontier models reason, act, and judge — going beyond simple recall.

The companion paper ([Burnell et al., 2025](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf)) identifies metacognition as one of five cognitive abilities where the evaluation gap is largest, comprising confidence calibration, error monitoring, source judgments, and error correction.

---

## License

MIT
