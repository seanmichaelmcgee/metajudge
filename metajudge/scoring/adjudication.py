"""
MetaJudge-AGI: Deterministic Answer Adjudication
==================================================
Source: planning/scoring_plan.md §3–4

Provides deterministic correctness grading with alias support.
No LLM judge in the primary scoring loop.

The adjudication layer separates "was the answer correct?" from
"how well-calibrated was the confidence?" — Brier scoring operates
on the boolean output of this module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, cast

from metajudge.utils.text import normalize_text


# ---------------------------------------------------------------------------
# Answer key types and loading
# ---------------------------------------------------------------------------

# Canonical answer-key schema (gold_answer / aliases / rule)
# {
#   "gold_answer": "42",
#   "aliases": ["42", "42.0"],
#   "rule": "alias"               # alias | numeric | yes_no
# }
# Optional fields: answer_type, format_instruction, notes

AnswerSpec = Dict[str, Any]
AnswerKey = Dict[str, AnswerSpec]


def load_answer_key(path: str | Path) -> AnswerKey:
    """Load the answer key from a JSON file.

    The file should be a dict keyed by example_id, where each value
    is an AnswerSpec dict.
    """
    with open(path) as f:
        return cast(AnswerKey, json.load(f))


# ---------------------------------------------------------------------------
# Grading rules
# ---------------------------------------------------------------------------

def _grade_alias_match(normalized: str, spec: AnswerSpec) -> bool:
    """Check against gold_answer and aliases."""
    if normalized == normalize_text(spec["gold_answer"]):
        return True
    for alias in spec.get("aliases", []):
        if normalized == normalize_text(alias):
            return True
    return False


def _grade_numeric_equivalence(normalized: str, spec: AnswerSpec) -> bool:
    """Check numeric equivalence (handles '42' == '42.0')."""
    try:
        return float(normalized) == float(spec["gold_answer"])
    except (ValueError, TypeError):
        return False


def _grade_yes_no(normalized: str, spec: AnswerSpec) -> bool:
    """Normalize yes/no variants."""
    yes_forms = {"yes", "y", "true", "correct"}
    no_forms = {"no", "n", "false", "incorrect"}

    canonical = normalize_text(spec["gold_answer"])
    canonical_is_yes = canonical in yes_forms
    canonical_is_no = canonical in no_forms

    if not (canonical_is_yes or canonical_is_no):
        # Fall back to alias match if canonical isn't a standard yes/no
        return _grade_alias_match(normalized, spec)

    if canonical_is_yes:
        return normalized in yes_forms
    else:
        return normalized in no_forms


# Grading rule dispatch
GRADER_RULES = {
    "alias": _grade_alias_match,
    "numeric": _grade_numeric_equivalence,
    "yes_no": _grade_yes_no,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def adjudicate_answer(
    example_id: str,
    raw_answer: str,
    answer_key: AnswerKey,
) -> bool:
    """Determine correctness of a model answer using deterministic grading.

    Grading hierarchy (scoring_plan.md §4.3):
      1. Exact normalized canonical match
      2. Exact normalized alias match
      3. Type-specific deterministic rule (if declared)
      4. Otherwise incorrect

    Args:
        example_id: The item's unique identifier.
        raw_answer: The model's raw answer string.
        answer_key: The full answer key dict.

    Returns:
        True if the answer is correct, False otherwise.
    """
    spec = answer_key.get(example_id)

    if spec is None:
        # No spec found — fall back to exact normalized match
        # This should not happen in production; log a warning.
        return False

    normalized = normalize_text(raw_answer)
    if normalized is None:
        return False

    # Step 1+2: Canonical and alias match (always attempted)
    if _grade_alias_match(normalized, spec):
        return True

    # Step 3: Type-specific grading rule
    rule = spec.get("rule", "alias")
    grader_fn = GRADER_RULES.get(rule)

    if grader_fn and grader_fn is not _grade_alias_match:
        # Only call if it's a different rule than alias (already tried)
        if grader_fn(normalized, spec):
            return True

    # Step 4: Not correct
    return False


def adjudicate_with_fallback(
    example_id: str,
    raw_answer: str,
    gold_answer: str,
    answer_key: Optional[AnswerKey] = None,
) -> bool:
    """Adjudicate with optional answer key, falling back to exact match.

    This allows the scoring pipeline to work both with and without
    the full answer key — useful during early development when the
    answer key may not yet exist for all items.
    """
    if answer_key and example_id in answer_key:
        return adjudicate_answer(example_id, raw_answer, answer_key)

    # Fallback: plain normalized exact match (original behavior)
    return normalize_text(raw_answer) == normalize_text(gold_answer)
