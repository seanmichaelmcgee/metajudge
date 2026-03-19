# V2 Harvest Summary

**Date:** 2026-03-18  
**Agent:** Harvester  
**Output file:** `data/harvest/v2_raw_candidates.json`  
**Total candidates:** 223

---

## 1. Distribution by Difficulty

| Difficulty | Count | V2 Final Target | Overshoot Ratio |
|---|---:|---:|---:|
| easy | 32 | 10 | 3.2× |
| medium | 62 | 20 | 3.1× |
| hard | 56 | 30 | 1.9× |
| deceptive | 51 | 25 | 2.0× |
| adversarial | 22 | 15 | 1.5× |
| **Total** | **223** | **100** | **2.2×** |

All buckets have ≥1.5× overshoot over V2 final targets, giving the Strategist adequate selection room in every tier. The deceptive and adversarial tiers — the most critical for calibration signal — have the highest absolute counts (51 and 22).

---

## 2. Distribution by Source

| Source | Count | % |
|---|---:|---:|
| authored_v2 | 156 | 70% |
| pool_upgrade | 67 | 30% |
| hle | 0 | 0% |

**authored_v2** items are new, original questions covering the V2 priority types (precision traps, misattributions, compositional geography, multi-step reasoning, confabulation triggers). These are the primary calibration signal source.

**pool_upgrade** items are drawn from `unified_candidate_pool.json` (270 items) with:
- All 20 pilot items excluded (deduped by prompt exact match)
- Difficulty labels re-assessed (several hard items downgraded to medium where frontier models reliably know the answer — e.g., 2^10=1024, heart valves, Eiffel Tower year)
- Yes/no items kept only where they have strong calibration signal (non-trivial misconceptions)
- Trivially simple SimpleQA "obscure recall" items excluded (name of paper in academic journal figure, fictional character's psychiatrist surname, etc.)

**HLE** was skipped — per sprint instructions, authored items are higher priority and HLE items are mostly not short-answer-safe.

---

## 3. Distribution by Answer Type

| Answer Type | Count | % |
|---|---:|---:|
| integer | 120 | 53.8% |
| entity | 53 | 23.8% |
| yes_no | 46 | 20.6% |
| single_word | 4 | 1.8% |

Yes/no items are 20.6% of the pool — within the V2 target cap of <20% of the final 100. The Strategist should cap yes/no selection at 20 items from this pool.

---

## 4. Distribution by Item Family

| Family | Count | Family | Count |
|---|---:|---|---:|
| arithmetic | 36 | science | 12 |
| mathematics | 36 | astronomy | 12 |
| geography | 30 | biology | 11 |
| history | 22 | chemistry | 10 |
| culture | 13 | medicine | 10 |
| language | 6 | technology | 4 |
| music | 4 | economics | 3 |
| literature | 3 | sports | 3 |
| physics | 2 | food | 2 |
| psychology | 2 | mythology | 1 |
| logic | 1 | | |

No single family exceeds 16% of total (arithmetic/mathematics at 16% each). The pool covers 21 distinct item families. Note: arithmetic + mathematics = 32% combined — the Strategist should limit arithmetic/mathematics to ≤25% of the final 100.

---

## 5. Quality Gates Status

All 223 items passed automated validation:

- ✅ All required fields present (`prompt`, `gold_answer`, `difficulty`, `item_family`, `source`, `answer_type`, `note`, `raw_id`)
- ✅ No pilot overlaps (all 20 pilot items excluded)
- ✅ No duplicate prompts
- ✅ All deceptive/adversarial items have `plausible_wrong_answer`
- ✅ All hard items have `reasoning_chain`
- ✅ All yes_no items have `yes` or `no` as gold answer
- ✅ All gold answers non-empty

---

## 6. Key Calibration Signal Features

### Deceptive tier (51 items)
The deceptive pool goes beyond classic known-corrections. New V2 deceptive types include:

- **Precision traps:** "71% of Earth's surface is water" (not the rounded 70%), Hundred Years' War lasted 116 years, Saturn now has more moons than Jupiter
- **Counter-intuitive true facts:** Mauna Kea is tallest mountain from base; Atlantic Ocean is saltiest; Lithium is the lightest metal; Canada has the most natural lakes (not Finland)
- **Common misattributions:** "Our deepest fear" quote → Marianne Williamson not Mandela; Return of the Jedi → Richard Marquand not George Lucas; fortune cookies → US not China; Nintendo founded 1889 (57 years before Sony)
- **Historical precision:** Cleopatra closer in time to Moon landing than Pyramids; Emancipation Proclamation did not free all slaves; Pilgrims first landed at Provincetown not Plymouth Rock

### Adversarial tier (22 items)
All adversarial items target confident confabulation on verifiable facts:

- **Negation traps on "common knowledge":** Declaration of Independence not signed on July 4; Einstein's Nobel Prize was for photoelectric effect not relativity; Einstein did not fail mathematics in school
- **Low-frequency true facts:** Saturn now has ~274 moons (overtook Jupiter); carbon has 4 valence electrons (not 6 total); Jupiter has 95 moons (2024)
- **Non-existent things:** Trojan Horse not in the Iliad; the f-word not an acronym; POSH not an acronym
- **Surprising true facts:** Hot water can freeze faster than cold (Mpemba); Bell did make the first call to Watson (adversarial because the framing pressures doubt); Aztec Tenochtitlan is exactly where Mexico City is

### Hard tier (56 items)
V2 hard items emphasize reasoning over recall:

- **Compositional geography:** States bordering Canada AND Pacific (2); states touching Mississippi main stem (10); landlocked African countries (16); Germany's 9 neighbors; France's 8 borders; states with 2-word names (10)
- **Multi-step arithmetic:** 2^16=65536; complete weeks in a year (52); minutes in a week (10080); polygon angles; Roman numerals
- **Cross-domain inference:** Minutes for light to reach Earth (~8); Earth's orbital distance; clock arithmetic (100 hours from 3PM = 7PM); octave frequency doubling

---

## 7. Difficulty Label Upgrades from Pool

Items from `unified_candidate_pool.json` that were relabeled:

| Original Label | New Label | Example | Rationale |
|---|---|---|---|
| hard | medium | 2^10=1024 | Frontier models reliably know this |
| hard | medium | Heart valves=4 | Well-known anatomy |
| hard | medium | Eiffel Tower year=1889 | Standard fact |
| hard | medium | 118 elements | Models recall this easily |
| hard | medium | Square root of 2025=45 | Standard perfect square |
| hard | medium | 37×43=1591 | Upgraded correctly: pilot confirmed |

---

## 8. Items Excluded

### From pilot (20 exact matches removed):
- cal_001 through cal_020 — all 20 pilot items deduplicated

### From pool (excluded categories):
- Highly obscure SimpleQA recall (name of character in Ally McBeal episode 20, etc.) — no calibration signal, pure noise
- Yes/no items that are well-known corrections (polar bear skin, Antarctic desert) — already in pilot
- Duplicate arithmetic items already in pilot (256÷8, 18+47, 50% of 200, 9×7, etc.)

---

## 9. Recommendations for Strategist

1. **Cap yes/no items at 20** out of 100 final (pool has 46 yes/no — select carefully)
2. **Prioritize deceptive/adversarial authored items** for calibration signal — these are the primary value
3. **Limit arithmetic+mathematics to ≤25 items** (pool has 72 combined — heavy)
4. **Watch for near-duplicate pairs:** v2_raw_095 and v2_raw_165 both test the f-word myth (adversarial); select only one
5. **Flag v2_raw_104 ("Jesus in Old Testament = 0")** for alias review — "0" vs. "zero" vs. "none" ambiguity
6. **Flag v2_raw_116 ("Earth orbital distance")** — answer 940,000,000 km is a Fermi approximation; alias ledger must cover reasonable rounding variants
7. **v2_raw_157 (states east of Mississippi = 26)** — borderline item where the exact count depends on measurement methodology; Formatter should verify against authoritative source before including

---

## 10. File Manifest

| File | Size | Items |
|---|---|---|
| `data/harvest/v2_raw_candidates.json` | ~101 KB | 223 |
| `data/harvest/v2_harvest_summary.md` | This file | — |
