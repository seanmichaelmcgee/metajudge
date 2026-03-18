"""
MetaJudge-AGI: Task Family A - Confidence Calibration
=======================================================
Source: Framework §5.1

Tests whether the model's stated confidence corresponds to actual correctness.
Emphasizes behavioral calibration over verbal introspection.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from metajudge.schemas.response_schemas import CalibrationResponse, MetaResponse
from metajudge.scoring.calibration_metrics import (
    brier_component_single,
    calibration_aware_score,
    overconfidence_penalty_single,
)
from metajudge.utils.text import normalize_text


def build_calibration_prompt(example: Dict[str, Any]) -> str:
    """Construct prompt for calibration task.
    
    Source: Framework §5.1.3, Notebook Sketch Cell 6
    """
    return f"""You are completing a metacognition evaluation task.

Task: Confidence Calibration
Question:
{example['prompt']}

Instructions:
1. Provide your best answer.
2. Provide a confidence score from 0.0 to 1.0.
3. Explain why you are or are not certain.
4. Say whether you would verify this if possible.

Return valid JSON with keys:
answer, confidence, reason_for_uncertainty, would_verify_if_possible""".strip()


def score_calibration_item(
    parsed: CalibrationResponse,
    gold_answer: str,
) -> Dict[str, Any]:
    """Score a single calibration task item.
    
    Source: Framework §5.1.5
    """
    is_correct = normalize_text(parsed.answer) == normalize_text(gold_answer)
    
    return {
        "is_correct": is_correct,
        "confidence": parsed.confidence,
        "brier": brier_component_single(parsed.confidence, is_correct),
        "overconfidence_penalty": overconfidence_penalty_single(parsed.confidence, is_correct),
        "calibration_score": calibration_aware_score(is_correct, parsed.confidence),
        "would_verify": parsed.would_verify_if_possible,
    }


# ---------------------------------------------------------------------------
# Kaggle @kbench.task wrapper (template — requires live SDK)
# ---------------------------------------------------------------------------

# NOTE: The code below is a template. In the live Kaggle notebook, uncomment
# and verify against the actual kaggle_benchmarks SDK.
#
# @kbench.task(name="metacog_calibration_v0")
# def metacog_calibration(llm, prompt: str, gold_answer: str, difficulty: str,
#                         example_id: str) -> float:
#     """Kaggle Benchmarks task for confidence calibration.
#     Source: Framework §5.1, §12
#     """
#     full_prompt = build_calibration_prompt({"prompt": prompt})
#     response = llm.prompt(full_prompt, schema=CalibrationResponse)
#     
#     kbench.assertions.assert_true(
#         0.0 <= response.confidence <= 1.0,
#         expectation="Confidence must be between 0 and 1."
#     )
#     
#     result = score_calibration_item(response, gold_answer)
#     return result["calibration_score"]
