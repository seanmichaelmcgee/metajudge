# Grading V2 Migration Guide

## What changed

`metajudge.scoring.grading_v2` is a **new, additive** grading module that sits alongside
`metajudge.scoring.adjudication`. It does NOT replace or modify `adjudication.py`.

### Why

The V4 answer-validity audit identified 8 HIGH-severity false fails and 9 MEDIUM-severity
grading issues caused by the original three-rule system (`alias`, `numeric`, `yes_no`).
Root causes:

| Pattern | Issue | Fix in V2 |
|---------|-------|-----------|
| T/F-contested conflict | `yes_no` rule rejects "contested" even when gold is "contested" | New `tri_label` grader with {true, false, contested} label space |
| Whitespace around × | `1.67 × 10⁻²⁷` fails alias match due to spaces | `_normalize_sci()` collapses spaces and Unicode superscripts |
| Stale population density | Time-sensitive numerics fail with tight tolerance | `approx_numeric_dynamic` with `time_anchor` metadata and 10% rel_tol |
| rel_tol=1e-9 too strict | Sig-fig rounding causes false fails on exact constants | Per-item configurable `tolerance_params` (e.g., rel_tol=1e-6) |
| Fraction/decimal mismatch | "4/5" not recognized as equivalent to "0.8" | `fraction_or_decimal` grader using `fractions.Fraction` |
| Alias gaps on numerics | Numeric items classified under `alias` rule | Reclassified to appropriate numeric grader rules |

### New grader rules (8 total)

| Rule | Description |
|------|-------------|
| `exact_constant` | SI-defined constants, float comparison with configurable `rel_tol` |
| `approx_numeric_small` | Fixed-tolerance numerics (`abs_tol` and/or `rel_tol`) |
| `approx_numeric_dynamic` | Time-sensitive numerics with `time_anchor`/`source_anchor` metadata |
| `tri_label` | Three-valued {true, false, contested} with canonical form mapping |
| `yes_no` | Binary true/false with synonym expansion |
| `fraction_or_decimal` | Accepts both "4/5" and "0.8" via `fractions.Fraction` |
| `code_output` | Exact string match after strip/lower |
| `alias_plus_normalization` | Enhanced alias matching with sci-notation normalization and numeric fallback |

## How to switch

### 1. Load the registry

```python
from metajudge.scoring.grading_v2 import load_registry, grade_item

registry = load_registry("data/adjudication_registry.json")
```

### 2. Grade items

```python
result = grade_item("gen_a_030", model_answer="71", registry=registry)
# {'correct': True, 'method': 'approx_numeric_small', 'match_detail': 'within tolerance abs=1.0 rel=0.0'}
```

### 3. Batch grading

```python
results = [grade_item(item_id, answer, registry) for item_id, answer in submissions]
accuracy = sum(r["correct"] for r in results) / len(results)
```

## Backward compatibility

- `adjudication.py` is untouched. All existing imports (`adjudicate_answer`,
  `adjudicate_with_fallback`, `canonicalize_answer`) continue to work.
- `grading_v2.py` has zero imports from `adjudication.py` or `metajudge.utils.text`.
  No circular dependency risk.
- The registry is a standalone JSON file — it does not affect any existing data files.

## Registry schema

Each entry in `data/adjudication_registry.json`:

```json
{
  "item_id": "gen_a_030",
  "answer_type": "numeric",
  "grader_rule": "approx_numeric_small",
  "gold_answer": "70",
  "accepted_forms": ["70"],
  "tolerance_class": "abs_1",
  "tolerance_params": {"abs_tol": 1.0},
  "time_anchor": null,
  "source_anchor": null,
  "normalization_notes": null,
  "tri_label_space": null,
  "edge_case_notes": null
}
```

## Test coverage

`tests/test_grading_v2.py` — 88 tests covering:
- All 8 grader rules (happy path + edge cases)
- All 6 audit regression items (gen_a_030, gen_a2_032, gen_a3_001, gen_b3_005, gen_b_004, gen_a_042)
- Normalization helpers (_normalize, _normalize_sci, _parse_float, _nums_close)
- Registry loading and dispatch integration
- Registry completeness (102 items, required keys)
