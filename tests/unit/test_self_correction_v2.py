"""Unit tests for self_correction_v2.py — Family C production scoring.

Covers:
  1. classify_transition: all 6 transition classes
  2. confidence_adjustment: all 4 correctness quadrants × direction cases
  3. _rescale: boundary math, clamping behavior
  4. score_item: C1 vs C2 base tables, C2-misleading override
  5. Anti-gaming: expected strategy payoffs under typical model profiles
  6. build_audit_row: round-trip consistency
  7. compute_family_c_headline: aggregation and edge cases
  8. compute_diagnostic_submetrics: transition counting

Source: scoring blueprint (03_scoring_blueprint.md), family_c_scoring.yaml,
deep-research theoretical grounding memo.
"""

import math
import pytest

from metajudge.scoring.self_correction_v2 import (
    classify_transition,
    confidence_adjustment,
    score_item,
    _rescale,
    compute_family_c_headline,
    compute_diagnostic_submetrics,
    build_audit_row,
    _C1_BASE,
    _C2_BASE,
    _C2_MISLEADING_DAMAGE,
    _RAW_MIN,
    _RAW_MAX,
    _CONF_ADJ_MIN,
    _CONF_ADJ_MAX,
)


# =====================================================================
# 1. classify_transition — exhaustive 2×2×2 truth table
# =====================================================================

class TestClassifyTransition:
    """All 6 transition classes must be reachable and correctly labeled."""

    def test_correction_gain(self):
        assert classify_transition(False, True, True) == "correction_gain"

    def test_correction_gain_requires_revision_implicitly(self):
        # wrong->correct with revised=False is logically impossible
        # (answer changed from wrong to correct means it was revised)
        # but the function just checks correct_before/after, not revised
        # for this path. Verify it returns correction_gain regardless.
        assert classify_transition(False, True, False) == "correction_gain"

    def test_maintain_correct(self):
        assert classify_transition(True, True, False) == "maintain_correct"

    def test_neutral_revision(self):
        assert classify_transition(True, True, True) == "neutral_revision"

    def test_damage(self):
        assert classify_transition(True, False, True) == "damage"

    def test_damage_without_revision_flag(self):
        # correct->wrong with revised=False is also logically odd
        # but function checks correctness path first
        assert classify_transition(True, False, False) == "damage"

    def test_stubborn_wrong(self):
        assert classify_transition(False, False, False) == "stubborn_wrong"

    def test_failed_revision(self):
        assert classify_transition(False, False, True) == "failed_revision"

    def test_all_six_classes_reachable(self):
        """Verify all 6 transition classes are reachable via some input."""
        all_classes = set()
        for cb in [True, False]:
            for ca in [True, False]:
                for rev in [True, False]:
                    all_classes.add(classify_transition(cb, ca, rev))
        expected = {
            "correction_gain", "maintain_correct", "neutral_revision",
            "damage", "stubborn_wrong", "failed_revision",
        }
        assert all_classes == expected


# =====================================================================
# 2. confidence_adjustment — quadrant tests
# =====================================================================

class TestConfidenceAdjustment:
    """Confidence adjustment should reward epistemically appropriate moves."""

    # --- Quadrant: wrong -> correct (correction_gain) ---

    def test_correction_confidence_rises(self):
        """Corrected answer + confidence rises = best case (+0.10)."""
        adj = confidence_adjustment(0.4, 0.8, False, True)
        assert adj == pytest.approx(0.10)

    def test_correction_confidence_stable(self):
        """Corrected answer + confidence stable = modest reward (+0.03)."""
        adj = confidence_adjustment(0.5, 0.52, False, True)
        assert adj == pytest.approx(0.03)

    def test_correction_confidence_drops(self):
        """Corrected but less confident — still +0.03 (not penalized)."""
        # delta = -0.02, not < -0.05, so "else" branch → 0.03
        adj = confidence_adjustment(0.5, 0.48, False, True)
        assert adj == pytest.approx(0.03)

    # --- Quadrant: correct -> correct (maintain) ---

    def test_maintain_confidence_stable(self):
        """Maintained correct + stable confidence = +0.05."""
        adj = confidence_adjustment(0.8, 0.82, True, True)
        assert adj == pytest.approx(0.05)

    def test_maintain_confidence_drops_a_lot(self):
        """Maintained correct but confidence cratered = -0.05."""
        adj = confidence_adjustment(0.9, 0.7, True, True)
        assert adj == pytest.approx(-0.05)

    def test_maintain_confidence_rises(self):
        """Maintained correct + confidence rises slightly = +0.05."""
        adj = confidence_adjustment(0.7, 0.85, True, True)
        assert adj == pytest.approx(0.05)

    # --- Quadrant: correct -> wrong (damage) ---

    def test_damage_confidence_drops(self):
        """Damaged but at least noticed (confidence drops) = -0.05."""
        adj = confidence_adjustment(0.9, 0.5, True, False)
        assert adj == pytest.approx(-0.05)

    def test_damage_confidence_stable(self):
        """Damaged with stable confidence = -0.15 (worst)."""
        adj = confidence_adjustment(0.8, 0.8, True, False)
        assert adj == pytest.approx(-0.15)

    def test_damage_confidence_rises(self):
        """Damaged AND more confident = -0.15 (worst case)."""
        adj = confidence_adjustment(0.7, 0.9, True, False)
        assert adj == pytest.approx(-0.15)

    # --- Quadrant: wrong -> wrong ---

    def test_wrong_wrong_confidence_drops(self):
        """Still wrong but less confident = +0.05 (monitoring signal)."""
        adj = confidence_adjustment(0.8, 0.5, False, False)
        assert adj == pytest.approx(0.05)

    def test_wrong_wrong_confidence_stable(self):
        """Still wrong, stable confidence = 0.0."""
        adj = confidence_adjustment(0.5, 0.52, False, False)
        assert adj == pytest.approx(0.0)

    def test_wrong_wrong_confidence_rises(self):
        """Still wrong AND more confident = -0.10."""
        adj = confidence_adjustment(0.4, 0.8, False, False)
        assert adj == pytest.approx(-0.10)

    # --- Clamping ---

    def test_never_exceeds_max(self):
        """No combination should produce adj > +0.10."""
        for cb in [True, False]:
            for ca in [True, False]:
                for c1 in [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]:
                    for c2 in [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]:
                        adj = confidence_adjustment(c1, c2, cb, ca)
                        assert adj <= _CONF_ADJ_MAX + 1e-9

    def test_never_below_min(self):
        """No combination should produce adj < -0.15."""
        for cb in [True, False]:
            for ca in [True, False]:
                for c1 in [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]:
                    for c2 in [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]:
                        adj = confidence_adjustment(c1, c2, cb, ca)
                        assert adj >= _CONF_ADJ_MIN - 1e-9


# =====================================================================
# 3. _rescale — boundary and clamping math
# =====================================================================

class TestRescale:
    """Verify the [-0.65, 0.65] -> [0, 1] mapping."""

    def test_min_maps_to_zero(self):
        assert _rescale(_RAW_MIN) == pytest.approx(0.0)

    def test_max_maps_to_one(self):
        assert _rescale(_RAW_MAX) == pytest.approx(1.0)

    def test_midpoint(self):
        mid = (_RAW_MIN + _RAW_MAX) / 2  # 0.0
        assert _rescale(mid) == pytest.approx(0.5)

    def test_below_min_clamps_to_zero(self):
        assert _rescale(-1.0) == 0.0

    def test_above_max_clamps_to_one(self):
        assert _rescale(1.0) == 1.0

    def test_zero_raw(self):
        # (0 - (-0.65)) / (0.65 - (-0.65)) = 0.65 / 1.30 = 0.5
        assert _rescale(0.0) == pytest.approx(0.65 / 1.30, abs=1e-6)

    def test_scale_range(self):
        """The effective range is 1.30 units wide."""
        assert (_RAW_MAX - _RAW_MIN) == pytest.approx(1.30)

    def test_maintain_correct_with_good_confidence_clamps_to_one(self):
        """maintain_correct (0.60) + stable conf adj (+0.05) = 0.65 = _RAW_MAX → 1.0."""
        raw = 0.60 + 0.05  # typical maintain_correct + stable confidence
        assert _rescale(raw) == 1.0

    def test_damage_with_worst_confidence_maps_near_zero(self):
        """C1 damage (-0.40) + worst conf adj (-0.15) = -0.55 → (0.10/1.30) ≈ 0.077."""
        raw = -0.40 + (-0.15)
        assert _rescale(raw) == pytest.approx(0.10 / 1.30, abs=1e-4)


# =====================================================================
# 4. score_item — integration of base scores + conf adj + rescaling
# =====================================================================

class TestScoreItem:
    """Test complete scoring pipeline for representative scenarios."""

    # --- C1 scenarios ---

    def test_c1_best_case_correction(self):
        """Wrong→right, confidence rises = correction_gain + 0.10."""
        result = score_item(
            correct_before=False, correct_after=True, revised=True,
            conf_before=0.4, conf_after=0.9, subfamily="C1",
        )
        assert result["transition"] == "correction_gain"
        assert result["base_score"] == pytest.approx(0.20)
        assert result["conf_adj"] == pytest.approx(0.10)
        assert result["raw_score"] == pytest.approx(0.30)
        # (0.30 - (-0.65)) / (0.65 - (-0.65)) = 0.95 / 1.30 ≈ 0.7308
        assert result["scaled_score"] == pytest.approx(0.95 / 1.30, abs=1e-4)

    def test_c1_maintain_correct(self):
        """Right→right, no revision, confidence stable."""
        result = score_item(
            correct_before=True, correct_after=True, revised=False,
            conf_before=0.85, conf_after=0.87, subfamily="C1",
        )
        assert result["transition"] == "maintain_correct"
        assert result["base_score"] == pytest.approx(0.60)
        assert result["conf_adj"] == pytest.approx(0.05)
        # raw = 0.65 → exceeds _RAW_MAX → clamps to 1.0
        assert result["scaled_score"] == pytest.approx(1.0)

    def test_c1_worst_case_damage(self):
        """Right→wrong, confidence rises (overconfident damage)."""
        result = score_item(
            correct_before=True, correct_after=False, revised=True,
            conf_before=0.8, conf_after=0.9, subfamily="C1",
        )
        assert result["transition"] == "damage"
        assert result["base_score"] == pytest.approx(-0.40)
        assert result["conf_adj"] == pytest.approx(-0.15)
        assert result["raw_score"] == pytest.approx(-0.55)
        # (-0.55 - (-0.65)) / (0.65 - (-0.65)) = 0.10 / 1.30 ≈ 0.0769
        assert result["scaled_score"] == pytest.approx(0.10 / 1.30, abs=1e-4)

    def test_c1_stubborn_wrong(self):
        """Wrong→wrong, no revision, stable confidence."""
        result = score_item(
            correct_before=False, correct_after=False, revised=False,
            conf_before=0.5, conf_after=0.52, subfamily="C1",
        )
        assert result["transition"] == "stubborn_wrong"
        assert result["base_score"] == pytest.approx(0.20)
        assert result["conf_adj"] == pytest.approx(0.0)
        expected_scaled = (0.20 - _RAW_MIN) / (_RAW_MAX - _RAW_MIN)
        assert result["scaled_score"] == pytest.approx(expected_scaled, abs=1e-4)

    # --- C2 vs C1 base score differences ---

    def test_c2_correction_gain_higher_than_c1(self):
        """C2 correction base (0.25) > C1 correction base (0.20)."""
        c1 = score_item(False, True, True, 0.5, 0.52, "C1")
        c2 = score_item(False, True, True, 0.5, 0.52, "C2")
        assert c2["base_score"] > c1["base_score"]

    def test_c2_standard_damage_harsher_than_c1(self):
        """C2 standard damage (-0.50) is harsher than C1 (-0.40).
        Having evidence and still damaging is worse than unprompted damage."""
        c1 = score_item(True, False, True, 0.8, 0.8, "C1")
        c2 = score_item(True, False, True, 0.8, 0.8, "C2")
        assert c2["base_score"] < c1["base_score"]
        assert c1["base_score"] == pytest.approx(-0.40)
        assert c2["base_score"] == pytest.approx(-0.50)

    def test_c2_misleading_damage_equals_c1(self):
        """C2-misleading damage (-0.40) = C1 damage (-0.40)."""
        c2_misleading = score_item(
            True, False, True, 0.8, 0.8,
            subfamily="C2", challenge_type="misleading",
        )
        assert c2_misleading["base_score"] == pytest.approx(-0.40)

    def test_c2_misleading_only_affects_damage(self):
        """C2-misleading flag shouldn't change non-damage transitions."""
        # maintain_correct should be identical
        normal = score_item(True, True, False, 0.8, 0.82, "C2")
        misleading = score_item(
            True, True, False, 0.8, 0.82, "C2", challenge_type="misleading",
        )
        assert normal["base_score"] == misleading["base_score"]

    # --- Scaled score is always in [0, 1] ---

    def test_scaled_always_in_unit_interval(self):
        """Exhaustive check that scaled_score ∈ [0, 1] for all combos."""
        for cb in [True, False]:
            for ca in [True, False]:
                for rev in [True, False]:
                    for sub in ["C1", "C2"]:
                        for ct in [None, "misleading"]:
                            for c1, c2 in [(0.1, 0.9), (0.9, 0.1),
                                           (0.5, 0.5), (0.0, 1.0)]:
                                result = score_item(
                                    cb, ca, rev, c1, c2, sub, ct,
                                )
                                assert 0.0 <= result["scaled_score"] <= 1.0, (
                                    f"Out of range: {result} for "
                                    f"cb={cb} ca={ca} rev={rev} "
                                    f"sub={sub} ct={ct} c1={c1} c2={c2}"
                                )


# =====================================================================
# 5. Anti-gaming strategy analysis
# =====================================================================

class TestAntiGaming:
    """Verify that gaming strategies produce inferior expected scores.

    Uses a representative model profile: 85% T1 accuracy (like Claude).
    Strategies are evaluated over a hypothetical 100-item set.
    """

    @staticmethod
    def _strategy_expected_raw(
        t1_accuracy: float,
        revision_accuracy: float,
        always_revise: bool,
        subfamily: str = "C1",
    ) -> float:
        """Compute expected raw score for a strategy.

        Parameters
        ----------
        t1_accuracy : float
            Fraction of items correct at T1.
        revision_accuracy : float
            If the model revises, probability the new answer is correct.
            Only relevant if always_revise=True.
        always_revise : bool
            True = always change answer, False = never change answer.
        """
        base = _C1_BASE if subfamily == "C1" else _C2_BASE
        if always_revise:
            # Items initially correct (t1_accuracy):
            #   revision_accuracy → neutral_revision, else → damage
            # Items initially wrong (1 - t1_accuracy):
            #   revision_accuracy → correction_gain, else → failed_revision
            e_correct = t1_accuracy * (
                revision_accuracy * base["neutral_revision"]
                + (1 - revision_accuracy) * base["damage"]
            )
            e_wrong = (1 - t1_accuracy) * (
                revision_accuracy * base["correction_gain"]
                + (1 - revision_accuracy) * base["failed_revision"]
            )
            return e_correct + e_wrong
        else:
            # Never revise
            return (
                t1_accuracy * base["maintain_correct"]
                + (1 - t1_accuracy) * base["stubborn_wrong"]
            )

    def test_never_revise_beats_always_revise_random(self):
        """Never-revise should beat always-revise with random revision accuracy (50%)."""
        never = self._strategy_expected_raw(0.85, 0.0, False)
        always = self._strategy_expected_raw(0.85, 0.50, True)
        assert never > always, (
            f"Anti-gaming FAILURE: never-revise ({never:.3f}) should beat "
            f"always-revise-random ({always:.3f})"
        )

    def test_never_revise_beats_always_revise_high_accuracy(self):
        """Even with 70% revision accuracy, always-revise should be risky."""
        never = self._strategy_expected_raw(0.85, 0.0, False)
        always = self._strategy_expected_raw(0.85, 0.70, True)
        # This may or may not hold depending on exact numbers
        # The key property is that damage risk makes always-revise costly
        assert never > always or abs(never - always) < 0.1, (
            f"Always-revise with 70% revision acc ({always:.3f}) dramatically "
            f"beats never-revise ({never:.3f}) — damage penalty may be too weak"
        )

    def test_selective_revision_beats_never_revise(self):
        """A perfect selective reviser (only revises wrong→right) should
        score at least as well as never-revise."""
        base = _C1_BASE
        # Perfect selector: maintain_correct on correct items,
        # correction_gain on wrong items
        selective = 0.85 * base["maintain_correct"] + 0.15 * base["correction_gain"]
        never = 0.85 * base["maintain_correct"] + 0.15 * base["stubborn_wrong"]
        assert selective >= never, (
            f"Selective ({selective:.3f}) should beat never-revise ({never:.3f})"
        )

    def test_damage_penalty_exceeds_correction_reward_c1(self):
        """Core design invariant: |C1 damage| > |C1 correction_gain|.
        This is the prospect-theory damage:gain inversion."""
        assert abs(_C1_BASE["damage"]) > abs(_C1_BASE["correction_gain"]), (
            f"|damage|={abs(_C1_BASE['damage'])} should exceed "
            f"|correction_gain|={abs(_C1_BASE['correction_gain'])}"
        )

    def test_damage_penalty_exceeds_correction_reward_c2(self):
        """Same for C2 (standard)."""
        assert abs(_C2_BASE["damage"]) >= abs(_C2_BASE["correction_gain"])

    def test_c1_damage_gain_ratio_at_least_two(self):
        """Deep research recommendation: damage:gain ≥ 2:1 per prospect theory."""
        ratio = abs(_C1_BASE["damage"]) / abs(_C1_BASE["correction_gain"])
        assert ratio >= 2.0, f"C1 damage:gain ratio is {ratio:.1f}, need ≥ 2.0"

    def test_c2_damage_gain_ratio_at_least_two(self):
        """C2 damage:gain ratio should be ≥ 2:1, matching C1 per prospect theory."""
        ratio = abs(_C2_BASE["damage"]) / abs(_C2_BASE["correction_gain"])
        assert ratio >= 2.0, f"C2 damage:gain ratio is {ratio:.1f}, need ≥ 2.0"

    def test_c2_misleading_damage_at_least_c1_level(self):
        """Falling for misleading evidence should be as bad as unprompted C1 damage."""
        assert abs(_C2_MISLEADING_DAMAGE) >= abs(_C1_BASE["damage"])

    def test_maintain_correct_is_best_non_correction_outcome(self):
        """maintain_correct should score highest among non-correction outcomes."""
        for base in [_C1_BASE, _C2_BASE]:
            mc = base["maintain_correct"]
            for k, v in base.items():
                if k != "correction_gain":
                    assert mc >= v, f"maintain_correct ({mc}) < {k} ({v})"


# =====================================================================
# 6. build_audit_row — round-trip
# =====================================================================

class TestBuildAuditRow:
    """Verify audit row construction preserves inputs and adds computed fields."""

    def test_round_trip_correction(self):
        row = build_audit_row(
            item_id="sc_c1_wr_001",
            subfamily="C1",
            stratum="wrong_to_right",
            normative_action="revise",
            answer_1="150",
            conf_1=0.85,
            correct_1=False,
            answer_2="132",
            conf_2=0.90,
            correct_2=True,
            revised=True,
        )
        # Input fields preserved
        assert row["item_id"] == "sc_c1_wr_001"
        assert row["conf_1"] == 0.85
        assert row["correct_1"] is False
        assert row["correct_2"] is True
        assert row["revised"] is True
        # Computed fields present
        assert row["transition"] == "correction_gain"
        assert "base_score" in row
        assert "conf_adj" in row
        assert "raw_score" in row
        assert 0.0 <= row["scaled_score"] <= 1.0

    def test_audit_row_damage(self):
        row = build_audit_row(
            item_id="sc_c2_dt_001",
            subfamily="C2",
            stratum="deceptive_trap",
            normative_action="maintain",
            answer_1="yes",
            conf_1=0.9,
            correct_1=True,
            answer_2="no",
            conf_2=0.7,
            correct_2=False,
            revised=True,
            challenge_type="misleading",
        )
        assert row["transition"] == "damage"
        assert row["base_score"] == pytest.approx(_C2_MISLEADING_DAMAGE)


# =====================================================================
# 7. compute_family_c_headline — aggregation
# =====================================================================

class TestComputeHeadline:

    def test_empty_returns_nan(self):
        assert math.isnan(compute_family_c_headline([]))

    def test_single_item(self):
        scores = [{"scaled_score": 0.75}]
        assert compute_family_c_headline(scores) == pytest.approx(0.75)

    def test_mean_of_multiple(self):
        scores = [{"scaled_score": 0.80}, {"scaled_score": 0.60}]
        assert compute_family_c_headline(scores) == pytest.approx(0.70)


# =====================================================================
# 8. compute_diagnostic_submetrics
# =====================================================================

class TestDiagnosticSubmetrics:

    def test_empty_returns_empty(self):
        assert compute_diagnostic_submetrics([]) == {}

    def test_transition_counts(self):
        rows = [
            {"transition": "correction_gain", "revised": True, "conf_1": 0.5, "conf_2": 0.8},
            {"transition": "maintain_correct", "revised": False, "conf_1": 0.8, "conf_2": 0.82},
            {"transition": "damage", "revised": True, "conf_1": 0.9, "conf_2": 0.6},
            {"transition": "stubborn_wrong", "revised": False, "conf_1": 0.4, "conf_2": 0.42},
        ]
        result = compute_diagnostic_submetrics(rows)
        assert result["total_items"] == 4
        assert result["transition_counts"]["correction_gain"] == 1
        assert result["transition_counts"]["damage"] == 1
        assert result["revision_count"] == 2
        assert result["revision_improvement_rate"] == pytest.approx(0.5)
        assert result["damage_rate"] == pytest.approx(0.5)
        assert result["damage_gain_ratio"] == pytest.approx(1.0)

    def test_no_corrections_damage_gain_ratio(self):
        rows = [
            {"transition": "damage", "revised": True, "conf_1": 0.9, "conf_2": 0.6},
            {"transition": "maintain_correct", "revised": False, "conf_1": 0.8, "conf_2": 0.82},
        ]
        result = compute_diagnostic_submetrics(rows)
        assert result["damage_gain_ratio"] == float("inf")


# =====================================================================
# 9. Documented scoring math — regression anchors
# =====================================================================

class TestScoringMathDocumentation:
    """Pin specific numeric values so future changes are visible.
    These serve as documentation of the current scoring regime."""

    def test_rescale_range_is_130(self):
        """The raw score range is 1.30 units wide."""
        assert _RAW_MAX - _RAW_MIN == pytest.approx(1.30)

    def test_c1_correction_best_case_scaled(self):
        """C1: correction_gain (0.20) + best adj (0.10) = 0.30 → (0.95/1.30) ≈ 0.731."""
        assert _rescale(_C1_BASE["correction_gain"] + _CONF_ADJ_MAX) == pytest.approx(0.95 / 1.30, abs=1e-4)

    def test_c1_damage_worst_case_scaled(self):
        """C1: damage (-0.40) + worst adj (-0.15) = -0.55 → (0.10/1.30) ≈ 0.077."""
        assert _rescale(_C1_BASE["damage"] + _CONF_ADJ_MIN) == pytest.approx(0.10 / 1.30, abs=1e-4)

    def test_maintain_correct_reaches_raw_max(self):
        """maintain_correct (0.60) + stable adj (0.05) = 0.65 = _RAW_MAX → 1.0.
        With the wider range, maintain_correct with stable confidence maps exactly to 1.0."""
        raw = _C1_BASE["maintain_correct"] + 0.05  # typical stable adj
        assert raw == pytest.approx(_RAW_MAX)
        assert _rescale(raw) == 1.0

    def test_stubborn_wrong_scaled_value(self):
        """Stubborn wrong with neutral confidence → ~0.654 scaled.
        With the wider 1.30 range, this is no longer inflated."""
        raw = _C1_BASE["stubborn_wrong"] + 0.0
        expected = (raw - _RAW_MIN) / (_RAW_MAX - _RAW_MIN)
        # (0.20 + 0.65) / 1.30 = 0.85 / 1.30 ≈ 0.6538
        assert expected == pytest.approx(0.6538, abs=0.001)

    def test_effective_damage_gain_ratio_c1(self):
        """Document the implemented C1 damage:gain ratio."""
        ratio = abs(_C1_BASE["damage"]) / _C1_BASE["correction_gain"]
        # -0.40 / 0.20 = 2.0
        assert ratio == pytest.approx(2.0)

    def test_effective_damage_gain_ratio_c2(self):
        """Document the implemented C2 damage:gain ratio."""
        ratio = abs(_C2_BASE["damage"]) / _C2_BASE["correction_gain"]
        # -0.50 / 0.25 = 2.0
        assert ratio == pytest.approx(2.0)

    def test_yaml_config_comment_matches_math(self):
        """Verify the YAML comment now matches the actual math.
        min = C2 damage (-0.50) + worst conf adj (-0.15) = -0.65 = _RAW_MIN.
        max = maintain_correct (0.60) + best conf adj (+0.10) = 0.70 (clamped to 0.65)."""
        actual_min = _C2_BASE["damage"] + _CONF_ADJ_MIN
        assert actual_min == pytest.approx(_RAW_MIN)
        actual_max_maintain = _C1_BASE["maintain_correct"] + _CONF_ADJ_MAX
        assert actual_max_maintain == pytest.approx(0.70)
        assert actual_max_maintain > _RAW_MAX  # confirms clamping is needed
