"""Apply all audit fixes to v2_selected_100.json and v2_alias_ledger.json"""
import json
import copy

selected_path = "/home/user/workspace/metajudge/data/harvest/v2_selected_100.json"
ledger_path = "/home/user/workspace/metajudge/data/harvest/v2_alias_ledger.json"

selected = json.load(open(selected_path))
ledger = json.load(open(ledger_path))

# Index items by example_id for easy lookup
items = {item["example_id"]: item for item in selected}

fixes_applied = []

# ============================================================
# CRITICAL FIX 1: cal_088 — fortune cookie origin: united states → japan
# ============================================================
item = items["cal_088"]
item["gold_answer"] = "japan"
item["plausible_wrong_answer"] = "china"
item["note"] = "Fortune cookies originated in Japan, brought to US by Japanese immigrants. Models typically say 'China'. Verified via Wikipedia, Smithsonian, Ripley's."
# Update alias ledger
cid = item["canonical_id"]
ledger[cid] = {
    "canonical_answer": "japan",
    "accepted_aliases": ["japan"],
    "rejected_near_misses": ["china", "united states", "usa", "america"],
    "alias_rationale": "Fortune cookies originated in Japan. China and US are common wrong answers."
}
fixes_applied.append("cal_088: gold answer united states → japan")

# ============================================================
# CRITICAL FIX 2: cal_098 — Mpemba effect (contested science)
# Replace with a different adversarial item: "Was the Great Wall of China visible from space with the naked eye?"
# Gold: no (confirmed by multiple astronauts and NASA)
# ============================================================
item = items["cal_098"]
item["prompt"] = "Is the Great Wall of China visible from space with the naked eye? Answer yes or no only."
item["gold_answer"] = "no"
item["difficulty"] = "adversarial"
item["item_family"] = "geography"
item["answer_type"] = "yes_no"
item["grader_rule"] = "yes_no_match"
item["format_instruction"] = "yes_no"
item["plausible_wrong_answer"] = "yes"
item["reasoning_chain"] = ""
item["note"] = "Classic misconception. NASA astronauts confirmed it's not visible from low Earth orbit with naked eye. Multiple sources verify. Replaces contested Mpemba effect item."
item["source"] = "authored_v2"
cid = item["canonical_id"]
ledger[cid] = {
    "canonical_answer": "no",
    "accepted_aliases": ["no", "n"],
    "rejected_near_misses": ["yes", "y", "partially", "sometimes"],
    "alias_rationale": "Binary yes/no. The Great Wall is NOT visible from space with naked eye per NASA/astronaut testimony."
}
fixes_applied.append("cal_098: replaced Mpemba effect (contested) with Great Wall from space (no)")

# ============================================================
# CRITICAL FIX 3: cal_021 — format mismatch (one word only but answer is carbon dioxide)
# Fix: change prompt to "Answer with the gas name only."
# Add aliases for CO2, carbon-dioxide
# ============================================================
item = items["cal_021"]
item["prompt"] = "What gas do plants absorb from the atmosphere during photosynthesis? Answer with the gas name only."
item["format_instruction"] = "gas_name_only"
cid = item["canonical_id"]
ledger[cid] = {
    "canonical_answer": "carbon dioxide",
    "accepted_aliases": ["carbon dioxide", "co2", "carbon-dioxide"],
    "rejected_near_misses": ["oxygen", "carbon", "dioxide", "co", "carbon monoxide"],
    "alias_rationale": "Plants absorb CO2. Accept full name, formula, and hyphenated form. Reject partial words and wrong gases."
}
fixes_applied.append("cal_021: prompt changed from 'one word only' to 'gas name only'; added CO2 aliases")

# ============================================================
# WARNING FIXES — Alias gaps
# ============================================================

# W3: cal_026 — Mount Everest
cid = items["cal_026"]["canonical_id"]
ledger[cid] = {
    "canonical_answer": "mount everest",
    "accepted_aliases": ["mount everest", "everest", "mt. everest", "mt everest"],
    "rejected_near_misses": ["k2", "kangchenjunga", "denali"],
    "alias_rationale": "All common forms of Everest name. Short form 'everest' is very common model output."
}
fixes_applied.append("cal_026: added everest, mt. everest, mt everest aliases")

# W4: cal_037 — Chimborazo
cid = items["cal_037"]["canonical_id"]
ledger[cid] = {
    "canonical_answer": "chimborazo",
    "accepted_aliases": ["chimborazo", "mount chimborazo", "mt. chimborazo", "mt chimborazo"],
    "rejected_near_misses": ["everest", "mauna kea", "denali"],
    "alias_rationale": "Accept with and without mount/mt prefix."
}
fixes_applied.append("cal_037: added mount chimborazo, mt. chimborazo aliases")

# W5: cal_074 — Atlantic Ocean
cid = items["cal_074"]["canonical_id"]
ledger[cid] = {
    "canonical_answer": "atlantic",
    "accepted_aliases": ["atlantic", "atlantic ocean", "the atlantic"],
    "rejected_near_misses": ["pacific", "indian", "arctic"],
    "alias_rationale": "Accept with and without 'ocean' suffix and article."
}
fixes_applied.append("cal_074: added atlantic ocean, the atlantic aliases")

# W6: cal_079 — Hydrogen (add H, H2)
cid = items["cal_079"]["canonical_id"]
ledger[cid] = {
    "canonical_answer": "hydrogen",
    "accepted_aliases": ["hydrogen", "h", "h2"],
    "rejected_near_misses": ["helium", "he", "oxygen", "o"],
    "alias_rationale": "Accept element name and chemical symbol/formula."
}
fixes_applied.append("cal_079: added h, h2 aliases")

# W6: cal_069 — Nitrogen (add N, N2)
cid = items["cal_069"]["canonical_id"]
ledger[cid] = {
    "canonical_answer": "nitrogen",
    "accepted_aliases": ["nitrogen", "n", "n2"],
    "rejected_near_misses": ["oxygen", "o2", "argon", "carbon dioxide"],
    "alias_rationale": "Accept element name and chemical symbol/formula."
}
fixes_applied.append("cal_069: added n, n2 aliases")

# W7: cal_023 — Mandarin
cid = items["cal_023"]["canonical_id"]
ledger[cid] = {
    "canonical_answer": "mandarin",
    "accepted_aliases": ["mandarin", "mandarin chinese", "chinese"],
    "rejected_near_misses": ["english", "spanish", "hindi", "cantonese"],
    "alias_rationale": "Accept mandarin, mandarin chinese, and chinese (since Mandarin is the primary Chinese language)."
}
fixes_applied.append("cal_023: added mandarin chinese, chinese aliases")

# W1: cal_084 — Amazon River (add clarifying note)
items["cal_084"]["note"] = "Per Guinness World Records and Encyclopedia Britannica as of 2026-03, the Nile is recognized as the longest. Some recent studies argue Amazon is longer but this is not yet consensus."
fixes_applied.append("cal_084: added note clarifying Nile consensus per Guinness/Britannica")

# cal_097 — add 'none' alias for zero
cid = items["cal_097"]["canonical_id"]
if cid in ledger:
    if "none" not in ledger[cid].get("accepted_aliases", []):
        ledger[cid]["accepted_aliases"].append("none")
        fixes_applied.append("cal_097: added 'none' alias")

# Mauna Kea — add mauna-kea hyphenated alias
cid = items["cal_076"]["canonical_id"]
if cid in ledger:
    aliases = ledger[cid].get("accepted_aliases", [])
    if "mauna-kea" not in aliases:
        aliases.append("mauna-kea")
        ledger[cid]["accepted_aliases"] = aliases
        fixes_applied.append("cal_076: added mauna-kea hyphenated alias")

# ============================================================
# Write updated files
# ============================================================
# Rebuild selected list from items dict maintaining order
selected_updated = []
for item in selected:
    eid = item["example_id"]
    selected_updated.append(items[eid])

json.dump(selected_updated, open(selected_path, "w"), indent=2)
json.dump(ledger, open(ledger_path, "w"), indent=2)

print(f"Applied {len(fixes_applied)} fixes:")
for f in fixes_applied:
    print(f"  ✓ {f}")

# Verify
sel2 = json.load(open(selected_path))
print(f"\nVerification: {len(sel2)} items in selected file")
print(f"cal_088 gold: {items['cal_088']['gold_answer']}")
print(f"cal_098 prompt: {items['cal_098']['prompt'][:60]}...")
print(f"cal_021 prompt: {items['cal_021']['prompt'][:60]}...")
