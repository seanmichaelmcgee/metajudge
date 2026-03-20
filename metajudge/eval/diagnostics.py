"""Diagnostics and success criteria for MetaJudge calibration evaluation."""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd


def _json_safe(obj):
    """JSON serializer fallback for numpy/pandas types."""
    try:
        import numpy as np
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return str(obj)


def compute_model_summary(audit_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-model summary statistics from audit sweep results.

    Expected columns: model, item_id, is_correct, confidence, brier_score
    Returns DataFrame with one row per model.
    """
    summaries = []
    for model, group in audit_df.groupby("model"):
        n = len(group)
        correct = group["is_correct"].sum()
        accuracy = correct / n if n > 0 else 0
        headline = group["brier_score"].mean()
        mean_conf = group["confidence"].mean()

        # ECE: binned calibration error
        ece = _compute_ece(group)

        # Overconfidence rate: wrong with conf > 0.8
        wrong = group[~group["is_correct"]]
        overconf = (wrong["confidence"] > 0.8).sum() if len(wrong) > 0 else 0
        overconf_rate = overconf / n if n > 0 else 0

        summaries.append({
            "model": model,
            "n_items": n,
            "correct": int(correct),
            "accuracy": round(accuracy, 4),
            "headline_score": round(headline, 4),
            "mean_confidence": round(mean_conf, 4),
            "ece": round(ece, 4),
            "overconfidence_rate": round(overconf_rate, 4),
            "overconfident_wrong": int(overconf),
        })

    return pd.DataFrame(summaries)


def _compute_ece(df: pd.DataFrame, n_bins: int = 10) -> float:
    """Expected Calibration Error with equal-width bins."""
    bins = defaultdict(list)
    for _, row in df.iterrows():
        bin_idx = min(int(row["confidence"] * n_bins), n_bins - 1)
        bins[bin_idx].append(row)

    ece = 0.0
    total = len(df)
    for bin_items in bins.values():
        if not bin_items:
            continue
        avg_conf = sum(r["confidence"] for r in bin_items) / len(bin_items)
        avg_acc = sum(1 for r in bin_items if r["is_correct"]) / len(bin_items)
        ece += abs(avg_conf - avg_acc) * len(bin_items) / total

    return ece


def compute_discrimination(audit_df: pd.DataFrame) -> pd.DataFrame:
    """Find items where models disagree on correctness.

    Returns DataFrame of discriminating items with agreement stats.
    """
    items = []
    for item_id, group in audit_df.groupby("item_id"):
        n_models = group["model"].nunique()
        n_correct = group["is_correct"].sum()
        if 0 < n_correct < n_models:  # disagreement
            items.append({
                "item_id": item_id,
                "n_models": n_models,
                "n_correct": int(n_correct),
                "n_wrong": int(n_models - n_correct),
                "models_correct": ", ".join(group[group["is_correct"]]["model"].tolist()),
                "models_wrong": ", ".join(group[~group["is_correct"]]["model"].tolist()),
            })

    return pd.DataFrame(items).sort_values("n_wrong", ascending=False) if items else pd.DataFrame()


def compute_success_criteria(
    audit_df: pd.DataFrame,
    mechanism_col: str = "mechanism_primary",
) -> dict:
    """Compute C1-C5 success criteria from audit data.

    Returns dict with criteria, measured values, and pass/fail.
    """
    models = audit_df["model"].unique()

    # Per-model headlines
    model_scores = {}
    for model in models:
        mdf = audit_df[audit_df["model"] == model]
        model_scores[model] = mdf["brier_score"].mean()

    scores = list(model_scores.values())

    # C1: Brier spread >= 0.05
    c1_spread = max(scores) - min(scores) if scores else 0

    # C2: High-deception mechanisms < 80% accuracy on >= 3 models
    c2_mechs = {"AmbiguityMetacognition", "Anchoring", "Prototype", "RLHF"}
    c2_under = 0
    c2_details = {}
    for model in models:
        mdf = audit_df[(audit_df["model"] == model) & (audit_df[mechanism_col].isin(c2_mechs))]
        if len(mdf) > 0:
            acc = mdf["is_correct"].mean() * 100
            c2_details[model] = round(acc, 1)
            if acc < 80:
                c2_under += 1

    # C3: High-adversarial mechanisms < 70% accuracy on >= 3 models
    c3_mechs = {"IOED", "Compositional", "CodeExecution", "ModifiedCRT"}
    c3_under = 0
    c3_details = {}
    for model in models:
        mdf = audit_df[(audit_df["model"] == model) & (audit_df[mechanism_col].isin(c3_mechs))]
        if len(mdf) > 0:
            acc = mdf["is_correct"].mean() * 100
            c3_details[model] = round(acc, 1)
            if acc < 70:
                c3_under += 1

    # C4: Items with conf-acc gap > 0.20 >= 10
    gap_items = set()
    for _, row in audit_df.iterrows():
        outcome = 1.0 if row["is_correct"] else 0.0
        if abs(row["confidence"] - outcome) > 0.20:
            gap_items.add(row["item_id"])

    # C5: ECE range >= 0.03
    model_eces = {}
    for model in models:
        mdf = audit_df[audit_df["model"] == model]
        model_eces[model] = _compute_ece(mdf)
    ece_vals = list(model_eces.values())
    c5_range = max(ece_vals) - min(ece_vals) if ece_vals else 0

    criteria = {
        "C1": {"name": "Brier spread", "threshold": ">= 0.05", "measured": round(c1_spread, 4),
                "pass": c1_spread >= 0.05, "details": {k: round(v, 4) for k, v in model_scores.items()}},
        "C2": {"name": "Deception < 80%", "threshold": ">= 3 models", "measured": c2_under,
                "pass": c2_under >= 3, "details": c2_details},
        "C3": {"name": "Adversarial < 70%", "threshold": ">= 3 models", "measured": c3_under,
                "pass": c3_under >= 3, "details": c3_details},
        "C4": {"name": "Conf-acc gap items", "threshold": ">= 10", "measured": len(gap_items),
                "pass": len(gap_items) >= 10},
        "C5": {"name": "ECE range", "threshold": ">= 0.03", "measured": round(c5_range, 4),
                "pass": c5_range >= 0.03, "details": {k: round(v, 4) for k, v in model_eces.items()}},
    }

    n_pass = sum(1 for c in criteria.values() if c["pass"])

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_models": len(models),
        "models": list(models),
        "criteria": criteria,
        "total_pass": n_pass,
        "total_criteria": 5,
        "verdict": "FREEZE" if n_pass >= 4 else ("REPLACE" if n_pass == 3 else "NEEDS_WORK"),
    }


def export_artifacts(
    audit_df: pd.DataFrame,
    output_dir: str | Path = "outputs/audit",
    tag: Optional[str] = None,
) -> dict:
    """Export all audit artifacts to structured files.

    Returns dict of file paths written.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = tag or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    paths = {}

    # Per-item audit CSV
    audit_path = output_dir / f"per_item_audit_{ts}.csv"
    audit_df.to_csv(audit_path, index=False)
    paths["per_item_audit"] = str(audit_path)

    # Model summary
    summary = compute_model_summary(audit_df)
    summary_path = output_dir / f"model_summary_{ts}.csv"
    summary.to_csv(summary_path, index=False)
    paths["model_summary"] = str(summary_path)

    # Discrimination report
    disc = compute_discrimination(audit_df)
    if len(disc) > 0:
        disc_path = output_dir / f"discrimination_{ts}.csv"
        disc.to_csv(disc_path, index=False)
        paths["discrimination"] = str(disc_path)

    # Success criteria verdict
    verdict = compute_success_criteria(audit_df)
    verdict_path = output_dir / f"verdict_{ts}.json"
    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=_json_safe)
    paths["verdict"] = str(verdict_path)

    return paths
