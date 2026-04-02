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
    return " ".join(str(text).strip().lower().split())


# ---------------------------------------------------------------------------
# Preprocessing: LaTeX unwrapping, markdown stripping, answer extraction
# ---------------------------------------------------------------------------

def _strip_latex(text: str) -> str:
    """Remove LaTeX wrappers, evaluate \\frac and simple exponents."""
    # Remove display math wrappers: \(...\), \[...\], $...$
    s = re.sub(r'\\\((.+?)\\\)', r'\1', text)
    s = re.sub(r'\\\[(.+?)\\\]', r'\1', s)
    s = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', r'\1', s)
    # Remove \boxed{...}, \text{...}, \mathrm{...}
    s = re.sub(r'\\boxed\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', s)
    # Convert \frac{a}{b} -> a/b
    s = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', s)
    return s


def _strip_markdown(text: str) -> str:
    """Remove markdown bold/italic/code formatting."""
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    s = re.sub(r'__(.+?)__', r'\1', s)
    s = re.sub(r'\*(.+?)\*', r'\1', s)
    s = re.sub(r'_(.+?)_', r'\1', s)
    s = re.sub(r'`(.+?)`', r'\1', s)
    return s


_NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20",
}


def _normalize_number_words(text: str) -> str:
    """Replace leading English number word with digit equivalent."""
    words = text.strip().split()
    if not words:
        return text
    first_lower = words[0].lower()
    if first_lower in _NUMBER_WORDS:
        words[0] = _NUMBER_WORDS[first_lower]
        return " ".join(words)
    return text


def _preprocess_answer(text: str) -> str:
    """Apply LaTeX unwrapping, markdown stripping, and number-word normalization."""
    return _normalize_number_words(_strip_markdown(_strip_latex(text)))


def _extract_final_answer(text: str) -> Optional[str]:
    """Extract a concise answer from verbose review/confirmation prose.

    Tries structured ANSWER: tag first, then 'the answer is X' patterns.
    Returns None if no pattern matches (caller should use full text).
    """
    # Priority 1: Explicit ANSWER: tag
    m = re.search(r'ANSWER:\s*(.+?)(?:\s*\||\s*$)', text, re.IGNORECASE)
    if m:
        extracted = m.group(1).strip()
        if len(extracted) < 100:  # Sanity check — ANSWER: shouldn't be a paragraph
            return extracted

    # Priority 2: "the answer is/remains X" patterns
    patterns = [
        r'(?:my\s+)?final\s+answer\s*(?:is|:)\s*(.+?)(?:\.|,|\s*$)',
        r'(?:the\s+)?(?:correct\s+)?answer\s+(?:is|remains|=)\s*(.+?)(?:\.|,|\s*$)',
        r'(?:there\s+are|there\s+is)\s+(.+?)(?:\.|,|\s*$)',
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        if matches:
            extracted = matches[-1].group(1).strip()
            if len(extracted) < 80:
                return extracted

    return None


def _extract_final_answer_number(text: str, gold_val: float) -> Optional[float]:
    """Extract the most likely answer number from verbose text.

    Priority: 'final answer' patterns > bold numbers > closest to gold > last number.
    """
    clean = _strip_markdown(_strip_latex(text))

    # Priority 1: "final answer" / "the answer is" patterns
    final_patterns = [
        r'(?:my\s+)?final\s+answer\s*(?:is|:)\s*[^\d]*(-?\d[\d,]*\.?\d*)',
        r'(?:the\s+)?answer\s+(?:is|remains|=)\s*[^\d]*(-?\d[\d,]*\.?\d*)',
        r'(?:so|therefore|thus)[,:]?\s*[^\d]*(-?\d[\d,]*\.?\d*)',
        r'=\s*[^\d]*(-?\d[\d,]*\.?\d*)\s*$',
    ]
    for pattern in final_patterns:
        m = re.search(pattern, clean, re.IGNORECASE | re.MULTILINE)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                pass

    # Priority 2: last number in bold emphasis
    bold_nums = re.findall(r'\*\*(-?\d[\d,]*\.?\d*)\*\*', text)
    if bold_nums:
        try:
            return float(bold_nums[-1].replace(',', ''))
        except ValueError:
            pass

    # Priority 3: smart extraction from all numbers
    # Use digit-only comma stripping (preserves "November 9, 1989")
    num_text = re.sub(r'(\d),(\d)', r'\1\2', clean)
    all_nums = [float(m.group()) for m in re.finditer(r'-?\d+\.?\d*', num_text)
                if _try_float(m.group()) is not None]

    if not all_nums:
        return None

    # If gold value is in the list, return it
    for n in all_nums:
        if gold_val != 0 and abs(n - gold_val) / abs(gold_val) < 0.001:
            return n
        if gold_val == 0 and abs(n) < 0.001:
            return n

    # Return last number (conclusion is usually at the end)
    return all_nums[-1]


def _try_float(s: str) -> Optional[float]:
    """Try to parse a float, return None on failure."""
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _normalize_sign_language(text: str) -> Optional[str]:
    """Convert 'N% decrease/decline/drop' to '-N%' and 'N% increase/rise' to '+N%'."""
    t = text.lower()
    # "N% decrease" or "N decrease"
    m = re.search(
        r'(\d+(?:\.\d+)?)\s*%?\s*(?:decrease|decline|drop|reduction|less|lower)',
        t
    )
    if m:
        return f"-{m.group(1)}%"
    # "decrease of N%" or "decrease by N%" or "decreases by N%"
    m = re.search(
        r'(?:decrease[sd]?|decline[sd]?|drop[sp]?|reduction)\s+(?:of|by)\s+(\d+(?:\.\d+)?)\s*%',
        t
    )
    if m:
        return f"-{m.group(1)}%"
    # "N% increase" or "increase of/by N%"
    m = re.search(
        r'(\d+(?:\.\d+)?)\s*%?\s*(?:increase|gain|rise|more|higher)',
        t
    )
    if m:
        return f"+{m.group(1)}%"
    m = re.search(
        r'(?:increase[sd]?|gain[sd]?|rise[sd]?)\s+(?:of|by)\s+(\d+(?:\.\d+)?)\s*%',
        t
    )
    if m:
        return f"+{m.group(1)}%"
    return None


def _normalize_sci(text: str) -> str:
    """Normalize scientific notation formatting.

    Collapses spaces around ×, ·, ^, and superscript characters.
    Converts Unicode superscripts to ASCII exponent notation.
    """
    s = text.strip().lower()
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
    """Parse a float from text, handling commas, LaTeX, and scientific notation."""
    if text is None:
        return None
    s = text.strip()

    # Strip LaTeX wrappers first
    s = _strip_latex(s)
    s = _strip_markdown(s)
    s = s.strip()

    # Strip commas between digits (smart: preserves "November 9, 1989")
    s_clean = re.sub(r'(\d),(\d)', r'\1\2', s)

    try:
        return float(s_clean)
    except (ValueError, TypeError):
        pass

    # Try evaluating simple fractions: "5/11", "a/b"
    frac_m = re.match(r'^(-?\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)$', s_clean.strip())
    if frac_m:
        try:
            return float(frac_m.group(1)) / float(frac_m.group(2))
        except (ValueError, ZeroDivisionError):
            pass

    # Try evaluating simple exponents: "2^81", "10^3"
    exp_m = re.match(r'^(\d+(?:\.\d+)?)\s*\^\s*\{?(\d+)\}?$', s_clean.strip())
    if exp_m:
        try:
            return float(exp_m.group(1)) ** int(exp_m.group(2))
        except (ValueError, OverflowError):
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
    numbers = _NUMBER_RE.findall(s_clean)
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

    # Verbose-answer fallback: try "final answer" extraction for review prose
    if ans_val is None or not _nums_close(ans_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
        final_val = _extract_final_answer_number(answer, gold_val)
        if final_val is not None and _nums_close(final_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
            return {"correct": True, "method": "approx_numeric_small",
                    "match_detail": f"final_answer_extraction: {final_val}"}

    # Contains-any fallback: try each number in text
    num_text = re.sub(r'(\d),(\d)', r'\1\2', _preprocess_answer(answer))
    for n_str in re.findall(r'-?\d+\.?\d*', num_text):
        n_val = _try_float(n_str)
        if n_val is not None and _nums_close(n_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
            return {"correct": True, "method": "approx_numeric_small",
                    "match_detail": f"number_in_text: {n_str}"}

    # Sign-language normalization: "4% decrease" → "-4%"
    sign_norm = _normalize_sign_language(answer)
    if sign_norm is not None:
        sign_val = _try_float(sign_norm.replace('%', ''))
        if sign_val is not None and _nums_close(sign_val, gold_val, rel_tol=rel_tol, abs_tol=abs_tol):
            return {"correct": True, "method": "approx_numeric_small",
                    "match_detail": f"sign_language_normalization: {sign_norm}"}

    detail = f"mismatch: {ans_val} vs {gold_val}" if ans_val is not None else "answer unparseable"
    return {"correct": False, "method": "approx_numeric_small", "match_detail": detail}


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
    # Quote-style normalization: treat single and double quotes as equivalent
    norm_q = norm.replace('"', "'") if norm else norm
    gold_q = gold_norm.replace('"', "'") if gold_norm else gold_norm
    if norm_q and norm_q == gold_q:
        return {"correct": True, "method": "code_output", "match_detail": "quote-normalized match"}
    # Also try replacing literal \n with actual newlines before normalizing
    norm_escaped = _normalize(answer.replace("\\n", "\n"))
    gold_escaped = _normalize(spec["gold_answer"].replace("\\n", "\n"))
    if norm_escaped == gold_escaped:
        return {"correct": True, "method": "code_output", "match_detail": "newline-normalized match"}
    # Try preprocessed (LaTeX/markdown stripped)
    norm_pp = _normalize(_preprocess_answer(answer))
    if norm_pp == gold_norm:
        return {"correct": True, "method": "code_output", "match_detail": "preprocessed match"}
    # Try extracting answer from verbose review prose
    extracted = _extract_final_answer(answer)
    if extracted and _normalize(extracted) == gold_norm:
        return {"correct": True, "method": "code_output",
                "match_detail": f"final_answer_extraction: {extracted!r}"}
    # Numeric fallback for code items with numeric output
    ans_float = _parse_float(answer)
    gold_float = _parse_float(spec["gold_answer"])
    if ans_float is not None and gold_float is not None:
        if ans_float == gold_float:
            return {"correct": True, "method": "code_output", "match_detail": "numeric match"}
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

    # Try with preprocessing (LaTeX/markdown stripped)
    preprocessed = _preprocess_answer(answer)
    norm_pp = _normalize(preprocessed)
    if norm_pp and norm_pp != norm and norm_pp == gold_norm:
        return {"correct": True, "method": "alias_plus_normalization", "match_detail": "preprocessed gold match"}

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

    # Try extracting a concise answer from verbose review prose
    extracted = _extract_final_answer(answer)
    if extracted:
        ext_norm = _normalize(extracted)
        if ext_norm == gold_norm:
            return {"correct": True, "method": "alias_plus_normalization",
                    "match_detail": f"final_answer_extraction: {extracted!r}"}
        for form in accepted:
            if _normalize(form) == ext_norm:
                return {"correct": True, "method": "alias_plus_normalization",
                        "match_detail": f"final_answer_alias: {form!r}"}
        # Contains check on extracted text
        if match_mode == "contains_any":
            for form in ([gold_norm] + [_normalize(f) for f in accepted]):
                if form and form in ext_norm:
                    return {"correct": True, "method": "alias_plus_normalization",
                            "match_detail": f"final_answer_contains: {form!r}"}

    # Sign-language normalization: "4% decrease" → "-4%"
    sign_norm = _normalize_sign_language(answer)
    if sign_norm is not None:
        sign_normalized = _normalize(sign_norm)
        if sign_normalized == gold_norm:
            return {"correct": True, "method": "alias_plus_normalization",
                    "match_detail": f"sign_language_match: {sign_norm}"}
        for form in accepted:
            if _normalize(form) == sign_normalized:
                return {"correct": True, "method": "alias_plus_normalization",
                        "match_detail": f"sign_language_alias: {form!r}"}

    # Leading-token match: if gold is short (≤3 words), accept if answer starts with it
    if gold_norm:
        gold_words = gold_norm.split()
        if len(gold_words) <= 3 and norm and norm.startswith(gold_norm):
            return {"correct": True, "method": "alias_plus_normalization",
                    "match_detail": f"leading_token_match: answer starts with '{gold_norm}'"}
        for form in accepted:
            form_norm = _normalize(form)
            if form_norm and len(form_norm.split()) <= 3 and norm and norm.startswith(form_norm):
                return {"correct": True, "method": "alias_plus_normalization",
                        "match_detail": f"leading_token_match: answer starts with alias '{form_norm}'"}

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
