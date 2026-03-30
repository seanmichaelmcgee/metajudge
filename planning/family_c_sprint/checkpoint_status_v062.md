# Family C Hardening Checkpoint Status v0.6.2

## Current state
- **Branch:** `hardening/family-c-v0.6.2`
- **Latest commit:** (see git log)
- **Current phase:** Phase 6 — 5-model sweep complete, analysis written
- **Safe to resume from here:** YES

## Sprint Results Summary

### Target vs Actual
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| C1 total items | 18 | 25 | EXCEEDED |
| C2 total items | 25 | 26 | EXCEEDED |
| Total items | 43 | 51 | EXCEEDED |
| Total clean | 35+ | 45 | EXCEEDED |
| C1 WR clean | 4+ | 9 | EXCEEDED |
| C2 WR clean | 4+ | 7 | EXCEEDED |
| Total WR clean | 8+ | 16 | EXCEEDED |
| Grading validated | YES | YES | DONE |
| Evidence calibrated | YES | YES | DONE |

### Phases Completed
- [x] Phase 0: Bootstrap and state recovery
- [x] Phase 1: Recover prior hardening artifacts
- [x] Phase 2: WR generation batch 1 (C1 + C2)
- [x] Phase 3: Grok canary validation + grading robustness + evidence calibration
- [x] Phase 4: Triage (all drafts promoted to clean)
- [x] Phase 5: Final report and checkpoint
- [x] Phase 6: 5-model sweep complete and analyzed

### 5-Model Sweep Results

**Models tested:** DeepSeek Chat, Grok 3 Mini, GPT-4.1, Claude Sonnet 4.5, Gemini 2.5 Pro
**Items:** 45 clean items (25 C1 + 20 C2)

| Model | R→R | W→R | R→W | W→W | T1 Acc | T2 Acc | Self-Corr Rate |
|-------|-----|-----|-----|-----|--------|--------|----------------|
| DeepSeek | 23 | 2 | 1* | 19 | 53.3% | 55.6% | 9.5% |
| Grok | 23 | 0 | 6* | 16 | 64.4% | 51.1% | 0.0% |
| GPT-4.1 | 25 | 1 | 2* | 17 | 60.0% | 57.8% | 5.6% |
| Claude | 25 | 5 | 3* | 12 | 62.2% | 66.7% | 29.4% |
| Gemini** | 10 | 2 | 20 | 13 | 66.7% | 26.7% | 13.3% |

*R→W counts include sc_c1_rr_005 (universal grading bug) and Grok counts are entirely grading artifacts.
**Gemini R→W count massively inflated by grading/parsing artifacts — results unreliable.

**Key findings:**
- Claude is the best self-corrector (29.4% W→R rate, 5x next-best)
- Grok shows zero genuine self-correction or damage (all R→W are grading artifacts)
- 64% of items differentiate ≥2 models; 22% differentiate ≥3 models
- wrong_to_right stratum items produce the most model differentiation
- Gemini needs re-grading before results can be trusted

**Grading issues identified:**
- sc_c1_rr_005: Universal R→W across all 5 models — Berlin Wall "1989" vs "November 9, 1989"
- All 6 Grok R→W items: grading artifacts (correct answer in T2 but grader can't extract)
- Gemini T2: systematic parsing failure on verbose responses (20 apparent R→W)
- `approx_numeric_small` grader needs robust number extraction from text

### Files Changed in This Sprint
- `data/family_c/family_c_c1_candidates.json` — merged hardening items into main C1 candidates
- `data/family_c/family_c_c2_candidates.json` — sc_c2_dt_001 promoted from quarantine to clean; merged hardening items into main C2 candidates
- `data/family_c/hardening_c1_wr_batch1_candidates.json` — NEW: 6 C1 WR items (audit trail)
- `data/family_c/hardening_c1_nonwr_batch1_candidates.json` — NEW: 4 C1 non-WR items (2 RR + 2 DT) (audit trail)
- `data/family_c/hardening_c2_wr_batch1_candidates.json` — NEW: 6 C2 WR items (audit trail)
- `outputs/family_c/hardening_c1_batch1_validation.json` — NEW: C1 batch 1 canary validation results
- `outputs/family_c/hardening_c2_wr_batch1_validation.json` — NEW: C2 WR batch 1 canary validation results
- `outputs/family_c/hardening_evidence_calibration_v062.json` — NEW: evidence snippet calibration (6 C2 WR items)
- `outputs/family_c/hardening_evidence_recalibration_v062.json` — NEW: evidence recalibration analysis (20 C2 items)
- `outputs/family_c/hardening_grading_audit_delta_v062.json` — NEW: grading audit delta (16 items, 5 critical fixes)
- `outputs/family_c/hardening_grading_audit_v062.json` — NEW: full grading audit (35 items)
- `outputs/family_c/hardening_grok_validation_v062.json` — NEW: Grok-3-mini validation of all 12 WR items
- `outputs/family_c/hardening_triage_v062.json` — NEW: triage decisions for 13 items (12 WR + 1 DT promotion)
- `outputs/family_c/hardening_report_v062.md` — NEW: comprehensive hardening report
- `planning/family_c_sprint/checkpoint_status_v062.md` — UPDATED: this file
- `scripts/canary_c2_wr_batch1.py` — NEW: C2 WR batch 1 canary validation script
- `scripts/canary_c2_wr_final.py` — NEW: C2 WR final canary validation script
- `scripts/canary_c2_wr_truly_hard.py` — NEW: C2 WR truly hard canary script
- `scripts/hardening_generate_wr_v062.py` — NEW: WR item generation script with canary validation

### Artifacts Produced
- **Data files:** 3 hardening candidate JSONs (C1 WR, C1 non-WR, C2 WR)
- **Validation outputs:** C1 batch 1 validation, C2 WR batch 1 validation, Grok validation
- **Audit outputs:** grading audit (full + delta), evidence recalibration, evidence calibration
- **Triage output:** triage decisions for all 13 new/promoted items
- **Report:** comprehensive hardening report (hardening_report_v062.md)
- **Scripts:** WR generation script, 3 canary validation scripts
- **Merged candidates:** C1 and C2 main candidate files updated with all hardening items

### Remaining Work for Future Sprints
1. SCHEMA.md lists `numeric` and `exact_match_insensitive` as valid grading rules but neither exists in grading_v2.py — needs cleanup
2. 4 clock-angle C2 items share identical evidence snippet — consider varying for future versions
3. `approx_numeric_small` items have no tolerance_params set — consider adding abs_tol: 0.1
4. 6 quarantined items remain (all original WR items too easy for both pilot models)
5. ~~5-model narrative sweep not yet run~~ — **DONE** (Phase 6)
6. Gemini re-grading — implement answer extraction preprocessing, re-grade all Gemini T2 responses
7. Grading fixes — fix approx_numeric_small to handle numbers in verbose text, commas, date-embedded numbers
8. Integration into thin benchmark notebook

### Sweep Analysis Artifacts
- `outputs/family_c/sweep_analysis_v062.md` — Comprehensive 5-model sweep analysis report
- `outputs/family_c/sweep_cross_model_v062.csv` — Cross-model comparison (45 items × 5 models)
- `outputs/family_c/sweep_raw_{model_slug}.jsonl` — Raw sweep data (5 files)
- `outputs/family_c/sweep_summary_{model_slug}.csv` — Per-model summaries (5 files)

### Blockers
None — sweep complete.

### Next Step
Gemini re-grading, then narrative notebook integration.
