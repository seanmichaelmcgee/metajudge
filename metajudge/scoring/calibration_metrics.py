"""
MetaJudge-AGI: Calibration Scoring Module
==========================================
Source: Framework §5.1.5, §7.2 (Calibration metrics)

Implements:
- Brier score
- Expected Calibration Error (ECE)
- Overconfidence rate and penalty
- Accuracy-by-confidence-bucket analysis
- Calibration-aware composite score
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np


def brier_score(confidences: List[float], correctness: List[bool]) -> float:
    """Compute mean Brier score across items.
    
    Lower is better. Range [0, 1].
    Source: Framework §7.2
    """
    c = np.array(confidences, dtype=float)
    y = np.array(correctness, dtype=float)
    return float(np.mean((c - y) ** 2))


def brier_component_single(confidence: float, is_correct: bool) -> float:
    """Brier score for a single item."""
    target = 1.0 if is_correct else 0.0
    return float((confidence - target) ** 2)


def expected_calibration_error(
    confidences: List[float],
    correctness: List[bool],
    n_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE).
    
    Partitions predictions into bins by confidence, then measures
    the weighted average gap between confidence and accuracy per bin.
    
    Source: Framework §7.2
    """
    c = np.array(confidences, dtype=float)
    y = np.array(correctness, dtype=float)
    
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total = len(c)
    
    if total == 0:
        return 0.0
    
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (c >= lo) & (c <= hi)
        else:
            mask = (c >= lo) & (c < hi)
        
        bin_count = int(mask.sum())
        if bin_count == 0:
            continue
        
        bin_confidence = float(c[mask].mean())
        bin_accuracy = float(y[mask].mean())
        ece += (bin_count / total) * abs(bin_accuracy - bin_confidence)
    
    return float(ece)


def overconfidence_rate(
    confidences: List[float],
    correctness: List[bool],
    threshold: float = 0.8,
) -> float:
    """Fraction of incorrect answers where confidence exceeded threshold.
    
    Source: Framework §5.1.5 - "confident wrong answers should be penalized
    much more heavily than low-confidence wrong answers"
    """
    incorrect_confs = [
        c for c, correct in zip(confidences, correctness) if not correct
    ]
    if not incorrect_confs:
        return 0.0
    return float(sum(1 for c in incorrect_confs if c >= threshold) / len(incorrect_confs))


def overconfidence_penalty_single(confidence: float, is_correct: bool) -> float:
    """Penalty for a single overconfident wrong answer.
    
    Returns confidence value as penalty when wrong, 0 when correct.
    Source: Notebook Sketch Cell 9
    """
    if is_correct:
        return 0.0
    return float(confidence)


def accuracy_by_confidence_bucket(
    confidences: List[float],
    correctness: List[bool],
    n_bins: int = 10,
) -> List[Tuple[float, float, int]]:
    """Return (mean_confidence, mean_accuracy, count) per bucket.
    
    Source: Framework §7.2
    """
    c = np.array(confidences, dtype=float)
    y = np.array(correctness, dtype=float)
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    
    buckets = []
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (c >= lo) & (c <= hi)
        else:
            mask = (c >= lo) & (c < hi)
        
        count = int(mask.sum())
        if count == 0:
            buckets.append((float((lo + hi) / 2), float("nan"), 0))
        else:
            buckets.append((float(c[mask].mean()), float(y[mask].mean()), count))
    
    return buckets


def calibration_aware_score(is_correct: bool, confidence: float) -> float:
    """Per-item calibration score based on the Brier scoring rule.

    Returns 1 - (confidence - outcome)^2, an affine transform of the
    per-item Brier loss that is higher-is-better and ranges [0, 1].

    This is a strictly proper scoring rule: the expected score is
    uniquely maximized when stated confidence equals the true probability
    of correctness (Brier 1950; Gneiting & Raftery 2007).

    Source: planning/scoring_plan.md §2
    """
    y = 1.0 if is_correct else 0.0
    return float(1.0 - (confidence - y) ** 2)


def coverage_conditioned_accuracy(confidences, correctness, threshold=0.5):
    """Accuracy on items where confidence exceeds threshold.

    Source: v1_architecture.md §4 diagnostics
    """
    import numpy as np
    c = np.array(confidences, dtype=float)
    y = np.array(correctness, dtype=float)
    mask = c >= threshold
    if mask.sum() == 0:
        return float("nan")
    return float(y[mask].mean())
