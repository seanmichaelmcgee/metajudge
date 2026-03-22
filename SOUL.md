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

| Priority | Document | Location | Scope | Role |
|----------|----------|----------|-------|------|
| 1 | **This file (SOUL.md)** | repo root | All families | Principles, constraints, non-negotiables |
| 2 | **Recommendations memo** | `docs/metacognition_assessor_recommendations.md` | All families | Two-axis framework, family specs, architectural guidance |
| 3 | **Family B scoring spec** | `docs/family_b_scoring_spec.md` | Family B | UWAA scoring, utility matrix, action F1, AUARC |
| 4 | **Family B notebook integration** | `docs/family_b_notebook_integration.md` | Family B | Cells 9-15, embedding strategy, composite |
| 5 | **Change prompt** | `docs/metacognition_assessor_change_prompt.md` | Family A | Implementation checklist (calibration-specific) |
| 6 | **V1 Architecture** | `planning/v1_architecture.md` | Family A | Production plan for calibration pipeline |
| 7 | **Scoring plan** | `planning/scoring_plan.md` | Family A | Brier-derived scoring, adjudication, diagnostics |
| 8 | **Dataset construction plan** | `planning/dataset_construction_plan.md` | Family A | Item sourcing, canonicalization, pilot gates |
| 9 | **Original framework** | `docs/source_framework.md` | Archived | Conceptual foundation (historical context only) |

When documents conflict, higher priority wins. Documents scoped to "Family A" are authoritative for calibration work but do not govern Family B or later families. The Recommendations memo (priority 2) is the cross-family source of truth for family specs, schemas, and scoring approaches.

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

### 8. Family B is integrated
Family B — Selective Abstention / Verification / Clarification — is now integrated into the lean notebook as a 48-item pilot. This is the second family on Axis I (Epistemic Monitoring) and the best monitoring-to-action bridge in the design. The canonical action labels are `answer`, `clarify`, `verify`, `abstain`. Schema: `AbstentionResponse`. Primary metric: UWAA (Utility-Weighted Action Accuracy) as specified in `docs/family_b_scoring_spec.md`.

---

## The five families

| ID | Family | Axis | Turns | Status |
|----|--------|------|-------|--------|
| A | Confidence Calibration | Monitoring | 1 | **117-item V4.2 dataset, grading_v2, lean notebook live** |
| B | Selective Abstention / Verification | Monitoring | 1 | **84-item pilot v0.5.4, UWAA scoring** |
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

## Canonical schemas

### Answer key (benchmark dataset)

All items in `data/metajudge_benchmark_v1.json` use these fields:

```json
{
  "item_id": "gen_b3_022",
  "question": "How many hearts does an octopus have?",
  "gold_answer": "3",
  "aliases": ["3", "three"],
  "rule": "numeric",
  "mechanism_primary": "ModifiedCRT",
  "batch": "batch_3"
}
```

### Adjudication registry (grading_v2)

The adjudication registry (`data/adjudication_registry.json`) drives the grading_v2 engine with 8 grader rules:

| Grader Rule | Items | Description |
|-------------|-------|-------------|
| `alias_plus_normalization` | 23 | Enhanced alias matching + sci-notation normalization |
| `approx_numeric_small` | 24 | Fixed tolerance (abs_tol / rel_tol) |
| `approx_numeric_dynamic` | 17 | Time-sensitive numerics with tolerance |
| `code_output` | 16 | Exact match after strip/lower |
| `tri_label` | 14 | Three-valued {true, false, contested} |
| `exact_constant` | 6 | SI constants with rel_tol=1e-6 |
| `fraction_or_decimal` | 2 | Accepts both fraction and decimal forms |
| `yes_no` | 0 | Binary true/false (supported, no V4.2 items) |

The lean notebook uses `grading_v2.grade_item()` exclusively. The old 3-rule `adjudication.py` system (alias/numeric/yes_no) is retained for backward compatibility but is NOT used for scoring.

---

## What agents must not do

1. **Do not add families not listed above** without updating this document first.
2. **Do not score narrative fields** unless you have a validated gold target and document why.
3. **Do not expand dataset scope** beyond what the current phase plan specifies.
4. **Do not spend quota** on anything other than the current implementation slice.
5. **Do not silently diverge** from this document. If you think something here is wrong, flag it explicitly.
6. **Do not use deprecated field names** (`canonical`, `canonical_answer`, `accepted_aliases`, `grader_rule`) in any new code or data files.

---

## Audit export requirements

Every serious Kaggle run MUST produce per-item audit CSVs written to `/kaggle/working/`:

| File | Required columns | When |
|------|-----------------|------|
| `calibration_item_audit.csv` | item_id, gold_answer, grader_rule, model_answer, confidence, is_correct, brier_score | Every run |
| `family_b_item_audit.csv` | item_id, gold_answer, gold_action, model_decision, model_answer, is_correct, utility | When Family B runs |
| `run_summary.json` | timestamp, accuracy, mean_score, per-family stats | Every run |

These are the backbone of auditability. No run is considered valid without them.

---

## What agents should do

1. **Read this file first** before starting work.
2. **Check the V1 architecture** for the current implementation plan.
3. **Write tests** for any new scoring logic before implementing the Kaggle wrapper.
4. **Keep the notebook thin** — scoring logic lives in `metajudge/`, SDK glue lives in the notebook.
5. **Commit frequently** with clear messages referencing the family/phase being worked on.

---

## API iteration policy (v0.5.5+)

Multi-turn API loops are authorized for item-level quality improvement. This replaces the earlier conservative per-call budgeting with a quality-first approach.

### Approved uses
- Item rewrite and wording refinement (multi-turn generator/critic/judge loops)
- Adversarial critique of item construct validity
- Alternative gold-label argument generation
- Scientific wording comparison and narrowing
- False-presupposition detection stress testing

### Model preferences
Use the most capable available models: Claude Opus/Sonnet, GPT-4o, Gemini 2.5 Pro, DeepSeek-R1. Multiple iteration rounds per item are expected — do not stop at one-shot when quality can be improved by further critique.

### Budget discipline
- Session-level awareness: do not burn the full $500 Kaggle budget in one run
- Per-call penny-pinching is explicitly discouraged — prioritize item quality
- Iterate as many rounds as needed to achieve defensible construct validity
- Cache API responses where possible to avoid redundant calls

### Prohibited uses (do not waste API quota)
- CSV aggregation, unit conversions, simple calculations
- Repository scanning or git diffs
- Test writing boilerplate
- Repeated summary generation

### Security
- API keys are **environment variables only** — NEVER committed to the repository
- Keys must not appear in notebooks, config files, logs, or any tracked file

---

## Key references

These four papers anchor the benchmark's theoretical framing:

1. Nelson & Narens (1990) — Monitoring vs. control distinction
2. Kadavath et al. (2022) — LLMs can produce useful self-evaluation under the right conditions
3. Xiong et al. (ICLR 2024) — Verbalized confidence is overconfident and prompt-sensitive
4. Huang et al. (ICLR 2024) — Intrinsic self-correction often fails without external evidence

For the full theoretical lineage (80+ papers across foundational psychology, modern cognitive science, and AI/ML), see `docs/metacognition_literature_report.md` and `docs/references.bib`.

---

## Standardized workflows

### Model sweep protocol

Every dataset change (item additions, difficulty revisions, alias updates) MUST be validated with a multi-model sweep before the dataset is frozen. This is the quality gate between "dataset built" and "dataset submitted."

**Sweep configuration:**
- Models: 5-model panel defined in Cell 7 of the submission notebook
- Current panel: gemini-2.5-flash, gemini-2.5-pro, claude-sonnet-4@20250514, claude-haiku-4-5@20251001, deepseek-v3.1
- Cost: 5 models × 100 items = 500 LLM calls per sweep

**Required outputs (auditable artifacts):**

| Artifact | Format | Contents |
|----------|--------|----------|
| Per-item audit trail | `sweep_results` dict (Cell 7 output) | model_answer, confidence, is_correct, brier_score per item per model |
| Cross-model leaderboard | Printed table (Cell 7) | Headline score, accuracy per model |
| Per-bucket accuracy matrix | Printed table (Cell 7) | Accuracy by difficulty bucket × model |
| Discrimination map | Printed list (Cell 7) | Items where models disagree (signal items) |
| Overconfidence report | Printed list (Cell 7) | Wrong answers with conf > 0.80 per model |
| Success criteria verdict | Printed checklist (Cell 7) | 5 criteria: pass/fail with measured values |
| Audit CSV | Audit export cell (Cell 16) | Flat table: model × item × all fields |

**Success criteria (must meet ≥4/5 to freeze):**

| # | Criterion | Threshold |
|---|-----------|----------|
| C1 | Brier score spread across models | ≥ 0.05 range |
| C2 | High-deception mechanism accuracy | < 80% on ≥ 3 models |
| C3 | High-adversarial mechanism accuracy | < 70% on ≥ 3 models |

> **V4 proxy mapping (since V4 uses `mechanism_primary` instead of `difficulty` buckets):**
> - C2 high-deception mechanisms: `AmbiguityMetacognition`, `Anchoring`, `Prototype`, `RLHF`
> - C3 high-adversarial mechanisms: `IOED`, `Compositional`, `CodeExecution`, `ModifiedCRT`
> - Rationale: V2 difficulty buckets were manually assigned; V4 mechanisms are the adversarial generation categories that produced items designed to exploit specific model weaknesses. The mechanism groupings map to the same intent (deceptive = items that trick confident wrong answers; adversarial = items that resist correct answers).
| C4 | Items with conf–acc gap > 0.20 | ≥ 10 distinct items (any model) |
| C5 | ECE range across models | ≥ 0.03 |

**Decision gates:**
- ≥ 4/5 criteria met → dataset frozen, proceed to writeup
- 3/5 criteria met → targeted item replacements from rejection log (no new authoring)
- < 3/5 criteria met → return to Harvester/Strategist for harder items

**Workflow sequence:**
1. Update notebook cells (Cells 1–6 must be current)
2. Run Cell 7 (quick headline scores via `evaluate()`) to verify models work
3. Run Cell 8 (audit sweep, `RUN_AUDIT=True`) — captures per-item detail for all models
4. Run Cell 9 (diagnostics) — produces verdict + audit artifacts
5. If verdict = freeze → commit sweep results, begin writeup
6. If verdict = replace → swap items, re-run from step 1
7. Export audit CSV for archival (`audit_df.to_csv('metajudge_sweep_audit.csv')`)

### Kaggle model workflow (verified)

This section codifies the verified approach for running models on the Kaggle Benchmarks SDK, based on the competition page, SDK cookbook, and getting-started notebook.

**Two approaches (use BOTH):**

| Approach | When to use | Notebook cells |
|----------|-------------|----------------|
| **A: UI "Evaluate More Models"** | Official leaderboard entries | Cell 6 (batch) → Cell 10 (`%choose`) → Task Detail page → "Evaluate More Models" button |
| **B: In-notebook `evaluate()`** | Development, validation, per-item audit | Cell 7 (headline sweep) or Cell 8 (full audit) |

Approach A is Kaggle's recommended path for leaderboard generation. Approach B is our development loop for iterating on the dataset before submission.

**Model key format:**
- Pattern: `"provider/model-name"` (e.g., `"google/gemini-2.5-flash"`)
- Discovery: `list(kbench.llms.keys())` — printed by Cell 1 on every run
- The key strings are NOT documented in advance; always verify via Cell 1 output

**Verified keys** (all confirmed on Kaggle, March 19 2026):
- `"google/gemini-2.5-flash"`
- `"google/gemini-2.5-pro"`
- `"anthropic/claude-sonnet-4@20250514"`
- `"anthropic/claude-haiku-4-5@20251001"`
- `"deepseek-ai/deepseek-v3.1"`

**Key format notes:**
- Anthropic uses `@` version separator: `model@date`
- DeepSeek provider is `deepseek-ai`, not `deepseek`
- 27 total models available on platform (see Cell 1 output for full list)

**If a key fails:** Cell 7 prints which keys are not found. Replace with the correct key from Cell 1's `kbench.llms.keys()` output. The notebook is designed to degrade gracefully — it runs with whatever models are available (minimum 2).

**Quota management:**
- $50/day, $500 total across the competition
- Cell 7 (evaluate-based sweep): ~500 calls for 5 models × 100 items
- Cell 8 (audit sweep): same cost, gated by `RUN_AUDIT = False` to prevent accidental burns
- Always run Cell 7 first for headline scores; only run Cell 8 when per-item diagnostics are needed

**Notebook cell map (lean notebook — current submission lineage):**

The official submission notebook is `notebooks/metajudge_submission_lean.ipynb`.

| Cell | Purpose | Key outputs |
|------|---------|-------------|
| 0 | Markdown header | — |
| 1 | Imports + sys.path + SDK setup | `grade_item`, `load_registry`, `brier_item_score` |
| 2 | CalibrationResponse schema | dataclass |
| 3 | Load dataset + registry from Kaggle Dataset | `dataset` (102 items), `ANSWER_KEY`, `REGISTRY` |
| 4 | Scoring self-tests (17 assertions + 102/102 gold self-adj) | pass/fail |
| 5 | Single-item `@kbench.task` + smoke test | `metacog_calibration_v1` |
| 6 | Batch `@kbench.task` (102-item calibration) | `metacog_calibration_v1_batch` |
| 7 | Multi-model sweep (5 models) | per-model scores |
| 8 | I/O contract: `run_summary.json` | structured output |
| 9 | Family B separator (markdown) | — |
| 10 | Family B setup: imports + dataset (48 items) | `family_b_items` |
| 11 | AbstentionResponse schema | dataclass (4-action) |
| 12 | Family B self-tests | pass/fail |
| 13 | Family B single-item `@kbench.task` + smoke test | `metacog_abstention_v1` |
| 14 | Family B batch (48-item pilot) | UWAA, action F1 |
| 15 | Composite score (calibration + abstention) | weighted blend |
| 16 | Audit export: CSV + enhanced run_summary.json | `calibration_item_audit.csv`, `family_b_item_audit.csv` |
| 17 | `%choose metacog_calibration_v1_batch` | Kaggle submission |

**Kaggle Dataset:** `seanmcgee2025/metajudge-benchmark` — mounted at `/kaggle/input/datasets/seanmcgee2025/metajudge-benchmark/` in Benchmarks notebooks.

### Iteration protocol

When replacing items after a failed sweep:
1. Identify failing items from the discrimination map and overconfidence report
2. Pull replacements from `data/harvest/v2_rejection_log.json` (123 candidates)
3. If the rejection log is exhausted, author new items following `expansion_sprint_v2.md` §2.2
4. Run the Formatter on new items (aliases + format gates)
5. Update production files (`data/metajudge_benchmark_v1.json`, `data/adjudication_registry.json`)
6. Re-run full sweep (step 1 above)
7. Document changes in a commit message referencing the sweep that triggered them

---

## Project history (abbreviated)

- **Phase 0 (Day 0):** Bootstrap — repo, schemas, scoring, tests, planning docs
- **SDK Verification:** All 26 SDK capabilities confirmed PASS
- **Evidence Notebook:** Wrapper-task pattern verified in live Kaggle environment
- **Architecture Revision:** Recommendations memo adopted; flat family list → two-axis model; source-awareness and strategy-adaptation redesigned
- **V2 Expansion Sprint:** 100-item calibration set built via 4-agent pipeline (Harvester → Formatter → Strategist → Auditor). Distribution: 10/26/30/22/12. 12 audit fixes applied.
- **Flash Sweep Results:** 97/100 correct (0.9756 headline). 3 real errors: cal_065 (France borders), cal_084 (Amazon river), cal_088 (fortune cookies). Adversarial: 100%, Deceptive: 90.9%. Scores too high on flash alone — need weaker models for spread.
- **SDK Alignment:** Notebook rebuilt to use `evaluate()` API per Kaggle SDK recommendations. Cell map updated to v3 (11 cells). Model discovery added to Cell 1.
- **5-Model Sweep (March 19):** All 5 models verified and run. Results: Pro 98/100, Flash 97/100, Haiku 97/100, Sonnet 95/100, DeepSeek 93/100. Success criteria: 1/5 met (C4 only). Brier spread 0.036 (need 0.05). 11 discriminating items. 16 overconfident errors. Verdict: NEEDS WORK — dataset not hard enough for frontier models.
- **V4 Adversarial Pipeline (March 20):** 4-batch 2-agent adversarial generation pipeline produced 266 candidates → 102 survivors (38.3% yield). 58/102 (56.9%) discriminate across 4-model panel. Best mechanisms: IOED (94% disc), Prototype (83%), Anchoring (60%).
- **V4.1 Remediation (March 20):** 37 items replaced via adversarial pipeline. 102-item dataset assembled with adjudication registry and grading_v2 engine (8 grader classes). Mechanism distribution: ModifiedCRT 18, Compositional 17, CodeExecution 16, AmbiguityMetacognition 14, Anchoring 10, Prototype 10, IOED 7, ConditionalTemporal 7, RLHF 3. All 212 tests pass. Awaiting V4.1 sweep.
- **VPS Session (March 21):** Lean notebook upgraded to grading_v2 (8-rule registry-driven adjudication). V4.2 dataset (7 IOED replacements). Family B 48-item pilot integrated (UWAA/F1/AUARC). Kaggle Benchmarks mount path discovered. Per-item audit CSV export added. 5-model sweep completed: Pro 0.894, Sonnet 0.769, DeepSeek 0.776, Haiku 0.730. C1 PASS (spread=0.16), C4 PASS (52 items), C5 PASS (ECE range=0.14). 246 tests passing.
- **Tri-label + Family B v3 (March 21):** Fixed 3 tri-label gold answers (gen_a2_001, gen_a2_007, gen_b_037: false→contested). Family B upgraded to v3: 60 items (was 48), 15 answer + 12 clarify + 18 verify + 15 abstain. All 71 candidates validated by Claude+DeepSeek+Gemini, 60 selected. Notebook self-tests updated (gen_b_039 replaces gen_b_037 for false-path test).
- **Current:** V4.2 lean notebook with corrected tri-labels and Family B v3 (60 items). 5-model sweep complete (3/5 criteria verified PASS, C2/C3 pending mechanism analysis). Next: re-run sweep with corrected gold answers, finalize C2/C3 analysis, begin writeup.
