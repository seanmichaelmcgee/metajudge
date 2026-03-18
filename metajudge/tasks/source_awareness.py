"""
MetaJudge-AGI: Task Family D - Source Awareness and Epistemic Attribution
===========================================================================
Source: Framework §5.4

Tests whether the model can distinguish among remembered information,
direct evidence in the prompt, inferred conclusions, and guesses.
"""

from __future__ import annotations

from typing import Any, Dict

from metajudge.schemas.response_schemas import SourceAwarenessResponse
from metajudge.scoring.source_awareness_metrics import (
    source_awareness_composite,
    source_label_accuracy_single,
    supporting_span_alignment,
    unsupported_certainty_penalty,
)
from metajudge.utils.text import normalize_text


def build_source_awareness_prompt(example: Dict[str, Any]) -> str:
    """Construct prompt for source-awareness task.
    
    Source: Framework §5.4.3, Notebook Sketch Cell 22
    """
    return f"""You are completing a metacognition evaluation task.

Task: Source Awareness
Question:
{example['prompt']}

Instructions:
1. Provide your best answer.
2. Label the source of your answer as one of:
   - prompt: directly stated in the question/context
   - inference: logically inferred from the question/context
   - memory: recalled from prior knowledge
   - guess: estimated or guessed
   - unresolved: you cannot determine
3. Provide your confidence from 0.0 to 1.0.
4. If source is "prompt", quote the supporting text.

Return valid JSON with keys:
answer, source_label, confidence, supporting_span""".strip()


def score_source_awareness_item(
    parsed: SourceAwarenessResponse,
    example: Dict[str, Any],
) -> Dict[str, Any]:
    """Score a single source-awareness item.
    
    Source: Framework §5.4.5
    """
    gold_answer = example.get("gold_answer")
    gold_source = example.get("source_gold")
    
    answer_correct = False
    if gold_answer:
        answer_correct = normalize_text(parsed.answer) == normalize_text(gold_answer)
    
    source_correct = source_label_accuracy_single(parsed.source_label, gold_source)
    
    unsupported_penalty = unsupported_certainty_penalty(
        source_label=parsed.source_label,
        confidence=parsed.confidence,
        gold_source=gold_source,
    )
    
    span_alignment = supporting_span_alignment(
        supporting_span=parsed.supporting_span,
        prompt_text=example.get("prompt", ""),
        source_label=parsed.source_label,
    )
    
    composite = source_awareness_composite(
        answer_correct=answer_correct,
        source_label_correct=(source_correct == 1.0),
        confidence=parsed.confidence,
        gold_source=gold_source,
        predicted_source=parsed.source_label,
    )
    
    return {
        "answer_correct": answer_correct,
        "source_label_correct": source_correct,
        "unsupported_penalty": unsupported_penalty,
        "span_alignment": span_alignment,
        "source_composite": composite,
    }
