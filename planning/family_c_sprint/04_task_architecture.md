# Family C Sprint: Task Architecture & SDK Plan

**Purpose:** Define the SDK implementation pattern, module layout, notebook
structure, and conversation handling for Family C.

**Continuity:** Builds on existing patterns in `metajudge_benchmark.ipynb`,
`metajudge/tasks/self_correction.py`, and verified SDK capabilities.

---

## 1. SDK Pattern: Multi-Turn Within `chats.new()`

The Kaggle Benchmarks SDK automatically maintains conversation history across
`llm.prompt()` calls. Family C uses this within a `chats.new()` block:

```python
@kbench.task(name="metacog_self_correction_c1", store_task=False)
def metacog_self_correction_c1(llm, item_id: str, question: str,
                                 gold_answer: str, challenge_type: str) -> dict:
    with chats.new():
        # Turn 1: Initial answer (model sees only the question)
        response_1 = llm.prompt(
            build_turn1_prompt(question),
            schema=CalibrationResponse
        )

        # Turn 2: Generic review (model sees T1 Q+A + review prompt)
        response_2 = llm.prompt(
            build_c1_turn2_prompt(challenge_type),
            schema=SelfCorrectionResponse
        )

    # Score outside the chat context
    return score_self_correction_item_v2(
        response_1, response_2, gold_answer, item_id,
        subfamily="C1", stratum=get_stratum(item_id)
    )
```

**Key points:**
- `chats.new()` isolates each item — no context bleed between items
- Turn 2 automatically sees Turn 1 exchange in conversation history
- Schema enforcement ensures structured output on both turns
- Scoring happens outside the `with` block

### 1.1 C1 vs C2 Task Separation

C1 and C2 are **separate tasks**, not parameterized variants:

```python
@kbench.task(name="metacog_self_correction_c1", store_task=False)
def metacog_self_correction_c1(llm, item_id, question, gold_answer,
                                 challenge_type) -> dict:
    # ... generic review, no evidence ...

@kbench.task(name="metacog_self_correction_c2", store_task=False)
def metacog_self_correction_c2(llm, item_id, question, gold_answer,
                                 challenge_type, followup_evidence) -> dict:
    # ... evidence-assisted review ...
```

This separation is non-negotiable (Huang et al.) and simplifies evaluation
data preparation — C1 and C2 datasets have different columns.

---

## 2. Module Layout

### 2.1 Updated File Structure

```
metajudge/
├── schemas/
│   └── response_schemas.py        ← EXISTS: SelfCorrectionResponse defined
│                                     UPDATE: add revise_decision field
├── scoring/
│   ├── self_correction_metrics.py ← EXISTS: basic metrics
│   │                                UPDATE: add v2 scoring per blueprint
│   └── bridge_metrics.py          ← EXISTS: extend for C-axis coupling
├── tasks/
│   ├── self_correction.py         ← EXISTS: prompt builders
│   │                                UPDATE: split C1/C2 task definitions
│   └── __init__.py
├── utils/
│   └── text.py                    ← EXISTS: normalize_text for grading

data/
├── family_c/
│   ├── family_c_seed_v1.json     ← NEW: seed dataset
│   └── family_c_manifest.json    ← NEW: clean-set tracking

notebooks/
├── family_c_analysis.ipynb        ← NEW: analysis notebook
└── metajudge_benchmark.ipynb      ← NO CHANGE until promotion
```

### 2.2 What Changes vs What's New

| File | Action | Details |
|------|--------|---------|
| `response_schemas.py` | Minor update | Add optional `revise_decision` enum to `SelfCorrectionResponse` |
| `self_correction_metrics.py` | Enhance | Add `score_self_correction_item_v2()`, `compute_family_c_headline()` |
| `self_correction.py` (tasks) | Refactor | Split into explicit C1 and C2 prompt builders |
| `bridge_metrics.py` | Extend | Add C-axis coupling analysis |
| `family_c_seed_v1.json` | New | Seed dataset (35 items) |
| `family_c_manifest.json` | New | Clean-set tracking |
| `family_c_analysis.ipynb` | New | Analysis notebook |

---

## 3. Task Signatures

### 3.1 C1 Task

```python
def metacog_self_correction_c1(
    llm,
    item_id: str,
    question: str,
    gold_answer: str,
    challenge_type: str,   # "generic" | "inspect" | "reconsider"
) -> dict
```

**Evaluation DataFrame columns:**
`item_id, question, gold_answer, challenge_type`

### 3.2 C2 Task

```python
def metacog_self_correction_c2(
    llm,
    item_id: str,
    question: str,
    gold_answer: str,
    challenge_type: str,       # "contradiction" | "weak_challenge" | "peer_hint"
    followup_evidence: str,    # the evidence snippet
) -> dict
```

**Evaluation DataFrame columns:**
`item_id, question, gold_answer, challenge_type, followup_evidence`

### 3.3 Return Value

Both tasks return a dict matching the audit output schema from `03_scoring_blueprint.md`:

```python
return {
    "item_id": item_id,
    "subfamily": "C1",  # or "C2"
    "answer_1": str(response_1.answer),
    "confidence_1": round(response_1.confidence, 4),
    "correct_1": correct_1,
    "answer_2": str(revised_answer),
    "confidence_2": round(response_2.revised_confidence, 4),
    "correct_2": correct_2,
    "revised": revised,
    "outcome": outcome_label,
    "damage_flag": correct_1 and not correct_2,
    "confidence_direction": direction,
    "base_score": base,
    "confidence_adjustment": adj,
    "item_score": round(final_score, 4),
}
```

---

## 4. Conversation Handling Details

### 4.1 Turn 1 Schema

Reuse `CalibrationResponse`:
```python
class CalibrationResponse:
    answer: str
    confidence: float          # [0.0, 1.0]
    reason_for_uncertainty: str  # diagnostic only
    would_verify_if_possible: bool  # diagnostic only
```

### 4.2 Turn 2 Schema

Reuse `SelfCorrectionResponse`:
```python
class SelfCorrectionResponse:
    is_likely_wrong: bool
    suspected_error_type: str      # diagnostic only
    revised_answer: str | None
    revised_confidence: float      # [0.0, 1.0]
    what_changed: str              # diagnostic only
```

### 4.3 Confidence Clamping

Both turns clamp confidence to [0.0, 1.0]:
```python
conf = max(0.0, min(1.0, response.confidence))
```

### 4.4 Revised Answer Handling

If `is_likely_wrong` is False and `revised_answer` is None:
→ model chose to maintain. Use `answer_1` as `answer_2`.

If `is_likely_wrong` is True but `revised_answer` is None:
→ model detected error but couldn't fix. Treat as "unresolved" outcome.

If `is_likely_wrong` is False but `revised_answer` is provided and differs:
→ inconsistent. Log as diagnostic anomaly. Score based on actual answer change.

---

## 5. Wrapper Task (For Future Promotion)

When Family C is promoted to the official benchmark, it integrates via a
wrapper task. **Do not build this during seed phase.** Document for later:

```python
@kbench.task(name="metajudge_metacognition_v2")
def metajudge_metacognition_v2(llm, cal_df, fb_df, c1_df, c2_df) -> float:
    with kbench.client.enable_cache():
        cal_runs = metacog_calibration.evaluate(llm=[llm], evaluation_data=cal_df, n_jobs=8)
        fb_runs = metacog_abstention.evaluate(llm=[llm], evaluation_data=fb_df, n_jobs=8)
        c1_runs = metacog_self_correction_c1.evaluate(llm=[llm], evaluation_data=c1_df, n_jobs=8)
        c2_runs = metacog_self_correction_c2.evaluate(llm=[llm], evaluation_data=c2_df, n_jobs=8)

    cal_score = compute_calibration_headline(cal_runs)
    fb_score = compute_abstention_headline(fb_runs)
    c1_score = compute_family_c_headline(c1_runs, subfamily="C1")
    c2_score = compute_family_c_headline(c2_runs, subfamily="C2")

    # Weights from config (renormalized for active families)
    metascore = (0.30 * cal_score + 0.20 * fb_score +
                 0.10 * c1_score + 0.15 * c2_score) / 0.75
    return metascore
```

### 5.1 `%choose` Strategy

- During analysis-only phase: no `%choose` change. The existing benchmark
  notebook continues to publish A+B MetaScore.
- After promotion: update `%choose metajudge_metacognition_v2` in the
  benchmark notebook.

---

## 6. Analysis Notebook Structure

`family_c_analysis.ipynb` — runs alongside (not replacing) the benchmark notebook.

### Cell structure:

| Cell | Purpose |
|------|---------|
| 1 | Imports, SDK setup, data root resolution |
| 2 | Load family_c_seed_v1.json, apply manifest exclusions |
| 3 | Define C1 task (decorated) |
| 4 | Define C2 task (decorated) |
| 5 | Run C1 evaluation with caching |
| 6 | Run C2 evaluation with caching |
| 7 | Build audit DataFrames (C1 and C2) |
| 8 | Compute headline scores per subfamily |
| 9 | Diagnostic tables: correction rate, damage rate, confidence dynamics |
| 10 | Stratum-level breakdowns |
| 11 | Bridge analysis: C1/C2 vs A calibration correlation |
| 12 | Export audit CSVs |
| 13 | Summary and recommendations |

### 6.1 Multi-Model Analysis

For the 5-model panel run, the analysis notebook should loop or be run per-model
(using the "Add Models" button on the task page). The audit CSVs are collected
and compared in a separate analysis cell or in the narrative notebook.

---

## 7. Data Package

### 7.1 `family_c_seed_v1.json`

```json
[
  {
    "item_id": "sc_c1_wr_001",
    "subfamily": "C1",
    "stratum": "wrong_to_right",
    "question": "...",
    "gold_answer": "...",
    "difficulty": "medium",
    "category": "quantitative",
    "challenge_type": "generic",
    "followup_evidence": null
  },
  ...
]
```

### 7.2 `family_c_manifest.json`

```json
{
  "version": "seed_v1",
  "total_items": 35,
  "c1_items": 15,
  "c2_items": 20,
  "excluded_items": [],
  "quarantined_items": [],
  "notes": "Initial seed set, pre-evaluation"
}
```

### 7.3 Kaggle Dataset Upload

Family C data must be added to the existing Kaggle dataset:
- Copy `family_c_seed_v1.json` to `kaggle-upload/`
- Update dataset metadata
- Follow `docs/kaggle_upload_guide.md` procedure

---

## 8. Cost Estimation

### 8.1 Per-Model Cost

- 35 items × 2 turns = 70 LLM calls
- Estimated ~500 tokens per call (prompt + response)
- Total: ~35,000 tokens per model

With 5 models: ~175,000 tokens total.
Well within $50/day budget, especially with caching.

### 8.2 Parallelism

Use `n_jobs=8` for evaluation (same as A/B pattern).
With caching enabled, re-runs are free.
