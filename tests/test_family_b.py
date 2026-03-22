"""
Tests for Family B: Selective Abstention / Verification / Clarification

Covers:
- Pilot dataset structure validation (87 items, v3)
- Action distribution and balance
- Per-class field requirements (clarify, verify, abstain, answer)
- Scoring function correctness (UWAA, action F1, AUARC)
- Schema validation (AbstentionResponse)
"""

import pytest
import json
from pathlib import Path
from collections import Counter


DATA_PATH = Path(__file__).parent.parent / "data" / "family_b_pilot_v2.json"


@pytest.fixture(scope="module")
def pilot_items():
    with open(DATA_PATH) as f:
        return json.load(f)


# ── Dataset structure ──────────────────────────────────────────────────


class TestPilotDatasetStructure:
    def test_item_count(self, pilot_items):
        assert len(pilot_items) == 87

    def test_required_fields(self, pilot_items):
        required_fields = [
            "item_id", "question", "gold_action", "gold_answer",
            "category", "difficulty", "acceptable_actions",
            "is_false_presupposition", "premise_type",
        ]
        for item in pilot_items:
            for field in required_fields:
                assert field in item, f"Missing {field} in {item['item_id']}"

    def test_valid_actions(self, pilot_items):
        valid_actions = {"answer", "clarify", "verify", "abstain"}
        for item in pilot_items:
            assert item["gold_action"] in valid_actions, (
                f"{item['item_id']} has invalid gold_action: {item['gold_action']}"
            )

    def test_valid_difficulties(self, pilot_items):
        valid_difficulties = {"easy", "medium", "hard"}
        for item in pilot_items:
            assert item["difficulty"] in valid_difficulties, (
                f"{item['item_id']} has invalid difficulty: {item['difficulty']}"
            )

    def test_id_prefix(self, pilot_items):
        for item in pilot_items:
            assert item["item_id"].startswith("abs_"), (
                f"Item ID {item['item_id']} does not start with abs_"
            )

    def test_unique_ids(self, pilot_items):
        ids = [item["item_id"] for item in pilot_items]
        assert len(ids) == len(set(ids)), "Duplicate item IDs found"


# ── Action distribution ────────────────────────────────────────────────


class TestActionDistribution:
    def test_all_four_action_classes(self, pilot_items):
        dist = Counter(item["gold_action"] for item in pilot_items)
        assert len(dist) == 4, f"Expected 4 action classes, got {len(dist)}"

    def test_no_class_too_small(self, pilot_items):
        """v3 distribution: answer=15, clarify=13, verify=30, abstain=29.
        Every class must have at least 10 items."""
        dist = Counter(item["gold_action"] for item in pilot_items)
        for action, count in dist.items():
            assert count >= 10, f"{action} has only {count} items (min 10)"


# ── Per-class field requirements ───────────────────────────────────────


class TestClarifyItems:
    def test_have_interpretations_where_present(self, pilot_items):
        """Items with interpretations must have ≥2 entries."""
        clarify_items = [i for i in pilot_items if i["gold_action"] == "clarify"]
        with_interp = [i for i in clarify_items if "interpretations" in i]
        assert len(with_interp) >= 4, "At least 4 clarify items should have interpretations"
        for item in with_interp:
            assert len(item["interpretations"]) >= 2, (
                f"{item['item_id']} needs ≥2 interpretations"
            )

    def test_have_canonical_clarification_where_present(self, pilot_items):
        """Items with canonical_clarification must be non-empty."""
        clarify_items = [i for i in pilot_items if i["gold_action"] == "clarify"]
        with_cc = [i for i in clarify_items if "canonical_clarification" in i]
        assert len(with_cc) >= 4, "At least 4 clarify items should have canonical_clarification"
        for item in with_cc:
            assert item["canonical_clarification"], (
                f"{item['item_id']} has empty canonical_clarification"
            )


class TestVerifyItems:
    def test_have_verification_target_where_present(self, pilot_items):
        """Items with verification_target must be non-empty."""
        verify_items = [i for i in pilot_items if i["gold_action"] == "verify"]
        with_vt = [i for i in verify_items if "verification_target" in i]
        assert len(with_vt) >= 4, "At least 4 verify items should have verification_target"
        for item in with_vt:
            assert item["verification_target"], (
                f"{item['item_id']} has empty verification_target"
            )


class TestAbstainItems:
    def test_have_unanswerability_type_where_present(self, pilot_items):
        """Items with unanswerability_type must have a valid value."""
        valid_types = {"false_premise", "unknowable", "subjective", "incoherent", "temporal"}
        abstain_items = [i for i in pilot_items if i["gold_action"] == "abstain"]
        with_ut = [i for i in abstain_items if "unanswerability_type" in i]
        assert len(with_ut) >= 8, "At least 8 abstain items should have unanswerability_type"
        for item in with_ut:
            assert item["unanswerability_type"] in valid_types, (
                f"{item['item_id']} has invalid unanswerability_type: "
                f"{item['unanswerability_type']}"
            )


class TestAnswerItems:
    def test_have_gold_answers(self, pilot_items):
        answer_items = [i for i in pilot_items if i["gold_action"] == "answer"]
        for item in answer_items:
            assert item["gold_answer"], (
                f"{item['item_id']} missing gold_answer"
            )


# ── Scoring functions ──────────────────────────────────────────────────


class TestDecisionUtility:
    def test_correct_answer_on_answer_item(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        assert decision_utility_single("answer", True, "answer") == 1.0

    def test_incorrect_answer_on_answer_item(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        assert decision_utility_single("answer", False, "answer") == -1.0

    def test_correct_action_on_each_gold(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        assert decision_utility_single("clarify", False, "clarify") == 1.0
        assert decision_utility_single("verify", False, "verify") == 1.0
        assert decision_utility_single("abstain", False, "abstain") == 1.0

    def test_over_abstention_penalty(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        u = decision_utility_single("abstain", False, "answer")
        assert u < 0, "Abstaining on an answerable item should be negative"

    def test_answer_correct_on_clarify_partial(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        u = decision_utility_single("answer", True, "clarify")
        assert u == 0.5, "Correct answer on clarify item gets +0.5 partial credit"

    def test_cautious_actions_partial_credit(self):
        from metajudge.scoring.abstention_metrics import decision_utility_single
        # Non-answer actions on non-answer items get partial credit
        assert decision_utility_single("clarify", False, "verify") == 0.3
        assert decision_utility_single("verify", False, "clarify") == 0.3
        assert decision_utility_single("abstain", False, "clarify") == 0.3


class TestUWAA:
    def test_perfect_score(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        # All +1.0 utilities → UWAA = (1.0 + 1.0) / 2.0 = 1.0
        assert compute_uwaa([1.0, 1.0, 1.0, 1.0]) == 1.0

    def test_worst_score(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        # All -1.0 utilities → UWAA = (-1.0 + 1.0) / 2.0 = 0.0
        assert compute_uwaa([-1.0, -1.0, -1.0, -1.0]) == 0.0

    def test_neutral_score(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        # Mean utility = 0 → UWAA = 0.5
        assert compute_uwaa([1.0, -1.0]) == pytest.approx(0.5)

    def test_empty_returns_neutral(self):
        from metajudge.scoring.abstention_metrics import compute_uwaa
        assert compute_uwaa([]) == 0.5


class TestActionF1:
    def test_perfect_predictions(self):
        from metajudge.scoring.abstention_metrics import compute_action_f1
        predicted = ["answer", "clarify", "verify", "abstain"]
        gold = ["answer", "clarify", "verify", "abstain"]
        f1_dict = compute_action_f1(predicted, gold)
        assert f1_dict["answer"]["f1"] == 1.0
        assert f1_dict["macro"]["f1"] == 1.0

    def test_some_errors(self):
        from metajudge.scoring.abstention_metrics import compute_action_f1
        predicted = ["answer", "answer", "clarify", "verify"]
        gold = ["answer", "clarify", "clarify", "verify"]
        f1_dict = compute_action_f1(predicted, gold)
        assert "answer" in f1_dict
        assert "macro" in f1_dict
        # answer precision should be < 1 (1 TP + 1 FP)
        assert f1_dict["answer"]["precision"] < 1.0

    def test_all_classes_present(self):
        from metajudge.scoring.abstention_metrics import compute_action_f1
        predicted = ["answer", "clarify", "verify", "abstain"]
        gold = ["answer", "clarify", "verify", "abstain"]
        f1_dict = compute_action_f1(predicted, gold)
        for action in ["answer", "clarify", "verify", "abstain"]:
            assert action in f1_dict


class TestAUARC:
    def test_perfect_confidence(self):
        from metajudge.scoring.abstention_metrics import compute_auarc
        # All correct, all high confidence
        auarc = compute_auarc([0.9, 0.8, 0.7, 0.6], [True, True, True, True])
        assert auarc == 1.0

    def test_empty_returns_nan(self):
        import math
        from metajudge.scoring.abstention_metrics import compute_auarc
        assert math.isnan(compute_auarc([], []))


# ── Schema validation ──────────────────────────────────────────────────


class TestAbstentionResponseSchema:
    def test_valid_answer_response(self):
        from metajudge.schemas.response_schemas import AbstentionResponse
        resp = AbstentionResponse(decision="answer", answer="42", confidence=0.9)
        assert resp.decision == "answer"
        assert resp.confidence == 0.9

    def test_valid_clarify_response(self):
        from metajudge.schemas.response_schemas import AbstentionResponse
        resp = AbstentionResponse(
            decision="clarify",
            confidence=0.3,
            clarification_request="Which Mercury do you mean?",
        )
        assert resp.decision == "clarify"
        assert resp.clarification_request is not None

    def test_valid_verify_response(self):
        from metajudge.schemas.response_schemas import AbstentionResponse
        resp = AbstentionResponse(
            decision="verify",
            confidence=0.5,
            verification_target="Check current Bitcoin price via API",
        )
        assert resp.decision == "verify"
        assert resp.verification_target is not None

    def test_valid_abstain_response(self):
        from metajudge.schemas.response_schemas import AbstentionResponse
        resp = AbstentionResponse(
            decision="abstain",
            confidence=0.1,
            abstention_reason="This is a subjective question with no objective answer",
        )
        assert resp.decision == "abstain"

    def test_invalid_decision_rejected(self):
        from pydantic import ValidationError
        from metajudge.schemas.response_schemas import AbstentionResponse
        with pytest.raises(ValidationError):
            AbstentionResponse(decision="ask", confidence=0.5)

    def test_confidence_bounds(self):
        from pydantic import ValidationError
        from metajudge.schemas.response_schemas import AbstentionResponse
        with pytest.raises(ValidationError):
            AbstentionResponse(decision="answer", answer="test", confidence=1.5)
