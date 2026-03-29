"""
MetaJudge — Shared notebook helper utilities.

Provides data loading, clean-subset filtering, and result formatting
functions used by both the official benchmark notebook and the public
narrative notebook. Keeps notebooks thin and logic package-owned.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Data root resolution
# ---------------------------------------------------------------------------

_DATA_ROOTS = [
    "/kaggle/input/datasets/seanmcgee2025/metajudge-benchmark",
    "/kaggle/input/metajudge-benchmark",
    "data",
]


def resolve_data_root() -> str:
    """Find the data root directory across Kaggle and local environments."""
    for root in _DATA_ROOTS:
        if os.path.exists(root):
            return root
    raise FileNotFoundError(
        f"No data root found. Tried: {_DATA_ROOTS}"
    )


def resolve_output_dir() -> str:
    """Resolve output directory across Kaggle and local environments."""
    if os.path.exists("/kaggle/working"):
        return "/kaggle/working"
    out = "outputs"
    os.makedirs(out, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_benchmark_dataset(data_root: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load the calibration benchmark dataset (v1 JSON).

    Returns list of item dicts with: item_id, question, gold_answer,
    mechanism_primary, aliases, rule, etc.
    """
    root = data_root or resolve_data_root()
    path = os.path.join(root, "metajudge_benchmark_v1.json")
    with open(path) as f:
        return json.load(f)


def load_family_b_dataset(data_root: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load the Family B selective abstention dataset (pilot v2 JSON).

    Returns list of item dicts with: item_id, question, gold_answer,
    gold_action, category, premise_type, acceptable_actions, etc.
    """
    root = data_root or resolve_data_root()
    path = os.path.join(root, "family_b_pilot_v2.json")
    with open(path) as f:
        return json.load(f)


def load_adjudication_registry(data_root: Optional[str] = None) -> Dict[str, Any]:
    """Load the adjudication registry (grading rules per item)."""
    root = data_root or resolve_data_root()
    path = os.path.join(root, "adjudication_registry.json")
    with open(path) as f:
        return json.load(f)


def load_clean_manifest(data_root: Optional[str] = None) -> Dict[str, Any]:
    """Load the clean subset manifest.

    Returns dict with 'calibration' and 'family_b' sections,
    each containing 'excluded_items' lists.
    """
    root = data_root or resolve_data_root()
    path = os.path.join(root, "clean_subset_manifest.json")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Clean subset filtering
# ---------------------------------------------------------------------------

def get_excluded_item_ids(
    manifest: Optional[Dict] = None,
    data_root: Optional[str] = None,
) -> Tuple[set, set]:
    """Return (cal_excluded, fb_excluded) item ID sets from the clean manifest.

    Args:
        manifest: Pre-loaded manifest dict, or None to load from disk.
        data_root: Data root for loading manifest if not provided.

    Returns:
        Tuple of (calibration_excluded_ids, family_b_excluded_ids).
    """
    if manifest is None:
        manifest = load_clean_manifest(data_root)
    cal_excl = set(manifest["calibration"]["excluded_items"])
    fb_excl = set(manifest["family_b"]["excluded_items"])
    return cal_excl, fb_excl


def filter_clean_subset(
    items: List[Dict[str, Any]],
    excluded_ids: set,
    id_key: str = "item_id",
) -> List[Dict[str, Any]]:
    """Filter a list of item dicts to the clean subset.

    Args:
        items: Full item list.
        excluded_ids: Set of item IDs to exclude.
        id_key: Key name for item ID in each dict.

    Returns:
        Filtered list with excluded items removed.
    """
    return [item for item in items if item[id_key] not in excluded_ids]


# ---------------------------------------------------------------------------
# Model name utilities
# ---------------------------------------------------------------------------

MODEL_SHORT_NAMES = {
    "google/gemini-2.5-flash": "Gemini Flash",
    "google/gemini-2.5-pro": "Gemini Pro",
    "anthropic/claude-sonnet-4@20250514": "Sonnet 4",
    "anthropic/claude-haiku-4-5@20251001": "Haiku 4.5",
    "deepseek-ai/deepseek-v3.1": "DeepSeek V3.1",
}

SWEEP_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4@20250514",
    "anthropic/claude-haiku-4-5@20251001",
    "deepseek-ai/deepseek-v3.1",
]


def short_model_name(model_id: str) -> str:
    """Convert a full model ID to a short display name."""
    return MODEL_SHORT_NAMES.get(model_id, model_id.split("/")[-1])


# ---------------------------------------------------------------------------
# Result formatting
# ---------------------------------------------------------------------------

def format_leaderboard_cal(
    model_results: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Format calibration results into a leaderboard-ready list of dicts.

    Args:
        model_results: {model_id: {accuracy, mean_brier, ece, overconfidence_rate, n_items}}

    Returns:
        Sorted list of dicts with short names, ready for DataFrame conversion.
    """
    rows = []
    for model_id, metrics in model_results.items():
        rows.append({
            "Model": short_model_name(model_id),
            "n": metrics.get("n_items", 0),
            "Accuracy": round(metrics.get("accuracy", 0), 3),
            "Mean Brier": round(metrics.get("mean_brier", 0), 4),
            "1-Brier": round(1 - metrics.get("mean_brier", 0), 4),
            "ECE": round(metrics.get("ece", 0), 4),
            "Overconf. Rate": round(metrics.get("overconfidence_rate", 0), 3),
        })
    return sorted(rows, key=lambda r: r["1-Brier"], reverse=True)


def format_leaderboard_fb(
    model_results: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Format Family B results into a leaderboard-ready list of dicts.

    Args:
        model_results: {model_id: {uwaa, mean_utility, action_accuracy, n_items}}

    Returns:
        Sorted list of dicts with short names.
    """
    rows = []
    for model_id, metrics in model_results.items():
        rows.append({
            "Model": short_model_name(model_id),
            "n": metrics.get("n_items", 0),
            "UWAA": round(metrics.get("uwaa", 0), 3),
            "Mean Utility": round(metrics.get("mean_utility", 0), 3),
            "Action Acc": round(metrics.get("action_accuracy", 0), 3),
        })
    return sorted(rows, key=lambda r: r["UWAA"], reverse=True)


# ---------------------------------------------------------------------------
# Benchmark answer key construction
# ---------------------------------------------------------------------------

def build_answer_key(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build an answer key dict from a benchmark dataset.

    Args:
        items: List of item dicts from load_benchmark_dataset().

    Returns:
        Dict mapping item_id -> {gold_answer, aliases, rule}.
    """
    return {
        item["item_id"]: {
            "gold_answer": item["gold_answer"],
            "aliases": item.get("aliases", []),
            "rule": item.get("rule", "alias"),
        }
        for item in items
    }
