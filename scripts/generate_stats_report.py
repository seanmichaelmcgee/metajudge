#!/usr/bin/env python3
"""
MetaJudge v0.5.5.1 — Statistical Analysis Report Generator

Produces three deliverables:
1. Stats theoretical backgrounder (markdown)
2. Polished results report (.docx with embedded figures)
3. Reproducibility log (markdown)

Usage:
    python scripts/generate_stats_report.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path("/tmp/v0551/v0.5.5.1 - results")
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"

CAL_CSV = DATA_DIR / "calibration_item_audit (8).csv"
FB_CSV = DATA_DIR / "family_b_item_audit (8).csv"
RUN_SUMMARY = DATA_DIR / "run_summary (7).json"
BRIDGE_JSON = DATA_DIR / "bridge_report_all_models (2).json"
VERDICT_JSON = DATA_DIR / "success_criteria_verdict.json"
AUDIT_QUEUE_CSV = DATA_DIR / "audit_review_queue (2).csv"

# Short display names for models
MODEL_SHORT = {
    "google/gemini-2.5-flash": "Gemini Flash",
    "google/gemini-2.5-pro": "Gemini Pro",
    "anthropic/claude-sonnet-4@20250514": "Sonnet 4",
    "anthropic/claude-haiku-4-5@20251001": "Haiku 4.5",
    "deepseek-ai/deepseek-v3.1": "DeepSeek V3.1",
}

SEED = 42

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def short_name(model: str) -> str:
    return MODEL_SHORT.get(model, model.split("/")[-1])


def load_all_data():
    """Load and structure all v0.5.5.1 data."""
    cal_rows = load_csv(CAL_CSV)
    fb_rows = load_csv(FB_CSV)
    run_summary = load_json(RUN_SUMMARY)
    audit_queue = load_csv(AUDIT_QUEUE_CSV)

    # Flagged item IDs for sensitivity analysis
    flagged_items = set(row["item_id"] for row in audit_queue)

    # Structure calibration data: {model: {item_id: {...}}}
    cal_by_model = defaultdict(dict)
    for row in cal_rows:
        m = row["model_name"]
        iid = row["item_id"]
        cal_by_model[m][iid] = {
            "is_correct": row["is_correct"] == "True",
            "brier_score": float(row["brier_score"]),
            "confidence": float(row["confidence"]),
            "mechanism": row["mechanism"],
            "gold_answer": row["gold_answer"],
            "model_answer": row["model_answer"],
        }

    # Structure Family B data: {model: {item_id: {...}}}
    fb_by_model = defaultdict(dict)
    for row in fb_rows:
        m = row["model_name"]
        iid = row["item_id"]
        fb_by_model[m][iid] = {
            "model_decision": row["model_decision"],
            "gold_action": row["gold_action"],
            "utility": float(row["utility"]),
            "confidence": float(row["confidence"]),
            "is_correct": row["is_correct"] == "True",
        }

    return {
        "cal_rows": cal_rows,
        "fb_rows": fb_rows,
        "cal_by_model": dict(cal_by_model),
        "fb_by_model": dict(fb_by_model),
        "run_summary": run_summary,
        "flagged_items": flagged_items,
    }


# ---------------------------------------------------------------------------
# Statistical computations (wrapping existing metajudge functions)
# ---------------------------------------------------------------------------

def compute_effect_sizes(scores_a, scores_b):
    """Cohen's d for paired differences."""
    a = np.asarray(scores_a, dtype=float)
    b = np.asarray(scores_b, dtype=float)
    diffs = a - b
    if np.std(diffs) == 0:
        return {"cohens_d": 0.0}
    d = float(np.mean(diffs) / np.std(diffs, ddof=1))
    return {"cohens_d": d}


def compute_odds_ratio(a_only: int, b_only: int) -> float:
    """Odds ratio from McNemar discordant cells."""
    if b_only == 0:
        return float("inf") if a_only > 0 else 1.0
    return a_only / b_only


def run_calibration_stats(cal_by_model, item_filter=None):
    """Run full pairwise calibration statistics."""
    from metajudge.scoring.statistics import (
        mcnemar_test,
        paired_permutation_test,
        paired_bootstrap_ci,
        holm_correction,
    )

    models = sorted(cal_by_model.keys())

    # Find common items
    common = set.intersection(*(set(cal_by_model[m].keys()) for m in models))
    if item_filter:
        common = common - item_filter
    item_ids = sorted(common)

    results = {}
    all_p = {}

    for m_a, m_b in combinations(models, 2):
        pair = f"{short_name(m_a)} vs {short_name(m_b)}"
        correct_a = [cal_by_model[m_a][i]["is_correct"] for i in item_ids]
        correct_b = [cal_by_model[m_b][i]["is_correct"] for i in item_ids]
        brier_a = [cal_by_model[m_a][i]["brier_score"] for i in item_ids]
        brier_b = [cal_by_model[m_b][i]["brier_score"] for i in item_ids]

        mcn = mcnemar_test(correct_a, correct_b)
        perm = paired_permutation_test(brier_a, brier_b)
        boot = paired_bootstrap_ci(brier_a, brier_b)
        eff = compute_effect_sizes(brier_a, brier_b)
        odds = compute_odds_ratio(mcn["a_only"], mcn["b_only"])

        results[pair] = {
            "n_items": len(item_ids),
            "acc_a": float(np.mean(correct_a)),
            "acc_b": float(np.mean(correct_b)),
            "mcnemar": mcn,
            "brier_mean_a": float(np.mean(brier_a)),
            "brier_mean_b": float(np.mean(brier_b)),
            "permutation": perm,
            "bootstrap_ci": boot,
            "cohens_d": eff["cohens_d"],
            "odds_ratio": odds,
        }
        all_p[f"{pair}_acc"] = mcn["p_value"]
        all_p[f"{pair}_brier"] = perm["p_value"]

    corrected = holm_correction(all_p)
    return {
        "models": models,
        "n_items": len(item_ids),
        "pairwise": results,
        "holm": corrected,
    }


def run_family_b_stats(fb_by_model, item_filter=None, min_items=10):
    """Run full pairwise Family B statistics."""
    from metajudge.scoring.statistics import (
        stuart_maxwell_test,
        paired_permutation_test,
        paired_bootstrap_ci,
        holm_correction,
    )

    # Exclude models with fewer than min_items
    models = sorted(m for m in fb_by_model if len(fb_by_model[m]) >= min_items)

    common = set.intersection(*(set(fb_by_model[m].keys()) for m in models))
    if item_filter:
        common = common - item_filter
    item_ids = sorted(common)

    results = {}
    all_p = {}

    for m_a, m_b in combinations(models, 2):
        pair = f"{short_name(m_a)} vs {short_name(m_b)}"
        actions_a = [fb_by_model[m_a][i]["model_decision"] for i in item_ids]
        actions_b = [fb_by_model[m_b][i]["model_decision"] for i in item_ids]
        util_a = [fb_by_model[m_a][i]["utility"] for i in item_ids]
        util_b = [fb_by_model[m_b][i]["utility"] for i in item_ids]

        sm = stuart_maxwell_test(actions_a, actions_b,
                                 labels=["answer", "clarify", "verify", "abstain"])
        perm = paired_permutation_test(util_a, util_b)
        boot = paired_bootstrap_ci(util_a, util_b)
        eff = compute_effect_sizes(util_a, util_b)

        results[pair] = {
            "n_items": len(item_ids),
            "util_mean_a": float(np.mean(util_a)),
            "util_mean_b": float(np.mean(util_b)),
            "stuart_maxwell": sm,
            "permutation": perm,
            "bootstrap_ci": boot,
            "cohens_d": eff["cohens_d"],
        }
        all_p[f"{pair}_util"] = perm["p_value"]
        if not np.isnan(sm["p_value"]):
            all_p[f"{pair}_actions"] = sm["p_value"]

    corrected = holm_correction(all_p) if all_p else {}
    return {
        "models": models,
        "n_items": len(item_ids),
        "pairwise": results,
        "holm": corrected,
    }


def compute_per_model_calibration_metrics(cal_by_model):
    """Compute ECE, overconfidence rate, accuracy per model."""
    from metajudge.scoring.calibration_metrics import (
        expected_calibration_error,
        overconfidence_rate,
        accuracy_by_confidence_bucket,
    )

    metrics = {}
    for model, items in cal_by_model.items():
        confs = [v["confidence"] for v in items.values()]
        corrects = [v["is_correct"] for v in items.values()]
        briers = [v["brier_score"] for v in items.values()]

        metrics[model] = {
            "accuracy": float(np.mean(corrects)),
            "mean_brier": float(np.mean(briers)),
            "ece": expected_calibration_error(confs, corrects),
            "overconfidence_rate": overconfidence_rate(confs, corrects),
            "n_items": len(items),
            "reliability_bins": accuracy_by_confidence_bucket(confs, corrects),
        }
    return metrics


def compute_per_model_fb_metrics(fb_by_model):
    """Compute UWAA, action accuracy, per-action F1 per model."""
    from metajudge.scoring.abstention_metrics import compute_uwaa, compute_action_f1

    metrics = {}
    for model, items in fb_by_model.items():
        utils = [v["utility"] for v in items.values()]
        decisions = [v["model_decision"] for v in items.values()]
        golds = [v["gold_action"] for v in items.values()]

        action_acc = float(np.mean([d == g for d, g in zip(decisions, golds)]))
        f1 = compute_action_f1(decisions, golds)

        metrics[model] = {
            "uwaa": compute_uwaa(utils),
            "mean_utility": float(np.mean(utils)),
            "action_accuracy": action_acc,
            "action_f1": f1,
            "n_items": len(items),
            "action_dist": {
                a: sum(1 for d in decisions if d == a) / len(decisions)
                for a in ["answer", "clarify", "verify", "abstain"]
            },
        }
    return metrics


def compute_per_mechanism_stats(cal_by_model):
    """Per-mechanism accuracy and Brier by model."""
    # Collect all mechanisms
    mechanisms = set()
    for items in cal_by_model.values():
        for v in items.values():
            mechanisms.add(v["mechanism"])
    mechanisms = sorted(mechanisms)

    models = sorted(cal_by_model.keys())
    result = {}
    for mech in mechanisms:
        result[mech] = {}
        for model in models:
            items = {k: v for k, v in cal_by_model[model].items()
                     if v["mechanism"] == mech}
            if not items:
                result[mech][model] = {"accuracy": float("nan"), "mean_brier": float("nan"), "n": 0}
                continue
            corrects = [v["is_correct"] for v in items.values()]
            briers = [v["brier_score"] for v in items.values()]
            result[mech][model] = {
                "accuracy": float(np.mean(corrects)),
                "mean_brier": float(np.mean(briers)),
                "n": len(items),
            }
    return result


def compute_bridge_correlations(cal_by_model):
    """Spearman correlation between confidence and correctness per model."""
    from metajudge.scoring.statistics import spearman_with_ci

    results = {}
    for model, items in cal_by_model.items():
        confs = [v["confidence"] for v in items.values()]
        corrects = [float(v["is_correct"]) for v in items.values()]
        results[model] = spearman_with_ci(confs, corrects)
    return results


# ---------------------------------------------------------------------------
# Placeholder for parts 2-5 (will be added incrementally)
# ---------------------------------------------------------------------------

def generate_visualizations(data, cal_stats, fb_stats, cal_metrics,
                            fb_metrics, mech_stats, bridge_corr,
                            cal_stats_clean, fb_stats_clean):
    """Generate all PNG visualizations. (Part 2)"""
    pass  # Will be implemented next


def generate_backgrounder(output_path):
    """Generate stats theoretical backgrounder markdown. (Part 3)"""
    pass  # Will be implemented next


def generate_docx_report(output_path, data, cal_stats, fb_stats,
                         cal_metrics, fb_metrics, mech_stats, bridge_corr,
                         cal_stats_clean, fb_stats_clean):
    """Generate polished .docx results report. (Part 4)"""
    pass  # Will be implemented next


def generate_reproducibility_log(output_path):
    """Generate reproducibility log markdown. (Part 5)"""
    pass  # Will be implemented next


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("MetaJudge v0.5.5.1 — Statistical Analysis Report Generator")
    print("=" * 60)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load data
    print("\n[1/6] Loading data...")
    data = load_all_data()
    n_cal = len(set(r["item_id"] for r in data["cal_rows"]))
    n_fb = len(set(r["item_id"] for r in data["fb_rows"]))
    print(f"  Calibration: {n_cal} items, {len(data['cal_by_model'])} models")
    print(f"  Family B: {n_fb} items, {len(data['fb_by_model'])} models")
    print(f"  Flagged items: {len(data['flagged_items'])}")

    # Step 2: Run statistics (full set)
    print("\n[2/6] Running statistical tests (full set)...")
    cal_stats = run_calibration_stats(data["cal_by_model"])
    print(f"  Calibration pairwise: {len(cal_stats['pairwise'])} pairs, "
          f"{cal_stats['n_items']} items each")

    fb_stats = run_family_b_stats(data["fb_by_model"])
    print(f"  Family B pairwise: {len(fb_stats['pairwise'])} pairs, "
          f"{fb_stats['n_items']} items each")

    # Step 2b: Sensitivity analysis (clean subset)
    print("  Running sensitivity analysis (clean subset)...")
    cal_stats_clean = run_calibration_stats(data["cal_by_model"],
                                            item_filter=data["flagged_items"])
    fb_stats_clean = run_family_b_stats(data["fb_by_model"],
                                        item_filter=data["flagged_items"])
    print(f"  Clean cal: {cal_stats_clean['n_items']} items, "
          f"Clean FB: {fb_stats_clean['n_items']} items")

    # Step 3: Per-model metrics
    print("\n[3/6] Computing per-model metrics...")
    cal_metrics = compute_per_model_calibration_metrics(data["cal_by_model"])
    fb_metrics = compute_per_model_fb_metrics(data["fb_by_model"])
    mech_stats = compute_per_mechanism_stats(data["cal_by_model"])
    bridge_corr = compute_bridge_correlations(data["cal_by_model"])
    print(f"  Mechanisms: {len(mech_stats)}")
    print(f"  Bridge correlations: {len(bridge_corr)} models")

    # Step 4: Generate visualizations
    print("\n[4/6] Generating visualizations...")
    generate_visualizations(data, cal_stats, fb_stats, cal_metrics,
                            fb_metrics, mech_stats, bridge_corr,
                            cal_stats_clean, fb_stats_clean)

    # Step 5: Generate reports
    print("\n[5/6] Generating reports...")
    generate_backgrounder(OUTPUT_DIR / "metajudge_v0551_stats_backgrounder.md")
    generate_docx_report(OUTPUT_DIR / "metajudge_v0551_stats_report.docx",
                         data, cal_stats, fb_stats, cal_metrics, fb_metrics,
                         mech_stats, bridge_corr, cal_stats_clean, fb_stats_clean)

    # Step 6: Reproducibility log
    print("\n[6/6] Generating reproducibility log...")
    generate_reproducibility_log(OUTPUT_DIR / "metajudge_v0551_stats_reproducibility.md")

    print("\n" + "=" * 60)
    print("Done. Outputs in:", OUTPUT_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
