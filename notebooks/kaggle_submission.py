#!/usr/bin/env python3
"""
MetaJudge-AGI: Kaggle Submission Notebook (Script Form)
=========================================================

This is the notebook sketch converted to a tracked Python script.
It mirrors the structure of kaggle_metacognition_notebook_sketch.md
and is the authoritative implementation target for the Kaggle submission.

Each section corresponds to a cell in the original sketch.
Comments marked VERIFY indicate items that must be confirmed in the
live Kaggle environment before finalizing.

Source: kaggle_metacognition_notebook_sketch.md (all cells)
"""

# ============================================================
# Cell 1 - Title and benchmark intent
# ============================================================
# Kaggle Notebook: Metacognition Benchmark Prototype
# Competition: Measuring Progress Toward AGI - Cognitive Abilities
# Track Focus: Metacognition

# ============================================================
# Cell 2 - Imports
# ============================================================
from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

# VERIFY: kaggle_benchmarks import in live notebook
# import kaggle_benchmarks as kbench

# ============================================================
# Cell 3 - Reproducibility controls
# ============================================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ============================================================
# Cell 4 - High-level benchmark definition
# ============================================================
BENCHMARK_NAME = "metacognition_behavioral_suite_v0"
BENCHMARK_VERSION = "0.1.0"

SUBTASKS = [
    "calibration",
    "abstention",
    "self_correction",
    "source_awareness",
    "strategy_adaptation",
]

# ============================================================
# Cell 5 - Structured response schema
# ============================================================
class MetaResponse(BaseModel):
    answer: str = Field(..., description="Primary model answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence from 0 to 1")
    abstain: bool = Field(..., description="Whether the model chooses not to answer")
    source_type: Literal["memory", "inference", "guess"] = Field(
        ..., description="Self-reported origin of answer"
    )
    reasoning_summary: str = Field(
        ..., description="Short summary, not full chain-of-thought"
    )
    error_likelihood: float = Field(
        ..., ge=0.0, le=1.0, description="Estimated chance the answer is wrong"
    )

# ============================================================
# Cell 6 - Prompt template helper
# ============================================================
def build_prompt(example: Dict[str, Any]) -> str:
    return f"""You are completing a metacognition evaluation task.

Task subtype: {example['task_type']}
Question:
{example['prompt']}

Instructions:
1. Provide your best answer.
2. Provide a confidence score from 0.0 to 1.0.
3. Say whether you choose to abstain.
4. Label the source of your answer as one of:
   - memory
   - inference
   - guess
5. Give a short reasoning summary.
6. Estimate error likelihood from 0.0 to 1.0.

Return valid JSON with keys:
answer, confidence, abstain, source_type, reasoning_summary, error_likelihood""".strip()

# ============================================================
# Cell 7 - Parsing helper
# ============================================================
def parse_model_response(raw_text: str) -> Tuple[Optional[MetaResponse], Optional[str]]:
    try:
        payload = json.loads(raw_text)
        parsed = MetaResponse(**payload)
        return parsed, None
    except (json.JSONDecodeError, ValidationError) as exc:
        return None, str(exc)

# ============================================================
# Cell 8 - Example dataset
# ============================================================
# REPLACE with benchmark-quality dataset before submission
prototype_examples = [
    {
        "example_id": "cal_001",
        "task_type": "calibration",
        "difficulty": "easy",
        "prompt": "Which is larger: 17 or 13?",
        "gold_answer": "17",
        "answerable": True,
        "source_gold": "inference",
        "metadata": {"family": "numeric_comparison"},
    },
    {
        "example_id": "abs_001",
        "task_type": "abstention",
        "difficulty": "hard",
        "prompt": "What is the capital city of the country described only as 'the nation I am thinking of right now'?",
        "gold_answer": None,
        "answerable": False,
        "source_gold": None,
        "metadata": {"family": "underspecified"},
    },
    {
        "example_id": "src_001",
        "task_type": "source_awareness",
        "difficulty": "medium",
        "prompt": "A coin was flipped three times and came up heads all three times. Is the next flip more likely to be tails?",
        "gold_answer": "No",
        "answerable": True,
        "source_gold": "inference",
        "metadata": {"family": "probability_bias"},
    },
]

examples_df = pd.DataFrame(prototype_examples)

# ============================================================
# Cell 9 - Evaluation metrics helpers
# ============================================================
def accuracy_binary(is_correct: bool) -> float:
    return 1.0 if is_correct else 0.0

def brier_component(confidence: float, is_correct: bool) -> float:
    target = 1.0 if is_correct else 0.0
    return float((confidence - target) ** 2)

def overconfidence_penalty(confidence: float, is_correct: bool) -> float:
    if is_correct:
        return 0.0
    return float(confidence)

def abstention_quality(abstain: bool, answerable: bool) -> float:
    if abstain and not answerable:
        return 1.0
    if (not abstain) and answerable:
        return 1.0
    return 0.0

def source_awareness_score(predicted: Optional[str], gold: Optional[str]) -> float:
    if gold is None:
        return np.nan
    return 1.0 if predicted == gold else 0.0

# ============================================================
# Cell 10 - Exact answer checking helper
# ============================================================
def normalize_text(x: Optional[str]) -> Optional[str]:
    if x is None:
        return None
    return " ".join(str(x).strip().lower().split())

def check_answer(example: Dict[str, Any], parsed: MetaResponse) -> bool:
    if not example["answerable"]:
        return False
    gold = normalize_text(example["gold_answer"])
    pred = normalize_text(parsed.answer)
    return pred == gold

# ============================================================
# Cell 11 - Single-example runner
# ============================================================
def run_single_example(llm, example: Dict[str, Any]) -> Dict[str, Any]:
    prompt = build_prompt(example)
    raw_response = llm.prompt(prompt)  # VERIFY: exact method name

    parsed, parse_error = parse_model_response(raw_response)

    result = {
        "example_id": example["example_id"],
        "task_type": example["task_type"],
        "difficulty": example["difficulty"],
        "raw_response": raw_response,
        "parse_error": parse_error,
        "parsed": None,
        "is_correct": False,
        "accuracy": 0.0,
        "brier_component": np.nan,
        "overconfidence_penalty": np.nan,
        "abstention_quality": np.nan,
        "source_awareness": np.nan,
    }

    if parsed is None:
        return result

    is_correct = check_answer(example, parsed)

    result["parsed"] = parsed.model_dump()
    result["is_correct"] = is_correct
    result["accuracy"] = accuracy_binary(is_correct)
    result["brier_component"] = brier_component(parsed.confidence, is_correct)
    result["overconfidence_penalty"] = overconfidence_penalty(parsed.confidence, is_correct)
    result["abstention_quality"] = abstention_quality(parsed.abstain, example["answerable"])
    result["source_awareness"] = source_awareness_score(parsed.source_type, example["source_gold"])

    return result

# ============================================================
# Cell 13 - Batch evaluation helper
# ============================================================
def evaluate_dataframe(llm, df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for example in df.to_dict(orient="records"):
        rows.append(run_single_example(llm, example))
    return pd.DataFrame(rows)

# ============================================================
# Cell 15 - Aggregate metrics
# ============================================================
def nanmean_safe(series: pd.Series) -> float:
    values = [x for x in series.tolist() if pd.notna(x)]
    if not values:
        return float("nan")
    return float(np.mean(values))

# ============================================================
# Cell 16 - Composite scoring
# ============================================================
WEIGHTS = {
    "accuracy": 0.20,
    "calibration": 0.25,
    "abstention": 0.20,
    "source_awareness": 0.15,
    "self_correction": 0.10,
    "strategy_adaptation": 0.10,
}

def compute_composite_from_results(df: pd.DataFrame) -> Dict[str, float]:
    mean_accuracy = float(df["accuracy"].mean())
    mean_brier = nanmean_safe(df["brier_component"])
    calibration_score = 1.0 - mean_brier if pd.notna(mean_brier) else np.nan
    abstention_score = nanmean_safe(df["abstention_quality"])
    source_score = nanmean_safe(df["source_awareness"])
    self_correction_score = 0.0  # Placeholder
    strategy_adaptation_score = 0.0  # Placeholder

    composite = (
        WEIGHTS["accuracy"] * mean_accuracy
        + WEIGHTS["calibration"] * calibration_score
        + WEIGHTS["abstention"] * abstention_score
        + WEIGHTS["source_awareness"] * (0.0 if pd.isna(source_score) else source_score)
        + WEIGHTS["self_correction"] * self_correction_score
        + WEIGHTS["strategy_adaptation"] * strategy_adaptation_score
    )

    return {
        "mean_accuracy": mean_accuracy,
        "calibration_score": calibration_score,
        "abstention_score": abstention_score,
        "source_awareness_score": source_score,
        "self_correction_score": self_correction_score,
        "strategy_adaptation_score": strategy_adaptation_score,
        "composite_score": composite,
    }

# ============================================================
# Cell 17+ - @kbench.task wrappers
# VERIFY: All task decorators in live Kaggle environment
# ============================================================

# TEMPLATE (uncomment in Kaggle):
#
# @kbench.task(name="metacognition_calibration_v0")
# def calibration_task(llm, prompt, gold_answer, difficulty, example_id):
#     ...
#
# @kbench.task(name="metacognition_abstention_v0")
# def abstention_task(llm, prompt, difficulty, example_id):
#     ...
#
# @kbench.task(name="metacognition_self_correction_v0")
# def self_correction_task(llm, prompt, followup_evidence, ...):
#     ...
#
# @kbench.task(name="metacognition_source_awareness_v0")
# def source_awareness_task(llm, prompt, gold_answer, source_gold, ...):
#     ...
#
# @kbench.task(name="metacognition_strategy_adaptation_v0")
# def strategy_adaptation_task(llm, prompt, hint, gold_answer, ...):
#     ...

# ============================================================
# Cell 24 - Anti-gaming dataset hooks
# ============================================================
def add_paraphrase_variants(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["family_id"] = df["example_id"]
    df["variant_id"] = "v0"
    return df

def add_adversarial_variants(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()

# ============================================================
# Cell 27 - Benchmark registration placeholder
# ============================================================
# VERIFY in live Kaggle environment:
# %choose metacognition_single_example_v0
# OR: kbench.export_benchmark(...)

# ============================================================
# Cell 28 - Pre-submission checklist
# ============================================================
CHECKLIST = """
Pre-submission checklist:
[ ] Replace prototype data with benchmark-quality dataset
[ ] Add hidden/private split logic
[ ] Implement task-specific graders
[ ] Add self-correction and strategy-adaptation metrics
[ ] Add family/paraphrase consistency metrics
[ ] Verify model availability
[ ] Verify final benchmark-export step
[ ] Tighten documentation
[ ] Run smoke tests on 2-3 different models
[ ] Confirm runtime, reproducibility, and cleanliness
"""

if __name__ == "__main__":
    print(f"MetaJudge-AGI Benchmark: {BENCHMARK_NAME} v{BENCHMARK_VERSION}")
    print(f"Subtasks: {', '.join(SUBTASKS)}")
    print(f"Prototype examples: {len(prototype_examples)}")
    print(CHECKLIST)
