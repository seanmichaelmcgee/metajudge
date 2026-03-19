# SOUL.md — MetaJudge-AGI

This is the governing document for the MetaJudge-AGI project. Every contributor (human or agent) should read this before making changes. When in doubt, this file wins.

---

## What this project is

MetaJudge-AGI is a Kaggle benchmark that measures **epistemically robust metacognitive behavior in LLMs**, with explicit separation of **epistemic monitoring** and **cognitive control**.

It is not a general intelligence test. It is not a reasoning benchmark. It is a behavioral assessment of whether a model can track the reliability of its own outputs and act on that information.

**Competition:** Kaggle "Measuring Progress Toward AGI — Cognitive Abilities"  
**Track:** Metacognition  
**Deadline:** April 16, 2026  
**Submission:** One Kaggle Benchmark (via `%choose`) + Writeup (1500 words)

---

## Governing design documents

These are the project's source-of-truth documents, in priority order:

| Priority | Document | Location | Role |
|----------|----------|----------|------|
| 1 | **This file (SOUL.md)** | repo root | Principles, constraints, non-negotiables |
| 2 | **Recommendations memo** | `docs/metacognition_assessor_recommendations.md` | Architectural revision guidance |
| 3 | **Change prompt** | `docs/metacognition_assessor_change_prompt.md` | Implementation requirements checklist |
| 4 | **V1 Architecture** | `planning/v1_architecture.md` | Current production plan |
| 5 | **Scoring plan** | `planning/scoring_plan.md` | Brier-derived scoring, adjudication, diagnostics |
| 6 | **Dataset construction plan** | `planning/dataset_construction_plan.md` | Item sourcing, canonicalization, pilot gates |
| 7 | **Original framework** | `docs/source_framework.md` | Conceptual foundation (read for context, do not treat as current spec) |

When documents conflict, higher priority wins. The original framework and implementation plan are historical context — they informed the current design but have been superseded by the recommendations memo.

---

## Non-negotiable principles

### 1. Behavioral evidence over self-report
Score what the model does, not what it says about itself. Narrative self-report fields (`reason_for_uncertainty`, `why_this_strategy`, `what_changed`) are **diagnostic only** — never scored — unless backed by a validated gold target.

### 2. Two axes, not a flat list
The benchmark is organized as:
- **Axis I — Epistemic Monitoring:** Does the model track the reliability of its cognition?
- **Axis II — Cognitive Control:** Does the model use monitoring information to change behavior?

Every family belongs to one axis. The composite score is a weighted blend, but axis-level scores are always reported.

### 3. Calibration is the anchor
Calibration (Family A) is the most empirically defensible family and the first implementation priority. It stays central. Other families are built around it, not in competition with it.

### 4. Kaggle practicality is a hard constraint
- One exported `@kbench.task` via `%choose`
- $500 total quota, $50/day
- Modular family-by-family rollout
- Caching and budget awareness in every design decision

### 5. Do not redesign from scratch
The wrapper-task architecture is verified and works. Changes are incremental: tighten constructs, rename modules, adjust scoring. The skeleton stays.

### 6. Intrinsic vs. evidence-assisted correction must be distinct
Self-correction is two separate subfamilies. Never blend them into a single score without reporting both.

### 7. No "expected strategy" scoring unless objectively necessary
Control-policy adaptation is scored by behavioral outcomes under perturbation, not by agreement with a hand-authored strategy label.

---

## The five families

| ID | Family | Axis | Turns | Status |
|----|--------|------|-------|--------|
| A | Confidence Calibration | Monitoring | 1 | V1 implementation target |
| B | Selective Abstention / Verification | Monitoring | 1 | V1 after calibration |
| C | Self-Correction (intrinsic + evidence-assisted) | Control | 2 | V2 |
| D | Grounding Sensitivity | Monitoring | 1 | V2 |
| E | Control-Policy Adaptation | Control | 2 | V2 |

---

## Composite scoring

```python
WEIGHTS = {
    "calibration": 0.30,
    "abstention_verification": 0.20,
    "intrinsic_self_correction": 0.10,
    "evidence_assisted_correction": 0.15,
    "grounding_sensitivity": 0.10,
    "control_policy_adaptation": 0.15,
}
```

Weights are provisional and will be tuned after pilot runs. The composite is for Kaggle ranking. Axis-level and family-level scores are always reported in diagnostics.

---

## What agents must not do

1. **Do not add families not listed above** without updating this document first.
2. **Do not score narrative fields** unless you have a validated gold target and document why.
3. **Do not expand dataset scope** beyond what the current phase plan specifies.
4. **Do not spend quota** on anything other than the current implementation slice.
5. **Do not silently diverge** from this document. If you think something here is wrong, flag it explicitly.

---

## What agents should do

1. **Read this file first** before starting work.
2. **Check the V1 architecture** for the current implementation plan.
3. **Write tests** for any new scoring logic before implementing the Kaggle wrapper.
4. **Keep the notebook thin** — scoring logic lives in `metajudge/`, SDK glue lives in the notebook.
5. **Commit frequently** with clear messages referencing the family/phase being worked on.

---

## Key references

These four papers anchor the benchmark's theoretical framing:

1. Nelson & Narens (1990) — Monitoring vs. control distinction
2. Kadavath et al. (2022) — LLMs can produce useful self-evaluation under the right conditions
3. Xiong et al. (ICLR 2024) — Verbalized confidence is overconfident and prompt-sensitive
4. Huang et al. (ICLR 2024) — Intrinsic self-correction often fails without external evidence

---

## Standardized workflows

### Model sweep protocol

Every dataset change (item additions, difficulty revisions, alias updates) MUST be validated with a multi-model sweep before the dataset is frozen. This is the quality gate between "dataset built" and "dataset submitted."

**Sweep configuration:**
- Models: 5-model panel defined in Cell 7 of the submission notebook
- Current panel: gemini-2.5-flash, gemini-2.5-pro, claude-sonnet-4, claude-3-5-haiku, deepseek-v3
- Cost: 5 models × 100 items = 500 LLM calls per sweep

**Required outputs (auditable artifacts):**

| Artifact | Format | Contents |
|----------|--------|----------|
| Per-item audit trail | `sweep_results` dict (Cell 7 output) | model_answer, confidence, is_correct, brier_score per item per model |
| Cross-model leaderboard | Printed table (Cell 8) | Headline score, accuracy per model |
| Per-bucket accuracy matrix | Printed table (Cell 8) | Accuracy by difficulty bucket × model |
| Discrimination map | Printed list (Cell 8) | Items where models disagree (signal items) |
| Overconfidence report | Printed list (Cell 8) | Wrong answers with conf > 0.80 per model |
| Success criteria verdict | Printed checklist (Cell 8) | 5 criteria: pass/fail with measured values |
| Audit CSV | Exportable DataFrame (Cell 8) | Flat table: model × item × all fields |

**Success criteria (must meet ≥4/5 to freeze):**

| # | Criterion | Threshold |
|---|-----------|----------|
| C1 | Brier score spread across models | ≥ 0.05 range |
| C2 | Deceptive bucket accuracy | < 80% on ≥ 3 models |
| C3 | Adversarial bucket accuracy | < 70% on ≥ 3 models |
| C4 | Items with conf–acc gap > 0.20 | ≥ 10 distinct items (any model) |
| C5 | ECE range across models | ≥ 0.03 |

**Decision gates:**
- ≥ 4/5 criteria met → dataset frozen, proceed to writeup
- 3/5 criteria met → targeted item replacements from rejection log (no new authoring)
- < 3/5 criteria met → return to Harvester/Strategist for harder items

**Workflow sequence:**
1. Update notebook cells (Cells 1–6 must be current)
2. Run Cell 7 (sweep) — captures per-item detail for all models
3. Run Cell 8 (diagnostics) — produces verdict + audit artifacts
4. If verdict = freeze → commit sweep results, begin writeup
5. If verdict = replace → swap items, re-run from step 1
6. Export audit CSV for archival (`audit_df.to_csv('metajudge_sweep_audit.csv')`)

### Iteration protocol

When replacing items after a failed sweep:
1. Identify failing items from the discrimination map and overconfidence report
2. Pull replacements from `data/harvest/v2_rejection_log.json` (123 candidates)
3. If the rejection log is exhausted, author new items following `expansion_sprint_v2.md` §2.2
4. Run the Formatter on new items (aliases + format gates)
5. Update production files (calibration.csv, answer_key.json, provenance.csv)
6. Update the embedded dataset in Cell 3 of the notebook
7. Re-run full sweep (step 1 above)
8. Document changes in a commit message referencing the sweep that triggered them

---

## Project history (abbreviated)

- **Phase 0 (Day 0):** Bootstrap — repo, schemas, scoring, tests, planning docs
- **SDK Verification:** All 26 SDK capabilities confirmed PASS
- **Evidence Notebook:** Wrapper-task pattern verified in live Kaggle environment
- **Architecture Revision:** Recommendations memo adopted; flat family list → two-axis model; source-awareness and strategy-adaptation redesigned
- **V2 Expansion Sprint:** 100-item calibration set built via 4-agent pipeline (Harvester → Formatter → Strategist → Auditor). Distribution: 10/26/30/22/12. 12 audit fixes applied.
- **Current:** V1 validation — 5-model sweep to confirm discriminatory power
