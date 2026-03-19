"""Build production files from v2_selected_100.json + v2_alias_ledger.json"""
import json
import csv
import io

REPO = "/home/user/workspace/metajudge"
selected = json.load(open(f"{REPO}/data/harvest/v2_selected_100.json"))
ledger = json.load(open(f"{REPO}/data/harvest/v2_alias_ledger.json"))

# ============================================================
# 1. calibration.csv — the main dataset file
# ============================================================
# Schema: example_id, prompt, gold_answer, difficulty
csv_rows = []
for item in selected:
    csv_rows.append({
        "example_id": item["example_id"],
        "prompt": item["prompt"],
        "gold_answer": item["gold_answer"],
        "difficulty": item["difficulty"],
    })

with open(f"{REPO}/data/calibration.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["example_id", "prompt", "gold_answer", "difficulty"])
    writer.writeheader()
    writer.writerows(csv_rows)

print(f"calibration.csv: {len(csv_rows)} rows written")

# ============================================================
# 2. calibration_answer_key.json
# ============================================================
# Schema per entry: gold_answer, aliases, answer_type, grader_rule, format_instruction
answer_key = {}
for item in selected:
    eid = item["example_id"]
    cid = item["canonical_id"]
    
    # Get aliases from ledger
    aliases = []
    if cid in ledger:
        aliases = ledger[cid].get("accepted_aliases", [])
    
    # Ensure gold_answer is in aliases
    if item["gold_answer"] not in aliases:
        aliases.insert(0, item["gold_answer"])
    
    answer_key[eid] = {
        "gold_answer": item["gold_answer"],
        "aliases": aliases,
        "answer_type": item["answer_type"],
        "grader_rule": item["grader_rule"],
        "format_instruction": item["format_instruction"],
    }

with open(f"{REPO}/data/calibration_answer_key.json", "w") as f:
    json.dump(answer_key, f, indent=2)

print(f"calibration_answer_key.json: {len(answer_key)} entries written")

# ============================================================
# 3. calibration_provenance.csv
# ============================================================
# Schema: example_id, source, item_family, difficulty, gold_answer, answer_type, aliases, note
prov_rows = []
for item in selected:
    eid = item["example_id"]
    cid = item["canonical_id"]
    
    aliases_str = ""
    if cid in ledger:
        aliases_str = "; ".join(ledger[cid].get("accepted_aliases", []))
    
    prov_rows.append({
        "example_id": eid,
        "source": item["source"],
        "item_family": item["item_family"],
        "difficulty": item["difficulty"],
        "gold_answer": item["gold_answer"],
        "answer_type": item["answer_type"],
        "aliases": aliases_str,
        "note": item.get("note", ""),
    })

with open(f"{REPO}/data/calibration_provenance.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["example_id", "source", "item_family", "difficulty", "gold_answer", "answer_type", "aliases", "note"])
    writer.writeheader()
    writer.writerows(prov_rows)

print(f"calibration_provenance.csv: {len(prov_rows)} rows written")

# ============================================================
# Verification
# ============================================================
# Re-read and verify
import csv as csv_mod

with open(f"{REPO}/data/calibration.csv") as f:
    reader = csv_mod.DictReader(f)
    rows = list(reader)
    print(f"\nVerification - calibration.csv: {len(rows)} data rows")
    
    # Check difficulty distribution
    diffs = {}
    for r in rows:
        d = r["difficulty"]
        diffs[d] = diffs.get(d, 0) + 1
    print(f"  Difficulty: {diffs}")
    
    # Check IDs
    ids = [r["example_id"] for r in rows]
    print(f"  IDs: {ids[0]} to {ids[-1]}, unique={len(set(ids))}")

ak = json.load(open(f"{REPO}/data/calibration_answer_key.json"))
print(f"\nVerification - answer_key: {len(ak)} entries")
# Check all IDs match
csv_ids = set(ids)
ak_ids = set(ak.keys())
if csv_ids == ak_ids:
    print("  All IDs match between CSV and answer key ✓")
else:
    print(f"  MISMATCH! CSV-only: {csv_ids - ak_ids}, AK-only: {ak_ids - csv_ids}")

with open(f"{REPO}/data/calibration_provenance.csv") as f:
    reader = csv_mod.DictReader(f)
    prov = list(reader)
    print(f"\nVerification - provenance: {len(prov)} rows")
    prov_ids = set(r["example_id"] for r in prov)
    if csv_ids == prov_ids:
        print("  All IDs match between CSV and provenance ✓")
    else:
        print(f"  MISMATCH! CSV-only: {csv_ids - prov_ids}, Prov-only: {prov_ids - csv_ids}")

