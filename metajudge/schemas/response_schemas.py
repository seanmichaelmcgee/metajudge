"""
MetaJudge-AGI: Structured Response Schemas
===========================================
Source: Framework §5.1-5.5, §6.2; Notebook Sketch Cell 5

These schemas define the structured outputs required from models under evaluation.
Each task family has its own schema, plus a unified superset for cross-task analysis.

All schemas use Pydantic v2 for validation. In the Kaggle notebook, these may be
converted to dataclasses or plain dicts depending on SDK constraints.
"""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Task Family A: Confidence Calibration
# Source: Framework §5.1.3
# ---------------------------------------------------------------------------

class CalibrationResponse(BaseModel):
    """Response schema for calibration tasks."""
    answer: str = Field(..., description="Primary model answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")
    reason_for_uncertainty: str = Field(
        ..., description="Why the model is or is not certain"
    )
    would_verify_if_possible: bool = Field(
        ..., description="Whether the model would seek verification"
    )


# ---------------------------------------------------------------------------
# Task Family B: Selective Abstention and Deferral
# Source: Framework §5.2.3
# ---------------------------------------------------------------------------

class AbstentionResponse(BaseModel):
    """Response schema for abstention/deferral tasks."""
    decision: Literal["answer", "ask", "abstain", "verify"] = Field(
        ..., description="Action choice"
    )
    answer: Optional[str] = Field(None, description="Answer if decision is 'answer'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")
    missing_information: Optional[str] = Field(
        None, description="What info is missing (if decision is 'ask')"
    )
    abstention_reason: Optional[str] = Field(
        None, description="Why abstaining (if decision is 'abstain')"
    )


# ---------------------------------------------------------------------------
# Task Family C: Error Detection and Targeted Self-Correction
# Source: Framework §5.3.3
# ---------------------------------------------------------------------------

class SelfCorrectionResponse(BaseModel):
    """Response schema for stage-2 self-correction tasks."""
    is_likely_wrong: bool = Field(
        ..., description="Whether the model thinks its prior answer was wrong"
    )
    suspected_error_type: Literal[
        "arithmetic", "misread", "unsupported_inference",
        "memory_failure", "none", "other"
    ] = Field(..., description="Category of suspected error")
    revised_answer: Optional[str] = Field(
        None, description="Updated answer if revision is warranted"
    )
    revised_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Updated confidence"
    )
    what_changed: str = Field(
        ..., description="Targeted explanation of what was revised and why"
    )


# ---------------------------------------------------------------------------
# Task Family D: Source Awareness and Epistemic Attribution
# Source: Framework §5.4.3
# ---------------------------------------------------------------------------

class SourceAwarenessResponse(BaseModel):
    """Response schema for source-awareness tasks."""
    answer: str = Field(..., description="Primary model answer")
    source_label: Literal[
        "prompt", "inference", "memory", "guess", "unresolved"
    ] = Field(..., description="Epistemic origin of the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")
    supporting_span: Optional[str] = Field(
        None, description="Quote from prompt supporting the answer, if applicable"
    )


# ---------------------------------------------------------------------------
# Task Family E: Strategy Selection and Adaptive Revision
# Source: Framework §5.5.3
# ---------------------------------------------------------------------------

class StrategyAdaptationResponse(BaseModel):
    """Response schema for strategy selection tasks."""
    chosen_strategy: Literal[
        "recall", "stepwise", "decompose", "verify_first", "decline"
    ] = Field(..., description="Selected solution strategy")
    why_this_strategy: str = Field(
        ..., description="Justification for strategy choice"
    )
    answer: str = Field(..., description="Primary model answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")
    would_change_strategy_after_feedback: bool = Field(
        ..., description="Whether the model would switch strategy given feedback"
    )


# ---------------------------------------------------------------------------
# Unified Meta Response (cross-task superset)
# Source: Notebook Sketch Cell 5; Framework §6.2
# ---------------------------------------------------------------------------

class MetaResponse(BaseModel):
    """Unified response schema used for general-purpose metacognition evaluation.
    
    This is a superset schema. Individual task families should prefer their
    specific schemas above, but this provides a common interface for
    cross-task analysis and prototype evaluation.
    """
    answer: str = Field(..., description="Primary model answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0-1")
    abstain: bool = Field(False, description="Whether the model chooses not to answer")
    source_type: Literal["memory", "inference", "guess"] = Field(
        ..., description="Self-reported origin of answer"
    )
    reasoning_summary: str = Field(
        ..., description="Short summary, not full chain-of-thought"
    )
    error_likelihood: float = Field(
        ..., ge=0.0, le=1.0, description="Estimated chance the answer is wrong"
    )


# ---------------------------------------------------------------------------
# Task Item Metadata Schema (hidden from model, used for evaluation)
# Source: Framework §6.3
# ---------------------------------------------------------------------------

class TaskItemMetadata(BaseModel):
    """Hidden evaluator metadata for each task item.
    
    Not exposed to the model under evaluation.
    """
    example_id: str
    task_type: Literal[
        "calibration", "abstention", "self_correction",
        "source_awareness", "strategy_adaptation"
    ]
    gold_answer: Optional[str] = None
    ambiguity_class: Literal[
        "clear", "underspecified", "ambiguous", "adversarial"
    ] = "clear"
    intended_optimal_action: Literal[
        "answer", "ask", "abstain", "verify", "revise", "keep"
    ] = "answer"
    source_type_gold: Optional[Literal[
        "prompt", "inference", "memory", "guess", "unresolved"
    ]] = None
    difficulty: Literal["easy", "medium", "hard", "deceptive", "adversarial"] = "medium"
    adversarial_category: Optional[str] = None
    expected_strategy_family: Optional[str] = None
    answerable: bool = True
    family_id: Optional[str] = None
    variant_id: Optional[str] = None
    penalty_schedule: Optional[str] = None
