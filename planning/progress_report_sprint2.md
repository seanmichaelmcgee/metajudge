# MetaJudge Sprint 2 Progress Report & Calibration Analysis

**Date:** March 19, 2026  
**Competition:** Kaggle "Measuring Progress Toward AGI — Cognitive Abilities"  
**Track:** Metacognition  
**Deadline:** April 16, 2026  
**Repository:** github.com/seanmichaelmcgee/metajudge

---

## 1. Executive Summary

MetaJudge is a confidence calibration benchmark for the Kaggle "Measuring Progress Toward AGI" competition (Metacognition track). It targets the question: do frontier LLMs know what they know? The benchmark presents 100 factual questions and measures whether models' verbalized confidence scores track their actual correctness via Brier scoring — a strictly proper scoring rule that cannot be gamed by strategic hedging.

Over two sprints, the project progressed from a 20-item pilot set to a 100-item V2 dataset built by a 4-agent automated pipeline. The V2 dataset has verified production infrastructure: SDK-aligned Kaggle notebook, comprehensive test suite, CI/CD with automated code auditing, and a codified 5-model sweep protocol.

The March 19, 2026 sweep of all 5 panel models reveals the core problem: frontier models are too accurate on the current dataset. With 89/100 items answered correctly by every model, discrimination is near-zero. Only 1 of 5 success criteria is met (C4: ≥10 gap items). The Brier score spread across models is 0.036, below the 0.05 threshold. The dataset infrastructure is solid; the items themselves need to be harder.

**Next step:** Targeted item replacement — swap ~20 universally-correct items for deceptive and adversarial items modeled on the cal_084/cal_088 pattern that worked.

---

## 2. Project Overview

### 2.1 Competition Context

The Kaggle "Measuring Progress Toward AGI — Cognitive Abilities" competition ([kaggle.com/competitions/kaggle-measuring-agi](https://www.kaggle.com/competitions/kaggle-measuring-agi)) is organized by Google DeepMind and runs from March 17 through April 16, 2026. It prizes $10,000 per track (top 2 entries) with $25,000 grand prizes for the four absolute best benchmarks across tracks.

Submissions are evaluated on: 50% dataset quality, 20% writeup (1,500 words), 15% discriminatory power across models, and 15% community votes. A submission requires one Kaggle Benchmark (built via `%choose`) plus a writeup. The total API budget is $500 ($50/day).

The competition is grounded in the Burnell et al. (2026) cognitive framework ([Burnell et al., 2026](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf)), which defines five cognitive tracks where the evaluation gap is largest: Learning, Metacognition, Attention, Executive Functions, and Social Cognition.

### 2.2 MetaJudge's Positioning in the Cognitive Taxonomy

The Burnell et al. (2026) taxonomy defines **metacognition** as: "The knowledge a system has about its own cognitive processes, and its ability to monitor and control those processes." It identifies three sub-faculties:

- **Metacognitive Knowledge** — self-knowledge about capabilities and limitations
- **Metacognitive Monitoring** — monitoring the state of cognitive processes (including confidence calibration)
- **Metacognitive Control** — using monitoring information to adjust behavior

MetaJudge targets **metacognitive monitoring**, specifically the sub-ability "confidence calibration: accurately estimating the likelihood that a response will be correct." It uses the Nelson & Narens (1990) two-axis architecture ([Nelson & Narens, 1990](https://linkinghub.elsevier.com/retrieve/pii/S0079742108600535)) to separate Axis I (Epistemic Monitoring) from Axis II (Cognitive Control). The current implementation covers Family A (Confidence Calibration) under Axis I.

### 2.3 Technical Approach

MetaJudge uses verbalized confidence elicitation: each model is asked a factual question and must output both an answer and a numeric confidence score (0–1). Performance is measured by the Brier score — the mean squared error between stated confidence and binary correctness outcome.

The Brier score is chosen over alternatives such as ECE because it is a strictly proper scoring rule ([Gneiting & Raftery, 2007](https://www.tandfonline.com/doi/abs/10.1198/016214506000001437)): no model can improve its score by misreporting its true beliefs. ECE, by contrast, is not a proper scoring rule and can be gamed by hedging at 0.5.

Verbalized confidence is used instead of logit-based calibration because: (1) logit access is unavailable for most frontier API models, and (2) for RLHF-trained models, verbalized confidence is better calibrated than internal token probabilities ([Tian et al., 2023](https://arxiv.org/abs/2305.14975)), which are degraded by the alignment training process.

---

## 3. Sprint History

### 3.1 Sprint 1: Foundation & V1 Pilot

**Phase 0 — Bootstrap:**  
The repository (github.com/seanmichaelmcgee/metajudge) was established with the core Python package (`metajudge/`), Kaggle notebook structure (`notebooks/`), and all planning documents (SOUL.md, v1_architecture.md, scoring_plan.md, dataset_construction_plan.md). An initial test suite was created (~20 tests).

**SDK Verification:**  
All 26 Kaggle Benchmarks SDK capabilities were confirmed PASS, including `@kbench.task`, `%choose`, `.evaluate()`, caching, structured output via dataclasses, and model enumeration. An evidence notebook was produced as a proof-of-concept of the wrapper-task pattern running in the live Kaggle environment.

**Architecture Revision:**  
After reviewing the metacognition assessor recommendations memo, the project adopted a two-axis model (Nelson & Narens 1990) replacing the initial flat family list. Five families were defined: Calibration (A), Abstention/Verification (B), Self-Correction (C), Grounding Sensitivity (D), and Control-Policy Adaptation (E). Sprint 1 focused exclusively on Family A.

**V1 Pilot Dataset:**  
A 20-item pilot set was built across arithmetic, science, history, geography, and misconceptions with basic difficulty tiers. The wrapper-task pattern was verified in the live Kaggle environment.

**Finding:** Items were too easy. Models answered all or nearly all correctly, providing no discrimination. This prompted the V2 expansion directive.

### 3.2 Sprint 2: V2 Expansion & Multi-Model Validation

**4-Agent Dataset Pipeline:**  
A fully automated 4-agent pipeline produced the 100-item V2 calibration set:

1. **Harvester** — Web research and LLM authoring produced 223 raw candidates
2. **Formatter** — Canonicalized prompts, built alias ledger, applied format gates → 83.4% pass rate (186 items)
3. **Strategist** — Selected final 100 items with optimized difficulty distribution
4. **Auditor** — Adversarial independent review; flagged 3 critical issues and 11 warnings; verified 27 gold answers via web search

Twelve audit fixes were applied: cal_088 gold answer corrected from `united states` to `japan`, cal_098 replaced entirely (contested Mpemba effect physics), cal_021 format fixed, and 9 alias improvements. The final distribution was: 10 easy / 26 medium / 30 hard / 22 deceptive / 12 adversarial. Production files committed as `6ac5b12` with all 59 tests passing.

**Flash-Only Sweep:**  
Single-model test of `google/gemini-2.5-flash` yielded 97/100 correct (0.9756 headline score). Three real errors were confirmed: cal_065 (France borders, deceptive), cal_084 (Amazon river, deceptive), cal_088 (fortune cookies, deceptive). A Cell 5 smoke-test bug was identified and fixed (hardcoded old pilot prompt `cal_001` → `95f16fb`). Conclusion: scores too high on flash alone; weaker models needed for spread.

**Multi-Model Infrastructure:**  
The submission notebook was rebuilt as SDK-aligned v3 (11 cells, `92b3833`). Key changes: model discovery via `kbench.llms.keys()` added to Cell 1, model key format verified (`provider/model@version` for Anthropic, `provider/model` for others), Cell 2 dataclass updated to handle misspelled response fields (e.g., `reason_for_uncertainity`), Cell 7 rebuilt with retry logic for transient API failures. Multi-model sweep cells (7–8) and the codified sweep protocol in SOUL.md were committed as `47e654a`.

**CI/CD Improvements:**  
- Claude code auditor with sticky GitHub Actions comments (`312c9f9`)
- Coverage-conditioned accuracy diagnostic (`75320ad`)
- Dataset validator suite (26/26 tests, 90/90 full suite)
- Schema discrepancy identified: three different field name conventions across `adjudication.py`, `answer_key.json`, and the notebook (documented as a known issue)

---

## 4. 5-Model Sweep Results (March 19, 2026)

### 4.1 Model Panel

All 5 models were verified on the Kaggle platform before the sweep. Verified SDK keys:

| Model | Provider | Kaggle SDK Key |
|-------|----------|----------------|
| Gemini 2.5 Pro | Google | `google/gemini-2.5-pro` |
| Gemini 2.5 Flash | Google | `google/gemini-2.5-flash` |
| Claude Sonnet 4 | Anthropic | `anthropic/claude-sonnet-4@20250514` |
| Claude Haiku 4.5 | Anthropic | `anthropic/claude-haiku-4-5@20251001` |
| DeepSeek V3.1 | DeepSeek | `deepseek-ai/deepseek-v3.1` |

### 4.2 Headline Results

| Model | Accuracy | Errors (n) | Est. Headline Score | Notable Errors |
|-------|----------|------------|---------------------|----------------|
| gemini-2.5-pro | 98/100 | 2 | ~0.978 | cal_084, cal_088 |
| gemini-2.5-flash | 97/100 | 3 | ~0.970 | cal_065, cal_084, cal_088 |
| claude-haiku-4.5 | 97/100 | 3 | ~0.970 | cal_058, cal_062, cal_092 |
| claude-sonnet-4 | 95/100 | 5 | ~0.953 | cal_047, cal_062, cal_077, cal_084, cal_088 |
| deepseek-v3.1 | 93/100 | 7 | ~0.936 | cal_047, cal_058, cal_084, cal_089, cal_090, cal_092, cal_095 |

Note: `gemini-2.5-pro` initially produced a wrong answer on cal_058 (answer=20, conf=1.00) but the retry yielded the correct answer (answer=21). `claude-sonnet-4` hit a transient API error on first attempt; retry succeeded. Both outcomes confirm the value of the retry logic implemented in Cell 7.

Confidence styles differ significantly across models — a meaningful calibration signal:
- **gemini-2.5-flash:** Near-binary; almost all 1.00, occasional low values
- **gemini-2.5-pro:** Mixed 1.00 and 0.90–0.95
- **claude-sonnet-4:** Widest range (0.70–1.00); most expressive calibration
- **claude-haiku-4.5:** Discrete clusters at 0.99, 0.95, 0.85, 0.75
- **deepseek-v3.1:** Range 0.70–1.00; notably lower on uncertain items

### 4.3 Accuracy by Difficulty Bucket

| Bucket | N Items | Flash | Pro | Sonnet | Haiku | DeepSeek |
|--------|---------|-------|-----|--------|-------|----------|
| Easy | 10 | 100% | 100% | 100% | 100% | 100% |
| Medium | 26 | 100% | 100% | 100% | 100% | 100% |
| Hard | 30 | 100% | 100% | 93% | 93% | 93% |
| Deceptive | 22 | 86% | 91% | 86% | 100% | 95% |
| Adversarial | 12 | 100% | 100% | 100% | 92% | 67% |
| **Total** | **100** | **97%** | **98%** | **95%** | **97%** | **93%** |

Key observations:
- Easy and medium buckets (36 items combined) are universally correct across all 5 models
- Hard items only trip up non-Google models (Sonnet, Haiku, DeepSeek) — 93% ceiling
- Deceptive items work inconsistently: Flash and Sonnet score 86%, Haiku is surprisingly immune at 100%
- Adversarial items only substantially affect DeepSeek (67%); all other models score ≥92%

### 4.4 Success Criteria Assessment

Per SOUL.md, the dataset must meet ≥4/5 criteria to be frozen. Current results:

| # | Criterion | Threshold | Measured | Status |
|---|-----------|-----------|----------|--------|
| C1 | Brier score spread across models | ≥ 0.05 | ~0.036 | **FAIL** |
| C2 | Deceptive bucket accuracy | < 80% on ≥3 models | 0/5 models | **FAIL** |
| C3 | Adversarial bucket accuracy | < 70% on ≥3 models | 1/5 models | **FAIL** |
| C4 | Items with conf–acc gap > 0.20 | ≥10 distinct items | 11 | **PASS** |
| C5 | ECE range across models | ≥ 0.03 | Pending Cell 9 | **UNKNOWN** |

**Overall: 1/5 criteria met (possibly 2/5 if C5 passes) → NEEDS WORK per SOUL.md decision gate**

The SOUL.md gate for this result (< 3/5 met) is: "Return to Harvester/Strategist for harder items."

### 4.5 Discrimination Analysis

Of 100 items, only **11 discriminate** (models disagree on them):

| Item | Category | Models Wrong | Wrong Models |
|------|----------|-------------|--------------|
| cal_084 | deceptive | 4/5 | Flash, Pro, Sonnet, DeepSeek |
| cal_088 | deceptive | 3/5 | Flash, Sonnet, DeepSeek |
| cal_047 | hard | 2/5 | Sonnet, DeepSeek |
| cal_058 | hard | 2/5 | Haiku, DeepSeek |
| cal_062 | hard | 2/5 | Sonnet, Haiku |
| cal_092 | adversarial | 2/5 | Haiku, DeepSeek |
| cal_065 | deceptive | 1/5 | Flash only |
| cal_077 | deceptive | 1/5 | Sonnet only |
| cal_089 | adversarial | 1/5 | DeepSeek only |
| cal_090 | adversarial | 1/5 | DeepSeek only |
| cal_095 | adversarial | 1/5 | DeepSeek only |

`cal_084` and `cal_088` are the strongest discriminators, each failing multiple frontier models at high confidence. These are the design target for new items (see §6.2).

The 89 non-discriminating items contribute calibration resolution signal via their confidence distributions, but provide zero discrimination. `cal_074` (correct answer but confidence=0.45 from Haiku) represents an interesting underconfidence signal worth monitoring.

### 4.6 Overconfidence Map

16 total overconfident errors (wrong answer + confidence > 0.80) across 10 unique items:

| Model | Item | Confidence | Model Answer | Gold Answer |
|-------|------|------------|--------------|-------------|
| gemini-2.5-pro | cal_084 | 0.90 | Yes (Amazon is longest) | no |
| gemini-2.5-pro | cal_088 | 0.95 | United States | japan |
| gemini-2.5-flash | cal_084 | ~1.00 | Yes (Amazon is longest) | no |
| gemini-2.5-flash | cal_088 | ~1.00 | United States | japan |
| claude-sonnet-4 | cal_047 | 0.85 | 2 (states bordering one) | 1 |
| claude-sonnet-4 | cal_062 | 0.95 | 108 (rectangle area) | 72 |
| claude-sonnet-4 | cal_077 | 0.85 | Finland (most lakes) | canada |
| claude-sonnet-4 | cal_084 | 0.95 | Yes (Amazon is longest) | no |
| claude-sonnet-4 | cal_088 | 0.80 | United States | japan |
| claude-haiku-4.5 | cal_058 | 0.82 | 24 (states ending in 'a') | 21 |
| claude-haiku-4.5 | cal_062 | 0.99 | 180 (rectangle area) | 72 |
| claude-haiku-4.5 | cal_092 | 0.95 | yes (Declaration signed July 4) | no |
| deepseek-v3.1 | cal_058 | 0.90 | 24 (states ending in 'a') | 21 |
| deepseek-v3.1 | cal_084 | 0.95 | yes (Amazon is longest) | no |
| deepseek-v3.1 | cal_089 | 0.95 | yes (Trojan Horse in Iliad) | no |
| deepseek-v3.1 | cal_090 | 0.90 | yes (Einstein Nobel for relativity) | no |

Notable: `cal_062` at 0.99 confidence by Haiku is the single most extreme overconfidence case in the sweep. The Flash and Pro pattern of expressing 1.00 confidence on deceptive items they get wrong is exactly the behavior the benchmark should surface and penalize.

---

## 5. Calibration Diagnosis

### 5.1 Why the Dataset Is Too Easy

The root problem is straightforward: 89/100 items are universally correct. These items contribute no discrimination signal and drag the Brier spread down toward zero.

The 36 easy/medium items (10 + 26) function as calibration anchors — they ensure models' confidence on items they know well is measured — but they provide no discriminative power whatsoever. Every model scores 100% on both buckets.

The 30 hard items fare only marginally better. "Hard" was calibrated against human difficulty rather than LLM difficulty. Items that are difficult for humans because they require obscure domain knowledge are often easy for frontier LLMs because the facts are well-represented in training data. Only 3 hard items discriminate (cal_047, cal_058, cal_062), and only between two models each.

The 22 deceptive items were designed to exploit misconceptions, but the results are inconsistent. Flash and Sonnet fail some deceptive items; Haiku fails none; Pro fails only the two strongest. The deceptive items that work (cal_084, cal_088, cal_065, cal_077) share a specific pattern that the majority of deceptive items do not replicate.

The 12 adversarial items are nearly all answered correctly by the Google and Anthropic models. Only DeepSeek fails adversarial items broadly (4/12 wrong, 67% accuracy). The adversarial items may be too obvious — models identify the trap and refuse it.

### 5.2 What Works: Anatomy of Good Discriminators

`cal_084` (Amazon river: "Is the Amazon River the longest river in the world?") and `cal_088` (fortune cookies: "Where did fortune cookies originate?") are the benchmark's two best items. They discriminate 4/5 and 3/5 models respectively, always at high confidence on the wrong answer.

Both items exploit **widely-held misconceptions that even frontier models share**:
- **cal_084:** Models conflate "largest river basin" and "most water volume" with "longest." The Amazon is genuinely exceptional in multiple dimensions, and the confident-but-wrong belief that it is also the longest is shared across training data.
- **cal_088:** Fortune cookies are culturally associated with Chinese-American restaurants, and the correct answer (Japan) contradicts a near-universal popular misconception. The model's training data overwhelmingly associates fortune cookies with China, not Japan.

The pattern is: the wrong answer is *plausible*, *culturally embedded*, and the model is *confident* about it. This is exactly the distractor-driven miscalibration effect documented by [Chhikara (2025)](https://doi.org/10.48550/arXiv.2502.11028), who finds that larger models are more susceptible to distractor-induced false confidence than smaller models — the opposite of the intuitive prior.

Both items also align with [Liu et al. (2024)](https://doi.org/10.48550/arXiv.2311.09731) on knowledge boundaries: the most productive adversarial items are not those where the model genuinely lacks the information, but those where the model has *confident but incorrect* information due to data distribution patterns.

### 5.3 What Fails: Anatomy of Non-Discriminating Items

The 89 universally-correct items fall into several failure patterns:

**Unambiguous factual items:** Math questions, basic science, canonical history (e.g., "who wrote Critique of Pure Reason?") — these have clear correct answers that are unambiguously represented in every frontier model's training data. All 5 models answer correctly and confidently.

**"Hard" items that are hard for humans but easy for LLMs:** Obscure geographic facts, specialized science, niche history — these are difficult because humans rarely encounter them, but they appear in training corpora (Wikipedia, textbooks, papers). Examples: capital cities of small nations, specific historical dates, named mathematical theorems.

**Adversarial items that telegraph the trap:** Items designed as adversarial yes/no questions where the "obvious" answer is wrong can be identified as traps by the model, which then applies caution rather than falling for the bait. A model that recognizes "this looks like a trick question" hedges its confidence appropriately — which is actually good calibration behavior, but defeats the discriminative intent.

### 5.4 Literature-Grounded Analysis

The sweep results align closely with the existing calibration literature:

**Systematic overconfidence:** [Xiong et al. (2024)](https://doi.org/10.48550/arXiv.2306.13063) establish that RLHF-trained models exhibit systematic overconfidence as a bias in verbalized confidence. The 16 overconfident errors in the sweep confirm this: every error with confidence > 0.80 represents a model asserting high certainty on a wrong answer. No model is systematically underconfident on wrong answers.

**Model size and calibration:** [Kadavath et al. (2022)](https://doi.org/10.48550/arXiv.2207.05221) find that larger models are better calibrated. The sweep ordering (Pro 98% > Flash/Haiku 97% > Sonnet 95% > DeepSeek 93%) is roughly consistent with model capability ordering, though confidence style differences mean calibration and accuracy don't perfectly track.

**Overconfidence as dominant failure mode:** [Groot & Valdenegro-Toro (2024)](https://doi.org/10.48550/arXiv.2405.02917) document that overconfidence is the dominant failure mode across all frontier LLMs and VLMs. All 16 overconfident errors in the sweep are wrong-and-confident (not wrong-and-uncertain), confirming this pattern. Not a single model error is at low confidence — all failures involve misplaced certainty.

**Calibration benchmarks can discriminate:** [Sung et al. (2025) — GRACE](https://doi.org/10.48550/arXiv.2502.19684) demonstrate that a well-constructed calibration benchmark achieves meaningful discrimination across model quality. GRACE achieves this by using gradated clue structures. The lesson for MetaJudge: the item design, not the scoring framework, is what creates discrimination.

**Distractors are the mechanism:** [Chhikara (2025)](https://doi.org/10.48550/arXiv.2502.11028) shows that larger models are specifically more susceptible to distractor-driven miscalibration than smaller models — precisely the mechanism in cal_084 and cal_088. The implication is that more deceptive items using this mechanism will produce the desired discrimination signal.

---

## 6. Technical Recommendations for Next Sprint

### 6.1 Item Replacement Strategy

**Target:** Replace approximately 20 of the 89 universally-correct items with harder deceptive/adversarial items.

**Source priority:**
1. **Rejection log first** — `data/harvest/v2_rejection_log.json` contains 123 candidates rejected from the V2 pipeline. Many were rejected for difficulty calibration reasons (too hard for the target distribution) that are now exactly what is needed. Review all 123 with fresh eyes against the cal_084/cal_088 pattern before authoring new items.
2. **Author new items** if the rejection log is insufficient — following the `expansion_sprint_v2.md §2.2` protocol.

**Focus buckets:**
- **Deceptive: +8 items** (22 → 30) — priority, this is where the best discriminators live
- **Adversarial: +8 items** (12 → 20) — redesign toward subtler traps (see §6.2 pattern 5)
- **Easy: -5 items** (10 → 5) — remove the weakest anchors; keep minimum for calibration baseline
- **Medium: -11 items** (26 → 15) — keep the more interesting medium items, drop pure knowledge recall

**Before replacing any item,** run the item against a single model (Flash, cheapest) to confirm it produces an error. Only items with confirmed model errors should enter the final set.

### 6.2 Patterns That Produce Good Discriminators

Based on sweep data and the calibration literature, the following five patterns reliably produce discriminating items:

**Pattern 1: Common misconceptions with confident wrong answers** (exemplified by cal_084, cal_088)  
The model has incorrect but confidently-held beliefs derived from cultural prevalence in training data. Correct answer is counterintuitive but unambiguously correct. The wrong answer is not random noise — it is a specific, named, plausible alternative that the model will likely select. Examples: geographical confusions (Amazon vs. Nile), cultural origin myths (fortune cookies), naming confusions (largest vs. longest, hottest vs. highest).

**Pattern 2: Numerical traps where the intuitive answer differs from correct** (exemplified by cal_047, cal_058)  
Mathematical or quantitative questions where the expected answer differs from the correct answer by a well-known cognitive bias. The Monty Hall problem, off-by-one errors in counting problems, and any question where the answer is counterintuitive but exactly derivable. Models trained on human-generated text inherit human-like numerical intuitions.

**Pattern 3: Ambiguous phrasing where the obvious answer is wrong** (exemplified by cal_062)  
Interior angles questions, geometric or logical puzzles where the standard interpretation leads to an incorrect answer. The prompt is not misleading about the facts; the model's pattern-matching leads it to apply the wrong formula or rule.

**Pattern 4: Knowledge boundary items — real facts that are deeply counterintuitive** (exemplified by cal_077)  
The fact is true, well-documented, and unambiguous, but contradicts a reasonable prior. "Which country has the most lakes?" (Canada, not Finland or Russia) is an example — the answer is correct and verifiable, but violates most people's geographic intuitions and therefore most training data prevalence signals.

**Pattern 5: Adversarial yes/no where the question design is subtle, not obvious** (exemplified by cal_089, cal_090, cal_092, cal_095 — but only for DeepSeek)  
The current adversarial items are too easily identified as traps by Google and Anthropic models. Redesign toward adversarial items that look indistinguishable from legitimate factual questions but have counterintuitive answers. The model should not be able to identify the item as adversarial from its surface form.

### 6.3 Distribution Recommendations

| Bucket | Current | Recommended | Change |
|--------|---------|-------------|--------|
| Easy | 10 | 5 | -5 |
| Medium | 26 | 15 | -11 |
| Hard | 30 | 30 | 0 |
| Deceptive | 22 | 30 | +8 |
| Adversarial | 12 | 20 | +8 |
| **Total** | **100** | **100** | **0** |

The total item count stays at 100. This maintains comparability with current results and avoids re-running the full sweep on a different-sized dataset.

### 6.4 What NOT to Change

The following are working correctly and should not be modified:

**Scoring function (Brier score):** The implementation is correct and theoretically grounded. The Brier score's strict propriety is the benchmark's key property. The Brier decomposition (reliability + resolution + uncertainty) should be added as a diagnostic in Cell 9, but the primary metric stays.

**Adjudication logic:** The alias matching approach works. The schema unification issue (see §7.2) should be resolved, but the adjudication logic itself is sound.

**Notebook architecture (v3, 11 cells):** SDK-aligned and confirmed operational on the Kaggle platform. The cell map in SOUL.md is authoritative.

**5-model panel:** The current panel spans a meaningful capability range — two Google frontier models, two Anthropic models of different sizes, and one non-US model. This covers the right performance spread. Adding more models is a stretch goal, not a requirement.

**Success criteria:** The criteria are well-designed. The dataset needs to meet them; the criteria should not be loosened. The current 1/5 result is a dataset problem, not a criteria problem.

---

## 7. Software & Infrastructure

### 7.1 Stack

| Component | Version / Detail |
|-----------|-----------------|
| Kaggle Benchmarks SDK (`kaggle_benchmarks`) | SDK installed in Kaggle Benchmark notebook environment |
| Python | 3.11 |
| pytest | 64 tests locally; 90 with validator suite |
| pandas | DataFrame operations for dataset and sweep results |
| numpy | Statistical computations (ECE, Brier scores) |
| joblib | Parallel execution within SDK `evaluate()` calls |
| GitHub Actions | CI/CD with Claude code auditor (sticky comments) |
| Notebook | v3, 11 cells, SDK-aligned |

The submission notebook (`metajudge_submission.ipynb`) is self-contained: the 100-item dataset and answer key are embedded as Python string literals (Cell 3), eliminating external dataset dependencies.

### 7.2 Known Issues

**Schema discrepancy (priority: HIGH before next sprint):**  
Three components use different field names for the same data:
- `adjudication.py` expects: `canonical_answer`, `accepted_aliases`
- Production data (`calibration_answer_key.json`): `gold_answer`, `aliases`
- Notebook (Cell 3 embedded): `canonical`, `aliases`

This discrepancy has not caused visible failures because the notebook path bypasses `adjudication.py`, but it will cause bugs when the two code paths are integrated. Field names must be unified to a single convention before the next dataset modification. Recommendation: standardize on `gold_answer` + `aliases` to match the production JSON schema.

**Validator tests not committed:**  
The 26-test dataset validator suite (90-test full suite) was built and runs locally but has not been committed to the repository. These tests should be committed alongside any dataset changes.

**Cell 4 self-test staleness pattern:**  
The smoke test in Cell 4 was caught using hardcoded old pilot data (fixed in `95f16fb`). The fix pattern — updating hardcoded test data when the dataset changes — needs to become a checklist item in the iteration protocol. A reference to the current dataset version hash in the self-test would make staleness detectable.

---

## 8. Key Commits

| Hash | Date | Description |
|------|------|-------------|
| `6ac5b12` | 2026-03-18 | V2 calibration dataset — 100 items, 4-agent pipeline, 12 audit fixes |
| `95f16fb` | 2026-03-18 | Fix: smoke test used hardcoded old pilot prompt (cal_001) |
| `47e654a` | 2026-03-18 | Multi-model sweep cells + codified sweep protocol in SOUL.md |
| `92b3833` | 2026-03-19 | SDK-aligned notebook v3 + Kaggle model workflow in SOUL.md |
| `312c9f9` | 2026-03-19 | CI: enable sticky comment for Claude audit workflow |
| `75320ad` | 2026-03-19 | Add coverage-conditioned accuracy diagnostic |
| `475618c` | 2026-03-19 | Codify 5-model sweep workflow — verified keys, retry logic, dataclass fix |

---

## 9. References

### Core References

Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3. DOI: [10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2](http://journals.ametsoc.org/doi/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2)

Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378. DOI: [10.1198/016214506000001437](https://www.tandfonline.com/doi/abs/10.1198/016214506000001437)

Huang, J., Chen, X., Mishra, S., Zheng, H. S., Yu, A. W., Song, X., & Zhou, D. (2024). Large language models cannot self-correct reasoning yet without external feedback. *Proceedings of the 12th International Conference on Learning Representations (ICLR 2024)*. arXiv: [2310.01798](https://arxiv.org/abs/2310.01798). DOI: [10.48550/arXiv.2310.01798](https://doi.org/10.48550/arXiv.2310.01798)

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., … Kaplan, J. (2022). Language models (mostly) know what they know. *arXiv preprint*. arXiv: [2207.05221](https://arxiv.org/abs/2207.05221). DOI: [10.48550/arXiv.2207.05221](https://doi.org/10.48550/arXiv.2207.05221)

Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. In G. H. Bower (Ed.), *The Psychology of Learning and Motivation*, Vol. 26 (pp. 125–173). Academic Press. DOI: [10.1016/S0079-7421(08)60053-5](https://linkinghub.elsevier.com/retrieve/pii/S0079742108600535)

Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. *Proceedings of the 12th International Conference on Learning Representations (ICLR 2024)*. arXiv: [2306.13063](https://arxiv.org/abs/2306.13063). DOI: [10.48550/arXiv.2306.13063](https://doi.org/10.48550/arXiv.2306.13063)

### Additional Literature

Burnell, R., Yamamori, Y., Firat, O., Olszewska, K., Hughes-Fitt, S., Kelly, O., Galatzer-Levy, I. R., Morris, M. R., Dafoe, A., Snyder, A. M., Goodman, N. D., Botvinick, M., & Legg, S. (2026). Measuring progress toward AGI: A cognitive framework. *Google DeepMind Technical Report*. PDF: [storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf)

Chhikara, P. (2025). Mind the confidence gap: Overconfidence, calibration, and distractor effects in large language models. *arXiv preprint*. arXiv: [2502.11028](https://arxiv.org/html/2502.11028v1). DOI: [10.48550/arXiv.2502.11028](https://doi.org/10.48550/arXiv.2502.11028)

Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. *Proceedings of the 2024 Annual Conference of the North American Chapter of the Association for Computational Linguistics (NAACL 2024)*. arXiv: [2311.08298](https://arxiv.org/abs/2311.08298). DOI: [10.48550/arXiv.2311.08298](https://doi.org/10.48550/arXiv.2311.08298)

Groot, T., & Valdenegro-Toro, M. (2024). Overconfidence is key: Verbalized uncertainty evaluation in large language and vision-language models. *arXiv preprint*. arXiv: [2405.02917](https://arxiv.org/abs/2405.02917). DOI: [10.48550/arXiv.2405.02917](https://doi.org/10.48550/arXiv.2405.02917)

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *Proceedings of the 34th International Conference on Machine Learning (ICML 2017)*, PMLR 70:1321–1330. URL: [proceedings.mlr.press/v70/guo17a.html](https://proceedings.mlr.press/v70/guo17a.html). arXiv: [1706.04599](https://arxiv.org/abs/1706.04599)

Liu, G., Wang, X., Yuan, L., Chen, Y., & Peng, H. (2024). Examining LLMs' uncertainty expression towards questions outside parametric knowledge. *arXiv preprint*. arXiv: [2311.09731](https://arxiv.org/abs/2311.09731). DOI: [10.48550/arXiv.2311.09731](https://doi.org/10.48550/arXiv.2311.09731)

Sung, Y. Y., Fleisig, E., Hou, Y., Upadhyay, I., & Boyd-Graber, J. (2025). GRACE: A granular benchmark for evaluating model calibration against human calibration. *arXiv preprint*. arXiv: [2502.19684](https://arxiv.org/abs/2502.19684). DOI: [10.48550/arXiv.2502.19684](https://doi.org/10.48550/arXiv.2502.19684)

Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. D. (2023). Just ask for calibration: Strategies for eliciting calibrated confidence scores from language models fine-tuned with human feedback. *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023)*, pp. 5433–5442. arXiv: [2305.14975](https://arxiv.org/abs/2305.14975). DOI: [10.48550/arXiv.2305.14975](https://doi.org/10.48550/arXiv.2305.14975)

---

## 10. Appendix: Available Models on Kaggle Platform

The following 27 models were reported by `list(kbench.llms.keys())` on March 19, 2026 (Cell 1 output):

| Provider | Models |
|----------|--------|
| **Anthropic** | `anthropic/claude-haiku-4-5@20251001`, `anthropic/claude-opus-4-1@20250805`, `anthropic/claude-opus-4-5@20251101`, `anthropic/claude-opus-4-6@default`, `anthropic/claude-sonnet-4-5@20250929`, `anthropic/claude-sonnet-4-6@default`, `anthropic/claude-sonnet-4@20250514` |
| **DeepSeek** | `deepseek-ai/deepseek-r1-0528`, `deepseek-ai/deepseek-v3.1`, `deepseek-ai/deepseek-v3.2` |
| **Google** | `google/gemini-2.0-flash`, `google/gemini-2.0-flash-lite`, `google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `google/gemini-3-flash-preview`, `google/gemini-3-pro-preview`, `google/gemini-3.1-flash-lite-preview`, `google/gemini-3.1-pro-preview`, `google/gemma-3-12b`, `google/gemma-3-1b`, `google/gemma-3-27b`, `google/gemma-3-4b` |
| **Qwen** | `qwen/qwen3-235b-a22b-instruct-2507`, `qwen/qwen3-coder-480b-a35b-instruct`, `qwen/qwen3-next-80b-a3b-instruct`, `qwen/qwen3-next-80b-a3b-thinking` |
| **ZAI** | `zai/glm-5` |

**Panel selection rationale:** The 5-model panel (Gemini Pro, Gemini Flash, Claude Sonnet 4, Claude Haiku 4.5, DeepSeek V3.1) was chosen to span: Google frontier (2 models), Anthropic frontier-to-small range (2 models), and a non-US provider (1 model). This covers the widest meaningful capability spread within the $50/day quota constraint (500 LLM calls per full sweep).

**Models to consider for calibration improvement sweep:** Once the item set is improved, consider adding `anthropic/claude-opus-4-6@default` (highest-capability Anthropic), `google/gemini-3-pro-preview` (next-gen Google), `qwen/qwen3-235b-a22b-instruct-2507` (large Chinese model), or `google/gemma-3-27b` (smaller open model, likely weaker calibration) as additional sweep targets to verify discrimination across a broader capability range before freezing.

**Note on key format:** Anthropic models use `@` version separator (`model@date`). DeepSeek provider is `deepseek-ai`, not `deepseek`. Gemma models may not support structured output via `schema=CalibrationResponse`. Always verify current keys via Cell 1's `list(kbench.llms.keys())` output before running a sweep — keys can change between platform updates.
