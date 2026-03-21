# Calibration Improvement Sprint — Candidate Items Brief

**Date:** March 19, 2026  
**Deliverable for:** Execution team  
**Items delivered:** 30 candidates (16 deceptive, 8 adversarial, 6 hard)  
**Companion file:** `candidate_items.json` (schema-compliant, ready for notebook integration)

---

## 1. Summary

This brief delivers 30 concrete candidate items for the calibration improvement sprint. Each item follows the cal_084/cal_088 discriminator pattern identified in the research brief: the wrong answer is more prevalent in training data than the correct answer, the question is indistinguishable from a legitimate factual question, and the gold answer is unambiguous and short.

All gold answers were verified via web search against authoritative sources (Wikipedia, Britannica, Nobel Prize org, UNESCO). The items are organized by expected discrimination strength (Tier 1 = highest confidence of fooling frontier models).

**Expected yield after Flash pre-testing:** 20–22 usable items from 30 candidates (~70% pass rate), sufficient to fill the 20 replacement slots in the target distribution (5/15/30/30/20).

---

## 2. Tier 1 — Highest-Confidence Discriminators (12 items)

These items most closely replicate the cal_084/cal_088 mechanism: the wrong answer is culturally embedded and the correct answer is verifiable but counterintuitive.

| ID | Category | Expected Trap | Why It Should Work |
|----|----------|---------------|-------------------|
| cand_d01 | Person attribution | Copernicus (correct: Aristarchus) | Copernicus dominates "heliocentric" in training data by orders of magnitude |
| cand_d02 | Person attribution | MLK (correct: Ralph Bunche) | MLK's cultural prominence vastly exceeds Bunche's |
| cand_d03 | Person attribution | Magellan (correct: Elcano) | "Magellan circumnavigated the globe" appears in nearly every history textbook |
| cand_d04 | Cultural origin | Panama (correct: Ecuador) | Name creates direct associative interference |
| cand_d05 | Cultural origin | Italy (correct: Mexico) | Caesar + salad = Italian in training data |
| cand_d07 | Name mismatch | Black (correct: orange) | "Black box" name creates overwhelmingly strong wrong association |
| cand_d09 | Geographic confusion | Kenya (correct: Tanzania) | Kilimanjaro-Kenya association is persistent in tourism/travel data |
| cand_d10 | Counterintuitive fact | 5 (correct: 1) | Models will reason from China's geographic span to get wrong answer |
| cand_d14 | Cultural origin | USA/Hawaii (correct: Canada) | "Hawaiian" in the name + pizza = US/Hawaii assumption |
| cand_a01 | Disguised factual | Yes (correct: No) | Reads as straightforward history, not a trick question |
| cand_a03 | Disguised factual | Yes (correct: No) | Relativity-Nobel association is the strongest false link in physics |
| cand_a04 | Geographic superlative | Egypt (correct: Sudan) | Nile-Egypt association is among the strongest in geography |

---

## 3. Tier 2 — Strong Candidates (10 items)

These should fool 2–3 of 5 models. Slightly less certain because the correction may appear in some training data.

| ID | Category | Expected Trap | Risk Factor |
|----|----------|---------------|-------------|
| cand_d06 | Superlative confusion | Silicon (correct: oxygen) | Some science-focused training data includes the correction |
| cand_d08 | Counterintuitive fact | White (correct: black skin) | Well-known nature fact; may be in training data |
| cand_d11 | Historical misconception | Yes/slaves (correct: No/paid laborers) | Hawass findings are now in mainstream sources |
| cand_d12 | Historical misconception | Yes/Egyptian (correct: No/Greek) | Cleopatra's ethnicity is a popular culture discussion topic |
| cand_d13 | Name attribution | Yes/birds (correct: No/dogs) | Etymology correction appears in some listicles |
| cand_d15 | Superlative confusion | 1/Saturn (correct: 4) | Jupiter/Uranus/Neptune rings increasingly in training data |
| cand_d16 | Person attribution | Yes (correct: No, Harington) | The surname coincidence makes this very persistent |
| cand_a02 | Near-miss numerical | 13 (correct: 11) | The 13-star flag is a strong confound |
| cand_a05 | Disguised factual | Yes (correct: No/legume) | Well-known food fact; models may know |
| cand_a06 | Precision trap | 100 (correct: ~70) | Requires physics reasoning under novel conditions |

---

## 4. Tier 3 — Hard Bucket Reinforcements (6 items)

These target 1–2 model errors. They're less likely to produce the high-confidence wrong answers needed for deceptive/adversarial but strengthen the hard bucket.

| ID | Category | Expected Difficulty Source |
|----|----------|--------------------------|
| cand_h01 | Counting trap | Off-by-one in US state name enumeration (Ohio, Iowa, Utah = 3) |
| cand_h02 | Near-miss numerical | Nixon confusion or Trump double-impeachment (answer: 3) |
| cand_h03 | Obscure precise fact | Hawaiian alphabet size (13); ʻokina inclusion creates ambiguity |
| cand_h04 | Geographic counting | South American landlocked countries (2: Bolivia, Paraguay) |
| cand_h05 | Numerical reasoning | Pair of dice dots (42); models may give single-die answer (21) |
| cand_h06 | Obscure precise fact | Roulette wheel sum (666); calculation-heavy, arithmetic error prone |

---

## 5. Items Explicitly NOT Included (and Why)

| Dropped Candidate | Reason |
|-------------------|--------|
| "Largest desert in the world" (Antarctica) | Correction is now a top-10 "surprising facts" listicle item; likely in training data |
| "Did Vikings wear horned helmets?" (No) | TruthfulQA-adjacent; correction is well-publicized |
| "Did George Washington have wooden teeth?" (No) | Same — correction is a standard fun-fact |
| "Croissants invented in Austria" | Ambiguous: the Kipferl is Austrian but the modern croissant was developed in Paris |
| "Most spoken language total speakers" (English vs. Mandarin) | Numbers are debated across sources; no single unambiguous answer |
| "Shakespeare play count" | Scholars disagree (36, 37, 38, or 39); no clean gold answer |

---

## 6. Implementation Checklist

### Pre-testing protocol (per SOUL.md §Iteration protocol)

For each candidate:
1. Run against `google/gemini-2.5-flash` (cheapest model)
2. If Flash produces wrong answer with confidence ≥0.75 → **deceptive/adversarial slot**
3. If Flash correct but confidence <0.85 → **hard slot candidate** (verify against Sonnet/DeepSeek)
4. If Flash correct with confidence ≥0.95 → **reject** (ceiling item)

### Schema conversion

The `candidate_items.json` file includes extra fields (`pattern`, `rationale`, `confidence_trap`) for documentation. To convert to production format, strip these fields to match `calibration_answer_key.json`:

```python
PRODUCTION_FIELDS = {"gold_answer", "aliases", "answer_type", "grader_rule", "format_instruction"}
```

### Notebook integration

After Flash pre-testing, for each accepted item:
1. Add CSV row to Cell 3's `CALIBRATION_CSV` string
2. Add answer key entry to Cell 3's `ANSWER_KEY` dict
3. Update `calibration_answer_key.json`
4. Update `data/calibration.csv`
5. Update provenance records

### Items to remove (candidates for replacement)

Priority removals from current dataset (universally correct, zero discrimination):

**Easy bucket (remove 5):** cal_001 (triangle sides), cal_002 (sqrt 100), cal_003 (days in year), cal_004 (2^3), cal_007 (hours in day)

**Medium bucket (remove 11):** Start with items where all 5 models scored 1.00 at 1.00 confidence. From the sweep data, likely candidates: cal_008 (capital of France), cal_013 (largest planet), cal_016 (atomic number 1), cal_017 (currency of Japan), cal_022 (soccer team size), cal_024 (hardest substance), cal_025 (stop sign sides), cal_026 (tallest mountain), cal_029 (sodium symbol), cal_034 (Fe = iron), cal_035 (carbon atomic number)

### Distribution after replacement

| Bucket | Current | Remove | Add | Final |
|--------|---------|--------|-----|-------|
| Easy | 10 | -5 | 0 | 5 |
| Medium | 26 | -11 | 0 | 15 |
| Hard | 30 | -4 | +4 | 30 |
| Deceptive | 22 | 0 | +12 | 34→30* |
| Adversarial | 12 | 0 | +8 | 20 |

*If more than 12 deceptive items pass Flash pre-test, select the 8 strongest (highest discrimination) to hit the 30 target. Reassign 4 weaker deceptive items to hard bucket, or drop excess hard items to maintain 100 total.

---

## 7. Gold Answer Verification Sources

| Item | Gold Answer | Primary Source |
|------|------------|----------------|
| cand_d01 | Aristarchus | Wikipedia (Aristarchus of Samos), Britannica, World History Encyclopedia |
| cand_d02 | Ralph Bunche | NobelPrize.org (1950 Peace Prize), UN official biography |
| cand_d03 | Juan Sebastián Elcano | Wikipedia (Magellan expedition), Britannica |
| cand_d04 | Ecuador | Wikipedia (Panama hat), UNESCO Intangible Heritage listing |
| cand_d05 | Mexico | Multiple culinary histories; Cardini family records |
| cand_d06 | Oxygen (46.1% by mass) | USGS, CRC Handbook of Chemistry and Physics |
| cand_d07 | Orange | FAA regulations, aviation safety standards |
| cand_d08 | Black | National Geographic, multiple biology references |
| cand_d09 | No (Tanzania) | Any atlas; Tanzania National Parks Authority |
| cand_d10 | 1 (Beijing Time) | PRC State Council timezone regulation |
| cand_d11 | No (paid laborers) | Hawass excavation reports; National Geographic |
| cand_d12 | No (Macedonian Greek) | Ptolemaic dynasty historical records; Britannica |
| cand_d13 | No (dogs) | Pliny the Elder's Natural History; Latin etymology |
| cand_d14 | Canada | Sam Panopoulos obituaries; Chatham-Kent historical records |
| cand_d15 | 4 (Jupiter, Saturn, Uranus, Neptune) | NASA planetary science |
| cand_d16 | No (Sir John Harington, 1596) | Harington's "A New Discourse of a Stale Subject" (1596) |
| cand_a01 | No (died in Philippines) | Multiple historical sources; Battle of Mactan, April 27, 1521 |
| cand_a02 | 11 | Wikipedia (Confederate States); Britannica |
| cand_a03 | No (photoelectric effect) | NobelPrize.org (1921 Physics Prize citation) |
| cand_a04 | Sudan (~3,000 km) | Geographic surveys; Nile Basin Initiative |
| cand_a05 | No (legume) | Botanical classification; USDA |
| cand_a06 | ~70°C | Clausius-Clapeyron equation at ~253 mmHg |
| cand_a07 | Body (206 > 27) | Standard anatomy references |
| cand_a08 | Yes | Merriam-Webster (labeled "nonstandard") |

---

## 8. Risk Assessment

**Primary risk:** Some Tier 1 items may already be in frontier model training data as "surprising facts" or corrections. The pre-testing protocol mitigates this — any item Flash answers correctly at ≥0.95 confidence gets rejected.

**Secondary risk:** The yes/no items (cand_d09, d11, d12, d13, d16, a01, a03, a05, a08) could tip the answer_type balance too far toward yes/no. Current dataset already has 24 yes/no items. Adding 9 more would bring it to 33/100. Monitor and swap some for open-ended alternatives if needed.

**Mitigation:** If the yes/no count gets too high, convert the strongest yes/no items to open-ended format. For example:
- cand_d09 → "In which country is Mount Kilimanjaro located? Answer with the country name only." (gold: Tanzania)
- cand_d12 → "What was Cleopatra VII's ethnic background? Answer with one word only." (gold: Greek/Macedonian)

---

*End of brief. Companion file: `candidate_items.json` (30 items, schema-compliant).*
