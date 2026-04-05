"""Unit tests for v6.5 Family B (selective abstention) scoring.

Covers: config loading, matrix values, new scoring function,
answer-rate penalty, Unicode normalization, backward compatibility.
"""

import math
import pytest


# ── Config and matrix tests ──────────────────────────────────────────

class TestFamilyBConfig:

    def test_config_loads(self):
        from metajudge.scoring.abstention_metrics import _get_family_b_config
        cfg = _get_family_b_config()
        assert cfg["version"] == "0.6.5"
        assert "utility_matrix" in cfg

    def test_matrix_has_all_cells(self):
        from metajudge.scoring.abstention_metrics import UTILITY_MATRIX
        # 5 rows × 4 cols = 20 cells
        assert len(UTILITY_MATRIX) == 20

    def test_matrix_diagonal_is_one(self):
        from metajudge.scoring.abstention_metrics import UTILITY_MATRIX
        for action in ["clarify", "verify", "abstain"]:
            assert UTILITY_MATRIX[(action, action)] == 1.0
        assert UTILITY_MATRIX[("answer_correct", "answer")] == 1.0

    def test_verify_abstain_differentiated(self):
        """CJ-005: verify→abstain and abstain→verify should differ."""
        from metajudge.scoring.abstention_metrics import UTILITY_MATRIX
        assert UTILITY_MATRIX[("verify", "abstain")] == 0.2
        assert UTILITY_MATRIX[("abstain", "verify")] == 0.1

    def test_spec_values_not_embedded_values(self):
        """CJ-004: clarify/verify/abstain→answer should be -0.2/-0.2/-0.3, NOT -0.5."""
        from metajudge.scoring.abstention_metrics import UTILITY_MATRIX
        assert UTILITY_MATRIX[("clarify", "answer")] == -0.2
        assert UTILITY_MATRIX[("verify", "answer")] == -0.2
        assert UTILITY_MATRIX[("abstain", "answer")] == -0.3


# ── Legacy function regression ───────────────────────────────────────

class TestLegacyRegression:

    def test_decision_utility_single_answer_correct(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        assert decision_utility_single("answer", True, "answer") == 1.0

    def test_decision_utility_single_answer_incorrect(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        assert decision_utility_single("answer", False, "answer") == -1.0

    def test_decision_utility_single_clarify_on_answer(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        # Should be -0.2 (spec), not -0.5 (old embedded)
        assert decision_utility_single("clarify", True, "answer") == -0.2

    def test_compute_uwaa_neutral(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        assert compute_uwaa([0.0]) == 0.5

    def test_compute_uwaa_perfect(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        assert compute_uwaa([1.0]) == 1.0

    def test_compute_uwaa_worst(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        assert compute_uwaa([-1.0]) == 0.0

    def test_compute_uwaa_empty(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        assert compute_uwaa([]) == 0.5

    def test_score_family_b_item_v2_returns_float(self):
        """Legacy function still returns a bare float."""
        from metajudge.scoring.abstention_metrics import score_family_b_item_v2
        result = score_family_b_item_v2(
            model_decision="answer",
            model_answer="test",
            is_correct=True,
            gold_action="answer",
        )
        assert isinstance(result, float)


# ── New v6.5 scoring function ────────────────────────────────────────

class TestComputeFamilyBScoreV65:

    def test_correct_answer_on_answer_item(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="answer",
            model_answer="correct answer",
            gold_action="answer",
            content_correct=True,
        )
        assert result["utility"] == 1.0
        assert result["action_correct"] is True
        assert result["content_correct"] is True

    def test_wrong_answer_on_answer_item(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="answer",
            model_answer="wrong",
            gold_action="answer",
            content_correct=False,
        )
        assert result["utility"] == -1.0

    def test_clarify_on_answer_item(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="clarify",
            model_answer="",
            gold_action="answer",
            content_correct=False,
        )
        assert result["utility"] == -0.2

    def test_corrective_answer_on_false_presupposition(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="answer",
            model_answer="The premise is false, there is no such thing",
            gold_action="abstain",
            content_correct=False,
            is_false_presupposition=True,
        )
        assert result["utility"] == 0.5
        assert result["method"] == "corrective_answer"

    def test_acceptable_alternative_floor(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="verify",
            model_answer="",
            gold_action="clarify",
            content_correct=False,
            acceptable_actions=["clarify", "verify"],
        )
        assert result["utility"] >= 0.3

    def test_ambiguous_item_verify(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="verify",
            model_answer="",
            gold_action="verify",
            content_correct=False,
            ambiguity="temporal",
        )
        assert result["utility"] > 0

    def test_returns_structured_dict(self):
        from metajudge.scoring.abstention_metrics import compute_family_b_score_v65
        result = compute_family_b_score_v65(
            model_decision="abstain",
            model_answer="",
            gold_action="abstain",
            content_correct=False,
        )
        assert set(result.keys()) == {"utility", "action_correct", "content_correct", "matrix_cell", "method"}


# ── Answer-rate penalty ──────────────────────────────────────────────

class TestAnswerRatePenalty:

    def test_below_threshold_no_penalty(self):
        from metajudge.scoring.abstention_metrics import apply_answer_rate_penalty
        utils = [0.5, 0.5, 0.5, 0.5, 0.5]
        decisions = ["answer", "verify", "abstain", "clarify", "verify"]  # 20% answer rate
        adjusted, penalty = apply_answer_rate_penalty(utils, decisions, baseline_answer_rate=0.18)
        assert penalty == 0.0
        assert adjusted == utils

    def test_above_threshold_gets_penalty(self):
        from metajudge.scoring.abstention_metrics import apply_answer_rate_penalty
        # 80% answer rate, baseline 18%, threshold 15% → excess = 0.80 - 0.18 - 0.15 = 0.47
        utils = [0.5] * 10
        decisions = ["answer"] * 8 + ["verify", "abstain"]
        adjusted, penalty = apply_answer_rate_penalty(utils, decisions, baseline_answer_rate=0.18)
        assert penalty > 0
        assert penalty <= 0.10  # capped at max_penalty

    def test_penalty_capped(self):
        from metajudge.scoring.abstention_metrics import apply_answer_rate_penalty
        # All answers → maximum excess → penalty should be capped
        utils = [0.5] * 10
        decisions = ["answer"] * 10
        adjusted, penalty = apply_answer_rate_penalty(utils, decisions, baseline_answer_rate=0.18)
        assert penalty == 0.10  # max_penalty


# ── Unicode normalization ────────────────────────────────────────────

class TestUnicodeNormalization:

    def test_normalize_unicode_minus(self):
        from metajudge.scoring.grading_v2 import _normalize
        result = _normalize("3n\u22126")
        assert "-" in result  # should contain ASCII minus
        assert "\u2212" not in result  # should NOT contain Unicode minus

    def test_normalize_sci_unicode_minus(self):
        from metajudge.scoring.grading_v2 import _normalize_sci
        result = _normalize_sci("3n\u22126")
        assert "\u2212" not in result
