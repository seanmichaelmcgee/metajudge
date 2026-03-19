"""Unit tests for scoring modules.

Source: Framework §7.2
"""
import math

import pytest

from metajudge.scoring.calibration_metrics import (
    brier_score,
    brier_component_single,
    expected_calibration_error,
    overconfidence_rate,
    overconfidence_penalty_single,
    calibration_aware_score,
)
from metajudge.scoring.abstention_metrics import (
    decision_utility_single,
    abstention_quality_binary,
    abstention_precision,
)
from metajudge.scoring.self_correction_metrics import (
    revision_improvement_rate,
    unnecessary_revision_rate,
    confidence_directionality,
    correction_efficiency_score,
)
from metajudge.scoring.composite_score import (
    compute_composite_score,
)
from metajudge.scoring.calibration_metrics import coverage_conditioned_accuracy


class TestCalibrationMetrics:
    def test_brier_perfect(self):
        # Perfect calibration: confident and correct
        score = brier_score([1.0, 1.0], [True, True])
        assert score == 0.0

    def test_brier_worst(self):
        # Worst case: fully confident and wrong
        score = brier_score([1.0, 1.0], [False, False])
        assert score == 1.0

    def test_brier_component_correct_confident(self):
        assert brier_component_single(0.9, True) == pytest.approx(0.01)

    def test_brier_component_wrong_confident(self):
        assert brier_component_single(0.9, False) == pytest.approx(0.81)

    def test_overconfidence_rate(self):
        # All wrong answers above threshold
        rate = overconfidence_rate([0.9, 0.85, 0.3], [False, False, False], threshold=0.8)
        assert rate == pytest.approx(2 / 3)

    def test_overconfidence_penalty_correct(self):
        assert overconfidence_penalty_single(0.99, True) == 0.0

    def test_overconfidence_penalty_wrong(self):
        assert overconfidence_penalty_single(0.8, False) == 0.8

    def test_calibration_aware_score_correct_high_conf(self):
        # 1 - (1.0 - 1.0)^2 = 1.0
        score = calibration_aware_score(True, 1.0)
        assert score == 1.0

    def test_calibration_aware_score_wrong_high_conf(self):
        # 1 - (1.0 - 0.0)^2 = 0.0
        score = calibration_aware_score(False, 1.0)
        assert score == 0.0

    def test_calibration_aware_score_wrong_low_conf(self):
        # 1 - (0.0 - 0.0)^2 = 1.0 (correctly admits ignorance)
        score = calibration_aware_score(False, 0.0)
        assert score == 1.0

    def test_calibration_aware_score_correct_low_conf(self):
        # 1 - (0.0 - 1.0)^2 = 0.0 (correct but no confidence = worst)
        score = calibration_aware_score(True, 0.0)
        assert score == 0.0

    def test_calibration_aware_score_correct_moderate_conf(self):
        # 1 - (0.7 - 1.0)^2 = 0.91
        score = calibration_aware_score(True, 0.7)
        assert score == pytest.approx(0.91)

    def test_calibration_aware_score_wrong_moderate_conf(self):
        # 1 - (0.5 - 0.0)^2 = 0.75
        score = calibration_aware_score(False, 0.5)
        assert score == pytest.approx(0.75)

    def test_ece_perfect(self):
        ece = expected_calibration_error([1.0, 0.0], [True, False])
        assert ece == pytest.approx(0.0, abs=0.15)


class TestAbstentionMetrics:
    def test_utility_correct_answer(self):
        u = decision_utility_single("answer", True, True)
        assert u == 1.0

    def test_utility_abstain_on_answerable(self):
        u = decision_utility_single("abstain", False, True)
        assert u == -0.3

    def test_utility_abstain_on_unanswerable(self):
        u = decision_utility_single("abstain", False, False)
        assert u == 0.6

    def test_binary_quality_correct_answer(self):
        assert abstention_quality_binary(False, True) == 1.0

    def test_binary_quality_correct_abstain(self):
        assert abstention_quality_binary(True, False) == 1.0

    def test_binary_quality_wrong_abstain(self):
        assert abstention_quality_binary(True, True) == 0.0

    def test_abstention_precision(self):
        prec = abstention_precision(
            ["answer", "abstain", "abstain", "answer"],
            [True, False, True, True],
        )
        assert prec == 0.5  # 1 of 2 abstentions was on non-answerable


class TestSelfCorrectionMetrics:
    def test_revision_improvement_rate(self):
        results = [
            (False, True, True),   # Fixed
            (False, False, True),  # Revised but still wrong
            (True, True, False),   # Not revised
        ]
        rate = revision_improvement_rate(results)
        assert rate == 0.5  # 1 of 2 revisions improved

    def test_unnecessary_revision_rate(self):
        results = [
            (True, False, True),  # Broke correct answer
            (True, True, True),   # Revised but still correct
            (False, True, True),  # Fixed an error
        ]
        rate = unnecessary_revision_rate(results)
        assert rate == 0.5  # 1 of 2 correct-then-revised was damaged

    def test_confidence_directionality_appropriate(self):
        d = confidence_directionality(0.5, 0.9, False, True)
        assert d == "appropriate_increase"

    def test_confidence_directionality_inappropriate(self):
        d = confidence_directionality(0.5, 0.9, True, False)
        assert d == "inappropriate_increase"

    def test_correction_efficiency_fixed(self):
        score = correction_efficiency_score(False, True, True, 0.5, 0.9)
        assert score >= 0.8  # Should be high

    def test_correction_efficiency_broke(self):
        score = correction_efficiency_score(True, False, True, 0.9, 0.5)
        assert score <= 0.2  # Should be low


class TestCompositeScore:
    def test_perfect_scores(self):
        subscores = {
            "calibration": 1.0,
            "abstention_verification": 1.0,
            "intrinsic_self_correction": 1.0,
            "evidence_assisted_correction": 1.0,
            "grounding_sensitivity": 1.0,
            "control_policy_adaptation": 1.0,
        }
        composite = compute_composite_score(subscores)
        assert composite == pytest.approx(1.0)

    def test_zero_scores(self):
        subscores = {
            "calibration": 0.0,
            "abstention_verification": 0.0,
            "intrinsic_self_correction": 0.0,
            "evidence_assisted_correction": 0.0,
            "grounding_sensitivity": 0.0,
            "control_policy_adaptation": 0.0,
        }
        composite = compute_composite_score(subscores)
        assert composite == pytest.approx(0.0)

    def test_partial_scores_calibration_only(self):
        subscores = {
            "calibration": 0.8,
        }
        composite = compute_composite_score(subscores)
        # Should normalize by actual weight used (only calibration weight)
        assert composite == pytest.approx(0.8)

    def test_partial_scores_monitoring_axis(self):
        subscores = {
            "calibration": 0.8,
            "abstention_verification": 0.6,
        }
        composite = compute_composite_score(subscores)
        # Should normalize by actual weight used
        expected = (0.30 * 0.8 + 0.20 * 0.6) / (0.30 + 0.20)
        assert composite == pytest.approx(expected)


class TestAdjudication:
    """Tests for deterministic answer adjudication."""

    def setup_method(self):
        self.answer_key = {
            "cal_001": {
                "canonical_answer": "au",
                "accepted_aliases": ["au", "gold"],
                "answer_type": "entity",
                "grader_rule": "alias_match",
            },
            "cal_002": {
                "canonical_answer": "42",
                "accepted_aliases": ["42", "42.0"],
                "answer_type": "integer",
                "grader_rule": "numeric_equivalence",
            },
            "cal_003": {
                "canonical_answer": "no",
                "accepted_aliases": ["no"],
                "answer_type": "yes_no",
                "grader_rule": "yes_no_normalization",
            },
            "cal_004": {
                "canonical_answer": "0.05",
                "accepted_aliases": ["0.05", "$0.05", "5 cents"],
                "answer_type": "decimal",
                "grader_rule": "alias_match",
            },
        }

    def test_canonical_match(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_001", "Au", self.answer_key) is True

    def test_alias_match(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_001", "gold", self.answer_key) is True

    def test_wrong_answer(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_001", "silver", self.answer_key) is False

    def test_numeric_equivalence(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_002", "42.0", self.answer_key) is True

    def test_numeric_wrong(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_002", "43", self.answer_key) is False

    def test_yes_no_normalization(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_003", "No", self.answer_key) is True
        assert adjudicate_answer("cal_003", "n", self.answer_key) is True
        assert adjudicate_answer("cal_003", "false", self.answer_key) is True

    def test_yes_no_wrong(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_003", "yes", self.answer_key) is False

    def test_alias_with_symbol(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("cal_004", "$0.05", self.answer_key) is True
        assert adjudicate_answer("cal_004", "5 cents", self.answer_key) is True

    def test_fallback_without_key(self):
        from metajudge.scoring.adjudication import adjudicate_with_fallback
        # No answer key — falls back to exact match
        assert adjudicate_with_fallback("unknown_id", "Paris", "Paris") is True
        assert adjudicate_with_fallback("unknown_id", "paris", "Paris") is True
        assert adjudicate_with_fallback("unknown_id", "London", "Paris") is False

    def test_fallback_with_key(self):
        from metajudge.scoring.adjudication import adjudicate_with_fallback
        # Has answer key — uses adjudication
        assert adjudicate_with_fallback("cal_001", "gold", "au", self.answer_key) is True

    def test_missing_id_in_key(self):
        from metajudge.scoring.adjudication import adjudicate_answer
        assert adjudicate_answer("nonexistent", "anything", self.answer_key) is False


class TestCoverageConditionedAccuracy:
    def test_normal_case(self):
        # 0.9 and 0.8 exceed threshold; 0.3 does not. Above-threshold: [True, False] → 0.5
        assert coverage_conditioned_accuracy([0.9, 0.8, 0.3], [True, False, True], 0.5) == 0.5

    def test_all_below_threshold(self):
        assert math.isnan(coverage_conditioned_accuracy([0.1, 0.2], [True, True], 0.5))

    def test_threshold_boundary(self):
        assert coverage_conditioned_accuracy([0.5, 0.5], [True, False], 0.5) == 0.5

    def test_empty_input(self):
        assert math.isnan(coverage_conditioned_accuracy([], [], 0.5))

    def test_all_correct_above(self):
        assert coverage_conditioned_accuracy([0.9, 0.8], [True, True], 0.5) == 1.0
