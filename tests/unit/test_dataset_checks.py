"""Unit tests for dataset validation checks.

Tests use small synthetic data — not the real calibration dataset.
FULL_SPEC uses the notebook schema (canonical/aliases/rule) as the source of truth.

Source: dataset-validation-task.md
"""

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _df(*rows):
    """Build a minimal DataFrame from dicts."""
    return pd.DataFrame(rows)


# Notebook schema — source of truth
# Canonical schema (per SOUL.md)
FULL_SPEC = {
    "gold_answer": "paris",
    "aliases": ["paris", "france capital"],
    "rule": "alias",
}

# Old-schema spec (pre-unification) — used only in drift/regression tests
OLD_SPEC = {
    "canonical_answer": "paris",
    "accepted_aliases": ["paris", "France capital"],
    "answer_type": "entity",
    "grader_rule": "alias_match",
    "format_instruction": "one_word",
}


# ---------------------------------------------------------------------------
# Check 1: CSV ↔ Answer Key Alignment
# ---------------------------------------------------------------------------

class TestCsvAnswerKeyAlignment:
    def test_all_match(self):
        df = _df(
            {"example_id": "cal_001", "gold_answer": "3", "difficulty": "easy"},
            {"example_id": "cal_002", "gold_answer": "paris", "difficulty": "medium"},
        )
        ak = {"cal_001": FULL_SPEC.copy(), "cal_002": FULL_SPEC.copy()}
        assert check_csv_answer_key_alignment(df, ak) == []

    def test_csv_id_missing_from_key(self):
        df = _df({"example_id": "cal_001", "gold_answer": "3", "difficulty": "easy"})
        ak = {}
        findings = check_csv_answer_key_alignment(df, ak)
        assert any("cal_001" in f and "missing from answer key" in f for f in findings)

    def test_key_id_missing_from_csv(self):
        df = _df({"example_id": "cal_001", "gold_answer": "3", "difficulty": "easy"})
        ak = {"cal_001": FULL_SPEC.copy(), "cal_099": FULL_SPEC.copy()}
        findings = check_csv_answer_key_alignment(df, ak)
        assert any("cal_099" in f and "missing from CSV" in f for f in findings)


# ---------------------------------------------------------------------------
# Check 2: Gold Answer Format
# ---------------------------------------------------------------------------

class TestGoldAnswerFormat:
    def test_normal_answer_passes(self):
        df = _df({"example_id": "cal_001", "gold_answer": "paris", "difficulty": "easy"})
        assert check_gold_answer_format(df) == []

    def test_too_long_flagged(self):
        df = _df({"example_id": "cal_001", "gold_answer": "one two three four five six", "difficulty": "easy"})
        findings = check_gold_answer_format(df)
        assert any("6 tokens" in f for f in findings)

    def test_terminal_punctuation_flagged(self):
        df = _df({"example_id": "cal_001", "gold_answer": "Paris.", "difficulty": "easy"})
        findings = check_gold_answer_format(df)
        assert any("terminal punctuation" in f for f in findings)

    def test_empty_flagged(self):
        df = _df({"example_id": "cal_001", "gold_answer": "", "difficulty": "easy"})
        findings = check_gold_answer_format(df)
        assert any("empty" in f for f in findings)

    def test_five_tokens_ok(self):
        df = _df({"example_id": "cal_001", "gold_answer": "one two three four five", "difficulty": "easy"})
        assert check_gold_answer_format(df) == []


# ---------------------------------------------------------------------------
# Check 3: Alias Adequacy
# ---------------------------------------------------------------------------

class TestAliasAdequacy:
    def test_adequate_aliases_pass(self):
        ak = {"cal_001": {**FULL_SPEC, "aliases": ["paris", "France capital", "city of light"]}}
        assert check_alias_adequacy(ak) == []

    def test_single_alias_flagged(self):
        ak = {"cal_001": {**FULL_SPEC, "aliases": ["au"]}}
        findings = check_alias_adequacy(ak)
        assert any("cal_001" in f and "1 alias" in f for f in findings)

    def test_zero_aliases_flagged(self):
        ak = {"cal_001": {**FULL_SPEC, "aliases": []}}
        findings = check_alias_adequacy(ak)
        assert any("cal_001" in f and "0 alias" in f for f in findings)

    def test_numeric_rule_valid_float(self):
        ak = {"cal_001": {**FULL_SPEC, "gold_answer": "42", "rule": "numeric", "aliases": ["42", "42.0"]}}
        assert check_alias_adequacy(ak) == []

    def test_numeric_rule_bad_canonical(self):
        ak = {"cal_001": {**FULL_SPEC, "gold_answer": "forty-two", "rule": "numeric", "aliases": ["42", "42.0"]}}
        findings = check_alias_adequacy(ak)
        assert any("not a float" in f for f in findings)

    def test_old_schema_numeric_equivalence_still_caught(self):
        # Tolerates grader_rule field name drift — still catches bad canonical
        ak = {"cal_001": {**OLD_SPEC, "gold_answer": "not-a-number", "grader_rule": "numeric_equivalence",
                          "aliases": ["42", "42.0"]}}
        findings = check_alias_adequacy(ak)
        assert any("not a float" in f for f in findings)


# ---------------------------------------------------------------------------
# Check 4: Difficulty Distribution
# ---------------------------------------------------------------------------

class TestDifficultyDistribution:
    def test_all_tiers_present(self):
        df = _df(
            {"example_id": "cal_001", "gold_answer": "x", "difficulty": "easy"},
            {"example_id": "cal_002", "gold_answer": "x", "difficulty": "medium"},
            {"example_id": "cal_003", "gold_answer": "x", "difficulty": "hard"},
            {"example_id": "cal_004", "gold_answer": "x", "difficulty": "deceptive"},
            {"example_id": "cal_005", "gold_answer": "x", "difficulty": "adversarial"},
        )
        findings = check_difficulty_distribution(df)
        assert not any("MISSING" in f for f in findings)

    def test_missing_tier_flagged(self):
        df = _df({"example_id": "cal_001", "gold_answer": "x", "difficulty": "easy"})
        findings = check_difficulty_distribution(df)
        assert any("MISSING" in f and "medium" in f for f in findings)

    def test_unexpected_tier_noted(self):
        df = _df({"example_id": "cal_001", "gold_answer": "x", "difficulty": "legendary"})
        findings = check_difficulty_distribution(df)
        assert any("unexpected" in f and "legendary" in f for f in findings)


# ---------------------------------------------------------------------------
# Check 5: ID Format and Uniqueness
# ---------------------------------------------------------------------------

class TestIdFormatAndUniqueness:
    def test_valid_ids_pass(self):
        df = _df(
            {"example_id": "cal_001", "gold_answer": "x", "difficulty": "easy"},
            {"example_id": "cal_002", "gold_answer": "x", "difficulty": "easy"},
        )
        findings = check_id_format_and_uniqueness(df)
        assert not any("duplicate" in f or "does not match" in f for f in findings)

    def test_duplicate_flagged(self):
        df = _df(
            {"example_id": "cal_001", "gold_answer": "x", "difficulty": "easy"},
            {"example_id": "cal_001", "gold_answer": "y", "difficulty": "easy"},
        )
        findings = check_id_format_and_uniqueness(df)
        assert any("duplicate" in f for f in findings)

    def test_bad_format_flagged(self):
        df = _df({"example_id": "item_1", "gold_answer": "x", "difficulty": "easy"})
        findings = check_id_format_and_uniqueness(df)
        assert any("does not match" in f for f in findings)

    def test_gap_noted(self):
        df = _df(
            {"example_id": "cal_001", "gold_answer": "x", "difficulty": "easy"},
            {"example_id": "cal_003", "gold_answer": "x", "difficulty": "easy"},
        )
        findings = check_id_format_and_uniqueness(df)
        assert any("cal_002" in f and "gap" in f for f in findings)


# ---------------------------------------------------------------------------
# Check 6: Answer Key Schema Consistency
# ---------------------------------------------------------------------------

class TestAnswerKeySchemaConsistency:
    def test_notebook_schema_passes(self):
        ak = {"cal_001": FULL_SPEC.copy(), "cal_002": FULL_SPEC.copy()}
        assert check_answer_key_schema_consistency(ak) == []

    def test_old_schema_flagged_as_missing_fields(self):
        # OLD_SPEC uses canonical_answer/accepted_aliases/grader_rule — missing gold_answer/aliases/rule
        ak = {"cal_001": OLD_SPEC.copy()}
        findings = check_answer_key_schema_consistency(ak)
        assert any("cal_001" in f and "missing" in f for f in findings)

    def test_missing_field_flagged(self):
        bad = {k: v for k, v in FULL_SPEC.items() if k != "rule"}
        ak = {"cal_001": FULL_SPEC.copy(), "cal_002": bad}
        findings = check_answer_key_schema_consistency(ak)
        assert any("cal_002" in f and "missing" in f for f in findings)

    def test_extra_field_flagged(self):
        extra = {**FULL_SPEC, "notes": "some note"}
        ak = {"cal_001": FULL_SPEC.copy(), "cal_002": extra}
        findings = check_answer_key_schema_consistency(ak)
        assert any("cal_002" in f and "extra" in f for f in findings)


# ---------------------------------------------------------------------------
# Check 7: Normalize-Text Safety
# ---------------------------------------------------------------------------

class TestNormalizeTextSafety:
    def test_matching_canonical_passes(self):
        df = _df({"example_id": "cal_001", "gold_answer": "Paris", "difficulty": "easy"})
        ak = {"cal_001": {**FULL_SPEC, "gold_answer": "paris", "aliases": ["paris", "france capital"]}}
        assert check_normalize_text_safety(df, ak) == []

    def test_mismatched_flagged(self):
        df = _df({"example_id": "cal_001", "gold_answer": "london", "difficulty": "easy"})
        ak = {"cal_001": {**FULL_SPEC, "gold_answer": "paris", "aliases": ["paris", "france capital"]}}
        findings = check_normalize_text_safety(df, ak)
        assert any("cal_001" in f and "normalizes to" in f for f in findings)

    def test_redundant_alias_flagged(self):
        df = _df({"example_id": "cal_001", "gold_answer": "paris", "difficulty": "easy"})
        ak = {"cal_001": {**FULL_SPEC, "gold_answer": "paris",
                          "aliases": ["Paris", "PARIS"]}}  # both normalize to "paris"
        findings = check_normalize_text_safety(df, ak)
        assert any("redundant alias" in f for f in findings)

    def test_old_schema_gold_answer_tolerated(self):
        # Even with old field name, matching values should not flag mismatch
        df = _df({"example_id": "cal_001", "gold_answer": "paris", "difficulty": "easy"})
        ak = {"cal_001": {**OLD_SPEC, "gold_answer": "paris", "aliases": ["paris", "france capital"]}}
        findings = check_normalize_text_safety(df, ak)
        assert not any("normalizes to" in f for f in findings)


# ---------------------------------------------------------------------------
# Check 8: Adjudication Schema Drift
# ---------------------------------------------------------------------------

class TestAdjudicationSchemaDrift:
    def test_no_drift_after_migration(self):
        # adjudication.py has been migrated — old field names must not appear
        findings = check_adjudication_schema_drift()
        assert findings == [], f"adjudication.py uses old field names: {findings}"


# ---------------------------------------------------------------------------
# Check 9: Adjudication Regression
# ---------------------------------------------------------------------------

class TestAdjudicationRegression:
    def test_old_schema_raises_key_error(self):
        # Old-schema data (gold_answer instead of canonical) must fail —
        # documents the error mode for unmigrated data
        df = _df({"example_id": "cal_001", "gold_answer": "3", "difficulty": "easy"})
        ak_old = {"cal_001": OLD_SPEC.copy()}  # gold_answer not canonical → KeyError
        findings = check_adjudication_regression(df, ak_old)
        assert len(findings) > 0
        assert any("KeyError" in f for f in findings)

    def test_no_errors_on_notebook_schema(self):
        # Notebook-schema key (canonical/aliases/rule) must score without errors
        df = _df({"example_id": "cal_001", "gold_answer": "paris", "difficulty": "easy"})
        ak = {
            "cal_001": {
                "gold_answer": "paris",
                "aliases": ["paris", "france capital"],
                "rule": "alias",
            }
        }
        findings = check_adjudication_regression(df, ak)
        assert findings == []
