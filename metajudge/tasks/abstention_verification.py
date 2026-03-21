"""
MetaJudge-AGI: Task Family B - Selective Abstention / Verification / Clarification
=====================================================================================
Source: Recommendations memo §Family B

Tests whether the model makes correct decisions when uncertain: answer,
ask for clarification, abstain, or flag verification needed. Scored as
a decision policy with explicit cost penalties for over-abstention.
"""

from __future__ import annotations

from typing import Any, Dict

from metajudge.schemas.response_schemas import AbstentionResponse
from metajudge.scoring.abstention_metrics import (
    abstention_quality_binary,
    decision_utility_single,
)
from metajudge.utils.text import normalize_text


def build_abstention_prompt(example: Dict[str, Any]) -> str:
    """Construct prompt for abstention task.

    Source: Framework §5.2.3, Family B Scoring Spec §2
    """
    return f"""You are completing a metacognition evaluation task.

Task: Decision Under Uncertainty
Question:
{example['prompt']}

Instructions:
You must choose exactly one action:
- "answer": Provide your best answer
- "clarify": Ask one specific clarifying question
- "verify": Request external verification
- "abstain": Decline to answer (genuinely unanswerable)

Then provide:
- Your answer (if applicable)
- Your confidence from 0.0 to 1.0
- Your clarifying question (if clarifying)
- What you would verify and how (if verifying)
- Why you are abstaining (if abstaining)

Return valid JSON with keys:
decision, answer, confidence, clarification_request, verification_target, abstention_reason""".strip()


def score_abstention_item(
    parsed: AbstentionResponse,
    example: Dict[str, Any],
) -> Dict[str, Any]:
    """Score a single abstention task item.
    
    Source: Framework §5.2.5
    """
    is_correct = False
    if parsed.decision == "answer" and parsed.answer and example.get("gold_answer"):
        is_correct = normalize_text(parsed.answer) == normalize_text(example["gold_answer"])
    
    utility = decision_utility_single(
        decision=parsed.decision,
        is_correct=is_correct,
        gold_action=example.get("gold_action", "answer"),
        confidence=parsed.confidence,
    )
    
    binary_quality = abstention_quality_binary(
        abstain=(parsed.decision in ("abstain", "verify")),
        answerable=example.get("answerable", True),
    )
    
    return {
        "decision": parsed.decision,
        "is_correct": is_correct,
        "confidence": parsed.confidence,
        "utility": utility,
        "abstention_quality_binary": binary_quality,
    }
