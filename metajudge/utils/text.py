"""
MetaJudge-AGI: Text Utilities
================================
Source: Notebook Sketch Cell 10

Common text normalization and comparison utilities.
"""

from __future__ import annotations

from typing import Optional


def normalize_text(x: Optional[str]) -> Optional[str]:
    """Normalize text for answer comparison.
    
    Source: Notebook Sketch Cell 10
    """
    if x is None:
        return None
    return " ".join(str(x).strip().lower().split())


def answers_match(predicted: Optional[str], gold: Optional[str]) -> bool:
    """Check if two answers match after normalization."""
    if gold is None:
        return False
    return normalize_text(predicted) == normalize_text(gold)
