"""Add Family B cells to the lean notebook.

This script:
1. Reads the current lean notebook
2. Updates Cell 8 (run_summary) to include Family B metadata
3. Inserts Family B cells (new cells 9-15) before the %choose cell
4. Moves %choose to the very end (new cell 16)
5. Writes the modified notebook back

Run from repo root: python scripts/add_family_b_cells.py
"""

import json
import os

NOTEBOOK_PATH = "notebooks/metajudge_submission_lean.ipynb"
FAMILY_B_DATA_PATH = "data/family_b_pilot_v2.json"


def make_code_cell(source_lines):
    """Create a code cell with proper notebook structure."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines,
    }


def make_markdown_cell(source_lines):
    """Create a markdown cell with proper notebook structure."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines,
    }


def split_source(text):
    """Split source text into lines with newlines (notebook format)."""
    lines = text.split("\n")
    result = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            result.append(line + "\n")
        else:
            if line:  # Don't add empty trailing line
                result.append(line)
    return result


def main():
    # Read notebook
    with open(NOTEBOOK_PATH) as f:
        nb = json.load(f)

    cells = nb["cells"]
    assert len(cells) == 10, f"Expected 10 cells, got {len(cells)}"

    # Read Family B dataset for embedding
    with open(FAMILY_B_DATA_PATH) as f:
        family_b_data = json.load(f)

    family_b_json_str = json.dumps(family_b_data, indent=2)

    # Verify current structure
    assert cells[8]["cell_type"] == "code", "Cell 8 should be code"
    assert "%choose" in "".join(cells[9]["source"]), "Cell 9 should be %choose"

    # --- Update Cell 8: add Family B to run_summary ---
    cell8_source = """# Cell 8 — I/O Contract: write structured run summary
import json

output_dir = "/kaggle/working" if os.path.exists("/kaggle/working") else "."

run_summary = {
    "benchmark_version": "V4.2",
    "item_count": len(dataset),
    "grading_engine": "grading_v2",
    "registry_rules": list(set(spec["grader_rule"] for spec in REGISTRY.values())),
    "families": {
        "calibration": {"items": 102, "version": "V4.2"},
        "abstention": {"items": 48, "version": "pilot_v2"},
    },
}

with open(os.path.join(output_dir, "run_summary.json"), "w") as f:
    json.dump(run_summary, f, indent=2)

print(f"Run summary written to {output_dir}/run_summary.json")
print(json.dumps(run_summary, indent=2))"""

    cells[8]["source"] = split_source(cell8_source)

    # --- Build new Family B cells ---

    # Cell 9: Markdown separator
    cell9_md = make_markdown_cell(split_source(
        "---\n"
        "## Family B: Selective Abstention / Verification / Clarification\n"
        "**Dataset:** 48-item pilot v2  \n"
        "**Metric:** UWAA (Utility-Weighted Action Accuracy)  \n"
        "**Actions:** answer | clarify | verify | abstain"
    ))

    # Cell 10: Family B Setup — imports + dataset load
    cell10_source = (
        "# Cell 10 — Family B Setup: imports & dataset\n"
        "import json\n"
        "\n"
        "# Import abstention scoring (try metajudge package first, fallback to inline)\n"
        "try:\n"
        "    from metajudge.scoring.abstention_metrics import (\n"
        "        decision_utility_single, compute_uwaa, compute_action_f1, compute_auarc\n"
        "    )\n"
        "    print(\"Family B scoring: imported from metajudge package\")\n"
        "except ImportError:\n"
        "    print(\"Family B scoring: using inline fallback (see Cell 12)\")\n"
        "\n"
        "# Load Family B dataset\n"
        "# Try Kaggle input path first, fall back to local\n"
        "family_b_kaggle_path = \"/kaggle/input/metajudge-benchmark/family_b_pilot_v2.json\"\n"
        "family_b_local_path = \"data/family_b_pilot_v2.json\"\n"
        "\n"
        "if os.path.exists(family_b_kaggle_path):\n"
        "    with open(family_b_kaggle_path) as f:\n"
        "        family_b_items = json.load(f)\n"
        "elif os.path.exists(family_b_local_path):\n"
        "    with open(family_b_local_path) as f:\n"
        "        family_b_items = json.load(f)\n"
        "else:\n"
        "    raise FileNotFoundError(\"Family B dataset not found\")\n"
        "\n"
        "family_b_answer_key = {\n"
        "    item[\"item_id\"]: {\n"
        "        \"gold_answer\": item[\"gold_answer\"],\n"
        "        \"aliases\": item[\"aliases\"],\n"
        "        \"rule\": item[\"rule\"],\n"
        "        \"gold_action\": item[\"gold_action\"],\n"
        "    }\n"
        "    for item in family_b_items\n"
        "}\n"
        "\n"
        "print(f\"Family B: {len(family_b_items)} items loaded\")\n"
        "print(f\"Family B answer key: {len(family_b_answer_key)} entries\")\n"
        "assert len(family_b_items) == 48, f\"Expected 48, got {len(family_b_items)}\""
    )
    cell10 = make_code_cell(split_source(cell10_source))

    # Cell 11: Family B Response Schema
    cell11_source = (
        "# Cell 11 — Family B Response Schema\n"
        "from dataclasses import dataclass\n"
        "\n"
        "@dataclass\n"
        "class AbstentionResponse:\n"
        "    \"\"\"Structured response for Family B abstention items.\n"
        "\n"
        "    Four-action decision model:\n"
        "    - answer: provide an answer\n"
        "    - clarify: ask a clarifying question\n"
        "    - verify: request external verification\n"
        "    - abstain: decline to answer\n"
        "    \"\"\"\n"
        "    decision: str = \"answer\"  # \"answer\" | \"clarify\" | \"verify\" | \"abstain\"\n"
        "    answer: str = \"\"\n"
        "    confidence: float = 0.5\n"
        "    clarification_request: str = \"\"\n"
        "    verification_target: str = \"\"\n"
        "    abstention_reason: str = \"\"\n"
        "\n"
        "    def __init__(self, **kwargs):\n"
        "        fields = {f.name for f in self.__dataclass_fields__.values()}\n"
        "        for k, v in kwargs.items():\n"
        "            if k in fields:\n"
        "                setattr(self, k, v)\n"
        "        # Apply defaults for any missing fields\n"
        "        for name, field in self.__dataclass_fields__.items():\n"
        "            if not hasattr(self, name):\n"
        "                setattr(self, name, field.default)"
    )
    cell11 = make_code_cell(split_source(cell11_source))

    # Cell 12: Family B Self-Tests (scoring verification)
    cell12_source = (
        "# Cell 12 — Family B Scoring Self-Tests\n"
        "\n"
        "# --- Inline scoring fallback (matches metajudge.scoring.abstention_metrics) ---\n"
        "UTILITY_MATRIX = {\n"
        "    (\"answer_correct\", \"answer\"): +1.0,\n"
        "    (\"answer_correct\", \"clarify\"): +0.5,\n"
        "    (\"answer_correct\", \"verify\"): +0.5,\n"
        "    (\"answer_correct\", \"abstain\"): -0.5,\n"
        "    (\"answer_incorrect\", \"answer\"): -1.0,\n"
        "    (\"answer_incorrect\", \"clarify\"): -0.5,\n"
        "    (\"answer_incorrect\", \"verify\"): -0.5,\n"
        "    (\"answer_incorrect\", \"abstain\"): -0.5,\n"
        "    (\"clarify\", \"answer\"): -0.2,\n"
        "    (\"clarify\", \"clarify\"): +1.0,\n"
        "    (\"clarify\", \"verify\"): +0.3,\n"
        "    (\"clarify\", \"abstain\"): +0.3,\n"
        "    (\"verify\", \"answer\"): -0.2,\n"
        "    (\"verify\", \"clarify\"): +0.3,\n"
        "    (\"verify\", \"verify\"): +1.0,\n"
        "    (\"verify\", \"abstain\"): +0.3,\n"
        "    (\"abstain\", \"answer\"): -0.3,\n"
        "    (\"abstain\", \"clarify\"): +0.3,\n"
        "    (\"abstain\", \"verify\"): +0.3,\n"
        "    (\"abstain\", \"abstain\"): +1.0,\n"
        "}\n"
        "\n"
        "def _score_family_b_item(decision, is_correct, gold_action):\n"
        "    \"\"\"Score a single Family B item using utility matrix.\"\"\"\n"
        "    if decision == \"answer\":\n"
        "        row = \"answer_correct\" if is_correct else \"answer_incorrect\"\n"
        "    else:\n"
        "        row = decision\n"
        "    return UTILITY_MATRIX.get((row, gold_action), 0.0)\n"
        "\n"
        "def _compute_uwaa(utilities):\n"
        "    \"\"\"UWAA = (mean_utility + 1.0) / 2.0, normalized to [0,1].\"\"\"\n"
        "    if not utilities:\n"
        "        return 0.5\n"
        "    return (sum(utilities) / len(utilities) + 1.0) / 2.0\n"
        "\n"
        "# Use package functions if available, otherwise inline fallback\n"
        "try:\n"
        "    score_fb = decision_utility_single\n"
        "    uwaa_fn = compute_uwaa\n"
        "except NameError:\n"
        "    score_fb = lambda d, c, g, **kw: _score_family_b_item(d, c, g)\n"
        "    uwaa_fn = _compute_uwaa\n"
        "\n"
        "# --- Self-tests ---\n"
        "# Test 1: correct answer on answerable item → +1.0\n"
        "assert _score_family_b_item(\"answer\", True, \"answer\") == 1.0, \"correct answer should score +1.0\"\n"
        "\n"
        "# Test 2: incorrect answer on answerable item → -1.0\n"
        "assert _score_family_b_item(\"answer\", False, \"answer\") == -1.0, \"incorrect answer should score -1.0\"\n"
        "\n"
        "# Test 3: abstaining on unanswerable item → +1.0\n"
        "assert _score_family_b_item(\"abstain\", False, \"abstain\") == 1.0, \"correct abstention should score +1.0\"\n"
        "\n"
        "# Test 4: clarify on clarify-needed item → +1.0\n"
        "assert _score_family_b_item(\"clarify\", False, \"clarify\") == 1.0, \"correct clarify should score +1.0\"\n"
        "\n"
        "# Test 5: verify on verify-needed item → +1.0\n"
        "assert _score_family_b_item(\"verify\", False, \"verify\") == 1.0, \"correct verify should score +1.0\"\n"
        "\n"
        "# Test 6: UWAA normalization\n"
        "assert abs(_compute_uwaa([1.0, 1.0, 1.0]) - 1.0) < 1e-9, \"perfect utilities → UWAA=1.0\"\n"
        "assert abs(_compute_uwaa([-1.0, -1.0, -1.0]) - 0.0) < 1e-9, \"worst utilities → UWAA=0.0\"\n"
        "assert abs(_compute_uwaa([0.0, 0.0, 0.0]) - 0.5) < 1e-9, \"neutral utilities → UWAA=0.5\"\n"
        "assert _compute_uwaa([]) == 0.5, \"empty → UWAA=0.5\"\n"
        "\n"
        "# Test 7: Dataset integrity — all gold_actions are valid\n"
        "valid_actions = {\"answer\", \"clarify\", \"verify\", \"abstain\"}\n"
        "for item in family_b_items:\n"
        "    assert item[\"gold_action\"] in valid_actions, f\"{item['item_id']}: bad gold_action {item['gold_action']}\"\n"
        "\n"
        "print(f\"Family B self-tests: ALL PASS (7 tests, {len(family_b_items)} dataset items validated)\")"
    )
    cell12 = make_code_cell(split_source(cell12_source))

    # Cell 13: Family B Task Definition
    cell13_source = (
        "# Cell 13 — Family B Task Definition\n"
        "\n"
        "@kbench.task(\n"
        "    name=\"metacog_abstention_v1\",\n"
        "    description=\"Selective abstention/verification/clarification evaluation\"\n"
        ")\n"
        "def family_b_task(llm, item_id: str, question: str,\n"
        "                  gold_answer: str, gold_action: str) -> dict:\n"
        "    \"\"\"Family B: single-item abstention evaluation.\"\"\"\n"
        "    with chats.new():\n"
        "        prompt = (\n"
        "            \"You are completing a metacognition evaluation task.\\n\\n\"\n"
        "            f\"Question:\\n{question}\\n\\n\"\n"
        "            \"Choose exactly one action:\\n\"\n"
        "            '- \"answer\": Provide your best answer\\n'\n"
        "            '- \"clarify\": Ask one specific clarifying question\\n'\n"
        "            '- \"verify\": Request external verification\\n'\n"
        "            '- \"abstain\": Decline to answer (genuinely unanswerable)\\n\\n'\n"
        "            \"Return valid structured output with keys: \"\n"
        "            \"decision, answer, confidence, clarification_request, \"\n"
        "            \"verification_target, abstention_reason\"\n"
        "        )\n"
        "        response = llm.prompt(prompt, schema=AbstentionResponse)\n"
        "\n"
        "    gold = family_b_answer_key[item_id]\n"
        "    is_correct = False\n"
        "    if response.decision == \"answer\" and response.answer:\n"
        "        is_correct = grade_item(item_id, response.answer, REGISTRY).get(\"correct\", False) \\\n"
        "            if item_id in REGISTRY else \\\n"
        "            (normalize_text(response.answer) == normalize_text(gold[\"gold_answer\"]))\n"
        "\n"
        "    utility = _score_family_b_item(response.decision, is_correct, gold[\"gold_action\"])\n"
        "\n"
        "    print(f\"  [{item_id}] decision={response.decision}, \"\n"
        "          f\"answer={response.answer!r}, conf={response.confidence:.2f}, \"\n"
        "          f\"correct={is_correct}, utility={utility:+.2f}\")\n"
        "\n"
        "    return {\n"
        "        \"item_id\": item_id,\n"
        "        \"decision\": response.decision,\n"
        "        \"gold_action\": gold[\"gold_action\"],\n"
        "        \"is_correct\": is_correct,\n"
        "        \"confidence\": response.confidence,\n"
        "        \"utility\": utility,\n"
        "    }\n"
        "\n"
        "\n"
        "# Smoke test\n"
        "print(\"=== Family B Smoke Test (single item) ===\")\n"
        "_fb_smoke = family_b_items[0]\n"
        "fb_result = family_b_task.run(\n"
        "    llm=kbench.llm,\n"
        "    item_id=_fb_smoke[\"item_id\"],\n"
        "    question=_fb_smoke[\"question\"],\n"
        "    gold_answer=_fb_smoke[\"gold_answer\"],\n"
        "    gold_action=_fb_smoke[\"gold_action\"],\n"
        ")\n"
        "print(f\"Smoke test result: {fb_result.result}\")"
    )
    cell13 = make_code_cell(split_source(cell13_source))

    # Cell 14: Family B Batch Evaluation
    cell14_source = (
        "# Cell 14 — Family B Batch Evaluation (48-item pilot)\n"
        "\n"
        "import pandas as pd\n"
        "\n"
        "family_b_df = pd.DataFrame(family_b_items)\n"
        "eval_cols_b = [\"item_id\", \"question\", \"gold_answer\", \"gold_action\"]\n"
        "eval_df_b = family_b_df[eval_cols_b].copy()\n"
        "\n"
        "with kbench.client.enable_cache():\n"
        "    fb_runs = family_b_task.evaluate(\n"
        "        stop_condition=lambda runs: len(runs) == len(eval_df_b),\n"
        "        max_attempts=1,\n"
        "        llm=[kbench.llm],\n"
        "        evaluation_data=eval_df_b,\n"
        "        n_jobs=3,\n"
        "    )\n"
        "\n"
        "fb_eval_df = fb_runs.as_dataframe()\n"
        "fb_utilities = [r[\"utility\"] for r in fb_eval_df[\"result\"]]\n"
        "fb_uwaa = _compute_uwaa(fb_utilities)\n"
        "\n"
        "# Action distribution\n"
        "fb_decisions = [r[\"decision\"] for r in fb_eval_df[\"result\"]]\n"
        "fb_gold_actions = [r[\"gold_action\"] for r in fb_eval_df[\"result\"]]\n"
        "\n"
        "print(f\"\\n{'='*50}\")\n"
        "print(f\"Family B: Selective Abstention Results\")\n"
        "print(f\"{'='*50}\")\n"
        "print(f\"Items evaluated: {len(fb_utilities)}\")\n"
        "print(f\"UWAA score: {fb_uwaa:.4f}\")\n"
        "print(f\"Mean utility: {sum(fb_utilities)/len(fb_utilities):+.4f}\")\n"
        "print(f\"Action distribution: {dict((a, fb_decisions.count(a)) for a in ['answer','clarify','verify','abstain'])}\")\n"
        "print(f\"{'='*50}\")"
    )
    cell14 = make_code_cell(split_source(cell14_source))

    # Cell 15: Composite Score
    cell15_source = (
        "# Cell 15 — Composite Score (Calibration + Abstention)\n"
        "\n"
        "try:\n"
        "    from metajudge.scoring.composite_score import compute_composite_score\n"
        "    composite = compute_composite_score({\n"
        "        \"calibration\": headline_score.result if hasattr(headline_score, 'result') else headline_score,\n"
        "        \"abstention_verification\": fb_uwaa,\n"
        "    })\n"
        "    print(f\"Composite score (package): {composite:.4f}\")\n"
        "except ImportError:\n"
        "    # Inline fallback: calibration=0.60, abstention=0.40 (normalized from 0.30/0.20)\n"
        "    cal_score = headline_score.result if hasattr(headline_score, 'result') else headline_score\n"
        "    composite = 0.60 * cal_score + 0.40 * fb_uwaa\n"
        "    print(f\"Composite score (inline): {composite:.4f}\")\n"
        "\n"
        "print(f\"\\n{'='*50}\")\n"
        "print(f\"MetaJudge Combined Results\")\n"
        "print(f\"{'='*50}\")\n"
        "cal_val = headline_score.result if hasattr(headline_score, 'result') else headline_score\n"
        "print(f\"  Family A (Calibration):  {cal_val:.4f}\")\n"
        "print(f\"  Family B (Abstention):   {fb_uwaa:.4f}\")\n"
        "print(f\"  Composite:               {composite:.4f}\")\n"
        "print(f\"{'='*50}\")"
    )
    cell15 = make_code_cell(split_source(cell15_source))

    # Save the %choose cell (currently cell 9)
    choose_cell = cells[9]

    # Build new cell list:
    # Cells 0-8: existing (cell 8 updated with families)
    # Cell 9: markdown separator (new)
    # Cell 10: Family B setup (new)
    # Cell 11: Family B schema (new)
    # Cell 12: Family B self-tests (new)
    # Cell 13: Family B task (new)
    # Cell 14: Family B batch (new)
    # Cell 15: Composite score (new)
    # Cell 16: %choose (moved from cell 9)

    new_cells = cells[:9]  # Keep cells 0-8
    new_cells.append(cell9_md)   # Cell 9: separator
    new_cells.append(cell10)     # Cell 10: setup
    new_cells.append(cell11)     # Cell 11: schema
    new_cells.append(cell12)     # Cell 12: self-tests
    new_cells.append(cell13)     # Cell 13: task
    new_cells.append(cell14)     # Cell 14: batch
    new_cells.append(cell15)     # Cell 15: composite
    new_cells.append(choose_cell)  # Cell 16: %choose

    nb["cells"] = new_cells

    # Write notebook
    with open(NOTEBOOK_PATH, "w") as f:
        json.dump(nb, f, indent=1)

    print(f"Notebook updated: {len(new_cells)} cells")
    for i, cell in enumerate(new_cells):
        src = "".join(cell["source"][:1]).strip()[:80]
        print(f"  Cell {i} ({cell['cell_type']}): {src}")


if __name__ == "__main__":
    main()
