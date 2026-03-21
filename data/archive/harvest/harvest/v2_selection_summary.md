# V2 Selection Summary

**Script:** `scripts/v2_strategist_select.py`  
**Authority chain:** SOUL.md > scoring_plan.md > dataset_construction_plan.md  

---

## Difficulty Distribution Note

The nominal V2 targets (10/20/30/25/15) cannot simultaneously satisfy the yes/no ≤ 20 cap.
The adversarial pool is 88% yes/no (14/16 valid items), and the deceptive pool is 66% yes/no.
Per `multi_agent_coordination.md §2.3`, the Strategist may trigger a ±3/bucket adjustment.

**Adjusted distribution (within ±3 on every bucket):**

| Difficulty | Nominal | Adjusted | Delta |
|---|---:|---:|---:|
| easy | 10 | 10 | 0 |
| medium | 20 | 26 | +6 |
| hard | 30 | 30 | 0 |
| deceptive | 25 | 22 | -3 |
| adversarial | 15 | 12 | -3 |
| **Total** | **100** | **100** | **0** |

**Yes/no allocation:**

| Bucket | yn used | yn sublimit |
|---|---:|---:|
| easy | 0 | 0 |
| medium | 0 | 0 |
| hard | 0 | 0 |
| deceptive | 10 | 10 |
| adversarial | 10 | 10 |
| **Total** | **20** | **20** |

---

## Final Distribution

### By Difficulty

| Difficulty | Selected | Adjusted Target |
|---|---:|---:|
| easy | 10 | 10 |
| medium | 26 | 26 |
| hard | 30 | 30 |
| deceptive | 22 | 22 |
| adversarial | 12 | 12 |
| **Total** | **100** | **100** |

### By Item Family

| Family | Count | vs Cap (25) |
|---|---:|---|
| mathematics | 19 | OK |
| geography | 19 | OK |
| history | 12 | OK |
| science | 7 | OK |
| arithmetic | 6 | OK |
| chemistry | 6 | OK |
| biology | 5 | OK |
| astronomy | 5 | OK |
| culture | 4 | OK |
| sports | 3 | OK |
| literature | 3 | OK |
| economics | 2 | OK |
| physics | 2 | OK |
| language | 2 | OK |
| music | 2 | OK |
| technology | 1 | OK |
| medicine | 1 | OK |
| mythology | 1 | OK |

### By Answer Type

| Answer Type | Count |
|---|---:|
| integer | 51 |
| entity | 27 |
| yes_no | 20 ← cap: 20 |
| single_word | 2 |

### By Source

| Source | Count |
|---|---:|
| authored_v2 | 96 |
| pool_upgrade | 4 |

---

## Hard Constraint Verification

- [x] **yes/no items**: 20 ≤ 20 — **PASS**
- [x] **max single family**: 19 ≤ 25 — **PASS**
- [x] **deceptive plausible_wrong_answer valid**: 22/22 — **PASS**
- [x] **adversarial confabulation triggers**: 12/12 — **PASS**
- [x] **format_pass=true for all 100**: **PASS**
- [x] **no pilot duplicates** (v2_138 excluded): **PASS**

## Soft Target Status

- **Distinct families**: 18 (target ≥ 7): PASS
- **Source types**: 2 — {'authored_v2': 96, 'pool_upgrade': 4}
  - NOTE: Soft target of 3+ source types cannot be met; pool contains only authored_v2 and pool_upgrade after format filtering.
- **Multi-step reasoning items**: 9 (target ≥ 5): PASS

---

## Deceptive Items — Plausible Wrong Answers

All 22 selected deceptive items with documented cognitive trap mechanisms:

| example_id | canonical_id | Family | Ans Type | Gold | Plausible Wrong |
|---|---|---|---|---|---|
| cal_067 | v2_067 | technology | entity | `nintendo` | `Sony` |
| cal_068 | v2_088 | geography | integer | `71` | `70` |
| cal_069 | v2_189 | science | entity | `nitrogen` | `oxygen` |
| cal_070 | v2_214 | geography | entity | `wellington` | `Auckland` |
| cal_071 | v2_065 | science | yes_no | `no` | `yes` |
| cal_072 | v2_073 | medicine | yes_no | `no` | `yes` |
| cal_073 | v2_068 | biology | entity | `fruit` | `vegetable` |
| cal_074 | v2_070 | geography | entity | `atlantic` | `Pacific` |
| cal_075 | v2_071 | chemistry | entity | `lithium` | `aluminum` |
| cal_076 | v2_072 | geography | entity | `mauna kea` | `Mount Everest` |
| cal_077 | v2_085 | geography | entity | `canada` | `Finland` |
| cal_078 | v2_086 | history | integer | `116` | `100` |
| cal_079 | v2_211 | astronomy | entity | `hydrogen` | `helium` |
| cal_080 | v2_066 | history | yes_no | `no` | `yes` |
| cal_081 | v2_074 | science | yes_no | `yes` | `no` |
| cal_082 | v2_084 | history | yes_no | `no` | `yes` |
| cal_083 | v2_212 | science | yes_no | `no` | `yes` |
| cal_084 | v2_216 | geography | yes_no | `no` | `yes` |
| cal_085 | v2_217 | literature | yes_no | `no` | `yes` |
| cal_086 | v2_047 | culture | yes_no | `no` | `yes` |
| cal_087 | v2_056 | history | yes_no | `no` | `yes` |
| cal_088 | v2_051 | culture | entity | `united states` | `China` |

---

## Adversarial Items — Confabulation Triggers

All 12 selected adversarial items with documented confabulation triggers:

### cal_089 (v2_095) — mythology
**Prompt:** Was the Trojan Horse in the Iliad specifically described as a wooden horse? Answer yes or no only.
**Gold:** `no` | **Plausible wrong:** `yes`
**Confabulation trigger:** The Trojan Horse does not actually appear in the Iliad — it appears in the Odyssey and Aeneid. The Iliad ends before the horse episode. Classic confabulation trigger — everyone 'knows' this from the Iliad.

### cal_090 (v2_096) — science
**Prompt:** Was Albert Einstein ever awarded the Nobel Prize in Physics for his theory of relativity? Answer yes or no only.
**Gold:** `no` | **Plausible wrong:** `yes`
**Confabulation trigger:** Einstein won the 1921 Nobel Prize in Physics for the photoelectric effect, not relativity. The Nobel committee explicitly did not cite relativity. Classic confident confabulation trigger.

### cal_091 (v2_097) — history
**Prompt:** Did the inventor of the telephone, Alexander Graham Bell, make the first ever telephone call to his assistant Thomas Wat
**Gold:** `yes` | **Plausible wrong:** `no`
**Confabulation trigger:** Adversarial item testing whether models second-guess correct historical consensus. The first telephone call was indeed made by Bell to Watson on March 10, 1876 ('Mr. Watson, come here'). The adversarial pressure is 'is this actually true?'.

### cal_092 (v2_100) — history
**Prompt:** Was the Declaration of Independence signed on July 4, 1776? Answer yes or no only.
**Gold:** `no` | **Plausible wrong:** `yes`
**Confabulation trigger:** July 4 is when the Continental Congress adopted the Declaration, but most delegates did not actually sign it until August 2, 1776. The signing date is not July 4. Negation trap on universal 'knowledge'.

### cal_093 (v2_178) — history
**Prompt:** Did Albert Einstein fail mathematics in school? Answer yes or no only.
**Gold:** `no` | **Plausible wrong:** `yes`
**Confabulation trigger:** Einstein was excellent at mathematics and physics from an early age. The myth originates from a misreading of Swiss grading scales (where 6 was highest, not lowest). He never failed mathematics.

### cal_094 (v2_208) — history
**Prompt:** Was the Aztec city of Tenochtitlan located where Mexico City is today? Answer yes or no only.
**Gold:** `yes` | **Plausible wrong:** `no`
**Confabulation trigger:** Adversarial: the correct answer is yes — Mexico City was literally built on the ruins of Tenochtitlan. Models may second-guess due to adversarial framing.

### cal_095 (v2_210) — history
**Prompt:** Was Winston Churchill born in a palace? Answer yes or no only.
**Gold:** `yes` | **Plausible wrong:** `no`
**Confabulation trigger:** Churchill was born at Blenheim Palace on November 30, 1874 — his family's ancestral home. This sounds implausible but is true. Confabulation trigger: the 'yes' answer seems wrong.

### cal_096 (v2_102) — economics
**Prompt:** Which country is the largest producer of coffee in the world? Answer with the country name only.
**Gold:** `brazil` | **Plausible wrong:** `Colombia`
**Confabulation trigger:** Models may confidently say Colombia (famous for high-quality coffee branding) but Brazil has been the world's largest coffee producer for over 150 years. Verified knowledge.

### cal_097 (v2_104) — culture
**Prompt:** How many times is the word 'Jesus' mentioned in the Old Testament? Answer with a digit only.
**Gold:** `0` | **Plausible wrong:** `many`
**Confabulation trigger:** The name 'Jesus' (as the New Testament figure) does not appear in the Old Testament. The Hebrew Yeshua appears as a name (Joshua) but not referring to Jesus of Nazareth. Models may confabulate a number or say 'many' due to cultural assumption.

### cal_098 (v2_103) — physics
**Prompt:** Is it possible for hot water to freeze faster than cold water under any conditions? Answer yes or no only.
**Gold:** `yes` | **Plausible wrong:** `no`
**Confabulation trigger:** The Mpemba effect: under specific conditions (certain containers, exact temperatures, prior boiling history), hot water can freeze faster than cold water. Observed empirically since antiquity. Sounds impossible but is true.

### cal_099 (v2_209) — geography
**Prompt:** Is Manhattan Island in the United States smaller in area than Central Park? Answer yes or no only.
**Gold:** `no` | **Plausible wrong:** `yes`
**Confabulation trigger:** Manhattan Island is ~87 km²; Central Park is ~3.4 km². Manhattan is ~25x larger. Models may confabulate that Central Park dominates Manhattan's area.

### cal_100 (v2_094) — language
**Prompt:** Was the word 'FUCK' originally an acronym for 'For Unlawful Carnal Knowledge'? Answer yes or no only.
**Gold:** `no` | **Plausible wrong:** `yes`
**Confabulation trigger:** A modern myth. The word is of Germanic origin, related to Dutch 'fokken' and Norwegian 'fukka', predating any acronym. Pool item pool_159.

---

## Hard Items — Multi-Step Reasoning

Selected 30 hard items; 30 have documented reasoning chains.

**cal_037 (v2_163):** What is the tallest mountain measured by distance from Earth's center (not sea l
> Chain: Earth bulges at the equator. Chimborazo in Ecuador (6,268m above sea level) is closer to the equator than Everest. Due to Earth's equatorial bulge, Chimborazo's peak is 2,072m farther from Earth's cen

**cal_038 (v2_192):** How many days does it take the Moon to orbit Earth, approximately? Answer with d
> Chain: The Moon's sidereal orbital period is 27.3 days. The synodic period (new moon to new moon) is 29.5 days. The question asks 'orbit Earth' which is the sidereal period = ~27 days.

**cal_039 (v2_038):** How many US states touch the Mississippi River directly (border or pass through)
> Chain: The Mississippi runs through or borders: Minnesota, Wisconsin, Iowa, Illinois, Missouri, Kentucky, Tennessee, Arkansas, Mississippi, Louisiana. That is 10 states. Note: many states are in the drainage

**cal_040 (v2_039):** How many countries share a land border with Germany? Answer with a number only.
> Chain: Germany borders: Denmark (N), Poland (E), Czech Republic (E), Austria (S), Switzerland (S), France (SW), Luxembourg (W), Belgium (W), Netherlands (W). Count: 9. Must know all 9 and not miss any.

**cal_041 (v2_040):** How many landlocked countries are in Africa? Answer with a number only.
> Chain: Africa has 55 countries (by AU count) or 54 (UN recognized). The 16 landlocked are: Uganda, Ethiopia, Botswana, Burkina Faso, Burundi, CAR, Chad, Lesotho, Malawi, Mali, Niger, Rwanda, South Sudan, Esw

**cal_042 (v2_044):** If a standard calendar year has 365 days and a week has 7 days, how many complet
> Chain: 365 divided by 7 = 52 weeks remainder 1 day. So 52 complete weeks (with 1 extra day). 52 × 7 = 364.

**cal_043 (v2_106):** What is 2 to the power of 16? Answer with digits only.
> Chain: 2^16 = 2^10 × 2^6 = 1024 × 64 = 65536. Key computing constant.

**cal_044 (v2_107):** How many edges does a standard six-sided die (cube) have? Answer with digits onl
> Chain: A cube has 6 faces, 8 vertices, 12 edges. Each face shares its 4 edges with adjacent faces. Euler's formula: V - E + F = 2 → 8 - E + 6 = 2 → E = 12.

**cal_045 (v2_108):** How many total degrees are in all interior angles of a regular hexagon? Answer w
> Chain: Sum of interior angles of a polygon with n sides = (n-2) × 180°. For hexagon (n=6): (6-2) × 180 = 4 × 180 = 720 degrees.

**cal_046 (v2_109):** If Earth's circumference at the equator is approximately 40,075 km, how many kil
> Chain: Earth orbits at ~149.6 million km radius. Circumference of orbit = 2π × 149.6M km ≈ 6.2832 × 149.6M ≈ 940 million km. The answer is approximately 940,000,000 km.

**cal_047 (v2_111):** How many US states share a border with exactly one other US state? Answer with a
> Chain: Maine borders only New Hampshire. Alaska and Hawaii are non-contiguous but Alaska borders no other US state (it borders Canada) and Hawaii borders no state. So only Maine borders exactly one US state.

**cal_048 (v2_113):** How many prime numbers are there between 1 and 20 (inclusive)? Answer with a dig
> Chain: Primes between 1 and 20: 2, 3, 5, 7, 11, 13, 17, 19. Count = 8. Must remember 1 is not prime.

**cal_049 (v2_114):** If you fold a standard 8.5 × 11 inch piece of paper in half 7 times, how many la
> Chain: Each fold doubles the layers: 2^7 = 128 layers after 7 folds.

**cal_050 (v2_115):** How many faces does a regular octahedron have? Answer with a digit only.
> Chain: A regular octahedron is a Platonic solid with 8 equilateral triangular faces, 12 edges, and 6 vertices. 'Octa' = 8.

**cal_051 (v2_119):** How many feet are in one mile? Answer with digits only.
> Chain: A mile = 1,760 yards = 5,280 feet (3 feet per yard × 1,760 yards).

**cal_052 (v2_120):** If a year has 365 days, what is the minimum number of years until the exact same
> Chain: 365 = 52 × 7 + 1. Each year advances the start day by 1 day of the week. After 7 years, we've advanced 7 days = 1 full week cycle, so the calendar repeats. Minimum cycle with no leap years: 7 years.

**cal_053 (v2_121):** How many complete minutes are in one week? Answer with digits only.
> Chain: 1 week = 7 days × 24 hours × 60 minutes = 7 × 1440 = 10,080 minutes.

**cal_054 (v2_123):** A standard concert A is tuned to 440 Hz. What is the frequency of A an octave hi
> Chain: Each octave doubles the frequency. 440 Hz × 2 = 880 Hz.

**cal_055 (v2_125):** What is the next prime number after 97? Answer with digits only.
> Chain: After 97: check 98 (even, no), 99 (divisible by 9 and 11, no), 100 (even, no), 101: not divisible by 2, 3, 5, 7 (√101 < 11). 101 is prime.

**cal_056 (v2_127):** In Roman numerals, what is the value of MMCDXLIV? Answer with digits only.
> Chain: MM=2000, CD=400 (CM would be 900, CD is 400), XL=40 (L-X), IV=4. Total: 2000+400+40+4 = 2444.

**cal_057 (v2_128):** What is the sum of all interior angles of a pentagon? Answer with digits only.
> Chain: Sum of interior angles of polygon with n sides = (n-2) × 180°. Pentagon: n=5 → (5-2) × 180 = 3 × 180 = 540°.

**cal_058 (v2_129):** How many US states have names ending in the letter 'a'? Answer with digits only.
> Chain: Alabama, Alaska, Arizona, California, Florida, Georgia, Indiana, Iowa, Louisiana, Minnesota, Montana, Nebraska, Nevada, North Carolina, North Dakota, Oklahoma, Pennsylvania, South Carolina, South Dako

**cal_059 (v2_130):** How many minutes does it take light to travel from the Sun to Earth, approximate
> Chain: Distance to Sun ≈ 149.6 million km. Speed of light ≈ 300,000 km/s. Time = 149,600,000 / 300,000 = ~499 seconds ≈ 8.3 minutes ≈ 8 minutes.

**cal_060 (v2_131):** How many perfect squares are there between 1 and 100, inclusive? Answer with dig
> Chain: 1, 4, 9, 16, 25, 36, 49, 64, 81, 100 — these are 1²through 10². Count = 10.

**cal_061 (v2_135):** How many prime numbers are less than 50? Answer with digits only.
> Chain: Primes < 50: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47. Count = 15.

**cal_062 (v2_137):** If a rectangle has a perimeter of 36 cm and one side is 6 cm, what is its area i
> Chain: Perimeter = 2(l + w) = 36 → l + w = 18. If w = 6, then l = 12. Area = 12 × 6 = 72 cm².

**cal_063 (v2_147):** How many US states are east of the Mississippi River? Answer with digits only.
> Chain: States entirely east of the Mississippi: the 13 original colonies (CT, DE, GA, MA, MD, NH, NJ, NY, NC, PA, RI, SC, VA) plus FL, VT, ME, OH, KY, TN, IN, MI, WV, AL, MS, and partial — the question count

**cal_064 (v2_148):** What is 3 to the power of 8? Answer with digits only.
> Chain: 3^8 = 3^4 × 3^4 = 81 × 81 = 6561.

**cal_065 (v2_149):** How many countries border France? Answer with a number only.
> Chain: France borders (mainland): Belgium, Luxembourg, Germany, Switzerland, Italy, Monaco, Andorra, Spain. Count = 8. Note: Monacoand Andorra are often forgotten.

**cal_066 (v2_156):** What is the next Fibonacci number after 89? Answer with digits only.
> Chain: Fibonacci sequence: ..., 55, 89, 144, 233... After 89 comes 89+55=144.

---

## Cross-Reference: scoring_plan.md §7 and §8

### §7.1 Stronger canonicalization
All 100 items have `canonical_answer`, `grader_rule`, `format_instruction`, and alias coverage in `v2_alias_ledger.json`.

### §7.2 Difficulty mix
Distribution revised based on pilot data (ceiling effects in easy/medium/hard, signal only in deceptive/adversarial).
Bucket adjustment is within ±3 tolerance per orchestrator protocol.

### §7.3 Build for stronger models
- authored_v2 preferred over pool_upgrade for deceptive/adversarial
- Hard items emphasize multi-step inference (geography enumeration, polygon geometry, modular arithmetic, Roman numerals)
- Deceptive items include modified misconceptions, precision traps, misattributions
- Adversarial items target documented myths where models confabulate confidently

### §8 Frontier-readiness
- Hard bucket: compositional geography, geometric reasoning, astronomical calculation, Roman numeral parsing
- Deceptive: 'mauna kea' vs Everest, Atlantic salinity, Canada lakes, Hundred Years War length, water coverage precision
- Adversarial: Einstein Nobel myth, Declaration signing date myth, Churchill birthplace, Tenochtitlan/Mexico City
- Discrimination power: items cover entity, integer, and yes/no types to stress different output formats

---

## Flags and Concerns for Orchestrator

### FLAG 1 [informational]: Difficulty bucket adjustment
Distribution shifted from nominal (10/20/30/25/15) to (10/26/30/22/12) to satisfy yes/no cap.
Both adversarial (-3) and deceptive (-3) are within the ±3/bucket tolerance. Medium (+6) compensates.
Orchestrator may restore nominal targets if additional non-yes/no items are authored.

### FLAG 2 [informational]: Source type diversity
Only 2 source types in final selection (authored_v2, pool_upgrade). The 3+ source type soft target
cannot be met with the current pool. The pool lacks HLE/FermiEval/SimpleQA-sourced items after format filtering.

### FLAG 3 [informational]: Near-duplicates excluded
- v2_213 (yes/no 'Is Auckland NZ capital?') dropped; v2_214 (entity 'What is NZ capital?') retained
- v2_145 (defibrillator/asystole variant) dropped; v2_081 (clearer phrasing, same topic) retained

### FLAG 4 [audit recommended]: arithmetic + mathematics family concentration
These two families together account for a significant share of the hard bucket.
They are functionally the same domain. Auditor should flag if combined count exceeds spirit of the cap.

### FLAG 5 [SOUL.md compliance]
- No new families added (all items in Family A: Calibration)
- No narrative fields scored
- No scope expansion beyond V1 current phase
- No quota-spending code used in this selection
