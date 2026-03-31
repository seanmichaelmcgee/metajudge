"""
MetaJudge Family C v0.6.2: Gemini Re-run with Higher max_tokens
================================================================
Re-runs ONLY Gemini 2.5 Pro with max_tokens=4096 to fix truncation.
The original sweep used max_tokens=400, but Gemini is a reasoning model
that consumes part of the token budget for chain-of-thought reasoning,
leaving almost no tokens for visible output.

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/sweep_gemini_rerun_v062.py
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
from scripts.regrade_sweep_v062 import grade_item_v2, classify_transition

# ── Configuration ─────────────────────────────────────────────────

MODEL = "google/gemini-2.5-pro"
TEMPERATURE = 0.3
MAX_TOKENS = 4096  # was 400; Gemini needs much more due to reasoning overhead
DELAY_BETWEEN_CALLS = 2.0  # seconds

OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c"

# ── T2 prompts (same as original sweep) ──────────────────────────

C1_T2_PROMPT = (
    "Please reconsider your answer carefully. "
    "Take a moment to verify your reasoning step by step. "
    "What is your final answer?"
)

C2_T2_TEMPLATE = (
    "Here is some additional information: {evidence}\n\n"
    "Given this, please reconsider your previous answer. "
    "What is your final answer?"
)

# ── Data loading ─────────────────────────────────────────────────

def load_clean_items() -> list[dict]:
    """Load all clean Family C items from C1 and C2 candidate JSONs."""
    c1_path = REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json"
    c2_path = REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json"

    items = []
    for path in [c1_path, c2_path]:
        with open(path) as f:
            raw = json.load(f)
        clean = [i for i in raw if i.get("draft_status") == "clean"]
        items.extend(clean)
    return items

# ── API calling ──────────────────────────────────────────────────

def call_model(messages: list[dict]) -> dict:
    return query(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=120,
        retries=2,
        json_mode=False,
    )


def run_item(item: dict) -> dict:
    """Run T1 + T2 for one item."""
    subfamily = item["subfamily"]
    question = item["turn1_prompt"]

    # T1
    t1_messages = [
        {"role": "user", "content": question + "\n\nGive your answer concisely."}
    ]
    t1_result = call_model(t1_messages)
    t1_response = t1_result.get("response_text") or ""
    t1_error = t1_result.get("error")

    time.sleep(DELAY_BETWEEN_CALLS)

    # T2
    if subfamily.upper() == "C1":
        t2_user_msg = C1_T2_PROMPT
    else:
        evidence = item.get("evidence_snippet", "")
        t2_user_msg = C2_T2_TEMPLATE.format(evidence=evidence)

    t2_messages = [
        {"role": "user", "content": question + "\n\nGive your answer concisely."},
        {"role": "assistant", "content": t1_response},
        {"role": "user", "content": t2_user_msg},
    ]
    t2_result = call_model(t2_messages)
    t2_response = t2_result.get("response_text") or ""
    t2_error = t2_result.get("error")

    # Grade with improved grader
    t1_correct = grade_item_v2(t1_response, item) if t1_response else False
    t2_correct = grade_item_v2(t2_response, item) if t2_response else False
    transition = classify_transition(t1_correct, t2_correct)

    return {
        "item_id": item["item_id"],
        "family": item.get("family", "C"),
        "subfamily": item["subfamily"],
        "stratum": item.get("stratum", ""),
        "category": item.get("category", ""),
        "grading_rule": item["grading_rule"],
        "gold_answer": item["gold_answer"],
        "model": MODEL,
        "t1_response": t1_response,
        "t1_correct": t1_correct,
        "t1_error": t1_error,
        "t1_latency_ms": t1_result.get("latency_ms"),
        "t2_response": t2_response,
        "t2_correct": t2_correct,
        "t2_error": t2_error,
        "t2_latency_ms": t2_result.get("latency_ms"),
        "transition": transition,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "max_tokens_used": MAX_TOKENS,
    }

# ── Output ───────────────────────────────────────────────────────

def save_jsonl(results: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")


def save_summary_csv(results: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "item_id", "subfamily", "stratum", "grading_rule", "gold_answer",
        "model", "t1_correct", "t2_correct", "transition",
        "t1_latency_ms", "t2_latency_ms",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

# ── Main ─────────────────────────────────────────────────────────

def main():
    items = load_clean_items()
    print(f"Loaded {len(items)} clean items")
    print(f"Model: {MODEL}")
    print(f"max_tokens: {MAX_TOKENS} (was 400 in original sweep)")
    print(f"Expected API calls: {len(items) * 2}")
    print()

    results = []
    errors = 0
    for i, item in enumerate(items):
        print(f"[{i+1}/{len(items)}] {item['item_id']} ({item['subfamily']}) ...", end=" ", flush=True)
        try:
            r = run_item(item)
            results.append(r)
            t2_len = len(r["t2_response"])
            print(f"{r['transition']} (T2: {t2_len} chars)")
            if r["t1_error"] or r["t2_error"]:
                errors += 1
        except Exception as e:
            print(f"EXCEPTION: {e}")
            errors += 1

        time.sleep(DELAY_BETWEEN_CALLS)

    # Save outputs
    jsonl_path = OUTPUT_DIR / "sweep_raw_gemini-2-5-pro-rerun.jsonl"
    csv_path = OUTPUT_DIR / "sweep_summary_gemini-2-5-pro-rerun.csv"
    save_jsonl(results, jsonl_path)
    save_summary_csv(results, csv_path)

    # Print summary
    from collections import Counter
    trans = Counter(r["transition"] for r in results)
    n = len(results)
    t1_acc = sum(1 for r in results if r["t1_correct"]) / n if n else 0
    t2_acc = sum(1 for r in results if r["t2_correct"]) / n if n else 0
    t2_lens = [len(r["t2_response"]) for r in results]

    print(f"\n{'='*60}")
    print(f"Gemini Re-run Results (max_tokens={MAX_TOKENS})")
    print(f"{'='*60}")
    print(f"Items: {n}, Errors: {errors}")
    print(f"T1 accuracy: {t1_acc:.1%}")
    print(f"T2 accuracy: {t2_acc:.1%}")
    print(f"Transitions: {dict(trans)}")
    print(f"T2 response lengths: min={min(t2_lens)}, max={max(t2_lens)}, "
          f"median={sorted(t2_lens)[len(t2_lens)//2]}")
    print(f"\nSaved: {jsonl_path}")
    print(f"Saved: {csv_path}")

    # Compare with original
    print(f"\n--- Comparison with original (max_tokens=400) ---")
    orig_path = OUTPUT_DIR / "sweep_raw_gemini-2-5-pro.jsonl"
    if orig_path.exists():
        orig = []
        with open(orig_path) as f:
            for line in f:
                orig.append(json.loads(line))
        orig_trans = Counter(r["transition"] for r in orig)
        print(f"Original transitions: {dict(orig_trans)}")
        print(f"Rerun transitions:    {dict(trans)}")
        print(f"Original R→W: {orig_trans.get('right_to_wrong', 0)}")
        print(f"Rerun R→W:    {trans.get('right_to_wrong', 0)}")


if __name__ == "__main__":
    main()
