#!/usr/bin/env python3
"""Generate a per-model .docx audit report from MetaJudge v5.1 notebook outputs.

Usage:
    python scripts/generate_audit_docx.py \
      --task calibration \
      --audit-csv /path/to/calibration_item_audit_flash2.5_v5.1.csv \
      --responses-json /path/to/calibration_full_responses_flash2.5_v5.1.json \
      --items-json /path/to/metajudge_benchmark_v1.json \
      --registry-json /path/to/adjudication_registry.json \
      --output MetaJudge_Calibration_Flash2.5.docx \
      [--run-json /path/to/run.json] \
      [--justifications-md /path/to/metajudge_v51_gold_answer_justifications.md]

Supports all 4 task types: calibration, abstention, sc_c1, sc_c2.
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path


# ── CLI ───────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Generate MetaJudge v5.1 audit .docx")
    p.add_argument("--task", required=True,
                   choices=["calibration", "abstention", "sc_c1", "sc_c2"],
                   help="Task type")
    p.add_argument("--audit-csv", required=True, help="Item-level audit CSV")
    p.add_argument("--responses-json", required=True, help="Full responses JSON")
    p.add_argument("--items-json", required=True, help="Benchmark items JSON")
    p.add_argument("--registry-json", required=True, help="Adjudication registry JSON")
    p.add_argument("--output", required=True, help="Output .docx path")
    p.add_argument("--run-json", default=None, help="SDK run.json (optional, for runtime/cost)")
    p.add_argument("--justifications-md", default=None,
                   help="Gold answer justifications markdown (optional)")
    return p.parse_args()


# ── Data loading ──────────────────────────────────────────────────────────

def load_audit_csv(path):
    """Load audit CSV into list of dicts."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_json(path):
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def load_justifications(path):
    """Parse justifications markdown into dict keyed by item_id."""
    if path is None:
        return {}
    with open(path) as f:
        content = f.read()
    pattern = r"#### (\S+)\n.*?\*\*Justification:\*\* (.+?)(?=\n\n#### |\n\n### |\n\n## |\n\n---|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    return {item_id: text.strip() for item_id, text in matches}


def load_run_metadata(path):
    """Extract model name, timestamps, and token/cost data from run.json."""
    if path is None:
        return None
    data = load_json(path)
    meta = {
        "model": "unknown",
        "start_time": None,
        "end_time": None,
        "input_tokens": 0,
        "output_tokens": 0,
        "input_cost": 0.0,
        "output_cost": 0.0,
    }
    # Model name
    mv = data.get("modelVersion", {})
    meta["model"] = mv.get("slug", data.get("model", "unknown"))
    # Timestamps
    meta["start_time"] = data.get("startTime")
    meta["end_time"] = data.get("endTime")
    # Token/cost aggregation across conversations
    for conv in data.get("conversations", []):
        for key in ("input_tokens", "output_tokens"):
            meta[key] += conv.get(key, 0)
        for key in ("input_tokens_cost", "output_tokens_cost"):
            target = "input_cost" if "input" in key else "output_cost"
            meta[target] += conv.get(key, 0.0)
    return meta


# ── Data merging ──────────────────────────────────────────────────────────

def build_items_lookup(items_json, task):
    """Build item_id → item dict, filtering by subfamily for C1/C2."""
    items = items_json if isinstance(items_json, list) else []
    if task == "sc_c1":
        items = [it for it in items if it.get("subfamily") == "C1"]
    elif task == "sc_c2":
        items = [it for it in items if it.get("subfamily") == "C2"]
    return {it["item_id"]: it for it in items}


def build_registry_lookup(registry_json):
    """Build item_id → registry entry dict."""
    if isinstance(registry_json, list):
        return {entry["item_id"]: entry for entry in registry_json}
    elif isinstance(registry_json, dict):
        return registry_json
    return {}


def extract_responses_lookup(responses_json, task):
    """Build item_id → full response dict from responses JSON.

    Handles both single-run ({"responses": [...]}) and
    dual-run ({"run_1": [...], "run_2": [...]}) formats.
    Returns (run1_lookup, run2_lookup_or_None).
    """
    # Strip metadata wrapper if present
    if "metadata" in responses_json:
        data = {k: v for k, v in responses_json.items() if k != "metadata"}
    else:
        data = responses_json

    run1 = data.get("run_1", data.get("responses", []))
    run2 = data.get("run_2", None)

    r1_lookup = {r["item_id"]: r for r in run1} if run1 else {}
    r2_lookup = {r["item_id"]: r for r in run2} if run2 else None

    return r1_lookup, r2_lookup


def merge_item_data(audit_rows, items_lookup, registry_lookup,
                    responses_r1, justifications):
    """Merge all data sources into a list of enriched item dicts."""
    merged = []
    for row in audit_rows:
        iid = row["item_id"]
        item = items_lookup.get(iid, {})
        reg = registry_lookup.get(iid, {})
        resp = responses_r1.get(iid, {})

        entry = {**row}  # Start with audit CSV fields
        # Add item metadata
        entry["question"] = item.get("question", item.get("turn1_prompt", ""))
        entry["gold_answer_full"] = item.get("gold_answer", row.get("gold_answer", ""))
        entry["category"] = item.get("category", item.get("mechanism_primary", ""))
        entry["mechanism"] = item.get("mechanism", item.get("mechanism_primary", ""))
        entry["difficulty"] = item.get("difficulty", "")
        entry["grading_rule"] = item.get("grading_rule", reg.get("rule", ""))
        entry["subfamily"] = item.get("subfamily", "")
        entry["normative_t2_action"] = item.get("normative_t2_action", "")
        entry["stratum"] = item.get("stratum", "")
        entry["evidence_snippet"] = item.get("evidence_snippet", "")
        # Registry accepted forms
        entry["accepted_forms"] = reg.get("aliases", reg.get("accepted_forms", []))
        # Justification
        entry["justification"] = justifications.get(iid, "")
        # Full response text (prefer over truncated CSV)
        if resp:
            entry["full_model_answer"] = resp.get("model_answer",
                                                   resp.get("t1_answer", ""))
            entry["full_t1_answer"] = resp.get("t1_answer", "")
            entry["full_t2_answer"] = resp.get("t2_answer", "")
        # Gold action (abstention)
        if "gold_action" not in entry:
            entry["gold_action"] = item.get("gold_action", "")
        # Acceptable actions (abstention)
        entry["acceptable_actions"] = item.get("acceptable_actions", [])
        entry["is_false_presupposition"] = item.get("is_false_presupposition", False)

        merged.append(entry)

    return sorted(merged, key=lambda x: x["item_id"])


# ── Report metadata ──────────────────────────────────────────────────────

TASK_DISPLAY = {
    "calibration": "Confidence Calibration",
    "abstention": "Selective Abstention",
    "sc_c1": "Intrinsic Self-Correction (C1)",
    "sc_c2": "Evidence-Assisted Self-Correction (C2)",
}


def infer_model_name(run_meta, responses_json):
    """Get model name from run.json or responses JSON metadata."""
    if run_meta and run_meta["model"] != "unknown":
        return run_meta["model"]
    if isinstance(responses_json, dict) and "metadata" in responses_json:
        return responses_json["metadata"].get("model", "unknown")
    return "unknown"


# ── Main (scaffold — docx generation added in later phases) ──────────────

def main():
    args = parse_args()

    # Load all data
    print(f"Loading data for task: {args.task}")
    audit_rows = load_audit_csv(args.audit_csv)
    responses_json = load_json(args.responses_json)
    items_json = load_json(args.items_json)
    registry_json = load_json(args.registry_json)
    justifications = load_justifications(args.justifications_md)
    run_meta = load_run_metadata(args.run_json)

    # Build lookups
    items_lookup = build_items_lookup(items_json, args.task)
    registry_lookup = build_registry_lookup(registry_json)
    responses_r1, responses_r2 = extract_responses_lookup(responses_json, args.task)

    # Merge
    merged = merge_item_data(audit_rows, items_lookup, registry_lookup,
                             responses_r1, justifications)

    model_name = infer_model_name(run_meta, responses_json)

    print(f"  Model: {model_name}")
    print(f"  Items: {len(merged)}")
    print(f"  Justifications matched: {sum(1 for m in merged if m['justification'])}/{len(merged)}")
    print(f"  Run 2 data: {'yes' if responses_r2 else 'no'}")

    # TODO: Generate docx (Phases B-D)
    print(f"\n[Scaffold only — docx generation not yet implemented]")
    print(f"Output would be: {args.output}")


if __name__ == "__main__":
    main()
