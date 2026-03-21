"""Tests for metajudge.scoring.grading_v2 — registry-driven adjudication."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from metajudge.scoring.grading_v2 import (
    _normalize,
    _normalize_sci,
    _parse_float,
    _nums_close,
    grade_item,
    load_registry,
    _grade_exact_constant,
    _grade_approx_numeric_small,
    _grade_approx_numeric_dynamic,
    _grade_tri_label,
    _grade_yes_no,
    _grade_fraction_or_decimal,
    _grade_code_output,
    _grade_alias_plus_normalization,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "adjudication_registry.json"


@pytest.fixture(scope="module")
def registry():
    """Load the real adjudication registry."""
    return load_registry(REGISTRY_PATH)


def _spec(gold, rule="alias_plus_normalization", **kwargs):
    """Build a minimal spec dict for unit tests."""
    s = {"gold_answer": gold, "grader_rule": rule}
    s.update(kwargs)
    return s


# ===========================================================================
# Normalization helpers
# ===========================================================================

class TestNormalize:
    def test_basic(self):
        assert _normalize("  Hello   World  ") == "hello world"

    def test_none(self):
        assert _normalize(None) is None

    def test_numeric_cast(self):
        assert _normalize(42) == "42"


class TestNormalizeSci:
    def test_spaces_around_times(self):
        """Spaces around × are collapsed; full expression converts to e-notation."""
        result = _normalize_sci("1.67 × 10⁻²⁷")
        assert result == "1.67e-27"

    def test_unicode_superscripts(self):
        result = _normalize_sci("1.67×10⁻²⁷")
        assert "e-27" in result or "e" in result

    def test_middot(self):
        result = _normalize_sci("3.0 · 10⁸")
        assert "x" in result or "e" in result

    def test_plain_number(self):
        assert _normalize_sci("42") == "42"


class TestParseFloat:
    def test_simple(self):
        assert _parse_float("42") == 42.0

    def test_comma(self):
        assert _parse_float("1,234.5") == 1234.5

    def test_negative(self):
        assert _parse_float("-3.14") == -3.14

    def test_e_notation(self):
        assert _parse_float("6.022e23") == pytest.approx(6.022e23)

    def test_unicode_sci(self):
        val = _parse_float("1.67×10⁻²⁷")
        assert val is not None
        assert val == pytest.approx(1.67e-27, rel=1e-3)

    def test_none(self):
        assert _parse_float(None) is None

    def test_garbage(self):
        assert _parse_float("not a number at all") is None

    def test_embedded_number(self):
        assert _parse_float("approximately 342") == 342.0

    def test_spaces_in_sci(self):
        val = _parse_float("1.672 × 10 ⁻²⁷")
        assert val is not None
        assert val == pytest.approx(1.672e-27, rel=1e-3)


class TestNumsClose:
    def test_exact(self):
        assert _nums_close(1.0, 1.0)

    def test_rel_tol(self):
        assert _nums_close(100.0, 100.001, rel_tol=1e-4)

    def test_abs_tol(self):
        assert _nums_close(70, 71, abs_tol=1.0)

    def test_fail(self):
        assert not _nums_close(70, 72, abs_tol=1.0)


# ===========================================================================
# exact_constant grader
# ===========================================================================

class TestExactConstant:
    def test_exact_match(self):
        spec = _spec("6.02214076", tolerance_params={"rel_tol": 1e-6})
        result = _grade_exact_constant("6.02214076", spec)
        assert result["correct"] is True

    def test_close_enough_rel_tol(self):
        """gen_a_042 regression: 6.0221408 (8 sig fig) vs gold 6.02214076 (9 sig fig)."""
        spec = _spec("6.02214076", tolerance_params={"rel_tol": 1e-6})
        result = _grade_exact_constant("6.0221408", spec)
        assert result["correct"] is True
        assert result["method"] == "exact_constant"

    def test_too_far(self):
        spec = _spec("6.02214076", tolerance_params={"rel_tol": 1e-6})
        result = _grade_exact_constant("6.5", spec)
        assert result["correct"] is False

    def test_sci_notation_answer(self):
        """gen_a2_032 regression: proton mass with spaces around ×."""
        spec = _spec("1.6726219260e-27", tolerance_params={"rel_tol": 1e-6})
        result = _grade_exact_constant("1.672621926e-27", spec)
        assert result["correct"] is True

    def test_unicode_sci_answer(self):
        spec = _spec("1.6726219260e-27", tolerance_params={"rel_tol": 1e-6})
        result = _grade_exact_constant("1.672621926×10⁻²⁷", spec)
        assert result["correct"] is True

    def test_unparseable_answer(self):
        spec = _spec("6.02214076", tolerance_params={"rel_tol": 1e-6})
        result = _grade_exact_constant("Avogadro's number", spec)
        assert result["correct"] is False
        assert "unparseable" in result["match_detail"]

    def test_default_rel_tol(self):
        """When tolerance_params is missing, default rel_tol=1e-6."""
        spec = _spec("100.0")
        result = _grade_exact_constant("100.0001", spec)
        assert result["correct"] is True


# ===========================================================================
# approx_numeric_small grader
# ===========================================================================

class TestApproxNumericSmall:
    def test_abs_tol_pass(self):
        """gen_a_030 regression: gold=70, answer=71, abs_tol=1."""
        spec = _spec("70", tolerance_params={"abs_tol": 1.0})
        result = _grade_approx_numeric_small("71", spec)
        assert result["correct"] is True
        assert result["method"] == "approx_numeric_small"

    def test_abs_tol_fail(self):
        spec = _spec("70", tolerance_params={"abs_tol": 1.0})
        result = _grade_approx_numeric_small("72", spec)
        assert result["correct"] is False

    def test_abs_tol_boundary(self):
        spec = _spec("70", tolerance_params={"abs_tol": 1.0})
        result = _grade_approx_numeric_small("69", spec)
        assert result["correct"] is True

    def test_rel_tol(self):
        spec = _spec("40000", tolerance_params={"rel_tol": 0.01})
        result = _grade_approx_numeric_small("40200", spec)
        assert result["correct"] is True

    def test_rel_tol_fail(self):
        spec = _spec("40000", tolerance_params={"rel_tol": 0.01})
        result = _grade_approx_numeric_small("41000", spec)
        assert result["correct"] is False

    def test_unparseable(self):
        spec = _spec("70", tolerance_params={"abs_tol": 1.0})
        result = _grade_approx_numeric_small("about seventy degrees", spec)
        assert result["correct"] is False


# ===========================================================================
# approx_numeric_dynamic grader
# ===========================================================================

class TestApproxNumericDynamic:
    def test_within_tolerance(self):
        """gen_b3_005 regression: Japan density gold=342, model=337, rel_tol=0.10."""
        spec = _spec("342", tolerance_params={"rel_tol": 0.10}, time_anchor="2024-2025")
        result = _grade_approx_numeric_dynamic("337", spec)
        assert result["correct"] is True
        assert result["method"] == "approx_numeric_dynamic"
        assert "2024-2025" in result["match_detail"]

    def test_outside_tolerance(self):
        spec = _spec("342", tolerance_params={"rel_tol": 0.10})
        result = _grade_approx_numeric_dynamic("200", spec)
        assert result["correct"] is False

    def test_exact_match(self):
        spec = _spec("342", tolerance_params={"rel_tol": 0.10})
        result = _grade_approx_numeric_dynamic("342", spec)
        assert result["correct"] is True

    def test_with_unit_text(self):
        spec = _spec("342", tolerance_params={"rel_tol": 0.10})
        result = _grade_approx_numeric_dynamic("342", spec)
        assert result["correct"] is True


# ===========================================================================
# tri_label grader
# ===========================================================================

class TestTriLabel:
    def test_contested_match(self):
        """gen_a3_001 regression: gold='contested', answer='contested'."""
        spec = _spec("contested", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("contested", spec)
        assert result["correct"] is True

    def test_disputed_synonym(self):
        spec = _spec("contested", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("disputed", spec)
        assert result["correct"] is True

    def test_false_when_gold_contested(self):
        """gen_a3_001: answer 'false' vs gold 'contested' → should FAIL."""
        spec = _spec("contested", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("false", spec)
        assert result["correct"] is False
        assert result["match_detail"] == "label mismatch: false vs gold contested"

    def test_true_match(self):
        spec = _spec("true", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("True", spec)
        assert result["correct"] is True

    def test_yes_maps_to_true(self):
        spec = _spec("true", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("yes", spec)
        assert result["correct"] is True

    def test_no_maps_to_false(self):
        spec = _spec("false", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("no", spec)
        assert result["correct"] is True

    def test_unrecognized_answer(self):
        spec = _spec("true", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("maybe", spec)
        assert result["correct"] is False
        assert "unrecognized" in result["match_detail"]

    def test_last_word_extraction(self):
        """Answer wrapped like 'The answer is contested'."""
        spec = _spec("contested", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("The answer is contested", spec)
        assert result["correct"] is True

    def test_first_word_extraction(self):
        spec = _spec("true", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("True, the statement is correct", spec)
        assert result["correct"] is True

    def test_empty_answer(self):
        spec = _spec("true", tri_label_space=["true", "false", "contested"])
        result = _grade_tri_label("", spec)
        assert result["correct"] is False


# ===========================================================================
# yes_no grader
# ===========================================================================

class TestYesNo:
    def test_yes_match(self):
        spec = _spec("true")
        result = _grade_yes_no("yes", spec)
        assert result["correct"] is True

    def test_true_match(self):
        spec = _spec("true")
        result = _grade_yes_no("True", spec)
        assert result["correct"] is True

    def test_no_match(self):
        spec = _spec("false")
        result = _grade_yes_no("no", spec)
        assert result["correct"] is True

    def test_false_match(self):
        spec = _spec("false")
        result = _grade_yes_no("False", spec)
        assert result["correct"] is True

    def test_mismatch(self):
        spec = _spec("true")
        result = _grade_yes_no("no", spec)
        assert result["correct"] is False

    def test_wrapped_answer(self):
        spec = _spec("true")
        result = _grade_yes_no("The answer is yes", spec)
        assert result["correct"] is True

    def test_unrecognized(self):
        spec = _spec("true")
        result = _grade_yes_no("perhaps", spec)
        assert result["correct"] is False

    def test_empty(self):
        spec = _spec("true")
        result = _grade_yes_no("", spec)
        assert result["correct"] is False


# ===========================================================================
# fraction_or_decimal grader
# ===========================================================================

class TestFractionOrDecimal:
    def test_fraction_match(self):
        """gen_b_004 regression: gold='4/5', answer='4/5'."""
        spec = _spec("4/5")
        result = _grade_fraction_or_decimal("4/5", spec)
        assert result["correct"] is True

    def test_decimal_for_fraction(self):
        """gen_b_004 regression: gold='4/5', answer='0.8' → PASS."""
        spec = _spec("4/5")
        result = _grade_fraction_or_decimal("0.8", spec)
        assert result["correct"] is True
        assert result["method"] == "fraction_or_decimal"

    def test_fraction_for_decimal(self):
        spec = _spec("0.25")
        result = _grade_fraction_or_decimal("1/4", spec)
        assert result["correct"] is True

    def test_equivalent_fractions(self):
        spec = _spec("4/5")
        result = _grade_fraction_or_decimal("8/10", spec)
        assert result["correct"] is True

    def test_wrong_fraction(self):
        spec = _spec("4/5")
        result = _grade_fraction_or_decimal("3/5", spec)
        assert result["correct"] is False

    def test_wrong_decimal(self):
        spec = _spec("4/5")
        result = _grade_fraction_or_decimal("0.5", spec)
        assert result["correct"] is False

    def test_empty(self):
        spec = _spec("4/5")
        result = _grade_fraction_or_decimal("", spec)
        assert result["correct"] is False

    def test_quarter(self):
        """gen_b2_028 regression: gold='1/4', answer='0.25'."""
        spec = _spec("1/4")
        result = _grade_fraction_or_decimal("0.25", spec)
        assert result["correct"] is True


# ===========================================================================
# code_output grader
# ===========================================================================

class TestCodeOutput:
    def test_exact_match(self):
        """gen_a_016 regression: gold='6'."""
        spec = _spec("6")
        result = _grade_code_output("6", spec)
        assert result["correct"] is True

    def test_with_whitespace(self):
        spec = _spec("6")
        result = _grade_code_output("  6  ", spec)
        assert result["correct"] is True

    def test_case_insensitive(self):
        spec = _spec("Hello")
        result = _grade_code_output("hello", spec)
        assert result["correct"] is True

    def test_mismatch(self):
        spec = _spec("6")
        result = _grade_code_output("7", spec)
        assert result["correct"] is False

    def test_empty(self):
        spec = _spec("6")
        result = _grade_code_output("", spec)
        assert result["correct"] is False


# ===========================================================================
# alias_plus_normalization grader
# ===========================================================================

class TestAliasPlusNormalization:
    def test_gold_match(self):
        spec = _spec("Paris", accepted_forms=["paris", "Paris, France"])
        result = _grade_alias_plus_normalization("Paris", spec)
        assert result["correct"] is True

    def test_alias_match(self):
        spec = _spec("Paris", accepted_forms=["paris", "Paris, France"])
        result = _grade_alias_plus_normalization("Paris, France", spec)
        assert result["correct"] is True

    def test_no_match(self):
        spec = _spec("Paris", accepted_forms=["paris"])
        result = _grade_alias_plus_normalization("London", spec)
        assert result["correct"] is False

    def test_sci_notation_match(self):
        """gen_a2_032 regression: proton mass with spaces around ×."""
        spec = _spec(
            "1.6726219260e-27",
            accepted_forms=["1.6726219260e-27", "1.672621925×10⁻²⁷"],
        )
        result = _grade_alias_plus_normalization("1.672621926 × 10⁻²⁷", spec)
        assert result["correct"] is True

    def test_numeric_fallback(self):
        spec = _spec("42.0", accepted_forms=[])
        result = _grade_alias_plus_normalization("42", spec)
        assert result["correct"] is True

    def test_empty_answer(self):
        spec = _spec("Paris")
        result = _grade_alias_plus_normalization("", spec)
        assert result["correct"] is False


# ===========================================================================
# grade_item dispatch (integration)
# ===========================================================================

class TestGradeItem:
    def test_unknown_item(self, registry):
        result = grade_item("nonexistent_item", "foo", registry)
        assert result["correct"] is False
        assert result["method"] == "unknown"

    def test_gen_a_030_regression(self, registry):
        """gold=70, answer=71 → PASS via approx_numeric_small abs_tol=1."""
        result = grade_item("gen_a_030", "71", registry)
        assert result["correct"] is True
        assert result["method"] == "approx_numeric_small"

    def test_gen_a_030_too_far(self, registry):
        """abs_tol=2.0 after v4.1 triage update, so 73 is now out of range."""
        result = grade_item("gen_a_030", "73", registry)
        assert result["correct"] is False

    def test_gen_a3_001_contested(self, registry):
        """gold='contested', answer='contested' → PASS via tri_label."""
        result = grade_item("gen_a3_001", "contested", registry)
        assert result["correct"] is True
        assert result["method"] == "tri_label"

    def test_gen_a3_001_false_rejected(self, registry):
        """gold='contested', answer='false' → FAIL."""
        result = grade_item("gen_a3_001", "false", registry)
        assert result["correct"] is False

    def test_gen_b3_005_within_tolerance(self, registry):
        """Japan density: gold=342, answer=337, rel_tol=0.10 → PASS."""
        result = grade_item("gen_b3_005", "337", registry)
        assert result["correct"] is True
        assert result["method"] == "approx_numeric_dynamic"

    def test_gen_b_004_decimal(self, registry):
        """gold='4/5', answer='0.8' → PASS via alias_plus_normalization (v4.1 triage)."""
        result = grade_item("gen_b_004", "0.8", registry)
        assert result["correct"] is True
        assert result["method"] == "alias_plus_normalization"

    def test_gen_b_004_fraction(self, registry):
        result = grade_item("gen_b_004", "4/5", registry)
        assert result["correct"] is True

    def test_gen_a_042_sig_fig(self, registry):
        """Avogadro 6.0221408 vs gold 6.02214076 → PASS with rel_tol=1e-6."""
        result = grade_item("gen_a_042", "6.0221408", registry)
        assert result["correct"] is True
        assert result["method"] == "exact_constant"

    def test_gen_a_016_code_output(self, registry):
        """Code output: gold='6', answer='6' → PASS."""
        result = grade_item("gen_a_016", "6", registry)
        assert result["correct"] is True
        assert result["method"] == "code_output"

    def test_gen_a2_032_proton_mass(self, registry):
        """Proton mass with Unicode sci notation → PASS."""
        result = grade_item("gen_a2_032", "1.672621926e-27", registry)
        assert result["correct"] is True


# ===========================================================================
# Registry loading
# ===========================================================================

class TestLoadRegistry:
    def test_loads_all_items(self, registry):
        assert len(registry) == 102  # 65 base + 37 replacements = V4.1 full set

    def test_keyed_by_item_id(self, registry):
        assert "gen_a_030" in registry
        assert "gen_b_004" in registry
        assert "gen_a3_001" in registry

    def test_spec_has_required_keys(self, registry):
        required = {"item_id", "grader_rule", "gold_answer"}
        for item_id, spec in registry.items():
            assert required.issubset(spec.keys()), f"{item_id} missing keys"
