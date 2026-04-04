# MetaJudge Pipeline Audit — Analysis Framework

**Source:** Planning agent analysis of Gemini 2.5 Pro v6.2 data
**Date:** 2026-04-04

---

## Purpose

This is not just a model performance report. It is a first-run evaluation of the **entire MetaJudge pipeline** — from answer string extraction through grading, scoring, and metric aggregation. Every response is scrutinized at 5 levels:

1. **Answer string quality** — parsing artifacts, truncation, schema bypass
2. **Grading accuracy** — false positives/negatives in the deterministic engine
3. **Score validity** — per-item scores correctly follow from grading
4. **Metric interpretability** — aggregates accurately represent item-level reality
5. **Stochasticity** — dual-run stability reveals measurement precision

---

## Critical Checks Identified

### Calibration
- Verify Brier formula: `1 - (conf - correct)²` vs stored `brier_score`
- Flag model_answer > 200 chars (parsing artifact indicator)
- Flag confidence clipping to exactly 0 or 1
- Confirm anchor (0.75) is appropriate for this model cluster

### Abstention
- **Two utility matrices exist in codebase** — verify v2 internal matrix was used
- Validate corrective-answer bonus: spot-check false-presupposition items for genuine corrective intent vs keyword false-positives
- Run 2 stability: identify which gold_action class is least stable

### SC C1
- **Pipeline uses accuracy delta, NOT score_item()** — transition-based scoring module is bypassed in production
- **Severe stochasticity:** Run 1 normalized 0.257 vs Run 2 0.543 (0.29 swing on 28 items)
- **Multiple models score exactly 0.2571** because -1/28 is a common delta — identical scores ≠ similar behavior
- Verify neutral_revision items have t1_t2_similarity < 0.9

### SC C2
- Verify 2 damage items show genuine capitulation to misleading evidence (not grading artifact)
- 100% T1 accuracy expected by design — confirm no false positives
- Run 2 produces identical delta despite 4 transition changes — verify offsetting changes

### Cross-Task
- Anchors must be frozen (not re-fit on evaluation data)
- SC C1 score variance renders single-run rankings unreliable
- Bootstrap CIs needed for any model ranking
