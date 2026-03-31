"""
MetaJudge-AGI: Self-Correction Scoring Module
===============================================
Source: Framework §5.3.4, §7.2 (Self-correction metrics)

Implements:
- Revision improvement rate
- Unnecessary revision rate
- Confidence change directionality
- Correction efficiency
"""

from __future__ import annotations

from typing import List, Optional, Tuple


def revision_improves_correctness(
    correct_before: bool,
    correct_after: bool,
    revised: bool,
) -> Optional[bool]:
    """Whether a revision improved correctness.
    
    Returns None if no revision was made.
    Source: Framework §5.3.4
    """
    if not revised:
        return None
    return (not correct_before) and correct_after


def unnecessary_revision(
    correct_before: bool,
    correct_after: bool,
    revised: bool,
) -> Optional[bool]:
    """Whether a revision was unnecessary (correct -> incorrect, or correct -> correct change).
    
    Source: Framework §5.3.4 - "avoid gratuitous revision when original was correct"
    """
    if not revised:
        return None
    return correct_before and not correct_after


def revision_improvement_rate(
    results: List[Tuple[bool, bool, bool]],
) -> float:
    """Fraction of revisions that improved correctness.
    
    Input: list of (correct_before, correct_after, revised) tuples
    Source: Framework §7.2
    """
    revisions = [(cb, ca) for cb, ca, r in results if r]
    if not revisions:
        return float("nan")
    improvements = sum(1 for cb, ca in revisions if not cb and ca)
    return float(improvements / len(revisions))


def unnecessary_revision_rate(
    results: List[Tuple[bool, bool, bool]],
) -> float:
    """Fraction of revisions on already-correct answers that made them wrong.
    
    Source: Framework §7.2
    """
    correct_revised = [(cb, ca) for cb, ca, r in results if r and cb]
    if not correct_revised:
        return float("nan")
    damaged = sum(1 for cb, ca in correct_revised if not ca)
    return float(damaged / len(correct_revised))


def confidence_directionality(
    confidence_before: float,
    confidence_after: float,
    correct_before: bool,
    correct_after: bool,
) -> str:
    """Classify whether confidence moved in the right direction.
    
    Source: Framework §5.3.4 - "whether confidence moves in the right direction"
    
    Returns one of:
    - "appropriate_increase": became correct, confidence went up
    - "appropriate_decrease": became wrong, confidence went down
    - "inappropriate_increase": became wrong, confidence went up
    - "inappropriate_decrease": became correct, confidence went down
    - "stable": confidence didn't change meaningfully
    """
    delta = confidence_after - confidence_before
    epsilon = 0.05  # threshold for meaningful change
    
    if abs(delta) < epsilon:
        return "stable"
    
    improved = (not correct_before) and correct_after
    worsened = correct_before and (not correct_after)
    
    if delta > 0:
        return "appropriate_increase" if improved else "inappropriate_increase"
    else:
        return "appropriate_decrease" if worsened else "inappropriate_decrease"


def correction_efficiency_score(
    correct_before: bool,
    correct_after: bool,
    revised: bool,
    confidence_before: float,
    confidence_after: float,
) -> float:
    """Composite correction efficiency score.
    
    Rewards: correct revision, appropriate confidence shift
    Penalizes: unnecessary revision, overconfident wrong revision
    Source: Framework §5.3.4, §7.2
    """
    if not revised:
        # No revision: small reward if already correct, neutral otherwise
        return 0.6 if correct_before else 0.3
    
    # Revision happened
    if not correct_before and correct_after:
        # Fixed an error — good
        base = 0.9
    elif correct_before and correct_after:
        # Changed but still correct — neutral/slight penalty
        base = 0.5
    elif correct_before and not correct_after:
        # Broke a correct answer — bad
        base = 0.1
    else:
        # Was wrong, still wrong after revision
        base = 0.2
    
    # Confidence direction bonus/penalty
    direction = confidence_directionality(
        confidence_before, confidence_after, correct_before, correct_after
    )
    if direction.startswith("appropriate"):
        base += 0.1
    elif direction.startswith("inappropriate"):
        base -= 0.1
    
    return max(0.0, min(1.0, base))
