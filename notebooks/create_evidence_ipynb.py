"""Create the minimal evidence notebook as a proper .ipynb file for Kaggle upload."""
import json

notebook = {
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        },
        "kaggle": {
            "accelerator": "none",
            "dataSources": [],
            "isInternetEnabled": True,
            "language": "python",
            "sourceType": "notebook"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4,
    "cells": [
        # ── Markdown: Title ──
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# MetaJudge-AGI — Minimal Evidence Notebook\n",
                "\n",
                "**Competition:** Measuring Progress Toward AGI — Cognitive Abilities  \n",
                "**Purpose:** Prove wrapper-task submission architecture in live Kaggle environment  \n",
                "**Scope:** 5 code cells, 2-row datasets, minimal quota spend  \n",
                "**Date:** 2026-03-18"
            ]
        },
        # ── Cell 1: Import & Environment Evidence ──
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 1 — Import & Environment Evidence\n",
                "import kaggle_benchmarks as kbench\n",
                "from kaggle_benchmarks import assertions, chats\n",
                "from dataclasses import dataclass\n",
                "import pandas as pd\n",
                "\n",
                "print(f\"SDK imported: kaggle_benchmarks\")\n",
                "print(f\"Default LLM: {kbench.llm}\")\n",
                "print(f\"Judge LLM:   {kbench.judge_llm}\")\n",
                "print(\"Environment OK\")"
            ],
            "execution_count": None,
            "outputs": []
        },
        # ── Cell 2: Subtask + Single Run ──
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 2 — Minimal Subtask: structured output + single run\n",
                "@dataclass\n",
                "class MiniCalibration:\n",
                "    answer: str\n",
                "    confidence: float\n",
                "\n",
                "@kbench.task(name=\"mini_calibration\")\n",
                "def mini_calibration(llm, question: str, gold_answer: str) -> float:\n",
                "    \"\"\"Subtask: structured prompt → score.\"\"\"\n",
                "    response = llm.prompt(\n",
                "        f\"Answer this question. Be honest about your confidence (0.0-1.0).\\n\"\n",
                "        f\"Question: {question}\",\n",
                "        schema=MiniCalibration\n",
                "    )\n",
                "    is_correct = gold_answer.lower() in response.answer.lower()\n",
                "    calibration_error = abs(response.confidence - (1.0 if is_correct else 0.0))\n",
                "    score = 1.0 - calibration_error\n",
                "    assertions.assert_true(\n",
                "        0.0 <= response.confidence <= 1.0,\n",
                "        expectation=f\"Confidence {response.confidence} in [0,1]\"\n",
                "    )\n",
                "    print(f\"  answer={response.answer!r}, conf={response.confidence:.2f}, correct={is_correct}, score={score:.3f}\")\n",
                "    return score\n",
                "\n",
                "# Single-item proof\n",
                "result = mini_calibration.run(\n",
                "    llm=kbench.llm,\n",
                "    question=\"What is the capital of France?\",\n",
                "    gold_answer=\"Paris\"\n",
                ")\n",
                "print(f\"\\nSingle run result: {result}\")"
            ],
            "execution_count": None,
            "outputs": []
        },
        # ── Cell 3: Dataset Evaluation ──
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 3 — Dataset Evaluation (2 rows, minimal quota)\n",
                "eval_df = pd.DataFrame([\n",
                "    {\"question\": \"What is the capital of Germany?\", \"gold_answer\": \"Berlin\"},\n",
                "    {\"question\": \"What is 7 times 8?\", \"gold_answer\": \"56\"},\n",
                "])\n",
                "\n",
                "with kbench.client.enable_cache():\n",
                "    runs = mini_calibration.evaluate(\n",
                "        llm=[kbench.llm],\n",
                "        evaluation_data=eval_df,\n",
                "        n_jobs=1,\n",
                "        max_attempts=1,\n",
                "    )\n",
                "\n",
                "results_df = runs.as_dataframe()\n",
                "print(f\"Evaluate returned {len(results_df)} rows\")\n",
                "print(results_df)"
            ],
            "execution_count": None,
            "outputs": []
        },
        # ── Cell 4: Wrapper Task (the key architectural proof) ──
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 4 — Wrapper Task: top-level composite returning float\n",
                "# This proves the production pattern: one @kbench.task wraps N sub-benchmarks.\n",
                "\n",
                "@kbench.task(name=\"metacognition_suite\")\n",
                "def metacognition_suite(llm) -> float:\n",
                "    \"\"\"\n",
                "    Top-level wrapper: calls sub-task .evaluate(), returns composite float.\n",
                "    Production version will wrap 5 families with weighted scoring.\n",
                "    \"\"\"\n",
                "    sub_df = pd.DataFrame([\n",
                "        {\"question\": \"What is the capital of Japan?\", \"gold_answer\": \"Tokyo\"},\n",
                "        {\"question\": \"What is 3 times 7?\", \"gold_answer\": \"21\"},\n",
                "    ])\n",
                "    with kbench.client.enable_cache():\n",
                "        sub_runs = mini_calibration.evaluate(\n",
                "            llm=[llm],\n",
                "            evaluation_data=sub_df,\n",
                "            n_jobs=1,\n",
                "            max_attempts=1,\n",
                "        )\n",
                "    sub_results = sub_runs.as_dataframe()\n",
                "    composite = float(sub_results[\"result\"].mean())\n",
                "    print(f\"Sub-results: {sub_results['result'].tolist()}\")\n",
                "    print(f\"Composite score: {composite:.4f}\")\n",
                "    assertions.assert_true(0.0 <= composite <= 1.0, expectation=f\"Composite in [0,1]\")\n",
                "    return composite\n",
                "\n",
                "wrapper_result = metacognition_suite.run(llm=kbench.llm)\n",
                "print(f\"\\nWrapper task returned: {wrapper_result}\")"
            ],
            "execution_count": None,
            "outputs": []
        },
        # ── Cell 5: Submission Path ──
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 5 — Submission Path\n",
                "# This is the final cell. It selects the top-level task for leaderboard.\n",
                "# In production, metacognition_suite wraps all 5 sub-benchmarks.\n",
                "%choose metacognition_suite"
            ],
            "execution_count": None,
            "outputs": []
        }
    ]
}

with open("/home/user/workspace/metajudge-agi/notebooks/metajudge_evidence.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)

print("Created: notebooks/metajudge_evidence.ipynb")
print(f"Cells: {len(notebook['cells'])} ({sum(1 for c in notebook['cells'] if c['cell_type']=='code')} code, {sum(1 for c in notebook['cells'] if c['cell_type']=='markdown')} markdown)")
