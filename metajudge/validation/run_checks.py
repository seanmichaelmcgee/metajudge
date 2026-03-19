"""
MetaJudge-AGI: Dataset Validation CLI
=======================================
Run structural and hygiene checks on calibration.csv and answer key.

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

    print("=" * 60)
    print("  MetaJudge-AGI Dataset Validation Report")
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
        result = _print_check(name, findings, is_fail)
        if not findings:
            n_pass += 1
        elif is_fail:
            n_fail += 1
        else:
            n_warn += 1

    print()
    print("=" * 60)
    print(f"  Summary: {n_pass} passed, {n_warn} warning(s), {n_fail} failure(s)")
    print("=" * 60)

    sys.exit(1 if n_fail > 0 else 0)


if __name__ == "__main__":
    main()
