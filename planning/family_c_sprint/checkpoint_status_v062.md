# Family C Hardening Checkpoint Status v0.6.2

## Current state
- **Branch:** `hardening/family-c-v0.6.2`
- **Latest commit:** (see git log)
- **Current phase:** Phase 1 (Next-Phase) — Grading semantics frozen for WR hardening
- **Safe to resume from here:** YES
- **User confirmation required:** YES — Phase 2 (high-cost WR hardening batches) awaits user go-ahead

### Phase 1 (Next-Phase) Artifacts
- `planning/family_c_sprint/grading_freeze_note_phase1.md` — grading semantics freeze documentation
- `tests/test_sweep_grading_v2.py` — 48 unit tests for all grading rules (semantics freeze)
- `scripts/regrade_sweep_v062.py` — v2 grader with alias fix in `grade_approx_numeric_small_v2`

### Phase 1 Bug Fix: Alias Check in approx_numeric_small
- `grade_approx_numeric_small_v2` now checks text aliases before numeric extraction
- Dispatcher `grade_item_v2` now passes aliases to `grade_approx_numeric_small_v2`
- Impact on original 225 sweep results: 3 items legitimately corrected (all alias-match fixes)
  - sc_c2_rr_005 (DeepSeek, GPT-4.1): gold=7, alias "seven" now matched → W→W becomes R→R
  - sc_c2_wc_001 (Gemini): gold=8, alias "eight" now matched in T1 → W→W becomes R→W

### Next Action
- **Phase 2:** High-cost WR hardening batches (awaiting user confirmation)

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
| Grading validated | YES | YES | DONE (v2 grader adopted) |
| Evidence calibrated | YES | YES | DONE |

### Phases Completed
- [x] Phase 0: Bootstrap and state recovery
- [x] Phase 1: Recover prior hardening artifacts
- [x] Phase 2: WR generation batch 1 (C1 + C2)
- [x] Phase 3: Grok canary validation + grading robustness + evidence calibration
- [x] Phase 4: Triage (all drafts promoted to clean)
- [x] Phase 5: Final report and checkpoint
- [x] Phase 6: 5-model sweep complete and analyzed
- [x] Phase 7: Corrected sweep analysis + Gemini rerun + WR item audit

### CRITICAL: Grading Fix Impact (Phase 7)

**61 of 225 grades were wrong (27%).** The improved grader (`regrade_sweep_v062.py`) fixes:
- `extract_first_number` grabbing intermediate computation numbers (e.g., "47" from "47 × 23 = 1,081")
- Date-embedded numbers (e.g., "9" from "November 9, 1989" instead of "1989")
- Verbose T2 responses where correct answer is buried in prose
- Markdown formatting not stripped before matching

### Corrected 5-Model Sweep Results

**Models tested:** DeepSeek Chat, Grok 3 Mini, GPT-4.1, Claude Sonnet 4.5
**Items:** 45 clean items (25 C1 + 20 C2)
**Gemini excluded** — data invalidated by max_tokens=400 truncation (re-run in progress)

| Model | R→R | W→R | R→W | W→W | T1 Acc | T2 Acc | SC Rate |
|-------|-----|-----|-----|-----|--------|--------|---------|
| Claude | 40 | 2 | 1 | 2 | 91.1% | 93.3% | 50.0% |
| Grok | 40 | 0 | 0 | 5 | 88.9% | 88.9% | 0.0% |
| Gemini† | 37 | 0 | 2† | 6 | 86.7% | 82.2% | 0.0% |
| GPT-4.1 | 38 | 2 | 0 | 5 | 84.4% | 88.9% | 28.6% |
| DeepSeek | 36 | 4 | 0 | 5 | 80.0% | 88.9% | 44.4% |

†Gemini re-run with max_tokens=4096. 2 remaining R→W are residual truncation artifacts.

**Key findings (corrected):**
- All 4 reliable models achieve ≥80% T1 accuracy and ≥88.9% T2 accuracy
- Claude leads with 91.1% T1, 93.3% T2, 50% self-correction
- DeepSeek shows strongest self-correction count (4 items) with 44.4% rate (was 9.5%)
- GPT-4.1 self-corrects at 28.6% (was 5.6%)
- Grok: zero change in either direction (completely rigid)
- Only 1 genuine R→W across all 4 models (Claude on sc_c2_dt_001)
- All non-rigid models show positive T2-T1 delta (metacognitive prompt produces net benefit)

### Gemini Investigation & Re-run

- **Root cause:** max_tokens=400 insufficient for reasoning model (consumes tokens for chain-of-thought)
- **19/20 R→W items were truncation artifacts** (95%)
- **Re-run complete** with max_tokens=4096
- **Re-run results:** T1=86.7%, T2=82.2%, R→R=37, W→R=0, R→W=2†, W→W=6
  - †2 remaining R→W are residual truncation (T2=10 chars whitespace)
  - 3 items had timeout errors on T2
  - Gemini profile: rigid like Grok — no self-correction, no genuine damage
  - T1 accuracy (86.7%) ranks 3rd behind Claude (91.1%) and Grok (88.9%)

### WR Item Audit (11 Too-Easy Items)

11 WR-stratum items are R→R across all 4 reliable models:
- **RECLASSIFY (3):** sc_c1_wr_002, sc_c1_wr_004, sc_c2_wr_001 — genuinely easy, no model consistently fails
- **KEEP (8):** sc_c1_wr_006, sc_c1_wr_008, sc_c1_wr_011, sc_c2_wr_007, sc_c2_wr_008, sc_c2_wr_009, sc_c2_wr_010, sc_c2_wr_011 — well-designed traps with evidence of canary failures; sweep prompt format may help models avoid errors

**Prompt-format confound:** The sweep's "Give your answer concisely" prompt may elicit longer chain-of-thought than canary prompts, enabling models to avoid errors. The WR construct may function as designed under different prompt formats.

### Grading issues identified (original → corrected):
- sc_c1_rr_005: Universal R→W across all 5 models → all 4 reliable models now RR (Berlin Wall "1989")
- All 6 Grok R→W items: grading artifacts → all corrected to RR (zero genuine R→W for Grok)
- sc_c1_rr_002: All-WW → all 4 reliable models RR (gold=1081, comma formatting fixed)
- sc_c1_dt_002: All-WW → all 4 reliable models RR (gold=5050, text extraction fixed)
- Gemini T2: systematic truncation — NOT a grading issue, hardware/config issue

### Files Changed in Phase 7
- `outputs/family_c/sweep_analysis_v062.md` — UPDATED: corrected analysis with regrade results
- `outputs/family_c/sweep_cross_model_v062.csv` — UPDATED: corrected transitions for all models
- `outputs/family_c/sweep_raw_gemini-2-5-pro-rerun.jsonl` — NEW: Gemini re-run raw data (pending)
- `outputs/family_c/sweep_summary_gemini-2-5-pro-rerun.csv` — NEW: Gemini re-run summary (pending)
- `scripts/sweep_gemini_rerun_v062.py` — NEW: Gemini re-run script with max_tokens=4096
- `planning/family_c_sprint/checkpoint_status_v062.md` — UPDATED: this file

### Files Changed in This Sprint (Complete)
- `data/family_c/family_c_c1_candidates.json` — merged hardening items into main C1 candidates
- `data/family_c/family_c_c2_candidates.json` — sc_c2_dt_001 promoted from quarantine to clean; merged hardening items into main C2 candidates
- `data/family_c/hardening_c1_wr_batch1_candidates.json` — NEW: 6 C1 WR items (audit trail)
- `data/family_c/hardening_c1_nonwr_batch1_candidates.json` — NEW: 4 C1 non-WR items (2 RR + 2 DT) (audit trail)
- `data/family_c/hardening_c2_wr_batch1_candidates.json` — NEW: 6 C2 WR items (audit trail)
- `outputs/family_c/hardening_c1_batch1_validation.json` — NEW: C1 batch 1 canary validation results
- `outputs/family_c/hardening_c2_wr_batch1_validation.json` — NEW: C2 WR batch 1 canary validation results
- `outputs/family_c/hardening_evidence_calibration_v062.json` — NEW: evidence snippet calibration
- `outputs/family_c/hardening_evidence_recalibration_v062.json` — NEW: evidence recalibration analysis
- `outputs/family_c/hardening_grading_audit_delta_v062.json` — NEW: grading audit delta
- `outputs/family_c/hardening_grading_audit_v062.json` — NEW: full grading audit
- `outputs/family_c/hardening_grok_validation_v062.json` — NEW: Grok-3-mini validation
- `outputs/family_c/hardening_triage_v062.json` — NEW: triage decisions
- `outputs/family_c/hardening_report_v062.md` — NEW: comprehensive hardening report
- `outputs/family_c/sweep_regraded_v062.jsonl` — NEW: regraded sweep results
- `outputs/family_c/sweep_regrade_changes_v062.json` — NEW: items that changed grade
- `scripts/regrade_sweep_v062.py` — NEW: improved grader
- `scripts/sweep_gemini_rerun_v062.py` — NEW: Gemini re-run script

### Remaining Work for Future Sprints
1. ~~Gemini re-grading~~ → **DONE**: max_tokens truncation identified as root cause, re-run in progress
2. ~~Grading fixes~~ → **DONE**: improved grader adopted (regrade_sweep_v062.py)
3. Reclassify 3 WR items to RR stratum (sc_c1_wr_002, sc_c1_wr_004, sc_c2_wr_001)
4. Add harder WR items targeting 40-60% T1 accuracy
5. Test prompt-format sensitivity for WR items
6. Integrate Gemini re-run data into corrected analysis
7. Integration into thin benchmark notebook

### Blockers
None — corrected analysis complete, Gemini re-run in progress.

### Next Step
**Phase 1 — Grading semantics freeze.** Lock grader behavior with unit tests before generating new items. Define target T1 accuracy range (40-60%) for WR items. Design adversarial generation pipeline.
