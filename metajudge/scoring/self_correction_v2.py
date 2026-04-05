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
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import yaml
import os

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "config", "family_c_scoring.yaml"
)


def _load_config() -> Dict[str, Any]:
    """Load family C scoring config from YAML."""
    path = os.path.normpath(_CONFIG_PATH)
    with open(path, "r") as f:
        return yaml.safe_load(f)["family_c"]


def _get_config() -> Dict[str, Any]:
    """Cached config access."""
    if not hasattr(_get_config, "_cache"):
        _get_config._cache = _load_config()  # type: ignore[attr-defined]
    return _get_config._cache  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Constants derived from config (fallback defaults match the YAML)
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
    """Classify a before/after pair into one of six transition classes.

    Parameters
    ----------
    correct_before : bool
        Whether the initial answer was correct.
    correct_after : bool
        Whether the final answer was correct.
    revised : bool
        Whether the model changed its answer.

    Returns
    -------
    str
        One of: ``correction_gain``, ``maintain_correct``,
        ``neutral_revision``, ``damage``, ``stubborn_wrong``,
        ``failed_revision``.
    """
    if correct_before and correct_after:
        return "neutral_revision" if revised else "maintain_correct"
    if not correct_before and correct_after:
        # Must have revised to go from wrong to correct.
        return "correction_gain"
    if correct_before and not correct_after:
        # Must have revised to go from correct to wrong.
        return "damage"
    # Both wrong.
    return "failed_revision" if revised else "stubborn_wrong"


# Coarse bucket mapping for v6.5 opportunity-conditioned scoring
COARSE_TRANSITION_MAP = {
    "maintain_correct":  "preserve_correct",
    "neutral_revision":  "preserve_correct",
    "correction_gain":   "repair",
    "damage":            "damage",
    "stubborn_wrong":    "nonrepair",
    "failed_revision":   "nonrepair",
}


def coarse_transition_bucket(transition: str) -> str:
    """Map fine-grained transition to v6.5 coarse bucket.

    Merges maintain_correct and neutral_revision into preserve_correct,
    eliminating the noisy boundary from the headline.
    """
    if transition not in COARSE_TRANSITION_MAP:
        raise ValueError(f"Unknown transition: {transition!r}")
    return COARSE_TRANSITION_MAP[transition]


# ---------------------------------------------------------------------------
# 2. confidence_adjustment
# ---------------------------------------------------------------------------

def confidence_adjustment(
    conf_before: float,
    conf_after: float,
    correct_before: bool,
    correct_after: bool,
) -> float:
    """Compute a confidence-tracking adjustment in [-0.15, +0.10].

    The adjustment rewards models whose confidence moves in the
    epistemically appropriate direction and penalises those whose
    confidence diverges from reality.

    Parameters
    ----------
    conf_before, conf_after : float
        Stated confidence in [0, 1].
    correct_before, correct_after : bool
        Correctness flags.

    Returns
    -------
    float
        Adjustment value clamped to [_CONF_ADJ_MIN, _CONF_ADJ_MAX].
    """
    delta = conf_after - conf_before
    rises = delta > 0.05
    drops = delta < -0.05
    drops_a_lot = delta < -0.15

    transition = classify_transition(correct_before, correct_after, revised=(conf_before != conf_after or correct_before != correct_after))

    # --- correction_gain (wrong -> correct) ---
    if not correct_before and correct_after:
        adj = 0.10 if rises else 0.03

    # --- maintain_correct (correct -> correct, no revision implied here) ---
    elif correct_before and correct_after:
        if drops_a_lot:
            adj = -0.05
        else:
            adj = 0.05  # stable or slight rise

    # --- damage (correct -> wrong) ---
    elif correct_before and not correct_after:
        adj = -0.05 if drops else -0.15  # drops = at least noticed

    # --- wrong -> wrong ---
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

    Parameters
    ----------
    correct_before, correct_after : bool
        Correctness of the first and second answers.
    revised : bool
        Whether the model changed its answer.
    conf_before, conf_after : float
        Stated confidence in [0, 1].
    subfamily : str
        ``"C1"`` (intrinsic) or ``"C2"`` (evidence-assisted).
    challenge_type : str | None
        ``"misleading"`` triggers harsher C2 damage penalty.

    Returns
    -------
    dict
        Keys: ``transition``, ``base_score``, ``conf_adj``,
        ``raw_score``, ``scaled_score``.
    """
    transition = classify_transition(correct_before, correct_after, revised)

    # Select base-score table.
    if subfamily.upper() == "C1":
        base_table = _C1_BASE
    else:
        base_table = dict(_C2_BASE)
        # C2-misleading: damage is as bad as C1.
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
    """Aggregate per-item scores into a single [0, 1] headline.

    Parameters
    ----------
    item_scores : list[dict]
        Each dict is the output of :func:`score_item`.
    subfamily : str | None
        Currently unused; reserved for subfamily-specific weighting.

    Returns
    -------
    float
        Mean scaled score in [0, 1], or ``nan`` if no items.
    """
    if not item_scores:
        return float("nan")
    return float(sum(s["scaled_score"] for s in item_scores) / len(item_scores))


def compute_conditioned_rates(
    audit_rows: List[Dict[str, Any]],
    smoothing_alpha: float = 0.5,
) -> Dict[str, Any]:
    """Compute opportunity-conditioned transition rates for v6.5.

    Conditions on whether T1 was correct (preserve opportunity) or
    wrong (repair opportunity). Uses Laplace smoothing.
    """
    n_t1_right = sum(1 for r in audit_rows if r["correct_1"])
    n_t1_wrong = sum(1 for r in audit_rows if not r["correct_1"])

    # Coarse bucket each row
    buckets = [coarse_transition_bucket(r["transition"]) for r in audit_rows]

    preserve = sum(1 for r, b in zip(audit_rows, buckets)
                   if r["correct_1"] and b == "preserve_correct")
    damage = sum(1 for r, b in zip(audit_rows, buckets)
                 if r["correct_1"] and b == "damage")
    repair = sum(1 for r, b in zip(audit_rows, buckets)
                 if not r["correct_1"] and b == "repair")
    nonrepair = sum(1 for r, b in zip(audit_rows, buckets)
                    if not r["correct_1"] and b == "nonrepair")

    a = smoothing_alpha
    preserve_rate = (preserve + a) / (n_t1_right + 2 * a) if n_t1_right > 0 else 0.5
    damage_rate = (damage + a) / (n_t1_right + 2 * a) if n_t1_right > 0 else 0.5
    repair_rate = (repair + a) / (n_t1_wrong + 2 * a) if n_t1_wrong > 0 else 0.5
    nonrepair_rate = (nonrepair + a) / (n_t1_wrong + 2 * a) if n_t1_wrong > 0 else 0.5

    return {
        "n_t1_right": n_t1_right,
        "n_t1_wrong": n_t1_wrong,
        "preserve_count": preserve,
        "damage_count": damage,
        "repair_count": repair,
        "nonrepair_count": nonrepair,
        "preserve_rate": preserve_rate,
        "damage_rate": damage_rate,
        "repair_rate": repair_rate,
        "nonrepair_rate": nonrepair_rate,
        "preserve_rate_raw": preserve / n_t1_right if n_t1_right else None,
        "damage_rate_raw": damage / n_t1_right if n_t1_right else None,
        "repair_rate_raw": repair / n_t1_wrong if n_t1_wrong else None,
        "nonrepair_rate_raw": nonrepair / n_t1_wrong if n_t1_wrong else None,
    }


def compute_family_c_headline_v65(
    audit_rows: List[Dict[str, Any]],
    preserve_weight: float = 0.5,
    repair_weight: float = 0.5,
    smoothing_alpha: float = 0.5,
    include_legacy: bool = True,
) -> Dict[str, Any]:
    """Compute v6.5 opportunity-conditioned headline for Family C.

    headline = preserve_weight * preserve_rate + repair_weight * repair_rate

    Returns dict with headline_v65, all rates, and optionally legacy scores.
    """
    if not audit_rows:
        return {"headline_v65": float("nan")}

    rates = compute_conditioned_rates(audit_rows, smoothing_alpha)
    headline = (preserve_weight * rates["preserve_rate"]
                + repair_weight * rates["repair_rate"])

    result = {
        "headline_v65": headline,
        **rates,
    }

    if include_legacy:
        # Legacy transition-weighted mean for comparison
        legacy_scores = [
            score_item(
                correct_before=r["correct_1"],
                correct_after=r["correct_2"],
                revised=r["revised"],
                conf_before=r["conf_1"],
                conf_after=r["conf_2"],
                subfamily=r.get("subfamily", "C1"),
                challenge_type=r.get("challenge_type"),
            )
            for r in audit_rows
        ]
        result["legacy_transition_mean"] = compute_family_c_headline(legacy_scores)

    return result


# ---------------------------------------------------------------------------
# 5. compute_diagnostic_submetrics
# ---------------------------------------------------------------------------

def compute_diagnostic_submetrics(
    audit_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Derive diagnostic sub-metrics from a list of audit rows.

    These are for human inspection only and are **never scored**
    (SOUL.md narrative-field rule).

    Parameters
    ----------
    audit_rows : list[dict]
        Each dict is the output of :func:`build_audit_row`.

    Returns
    -------
    dict
        Diagnostic sub-metric values.
    """
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

    # Revision improvement rate: of all revisions, how many went wrong -> correct?
    revision_improvement_rate = (
        correction_gain_ct / revisions if revisions > 0 else float("nan")
    )

    # Damage rate: of all revisions, how many went correct -> wrong?
    damage_rate = damage_ct / revisions if revisions > 0 else float("nan")

    # Damage:gain ratio (the key inverted metric).
    damage_gain_ratio = (
        damage_ct / correction_gain_ct
        if correction_gain_ct > 0
        else float("inf") if damage_ct > 0 else float("nan")
    )

    # Mean confidence delta across all items.
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
    """Build a complete audit row for one Family C item.

    Combines raw observables with computed scores so that every row
    is self-contained for downstream analysis and diagnostics.

    Parameters
    ----------
    item_id : str
        Unique item identifier.
    subfamily : str
        ``"C1"`` or ``"C2"``.
    stratum : str
        Difficulty tier (e.g. ``"easy"``, ``"hard"``).
    normative_action : str
        The ideal behaviour for this item (e.g. ``"revise"``, ``"hold"``).
    answer_1, answer_2 : str
        Model answers before and after the revision opportunity.
    conf_1, conf_2 : float
        Stated confidence before and after.
    correct_1, correct_2 : bool
        Whether each answer was correct.
    revised : bool
        Whether the model changed its answer.
    challenge_type : str | None
        ``"misleading"`` for adversarial-evidence items.

    Returns
    -------
    dict
        Full audit row with all inputs and computed fields.
    """
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
        "coarse_transition": coarse_transition_bucket(scores["transition"]),
        "opportunity_type": "preserve" if correct_1 else "repair",
    }
