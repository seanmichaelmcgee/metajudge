"""
MetaJudge-AGI: Dataset Validation Checks
==========================================
Structural and hygiene checks for calibration.csv and the answer key.

Source of truth: the Kaggle notebook schema (Cell 3 ANSWER_KEY).
All other representations are checked for drift against it.

Notebook schema (canonical):
    {
        "canonical": "<answer>",
        "aliases": ["<alias1>", ...],
        "rule": "alias" | "numeric"
    }

Known drift (flagged by these checks, fixed after sweep):
- data/calibration_answer_key.json uses gold_answer/grader_rule instead of
  canonical/rule, and carries extra fields answer_type/format_instruction.
- metajudge/scoring/adjudication.py uses canonical_answer/accepted_aliases/
  grader_rule instead of canonical/aliases/rule.

Run via: python -m metajudge.validation.run_checks
"""

from __future__ import annotations

import inspect
import re
from typing import Any, Dict, List

import pandas as pd

from metajudge.utils.text import normalize_text

AnswerKey = Dict[str, Dict[str, Any]]

# Notebook schema — source of truth
EXPECTED_AK_FIELDS = {"canonical", "aliases", "rule"}

# Old field names that indicate drift from notebook schema
_ADJUDICATION_DRIFT_FIELDS = {
    "canonical_answer": "canonical",
    "accepted_aliases": "aliases",
    "grader_rule": "rule",
}

# Difficulty tiers expected by SOUL.md
EXPECTED_DIFFICULTIES = {"easy", "medium", "hard", "deceptive", "adversarial"}


def _get_canonical(spec: Dict[str, Any]) -> str:
    """Read canonical answer from a spec, tolerating current field-name drift."""
    return str(spec.get("canonical") or spec.get("gold_answer") or "").strip()


def _get_rule(spec: Dict[str, Any]) -> str:
    """Read grading rule from a spec, tolerating current field-name drift."""
    return str(spec.get("rule") or spec.get("grader_rule") or "")


# ---------------------------------------------------------------------------
# Check 1: CSV ↔ Answer key alignment (FAIL)
# ---------------------------------------------------------------------------

def check_csv_answer_key_alignment(df: pd.DataFrame, answer_key: AnswerKey) -> List[str]:
    """Flag example_ids present in one source but not the other."""
    csv_ids = set(df["example_id"].astype(str))
    key_ids = set(answer_key.keys())

    findings = []
    for eid in sorted(csv_ids - key_ids):
        findings.append(f"{eid}: in CSV but missing from answer key")
    for eid in sorted(key_ids - csv_ids):
        findings.append(f"{eid}: in answer key but missing from CSV")
    return findings


# ---------------------------------------------------------------------------
# Check 2: Gold answer format (WARN)
# ---------------------------------------------------------------------------

def check_gold_answer_format(df: pd.DataFrame) -> List[str]:
    """Flag gold answers that are empty, too long, or contain terminal punctuation."""
    findings = []
    for _, row in df.iterrows():
        eid = row["example_id"]
        gold = row.get("gold_answer")

        if gold is None or (isinstance(gold, float) and pd.isna(gold)) or str(gold).strip() == "":
            findings.append(f"{eid}: gold_answer is empty or None")
            continue

        gold_str = str(gold).strip()
        tokens = gold_str.split()
        if len(tokens) > 5:
            findings.append(
                f"{eid}: gold_answer has {len(tokens)} tokens ({gold_str!r}) — may cause adjudication failures"
            )

        if re.search(r"[.?!]$", gold_str):
            findings.append(
                f"{eid}: gold_answer ends with terminal punctuation ({gold_str!r})"
            )

    return findings


# ---------------------------------------------------------------------------
# Check 3: Alias adequacy (WARN)
# ---------------------------------------------------------------------------

def check_alias_adequacy(answer_key: AnswerKey) -> List[str]:
    """Flag items with too few aliases or non-numeric canonical on numeric rules."""
    findings = []
    for eid, spec in sorted(answer_key.items()):
        aliases = spec.get("aliases", [])
        if len(aliases) < 2:
            findings.append(
                f"{eid}: only {len(aliases)} alias(es) {aliases!r} — model variants may be marked wrong"
            )

        rule = _get_rule(spec)
        if rule in ("numeric_equivalence", "numeric"):
            canonical = _get_canonical(spec)
            try:
                float(canonical)
            except (ValueError, TypeError):
                findings.append(
                    f"{eid}: rule={rule!r} but canonical answer {canonical!r} is not a float"
                )

    return findings


# ---------------------------------------------------------------------------
# Check 4: Difficulty distribution (WARN)
# ---------------------------------------------------------------------------

def check_difficulty_distribution(df: pd.DataFrame) -> List[str]:
    """Report difficulty tier counts; flag any missing tier."""
    findings = []
    counts = df["difficulty"].value_counts().to_dict()

    for tier in sorted(EXPECTED_DIFFICULTIES):
        n = counts.get(tier, 0)
        findings.append(f"{tier}: {n} items")
        if n == 0:
            findings.append(f"  *** MISSING tier '{tier}' has 0 items")

    unexpected = set(counts) - EXPECTED_DIFFICULTIES
    for tier in sorted(unexpected):
        findings.append(f"unexpected tier '{tier}': {counts[tier]} items")

    return findings


# ---------------------------------------------------------------------------
# Check 5: ID format and uniqueness (FAIL)
# ---------------------------------------------------------------------------

def check_id_format_and_uniqueness(df: pd.DataFrame) -> List[str]:
    """Verify cal_NNN format, no duplicates, flag gaps."""
    findings = []
    ids = df["example_id"].astype(str).tolist()

    seen: Dict[str, int] = {}
    for eid in ids:
        seen[eid] = seen.get(eid, 0) + 1
    for eid, count in sorted(seen.items()):
        if count > 1:
            findings.append(f"{eid}: duplicate — appears {count} times")

    pattern = re.compile(r"^cal_\d{3}$")
    for eid in ids:
        if not pattern.match(eid):
            findings.append(f"{eid}: does not match cal_NNN pattern")

    numeric = sorted(int(eid.split("_")[1]) for eid in ids if pattern.match(eid))
    if numeric:
        for i in range(numeric[0], numeric[-1] + 1):
            if i not in numeric:
                findings.append(f"cal_{i:03d}: gap in sequence (warn only)")

    return findings


# ---------------------------------------------------------------------------
# Check 6: Answer key schema consistency (FAIL)
# ---------------------------------------------------------------------------

def check_answer_key_schema_consistency(answer_key: AnswerKey) -> List[str]:
    """Flag entries that drift from the notebook schema {canonical, aliases, rule}."""
    findings = []
    for eid, spec in sorted(answer_key.items()):
        actual = set(spec.keys())
        missing = EXPECTED_AK_FIELDS - actual
        extra = actual - EXPECTED_AK_FIELDS
        if missing:
            findings.append(f"{eid}: missing notebook-schema fields {sorted(missing)}")
        if extra:
            findings.append(f"{eid}: extra fields not in notebook schema {sorted(extra)}")
    return findings


# ---------------------------------------------------------------------------
# Check 7: normalize_text safety (WARN)
# ---------------------------------------------------------------------------

def check_normalize_text_safety(df: pd.DataFrame, answer_key: AnswerKey) -> List[str]:
    """Flag items where CSV gold_answer and answer key canonical disagree after normalization,
    and items with redundant aliases."""
    findings = []
    for _, row in df.iterrows():
        eid = str(row["example_id"])
        spec = answer_key.get(eid)
        if spec is None:
            continue

        csv_gold = str(row.get("gold_answer", "")).strip()
        key_canonical = _get_canonical(spec)

        norm_csv = normalize_text(csv_gold)
        norm_key = normalize_text(key_canonical)

        if norm_csv != norm_key:
            findings.append(
                f"{eid}: CSV gold_answer {csv_gold!r} normalizes to {norm_csv!r} "
                f"but answer key canonical {key_canonical!r} normalizes to {norm_key!r}"
            )

        aliases = spec.get("aliases", [])
        norm_aliases = [normalize_text(str(a)) for a in aliases]

        for alias, norm_alias in zip(aliases, norm_aliases):
            if not norm_alias:
                findings.append(f"{eid}: alias {alias!r} normalizes to empty string")

        seen_norms: Dict[str, str] = {}
        for alias, norm_alias in zip(aliases, norm_aliases):
            if norm_alias in seen_norms:
                findings.append(
                    f"{eid}: alias {alias!r} and {seen_norms[norm_alias]!r} "
                    f"both normalize to {norm_alias!r} — redundant alias"
                )
            elif norm_alias:
                seen_norms[norm_alias] = alias

    return findings


# ---------------------------------------------------------------------------
# Check 8: Adjudication.py schema drift (FAIL)
# ---------------------------------------------------------------------------

def check_adjudication_schema_drift() -> List[str]:
    """Check that adjudication.py uses notebook schema field names.

    Flags any use of old field names (canonical_answer, accepted_aliases, grader_rule)
    that should be canonical, aliases, rule respectively.
    """
    from metajudge.scoring import adjudication as adj_module

    source = inspect.getsource(adj_module)
    findings = []
    for old_name, new_name in sorted(_ADJUDICATION_DRIFT_FIELDS.items()):
        # Look for the string as a dict key or attribute access
        if re.search(rf'["\']?{re.escape(old_name)}["\']?', source):
            findings.append(
                f"adjudication.py: uses '{old_name}' — should be '{new_name}' (notebook schema)"
            )
    return findings


# ---------------------------------------------------------------------------
# Check 9: Adjudication regression (FAIL)
# ---------------------------------------------------------------------------

def check_adjudication_regression(df: pd.DataFrame, answer_key: AnswerKey) -> List[str]:
    """Run adjudicate_answer() on every production item and capture any errors.

    A non-empty result here means the package cannot score the production dataset.
    This documents the broken state so it's immediately visible when the schema
    migration is complete.
    """
    from metajudge.scoring.adjudication import adjudicate_answer

    findings = []
    errors: Dict[str, int] = {}
    first_examples: Dict[str, str] = {}

    for _, row in df.iterrows():
        eid = str(row["example_id"])
        gold = str(row.get("gold_answer", ""))
        try:
            adjudicate_answer(eid, gold, answer_key)
        except Exception as e:
            error_type = type(e).__name__
            errors[error_type] = errors.get(error_type, 0) + 1
            if error_type not in first_examples:
                first_examples[error_type] = f"{eid}: {e}"

    for error_type, count in sorted(errors.items()):
        findings.append(
            f"{error_type} on {count}/{len(df)} items — e.g. {first_examples[error_type]}"
        )

    return findings
