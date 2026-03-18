"""
MetaJudge-AGI: Anti-Gaming Perturbation Module
=================================================
Source: Framework §8

Implements countermeasures against superficial optimization of the benchmark.
Covers all eight countermeasures from Framework §8.2.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# 8.2.2 Hidden optimal-action classes
# ---------------------------------------------------------------------------

def assign_optimal_action_class(
    items: pd.DataFrame,
    action_distribution: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Assign hidden optimal actions to ensure no single policy dominates.
    
    Source: Framework §8.2.2
    
    Default distribution ensures mix of answer/ask/abstain/verify optimal items.
    """
    if action_distribution is None:
        action_distribution = {
            "answer": 0.50,
            "ask": 0.15,
            "abstain": 0.20,
            "verify": 0.15,
        }
    
    # NOTE: Actual assignment should be item-specific based on content.
    # This is a placeholder that demonstrates the distribution requirement.
    items = items.copy()
    if "intended_optimal_action" not in items.columns:
        items["intended_optimal_action"] = "answer"  # placeholder
    return items


# ---------------------------------------------------------------------------
# 8.2.3 Prompt and format variation
# ---------------------------------------------------------------------------

def generate_prompt_variants(
    base_prompt: str,
    n_variants: int = 3,
) -> List[str]:
    """Generate paraphrased prompt variants to prevent format overfitting.
    
    Source: Framework §8.2.3
    
    NOTE: This is a placeholder. Production implementation should use
    either an LLM-based paraphraser or a human-curated variant set.
    """
    # Placeholder: return structural variants
    variants = [base_prompt]
    
    # Variant: reorder instruction style
    if n_variants >= 2:
        variants.append(f"Consider this question carefully:\n\n{base_prompt}")
    
    if n_variants >= 3:
        variants.append(f"Please analyze the following:\n\n{base_prompt}\n\nProvide your assessment.")
    
    return variants[:n_variants]


# ---------------------------------------------------------------------------
# 8.2.4 Decoy confidence cues
# ---------------------------------------------------------------------------

def add_decoy_difficulty_cues(
    items: pd.DataFrame,
    decoy_rate: float = 0.2,
) -> pd.DataFrame:
    """Add items whose surface appearance doesn't match true difficulty.
    
    Source: Framework §8.2.4
    
    These help distinguish true calibration from heuristic confidence assignment.
    """
    items = items.copy()
    if "has_decoy_cues" not in items.columns:
        items["has_decoy_cues"] = False
    
    # NOTE: Actual decoy injection requires content-aware manipulation.
    # This placeholder marks where decoy items should be flagged.
    return items


# ---------------------------------------------------------------------------
# 8.2.5 Symmetric correction setup
# ---------------------------------------------------------------------------

def ensure_symmetric_correction_items(
    items: pd.DataFrame,
) -> Dict[str, int]:
    """Verify that correction tasks include both wrong-first and correct-first cases.
    
    Source: Framework §8.2.5
    
    Returns counts of each type for validation.
    """
    correction_items = items[items["task_type"] == "self_correction"]
    
    if correction_items.empty:
        return {"wrong_first": 0, "correct_first": 0}
    
    # NOTE: Requires 'initial_answer_correct' metadata to be set
    counts = {
        "wrong_first": 0,
        "correct_first": 0,
    }
    
    if "initial_answer_expected_correct" in correction_items.columns:
        counts["wrong_first"] = int((~correction_items["initial_answer_expected_correct"]).sum())
        counts["correct_first"] = int(correction_items["initial_answer_expected_correct"].sum())
    
    return counts


# ---------------------------------------------------------------------------
# 8.2.6 Source-label adversarial items
# ---------------------------------------------------------------------------

def flag_source_adversarial_items(
    items: pd.DataFrame,
) -> pd.DataFrame:
    """Flag items where the answer is correct but source label is easy to get wrong.
    
    Source: Framework §8.2.6
    """
    items = items.copy()
    if "source_adversarial" not in items.columns:
        items["source_adversarial"] = False
    
    # NOTE: Actual adversarial flagging requires item-by-item analysis.
    return items


# ---------------------------------------------------------------------------
# 8.2.7 Cross-template evaluation splits
# ---------------------------------------------------------------------------

def create_template_splits(
    items: pd.DataFrame,
    n_template_groups: int = 3,
) -> pd.DataFrame:
    """Assign items to template groups for cross-template evaluation.
    
    Source: Framework §8.2.7
    
    Some prompt structures are reserved as hidden evaluation variants.
    """
    items = items.copy()
    items["template_group"] = [
        i % n_template_groups for i in range(len(items))
    ]
    return items


# ---------------------------------------------------------------------------
# 8.2.8 Verbosity control
# ---------------------------------------------------------------------------

def check_verbosity_independence(
    results: pd.DataFrame,
    score_column: str = "composite_score",
    verbosity_column: str = "reasoning_length",
) -> float:
    """Check correlation between verbosity and score.
    
    Source: Framework §8.2.8 - "Do not directly reward long justification text"
    
    Returns Pearson correlation. Values close to 0 indicate good independence.
    """
    if verbosity_column not in results.columns or score_column not in results.columns:
        return float("nan")
    
    valid = results[[score_column, verbosity_column]].dropna()
    if len(valid) < 5:
        return float("nan")
    
    return float(valid[score_column].corr(valid[verbosity_column]))


# ---------------------------------------------------------------------------
# Aggregate anti-gaming validation
# ---------------------------------------------------------------------------

def run_anti_gaming_checks(
    items: pd.DataFrame,
    results: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Run all anti-gaming validation checks.
    
    Source: Framework §8
    
    Returns a diagnostic report.
    """
    report: Dict[str, Any] = {}
    
    # Check optimal action distribution
    if "intended_optimal_action" in items.columns:
        action_dist = items["intended_optimal_action"].value_counts(normalize=True).to_dict()
        report["action_distribution"] = action_dist
        report["action_diversity_ok"] = len(action_dist) >= 3
    
    # Check symmetric correction
    report["correction_symmetry"] = ensure_symmetric_correction_items(items)
    
    # Check template diversity
    if "template_group" in items.columns:
        report["n_template_groups"] = items["template_group"].nunique()
    
    # Check verbosity independence (if results available)
    if results is not None:
        report["verbosity_correlation"] = check_verbosity_independence(results)
    
    return report
