"""
MetaJudge-AGI: Dataset Validation CLI
=======================================
Run structural and hygiene checks on:
  - V2 dataset: calibration.csv + calibration_answer_key.json
  - V4 dataset: data/metajudge_benchmark_v1.json

Usage:
    python -m metajudge.validation.run_checks

Exit codes:
    0 — no FAIL-level findings
    1 — one or more FAIL-level findings
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from metajudge.validation.dataset_checks import (
    check_adjudication_regression,
    check_adjudication_schema_drift,
    check_alias_adequacy,
    check_answer_key_schema_consistency,
    check_csv_answer_key_alignment,
    check_difficulty_distribution,
    check_gold_answer_format,
    check_id_format_and_uniqueness,
    check_normalize_text_safety,
)

# FAIL-level checks: structural problems that break adjudication
FAIL_CHECKS = {
    "CSV-Answer Key Alignment",
    "ID Format and Uniqueness",
    "Answer Key Schema Consistency",
    "Adjudication Schema Drift",
    "Adjudication Regression",
}

# ---------------------------------------------------------------------------
# V4 dataset constants
# ---------------------------------------------------------------------------

V4_EXPECTED_COUNT = 102
V4_REQUIRED_FIELDS = {"item_id", "question", "gold_answer", "aliases", "rule"}
V4_VALID_RULES = {"alias", "numeric", "yes_no"}
V4_EXPECTED_BATCH_DISTRIBUTION: Dict[int, int] = {1: 19, 2: 25, 3: 45, 4: 13}

# ---------------------------------------------------------------------------
# V4 inline check functions
# ---------------------------------------------------------------------------


def _v4_check_item_count(items: List[Dict[str, Any]]) -> List[str]:
    """FAIL: dataset must contain exactly 102 items."""
    n = len(items)
    if n != V4_EXPECTED_COUNT:
        return [f"expected {V4_EXPECTED_COUNT} items, got {n}"]
    return []


def _v4_check_unique_ids(items: List[Dict[str, Any]]) -> List[str]:
    """FAIL: all item_ids must be unique."""
    seen: Dict[str, int] = {}
    for item in items:
        iid = str(item.get("item_id", ""))
        seen[iid] = seen.get(iid, 0) + 1
    findings = []
    for iid, count in sorted(seen.items()):
        if count > 1:
            findings.append(f"{iid}: appears {count} times")
    return findings


def _v4_check_required_fields(items: List[Dict[str, Any]]) -> List[str]:
    """FAIL: every item must have all required fields present."""
    findings = []
    for item in items:
        iid = item.get("item_id", "<no id>")
        for field in sorted(V4_REQUIRED_FIELDS):
            if field not in item:
                findings.append(f"{iid}: missing field '{field}'")
    return findings


def _v4_check_no_truncated_questions(items: List[Dict[str, Any]]) -> List[str]:
    """FAIL: no question shorter than 30 characters (guards against truncation)."""
    findings = []
    for item in items:
        iid = item.get("item_id", "<no id>")
        q = str(item.get("question") or "")
        if len(q) <= 30:
            findings.append(
                f"{iid}: question too short ({len(q)} chars) — may be truncated: {q!r}"
            )
    return findings


def _v4_check_valid_rules(items: List[Dict[str, Any]]) -> List[str]:
    """FAIL: every item's rule must be one of alias, numeric, yes_no."""
    findings = []
    for item in items:
        iid = item.get("item_id", "<no id>")
        rule = item.get("rule")
        if rule not in V4_VALID_RULES:
            findings.append(
                f"{iid}: invalid rule {rule!r} (expected one of {sorted(V4_VALID_RULES)})"
            )
    return findings


def _v4_check_gold_answer_fallback(items: List[Dict[str, Any]]) -> List[str]:
    """FAIL: items with empty aliases[] must still have a non-empty gold_answer."""
    findings = []
    for item in items:
        iid = item.get("item_id", "<no id>")
        aliases = item.get("aliases", None)
        gold = str(item.get("gold_answer") or "").strip()
        if isinstance(aliases, list) and len(aliases) == 0 and not gold:
            findings.append(
                f"{iid}: empty aliases[] and empty gold_answer — adjudicate() has no fallback"
            )
    return findings


def _v4_check_batch_distribution(items: List[Dict[str, Any]]) -> List[str]:
    """WARN: batch item counts should match expected distribution."""
    actual: Dict[int, int] = {}
    for item in items:
        b = item.get("batch")
        actual[b] = actual.get(b, 0) + 1

    findings = []
    for batch, expected in sorted(V4_EXPECTED_BATCH_DISTRIBUTION.items()):
        got = actual.get(batch, 0)
        status = "OK" if got == expected else "MISMATCH"
        findings.append(f"batch {batch}: expected {expected}, got {got} [{status}]")
    unexpected = set(actual.keys()) - set(V4_EXPECTED_BATCH_DISTRIBUTION.keys())
    for b in sorted(unexpected, key=lambda x: (x is None, x)):
        findings.append(f"unexpected batch value {b!r}: {actual[b]} items")
    return findings


def _v4_check_empty_aliases(items: List[Dict[str, Any]]) -> List[str]:
    """WARN: report count of items with empty aliases list."""
    empty = [item.get("item_id", "<no id>") for item in items
             if isinstance(item.get("aliases"), list) and len(item["aliases"]) == 0]
    if not empty:
        return []
    return [f"{len(empty)} item(s) have empty aliases[] (gold_answer used as sole match target)"]


def _load_data(repo_root: Path) -> tuple:
    csv_path = repo_root / "data" / "calibration.csv"
    key_path = repo_root / "data" / "calibration_answer_key.json"

    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        sys.exit(2)
    if not key_path.exists():
        print(f"ERROR: {key_path} not found")
        sys.exit(2)

    df = pd.read_csv(csv_path)
    with open(key_path) as f:
        answer_key = json.load(f)

    return df, answer_key


def _print_check(name: str, findings: list[str], is_fail_level: bool) -> int:
    """Print a check result. Returns 1 if failed, 0 otherwise."""
    level = "FAIL" if is_fail_level else "WARN"

    if not findings:
        print(f"  [PASS] {name}")
        return 0

    status = f"[{level}]"
    print(f"  {status} {name} ({len(findings)} finding{'s' if len(findings) != 1 else ''})")
    for f in findings:
        print(f"     - {f}")
    return 1 if is_fail_level else 0


def main() -> None:
    repo_root = Path(__file__).parent.parent.parent
    df, answer_key = _load_data(repo_root)

    # -----------------------------------------------------------------------
    # V2 Dataset Validation
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("  V2 Dataset Validation")
    print(f"  {len(df)} CSV rows | {len(answer_key)} answer key entries")
    print("=" * 60)
    print()

    checks = [
        ("CSV-Answer Key Alignment",      check_csv_answer_key_alignment(df, answer_key)),
        ("ID Format and Uniqueness",       check_id_format_and_uniqueness(df)),
        ("Answer Key Schema Consistency",  check_answer_key_schema_consistency(answer_key)),
        ("Adjudication Schema Drift",      check_adjudication_schema_drift()),
        ("Adjudication Regression",        check_adjudication_regression(df, answer_key)),
        ("Gold Answer Format",             check_gold_answer_format(df)),
        ("Alias Adequacy",                 check_alias_adequacy(answer_key)),
        ("Difficulty Distribution",        check_difficulty_distribution(df)),
        ("Normalize-Text Safety",          check_normalize_text_safety(df, answer_key)),
    ]

    n_pass = n_warn = n_fail = 0
    for name, findings in checks:
        is_fail = name in FAIL_CHECKS
        _print_check(name, findings, is_fail)
        if not findings:
            n_pass += 1
        elif is_fail:
            n_fail += 1
        else:
            n_warn += 1

    print()
    print("=" * 60)
    print(f"  V2 Summary: {n_pass} passed, {n_warn} warning(s), {n_fail} failure(s)")
    print("=" * 60)

    v2_fail = n_fail

    # -----------------------------------------------------------------------
    # V4 Dataset Validation  (data/metajudge_benchmark_v1.json)
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("  V4 Dataset Validation")
    print("  (data/metajudge_benchmark_v1.json)")
    print("=" * 60)
    print()

    v4_path = repo_root / "data" / "metajudge_benchmark_v1.json"
    if not v4_path.exists():
        print(f"  NOTE: {v4_path} not found — skipping V4 validation")
        print()
        sys.exit(1 if v2_fail > 0 else 0)

    with open(v4_path, encoding="utf-8") as fh:
        v4_items = json.load(fh)

    print(f"  {len(v4_items)} items loaded from {v4_path.name}")
    print()

    # FAIL-level checks for V4
    V4_FAIL_CHECKS = [
        ("V4 Item Count",            _v4_check_item_count(v4_items)),
        ("V4 Unique Item IDs",        _v4_check_unique_ids(v4_items)),
        ("V4 Required Fields",        _v4_check_required_fields(v4_items)),
        ("V4 No Truncated Questions", _v4_check_no_truncated_questions(v4_items)),
        ("V4 Valid Rules",            _v4_check_valid_rules(v4_items)),
        ("V4 Gold Answer Fallback",   _v4_check_gold_answer_fallback(v4_items)),
    ]

    # WARN-level checks for V4
    V4_WARN_CHECKS = [
        ("V4 Batch Distribution",    _v4_check_batch_distribution(v4_items)),
        ("V4 Empty Aliases",         _v4_check_empty_aliases(v4_items)),
    ]

    v4_pass = v4_warn = v4_fail = 0
    for name, findings in V4_FAIL_CHECKS:
        result = _print_check(name, findings, is_fail_level=True)
        if not findings:
            v4_pass += 1
        else:
            v4_fail += result

    for name, findings in V4_WARN_CHECKS:
        result = _print_check(name, findings, is_fail_level=False)
        if not findings:
            v4_pass += 1
        else:
            v4_warn += 1

    print()
    print("=" * 60)
    print(f"  V4 Summary: {v4_pass} passed, {v4_warn} warning(s), {v4_fail} failure(s)")
    print("=" * 60)

    total_fail = v2_fail + v4_fail
    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
