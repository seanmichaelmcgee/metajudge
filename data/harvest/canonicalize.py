"""
Canonicalization pipeline for MetaJudge-AGI calibration dataset.
Reads all harvested candidates, applies exact-match filters,
normalizes answers, assigns IDs, and produces:
  1. Unified candidate pool (all items with standardized schema)
  2. 20-item pilot CSV (data/calibration.csv)
  3. Answer key JSON (data/calibration_answer_key.json)
  4. Provenance CSV (data/calibration_provenance.csv)
"""

import json
import csv
import re
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path("/home/user/workspace/metajudge-agi/data")
HARVEST_DIR = DATA_DIR / "harvest"

# ---------------------------------------------------------------------------
# Load all candidates
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path) as f:
        return json.load(f)

simpleqa = load_json(HARVEST_DIR / "simpleqa_candidates.json")
truthfulqa = load_json(HARVEST_DIR / "truthfulqa_candidates.json")
authored = load_json(HARVEST_DIR / "authored_candidates.json")

print(f"Loaded: SimpleQA={len(simpleqa)}, TruthfulQA={len(truthfulqa)}, Authored={len(authored)}")

# ---------------------------------------------------------------------------
# Normalize to unified schema
# ---------------------------------------------------------------------------

def normalize_text(x):
    if x is None:
        return None
    return " ".join(str(x).strip().lower().split())

def token_count(s):
    return len(s.split())

def has_punctuation_dependency(answer):
    """Check if answer relies on punctuation for meaning."""
    stripped = re.sub(r'[^\w\s]', '', answer)
    return normalize_text(stripped) != normalize_text(answer) and len(stripped) > 0

def is_time_sensitive(prompt):
    """Basic check for time-sensitive questions."""
    patterns = [r'\bcurrent\b', r'\btoday\b', r'\bnow\b', r'\brecent\b', 
                r'\blatest\b', r'\b202[4-6]\b', r'\bpresident of\b']
    return any(re.search(p, prompt, re.IGNORECASE) for p in patterns)

unified = []
reject_reasons = {}

def reject(reason):
    reject_reasons[reason] = reject_reasons.get(reason, 0) + 1

# Process SimpleQA
for i, item in enumerate(simpleqa):
    gold = normalize_text(item["gold_answer"])
    prompt = item["prompt"]
    
    if gold is None or len(gold) == 0:
        reject("empty_answer"); continue
    if token_count(gold) > 5:
        reject("answer_too_long"); continue
    if is_time_sensitive(prompt):
        reject("time_sensitive"); continue
    
    # Ensure prompt has format instruction
    if not any(prompt.rstrip().endswith(s) for s in [".", "?", "!"]):
        prompt = prompt.rstrip() + "."
    if "answer with" not in prompt.lower() and "give" not in prompt.lower():
        prompt = prompt.rstrip() + " Answer in as few words as possible."
    
    aliases = item.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    aliases = [normalize_text(a) for a in aliases if a]
    if gold not in aliases:
        aliases.insert(0, gold)
    
    unified.append({
        "prompt": prompt,
        "gold_answer": gold,
        "aliases": aliases,
        "difficulty": item.get("difficulty", "medium"),
        "item_family": item.get("item_family", "factual_recall"),
        "source": "simpleqa",
        "note": item.get("note", ""),
        "answer_type": "entity" if not gold.replace(".", "").replace("-", "").isdigit() else "integer",
    })

# Process TruthfulQA
for item in truthfulqa:
    gold = normalize_text(item["gold_answer"])
    prompt = item["prompt"]
    
    if gold is None or len(gold) == 0:
        reject("empty_answer"); continue
    if token_count(gold) > 5:
        reject("answer_too_long"); continue
    
    aliases = item.get("gold_aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    aliases = [normalize_text(a) for a in aliases if a]
    if gold not in aliases:
        aliases.insert(0, gold)
    
    # Determine answer type
    answer_type = "entity"
    if gold in ("yes", "no", "true", "false"):
        answer_type = "yes_no"
    elif gold.replace(".", "").replace("-", "").isdigit():
        answer_type = "integer"
    
    unified.append({
        "prompt": prompt,
        "gold_answer": gold,
        "aliases": aliases,
        "difficulty": "deceptive",
        "item_family": item.get("item_family", "misconception"),
        "source": "truthfulqa_rewritten",
        "note": item.get("misconception", ""),
        "common_wrong_answer": item.get("common_wrong_answer", ""),
        "answer_type": answer_type,
    })

# Process Authored
for item in authored:
    gold = normalize_text(item["gold_answer"])
    prompt = item["prompt"]
    
    if gold is None or len(gold) == 0:
        reject("empty_answer"); continue
    
    aliases = item.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    aliases = [normalize_text(a) for a in aliases if a]
    if gold not in aliases:
        aliases.insert(0, gold)
    
    answer_type = "integer" if gold.replace(".", "").replace("-", "").isdigit() else "entity"
    
    unified.append({
        "prompt": prompt,
        "gold_answer": gold,
        "aliases": aliases,
        "difficulty": item.get("difficulty", "medium"),
        "item_family": item.get("item_family", "arithmetic"),
        "source": "authored",
        "note": item.get("note", ""),
        "answer_type": answer_type,
    })

print(f"Unified pool: {len(unified)} items")
print(f"Rejected: {sum(reject_reasons.values())} items")
for reason, count in sorted(reject_reasons.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}")

# ---------------------------------------------------------------------------
# Difficulty distribution check
# ---------------------------------------------------------------------------

diff_counts = {}
for item in unified:
    d = item["difficulty"]
    diff_counts[d] = diff_counts.get(d, 0) + 1

print(f"\nDifficulty distribution:")
for d in ["easy", "medium", "hard", "deceptive", "adversarial"]:
    print(f"  {d}: {diff_counts.get(d, 0)}")

# ---------------------------------------------------------------------------
# Build 20-item pilot set
# ---------------------------------------------------------------------------

# Target: 4 easy, 7 medium, 5 hard, 3 deceptive, 1 adversarial
pilot_targets = {"easy": 4, "medium": 7, "hard": 5, "deceptive": 3, "adversarial": 1}

# Group by difficulty
by_diff = {}
for item in unified:
    d = item["difficulty"]
    if d not in by_diff:
        by_diff[d] = []
    by_diff[d].append(item)

# Sample pilot items with domain diversity
pilot_items = []
for diff, count in pilot_targets.items():
    pool = by_diff.get(diff, [])
    if len(pool) < count:
        print(f"  WARNING: only {len(pool)} items for difficulty={diff}, need {count}")
        selected = pool
    else:
        # Try for domain diversity
        random.shuffle(pool)
        seen_families = set()
        diverse_first = []
        rest = []
        for item in pool:
            if item["item_family"] not in seen_families:
                diverse_first.append(item)
                seen_families.add(item["item_family"])
            else:
                rest.append(item)
        candidates = diverse_first + rest
        selected = candidates[:count]
    pilot_items.extend(selected)

# Assign example_ids
for i, item in enumerate(pilot_items):
    item["example_id"] = f"cal_{i+1:03d}"

print(f"\nPilot set: {len(pilot_items)} items")
for item in pilot_items:
    print(f"  {item['example_id']}: [{item['difficulty']}] [{item['item_family']}] "
          f"gold={item['gold_answer']!r} source={item['source']}")

# ---------------------------------------------------------------------------
# Write pilot CSV
# ---------------------------------------------------------------------------

csv_path = DATA_DIR / "calibration.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["example_id", "prompt", "gold_answer", "difficulty"])
    writer.writeheader()
    for item in pilot_items:
        writer.writerow({
            "example_id": item["example_id"],
            "prompt": item["prompt"],
            "gold_answer": item["gold_answer"],
            "difficulty": item["difficulty"],
        })
print(f"\nWrote: {csv_path}")

# ---------------------------------------------------------------------------
# Write answer key JSON
# ---------------------------------------------------------------------------

answer_key = {}
for item in pilot_items:
    grader_rule = "alias_match"
    if item["answer_type"] in ("integer", "decimal"):
        grader_rule = "numeric_equivalence"
    elif item["answer_type"] == "yes_no":
        grader_rule = "yes_no_normalization"
    
    answer_key[item["example_id"]] = {
        "canonical_answer": item["gold_answer"],
        "accepted_aliases": item["aliases"],
        "answer_type": item["answer_type"],
        "format_instruction": "bare_value",
        "grader_rule": grader_rule,
        "notes": item.get("note", ""),
    }

key_path = DATA_DIR / "calibration_answer_key.json"
with open(key_path, "w") as f:
    json.dump(answer_key, f, indent=2)
print(f"Wrote: {key_path}")

# ---------------------------------------------------------------------------
# Write provenance CSV
# ---------------------------------------------------------------------------

prov_path = DATA_DIR / "calibration_provenance.csv"
with open(prov_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "example_id", "source", "item_family", "difficulty", 
        "gold_answer", "answer_type", "aliases", "note"
    ])
    writer.writeheader()
    for item in pilot_items:
        writer.writerow({
            "example_id": item["example_id"],
            "source": item["source"],
            "item_family": item["item_family"],
            "difficulty": item["difficulty"],
            "gold_answer": item["gold_answer"],
            "answer_type": item["answer_type"],
            "aliases": "|".join(item["aliases"]),
            "note": item.get("note", ""),
        })
print(f"Wrote: {prov_path}")

# ---------------------------------------------------------------------------
# Save full unified pool for later expansion to 100 items
# ---------------------------------------------------------------------------

# Assign IDs to all items in the pool
for i, item in enumerate(unified):
    if "example_id" not in item:
        item["example_id"] = f"pool_{i+1:03d}"

pool_path = HARVEST_DIR / "unified_candidate_pool.json"
with open(pool_path, "w") as f:
    json.dump(unified, f, indent=2)
print(f"Wrote: {pool_path} ({len(unified)} items)")

print("\n✓ Canonicalization complete.")
