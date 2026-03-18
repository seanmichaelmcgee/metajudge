"""
MetaJudge-AGI: Strategy Adaptation Scoring Module
===================================================
Source: Framework §5.5.4, §7.2 (Strategy metrics)

Implements:
- Strategy-selection accuracy
- Improvement after strategy change
- Behavioral consistency (declared vs observed strategy)
- Diversity-adjusted strategy use
"""

from __future__ import annotations

from typing import Dict, List, Optional
from collections import Counter


def strategy_selection_accuracy(
    chosen_strategies: List[str],
    expected_strategies: List[Optional[str]],
) -> float:
    """Fraction of items where the chosen strategy matched the expected best strategy.
    
    Source: Framework §7.2
    """
    scoreable = [
        (c, e) for c, e in zip(chosen_strategies, expected_strategies)
        if e is not None
    ]
    if not scoreable:
        return float("nan")
    return float(sum(1 for c, e in scoreable if c == e) / len(scoreable))


def improvement_after_change(
    correct_before: List[bool],
    correct_after: List[bool],
    strategy_changed: List[bool],
) -> float:
    """Among items where strategy was changed, fraction that improved.
    
    Source: Framework §5.5.4, §7.2
    """
    changed = [
        (cb, ca) for cb, ca, sc in zip(correct_before, correct_after, strategy_changed)
        if sc
    ]
    if not changed:
        return float("nan")
    improved = sum(1 for cb, ca in changed if not cb and ca)
    return float(improved / len(changed))


def strategy_diversity(
    chosen_strategies: List[str],
    available_strategies: Optional[List[str]] = None,
) -> float:
    """Measure how diverse the model's strategy selections are.
    
    Returns normalized entropy of strategy distribution.
    A model that always picks the same strategy scores low.
    
    Source: Framework §5.5.4 - penalize "always selecting the same strategy"
    """
    import math
    
    if not chosen_strategies:
        return 0.0
    
    if available_strategies is None:
        available_strategies = ["recall", "stepwise", "decompose", "verify_first", "decline"]
    
    counts = Counter(chosen_strategies)
    total = len(chosen_strategies)
    n_categories = len(available_strategies)
    
    if n_categories <= 1:
        return 1.0
    
    # Shannon entropy
    entropy = 0.0
    for strategy in available_strategies:
        p = counts.get(strategy, 0) / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    # Normalize by max entropy
    max_entropy = math.log2(n_categories)
    return float(entropy / max_entropy) if max_entropy > 0 else 0.0


def behavioral_consistency_single(
    declared_strategy: str,
    observed_behavior_tags: List[str],
) -> float:
    """Score whether the declared strategy matches observed behavior.
    
    This is a placeholder for what would ideally be a judge-model check.
    For now, uses simple heuristic matching.
    
    Source: Framework §5.5.4 - "strategy labels that do not match actual behavior"
    """
    # Map strategies to expected behavioral indicators
    strategy_indicators: Dict[str, List[str]] = {
        "recall": ["direct_answer", "no_computation", "from_memory"],
        "stepwise": ["step_by_step", "shows_work", "sequential"],
        "decompose": ["subproblems", "breakdown", "parts"],
        "verify_first": ["checks_premises", "validates", "verification"],
        "decline": ["abstains", "insufficient_info", "cannot_determine"],
    }
    
    expected = strategy_indicators.get(declared_strategy, [])
    if not expected or not observed_behavior_tags:
        return 0.5  # neutral when we can't assess
    
    overlap = set(expected) & set(observed_behavior_tags)
    return float(len(overlap) / len(expected)) if expected else 0.5


def strategy_adaptation_composite(
    strategy_correct: bool,
    answer_correct_before: bool,
    answer_correct_after: bool,
    strategy_changed: bool,
    confidence_before: float,
    confidence_after: float,
) -> float:
    """Composite strategy adaptation score for a single item.
    
    Source: Framework §5.5.4
    """
    score = 0.0
    
    # Strategy selection quality (30%)
    if strategy_correct:
        score += 0.3
    
    # Task completion (30%)
    if answer_correct_after:
        score += 0.3
    
    # Adaptation quality (40%)
    if strategy_changed:
        if not answer_correct_before and answer_correct_after:
            score += 0.4  # successful adaptation
        elif answer_correct_before and answer_correct_after:
            score += 0.2  # unnecessary but harmless
        elif answer_correct_before and not answer_correct_after:
            score += 0.0  # harmful adaptation
        else:
            score += 0.1  # adapted but still wrong
    else:
        # Didn't change strategy
        if answer_correct_before:
            score += 0.35  # correctly held strategy
        else:
            score += 0.05  # should have adapted but didn't
    
    return max(0.0, min(1.0, score))
