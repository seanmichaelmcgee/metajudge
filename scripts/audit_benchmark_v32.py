#!/usr/bin/env python3
"""
MetaJudge v3.2 Unified Benchmark Audit
=======================================
Audits a benchmark results directory (from metajudge_benchmark_v3_2.ipynb)
by re-grading every item across all 3 families and validating the composite.

Usage:
    python scripts/audit_benchmark_v32.py <results_dir> [--registry PATH]

Input: a directory containing:
    calibration_item_audit.csv
    family_b_item_audit.csv
    family_c_item_audit.csv
    composite_analysis.csv
    benchmark_run_summary.json

Output: prints structured audit report + writes audit_report.md to results_dir.
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "kaggle-package-v3"))

from metajudge.scoring.grading_v2 import grade_item, load_registry
from metajudge.scoring.abstention_metrics import score_family_b_item_v2, compute_uwaa

# ---------------------------------------------------------------------------
# Anchor constants (must match benchmark notebook Cell 2)
# ---------------------------------------------------------------------------
ANCHOR_A_FLOOR = 0.75
ANCHOR_A_CEIL = 1.00
ANCHOR_B_FLOOR = 0.60
ANCHOR_B_CEIL = 1.00
ANCHOR_C_FLOOR = -1.00
ANCHOR_C_CEIL = 1.00


def normalize(score, floor, ceil):
    return max(0.0, min(1.0, (score - floor) / (ceil - floor)))


# ---------------------------------------------------------------------------
# Audit functions
# ---------------------------------------------------------------------------

def audit_family_a(results_dir, registry):
    """Re-grade every calibration item and check for flips."""
    path = os.path.join(results_dir, "calibration_item_audit.csv")
    if not os.path.exists(path):
        return {"status": "MISSING", "rows": 0}

    rows = list(csv.DictReader(open(path)))
    flips_to_correct = []
    flips_to_wrong = []
    all_wrong_items = defaultdict(list)

    for row in rows:
        iid = row["item_id"]
        recorded = row["is_correct"] == "True"
        result = grade_item(iid, row["model_answer"], registry)
        reaudit = result.get("correct", False)

        if recorded != reaudit:
            entry = {
                "item_id": iid,
                "model_answer": row["model_answer"][:80],
                "gold": registry.get(iid, {}).get("gold_answer", "?"),
                "confidence": row["confidence"],
                "recorded": recorded,
                "reaudit": reaudit,
                "method": result.get("method", ""),
                "detail": result.get("match_detail", "")[:60],
            }
            if reaudit:
                flips_to_correct.append(entry)
            else:
                flips_to_wrong.append(entry)

        if not reaudit:
            all_wrong_items[iid].append(row["model_answer"][:60])

    # Metrics
    brier_scores = [float(r["brier_score"]) for r in rows]
    accuracy = sum(1 for r in rows if r["is_correct"] == "True") / len(rows)
    mean_brier = sum(brier_scores) / len(brier_scores)

    return {
        "status": "OK",
        "rows": len(rows),
        "accuracy": accuracy,
        "mean_1_brier": mean_brier,
        "flips_to_correct": flips_to_correct,
        "flips_to_wrong": flips_to_wrong,
        "items_all_wrong": {k: v for k, v in all_wrong_items.items()
                           if len(v) >= 1},  # single model, so any wrong
    }


def audit_family_b(results_dir, registry, fb_source):
    """Re-grade every abstention item and check for flips."""
    path = os.path.join(results_dir, "family_b_item_audit.csv")
    if not os.path.exists(path):
        return {"status": "MISSING", "rows": 0}

    rows = list(csv.DictReader(open(path)))
    flips_to_correct = []
    flips_to_wrong = []

    for row in rows:
        iid = row["item_id"]
        recorded_correct = row["is_correct"] == "True"
        recorded_decision = row["model_decision"]

        # Re-grade answer correctness
        if recorded_decision == "answer" and row["model_answer"]:
            result = grade_item(iid, row["model_answer"], registry,
                               gold_answer=row.get("gold_answer"))
            reaudit_correct = result.get("correct", False)
        else:
            reaudit_correct = False

        if recorded_correct != reaudit_correct:
            entry = {
                "item_id": iid,
                "decision": recorded_decision,
                "model_answer": row["model_answer"][:80],
                "gold": row.get("gold_answer", "?"),
                "recorded": recorded_correct,
                "reaudit": reaudit_correct,
            }
            if reaudit_correct:
                flips_to_correct.append(entry)
            else:
                flips_to_wrong.append(entry)

    # Metrics
    utilities = [float(r["utility"]) for r in rows]
    uwaa = (sum(utilities) / len(utilities) + 1) / 2
    actions = Counter(r["model_decision"] for r in rows)

    return {
        "status": "OK",
        "rows": len(rows),
        "uwaa": uwaa,
        "action_dist": dict(actions),
        "flips_to_correct": flips_to_correct,
        "flips_to_wrong": flips_to_wrong,
    }


def audit_family_c(results_dir, registry):
    """Re-grade every self-correction item (T1 and T2) and check for flips."""
    path = os.path.join(results_dir, "family_c_item_audit.csv")
    if not os.path.exists(path):
        return {"status": "MISSING", "rows": 0}

    rows = list(csv.DictReader(open(path)))
    flips = []
    verbose_t2 = 0

    for row in rows:
        iid = row["item_id"]

        # Re-grade T1
        t1_recorded = row["t1_correct"] == "True"
        t1_result = grade_item(iid, row["t1_answer"], registry)
        t1_reaudit = t1_result.get("correct", False)

        # Re-grade T2
        t2_recorded = row["t2_correct"] == "True"
        t2_result = grade_item(iid, row["t2_answer"], registry)
        t2_reaudit = t2_result.get("correct", False)

        if t1_recorded != t1_reaudit:
            flips.append({
                "item_id": iid, "turn": "T1",
                "direction": "TO_CORRECT" if t1_reaudit else "TO_WRONG",
                "model_answer": row["t1_answer"][:80],
                "gold": registry.get(iid, {}).get("gold_answer", "?"),
                "detail": t1_result.get("match_detail", "")[:60],
            })

        if t2_recorded != t2_reaudit:
            flips.append({
                "item_id": iid, "turn": "T2",
                "direction": "TO_CORRECT" if t2_reaudit else "TO_WRONG",
                "model_answer": row["t2_answer"][:80],
                "gold": registry.get(iid, {}).get("gold_answer", "?"),
                "detail": t2_result.get("match_detail", "")[:60],
            })

        if len(row.get("t2_answer", "")) > 60:
            verbose_t2 += 1

    # Metrics
    n = len(rows)
    t1c = sum(1 for r in rows if r["t1_correct"] == "True")
    t2c = sum(1 for r in rows if r["t2_correct"] == "True")
    wr = sum(1 for r in rows if r["t1_correct"] == "False" and r["t2_correct"] == "True")
    rw = sum(1 for r in rows if r["t1_correct"] == "True" and r["t2_correct"] == "False")
    t1_right = sum(1 for r in rows if r["t1_correct"] == "True")
    dmg_rate = rw / t1_right if t1_right > 0 else 0

    return {
        "status": "OK",
        "rows": n,
        "t1_accuracy": t1c / n,
        "t2_accuracy": t2c / n,
        "delta": (t2c - t1c) / n,
        "wr": wr, "rw": rw,
        "damage_rate": dmg_rate,
        "verbose_t2": verbose_t2,
        "flips": flips,
    }


def audit_composite(results_dir, a_result, b_result, c_result):
    """Validate anchor normalization math in composite_analysis.csv."""
    path = os.path.join(results_dir, "composite_analysis.csv")
    if not os.path.exists(path):
        return {"status": "MISSING"}

    rows = list(csv.DictReader(open(path)))
    if not rows:
        return {"status": "EMPTY"}

    row = rows[0]
    issues = []

    # Check recorded values match re-computed from audit CSVs
    if a_result["status"] == "OK":
        recorded_a = float(row["a_1brier"])
        if abs(recorded_a - a_result["mean_1_brier"]) > 0.001:
            issues.append(f"A score mismatch: composite={recorded_a:.4f} vs audit={a_result['mean_1_brier']:.4f}")

    if b_result["status"] == "OK":
        recorded_b = float(row["b_uwaa"])
        if abs(recorded_b - b_result["uwaa"]) > 0.001:
            issues.append(f"B score mismatch: composite={recorded_b:.4f} vs audit={b_result['uwaa']:.4f}")

    if c_result["status"] == "OK":
        recorded_c = float(row["c_delta"])
        if abs(recorded_c - c_result["delta"]) > 0.002:
            issues.append(f"C score mismatch: composite={recorded_c:.4f} vs audit={c_result['delta']:.4f}")

    # Validate normalization
    norm_a = float(row["norm_a"])
    norm_b = float(row["norm_b"])
    norm_c = float(row["norm_c"])
    meta = float(row["metascore"])
    monitoring = float(row["monitoring"])
    control = float(row["control"])

    expected_norm_a = normalize(float(row["a_1brier"]), ANCHOR_A_FLOOR, ANCHOR_A_CEIL)
    expected_norm_b = normalize(float(row["b_uwaa"]), ANCHOR_B_FLOOR, ANCHOR_B_CEIL)
    expected_norm_c = normalize(float(row["c_delta"]), ANCHOR_C_FLOOR, ANCHOR_C_CEIL)
    expected_meta = (expected_norm_a + expected_norm_b + expected_norm_c) / 3
    expected_mon = (expected_norm_a + expected_norm_b) / 2

    for label, recorded, expected in [
        ("norm_a", norm_a, expected_norm_a),
        ("norm_b", norm_b, expected_norm_b),
        ("norm_c", norm_c, expected_norm_c),
        ("metascore", meta, expected_meta),
        ("monitoring", monitoring, expected_mon),
        ("control", control, norm_c),
    ]:
        if abs(recorded - expected) > 0.001:
            issues.append(f"{label}: recorded={recorded:.4f} expected={expected:.4f}")

    # Range checks
    for label, val in [("norm_a", norm_a), ("norm_b", norm_b), ("norm_c", norm_c),
                       ("metascore", meta), ("monitoring", monitoring), ("control", control)]:
        if not (0 <= val <= 1):
            issues.append(f"{label}={val} out of [0,1]")

    return {
        "status": "OK" if not issues else "ISSUES",
        "issues": issues,
        "metascore": meta,
        "monitoring": monitoring,
        "control": control,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(results_dir, a, b, c, comp):
    """Generate markdown audit report."""
    lines = []
    lines.append(f"# Benchmark v3.2 Audit Report")
    lines.append(f"\n**Results:** `{results_dir}`")
    lines.append(f"**Grading engine:** `kaggle-package-v3/metajudge/scoring/grading_v2.py`\n")

    # Summary
    total_flips = (len(a.get("flips_to_correct", [])) + len(a.get("flips_to_wrong", []))
                   + len(b.get("flips_to_correct", [])) + len(b.get("flips_to_wrong", []))
                   + len(c.get("flips", [])))

    lines.append("## Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Family A rows | {a.get('rows', 0)} |")
    lines.append(f"| Family B rows | {b.get('rows', 0)} |")
    lines.append(f"| Family C rows | {c.get('rows', 0)} |")
    lines.append(f"| Total grading flips | {total_flips} |")
    lines.append(f"| Composite valid | {comp.get('status', '?')} |")
    lines.append(f"| MetaScore | {comp.get('metascore', '?')} |")

    # Family A
    lines.append(f"\n## Family A — Calibration\n")
    if a["status"] == "OK":
        lines.append(f"- Items: {a['rows']}, Accuracy: {a['accuracy']:.1%}, 1-Brier: {a['mean_1_brier']:.4f}")
        lines.append(f"- Flips to correct: {len(a['flips_to_correct'])}")
        lines.append(f"- Flips to wrong: {len(a['flips_to_wrong'])}")
        for f in a["flips_to_correct"] + a["flips_to_wrong"]:
            direction = "→CORRECT" if f["reaudit"] else "→WRONG"
            lines.append(f"  - `{f['item_id']}` {direction}: gold='{f['gold'][:30]}' "
                        f"ans='{f['model_answer'][:40]}' ({f.get('detail', '')})")

    # Family B
    lines.append(f"\n## Family B — Abstention\n")
    if b["status"] == "OK":
        lines.append(f"- Items: {b['rows']}, UWAA: {b['uwaa']:.4f}")
        lines.append(f"- Actions: {b['action_dist']}")
        lines.append(f"- Flips to correct: {len(b['flips_to_correct'])}")
        lines.append(f"- Flips to wrong: {len(b['flips_to_wrong'])}")
        for f in b["flips_to_correct"] + b["flips_to_wrong"]:
            direction = "→CORRECT" if f["reaudit"] else "→WRONG"
            lines.append(f"  - `{f['item_id']}` {direction}: decision={f['decision']} "
                        f"gold='{f['gold'][:30]}' ans='{f['model_answer'][:40]}'")

    # Family C
    lines.append(f"\n## Family C — Self-Correction\n")
    if c["status"] == "OK":
        lines.append(f"- Items: {c['rows']}, T1: {c['t1_accuracy']:.1%}, T2: {c['t2_accuracy']:.1%}, "
                     f"Δ: {c['delta']:+.4f}")
        lines.append(f"- W→R: {c['wr']}, R→W: {c['rw']}, Damage: {c['damage_rate']:.1%}")
        lines.append(f"- Verbose T2: {c['verbose_t2']}/{c['rows']}")
        lines.append(f"- Grading flips: {len(c['flips'])}")
        for f in c["flips"]:
            lines.append(f"  - `{f['item_id']}` {f['turn']} {f['direction']}: "
                        f"gold='{f['gold'][:30]}' ans='{f['model_answer'][:40]}' ({f['detail']})")

    # Composite
    lines.append(f"\n## Composite Validation\n")
    if comp["status"] in ("OK", "ISSUES"):
        lines.append(f"- MetaScore: {comp['metascore']}")
        lines.append(f"- Monitoring: {comp['monitoring']}, Control: {comp['control']}")
        if comp.get("issues"):
            lines.append(f"- **Issues:**")
            for issue in comp["issues"]:
                lines.append(f"  - {issue}")
        else:
            lines.append(f"- Anchor normalization: **VALID**")

    # Verdict
    lines.append(f"\n## Verdict\n")
    if total_flips == 0 and comp.get("status") == "OK":
        lines.append("**PASS** — No grading flips, composite math valid.")
    else:
        lines.append(f"**REVIEW NEEDED** — {total_flips} grading flip(s) found.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Audit MetaJudge v3.2 benchmark results")
    parser.add_argument("results_dir", help="Path to results directory")
    parser.add_argument("--registry", default=str(REPO_ROOT / "kaggle-dataset-v3" / "adjudication_registry.json"),
                        help="Path to adjudication registry")
    parser.add_argument("--fb-source", default=str(REPO_ROOT / "kaggle-dataset-v3" / "family_b_pilot_v2.json"),
                        help="Path to Family B source items")
    args = parser.parse_args()

    print(f"Loading registry: {args.registry}")
    registry = load_registry(args.registry)
    print(f"Registry: {len(registry)} entries")

    fb_source = {}
    if os.path.exists(args.fb_source):
        with open(args.fb_source) as f:
            fb_source = {it["item_id"]: it for it in json.load(f)}
        print(f"Family B source: {len(fb_source)} items")

    print(f"\nAuditing: {args.results_dir}\n")

    a = audit_family_a(args.results_dir, registry)
    b = audit_family_b(args.results_dir, registry, fb_source)
    c = audit_family_c(args.results_dir, registry)
    comp = audit_composite(args.results_dir, a, b, c)

    report = generate_report(args.results_dir, a, b, c, comp)
    print(report)

    # Write report
    report_path = os.path.join(args.results_dir, "audit_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
