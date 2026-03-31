#!/usr/bin/env python3
"""
MetaJudge Family A & B Question-Level Result Validity Audit
============================================================
Independently re-adjudicates every recorded correctness flag and surfaces:
  - False negatives (recorded wrong but re-audit says correct)
  - False positives (recorded correct but re-audit says wrong)
  - Verbose-answer adjudication failures (Family B answer contains gold)
  - Gold answer validity concerns (all/most models wrong)
  - Gold answer version drift between CSVs and source data

Outputs:
  outputs/audit_family_ab_revalidation.csv   — per-row audit
  outputs/audit_family_ab_summary.md         — executive summary
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Ensure metajudge is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metajudge.scoring.grading_v2 import grade_item, load_registry

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
RESULTS_DIR = OUTPUT_DIR / "results-narrative-v0551"

BENCHMARK_V1 = DATA_DIR / "metajudge_benchmark_v1.json"
FAMILY_B_PILOT = DATA_DIR / "family_b_pilot_v2.json"
REGISTRY_PATH = DATA_DIR / "adjudication_registry.json"
CLEAN_MANIFEST = DATA_DIR / "clean_subset_manifest.json"

CAL_CSV_V0551 = RESULTS_DIR / "calibration_item_audit-v0.5.5.1.1.csv"
FB_CSV_V0551 = RESULTS_DIR / "family_b_item_audit-v0.5.5.1.1.csv"
CAL_CSV_V051 = OUTPUT_DIR / "calibration_item_audit_v0.5.1.csv"
FB_CSV_V051 = OUTPUT_DIR / "family_b_item_audit_v0.5.1.csv"

OUT_CSV = OUTPUT_DIR / "audit_family_ab_revalidation.csv"
OUT_MD = OUTPUT_DIR / "audit_family_ab_summary.md"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_source_items() -> dict[str, dict]:
    """Load full questions from benchmark JSON files (not truncated CSVs)."""
    items: dict[str, dict] = {}

    with open(BENCHMARK_V1) as f:
        for it in json.load(f):
            items[it["item_id"]] = it

    with open(FAMILY_B_PILOT) as f:
        for it in json.load(f):
            items[it["item_id"]] = it

    return items


def load_clean_manifest() -> dict:
    with open(CLEAN_MANIFEST) as f:
        return json.load(f)


def load_csv_rows(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Re-adjudication helpers
# ---------------------------------------------------------------------------

def contains_gold_check(model_answer: str, gold_answer: str) -> bool:
    """Check if gold answer appears as substring in model answer (case-insensitive)."""
    if not model_answer or not gold_answer:
        return False
    return gold_answer.strip().lower() in model_answer.strip().lower()


def reaudit_calibration_row(
    row: dict,
    registry: dict[str, dict],
    source_items: dict[str, dict],
) -> dict:
    """Re-adjudicate a single Family A calibration row."""
    item_id = row["item_id"]
    model_answer = row["model_answer"]
    recorded_correct = row["is_correct"] == "True"

    source = source_items.get(item_id, {})
    source_gold = source.get("gold_answer", "")
    csv_gold = row["gold_answer"]

    # Re-grade using current registry + grading_v2
    result = grade_item(item_id, model_answer, registry, gold_answer=source_gold)
    reaudit_correct = result.get("correct", False)

    # Build flags
    flags = []
    if csv_gold and source_gold and csv_gold.strip().lower() != str(source_gold).strip().lower():
        flags.append("GOLD_DRIFT")
    if recorded_correct and not reaudit_correct:
        flags.append("FLIP_TO_WRONG")
    if not recorded_correct and reaudit_correct:
        flags.append("FLIP_TO_CORRECT")

    return {
        "item_id": item_id,
        "family": "A",
        "model_name": row["model_name"],
        "question_full": source.get("question", row.get("question", "")),
        "gold_answer_source": str(source_gold),
        "gold_answer_csv": csv_gold,
        "model_answer": model_answer,
        "model_decision": "",
        "gold_action": "",
        "recorded_correct": str(recorded_correct),
        "reaudit_correct": str(reaudit_correct),
        "reaudit_method": result.get("method", ""),
        "reaudit_detail": result.get("match_detail", ""),
        "contains_gold": str(contains_gold_check(model_answer, str(source_gold))),
        "flag": "|".join(flags) if flags else "",
    }


def reaudit_family_b_row(
    row: dict,
    registry: dict[str, dict],
    source_items: dict[str, dict],
) -> dict:
    """Re-adjudicate a single Family B row."""
    item_id = row["item_id"]
    model_answer = row.get("model_answer", "")
    model_decision = row.get("model_decision", "")
    gold_action = row.get("gold_action", "")
    recorded_correct = row.get("is_correct", "False") == "True"

    source = source_items.get(item_id, {})
    source_gold = source.get("gold_answer", "")
    csv_gold = row.get("gold_answer", "")

    # Re-grade answer correctness (only meaningful when decision == "answer")
    reaudit_correct = False
    reaudit_method = ""
    reaudit_detail = ""

    if model_decision == "answer" and gold_action == "answer":
        result = grade_item(item_id, model_answer, registry, gold_answer=str(source_gold))
        reaudit_correct = result.get("correct", False)
        reaudit_method = result.get("method", "")
        reaudit_detail = result.get("match_detail", "")
    elif model_decision == "answer" and gold_action != "answer":
        # Model answered but gold says non-answer action — correctness is about the action, not the answer
        reaudit_correct = False
        reaudit_method = "action_mismatch"
        reaudit_detail = f"model answered, gold={gold_action}"
    else:
        # Non-answer decisions: correctness = decision matches gold_action
        reaudit_correct = (model_decision == gold_action)
        reaudit_method = "action_match"
        reaudit_detail = f"decision={model_decision} vs gold={gold_action}"

    gold_in_answer = contains_gold_check(model_answer, str(source_gold)) if source_gold else False

    flags = []
    if csv_gold and source_gold and csv_gold.strip().lower() != str(source_gold).strip().lower():
        flags.append("GOLD_DRIFT")
    if model_decision == "answer" and gold_action == "answer":
        if not recorded_correct and reaudit_correct:
            flags.append("FLIP_TO_CORRECT")
        if recorded_correct and not reaudit_correct:
            flags.append("FLIP_TO_WRONG")
        if not recorded_correct and gold_in_answer:
            flags.append("CONTAINS_GOLD_BUT_WRONG")

    return {
        "item_id": item_id,
        "family": "B",
        "model_name": row.get("model_name", ""),
        "question_full": source.get("question", row.get("question", "")),
        "gold_answer_source": str(source_gold),
        "gold_answer_csv": csv_gold,
        "model_answer": model_answer,
        "model_decision": model_decision,
        "gold_action": gold_action,
        "recorded_correct": str(recorded_correct),
        "reaudit_correct": str(reaudit_correct),
        "reaudit_method": reaudit_method,
        "reaudit_detail": reaudit_detail,
        "contains_gold": str(gold_in_answer),
        "flag": "|".join(flags) if flags else "",
    }


# ---------------------------------------------------------------------------
# Cross-model analysis
# ---------------------------------------------------------------------------

def compute_cross_model_flags(
    audit_rows: list[dict],
    source_items: dict[str, dict],
    manifest: dict,
) -> list[dict]:
    """Add ALL_MODELS_WRONG and EXCLUDED flags."""
    # Group by item
    by_item: dict[str, list[dict]] = defaultdict(list)
    for r in audit_rows:
        by_item[r["item_id"]].append(r)

    excluded_cal = set(manifest.get("calibration", {}).get("excluded_items", []))
    excluded_fb = set(manifest.get("family_b", {}).get("excluded_items", []))
    all_excluded = excluded_cal | excluded_fb

    for item_id, rows in by_item.items():
        # Only check answer-action rows for Family B
        relevant = rows
        if rows[0]["family"] == "B":
            relevant = [r for r in rows if r["model_decision"] == "answer" and r["gold_action"] == "answer"]

        if relevant:
            n_correct = sum(1 for r in relevant if r["reaudit_correct"] == "True")
            n_total = len(relevant)
            if n_correct == 0 and n_total >= 3:
                for r in rows:
                    existing = r["flag"]
                    if "ALL_MODELS_WRONG" not in existing:
                        r["flag"] = (existing + "|ALL_MODELS_WRONG").lstrip("|")

        if item_id in all_excluded:
            for r in rows:
                existing = r["flag"]
                if "EXCLUDED_ITEM" not in existing:
                    r["flag"] = (existing + "|EXCLUDED_ITEM").lstrip("|")

    return audit_rows


# ---------------------------------------------------------------------------
# Output generation
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "item_id", "family", "model_name", "question_full",
    "gold_answer_source", "gold_answer_csv", "model_answer",
    "model_decision", "gold_action",
    "recorded_correct", "reaudit_correct",
    "reaudit_method", "reaudit_detail",
    "contains_gold", "flag",
]


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)
    print(f"  CSV: {path} ({len(rows)} rows)")


def write_summary(rows: list[dict], source_items: dict[str, dict], path: Path) -> None:
    total = len(rows)
    flagged = [r for r in rows if r["flag"]]
    flag_counts: Counter = Counter()
    for r in flagged:
        for f in r["flag"].split("|"):
            flag_counts[f] += 1

    cal_rows = [r for r in rows if r["family"] == "A"]
    fb_rows = [r for r in rows if r["family"] == "B"]
    cal_items = len(set(r["item_id"] for r in cal_rows))
    fb_items = len(set(r["item_id"] for r in fb_rows))
    models = sorted(set(r["model_name"] for r in rows))

    # Items where ALL models wrong (unique item_ids)
    amw_items = sorted(set(r["item_id"] for r in rows if "ALL_MODELS_WRONG" in r["flag"]))

    # Items with CONTAINS_GOLD_BUT_WRONG
    cgbw_rows = [r for r in rows if "CONTAINS_GOLD_BUT_WRONG" in r["flag"]]
    cgbw_items = sorted(set(r["item_id"] for r in cgbw_rows))

    # Items with FLIP_TO_CORRECT
    ftc_rows = [r for r in rows if "FLIP_TO_CORRECT" in r["flag"]]

    # Items with FLIP_TO_WRONG
    ftw_rows = [r for r in rows if "FLIP_TO_WRONG" in r["flag"]]

    # Items with GOLD_DRIFT
    gd_rows = [r for r in rows if "GOLD_DRIFT" in r["flag"]]
    gd_items = sorted(set(r["item_id"] for r in gd_rows))

    lines = [
        "# Family A & B Question-Level Validity Audit",
        "",
        f"> **Date:** 2026-03-31 | **Script:** `scripts/audit_family_ab_results.py`",
        f"> **Grading engine:** `metajudge.scoring.grading_v2.grade_item()`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total audit rows | {total} |",
        f"| Family A rows (items) | {len(cal_rows)} ({cal_items}) |",
        f"| Family B rows (items) | {len(fb_rows)} ({fb_items}) |",
        f"| Models | {len(models)} |",
        f"| Flagged rows | {len(flagged)} |",
        "",
        "### Flag Distribution",
        "",
        "| Flag | Count | Description |",
        "|------|-------|-------------|",
    ]

    flag_descs = {
        "FLIP_TO_CORRECT": "Recorded wrong, re-audit says correct",
        "FLIP_TO_WRONG": "Recorded correct, re-audit says wrong",
        "CONTAINS_GOLD_BUT_WRONG": "Family B answer contains gold but marked wrong",
        "ALL_MODELS_WRONG": "All models got this item wrong (gold suspect)",
        "GOLD_DRIFT": "Gold answer differs between CSV and source data",
        "EXCLUDED_ITEM": "Item excluded from clean subset",
    }
    for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        desc = flag_descs.get(flag, "")
        lines.append(f"| `{flag}` | {count} | {desc} |")

    lines.extend([
        "",
        "---",
        "",
        "## Issue 1: Correctness Flips (FLIP_TO_CORRECT / FLIP_TO_WRONG)",
        "",
        f"**FLIP_TO_CORRECT:** {len(ftc_rows)} rows — recorded as wrong but re-audit says correct.",
        "",
    ])
    if ftc_rows:
        lines.append("| Item | Family | Model | Gold | Model Answer | Re-audit Detail |")
        lines.append("|------|--------|-------|------|-------------|-----------------|")
        for r in sorted(ftc_rows, key=lambda x: (x["family"], x["item_id"])):
            ma = r["model_answer"][:60] + ("..." if len(r["model_answer"]) > 60 else "")
            lines.append(
                f"| {r['item_id']} | {r['family']} | {r['model_name'][:25]} | "
                f"{r['gold_answer_source'][:30]} | {ma} | {r['reaudit_detail'][:50]} |"
            )

    lines.extend([
        "",
        f"**FLIP_TO_WRONG:** {len(ftw_rows)} rows — recorded as correct but re-audit says wrong.",
        "",
    ])
    if ftw_rows:
        lines.append("| Item | Family | Model | Gold | Model Answer | Re-audit Detail |")
        lines.append("|------|--------|-------|------|-------------|-----------------|")
        for r in sorted(ftw_rows, key=lambda x: (x["family"], x["item_id"])):
            ma = r["model_answer"][:60] + ("..." if len(r["model_answer"]) > 60 else "")
            lines.append(
                f"| {r['item_id']} | {r['family']} | {r['model_name'][:25]} | "
                f"{r['gold_answer_source'][:30]} | {ma} | {r['reaudit_detail'][:50]} |"
            )

    # Issue 2: Family B verbose-answer problem
    lines.extend([
        "",
        "---",
        "",
        "## Issue 2: Family B Verbose-Answer Adjudication (CONTAINS_GOLD_BUT_WRONG)",
        "",
        f"**{len(cgbw_rows)} rows** across **{len(cgbw_items)} items** where the model's answer field "
        "contains the gold answer as a substring but is graded incorrect due to strict matching.",
        "",
        "This occurs because Family B `abs_*` registry entries use `alias_plus_normalization` "
        "without `match_mode: \"contains_any\"`, so verbose answers like "
        "\"Lithium (Li)\" fail to match gold=\"Lithium\".",
        "",
    ])
    if cgbw_items:
        lines.append("| Item | Gold | Example Model Answer (truncated) | Models Affected |")
        lines.append("|------|------|----------------------------------|-----------------|")
        for iid in cgbw_items:
            item_rows = [r for r in cgbw_rows if r["item_id"] == iid]
            gold = item_rows[0]["gold_answer_source"][:30]
            example = item_rows[0]["model_answer"][:60] + ("..." if len(item_rows[0]["model_answer"]) > 60 else "")
            n = len(item_rows)
            lines.append(f"| {iid} | {gold} | {example} | {n} |")

    # Issue 3: All-models-wrong
    lines.extend([
        "",
        "---",
        "",
        "## Issue 3: Gold Answer Validity Concerns (ALL_MODELS_WRONG)",
        "",
        f"**{len(amw_items)} items** where all models answered incorrectly. "
        "These warrant manual review of the gold answer.",
        "",
    ])
    if amw_items:
        lines.append("| Item | Family | Gold Answer | Question (truncated) |")
        lines.append("|------|--------|-------------|---------------------|")
        for iid in amw_items:
            src = source_items.get(iid, {})
            gold = str(src.get("gold_answer", ""))[:40]
            q = src.get("question", "")[:80] + ("..." if len(src.get("question", "")) > 80 else "")
            fam = "A" if iid.startswith(("v4", "gen_a", "gen_b")) and not iid.startswith("abs_") else "B"
            # Better: check from audit rows
            fam_rows = [r for r in rows if r["item_id"] == iid]
            if fam_rows:
                fam = fam_rows[0]["family"]
            lines.append(f"| {iid} | {fam} | {gold} | {q} |")

    # Issue 4: Gold drift
    lines.extend([
        "",
        "---",
        "",
        "## Issue 4: Gold Answer Version Drift (GOLD_DRIFT)",
        "",
        f"**{len(gd_items)} items** where the gold answer in the CSV differs from the source data file.",
        "",
    ])
    if gd_items:
        lines.append("| Item | Gold (CSV) | Gold (Source) |")
        lines.append("|------|-----------|--------------|")
        for iid in gd_items:
            item_rows = [r for r in gd_rows if r["item_id"] == iid]
            csv_g = item_rows[0]["gold_answer_csv"][:40]
            src_g = item_rows[0]["gold_answer_source"][:40]
            lines.append(f"| {iid} | {csv_g} | {src_g} |")

    # Issue 5: Question truncation
    lines.extend([
        "",
        "---",
        "",
        "## Issue 5: Question Truncation in v0551 CSV",
        "",
        "The notebook export (Cell 7) truncates questions at 150 characters:",
        "```python",
        '"question": gold.get("question", "")[:150]',
        "```",
        "This affects 44% of calibration rows. This audit uses full questions from source data.",
        "**Fix:** Remove `[:150]` from both calibration and Family B export blocks in the notebook.",
        "",
        "---",
        "",
        "## Recommendations",
        "",
        "1. **Family B registry fix:** Add `\"match_mode\": \"contains_any\"` to all `abs_*` answer items "
        "in `data/adjudication_registry.json` to accept verbose answers containing the gold answer.",
        "2. **Re-run Family B scoring** after registry fix — UWAA scores will change significantly.",
        "3. **Review all-models-wrong items** — consider whether gold answers for contested/temporal items "
        "need updating or whether items should be excluded.",
        "4. **Fix notebook truncation** — remove `[:150]` from CSV export cell.",
        "5. **Archive stale v0.5.1 CSVs** — gold answers have drifted; these CSVs should not be used for analysis.",
    ]
    )

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Summary: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading source data...")
    source_items = load_source_items()
    registry = load_registry(str(REGISTRY_PATH))
    manifest = load_clean_manifest()

    print(f"  Source items: {len(source_items)}")
    print(f"  Registry entries: {len(registry)}")

    all_rows: list[dict] = []

    # --- Family A: v0551 clean set ---
    print("\nAuditing Family A (v0551 clean set)...")
    cal_v0551 = load_csv_rows(CAL_CSV_V0551)
    for row in cal_v0551:
        all_rows.append(reaudit_calibration_row(row, registry, source_items))
    print(f"  Processed {len(cal_v0551)} rows")

    # --- Family A: excluded items from v0.5.1 ---
    excluded_cal = set(manifest.get("calibration", {}).get("excluded_items", []))
    if CAL_CSV_V051.exists():
        print("\nAuditing Family A excluded items (v0.5.1)...")
        cal_v051 = load_csv_rows(CAL_CSV_V051)
        seen_v0551 = {(r["item_id"], r["model_name"]) for r in cal_v0551}
        excluded_rows = [r for r in cal_v051
                         if r["item_id"] in excluded_cal
                         and (r["item_id"], r["model_name"]) not in seen_v0551]
        for row in excluded_rows:
            all_rows.append(reaudit_calibration_row(row, registry, source_items))
        print(f"  Processed {len(excluded_rows)} excluded rows")

    # --- Family B: v0551 clean set ---
    print("\nAuditing Family B (v0551 clean set)...")
    fb_v0551 = load_csv_rows(FB_CSV_V0551)
    for row in fb_v0551:
        all_rows.append(reaudit_family_b_row(row, registry, source_items))
    print(f"  Processed {len(fb_v0551)} rows")

    # --- Family B: excluded items from v0.5.1 (if available with enough data) ---
    excluded_fb = set(manifest.get("family_b", {}).get("excluded_items", []))
    if FB_CSV_V051.exists():
        print("\nAuditing Family B excluded items (v0.5.1)...")
        fb_v051 = load_csv_rows(FB_CSV_V051)
        seen_fb_v0551 = {(r["item_id"], r["model_name"]) for r in fb_v0551}
        excluded_fb_rows = [r for r in fb_v051
                            if r["item_id"] in excluded_fb
                            and (r["item_id"], r["model_name"]) not in seen_fb_v0551]
        for row in excluded_fb_rows:
            all_rows.append(reaudit_family_b_row(row, registry, source_items))
        print(f"  Processed {len(excluded_fb_rows)} excluded rows")

    # --- Cross-model flags ---
    print("\nComputing cross-model flags...")
    all_rows = compute_cross_model_flags(all_rows, source_items, manifest)

    # --- Output ---
    print("\nWriting outputs...")
    write_csv(all_rows, OUT_CSV)
    write_summary(all_rows, source_items, OUT_MD)

    # --- Quick stats ---
    flagged = [r for r in all_rows if r["flag"]]
    print(f"\n{'='*60}")
    print(f"AUDIT COMPLETE")
    print(f"  Total rows: {len(all_rows)}")
    print(f"  Flagged rows: {len(flagged)}")
    flag_c = Counter()
    for r in flagged:
        for f in r["flag"].split("|"):
            flag_c[f] += 1
    for flag, count in sorted(flag_c.items(), key=lambda x: -x[1]):
        print(f"    {flag}: {count}")


if __name__ == "__main__":
    main()
