"""Unit tests for response schemas.

Source: Framework §5.1-5.5, §6.2-6.3
"""
import pytest
from pydantic import ValidationError

from metajudge.schemas.response_schemas import (
    CalibrationResponse,
    AbstentionResponse,
    SelfCorrectionResponse,
    SourceAwarenessResponse,
    StrategyAdaptationResponse,
    MetaResponse,
    TaskItemMetadata,
)


class TestCalibrationResponse:
    def test_valid_response(self):
        r = CalibrationResponse(
            answer="42",
            confidence=0.95,
            reason_for_uncertainty="Simple arithmetic",
            would_verify_if_possible=False,
        )
        assert r.confidence == 0.95
        assert r.answer == "42"

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            CalibrationResponse(
                answer="x",
                confidence=1.5,
                reason_for_uncertainty="test",
                would_verify_if_possible=False,
            )

    def test_confidence_lower_bound(self):
        with pytest.raises(ValidationError):
            CalibrationResponse(
                answer="x",
                confidence=-0.1,
                reason_for_uncertainty="test",
                would_verify_if_possible=False,
            )


class TestAbstentionResponse:
    def test_valid_answer(self):
        r = AbstentionResponse(
            decision="answer",
            answer="Paris",
            confidence=0.99,
        )
        assert r.decision == "answer"

    def test_valid_abstain(self):
        r = AbstentionResponse(
            decision="abstain",
            confidence=0.1,
            abstention_reason="Insufficient information",
        )
        assert r.decision == "abstain"

    def test_invalid_decision(self):
        with pytest.raises(ValidationError):
            AbstentionResponse(
                decision="invalid_choice",
                confidence=0.5,
            )


class TestSelfCorrectionResponse:
    def test_valid_correction(self):
        r = SelfCorrectionResponse(
            is_likely_wrong=True,
            suspected_error_type="arithmetic",
            revised_answer="133",
            revised_confidence=0.85,
            what_changed="Fixed addition error",
        )
        assert r.is_likely_wrong is True
        assert r.suspected_error_type == "arithmetic"

    def test_no_correction(self):
        r = SelfCorrectionResponse(
            is_likely_wrong=False,
            suspected_error_type="none",
            revised_confidence=0.9,
            what_changed="No changes needed",
        )
        assert r.revised_answer is None


class TestSourceAwarenessResponse:
    def test_valid_prompt_source(self):
        r = SourceAwarenessResponse(
            answer="1937",
            source_label="prompt",
            confidence=0.95,
            supporting_span="completed in 1937",
        )
        assert r.source_label == "prompt"

    def test_valid_guess_source(self):
        r = SourceAwarenessResponse(
            answer="Unknown",
            source_label="guess",
            confidence=0.2,
        )
        assert r.source_label == "guess"

    def test_invalid_source_label(self):
        with pytest.raises(ValidationError):
            SourceAwarenessResponse(
                answer="test",
                source_label="internet",
                confidence=0.5,
            )


class TestStrategyAdaptationResponse:
    def test_valid_strategy(self):
        r = StrategyAdaptationResponse(
            chosen_strategy="decompose",
            why_this_strategy="Problem has multiple parts",
            answer="0",
            confidence=0.9,
            would_change_strategy_after_feedback=False,
        )
        assert r.chosen_strategy == "decompose"

    def test_invalid_strategy(self):
        with pytest.raises(ValidationError):
            StrategyAdaptationResponse(
                chosen_strategy="brute_force",
                why_this_strategy="test",
                answer="test",
                confidence=0.5,
                would_change_strategy_after_feedback=False,
            )


class TestMetaResponse:
    def test_valid_response(self):
        r = MetaResponse(
            answer="Paris",
            confidence=0.99,
            abstain=False,
            source_type="memory",
            reasoning_summary="Common knowledge",
            error_likelihood=0.01,
        )
        assert r.source_type == "memory"

    def test_invalid_source_type(self):
        with pytest.raises(ValidationError):
            MetaResponse(
                answer="test",
                confidence=0.5,
                abstain=False,
                source_type="internet",
                reasoning_summary="test",
                error_likelihood=0.5,
            )


class TestTaskItemMetadata:
    def test_valid_metadata(self):
        m = TaskItemMetadata(
            example_id="cal_001",
            task_type="calibration",
            gold_answer="42",
            difficulty="easy",
            answerable=True,
        )
        assert m.task_type == "calibration"
        assert m.answerable is True

    def test_defaults(self):
        m = TaskItemMetadata(
            example_id="test",
            task_type="abstention",
        )
        assert m.ambiguity_class == "clear"
        assert m.intended_optimal_action == "answer"
        assert m.difficulty == "medium"
