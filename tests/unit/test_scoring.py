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
        score = calibration_aware_score(True, 1.0)
        assert score == 1.0

    def test_calibration_aware_score_wrong_high_conf(self):
        score = calibration_aware_score(False, 1.0)
        assert score == 0.0

    def test_calibration_aware_score_wrong_low_conf(self):
        score = calibration_aware_score(False, 0.0)
        assert score == 0.5

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
