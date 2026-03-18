"""
MetaJudge-AGI: Evaluation Runner
==================================
Source: Notebook Sketch Cells 11-14

Orchestrates running task items through models and collecting results.
This module handles local evaluation; Kaggle-specific integration is separate.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from metajudge.schemas.response_schemas import MetaResponse
from metajudge.utils.text import normalize_text


def parse_model_response(
    raw_text: str,
) -> Tuple[Optional[MetaResponse], Optional[str]]:
    """Parse raw model output into MetaResponse.
    
    Source: Notebook Sketch Cell 7
    
    Returns:
        (parsed_response, error_message)
    """
    try:
        payload = json.loads(raw_text)
        parsed = MetaResponse(**payload)
        return parsed, None
    except (json.JSONDecodeError, Exception) as exc:
        return None, str(exc)


def build_prompt(example: Dict[str, Any]) -> str:
    """Construct a controlled prompt for the model.
    
    Source: Notebook Sketch Cell 6
    """
    return f"""You are completing a metacognition evaluation task.

Task subtype: {example['task_type']}
Question:
{example['prompt']}

Instructions:
1. Provide your best answer.
2. Provide a confidence score from 0.0 to 1.0.
3. Say whether you choose to abstain.
4. Label the source of your answer as one of: memory, inference, guess
5. Give a short reasoning summary.
6. Estimate error likelihood from 0.0 to 1.0.

Return valid JSON with keys:
answer, confidence, abstain, source_type, reasoning_summary, error_likelihood""".strip()


def run_single_example(
    model_fn: Callable[[str], str],
    example: Dict[str, Any],
) -> Dict[str, Any]:
    """Run a single example through a model function.
    
    Source: Notebook Sketch Cell 11
    
    Args:
        model_fn: Callable that takes a prompt string and returns raw text
        example: Task item dict
    """
    prompt = build_prompt(example)
    raw_response = model_fn(prompt)
    
    parsed, parse_error = parse_model_response(raw_response)
    
    result = {
        "example_id": example.get("example_id", "unknown"),
        "task_type": example.get("task_type", "unknown"),
        "difficulty": example.get("difficulty", "unknown"),
        "raw_response": raw_response,
        "parse_error": parse_error,
        "parsed": None,
        "is_correct": False,
        "confidence": float("nan"),
    }
    
    if parsed is None:
        return result
    
    is_correct = False
    gold = example.get("gold_answer")
    if gold is not None and example.get("answerable", True):
        is_correct = normalize_text(parsed.answer) == normalize_text(gold)
    
    result["parsed"] = parsed.model_dump()
    result["is_correct"] = is_correct
    result["confidence"] = parsed.confidence
    
    return result


def evaluate_dataframe(
    model_fn: Callable[[str], str],
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Run all examples in a dataframe through the model.
    
    Source: Notebook Sketch Cell 13
    """
    rows = []
    for example in df.to_dict(orient="records"):
        rows.append(run_single_example(model_fn, example))
    return pd.DataFrame(rows)
