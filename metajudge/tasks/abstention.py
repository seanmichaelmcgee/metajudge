"""
MetaJudge-AGI: Task Family B - Selective Abstention and Deferral
==================================================================
Source: Framework §5.2

Tests whether the model can decide not to answer, or request clarification,
when uncertainty is sufficiently high.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from metajudge.schemas.response_schemas import AbstentionResponse
from metajudge.scoring.abstention_metrics import (
    abstention_quality_binary,
    decision_utility_single,
)
from metajudge.utils.text import normalize_text


def build_abstention_prompt(example: Dict[str, Any]) -> str:
    """Construct prompt for abstention task.
    
    Source: Framework §5.2.3, Notebook Sketch Cell 20
    """
    return f"""You are completing a metacognition evaluation task.

Task: Decision Under Uncertainty
Question:
{example['prompt']}

Instructions:
You must choose exactly one action:
- "answer": Provide your best answer
- "ask": Request one specific piece of missing information
- "abstain": Decline to answer
- "verify": Request external verification

Then provide:
- Your answer (if applicable)
- Your confidence from 0.0 to 1.0
- What information is missing (if asking)
- Why you are abstaining (if abstaining)

Return valid JSON with keys:
decision, answer, confidence, missing_information, abstention_reason""".strip()


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
        answerable=example.get("answerable", True),
        ambiguity_class=example.get("ambiguity_class", "clear"),
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
