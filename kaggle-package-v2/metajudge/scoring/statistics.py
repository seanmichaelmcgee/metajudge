"""
Statistical testing for MetaJudge benchmark — paired model comparisons.

Implements:
- McNemar's test (accuracy)
- Paired permutation test (mean scores)
- Paired bootstrap CI (any metric)
- Stuart-Maxwell test (action distributions)
- Spearman correlation + bootstrap CI (bridge)
- Holm correction for multiple comparisons
"""

from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np
from scipy import stats as scipy_stats


# ---------------------------------------------------------------------------
# Bootstrap utilities
# ---------------------------------------------------------------------------

def paired_bootstrap_ci(
    scores_a: list[float],
    scores_b: list[float],
    n_boot: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict[str, float]:
    """Bootstrap CI for mean(scores_a) - mean(scores_b)."""
    rng = np.random.default_rng(seed)
    a = np.asarray(scores_a, dtype=float)
    b = np.asarray(scores_b, dtype=float)
    diffs = a - b
    n = len(diffs)

    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_means[i] = diffs[idx].mean()

    lo = float(np.percentile(boot_means, 100 * alpha / 2))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    observed = float(diffs.mean())

    return {
        "observed_diff": observed,
        "ci_lower": lo,
        "ci_upper": hi,
        "alpha": alpha,
        "n_boot": n_boot,
    }


def bootstrap_ci_single(
    scores: list[float],
    n_boot: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict[str, float]:
    """Bootstrap CI for a single sample mean."""
    rng = np.random.default_rng(seed)
    a = np.asarray(scores, dtype=float)
    n = len(a)

    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_means[i] = a[idx].mean()

    lo = float(np.percentile(boot_means, 100 * alpha / 2))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))

    return {
        "mean": float(a.mean()),
        "ci_lower": lo,
        "ci_upper": hi,
        "alpha": alpha,
    }


# ---------------------------------------------------------------------------
# McNemar's test (paired binary accuracy)
# ---------------------------------------------------------------------------

def mcnemar_test(
    correct_a: list[bool],
    correct_b: list[bool],
) -> dict[str, float]:
    """McNemar's test for paired binary outcomes.

    Compares whether model A and model B differ in accuracy
    on the same items.
    """
    a = np.asarray(correct_a, dtype=bool)
    b = np.asarray(correct_b, dtype=bool)

    # Discordant pairs
    b_only = int(np.sum(~a & b))  # B correct, A wrong
    a_only = int(np.sum(a & ~b))  # A correct, B wrong

    n_discordant = a_only + b_only
    if n_discordant == 0:
        return {"statistic": 0.0, "p_value": 1.0, "a_only": 0, "b_only": 0}

    # Exact binomial test (mid-p for small samples)
    if n_discordant < 25:
        p_value = float(scipy_stats.binomtest(a_only, n_discordant, 0.5).pvalue)
    else:
        # Chi-squared approximation with continuity correction
        chi2 = (abs(a_only - b_only) - 1) ** 2 / n_discordant
        p_value = float(1 - scipy_stats.chi2.cdf(chi2, df=1))

    return {
        "statistic": float((a_only - b_only) ** 2 / n_discordant),
        "p_value": p_value,
        "a_only": a_only,
        "b_only": b_only,
    }


# ---------------------------------------------------------------------------
# Paired permutation test
# ---------------------------------------------------------------------------

def paired_permutation_test(
    scores_a: list[float],
    scores_b: list[float],
    n_perm: int = 10000,
    seed: int = 42,
) -> dict[str, float]:
    """Two-sided paired permutation test for mean difference."""
    rng = np.random.default_rng(seed)
    a = np.asarray(scores_a, dtype=float)
    b = np.asarray(scores_b, dtype=float)
    diffs = a - b
    n = len(diffs)
    observed = float(np.abs(diffs.mean()))

    count = 0
    for _ in range(n_perm):
        signs = rng.choice([-1, 1], size=n)
        perm_mean = np.abs((diffs * signs).mean())
        if perm_mean >= observed:
            count += 1

    p_value = (count + 1) / (n_perm + 1)

    return {
        "observed_diff": float(diffs.mean()),
        "p_value": float(p_value),
        "n_perm": n_perm,
    }


# ---------------------------------------------------------------------------
# Stuart-Maxwell test (paired k×k table)
# ---------------------------------------------------------------------------

def stuart_maxwell_test(
    actions_a: list[str],
    actions_b: list[str],
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Stuart-Maxwell test for marginal homogeneity.

    Tests whether the distribution of actions differs between
    two models on the same items.
    """
    if labels is None:
        labels = sorted(set(actions_a) | set(actions_b))

    k = len(labels)
    label_idx = {l: i for i, l in enumerate(labels)}

    # Build contingency table
    table = np.zeros((k, k), dtype=int)
    for a, b in zip(actions_a, actions_b):
        if a in label_idx and b in label_idx:
            table[label_idx[a], label_idx[b]] += 1

    # Marginal differences
    d = np.array([table[i, :].sum() - table[:, i].sum() for i in range(k - 1)],
                 dtype=float)

    # Variance-covariance matrix of marginal differences
    V = np.zeros((k - 1, k - 1))
    for i in range(k - 1):
        for j in range(k - 1):
            if i == j:
                V[i, j] = (table[i, :].sum() + table[:, i].sum()
                           - 2 * table[i, i])
            else:
                V[i, j] = -(table[i, j] + table[j, i])

    # Check for zero differences (identical distributions)
    if np.allclose(d, 0):
        return {
            "statistic": 0.0,
            "df": k - 1,
            "p_value": 1.0,
            "labels": labels,
        }

    try:
        if np.linalg.matrix_rank(V) < k - 1:
            V_inv = np.linalg.pinv(V)
        else:
            V_inv = np.linalg.inv(V)
        chi2 = float(d @ V_inv @ d)
        df = k - 1
        p_value = float(1 - scipy_stats.chi2.cdf(chi2, df=df))
    except np.linalg.LinAlgError:
        chi2 = float("nan")
        p_value = float("nan")
        df = k - 1

    return {
        "statistic": chi2,
        "df": df,
        "p_value": p_value,
        "labels": labels,
    }


# ---------------------------------------------------------------------------
# Spearman correlation with bootstrap CI
# ---------------------------------------------------------------------------

def spearman_with_ci(
    x: list[float],
    y: list[float],
    n_boot: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict[str, float]:
    """Spearman rank correlation with bootstrap confidence interval."""
    rng = np.random.default_rng(seed)
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    n = len(x_arr)

    rho, p_value = scipy_stats.spearmanr(x_arr, y_arr)

    boot_rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        r, _ = scipy_stats.spearmanr(x_arr[idx], y_arr[idx])
        boot_rhos[i] = r

    lo = float(np.percentile(boot_rhos, 100 * alpha / 2))
    hi = float(np.percentile(boot_rhos, 100 * (1 - alpha / 2)))

    return {
        "rho": float(rho),
        "p_value": float(p_value),
        "ci_lower": lo,
        "ci_upper": hi,
        "alpha": alpha,
    }


# ---------------------------------------------------------------------------
# Multiple comparison correction
# ---------------------------------------------------------------------------

def holm_correction(p_values: dict[str, float]) -> dict[str, dict[str, float]]:
    """Apply Holm-Bonferroni correction to a set of p-values.

    Args:
        p_values: mapping of test_name → raw p-value

    Returns:
        mapping of test_name → {raw_p, adjusted_p, significant}
    """
    names = list(p_values.keys())
    raw = np.array([p_values[n] for n in names])
    m = len(raw)

    # Sort by raw p-value
    order = np.argsort(raw)
    adjusted = np.empty(m)

    for rank, idx in enumerate(order):
        adjusted[idx] = min(1.0, raw[idx] * (m - rank))

    # Enforce monotonicity
    for rank in range(1, m):
        idx = order[rank]
        prev_idx = order[rank - 1]
        adjusted[idx] = max(adjusted[idx], adjusted[prev_idx])

    result = {}
    for i, name in enumerate(names):
        result[name] = {
            "raw_p": float(raw[i]),
            "adjusted_p": float(adjusted[i]),
            "significant_0.05": bool(adjusted[i] < 0.05),
        }
    return result


# ---------------------------------------------------------------------------
# Full stats report generator
# ---------------------------------------------------------------------------

def compute_pairwise_stats(
    model_results: dict[str, dict[str, dict]],
    item_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Compute pairwise statistical comparisons between models.

    Args:
        model_results: {model_name: {item_id: {is_correct, brier_score, ...}}}
        item_ids: optional list of item IDs to restrict comparison

    Returns:
        Full stats report dict suitable for JSON serialization.
    """
    models = sorted(model_results.keys())
    if len(models) < 2:
        return {"error": "Need at least 2 models for comparison"}

    # Find common items
    if item_ids is None:
        common = set.intersection(*(set(model_results[m].keys()) for m in models))
        item_ids = sorted(common)

    pairwise = {}
    all_p_values = {}

    for m_a, m_b in combinations(models, 2):
        pair_key = f"{m_a}_vs_{m_b}"

        # Extract paired data
        correct_a = [model_results[m_a][iid]["is_correct"] for iid in item_ids
                     if iid in model_results[m_a] and iid in model_results[m_b]]
        correct_b = [model_results[m_b][iid]["is_correct"] for iid in item_ids
                     if iid in model_results[m_a] and iid in model_results[m_b]]

        brier_a = [model_results[m_a][iid].get("brier_score", 0) for iid in item_ids
                   if iid in model_results[m_a] and iid in model_results[m_b]]
        brier_b = [model_results[m_b][iid].get("brier_score", 0) for iid in item_ids
                   if iid in model_results[m_a] and iid in model_results[m_b]]

        pair_result = {
            "n_items": len(correct_a),
            "accuracy": {
                "model_a": float(np.mean(correct_a)),
                "model_b": float(np.mean(correct_b)),
                "mcnemar": mcnemar_test(correct_a, correct_b),
            },
        }

        if brier_a and brier_b:
            pair_result["brier"] = {
                "mean_a": float(np.mean(brier_a)),
                "mean_b": float(np.mean(brier_b)),
                "permutation": paired_permutation_test(brier_a, brier_b),
                "bootstrap_ci": paired_bootstrap_ci(brier_a, brier_b),
            }

        pairwise[pair_key] = pair_result
        all_p_values[f"{pair_key}_accuracy"] = pair_result["accuracy"]["mcnemar"]["p_value"]
        if "brier" in pair_result:
            all_p_values[f"{pair_key}_brier"] = pair_result["brier"]["permutation"]["p_value"]

    # Multiple comparison correction
    corrected = holm_correction(all_p_values)

    return {
        "n_models": len(models),
        "n_items": len(item_ids),
        "models": models,
        "pairwise_comparisons": pairwise,
        "multiple_comparison_correction": {
            "method": "Holm-Bonferroni",
            "tests": corrected,
        },
        "notes": {
            "accuracy_test": "McNemar's test (exact binomial for n<25, chi2 otherwise)",
            "brier_test": "Paired permutation test (10000 permutations)",
            "brier_ci": "Paired bootstrap CI (10000 resamples, 95%)",
            "correction": "Holm-Bonferroni for familywise error rate control",
        },
    }


def compute_family_b_stats(
    model_results: dict[str, dict[str, dict]],
    item_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Compute pairwise stats for Family B (action-based metrics)."""
    models = sorted(model_results.keys())
    if len(models) < 2:
        return {"error": "Need at least 2 models"}

    if item_ids is None:
        common = set.intersection(*(set(model_results[m].keys()) for m in models))
        item_ids = sorted(common)

    pairwise = {}
    all_p_values = {}

    for m_a, m_b in combinations(models, 2):
        pair_key = f"{m_a}_vs_{m_b}"

        actions_a = [model_results[m_a][iid].get("model_decision", "unknown")
                     for iid in item_ids
                     if iid in model_results[m_a] and iid in model_results[m_b]]
        actions_b = [model_results[m_b][iid].get("model_decision", "unknown")
                     for iid in item_ids
                     if iid in model_results[m_a] and iid in model_results[m_b]]

        utility_a = [model_results[m_a][iid].get("utility", 0)
                     for iid in item_ids
                     if iid in model_results[m_a] and iid in model_results[m_b]]
        utility_b = [model_results[m_b][iid].get("utility", 0)
                     for iid in item_ids
                     if iid in model_results[m_a] and iid in model_results[m_b]]

        pair_result = {
            "n_items": len(actions_a),
            "utility": {
                "mean_a": float(np.mean(utility_a)),
                "mean_b": float(np.mean(utility_b)),
                "permutation": paired_permutation_test(utility_a, utility_b),
                "bootstrap_ci": paired_bootstrap_ci(utility_a, utility_b),
            },
        }

        # Stuart-Maxwell for action distribution
        sm = stuart_maxwell_test(
            actions_a, actions_b,
            labels=["answer", "clarify", "verify", "abstain"],
        )
        pair_result["action_distribution"] = sm

        pairwise[pair_key] = pair_result
        all_p_values[f"{pair_key}_utility"] = pair_result["utility"]["permutation"]["p_value"]
        if not np.isnan(sm["p_value"]):
            all_p_values[f"{pair_key}_actions"] = sm["p_value"]

    corrected = holm_correction(all_p_values) if all_p_values else {}

    return {
        "n_models": len(models),
        "n_items": len(item_ids),
        "models": models,
        "pairwise_comparisons": pairwise,
        "multiple_comparison_correction": {
            "method": "Holm-Bonferroni",
            "tests": corrected,
        },
    }
