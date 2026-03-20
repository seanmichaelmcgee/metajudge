#!/usr/bin/env python3
"""
validate_benchmark.py
=====================
Verification script for data/metajudge_benchmark_v1.json.

Checks:
  1.  Loads the output file successfully.
  2.  Asserts exactly 102 items.
  3.  Asserts zero duplicate item_ids.
  4.  Asserts every item has non-empty question, gold_answer, rule,
      item_id, mechanism_primary, batch; and that the aliases field is
      present (an empty list [] is a valid value meaning "no aliases").
  5.  For batch 1 items: asserts no question is exactly 120 chars AND
      ends mid-sentence (i.e., does not end with a sentence-terminal
      punctuation mark).
  6.  For batch 1 items: cross-checks that question text matches CDM exactly.
  7.  For batch 2/3/4 items: cross-checks that question text matches
      combined_survivors.json exactly (proves batch 2-4 were not modified).
  8.  Prints a summary: item count, batch distribution, question length
      stats (min/max/mean per batch).

Usage:
    python scripts/validate_benchmark.py
"""

import json
import statistics
from pathlib import Path

REPO_ROOT       = Path(__file__).parent.parent
BENCHMARK_PATH  = REPO_ROOT / "data" / "metajudge_benchmark_v1.json"
SURVIVORS_PATH  = REPO_ROOT / "data" / "combined_survivors.json"
CDM_PATH        = REPO_ROOT / "data" / "combined_discrimination_matrix.json"

REQUIRED_NONEMPTY_FIELDS = [
    "item_id",
    "batch",
    "question",
    "gold_answer",
    "rule",
    "mechanism_primary",
]
# 'aliases' is separately validated — present and not None, but [] is valid.

SENTENCE_TERMINALS = {".", "?", "!", '"', "'"}


def check(condition: bool, message: str) -> None:
    """Assert with a descriptive error message."""
    if not condition:
        raise AssertionError(f"FAIL: {message}")


def load_json(path: Path) -> object:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    failures: list[str] = []
    passed:   list[str] = []

    def ok(label: str) -> None:
        passed.append(label)
        print(f"  PASS  {label}")

    def fail(label: str, detail: str) -> None:
        msg = f"{label}: {detail}"
        failures.append(msg)
        print(f"  FAIL  {msg}")

    print("=" * 60)
    print("MetaJudge Benchmark Validation Report")
    print("=" * 60)
    print()

    # ------------------------------------------------------------------
    # Load files
    # ------------------------------------------------------------------
    print("[Loading files]")
    benchmark  = load_json(BENCHMARK_PATH)
    survivors  = load_json(SURVIVORS_PATH)
    cdm        = load_json(CDM_PATH)
    print(f"  benchmark  : {len(benchmark)} items  ({BENCHMARK_PATH})")
    print(f"  survivors  : {len(survivors)} items  ({SURVIVORS_PATH})")
    print(f"  CDM        : {len(cdm)} items  ({CDM_PATH})")
    print()

    # Build lookup maps
    surv_lookup: dict[str, dict] = {item["item_id"]: item for item in survivors}
    cdm_lookup:  dict[str, dict] = {item["item_id"]: item for item in cdm}

    # ------------------------------------------------------------------
    # Check 1: Exactly 102 items
    # ------------------------------------------------------------------
    print("[Check 1] Item count == 102")
    if len(benchmark) == 102:
        ok(f"item count == 102")
    else:
        fail("item count", f"expected 102, got {len(benchmark)}")
    print()

    # ------------------------------------------------------------------
    # Check 2: No duplicate item_ids
    # ------------------------------------------------------------------
    print("[Check 2] No duplicate item_ids")
    seen_ids: set[str] = set()
    dup_ids:  list[str] = []
    for item in benchmark:
        iid = item.get("item_id", "")
        if iid in seen_ids:
            dup_ids.append(iid)
        seen_ids.add(iid)
    if not dup_ids:
        ok("zero duplicate item_ids")
    else:
        fail("duplicate item_ids", f"duplicates: {dup_ids}")
    print()

    # ------------------------------------------------------------------
    # Check 3: Required fields non-empty on every item
    # ------------------------------------------------------------------
    print("[Check 3] Required fields non-empty on every item")
    field_errors: list[str] = []
    for item in benchmark:
        iid = item.get("item_id", "<no id>")
        for field in REQUIRED_NONEMPTY_FIELDS:
            val = item.get(field)
            if val is None or val == "":
                field_errors.append(f"{iid}.{field}={repr(val)}")
        # aliases must be present and not None ([] is OK)
        if "aliases" not in item:
            field_errors.append(f"{iid}.aliases=<missing>")
        elif item["aliases"] is None:
            field_errors.append(f"{iid}.aliases=None")
    if not field_errors:
        ok("all required fields present and non-empty on all 102 items")
    else:
        for e in field_errors[:10]:
            fail("missing/empty field", e)
        if len(field_errors) > 10:
            print(f"    ... and {len(field_errors)-10} more")
    print()

    # ------------------------------------------------------------------
    # Check 4 & 5: Batch 1 — no truncated questions + CDM match
    # ------------------------------------------------------------------
    print("[Check 4] Batch 1 — no question is exactly 120 chars ending mid-sentence")
    print("[Check 5] Batch 1 — every question matches CDM exactly")
    batch1_items = [item for item in benchmark if item.get("batch") == 1]
    print(f"  batch 1 item count: {len(batch1_items)}")
    trunc_errors:    list[str] = []
    cdm_mismatch:    list[str] = []
    cdm_missing:     list[str] = []
    for item in batch1_items:
        iid = item["item_id"]
        q   = item.get("question", "")
        # Truncation check: exactly 120 chars AND last char is not a sentence terminal
        if len(q) == 120 and q[-1] not in SENTENCE_TERMINALS:
            trunc_errors.append(f"{iid}: len=120, last_char={repr(q[-1])}, q={repr(q[:60])}...")
        # CDM match check
        if iid not in cdm_lookup:
            cdm_missing.append(iid)
        else:
            cdm_q = cdm_lookup[iid].get("question", "")
            if q != cdm_q:
                cdm_mismatch.append(
                    f"{iid}: bench_len={len(q)}, cdm_len={len(cdm_q)}"
                )
    if not trunc_errors:
        ok("no batch 1 question is truncated at 120 chars")
    else:
        for e in trunc_errors:
            fail("truncated question", e)
    if cdm_missing:
        for iid in cdm_missing:
            fail("CDM item missing", iid)
    if not cdm_mismatch:
        ok("all batch 1 questions match CDM exactly")
    else:
        for e in cdm_mismatch:
            fail("CDM question mismatch", e)
    print()

    # ------------------------------------------------------------------
    # Check 6: Batch 2/3/4 — questions unchanged from combined_survivors.json
    # ------------------------------------------------------------------
    print("[Check 6] Batch 2/3/4 — questions unchanged from combined_survivors.json")
    non_b1_items = [item for item in benchmark if item.get("batch") != 1]
    print(f"  non-batch-1 item count: {len(non_b1_items)}")
    surv_mismatch: list[str] = []
    surv_missing:  list[str] = []
    for item in non_b1_items:
        iid = item["item_id"]
        q   = item.get("question", "")
        if iid not in surv_lookup:
            surv_missing.append(iid)
        else:
            surv_q = surv_lookup[iid].get("question", "")
            if q != surv_q:
                surv_mismatch.append(
                    f"{iid}: bench_len={len(q)}, surv_len={len(surv_q)}"
                )
    if surv_missing:
        for iid in surv_missing:
            fail("survivors item missing", iid)
    if not surv_mismatch:
        ok("all batch 2/3/4 questions are byte-for-byte identical to combined_survivors.json")
    else:
        for e in surv_mismatch:
            fail("survivors question mismatch", e)
    print()

    # ------------------------------------------------------------------
    # Summary stats
    # ------------------------------------------------------------------
    print("[Summary Statistics]")
    batch_distribution: dict[int, list[int]] = {}
    for item in benchmark:
        b = item.get("batch")
        q = item.get("question", "")
        if b not in batch_distribution:
            batch_distribution[b] = []
        batch_distribution[b].append(len(q))

    total_lengths = [len(item.get("question", "")) for item in benchmark]
    print(f"  Total items  : {len(benchmark)}")
    print(f"  Batch dist   : { {b: len(v) for b, v in sorted(batch_distribution.items())} }")
    print(f"  Q len overall: min={min(total_lengths)}, max={max(total_lengths)}, "
          f"mean={statistics.mean(total_lengths):.1f}")
    print()
    print(f"  {'Batch':<8} {'Count':<8} {'Min Q':<8} {'Max Q':<8} {'Mean Q':<8}")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for b in sorted(batch_distribution.keys()):
        lens = batch_distribution[b]
        print(f"  {b:<8} {len(lens):<8} {min(lens):<8} {max(lens):<8} {statistics.mean(lens):<8.1f}")
    print()

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------
    print("=" * 60)
    total_checks = len(passed) + len(failures)
    print(f"Result: {len(passed)}/{total_checks} checks passed")
    if failures:
        print()
        print("FAILURES:")
        for f_msg in failures:
            print(f"  - {f_msg}")
        print()
        print("STATUS: FAILED")
        raise SystemExit(1)
    else:
        print()
        print("STATUS: ALL CHECKS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
