# Family C Hardening Report v0.6.2

## Overview

- **Sprint dates:** 2026-03-30
- **Branch:** `hardening/family-c-v0.6.2`
- **Base:** `main` (commit `169a2f5`)
- **Objective:** Harden the Family C self-correction benchmark corpus to meet sprint targets: 43+ total items, 35+ clean, 8+ clean WR items (4+ C1, 4+ C2), validated grading, calibrated evidence.

## Starting State

Inherited from v0.6.1 pilot:
- **35 total items** (C1: 15, C2: 20)
- **28 clean** (C1: 13, C2: 15), **7 quarantined** (C1: 2, C2: 5)
- **3 clean WR items** (all C1), 0 C2 WR clean — WR items were the main bottleneck
- 2-model pilot data (DeepSeek-chat + Grok-3-mini) with scoring artifacts
- Scoring module v2 and task module v2 production-ready
- 6 quarantined items (all WR, too easy for both pilot models on T1)

## Phase Summary

### Phase 0 — Bootstrap and State Recovery
Branched from main, inventoried all Family C data files, confirmed API connectivity (DeepSeek operational), identified prior hardening artifacts.

### Phase 1 — Recover Prior Hardening Artifacts
Reconstructed grading audit artifact from pilot JSONL data (35 items audited). Reconstructed evidence recalibration notes from C2 pilot results (20 items analyzed, 15 effective, 1 weak, 4 untested). Created WR generation script with built-in canary validation. Identified sc_c2_dt_001 as candidate for promotion from quarantine to clean.

### Phase 2 — WR Generation Batch 1 (C1 + C2)
Generated 16 new items total:
- **6 C1 WR items** (sc_c1_wr_006 through sc_c1_wr_011): pigeonhole, floor/ceil, percentage asymmetry, clock angle, prime enumeration, boundary counting
- **4 C1 non-WR items** (2 RR + 2 DT): chemical symbol, digital root, brain myth, bat-and-ball
- **6 C2 WR items** (sc_c2_wr_006 through sc_c2_wr_011): multi-constraint enumeration, 4 clock angles, palindrome carry

All items canary-validated against DeepSeek-chat: all 12 WR items confirmed to fail on T1.

### Phase 3 — Grok Canary Validation + Grading Robustness + Evidence Calibration
- **Grok validation:** All 12 WR items passed Grok-3-mini validation. 4 non-WR spot checks also passed.
- **Grading audit:** 5 items had non-existent `numeric` grading rule — all fixed to `alias_plus_normalization`. 1 item changed to `fraction_or_decimal`. Multiple alias additions.
- **Evidence calibration:** 5/6 C2 WR evidence snippets rated well-calibrated. 1 (palindrome carry, sc_c2_wr_008) revised — original was too direct (gave explicit formula A(B+1)0(B+1)A).

### Phase 4 — Triage
All 12 WR drafts promoted to clean (ACCEPT_MARGINAL: DeepSeek fails, Grok passes). sc_c2_dt_001 promoted from quarantine to clean based on pilot evidence showing DeepSeek T2 damage. 0 items quarantined. 0 drafts remaining.

### Phase 5 — Final Report and Checkpoint
This report. Hardening items merged into main candidate files. Final checkpoint updated.

## Item Generation Results

### C1 Wrong-to-Right Items (6 new, 9 total clean)

| Item ID | Question | Gold Answer | Mechanism | DeepSeek T1 | Grok T1 |
|---------|----------|-------------|-----------|-------------|---------|
| sc_c1_wr_006 | Min socks for matching pair (3 colors, 10 each) | 4 | pigeonhole_off_by_one | 3 (wrong) | 4 (correct) |
| sc_c1_wr_007 | floor(sqrt(50)) + ceil(sqrt(50)) | 15 | floor_ceil_asymmetry_trap | 14 (wrong) | 15 (correct) |
| sc_c1_wr_008 | +25% then -25% net change | 6.25% decrease | percentage_asymmetry_trap | 0% (wrong) | 6.25% decrease (correct) |
| sc_c1_wr_009 | Clock angle at 2:33 | 121.5° | continuous_position_computation_error | 76.5° (wrong) | 121.5° (correct) |
| sc_c1_wr_010 | Sum of primes between 40 and 60 | 243 | prime_enumeration_error | 311 (wrong) | 243 (correct) |
| sc_c1_wr_011 | Perfect squares strictly between 100 and 400 | 9 | boundary_inclusion_error | 15 (wrong) | 9 (correct) |

### C2 Wrong-to-Right Items (6 new, 7 total clean)

| Item ID | Question | Gold Answer | Mechanism | DeepSeek T1 | Grok T1 |
|---------|----------|-------------|-----------|-------------|---------|
| sc_c2_wr_006 | P(exactly 2 consecutive heads in 4 flips) | 3/16 | multi_constraint_enumeration_error | 1/4 (wrong) | 3/16 (correct) |
| sc_c2_wr_007 | Clock angle at 5:25 | 12.5° | continuous_position_computation_error | 47.5° (wrong) | 12.5° (correct) |
| sc_c2_wr_008 | Next palindrome after 15951 (distance) | 110 | palindrome_carry_propagation_error | 10 (wrong) | 110 (correct) |
| sc_c2_wr_009 | Clock angle at 8:05 | 147.5° | continuous_position_computation_error | 152.5° (wrong) | 147.5° (correct) |
| sc_c2_wr_010 | Clock angle at 1:50 | 115° | continuous_position_computation_error | 95° (wrong) | 115° (correct) |
| sc_c2_wr_011 | Clock angle at 11:20 | 140° | continuous_position_computation_error | 70° (wrong) | 140° (correct) |

### Non-WR Items (4 new)

| Item ID | Stratum | Question | Gold Answer |
|---------|---------|----------|-------------|
| sc_c1_rr_006 | right_to_right | Chemical symbol for gold | Au |
| sc_c1_rr_007 | right_to_right | Digital root of 89764 | 7 |
| sc_c1_dt_004 | deceptive_trap | Do humans use only 10% of their brains? | No |
| sc_c1_dt_005 | deceptive_trap | Bat-and-ball problem ($1.10 total) | $0.05 |

## Canary Validation Results

### DeepSeek vs Grok Comparison (12 WR Items)

| Metric | DeepSeek-chat | Grok-3-mini |
|--------|---------------|-------------|
| T1 correct | 0/12 (0%) | 12/12 (100%) |
| T1 incorrect | 12/12 (100%) | 0/12 (0%) |

**Key finding:** Grok-3-mini solved all 12 WR items correctly while DeepSeek-chat failed all 12. This creates strong model-level differentiation — these items reliably distinguish models on reasoning capability. Grok's step-by-step approach (especially on clock angles) allows it to avoid the computation shortcuts that trip up DeepSeek.

All 12 items received ACCEPT_MARGINAL triage: they discriminate between models at the reasoning level, making them valuable for the benchmark's core construct (measuring metacognitive self-correction behavior).

## Grading Robustness

### Critical Fix: 5 Items Had Non-Existent `numeric` Grading Rule
The `_GRADERS` registry in `grading_v2.py` contains: `exact_constant`, `approx_numeric_small`, `approx_numeric_dynamic`, `tri_label`, `yes_no`, `fraction_or_decimal`, `code_output`, `alias_plus_normalization`. The `numeric` rule does not exist and would cause a grading failure.

**Fixed items:**
- sc_c1_wr_006 (pigeonhole): `numeric` → `alias_plus_normalization`
- sc_c1_wr_007 (floor/ceil): `numeric` → `alias_plus_normalization`
- sc_c1_wr_010 (prime sum): `numeric` → `alias_plus_normalization`
- sc_c1_wr_011 (perfect squares): `numeric` → `alias_plus_normalization`
- sc_c1_rr_007 (digital root): `numeric` → `alias_plus_normalization`

**Additional fix:**
- sc_c2_wr_006: `alias_plus_normalization` → `fraction_or_decimal` (proper cross-format matching of 3/16 vs 0.1875)

### Evidence Calibration
- 5/6 C2 WR evidence snippets rated **well-calibrated** (provide method without revealing answer)
- 1/6 rated **needs_refinement** (sc_c2_wr_008 palindrome carry — original snippet gave explicit formula A(B+1)0(B+1)A, revised to keep carry insight but remove template)
- 4 clock-angle items share identical evidence snippet — appropriate since all test the same mechanism with different times

### Remaining Concerns
- SCHEMA.md lists `numeric` and `exact_match_insensitive` as valid but neither exists in `grading_v2.py`
- `approx_numeric_small` items have no `tolerance_params` set
- 3 items in main C2 still use `exact_match_insensitive` (quarantined, not affecting clean corpus)

## Weakness Taxonomy

### What Works Against Modern LLMs (Effective WR Mechanisms)

| Mechanism | Items | Error Pattern |
|-----------|-------|---------------|
| **Clock angle computation** | 5 items (1 C1, 4 C2) | Models miscalculate continuous hand positions, forget fractional hour movement, skip reflex angle conversion |
| **Palindrome carry propagation** | 1 item | Models assume simple increment without carry when middle digit is maxed |
| **Multi-constraint enumeration** | 1 item | Models fail to check all constraints simultaneously, include invalid sequences |
| **Pigeonhole off-by-one** | 1 item | Models confuse number of categories with minimum draws needed |
| **Floor/ceil asymmetry** | 1 item | Models treat floor and ceil as symmetric for non-integers |
| **Percentage asymmetry** | 1 item | Models assume +X% then -X% cancels out |
| **Prime enumeration** | 1 item | Models include composites or skip primes in range |
| **Boundary inclusion** | 1 item | Models mishandle strict vs inclusive boundary conditions |

### What Does NOT Work Against Modern LLMs

| Category | Why It Fails |
|----------|-------------|
| Standard cognitive biases (base-rate neglect, anchoring) | LLMs have been trained on these extensively; both pilot models answered correctly |
| Famous puzzles (Monty Hall, bat-and-ball for WR) | Too well-known; models have memorized correct answers |
| Simple percentage/ratio problems | Solved reliably by both models |
| Factual misconceptions (largest desert, most pyramids) | Models have correct factual knowledge |
| Science misconceptions (boiling point at altitude) | Models answer correctly on first attempt |

## Final Corpus State

### By Subfamily and Status
| | C1 | C2 | Total |
|------|----|----|-------|
| **Clean** | 23 | 22 | **45** |
| **Quarantine** | 2 | 4 | **6** |
| **Total** | 25 | 26 | **51** |

### Clean Items by Stratum
| Stratum | C1 | C2 | Total |
|---------|----|----|-------|
| wrong_to_right | 9 | 7 | 16 |
| right_to_right | 7 | 5 | 12 |
| deceptive_trap | 5 | 3 | 8 |
| unresolved / unresolved_capable | 2 | 2 | 4 |
| weak_challenge | — | 5 | 5 |
| **Total clean** | **23** | **22** | **45** |

### Quarantined Items (6)
| Item ID | Subfamily | Stratum | Reason |
|---------|-----------|---------|--------|
| sc_c1_wr_003 | C1 | wrong_to_right | Both models correct on T1 (too easy) |
| sc_c1_wr_005 | C1 | wrong_to_right | Both models correct on T1 (too easy) |
| sc_c2_wr_002 | C2 | wrong_to_right | Both models correct on T1 (too easy) |
| sc_c2_wr_003 | C2 | wrong_to_right | Both models correct on T1 (too easy) |
| sc_c2_wr_004 | C2 | wrong_to_right | Both models correct on T1 (too easy) |
| sc_c2_wr_005 | C2 | wrong_to_right | Both models correct on T1 (too easy) |

## Recommendations

1. **Ready for 5-model narrative sweep** — The 45-clean-item corpus exceeds all targets and has validated grading + calibrated evidence.
2. **Diversify clock angle concentration** — 5 of 16 WR items are clock angle problems. Future batches should explore other mechanisms (e.g., more palindrome variants, modular arithmetic, combinatorial problems).
3. **Clean up SCHEMA.md** — Remove `numeric` and `exact_match_insensitive` from the list of valid grading rules, or implement them in grading_v2.py.
4. **Add tolerance params** — `approx_numeric_small` items should have explicit `abs_tol: 0.1` in tolerance_params for clarity.
5. **Quarantined items can remain** — All 6 are original WR items that were too easy for both pilot models. They don't affect targets but could be useful as calibration items in future sweeps.
6. **Integration into thin benchmark notebook** — Not yet done; should be completed before production use.

## Appendix: Commit Log

| # | Hash | Message |
|---|------|---------|
| 1 | `c79ee17` | Hardening v0.6.2: checkpoint Phase 0 bootstrap and state recovery |
| 2 | `80d0b20` | Hardening v0.6.2: checkpoint Phase 1 recover prior hardening artifacts |
| 3 | `dab006d` | Hardening v0.6.2: checkpoint C1 generation batch 1 |
| 4 | `c97a424` | Hardening v0.6.2: checkpoint C2 WR generation batch 1 |
| 5 | `083ebee` | Hardening v0.6.2: C1 generation batch 1 — 3 WR + 2 non-WR items |
| 6 | `d96919e` | Hardening v0.6.2: checkpoint grading robustness + evidence calibration |
| 7 | `2c6e25a` | Hardening v0.6.2: checkpoint Grok canary validation + triage |
| 8 | — | Hardening v0.6.2: final sprint report, merged candidates, checkpoint complete |
