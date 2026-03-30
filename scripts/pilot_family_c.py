"""
MetaJudge-AGI: Family C Pilot Runner
=====================================
Runs all 35 Family C items (15 C1 + 20 C2) against a specified model
via OpenRouter, producing raw JSONL audit rows and per-item summary CSVs.

Usage:
    PYTHONPATH=. python scripts/pilot_family_c.py --model deepseek-chat
    PYTHONPATH=. python scripts/pilot_family_c.py --model grok-3-mini
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Ensure repo root is on path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from metajudge.tasks.self_correction_v2 import run_family_c_batch
from scripts.openrouter.client import query


def load_items():
    """Load all Family C candidate items (C1 + C2)."""
    c1_path = REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json"
    c2_path = REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json"

    with open(c1_path) as f:
        c1_items = json.load(f)
    with open(c2_path) as f:
        c2_items = json.load(f)

    print(f"Loaded {len(c1_items)} C1 items and {len(c2_items)} C2 items")
    return c1_items + c2_items


def save_jsonl(rows, path):
    """Save audit rows as JSONL."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row, default=str) + "\n")
    print(f"  Saved {len(rows)} rows to {path}")


def save_csv(rows, path):
    """Save per-item summary CSV."""
    columns = [
        "item_id", "subfamily", "stratum", "normative_action",
        "correct_1", "correct_2", "transition", "revised",
        "conf_1", "conf_2", "base_score", "scaled_score", "model",
    ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {len(rows)} rows to {path}")


def run_pilot(model: str):
    """Run the full Family C pilot for a single model."""
    items = load_items()
    model_safe = model.replace("/", "-")

    output_dir = REPO_ROOT / "outputs" / "family_c"
    jsonl_path = output_dir / f"pilot_raw_{model_safe}.jsonl"
    csv_path = output_dir / f"pilot_summary_{model_safe}.csv"

    print(f"\n=== Running Family C Pilot: {model} ===")
    print(f"  Items: {len(items)}")
    print(f"  API calls expected: {len(items) * 2} (2 turns per item)")

    start = time.monotonic()
    results = run_family_c_batch(items, query, model, json_mode=True)
    elapsed = time.monotonic() - start

    # Count outcomes
    parse_success = sum(1 for r in results if r.get("transition") != "")
    parse_fail = len(results) - parse_success
    transitions = {}
    for r in results:
        t = r.get("transition", "unknown")
        transitions[t] = transitions.get(t, 0) + 1

    print(f"\n  Completed in {elapsed:.1f}s")
    print(f"  Parse success: {parse_success}/{len(results)}")
    if parse_fail > 0:
        print(f"  Parse failures: {parse_fail}")
    print(f"  Transition distribution: {transitions}")

    # Compute mean scaled score
    scores = [r["scaled_score"] for r in results]
    mean_score = sum(scores) / len(scores) if scores else 0
    print(f"  Mean scaled score: {mean_score:.4f}")

    # Save outputs
    save_jsonl(results, jsonl_path)
    save_csv(results, csv_path)

    # Summary stats
    damage_count = transitions.get("damage", 0)
    revised_count = sum(1 for r in results if r.get("revised"))
    damage_rate = damage_count / revised_count if revised_count > 0 else 0
    revision_rate = revised_count / len(results) if results else 0

    print(f"\n  Summary:")
    print(f"    Items run: {len(results)}")
    print(f"    Parse success: {parse_success}/{len(results)}")
    print(f"    Mean scaled score: {mean_score:.4f}")
    print(f"    Damage rate (of revisions): {damage_rate:.2%}")
    print(f"    Revision rate: {revision_rate:.2%}")
    print(f"    Transitions: {transitions}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Family C Pilot Runner")
    parser.add_argument("--model", required=True, help="Model short name (e.g. deepseek-chat, grok-3-mini)")
    args = parser.parse_args()
    run_pilot(args.model)
