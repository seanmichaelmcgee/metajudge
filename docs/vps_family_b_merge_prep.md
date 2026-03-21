# Family B Merge Prep

## Source Branch
`feat/family-b-selective-abstention` (6 commits, 17 files changed)

## Target Branch
`vps/lean-calibration-v2` (lean notebook upgraded to grading_v2 with V4.2 data)

## What Was Merged

### New Files Added
- `data/family_b_pilot_v2.json` — 48-item pilot dataset (3-model probed)
- `data/family_b_probe_report.json` — Probe results summary
- `data/family_b_rejection_log.json` — Items rejected during curation
- `data/probe_results/` — Per-model probe analysis (Claude, DeepSeek, Gemini)
- `docs/family_b_dataset_design.md` — Dataset design rationale
- `docs/family_b_kickoff_findings.md` — Literature kickoff findings
- `docs/family_b_literature_review.md` — Full literature review
- `docs/family_b_notebook_integration.md` — Notebook cell specifications
- `docs/family_b_scoring_spec.md` — Scoring specification (UWAA, F1, AUARC)
- `scripts/family_b_probe.py` — Multi-model probing script
- `tests/test_family_b.py` — 34 Family B tests

### Modified Files
- `metajudge/schemas/response_schemas.py` — Added `AbstentionResponse` Pydantic schema
- `metajudge/scoring/abstention_metrics.py` — Rewritten: UWAA, action F1, AUARC, utility matrix
- `metajudge/tasks/abstention_verification.py` — Updated task wiring
- `tests/unit/test_scoring.py` — Updated test imports

## Conflict Resolution
The merge completed cleanly (no conflicts). Both branches had different scopes:
- `vps/lean-calibration-v2`: notebook upgrade + grading_v2
- `feat/family-b-selective-abstention`: Family B scoring + data + tests

## Post-Merge Notebook Changes
Family B cells (9–15) added to lean notebook after calibration cells. The `%choose` cell moved to position 16 (end of notebook).

## Post-Merge SOUL.md Patch
Updated §8 action labels from `ask_clarifying_question`/`verify_needed` to canonical short labels `clarify`/`verify`.
