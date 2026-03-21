"""
MetaJudge-AGI: Abstention and Deferral Scoring Module
======================================================
Source: Family B Scoring Spec (docs/family_b_scoring_spec.md)

Implements:
- Utility-based payoff matrix (4-action × 4-gold with correct/incorrect answer split)
- UWAA: Utility-Weighted Action Accuracy (primary metric)
- Per-class Action F1 (diagnostic metric)
- AUARC: Area Under Accuracy-Rejection Curve (global quality)
- Risk-coverage analysis
- Abstention precision
- False-answer-under-uncertainty rate
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Utility payoff matrix
# Source: Family B Scoring Spec §3
#
# Rows: predicted action (with answer split into correct/incorrect)
# Columns: gold action
# Order: answer, clarify, verify, abstain
# ---------------------------------------------------------------------------

ActionLabel = Literal["answer", "clarify", "verify", "abstain"]

_ACTIONS: List[str] = ["answer", "clarify", "verify", "abstain"]

# 5×4 matrix: rows = [answer_correct, answer_incorrect, clarify, verify, abstain]
#              cols = [answer, clarify, verify, abstain]
UTILITY_MATRIX: Dict[Tuple[str, str], float] = {
    # answer (correct) row
    ("answer_correct", "answer"):   +1.0,
    ("answer_correct", "clarify"):  +0.5,
    ("answer_correct", "verify"):   +0.5,
    ("answer_correct", "abstain"):  -0.5,
    # answer (incorrect) row
    ("answer_incorrect", "answer"):  -1.0,
    ("answer_incorrect", "clarify"): -0.5,
    ("answer_incorrect", "verify"):  -0.5,
    ("answer_incorrect", "abstain"): -0.5,
    # clarify row
    ("clarify", "answer"):   -0.2,
    ("clarify", "clarify"):  +1.0,
    ("clarify", "verify"):   +0.3,
    ("clarify", "abstain"):  +0.3,
    # verify row
    ("verify", "answer"):   -0.2,
    ("verify", "clarify"):  +0.3,
    ("verify", "verify"):   +1.0,
    ("verify", "abstain"):  +0.3,
    # abstain row
    ("abstain", "answer"):   -0.3,
    ("abstain", "clarify"):  +0.3,
    ("abstain", "verify"):   +0.3,
    ("abstain", "abstain"):  +1.0,
}

# Min/max possible utility for normalization
UTILITY_MIN = -1.0
UTILITY_MAX = +1.0


def decision_utility_single(
    decision: str,
    is_correct: bool,
    gold_action: str,
    confidence: float = 0.5,
) -> float:
    """Compute utility for a single item using the Family B payoff matrix.

    Args:
        decision: Model's predicted action ("answer", "clarify", "verify", "abstain").
        is_correct: Whether the model's answer is correct (only meaningful when
            decision="answer"; ignored otherwise).
        gold_action: The item's intended optimal action.
        confidence: Model's stated confidence (reserved for future use; currently
            unused in the utility lookup).

    Returns:
        Scalar utility in [−1.0, +1.0].
    """
    if decision == "answer":
        row_key = "answer_correct" if is_correct else "answer_incorrect"
    else:
        row_key = decision

    key = (row_key, gold_action)
    if key in UTILITY_MATRIX:
        return UTILITY_MATRIX[key]

    # Fallback for unknown combinations
    return 0.0


def compute_uwaa(utilities: List[float]) -> float:
    """Compute Utility-Weighted Action Accuracy (UWAA).

    UWAA normalises the mean per-item utility to [0, 1]:
        UWAA = (mean_utility − min) / (max − min)
             = (mean_utility + 1.0) / 2.0

    Args:
        utilities: List of per-item utility scores from decision_utility_single().

    Returns:
        UWAA score in [0.0, 1.0].  Returns 0.5 (neutral) if the list is empty.
    """
    if not utilities:
        return 0.5
    raw = float(np.mean(utilities))
    return (raw - UTILITY_MIN) / (UTILITY_MAX - UTILITY_MIN)


def compute_action_f1(
    predicted: List[str],
    gold: List[str],
) -> Dict[str, Dict[str, float]]:
    """Compute per-class precision, recall, F1 and macro F1.

    Args:
        predicted: List of predicted action labels.
        gold: List of gold action labels.

    Returns:
        Dictionary with per-class metrics and ``"macro"`` summary::

            {
                "answer":  {"precision": ..., "recall": ..., "f1": ...},
                "clarify": {"precision": ..., "recall": ..., "f1": ...},
                "verify":  {"precision": ..., "recall": ..., "f1": ...},
                "abstain": {"precision": ..., "recall": ..., "f1": ...},
                "macro":   {"precision": ..., "recall": ..., "f1": ...},
            }

        Undefined values (0/0) are reported as ``float('nan')``.
    """
    result: Dict[str, Dict[str, float]] = {}
    f1_values: List[float] = []
    prec_values: List[float] = []
    rec_values: List[float] = []

    for cls in _ACTIONS:
        tp = sum(1 for p, g in zip(predicted, gold) if p == cls and g == cls)
        fp = sum(1 for p, g in zip(predicted, gold) if p == cls and g != cls)
        fn = sum(1 for p, g in zip(predicted, gold) if p != cls and g == cls)

        precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        recall = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = float("nan")

        result[cls] = {"precision": precision, "recall": recall, "f1": f1}

        # Accumulate for macro average (only defined values)
        if not np.isnan(f1):
            f1_values.append(f1)
        if not np.isnan(precision):
            prec_values.append(precision)
        if not np.isnan(recall):
            rec_values.append(recall)

    result["macro"] = {
        "precision": float(np.mean(prec_values)) if prec_values else float("nan"),
        "recall": float(np.mean(rec_values)) if rec_values else float("nan"),
        "f1": float(np.mean(f1_values)) if f1_values else float("nan"),
    }
    return result


# ---------------------------------------------------------------------------
# Legacy / auxiliary metrics (preserved from original module)
# ---------------------------------------------------------------------------

def abstention_quality_binary(abstain: bool, answerable: bool) -> float:
    """Simple binary abstention quality.

    Returns 1.0 if the abstention decision matches answerability, 0.0 otherwise.
    """
    if abstain and not answerable:
        return 1.0
    if (not abstain) and answerable:
        return 1.0
    return 0.0


def abstention_precision(
    decisions: List[str],
    answerables: List[bool],
) -> float:
    """Precision of abstention: fraction of abstentions on non-answerable items.

    Counts both ``"abstain"`` and ``"verify"`` as abstention-like actions.
    """
    abstentions = [
        (d, a) for d, a in zip(decisions, answerables)
        if d in ("abstain", "verify")
    ]
    if not abstentions:
        return float("nan")
    correct_abstentions = sum(1 for _, a in abstentions if not a)
    return float(correct_abstentions / len(abstentions))


def false_answer_under_uncertainty_rate(
    decisions: List[str],
    answerables: List[bool],
    correctness: List[bool],
) -> float:
    """Rate of incorrect answers on non-answerable items."""
    non_answerable_answers = [
        c for d, a, c in zip(decisions, answerables, correctness)
        if not a and d == "answer"
    ]
    if not non_answerable_answers:
        return 0.0
    return float(sum(1 for c in non_answerable_answers if not c) / len(non_answerable_answers))


def risk_coverage_curve(
    confidences: List[float],
    correctness: List[bool],
    n_thresholds: int = 20,
) -> List[Tuple[float, float, float]]:
    """Compute risk-coverage curve data points.

    Returns list of (threshold, coverage, accuracy_above_threshold).
    """
    c = np.array(confidences, dtype=float)
    y = np.array(correctness, dtype=float)

    thresholds = np.linspace(0.0, 1.0, n_thresholds)
    curve = []

    for t in thresholds:
        mask = c >= t
        coverage = float(mask.sum() / len(c)) if len(c) > 0 else 0.0
        if mask.sum() > 0:
            accuracy = float(y[mask].mean())
        else:
            accuracy = float("nan")
        curve.append((float(t), coverage, accuracy))

    return curve


def compute_auarc(
    confidences: List[float],
    correctness: List[bool],
) -> float:
    """Compute Area Under Accuracy-Rejection Curve (AUARC).

    Items are sorted by confidence descending. For each coverage level
    k/N, accuracy is computed on the top-k most-confident items.  AUARC
    is the mean of these accuracy values (Riemann sum approximation).

    Args:
        confidences: Per-item confidence scores.
        correctness: Per-item correctness booleans.

    Returns:
        AUARC in [0.0, 1.0].  Returns NaN if inputs are empty.
    """
    if not confidences:
        return float("nan")

    c = np.array(confidences, dtype=float)
    y = np.array(correctness, dtype=float)

    # Sort by confidence descending
    order = np.argsort(-c)
    y_sorted = y[order]

    n = len(y_sorted)
    cumsum = np.cumsum(y_sorted)
    accuracies = cumsum / np.arange(1, n + 1)

    return float(np.mean(accuracies))
