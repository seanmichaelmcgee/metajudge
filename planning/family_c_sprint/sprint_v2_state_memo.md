# Sprint v2 State-Recovery Memo
**Branch:** sprint/family-c-v2 (fresh off main)
**Date:** 2026-03-31
**Sprint blueprint:** planning/family_c_sprint/21_family_c_design_review_v2.md

## Current Repository State
- Branch created from: main at commit 38e1dec9c0ebc8a984cf1025eb9dea533fa5bb19
- Previous sprint branch: hardening/family-c-v0.6.2 (PR #16)

## Dataset Inventory
- C1 candidates: 27 total, 23 clean, 4 quarantine
- C2 candidates: 27 total, 22 clean, 5 quarantine
- Total clean items: 45
- WR items (clean): C1=9, C2=7
- WR items (quarantine): C1=4, C2=5

## Current Code State (pre-Phase 1 changes)
- _RAW_MAX: 0.30 (needs change to 0.65)
- C2 standard damage: -0.25 (needs change to -0.50)
- C1 T2 prompt: "Please reconsider your answer carefully. Take a moment to verify your reasoning step by step. What is your final answer?" (needs redesign to third-person detect-only)
- C2 T2 prompt: "Here is some additional information:\n\n{evidence}\n\nGiven this additional information, please reconsider. What is your final answer?" (needs redesign to reviewer's note framing)
- Temperature: 0.3 (needs change to 0.0 for C1/B0)
- B0 baseline: NOT IMPLEMENTED (needs addition)
- Confidence elicitation: NOT IMPLEMENTED (needs addition)
- Edit-distance metric: NOT IMPLEMENTED (needs addition)
- Word-number parsing: NOT IMPLEMENTED (needs addition)
- LaTeX fraction parsing: NOT IMPLEMENTED (needs addition)

## Grading Bugs to Fix (Phase 1)
1. sc_c2_rr_005: grading_rule is `approx_numeric_small`, needs `alias_plus_normalization` (word "seven" not parsed)
2. Word-number parsing missing from numeric grader
3. LaTeX \frac{}{} parsing missing
4. Unresolved-stratum aliases too narrow (sc_c2_ur_001, sc_c2_ur_002)
5. Regrade improvements from scripts/regrade_sweep_v062.py not in production grader

## Scoring Changes Needed (Phase 1)
1. _RAW_MAX: 0.30 -> 0.65
2. C2 standard damage: -0.25 -> -0.50 (achieving 2:1 damage:gain ratio)
3. Update unit tests for new expected values

## Test Status
All 65 tests passing:
```
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_wrong_to_correct_is_correction_gain PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_correct_to_correct_no_revision PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_correct_revised_same_answer PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_correct_to_wrong_is_damage PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_wrong_stays_wrong PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_wrong_revised_still_wrong PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_none_confidence PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_unresolved_correct PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_unresolved_wrong PASSED
tests/unit/test_self_correction_v2.py::TestTransitionClassifier::test_unresolved_explicit_no_answer PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_correct_direction_down PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_wrong_direction PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_no_change PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_clamp_positive PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_clamp_negative PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_nan_if_missing PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_nan_if_none PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_improvement_correct_raises PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_maintain_correct_high_confidence_positive PASSED
tests/unit/test_self_correction_v2.py::TestConfidenceAdjustment::test_maintain_correct_low_confidence_penalized PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_min_raw PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_max_raw PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_above_max_clamps_to_one PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_zero_raw PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_scale_range PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_maintain_correct_with_good_confidence_clamps_to_one PASSED
tests/unit/test_self_correction_v2.py::TestRescale::test_damage_with_worst_confidence_maps_to_zero PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c1_best_case_correction PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c1_maintain_correct PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c1_worst_case_damage PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c1_stubborn_wrong PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c2_correction_gain_higher_than_c1 PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c2_damage_less_harsh_than_c1 PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c2_misleading_damage_equals_c1 PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_c2_misleading_only_affects_damage PASSED
tests/unit/test_self_correction_v2.py::TestScoreItem::test_scaled_always_in_unit_interval PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_never_revise_beats_always_revise_random PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_never_revise_beats_always_revise_high_accuracy PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_selective_revision_beats_never_revise PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_damage_penalty_exceeds_correction_reward_c1 PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_damage_penalty_exceeds_correction_reward_c2 PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_c1_damage_gain_ratio_at_least_two PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_c2_misleading_damage_at_least_c1_level PASSED
tests/unit/test_self_correction_v2.py::TestAntiGaming::test_maintain_correct_is_best_non_correction_outcome PASSED
tests/unit/test_self_correction_v2.py::TestBuildAuditRow::test_round_trip_correction PASSED
tests/unit/test_self_correction_v2.py::TestBuildAuditRow::test_audit_row_damage PASSED
tests/unit/test_self_correction_v2.py::TestComputeHeadline::test_empty_returns_nan PASSED
tests/unit/test_self_correction_v2.py::TestComputeHeadline::test_single_item PASSED
tests/unit/test_self_correction_v2.py::TestComputeHeadline::test_mean_of_multiple PASSED
tests/unit/test_self_correction_v2.py::TestDiagnosticSubmetrics::test_empty_returns_empty PASSED
tests/unit/test_self_correction_v2.py::TestDiagnosticSubmetrics::test_transition_counts PASSED
tests/unit/test_self_correction_v2.py::TestDiagnosticSubmetrics::test_no_corrections_damage_gain_ratio PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_rescale_range_is_085 PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_c1_correction_best_case_is_one PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_c1_damage_worst_case_is_zero PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_maintain_correct_exceeds_raw_max PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_stubborn_wrong_scaled_value PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_effective_damage_gain_ratio_c1 PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_effective_damage_gain_ratio_c2 PASSED
tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation::test_yaml_config_comment_error_documented PASSED
============================== 65 passed in 0.18s ==============================
```

## Sprint v2 Decision Log
- Branch: fresh off main (not continuing hardening/family-c-v0.6.2)
- Model tiers:
  - T1 (cheap): gemini-2.5-flash-lite, gpt-5-mini
  - T2 (workhorse): claude-sonnet-4.6, gpt-5.2, gemini-2.5-flash
  - T3 (frontier): deepseek-r1, gpt-5.2-pro, claude-opus-4.6
- Temperature: 0 for C1 and B0, 0.3 for C2 (Kaggle constraint)
- B0: 15-item diagnostic subset initially, expand after usage check
- _RAW_MAX fix AND C2 damage ratio change: both implemented in Phase 1

## Phase Execution Plan
1. **Phase 1** (next): Grading fixes + scoring changes + test updates -> gate: all tests green -> STOP
2. **Phase 2**: Protocol updates (C1/C2 prompts, B0, confidence, edit-distance) -> gate: smoke test -> STOP
3. **Phase 3**: Validation sweep (45 items x model panel) -> gate: >=90% gradeable -> STOP
4. **Phase 4**: Item generation (15-20 CoT-resistant items) -> gate: user review -> STOP
5. **Phase 5**: Integrated sweep -> gate: analysis complete -> STOP
6. **Phase 6**: Analysis + writeup prep

## Next Action
Proceed to Phase 1: grading fixes, scoring changes, and test updates.
User confirmation required before Phase 1 begins.
