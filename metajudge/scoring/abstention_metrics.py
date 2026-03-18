"""
MetaJudge-AGI: Abstention and Deferral Scoring Module
======================================================
Source: Framework §5.2.5, §7.2 (Decision metrics)

Implements:
- Utility-based reward matrix
- Risk-coverage analysis
- Abstention precision
- False-answer-under-uncertainty rate
- Risk-aware utility score
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Decision-theoretic reward matrix
# Source: Framework §5.2.5
# ---------------------------------------------------------------------------

# Default reward values — these should be tuned after pilot runs
DEFAULT_REWARD_MATRIX: Dict[str, float] = {
    "correct_answer_on_answerable": 1.0,           # strong positive
    "abstain_on_answerable": -0.3,                  # modest penalty
    "wrong_answer_on_answerable": -0.5,             # moderate penalty
    "wrong_answer_on_underspecified": -0.8,          # stronger penalty
    "ask_correct_on_underspecified": 0.7,            # positive reward
    "abstain_on_unreliable": 0.6,                    # positive reward
    "confident_hallucination_on_impossible": -1.0,   # largest penalty
}


def decision_utility_single(
    decision: Literal["answer", "ask", "abstain", "verify"],
    is_correct: bool,
    answerable: bool,
    ambiguity_class: str = "clear",
    confidence: float = 0.5,
    reward_matrix: Optional[Dict[str, float]] = None,
) -> float:
    """Compute utility for a single decision on one item.
    
    Source: Framework §5.2.5 - decision-theoretic reward matrix
    """
    rm = reward_matrix or DEFAULT_REWARD_MATRIX
    
    if answerable:
        if decision == "answer" and is_correct:
            return rm["correct_answer_on_answerable"]
        elif decision == "answer" and not is_correct:
            return rm["wrong_answer_on_answerable"]
        elif decision in ("abstain", "verify"):
            return rm["abstain_on_answerable"]
        elif decision == "ask":
            return rm["abstain_on_answerable"]  # treat ask like abstain on answerable
    else:
        # Not answerable: underspecified or unreliable
        if decision == "answer":
            if ambiguity_class == "underspecified":
                return rm["wrong_answer_on_underspecified"]
            else:
                # Adversarial / impossible
                penalty = rm["confident_hallucination_on_impossible"]
                return penalty * confidence  # scale by confidence
        elif decision == "ask" and ambiguity_class == "underspecified":
            return rm["ask_correct_on_underspecified"]
        elif decision in ("abstain", "verify"):
            return rm["abstain_on_unreliable"]
    
    return 0.0


def abstention_quality_binary(abstain: bool, answerable: bool) -> float:
    """Simple binary abstention quality.
    
    Source: Notebook Sketch Cell 9
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
    """Precision of abstention: fraction of abstentions that were on non-answerable items.
    
    Source: Framework §7.2
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
    """Rate of incorrect answers on non-answerable items.
    
    Source: Framework §7.2
    """
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
    Source: Framework §7.2
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
