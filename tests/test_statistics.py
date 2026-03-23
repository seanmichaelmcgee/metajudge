"""
Tests for metajudge.scoring.statistics — paired statistical comparisons.
"""

import numpy as np
import pytest

from metajudge.scoring.statistics import (
    bootstrap_ci_single,
    compute_family_b_stats,
    compute_pairwise_stats,
    holm_correction,
    mcnemar_test,
    paired_bootstrap_ci,
    paired_permutation_test,
    spearman_with_ci,
    stuart_maxwell_test,
)


# ---------------------------------------------------------------------------
# McNemar's test
# ---------------------------------------------------------------------------

class TestMcNemar:
    def test_identical_models(self):
        correct = [True, True, False, True, False]
        result = mcnemar_test(correct, correct)
        assert result["p_value"] == 1.0
        assert result["a_only"] == 0
        assert result["b_only"] == 0

    def test_one_sided_difference(self):
        a = [True, True, True, False, False]
        b = [False, False, False, False, False]
        result = mcnemar_test(a, b)
        assert result["a_only"] == 3
        assert result["b_only"] == 0
        assert result["p_value"] < 0.5

    def test_symmetric_discordance(self):
        a = [True, False, True, False]
        b = [False, True, False, True]
        result = mcnemar_test(a, b)
        assert result["a_only"] == 2
        assert result["b_only"] == 2
        assert result["p_value"] == 1.0


# ---------------------------------------------------------------------------
# Paired bootstrap CI
# ---------------------------------------------------------------------------

class TestPairedBootstrap:
    def test_no_difference(self):
        scores = [0.5, 0.6, 0.7, 0.8, 0.9]
        result = paired_bootstrap_ci(scores, scores)
        assert result["observed_diff"] == 0.0
        assert result["ci_lower"] <= 0.0 <= result["ci_upper"]

    def test_clear_difference(self):
        a = [1.0] * 50
        b = [0.0] * 50
        result = paired_bootstrap_ci(a, b)
        assert result["observed_diff"] == 1.0
        assert result["ci_lower"] > 0.5

    def test_ci_contains_observed(self):
        rng = np.random.default_rng(123)
        a = list(rng.normal(0.7, 0.1, 30))
        b = list(rng.normal(0.5, 0.1, 30))
        result = paired_bootstrap_ci(a, b)
        assert result["ci_lower"] <= result["observed_diff"] <= result["ci_upper"]


class TestBootstrapSingle:
    def test_basic(self):
        scores = [0.5, 0.6, 0.7, 0.8, 0.9]
        result = bootstrap_ci_single(scores)
        assert result["ci_lower"] <= result["mean"] <= result["ci_upper"]
        assert abs(result["mean"] - 0.7) < 0.01


# ---------------------------------------------------------------------------
# Paired permutation test
# ---------------------------------------------------------------------------

class TestPairedPermutation:
    def test_no_difference(self):
        scores = [0.5, 0.6, 0.7, 0.8, 0.9]
        result = paired_permutation_test(scores, scores)
        assert result["p_value"] == 1.0

    def test_large_difference(self):
        a = [1.0] * 30
        b = [0.0] * 30
        result = paired_permutation_test(a, b)
        assert result["p_value"] < 0.01


# ---------------------------------------------------------------------------
# Stuart-Maxwell test
# ---------------------------------------------------------------------------

class TestStuartMaxwell:
    def test_identical_distributions(self):
        actions = ["answer", "clarify", "verify", "abstain"] * 10
        result = stuart_maxwell_test(actions, actions)
        assert result["p_value"] == 1.0 or result["statistic"] == 0.0

    def test_different_distributions(self):
        a = ["answer"] * 10 + ["clarify"] * 10 + ["verify"] * 10 + ["abstain"] * 10
        b = ["clarify"] * 10 + ["answer"] * 10 + ["abstain"] * 10 + ["verify"] * 10
        result = stuart_maxwell_test(a, b, labels=["answer", "clarify", "verify", "abstain"])
        # Marginals are identical (each has 10 of each), so no significant difference
        # Use a case with genuinely different marginals
        a2 = ["answer"] * 20 + ["clarify"] * 5 + ["verify"] * 10 + ["abstain"] * 5
        b2 = ["answer"] * 5 + ["clarify"] * 20 + ["verify"] * 5 + ["abstain"] * 10
        result2 = stuart_maxwell_test(a2, b2, labels=["answer", "clarify", "verify", "abstain"])
        assert result2["p_value"] < 0.05


# ---------------------------------------------------------------------------
# Spearman with CI
# ---------------------------------------------------------------------------

class TestSpearman:
    def test_perfect_correlation(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = spearman_with_ci(x, y)
        assert abs(result["rho"] - 1.0) < 1e-10
        assert result["p_value"] < 0.05

    def test_negative_correlation(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [5.0, 4.0, 3.0, 2.0, 1.0]
        result = spearman_with_ci(x, y)
        assert abs(result["rho"] - (-1.0)) < 1e-10

    def test_ci_contains_rho(self):
        rng = np.random.default_rng(42)
        x = list(rng.normal(0, 1, 30))
        y = [xi + rng.normal(0, 0.5) for xi in x]
        result = spearman_with_ci(x, y)
        assert result["ci_lower"] <= result["rho"] <= result["ci_upper"]


# ---------------------------------------------------------------------------
# Holm correction
# ---------------------------------------------------------------------------

class TestHolmCorrection:
    def test_single_test(self):
        result = holm_correction({"test1": 0.03})
        assert result["test1"]["adjusted_p"] == 0.03
        assert result["test1"]["significant_0.05"] is True

    def test_multiple_tests(self):
        pvals = {"t1": 0.01, "t2": 0.04, "t3": 0.06}
        result = holm_correction(pvals)
        # t1: 0.01 * 3 = 0.03 (significant)
        assert result["t1"]["significant_0.05"] is True
        # t2: 0.04 * 2 = 0.08 (not significant after correction)
        assert result["t2"]["significant_0.05"] is False
        # t3: 0.06 * 1 = 0.06 (not significant)
        assert result["t3"]["significant_0.05"] is False

    def test_all_significant(self):
        pvals = {"t1": 0.001, "t2": 0.002, "t3": 0.003}
        result = holm_correction(pvals)
        assert all(v["significant_0.05"] for v in result.values())


# ---------------------------------------------------------------------------
# Integration: pairwise stats
# ---------------------------------------------------------------------------

class TestPairwiseStats:
    def test_two_model_comparison(self):
        model_results = {
            "model_a": {
                "item1": {"is_correct": True, "brier_score": 0.1},
                "item2": {"is_correct": False, "brier_score": 0.8},
                "item3": {"is_correct": True, "brier_score": 0.2},
            },
            "model_b": {
                "item1": {"is_correct": False, "brier_score": 0.7},
                "item2": {"is_correct": True, "brier_score": 0.3},
                "item3": {"is_correct": True, "brier_score": 0.1},
            },
        }
        result = compute_pairwise_stats(model_results)
        assert result["n_models"] == 2
        assert result["n_items"] == 3
        assert "model_a_vs_model_b" in result["pairwise_comparisons"]
        pair = result["pairwise_comparisons"]["model_a_vs_model_b"]
        assert "accuracy" in pair
        assert "brier" in pair

    def test_single_model_returns_error(self):
        result = compute_pairwise_stats({"model_a": {"i1": {"is_correct": True}}})
        assert "error" in result


class TestFamilyBStats:
    def test_two_model_comparison(self):
        model_results = {
            "model_a": {
                "item1": {"model_decision": "answer", "utility": 1.0},
                "item2": {"model_decision": "verify", "utility": 0.3},
            },
            "model_b": {
                "item1": {"model_decision": "clarify", "utility": 0.5},
                "item2": {"model_decision": "answer", "utility": -1.0},
            },
        }
        result = compute_family_b_stats(model_results)
        assert result["n_models"] == 2
        pair = result["pairwise_comparisons"]["model_a_vs_model_b"]
        assert "utility" in pair
        assert "action_distribution" in pair
