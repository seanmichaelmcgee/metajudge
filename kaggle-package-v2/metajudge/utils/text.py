"""
MetaJudge-AGI: Text Utilities
================================
Source: Notebook Sketch Cell 10, grading contract fix (2026-03-20)

Common text normalization, wrapper stripping, and comparison utilities.
"""

from __future__ import annotations

from typing import Optional, Tuple


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


# ---------------------------------------------------------------------------
# Wrapper stripping (from grading contract fix)
# ---------------------------------------------------------------------------

_WRAPPER_PREFIXES = [
    "the correct answer is",
    "the answer is",
    "the claim is",
    "the statement is",
    "the country is",
    "this is",
    "answer:",
    "answer is",
    "it is approximately",
    "it's approximately",
    "approximately",
    "it is about",
    "it's about",
    "it is",
    "it's",
    "about",
]

_HEDGE_PREFIXES = [
    "probably",
    "i think",
    "i believe",
    "maybe",
    "perhaps",
]


def strip_wrapper(text: Optional[str]) -> Tuple[Optional[str], bool, bool]:
    """Strip light sentence wrappers from a normalized answer.

    Returns (stripped_text, was_stripped, is_hedged).
    Conservative: only strips known prefixes, trailing punctuation.
    Does NOT do fuzzy semantic matching.
    """
    if text is None:
        return None, False, False

    s = text.strip()

    # Check for hedging — return original unchanged and signal hedge
    for hedge in _HEDGE_PREFIXES:
        if s.startswith(hedge + " ") or s == hedge:
            return text, False, True

    # Strip known prefixes
    stripped = False
    for prefix in _WRAPPER_PREFIXES:
        if s.startswith(prefix + " "):
            s = s[len(prefix):].strip()
            stripped = True
            break
        elif prefix.endswith(":") and s.startswith(prefix):
            s = s[len(prefix):].strip()
            stripped = True
            break

    # Strip trailing punctuation
    s = s.rstrip(".,;:!?")

    return s.strip(), stripped, False
