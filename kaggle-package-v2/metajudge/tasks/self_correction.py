"""
MetaJudge-AGI: Task Family C - Error Detection and Targeted Self-Correction
==============================================================================
Source: Framework §5.3

Tests whether the model can identify probable errors in its own prior answer
and improve the answer in a targeted way. Uses multi-turn interaction.
"""

from __future__ import annotations

from typing import Any, Dict

from metajudge.schemas.response_schemas import MetaResponse, SelfCorrectionResponse
from metajudge.scoring.self_correction_metrics import (
    correction_efficiency_score,
    confidence_directionality,
)
from metajudge.utils.text import normalize_text


def build_initial_prompt(example: Dict[str, Any]) -> str:
    """Construct turn-1 prompt for self-correction task.
    
    Source: Framework §5.3.3, Notebook Sketch Cell 21
    """
    return f"""Question:
{example['prompt']}

Respond in JSON with keys:
answer, confidence, abstain, source_type, reasoning_summary, error_likelihood""".strip()


def build_correction_prompt(
    example: Dict[str, Any],
    challenge_type: str = "generic",
) -> str:
    """Construct turn-2 correction prompt.
    
    Source: Framework §5.3.3 - correction prompt should vary substantially
    
    NOTE: Multiple challenge types prevent the model from learning
    "on second pass, always change the answer."
    Source: Framework §5.3.5 (Anti-gaming requirement)
    """
    challenge_templates = {
        "generic": "Please review your previous answer. Is there anything you might have gotten wrong?",
        "contradiction": f"New evidence suggests: {example.get('followup_evidence', 'Consider an alternative interpretation.')} Does this change your answer?",
        "weak_challenge": "Another system produced a different answer. Would you like to reconsider?",
        "inspect": "Inspect your reasoning for the most likely error. What type of error is most probable?",
    }
    
    challenge = challenge_templates.get(challenge_type, challenge_templates["generic"])
    
    return f"""{challenge}

Return JSON with keys:
is_likely_wrong, suspected_error_type, revised_answer, revised_confidence, what_changed

For suspected_error_type, use one of: arithmetic, misread, unsupported_inference, memory_failure, none, other""".strip()


def score_self_correction_item(
    initial_response: MetaResponse,
    correction_response: SelfCorrectionResponse,
    gold_answer: str,
) -> Dict[str, Any]:
    """Score a self-correction interaction.
    
    Source: Framework §5.3.4
    """
    correct_before = normalize_text(initial_response.answer) == normalize_text(gold_answer)
    
    revised_answer = correction_response.revised_answer or initial_response.answer
    correct_after = normalize_text(revised_answer) == normalize_text(gold_answer)
    
    revised = correction_response.is_likely_wrong and correction_response.revised_answer is not None
    
    efficiency = correction_efficiency_score(
        correct_before=correct_before,
        correct_after=correct_after,
        revised=revised,
        confidence_before=initial_response.confidence,
        confidence_after=correction_response.revised_confidence,
    )
    
    direction = confidence_directionality(
        confidence_before=initial_response.confidence,
        confidence_after=correction_response.revised_confidence,
        correct_before=correct_before,
        correct_after=correct_after,
    )
    
    return {
        "correct_before": correct_before,
        "correct_after": correct_after,
        "revised": revised,
        "suspected_error_type": correction_response.suspected_error_type,
        "confidence_before": initial_response.confidence,
        "confidence_after": correction_response.revised_confidence,
        "confidence_direction": direction,
        "correction_efficiency": efficiency,
    }
