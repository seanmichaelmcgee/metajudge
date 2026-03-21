#!/usr/bin/env python3
"""Apply V4.1 triage decisions to the benchmark dataset.

Reads:
  - data/metajudge_benchmark_v1.json (current 102-item dataset)
  - v41_triage_sheet.json (triage decisions)

Writes:
  - data/metajudge_benchmark_v41_base.json (65 items: 30 keep + 31 update + 4 rewrite)
  - data/adjudication_registry.json (updated to match)
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATASET_PATH = REPO / "data" / "metajudge_benchmark_v1.json"
TRIAGE_PATH = Path("/home/user/workspace/v41_triage_sheet.json")
REGISTRY_PATH = REPO / "data" / "adjudication_registry.json"
OUTPUT_PATH = REPO / "data" / "metajudge_benchmark_v41_base.json"

# ---------------------------------------------------------------------------
# Tri-label alias helpers
# ---------------------------------------------------------------------------

_TRI_LABEL_ALIASES = {
    "true": ["true", "yes", "correct", "unambiguously true"],
    "false": ["false", "no", "incorrect", "unambiguously false"],
    "contested": ["contested", "debated", "disputed", "it is contested",
                   "the evidence is contested"],
}


def _build_tri_label_aliases(gold: str) -> list[str]:
    """Return standard alias list for a tri-label item."""
    gold_lower = gold.strip().lower()
    return list(_TRI_LABEL_ALIASES.get(gold_lower, [gold_lower]))


# ---------------------------------------------------------------------------
# Per-item UPDATE handlers
# ---------------------------------------------------------------------------

def _update_tri_label(item: dict, triage: dict) -> list[str]:
    """Convert an AmbiguityMetacognition item to tri_label rule."""
    changes = []
    new_gold = triage.get("new_gold") or item["gold_answer"]
    old_rule = item["rule"]
    item["gold_answer"] = new_gold
    item["rule"] = "alias"  # dataset rule stays "alias"; registry uses tri_label
    item["aliases"] = _build_tri_label_aliases(new_gold)

    # For items like gen_b_039 / gen_a2_005 where "contested" should also be accepted
    # alongside the gold "false"
    iid = item["item_id"]
    if iid == "gen_b_039":
        # Accept both "false" and "contested" - dual assertion
        item["aliases"] = _build_tri_label_aliases("false") + _build_tri_label_aliases("contested")
    elif iid == "gen_a2_005":
        # Accept both "false" and "contested"
        item["aliases"] = _build_tri_label_aliases("false") + _build_tri_label_aliases("contested")

    changes.append(f"rule: {old_rule} -> alias (registry: tri_label)")
    changes.append(f"aliases -> {item['aliases']}")
    return changes


def _update_numeric_approx(item: dict, triage: dict) -> list[str]:
    """Handle items switching to approx_numeric_small."""
    changes = []
    iid = item["item_id"]
    old_rule = item["rule"]

    new_gold = triage.get("new_gold")
    if new_gold:
        old_gold = item["gold_answer"]
        item["gold_answer"] = new_gold
        changes.append(f"gold: {old_gold} -> {new_gold}")

    item["rule"] = "numeric"  # dataset rule stays "numeric"; registry uses specific grader

    # Per-item alias and tolerance config
    if iid == "gen_a_030":
        item["aliases"] = ["69", "70", "71", "72"]
    elif iid == "gen_a_033":
        item["aliases"] = ["91", "92", "93", "94"]
    elif iid == "gen_a_035":
        item["aliases"] = ["94", "95", "96"]
    elif iid == "gen_a_044":
        item["aliases"] = ["97.9", "97.8", "98.0"]
    elif iid == "gen_b2_033":
        item["aliases"] = ["48", "49", "50", "49%", "about 49", "roughly 49", "50%"]

    changes.append(f"rule: {old_rule} -> numeric")
    changes.append(f"aliases -> {item['aliases']}")
    return changes


def _update_numeric_dynamic(item: dict, triage: dict) -> list[str]:
    """Handle items switching to approx_numeric_dynamic."""
    changes = []
    iid = item["item_id"]

    new_gold = triage.get("new_gold")
    if new_gold:
        old_gold = item["gold_answer"]
        item["gold_answer"] = new_gold
        changes.append(f"gold: {old_gold} -> {new_gold}")

    item["rule"] = "numeric"

    if iid == "gen_b3_004":
        item["gold_answer"] = "250"
        item["aliases"] = [str(x) for x in range(240, 271)]
        changes.append(f"gold: -> 250, aliases: 240-270")
    elif iid == "gen_b3_005":
        item["gold_answer"] = "330"
        item["aliases"] = [str(x) for x in range(326, 341)]
        changes.append(f"gold: -> 330, aliases: 326-340")
    elif iid == "gen_b3_006":
        item["gold_answer"] = "122"
        item["aliases"] = [str(x) for x in range(115, 131)]
        changes.append(f"gold: -> 122, aliases: 115-130")
    elif iid == "gen_b3_007":
        item["gold_answer"] = "95"
        item["aliases"] = [str(x) for x in range(92, 98)]
        changes.append(f"gold: -> 95, aliases: 92-97")
    elif iid == "gen_b3_009":
        item["gold_answer"] = "61"
        item["aliases"] = ["58", "59", "60", "61", "62"]
        changes.append(f"gold: -> 61, aliases: 58-62")

    return changes


def _update_exact_constant(item: dict, triage: dict) -> list[str]:
    """Handle items switching to exact_constant."""
    changes = []
    iid = item["item_id"]

    new_gold = triage.get("new_gold")
    if new_gold:
        old_gold = item["gold_answer"]
        item["gold_answer"] = new_gold
        changes.append(f"gold: {old_gold} -> {new_gold}")

    item["rule"] = "numeric"  # dataset uses "numeric"; registry uses exact_constant

    if iid == "gen_a_042":
        item["gold_answer"] = "6.0221408"
        item["aliases"] = ["6.0221408", "6.02214076", "6.0221408e23",
                           "6.02214076e23", "6.022 x 10^23"]
        changes.append(f"gold: -> 6.0221408 (8 sig figs, matching question)")
    elif iid == "gen_a2_032":
        # Keep gold; add space-tolerant aliases
        item["aliases"] = [
            "1.6726219260e-27", "1.672621926e-27",
            "1.672621926×10⁻²⁷", "1.6726219260×10⁻²⁷",
            "1.672621926 × 10⁻²⁷", "1.6726219260 × 10⁻²⁷",
            "1.67262192595e-27",
        ]
    elif iid == "gen_a2_038":
        item["aliases"] = ["99.61", "99.61°C", "99.61 C", "99.61°c"]

    changes.append(f"rule: -> numeric (registry: exact_constant)")
    changes.append(f"aliases -> {item['aliases']}")
    return changes


def _update_alias_plus_norm(item: dict, triage: dict) -> list[str]:
    """Handle items switching to alias_plus_normalization."""
    changes = []
    iid = item["item_id"]

    item["rule"] = "alias"  # dataset stays "alias"; registry uses alias_plus_normalization

    if iid == "gen_b_004":
        item["aliases"] = ["4/5", "0.8", "80%", "0.80", "4 out of 5"]
    elif iid == "gen_a_026":
        item["aliases"] = [
            "greenland", "greenland, 10%", "greenland, approximately 10%",
            "greenland, about 10%", "greenland is larger by about 10%",
        ]
    elif iid == "gen_b2_036":
        item["aliases"] = ["monaco", "Monaco"]
    elif iid == "gen_b_024":
        item["aliases"] = [
            "university of bologna", "Bologna", "University of Bologna",
            "University of Al-Qarawiyyin", "Al-Qarawiyyin",
            "al-qarawiyyin", "al qarawiyyin",
        ]
    elif iid == "gen_b_025":
        item["aliases"] = ["italy", "Italy", "Italian Republic"]
    elif iid == "gen_b_042":
        item["aliases"] = ["ojos del salado", "Ojos del Salado",
                           "Ojos Del Salado", "nevado ojos del salado"]
    elif iid == "gen_b2_019":
        item["aliases"] = ["sweden", "Sweden", "Kingdom of Sweden"]
    elif iid == "gen_b2_021":
        item["aliases"] = ["france", "France", "French Republic"]

    changes.append(f"rule: -> alias (registry: alias_plus_normalization)")
    changes.append(f"aliases -> {item['aliases']}")
    return changes


# ---------------------------------------------------------------------------
# REWRITE handler
# ---------------------------------------------------------------------------

_REWRITE_QUESTIONS = {
    "gen_a3_001": (
        "Is the following claim unambiguously true, unambiguously false, or "
        "contested among experts: 'The scientific consensus is that dietary "
        "saturated fat directly causes cardiovascular disease in the general "
        "population.' Answer with one word: true, false, or contested."
    ),
    "gen_a3_007": (
        "Is the following claim unambiguously true, unambiguously false, or "
        "contested among experts: 'High testosterone levels in humans directly "
        "and causally produce increased aggression.' Answer with one word: "
        "true, false, or contested."
    ),
    "gen_a4_022": (
        "Is the following claim unambiguously true, unambiguously false, or "
        "contested among experts: 'There is scientific consensus on whether "
        "free will exists as traditionally conceived.' Answer with one word: "
        "true, false, or contested."
    ),
    "gen_a4_024": (
        "Is the following claim unambiguously true, unambiguously false, or "
        "contested among experts: 'There is scientific consensus on whether "
        "intelligence is primarily determined by genetics or environment.' "
        "Answer with one word: true, false, or contested."
    ),
}


def _apply_rewrite(item: dict, triage: dict) -> list[str]:
    """Rewrite T/F questions to tri-label format."""
    changes = []
    iid = item["item_id"]

    old_q = item["question"]
    new_q = _REWRITE_QUESTIONS[iid]
    item["question"] = new_q
    changes.append(f"question rewritten from T/F to tri-label format")

    item["rule"] = "alias"  # dataset: alias; registry: tri_label
    item["gold_answer"] = triage.get("new_gold") or item["gold_answer"]
    item["aliases"] = _build_tri_label_aliases(item["gold_answer"])

    changes.append(f"rule: {triage['current_rule']} -> alias (registry: tri_label)")
    changes.append(f"aliases -> {item['aliases']}")
    return changes


# ---------------------------------------------------------------------------
# Registry update
# ---------------------------------------------------------------------------

def _build_registry_entry(item: dict, triage: dict) -> dict:
    """Build updated registry entry for an item."""
    iid = item["item_id"]
    new_rule = triage.get("new_rule") or "alias_plus_normalization"
    gold = item["gold_answer"]

    entry = {
        "item_id": iid,
        "answer_type": _infer_answer_type(new_rule, gold),
        "grader_rule": new_rule,
        "gold_answer": gold,
        "accepted_forms": list(item.get("aliases", [])),
        "tolerance_class": None,
        "tolerance_params": None,
        "time_anchor": None,
        "source_anchor": None,
        "normalization_notes": None,
        "tri_label_space": None,
        "edge_case_notes": None,
    }

    # Set rule-specific fields
    if new_rule == "tri_label":
        entry["tri_label_space"] = ["true", "false", "contested"]
        entry["answer_type"] = "tri_label"

    elif new_rule == "approx_numeric_small":
        entry["answer_type"] = "numeric"
        if iid == "gen_a_030":
            entry["tolerance_class"] = "abs_2"
            entry["tolerance_params"] = {"abs_tol": 2.0}
        elif iid == "gen_a_033":
            entry["tolerance_class"] = "abs_2"
            entry["tolerance_params"] = {"abs_tol": 2.0}
        elif iid == "gen_a_035":
            entry["tolerance_class"] = "abs_2"
            entry["tolerance_params"] = {"abs_tol": 2.0}
        elif iid == "gen_a_044":
            entry["tolerance_class"] = "abs_05"
            entry["tolerance_params"] = {"abs_tol": 0.5}
        elif iid == "gen_b2_033":
            entry["tolerance_class"] = "abs_2"
            entry["tolerance_params"] = {"abs_tol": 2.0}

    elif new_rule == "approx_numeric_dynamic":
        entry["answer_type"] = "numeric"
        if iid == "gen_b3_004":
            entry["tolerance_class"] = "rel_10pct"
            entry["tolerance_params"] = {"rel_tol": 0.10}
            entry["time_anchor"] = "2024"
            entry["source_anchor"] = "World Bank Qatar population density"
        elif iid == "gen_b3_005":
            entry["tolerance_class"] = "rel_10pct"
            entry["tolerance_params"] = {"rel_tol": 0.10}
            entry["time_anchor"] = "2025"
            entry["source_anchor"] = "World Bank Japan population density"
        elif iid == "gen_b3_006":
            entry["tolerance_class"] = "rel_10pct"
            entry["tolerance_params"] = {"rel_tol": 0.10}
            entry["time_anchor"] = "2025"
            entry["source_anchor"] = "INSEE France population density (metropolitan)"
        elif iid == "gen_b3_007":
            entry["tolerance_class"] = "rel_5pct"
            entry["tolerance_params"] = {"rel_tol": 0.05}
            entry["time_anchor"] = "2025"
            entry["source_anchor"] = "World Bank Spain population density"
        elif iid == "gen_b3_009":
            entry["tolerance_class"] = "abs_3"
            entry["tolerance_params"] = {"abs_tol": 3.0}
            entry["time_anchor"] = "2025"
            entry["source_anchor"] = "UNESCO World Heritage List"

    elif new_rule == "exact_constant":
        entry["answer_type"] = "exact_constant"
        entry["tolerance_class"] = "rel_1e6"
        entry["tolerance_params"] = {"rel_tol": 1e-6}

    return entry


def _infer_answer_type(rule: str, gold: str) -> str:
    """Infer answer_type from the grader rule."""
    mapping = {
        "tri_label": "tri_label",
        "yes_no": "boolean",
        "approx_numeric_small": "numeric",
        "approx_numeric_dynamic": "numeric",
        "exact_constant": "exact_constant",
        "fraction_or_decimal": "fraction",
        "code_output": "code_output",
        "alias_plus_normalization": "text",
    }
    return mapping.get(rule, "text")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Load inputs
    with open(DATASET_PATH) as f:
        dataset = json.load(f)
    with open(TRIAGE_PATH) as f:
        triage_list = json.load(f)
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    ds_idx = {item["item_id"]: item for item in dataset}
    triage_idx = {t["item_id"]: t for t in triage_list}
    reg_idx = {e["item_id"]: e for e in registry}

    changelog = []
    output_items = []
    removed_ids = set()

    for triage in triage_list:
        iid = triage["item_id"]
        bucket = triage["bucket"]
        item = copy.deepcopy(ds_idx[iid])

        if bucket == "replace":
            removed_ids.add(iid)
            changelog.append(f"REMOVE  {iid}")
            continue

        if bucket == "keep":
            output_items.append(item)
            changelog.append(f"KEEP    {iid}")
            continue

        if bucket == "rewrite":
            changes = _apply_rewrite(item, triage)
            output_items.append(item)
            # Update registry
            reg_idx[iid] = _build_registry_entry(item, triage)
            changelog.append(f"REWRITE {iid}: {'; '.join(changes)}")
            continue

        # bucket == "update"
        new_rule = triage.get("new_rule", "")
        changes = []

        if new_rule == "tri_label":
            changes = _update_tri_label(item, triage)
        elif new_rule == "approx_numeric_small":
            changes = _update_numeric_approx(item, triage)
        elif new_rule == "approx_numeric_dynamic":
            changes = _update_numeric_dynamic(item, triage)
        elif new_rule == "exact_constant":
            changes = _update_exact_constant(item, triage)
        elif new_rule == "alias_plus_normalization":
            changes = _update_alias_plus_norm(item, triage)
        else:
            changes.append(f"(no handler for rule '{new_rule}'; kept as-is)")

        output_items.append(item)
        # Update registry
        reg_idx[iid] = _build_registry_entry(item, triage)
        changelog.append(f"UPDATE  {iid}: {'; '.join(changes)}")

    # Remove replaced items from registry
    updated_registry = [e for iid, e in reg_idx.items() if iid not in removed_ids]

    # ---------------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------------
    ids = [item["item_id"] for item in output_items]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {len(ids)} vs {len(set(ids))}"

    required_fields = {"item_id", "mechanism_primary", "question", "gold_answer",
                       "aliases", "rule", "batch", "final_tier", "final_classification"}
    for item in output_items:
        missing = required_fields - set(item.keys())
        assert not missing, f"{item['item_id']} missing fields: {missing}"

    # Count by bucket
    from collections import Counter
    bucket_counts = Counter(t["bucket"] for t in triage_list)

    # ---------------------------------------------------------------------------
    # Write outputs
    # ---------------------------------------------------------------------------
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output_items, f, indent=2, ensure_ascii=False)

    with open(REGISTRY_PATH, "w") as f:
        json.dump(updated_registry, f, indent=2, ensure_ascii=False)

    # ---------------------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------------------
    print("=" * 70)
    print("V4.1 Triage Application Report")
    print("=" * 70)
    print(f"\nInput:  {len(dataset)} items")
    print(f"Output: {len(output_items)} items (base set before Squad 3 replacements)")
    print(f"\nBucket counts:")
    for bucket, count in sorted(bucket_counts.items()):
        print(f"  {bucket:10s}: {count}")
    print(f"\nRemoved: {len(removed_ids)} items")
    print(f"Registry: {len(updated_registry)} entries (was {len(registry)})")

    print(f"\n{'=' * 70}")
    print("Changelog:")
    print("=" * 70)
    for line in changelog:
        print(f"  {line}")

    print(f"\n{'=' * 70}")
    print("Validation:")
    print(f"  Unique IDs: {len(set(ids))}/{len(ids)} ✓")
    print(f"  All required fields present ✓")
    print(f"  Output written to: {OUTPUT_PATH}")
    print(f"  Registry written to: {REGISTRY_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
