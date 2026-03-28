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
    """Generate all PNG visualizations."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", font_scale=1.1)
    COLORS = sns.color_palette("tab10", n_colors=len(cal_metrics))
    model_order = sorted(cal_metrics.keys(), key=lambda m: short_name(m))
    model_colors = {m: COLORS[i] for i, m in enumerate(model_order)}

    # --- 1. Calibration reliability diagram ---
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect calibration")
    for model in model_order:
        bins = cal_metrics[model]["reliability_bins"]
        confs = [b[0] for b in bins if b[2] > 0]
        accs = [b[1] for b in bins if b[2] > 0]
        ax.plot(confs, accs, "o-", color=model_colors[model],
                label=short_name(model), markersize=6)
    ax.set_xlabel("Mean Predicted Confidence")
    ax.set_ylabel("Observed Accuracy")
    ax.set_title("Calibration Reliability Diagram")
    ax.legend(loc="lower right", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cal_reliability_diagram.png", dpi=150)
    plt.close(fig)
    print("  [1/11] cal_reliability_diagram.png")

    # --- 2. Brier score forest plot ---
    pairs = list(cal_stats["pairwise"].keys())
    fig, ax = plt.subplots(figsize=(10, max(4, len(pairs) * 0.5)))
    y_pos = list(range(len(pairs)))
    for i, pair in enumerate(pairs):
        d = cal_stats["pairwise"][pair]
        ci = d["bootstrap_ci"]
        ax.errorbar(ci["observed_diff"], i,
                    xerr=[[ci["observed_diff"] - ci["ci_lower"]],
                          [ci["ci_upper"] - ci["observed_diff"]]],
                    fmt="o", color="steelblue", capsize=4, markersize=6)
    ax.axvline(0, color="red", linestyle="--", alpha=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(pairs, fontsize=9)
    ax.set_xlabel("Brier Score Difference (A − B)")
    ax.set_title("Pairwise Brier Score Differences with 95% Bootstrap CI")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cal_brier_forest_plot.png", dpi=150)
    plt.close(fig)
    print("  [2/11] cal_brier_forest_plot.png")

    # --- 3. Per-mechanism accuracy heatmap ---
    mechanisms = sorted(mech_stats.keys())
    models_sorted = model_order
    acc_matrix = []
    for mech in mechanisms:
        row = [mech_stats[mech].get(m, {}).get("accuracy", float("nan"))
               for m in models_sorted]
        acc_matrix.append(row)
    acc_arr = np.array(acc_matrix)

    fig, ax = plt.subplots(figsize=(10, max(5, len(mechanisms) * 0.6)))
    sns.heatmap(acc_arr, annot=True, fmt=".2f", cmap="RdYlGn",
                xticklabels=[short_name(m) for m in models_sorted],
                yticklabels=mechanisms, ax=ax, vmin=0, vmax=1,
                linewidths=0.5)
    ax.set_title("Accuracy by Mechanism × Model")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cal_mechanism_heatmap.png", dpi=150)
    plt.close(fig)
    print("  [3/11] cal_mechanism_heatmap.png")

    # --- 4. Per-mechanism Brier bars ---
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(mechanisms))
    width = 0.15
    for i, model in enumerate(models_sorted):
        vals = [mech_stats[mech].get(model, {}).get("mean_brier", 0)
                for mech in mechanisms]
        ax.bar(x + i * width, vals, width, label=short_name(model),
               color=model_colors[model])
    ax.set_xticks(x + width * (len(models_sorted) - 1) / 2)
    ax.set_xticklabels(mechanisms, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Mean Brier Score")
    ax.set_title("Mean Brier Score by Mechanism × Model")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cal_mechanism_brier_bars.png", dpi=150)
    plt.close(fig)
    print("  [4/11] cal_mechanism_brier_bars.png")

    # --- 5. Calibration p-value heatmap ---
    pair_names = list(cal_stats["pairwise"].keys())
    test_types = ["McNemar (acc)", "Permutation (Brier)"]
    pval_matrix = []
    for pair in pair_names:
        d = cal_stats["pairwise"][pair]
        pval_matrix.append([d["mcnemar"]["p_value"], d["permutation"]["p_value"]])
    pval_arr = np.array(pval_matrix)

    fig, ax = plt.subplots(figsize=(6, max(4, len(pair_names) * 0.5)))
    sns.heatmap(pval_arr, annot=True, fmt=".3f", cmap="RdYlGn_r",
                xticklabels=test_types, yticklabels=pair_names,
                ax=ax, vmin=0, vmax=0.2, linewidths=0.5)
    ax.set_title("Calibration P-values (darker = more significant)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cal_pvalue_heatmap.png", dpi=150)
    plt.close(fig)
    print("  [5/11] cal_pvalue_heatmap.png")

    # --- 6. Family B action distribution ---
    fb_model_order = sorted(fb_metrics.keys(), key=lambda m: short_name(m))
    actions = ["answer", "clarify", "verify", "abstain"]
    action_colors = {"answer": "#4CAF50", "clarify": "#2196F3",
                     "verify": "#FF9800", "abstain": "#F44336"}

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(fb_model_order))
    for action in actions:
        vals = [fb_metrics[m]["action_dist"].get(action, 0) for m in fb_model_order]
        ax.bar([short_name(m) for m in fb_model_order], vals, bottom=bottom,
               label=action, color=action_colors[action])
        bottom += np.array(vals)
    ax.set_ylabel("Proportion")
    ax.set_title("Action Distribution by Model (Family B)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fb_action_distribution.png", dpi=150)
    plt.close(fig)
    print("  [6/11] fb_action_distribution.png")

    # --- 7. Family B action confusion heatmaps ---
    # One subplot per model (exclude models with <10 items)
    fb_models_full = [m for m in fb_model_order if fb_metrics[m]["n_items"] >= 10]
    n_models = len(fb_models_full)
    fig, axes = plt.subplots(1, n_models, figsize=(4 * n_models, 4))
    if n_models == 1:
        axes = [axes]
    for idx, model in enumerate(fb_models_full):
        items = data["fb_by_model"][model]
        conf_mat = np.zeros((4, 4), dtype=int)
        for v in items.values():
            gi = actions.index(v["gold_action"]) if v["gold_action"] in actions else -1
            di = actions.index(v["model_decision"]) if v["model_decision"] in actions else -1
            if gi >= 0 and di >= 0:
                conf_mat[gi][di] += 1
        sns.heatmap(conf_mat, annot=True, fmt="d", cmap="Blues",
                    xticklabels=actions, yticklabels=actions,
                    ax=axes[idx], linewidths=0.5)
        axes[idx].set_title(short_name(model), fontsize=10)
        axes[idx].set_xlabel("Model Decision")
        axes[idx].set_ylabel("Gold Action")
    fig.suptitle("Action Confusion Matrices (Family B)", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fb_action_confusion.png", dpi=150)
    plt.close(fig)
    print("  [7/11] fb_action_confusion.png")

    # --- 8. Family B utility forest plot ---
    if fb_stats["pairwise"]:
        fb_pairs = list(fb_stats["pairwise"].keys())
        fig, ax = plt.subplots(figsize=(10, max(4, len(fb_pairs) * 0.5)))
        for i, pair in enumerate(fb_pairs):
            d = fb_stats["pairwise"][pair]
            ci = d["bootstrap_ci"]
            ax.errorbar(ci["observed_diff"], i,
                        xerr=[[ci["observed_diff"] - ci["ci_lower"]],
                              [ci["ci_upper"] - ci["observed_diff"]]],
                        fmt="o", color="darkorange", capsize=4, markersize=6)
        ax.axvline(0, color="red", linestyle="--", alpha=0.5)
        ax.set_yticks(range(len(fb_pairs)))
        ax.set_yticklabels(fb_pairs, fontsize=9)
        ax.set_xlabel("Utility Difference (A − B)")
        ax.set_title("Pairwise Utility Differences with 95% Bootstrap CI (Family B)")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "fb_utility_forest_plot.png", dpi=150)
        plt.close(fig)
    print("  [8/11] fb_utility_forest_plot.png")

    # --- 9. Confidence distribution violin plots ---
    conf_data = []
    conf_labels = []
    for model in model_order:
        confs = [v["confidence"] for v in data["cal_by_model"][model].values()]
        conf_data.extend(confs)
        conf_labels.extend([short_name(model)] * len(confs))

    fig, ax = plt.subplots(figsize=(10, 6))
    import pandas as pd
    df_conf = pd.DataFrame({"Confidence": conf_data, "Model": conf_labels})
    sns.violinplot(data=df_conf, x="Model", y="Confidence", ax=ax,
                   palette="tab10", inner="quartile")
    ax.set_title("Confidence Distribution by Model (Calibration)")
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "bridge_confidence_violins.png", dpi=150)
    plt.close(fig)
    print("  [9/11] bridge_confidence_violins.png")

    # --- 10. Confidence-accuracy scatter with Spearman ---
    fig, ax = plt.subplots(figsize=(8, 6))
    for model in model_order:
        bins = cal_metrics[model]["reliability_bins"]
        confs = [b[0] for b in bins if b[2] > 0]
        accs = [b[1] for b in bins if b[2] > 0]
        rho = bridge_corr[model]["rho"]
        ax.plot(confs, accs, "o-", color=model_colors[model],
                label=f"{short_name(model)} (ρ={rho:.2f})", markersize=5)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title("Confidence vs Accuracy with Spearman ρ")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "bridge_confidence_accuracy.png", dpi=150)
    plt.close(fig)
    print("  [10/11] bridge_confidence_accuracy.png")

    # --- 11. Master significance heatmap ---
    all_pairs = list(cal_stats["pairwise"].keys())
    # Combine cal and FB test p-values
    test_cols = ["McNemar", "Brier Perm", "Utility Perm", "Stuart-Maxwell"]
    sig_matrix = []
    for pair in all_pairs:
        row = []
        cd = cal_stats["pairwise"].get(pair, {})
        row.append(cd.get("mcnemar", {}).get("p_value", float("nan")))
        row.append(cd.get("permutation", {}).get("p_value", float("nan")))
        fd = fb_stats["pairwise"].get(pair, {})
        row.append(fd.get("permutation", {}).get("p_value", float("nan")))
        row.append(fd.get("stuart_maxwell", {}).get("p_value", float("nan")))
        sig_matrix.append(row)
    sig_arr = np.array(sig_matrix)

    fig, ax = plt.subplots(figsize=(8, max(4, len(all_pairs) * 0.5)))
    sns.heatmap(sig_arr, annot=True, fmt=".3f", cmap="RdYlGn_r",
                xticklabels=test_cols, yticklabels=all_pairs,
                ax=ax, vmin=0, vmax=0.2, linewidths=0.5,
                mask=np.isnan(sig_arr))
    ax.set_title("Master Significance Heatmap (p-values)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "significance_master_heatmap.png", dpi=150)
    plt.close(fig)
    print("  [11/11] significance_master_heatmap.png")


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
