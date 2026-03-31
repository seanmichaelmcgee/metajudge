# Family C Hardening Checkpoint Status v0.6.2

## Current state
- **Branch:** `hardening/family-c-v0.6.2`
- **Latest commit:** (see git log)
- **Current phase:** Phase 2 — Batch 1 frontier-validated, all 3 quarantined (too easy)
- **Safe to resume from here:** YES

## Next-Phase Progress

### Completed
- [x] Phase 0: State recovery + freeze on current truths
- [x] Phase 1: Grading semantics frozen (unit tests, alias fix, freeze note)
- [x] Phase 2 Batch 1: 3 WR candidates generated (2 C1, 1 C2)
- [x] Phase 2 Batch 1 Validation: Frontier check — all 3 quarantined (too easy)

### Pending
- [ ] Phase 2 Batch 2+: More WR hardening (need ~8-12 more hard WR items)
- [ ] Phase 3: C2 snippet calibration + edge-case cleanup
- [ ] Phase 4: Integrated narrative-sweep preparation
- [ ] Phase 5: Post-sweep interpretation + benchmark recommendation

### Phase 2 Batch 1 Generation Results
| Item ID | Subfamily | Gold | Mechanism | Canary Acc | Verdict |
|---------|-----------|------|-----------|------------|---------|
| sc_c1_wr_012 | C1 | 42 | digit_range_boundary_error | 33% (1/3) | ACCEPT → QUARANTINE |
| sc_c1_wr_013 | C1 | 31 | upper_bound_omission_stars_bars | 67% (2/3) | ACCEPT → QUARANTINE |
| sc_c2_wr_012 | C2 | 6.81 | temperature_dependent_kw_ignored | 0% (0/3) | ACCEPT → QUARANTINE |
| (rejected) | C1 | 6 | odd_balls_in_boxes | 100% (3/3) | REJECT (too easy) |

### Frontier Validation Results (5 models × 3 items = 15 trials)
| Item ID | GPT-5.2 | Claude Opus | Gemini 3 Pro | DeepSeek-R1 | Grok-4.1 | Acc (excl Gemini) |
|---------|---------|-------------|-------------|-------------|----------|-------------------|
| sc_c1_wr_012 | ✅ | ✅ | ❌ (trunc) | ✅ | ✅ | 100% (4/4) |
| sc_c1_wr_013 | ✅ | ✅ | ❌ (trunc) | ✅ | ✅ | 100% (4/4) |
| sc_c2_wr_012 | ✅ | ✅ | ❌ (trunc) | ✅ | ✅ | 100% (4/4) |

**Key finding:** Canary accuracy (Tier 1 cheap models) does NOT predict frontier difficulty. All 3 items were hard for T1 but trivially easy for frontier reasoning models. Gemini failures are truncation artifacts (max_tokens too low), not genuine reasoning errors.

**Lesson for Batch 2:** Must add a **frontier pre-test** during generation — require ≥1 frontier model to fail before accepting any candidate.

### Model Routing Used (Batch 1)
- Author: claude-sonnet-4.6 (Tier 2)
- Adversary: grok-4.1-fast (Tier 2)
- Auditor: gpt-5.2 (Tier 2)
- Canaries: gemini-2.5-flash-lite, grok-3-mini, gpt-5-mini (Tier 1)
- Frontier validators: gpt-5.2, claude-opus-4.6, gemini-3-pro-preview, deepseek-r1, grok-4.1 (Tier 2/3)

### Dataset Counts (post-validation)
| Set | C1 | C2 | Total |
|-----|----|----|-------|
| Clean | 23 | 22 | 45 |
| Quarantine | 4 | 5 | 9 |
| **Total** | **27** | **27** | **54** |

### WR Item Counts (post-validation)
| Category | Clean | Quarantine |
|----------|-------|------------|
| C1 WR | 11 | 2 (batch 1) |
| C2 WR | 7 | 1 (batch 1) |
| **Total WR** | **18** | **3** |

Note: 3 batch-1 quarantine items are separate from the 6 prior quarantine items.

### What works for WR difficulty (from 45 clean items)
- Banker's rounding (sc_c1_wr_001: 60% T1)
- Clock angles with continuous second-hand position (sc_c1_wr_009: 60% T1)
- Prime enumeration boundary errors (sc_c1_wr_010: 60% T1)
- Multi-constraint enumeration with non-obvious constraint counts (sc_c2_wr_006: 40% T1)

### What doesn't work
- Common misconceptions (too well-known to frontier models)
- Standard combinatorics like stars-and-bars (easily solved)
- Well-known chemistry facts (trivially recalled)
- Standard cognitive biases (pattern-matched and corrected)

### Exact next action
- User confirmation required: YES
- Wait for user to direct Batch 2 strategy
- Need items where ≥1 frontier model genuinely fails (not truncation)
- Consider: frontier pre-test gate, harder multi-step reasoning, ambiguous conventions

### Artifacts written this session
- `scripts/wr_hardening_phase2.py` — multi-turn hardening loop (full batch runner)
- `scripts/wr_hardening_single.py` — single-item hardening (used for batch 1)
- `scripts/frontier_validate_batch1.py` — 5-model frontier validation script
- `outputs/family_c/phase2_wr_hardening/batch1_report.md` — batch 1 generation report
- `outputs/family_c/phase2_wr_hardening/batch1_validation_report.md` — frontier validation report
- `outputs/family_c/phase2_wr_hardening/batch1_frontier_validation.jsonl` — raw validation results (15 trials)
- `outputs/family_c/phase2_wr_hardening/audit_logs/` — full audit logs per item
- `data/family_c/family_c_c1_candidates.json` — 2 batch-1 items moved to quarantine
- `data/family_c/family_c_c2_candidates.json` — 1 batch-1 item moved to quarantine
