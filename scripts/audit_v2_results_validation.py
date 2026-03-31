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
# Check 2: Cross-Reference with Audit Predictions
# ---------------------------------------------------------------------------
def check_2_audit_concordance(check1_results, audit_preds):
    """Compare pre-audit predicted flips with actual v1→v2 flips."""
    # Index check1 FB results by (model_name, item_id)
    fb_by_key = {(r["model_name"], r["item_id"]): r for r in check1_results["fb"]}
    cal_by_key = {(r["model_name"], r["item_id"]): r for r in check1_results["cal"]}

    # Categorize audit predictions
    pred_contains_gold = []  # FLIP_TO_CORRECT|CONTAINS_GOLD_BUT_WRONG
    pred_flip_correct = []   # any FLIP_TO_CORRECT (including excluded)
    pred_all_other = []

    for p in audit_preds:
        flags = p.get("flag", "")
        if "CONTAINS_GOLD_BUT_WRONG" in flags:
            pred_contains_gold.append(p)
        if "FLIP_TO_CORRECT" in flags:
            pred_flip_correct.append(p)

    # Check concordance for CONTAINS_GOLD_BUT_WRONG predictions
    concordance_rows = []
    for p in pred_contains_gold:
        key = (p["model_name"], p["item_id"])
        actual = fb_by_key.get(key)
        if actual is None:
            status = "NOT_IN_V2"
        elif actual["status"] == "FLIP_TO_CORRECT":
            status = "CONFIRMED"
        elif actual["status"] == "SAME_CORRECT":
            status = "ALREADY_CORRECT"  # was correct in both
        elif actual["status"] == "SAME_WRONG":
            status = "STILL_WRONG"
        else:
            status = actual["status"]

        concordance_rows.append({
            "item_id": p["item_id"],
            "model_name": p["model_name"],
            "family": p["family"],
            "predicted_flag": p["flag"],
            "v2_status": status,
            "audit_answer": p.get("model_answer", "")[:80],
            "v2_answer": actual["v2_answer"][:80] if actual else "",
            "gold": p.get("gold_answer_source", "")[:40],
        })

    # Check for unexpected flips (in v2 but NOT predicted by audit)
    actual_fb_flips = {(r["model_name"], r["item_id"])
                       for r in check1_results["fb"] if r["status"] == "FLIP_TO_CORRECT"}
    predicted_fb_flips = {(p["model_name"], p["item_id"])
                          for p in pred_flip_correct if p["family"] == "B"}
    unexpected_flips = actual_fb_flips - predicted_fb_flips

    return {
        "concordance_rows": concordance_rows,
        "unexpected_flips": unexpected_flips,
        "pred_contains_gold": pred_contains_gold,
    }


def format_check_2(results):
    """Format Check 2 results as markdown."""
    lines = ["## Check 2: Cross-Reference with Audit Predictions\n"]

    rows = results["concordance_rows"]
    total = len(rows)
    status_counts = Counter(r["v2_status"] for r in rows)

    lines.append(f"### CONTAINS_GOLD_BUT_WRONG Predictions ({total} rows)\n")
    lines.append("These are the 49 rows the pre-audit flagged as false negatives.\n")
    lines.append("| V2 Outcome | Count | % |")
    lines.append("|------------|-------|---|")
    for s in ["CONFIRMED", "ALREADY_CORRECT", "STILL_WRONG", "NOT_IN_V2"]:
        c = status_counts.get(s, 0)
        pct = c / total * 100 if total else 0
        if c > 0:
            lines.append(f"| {s} | {c} | {pct:.1f}% |")
    # Any other statuses
    for s, c in status_counts.items():
        if s not in ("CONFIRMED", "ALREADY_CORRECT", "STILL_WRONG", "NOT_IN_V2"):
            pct = c / total * 100
            lines.append(f"| {s} | {c} | {pct:.1f}% |")
    lines.append("")

    confirmed = status_counts.get("CONFIRMED", 0)
    concordance = confirmed / total * 100 if total else 0
    lines.append(f"**Concordance rate: {confirmed}/{total} = {concordance:.1f}%**\n")

    # Show any STILL_WRONG rows (predictions that didn't materialize)
    still_wrong = [r for r in rows if r["v2_status"] == "STILL_WRONG"]
    if still_wrong:
        lines.append(f"### Predictions Not Confirmed ({len(still_wrong)} rows)\n")
        lines.append("These were predicted to flip but didn't (model may have given a different answer in v2).\n")
        lines.append("| Model | Item | Gold | Audit Answer | V2 Answer |")
        lines.append("|-------|------|------|-------------|-----------|")
        for r in still_wrong:
            mn = r["model_name"].split("/")[-1][:20]
            lines.append(f"| {mn} | {r['item_id']} | {r['gold'][:30]} | {r['audit_answer'][:40]} | {r['v2_answer'][:40]} |")
        lines.append("")

    # Show unexpected flips
    unexpected = results["unexpected_flips"]
    if unexpected:
        lines.append(f"### Unexpected Flips ({len(unexpected)} rows)\n")
        lines.append("Rows that flipped to correct in v2 but were NOT predicted by the audit.\n")
        for mn, iid in sorted(unexpected):
            lines.append(f"- {mn.split('/')[-1][:20]} × {iid}")
        lines.append("")
    else:
        lines.append("### Unexpected Flips: None\n")
        lines.append("All v2 FLIP_TO_CORRECT rows were predicted by the audit.\n")

    # Verdict
    lines.append("### Check 2 Verdict\n")
    if concordance >= 90:
        lines.append(f"**✓ Concordance {concordance:.1f}% — audit predictions strongly confirmed. Check 2 PASSED.**")
    elif concordance >= 70:
        lines.append(f"**~ Concordance {concordance:.1f}% — mostly confirmed, some variance. Check 2 MARGINAL.**")
    else:
        lines.append(f"**⚠ Concordance {concordance:.1f}% — below threshold. Check 2 NEEDS REVIEW.**")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Check 3: abs_* Item Deep Dive
# ---------------------------------------------------------------------------
def check_3_abs_deep_dive(check1_results, v2_fb, registry):
    """Re-grade each abs_001..abs_015 × 5 models independently."""
    v2k = keyed(v2_fb)
    abs_rows = [r for r in check1_results["fb"] if r["item_id"].startswith("abs_")]
    abs_rows.sort(key=lambda r: (r["item_id"], r["model_name"]))

    detail = []
    for r in abs_rows:
        key = (r["model_name"], r["item_id"])
        v2r = v2k.get(key, {})
        v2_answer = v2r.get("model_answer", "")
        v2_decision = v2r.get("model_decision", "")
        gold = r["gold_answer"]

        # Re-grade independently
        regrade = {"correct": False, "method": "n/a", "match_detail": "non-answer decision"}
        if v2_decision == "answer" and v2_answer:
            regrade = grade_item(r["item_id"], v2_answer, registry, gold_answer=gold)

        recorded_correct = r["v2_correct"]
        regrade_correct = regrade["correct"]
        agreement = recorded_correct == regrade_correct

        detail.append({
            "item_id": r["item_id"],
            "model": r["model_name"].split("/")[-1][:20],
            "model_full": r["model_name"],
            "gold": gold,
            "v1_correct": r["v1_correct"],
            "v2_correct": recorded_correct,
            "v2_decision": v2_decision,
            "v2_answer": v2_answer[:100],
            "flip": r["status"],
            "regrade_correct": regrade_correct,
            "regrade_method": regrade.get("method", ""),
            "regrade_detail": regrade.get("match_detail", "")[:80],
            "agreement": agreement,
        })

    return detail


def format_check_3(detail):
    """Format Check 3 results as markdown."""
    lines = ["## Check 3: abs_* Item Deep Dive (15 items × 5 models = 75 rows)\n"]

    # Summary stats
    total = len(detail)
    flips_ftc = sum(1 for d in detail if d["flip"] == "FLIP_TO_CORRECT")
    flips_ftw = sum(1 for d in detail if d["flip"] == "FLIP_TO_WRONG")
    agreements = sum(1 for d in detail if d["agreement"])
    disagreements = [d for d in detail if not d["agreement"]]

    lines.append(f"- Total rows: {total}")
    lines.append(f"- FLIP_TO_CORRECT: {flips_ftc}")
    lines.append(f"- FLIP_TO_WRONG: {flips_ftw}")
    lines.append(f"- Re-grade agreement with recorded: {agreements}/{total} ({agreements/total*100:.1f}%)")
    lines.append("")

    # Per-item summary
    items = sorted(set(d["item_id"] for d in detail))
    lines.append("### Per-Item Summary\n")
    lines.append("| Item | Gold | V1 Correct | V2 Correct | Flips | Re-grade Match |")
    lines.append("|------|------|-----------|-----------|-------|---------------|")
    for iid in items:
        rows = [d for d in detail if d["item_id"] == iid]
        gold = rows[0]["gold"][:25]
        v1c = sum(1 for d in rows if d["v1_correct"])
        v2c = sum(1 for d in rows if d["v2_correct"])
        ftc = sum(1 for d in rows if d["flip"] == "FLIP_TO_CORRECT")
        agree = sum(1 for d in rows if d["agreement"])
        lines.append(f"| {iid} | {gold} | {v1c}/5 | {v2c}/5 | +{ftc} | {agree}/5 |")
    lines.append("")

    # Full detail table
    lines.append("### Full Detail\n")
    lines.append("| Item | Model | V1→V2 | Decision | V2 Answer (truncated) | Re-grade | Method | Match? |")
    lines.append("|------|-------|-------|----------|----------------------|----------|--------|--------|")
    for d in detail:
        v2a = d["v2_answer"][:40].replace("|", "\\|")
        arrow = "✓→✓" if d["v1_correct"] and d["v2_correct"] else \
                "✗→✓" if not d["v1_correct"] and d["v2_correct"] else \
                "✓→✗" if d["v1_correct"] and not d["v2_correct"] else "✗→✗"
        match = "✓" if d["agreement"] else "**✗**"
        lines.append(f"| {d['item_id']} | {d['model']} | {arrow} | {d['v2_decision']} | {v2a} | {d['regrade_correct']} | {d['regrade_method'][:20]} | {match} |")
    lines.append("")

    # Disagreements
    if disagreements:
        lines.append(f"### Re-grade Disagreements ({len(disagreements)} rows)\n")
        lines.append("These rows have different `is_correct` in the v2 CSV vs independent re-grading.\n")
        for d in disagreements:
            lines.append(f"- **{d['item_id']}** × {d['model']}: recorded={d['v2_correct']}, regrade={d['regrade_correct']}")
            lines.append(f"  - Decision: {d['v2_decision']}, Answer: {d['v2_answer'][:60]}")
            lines.append(f"  - Re-grade: {d['regrade_method']} — {d['regrade_detail']}")
        lines.append("")

    # abs_002 edge case check
    abs002 = [d for d in detail if d["item_id"] == "abs_002"]
    lines.append("### Edge Case: abs_002 (gold=Lithium, alias=Li)\n")
    for d in abs002:
        flag = ""
        if "helium" in d["v2_answer"].lower() and d["regrade_correct"]:
            flag = " **⚠ POSSIBLE FALSE POSITIVE — 'Li' substring in Helium answer**"
        lines.append(f"- {d['model']}: v2_correct={d['v2_correct']}, answer={d['v2_answer'][:60]}{flag}")
    lines.append("")

    # Verdict
    lines.append("### Check 3 Verdict\n")
    if flips_ftw == 0 and len(disagreements) == 0:
        lines.append("**✓ Zero regressions, 100% re-grade agreement. Check 3 PASSED.**")
    elif flips_ftw == 0:
        lines.append(f"**~ Zero regressions but {len(disagreements)} re-grade disagreement(s). Check 3 MARGINAL.**")
    else:
        lines.append(f"**⚠ {flips_ftw} regressions found. Check 3 NEEDS REVIEW.**")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Check 4: Independent Re-Grading of All V2 Results
# ---------------------------------------------------------------------------
def check_4_independent_regrade(v2_cal, v2_fb, registry):
    """Re-grade every v2 row with grade_item() and compare."""
    results = {"cal": [], "fb": []}

    # Calibration — all rows use grade_item
    for r in v2_cal:
        recorded = bool_str(r["is_correct"])
        rg = grade_item(r["item_id"], r["model_answer"], registry,
                        gold_answer=r["gold_answer"])
        results["cal"].append({
            "item_id": r["item_id"],
            "model_name": r["model_name"],
            "recorded": recorded,
            "regraded": rg["correct"],
            "agree": recorded == rg["correct"],
            "method": rg.get("method", ""),
            "detail": rg.get("match_detail", "")[:80],
            "answer": r["model_answer"][:60],
            "gold": r["gold_answer"][:40],
        })

    # Family B — only re-grade rows where decision == "answer" and answer exists
    for r in v2_fb:
        recorded = bool_str(r["is_correct"])
        decision = r.get("model_decision", "").strip().lower()
        answer = r.get("model_answer", "")

        if decision == "answer" and answer:
            rg = grade_item(r["item_id"], answer, registry,
                            gold_answer=r["gold_answer"])
            regraded = rg["correct"]
            method = rg.get("method", "")
            detail = rg.get("match_detail", "")[:80]
        else:
            # Non-answer decisions: is_correct should be False
            regraded = False
            method = "non-answer"
            detail = f"decision={decision}"

        results["fb"].append({
            "item_id": r["item_id"],
            "model_name": r["model_name"],
            "recorded": recorded,
            "regraded": regraded,
            "agree": recorded == regraded,
            "method": method,
            "detail": detail,
            "decision": decision,
            "answer": answer[:60],
            "gold": r["gold_answer"][:40],
        })

    return results


def format_check_4(results):
    """Format Check 4 results as markdown."""
    lines = ["## Check 4: Independent Re-Grading of All V2 Results\n"]

    for family, label in [("cal", "Family A (Calibration)"), ("fb", "Family B (Abstention)")]:
        rows = results[family]
        total = len(rows)
        agree = sum(1 for r in rows if r["agree"])
        disagree = [r for r in rows if not r["agree"]]

        lines.append(f"### {label}\n")
        lines.append(f"- Total rows: {total}")
        lines.append(f"- Agreement: {agree}/{total} ({agree/total*100:.1f}%)")
        lines.append(f"- Disagreements: {len(disagree)}")
        lines.append("")

        if disagree:
            lines.append("#### Disagreements\n")
            lines.append("| Model | Item | Gold | Answer | Recorded | Re-graded | Method |")
            lines.append("|-------|------|------|--------|----------|-----------|--------|")
            for d in disagree[:30]:  # cap at 30
                mn = d["model_name"].split("/")[-1][:18]
                lines.append(f"| {mn} | {d['item_id']} | {d['gold'][:20]} | {d['answer'][:30]} | {d['recorded']} | {d['regraded']} | {d['method']} |")
            if len(disagree) > 30:
                lines.append(f"| ... | ... | ... | ... | ... | ... | ({len(disagree)-30} more) |")
            lines.append("")

    # Verdict
    cal_agree = sum(1 for r in results["cal"] if r["agree"])
    fb_agree = sum(1 for r in results["fb"] if r["agree"])
    cal_total = len(results["cal"])
    fb_total = len(results["fb"])
    overall = (cal_agree + fb_agree) / (cal_total + fb_total) * 100

    lines.append("### Check 4 Verdict\n")
    if overall >= 99:
        lines.append(f"**✓ Overall re-grade agreement {overall:.1f}%. Check 4 PASSED.**")
    elif overall >= 95:
        lines.append(f"**~ Overall re-grade agreement {overall:.1f}%. Check 4 MARGINAL.**")
    else:
        lines.append(f"**⚠ Overall re-grade agreement {overall:.1f}%. Check 4 NEEDS REVIEW.**")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Check 5: Family A Calibration Stability
# ---------------------------------------------------------------------------
def check_5_calibration_stability(v1_cal, v2_cal):
    """Compare calibration metrics v1 vs v2 per model + item-level deltas."""
    v1k = keyed(v1_cal)
    v2k = keyed(v2_cal)

    # Per-model stats
    model_stats = {}
    for label, data in [("v1", v1_cal), ("v2", v2_cal)]:
        by_model = defaultdict(lambda: {"correct": 0, "total": 0, "brier_sum": 0.0, "conf_sum": 0.0})
        for r in data:
            m = r["model_name"]
            by_model[m]["total"] += 1
            if bool_str(r["is_correct"]):
                by_model[m]["correct"] += 1
            by_model[m]["brier_sum"] += float(r["brier_score"])
            by_model[m]["conf_sum"] += float(r["confidence"])
        model_stats[label] = dict(by_model)

    # Item-level Brier deltas
    brier_deltas = []
    for k in sorted(v1k.keys()):
        if k in v2k:
            b1 = float(v1k[k]["brier_score"])
            b2 = float(v2k[k]["brier_score"])
            brier_deltas.append({
                "model_name": k[0],
                "item_id": k[1],
                "v1_brier": b1,
                "v2_brier": b2,
                "delta": b2 - b1,
            })

    return {"model_stats": model_stats, "brier_deltas": brier_deltas}


def format_check_5(results):
    """Format Check 5 results as markdown."""
    lines = ["## Check 5: Family A Calibration Stability\n"]

    ms = results["model_stats"]
    models = sorted(ms["v1"].keys())

    lines.append("### Per-Model Comparison\n")
    lines.append("| Model | V1 Acc | V2 Acc | V1 1-Brier | V2 1-Brier | V1 Conf | V2 Conf |")
    lines.append("|-------|--------|--------|------------|------------|---------|---------|")
    v1_scores = []
    v2_scores = []
    for m in models:
        s1 = ms["v1"][m]
        s2 = ms["v2"].get(m, {"correct": 0, "total": 1, "brier_sum": 0, "conf_sum": 0})
        a1 = s1["correct"] / s1["total"]
        a2 = s2["correct"] / s2["total"]
        b1 = 1 - s1["brier_sum"] / s1["total"]
        b2 = 1 - s2["brier_sum"] / s2["total"]
        c1 = s1["conf_sum"] / s1["total"]
        c2 = s2["conf_sum"] / s2["total"]
        v1_scores.append(b1)
        v2_scores.append(b2)
        mn = m.split("/")[-1][:20]
        lines.append(f"| {mn} | {a1:.3f} | {a2:.3f} | {b1:.4f} | {b2:.4f} | {c1:.3f} | {c2:.3f} |")
    lines.append("")

    # Rank order check
    v1_rank = sorted(range(len(v1_scores)), key=lambda i: -v1_scores[i])
    v2_rank = sorted(range(len(v2_scores)), key=lambda i: -v2_scores[i])
    rank_preserved = v1_rank == v2_rank
    lines.append(f"**Rank order preserved: {'Yes' if rank_preserved else 'No'}**")

    if not rank_preserved:
        lines.append(f"- V1 rank: {[models[i].split('/')[-1][:12] for i in v1_rank]}")
        lines.append(f"- V2 rank: {[models[i].split('/')[-1][:12] for i in v2_rank]}")
    lines.append("")

    # Brier delta statistics
    deltas = [d["delta"] for d in results["brier_deltas"]]
    n = len(deltas)
    mean_d = sum(deltas) / n
    std_d = (sum((d - mean_d) ** 2 for d in deltas) / (n - 1)) ** 0.5
    min_d = min(deltas)
    max_d = max(deltas)
    pos = sum(1 for d in deltas if d > 0)
    neg = sum(1 for d in deltas if d < 0)
    zero = sum(1 for d in deltas if d == 0)

    lines.append("### Item-Level Brier Score Deltas (v2 - v1)\n")
    lines.append(f"- N: {n}")
    lines.append(f"- Mean delta: {mean_d:+.4f}")
    lines.append(f"- Std dev: {std_d:.4f}")
    lines.append(f"- Range: [{min_d:+.4f}, {max_d:+.4f}]")
    lines.append(f"- Positive (v2 better): {pos} ({pos/n*100:.1f}%)")
    lines.append(f"- Negative (v1 better): {neg} ({neg/n*100:.1f}%)")
    lines.append(f"- Zero (same): {zero} ({zero/n*100:.1f}%)")
    lines.append("")

    # t-test for mean = 0
    if std_d > 0:
        t_stat = mean_d / (std_d / n ** 0.5)
        # Two-tailed p approximation for large n (normal)
        import math
        p_approx = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / 2 ** 0.5)))
        lines.append(f"**t-test (H0: mean delta = 0):** t = {t_stat:.3f}, p ≈ {p_approx:.4f}")
        if p_approx > 0.05:
            lines.append("No significant systematic shift detected.")
        else:
            lines.append(f"Statistically significant shift (p < 0.05), but magnitude is small ({mean_d:+.4f}).")
    lines.append("")

    # Verdict
    lines.append("### Check 5 Verdict\n")
    if abs(mean_d) < 0.05:
        lines.append(f"**✓ Mean Brier delta {mean_d:+.4f} (within ±0.05). Check 5 PASSED.**")
    else:
        lines.append(f"**⚠ Mean Brier delta {mean_d:+.4f} (outside ±0.05). Check 5 NEEDS REVIEW.**")

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

    # --- Check 2 ---
    print("\nRunning Check 2: Audit Concordance...")
    audit_preds = load_csv(AUDIT_PREDS)
    print(f"  Loaded {len(audit_preds)} audit prediction rows")
    check2 = check_2_audit_concordance(check1, audit_preds)
    check2_md = format_check_2(check2)
    print("  Done.")

    # --- Check 3 ---
    print("\nRunning Check 3: abs_* Deep Dive...")
    check3 = check_3_abs_deep_dive(check1, v2_fb, registry)
    check3_md = format_check_3(check3)
    print("  Done.")

    # --- Check 4 ---
    print("\nRunning Check 4: Independent Re-Grading...")
    check4 = check_4_independent_regrade(v2_cal, v2_fb, registry)
    check4_md = format_check_4(check4)
    print("  Done.")

    # --- Check 5 ---
    print("\nRunning Check 5: Calibration Stability...")
    check5 = check_5_calibration_stability(v1_cal, v2_cal)
    check5_md = format_check_5(check5)
    print("  Done.")

    # --- Write report (append checks as they're implemented) ---
    report_lines = [
        "# Audit: V2 Narrative Results Validation\n",
        f"Generated by `scripts/audit_v2_results_validation.py`\n",
        f"V1: `{V1_CAL}` + `{V1_FB}`\n",
        f"V2: `{V2_CAL}` + `{V2_FB}`\n",
        "---\n",
        check1_md,
        "---\n",
        check2_md,
        "---\n",
        check3_md,
        "---\n",
        check4_md,
        "---\n",
        check5_md,
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
