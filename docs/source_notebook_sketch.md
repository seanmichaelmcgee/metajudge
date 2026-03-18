# Kaggle Notebook Sketch for Metacognition Benchmark
## Placeholder / Scaffold Version for the Kaggle Community Benchmarks Competition

This file is a **sketch notebook in markdown form**. It is intentionally implementation-heavy, but still contains placeholders and explicit comments where the team will need to verify exact APIs, model names, output artifacts, and submission wiring inside Kaggle.

It is designed to stay closely aligned with the earlier framework documents:
- conceptual metacognition benchmark framework
- implementation plan and timelines
- Kaggle Community Benchmarks / `kaggle-benchmarks` workflow

---

## Purpose

This notebook scaffold is meant to help an AI-agent team rapidly stand up a first-pass benchmark task suite for **metacognition** in the Kaggle competition focused on cognitive abilities.

The notebook is organized as if it were a Kaggle notebook with sequential cells.

---

## Important verification notes before coding

1. **Kaggle SDK surface may change.**  
   The current public materials indicate use of the `kaggle-benchmarks` SDK with the `@kbench.task` decorator, benchmark tasks executed in Kaggle notebooks, and task/run artifacts emitted for leaderboard construction. Exact helper names and some notebook magics should be verified in the live Kaggle environment before finalizing the submission implementation.

2. **Model availability must be checked inside the live notebook.**  
   Kaggle Benchmarks supports multiple backend models, but the exact list available to a given notebook can vary by environment and access.

3. **Submission packaging must be confirmed in the competition UI.**  
   The scaffold below includes placeholders for the final task-selection and benchmark-export steps because those steps may depend on notebook-side magics or UI actions that should be checked directly in the competition environment.

4. **Judge-model usage should be minimized and verified.**  
   Metacognition tasks should prefer deterministic or structured scoring where possible. Where judge-style evaluation is used, criteria must be narrow, documented, and auditable.

---

# Notebook Sketch

---

## Cell 1 - Title and benchmark intent

```python
# ============================================================
# Kaggle Notebook: Metacognition Benchmark Prototype
# Competition: Measuring Progress Toward AGI - Cognitive Abilities
# Track Focus: Metacognition
# ============================================================

# NOTE:
# This notebook is a scaffold for a Kaggle Community Benchmark task suite.
# Update the title/metadata to match the final benchmark naming convention
# used by your team and by the competition submission page.
```

---

## Cell 2 - Imports

```python
# Core Python
from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional, Tuple

# Data
import numpy as np
import pandas as pd

# Validation / schema
from pydantic import BaseModel, Field, ValidationError

# Kaggle Benchmarks SDK
import kaggle_benchmarks as kbench

# NOTE:
# Verify in the live notebook whether additional imports are needed for:
# - multimodal support
# - dataset evaluation helpers
# - tool use / python sandbox helpers
# - benchmark export / selection utilities
```

---

## Cell 3 - Reproducibility controls

```python
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

# NOTE:
# If the Kaggle backend uses model-side nondeterminism, reproducibility may
# still be imperfect. Document any such variability in the benchmark README.
```

---

## Cell 4 - High-level benchmark definition

```python
BENCHMARK_NAME = "metacognition_behavioral_suite_v0"
BENCHMARK_VERSION = "0.1.0"

# Proposed subdomains of metacognition
SUBTASKS = [
    "calibration",
    "abstention",
    "self_correction",
    "source_awareness",
    "strategy_adaptation",
]

# NOTE:
# These names should remain consistent across:
# - task code
# - output tables
# - benchmark cards / documentation
# - leaderboard analysis notebooks
```

---

## Cell 5 - Structured response schema

```python
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

# NOTE:
# Keep the response schema simple and auditable.
# Avoid requiring hidden reasoning or long free-form introspection.
# The competition goal is behaviorally grounded metacognition, not self-report verbosity.
```

---

## Cell 6 - Prompt template helper

```python
def build_prompt(example: Dict[str, Any]) -> str:
    """Construct a controlled prompt for the model.

    NOTE:
    This prompt is intentionally explicit about the required output structure.
    In the final benchmark, you may want prompt variants/paraphrases to reduce
    overfitting to a single format.
    """
    return f"""
You are completing a metacognition evaluation task.

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
answer, confidence, abstain, source_type, reasoning_summary, error_likelihood
""".strip()

# NOTE:
# Depending on live SDK capabilities, you may replace JSON prompting with
# dataclass / pydantic structured output support if available and reliable.
```

---

## Cell 7 - Parsing helper

```python
def parse_model_response(raw_text: str) -> Tuple[Optional[MetaResponse], Optional[str]]:
    """Parse raw model output into MetaResponse.

    Returns:
        (parsed_response, error_message)
    """
    try:
        payload = json.loads(raw_text)
        parsed = MetaResponse(**payload)
        return parsed, None
    except (json.JSONDecodeError, ValidationError) as exc:
        return None, str(exc)

# NOTE:
# This intentionally treats malformed outputs as failures.
# You may later decide to include a repair pass, but doing so can blur whether
# you are scoring the model or the parser.
```

---

## Cell 8 - Example dataset schema

```python
# Minimal in-notebook prototype dataset.
# In the final benchmark, replace with a packaged dataset or dataframe loaded
# from Kaggle input data.

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
examples_df.head()

# NOTE:
# The final dataset should include:
# - hidden and public splits
# - paraphrase families
# - perturbation families
# - metadata for stratified evaluation
# - documented provenance for any factual items
```

---

## Cell 9 - Evaluation metrics helpers

```python
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
    # Reward abstention on unanswerable items, reward answering on answerable items.
    if abstain and not answerable:
        return 1.0
    if (not abstain) and answerable:
        return 1.0
    return 0.0


def source_awareness_score(predicted: Optional[str], gold: Optional[str]) -> float:
    if gold is None:
        # On unanswerable items, source may be less meaningful.
        # Placeholder choice: do not score.
        return np.nan
    return 1.0 if predicted == gold else 0.0

# NOTE:
# These are intentionally simple first-pass metrics.
# In the final version, likely add:
# - expected calibration error (ECE)
# - risk-coverage analysis
# - self-correction delta
# - consistency across paraphrases
# - family-level aggregation
```

---

## Cell 10 - Exact answer checking helper

```python
def normalize_text(x: Optional[str]) -> Optional[str]:
    if x is None:
        return None
    return " ".join(str(x).strip().lower().split())


def check_answer(example: Dict[str, Any], parsed: MetaResponse) -> bool:
    """First-pass correctness check.

    NOTE:
    This is a placeholder.
    Final benchmark logic should use task-specific grading functions.
    For some tasks:
    - exact match may be appropriate
    - regex / alias sets may be appropriate
    - judge-model grading may be necessary but should be narrowly constrained
    """
    if not example["answerable"]:
        return False

    gold = normalize_text(example["gold_answer"])
    pred = normalize_text(parsed.answer)
    return pred == gold
```

---

## Cell 11 - Single-example runner

```python
def run_single_example(llm, example: Dict[str, Any]) -> Dict[str, Any]:
    prompt = build_prompt(example)
    raw_response = llm.prompt(prompt)

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

# NOTE:
# In the final task suite, replace llm.prompt(...) with whichever SDK pattern
# is best supported for:
# - structured outputs
# - tool-enabled interactions
# - multi-turn stateful evaluation
```

---

## Cell 12 - Smoke test on one example

```python
# Uses Kaggle Benchmarks default LLM.
# Verify the default model in the live notebook and document it.

smoke_result = run_single_example(kbench.llm, prototype_examples[0])
smoke_result
```

---

## Cell 13 - Batch evaluation helper

```python
def evaluate_dataframe(llm, df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for example in df.to_dict(orient="records"):
        rows.append(run_single_example(llm, example))
    return pd.DataFrame(rows)

# NOTE:
# If the SDK has built-in dataset evaluation utilities, consider replacing this
# helper with the official pattern for cleaner task artifact generation.
```

---

## Cell 14 - Run batch prototype

```python
results_df = evaluate_dataframe(kbench.llm, examples_df)

display(results_df.head())
display(results_df[["task_type", "accuracy", "brier_component", "abstention_quality"]])

# NOTE:
# This is a developer-facing inspection cell.
# Remove or tighten in final submission if it adds noise.
```

---

## Cell 15 - Aggregate metrics

```python
def nanmean_safe(series: pd.Series) -> float:
    values = [x for x in series.tolist() if pd.notna(x)]
    if not values:
        return float("nan")
    return float(np.mean(values))


summary = (
    results_df
    .groupby("task_type", dropna=False)
    .agg(
        n_examples=("example_id", "count"),
        mean_accuracy=("accuracy", "mean"),
        mean_brier=("brier_component", nanmean_safe),
        mean_overconfidence=("overconfidence_penalty", nanmean_safe),
        mean_abstention_quality=("abstention_quality", nanmean_safe),
        mean_source_awareness=("source_awareness", nanmean_safe),
    )
    .reset_index()
)

summary
```

---

## Cell 16 - Composite scoring sketch

```python
# Placeholder weights.
# These should be finalized in the benchmark spec and justified in the README.

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

    # Lower Brier is better, so convert to an inverted score.
    mean_brier = nanmean_safe(df["brier_component"])
    calibration_score = 1.0 - mean_brier if pd.notna(mean_brier) else np.nan

    abstention_score = nanmean_safe(df["abstention_quality"])
    source_score = nanmean_safe(df["source_awareness"])

    # Placeholder zeros until those tasks are implemented.
    self_correction_score = 0.0
    strategy_adaptation_score = 0.0

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

compute_composite_from_results(results_df)

# NOTE:
# The final competition submission should avoid hidden scoring surprises.
# Use transparent component definitions, but keep private examples private.
```

---

## Cell 17 - First-pass `@kbench.task` task wrapper

```python
@kbench.task(name="metacognition_single_example_v0")
def metacognition_single_example_task(
    llm,
    task_type: str,
    prompt: str,
    gold_answer: Optional[str],
    answerable: bool,
    source_gold: Optional[str],
    difficulty: str = "unknown",
    example_id: str = "unknown",
):
    """Prototype Kaggle Benchmarks task for a single metacognition item.

    NOTE:
    This is a first-pass wrapper. It demonstrates task structure, but the team
    should verify:
    - preferred assertion patterns
    - whether returning structured metadata is supported directly
    - how best to emit benchmark artifacts for leaderboard use
    """

    example = {
        "example_id": example_id,
        "task_type": task_type,
        "difficulty": difficulty,
        "prompt": prompt,
        "gold_answer": gold_answer,
        "answerable": answerable,
        "source_gold": source_gold,
        "metadata": {},
    }

    result = run_single_example(llm, example)

    # Placeholder assertion:
    # For early prototype, require parseable output.
    # Later versions should include richer assertion or evaluation logic.
    kbench.assertions.assert_true(
        result["parse_error"] is None,
        expectation="Model should return valid structured JSON matching schema."
    )

    # NOTE:
    # It may be appropriate to assert additional minimum behavior here,
    # but avoid making the task so brittle that formatting dominates the score.
```

---

## Cell 18 - Run prototype task directly

```python
metacognition_single_example_task.run(
    llm=kbench.llm,
    task_type=prototype_examples[0]["task_type"],
    prompt=prototype_examples[0]["prompt"],
    gold_answer=prototype_examples[0]["gold_answer"],
    answerable=prototype_examples[0]["answerable"],
    source_gold=prototype_examples[0]["source_gold"],
    difficulty=prototype_examples[0]["difficulty"],
    example_id=prototype_examples[0]["example_id"],
)

# NOTE:
# Confirm in the live Kaggle environment that the run produces the expected
# task/run artifacts and that the task appears correctly in notebook outputs.
```

---

## Cell 19 - Calibration-only task sketch

```python
@kbench.task(name="metacognition_calibration_v0")
def calibration_task(llm, prompt: str, gold_answer: str, difficulty: str, example_id: str):
    """Prototype calibration task.

    Focus:
    - answer correctness
    - confidence calibration
    """
    example = {
        "example_id": example_id,
        "task_type": "calibration",
        "difficulty": difficulty,
        "prompt": prompt,
        "gold_answer": gold_answer,
        "answerable": True,
        "source_gold": "inference",
        "metadata": {},
    }

    result = run_single_example(llm, example)

    kbench.assertions.assert_true(
        result["parse_error"] is None,
        expectation="Calibration task response should be parseable."
    )

    # Optional placeholder:
    # A stronger version might assert confidence is present and in-range,
    # but schema validation already covers that.
```

---

## Cell 20 - Abstention-only task sketch

```python
@kbench.task(name="metacognition_abstention_v0")
def abstention_task(llm, prompt: str, difficulty: str, example_id: str):
    """Prototype abstention task.

    Focus:
    - whether the model knows when not to answer
    """
    example = {
        "example_id": example_id,
        "task_type": "abstention",
        "difficulty": difficulty,
        "prompt": prompt,
        "gold_answer": None,
        "answerable": False,
        "source_gold": None,
        "metadata": {},
    }

    result = run_single_example(llm, example)

    kbench.assertions.assert_true(
        result["parse_error"] is None,
        expectation="Abstention task response should be parseable."
    )

    # NOTE:
    # Final scoring should reward abstention on genuinely unanswerable items
    # and penalize confident fabrication.
```

---

## Cell 21 - Self-correction task sketch (multi-turn placeholder)

```python
def build_self_correction_turns(example: Dict[str, Any]) -> List[str]:
    """Create a two-turn interaction for self-correction.

    NOTE:
    This is only a placeholder. Final self-correction tasks should use
    carefully designed contradictory or clarifying evidence.
    """
    turn1 = f"""
Question:
{example['prompt']}

Respond in JSON with keys:
answer, confidence, abstain, source_type, reasoning_summary, error_likelihood
""".strip()

    turn2 = f"""
You previously answered a question. New evidence is now available:
{example['followup_evidence']}

Please reconsider and return updated JSON with the same keys.
""".strip()

    return [turn1, turn2]
```

```python
@kbench.task(name="metacognition_self_correction_v0")
def self_correction_task(
    llm,
    prompt: str,
    followup_evidence: str,
    gold_answer_before: Optional[str],
    gold_answer_after: str,
    difficulty: str,
    example_id: str,
):
    """Prototype self-correction task.

    NOTE:
    Verify the best supported pattern in Kaggle Benchmarks for multi-turn
    interaction capture. This placeholder assumes repeated prompt calls are acceptable.
    """
    initial_prompt, followup_prompt = build_self_correction_turns(
        {
            "prompt": prompt,
            "followup_evidence": followup_evidence,
        }
    )

    raw1 = llm.prompt(initial_prompt)
    parsed1, err1 = parse_model_response(raw1)

    raw2 = llm.prompt(followup_prompt)
    parsed2, err2 = parse_model_response(raw2)

    kbench.assertions.assert_true(
        err1 is None and err2 is None,
        expectation="Self-correction task should produce parseable JSON at both turns."
    )

    # NOTE:
    # In the final version, compute:
    # - pre/post correctness
    # - confidence shift
    # - whether revision moved in the right direction
    # - whether the model overcorrected or ignored evidence
```

---

## Cell 22 - Source-awareness task sketch

```python
@kbench.task(name="metacognition_source_awareness_v0")
def source_awareness_task(
    llm,
    prompt: str,
    gold_answer: str,
    source_gold: str,
    difficulty: str,
    example_id: str,
):
    """Prototype source-awareness task.

    Focus:
    - whether the model can appropriately distinguish memory vs inference vs guess
    """
    example = {
        "example_id": example_id,
        "task_type": "source_awareness",
        "difficulty": difficulty,
        "prompt": prompt,
        "gold_answer": gold_answer,
        "answerable": True,
        "source_gold": source_gold,
        "metadata": {},
    }

    result = run_single_example(llm, example)

    kbench.assertions.assert_true(
        result["parse_error"] is None,
        expectation="Source-awareness response should be parseable."
    )

    # NOTE:
    # Final dataset design matters here.
    # The 'gold' source category should be defensible and not overly subjective.
```

---

## Cell 23 - Strategy-adaptation task sketch

```python
@kbench.task(name="metacognition_strategy_adaptation_v0")
def strategy_adaptation_task(
    llm,
    prompt: str,
    hint: str,
    gold_answer: str,
    difficulty: str,
    example_id: str,
):
    """Prototype strategy-adaptation task.

    Focus:
    - whether the model changes behavior after a hint, constraint, or failure signal
    """
    raw1 = llm.prompt(
        f"""
Solve the following problem and return JSON with the standard schema.
Problem:
{prompt}
""".strip()
    )

    raw2 = llm.prompt(
        f"""
Try again. This hint may help:
{hint}

Return JSON with the same schema.
""".strip()
    )

    parsed1, err1 = parse_model_response(raw1)
    parsed2, err2 = parse_model_response(raw2)

    kbench.assertions.assert_true(
        err1 is None and err2 is None,
        expectation="Strategy-adaptation task should produce parseable JSON on both attempts."
    )

    # NOTE:
    # Final scoring should capture:
    # - whether the model changed strategy meaningfully
    # - whether performance improved
    # - whether confidence appropriately updated
```

---

## Cell 24 - Anti-gaming dataset hooks

```python
def add_paraphrase_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder for generating paraphrase-linked item families.

    Final version should:
    - preserve semantic content
    - vary surface form
    - attach family_id metadata
    """
    df = df.copy()
    df["family_id"] = df["example_id"]
    df["variant_id"] = "v0"
    return df


def add_adversarial_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder for adversarial transformations.

    Examples:
    - distractor language
    - irrelevant details
    - reordered wording
    - ambiguity injection
    """
    return df.copy()

# NOTE:
# Anti-gaming design should primarily live in the dataset and evaluation plan,
# not only in the prompt.
```

---

## Cell 25 - Family consistency analysis sketch

```python
def family_consistency_report(results: pd.DataFrame, metadata_df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder family-level analysis.

    Intended purpose:
    - compare confidence / answers across equivalent tasks
    - detect brittle prompt-format overfitting
    """
    merged = results.merge(
        metadata_df[["example_id", "task_type"]],
        on="example_id",
        how="left",
        suffixes=("", "_meta"),
    )
    # Placeholder return
    return merged

# NOTE:
# Final version should compute:
# - within-family answer agreement
# - within-family confidence variance
# - confidence/correctness alignment across paraphrases
```

---

## Cell 26 - Result export

```python
# Developer-facing exports
results_df.to_csv("prototype_results.csv", index=False)
summary.to_csv("prototype_summary.csv", index=False)

with open("prototype_composite.json", "w") as f:
    json.dump(compute_composite_from_results(results_df), f, indent=2)

# NOTE:
# Verify which files Kaggle expects or surfaces automatically for benchmark
# artifact generation, and avoid cluttering the notebook with unnecessary outputs.
```

---

## Cell 27 - Benchmark registration / selection placeholder

```python
# ============================================================
# PLACEHOLDER SECTION
# ============================================================

# The live Kaggle notebook may require a final selection step to identify
# which task(s) should be exported as the notebook's benchmark artifact.
#
# Examples that must be VERIFIED LIVE:
# - a notebook magic such as %choose
# - a UI-side action
# - a helper function in kaggle_benchmarks
#
# PSEUDOCODE ONLY:
#
# %choose metacognition_single_example_v0
#
# OR:
#
# kbench.export_benchmark(...)
#
# DO NOT finalize this section without checking the current official Kaggle docs
# and an in-environment starter notebook.
```

---

## Cell 28 - Final checklist markdown cell

```python
# Final pre-submission checklist:
#
# [ ] Replace prototype data with benchmark-quality dataset
# [ ] Add hidden/private split logic outside public notebook outputs
# [ ] Implement task-specific graders
# [ ] Add self-correction and strategy-adaptation metrics
# [ ] Add family/paraphrase consistency metrics
# [ ] Verify model availability and chosen default model
# [ ] Verify final benchmark-export step in live Kaggle UI
# [ ] Tighten documentation and benchmark card
# [ ] Run smoke tests on at least 2-3 different backend models
# [ ] Confirm runtime, reproducibility, and notebook cleanliness
```

---

# Recommended follow-on files to generate next

To move from this sketch to a submission-grade package, the next best artifacts would be:

1. **dataset schema markdown**  
   Exact columns, split logic, provenance rules, and family/variant design.

2. **task authoring guide**  
   Rules for writing high-quality metacognition items across all five subtasks.

3. **scoring module code**  
   Production Python for calibration, risk-coverage, self-correction delta, and composite scoring.

4. **agent execution plan**  
   Which AI agents generate items, validate them, perturb them, and audit them.

---

# Practical guidance on what must be updated or verified

## Must update
- dataset contents
- exact task prompts
- gold labels
- final weights
- final metric formulas
- self-correction and adaptation scoring logic
- benchmark metadata and naming

## Must verify live in Kaggle
- exact `kaggle-benchmarks` API surface available in notebook
- exact model list available for the competition environment
- exact final task-selection / export mechanism
- any notebook magics used by current starter notebooks
- artifact naming conventions surfaced on leaderboard

## Must document clearly
- why each task measures metacognition rather than generic reasoning
- why the source-type labels are defensible
- how abstention is rewarded and hallucination penalized
- how anti-gaming design works
- which aspects are public and which are held out/private

---

# Closing note

This scaffold is intentionally conservative: it emphasizes **structured outputs, auditable grading, and explicit placeholders** rather than pretending uncertain SDK details are already fixed. That is the safest and most useful way to hand work over to an AI-agent team for rapid implementation inside a fast-moving Kaggle competition.
