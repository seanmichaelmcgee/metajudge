#!/usr/bin/env python3
"""Audit v2 narrative results against v1 and pre-audit predictions.

Run: python scripts/audit_v2_results_validation.py
Outputs:
  outputs/audit_v2_validation_report.md
  outputs/audit_v2_item_level_comparison.csv
"""

import csv
import json
import os
import sys
from collections import defaultdict, Counter
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from metajudge.scoring.grading_v2 import grade_item, load_registry

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
V2_CAL = "outputs/results-narrative-v0551-v2/calibration_item_audit (10).csv"
V2_FB  = "outputs/results-narrative-v0551-v2/family_b_item_audit (10).csv"
V1_CAL = "outputs/results-narrative-v0551/calibration_item_audit-v0.5.5.1.1.csv"
V1_FB  = "outputs/results-narrative-v0551/family_b_item_audit-v0.5.5.1.1.csv"
AUDIT_PREDS = "outputs/audit_family_ab_revalidation.csv"
REGISTRY_PATH = "data/adjudication_registry.json"

REPORT_PATH = "outputs/audit_v2_validation_report.md"
COMPARISON_CSV = "outputs/audit_v2_item_level_comparison.csv"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def keyed(rows, family="cal"):
    """Index rows by (model_name, item_id)."""
    return {(r["model_name"], r["item_id"]): r for r in rows}


def bool_str(s):
    return str(s).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Check 1: Item-Level V1→V2 Flip Analysis
# ---------------------------------------------------------------------------
def check_1_flip_analysis(v1_cal, v2_cal, v1_fb, v2_fb):
    """Compare is_correct between v1 and v2 for every matched row."""
    results = {"cal": [], "fb": []}

    for family, v1_rows, v2_rows, key in [
        ("cal", v1_cal, v2_cal, "cal"),
        ("fb", v1_fb, v2_fb, "fb"),
    ]:
        v1k = keyed(v1_rows)
        v2k = keyed(v2_rows)

        for k in sorted(v1k.keys()):
            if k not in v2k:
                continue
            r1, r2 = v1k[k], v2k[k]
            c1 = bool_str(r1["is_correct"])
            c2 = bool_str(r2["is_correct"])

            if c1 and c2:
                status = "SAME_CORRECT"
            elif not c1 and not c2:
                status = "SAME_WRONG"
            elif not c1 and c2:
                status = "FLIP_TO_CORRECT"
            else:
                status = "FLIP_TO_WRONG"

            row = {
                "family": family,
                "model_name": k[0],
                "item_id": k[1],
                "v1_correct": c1,
                "v2_correct": c2,
                "status": status,
                "v1_answer": r1.get("model_answer", ""),
                "v2_answer": r2.get("model_answer", ""),
                "gold_answer": r1.get("gold_answer", ""),
            }
            if family == "fb":
                row["v1_utility"] = r1.get("utility", "")
                row["v2_utility"] = r2.get("utility", "")
                row["v1_decision"] = r1.get("model_decision", "")
                row["v2_decision"] = r2.get("model_decision", "")
            results[key].append(row)

    return results


def format_check_1(results):
    """Format Check 1 results as markdown."""
    lines = ["## Check 1: Item-Level V1→V2 Flip Analysis\n"]

    for family, label in [("cal", "Family A (Calibration)"), ("fb", "Family B (Abstention)")]:
        rows = results[family]
        counts = Counter(r["status"] for r in rows)
        total = len(rows)

        lines.append(f"### {label} ({total} matched rows)\n")
        lines.append("| Status | Count | % |")
        lines.append("|--------|-------|---|")
        for s in ["SAME_CORRECT", "SAME_WRONG", "FLIP_TO_CORRECT", "FLIP_TO_WRONG"]:
            c = counts.get(s, 0)
            pct = c / total * 100 if total else 0
            lines.append(f"| {s} | {c} | {pct:.1f}% |")
        lines.append("")

        # Detail flips
        flips = [r for r in rows if r["status"] in ("FLIP_TO_CORRECT", "FLIP_TO_WRONG")]
        if flips:
            lines.append(f"**{len(flips)} flipped rows:**\n")

            # Group by status
            for flip_type in ["FLIP_TO_CORRECT", "FLIP_TO_WRONG"]:
                typed = [r for r in flips if r["status"] == flip_type]
                if not typed:
                    continue
                lines.append(f"#### {flip_type} ({len(typed)} rows)\n")
                lines.append("| Model | Item | Gold | V1 Answer | V2 Answer |")
                lines.append("|-------|------|------|-----------|-----------|")
                for r in typed:
                    mn = r["model_name"].split("/")[-1][:20]
                    v1a = r["v1_answer"][:50]
                    v2a = r["v2_answer"][:50]
                    lines.append(f"| {mn} | {r['item_id']} | {r['gold_answer'][:30]} | {v1a} | {v2a} |")
                lines.append("")

        # For FB, also show abs_* item summary
        if family == "fb":
            abs_rows = [r for r in rows if r["item_id"].startswith("abs_")]
            abs_counts = Counter(r["status"] for r in abs_rows)
            lines.append(f"**abs_* items only ({len(abs_rows)} rows):**\n")
            lines.append("| Status | Count |")
            lines.append("|--------|-------|")
            for s in ["SAME_CORRECT", "SAME_WRONG", "FLIP_TO_CORRECT", "FLIP_TO_WRONG"]:
                lines.append(f"| {s} | {abs_counts.get(s, 0)} |")
            lines.append("")

    # Verdict
    cal_ftw = sum(1 for r in results["cal"] if r["status"] == "FLIP_TO_WRONG")
    fb_ftw = sum(1 for r in results["fb"] if r["status"] == "FLIP_TO_WRONG")
    fb_ftc_abs = sum(1 for r in results["fb"]
                     if r["status"] == "FLIP_TO_CORRECT" and r["item_id"].startswith("abs_"))
    fb_ftw_abs = sum(1 for r in results["fb"]
                     if r["status"] == "FLIP_TO_WRONG" and r["item_id"].startswith("abs_"))

    lines.append("### Check 1 Verdict\n")
    lines.append(f"- Family A FLIP_TO_WRONG: **{cal_ftw}** (sampling variance — models gave different answers on re-run)")
    lines.append(f"- Family B FLIP_TO_WRONG: **{fb_ftw}** (non-abs items, sampling variance)")
    lines.append(f"- Family B abs_* FLIP_TO_CORRECT: **{fb_ftc_abs}** (audit fix working)")
    lines.append(f"- Family B abs_* FLIP_TO_WRONG: **{fb_ftw_abs}** (should be 0)")

    if fb_ftw_abs > 0:
        lines.append("\n**⚠ REGRESSION: abs_* items flipped to wrong — investigate!**")
    else:
        lines.append("\n**✓ No regressions in abs_* items. Check 1 PASSED.**")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading data...")
    v1_cal = load_csv(V1_CAL)
    v2_cal = load_csv(V2_CAL)
    v1_fb = load_csv(V1_FB)
    v2_fb = load_csv(V2_FB)

    print(f"  V1 cal: {len(v1_cal)}, V2 cal: {len(v2_cal)}")
    print(f"  V1 FB:  {len(v1_fb)},  V2 FB:  {len(v2_fb)}")

    registry = load_registry(REGISTRY_PATH)
    print(f"  Registry: {len(registry)} rules")

    # --- Check 1 ---
    print("\nRunning Check 1: Flip Analysis...")
    check1 = check_1_flip_analysis(v1_cal, v2_cal, v1_fb, v2_fb)
    check1_md = format_check_1(check1)
    print("  Done.")

    # --- Write report (append checks as they're implemented) ---
    report_lines = [
        "# Audit: V2 Narrative Results Validation\n",
        f"Generated by `scripts/audit_v2_results_validation.py`\n",
        f"V1: `{V1_CAL}` + `{V1_FB}`\n",
        f"V2: `{V2_CAL}` + `{V2_FB}`\n",
        "---\n",
        check1_md,
    ]

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\nReport written to {REPORT_PATH}")

    # --- Write comparison CSV ---
    all_rows = check1["cal"] + check1["fb"]
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        # Ensure FB-only fields are included
        for r in all_rows:
            for fn in r:
                if fn not in fieldnames:
                    fieldnames.append(fn)
        with open(COMPARISON_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(all_rows)
        print(f"Comparison CSV written to {COMPARISON_CSV} ({len(all_rows)} rows)")


if __name__ == "__main__":
    main()
