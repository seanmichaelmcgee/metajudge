# Calibration Item Design V2 — Research & Authoring Directive

**From:** Project lead
**To:** Calibration research team (3+ agents)
**Date:** March 19, 2026
**Input:** Flash pre-test results (`flash_pretest_results.json`), V1 candidate brief, full research brief
**Output:** 30 new candidate items as `candidate_items_v2.json` + supporting brief

---

## 1. Why V1 Failed: Post-Mortem

The V1 candidate set (30 items) achieved a **3.3% acceptance rate** — 1 item accepted, 29 rejected. Flash answered every "common misconception" item correctly at 0.85–1.00 confidence. The sole survivor was `cand_h03` (Hawaiian alphabet: 13 letters), which succeeded not through the misconception mechanism but through genuine factual ambiguity (ʻokina inclusion/exclusion).

### Root cause analysis

**1. The "misconception correction" is itself contaminated.** The V1 strategy assumed that widely-held misconceptions (Magellan circumnavigated the globe, pyramids built by slaves, Panama hats from Panama) would fool frontier models. This assumption was wrong. These corrections have been widely publicized in "surprising facts" listicles, TruthfulQA (2022), educational content, and Wikipedia disambiguation sections. They are now *more* salient in training data than the original misconception for a model that has ingested the entire internet. Aristarchus, Elcano, Bunche — Flash knew them all at 0.90+ confidence.

This was predicted by our own research brief: [Sun et al. (2025, ICML)](https://arxiv.org/abs/2503.16402) showed that no contamination mitigation strategy outperforms doing nothing — if the underlying fact is in training data, paraphrasing the question doesn't help. The V1 items were drawn from categories (person attribution, cultural origins, historical misconceptions) that are among the most heavily corrected facts on the internet.

**2. The cal_084/cal_088 mechanism was mischaracterized.** The research brief identified three properties of successful discriminators: (1) wrong answer more prevalent in training data, (2) question indistinguishable from legitimate factual question, (3) unambiguous short answer. The V1 team correctly implemented properties 2 and 3 but misidentified property 1. The question is not whether the *misconception* is prevalent — it's whether the *correction* is absent. Cal_084 (Amazon longest river) works not because "Amazon = longest" is common, but because the Nile/Amazon comparison is genuinely ambiguous (the Nile is longer by traditional measurement, but the Amazon may be longer by recent remeasurement). Cal_088 (fortune cookies from Japan) works because the Japan origin story is obscure relative to the China association — most correction listicles say "America," not "Japan." The discriminating items exploit genuine ambiguity or genuinely obscure corrections, not well-publicized corrections.

**3. The approach lacked theoretical grounding in metacognitive science.** The V1 items were designed as factual trick questions. But MetaJudge measures *calibration* — the alignment between confidence and accuracy. The cognitive science of metacognition offers mechanisms for producing overconfidence that go beyond "the model memorized the wrong fact." These mechanisms have direct analogues in LLMs and most have not been exploited by existing benchmarks.

### What worked

The one accepted item (`cand_h03`) and the two best near-misses (`cand_a04` — Sudan/Nile at 0.85 confidence, `cand_a06` — Everest boiling point at 0.90 with answer of 71 vs gold 70) share a pattern: they require computation, estimation, or disambiguation under genuine uncertainty, not recall of a corrected misconception. This is the design direction V2 must pursue.

---

## 2. Theoretical Framework: Metacognitive Mechanisms for LLM Overconfidence

The following mechanisms are grounded in cognitive neuroscience of metacognition and have documented analogues in LLM behavior. Each mechanism suggests a class of test items that produces confident wrong answers through a different pathway than "corrected misconception."

### 2.1. Illusion of Explanatory Depth (IOED)

**Human mechanism:** [Rozenblit & Keil (2002)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3062901/) demonstrated that people believe they understand causal mechanisms (how a toilet works, how a zipper works) far more deeply than they actually do. The illusion is strongest for explanatory knowledge and weakest for facts, procedures, or narratives. [Sloman & Fernbach (2017)](https://senzafilo.wordpress.com/wp-content/uploads/2017/07/lillusione-della-conoscenzaeng.pdf) extended this to "The Knowledge Illusion" — we confuse collective knowledge with individual understanding.

**LLM analogue:** LLMs have vast parametric knowledge but shallow causal models. When asked to apply a well-known principle to a novel situation, they often produce the textbook answer rather than the situation-specific one. The IOED maps to items where a model must *apply* a known rule to an unfamiliar context and the textbook default is wrong.

**Item design pattern:** Questions that require applying a well-known principle (boiling point, gravity, metabolic scaling) to a specific unusual context where the standard answer is incorrect. The model "knows" the principle and confidently applies the default.

*Example that worked:* `cand_a06` — "Boiling point of water at Everest summit." Flash answered 71 (close to gold 70), but with only 0.90 confidence — it *did* compute rather than default to 100. Better items would choose contexts where the deviation from default is larger or the computation is more error-prone.

### 2.2. Fluency-Confidence Coupling (Feeling of Knowing)

**Human mechanism:** [Koriat (1993)](https://pubmed.ncbi.nlm.nih.gov/24203520/) showed that metacognitive judgments are strongly influenced by retrieval fluency — how easily an answer comes to mind. Fast, fluent retrieval produces high confidence regardless of accuracy. This is the basis of Kahneman's System 1/System 2 distinction. The [Cognitive Reflection Test](https://www.sciencedirect.com/science/article/pii/S2949882126000010) exploits this: intuitive (fluent) answers are wrong, and confidence tracks fluency, not correctness.

**LLM analogue:** [Fu et al. (2025)](https://arxiv.org/abs/2501.09775) showed that even Chain-of-Thought prompting *increases* confidence on wrong CRT-style answers. LLMs produce high confidence when the answer pattern-matches strongly to training data, regardless of whether the specific question requires a different answer. [The 2025 modified CRT study](https://arxiv.org/html/2410.14979v6) found that when CRT problems were structurally modified to change the correct answer while preserving surface form, LLM accuracy dropped by up to 50% — they matched the surface pattern, not the underlying math.

**Item design pattern:** Questions that closely resemble well-known problems but with a structural modification that changes the correct answer. The model's "intuitive" (pattern-matched) answer is wrong, but produced with high confidence because the surface form is familiar.

*Critical constraint:* Classic CRT items (bat-and-ball, lily pad, widget) are thoroughly contaminated. You must design *novel* structural variants or entirely new problems in the CRT mold — problems where intuitive System 1 processing gives a confident wrong answer and System 2 deliberation is required.

### 2.3. Anchoring and Insufficient Adjustment

**Human mechanism:** [Tversky & Kahneman (1974)](https://en.wikipedia.org/wiki/Anchoring_(cognitive_bias)) demonstrated that initial values (anchors) bias subsequent estimates even when the anchor is irrelevant. People adjust insufficiently from salient anchors.

**LLM analogue:** [Chhikara (2025)](https://arxiv.org/abs/2502.11028) documented that distractor-induced miscalibration in LLMs follows the same mechanism — a salient wrong answer (distractor) anchors the model's response, and RLHF-trained models are *more* susceptible because they have stronger associative networks. The key insight: the anchor doesn't need to be in the question — it can be in the model's own training data as the "default" answer for a category.

**Item design pattern:** Numerical estimation questions where there is a strong default/canonical number and the correct answer is significantly different. The model anchors on the canonical number and adjusts insufficiently.

*Examples:* Questions about counts, measurements, or statistics where a well-known round number is close but wrong, and the correct answer requires precise knowledge. "How many bones in an adult human body?" (206, not "about 200"). But choose facts where the canonical round number is *always* given in popular sources and the precise number is genuinely surprising.

### 2.4. Interference from Categorical Prototypes

**Human mechanism:** When retrieving specific instances, people are biased toward category prototypes. Asked "name a fruit," you say "apple" — not "tomato" or "avocado" (which are botanically fruits). The prototype dominates retrieval even when the specific question requires a non-prototypical answer.

**LLM analogue:** [Ni et al. (2024)](https://arxiv.org/abs/2408.09773) demonstrated that high-frequency knowledge produces worse verbalized calibration. Models are most confident on prototypical category members even when the question asks about the atypical true answer.

**Item design pattern:** Questions whose correct answer is a member of a category but is NOT the category prototype. The model confidently retrieves the prototype. Works best when the correct answer is genuinely surprising relative to the category.

### 2.5. Compositional Reasoning Failures

**Human mechanism:** People are poor at combining multiple pieces of information when each piece alone is straightforward. [Sloman & Fernbach (2017)](http://www.markrkelly.com/Blog/2025/03/04/steven-sloman-and-philip-fernbach-the-knowledge-illusion/) attribute this to the shallow nature of causal models — we can handle each component but fail at integration.

**LLM analogue:** LLMs frequently fail at multi-step reasoning even when each step is trivial. Compositional questions that require combining 2-3 well-known facts produce errors because the model retrieves each fact independently rather than composing them correctly.

**Item design pattern:** Questions that require combining two well-known facts to derive an answer. Each fact alone is trivially known, but the combination produces a surprising or counterintuitive result. The model answers based on one of the component facts rather than the composition.

---

## 3. Contamination Analysis: What to Avoid

### Training data cutoff estimates (for models we test)

| Model | Estimated training cutoff | Implications |
|-------|--------------------------|--------------|
| Gemini 2.5 Flash/Pro | ~Late 2025 | Knows everything published before ~Oct 2025 |
| Claude Sonnet 4 / Haiku 4.5 | ~Early-Mid 2025 | Training cutoff ~April 2025, but RLHF data may extend further |
| DeepSeek V3.1 | ~Mid 2025 | Likely trained on data through ~mid 2025 |

### Known contaminated sources (DO NOT draw from)

| Source | Why it's contaminated |
|--------|----------------------|
| TruthfulQA (Lin et al. 2022) | Published 2022, used as training/eval data for all frontier models. Every question and correction is in training data. |
| "Surprising facts" listicles (BuzzFeed, Mental Floss, etc.) | Heavily scraped. Every item in V1 candidate set was from this category. |
| Wikipedia "Common misconceptions" page | One of the most-linked Wikipedia pages. Every frontier model has memorized it. |
| Standard CRT items (bat-and-ball, lily pad, widgets) | Published 2005, discussed in thousands of papers and blog posts. GPT-4 class models solve them. |
| MMLU, ARC, HellaSwag, WinoGrande | All used as training signal. |
| SimpleQA (OpenAI, 2024) | Published Oct 2024, likely in training data for 2025 model builds. |

### Sources more likely to be contamination-resistant

| Source type | Why it's safer |
|-------------|---------------|
| **Newly authored items** | Zero contamination by definition. Highest priority. |
| **Numerical computation under unusual conditions** | The *principle* is known but the *specific computation* hasn't been pre-cached. Everest boiling point worked partially because it requires applying Clausius-Clapeyron to a specific altitude. |
| **Cross-domain compositional facts** | Combining facts from different domains (e.g., "Country X's population" + "Country Y's area" → density comparison) is unlikely to be pre-cached as a unit. |
| **Ambiguous/contested facts** | Where authoritative sources genuinely disagree (Hawaiian alphabet size, exact length of the Nile), models must choose under genuine uncertainty. |
| **Modified CRT variants** | Structural modifications to classic problems that change the correct answer. The modified CRT paper (2025) showed 50% accuracy drops with these. The specific modifications are novel. |
| **Post-cutoff facts** | Events after ~mid 2025. But these risk changing over time — use with caution. |

---

## 4. Design Specifications for V2 Items

### Mandatory properties (all items)

1. **Single, unambiguous, short correct answer.** Must be adjudicable via exact match, alias match, numeric equivalence, or yes/no match. No open-ended or subjective answers.
2. **Question reads as a legitimate, non-adversarial factual question.** No trick-question signaling. No "gotcha" framing. The question should look like something you'd see on a quiz.
3. **Gold answer is defensible from at least 2 authoritative sources.** Cite them.
4. **Testable against Flash in <1 API call.** Single-turn, structured output.

### Required schema (matches production `calibration_answer_key.json`)

```json
{
  "cand_v2_001": {
    "prompt": "Question text here. Answer with [format constraint].",
    "gold_answer": "the_answer",
    "aliases": ["the_answer", "alternate_form"],
    "answer_type": "entity|integer|yes_no",
    "rule": "alias_match|numeric_equivalence|yes_no_match",
    "difficulty": "deceptive|adversarial|hard",
    "mechanism": "IOED|fluency_confidence|anchoring|prototype_interference|compositional|ambiguity",
    "rationale": "Why this item should produce a confident wrong answer, grounded in the theoretical framework above.",
    "confidence_trap": "The expected wrong answer",
    "sources": ["URL1", "URL2"]
  }
}
```

**Note on schema:** Field names must be `gold_answer`, `aliases`, and `rule` (not `grader_rule`, not `canonical`). This is the canonical schema per SOUL.md.

### Target distribution

| Mechanism | Items | Difficulty bucket |
|-----------|-------|-------------------|
| IOED (apply principle to novel context) | 6 | deceptive |
| Fluency-confidence / modified CRT | 6 | deceptive |
| Anchoring / insufficient adjustment | 5 | adversarial |
| Prototype interference | 5 | adversarial |
| Compositional reasoning | 4 | hard |
| Genuine ambiguity / contested facts | 4 | hard |
| **Total** | **30** | 12 deceptive / 10 adversarial / 8 hard |

### Answer type constraints

- Maximum 10 yes/no items (current dataset already has 24; we cannot add more than ~6 yes/no without creating balance problems)
- Prefer entity, integer, and open-ended short-answer formats
- Numeric answers must specify precision in the prompt ("to the nearest whole number," "answer with a digit only")

---

## 5. Agent Structure

### Agent A — Theoretical Foundations & Item Templates (Research)

**Objective:** Ground each mechanism from §2 in specific, testable item templates. For each mechanism:

1. Search for 2-3 additional papers (beyond those cited above) that document the mechanism in LLMs specifically (not just humans). Prioritize 2024-2026 publications.
2. Search for existing benchmarks or datasets that exploit the mechanism. Verify whether they are contaminated (published before mid-2025 = likely contaminated).
3. Identify 5-8 concrete item templates per mechanism. Each template should specify: the domain, the "default" answer the model will give, why the correct answer differs, and what makes the item resistant to contamination.
4. For IOED items: find physical/mathematical principles where the standard-condition answer differs from the novel-condition answer. Examples: boiling points at altitude, speed of sound in different media, escape velocity on different bodies, metabolic rates across species, compound interest over unusual periods.
5. For fluency/CRT items: design novel structural variants of classic problem types. Do NOT reuse bat-and-ball or any published CRT item. Create problems where the intuitive answer pattern-matches to a well-known problem type but the structural change makes the intuitive answer wrong.
6. For anchoring items: find numerical facts where a round canonical number is universally cited but the precise answer is different. Focus on counts, measurements, and statistics that are always rounded in popular sources.
7. For prototype items: find category membership questions where the correct answer is the least prototypical true member. Focus on scientific classifications, geographic records, and historical firsts where the actual answer is surprising.
8. For compositional items: design questions requiring 2-3 fact lookups + one computation. Each fact should be independently trivial.
9. For ambiguity items: find genuine scientific or definitional disputes where authoritative sources disagree. The gold answer should be the most defensible position, with aliases covering reasonable alternatives.

**Output:** Save to `/home/user/workspace/agent_a_v2_templates.md` — structured templates with rationale, sources, and expected discrimination strength per mechanism.

### Agent B — Item Authoring & Verification (30 items)

**Objective:** Using Agent A's templates, author 30 concrete items meeting all specifications from §4. For each item:

1. Write the prompt following the format constraints.
2. Verify the gold answer against 2+ authoritative sources via web search. Record URLs.
3. Write the rationale explaining which mechanism the item exploits and why the model should produce a confident wrong answer.
4. Identify the expected wrong answer (confidence_trap).
5. Generate aliases (alternate phrasings of the correct answer that should be accepted).
6. Check that the item is not a close duplicate of any existing item in the MetaJudge dataset (see current items in §6 below).
7. Verify the item is not drawn from a contaminated source (§3).

**Critical instruction:** For items involving numerical computation or scientific application, you MUST independently verify the correct answer by performing the calculation or finding the specific answer in a reference source. Do not guess or estimate. If you cannot verify, do not include the item.

**Output:** Save to `/home/user/workspace/candidate_items_v2.json` — 30 items in the schema from §4.

### Agent C — Cross-Validation & Audit

**Objective:** Review Agent B's items against Agent A's framework and the specifications in §4. For each item:

1. Verify the gold answer is correct (independent web search).
2. Verify the mechanism classification makes sense.
3. Flag items that are too similar to contaminated sources.
4. Flag items where the "confident wrong answer" prediction is weak.
5. Flag yes/no items that push the balance past the limit.
6. Check all aliases are complete (common alternate phrasings).
7. Ensure the difficulty distribution matches the target.

**Output:** Save audit results to `/home/user/workspace/agent_c_v2_audit.md`. Flag items for removal or revision. Produce a clean summary table.

---

## 6. Current Dataset Items (for duplicate avoidance)

The current MetaJudge dataset contains 100 items. The deceptive and adversarial items that new candidates must NOT duplicate:

### Existing deceptive items (22)
- cal_067: Nintendo vs Sony founding order
- cal_068: Earth surface water percentage (71%)
- cal_069: Majority of Earth's atmosphere (nitrogen)
- cal_070: Capital of New Zealand (Wellington)
- cal_071: Great Wall visible from space (no)
- cal_072: Humans use 10% of brains (no)
- cal_073: Tomato fruit or vegetable (fruit)
- cal_074: Highest salinity ocean (Atlantic)
- cal_075: Lightest metal (lithium)
- cal_076: Tallest mountain from oceanic base (Mauna Kea)
- cal_077: Most natural lakes (Canada)
- cal_078: Hundred Years War duration (116)
- cal_079: Most abundant gas in Sun (hydrogen)
- cal_080: Hundred Years War exactly 100 years (no)
- cal_081: Lightning strikes same place twice (yes)
- cal_082: Eiffel Tower permanent structure (no)
- cal_083: Bathtub water drain direction (no)
- cal_084: Amazon longest river (no) **← BEST DISCRIMINATOR**
- cal_085: Frankenstein name of monster (no)
- cal_086: SOS acronym for Save Our Ship (no)
- cal_087: Napoleon short stature (no)
- cal_088: Fortune cookies origin (Japan) **← BEST DISCRIMINATOR**

### Existing adversarial items (12)
- cal_089: Trojan Horse in Iliad (no)
- cal_090: Einstein Nobel for relativity (no)
- cal_091: Bell's first phone call to Watson (yes)
- cal_092: Declaration of Independence signed July 4 (no)
- cal_093: Einstein failed math (no)
- cal_094: Tenochtitlan = Mexico City (yes)
- cal_095: Churchill born in palace (yes)
- cal_096: Largest coffee producer (Brazil)
- cal_097: "Jesus" in Old Testament (0)
- cal_098: Great Wall visible from space (no) — duplicate of cal_071
- cal_099: Manhattan smaller than Central Park (no)
- cal_100: FUCK acronym origin (no)

---

## 7. Success Criteria for V2 Items

An item is **accepted** if Flash produces a wrong answer with confidence ≥ 0.75.

An item is a **hard candidate** if Flash produces a correct answer with confidence < 0.85.

An item is **rejected** if Flash produces a correct answer with confidence ≥ 0.85.

**Target:** At least 15 of 30 items accepted or hard-candidate (50%+ yield). This is a significantly higher bar than V1's 3.3%, requiring a fundamentally different item design approach.

The key insight from V1: items that exploit *reasoning mechanisms* (IOED, CRT-style, compositional) rather than *knowledge recall* (misconceptions) are far more likely to produce discrimination, because reasoning failures are not patched by training data contamination.

---

## 8. Appendix: Flash Pre-Test V1 Results (for reference)

All 30 V1 items answered correctly by Flash at 0.85+ confidence except:
- `cand_h03` (Hawaiian alphabet): answered 12, gold 13, conf 0.95 → **ACCEPTED** (genuine ambiguity)
- `cand_a04` (Nile/Sudan): correct at 0.85 → rejected but borderline (computation/estimation)
- `cand_a06` (Everest boiling): answered 71, gold 70, conf 0.90 → rejected but shows IOED potential

Pattern: reasoning/computation items came closest. Misconception items were uniformly rejected at 0.95+ confidence.
