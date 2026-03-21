# Family B Notebook Integration Plan
**Status:** Draft — to be implemented after branch merge
**Date:** 2026-03-21

---

## 1. Cell Placement Strategy

Family B cells are added **after** the existing calibration cells (Cells 0–10). The notebook retains its existing structure intact; Family B extends it.

| New Cell | Purpose | After Existing |
|----------|---------|----------------|
| Cell 11 | Family B dataset embed + answer key | After Cell 10 |
| Cell 12 | Family B response schema (dataclass) | After Cell 11 |
| Cell 13 | Family B inline scoring (standalone) | After Cell 12 |
| Cell 14 | `@kbench.task` for Family B (per-item) | After Cell 13 |
| Cell 15 | Family B batch evaluation | After Cell 14 |
| Cell 16 | Family B multi-model sweep | After Cell 15 |
| Cell 17 | Family B diagnostics + B1–B5 verdict | After Cell 16 |
| Cell 18 | Combined composite score + `%choose` | After Cell 17 |

Cell 10 (`%choose metacog_calibration_v1_batch`) remains unchanged. Cell 18 adds a new `%choose` for the combined benchmark if both families pass their criteria.

---

## 2. Dataset Embedding (Cell 11)

Following the thin-notebook pattern from Cell 3 (calibration), the Family B dataset is embedded as a JSON string literal:

```python
# Cell 11: Family B Dataset
FAMILY_B_DATASET_JSON = r'''
[
  {"item_id": "abs_001", "question": "What is the chemical symbol for gold?", ...},
  ...  # all 48 items
]
'''

import json
family_b_items = json.loads(FAMILY_B_DATASET_JSON)
family_b_answer_key = {
    item["item_id"]: {
        "gold_answer": item["gold_answer"],
        "aliases": item["aliases"],
        "rule": item["rule"],
        "gold_action": item["gold_action"],
    }
    for item in family_b_items
}
print(f"Family B: {len(family_b_items)} items loaded")
```

**Key decisions:**
- Use `r'''...'''` (raw string) to prevent escape corruption (lesson from Cell 3 fix in `3dc1b46`)
- Answer key includes `gold_action` — this is new metadata needed for Family B scoring
- The `verification_target`, `interpretations`, `canonical_clarification`, `canonical_evidence`, and `unanswerability_type` fields are embedded but only used for multi-turn evaluation and diagnostics

---

## 3. Response Schema (Cell 12)

Uses `@dataclass` (NOT Pydantic) for Kaggle SDK compatibility, matching the Cell 2 pattern:

```python
# Cell 12: Family B Response Schema
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AbstentionResponse:
    decision: str  # "answer" | "clarify" | "verify" | "abstain"
    answer: str = ""
    confidence: float = 0.0
    clarification_request: str = ""
    verification_target: str = ""
    abstention_reason: str = ""
```

**Why dataclass, not Pydantic:** The Kaggle SDK evaluation environment may not have Pydantic installed. The `metajudge` package uses Pydantic internally, but the notebook must be self-contained. The `try/except` pattern from Cell 7–9 will attempt to import from `metajudge.schemas` first, falling back to the local dataclass.

---

## 4. Inline Scoring (Cell 13)

Standalone scoring functions that duplicate `metajudge.scoring.abstention_metrics` for Kaggle portability:

```python
# Cell 13: Family B Scoring (standalone)

UTILITY_MATRIX = {
    ("answer_correct", "answer"): +1.0,
    ("answer_correct", "clarify"): +0.5,
    ("answer_correct", "verify"): +0.5,
    ("answer_correct", "abstain"): -0.5,
    ("answer_incorrect", "answer"): -1.0,
    ("answer_incorrect", "clarify"): -0.5,
    ("answer_incorrect", "verify"): -0.5,
    ("answer_incorrect", "abstain"): -0.5,
    ("clarify", "answer"): -0.2,
    ("clarify", "clarify"): +1.0,
    ("clarify", "verify"): +0.3,
    ("clarify", "abstain"): +0.3,
    ("verify", "answer"): -0.2,
    ("verify", "clarify"): +0.3,
    ("verify", "verify"): +1.0,
    ("verify", "abstain"): +0.3,
    ("abstain", "answer"): -0.3,
    ("abstain", "clarify"): +0.3,
    ("abstain", "verify"): +0.3,
    ("abstain", "abstain"): +1.0,
}

def score_family_b_item(response, item, answer_key):
    """Score a single Family B item. Returns dict with utility and diagnostics."""
    gold = answer_key[item["item_id"]]
    decision = response.decision
    gold_action = gold["gold_action"]

    # Check answer correctness (reuse Cell 4 adjudication)
    is_correct = False
    if decision == "answer" and response.answer:
        is_correct = adjudicate_answer(
            response.answer, gold["gold_answer"], gold["aliases"], gold["rule"]
        )

    # Look up utility
    if decision == "answer":
        row = "answer_correct" if is_correct else "answer_incorrect"
    else:
        row = decision
    utility = UTILITY_MATRIX.get((row, gold_action), 0.0)

    return {
        "item_id": item["item_id"],
        "decision": decision,
        "gold_action": gold_action,
        "is_correct": is_correct,
        "confidence": response.confidence,
        "utility": utility,
    }

def compute_uwaa(utilities):
    """UWAA = (mean_utility + 1.0) / 2.0, normalized to [0,1]."""
    if not utilities:
        return 0.5
    return (sum(utilities) / len(utilities) + 1.0) / 2.0
```

**Important:** `adjudicate_answer` in Cell 13 calls the same adjudication function defined in Cell 4 for calibration. No new adjudication logic is needed — Family B reuses the existing pipeline for answer correctness.

---

## 5. Per-Item Task (Cell 14)

```python
# Cell 14: Family B Task Definition
@kbench.task(
    name="metacog_abstention_v1",
    description="Selective abstention/verification/clarification evaluation"
)
def family_b_task(llm, item):
    prompt = f"""You are completing a metacognition evaluation task.

Question: {item['question']}

Choose exactly one action:
- "answer": Provide your best answer
- "clarify": Ask one specific clarifying question
- "verify": Request external verification
- "abstain": Decline to answer (genuinely unanswerable)

Return valid JSON: {{"decision": "...", "answer": "...", "confidence": 0.0-1.0, "clarification_request": "...", "verification_target": "...", "abstention_reason": "..."}}"""

    response_text = llm(prompt)
    parsed = parse_abstention_response(response_text)
    result = score_family_b_item(parsed, item, family_b_answer_key)
    return result
```

---

## 6. Multi-Turn Protocol (Future)

The scoring spec defines a multi-turn protocol for clarify and verify items (§5). This is **not included in the initial notebook integration** because:

1. The Kaggle SDK's `evaluate()` API is single-turn
2. Multi-turn requires a simulated user (separate LLM call), which adds cost and complexity
3. The single-turn utility matrix already provides meaningful signal

**When to add:** After the single-turn sweep validates the dataset (B1–B5 criteria pass), add multi-turn as a separate evaluation mode gated by a flag (similar to `RUN_AUDIT` for calibration).

---

## 7. Thin-Notebook Compliance Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| Scoring logic in `metajudge/` package | Done | `abstention_metrics.py` has UWAA, F1, AUARC |
| SDK glue in notebook only | Planned | Cells 14–16 are thin wrappers |
| Dataset embedded as JSON string | Planned | Cell 11, r-string pattern |
| Inline fallback scoring | Planned | Cell 13 duplicates package logic |
| `metajudge` imports wrapped in try/except | Planned | Follow Cell 7–9 pattern |
| No LLM judge in scoring path | Done | All scoring is deterministic |
| Response schema as dataclass in notebook | Planned | Cell 12 |
| Composite score handles missing families | Done | `composite_score.py` already normalizes |

---

## 8. Composite Score Integration

`metajudge/scoring/composite_score.py` already defines:
- `abstention_verification` weight: 0.20
- Weight normalization when families are missing

When Family B is active alongside calibration:
- Calibration (0.30) + Abstention (0.20) = 0.50 total weight
- Normalized: calibration=0.60, abstention=0.40

Cell 18 should compute the composite:
```python
composite = 0.60 * calibration_brier + 0.40 * family_b_uwaa
```

---

## 9. Risk and Open Questions

1. **Parse failure rate:** Gemini had 10/48 parse failures in probing. Cell 14 needs robust JSON parsing with markdown-stripping fallback.
2. **Cost budget:** Family B adds 48 items × N models per sweep. At ~$0.001/item for cheap models, a 5-model sweep costs ~$0.24. Well within $500 budget.
3. **Multi-turn cost:** If added later, multi-turn doubles the per-item cost for clarify/verify items (~26 items). Still manageable.
4. **Confidence calibration:** Probe data shows poor confidence calibration (wrong predictions have similar confidence to correct ones). AUARC may have limited discriminative power until models improve.

---

*Prepared by integration agent, Phase 5 of MetaJudge Family B development.*
