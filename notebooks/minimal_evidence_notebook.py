# =============================================================================
# MetaJudge-AGI: Minimal Evidence Notebook
# Competition: Measuring Progress Toward AGI — Cognitive Abilities
# Purpose: Prove wrapper-task architecture in live Kaggle environment
# =============================================================================

# %% [markdown]
# # MetaJudge-AGI — Minimal Evidence Notebook
# **Purpose:** Prove that our wrapper-task submission architecture works in the live Kaggle competition environment.
# **Scope:** 5 cells, 2-row dataset, ~$0.01 quota spend.

# %% Cell 1 — Environment & Import Evidence
import kaggle_benchmarks as kbench
from kaggle_benchmarks import assertions, chats
from dataclasses import dataclass
import pandas as pd

print(f"SDK imported successfully")
print(f"Default LLM: {kbench.llm}")
print(f"Judge LLM:   {kbench.judge_llm}")
print(f"Available: kbench.llms keys accessible")

# %% Cell 2 — Minimal Subtask (simulates one family)
@dataclass
class MiniCalibration:
    answer: str
    confidence: float

@kbench.task(name="mini_calibration")
def mini_calibration(llm, question: str, gold_answer: str) -> float:
    """Tiny subtask: ask a question, get structured response, score confidence calibration."""
    response = llm.prompt(
        f"Answer this question. Be honest about your confidence.\nQuestion: {question}",
        schema=MiniCalibration
    )
    # Simple binary correctness + calibration error
    is_correct = gold_answer.lower() in response.answer.lower()
    calibration_error = abs(response.confidence - (1.0 if is_correct else 0.0))
    score = 1.0 - calibration_error
    assertions.assert_true(
        0.0 <= response.confidence <= 1.0,
        f"Confidence {response.confidence} out of [0,1]"
    )
    return score

# Quick single-item test
single_result = mini_calibration.run(
    llm=kbench.llm,
    question="What is the capital of France?",
    gold_answer="Paris"
)
print(f"Single run result: {single_result}")

# %% Cell 3 — Dataset Evaluation (2 rows, minimal quota)
eval_df = pd.DataFrame([
    {"question": "What is the capital of France?", "gold_answer": "Paris"},
    {"question": "What is 2+2?", "gold_answer": "4"},
])

with kbench.client.enable_cache():
    runs = mini_calibration.evaluate(
        llm=[kbench.llm],
        evaluation_data=eval_df,
        n_jobs=1,
        max_attempts=1,
    )

results_df = runs.as_dataframe()
print(f"Evaluate returned {len(results_df)} rows")
print(results_df)

# %% Cell 4 — Wrapper Task (top-level composite pattern)
@kbench.task(name="metacognition_suite")
def metacognition_suite(llm) -> float:
    """
    Top-level wrapper: runs sub-benchmarks via .evaluate(), returns composite float.
    In production this wraps 5 families. Here we wrap 1 to prove the pattern.
    """
    sub_df = pd.DataFrame([
        {"question": "What is the capital of Japan?", "gold_answer": "Tokyo"},
        {"question": "What is 3*7?", "gold_answer": "21"},
    ])
    with kbench.client.enable_cache():
        sub_runs = mini_calibration.evaluate(
            llm=[llm],
            evaluation_data=sub_df,
            n_jobs=1,
            max_attempts=1,
        )
    sub_results = sub_runs.as_dataframe()
    # Composite: mean of subtask scores (production will weight 5 families)
    composite = sub_results["result"].mean()
    assertions.assert_true(0.0 <= composite <= 1.0, f"Composite {composite} out of range")
    return float(composite)

wrapper_result = metacognition_suite.run(llm=kbench.llm)
print(f"Wrapper task composite score: {wrapper_result}")

# %% Cell 5 — Submission Path
# This is the final cell that selects the top-level task for leaderboard submission.
# In production, this is the ONLY task exported.
%choose metacognition_suite
