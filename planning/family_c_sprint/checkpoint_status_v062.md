# Family C Hardening Checkpoint Status v0.6.2

## Current state
- **Branch:** `hardening/family-c-v0.6.2`
- **Current phase:** Phase 1 — Recovery complete, ready for Phase 2 generation
- **Safe to resume from here:** YES

## What is done

### Phase 0 — Bootstrap and State Recovery
- [x] Branch created from latest main
- [x] All required files read and understood
- [x] Family C data inventoried
- [x] Prior hardening artifacts identified
- [x] Checkpoint file created

### Phase 1 — Recover and Preserve Prior Hardening Outputs
- [x] API smoke test passed (deepseek-chat confirmed operational)
- [x] Grading audit artifact reconstructed from pilot JSONL data
- [x] Evidence recalibration notes reconstructed from C2 pilot results
- [x] Quarantine promotion assessment completed (sc_c2_dt_001 → promote to clean)
- [x] WR generation script created and dry-run validated

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

### New v0.6.2 Phase 1 Artifacts
| File | Status |
|------|--------|
| `outputs/family_c/hardening_grading_audit_v062.json` | NEW — 35 items audited |
| `outputs/family_c/hardening_evidence_recalibration_v062.json` | NEW — 20 C2 items analyzed |
| `scripts/hardening_generate_wr_v062.py` | NEW — WR generation script with canary validation |

### Planning Documents
| File | Status |
|------|--------|
| `planning/family_c_sprint/13_pilot_orchestrator_instructions.md` | Present |
| `planning/family_c_sprint/14_hardening_orchestrator_prompt.md` | NOT FOUND (confirmed lost) |
| `planning/family_c_sprint/15_resume_safe_hardening_orchestrator_prompt.md` | Present |

## Artifacts produced (Phase 1)
- `outputs/family_c/hardening_grading_audit_v062.json` — grading audit for all 35 items
- `outputs/family_c/hardening_evidence_recalibration_v062.json` — evidence effectiveness for all 20 C2 items
- `scripts/hardening_generate_wr_v062.py` — WR item generation script with canary validation
- `planning/family_c_sprint/checkpoint_status_v062.md` (this file, updated)

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

### Grading Audit Summary
- **6 grading rule fixes** were applied during the v0.6.1 pilot (documented in audit artifact)
- **6 items** flagged with potential grading issues (high-confidence stubborn_wrong — may warrant manual check)
- **8 items** with remaining concerns (quarantine items + items using exact_match_insensitive)

### Evidence Recalibration Summary
- **15/20 C2 items** rated effective
- **1/20** rated weak (evidence didn't trigger needed revision)
- **4/20** rated untested (both models correct on T1 — all quarantined WR items)
- **0/20** rated too_strong
- **sc_c2_dt_001**: Recommended for promotion to clean (deceptive_trap working as designed)

### What Prior Work is Committed vs Missing
| Work | Committed? | Notes |
|------|-----------|-------|
| Family C items (C1: 15, C2: 20) | YES | In data/family_c/ |
| Scoring module v2 | YES | metajudge/scoring/self_correction_v2.py |
| Task module v2 | YES | metajudge/tasks/self_correction_v2.py |
| OpenRouter client | YES | scripts/openrouter/client.py |
| Pilot data (2-model) | YES | outputs/family_c/ |
| Pilot report v0.6.1 | YES | outputs/family_c/pilot_report_v061.md |
| Grading audit | YES (NEW) | outputs/family_c/hardening_grading_audit_v062.json |
| Evidence recalibration | YES (NEW) | outputs/family_c/hardening_evidence_recalibration_v062.json |
| WR generation script | YES (NEW) | scripts/hardening_generate_wr_v062.py |
| 14_hardening_orchestrator_prompt.md | CONFIRMED LOST | Not recoverable — only doc 15 exists |

### Sprint Targets (from v0.6.2 resume prompt)
- **18 C1 items** total
- **25 C2 items** total
- **43 Family C items** total
- **35+ clean items** after triage
- **8+ clean wrong-to-right items**, with >=4 C1 WR and >=4 C2 WR
- All grading rules validated
- Evidence snippets calibrated
- All work in committed repo artifacts

### Key Gaps Remaining
1. **Wrong-to-right items are the main bottleneck**: Only 3 clean WR items exist (all C1). Need 5 more WR clean total, with at least 4 C2 WR.
2. **Need 3 new C1 items** and **5 new C2 items** to hit count targets.
3. **sc_c2_dt_001** should be promoted to clean (recommendation in recalibration artifact).

## Exact next step
- **Phase 2 — Wrong-to-right generation batch 1**
  - Run `scripts/hardening_generate_wr_v062.py --subfamily C2 --batch-size 4`
  - Canary-validate generated items
  - Merge passing items into candidate JSONs
  - Run `scripts/hardening_generate_wr_v062.py --subfamily C1 --batch-size 3`
  - Promote sc_c2_dt_001 to clean
  - Micro-commit after each batch

## Blockers / user decisions needed
- None. API key confirmed working. All tools in place for Phase 2.

## Resume safe: YES
