"""
MetaJudge-AGI: Dataset Validation Checks
==========================================
Structural and hygiene checks for calibration.csv and the answer key.

Schema note: the actual answer key (data/calibration_answer_key.json) uses
field names 'gold_answer' and 'aliases', NOT 'canonical_answer' and
'accepted_aliases' as referenced in metajudge/scoring/adjudication.py.
This discrepancy is a known finding — do not resolve here.

Run via: python -m metajudge.validation.run_checks
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

import pandas as pd

from metajudge.utils.text import normalize_text

AnswerKey = Dict[str, Dict[str, Any]]

# Fields expected on every answer key entry (based on actual data inspection)
EXPECTED_AK_FIELDS = {"gold_answer", "aliases", "answer_type", "grader_rule", "format_instruction"}

# Difficulty tiers expected by SOUL.md
EXPECTED_DIFFICULTIES = {"easy", "medium", "hard", "deceptive", "adversarial"}


# ---------------------------------------------------------------------------
# Check 1: CSV ↔ Answer key alignment
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
# Check 2: Gold answer format
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
# Check 3: Alias adequacy
# ---------------------------------------------------------------------------

def check_alias_adequacy(answer_key: AnswerKey) -> List[str]:
    """Flag items with too few aliases or bad numeric canonical answers."""
    findings = []
    for eid, spec in sorted(answer_key.items()):
        aliases = spec.get("aliases", [])
        if len(aliases) < 2:
            findings.append(
                f"{eid}: only {len(aliases)} alias(es) {aliases!r} — model variants may be marked wrong"
            )

        # For numeric_equivalence items, canonical must parse as float
        if spec.get("grader_rule") == "numeric_equivalence":
            canonical = spec.get("gold_answer", "")
            try:
                float(str(canonical))
            except (ValueError, TypeError):
                findings.append(
                    f"{eid}: grader_rule=numeric_equivalence but gold_answer {canonical!r} is not a float"
                )

    return findings


# ---------------------------------------------------------------------------
# Check 4: Difficulty distribution
# ---------------------------------------------------------------------------

def check_difficulty_distribution(df: pd.DataFrame) -> List[str]:
    """Report difficulty tier counts; flag any missing tier."""
    findings = []
    counts = df["difficulty"].value_counts().to_dict()

    for tier in EXPECTED_DIFFICULTIES:
        n = counts.get(tier, 0)
        findings.append(f"{tier}: {n} items")
        if n == 0:
            findings.append(f"  *** MISSING tier '{tier}' has 0 items")

    unexpected = set(counts) - EXPECTED_DIFFICULTIES
    for tier in sorted(unexpected):
        findings.append(f"unexpected tier '{tier}': {counts[tier]} items")

    return findings


# ---------------------------------------------------------------------------
# Check 5: ID format and uniqueness
# ---------------------------------------------------------------------------

def check_id_format_and_uniqueness(df: pd.DataFrame) -> List[str]:
    """Verify cal_NNN format, no duplicates, and flag gaps."""
    findings = []
    ids = df["example_id"].astype(str).tolist()

    # Duplicates
    seen: Dict[str, int] = {}
    for eid in ids:
        seen[eid] = seen.get(eid, 0) + 1
    for eid, count in sorted(seen.items()):
        if count > 1:
            findings.append(f"{eid}: duplicate — appears {count} times")

    # Format
    pattern = re.compile(r"^cal_\d{3}$")
    bad_format = [eid for eid in ids if not pattern.match(eid)]
    for eid in bad_format:
        findings.append(f"{eid}: does not match cal_NNN pattern")

    # Gaps (warn only — not a FAIL)
    numeric = sorted(
        int(eid.split("_")[1]) for eid in ids if pattern.match(eid)
    )
    if numeric:
        for i in range(numeric[0], numeric[-1] + 1):
            if i not in numeric:
                findings.append(f"cal_{i:03d}: gap in sequence (warn only)")

    return findings


# ---------------------------------------------------------------------------
# Check 6: Answer key schema consistency
# ---------------------------------------------------------------------------

def check_answer_key_schema_consistency(answer_key: AnswerKey) -> List[str]:
    """Flag entries with missing or extra fields relative to the expected schema."""
    findings = []
    for eid, spec in sorted(answer_key.items()):
        actual = set(spec.keys())
        missing = EXPECTED_AK_FIELDS - actual
        extra = actual - EXPECTED_AK_FIELDS
        if missing:
            findings.append(f"{eid}: missing fields {sorted(missing)}")
        if extra:
            findings.append(f"{eid}: unexpected extra fields {sorted(extra)}")
    return findings


# ---------------------------------------------------------------------------
# Check 7: normalize_text safety
# ---------------------------------------------------------------------------

def check_normalize_text_safety(df: pd.DataFrame, answer_key: AnswerKey) -> List[str]:
    """Flag items where normalized CSV gold_answer != normalized answer key gold_answer,
    and items where alias normalization is inconsistent with canonical."""
    findings = []
    for _, row in df.iterrows():
        eid = str(row["example_id"])
        spec = answer_key.get(eid)
        if spec is None:
            continue

        csv_gold = str(row.get("gold_answer", "")).strip()
        key_gold = str(spec.get("gold_answer", "")).strip()

        norm_csv = normalize_text(csv_gold)
        norm_key = normalize_text(key_gold)

        if norm_csv != norm_key:
            findings.append(
                f"{eid}: CSV gold_answer {csv_gold!r} normalizes to {norm_csv!r} "
                f"but answer key gold_answer {key_gold!r} normalizes to {norm_key!r}"
            )

        # Check alias consistency: each alias should normalize to something
        # meaningful (warn if any alias normalizes identically to another)
        aliases = spec.get("aliases", [])
        norm_aliases = [normalize_text(str(a)) for a in aliases]
        norm_canonical = norm_key
        for alias, norm_alias in zip(aliases, norm_aliases):
            if norm_alias is None or norm_alias == "":
                findings.append(f"{eid}: alias {alias!r} normalizes to empty string")

        # Warn if duplicate normalized aliases
        seen_norms: Dict[str, str] = {}
        for alias, norm_alias in zip(aliases, norm_aliases):
            if norm_alias in seen_norms:
                findings.append(
                    f"{eid}: alias {alias!r} and {seen_norms[norm_alias]!r} "
                    f"both normalize to {norm_alias!r} — redundant alias"
                )
            else:
                if norm_alias is not None:
                    seen_norms[norm_alias] = alias

    return findings
