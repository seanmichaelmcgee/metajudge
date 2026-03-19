# CLAUDE.md — MetaJudge-AGI

This file tells Claude Code what this project is and how to work in it.
Read SOUL.md first. This file is second. SOUL.md wins on any conflict.

---

## What this project is

MetaJudge-AGI is a Kaggle benchmark measuring metacognitive behavior in LLMs.
It is not a reasoning benchmark. It measures whether a model can track the
reliability of its own outputs and act on that information.

**Competition deadline: April 16, 2026**
**Kaggle budget: $500 total, $50/day**

---

## Package structure

```
metajudge/       # Core Python package — scoring, schemas, task definitions
tests/           # pytest unit and integration tests
notebooks/       # Kaggle submission notebook (thin — logic lives in metajudge/)
data/            # Benchmark datasets (large files gitignored)
config/          # Benchmark configuration (weights, thresholds)
docs/            # Design documents
planning/        # Architecture plans (v1_architecture.md is current)
```

---

## Governing documents (read in this order)

1. `SOUL.md` — principles and non-negotiables. This wins.
2. `docs/metacognition_assessor_recommendations.md` — architectural guidance
3. `planning/v1_architecture.md` — current implementation plan
4. `planning/scoring_plan.md` — Brier scoring and adjudication

---

## The five families (do not add others without updating SOUL.md)

| ID | Family | Axis | V1 status |
|----|--------|------|-----------|
| A  | Confidence Calibration | Monitoring | Current sprint |
| B  | Selective Abstention / Verification | Monitoring | After A |
| C  | Self-Correction | Control | V2 |
| D  | Grounding Sensitivity | Monitoring | V2 |
| E  | Control-Policy Adaptation | Control | V2 |

---

## Hard rules for any code changes

- Scoring logic lives in `metajudge/`, not in notebooks
- Every new scoring function needs a test in `tests/` before the Kaggle wrapper
- Narrative fields (reason_for_uncertainty, why_this_strategy, what_changed) are diagnostic only — never scored
- Scoring weights live in `config/` — no hardcoded floats in scoring code
- No model API calls without caching and budget guards
- Do not expand dataset scope beyond the current phase plan

---

## Dev commands

```bash
# Install
pip install -e ".[dev]"

# Test
pytest tests/ --tb=short

# Lint
ruff check .

# Format
black .

# Type check
mypy metajudge/ --ignore-missing-imports
```

---

## What to do if something in SOUL.md seems wrong

Flag it explicitly in your PR comment or commit message. Do not silently diverge.
