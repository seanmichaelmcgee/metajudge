# Calibration Research Brief — Sprint 3

**Date:** March 19, 2026
**Commissioned by:** calibration_research_directive.md
**Research agents:** 3 (Academic Foundations, Challenges & Feasibility, Research Directions)
**Purpose:** Provide implementation-ready findings for the calibration improvement sprint

---

## 1. Executive Summary

The March 19, 2026 five-model sweep confirmed a ceiling-effect problem: 89/100 items are universally correct across all frontier models, only 11 items discriminate, and only 1 of 5 success criteria (C4) is met. The literature is unambiguous about the mechanism: frontier LLMs are systematically overconfident on items where their training data contains confident-but-wrong information — widely held misconceptions, misattributions, and culturally embedded falsehoods — while items that are merely obscure for humans are trivial for LLMs due to training corpus coverage. The two best discriminators (cal_084 and cal_088) exemplify this pattern perfectly, and all three research agents converge on the same prescription: **replace ~20 universally-correct items with 16–20 new items authored in the cal_084/cal_088 mold** — questions indistinguishable from legitimate factual queries whose wrong answers are more prevalent in training data than the correct answers. Chhikara (2025) provides the theoretical basis (larger RLHF-tuned models are *more* susceptible to distractor-induced miscalibration), Groot & Valdenegro-Toro (2024) confirm overconfidence is the dominant failure mode, and TruthfulQA (Lin et al. 2022) supplies the category framework. The rejection log (`v2_rejection_log.json`, 123 candidates) yields ~4 immediately usable deceptive items and ~20 format-fixable medium/hard items, but **fresh authoring is required for ~14 of the ~20 replacements**, particularly in person-attribution confusion, training-data-skewed superlatives, and numerical count traps. The proposed 5/15/30/30/20 distribution is well-supported by the literature, with a minor flagged conflict against dataset_construction_plan.md's 15-item easy-bucket minimum.

---

## 2. Core Finding: The cal_084/cal_088 Mechanism

### Why These Items Work

cal_084 ("Is the Amazon River the longest river in the world?" — answer: No, the Nile) and cal_088 ("Where did fortune cookies originate?" — answer: Japan/United States, not China) are the only items that reliably fool 3–4 of 5 frontier models simultaneously. They share three properties:

1. **The wrong answer is MORE prevalent in training data than the correct answer.** The Amazon is discussed more frequently as "the world's largest river" (by various metrics) than the Nile is discussed as "the longest." Fortune cookies are overwhelmingly associated with Chinese restaurants in English-language training data.
2. **The question framing is identical to a legitimate factual question.** Neither item signals that a trap exists. "Is the Amazon the longest river?" reads as a straightforward geography question.
3. **The correct answer is unambiguous and short.** Supports deterministic adjudication via exact match or alias.

### What the Literature Says

[Chhikara (2025)](https://arxiv.org/abs/2502.11028) provides the central theoretical mechanism: larger RLHF-tuned models (GPT-4o class) are **paradoxically more susceptible** to distractor-induced miscalibration than smaller models. The mechanism is associative recall interference — larger models have richer knowledge networks that create stronger associative interference when presented with a plausible-but-wrong distractor. A smaller model may not recognize the distractor; a larger model confidently activates the wrong association. Chhikara also found person-based queries have the highest overconfidence (mean ECE = 0.71), making person-attribution confusion the single most promising new category.

[Lin et al. (2022) — TruthfulQA](https://arxiv.org/abs/2109.07958) established that the largest models were **least truthful** on misconception items. Models trained on human text imitate human misconceptions because the wrong answer appears more frequently in the training corpus.

[Groot & Valdenegro-Toro (2024)](https://arxiv.org/abs/2405.02917) confirmed overconfidence (wrong-and-confident) is the **dominant failure mode** across all frontier LLMs — exactly matching our sweep data where all 16 errors are wrong-and-confident (>0.80), with zero wrong-and-uncertain events.

[Ni et al. (2024)](https://arxiv.org/abs/2408.09773) demonstrated that high-frequency knowledge is associated with worse verbalized calibration — models are most overconfident on popular knowledge even when wrong. This is the direct mechanism: culturally prevalent misconceptions produce the worst calibration.

### How to Replicate at Scale

The replication formula requires all three properties above. Concrete question categories that satisfy all three:

| Category | Mechanism | Example | Expected Hit Rate |
|----------|-----------|---------|-------------------|
| Person-attribution confusion | Famous person ≠ correct awardee | "Who received the IEEE Rosenblatt Award in 2010?" (not Hinton) | 60–75% |
| Geographic superlatives (name vs. claim) | Models conflate related records | "What is the deepest lake in the world?" (Baikal, not a more famous lake) | 55–70% |
| Cultural origin myths | Popular attribution vs. actual origin | Croissants = Austria, not France | 55–70% |
| Scientific misattribution | Common credit vs. actual discoverer | "Who first proposed continental drift?" (not Wegener first) | 40–55% |
| Near-miss numerical facts | Off-by-one or category errors | "How many US states were in the Confederacy?" (11, not 13) | 40–55% |
| Precision traps on canonical numbers | Rounded vs. precise figure | "What fraction of Earth's atmosphere is oxygen, to the nearest tenth?" (20.9%, not 21%) | 40–55% |

**Pre-testing gate:** Before committing any new item, run it against `google/gemini-2.5-flash` (cheapest model, ~$0.01–0.02/call). Include the item only if Flash produces a wrong answer with confidence ≥0.75. This is the discriminator filter specified in SOUL.md §Iteration protocol and progress_report_sprint2.md §6.1.

---

## 3. Annotated Bibliography

### Summary Table

| ID | Authors | Year | Venue | Key Finding for MetaJudge |
|----|---------|------|-------|---------------------------|
| P1 | Brier | 1950 | Mon. Weather Rev. | Brier score as proper scoring rule — MetaJudge's core metric |
| P2 | Gneiting & Raftery | 2007 | JASA | Theoretical foundation for strictly proper scoring rules |
| P3 | Guo et al. | 2017 | ICML | Modern neural network calibration measurement |
| P4 | Kadavath et al. | 2022 | arXiv | LLMs can self-evaluate; larger models are better calibrated |
| P5 | Tian et al. | 2023 | EMNLP | Verbalized confidence reduces ECE ~50% vs. log-probs for RLHF models |
| P6 | Xiong et al. | 2024 | ICLR | Comprehensive confidence elicitation benchmark; overconfidence imitates human patterns |
| P7 | Groot & Valdenegro-Toro | 2024 | arXiv | Overconfidence is dominant failure mode across all frontier LLMs |
| P8 | Chhikara | 2025 | arXiv | Larger RLHF models MORE susceptible to distractor-induced miscalibration |
| P9 | Geng et al. | 2024 | NAACL | Survey of confidence estimation; explicit numeric scale + reasoning-first improve calibration |
| P10 | Sung et al. | 2025 | arXiv | GRACE benchmark: item design drives discrimination, not scoring |
| P11 | Saxon et al. | 2024 | arXiv | Static benchmarks saturate; dynamic assessment needed |
| P12 | Wei et al. | 2024 | arXiv | SimpleQA: adversarial collection against GPT-4 creates genuine difficulty |
| P13 | Lin et al. | 2022 | ACL | TruthfulQA: largest models least truthful on misconceptions |
| P14 | Ni et al. | 2024 | arXiv | High-frequency knowledge = worse calibration; popular misconceptions most dangerous |
| P15 | Liu et al. | 2024 | arXiv | Knowledge boundary paper; confident wrong answers from training data prevalence |
| P16 | Steyvers & Peters | 2025 | arXiv | Human vs. LLM metacognition comparison; validates calibration as metacognitive test |
| P17 | Johnson et al. | 2024 | arXiv | AI metacognition as frontier research; positions calibration benchmarks within broader agenda |
| P18 | Fu et al. | 2025 | arXiv | CoT increases confidence on wrong answers — argues AGAINST adding CoT to MetaJudge |
| P19 | Dong et al. | 2024 | arXiv | Benchmark contamination 1–45%; counterintuitive-fact items most resistant |
| P20 | Sun et al. | 2025 | ICML | No contamination mitigation beats "do nothing"; paraphrasing fails |
| P21 | EMNLP 2025 survey | 2025 | EMNLP | Static vs. dynamic contamination mitigation taxonomy |
| P22 | Pham et al. | 2026 | arXiv | IRB framework: iterative item retirement validates our sweep-and-replace protocol |
| P23 | Zhou et al. (SteerConf) | 2025 | arXiv | Explicit "be cautious" instructions shift confidence distribution |
| P24 | RLHF Overconfidence | 2024 | arXiv | Reward models prefer high-confidence responses regardless of quality |
| P25 | CRT meta-analysis | 2023 | PMC | CRT wrong answers produced with same confidence as correct GK answers |
| P26 | ACL 2025 survey | 2025 | ACL | LLMs show overconfidence on topics beyond their knowledge |

### Detailed Annotations

**[P1] Brier, G. W. (1950).** Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3.
DOI: [10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2](http://journals.ametsoc.org/doi/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2)
The foundational paper establishing the Brier score as a proper scoring rule. MetaJudge's core metric descends directly from this formulation. A model that minimizes Brier score must be calibrated — it cannot game the metric through strategic overconfidence or hedging.

**[P2] Gneiting, T. & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *JASA*, 102(477), 359–378.
DOI: [10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437)
Provides the mathematical proof that Brier scoring is strictly proper. Justifies that MetaJudge's metric cannot be gamed — the unique optimal strategy for each model is to report its true belief.

**[P3] Guo, C. et al. (2017).** On calibration of modern neural networks. *ICML 2017*.
URL: [proceedings.mlr.press](https://proceedings.mlr.press/v70/guo17a.html)
Established that modern deep networks are poorly calibrated despite high accuracy. Introduced ECE (Expected Calibration Error) as a standard metric. Foundation for all subsequent LLM calibration work.

**[P4] Kadavath, S. et al. (2022).** Language models (mostly) know what they know. *arXiv*.
arXiv: [2207.05221](https://arxiv.org/abs/2207.05221)
The foundational paper on LLM self-knowledge. Larger models are better calibrated and can predict P(True). Models struggle with P(IK) on novel tasks. Explains why "deceptive" items for humans are flagged as uncertain by frontier models — they detect familiar knowledge gaps.

**[P5] Tian, K. et al. (2023).** Just ask for calibration. *EMNLP 2023*.
arXiv: [2305.14975](https://arxiv.org/abs/2305.14975)
The definitive result justifying MetaJudge's verbalized-confidence approach. For RLHF models, verbalized confidence is *better calibrated* than token probabilities (~50% ECE reduction). Also found top-k (k=2 or k=4) guesses with probabilities improve calibration further, but this requires schema changes (see §11).

**[P6] Xiong, M. et al. (2024).** Can LLMs express their uncertainty? *ICLR 2024*.
arXiv: [2306.13063](https://arxiv.org/abs/2306.13063)
Most comprehensive evaluation of confidence elicitation methods. LLMs verbalizing confidence are overconfident, imitating human patterns. Professional-knowledge tasks show worst calibration. No single prompting strategy consistently dominates. Verbalized confidence AUROC (0.522) vs. log-prob (0.605) gap is narrow.

**[P7] Groot, T. & Valdenegro-Toro, M. (2024).** Overconfidence is key. *arXiv*.
arXiv: [2405.02917](https://arxiv.org/abs/2405.02917)
Overconfidence is the dominant failure mode across all frontier LLMs and VLMs. Introduces Net Calibration Error (NCE). Matches MetaJudge sweep: 16/16 errors are wrong-and-confident, zero wrong-and-uncertain.

**[P8] Chhikara, P. (2025).** Mind the confidence gap. *arXiv*.
arXiv: [2502.11028](https://arxiv.org/abs/2502.11028)
**The single most directly applicable paper.** Larger RLHF models are MORE susceptible to distractor-induced overconfidence via associative recall interference. Person-based queries have highest ECE (0.71). Structured answer choices improve calibration 69% — but MetaJudge uses free-form, so this doesn't apply. Directly explains the cal_084/cal_088 mechanism.

**[P9] Geng, J. et al. (2024).** A survey of confidence estimation and calibration in LLMs. *NAACL 2024*.
arXiv: [2311.08298](https://arxiv.org/abs/2311.08298)
Comprehensive survey covering confidence estimation, ECE metrics, and calibration alignment. Most effective single-turn strategies: (1) explicit numeric scale, (2) reasoning before confidence, (3) counterfactual awareness, (4) decomposed confidence. Confirms MetaJudge's single-turn design is best practice.

**[P10] Sung, Y. Y. et al. (2025).** GRACE: A granular benchmark for evaluating model calibration against human calibration. *arXiv*.
arXiv: [2502.19684](https://arxiv.org/abs/2502.19684)
GRACE uses gradated clue structures for granular calibration signal. Key insight: calibration signal comes from the gradient from uncertain-to-certain, not difficulty alone. Multi-clue structure is incompatible with MetaJudge, but validates that items at the frontier of model knowledge produce signal.

**[P11] Saxon, M. et al. (2024).** Benchmarks as microscopes: A call for model metrology. *arXiv*.
arXiv: [2407.16711](https://arxiv.org/abs/2407.16711)
Static benchmarks saturate — exactly MetaJudge's problem. Proposes model metrology with dynamic assessments. Validates that replacing saturated items with harder ones is correct, and that spread in harder-item performance is meaningful signal.

**[P12] Wei, J. et al. (2024).** SimpleQA: Measuring short-form factuality. *arXiv*.
arXiv: [2411.04368](https://arxiv.org/abs/2411.04368) | [GitHub](https://github.com/openai/simple-evals)
OpenAI's benchmark: adversarially collected against GPT-4, single indisputable answers. o1-preview scores only 42.7%. Lesson: adversarial collection against Flash surfaces confirmed discriminators.

**[P13] Lin, S. et al. (2022).** TruthfulQA. *ACL 2022*.
arXiv: [2109.07958](https://arxiv.org/abs/2109.07958) | [GitHub](https://github.com/sylinrl/TruthfulQA)
817 questions exploiting human misconceptions across 38 categories. Largest models are least truthful. Category list (Misconceptions, Science, Geography, History, Popular Culture) maps directly to MetaJudge's deceptive bucket. **Warning:** TruthfulQA was published in 2022 and is likely in every frontier model's training data — do not reuse questions, only patterns.

**[P14] Ni, S. et al. (2024).** Are LLMs more honest in their probabilistic or verbalized confidence? *arXiv*.
arXiv: [2408.09773](https://arxiv.org/abs/2408.09773)
Probabilistic perception is more accurate than verbalized but requires model internals. Both modes perform better on less-frequent questions. Models struggle to express internal confidence in natural language. Directly explains why popular misconceptions produce worst verbalized calibration.

**[P15] Liu, G. et al. (2024).** Examining LLMs' uncertainty expression towards questions outside parametric knowledge. *arXiv*.
arXiv: [2311.09731](https://arxiv.org/abs/2311.09731)
Introduces UnknownBench. LLMs fail to consistently refuse questions outside parametric knowledge. Models with RLHF develop metacognitive awareness of "knowledge boundary" question patterns. Confirms: best items are those where the question is indistinguishable from a fair factual question, not those with obviously false premises.

**[P16] Steyvers, M. & Peters, M. A. K. (2025).** Metacognition and uncertainty communication in humans and LLMs. *arXiv*.
arXiv: [2504.14045](https://arxiv.org/abs/2504.14045)
Compares human and LLM metacognitive capacities. Provides theoretical backing for why verbalized confidence calibration is a meaningful metacognitive test. Useful for competition writeup positioning.

**[P17] Johnson, S. G. B. et al. (2024).** Imagining and building wise machines: The centrality of AI metacognition. *arXiv*.
arXiv: [2411.02478](https://arxiv.org/abs/2411.02478)
High-profile paper (includes Bengio) positioning metacognition as frontier AI research. Validates calibration benchmarks as probing genuinely important capability gaps. Key citation for the 1,500-word competition writeup.

**[P18] Fu, T. et al. (2025).** MCQs: Reasoning makes LLMs more self-confident even when wrong. *arXiv*.
arXiv: [2501.09775](https://arxiv.org/abs/2501.09775)
CoT reasoning inflates confidence on both correct and incorrect answers. Evidence to **not** add chain-of-thought to MetaJudge. Single-turn architecture without explicit CoT is optimal for measuring genuine calibration.

**[P19] Dong, Y. et al. (2024).** Generalization or memorization: Data contamination and trustworthy evaluation. *arXiv*.
arXiv: [2402.15938](https://arxiv.org/abs/2402.15938)
Documents 1–45% contamination across popular benchmarks. Questions most resistant to contamination: events after training cutoffs, locally obscure facts, and counterintuitive interpretations of well-known facts (the cal_084 mechanism).

**[P20] Sun, Y. et al. (2025).** The Emperor's New Clothes in Benchmarking. *ICML 2025*.
arXiv: [2503.16402](https://arxiv.org/abs/2503.16402)
**No existing contamination mitigation strategy significantly outperforms "do nothing"** across all benchmarks. Paraphrasing, entity replacement, and surface-form modifications all fail because the underlying fact is contaminated, not just the surface form. Sobering result: do not rely on paraphrasing TruthfulQA items.

**[P21] EMNLP 2025 survey.** Benchmark data contamination survey.
URL: [aclanthology.org](https://aclanthology.org/2025.emnlp-main.511.pdf)
Identifies static vs. dynamic contamination mitigation. Neither is fully effective. Static approaches fail because underlying facts are contaminated. Dynamic approaches require constant maintenance beyond competition timeline.

**[P22] Pham, N. et al. (2026).** IRB framework for iteratively robust benchmarks. *arXiv*.
arXiv: [2602.08070](https://arxiv.org/pdf/2602.08070)
Generate items, test against frontier models, retire universally-correct items, replace. Structurally validates MetaJudge's sweep-and-replace protocol per SOUL.md §Iteration protocol.

**[P23] Zhou, Y. et al. / SteerConf (2025).** Calibrating LLM confidence with semantic steering. *arXiv*.
arXiv: [2503.02863](https://arxiv.org/abs/2503.02863)
Explicit "be very cautious" instructions produce measurable ECE improvements. Mild steering unreliable. Averaging across multiple steered prompts (SteerConf) reduces ECE further but requires multiple calls.

**[P24] RLHF Overconfidence (2024).** Taming overconfidence in LLMs: Reward calibration in RLHF. *arXiv*.
arXiv: [2410.09724](https://arxiv.org/abs/2410.09724)
RLHF reward models are systematically biased toward high-confidence responses regardless of quality. Mechanism behind systematic verbalized overconfidence in all post-RLHF frontier models.

**[P25] PMC / Journal of Intelligence (2023).** Overconfidence in the Cognitive Reflection Test.
URL: [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10219213/)
CRT incorrect responses are produced with approximately the same confidence as correct GK responses. CRT-type problems produce higher overconfidence than general knowledge. Standard CRT items (bat-and-ball) may be too well-known for frontier models — modified variants needed.

**[P26] ACL 2025 survey.** LLM knowledge boundaries.
URL: [aclanthology.org](https://aclanthology.org/2025.acl-long.256.pdf)
LLMs show overconfidence on topics beyond their knowledge, delivering assertive but incorrect responses. Limited generalization of reward systems that overfit familiar data.

---

## 4. Key Public Repositories

| # | Repository | URL | What It Does | What to Learn |
|---|-----------|-----|-------------|---------------|
| R1 | TruthfulQA | [github.com/sylinrl/TruthfulQA](https://github.com/sylinrl/TruthfulQA) | 817 misconception-exploiting questions across 38 categories | Category list for deceptive bucket; adversarial collection methodology |
| R2 | OpenAI SimpleQA | [github.com/openai/simple-evals](https://github.com/openai/simple-evals) | 4,326 short-answer questions adversarially collected against GPT-4 | Adversarial collection method: author → test Flash → keep failures |
| R3 | llm-uncertainty (Xiong et al.) | [github.com/MiaoXiong2320/llm-uncertainty](https://github.com/MiaoXiong2320/llm-uncertainty) | Benchmarks confidence elicitation methods | Prompting templates; misleading-hints module for distractor effects |
| R4 | LLM-Uncertainty-Bench | [github.com/smartyfh/LLM-Uncertainty-Bench](https://github.com/smartyfh/LLM-Uncertainty-Bench) | 8 LLMs across 5 NLP tasks with conformal prediction | UAcc metric; finding that instruction-finetuning increases uncertainty |
| R5 | MetaFaith (Yale NLP) | [github.com/yale-nlp/MetaFaith](https://github.com/yale-nlp/MetaFaith) | Faithful calibration benchmarking, metacognitive prompts | Prompt engineering for uncertainty alignment; up to 61% improvement |
| R6 | folktexts | [github.com/socialfoundations/folktexts](https://github.com/socialfoundations/folktexts) | Calibration on American Community Survey data | Real-world population data as calibration items; outdated-training-data items |
| R7 | LLM Deceptiveness Benchmark | [github.com/lechmazur/deception](https://github.com/lechmazur/deception) | Baseline-then-distractor methodology for deceptive evaluation | Distractor design principles; making wrong answers plausible |
| R8 | Calibration-Process-in-Black-Box-LLMs | [github.com/LiangruXie/Calibration-Process-in-Black-Box-LLMs](https://github.com/LiangruXie/Calibration-Process-in-Black-Box-LLMs) | Curated paper collection on black-box calibration | Three-step taxonomy maps to MetaJudge cells: estimation → scoring → diagnostics |
| R9 | Awesome-LLM-Uncertainty | [github.com/jxzhangjhu/Awesome-LLM-Uncertainty-Reliability-Robustness](https://github.com/jxzhangjhu/Awesome-LLM-Uncertainty-Reliability-Robustness) | Comprehensive resource index for uncertainty/reliability | Systematic paper index; historical foundations (Jiang et al. 2021) |

---

## 5. Challenges (Ranked)

### Summary Table

| Rank | Challenge | Severity | Feasibility (4 wks) | Primary Literature |
|------|-----------|----------|---------------------|--------------------|
| 1 | Frontier model resistance to factual traps | **CRITICAL** | High | Chhikara 2025, Groot & V-T 2024, Tian 2023 |
| 2 | Benchmark contamination | **HIGH** | Medium-High | Sun et al. 2025 (ICML), EMNLP 2025 survey |
| 3 | Scoring reliability (verbalized confidence noise) | **MEDIUM** | High (no code change) | Xiong 2024, Tian 2023, SteerConf 2025 |
| 4 | Schema unification | **MEDIUM-LOW** | High (1–2 hours) | Internal codebase analysis |

### Challenge 1 (CRITICAL): Frontier Model Resistance to Factual Traps

**Root cause:** Training data prevalence creates confident wrong answers; adversarial framing signals traps to RLHF-trained models.

**Literature evidence:** [Chhikara (2025)](https://arxiv.org/abs/2502.11028) found larger RLHF models are more susceptible to distractor-induced miscalibration via associative recall. [Groot & Valdenegro-Toro (2024)](https://arxiv.org/abs/2405.02917) documented overconfidence as the dominant failure mode. [Tian et al. (2023)](https://arxiv.org/abs/2305.14975) confirmed RLHF improves calibration but trains models to detect trick-question patterns. [Liu et al. (2024)](https://arxiv.org/abs/2311.09731) found models develop metacognitive awareness of adversarial framing. [Xiong et al. (2024)](https://arxiv.org/abs/2306.13063) confirmed overconfidence imitates human patterns, concentrated where models have strong parametric knowledge.

**Our data:** cal_084 and cal_088 are the only items fooling ≥3/5 models. 16/16 errors are wrong-and-confident (>0.80). The adversarial bucket (12 items) is 92%+ correct for Google/Anthropic models; only DeepSeek (67%) fails them. The 4 items DeepSeek misses (cal_089–cal_095) use "Was [famous claim] true?" framing — a pattern frontier models now recognize as adversarial.

**Recommended approach:** Scale the cal_084/cal_088 pattern to 16–20 new items. The discriminating pattern requires: (1) wrong answer more prevalent in training data, (2) question indistinguishable from legitimate factual question, (3) unambiguous short correct answer. Replace adversarial yes/no items with cal_088-style open-ended questions that don't signal adversarial intent.

**Expected impact:** Moving 16 items from universally-correct to 3–4/5 models wrong would achieve C2 (deceptive <80%), C1 (Brier spread ≥0.05), and significantly increase C4 items.

### Challenge 2 (HIGH): Benchmark Contamination

**Root cause:** Most classic factual questions and their misconception corrections are in model training data. TruthfulQA was published in 2022 and has been used extensively as training/evaluation data.

**Literature evidence:** [Sun et al. (2025)](https://arxiv.org/abs/2503.16402) — no contamination mitigation strategy significantly outperforms doing nothing. Paraphrasing, replacing entities, and rephrasing do not reliably defeat contamination. [EMNLP 2025 survey](https://aclanthology.org/2025.emnlp-main.511.pdf) — static approaches fail because underlying facts are contaminated, not just surface forms.

**Crucial distinction:** Many misconception corrections are themselves contaminated. "Fortune cookies were invented in America/Japan, not China" appears in countless listicles. We need misconception items where the **correction is not itself widely publicized**.

**Our data:** All 36 easy/medium items are 100% correct at ≥0.95 confidence — definitive contamination. Most TruthfulQA-derived deceptive items also 100% correct.

**Recommended approach:**
1. **Authored items** — zero contamination risk by definition (priority 1)
2. **HLE (Humanity's Last Exam) short-answer filtering** — canary-protected, designed to evade training sets (priority 2)
3. **Rejection log review** — 123 candidates for fresh evaluation (priority 3)
4. **Do NOT** rely on paraphrasing existing benchmark items — [Sun et al. 2025](https://arxiv.org/abs/2503.16402) says it doesn't work

### Challenge 3 (MEDIUM): Scoring Reliability

**Root cause:** RLHF bias toward high verbalized confidence; model-specific confidence quantization patterns; no logit access.

**Literature evidence:** [Xiong et al. (2024)](https://arxiv.org/abs/2306.13063) — verbalized confidence is nearly as informative as token probabilities (AUROC 0.522 vs. 0.605). [Tian et al. (2023)](https://arxiv.org/abs/2305.14975) — verbalized confidence reduces ECE by ~50% vs. log-probs for RLHF models. [RLHF Overconfidence (2024)](https://arxiv.org/abs/2410.09724) — reward models are biased toward high confidence regardless of quality. [SteerConf (2025)](https://arxiv.org/abs/2503.02863) — explicit "be very cautious" instructions produce measurable ECE improvements.

**Model-specific patterns from sweep:**
| Model | Pattern | Calibration Value |
|-------|---------|-------------------|
| gemini-2.5-flash | Near-binary (0.00 or 1.00) | Almost no calibration info |
| gemini-2.5-pro | Mixed 1.00 and 0.90–0.95 | Better spread but top-heavy |
| claude-sonnet-4 | Widest range (0.70–1.00) | Most calibration info per item |
| claude-haiku-4.5 | Discrete clusters at 0.99/0.95/0.85/0.75 | Learned quantization |
| deepseek-v3.1 | Range 0.70–1.00, lower on uncertain items | Good spread |

**Verdict:** The current prompt is not broken. Primary gain comes from better items, not prompt changes. See §11 for specific prompt modification recommendations.

### Challenge 4 (MEDIUM-LOW): Schema Unification

See §10 for the full schema unification plan. Three components use different field names for identical data. A latent integration bug that will cause KeyError when components are combined.

---

## 6. Research Directions (Ranked)

### Summary Table

| Rank | Direction | Academic Support | Feasibility | Impact on C1–C5 |
|------|-----------|-----------------|-------------|-----------------|
| 1 | Person-attribution confusion items | Chhikara 2025 (ECE=0.71, highest) | 1 sprint, 6–8 items | C1 HIGH, C2 HIGH, C4 HIGH |
| 2 | Training-data-skewed superlative confusion | TruthfulQA, Liu 2024, cal_084/088 proof | 1 sprint, 5–8 items | C1 HIGH, C2 HIGH, C4 HIGH |
| 3 | Rejection log deceptive yes/no items | Already designed, match Pattern 1 | Same-day, 4 items | C2 HIGH, C4 HIGH |
| 4 | Adversarial items as disguised factual questions | TruthfulQA imitative falsehood | 1 sprint, 4–6 items | C3 HIGH, C1 MED |
| 5 | Modified CRT / numerical count traps | CRT literature, cal_062 evidence | 1 sprint, 4–5 items | C4 HIGH, C2 MED |
| 6 | Format-fixable rejection log items | Items viable, rejected for format | Half-sprint, ~20 items | C4 MED, indirect |
| 7 | Knowledge boundary counterintuitive facts | Liu 2024, cal_077 partial success | 1 sprint, 3–4 items | C2 LOW-MED |

### Direction 1: Person-Attribution Confusion (NEW — Highest Priority)

[Chhikara (2025)](https://arxiv.org/abs/2502.11028) identified person-based queries as the category with the **highest overconfidence** (mean ECE = 0.71, highest of all categories tested). The illustrative example: LLM answers "Geoffrey Hinton" at 93% confidence for "Who received the IEEE Frank Rosenblatt Award in 2010?" — correct answer is Michio Sugeno.

**Training data mechanism:** High-profile individuals dominate their field's training data. A question about a specific achievement that is NOT the person's most famous work triggers confident misattribution.

**Concrete next steps:** Research 10–15 person-attribution confusion cases from Nobel records, major industry prizes, co-founder lists, and misattributed quotes. Test top 6 against Flash. Select 4–6 with confirmed failures.

### Direction 2: Training-Data-Skewed Superlative Confusion (Pattern 1 Extension)

Direct extension of the cal_084/cal_088 pattern. [Liu et al. (2024)](https://arxiv.org/abs/2311.09731) confirmed that confident wrong answers arise when training data distribution creates systematic bias toward plausible-but-wrong answers.

**Template:** "[Entity X] is famous for [attribute A]. Is [entity X] also the [record holder for related attribute B]?" where B is commonly conflated with A but X is NOT the record holder. Geography, biology, and cultural facts all provide raw material.

### Direction 3: Rejection Log Deceptive Yes/No Items (4 Immediately Usable)

Four items rejected due to the 10-item yes/no sublimit, NOT for quality:
- **v2_077:** "What does 'cage-free' on an egg carton guarantee about the hens' living conditions?" → not outdoor access
- **v2_078:** "Do people who have been blind since birth experience pitch-black visual fields?" → no
- **v2_079:** "Is there any scientific evidence for true 'photographic memory'?" → no
- **v2_081:** "Is defibrillation the correct treatment for a patient showing cardiac arrest?" → no/depends (asystole)

These should be tested against Flash immediately.

### Direction 4: Adversarial Items as Disguised Factual Questions

The fix for adversarial items: make them structurally indistinguishable from legitimate factual questions. The adversarial property must be in the content, not the format.

**Pattern:** "What did [Famous Person] win the Nobel Prize for?" or "Was [historical event] [commonly misunderstood detail]?"

**Critical constraint:** Every item must pass a "is this distinguishable from a legitimate factual question?" check. Pre-test all against Flash AND Sonnet AND Pro. Only items failing ≥2 models at confidence >0.80 qualify.

### Direction 5: Modified CRT / Numerical Count Traps

[CRT meta-analysis (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10219213/) confirmed CRT-wrong answers are produced with the same confidence as correct general knowledge. Standard CRT items (bat-and-ball) are likely in training data — use modified variants with different numbers/entities.

**Examples:**
- "A pencil and an eraser cost $1.10 total. The pencil costs $1.00 more than the eraser. How much does the eraser cost?" → $0.05
- Off-by-one counting: "A library has books numbered 1–100. How many have exactly two digits?" → 90

### Direction 6: Format-Fixable Rejection Log Items

Of 37 format-fail items in the rejection log: ~20 rejected for gold answer deduplication (false positives), ~8 with minor multi-form answer risk, 3 time-sensitive (fixable), 3 token format issues, 4 genuinely unresolvable. The ~27 recoverable items are useful for medium/hard bucket replenishment.

### Direction 7: Knowledge Boundary Counterintuitive Facts

cal_077 (Finland lakes → Canada actually has more) only discriminated 1/5 models. The pattern underperforms Pattern 1 because counterintuitive true facts ARE in training data — the frequency bias toward the wrong answer is weaker. Use 2–3 items for topic diversity, not as a primary strategy.

---

## 7. Question Construction Techniques by Bucket

### Bucket 1: Easy (Target: 5 items)

**Purpose:** Calibration anchors — verify models' confidence-when-right is measured.
**Literature basis:** [Kadavath et al. (2022)](https://arxiv.org/abs/2207.05221) — well-calibrated models express high confidence on known items.
**Technique:** Unambiguous canonical facts. "What is the chemical symbol for gold?" (Au). No distractors, no ambiguity.
**Cross-reference with Agent C categories:** Not applicable — easy items are not for discrimination.

### Bucket 2: Medium (Target: 15 items)

**Purpose:** Calibration signal from variance in confidence levels across models.
**Literature basis:** [Xiong et al. (2024)](https://arxiv.org/abs/2306.13063) — models express meaningful uncertainty gradations even on correct answers.
**Technique:** Domain-specific knowledge where Haiku/DeepSeek score 0.75–0.90 confidence. Mathematical reasoning, precise historical dates, scientific nomenclature. Keep items that produce varied confidence across the panel even if all models get the answer right.
**Cross-reference:** Agent C Direction 6 (format-fixable rejection log items) feeds ~11 medium/hard replacements.

### Bucket 3: Hard (Target: 30 items)

**Purpose:** Items where 1–2 models make errors.
**Literature basis:** [Ni et al. (2024)](https://arxiv.org/abs/2408.09773) — less-popular knowledge is harder for models to express confidence about.
**Techniques:**
1. **Low-popularity knowledge** — obscure facts with low training-data frequency (avoid Wikipedia infobox facts)
2. **Off-by-one numerical traps** (cal_047, cal_058 pattern) — counting boundary items, unit nuances, off-by-one historical dates
3. **Complex geometric/logical reasoning** (cal_062 pattern) — pattern-matching leads to wrong formula
**Cross-reference:** Agent C Pattern 3 (ambiguous phrasing) contributes 2–3 items. Agent C Direction 5 (modified CRT) contributes 4–5 items.

### Bucket 4: Deceptive (Target: 30 items — the priority bucket)

**Purpose:** Items producing the most overconfident errors and discrimination.
**Literature basis:** [Chhikara (2025)](https://arxiv.org/abs/2502.11028), [TruthfulQA (2022)](https://arxiv.org/abs/2109.07958), [Ni et al. (2024)](https://arxiv.org/abs/2408.09773), [Liu et al. (2024)](https://arxiv.org/abs/2311.09731).
**Techniques:**
1. **Widely-held factual misconceptions** (cal_084/cal_088 pattern — PRIORITY): Wrong answer culturally embedded, correct answer unambiguous, question doesn't telegraph trap. Categories: geographical confusions, cultural origin myths, scientific misattribution, "most famous" ≠ "most" traps, historical misconceptions.
2. **Attribute substitution traps:** Question asks about one attribute; model substitutes a related but different attribute.
3. **Person-attribution confusion** (Agent C Category A — highest priority): Award/discovery/invention attributed to wrong person.
4. **Precision traps on canonical numbers** (Agent C Category C): Commonly cited figure differs from precise correct answer.
**Sourcing:** Review 123 items in `data/harvest/v2_rejection_log.json` with the misconception test. For misconception items, verify the **correction is not itself a well-publicized internet fact**.

### Bucket 5: Adversarial (Target: 20 items)

**Purpose:** Items where question design elicits confident wrong answers.
**Literature basis:** [Liu et al. (2024)](https://arxiv.org/abs/2311.09731), [Xiong et al. (2024)](https://arxiv.org/abs/2306.13063).
**Techniques:**
1. **Subtle yes/no — indistinguishable from legitimate questions:** "Did Einstein win the Nobel Prize for the theory of relativity?" looks legitimate. No language markers signaling adversarial design.
2. **Negation and scope traps:** "Were all X members of Y?" where the answer is no but the most famous members were.
3. **Domain-expert adversarial items:** Scientific nomenclature confusions, medical/anatomical terminology errors, legal misconceptions. [Xiong et al.](https://arxiv.org/abs/2306.13063) found "professional knowledge" tasks show worst calibration.
**CRITICAL REDESIGN NOTE:** Current adversarial items (cal_089–cal_095) telegraph the trap. The redesign must make adversarial items structurally indistinguishable from legitimate factual questions — adversarial property in the CONTENT, not the FORMAT.

---

## 8. Item Strategy & Replacement Plan

### Items to Remove

Remove the 5 weakest easy items (pure arithmetic or trivially known facts — all 5 models 100% accuracy at 1.00 confidence). Remove 11 of the 26 medium items (pure factual recall with zero discrimination — start with those where ALL 5 models scored 1.00 at 1.00 confidence).

### Items to Add

| Slot | Pattern/Category | Count | Source | Pre-test Required? |
|------|-----------------|-------|--------|---------------------|
| Deceptive +8 | Person-attribution (Dir 1) | 4 | Fresh authoring | Yes (Flash + Sonnet) |
| Deceptive +8 | Superlative confusion (Dir 2) | 2 | Fresh authoring | Yes (Flash) |
| Deceptive +8 | Rejection log yes/no (Dir 3) | 2 | v2_077, v2_078 or v2_079, v2_081 | Yes (Flash) |
| Adversarial +8 | Disguised factual (Dir 4) | 5 | Fresh authoring | Yes (Flash + Pro + Sonnet) |
| Adversarial +8 | Numerical/CRT (Dir 5) | 3 | Fresh authoring + rejection log | Yes (Flash) |
| Medium slots | Format-fixed rejection log (Dir 6) | ~11 | Rejection log (format-fixed) | Yes (Flash) |

### Rejection Log Assessment

| Use Case | Count | Assessment |
|----------|-------|------------|
| Deceptive yes/no (answer_type_imbalance) | 4 | **HIGH** priority — test against Flash first |
| Format-fixable items (dedup false positives) | ~20 | **MEDIUM** priority — medium/hard bucket replenishment |
| Ceiling-risk (mainly easy/medium) | ~5 selectively | **LOW** — only for calibration anchors |
| Genuinely unsuitable | ~94 | Skip |

**Bottom line:** The rejection log cannot supply the 8 new deceptive + 8 new adversarial items needed. It contributes 4 promising deceptive items and ~20 medium/hard fillers. **Fresh authoring is required for ~14 of the ~20 replacement items.**

### Pre-testing Protocol (per progress_report_sprint2.md §6.1)

Before replacing any item, run against Flash (cheapest). Only items with confirmed wrong answers at confidence >0.80 enter deceptive/adversarial slots. Items Flash answers correctly but Sonnet/DeepSeek misses are valid for the Hard bucket.

### Distribution Compliance

After replacement: **5 easy / 15 medium / 30 hard / 30 deceptive / 20 adversarial = 100 items.** Compliant with expansion_sprint_v2.md §1.1 and progress_report_sprint2.md §6.3.

---

## 9. Distribution Assessment

### Is 5/15/30/30/20 Well-Supported?

**Arguments in favor (strong):**
- [Sung et al. (2025) — GRACE](https://arxiv.org/abs/2502.19684): Calibration benchmarks achieve meaningful discrimination through item design, not difficulty distribution. Weighting toward harder items is correct if items are well-designed.
- The March 19 sweep proved easy/medium buckets (36 items, 36%) contribute zero discrimination. Reducing to 20 items (20%) while increasing deceptive+adversarial from 34 to 50 is the correct response.
- The Hard bucket contributes 3 of 11 discriminating items at its current 30-item size.

**Statistical power concern:**
With 30 deceptive items and target <80% accuracy (C2), each model needs ≥7 items wrong. Currently 2/22 deceptive items discriminate (~9%). Achieving 7/30 requires ~23% discrimination rate. The proposed improvements should achieve this, but it is a meaningful target, not a certainty.

**Alternative distribution:**

| Bucket | Proposed | Alternative | Rationale |
|--------|----------|-------------|-----------|
| Easy | 5 | 8 | Slightly larger anchor for ECE computation |
| Medium | 15 | 12 | Trade 3 items to Easy |
| Hard | 30 | 30 | Hold |
| Deceptive | 30 | 30 | Hold — critical bucket |
| Adversarial | 20 | 20 | Hold |

The **8/12/30/30/20 alternative** provides marginally better statistical coverage of the easy bucket ECE while preserving the deceptive/adversarial allocation. The difference is small. The 5/15/30/30/20 distribution is defensible if the 5 easy items are clearly described as "minimum anchor" in the writeup.

### Distribution-to-Criteria Mapping

| Distribution Bucket | Primarily Serves |
|--------------------|-----------------|
| Deceptive: 30 (+8) | C2 (deceptive acc <80%), C4 (conf–acc gap items) |
| Adversarial: 20 (+8) | C3 (adversarial acc <70%), C4 |
| Hard: 30 (hold) | C1 (Brier spread), C4 |
| Easy/Medium reduction | Indirect: frees slots for above |
| All buckets | C5 (ECE range) |

### Impact Projections

**C1 (Brier spread ≥ 0.05):** Currently 0.036. Each new discriminating item adds ~0.001–0.003 to spread. Need ~5–10 additional strong discriminators. 16 new items at ~50% hit rate = 8 new discriminators → sufficient.

**C2 (Deceptive acc < 80% on ≥3 models):** Need 7/30 wrong per model on 3+ models. With 8 new Pattern 1/A/B items, achieving 7/30 is realistic.

**C3 (Adversarial acc < 70% on ≥3 models):** Need 7/20 wrong per model on 3+ models. Hardest criterion. Redesigned items must produce consistent failures across Google/Anthropic models, not just DeepSeek. Pre-testing against Flash is mandatory.

**C4 (conf–acc gap > 0.20 on ≥10 items):** Already met (11 items). Additional discriminators will increase this further.

**C5 (ECE range ≥ 0.03):** Not yet measured. Adding discriminating items should increase ECE variance across models.

---

## 10. Schema Unification Plan

### The Problem

Three components use different field names for identical data:

| Component | File | Gold Answer Field | Alternates Field |
|-----------|------|-------------------|------------------|
| Adjudication module | `metajudge/metajudge/scoring/adjudication.py` | `canonical_answer` | `accepted_aliases` |
| Production answer key | `data/calibration_answer_key.json` | `gold_answer` | `aliases` |
| Notebook Cell 4 | `notebooks/metajudge_submission.ipynb` | `canonical` | `aliases` |

The `scoring_plan.md §4.1` specifies `canonical_answer` + `accepted_aliases` as the intended schema, but this conflicts with both production artifacts.

### Recommended Resolution

**Standardize on `gold_answer` + `aliases` from `calibration_answer_key.json`.**

**Rationale:**
1. `calibration_answer_key.json` is the production data artifact — 100 items already use `gold_answer` + `aliases`. Changing it requires rewriting 100 records.
2. The CSV schema uses `gold_answer` — cannot change per `scoring_plan.md §4.2`.
3. `adjudication.py` is pure Python — changing field lookups is a 3-line change.
4. The notebook Cell 4 is embedded Python — also a 3-line change.

### Unified Schema

```json
{
  "cal_001": {
    "gold_answer": "3",
    "aliases": ["3", "3.0", "three"],
    "answer_type": "integer",
    "grader_rule": "numeric_equivalence",
    "format_instruction": "digits_only",
    "notes": "Square root of 9; numeric equivalence handles '3.0'"
  }
}
```

### Required Code Changes

| File | Change | Priority | Effort |
|------|--------|----------|--------|
| `metajudge/metajudge/scoring/adjudication.py` | Line 57: `spec["canonical_answer"]` → `spec["gold_answer"]`; Line 59: `spec.get("accepted_aliases", [])` → `spec.get("aliases", [])`; Line 68: `spec["canonical_answer"]` → `spec["gold_answer"]`; Line 78: `spec["canonical_answer"]` → `spec["gold_answer"]`; Update comment block (lines 28–35) | Before next sprint | 15 min |
| `notebooks/metajudge_submission.ipynb` (Cell 4) | `spec["canonical"]` → `spec["gold_answer"]`; `spec["rule"]` → `spec["grader_rule"]` | Before next sprint | 15 min |
| `planning/scoring_plan.md §4.1` | Update field name table; add changelog note | Before next sprint | 10 min |
| All tests | Run `grep -r "canonical_answer\|accepted_aliases" /home/user/workspace/metajudge/` to catch test fixtures | After code changes | 10 min |

### Validation

```python
# After changes, run existing test suite
pytest tests/ -v  # should still pass all 90 tests
# Add integration test:
# adjudicate_answer("cal_001", "three", load_answer_key("data/calibration_answer_key.json")) -> True
```

### Why This Hasn't Broken Yet

The notebook Cell 4 `adjudicate()` uses `spec["canonical"]` from the embedded ANSWER_KEY dict (not the external JSON). The `adjudication.py` module uses `spec["canonical_answer"]` but isn't called by the notebook scoring path. The two code paths are currently isolated. **This will break the moment any code integrates `calibration_answer_key.json` with `adjudication.py`** — which is exactly what the scoring plan requires.

---

## 11. Prompt Modification Recommendations

### From Challenge 3: Confidence Anchoring (Agent B)

**Recommendation A: Add explicit calibration anchoring instruction**

Replace in the confidence elicitation prompt:
```
"2. Provide a confidence score from 0.0 to 1.0."
```
With:
```
"2. Provide a confidence score from 0.0 to 1.0, where 0.5 means you have no useful
information and would guess randomly, 0.8 means you believe this is probably correct but
have some doubt, and 1.0 means you are certain. Only use values above 0.9 if you would
stake significant credibility on this answer."
```

**Rationale:** [Tian et al. (2023)](https://arxiv.org/abs/2305.14975) found verbalized confidence with explicit scale calibration reduces ECE. The instruction counteracts RLHF's high-confidence bias per [RLHF Overconfidence (2024)](https://arxiv.org/abs/2410.09724) by making the cost of 0.9+ explicit.

**Recommendation B: Test modified prompt on 10-item sample before full sweep**

Cost: 50 calls (5 models × 10 items). If overconfident error rate drops, commit. If not, revert.

**Recommendation C: Do not pursue repeated sampling for the official sweep**

Cost tradeoff unfavorable: 3-sample approach = 1,500 calls per sweep, approaching daily limits. Repeated sampling acceptable as a validation tool for ambiguous items only.

### From Research Directions: What NOT to Change (Agent C)

**Do NOT add cautionary language to item prompts.** [SteerConf (2025)](https://arxiv.org/abs/2503.02863) showed "be very cautious" prompting reduces overconfidence — exactly the **opposite** of what MetaJudge wants. MetaJudge measures natural miscalibration, not prompted calibration. Adding caution-prompting would make all models better calibrated and shrink the discrimination signal.

**Do NOT add chain-of-thought.** [Fu et al. (2025)](https://arxiv.org/abs/2501.09775) found CoT reasoning inflates confidence on both correct and incorrect answers. This would reduce the discriminative power of deceptive/adversarial buckets.

### Top-k Strategy Assessment (Agent C)

[Tian et al. (2023)](https://arxiv.org/abs/2305.14975) found top-k (k=2 or k=4) guesses with per-guess probabilities significantly improve calibration — 48% ECE reduction on TruthfulQA, 72% on SciQ. The strategy is **compatible with single-turn** and would require updating the CalibrationResponse dataclass in Cell 2 and the adjudication logic in Cell 4.

**However: Do NOT implement.** Top-k would IMPROVE calibration across all models, making C1/C2/C3 HARDER to achieve. The strategy reduces the overconfidence signal MetaJudge is measuring. Potentially useful as a diagnostic comparison in the writeup — showing that forced deliberation improves calibration, strengthening the benchmark's case.

### Precision-Forcing Prompt Language for Item Authoring

Both best discriminators use precise attribute language: "longest" not "biggest"; "originate" not "associated with." This narrows the question to a specific fact where training data distribution pulls toward the wrong answer. **Make this an explicit authoring principle.** Estimated impact: increases deceptive item success rate by ~15–20%.

---

## 12. Compatibility Check

All recommendations have been checked against SOUL.md and the governing documents.

| SOUL.md Principle | Compatibility |
|-------------------|---------------|
| Behavioral evidence over self-report | ✅ All changes score behavioral outputs (answer + confidence), not narrative fields |
| Two axes (Monitoring / Control) | ✅ All changes are within Family A (Calibration / Axis I) |
| Calibration is the anchor | ✅ All changes strengthen calibration signal |
| Kaggle practicality ($500 total, $50/day) | ✅ Single-turn architecture preserved; no repeated sampling recommended |
| Do not redesign from scratch | ✅ All changes are incremental (item replacement, prompt tweak, field name fix) |
| No "expected strategy" scoring | ✅ No change to scoring philosophy |

### Flagged Conflict

**5-item easy bucket vs. dataset_construction_plan.md minimum.**

- `dataset_construction_plan.md §9, §3.3` recommends: "easy: 15+ minimum"
- This brief recommends: 5 items
- **Justification:** The March 19 sweep proved zero discrimination from all easy items. 5 items are sufficient as calibration baseline anchors. The departure is justified by empirical evidence and should be documented in the competition writeup.
- **Resolution:** If the 8/12/30/30/20 alternative is preferred, this conflict is reduced (8 > 5, though still below 15).

### Other Planning Document Compatibility

| Document | Status |
|----------|--------|
| `scoring_plan.md §4.1` | Needs update to reflect `gold_answer` + `aliases` convention (documentation change only) |
| `scoring_plan.md §4.2` (CSV stability) | ✅ No conflict |
| `expansion_sprint_v2.md §3.4` discrimination gates | ✅ Recommended approach consistent with these gates |
| `progress_report_sprint2.md §6.3` distribution targets | ✅ 5/15/30/30/20 matches |
| `v1_architecture.md` | ✅ No conflict — all changes are within Family A |

---

## 13. References

Unified, deduplicated reference list across all three research agents. DOIs and URLs verified as of March 19, 2026.

1. **Brier, G. W. (1950).** Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3. [DOI](http://journals.ametsoc.org/doi/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2)

2. **Gneiting, T. & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *JASA*, 102(477), 359–378. [DOI](https://doi.org/10.1198/016214506000001437)

3. **Guo, C. et al. (2017).** On calibration of modern neural networks. *ICML 2017*. [URL](https://proceedings.mlr.press/v70/guo17a.html)

4. **Kadavath, S. et al. (2022).** Language models (mostly) know what they know. *arXiv*. [arXiv:2207.05221](https://arxiv.org/abs/2207.05221)

5. **Lin, S., Hilton, J. & Evans, O. (2022).** TruthfulQA: Measuring how models mimic human falsehoods. *ACL 2022*. [arXiv:2109.07958](https://arxiv.org/abs/2109.07958) | [GitHub](https://github.com/sylinrl/TruthfulQA)

6. **Tian, K. et al. (2023).** Just ask for calibration: Strategies for eliciting calibrated confidence scores from language models fine-tuned with human feedback. *EMNLP 2023*. [arXiv:2305.14975](https://arxiv.org/abs/2305.14975)

7. **PMC / Journal of Intelligence (2023).** Overconfidence in the Cognitive Reflection Test. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10219213/)

8. **Dong, Y. et al. (2024).** Generalization or memorization: Data contamination and trustworthy evaluation for large language models. *arXiv*. [arXiv:2402.15938](https://arxiv.org/abs/2402.15938)

9. **Geng, J. et al. (2024).** A survey of confidence estimation and calibration in large language models. *NAACL 2024*. [arXiv:2311.08298](https://arxiv.org/abs/2311.08298)

10. **Groot, T. & Valdenegro-Toro, M. (2024).** Overconfidence is key: Verbalized uncertainty evaluation in large language and vision-language models. *arXiv*. [arXiv:2405.02917](https://arxiv.org/abs/2405.02917)

11. **Liu, G. et al. (2024).** Examining LLMs' uncertainty expression towards questions outside parametric knowledge. *arXiv*. [arXiv:2311.09731](https://arxiv.org/abs/2311.09731)

12. **Ni, S. et al. (2024).** Are large language models more honest in their probabilistic or verbalized confidence? *arXiv*. [arXiv:2408.09773](https://arxiv.org/abs/2408.09773)

13. **Saxon, M. et al. (2024).** Benchmarks as microscopes: A call for model metrology. *arXiv*. [arXiv:2407.16711](https://arxiv.org/abs/2407.16711)

14. **Wei, J. et al. (2024).** SimpleQA: Measuring short-form factuality in large language models. *arXiv*. [arXiv:2411.04368](https://arxiv.org/abs/2411.04368) | [GitHub](https://github.com/openai/simple-evals)

15. **Xiong, M. et al. (2024).** Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in LLMs. *ICLR 2024*. [arXiv:2306.13063](https://arxiv.org/abs/2306.13063)

16. **RLHF Overconfidence (2024).** Taming overconfidence in LLMs: Reward calibration in RLHF. *arXiv*. [arXiv:2410.09724](https://arxiv.org/abs/2410.09724)

17. **Johnson, S. G. B. et al. (2024).** Imagining and building wise machines: The centrality of AI metacognition. *arXiv*. [arXiv:2411.02478](https://arxiv.org/abs/2411.02478)

18. **Chhikara, P. (2025).** Mind the confidence gap: Overconfidence, calibration, and distractor effects in large language models. *arXiv*. [arXiv:2502.11028](https://arxiv.org/abs/2502.11028)

19. **Fu, T. et al. (2025).** Multiple choice questions: Reasoning makes large language models more self-confident even when they are wrong. *arXiv*. [arXiv:2501.09775](https://arxiv.org/abs/2501.09775)

20. **Steyvers, M. & Peters, M. A. K. (2025).** Metacognition and uncertainty communication in humans and large language models. *arXiv*. [arXiv:2504.14045](https://arxiv.org/abs/2504.14045)

21. **Sung, Y. Y. et al. (2025).** GRACE: A granular benchmark for evaluating model calibration against human calibration. *arXiv*. [arXiv:2502.19684](https://arxiv.org/abs/2502.19684)

22. **Sun, Y. et al. (2025).** The Emperor's New Clothes in Benchmarking. *ICML 2025*. [arXiv:2503.16402](https://arxiv.org/abs/2503.16402)

23. **Zhou, Y. et al. / SteerConf (2025).** Calibrating LLM confidence with semantic steering. *arXiv*. [arXiv:2503.02863](https://arxiv.org/abs/2503.02863)

24. **EMNLP 2025 survey.** Benchmark data contamination. [URL](https://aclanthology.org/2025.emnlp-main.511.pdf)

25. **ACL 2025 survey.** LLM knowledge boundaries. [URL](https://aclanthology.org/2025.acl-long.256.pdf)

26. **Pham, N. et al. (2026).** IRB framework for iteratively robust benchmarks. *arXiv*. [URL](https://arxiv.org/pdf/2602.08070)

27. **Haas, L. et al. (2025).** SimpleQA Verified: A reliable factuality benchmark. *arXiv*. [URL](https://arxiv.org/html/2509.07968v2)

---

*End of Calibration Research Brief — Sprint 3. All source URLs and DOIs verified as of March 19, 2026.*
*Merged from: Agent A (Academic Foundations), Agent B (Challenges & Feasibility), Agent C (Research Directions)*
