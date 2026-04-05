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

import os
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import yaml


def _load_family_b_config():
    """Load Family B scoring config from YAML."""
    path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir,
        "config", "family_b_scoring.yaml"
    ))
    with open(path, "r") as f:
        return yaml.safe_load(f)["family_b"]

def _get_family_b_config():
    """Cached config accessor."""
    if not hasattr(_get_family_b_config, "_cache"):
        _get_family_b_config._cache = _load_family_b_config()
    return _get_family_b_config._cache

def _build_utility_matrix_from_config(config):
    """Build utility matrix dict from YAML config."""
    m = {}
    for row_key, cols in config["utility_matrix"].items():
        for col_key, val in cols.items():
            m[(row_key, col_key)] = float(val)
    return m


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
# Build from YAML config (single source of truth)
try:
    _FB_CONFIG = _get_family_b_config()
    UTILITY_MATRIX = _build_utility_matrix_from_config(_FB_CONFIG)
    UTILITY_MIN = float(_FB_CONFIG.get("utility_min", -1.0))
    UTILITY_MAX = float(_FB_CONFIG.get("utility_max", 1.0))
except (FileNotFoundError, KeyError):
    # Fallback: hardcoded defaults matching the scoring spec
    UTILITY_MATRIX = {
        ("answer_correct", "answer"): +1.0,
        ("answer_correct", "clarify"): +0.5,
        ("answer_correct", "verify"): +0.5,
        ("answer_correct", "abstain"): -0.5,
        ("answer_incorrect", "answer"): -1.0,
        ("answer_incorrect", "clarify"): -0.5,
        ("answer_incorrect", "verify"): -0.5,
        ("answer_incorrect", "abstain"): -0.5,
        ("clarify", "answer"): -0.2,
        ("clarify", "clarify"): +1.0,
        ("clarify", "verify"): +0.3,
        ("clarify", "abstain"): +0.3,
        ("verify", "answer"): -0.2,
        ("verify", "clarify"): +0.3,
        ("verify", "verify"): +1.0,
        ("verify", "abstain"): +0.3,
        ("abstain", "answer"): -0.3,
        ("abstain", "clarify"): +0.3,
        ("abstain", "verify"): +0.3,
        ("abstain", "abstain"): +1.0,
    }
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


# ---------------------------------------------------------------------------
# Family B v2 scoring — corrective answer support
# ---------------------------------------------------------------------------

def score_family_b_item_v2(
    model_decision: str,
    model_answer: str,
    is_correct: bool,
    gold_action: str,
    acceptable_actions: list = None,
    is_false_presupposition: bool = False,
) -> float:
    # DEPRECATED in v6.5: Use compute_family_b_score_v65() instead.
    # This function is retained for backward compatibility only.
    # Known issue: embedded matrix uses -0.5 for non-answer→answer cells
    # (spec says -0.2/-0.3) and uses (gold, predicted) convention instead
    # of (predicted, gold). See CJ-004 in v62_to_v65_changelog.md.
    """Score a Family B item with corrective-answer support.

    Changes from v1:
    - If the item is a false presupposition and the model gave a corrective answer
      (decision="answer" but the answer corrects the premise), award +0.5 instead of -0.5
    - If the model's decision is in acceptable_actions, use the better of
      the standard utility or 0.3 (partial credit)

    Args:
        model_decision: The model's chosen action (answer/clarify/verify/abstain)
        model_answer: The model's answer text (for corrective detection)
        is_correct: Whether the model's factual answer was correct (if applicable)
        gold_action: The intended gold action
        acceptable_actions: List of acceptable actions for this item
        is_false_presupposition: Whether this item has a false premise

    Returns:
        Utility score in [-1.0, +1.0]
    """
    if acceptable_actions is None:
        acceptable_actions = [gold_action]

    # Standard utility matrix (same as v1)
    UTILITY = {
        ("answer_correct", "answer"): +1.0,
        ("answer_correct", "clarify"): +0.5,
        ("answer_correct", "verify"): +0.5,
        ("answer_correct", "abstain"): -0.5,
        ("answer_incorrect", "answer"): -1.0,
        ("answer_incorrect", "clarify"): -0.5,
        ("answer_incorrect", "verify"): -0.5,
        ("answer_incorrect", "abstain"): -0.5,
        ("clarify", "answer"): -0.5,
        ("clarify", "clarify"): +1.0,
        ("clarify", "verify"): +0.3,
        ("clarify", "abstain"): +0.3,
        ("verify", "answer"): -0.5,
        ("verify", "clarify"): +0.3,
        ("verify", "verify"): +1.0,
        ("verify", "abstain"): +0.3,
        ("abstain", "answer"): -0.5,
        ("abstain", "clarify"): +0.3,
        ("abstain", "verify"): +0.3,
        ("abstain", "abstain"): +1.0,
    }

    # Determine the row key
    if gold_action == "answer":
        row = "answer_correct" if is_correct else "answer_incorrect"
    else:
        row = gold_action

    # Standard utility lookup
    standard_utility = UTILITY.get((row, model_decision), -0.5)

    # === CORRECTIVE ANSWER HANDLING ===
    # If this is a false presupposition item and the model chose "answer",
    # check if the answer is corrective (identifies the false premise)
    if is_false_presupposition and model_decision == "answer":
        corrective_indicators = [
            "false", "incorrect", "not true", "no such", "did not",
            "doesn't exist", "does not exist", "never", "premise",
            "assumption", "there is no", "there are no", "there was no",
            "not applicable", "n/a", "cannot", "impossible",
            "none", "zero", "the question is wrong",
        ]
        answer_lower = (model_answer or "").lower()
        is_corrective = any(ind in answer_lower for ind in corrective_indicators)

        if is_corrective:
            # Corrective answer on false premise: this is GOOD behavior
            return +0.5  # partial credit (full credit goes to abstain)

    # === ACCEPTABLE ALTERNATIVE HANDLING ===
    # If the model's decision is in the acceptable alternatives, give at least partial credit
    if model_decision in acceptable_actions and model_decision != gold_action:
        return max(standard_utility, 0.3)  # at least partial credit

    return standard_utility


# ---------------------------------------------------------------------------
# v6.5 scoring functions — config-driven, structured output
# ---------------------------------------------------------------------------

def compute_family_b_score_v65(
    model_decision: str,
    model_answer: str,
    gold_action: str,
    content_correct: bool,
    acceptable_actions: Optional[List[str]] = None,
    is_false_presupposition: bool = False,
    ambiguity: Optional[str] = None,
    config: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Score a Family B item using v6.5 config-driven matrix.

    Returns structured dict instead of bare float.
    Uses (predicted_row, gold_col) convention matching the spec.
    """
    if acceptable_actions is None:
        acceptable_actions = [gold_action]

    cfg = config or _get_family_b_config()
    matrix = _build_utility_matrix_from_config(cfg)

    # Determine row key based on model's decision
    if model_decision == "answer":
        row_key = "answer_correct" if content_correct else "answer_incorrect"
    else:
        row_key = model_decision

    # Base utility from matrix: (predicted, gold)
    base_utility = matrix.get((row_key, gold_action), -0.5)

    utility = base_utility
    method = f"matrix[({row_key}, {gold_action})]"

    # Corrective answer handling (false presupposition items)
    if is_false_presupposition and model_decision == "answer":
        corrective_indicators = [
            "false", "incorrect", "not true", "no such", "did not",
            "doesn't exist", "does not exist", "never", "premise",
            "assumption", "there is no", "there are no", "there was no",
            "not applicable", "n/a", "cannot", "impossible",
            "none", "zero", "the question is wrong",
        ]
        answer_lower = (model_answer or "").lower()
        is_corrective = any(ind in answer_lower for ind in corrective_indicators)
        if is_corrective:
            credit = cfg.get("corrective_answer_credit", 0.5)
            utility = credit
            method = "corrective_answer"

    # Acceptable alternative handling
    if model_decision in acceptable_actions and model_decision != gold_action:
        floor = cfg.get("acceptable_alternative_floor", 0.3)
        if utility < floor:
            utility = floor
            method = f"acceptable_alt_floor({floor})"

    # Ambiguity handling
    if ambiguity and model_decision in ("verify", "abstain"):
        policy = cfg.get("ambiguous_item_policy", "accept_cautious")
        if policy == "accept_cautious":
            diag_utility = matrix.get((model_decision, model_decision), 1.0)
            utility = min(diag_utility, 0.8)
            method = f"ambiguous_{policy}"

    action_correct = (model_decision == gold_action or
                      model_decision in acceptable_actions)

    return {
        "utility": float(utility),
        "action_correct": action_correct,
        "content_correct": content_correct,
        "matrix_cell": f"({row_key}, {gold_action})",
        "method": method,
    }


def compute_baseline_answer_rate(items: List[Dict]) -> float:
    """Proportion of items whose gold_action is 'answer'."""
    if not items:
        return 0.0
    return sum(1 for it in items if it.get("gold_action") == "answer") / len(items)


def apply_answer_rate_penalty(
    utilities: List[float],
    decisions: List[str],
    baseline_answer_rate: float,
    config: Optional[Dict] = None,
) -> tuple:
    """Apply answer-rate penalty if model over-answers.

    Returns (adjusted_utilities, penalty_amount).
    """
    cfg = config or _get_family_b_config()
    penalty_cfg = cfg.get("answer_rate_penalty", {})

    if not penalty_cfg.get("enabled", False) or not decisions:
        return list(utilities), 0.0

    answer_rate = sum(1 for d in decisions if d == "answer") / len(decisions)
    threshold = penalty_cfg.get("threshold", 0.15)
    slope = penalty_cfg.get("slope", 2.0)
    max_penalty = penalty_cfg.get("max_penalty", 0.10)

    excess = answer_rate - baseline_answer_rate - threshold
    if excess <= 0:
        return list(utilities), 0.0

    penalty = min(slope * excess, max_penalty)
    adjusted = [u - penalty for u in utilities]
    return adjusted, float(penalty)
