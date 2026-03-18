# MetaJudge-AGI

Epistemically robust metacognitive assessment benchmark for LLMs.

**Competition:** [Kaggle — Measuring Progress Toward AGI](https://www.kaggle.com/competitions/kaggle-measuring-agi)  
**Track:** Metacognition  
**Deadline:** April 16, 2026

## What this measures

Two axes of metacognitive behavior:

**Axis I — Epistemic Monitoring:** Does the model track the reliability of its own cognition?
- Confidence Calibration (anchor family)
- Selective Abstention / Verification
- Grounding Sensitivity

**Axis II — Cognitive Control:** Does the model use monitoring to change behavior?
- Intrinsic Self-Correction
- Evidence-Assisted Correction
- Control-Policy Adaptation

## Start here

1. Read `SOUL.md` — governing principles and non-negotiables
2. Read `planning/v1_architecture.md` — current implementation plan
3. Read `docs/metacognition_assessor_recommendations.md` — theoretical grounding

## Project structure

```
metajudge/           # Python package (scoring, schemas, tasks)
data/                # Benchmark datasets (CSV)
notebooks/           # Kaggle submission notebook
tests/               # Unit and integration tests
config/              # Benchmark configuration
docs/                # Design documents and references
planning/            # Architecture plans and verification records
```

## Key references

1. Nelson & Narens (1990) — Monitoring vs. control
2. Kadavath et al. (2022) — LLMs know what they know
3. Xiong et al. (ICLR 2024) — Verbalized confidence is overconfident
4. Huang et al. (ICLR 2024) — Intrinsic self-correction often fails
