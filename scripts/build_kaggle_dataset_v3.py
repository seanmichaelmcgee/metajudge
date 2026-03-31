#!/usr/bin/env python3
"""Build kaggle-dataset-v3/ from source data.

Merges Family C clean items into the Kaggle dataset alongside A/B,
extends the adjudication registry, and updates the manifest.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_C1 = ROOT / "data" / "family_c" / "family_c_c1_candidates.json"
SRC_C2 = ROOT / "data" / "family_c" / "family_c_c2_candidates.json"
V2_DIR = ROOT / "kaggle-dataset-v2"
V3_DIR = ROOT / "kaggle-dataset-v3"

# --- Field mapping: internal candidate → export format ---
EXPORT_FIELDS = [
    "item_id", "family", "subfamily", "question", "gold_answer", "aliases",
    "rule", "stratum", "mechanism_primary", "category", "difficulty",
    "normative_t2_action", "challenge_type", "evidence_snippet", "tolerance",
]

FIELD_MAP = {
    "turn1_prompt": "question",
    "gold_answer_aliases": "aliases",
    "grading_rule": "rule",
}

# --- Grading rule → answer_type mapping ---
RULE_TO_ANSWER_TYPE = {
    "exact_constant": "numeric",
    "approx_numeric_small": "numeric",
    "approx_numeric_dynamic": "numeric",
    "fraction_or_decimal": "numeric",
    "tri_label": "tri_label",
    "yes_no": "boolean",
    "code_output": "text",
    "alias_plus_normalization": "text",
}


def load_clean_candidates(path):
    with open(path) as f:
        items = json.load(f)
    return [it for it in items if it.get("draft_status") == "clean"]


def map_to_export(item):
    """Map internal candidate fields to export schema."""
    out = {}
    for field in EXPORT_FIELDS:
        # Check if field needs mapping from internal name
        internal_key = next((k for k, v in FIELD_MAP.items() if v == field), field)
        val = item.get(internal_key, item.get(field))
        out[field] = val
    return out


def build_registry_entry(item):
    """Build adjudication registry entry from candidate item."""
    rule = item.get("grading_rule", "alias_plus_normalization")
    tolerance = item.get("tolerance")

    entry = {
        "item_id": item["item_id"],
        "answer_type": RULE_TO_ANSWER_TYPE.get(rule, "text"),
        "grader_rule": rule,
        "gold_answer": item["gold_answer"],
        "accepted_forms": item.get("gold_answer_aliases", [item["gold_answer"]]),
        "tolerance_class": None,
        "tolerance_params": None,
        "time_anchor": None,
        "source_anchor": None,
        "normalization_notes": None,
        "tri_label_space": None,
        "edge_case_notes": item.get("audit_notes"),
    }

    if tolerance:
        entry["tolerance_params"] = tolerance
        if "abs_tol" in tolerance:
            entry["tolerance_class"] = f"abs_{tolerance['abs_tol']}"

    if rule == "tri_label":
        entry["tri_label_space"] = ["true", "false", "contested"]

    # Add match_mode for alias rules with multiple accepted forms
    if rule == "alias_plus_normalization" and len(entry["accepted_forms"]) > 1:
        entry["match_mode"] = "contains_any"

    return entry


def build_manifest_fc_section(c1_items, c2_items, c1_all, c2_all):
    """Build family_c section for clean_subset_manifest."""
    c1_quarantine = [it["item_id"] for it in c1_all if it.get("draft_status") != "clean"]
    c2_quarantine = [it["item_id"] for it in c2_all if it.get("draft_status") != "clean"]
    excluded = c1_quarantine + c2_quarantine

    # Stratum coverage
    from collections import Counter
    strata_total = Counter()
    strata_clean = Counter()
    for it in c1_all + c2_all:
        s = it.get("stratum", "unknown")
        strata_total[s] += 1
        if it.get("draft_status") == "clean":
            strata_clean[s] += 1

    stratum_coverage = {}
    for s in sorted(strata_total):
        t, c = strata_total[s], strata_clean[s]
        stratum_coverage[s] = {"total": t, "clean": c, "pct": round(c / t, 3) if t else 0}

    return {
        "total_items": len(c1_all) + len(c2_all),
        "excluded_items": excluded,
        "excluded_count": len(excluded),
        "clean_count": len(c1_items) + len(c2_items),
        "retention_rate": round((len(c1_items) + len(c2_items)) / (len(c1_all) + len(c2_all)), 3),
        "subfamily_counts": {
            "C1": len(c1_items),
            "C2": len(c2_items),
        },
        "stratum_coverage": stratum_coverage,
    }


def main():
    # Load candidates
    c1_all = json.load(open(SRC_C1))
    c2_all = json.load(open(SRC_C2))
    c1_clean = load_clean_candidates(SRC_C1)
    c2_clean = load_clean_candidates(SRC_C2)
    print(f"C1: {len(c1_clean)}/{len(c1_all)} clean, C2: {len(c2_clean)}/{len(c2_all)} clean")

    # Create v3 directory
    V3_DIR.mkdir(exist_ok=True)

    # --- A1: family_c_items.json ---
    fc_items = [map_to_export(it) for it in c1_clean + c2_clean]
    with open(V3_DIR / "family_c_items.json", "w") as f:
        json.dump(fc_items, f, indent=2)
    print(f"Wrote {len(fc_items)} items to family_c_items.json")

    # --- A2: Extended adjudication_registry.json ---
    with open(V2_DIR / "adjudication_registry.json") as f:
        registry = json.load(f)
    existing_ids = {e["item_id"] for e in registry}
    new_entries = []
    for it in c1_clean + c2_clean:
        if it["item_id"] not in existing_ids:
            new_entries.append(build_registry_entry(it))
    registry.extend(new_entries)
    with open(V3_DIR / "adjudication_registry.json", "w") as f:
        json.dump(registry, f, indent=2)
    print(f"Registry: {len(registry)} entries ({len(new_entries)} new Family C)")

    # --- A3: Updated clean_subset_manifest.json ---
    with open(V2_DIR / "clean_subset_manifest.json") as f:
        manifest = json.load(f)
    manifest["version"] = "v3.0"
    manifest["created"] = "2026-03-31"
    manifest["family_c"] = build_manifest_fc_section(c1_clean, c2_clean, c1_all, c2_all)
    with open(V3_DIR / "clean_subset_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest updated with family_c section: {manifest['family_c']['clean_count']} clean items")

    # --- A4: Copy unchanged files ---
    for fname in ["metajudge_benchmark_v1.json", "family_b_pilot_v2.json"]:
        shutil.copy2(V2_DIR / fname, V3_DIR / fname)
        print(f"Copied {fname}")

    # --- A5: dataset-metadata.json ---
    metadata = {
        "title": "MetaJudge Benchmark Data v3 (Families A+B+C)",
        "id": "seanmcgee2025/metajudge-data-v3",
        "licenses": [{"name": "CC-BY-4.0"}],
        "description": (
            "MetaJudge benchmark v3: adds Family C (Self-Correction) to existing "
            "Family A (Calibration) and Family B (Selective Abstention). "
            f"Family C: {len(fc_items)} clean items ({len(c1_clean)} C1 intrinsic + "
            f"{len(c2_clean)} C2 evidence-assisted). "
            "Registry extended with Family C grading entries. "
            "Family A/B data unchanged from v2."
        ),
        "keywords": [
            "metacognition", "llm-evaluation", "calibration",
            "self-correction", "benchmark", "families-abc",
        ],
    }
    with open(V3_DIR / "dataset-metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("Wrote dataset-metadata.json")

    print(f"\nDone. kaggle-dataset-v3/ contains {len(list(V3_DIR.iterdir()))} files.")


if __name__ == "__main__":
    main()
