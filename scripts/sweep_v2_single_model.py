"""
Run sweep_v2 for a single model (for parallel execution).

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/sweep_v2_single_model.py "anthropic/claude-sonnet-4.6"
"""
import sys
import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.sweep_v2 import (
    load_clean_items, run_item, save_jsonl, save_summary_csv,
    B0_DIAGNOSTIC_IDS, model_slug, OUTPUT_DIR
)


def run_single_model(model: str):
    items = load_clean_items()
    print(f"Running {model} on {len(items)} items...")

    results = []
    errors = 0
    for i, item in enumerate(items):
        run_b0 = item["item_id"] in B0_DIAGNOSTIC_IDS
        tag = " [+B0]" if run_b0 else ""
        print(f"  [{i+1}/{len(items)}] {item['item_id']}{tag} ...", end=" ", flush=True)
        try:
            r = run_item(model, item, run_b0=run_b0)
            results.append(r)
            status = r["transition"]
            if r.get("t1_error") or r.get("t2_error"):
                errors += 1
                status += " (API error)"
            print(status)
        except Exception as e:
            print(f"EXCEPTION: {e}")
            errors += 1
        time.sleep(0.3)

    slug = model_slug(model)
    jsonl_path = OUTPUT_DIR / "sweep_v2" / f"sweep_v2_raw_{slug}.jsonl"
    csv_path = OUTPUT_DIR / "sweep_v2" / f"sweep_v2_summary_{slug}.csv"
    save_jsonl(results, jsonl_path)
    save_summary_csv(results, csv_path)

    # Transition summary
    transitions = {}
    for r in results:
        t = r["transition"]
        transitions[t] = transitions.get(t, 0) + 1

    t1_correct = sum(1 for r in results if r["t1_correct"])
    t2_correct = sum(1 for r in results if r["t2_correct"])

    print(f"\n  Results for {model}:")
    print(f"    Items: {len(results)}, Errors: {errors}")
    print(f"    T1 accuracy: {t1_correct}/{len(results)} ({100*t1_correct/len(results):.1f}%)")
    print(f"    T2 accuracy: {t2_correct}/{len(results)} ({100*t2_correct/len(results):.1f}%)")
    print(f"    Transitions: {transitions}")
    print(f"    Saved: {jsonl_path}")

    # Save summary to workspace for easy collection
    summary = {
        "model": model,
        "total_items": len(results),
        "errors": errors,
        "t1_accuracy": t1_correct / len(results) if results else 0,
        "t2_accuracy": t2_correct / len(results) if results else 0,
        "transitions": transitions,
        "jsonl_path": str(jsonl_path),
    }
    summary_path = Path(f"/home/user/workspace/sweep_v2_{slug}_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"    Summary: {summary_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/sweep_v2_single_model.py MODEL_ID")
        sys.exit(1)
    run_single_model(sys.argv[1])
