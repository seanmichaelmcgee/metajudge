# Family C Integration Notes

**Version:** v0.6.1
**Date:** 2026-03-29
**Branch:** `claude/family-c-build-v061`

---

## 1. File Manifest

| File | Purpose |
|------|---------|
| `metajudge/scoring/self_correction_v2.py` | Production scoring — 6 transition classes, confidence adjustment, rescaling |
| `config/family_c_scoring.yaml` | All tunable scoring parameters (externalized, not hardcoded) |
| `metajudge/tasks/self_correction_v2.py` | Task runner — prompt builders, grading, batch evaluation |
| `data/family_c/SCHEMA.md` | Item bundle schema documentation |
| `data/family_c/family_c_c1_candidates.json` | 15 C1 (intrinsic) candidate items |
| `data/family_c/family_c_c2_candidates.json` | 20 C2 (evidence-assisted) candidate items |
| `scripts/openrouter/client.py` | OpenRouter client for multi-model queries |

## 2. Notebook Integration

### Split Strategy
Family C runs in a **separate notebook cell block** from A/B, with its own `chats.new()` isolation per item. This prevents cross-family memory contamination.

```python
# Pseudocode for Kaggle notebook integration
import json
from metajudge.tasks.self_correction_v2 import run_family_c_batch
from scripts.openrouter.client import query

# Load items
with open("data/family_c/family_c_c1_candidates.json") as f:
    c1_items = json.load(f)
with open("data/family_c/family_c_c2_candidates.json") as f:
    c2_items = json.load(f)

# Run C1
c1_results = run_family_c_batch(c1_items, query, "deepseek-chat", json_mode=True)

# Run C2 (separate pass)
c2_results = run_family_c_batch(c2_items, query, "deepseek-chat", json_mode=True)
```

### Composite Score Update
Family C feeds into the composite MetaScore via `config/benchmark_config.yaml`:
- C1 weight: 0.10 (intrinsic self-correction — frontier probe)
- C2 weight: 0.15 (evidence-assisted — primary signal)
- Total Family C: 0.25 of composite

When Family C is missing (e.g., models not yet evaluated), the composite
gracefully re-normalizes over available families (existing behavior in
`metajudge/scoring/composite_score.py`).

## 3. Model Routing

For the 5-model validation sweep, use the OpenRouter client with these models:

| Short Name | OpenRouter ID | Tier |
|-----------|--------------|------|
| deepseek-chat | deepseek/deepseek-chat | A (cheap, high-volume) |
| grok-3-mini | x-ai/grok-3-mini | A |
| gemini-2.5-pro | google/gemini-2.5-pro | B (mid-tier) |
| claude-sonnet-4.5 | anthropic/claude-sonnet-4.5 | C (frontier) |
| gpt-4.1 | openai/gpt-4.1 | C |

**Budget**: Run Tier A first for fast iteration, then B and C for validation.
Each full sweep (35 items × 2 turns × 5 models) ≈ 350 API calls.

## 4. Scoring Pipeline

```
Turn 1 response → grade_answer() → correct_1
Turn 2 response → grade_answer() → correct_2
                → classify_transition() → transition class
                → confidence_adjustment() → conf_adj
                → score_item() → {base_score, raw_score, scaled_score}
                → build_audit_row() → full audit record
```

All audit rows are self-contained: inputs, computed fields, and scores in one dict.

## 5. Relationship to v1 Task/Scoring

| Component | v1 (placeholder) | v2 (production) |
|-----------|------------------|-----------------|
| Task file | `tasks/self_correction.py` | `tasks/self_correction_v2.py` |
| Scoring file | `scoring/self_correction_metrics.py` | `scoring/self_correction_v2.py` |
| Damage:gain | 0.1/0.9 (WRONG) | -0.40/0.20 C1, -0.25/0.25 C2 |
| Transitions | 4 classes | 6 classes |
| Config | Hardcoded | `config/family_c_scoring.yaml` |
| Evidence | Generic templates | Per-item frozen snippets |

v1 files are **not deleted** — they remain as historical reference. v2 files
are the production implementation. Import paths in notebooks should use v2.

## 6. %choose Leaderboard Strategy

When publishing to the Kaggle leaderboard:
- Primary metric: **Composite MetaScore** (A + B + C weighted)
- Diagnostic metrics: C1 headline, C2 headline, damage rate, revision improvement rate
- C1 and C2 are **always reported separately** — never averaged into a single "Family C" score

## 7. Known Limitations

1. **C1 may show floor effect**: Per Huang et al. (2024), intrinsic self-correction
   largely fails. C1 is positioned as a "frontier probe" — low scores are expected
   and informative.
2. **Grading is simplified**: `grade_answer()` in the task module is a basic dispatcher.
   Production grading should integrate with the full `grading_v2` module.
3. **Items are draft status**: All 35 items need pilot testing on 2+ models before
   promotion to "clean" status.
4. **Three-turn probes are diagnostic only**: Turn 3 data informs item quality
   assessment but is not scored in the headline metric.
