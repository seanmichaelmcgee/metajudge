#!/usr/bin/env python3
"""
build_frozen_benchmark.py
=========================
Reconstruction script for the canonical frozen MetaJudge benchmark dataset.

Recipe:
1. Load data/combined_survivors.json as the structural base (102 items with
   aliases, rule, and all scoring fields).
2. Load data/combined_discrimination_matrix.json (CDM) which holds full
   question text for all items, including batch 1 items that are truncated
   in combined_survivors.json.
3. For all 19 batch 1 items: replace question with the full text from CDM.
4. Verify 102 items, no duplicates, all required fields populated.
5. Write data/metajudge_benchmark_v1.json (pretty-printed JSON array).

Usage:
    python scripts/build_frozen_benchmark.py
"""

import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
SURVIVORS_PATH  = REPO_ROOT / "data" / "combined_survivors.json"
CDM_PATH        = REPO_ROOT / "data" / "combined_discrimination_matrix.json"
OUTPUT_PATH     = REPO_ROOT / "data" / "metajudge_benchmark_v1.json"

REQUIRED_FIELDS = [
    "item_id",
    "batch",
    "question",
    "gold_answer",
    "aliases",
    "rule",
    "mechanism_primary",
    "final_tier",
    "final_classification",
]


def load_json(path: Path) -> object:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    print("=== build_frozen_benchmark.py ===")
    print(f"Survivors path : {SURVIVORS_PATH}")
    print(f"CDM path       : {CDM_PATH}")
    print(f"Output path    : {OUTPUT_PATH}")
    print()

    # ------------------------------------------------------------------
    # Step 1 – Load source files
    # ------------------------------------------------------------------
    survivors = load_json(SURVIVORS_PATH)
    cdm       = load_json(CDM_PATH)

    assert isinstance(survivors, list), "combined_survivors.json must be a JSON array"
    assert isinstance(cdm, list),       "combined_discrimination_matrix.json must be a JSON array"

    print(f"Loaded {len(survivors)} survivors")
    print(f"Loaded {len(cdm)} CDM items")

    # ------------------------------------------------------------------
    # Step 2 – Build CDM lookup keyed by item_id
    # ------------------------------------------------------------------
    cdm_lookup: dict[str, dict] = {}
    for item in cdm:
        iid = item["item_id"]
        assert iid not in cdm_lookup, f"Duplicate item_id in CDM: {iid}"
        cdm_lookup[iid] = item

    # ------------------------------------------------------------------
    # Step 3 – For batch 1 items: replace question from CDM
    # ------------------------------------------------------------------
    fixed = 0
    unchanged = 0
    output_items = []

    for item in survivors:
        # Deep-copy so we don't mutate the source list
        out_item = dict(item)

        if out_item.get("batch") == 1:
            iid = out_item["item_id"]
            assert iid in cdm_lookup, f"Batch 1 item {iid} not found in CDM"
            cdm_question = cdm_lookup[iid]["question"]
            if out_item["question"] != cdm_question:
                out_item["question"] = cdm_question
                fixed += 1
            else:
                unchanged += 1
        else:
            unchanged += 1

        output_items.append(out_item)

    print(f"Batch 1 questions fixed from CDM  : {fixed}")
    print(f"Items left unchanged              : {unchanged}")
    print(f"Total output items                : {len(output_items)}")

    # ------------------------------------------------------------------
    # Step 4 – Pre-write sanity checks
    # ------------------------------------------------------------------
    assert len(output_items) == 102, f"Expected 102 items, got {len(output_items)}"

    seen_ids: set[str] = set()
    for item in output_items:
        iid = item["item_id"]
        assert iid not in seen_ids, f"Duplicate item_id: {iid}"
        seen_ids.add(iid)

        for field in REQUIRED_FIELDS:
            val = item.get(field)
            # aliases may be an empty list (valid: means no aliases for this item)
            if field == "aliases":
                assert val is not None, \
                    f"Item {iid} has aliases=None"
            else:
                assert val is not None and val != "", \
                    f"Item {iid} has empty/missing field '{field}': {repr(val)}"

    batch_counts: dict[int, int] = {}
    for item in output_items:
        b = item["batch"]
        batch_counts[b] = batch_counts.get(b, 0) + 1

    print(f"Batch distribution: {dict(sorted(batch_counts.items()))}")
    print()
    print("Pre-write checks passed.")

    # ------------------------------------------------------------------
    # Step 5 – Write output
    # ------------------------------------------------------------------
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(output_items, fh, indent=2, ensure_ascii=False)

    print(f"Written: {OUTPUT_PATH}")
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"File size: {file_size:,} bytes")
    print()
    print("Build complete.")


if __name__ == "__main__":
    main()
