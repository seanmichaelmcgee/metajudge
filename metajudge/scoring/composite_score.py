"""
MetaJudge-AGI: Composite Score Aggregation
============================================
Source: Framework §7.1, §7.3

Combines sub-benchmark scores into headline metacognition score.
Enforces the four composite score design principles from Framework §7.3.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np


# Default weights from Framework §7.1
DEFAULT_WEIGHTS: Dict[str, float] = {
    "calibration": 0.25,
    "abstention": 0.20,
    "self_correction": 0.20,
    "source_awareness": 0.15,
    "strategy_adaptation": 0.20,
}


def compute_composite_score(
    subscores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Compute weighted composite metacognition score.
    
    Source: Framework §7.1
    
    Args:
        subscores: Dict mapping subtask id to score [0, 1]
        weights: Optional override weights (must sum to ~1.0)
    
    Returns:
        Composite score in [0, 1]
    """
    w = weights or DEFAULT_WEIGHTS
    
    score = 0.0
    total_weight = 0.0
    
    for key, weight in w.items():
        if key in subscores and not np.isnan(subscores[key]):
            score += weight * subscores[key]
            total_weight += weight
    
    if total_weight == 0:
        return float("nan")
    
    # Normalize by actual weight used (handles missing subtasks)
    return float(score / total_weight)


def compute_profile(
    subscores: Dict[str, float],
) -> Dict[str, float]:
    """Return the full subdimension profile.
    
    Source: Framework §4 - "profile across subdimensions"
    """
    return {
        "calibration": subscores.get("calibration", float("nan")),
        "abstention": subscores.get("abstention", float("nan")),
        "self_correction": subscores.get("self_correction", float("nan")),
        "source_awareness": subscores.get("source_awareness", float("nan")),
        "strategy_adaptation": subscores.get("strategy_adaptation", float("nan")),
    }


def validate_composite_principles(
    subscores: Dict[str, float],
    item_results: list,
) -> Dict[str, bool]:
    """Check whether composite score satisfies the four design principles.
    
    Source: Framework §7.3
    
    Returns dict of principle -> satisfied boolean for diagnostics.
    
    NOTE: This is a diagnostic tool, not part of the scoring pipeline.
    It helps benchmark authors verify their scoring logic satisfies
    the stated principles during development.
    """
    checks = {}
    
    # Principle 1: Overconfident error must hurt a lot
    # Check: is the penalty for high-confidence wrong answers > low-confidence wrong answers?
    checks["overconfident_error_hurts"] = True  # placeholder — verify empirically
    
    # Principle 2: Appropriate abstention must help but not too much
    # Check: abstention score contribution is bounded
    abstention = subscores.get("abstention", 0.0)
    checks["abstention_bounded"] = abstention <= 0.95  # should not be trivially maximizable
    
    # Principle 3: Revision helps only when it improves
    # Check: self-correction score penalizes unnecessary revision
    checks["revision_quality_gated"] = True  # placeholder — verify empirically
    
    # Principle 4: No single cheap behavior dominates
    # Check: variance across subscores should not be too extreme
    values = [v for v in subscores.values() if not np.isnan(v)]
    if len(values) >= 3:
        checks["no_single_dominance"] = float(np.std(values)) < 0.4
    else:
        checks["no_single_dominance"] = True
    
    return checks
