"""Unit tests for the v2 grader — grading semantics freeze for Phase 1."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts to path so we can import the sweep grader
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.regrade_sweep_v062 import (
    grade_approx_numeric_small_v2,
    grade_alias_plus_normalization_v2,
    grade_code_output_v2,
    grade_fraction_or_decimal_v2,
    grade_yes_no_v2,
    grade_item_v2,
    strip_markdown,
    check_text_answer,
    extract_all_numbers,
    extract_best_number,
)


# ===========================================================================
# approx_numeric_small
# ===========================================================================

class TestApproxNumericSmall:
    """Tests for grade_approx_numeric_small_v2."""

    def test_basic_numeric_match(self):
        """Basic numeric match: "The answer is 243" with gold=243."""
        assert grade_approx_numeric_small_v2(
            "The answer is 243", "243", None
        ) is True

    def test_alias_text_match(self):
        """Alias text match: "Seven continents" with gold=7, aliases=["7","seven"]."""
        assert grade_approx_numeric_small_v2(
            "Seven continents", "7", None, aliases=["7", "seven"]
        ) is True

    def test_within_abs_tol(self):
        """Within abs_tol: "122 degrees" with gold=121.5, abs_tol=0.5."""
        assert grade_approx_numeric_small_v2(
            "122 degrees", "121.5", {"abs_tol": 0.5, "rel_tol": 0.01}
        ) is True

    def test_outside_abs_tol(self):
        """Outside abs_tol: "120 degrees" with gold=121.5, abs_tol=0.5."""
        assert grade_approx_numeric_small_v2(
            "120 degrees", "121.5", {"abs_tol": 0.5, "rel_tol": 0.01}
        ) is False

    def test_boundary_abs_tol(self):
        """Boundary: "121 degrees" with gold=121.5, abs_tol=0.5 → True (|121.5-121|=0.5, <=0.5)."""
        assert grade_approx_numeric_small_v2(
            "121 degrees", "121.5", {"abs_tol": 0.5, "rel_tol": 0.01}
        ) is True

    def test_intermediate_numbers_correct_final(self):
        """Intermediate numbers: response with gold=121.5 present as final answer."""
        response = "33 × 0.5 = 16.5 degrees. 60 + 16.5 = 76.5. 198 - 76.5 = 121.5"
        assert grade_approx_numeric_small_v2(
            response, "121.5", {"abs_tol": 0.5, "rel_tol": 0.01}
        ) is True

    def test_wrong_final_answer_with_intermediates(self):
        """Wrong final answer with intermediates: gold=121.5 but answer=138."""
        response = "2:33 means 33 × 6 = 198, minus 60 = 138"
        assert grade_approx_numeric_small_v2(
            response, "121.5", {"abs_tol": 0.5, "rel_tol": 0.01}
        ) is False

    def test_no_aliases_defaults_empty(self):
        """Without aliases, numeric extraction still works."""
        assert grade_approx_numeric_small_v2(
            "The number is 42", "42", None
        ) is True

    def test_alias_with_markdown(self):
        """Alias match should work even with markdown formatting."""
        assert grade_approx_numeric_small_v2(
            "**Seven** continents", "7", None, aliases=["7", "seven"]
        ) is True

    def test_gold_not_a_number(self):
        """Non-numeric gold returns False from numeric path."""
        assert grade_approx_numeric_small_v2(
            "The answer is hello", "hello", None
        ) is False


# ===========================================================================
# alias_plus_normalization
# ===========================================================================

class TestAliasPlusNormalization:
    """Tests for grade_alias_plus_normalization_v2."""

    def test_basic_text(self):
        """Basic text: "The answer is Gold" with gold="Gold"."""
        assert grade_alias_plus_normalization_v2(
            "The answer is Gold", "Gold", ["Au"]
        ) is True

    def test_alias_match(self):
        """Alias match: "The element is Au" with gold="Gold", aliases=["Au"]."""
        assert grade_alias_plus_normalization_v2(
            "The element is Au", "Gold", ["Au"]
        ) is True

    def test_numeric_fallback(self):
        """Numeric fallback: "The answer is 42" with gold="42"."""
        assert grade_alias_plus_normalization_v2(
            "The answer is 42", "42", []
        ) is True

    def test_fraction_substring(self):
        """Fraction substring: "3/16" in response with gold="3/16"."""
        assert grade_alias_plus_normalization_v2(
            "The fraction is 3/16", "3/16", []
        ) is True

    def test_markdown_stripping(self):
        """Markdown stripping: "The answer is **Gold**" → True."""
        assert grade_alias_plus_normalization_v2(
            "The answer is **Gold**", "Gold", ["Au"]
        ) is True

    def test_no_match(self):
        """No match: wrong answer."""
        assert grade_alias_plus_normalization_v2(
            "The element is Silver", "Gold", ["Au"]
        ) is False

    def test_case_insensitive(self):
        """Case insensitive matching."""
        assert grade_alias_plus_normalization_v2(
            "the answer is gold", "Gold", []
        ) is True

    def test_empty_response(self):
        """Empty response returns False."""
        assert grade_alias_plus_normalization_v2("", "Gold", []) is False


# ===========================================================================
# code_output
# ===========================================================================

class TestCodeOutput:
    """Tests for grade_code_output_v2."""

    def test_exact_match(self):
        """Exact match: "12" with gold="12"."""
        assert grade_code_output_v2("12", "12", []) is True

    def test_text_alias(self):
        """Text alias: "twelve" with gold="12", aliases=["12.0","twelve"]."""
        assert grade_code_output_v2(
            "twelve", "12", ["12.0", "twelve"]
        ) is True

    def test_wrong(self):
        """Wrong: "10" with gold="12"."""
        assert grade_code_output_v2("10", "12", []) is False

    def test_numeric_equivalence(self):
        """Numeric equivalence: "12.0" matches "12"."""
        assert grade_code_output_v2("12.0", "12", []) is True


# ===========================================================================
# fraction_or_decimal
# ===========================================================================

class TestFractionOrDecimal:
    """Tests for grade_fraction_or_decimal_v2."""

    def test_fraction(self):
        """Fraction: "3/16" with gold="3/16"."""
        assert grade_fraction_or_decimal_v2("3/16", "3/16", []) is True

    def test_decimal_alias(self):
        """Decimal: "0.1875" with gold="3/16", aliases=["3/16","0.1875"]."""
        assert grade_fraction_or_decimal_v2(
            "0.1875", "3/16", ["3/16", "0.1875"]
        ) is True

    def test_wrong_fraction(self):
        """Wrong fraction: "3/8" with gold="3/16"."""
        assert grade_fraction_or_decimal_v2("3/8", "3/16", []) is False

    def test_equivalent_fraction_not_matched(self):
        """Equivalent fraction: "6/32" vs "3/16" — not matched (no cross-fraction eval)."""
        # The grader doesn't cross-evaluate fractions in response against fraction gold.
        # This is an accepted limitation documented in the grading freeze note.
        assert grade_fraction_or_decimal_v2("6/32", "3/16", []) is False

    def test_decimal_for_fraction_gold(self):
        """Decimal response for fraction gold via evaluation."""
        assert grade_fraction_or_decimal_v2("0.1875", "3/16", []) is True

    def test_empty_response(self):
        """Empty response returns False."""
        assert grade_fraction_or_decimal_v2("", "3/16", []) is False


# ===========================================================================
# yes_no
# ===========================================================================

class TestYesNo:
    """Tests for grade_yes_no_v2."""

    def test_correct_yes(self):
        """Correct yes: "Yes, definitely" with gold="yes"."""
        assert grade_yes_no_v2("Yes, definitely", "yes") is True

    def test_correct_no(self):
        """Correct no: "No, it is not" with gold="no"."""
        assert grade_yes_no_v2("No, it is not", "no") is True

    def test_wrong_yes_for_no(self):
        """Wrong: "Yes" with gold="no"."""
        assert grade_yes_no_v2("Yes", "no") is False

    def test_wrong_no_for_yes(self):
        """Wrong: "No" with gold="yes"."""
        assert grade_yes_no_v2("No", "yes") is False

    def test_empty_response(self):
        """Empty response returns False."""
        assert grade_yes_no_v2("", "yes") is False

    def test_invalid_gold(self):
        """Non yes/no gold returns False."""
        assert grade_yes_no_v2("maybe", "maybe") is False


# ===========================================================================
# grade_item_v2 dispatcher
# ===========================================================================

class TestGradeItemV2:
    """Tests for the grade_item_v2 dispatcher."""

    def test_approx_numeric_small_gets_aliases(self):
        """Test that approx_numeric_small items get aliases passed through."""
        item = {
            "grading_rule": "approx_numeric_small",
            "gold_answer": "7",
            "gold_answer_aliases": ["7", "seven"],
            "tolerance": None,
        }
        # "Seven continents" should match via alias
        assert grade_item_v2("Seven continents", item) is True

    def test_approx_numeric_small_numeric_path(self):
        """Numeric path still works through dispatcher."""
        item = {
            "grading_rule": "approx_numeric_small",
            "gold_answer": "243",
            "gold_answer_aliases": [],
            "tolerance": None,
        }
        assert grade_item_v2("The answer is 243", item) is True

    def test_unknown_rule_falls_back(self):
        """Unknown grading rules fall back to alias_plus_normalization."""
        item = {
            "grading_rule": "some_unknown_rule",
            "gold_answer": "Paris",
            "gold_answer_aliases": ["paris"],
            "tolerance": None,
        }
        assert grade_item_v2("The answer is Paris", item) is True

    def test_alias_plus_normalization_dispatch(self):
        """alias_plus_normalization rule dispatches correctly."""
        item = {
            "grading_rule": "alias_plus_normalization",
            "gold_answer": "Gold",
            "gold_answer_aliases": ["Au"],
            "tolerance": None,
        }
        assert grade_item_v2("Au is the symbol", item) is True

    def test_yes_no_dispatch(self):
        """yes_no rule dispatches correctly."""
        item = {
            "grading_rule": "yes_no",
            "gold_answer": "yes",
            "gold_answer_aliases": [],
            "tolerance": None,
        }
        assert grade_item_v2("Yes, definitely", item) is True

    def test_code_output_dispatch(self):
        """code_output rule dispatches correctly."""
        item = {
            "grading_rule": "code_output",
            "gold_answer": "12",
            "gold_answer_aliases": ["twelve"],
            "tolerance": None,
        }
        assert grade_item_v2("twelve", item) is True

    def test_fraction_or_decimal_dispatch(self):
        """fraction_or_decimal rule dispatches correctly."""
        item = {
            "grading_rule": "fraction_or_decimal",
            "gold_answer": "3/16",
            "gold_answer_aliases": ["0.1875"],
            "tolerance": None,
        }
        assert grade_item_v2("0.1875", item) is True


# ===========================================================================
# Helper function tests
# ===========================================================================

class TestHelpers:
    """Tests for helper functions."""

    def test_strip_markdown_bold(self):
        assert strip_markdown("**bold**") == "bold"

    def test_strip_markdown_italic(self):
        assert strip_markdown("*italic*") == "italic"

    def test_strip_markdown_code(self):
        assert strip_markdown("`code`") == "code"

    def test_check_text_answer_basic(self):
        assert check_text_answer("The answer is Gold", "Gold", []) is True

    def test_check_text_answer_alias(self):
        assert check_text_answer("The element is Au", "Gold", ["Au"]) is True

    def test_check_text_answer_no_match(self):
        assert check_text_answer("Silver is wrong", "Gold", ["Au"]) is False

    def test_extract_all_numbers(self):
        nums = extract_all_numbers("47 × 23 = 1081")
        assert 47 in nums
        assert 23 in nums
        assert 1081 in nums
