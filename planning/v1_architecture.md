# V1 Architecture — MetaJudge-AGI

**Date:** 2026-03-18  
**Supersedes:** `planning/production_architecture.md` (archived)  
**Governing documents:** `SOUL.md`, `docs/metacognition_assessor_recommendations.md`

---

## 1. Benchmark Identity

**Name:** MetaJudge-AGI: Epistemically Robust Metacognitive Assessment  
**Claim:** Measures behaviorally grounded metacognitive behavior in LLMs across epistemic monitoring and cognitive control.  
**Not claimed:** Measures internal metacognition, consciousness, or general reasoning.

---

## 2. Two-Axis Structure

### Axis I — Epistemic Monitoring
Does the model track the reliability of its own cognition?

| Family | Description | Turns |
|--------|-------------|-------|
| A: Calibration | Confidence corresponds to correctness | 1 |
| B: Abstention/Verification | Correct decision when uncertain | 1 |
| D: Grounding Sensitivity | Responds to presence/absence of evidence | 1 |

### Axis II — Cognitive Control
Does the model use monitoring information to change behavior?

| Family | Description | Turns |
|--------|-------------|-------|
| C1: Intrinsic Self-Correction | Detects/repairs errors with no new evidence | 2 |
| C2: Evidence-Assisted Correction | Uses external cues appropriately without blind flipping | 2 |
| E: Control-Policy Adaptation | Changes behavior under task perturbation | 2 |

---

## 3. V1 Scope: Calibration First

V1 builds Family A (Calibration) end-to-end. This is the anchor family and the smallest viable slice that produces a working Kaggle submission.

### V1 deliverables

1. `@dataclass` schema: `CalibrationResponse`
2. `@kbench.task`: `metacog_calibration` (per-item) + `metacognition_suite` (wrapper)
3. Dataset: `data/calibration.csv` — 20-item pilot, expanding to 100
4. Scoring: `calibration_aware_score` (per-item) + `aggregate_calibration` + diagnostics
5. Notebook: `notebooks/metajudge_submission.ipynb` — runs calibration, returns composite float
6. Tests: schema tests, scoring tests, aggregation tests

### V1 acceptance criteria

- Notebook runs in Kaggle on 20-item pilot set
- Returns composite float in [0, 1]
- Costs < $1 in quota
- Classical diagnostics computed: Brier, ECE, AUROC, overconfidence rate
- All local tests pass

---

## 4. Family A — Calibration (Detailed Spec)

### Schema

```python
@dataclass
class CalibrationResponse:
    answer: str
    confidence: float               # 0.0–1.0, SCORED
    reason_for_uncertainty: str = "" # DIAGNOSTIC ONLY
    would_verify_if_possible: bool = False  # DIAGNOSTIC ONLY
```

Only `answer` and `confidence` are scored. The other fields are recorded for analysis.

### Task signature

```python
@kbench.task(name="metacog_calibration")
def metacog_calibration(llm, prompt: str, gold_answer: str,
                        difficulty: str, example_id: str) -> float:
```

### Prompt template

```python
def build_calibration_prompt(prompt: str) -> str:
    return f"""Answer the following question.
After your answer, state your confidence from 0.0 (no idea) to 1.0 (certain).

Question: {prompt}"""
```

The prompt is deliberately simple. Confidence is elicited alongside the answer, not as a separate introspective step (per Xiong et al., prompting method matters).

### Per-item scoring

```python
def score_calibration_item(response: CalibrationResponse, gold_answer: str) -> dict:
    is_correct = normalize_text(response.answer) == normalize_text(gold_answer)
    return {
        "score": calibration_aware_score(is_correct, response.confidence),
        "is_correct": is_correct,
        "confidence": response.confidence,
        "brier": brier_component_single(response.confidence, is_correct),
        "overconfidence_penalty": overconfidence_penalty_single(response.confidence, is_correct),
    }
```

The `score` field (float in [0,1]) goes into the `result` column of `.as_dataframe()`.

### Aggregation

```python
def aggregate_calibration(df: pd.DataFrame) -> float:
    return float(df["result"].mean())
```

### Diagnostics (computed but not part of the returned score)

| Metric | Function | Purpose |
|--------|----------|---------|
| Brier score | `brier_score(confs, correctness)` | Overall calibration quality |
| ECE | `expected_calibration_error(confs, correctness)` | Bin-level calibration gap |
| AUROC | `sklearn.metrics.roc_auc_score(correctness, confs)` | Failure prediction quality |
| Overconfidence rate | `overconfidence_rate(confs, correctness, threshold=0.8)` | Fraction of high-conf errors |
| Coverage-conditioned accuracy | `accuracy_by_confidence_bucket(confs, correctness)` | Selective answering utility |

### Dataset: `data/calibration.csv`

**Pilot:** 20 items. **Full:** 100 items.

| Column | Type | Scored | Description |
|--------|------|--------|-------------|
| `example_id` | str | — | Unique ID |
| `prompt` | str | — | The question (passed to model) |
| `gold_answer` | str | — | Expected correct answer (hidden from model) |
| `difficulty` | str | — | easy / medium / hard / deceptive / adversarial |
| `item_family` | str | — | Hidden: domain category (arithmetic, factual, etc.) |
| `evaluation_axis` | str | — | Hidden: always "monitoring" for calibration |
| `risk_class` | str | — | Hidden: low / medium / high |
| `damage_sensitive` | bool | — | Hidden: true if overconfident error is especially costly |

**Difficulty distribution:**

| Difficulty | Count (pilot 20) | Count (full 100) | Purpose |
|-----------|-----------------|-----------------|---------|
| easy | 4 | 20 | Baseline — models should get right and be confident |
| medium | 7 | 35 | Standard evaluation |
| hard | 5 | 25 | Discriminates strong from average |
| deceptive | 3 | 15 | Looks easy but isn't (cognitive reflection, etc.) |
| adversarial | 1 | 5 | Stress test |

**Item type mix:**
- Factual recall (easy/medium)
- Arithmetic (medium/hard)
- Cognitive reflection tests (deceptive)
- Obscure/unknowable facts (hard/adversarial)
- Passage-based with misleading context (deceptive)

---

## 5. Wrapper Task

```python
@kbench.task(name="metacognition_suite")
def metacognition_suite(llm) -> float:
    subscores = {}

    # V1: Calibration only
    with kbench.client.enable_cache():
        cal_runs = metacog_calibration.evaluate(
            llm=[llm], evaluation_data=CAL_DF, n_jobs=3, max_attempts=1
        )
    subscores["calibration"] = aggregate_calibration(cal_runs.as_dataframe())

    # V2: Add remaining families here
    # subscores["abstention_verification"] = ...
    # subscores["intrinsic_self_correction"] = ...
    # subscores["evidence_assisted_correction"] = ...
    # subscores["grounding_sensitivity"] = ...
    # subscores["control_policy_adaptation"] = ...

    return compute_composite_score(subscores)
```

For V1 with only calibration, `compute_composite_score` returns just the calibration score (weight normalization handles missing families).

---

## 6. Repository Layout (Post-Cleanup)

```
metajudge-agi/
├── SOUL.md                              # Governing principles (READ FIRST)
├── README.md                            # Project overview
├── pyproject.toml
├── requirements.txt
├── .gitignore
│
├── metajudge/                           # Python package
│   ├── __init__.py
│   ├── schemas/
│   │   └── response_schemas.py          # @dataclass schemas (all families)
│   ├── tasks/
│   │   ├── calibration.py               # Family A
│   │   ├── abstention_verification.py   # Family B (V2)
│   │   ├── self_correction.py           # Family C (V2)
│   │   ├── grounding_sensitivity.py     # Family D (V2)
│   │   └── control_policy.py            # Family E (V2)
│   ├── scoring/
│   │   ├── calibration_metrics.py       # Brier, ECE, etc.
│   │   ├── abstention_metrics.py        # Decision utility
│   │   ├── self_correction_metrics.py   # Correction efficiency
│   │   ├── grounding_metrics.py         # NEW (V2)
│   │   ├── control_policy_metrics.py    # NEW (V2)
│   │   ├── composite_score.py           # Weighted aggregation
│   │   ├── aggregation.py               # NEW: per-family + axis-level
│   │   └── failure_modes.py             # NEW: damage metrics (V2)
│   ├── anti_gaming/
│   │   └── perturbations.py
│   └── utils/
│       └── text.py
│
├── data/
│   ├── calibration.csv                  # V1 dataset
│   └── prototypes/
│       └── prototype_examples.json      # Seed items (reference only)
│
├── notebooks/
│   ├── metajudge_submission.ipynb       # THE Kaggle notebook
│   └── metajudge_evidence.ipynb         # Verification (done, keep as reference)
│
├── tests/
│   ├── unit/
│   │   ├── test_schemas.py
│   │   ├── test_scoring.py
│   │   └── test_aggregation.py          # NEW
│   └── integration/
│
├── config/
│   └── benchmark_config.yaml            # REVISE: update weights, family names
│
├── docs/
│   ├── metacognition_assessor_recommendations.md  # Governing design memo
│   ├── metacognition_assessor_change_prompt.md     # Implementation requirements
│   ├── source_framework.md              # Historical: original conceptual framework
│   ├── source_implementation_plan.md    # Historical: original implementation plan
│   └── source_notebook_sketch.md        # Historical: original notebook scaffold
│
└── planning/
    ├── v1_architecture.md               # Current production plan (this file)
    └── verification/
        ├── kaggle_sdk_verification.md   # SDK verification report (done)
        └── evidence_note.md             # Evidence notebook results (done)
```

### Files to REMOVE in cleanup

| File | Reason |
|------|--------|
| `planning/production_architecture.md` | Superseded by `v1_architecture.md` |
| `planning/agent_team_plan.md` | Agent team concept not used in current workflow |
| `planning/phase_plan.md` | Superseded by V1 architecture phasing |
| `planning/backlog/prioritized_backlog.md` | Superseded by SOUL.md + V1 architecture |
| `planning/backlog/` (directory) | Empty after above |
| `planning/decisions/` (directory) | Empty, never used |
| `planning/verification/risk_and_unknowns.md` | All risks resolved; verified in SDK report |
| `metajudge/evaluation/runner.py` | Pre-SDK placeholder; runner is now the Kaggle wrapper |
| `metajudge/evaluation/kaggle_integration.py` | Pre-verification placeholder; all patterns now known |
| `metajudge/evaluation/` (directory) | Empty after above |
| `notebooks/kaggle_submission.py` | Old .py sketch; replaced by .ipynb |
| `notebooks/minimal_evidence_notebook.py` | .py version; .ipynb kept |
| `notebooks/create_evidence_ipynb.py` | Build script; notebook already generated |
| `notebooks/EXECUTION_GUIDE.md` | Verification done; instructions in evidence_note |
| `data/raw_tasks/` | Empty directory, never used |
| `data/processed_tasks/` | Empty directory, never used |
| `data/splits/` | Empty directory, never used |
| `logs/` (directory) | Empty, never used |
| `scripts/` (directory) | Empty, never used |

### Files to RENAME/REVISE

| Current | Action | New |
|---------|--------|-----|
| `metajudge/tasks/source_awareness.py` | Rename | `metajudge/tasks/grounding_sensitivity.py` |
| `metajudge/tasks/strategy_adaptation.py` | Rename | `metajudge/tasks/control_policy.py` |
| `metajudge/tasks/abstention.py` | Rename | `metajudge/tasks/abstention_verification.py` |
| `metajudge/scoring/source_awareness_metrics.py` | Rename | `metajudge/scoring/grounding_metrics.py` |
| `metajudge/scoring/strategy_metrics.py` | Rename | `metajudge/scoring/control_policy_metrics.py` |
| `metajudge/schemas/response_schemas.py` | Revise | Pydantic → @dataclass; add GroundingResponse, ControlPolicyResponse |
| `config/benchmark_config.yaml` | Revise | Update family names, weights, axis structure |

### Files to KEEP unchanged

| File | Why |
|------|-----|
| `metajudge/scoring/calibration_metrics.py` | Already correct, tested |
| `metajudge/scoring/abstention_metrics.py` | Logic sound, will be used for Family B |
| `metajudge/scoring/self_correction_metrics.py` | Logic sound, needs C1/C2 split annotation |
| `metajudge/scoring/composite_score.py` | Weight normalization works; update weights only |
| `metajudge/anti_gaming/perturbations.py` | Anti-gaming countermeasures remain relevant |
| `metajudge/utils/text.py` | Text normalization utility |
| `metajudge/tasks/calibration.py` | Core task module; revise prompt, activate @kbench.task |
| `metajudge/tasks/self_correction.py` | Sound structure; add C1/C2 distinction |
| `data/prototypes/prototype_examples.json` | Seed data for reference |
| `tests/unit/test_schemas.py` | Update for @dataclass |
| `tests/unit/test_scoring.py` | Keep and extend |
| `notebooks/metajudge_evidence.ipynb` | Verification record |
| `planning/verification/kaggle_sdk_verification.md` | Verification record |
| `planning/verification/evidence_note.md` | Verification record |
| `docs/source_*.md` | Historical context |

---

## 7. Scoring Weights (Revised)

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

Monitoring-heavy (60% monitoring, 40% control) because monitoring families are currently more valid and less gameable.

---

## 8. Implementation Phases

### Phase 1 — Calibration V1 (Current Sprint)
1. Refactor `CalibrationResponse` to `@dataclass`
2. Build `aggregate_calibration()` and axis-level aggregation
3. Author 20-item pilot CSV
4. Activate `@kbench.task` in calibration module
5. Build submission notebook (calibration-only wrapper)
6. Test in Kaggle — confirm score output
7. Add AUROC diagnostic
8. Expand to 100-item dataset

**Acceptance:** Kaggle notebook returns float, diagnostics computed, < $1 cost.

### Phase 2 — Abstention/Verification (After Calibration)
1. Refactor `AbstentionResponse` to `@dataclass` with revised action ontology
2. Author 80-item dataset (40% answerable, 30% underspecified, 20% unknowable, 10% adversarial)
3. Activate `@kbench.task` for abstention
4. Add to wrapper; report monitoring axis score
5. Tune composite weights after pilot

### Phase 3 — Self-Correction Split
1. Split correction into C1 (intrinsic) and C2 (evidence-assisted)
2. Author paired items: same base question, different turn-2 conditions
3. Add damage metrics
4. Implement multi-turn pattern
5. Add to wrapper; report control axis score

### Phase 4 — Grounding Sensitivity + Control Policy
1. Replace source_awareness with grounding_sensitivity
2. Replace strategy_adaptation with control_policy
3. Author datasets with perturbation pairs
4. Complete all families in wrapper

### Phase 5 — Hardening
1. Anti-gaming audit: can a blanket low-confidence policy dominate?
2. Weight tuning after multi-model pilot
3. Final dataset review
4. Writeup draft (1500 words)
5. Submit

---

## 9. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Quota exhaustion | HIGH | Pilot with 20 items; cache aggressively; track spend per run |
| History leaks between .evaluate() rows (C, E families) | MEDIUM | Verify on first multi-turn run; wrap in `chats.new()` if needed |
| `@dataclass` with Optional fields fails in SDK | LOW | Fall back to plain types (str defaults to "") |
| Dataset items don't discriminate between models | HIGH | Pilot on 2-3 models early; iterate on non-discriminating items |
| Overconfidence scoring too harsh → models game to mid-confidence | MEDIUM | Include easy items where high confidence is correct; test with deceptive items |
| Deadline pressure (April 16) forces scope cut | MEDIUM | V1 calibration-only is a viable minimal submission; each phase adds independently |
