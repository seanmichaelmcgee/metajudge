"""Unit tests for v6.5 self-correction scoring functions.

Tests cover:
- Coarse transition mapping (new)
- Conditioned rates computation (new)
- v6.5 headline computation (new)
- Extended build_audit_row fields (new)
- Legacy function regression tests
"""

import math
import pytest

from metajudge.scoring.self_correction_v2 import (
    classify_transition,
    coarse_transition_bucket,
    COARSE_TRANSITION_MAP,
    compute_conditioned_rates,
    compute_family_c_headline,
    compute_family_c_headline_v65,
    score_item,
    build_audit_row,
    confidence_adjustment,
)


# ── Coarse transition mapping ────────────────────────────────────────

class TestCoarseTransitionBucket:
    """Test coarse_transition_bucket() maps correctly."""

    def test_maintain_correct_maps_to_preserve(self):
        assert coarse_transition_bucket("maintain_correct") == "preserve_correct"

    def test_neutral_revision_maps_to_preserve(self):
        assert coarse_transition_bucket("neutral_revision") == "preserve_correct"

    def test_correction_gain_maps_to_repair(self):
        assert coarse_transition_bucket("correction_gain") == "repair"

    def test_damage_maps_to_damage(self):
        assert coarse_transition_bucket("damage") == "damage"

    def test_stubborn_wrong_maps_to_nonrepair(self):
        assert coarse_transition_bucket("stubborn_wrong") == "nonrepair"

    def test_failed_revision_maps_to_nonrepair(self):
        assert coarse_transition_bucket("failed_revision") == "nonrepair"

    def test_unknown_transition_raises_error(self):
        with pytest.raises(ValueError, match="Unknown transition"):
            coarse_transition_bucket("invented_transition")

    def test_all_six_transitions_covered(self):
        """Every fine-grained transition has a mapping."""
        expected = {
            "maintain_correct", "neutral_revision", "correction_gain",
            "damage", "stubborn_wrong", "failed_revision",
        }
        assert set(COARSE_TRANSITION_MAP.keys()) == expected


# ── Conditioned rates ────────────────────────────────────────────────

def _make_audit_row(correct_1, correct_2, revised, conf_1=0.5, conf_2=0.5):
    """Helper to build a minimal audit row for testing."""
    return build_audit_row(
        item_id="test_item",
        subfamily="C1",
        stratum="test",
        normative_action="test",
        answer_1="a",
        conf_1=conf_1,
        correct_1=correct_1,
        answer_2="b" if revised else "a",
        conf_2=conf_2,
        correct_2=correct_2,
        revised=revised,
    )


class TestComputeConditionedRates:
    """Test compute_conditioned_rates()."""

    def test_all_preserve(self):
        """All T1-right, all maintained correct."""
        rows = [_make_audit_row(True, True, False) for _ in range(5)]
        rates = compute_conditioned_rates(rows)
        assert rates["n_t1_right"] == 5
        assert rates["n_t1_wrong"] == 0
        assert rates["preserve_count"] == 5
        assert rates["damage_count"] == 0
        assert rates["preserve_rate"] > 0.8  # 5/(5+1) with smoothing

    def test_all_repair(self):
        """All T1-wrong, all corrected."""
        rows = [_make_audit_row(False, True, True) for _ in range(5)]
        rates = compute_conditioned_rates(rows)
        assert rates["n_t1_wrong"] == 5
        assert rates["n_t1_right"] == 0
        assert rates["repair_count"] == 5
        assert rates["repair_rate"] > 0.8

    def test_mixed(self):
        """Mix of T1-right and T1-wrong with various outcomes."""
        rows = [
            _make_audit_row(True, True, False),   # maintain_correct → preserve
            _make_audit_row(True, True, True),     # neutral_revision → preserve
            _make_audit_row(True, False, True),    # damage
            _make_audit_row(False, True, True),    # correction_gain → repair
            _make_audit_row(False, False, False),  # stubborn_wrong → nonrepair
        ]
        rates = compute_conditioned_rates(rows)
        assert rates["n_t1_right"] == 3
        assert rates["n_t1_wrong"] == 2
        assert rates["preserve_count"] == 2
        assert rates["damage_count"] == 1
        assert rates["repair_count"] == 1
        assert rates["nonrepair_count"] == 1

    def test_empty_input(self):
        """Empty list should not crash."""
        rates = compute_conditioned_rates([])
        assert rates["n_t1_right"] == 0
        assert rates["n_t1_wrong"] == 0

    def test_smoothing_prevents_zero_division(self):
        """When all items are T1-right, repair rate should use smoothing default."""
        rows = [_make_audit_row(True, True, False) for _ in range(3)]
        rates = compute_conditioned_rates(rows, smoothing_alpha=0.5)
        # No T1-wrong items, so repair_rate should be 0.5 (smoothing default)
        assert rates["repair_rate"] == 0.5

    def test_raw_rates_are_unsmoothed(self):
        """Raw rates should be simple count/total without smoothing."""
        rows = [
            _make_audit_row(True, True, False),
            _make_audit_row(True, False, True),
        ]
        rates = compute_conditioned_rates(rows)
        assert rates["preserve_rate_raw"] == 0.5  # 1/2
        assert rates["damage_rate_raw"] == 0.5    # 1/2


# ── v6.5 headline ───────────────────────────────────────────────────

class TestComputeFamilyCHeadlineV65:
    """Test compute_family_c_headline_v65()."""

    def test_perfect_preserve_and_repair(self):
        """All preserved + all repaired → headline near 1.0."""
        rows = [
            _make_audit_row(True, True, False),   # preserve
            _make_audit_row(True, True, False),   # preserve
            _make_audit_row(False, True, True),   # repair
            _make_audit_row(False, True, True),   # repair
        ]
        result = compute_family_c_headline_v65(rows)
        assert result["headline_v65"] > 0.8

    def test_all_damage_and_nonrepair(self):
        """All damaged + all stubborn → headline near 0."""
        rows = [
            _make_audit_row(True, False, True),   # damage
            _make_audit_row(False, False, False),  # nonrepair
        ]
        result = compute_family_c_headline_v65(rows)
        assert result["headline_v65"] < 0.3

    def test_custom_weights(self):
        """Custom preserve/repair weights change the headline."""
        rows = [
            _make_audit_row(True, True, False),   # preserve
            _make_audit_row(True, True, False),   # preserve (extra to break symmetry)
            _make_audit_row(False, True, True),   # repair
        ]
        # Weight preserve at 0.8, repair at 0.2
        result = compute_family_c_headline_v65(rows, preserve_weight=0.8, repair_weight=0.2)
        # Same but inverted weights
        result2 = compute_family_c_headline_v65(rows, preserve_weight=0.2, repair_weight=0.8)
        # With asymmetric counts the smoothed rates differ, so weights matter
        assert result["headline_v65"] != result2["headline_v65"]

    def test_empty_input(self):
        """Empty list returns nan."""
        result = compute_family_c_headline_v65([])
        assert math.isnan(result["headline_v65"])

    def test_includes_legacy(self):
        """When include_legacy=True, result contains legacy_transition_mean."""
        rows = [_make_audit_row(True, True, False)]
        result = compute_family_c_headline_v65(rows, include_legacy=True)
        assert "legacy_transition_mean" in result
        assert isinstance(result["legacy_transition_mean"], float)

    def test_excludes_legacy(self):
        """When include_legacy=False, no legacy key."""
        rows = [_make_audit_row(True, True, False)]
        result = compute_family_c_headline_v65(rows, include_legacy=False)
        assert "legacy_transition_mean" not in result


# ── Extended build_audit_row ─────────────────────────────────────────

class TestBuildAuditRowV65Fields:
    """Test that build_audit_row includes new v6.5 fields."""

    def test_coarse_transition_present(self):
        row = _make_audit_row(True, True, False)
        assert "coarse_transition" in row
        assert row["coarse_transition"] == "preserve_correct"

    def test_opportunity_type_preserve(self):
        row = _make_audit_row(True, True, False)
        assert row["opportunity_type"] == "preserve"

    def test_opportunity_type_repair(self):
        row = _make_audit_row(False, True, True)
        assert row["opportunity_type"] == "repair"

    def test_coarse_damage(self):
        row = _make_audit_row(True, False, True)
        assert row["coarse_transition"] == "damage"

    def test_coarse_nonrepair(self):
        row = _make_audit_row(False, False, False)
        assert row["coarse_transition"] == "nonrepair"


# ── Legacy regression tests ──────────────────────────────────────────

class TestLegacyRegression:
    """Ensure existing functions still behave exactly as before."""

    def test_classify_transition_maintain(self):
        assert classify_transition(True, True, False) == "maintain_correct"

    def test_classify_transition_neutral_revision(self):
        assert classify_transition(True, True, True) == "neutral_revision"

    def test_classify_transition_correction_gain(self):
        assert classify_transition(False, True, True) == "correction_gain"

    def test_classify_transition_damage(self):
        assert classify_transition(True, False, True) == "damage"

    def test_classify_transition_stubborn_wrong(self):
        assert classify_transition(False, False, False) == "stubborn_wrong"

    def test_classify_transition_failed_revision(self):
        assert classify_transition(False, False, True) == "failed_revision"

    def test_score_item_returns_expected_keys(self):
        result = score_item(True, True, False, 0.8, 0.8)
        assert set(result.keys()) == {"transition", "base_score", "conf_adj", "raw_score", "scaled_score"}

    def test_compute_family_c_headline_empty(self):
        assert math.isnan(compute_family_c_headline([]))

    def test_compute_family_c_headline_single(self):
        scores = [score_item(True, True, False, 0.8, 0.8)]
        result = compute_family_c_headline(scores)
        assert 0.0 <= result <= 1.0

    def test_build_audit_row_has_original_fields(self):
        row = _make_audit_row(True, True, False)
        required = {"item_id", "subfamily", "stratum", "normative_action",
                     "answer_1", "conf_1", "correct_1", "answer_2", "conf_2",
                     "correct_2", "revised", "challenge_type", "transition",
                     "base_score", "conf_adj", "raw_score", "scaled_score"}
        assert required.issubset(set(row.keys()))
