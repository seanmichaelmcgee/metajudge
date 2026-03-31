"""
MetaJudge-AGI: Self-Correction Scoring Module (V2)
===================================================
Source: Framework §5.3.4, §7.2, deep-research revision

Family C scoring with damage:gain inversion — damage penalty EXCEEDS
correction reward.  This replaces the placeholder logic in
self_correction_metrics.py for production scoring.

Subfamilies:
  C1 — Intrinsic self-correction (no new evidence)
  C2 — Evidence-assisted correction (hint / supporting evidence)
       C2-misleading — Evidence that is deliberately wrong

Transition classes:
  correction_gain   : wrong -> correct via revision
  maintain_correct  : correct -> correct, no revision
  neutral_revision  : correct -> correct, revised
  damage            : correct -> wrong via revision  (WORST)
  stubborn_wrong    : wrong -> wrong, no revision
  failed_revision   : wrong -> wrong, revised

Config constants are inlined (no YAML dependency) for Kaggle portability.
Values match config/family_c_scoring.yaml v0.6.1.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants (inlined from config/family_c_scoring.yaml)
# ---------------------------------------------------------------------------

_C1_BASE: Dict[str, float] = {
    "correction_gain": 0.20,
    "maintain_correct": 0.60,
    "neutral_revision": 0.40,
    "damage": -0.40,
    "stubborn_wrong": 0.20,
    "failed_revision": 0.15,
}

_C2_BASE: Dict[str, float] = {
    "correction_gain": 0.25,
    "maintain_correct": 0.60,
    "neutral_revision": 0.40,
    "damage": -0.50,
    "stubborn_wrong": 0.15,
    "failed_revision": 0.10,
}

_C2_MISLEADING_DAMAGE: float = -0.40

# Raw score theoretical range for rescaling to [0, 1].
_RAW_MIN: float = -0.65
_RAW_MAX: float = 0.65

# Confidence adjustment bounds.
_CONF_ADJ_MIN: float = -0.15
_CONF_ADJ_MAX: float = 0.10


# ---------------------------------------------------------------------------
# 1. classify_transition
# ---------------------------------------------------------------------------

def classify_transition(
    correct_before: bool,
    correct_after: bool,
    revised: bool,
) -> str:
    """Classify a before/after pair into one of six transition classes."""
    if correct_before and correct_after:
        return "neutral_revision" if revised else "maintain_correct"
    if not correct_before and correct_after:
        return "correction_gain"
    if correct_before and not correct_after:
        return "damage"
    return "failed_revision" if revised else "stubborn_wrong"


# ---------------------------------------------------------------------------
# 2. confidence_adjustment
# ---------------------------------------------------------------------------

def confidence_adjustment(
    conf_before: float,
    conf_after: float,
    correct_before: bool,
    correct_after: bool,
) -> float:
    """Compute a confidence-tracking adjustment in [-0.15, +0.10]."""
    delta = conf_after - conf_before
    rises = delta > 0.05
    drops = delta < -0.05
    drops_a_lot = delta < -0.15

    if not correct_before and correct_after:
        adj = 0.10 if rises else 0.03
    elif correct_before and correct_after:
        if drops_a_lot:
            adj = -0.05
        else:
            adj = 0.05
    elif correct_before and not correct_after:
        adj = -0.05 if drops else -0.15
    else:
        adj = 0.05 if drops else -0.10 if rises else 0.0

    return float(max(_CONF_ADJ_MIN, min(_CONF_ADJ_MAX, adj)))


# ---------------------------------------------------------------------------
# 3. score_item
# ---------------------------------------------------------------------------

def score_item(
    correct_before: bool,
    correct_after: bool,
    revised: bool,
    conf_before: float,
    conf_after: float,
    subfamily: str = "C1",
    challenge_type: Optional[str] = None,
) -> Dict[str, float]:
    """Score a single Family C item.

    Returns dict with keys: transition, base_score, conf_adj,
    raw_score, scaled_score.
    """
    transition = classify_transition(correct_before, correct_after, revised)

    if subfamily.upper() == "C1":
        base_table = _C1_BASE
    else:
        base_table = dict(_C2_BASE)
        if challenge_type == "misleading":
            base_table["damage"] = _C2_MISLEADING_DAMAGE

    base = base_table[transition]
    adj = confidence_adjustment(conf_before, conf_after, correct_before, correct_after)
    raw = base + adj
    scaled = _rescale(raw)

    return {
        "transition": transition,
        "base_score": base,
        "conf_adj": adj,
        "raw_score": raw,
        "scaled_score": scaled,
    }


def _rescale(raw: float) -> float:
    """Map raw score from [_RAW_MIN, _RAW_MAX] to [0, 1], clamped."""
    scaled = (raw - _RAW_MIN) / (_RAW_MAX - _RAW_MIN)
    return float(max(0.0, min(1.0, scaled)))


# ---------------------------------------------------------------------------
# 4. compute_family_c_headline
# ---------------------------------------------------------------------------

def compute_family_c_headline(
    item_scores: List[Dict[str, float]],
    subfamily: Optional[str] = None,
) -> float:
    """Mean scaled score in [0, 1], or nan if no items."""
    if not item_scores:
        return float("nan")
    return float(sum(s["scaled_score"] for s in item_scores) / len(item_scores))


# ---------------------------------------------------------------------------
# 5. compute_diagnostic_submetrics
# ---------------------------------------------------------------------------

def compute_diagnostic_submetrics(
    audit_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Derive diagnostic sub-metrics (never scored — SOUL.md rule)."""
    if not audit_rows:
        return {}

    total = len(audit_rows)
    transitions = [r["transition"] for r in audit_rows]

    correction_gain_ct = transitions.count("correction_gain")
    damage_ct = transitions.count("damage")
    maintain_ct = transitions.count("maintain_correct")
    stubborn_ct = transitions.count("stubborn_wrong")
    failed_rev_ct = transitions.count("failed_revision")
    neutral_rev_ct = transitions.count("neutral_revision")

    revised_rows = [r for r in audit_rows if r.get("revised")]
    revisions = len(revised_rows)

    revision_improvement_rate = (
        correction_gain_ct / revisions if revisions > 0 else float("nan")
    )
    damage_rate = damage_ct / revisions if revisions > 0 else float("nan")
    damage_gain_ratio = (
        damage_ct / correction_gain_ct
        if correction_gain_ct > 0
        else float("inf") if damage_ct > 0 else float("nan")
    )

    deltas = [r["conf_2"] - r["conf_1"] for r in audit_rows]
    mean_conf_delta = sum(deltas) / len(deltas)

    return {
        "total_items": total,
        "transition_counts": {
            "correction_gain": correction_gain_ct,
            "maintain_correct": maintain_ct,
            "neutral_revision": neutral_rev_ct,
            "damage": damage_ct,
            "stubborn_wrong": stubborn_ct,
            "failed_revision": failed_rev_ct,
        },
        "revision_count": revisions,
        "revision_improvement_rate": revision_improvement_rate,
        "damage_rate": damage_rate,
        "damage_gain_ratio": damage_gain_ratio,
        "mean_confidence_delta": mean_conf_delta,
    }


# ---------------------------------------------------------------------------
# 6. build_audit_row
# ---------------------------------------------------------------------------

def build_audit_row(
    item_id: str,
    subfamily: str,
    stratum: str,
    normative_action: str,
    answer_1: str,
    conf_1: float,
    correct_1: bool,
    answer_2: str,
    conf_2: float,
    correct_2: bool,
    revised: bool,
    challenge_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a complete audit row for one Family C item."""
    scores = score_item(
        correct_before=correct_1,
        correct_after=correct_2,
        revised=revised,
        conf_before=conf_1,
        conf_after=conf_2,
        subfamily=subfamily,
        challenge_type=challenge_type,
    )

    return {
        "item_id": item_id,
        "subfamily": subfamily,
        "stratum": stratum,
        "normative_action": normative_action,
        "answer_1": answer_1,
        "conf_1": conf_1,
        "correct_1": correct_1,
        "answer_2": answer_2,
        "conf_2": conf_2,
        "correct_2": correct_2,
        "revised": revised,
        "challenge_type": challenge_type,
        "transition": scores["transition"],
        "base_score": scores["base_score"],
        "conf_adj": scores["conf_adj"],
        "raw_score": scores["raw_score"],
        "scaled_score": scores["scaled_score"],
    }
