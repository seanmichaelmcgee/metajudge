#!/usr/bin/env python3
"""
Extract all wrong-graded items from v3.2 benchmark results for LLM audit.

Usage:
    python scripts/extract_wrong_for_llm_audit.py <results_dir> [<results_dir> ...]

Output: CSV data for each family, ready to paste into the LLM audit prompt.
"""

import csv
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "kaggle-dataset-v3" / "adjudication_registry.json"
SOURCE_A = REPO_ROOT / "kaggle-dataset-v3" / "metajudge_benchmark_v1.json"
SOURCE_B = REPO_ROOT / "kaggle-dataset-v3" / "family_b_pilot_v2.json"
SOURCE_C = REPO_ROOT / "kaggle-dataset-v3" / "family_c_items.json"


def load_source(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return {it["item_id"]: it for it in data}
    return data


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <results_dir> [<results_dir> ...]")
        sys.exit(1)

    results_dirs = sys.argv[1:]

    with open(REGISTRY_PATH) as f:
        registry = {r["item_id"]: r for r in json.load(f)}

    items_a = load_source(SOURCE_A)
    items_b = load_source(SOURCE_B)
    items_c = load_source(SOURCE_C)

    # --- Family A ---
    print("=== FAMILY A — Calibration (items marked wrong) ===")
    print("model,item_id,question,gold_answer,model_answer,confidence,grading_rule,aliases")
    a_count = 0
    for rdir in results_dirs:
        model = os.path.basename(rdir.rstrip("/"))
        path = os.path.join(rdir, "calibration_item_audit.csv")
        if not os.path.exists(path):
            continue
        for row in csv.DictReader(open(path)):
            if row["is_correct"] == "False":
                iid = row["item_id"]
                src = items_a.get(iid, {})
                reg = registry.get(iid, {})
                q = src.get("question", "")[:200].replace('"', "'")
                gold = row.get("gold_answer", reg.get("gold_answer", "?")).replace('"', "'")
                ans = row["model_answer"][:150].replace('"', "'")
                aliases = "|".join(reg.get("accepted_forms", []))[:100]
                rule = reg.get("grader_rule", "?")
                print(f'{model},"{iid}","{q}","{gold}","{ans}",{row["confidence"]},{rule},"{aliases}"')
                a_count += 1

    # --- Family B ---
    print(f"\n=== FAMILY B — Abstention (decision=answer, marked wrong) ===")
    print("model,item_id,question,gold_answer,gold_action,model_answer,grading_rule,aliases")
    b_count = 0
    for rdir in results_dirs:
        model = os.path.basename(rdir.rstrip("/"))
        path = os.path.join(rdir, "family_b_item_audit.csv")
        if not os.path.exists(path):
            continue
        for row in csv.DictReader(open(path)):
            if row["model_decision"] == "answer" and row["is_correct"] == "False":
                iid = row["item_id"]
                src = items_b.get(iid, {})
                reg = registry.get(iid, {})
                q = src.get("question", "")[:200].replace('"', "'")
                gold = row.get("gold_answer", "?").replace('"', "'")
                ans = row["model_answer"][:150].replace('"', "'")
                aliases = "|".join(reg.get("accepted_forms", []))[:100]
                rule = reg.get("grader_rule", "?")
                gold_action = row.get("gold_action", "?")
                print(f'{model},"{iid}","{q}","{gold}",{gold_action},"{ans}",{rule},"{aliases}"')
                b_count += 1

    # --- Family C ---
    print(f"\n=== FAMILY C — Self-Correction (T1 or T2 marked wrong) ===")
    print("model,item_id,turn,question,gold_answer,model_answer,grading_rule,aliases")
    c_count = 0
    for rdir in results_dirs:
        model = os.path.basename(rdir.rstrip("/"))
        path = os.path.join(rdir, "family_c_item_audit.csv")
        if not os.path.exists(path):
            continue
        for row in csv.DictReader(open(path)):
            iid = row["item_id"]
            src = items_c.get(iid, {})
            reg = registry.get(iid, {})
            q = src.get("question", "")[:200].replace('"', "'")
            gold = reg.get("gold_answer", "?").replace('"', "'")
            aliases = "|".join(reg.get("accepted_forms", []))[:100]
            rule = reg.get("grader_rule", "?")

            if row["t1_correct"] == "False":
                ans = row["t1_answer"][:150].replace('"', "'")
                print(f'{model},"{iid}",T1,"{q}","{gold}","{ans}",{rule},"{aliases}"')
                c_count += 1
            if row["t2_correct"] == "False":
                ans = row["t2_answer"][:150].replace('"', "'")
                print(f'{model},"{iid}",T2,"{q}","{gold}","{ans}",{rule},"{aliases}"')
                c_count += 1

    # Summary
    total = a_count + b_count + c_count
    print(f"\n=== SUMMARY ===")
    print(f"Family A wrong: {a_count}")
    print(f"Family B answer+wrong: {b_count}")
    print(f"Family C T1/T2 wrong: {c_count}")
    print(f"TOTAL items for review: {total}")


if __name__ == "__main__":
    main()
