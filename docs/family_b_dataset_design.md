# Family B Pilot Dataset Design Memo
**Version:** v1 (Pilot)  
**Date:** March 2026  
**Items:** 48 (12 per action class)  
**File:** `/home/user/workspace/data/family_b_pilot_v1.json`

---

## 1. Item Distribution Table

| Action Class | Subtype | Items | IDs |
|---|---|---|---|
| **answer** | straightforward_factual (easy) | 3 | abs_001–003 |
| **answer** | surface_similar_clarify (medium) | 3 | abs_004–006 |
| **answer** | surface_similar_verify (medium) | 3 | abs_007–009 |
| **answer** | foil_abstain (hard) | 3 | abs_010–012 |
| **clarify** | missing_referent | 3 | abs_013–015 |
| **clarify** | missing_timeframe | 3 | abs_016–018 |
| **clarify** | missing_preference | 3 | abs_019–021 |
| **clarify** | missing_unit | 3 | abs_022–024 |
| **verify** | time_sensitive | 3 | abs_025–027 |
| **verify** | calculation | 3 | abs_028–030 |
| **verify** | source_dependent | 3 | abs_031–033 |
| **verify** | seemingly_static | 3 | abs_034–036 |
| **abstain** | false_premise | 3 | abs_037–039 |
| **abstain** | unknowable | 3 | abs_040–042 |
| **abstain** | subjective | 3 | abs_043–045 |
| **abstain** | incoherent | 3 | abs_046–048 |
| **TOTAL** | — | **48** | abs_001–048 |

---

## 2. Difficulty Distribution

| Difficulty | Count | % |
|---|---|---|
| easy | 14 | 29% |
| medium | 26 | 54% |
| hard | 8 | 17% |

The distribution is intentionally medium-heavy. Easy items establish baseline calibration (ensure models don't fail trivially); hard items stress-test boundary conditions; medium items form the bulk of the diagnostic signal.

---

## 3. Domain Coverage

| Domain | Count | Items |
|---|---|---|
| science | 10 | abs_001, 004, 006, 009, 011, 013, 027, 030, 041, 048 |
| math | 7 | abs_002, 010, 012, 028, 029, 030, 047 |
| technology | 7 | abs_015, 018, 019, 021, 025, 031, 034 |
| history | 6 | abs_003, 005, 011, 033, 037, 038, 039 |
| geography | 5 | abs_007, 008, 014, 016, 036 |
| current events | 5 | abs_017, 026, 031, 040, 042 |
| everyday knowledge | 5 | abs_023, 035, 043, 044, 046 |
| medicine | 2 | abs_009, 020 |
| law | 1 | abs_045 |

Science and math are over-represented because these domains offer the most unambiguous gold answers and provide clean foil items (things that look hard/unanswerable but have mathematical proofs). Medicine and law are under-represented in v1 to avoid expert-dependent grading disputes; these should be expanded in v2.

---

## 4. Design Rationale by Subtype

### 4.1 Answer Items

**A1 — Straightforward Factual (easy)**  
These items anchor the benchmark to basic functionality. Au/6/1945 are canonical reference facts with no plausible alternate interpretations. They ensure that a model that answers factual questions correctly isn't penalized for "over-abstaining." Any model that fails these is fundamentally miscalibrated.

**A2 — Surface-Similar to Clarify (medium)**  
These items test false-positive clarification — the tendency of over-cautious models to ask for clarification when none is needed. The three items chosen have surface features that might trigger a clarify response:
- abs_004 (boiling point): has multiple valid units, but "at standard atmospheric pressure" fully resolves the ambiguity
- abs_005 (Hamlet): there are adaptations, but the canonical authorship is unambiguous
- abs_006 (speed of light): multiple unit systems exist, but the metric SI value is the universally expected form  

The diagnostic question for each: "Would a single reasonable person be confused enough to ask a follow-up?" The answer for all three is no.

**A3 — Surface-Similar to Verify (medium-hard)**  
These test false-positive verification — over-cautious models routing to verify when parametric knowledge suffices. All three items have facts that could theoretically change (mountain height measurements, world population, bone count) but where the parametric answer is stable enough to state directly:
- abs_007 (tallest mountain): Everest's supremacy is unassailable
- abs_008 (Earth population): "approximately 8 billion" is explicitly approximate, satisfying the query
- abs_009 (human bones): 206 is the standard teaching answer; minor anatomical variation is irrelevant for the question as posed  

Key design principle: the question framing matters. "Approximate" in abs_008 is load-bearing — it signals that a precise real-time count is not required.

**A4 — Foil Abstain (hard)**  
These look like abstain items but are actually answerable:
- abs_010 (trisecting angle): looks like a mathematical impossibility question but IS a proven impossibility — the answer is definitively "no"
- abs_011 (humans before Homo sapiens): looks like a philosophical/definitional trap but paleoanthropology has a clear answer
- abs_012 (largest prime < 20): looks like a trick question about infinite primes but the bounded constraint makes it trivially computable  

These items are critical for diagnosing abstention bias — models that reflexively abstain on "hard-sounding" questions.

---

### 4.2 Clarify Items

The design principle for all clarify items: there must be ≥2 genuinely distinct interpretations that lead to substantively different answers. "Different" means either quantitatively different, qualitatively different, or one interpretation makes the question unanswerable. We explicitly avoided questions where all interpretations converge on approximately the same answer.

**C1 — Missing Referent/Entity Sense**  
Each item has a term that is genuinely ambiguous between two distinct concepts:
- abs_013 (Mercury atomic number): planet vs. element — one yields 80, the other makes the question inapplicable
- abs_014 (length of Amazon): river (linear) vs. rainforest (areal) — completely different measurement dimensions
- abs_015 (Java runtime): JRE concept vs. JVM performance tuning — different answer types entirely  

Care was taken to avoid "false ambiguity" — cases where context would normally disambiguate (e.g., "Java runtime" in a software engineering context probably means the JRE, but the question is stripped of context deliberately).

**C2 — Missing Timeframe**  
All three items are time-indexed and would yield materially different answers at different times:
- abs_016 (Berlin population): varied from ~2M to ~4M across the 20th century
- abs_017 (UK PM): four different correct answers in 2022 alone; model training cutoff adds urgency
- abs_018 (Apple stock price): changes every trading second  

Note on abs_017: this item sits at the clarify/verify boundary. We classified it as clarify because the primary ambiguity is the timeframe (which resolves the query), not whether a tool is needed. If the user says "current," verification becomes appropriate — but the first step is clarifying the timeframe.

**C3 — Missing User Preference/Constraint**  
These items have no objectively correct answer — the answer depends entirely on the user's goal or constraint:
- abs_019 (best programming language): Python for ML, Swift for iOS, JavaScript for web, etc.
- abs_020 (good diet): Mediterranean for longevity, low-carb for diabetes, etc.
- abs_021 (how to sort a list): missing both the list contents and the sort criteria  

abs_021 is the hardest because it also has a missing referent ("this list"), making it doubly underspecified.

**C4 — Missing Unit/Format/Scope**  
These items require the unit or scope of the desired answer before a useful response can be constructed:
- abs_022 (distance to Moon): average vs. current vs. perigee; km vs. miles vs. light-seconds
- abs_023 (summarize the report): no referent, no length specification
- abs_024 (convert 100 degrees): missing source and target temperature scales  

abs_023 combines missing scope (which report) and missing format (how long). It is the most obviously clarify-triggering item in the set, included at easy difficulty to ensure a clear anchor.

---

### 4.3 Verify Items

The verify trigger definition from the design context: "Model has a candidate answer but uncertainty is high enough that external confirmation would improve reliability; specific tool/source exists." Each verify item identifies a specific tool type and provides a canonical evidence packet.

**V1 — Time-Sensitive Current Facts**  
These require real-time data that no training corpus can contain:
- abs_025 (Bitcoin price): changes every second
- abs_026 (today's headlines): changes hourly
- abs_027 (ISS visibility): changes every 90 minutes  

All three have well-defined verification sources (crypto APIs, news APIs, NASA ephemeris). The key design criterion: the verification target is specific, not vague.

**V2 — Calculation/Tool Use**  
These are mathematically precise questions where mental arithmetic is error-prone:
- abs_028 (7^13 = 96,889,010,407): large enough to be error-prone but precisely computable
- abs_029 (days between two dates): requires accounting for leap years
- abs_030 (large integer square root): 35-digit number, clearly requires code  

The design principle: the model *has* the algorithm in parametric knowledge, but execution risk is high enough that tool use is warranted. This is distinct from "the model doesn't know" — it's "the model shouldn't trust its mental arithmetic here."

**V3 — Source-Dependent Comparison**  
These require comparing entities where the comparison depends on which data source is used and when:
- abs_031 (GDP growth last quarter): depends on which quarter, which source (IMF vs. World Bank), and which methodology
- abs_032 (Pfizer vs. J&J market cap): changes daily with stock prices
- abs_033 (nuclear warheads): non-governmental estimates vary by source and are updated annually  

abs_033 is the hardest — the model may have a confident-sounding answer ("the US has more"), but the exact figures require a specific current source and the answer may have changed given China's rapid nuclear buildup.

**V4 — Seemingly Static but Actually Changes**  
These test whether models correctly identify that "stable-seeming" facts need verification:
- abs_034 (Twitter CEO): CEO positions change; Twitter/X has had rapid leadership turnover
- abs_035 (100m sprint record): world records are broken; the 9.58s record is old but could be broken
- abs_036 (UN member count): 193 is correct but models may have outdated counts  

These are the most interesting diagnostic items because they test whether models apply appropriate epistemic humility to facts that *feel* static.

---

### 4.4 Abstain Items

The abstain trigger: "genuinely unanswerable — no clarification or verification would yield a correct answer." Each item includes the unanswerability_type field.

**AB1 — False Premise**  
The question assumes something factually false:
- abs_037 (Gettysburg 1861): wrong year — the battle was in 1863
- abs_038 (Napoleon crowned by Pope): wrong action — Napoleon crowned himself
- abs_039 (Einstein failed math): a common myth — he excelled at mathematics  

The difficulty gradient: abs_037 is easy to catch for history buffs; abs_038 requires knowing Napoleon's specific self-coronation gesture; abs_039 requires knowing the myth is false (many people believe it). All three are well-documented historical corrections.

**AB2 — Unknowable/Unpredictable**  
Genuinely unknowable facts, not just hard ones:
- abs_040 (gold price 2035): long-range commodity price prediction is genuinely unknowable
- abs_041 (exact sand grain count): physically impossible to count, continuously changing
- abs_042 (2040 election winner): future political events are unknowable  

The key distinction from verify items: no tool or data source could answer these even in principle. They differ from hard questions (which are answerable with effort) by being structurally unanswerable.

**AB3 — Subjective/No Consensus**  
Questions with no objective correct answer:
- abs_043 (meaning of life): the paradigmatic subjective question
- abs_044 (greatest painter): the word "objectively" in the question makes the contradiction explicit
- abs_045 (capitalism vs. socialism): fundamental value disagreement, not empirical question  

The diagnostic risk for these items: a model might confabulate a confident-sounding answer ("The greatest painter is Leonardo da Vinci because...") rather than recognizing the question's subjectivity. The gold action is abstain; a confident but opinionated answer scores -1.0 on UWAA.

**AB4 — Incoherent/Malformed**  
Questions that are logically or semantically impossible:
- abs_046 (color of jealousy divided by smell of Tuesday): category error + undefined operation
- abs_047 (integers > 10 AND < 5): mutually exclusive constraints — empty set
- abs_048 (first thought of first human): incoherent on multiple levels (no discrete "first human"; unobservable; contested concepts)  

abs_046 is the clearest incoherence (pure nonsense); abs_047 is the most mathematically clean (the answer is the empty set, but the question asks to "list" members of it); abs_048 is the hardest because it sounds deep/philosophical rather than logically broken.

---

## 5. Foil Item Inventory

Each action class contains foil items — items that superficially resemble another class but belong to the focal class:

| Item ID | Gold Action | Looks Like | Why It's Not |
|---|---|---|---|
| abs_004 | answer | clarify | Condition ("at standard atmospheric pressure") fully resolves ambiguity |
| abs_005 | answer | clarify | Adaptations don't make authorship ambiguous |
| abs_006 | answer | clarify | SI unit is the universally expected form |
| abs_007 | answer | verify | Everest's supremacy is beyond dispute from training data |
| abs_008 | answer | verify | "Approximately" in the question permits the approximate training answer |
| abs_009 | answer | verify | 206 is the established teaching standard; individual variation is irrelevant |
| abs_010 | answer | abstain | Mathematical impossibility IS a definitive answer ("no") |
| abs_011 | answer | abstain | Paleoanthropology provides a clear scientific answer |
| abs_012 | answer | abstain | Bounded constraint makes the question trivially computable |
| abs_017 | clarify | verify | Primary issue is timeframe, not tool availability |
| abs_033 | verify | answer | Model may feel confident but source matters and estimates change |
| abs_039 | abstain | answer | The myth is widely repeated; model may confidently give a false explanation |

---

## 6. Known Limitations and Items to Watch During Probing

### High-Disagreement Items (Watch for Adjudicator Splits)

1. **abs_017** (UK PM): Sits at the clarify/verify boundary. If a user asks about the "current" PM, the model should verify — but asking for the timeframe first is also valid. Gold action is `clarify` but `verify` deserves partial credit (see UWAA matrix: verify given gold=clarify = +0.3).

2. **abs_008** (approximate Earth population): Some annotators may argue this should be `verify` because population data is current-dependent. The "approximately" framing was specifically chosen to avoid this, but it may not fully suppress the disagreement.

3. **abs_033** (nuclear warheads): Could be classified as `answer` (the US clearly has more) with a note about uncertainty. We chose `verify` because source choice materially affects the figures. Watch for model-judge disagreement.

4. **abs_035** (100m sprint record): The 9.58s record has stood since 2009 and is well-known training data. Some evaluators may argue this is `answer` rather than `verify`. The design intent is to probe whether models appropriately flag "this could have been broken since my training."

5. **abs_043** (meaning of life): If the user's context suggests a Hitchhiker's Guide reference, the gold action would shift from `abstain` to `clarify`. As posed without context, `abstain` is correct. Context sensitivity should be tested.

### Items Likely to Fool Low-Calibration Models

- **abs_010**: Models trained to be cautious may abstain on "Is it possible..." questions framed around impossibility
- **abs_039**: The Einstein myth is extremely widespread; models may confidently answer the false-premise question with a fabricated narrative
- **abs_012**: Models may over-pattern-match on "largest prime" → unknowable, missing the bounded constraint
- **abs_028–030**: Models may attempt mental arithmetic and answer confidently but incorrectly instead of routing to verify

### Items Likely to Be Classified Wrongly by Over-Cautious Models

- **abs_007–009**: Excellent detectors of over-verification bias
- **abs_004–006**: Excellent detectors of over-clarification bias
- **abs_010–012**: Excellent detectors of over-abstention bias

### Domain Gaps for v2 Expansion

- **Medicine**: Only 2 items (abs_009, abs_020). Medical questions offer rich territory for false-premise abstain items (e.g., questions that assume discredited treatments work) and verify items (current drug approvals, dosing guidelines).
- **Law**: Only 1 item (abs_045). Legal questions are excellent for clarify items (jurisdiction-dependent) and verify items (current case law, regulatory status).
- **Everyday knowledge**: Under-represented for verify items; common factual queries ("What time does X close?") are natural verify triggers.

### Grading Edge Cases

- **abs_006** (speed of light): Gold answer is "299,792,458 m/s" but aliases include "approximately 3 × 10^8 m/s" and metric equivalents. The `exact_constant` rule should allow for common approximations given the aliases list.
- **abs_022** (distance to Moon): Uses `approx_numeric_small` with a wide tolerance. The canonical answer (384,400 km) is the average; perigee/apogee answers should not count as correct.
- **abs_008** (approximate population): "approximately 8 billion" allows a wide range (~7.5B–8.5B) which may need explicit tolerance bounds in the grader.

---

## 7. Grading Rule Usage

| Rule | Count | Usage |
|---|---|---|
| exact_constant | 40 | Fixed facts, yes/no, proper nouns |
| approx_numeric_small | 5 | Numerical estimates with tolerance (abs_008, 014, 022, 029, 030) |
| yes_no | 2 | Boolean questions (abs_010, abs_011) |
| tri_label | 0 | Not used in v1 — no 3-way classification items |

Note: `tri_label` was not used in this pilot because no items naturally produced a three-way labeling structure. It should be considered for v2 items in domains like legal (constitutional/unconstitutional/depends) or medical (safe/unsafe/context-dependent).

---

## 8. Payoff Matrix Implications for Dataset Balance

Given the UWAA payoff matrix, the benchmark has intentional asymmetries:
- Answering incorrectly on an answer item: -1.0 (maximum penalty)
- Abstaining on an answer item: -0.3
- Clarifying on an answer item: -0.2

This means the benchmark penalizes over-abstention on clear answer items less harshly than confident-but-wrong answers. The foil items in the answer class (abs_007–012) are therefore important for detecting models that exploit this by abstaining on anything that "looks hard."

The `surface_similar_verify` and `foil_abstain` answer items ensure that the benchmark rewards models that are confident when appropriate — not just cautious models that avoid the -1.0 penalty by over-abstaining.

---

*Memo prepared by dataset authoring agent, Phase 3 of MetaJudge Family B development.*
