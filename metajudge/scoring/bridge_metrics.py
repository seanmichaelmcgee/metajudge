"""
MetaJudge-AGI: Bridge Layer Metrics
====================================
Links calibration (monitoring) and Family B (control) into a
monitoring-control coupling analysis.

Consumes audit DataFrames from both families and produces:
- per-model monitoring vs control summary
- confidence-band to action-quality mapping
- monitoring-control alignment flags
- failure-mode classification
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Confidence band classification
# ---------------------------------------------------------------------------

CONFIDENCE_BANDS = [
    ("very_low", 0.0, 0.3),
    ("low", 0.3, 0.5),
    ("moderate", 0.5, 0.7),
    ("high", 0.7, 0.85),
    ("very_high", 0.85, 0.95),
    ("extreme", 0.95, 1.01),
]


def classify_confidence_band(confidence: float) -> str:
    """Classify a confidence value into a named band."""
    for name, lo, hi in CONFIDENCE_BANDS:
        if lo <= confidence < hi:
            return name
    return "extreme"


# ---------------------------------------------------------------------------
# Monitoring quality (from calibration)
# ---------------------------------------------------------------------------

def compute_monitoring_summary(cal_audit: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute monitoring quality metrics from calibration audit data.

    Args:
        cal_audit: List of dicts with keys: item_id, confidence, is_correct, brier_score

    Returns:
        Dict with monitoring quality metrics.
    """
    if not cal_audit:
        return {"error": "no calibration data"}

    n = len(cal_audit)
    correct = [r for r in cal_audit if r.get("is_correct")]
    wrong = [r for r in cal_audit if not r.get("is_correct")]

    accuracy = len(correct) / n if n else 0
    mean_conf = np.mean([r["confidence"] for r in cal_audit])
    mean_brier = np.mean([r["brier_score"] for r in cal_audit])

    # Confidence discrimination: mean conf on correct vs wrong
    conf_correct = np.mean([r["confidence"] for r in correct]) if correct else 0
    conf_wrong = np.mean([r["confidence"] for r in wrong]) if wrong else 0
    discrimination = conf_correct - conf_wrong  # positive = good monitoring

    # Overconfidence rate: wrong + conf > 0.8
    overconf = [r for r in wrong if r["confidence"] > 0.8]
    overconf_rate = len(overconf) / len(wrong) if wrong else 0

    # ECE approximation
    ece = 0.0
    for name, lo, hi in CONFIDENCE_BANDS:
        band = [r for r in cal_audit if lo <= r["confidence"] < hi]
        if band:
            avg_conf = np.mean([r["confidence"] for r in band])
            avg_acc = np.mean([1.0 if r.get("is_correct") else 0.0 for r in band])
            ece += abs(avg_conf - avg_acc) * len(band) / n

    return {
        "n_items": n,
        "accuracy": round(accuracy, 4),
        "mean_confidence": round(float(mean_conf), 4),
        "mean_brier_score": round(float(mean_brier), 4),
        "confidence_discrimination": round(float(discrimination), 4),
        "overconfidence_rate": round(overconf_rate, 4),
        "ece": round(float(ece), 4),
    }


# ---------------------------------------------------------------------------
# Control quality (from Family B)
# ---------------------------------------------------------------------------

def compute_control_summary(fb_audit: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute control quality metrics from Family B audit data.

    Args:
        fb_audit: List of dicts with keys: item_id, gold_action, model_decision,
                  is_correct, utility, confidence

    Returns:
        Dict with control quality metrics.
    """
    if not fb_audit:
        return {"error": "no family B data"}

    n = len(fb_audit)
    utilities = [r["utility"] for r in fb_audit]
    mean_util = float(np.mean(utilities))

    # Action accuracy (exact match)
    action_correct = sum(1 for r in fb_audit if r["model_decision"] == r["gold_action"])
    action_accuracy = action_correct / n

    # Per-action breakdown
    per_action = {}
    for action in ["answer", "clarify", "verify", "abstain"]:
        items = [r for r in fb_audit if r["gold_action"] == action]
        if items:
            correct = sum(1 for r in items if r["model_decision"] == action)
            per_action[action] = {
                "n": len(items),
                "correct": correct,
                "accuracy": round(correct / len(items), 4),
                "mean_utility": round(float(np.mean([r["utility"] for r in items])), 4),
            }

    # Over-answering rate: model chose "answer" when it shouldn't have
    non_answer = [r for r in fb_audit if r["gold_action"] != "answer"]
    over_answer = sum(1 for r in non_answer if r["model_decision"] == "answer")
    over_answer_rate = over_answer / len(non_answer) if non_answer else 0

    return {
        "n_items": n,
        "mean_utility": round(mean_util, 4),
        "action_accuracy": round(action_accuracy, 4),
        "over_answer_rate": round(over_answer_rate, 4),
        "per_action": per_action,
    }


# ---------------------------------------------------------------------------
# Bridge: monitoring-control coupling
# ---------------------------------------------------------------------------

def compute_bridge_report(
    cal_audit: List[Dict[str, Any]],
    fb_audit: List[Dict[str, Any]],
    model_name: str = "unknown",
) -> Dict[str, Any]:
    """Compute the full bridge report linking monitoring to control.

    Args:
        cal_audit: Calibration audit rows (one model)
        fb_audit: Family B audit rows (one model)
        model_name: Model identifier

    Returns:
        Complete bridge report dict.
    """
    monitoring = compute_monitoring_summary(cal_audit)
    control = compute_control_summary(fb_audit)

    # Quadrant classification
    # Good monitoring = discrimination > 0.1 and ECE < 0.15
    # Good control = action_accuracy > 0.6 and mean_utility > 0.0
    good_monitoring = (
        monitoring.get("confidence_discrimination", 0) > 0.1
        and monitoring.get("ece", 1) < 0.15
    )
    good_control = (
        control.get("action_accuracy", 0) > 0.6
        and control.get("mean_utility", -1) > 0.0
    )

    if good_monitoring and good_control:
        quadrant = "monitoring_good_control_good"
    elif good_monitoring and not good_control:
        quadrant = "monitoring_good_control_bad"
    elif not good_monitoring and good_control:
        quadrant = "monitoring_bad_control_good"
    else:
        quadrant = "monitoring_bad_control_bad"

    # Confidence band to utility mapping (bridge signal)
    band_utility = {}
    for name, lo, hi in CONFIDENCE_BANDS:
        band_items = [r for r in fb_audit if lo <= r.get("confidence", 0.5) < hi]
        if band_items:
            band_utility[name] = {
                "n": len(band_items),
                "mean_utility": round(float(np.mean([r["utility"] for r in band_items])), 4),
                "action_dist": {},
            }
            for r in band_items:
                d = r["model_decision"]
                band_utility[name]["action_dist"][d] = band_utility[name]["action_dist"].get(d, 0) + 1

    # Failure mode classification
    failure_modes = {
        "overconfident_wrong_answer": 0,  # high conf + wrong + chose answer
        "correct_but_over_cautious": 0,   # would have been correct but abstained/verified
        "false_premise_not_caught": 0,    # false presup item + model answered within premise
        "unnecessary_clarification": 0,   # answerable item + model asked clarify
    }

    for r in fb_audit:
        conf = r.get("confidence", 0.5)
        if r["model_decision"] == "answer" and not r.get("is_correct") and conf > 0.8:
            failure_modes["overconfident_wrong_answer"] += 1
        if r["gold_action"] == "answer" and r["model_decision"] in ("abstain", "verify"):
            failure_modes["correct_but_over_cautious"] += 1
        if r.get("is_false_presupposition") and r["model_decision"] == "answer":
            # Check if it was a corrective answer or a premise-accepting answer
            # Heuristic: if utility is negative, they accepted the false premise
            if r["utility"] < 0:
                failure_modes["false_premise_not_caught"] += 1
        if r["gold_action"] == "answer" and r["model_decision"] == "clarify":
            failure_modes["unnecessary_clarification"] += 1

    return {
        "model": model_name,
        "monitoring": monitoring,
        "control": control,
        "quadrant": quadrant,
        "confidence_band_utility": band_utility,
        "failure_modes": failure_modes,
    }
