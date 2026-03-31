"""
MetaJudge-AGI: Deterministic Answer Adjudication (with canonicalization)
=========================================================================
Source: notebooks/metajudge_submission.ipynb Cell 4 (grading contract fix, 2026-03-20)

Provides deterministic correctness grading with:
- Alias matching
- Numeric equivalence (commas, scientific notation, word-to-digit)
- Yes/No/Contested normalization
- Conservative wrapper stripping
- Hedge and explanation rejection

No LLM judge in the primary scoring loop.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, Optional, cast

from metajudge.utils.text import normalize_text, strip_wrapper

# ---------------------------------------------------------------------------
# Answer key types and module-level state
# ---------------------------------------------------------------------------

AnswerSpec = Dict[str, Any]
AnswerKey = Dict[str, AnswerSpec]

# Module-level answer key — set via set_answer_key() or load_answer_key()
_ANSWER_KEY: AnswerKey = {}


def load_answer_key(path: str | Path) -> AnswerKey:
    """Load the answer key from a benchmark dataset JSON file.

    The file should be a list of item dicts, each with at minimum:
    item_id, gold_answer, aliases, rule.

    Returns the answer key dict (item_id -> spec).
    Also sets the module-level ANSWER_KEY.
    """
    with open(path) as f:
        items = json.load(f)

    if isinstance(items, list):
        # Dataset format: list of item dicts
        key = {
            item["item_id"]: {
                "gold_answer": item["gold_answer"],
                "aliases": item.get("aliases", []),
                "rule": item.get("rule", "alias"),
            }
            for item in items
        }
    elif isinstance(items, dict):
        # Already in answer-key format
        key = cast(AnswerKey, items)
    else:
        raise ValueError(f"Unexpected format in {path}")

    set_answer_key(key)
    return key


def set_answer_key(key: AnswerKey) -> None:
    """Set the module-level answer key used by adjudicate()."""
    global _ANSWER_KEY
    _ANSWER_KEY = key


def get_answer_key() -> AnswerKey:
    """Return the current module-level answer key."""
    return _ANSWER_KEY


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

_WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20",
    "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60",
    "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "100",
}

_COMPOUND_WORD_RE = re.compile(
    r'^(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[\s-]'
    r'(one|two|three|four|five|six|seven|eight|nine)$'
)

_SUPERSCRIPT_MAP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')

_SCI_NOTATION_RE = re.compile(
    r'([+-]?\d+\.?\d*)\s*[×x]\s*10\s*\^?\s*([⁻\-]?\s*[⁰¹²³⁴⁵⁶⁷⁸⁹0-9]+)'
)

_NUMBER_RE = re.compile(r'[-+]?\d[\d,]*\.?\d*(?:[eE][+-]?\d+)?')


def _word_to_number(text: str) -> Optional[str]:
    """Convert simple number words to digit strings. Returns None if not a number word."""
    t = text.strip().lower()
    if t in _WORD_TO_DIGIT:
        return _WORD_TO_DIGIT[t]
    m = _COMPOUND_WORD_RE.match(t)
    if m:
        tens = int(_WORD_TO_DIGIT[m.group(1)])
        ones = int(_WORD_TO_DIGIT[m.group(2)])
        return str(tens + ones)
    return None


def _parse_number(text: Optional[str]) -> Optional[float]:
    """Try to parse a number from text, handling commas and scientific notation.

    Returns float or None.
    """
    if text is None:
        return None
    s = text.strip()

    # Strip commas: "299,792,458" -> "299792458"
    s_no_commas = s.replace(",", "")
    try:
        return float(s_no_commas)
    except (ValueError, TypeError):
        pass

    # Unicode scientific notation: "6.02214076 × 10²³"
    m = _SCI_NOTATION_RE.search(s)
    if m:
        base = float(m.group(1))
        exp_str = m.group(2).translate(_SUPERSCRIPT_MAP).replace(" ", "")
        try:
            exp = int(exp_str)
            return base * (10 ** exp)
        except ValueError:
            pass

    # Standard e-notation
    try:
        return float(s)
    except (ValueError, TypeError):
        pass

    return None


def _nums_match(a: float, b: float) -> bool:
    """Check if two floats match, handling zero correctly."""
    if b == 0:
        return a == 0
    return math.isclose(a, b, rel_tol=1e-9)


def canonicalize_numeric(text: str, gold_answer: str) -> bool:
    """Extract a canonical numeric value from text for comparison with gold.

    Returns True if the extracted number matches gold, False otherwise.
    """
    gold_num = _parse_number(gold_answer)
    if gold_num is None:
        return False

    # Direct parse of the full text
    ans_num = _parse_number(text)
    if ans_num is not None:
        return _nums_match(ans_num, gold_num)

    # Number word conversion
    word_num = _word_to_number(text)
    if word_num is not None:
        ans_num = _parse_number(word_num)
        if ans_num is not None:
            return _nums_match(ans_num, gold_num)

    # Extract the single salient number from text
    numbers_found = _NUMBER_RE.findall(text)
    if len(numbers_found) == 1:
        ans_num = _parse_number(numbers_found[0])
        if ans_num is not None:
            return _nums_match(ans_num, gold_num)

    # Check for number words in the text tokens
    for word in text.split():
        wn = _word_to_number(word)
        if wn is not None:
            ans_num = _parse_number(wn)
            if ans_num is not None and _nums_match(ans_num, gold_num):
                return True

    return False


# ---------------------------------------------------------------------------
# Yes/No/Contested canonicalization
# ---------------------------------------------------------------------------

_YES_FORMS = frozenset({"yes", "y", "true", "correct"})
_NO_FORMS = frozenset({"no", "n", "false", "incorrect"})
_CONTESTED_FORMS = frozenset({"contested", "debated", "disputed"})
_ALL_YN_FORMS = _YES_FORMS | _NO_FORMS | _CONTESTED_FORMS


def canonicalize_yes_no(text: str, spec: AnswerSpec) -> bool:
    """Handle yes/no/contested items after wrapper stripping.

    Also checks if the text ends with a valid yes/no/contested word
    (e.g., 'the claim is false' -> 'false').
    """
    canonical_gold = normalize_text(spec["gold_answer"])

    # Direct match
    if canonical_gold in _CONTESTED_FORMS:
        if text in _CONTESTED_FORMS:
            return True
    elif canonical_gold in _YES_FORMS:
        if text in _YES_FORMS:
            return True
    elif canonical_gold in _NO_FORMS:
        if text in _NO_FORMS:
            return True

    # Last-word extraction: "the claim is false" -> "false"
    words = text.split()
    if words:
        last_word = words[-1]
        if last_word in _ALL_YN_FORMS:
            if canonical_gold in _CONTESTED_FORMS:
                return last_word in _CONTESTED_FORMS
            elif canonical_gold in _YES_FORMS:
                return last_word in _YES_FORMS
            elif canonical_gold in _NO_FORMS:
                return last_word in _NO_FORMS

    # First-word extraction: "debated among experts" -> "debated"
    if words:
        first_word = words[0]
        if first_word in _ALL_YN_FORMS:
            if canonical_gold in _CONTESTED_FORMS:
                return first_word in _CONTESTED_FORMS
            elif canonical_gold in _YES_FORMS:
                return first_word in _YES_FORMS
            elif canonical_gold in _NO_FORMS:
                return first_word in _NO_FORMS

    return False


# ---------------------------------------------------------------------------
# Grading rules
# ---------------------------------------------------------------------------

def _grade_alias_match(normalized: str, spec: AnswerSpec) -> bool:
    """Check gold_answer first, then aliases (matching library behavior)."""
    if normalized == normalize_text(spec["gold_answer"]):
        return True
    for alias in spec.get("aliases", []):
        if normalized == normalize_text(alias):
            return True
    return False


def _grade_yes_no(normalized: str, spec: AnswerSpec) -> bool:
    """Handle yes/no rule items (matching library behavior)."""
    canonical = normalize_text(spec["gold_answer"])
    canonical_is_yes = canonical in _YES_FORMS
    canonical_is_no = canonical in _NO_FORMS
    if not (canonical_is_yes or canonical_is_no):
        return _grade_alias_match(normalized, spec)
    if canonical_is_yes:
        return normalized in _YES_FORMS
    else:
        return normalized in _NO_FORMS


# ---------------------------------------------------------------------------
# Canonicalization orchestrator
# ---------------------------------------------------------------------------

def canonicalize_answer(
    item_id: str,
    raw_answer: str,
    spec: AnswerSpec,
) -> bool:
    """Orchestrate canonicalization pipeline.

    Steps:
      1. normalize_text (already done by caller)
      2. reject hedging and explanations
      3. strip_wrapper
      4. rule-specific canonicalization

    Returns True/False for correctness.
    """
    norm = raw_answer  # caller already normalized
    if norm is None:
        return False

    # Reject answers with explanation ("because" clause)
    if " because " in norm:
        return False

    # Strip wrapper
    stripped, was_stripped, is_hedged = strip_wrapper(norm)

    # Hedged answers are rejected entirely (no further canonicalization)
    if is_hedged:
        return False

    # None guard — strip_wrapper can return None for None input
    if stripped is None:
        return False

    # Try alias match on stripped text
    if _grade_alias_match(stripped, spec):
        return True

    rule = spec.get("rule", "alias")

    if rule == "numeric":
        if canonicalize_numeric(stripped, spec["gold_answer"]):
            return True
        if was_stripped and canonicalize_numeric(norm, spec["gold_answer"]):
            return True
        return False

    if rule == "yes_no":
        if canonicalize_yes_no(stripped, spec):
            return True
        return False

    if rule == "alias":
        # For alias items whose gold is a yes/no/contested word,
        # also try yes_no canonicalization
        gold_norm = normalize_text(spec["gold_answer"])
        yn_forms = {"yes", "no", "true", "false", "contested", "debated", "disputed"}
        if gold_norm in yn_forms:
            if canonicalize_yes_no(stripped, spec):
                return True

    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def adjudicate(
    item_id: str,
    raw_answer: str,
    gold_answer: str,
    answer_key: Optional[AnswerKey] = None,
) -> bool:
    """Deterministic correctness grading with canonicalization pipeline.

    Grading hierarchy:
      1. Exact normalized gold_answer match
      2. Exact normalized alias match
      3. Numeric equivalence (if rule == 'numeric')
      4. Yes/No normalization (if rule == 'yes_no')
      5. Canonicalization pipeline (wrapper stripping + rule-specific)
      6. Otherwise incorrect

    No LLM judge in the scoring loop.

    Args:
        item_id: The item's unique identifier.
        raw_answer: The model's raw answer string.
        gold_answer: The gold standard answer.
        answer_key: Optional answer key dict. If None, uses the module-level key.

    Returns:
        True if the answer is correct, False otherwise.
    """
    key = answer_key if answer_key is not None else _ANSWER_KEY
    spec = key.get(item_id)
    norm = normalize_text(raw_answer)
    if norm is None:
        return False

    # If no spec, fall back to exact match
    if spec is None:
        return norm == normalize_text(gold_answer)

    # 1 & 2. Gold answer + alias match (fast path)
    if _grade_alias_match(norm, spec):
        return True

    # 3. Numeric equivalence (original logic)
    if spec["rule"] == "numeric":
        try:
            if float(norm) == float(spec["gold_answer"]):
                return True
        except (ValueError, TypeError):
            pass

    # 4. Yes/No normalization (original logic)
    if spec["rule"] == "yes_no":
        if _grade_yes_no(norm, spec):
            return True

    # 5. Canonicalization pipeline (new)
    return canonicalize_answer(item_id, norm, spec)


def brier_item_score(is_correct: bool, confidence: float) -> float:
    """Per-item calibration score: 1 - (confidence - outcome)^2.

    This is an affine transform of per-item Brier loss.
    Strictly proper: expected score is uniquely maximized when
    stated confidence equals true probability of correctness.

    Range: [0, 1]. Higher is better.
    Reference: Brier (1950); Gneiting & Raftery (2007).
    """
    y = 1.0 if is_correct else 0.0
    return 1.0 - (confidence - y) ** 2


# ---------------------------------------------------------------------------
# Backward compatibility aliases
# ---------------------------------------------------------------------------

def adjudicate_answer(example_id: str, raw_answer: str, answer_key: AnswerKey) -> bool:
    """Legacy wrapper — delegates to adjudicate()."""
    spec = answer_key.get(example_id)
    gold = spec["gold_answer"] if spec else ""
    return adjudicate(example_id, raw_answer, gold, answer_key)


def adjudicate_with_fallback(
    example_id: str,
    raw_answer: str,
    gold_answer: str,
    answer_key: Optional[AnswerKey] = None,
) -> bool:
    """Legacy wrapper — delegates to adjudicate()."""
    return adjudicate(example_id, raw_answer, gold_answer, answer_key)
