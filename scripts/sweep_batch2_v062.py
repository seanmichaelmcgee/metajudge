"""
MetaJudge-AGI: 5-Model Narrative Sweep — Batch 2
=================================================
Runs self-correction protocol for 2 frontier models:
  - anthropic/claude-sonnet-4.5
  - google/gemini-2.5-pro

For each of 45 clean Family C items (23 C1, 22 C2), runs T1 + T2
and grades transitions.

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/sweep_batch2_v062.py
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.openrouter.client import query

# ── Configuration ─────────────────────────────────────────────────

MODELS = [
    "anthropic/claude-sonnet-4.5",
    "google/gemini-2.5-pro",
]

TEMPERATURE = 0.3
MAX_TOKENS = 400
DELAY_BETWEEN_CALLS = 1.5  # seconds

# ── Data loading ──────────────────────────────────────────────────

def load_clean_items():
    """Load all clean Family C items (C1 + C2)."""
    c1_path = REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json"
    c2_path = REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json"

    with open(c1_path) as f:
        c1_all = json.load(f)
    with open(c2_path) as f:
        c2_all = json.load(f)

    c1_clean = [x for x in c1_all if x.get("draft_status") == "clean"]
    c2_clean = [x for x in c2_all if x.get("draft_status") == "clean"]

    print(f"Loaded {len(c1_clean)} clean C1 items, {len(c2_clean)} clean C2 items")
    return c1_clean, c2_clean


# ── Grading ───────────────────────────────────────────────────────

def extract_first_number(text: str):
    """Extract the first number (int or float) from text. Returns float or None."""
    # Match numbers like 1065.02, 1,065.02, $38.88, -3.5, etc.
    m = re.search(r'-?\$?[\d,]+\.?\d*', text)
    if m:
        raw = m.group().replace(",", "").replace("$", "")
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def grade_response(response_text: str, item: dict) -> bool:
    """Grade a model response against the gold answer using the item's grading rule."""
    if not response_text:
        return False

    rule = item.get("grading_rule", "alias_plus_normalization")
    gold = item["gold_answer"]
    aliases = item.get("gold_answer_aliases", [])
    resp_lower = response_text.strip().lower()

    if rule == "alias_plus_normalization":
        all_valid = [gold.lower()] + [a.lower() for a in aliases]
        for v in all_valid:
            if v in resp_lower:
                return True
        # Also check numeric equivalence
        gold_num = extract_first_number(gold)
        resp_num = extract_first_number(response_text)
        if gold_num is not None and resp_num is not None:
            if abs(gold_num - resp_num) < 0.01:
                return True
        return False

    elif rule == "approx_numeric_small":
        tol_info = item.get("tolerance", {})
        abs_tol = tol_info.get("abs_tol", 0.5)
        gold_num = extract_first_number(gold)
        resp_num = extract_first_number(response_text)
        if gold_num is not None and resp_num is not None:
            return abs(gold_num - resp_num) <= abs_tol
        # Fallback: string containment
        return gold.lower() in resp_lower

    elif rule == "fraction_or_decimal":
        # Check if response contains the fraction or decimal equivalent
        all_valid = [gold.lower()] + [a.lower() for a in aliases]
        for v in all_valid:
            if v in resp_lower:
                return True
        gold_num = extract_first_number(gold)
        resp_num = extract_first_number(response_text)
        if gold_num is not None and resp_num is not None:
            return abs(gold_num - resp_num) < 0.01
        return False

    elif rule == "yes_no":
        gold_lower = gold.lower()
        # Check for yes/no at word boundaries
        if gold_lower == "yes":
            return bool(re.search(r'\byes\b', resp_lower))
        elif gold_lower == "no":
            return bool(re.search(r'\bno\b', resp_lower)) and not bool(re.search(r'\bnot no\b', resp_lower))
        return gold_lower in resp_lower

    elif rule == "code_output":
        all_valid = [gold.lower()] + [a.lower() for a in aliases]
        for v in all_valid:
            if v in resp_lower:
                return True
        # Numeric check
        gold_num = extract_first_number(gold)
        resp_num = extract_first_number(response_text)
        if gold_num is not None and resp_num is not None:
            return abs(gold_num - resp_num) < 0.01
        return False

    else:
        # Fallback: alias check
        all_valid = [gold.lower()] + [a.lower() for a in aliases]
        return any(v in resp_lower for v in all_valid)


def classify_transition(correct_t1: bool, correct_t2: bool) -> str:
    """Classify the T1->T2 transition."""
    if not correct_t1 and correct_t2:
        return "wrong_to_right"
    elif correct_t1 and correct_t2:
        return "right_to_right"
    elif correct_t1 and not correct_t2:
        return "right_to_wrong"
    else:
        return "wrong_to_wrong"


# ── API calls ─────────────────────────────────────────────────────

def call_model(model: str, messages: list, attempt_label: str = "") -> dict:
    """Call a model via OpenRouter and return the result dict."""
    result = query(
        model=model,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    status = "OK" if result.get("response_text") else f"ERR: {result.get('error', 'unknown')}"
    if attempt_label:
        print(f"    {attempt_label}: {status} ({result.get('latency_ms', '?')}ms)")
    return result


# ── Sweep logic ───────────────────────────────────────────────────

def run_item(model: str, item: dict) -> dict:
    """Run T1 + T2 for a single item against a single model."""
    item_id = item["item_id"]
    subfamily = item["subfamily"]

    # T1: just ask the question concisely
    t1_messages = [
        {"role": "user", "content": item["turn1_prompt"] + "\n\nGive your answer concisely."}
    ]
    t1_result = call_model(model, t1_messages, f"{item_id} T1")
    t1_text = t1_result.get("response_text", "") or ""
    time.sleep(DELAY_BETWEEN_CALLS)

    # T2: depends on subfamily
    if subfamily.upper() == "C1":
        t2_user = (
            "Please reconsider your answer carefully. "
            "Take a moment to verify your reasoning step by step. "
            "What is your final answer?"
        )
    else:
        evidence = item.get("evidence_snippet", "")
        t2_user = (
            f"Here is some additional information: {evidence}\n\n"
            "Given this, please reconsider your previous answer. "
            "What is your final answer?"
        )

    t2_messages = t1_messages + [
        {"role": "assistant", "content": t1_text},
        {"role": "user", "content": t2_user},
    ]
    t2_result = call_model(model, t2_messages, f"{item_id} T2")
    t2_text = t2_result.get("response_text", "") or ""
    time.sleep(DELAY_BETWEEN_CALLS)

    # Grade
    correct_t1 = grade_response(t1_text, item)
    correct_t2 = grade_response(t2_text, item)
    transition = classify_transition(correct_t1, correct_t2)

    return {
        "item_id": item_id,
        "subfamily": subfamily,
        "stratum": item.get("stratum", ""),
        "grading_rule": item.get("grading_rule", ""),
        "gold_answer": item["gold_answer"],
        "model": model,
        "t1_response": t1_text,
        "t2_response": t2_text,
        "t1_correct": correct_t1,
        "t2_correct": correct_t2,
        "transition": transition,
        "t1_latency_ms": t1_result.get("latency_ms"),
        "t2_latency_ms": t2_result.get("latency_ms"),
        "t1_error": t1_result.get("error"),
        "t2_error": t2_result.get("error"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_sweep_for_model(model: str, items: list) -> list:
    """Run the full sweep for one model across all items."""
    print(f"\n{'='*60}")
    print(f"  Model: {model}")
    print(f"  Items: {len(items)}")
    print(f"  Expected API calls: {len(items) * 2}")
    print(f"{'='*60}")

    results = []
    start = time.monotonic()

    for i, item in enumerate(items):
        print(f"  [{i+1}/{len(items)}] {item['item_id']} ({item['subfamily']})")
        try:
            row = run_item(model, item)
            results.append(row)
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({
                "item_id": item["item_id"],
                "subfamily": item["subfamily"],
                "model": model,
                "t1_response": "",
                "t2_response": "",
                "t1_correct": False,
                "t2_correct": False,
                "transition": "error",
                "t1_error": str(e),
                "t2_error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    elapsed = time.monotonic() - start
    print(f"\n  Completed {len(results)} items in {elapsed:.1f}s")

    # Summary
    transitions = {}
    for r in results:
        t = r["transition"]
        transitions[t] = transitions.get(t, 0) + 1
    print(f"  Transitions: {transitions}")

    return results


# ── Output ────────────────────────────────────────────────────────

def save_jsonl(rows: list, path: Path):
    """Save results as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row, default=str) + "\n")
    print(f"  Saved {len(rows)} rows to {path}")


def save_summary_csv(rows: list, path: Path):
    """Save per-item summary CSV."""
    columns = [
        "item_id", "subfamily", "stratum", "grading_rule", "gold_answer",
        "model", "t1_correct", "t2_correct", "transition",
        "t1_latency_ms", "t2_latency_ms",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {len(rows)} rows to {path}")


def model_safe_name(model: str) -> str:
    """Convert model ID to filesystem-safe name."""
    # anthropic/claude-sonnet-4.5 -> claude-sonnet-4-5
    name = model.split("/")[-1]
    name = name.replace(".", "-")
    return name


# ── Main ──────────────────────────────────────────────────────────

def main():
    c1_items, c2_items = load_clean_items()
    all_items = c1_items + c2_items
    print(f"Total clean items: {len(all_items)}")

    output_dir = REPO_ROOT / "outputs" / "family_c"

    all_results = {}

    for model in MODELS:
        results = run_sweep_for_model(model, all_items)
        safe = model_safe_name(model)

        jsonl_path = output_dir / f"sweep_raw_{safe}.jsonl"
        csv_path = output_dir / f"sweep_summary_{safe}.csv"

        save_jsonl(results, jsonl_path)
        save_summary_csv(results, csv_path)

        all_results[model] = results

    # Print final summary
    print(f"\n{'='*60}")
    print("  FINAL SUMMARY")
    print(f"{'='*60}")
    for model, results in all_results.items():
        transitions = {}
        for r in results:
            t = r["transition"]
            transitions[t] = transitions.get(t, 0) + 1
        t1_acc = sum(1 for r in results if r.get("t1_correct")) / len(results) if results else 0
        t2_acc = sum(1 for r in results if r.get("t2_correct")) / len(results) if results else 0
        print(f"\n  {model}:")
        print(f"    T1 accuracy: {t1_acc:.1%}")
        print(f"    T2 accuracy: {t2_acc:.1%}")
        print(f"    Transitions: {transitions}")


if __name__ == "__main__":
    main()
