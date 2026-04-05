"""
MetaJudge-AGI: Grading V2 — Registry-driven adjudication
==========================================================
Dispatches to per-rule grader functions using the adjudication registry.
Does NOT modify or replace adjudication.py — this is an additive layer.

Grader rules:
  exact_constant          SI-defined constants, rel_tol comparison
  approx_numeric_small    Approximate numerics with fixed tolerance
  approx_numeric_dynamic  Date/source-sensitive numerics with tolerance
  tri_label               Three-valued {true, false, contested}
  alias_plus_normalization Enhanced alias matching with sci-notation normalization
  yes_no                  Binary true/false
  fraction_or_decimal     Accepts both fraction and decimal forms
  code_output             Exact string match after strip/lower
"""

from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Text normalization (standalone — no dependency on metajudge.utils.text)
# ---------------------------------------------------------------------------

def _normalize(text: Optional[str]) -> Optional[str]:
    """Lowercase, collapse whitespace, strip."""
    if text is None:
        return None
    s = " ".join(str(text).strip().lower().split())
    s = s.replace('\u2212', '-')  # Unicode minus → ASCII hyphen-minus
    return s


def _normalize_sci(text: str) -> str:
    """Normalize scientific notation formatting.

    Collapses spaces around ×, ·, ^, and superscript characters.
    Converts Unicode superscripts to ASCII exponent notation.
    """
    s = text.strip().lower()
    s = s.replace('\u2212', '-')  # Unicode minus → ASCII hyphen-minus
    # Normalize multiplication signs
    s = s.replace("×", "x").replace("·", "x")
    # Collapse spaces around x (multiplication) and ^
    s = re.sub(r'\s*x\s*', 'x', s)
    s = re.sub(r'\s*\^\s*', '^', s)
    # Translate Unicode superscripts
    sup_map = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')
    s = s.translate(sup_map)
    # Convert "10^XX" after x to e-notation inline
    m = re.search(r'([\d.]+)\s*x\s*10\^?\s*(-?\d+)', s)
    if m:
        base, exp = m.group(1), m.group(2)
        s = f"{base}e{exp}"
    return " ".join(s.split())


# ---------------------------------------------------------------------------
# Numeric parsing helpers
# ---------------------------------------------------------------------------

_SUPERSCRIPT_MAP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')

_SCI_RE = re.compile(
    r'([+-]?\d+\.?\d*)\s*[×x]\s*10\s*\^?\s*([⁻\-]?\s*[⁰¹²³⁴⁵⁶⁷⁸⁹0-9]+)'
)

_NUMBER_RE = re.compile(r'[-+]?\d[\d,]*\.?\d*(?:[eE][+-]?\d+)?')


def _parse_float(text: Optional[str]) -> Optional[float]:
    """Parse a float from text, handling commas and scientific notation."""
    if text is None:
        return None
    s = text.strip()

    # Strip commas
    try:
        return float(s.replace(",", ""))
    except (ValueError, TypeError):
        pass

    # Unicode scientific notation
    m = _SCI_RE.search(s)
    if m:
        base = float(m.group(1))
        exp_str = m.group(2).translate(_SUPERSCRIPT_MAP).replace(" ", "")
        try:
            return base * (10 ** int(exp_str))
        except ValueError:
            pass

    # Standard e-notation
    try:
        return float(s)
    except (ValueError, TypeError):
        pass

    # Last resort: find the first number-like substring
    numbers = _NUMBER_RE.findall(s)
    if len(numbers) == 1:
        try:
            return float(numbers[0].replace(",", ""))
        except (ValueError, TypeError):
            pass

    return None


def _nums_close(a: float, b: float, rel_tol: float = 0.0, abs_tol: float = 0.0) -> bool:
    """Compare two floats with configurable tolerance."""
    if abs_tol > 0 and abs(a - b) <= abs_tol:
        return True
    if rel_tol > 0:
        return math.isclose(a, b, rel_tol=rel_tol)
    return a == b


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

def load_registry(path: str | Path = "data/adjudication_registry.json") -> Dict[str, Dict[str, Any]]:
    """Load the adjudication registry and index by item_id."""
    with open(path) as f:
        entries = json.load(f)
    return {e["item_id"]: e for e in entries}


# ---------------------------------------------------------------------------
# Individual grader functions
# ---------------------------------------------------------------------------

def _grade_exact_constant(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade SI-defined exact constants. Float comparison with rel_tol."""
    gold_val = _parse_float(spec["gold_answer"])
    ans_val = _parse_float(answer)
    if gold_val is None:
        return {"correct": False, "method": "exact_constant", "match_detail": "gold unparseable"}
    if ans_val is None:
        # Try normalizing scientific notation first
        ans_val = _parse_float(_normalize_sci(answer))
    if ans_val is None:
        return {"correct": False, "method": "exact_constant", "match_detail": "answer unparseable"}

    params = spec.get("tolerance_params") or {}
    rel_tol = params.get("rel_tol", 1e-6)
    if _nums_close(ans_val, gold_val, rel_tol=rel_tol):
        return {"correct": True, "method": "exact_constant", "match_detail": f"float match rel_tol={rel_tol}"}
    return {"correct": False, "method": "exact_constant",
            "match_detail": f"mismatch: {ans_val} vs {gold_val}"}


def _grade_approx_numeric_small(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade approximate numerics with fixed tolerance."""
    gold_val = _parse_float(spec["gold_answer"])
    ans_val = _parse_float(answer)
    if gold_val is None:
        return {"correct": False, "method": "approx_numeric_small", "match_detail": "gold unparseable"}

    params = spec.get("tolerance_params") or {}
    abs_tol = params.get("abs_tol", 0.0)
    rel_tol = params.get("rel_tol", 0.0)

    if ans_val is not None:
        if _nums_close(ans_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
            return {"correct": True, "method": "approx_numeric_small",
                    "match_detail": f"within tolerance abs={abs_tol} rel={rel_tol}"}
        return {"correct": False, "method": "approx_numeric_small",
                "match_detail": f"mismatch: {ans_val} vs {gold_val}"}

    # Verbose-answer fallback: when answer is unparseable but contains_any mode
    # is set, try each extracted number individually (handles e.g. "carbon-14...
    # 5,730 years" where multiple numbers prevent single-number extraction).
    if spec.get("match_mode") == "contains_any":
        for n_str in _NUMBER_RE.findall(answer):
            n_val = _parse_float(n_str)
            if n_val is not None and _nums_close(n_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
                return {"correct": True, "method": "approx_numeric_small",
                        "match_detail": f"contains_any numeric match: {n_str}"}

    return {"correct": False, "method": "approx_numeric_small", "match_detail": "answer unparseable"}


def _grade_approx_numeric_dynamic(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade time-sensitive approximate numerics."""
    # Same numeric comparison as approx_numeric_small, but spec carries
    # time_anchor and source_anchor metadata for audit purposes.
    gold_val = _parse_float(spec["gold_answer"])
    ans_val = _parse_float(answer)
    if gold_val is None:
        return {"correct": False, "method": "approx_numeric_dynamic", "match_detail": "gold unparseable"}
    if ans_val is None:
        return {"correct": False, "method": "approx_numeric_dynamic", "match_detail": "answer unparseable"}

    params = spec.get("tolerance_params") or {}
    abs_tol = params.get("abs_tol", 0.0)
    rel_tol = params.get("rel_tol", 0.0)
    if _nums_close(ans_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
        return {"correct": True, "method": "approx_numeric_dynamic",
                "match_detail": f"within tolerance (anchor: {spec.get('time_anchor')})"}
    return {"correct": False, "method": "approx_numeric_dynamic",
            "match_detail": f"mismatch: {ans_val} vs {gold_val}"}


def _grade_tri_label(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade three-valued label items: {true, false, contested}."""
    norm = _normalize(answer)
    if norm is None:
        return {"correct": False, "method": "tri_label", "match_detail": "empty answer"}

    gold_norm = _normalize(spec["gold_answer"])

    # Canonical form mapping
    true_forms = {"true", "yes", "correct", "y"}
    false_forms = {"false", "no", "incorrect", "n"}
    contested_forms = {"contested", "debated", "disputed"}

    def _to_canonical(text: str) -> Optional[str]:
        if text in true_forms:
            return "true"
        if text in false_forms:
            return "false"
        if text in contested_forms:
            return "contested"
        # Last-word extraction for wrapped answers
        words = text.split()
        if words:
            last = words[-1]
            if last in true_forms:
                return "true"
            if last in false_forms:
                return "false"
            if last in contested_forms:
                return "contested"
        if words:
            first = words[0]
            if first in true_forms:
                return "true"
            if first in false_forms:
                return "false"
            if first in contested_forms:
                return "contested"
        return None

    gold_canonical = _to_canonical(gold_norm)
    ans_canonical = _to_canonical(norm)

    if ans_canonical is None:
        return {"correct": False, "method": "tri_label", "match_detail": f"unrecognized: {norm!r}"}

    # Validate the label space
    label_space = spec.get("tri_label_space") or ["true", "false", "contested"]
    if ans_canonical not in label_space:
        return {"correct": False, "method": "tri_label",
                "match_detail": f"{ans_canonical!r} not in label space {label_space}"}

    if ans_canonical == gold_canonical:
        return {"correct": True, "method": "tri_label", "match_detail": f"matched: {ans_canonical}"}

    # Check accepted_forms from registry (may include alternative labels)
    accepted = spec.get("accepted_forms", [])
    if accepted:
        accepted_lower = {a.lower().strip() for a in accepted}
        if norm in accepted_lower or ans_canonical in accepted_lower:
            return {"correct": True, "method": "tri_label",
                    "match_detail": f"accepted_form: {ans_canonical} (gold: {gold_canonical})"}

    return {"correct": False, "method": "tri_label",
            "match_detail": f"label mismatch: {ans_canonical} vs gold {gold_canonical}"}


def _grade_yes_no(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade binary yes/no (true/false) items."""
    norm = _normalize(answer)
    if norm is None:
        return {"correct": False, "method": "yes_no", "match_detail": "empty answer"}

    gold_norm = _normalize(spec["gold_answer"])

    yes_forms = {"true", "yes", "correct", "y"}
    no_forms = {"false", "no", "incorrect", "n"}

    def _to_binary(text: str) -> Optional[str]:
        if text in yes_forms:
            return "yes"
        if text in no_forms:
            return "no"
        words = text.split()
        if words:
            for w in (words[-1], words[0]):
                if w in yes_forms:
                    return "yes"
                if w in no_forms:
                    return "no"
        return None

    gold_bin = _to_binary(gold_norm)
    ans_bin = _to_binary(norm)

    if ans_bin is None:
        return {"correct": False, "method": "yes_no", "match_detail": f"unrecognized: {norm!r}"}
    if ans_bin == gold_bin:
        return {"correct": True, "method": "yes_no", "match_detail": f"matched: {ans_bin}"}
    return {"correct": False, "method": "yes_no", "match_detail": f"mismatch: {ans_bin} vs gold {gold_bin}"}


def _grade_fraction_or_decimal(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade items that accept both fraction and decimal forms."""
    norm = _normalize(answer)
    if norm is None:
        return {"correct": False, "method": "fraction_or_decimal", "match_detail": "empty answer"}

    gold = spec["gold_answer"]

    # Parse gold as Fraction
    try:
        gold_frac = Fraction(gold).limit_denominator(10000)
    except (ValueError, ZeroDivisionError):
        gold_frac = None

    # Also get gold as float
    gold_float = _parse_float(gold)

    # Try parsing answer as fraction first
    ans_frac = None
    # Handle "4/5" style
    frac_match = re.match(r'^(-?\d+)\s*/\s*(\d+)$', norm.strip())
    if frac_match:
        try:
            ans_frac = Fraction(int(frac_match.group(1)), int(frac_match.group(2)))
        except ZeroDivisionError:
            pass

    # Try as float
    ans_float = _parse_float(norm)

    # Compare via Fraction if both parseable
    if gold_frac is not None and ans_frac is not None:
        if ans_frac == gold_frac:
            return {"correct": True, "method": "fraction_or_decimal", "match_detail": "fraction match"}

    # Compare via float
    if gold_float is not None and ans_float is not None:
        if _nums_close(ans_float, gold_float, rel_tol=1e-9):
            return {"correct": True, "method": "fraction_or_decimal", "match_detail": "decimal match"}

    # Cross-compare: answer as float vs gold as fraction
    if gold_frac is not None and ans_float is not None:
        if _nums_close(ans_float, float(gold_frac), rel_tol=1e-9):
            return {"correct": True, "method": "fraction_or_decimal", "match_detail": "decimal-to-fraction match"}

    if ans_frac is not None and gold_float is not None:
        if _nums_close(float(ans_frac), gold_float, rel_tol=1e-9):
            return {"correct": True, "method": "fraction_or_decimal", "match_detail": "fraction-to-decimal match"}

    return {"correct": False, "method": "fraction_or_decimal",
            "match_detail": f"no match: {norm!r} vs gold {gold!r}"}


def _grade_code_output(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Grade code execution output — exact match after strip/lower + newline normalization."""
    norm = _normalize(answer)
    gold_norm = _normalize(spec["gold_answer"])
    if norm == gold_norm:
        return {"correct": True, "method": "code_output", "match_detail": "exact match"}
    # Also try replacing literal \n with actual newlines before normalizing
    norm_escaped = _normalize(answer.replace("\\n", "\n"))
    gold_escaped = _normalize(spec["gold_answer"].replace("\\n", "\n"))
    if norm_escaped == gold_escaped:
        return {"correct": True, "method": "code_output", "match_detail": "newline-normalized match"}
    return {"correct": False, "method": "code_output",
            "match_detail": f"mismatch: {norm!r} vs {gold_norm!r}"}


def _grade_alias_plus_normalization(answer: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced alias matching with scientific notation normalization."""
    norm = _normalize(answer)
    if norm is None:
        return {"correct": False, "method": "alias_plus_normalization", "match_detail": "empty answer"}

    gold_norm = _normalize(spec["gold_answer"])

    # Direct match against gold
    if norm == gold_norm:
        return {"correct": True, "method": "alias_plus_normalization", "match_detail": "gold match"}

    # Match against accepted_forms
    accepted = spec.get("accepted_forms") or []
    for form in accepted:
        if _normalize(form) == norm:
            return {"correct": True, "method": "alias_plus_normalization", "match_detail": f"alias match: {form!r}"}

    # Substring matching mode for items with explanatory answers
    match_mode = spec.get("match_mode")
    if match_mode == "contains_any":
        for form in ([gold_norm] + [_normalize(f) for f in accepted]):
            if form and form in norm:
                return {"correct": True, "method": "alias_plus_normalization", "match_detail": f"contains match: {form!r}"}

    # Try with scientific notation normalization
    norm_sci = _normalize_sci(answer)
    gold_sci = _normalize_sci(spec["gold_answer"])
    if norm_sci == gold_sci:
        return {"correct": True, "method": "alias_plus_normalization", "match_detail": "sci-notation match"}

    for form in accepted:
        if _normalize_sci(form) == norm_sci:
            return {"correct": True, "method": "alias_plus_normalization",
                    "match_detail": f"sci-notation alias match: {form!r}"}

    # Try numeric comparison as fallback for numeric-looking items
    ans_float = _parse_float(answer)
    gold_float = _parse_float(spec["gold_answer"])
    if ans_float is not None and gold_float is not None:
        if _nums_close(ans_float, gold_float, rel_tol=1e-9):
            return {"correct": True, "method": "alias_plus_normalization", "match_detail": "numeric fallback"}

    return {"correct": False, "method": "alias_plus_normalization",
            "match_detail": f"no match: {norm!r} vs gold {gold_norm!r}"}


# ---------------------------------------------------------------------------
# Grader dispatch
# ---------------------------------------------------------------------------

_GRADERS = {
    "exact_constant": _grade_exact_constant,
    "approx_numeric_small": _grade_approx_numeric_small,
    "approx_numeric_dynamic": _grade_approx_numeric_dynamic,
    "tri_label": _grade_tri_label,
    "yes_no": _grade_yes_no,
    "fraction_or_decimal": _grade_fraction_or_decimal,
    "code_output": _grade_code_output,
    "alias_plus_normalization": _grade_alias_plus_normalization,
}


def grade_item(
    item_id: str,
    model_answer: str,
    registry: Dict[str, Dict[str, Any]],
    gold_answer: Optional[str] = None,
) -> Dict[str, Any]:
    """Grade a single item using the adjudication registry.

    Args:
        item_id: The benchmark item identifier.
        model_answer: The model's raw answer string.
        registry: The loaded registry dict (item_id -> spec).
        gold_answer: Optional fallback gold answer for items not in the
            registry. When provided and the item is missing from the
            registry, uses normalised string + numeric comparison.

    Returns:
        {"correct": bool, "method": str, "match_detail": str}
    """
    spec = registry.get(item_id)
    if spec is None:
        if gold_answer is not None:
            return _grade_fallback(model_answer, gold_answer)
        return {"correct": False, "method": "unknown", "match_detail": f"item {item_id!r} not in registry"}

    rule = spec.get("grader_rule", "alias_plus_normalization")
    grader = _GRADERS.get(rule)
    if grader is None:
        return {"correct": False, "method": rule, "match_detail": f"unknown grader rule: {rule!r}"}

    return grader(model_answer, spec)


def _grade_fallback(model_answer: str, gold_answer: str) -> Dict[str, Any]:
    """Lightweight fallback grading for items not in the registry.

    Tries normalised string match, then comma-stripped numeric match.
    Deliberately conservative — no substring or containment matching.
    """
    norm_ans = _normalize(model_answer)
    norm_gold = _normalize(gold_answer)

    if norm_ans is None or norm_gold is None:
        return {"correct": False, "method": "fallback", "match_detail": "empty answer or gold"}

    # Exact normalised match
    if norm_ans == norm_gold:
        return {"correct": True, "method": "fallback", "match_detail": "normalised exact match"}

    # Numeric comparison (handles commas, whitespace)
    ans_float = _parse_float(model_answer)
    gold_float = _parse_float(gold_answer)
    if ans_float is not None and gold_float is not None:
        if _nums_close(ans_float, gold_float, rel_tol=1e-6):
            return {"correct": True, "method": "fallback", "match_detail": "numeric match"}

    return {"correct": False, "method": "fallback",
            "match_detail": f"no match: {norm_ans!r} vs gold {norm_gold!r}"}
