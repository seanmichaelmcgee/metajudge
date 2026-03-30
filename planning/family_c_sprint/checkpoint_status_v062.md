# Family C Hardening Checkpoint Status v0.6.2

## Current state
- **Branch:** `hardening/family-c-v0.6.2`
- **Latest commit:** `1335010` (base — inherited from main)
- **Current phase:** Phase 0 — Bootstrap complete
- **Safe to resume from here:** YES

## What is done

### Phase 0 — Bootstrap and State Recovery
- [x] Branch created from latest main
- [x] All required files read and understood
- [x] Family C data inventoried
- [x] Prior hardening artifacts identified
- [x] Checkpoint file created
- [ ] API smoke test — BLOCKED (OPENROUTER_API_KEY not set in environment)

## Files inventoried

### Family C Data Files
| File | Path | Count |
|------|------|-------|
| C1 candidates | `data/family_c/family_c_c1_candidates.json` | 15 items |
| C2 candidates | `data/family_c/family_c_c2_candidates.json` | 20 items |
| Schema | `data/family_c/SCHEMA.md` | — |

### C1 Item Breakdown (15 total)
| Status | Count |
|--------|-------|
| clean | 13 |
| quarantine | 2 |

| Stratum | Count |
|---------|-------|
| wrong_to_right | 5 |
| right_to_right | 5 |
| unresolved | 2 |
| deceptive_trap | 3 |

### C2 Item Breakdown (20 total)
| Status | Count |
|--------|-------|
| clean | 15 |
| quarantine | 5 |

| Stratum | Count |
|---------|-------|
| wrong_to_right | 5 |
| right_to_right | 5 |
| weak_challenge | 5 |
| unresolved_capable | 2 |
| deceptive_trap | 3 |

### Scoring & Task Modules
| File | Status |
|------|--------|
| `metajudge/scoring/self_correction_v2.py` | Present, production-ready |
| `metajudge/tasks/self_correction_v2.py` | Present, production-ready |
| `config/family_c_scoring.yaml` | Present (v0.6.1) |
| `scripts/openrouter/client.py` | Present, 5-model routing |

### Prior Outputs (v0.6.1 pilot)
| File | Status |
|------|--------|
| `outputs/family_c/smoke_test_results.txt` | Present — all 5 models OK |
| `outputs/family_c/pilot_raw_deepseek-chat.jsonl` | Present (33KB) |
| `outputs/family_c/pilot_raw_grok-3-mini.jsonl` | Present (32KB) |
| `outputs/family_c/pilot_summary_deepseek-chat.csv` | Present |
| `outputs/family_c/pilot_summary_grok-3-mini.csv` | Present |
| `outputs/family_c/pilot_report_v061.md` | Present |
| `scripts/pilot_family_c.py` | Present |

### Planning Documents
| File | Status |
|------|--------|
| `planning/family_c_sprint/13_pilot_orchestrator_instructions.md` | Present |
| `planning/family_c_sprint/14_hardening_orchestrator_prompt.md` | NOT FOUND |
| `planning/family_c_sprint/15_resume_safe_hardening_orchestrator_prompt.md` | Present |

## Artifacts produced
- `planning/family_c_sprint/checkpoint_status_v062.md` (this file)

## State Recovery Section

### Current Counts vs Sprint Targets
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| C1 total items | 15 | 18 | -3 |
| C2 total items | 20 | 25 | -5 |
| Total items | 35 | 43 | -8 |
| C1 clean | 13 | — | — |
| C2 clean | 15 | — | — |
| Total clean | 28 | 35+ | -7 |
| C1 WR clean | 3 | 4+ | -1 |
| C2 WR clean | 0 | 4+ | -4 |
| Total WR clean | 3 | 8+ | -5 |

### Existing Hardening Artifacts
- **Committed from v0.6.1 pilot:** smoke test, 2-model pilot data, pilot report, triage results
- **Grading audit artifacts:** NOT FOUND in outputs/family_c/ (work mentioned in resume prompt as done during prior VPS run, but not committed)
- **Evidence recalibration artifacts:** NOT FOUND (same — mentioned but not committed)
- **Generation scripts (hardening_generate_v2.py):** NOT FOUND
- **Quarantine manifest:** Embedded in candidate JSONs (draft_status field), no separate manifest file
- **Prior checkpoint files:** NONE (this is the first)

### What Prior Work is Committed vs Missing
| Work | Committed? | Notes |
|------|-----------|-------|
| Family C items (C1: 15, C2: 20) | YES | In data/family_c/ |
| Scoring module v2 | YES | metajudge/scoring/self_correction_v2.py |
| Task module v2 | YES | metajudge/tasks/self_correction_v2.py |
| OpenRouter client | YES | scripts/openrouter/client.py |
| Pilot data (2-model) | YES | outputs/family_c/ |
| Pilot report v0.6.1 | YES | outputs/family_c/pilot_report_v061.md |
| Grading audit fixes | PARTIAL | 6 grading rule fixes committed in pilot, but no audit artifact file |
| Evidence recalibration | NOT COMMITTED | Prior VPS run mentioned doing this — artifacts lost |
| hardening_generate_v2.py | NOT COMMITTED | Script mentioned in resume prompt — never committed |
| 14_hardening_orchestrator_prompt.md | NOT COMMITTED | Resume prompt says it was copied, but file not in repo |

### Sprint Targets (from v0.6.2 resume prompt)
- **18 C1 items** total
- **25 C2 items** total
- **43 Family C items** total
- **35+ clean items** after triage
- **8+ clean wrong-to-right items**, with ≥4 C1 WR and ≥4 C2 WR
- All grading rules validated
- Evidence snippets calibrated
- All work in committed repo artifacts

### Key Gaps Identified
1. **Wrong-to-right items are the main bottleneck**: Only 3 clean WR items exist (all C1). Need 5 more WR clean total, with at least 4 C2 WR.
2. **Need 3 new C1 items** and **5 new C2 items** to hit count targets.
3. **Prior hardening artifacts (grading audit, evidence recalibration) were lost** — must be regenerated.
4. **No hardening orchestrator prompt (doc 14)** committed — only the resume-safe v0.6.2 version (doc 15) exists.

## Exact next step
- **Phase 1 — Recover and preserve prior hardening outputs**
  - Verify grading audit state from pilot data
  - Reconstruct evidence recalibration notes from pilot results
  - Begin wrong-to-right item generation planning

## Blockers / user decisions needed
1. **OPENROUTER_API_KEY not set in environment** — must be provided before any API calls (generation, validation, canary testing)
2. No other blockers identified — repo state is clean and well-structured

## Exact next actions for Phase 1
1. Set OPENROUTER_API_KEY environment variable
2. Re-run smoke test to verify API connectivity
3. Reconstruct grading audit artifact from pilot data
4. Reconstruct evidence recalibration notes
5. Begin WR item generation (small batches, 2-4 items per batch)
6. Canary-validate new WR items against cheap models
7. Update candidate JSONs with new items
8. Micro-commit after each batch
