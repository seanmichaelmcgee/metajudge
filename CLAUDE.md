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
  scoring/
    self_correction_v2.py  # Family C scoring (USE THIS, not self_correction_metrics.py)
  tasks/
    self_correction_v2.py  # Family C task defs (USE THIS, not self_correction.py)
tests/           # pytest unit and integration tests
notebooks/       # Kaggle submission notebook (thin — logic lives in metajudge/)
data/            # Benchmark datasets
  family_c/      # Family C item bundles (C1 + C2 candidates, SCHEMA.md)
config/          # Benchmark configuration (weights, thresholds)
  family_c_scoring.yaml  # Family C base scores, damage penalties, ranges
docs/            # Design documents (see docs/README.md for index)
planning/        # Architecture and sprint plans (see planning/README.md for index)
  family_c_sprint/  # Current sprint — 17 planning docs for Family C
scripts/         # Runners and utilities
  pilot_family_c.py  # Family C model sweep runner
  openrouter/    # OpenRouter API client
outputs/         # Run artifacts, audit CSVs, figures
  family_c/      # Family C pilot outputs
```

---

## Governing documents (read in this order)

1. `SOUL.md` — principles and non-negotiables. This wins.
2. `planning/family_c_sprint/07_sprint_checklist.md` — current sprint execution plan
3. `planning/family_c_sprint/03_scoring_blueprint.md` — Family C scoring design
4. `data/family_c/SCHEMA.md` — Family C item bundle specification
5. `docs/metacognition_assessor_recommendations.md` — cross-family architecture (background)
6. `planning/scoring_plan.md` — Family A Brier scoring (background)

---

## The five families (do not add others without updating SOUL.md)

| ID | Family | Axis | Status |
|----|--------|------|--------|
| A  | Confidence Calibration | Monitoring | **Complete** — 105 clean items, grading_v2, lean notebook live |
| B  | Selective Abstention / Verification | Monitoring | **Complete** — 72 clean items, UWAA scoring |
| C  | Self-Correction | Control | **Current sprint** — v0.6.1 pilot, 28 clean items, 5-model sweep pending |
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
