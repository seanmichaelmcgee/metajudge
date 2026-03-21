"""
MetaJudge-AGI: Source Awareness Scoring Module
================================================
Source: Framework §5.4.5, §7.2 (Source-awareness metrics)

Implements:
- Answer correctness (separate from source scoring)
- Source-label accuracy
- Unsupported-source claims penalty
- Prompt-span evidence alignment
"""

from __future__ import annotations

from typing import List, Optional


def source_label_accuracy(
    predicted_labels: List[str],
    gold_labels: List[Optional[str]],
) -> float:
    """Fraction of items where the predicted source label matches gold.
    
    Skips items where gold label is None.
    Source: Framework §5.4.5, §7.2
    """
    scoreable = [
        (p, g) for p, g in zip(predicted_labels, gold_labels) if g is not None
    ]
    if not scoreable:
        return float("nan")
    return float(sum(1 for p, g in scoreable if p == g) / len(scoreable))


def source_label_accuracy_single(
    predicted: Optional[str],
    gold: Optional[str],
) -> float:
    """Single-item source label accuracy.
    
    Source: Notebook Sketch Cell 9
    """
    if gold is None:
        return float("nan")
    return 1.0 if predicted == gold else 0.0


def unsupported_certainty_penalty(
    source_label: str,
    confidence: float,
    gold_source: Optional[str],
    threshold: float = 0.7,
) -> float:
    """Penalty for high confidence with wrong source attribution.
    
    Detects when a model claims a strong source (e.g., "prompt") but the
    gold source is "guess" or "unresolved", and confidence is high.
    
    Source: Framework §5.4.5 - "unsupported certainty penalties"
    """
    if gold_source is None:
        return 0.0
    
    strong_source_claims = {"prompt", "memory"}
    weak_gold_sources = {"guess", "unresolved"}
    
    if (
        source_label in strong_source_claims
        and gold_source in weak_gold_sources
        and confidence >= threshold
    ):
        return float(confidence)  # penalty proportional to confidence
    
    return 0.0


def supporting_span_alignment(
    supporting_span: Optional[str],
    prompt_text: str,
    source_label: str,
) -> float:
    """Check if the claimed supporting span actually appears in the prompt.
    
    Only relevant when source_label is "prompt".
    Returns 1.0 if span is found in prompt, 0.0 otherwise.
    
    Source: Framework §5.4.5 - "prompt-span evidence alignment"
    
    NOTE: This is a simple substring check. A production version may need
    fuzzy matching or judge-model verification for paraphrased spans.
    """
    if source_label != "prompt":
        return float("nan")
    
    if not supporting_span:
        return 0.0
    
    # Normalize both for comparison
    span_norm = " ".join(supporting_span.strip().lower().split())
    prompt_norm = " ".join(prompt_text.strip().lower().split())
    
    return 1.0 if span_norm in prompt_norm else 0.0


def source_awareness_composite(
    answer_correct: bool,
    source_label_correct: bool,
    confidence: float,
    gold_source: Optional[str],
    predicted_source: str,
) -> float:
    """Composite source-awareness score for a single item.
    
    Source: Framework §5.4.5
    """
    if gold_source is None:
        return float("nan")
    
    base = 0.0
    
    # Answer correctness component (40%)
    if answer_correct:
        base += 0.4
    
    # Source label component (40%)
    if source_label_correct:
        base += 0.4
    
    # Calibration alignment (20%)
    # Reward when confidence aligns with source certainty
    certain_sources = {"prompt", "memory"}
    uncertain_sources = {"guess", "unresolved"}
    
    if predicted_source in certain_sources and answer_correct:
        base += 0.2 * confidence
    elif predicted_source in uncertain_sources:
        base += 0.2 * (1.0 - confidence)
    else:
        base += 0.1  # neutral
    
    return max(0.0, min(1.0, base))
