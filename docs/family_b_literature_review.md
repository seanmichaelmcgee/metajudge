# Phase 1A: Literature Review on Selective Abstention and Verification
**MetaJudge Benchmark Project — Family B Design Research**
*Prepared: March 2026 | Step budget: Phase 1A*

---

## Scope

This review covers the twelve research themes driving Family B of MetaJudge: a benchmark family measuring whether LLMs make correct *next-action* decisions under epistemic uncertainty (answer / ask clarifying question / verify / abstain). Sources span arXiv, ACL, EMNLP, NAACL, ICLR, NeurIPS, and workshop proceedings, with emphasis on 2024–2026. Older watershed references are included where they materially inform design.

---

# PART 1: PAPER-BY-PAPER SUMMARIES

---

## 1. "Know Your Limits: A Survey of Abstention in Large Language Models"
**Authors:** Bingbing Wen, Jihan Yao, Shangbin Feng, Chenjun Xu, Yulia Tsvetkov, Bill Howe, Lucy Lu Wang  
**Venue/Date:** arXiv 2407.18418 — July 2024 (updated February 2025)  
**URL:** https://arxiv.org/abs/2407.18418

**Key findings:**  
This is the most comprehensive taxonomy of LLM abstention to date. The survey organizes abstention from three perspectives:
1. **Query-level triggers** — factual unknowns, logical unanswerability, harmful/out-of-scope requests, inherent ambiguity
2. **Model-level triggers** — low internal confidence, self-consistency failure, knowledge boundary violation
3. **Human values triggers** — safety, honesty, user autonomy norms

The authors distinguish *hard* abstention (refusing to respond at all) from *soft* abstention (hedged responses), and note that these serve different downstream use cases. They identify key evaluation gaps: most existing benchmarks evaluate abstention on answerable/unanswerable binary tasks, ignoring the richer decision space where a model should ask clarifying questions or invoke a verification tool instead. They further note that abstention quality is highly sensitive to evaluation methodology—auto-evaluation metrics disagree substantially with human judgments on whether abstention was warranted.

**Relevance to Family B design:**  
Provides the authoritative taxonomy of *why* abstention should be triggered, informing item construction. The three-perspective framework maps cleanly to Family B's coverage: query-level ambiguity → clarify action; model-level confidence failure → verify or abstain action; harmful/unsafe requests require a separate refusal treatment. The survey's identification of evaluation gaps is direct motivation for Family B's utility-matrix scoring approach.

---

## 2. "Answer, Refuse, or Guess? Investigating Risk-Aware Decision Making in Language Models"
**Authors:** Cheng-Kuang Wu, Zhi Rui Tam, Chieh-Yen Lin, Yun-Nung Chen, Hung-yi Lee  
**Venue/Date:** arXiv 2503.01332 — March 2025  
**URL:** https://arxiv.org/abs/2503.01332

**Key findings:**  
The paper formalizes a **risk-aware answer-or-defer** framework with an explicit reward/penalty structure: each scenario assigns a triple (r_cor, r_inc, r_ref) — reward for correct answer, penalty for wrong answer, reward for refusal. By varying this triple while keeping underlying tasks fixed, the authors can test whether models adjust their decisions appropriately to risk context. The core finding is that **LMs systematically miscalibrate their risk-sensitivity**: they over-answer in high-risk settings (where wrong answers are very costly) and over-defer in low-risk settings (where attempted answers are profitable even if wrong). A "skill-decomposition" approach — training models to separately estimate correctness probability and then apply the utility matrix — consistently improves decision quality. Notably, this failure is present even in frontier reasoning models like GPT-4o.

**Relevance to Family B design:**  
This paper directly validates a **utility matrix scoring** approach for Family B. The (r_cor, r_inc, r_ref) triple is a concrete instantiation of asymmetric payoffs that can encode different deployment contexts. The finding that models fail at *risk-conditioned* decisions (not just binary abstention) is a key motivation for Family B testing *context-conditioned* correctness of action choice. The skill-decomposition analysis suggests that separating "confidence estimation" from "action selection" is methodologically important for diagnosing failure modes.

---

## 3. "CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in Large Language Models"
**Authors:** Tong Zhang, Peixin Qin, Yang Deng, Chen Huang, Wenqiang Lei, et al.  
**Venue/Date:** arXiv 2405.12063 — May/June 2024  
**URL:** https://arxiv.org/abs/2405.12063

**Key findings:**  
CLAMBER is a ~12K-item benchmark built around a multi-level taxonomy of ambiguity types (lexical ambiguity, referential ambiguity, scope ambiguity, intent ambiguity, temporal ambiguity, and others). Key findings:
- Current LLMs have **limited practical utility** in identifying ambiguous queries, even with chain-of-thought or few-shot prompting
- CoT prompting can cause **overconfidence**, making models *less* willing to seek clarification on genuinely ambiguous items
- Models fail at generating high-quality clarifying questions: they frequently ask low-information questions (that do not reduce ambiguity) or questions that presuppose incorrect interpretations
- Ambiguity detection accuracy is inversely related to the subtlety of ambiguity type — lexical ambiguity is easier to detect than intent ambiguity

**Relevance to Family B design:**  
CLAMBER's taxonomy is essential for item construction: Family B's clarify-action items should span multiple ambiguity types, and the benchmark reveals that intent ambiguity (the hardest case) is the most ecologically valid. The finding about CoT overconfidence has direct implications for evaluation: do not use CoT prompting as the standard test protocol, as it may artificially inflate apparent clarification judgments. Item quality checking must verify that "requires clarification" items actually reduce downstream answer quality when the model presupposes an interpretation.

---

## 4. "Clarify When Necessary: Resolving Ambiguity Through Interaction with LMs"
**Authors:** Michael J.Q. Zhang, Eunsol Choi  
**Venue/Date:** arXiv 2311.09469 — November 2023  
**URL:** https://arxiv.org/abs/2311.09469

**Key findings:**  
This foundational paper decomposes clarification into three distinct subtasks: (1) *when* to clarify, (2) *what* to ask, and (3) *how to use* clarification to produce a better answer. The key technical contribution is **intent-sim**, an uncertainty estimator that measures entropy over the space of user intents rather than over answer tokens. Intent-sim outperforms standard confidence measures (model likelihood, self-verification) for detecting when clarification is beneficial. When constrained to clarify only 10% of examples, intent-sim-guided selection doubles the performance gain compared to random selection. The framework is task-agnostic and tested across QA, machine translation, and NLI.

**Relevance to Family B design:**  
The three-subtask decomposition is the cleanest analytical framework for Family B's clarify action. Family B should ideally evaluate all three subtasks separately — does the model correctly identify that clarification is needed? Does it ask an *informative* question (high information gain)? Does it use the clarification response appropriately? The intent-sim approach (entropy over user intent interpretations) is a principled method for constructing ground truth for Family B's clarify-action items.

---

## 5. "Modeling Future Conversation Turns to Teach LLMs to Ask Clarifying Questions"
**Authors:** Michael J.Q. Zhang, W. Bradley Knox, Eunsol Choi  
**Venue/Date:** arXiv 2410.13788 — October 2024/March 2025  
**URL:** https://arxiv.org/abs/2410.13788

**Key findings:**  
This paper identifies a specific failure mode in LLM clarification behavior: **single-interpretation presupposition**. LLMs trained by standard RLHF methods tend to presuppose the most common interpretation of an ambiguous request and answer it directly, because their reward signal evaluates responses against the context at hand (not against what would have happened in future turns). The authors propose future-turn simulation: preference labels are assigned by simulating what response *would* have been optimal if the model had first asked for clarification. With this training approach, models achieve 5% F1 improvement on recovering correct user interpretations and 3% improvement in judicious clarify-vs-answer decisions. The paper also demonstrates the ability to train models that know *when not* to ask (to avoid unnecessary friction on unambiguous requests).

**Relevance to Family B design:**  
This paper provides the theoretical grounding for why clarification training is hard and what makes good training data. For Family B benchmark construction, it underscores the need to have items where presupposing the "obvious" interpretation leads to measurably worse outcomes. The 5% F1 improvement metric suggests that clarification utility should be measured by downstream answer quality, not just whether a clarifying question was asked. This maps to a **conditional scoring** design: a clarify action earns credit only if the clarification would have been useful.

---

## 6. "Active Task Disambiguation with LLMs"
**Authors:** Katarzyna Kobalczyk, Nicolas Astorga, Tennison Liu, Mihaela van der Schaar  
**Venue/Date:** arXiv 2502.04485 — February 2025  
**URL:** https://arxiv.org/abs/2502.04485

**Key findings:**  
This paper provides a formal foundation for when to ask clarifying questions using **Bayesian Experimental Design (BED)**. Task ambiguity is formalized as uncertainty over the space of viable solutions to a task. A clarifying question is valuable proportional to its expected information gain — i.e., how much it narrows the viable solution space. The authors show that LLMs may lack the meta-cognitive capacity to generate high-information-gain questions, but that an explicit BED framing can guide this behavior. Empirical results show that BED-guided question selection outperforms approaches that reason only in the space of questions (without modeling their downstream effect on the solution space).

**Relevance to Family B design:**  
The BED framework gives a rigorous answer to the question "what makes a clarifying question valid vs. noisy?" — a question that is critical for Family B item quality. A clarify item is valid if there exists a genuine distribution over user intents such that asking a clarifying question has measurable expected information gain over the task's solution space. This criteria can be operationalized as an item quality check: annotators must be able to enumerate at least two meaningfully distinct interpretations of the query and show that they lead to different preferred answers.

---

## 7. "Learning to Clarify: Multi-turn Conversations with Action-Based Contrastive Self-Training"
**Authors:** Maximillian Chen, Ruoxi Sun, Sercan Ö. Arık, Tomas Pfister  
**Venue/Date:** arXiv 2406.00222 — May/June 2024 (ACL 2024)  
**URL:** https://arxiv.org/abs/2406.00222

**Key findings:**  
This paper establishes that LLMs trained by standard methods systematically **overhedge** — they add hedging caveats to answers rather than asking focused clarifying questions, and they implicitly guess the most likely intent rather than surfacing uncertainty explicitly. The Action-Based Contrastive Self-Training (ACT) framework, based on DPO, trains models to choose between dialogue actions (clarify, answer, hedge) rather than just to produce better text. ACT demonstrates that even without labeled action data, contrastive self-training can substantially improve disambiguation behavior across tabular QA, reading comprehension, and AmbigSQL tasks.

**Relevance to Family B design:**  
The overhedging behavior documented here is a primary failure mode that Family B must be able to detect and penalize. Overhedging (producing a caveat-laden answer instead of asking for clarification or abstaining) should be distinguished from genuine clarification in the action ontology. The ACT framework also validates the hypothesis that action-level evaluation is more discriminating than output-quality evaluation for measuring clarification ability.

---

## 8. "Mitigating LLM Hallucinations via Conformal Abstention"
**Authors:** Yasin Abbasi-Yadkori et al. (Google DeepMind)  
**Venue/Date:** arXiv 2405.01563 — April 2024  
**URL:** https://arxiv.org/abs/2405.01563

**Key findings:**  
This paper develops a statistically rigorous abstention procedure using conformal prediction. The method uses the LLM to self-evaluate the similarity between multiple sampled responses (self-consistency), then sets an abstention threshold calibrated to bound the hallucination rate at a user-specified level. Key technical contributions: (1) using the LLM itself as a similarity judge (not external oracles); (2) conformal calibration that provides finite-sample theoretical guarantees; (3) demonstrating that this approach is less conservative than log-probability baselines on long-form generation. The paper frames abstention as a **coverage-risk tradeoff** — the user specifies a maximum acceptable error rate, and the system computes the optimal coverage (fraction of queries answered) achievable under that constraint.

**Relevance to Family B design:**  
The coverage-risk tradeoff framing is the right lens for Family B's scoring. An ideal model operating on Family B items should behave like a well-calibrated conformal predictor: it should be willing to answer when its confidence exceeds the item's risk threshold, and abstain otherwise. The self-consistency-based confidence signal (sampling multiple outputs and measuring their similarity) suggests a cheap but principled way to construct uncertainty labels for Family B items: items that have high within-model variance should be labeled as abstain-appropriate.

---

## 9. "LLMs Can Learn Self-Restraint Through Iterative Self-Reflection (ReSearch)"
**Authors:** Alexandre Piché, Aristides Milios, Dzmitry Bahdanau, Chris Pal  
**Venue/Date:** arXiv 2405.13022 — May 2024  
**URL:** https://arxiv.org/abs/2405.13022

**Key findings:**  
ReSearch introduces a **utility function** for self-restraint that scores both responses of various lengths and abstention on a unified scale. The utility function awards points for correct answers proportional to their confidence, and deducts points for incorrect answers. Abstention earns a fixed intermediate score. Through iterative self-prompting (the model critiques its own responses) and self-evaluation against this utility function, synthetic training data is generated that teaches models when to restrain themselves. Resulting models show substantially fewer hallucinations at no inference-time cost. The utility function naturally handles the tradeoff between helpfulness and accuracy.

**Relevance to Family B design:**  
ReSearch's utility function is one of the clearest precedents for Family B's scoring. The key design element is that abstention earns a non-zero (but sub-optimal) score — neither 0 nor full credit. This creates the right incentive structure: models are rewarded for correct answers, penalized for wrong answers, and given partial credit for appropriate abstention. The iterative self-reflection approach also suggests a data generation method for Family B: use models to annotate items with their own uncertainty, then filter items where the model is appropriately uncertain.

---

## 10. "Do LLMs Know When to NOT Answer? Investigating Abstention Abilities of Large Language Models"
**Authors:** Nishanth Madhusudhan, Sathwik Tejaswi Madhusudhan, Vikas Yadav, Masoud Hashemi  
**Venue/Date:** arXiv 2407.16221 — July/September 2024  
**URL:** https://arxiv.org/abs/2407.16221

**Key findings:**  
This paper introduces Abstain-QA, a black-box evaluation dataset, and the **Answerable-Unanswerable Confusion Matrix (AUCM)** — a 2×2 matrix tracking the four outcomes: correctly answers, incorrectly answers, correctly abstains, incorrectly abstains. Even GPT-4 and Mixtral-8x22B struggle with abstention. Key findings: (1) models have high false-negative abstention rates on "hard" unanswerable questions; (2) models have high false-positive abstention rates on well-known domains where they actually have the answer; (3) chain-of-thought prompting and strict prompting improve abstention behavior. The dataset covers fact-centric and reasoning tasks across well-represented and under-represented domains.

**Relevance to Family B design:**  
The AUCM is directly adoptable as a sub-metric for Family B's abstain action. The distinction between well-represented vs. under-represented domains is critical: Family B items should be stratified by domain representativeness, since models fail differently on these. The false-positive abstention failure (abstaining when they could answer correctly) is as important to measure as false-negative abstention — both are costly, and a complete evaluation must penalize both.

---

## 11. "Can Large Language Models Faithfully Express Their Intrinsic Uncertainty in Words?"
**Authors:** Gal Yona, Roee Aharoni, Mor Geva  
**Venue/Date:** arXiv 2405.16908 — May 2024  
**URL:** https://arxiv.org/abs/2405.16908

**Key findings:**  
This paper proposes a precise, example-level metric called **faithful response uncertainty**: the gap between the model's *intrinsic* confidence (estimated from its token probability distribution) and the *decisiveness* with which it conveys its answer in text. The metric penalizes both excessive hedging (the model is confident but uses tentative language) and insufficient hedging (the model is uncertain but asserts confidently). Evaluations across multiple aligned LLMs show a consistent finding: **modern LLMs are systematically poor at faithfully conveying uncertainty** — they tend toward verbal overconfidence even when their intrinsic probability mass is diffuse. RLHF/alignment training appears to actively reduce faithful uncertainty expression.

**Relevance to Family B design:**  
This paper is the strongest evidence that verbal hedging cannot be used as a proxy for appropriate abstention in Family B. A model that says "I think it might be X, but I'm not entirely sure" might have a very confident internal distribution pointing to X, or might genuinely not know. These are completely different epistemic situations. Family B must therefore evaluate the *action* (answer/clarify/verify/abstain) rather than the *tone* of the response. The faithful uncertainty metric also suggests a quality check: Family B items where a model gives confident-sounding wrong answers (unfaithful overconfidence) are the most diagnostically valuable.

---

## 12. "SaySelf: Teaching LLMs to Express Confidence with Self-Reflective Rationales"
**Authors:** Tianyang Xu, Shujin Wu, Shizhe Diao, et al.  
**Venue/Date:** arXiv 2405.20974 — May 2024 (EMNLP 2024 Main)  
**URL:** https://arxiv.org/abs/2405.20974

**Key findings:**  
SaySelf trains LLMs to output both (1) a calibrated numerical confidence score and (2) a self-reflective rationale explaining the source of uncertainty. Rationales are generated by analyzing inconsistencies across multiple sampled reasoning chains (where chains diverge indicates genuine uncertainty). Training uses supervised fine-tuning on these synthetic rationale+score pairs, followed by RL with a reward function penalizing calibration error. Results: SaySelf reduces ECE substantially and, notably, the self-reflective rationales themselves *improve* calibration beyond confidence scores alone.

**Relevance to Family B design:**  
SaySelf establishes that models *can* be trained to produce accurate uncertainty self-assessments — the deficiencies found by Yona et al. (2024) are not fundamental. For Family B, this means that recent models trained with SaySelf-like methods may produce reliable verbal uncertainty signals. This motivates using model-generation conditions carefully in evaluation: when should Family B items supply internal confidence vs. elicit verbal uncertainty? The rationale generation approach also suggests a method for constructing high-quality Family B items by identifying queries where models' sampled reasoning chains diverge.

---

## 13. "Selectively Answering Ambiguous Questions"
**Authors:** Jeremy R. Cole, Michael J.Q. Zhang, Daniel Gillick, Julian Martin Eisenschlos, Bhuwan Dhingra, Jacob Eisenstein  
**Venue/Date:** arXiv 2305.14613 — EMNLP 2023  
**URL:** https://arxiv.org/abs/2305.14613

**Key findings:**  
This paper explicitly distinguishes two sources of "unknowns" in QA: (1) the model lacks the knowledge, and (2) the question is inherently ambiguous. These require different responses — the first warrants abstention (I don't know), the second warrants clarification (there are multiple valid answers depending on interpretation). The key empirical finding is that **sampling-based confidence** (measuring repetition across multiple model outputs) is the most reliable signal for deciding when to abstain on ambiguous questions — more reliable than single-sample model likelihood or self-verification. The benefit of sampling is especially pronounced for ambiguous (vs. unambiguous but unknown) questions.

**Relevance to Family B design:**  
This paper provides empirical grounding for a crucial Family B item type distinction: items where the model lacks knowledge (abstain-appropriate) vs. items where the question is genuinely ambiguous (clarify-appropriate). Family B's item design must encode which type of unknown is present, and the evaluation should check whether models correctly discriminate these two cases. The sampling-based confidence finding also suggests a cheap automated confidence signal for Family B item calibration.

---

## 14. "Aligning Language Models to Explicitly Handle Ambiguity (APA)"
**Authors:** Hyuhng Joon Kim, Youna Kim, Cheonbok Park, et al.  
**Venue/Date:** arXiv 2404.11972 — April 2024 (EMNLP 2024)  
**URL:** https://arxiv.org/abs/2404.11972

**Key findings:**  
APA (Alignment with Perceived Ambiguity) proposes training LLMs using the model's own estimate of ambiguity as the supervision signal, bypassing the need for gold-standard human ambiguity labels (which are expensive). The pipeline: (1) the model generates multiple interpretations of a query; (2) perceived ambiguity = variance across interpretations; (3) the model is trained to either ask for clarification or provide an answer, conditioned on this perceived ambiguity. Key result: APA achieves better out-of-distribution generalization than models trained on human-labeled ambiguity — likely because human labels reflect the annotators' particular knowledge, while perceived ambiguity reflects the model's actual knowledge state.

**Relevance to Family B design:**  
The APA pipeline is directly relevant as an item generation method. Using the LLM's own "perceived ambiguity" to identify candidates for clarify-action items is more scalable than human annotation. However, the paper also illustrates a failure mode for Family B evaluation: if the evaluating model uses the same perceived-ambiguity signal as the model being evaluated, circular scoring may arise. Family B should use orthogonal evidence (human annotations or a different model family) to validate that items are genuinely ambiguous.

---

## 15. "Robots That Ask For Help: Uncertainty Alignment for LLM Planners (KnowNo)"
**Authors:** Allen Z. Ren, Anushri Dixit, Alexandra Bodrova, et al.  
**Venue/Date:** arXiv 2307.01928 — July 2023 (CoRL 2023)  
**URL:** https://arxiv.org/abs/2307.01928

**Key findings:**  
KnowNo is a conformal-prediction-based framework for robot action planning that decides when the LLM should proceed autonomously vs. ask for human help. The framework covers four modes of ambiguity: spatial uncertainty, numeric uncertainty, human preference uncertainty, and Winograd-style linguistic ambiguity. The key insight is that LLMs can reliably enumerate possible action options, and a conformal predictor over these options can generate a prediction set at a user-specified coverage level. When the prediction set contains multiple options (ambiguity), the robot asks for help. This approach requires no fine-tuning and scales with model capability.

**Relevance to Family B design:**  
KnowNo is the strongest existence proof that a **decision-making benchmark** requiring a 3-way choice (proceed, ask, abstain) is feasible and meaningful. The four ambiguity modes map to Family B item types. The conformal prediction approach suggests an automated method for generating verify-action items: tasks where the model's enumerated option set has high coverage uncertainty are candidates for verification actions. KnowNo's "task completion while minimizing help requests" framing also defines a natural utility function for Family B.

---

## 16. "Efficiently Deploying LLMs with Controlled Risk (HCMA)"
**Authors:** Michael J. Zellinger, Matt Thomson  
**Venue/Date:** arXiv 2410.02173 — October 2024  
**URL:** https://arxiv.org/abs/2410.02173

**Key findings:**  
HCMA (Hierarchical Chains with Multi-Level Abstention) deploys LLMs in a hierarchy, routing queries to larger models when smaller models are uncertain and abstaining entirely when even the largest model is uncertain. Key quantitative finding: on MMLU, allowing 20% abstention cuts the error rate of Llama-3 405B by 30%. On free-form generation, zero-shot prompting drives error to 0% on TruthfulQA at high abstention rates (chain-of-thought is *less* effective). ECE can be reduced by 50% over Platt scaling using only 50-100 labeled examples. The paper demonstrates the practical value of combining model-switching with selective abstention.

**Relevance to Family B design:**  
The HCMA finding that chain-of-thought is counterproductive for selective prediction on free-form tasks is important for Family B evaluation protocol design. Standard test conditions (with or without CoT) should be specified in advance, and CoT conditions should be evaluated separately. The 50-100 labeled example requirement for good calibration also suggests that Family B should include a held-out calibration set for models that use threshold-setting approaches.

---

## 17. "Mitigating LLM Hallucinations via Conformal Abstention / Learning Conformal Abstention Policies"
**Authors:** Sina Tayebati, Divake Kumar, Nastaran Darabi, et al.  
**Venue/Date:** arXiv 2502.06884 — February 2025  
**URL:** https://arxiv.org/abs/2502.06884

**Key findings:**  
This paper extends static conformal prediction abstention to a **reinforcement learning framework** that dynamically optimizes abstention thresholds per task. The RL approach treats CP thresholds as actions and optimizes a reward that simultaneously minimizes prediction set size while maintaining coverage. Results: 22.19% improvement in AUROC for hallucination detection; 21.17% improvement in uncertainty-guided selective generation (AUARC); 70-85% reduction in calibration error, all while meeting a 90% coverage target. AUARC (Area Under the Accuracy-Rejection Curve) is introduced as a key metric.

**Relevance to Family B design:**  
AUARC — the area under the curve plotting accuracy as a function of abstention rate — is a strong candidate primary metric for Family B. It summarizes the quality of the entire abstention decision policy (not just at a single threshold), resists gaming (a model must be well-calibrated across the full coverage range), and has a clean interpretation. Family B should include an AUARC-style global metric alongside per-item action accuracy scores.

---

## 18. "MT-Eval: A Multi-Turn Capabilities Evaluation Benchmark for LLMs"
**Authors:** Wai-Chung Kwan, Xingshan Zeng, Yuxin Jiang, et al.  
**Venue/Date:** arXiv 2401.16745 — January 2024  
**URL:** https://arxiv.org/abs/2401.16745

**Key findings:**  
MT-Eval categorizes multi-turn interaction into four patterns: **recollection** (remembering earlier context), **expansion** (building on prior turns), **refinement** (correcting errors from prior turns), **follow-up** (answering follow-up questions). Key finding: most LLMs show significant performance degradation in multi-turn settings vs. single-turn, and this is **not correlated with single-turn capability** — meaning multi-turn handling is a separable ability. The two main failure modes are: distance to relevant content (forgetting information from earlier turns) and error propagation (mistakes compound across turns). 1170 multi-turn queries were constructed across 11 LLMs.

**Relevance to Family B design:**  
Family B's clarify action produces a multi-turn sequence. MT-Eval demonstrates that multi-turn evaluation must explicitly control for turn distance and error propagation. For Family B, a clarification exchange that spans 2-3 turns is feasible but should control for context length and position of relevant information. The four interaction patterns suggest that Family B's multi-turn items should span at least refinement (correcting a presupposition after clarification) and expansion (using new context to improve an answer).

---

## 19. "CLAM: Selective Clarification for Ambiguous Questions with Generative Language Models"
**Authors:** Lorenz Kuhn, Yarin Gal, Sebastian Farquhar  
**Venue/Date:** arXiv 2212.07769 — December 2022 (EACL 2023)  
**URL:** https://arxiv.org/abs/2212.07769

**Key findings:**  
CLAM is the watershed paper establishing selective clarification as a task. It demonstrates that language models rarely ask for clarification on ambiguous questions and instead provide incorrect confident answers. The CLAM pipeline: detect ambiguity → generate clarifying question → receive answer → produce final response. A key methodological contribution is **simulated users** — the LLM is given "privileged information" about the correct interpretation and used to simulate user responses, enabling fully automated multi-turn evaluation. This approach was validated against human user experiments.

**Relevance to Family B design:**  
The simulated-user methodology in CLAM is the most practical approach for Family B's multi-turn evaluation. Rather than requiring real users for each item, Family B should simulate clarification responses using a separate model with privileged intent information. This allows fully automated evaluation and scales to large benchmark sizes. The CLAM approach also shows that automatic multi-turn evaluation is valid: simulated-user CLAM evaluation correlates well with real human evaluation.

---

## 20. "Do Large Language Models Know What They Don't Know? (SelfAware)"
**Authors:** Zhangyue Yin, Qiushi Sun, Qipeng Guo, Jiawen Wu, Xipeng Qiu, Xuanjing Huang  
**Venue/Date:** ACL Findings 2023 (arXiv 2305.18153)  
**URL:** https://arxiv.org/abs/2305.18153

**Key findings:**  
This paper introduces the SelfAware benchmark: a dataset of unanswerable questions across five categories (temporal, future-unknown, subjective, controversial, unknowable facts) and their answerable counterparts. The key finding is that LLMs have significant **self-knowledge deficits**: they answer unanswerable questions confidently rather than abstaining, and their ability to detect that a question is unanswerable (vs. answerable) is poor across 20 models. Larger models perform better, but even frontier models at the time of writing showed substantial failure rates. The paper proposes automated uncertainty detection in model responses using NLI classifiers.

**Relevance to Family B design:**  
SelfAware establishes the benchmark design template for abstain-action items: a structured collection of items across multiple unanswerability types, paired with answerable counterparts at matched difficulty. The five unanswerability categories map directly to Family B abstain-item subcategories. The NLI-based automated detection of whether a model expressed appropriate uncertainty is a practical evaluation method for Family B's abstain-action items.

---

## 21. "Selectively Answering Under Domain Shift"
**Authors:** Amita Kamath, Percy Liang, Robin Jia  
**Venue/Date:** ACL 2020  
**URL:** https://aclanthology.org/2020.acl-main.503.pdf

**Key findings:**  
This watershed paper formally defines selective QA: answer as many questions as possible while maintaining accuracy above a target threshold. The key finding is that softmax probabilities alone are unreliable for selective prediction under domain shift because models are systematically overconfident on OOD data. The paper introduces abstention policies combining model confidence with calibration techniques and shows that abstention on OOD items reduces error rates substantially. The risk-coverage curve is the central evaluation tool.

**Relevance to Family B design:**  
The risk-coverage curve is the progenitor of Family B's AUARC metric. Domain shift is relevant to Family B: items should include cases where models might be overconfident in unfamiliar territory. The formal selective QA framing — maintain accuracy above τ while maximizing coverage — is the clearest decision-theoretic foundation for the abstain action.

---

## 22. "Uncertainty-Based Abstention in LLMs Improves Safety and Reduces Hallucinations"
**Authors:** Christian Tomani, Kamalika Chaudhuri, Ivan Evtimov, Daniel Cremers, Mark Ibrahim  
**Venue/Date:** arXiv 2404.10960 — April 2024  
**URL:** https://arxiv.org/abs/2404.10960

**Key findings:**  
This paper contrasts multiple types of uncertainty signals for abstention: statistical measures (entropy, mutual information), verbal uncertainty (the model's own expressed uncertainty), and a novel **In-Dialogue Uncertainty (InDU)** measure that tracks uncertainty expressed within the conversation itself. Key finding: the appropriate uncertainty signal depends critically on the model type — models *with* RLHF training benefit most from verbal/InDU signals, while models *without* RLHF respond better to statistical signals. Properly matched abstention reduces hallucinations by 50% while improving correctness by 2-8%, and increases safety by 70-99% with minimal extra compute.

**Relevance to Family B design:**  
This paper has critical implications for Family B's evaluation fairness: the appropriate signal for detecting whether abstention is warranted may differ across model families. Family B should not assume a uniform evaluation protocol; it should either: (a) allow models to use any abstention signal, evaluated purely by action outcome; or (b) specify a standardized uncertainty elicitation protocol that is model-agnostic (verbal confidence, for instance). The strong dependence of optimal signal on RLHF training status argues for (a).

---

## 23. "Interactive Agents to Overcome Ambiguity in Software Engineering"
**Authors:** Sanidhya Vijayvargiya, Xuhui Zhou, Akhila Yerukola, Maarten Sap, Graham Neubig  
**Venue/Date:** arXiv 2502.13069 — February 2025  
**URL:** https://arxiv.org/abs/2502.13069

**Key findings:**  
This paper evaluates whether LLM coding agents can detect ambiguity and ask targeted clarifying questions to improve code generation outcomes. Three-step evaluation: (a) does interactivity improve performance on ambiguous tasks?, (b) do models detect ambiguity?, (c) do they ask useful questions? Key finding: LLMs can substantially improve performance by leveraging interactivity but are poor at detecting *when* to do so — they frequently ask unnecessary questions on clear tasks (wasting turns) and fail to ask on genuinely ambiguous tasks. The paper distinguishes **appropriate interactivity** (asking when necessary) from **over-interactivity** (asking unnecessarily) as separate failure modes.

**Relevance to Family B design:**  
The distinction between under-asking and over-asking is essential for Family B's scoring. Over-asking (asking clarifying questions on unambiguous items) should be penalized, not just rewarded for caution. The software engineering domain provides a concrete example of items where the cost of over-clarifying is measurable (wasted code generation attempts). Family B should include items where the appropriate action is clearly "answer" with no ambiguity — to test false-positive clarification rates.

---

## 24. "MINT: Evaluating LLMs in Multi-turn Interaction with Tools and Language Feedback"
**Authors:** Xingyao Wang, Zihan Wang, Jiateng Liu, et al.  
**Venue/Date:** arXiv 2309.10691 — September 2023 (ICLR 2024)  
**URL:** https://arxiv.org/abs/2309.10691

**Key findings:**  
MINT evaluates LLMs' ability to use tools and respond to natural language feedback across multiple turns. Key findings: (1) providing tools consistently improves performance on complex tasks but models fail to use them effectively under uncertainty; (2) models that use tools too liberally (invoking verification tools when unnecessary) underperform models that make targeted tool calls; (3) models that refuse to use tools when needed underperform even more. The benchmark includes tasks at multiple difficulty levels and measures both final accuracy and interaction efficiency.

**Relevance to Family B design:**  
MINT validates the verify action in Family B's ontology. It demonstrates that tool use (verification) is a genuine strategic choice — not just about "having access" to tools, but about knowing when to invoke them. The finding that over-use of tools harms performance is important: Family B's verify action should not be trivially rewarded, and benchmark items must include cases where verifying is unnecessary. MINT's multi-turn interaction protocol with tool feedback is a model for Family B's verify-action evaluation.

---

## 25. "Alignment for Honesty"
**Authors:** Yuqing Yang, Ethan Chern, Xipeng Qiu, Graham Neubig, Pengfei Liu  
**Venue/Date:** arXiv 2312.07000 — December 2023 (NAACL 2024)  
**URL:** https://arxiv.org/abs/2312.07000

**Key findings:**  
This paper operationalizes "honesty" in LLMs as comprising: *truthfulness* (only asserting what the model believes), *calibration* (expressing uncertainty proportional to actual uncertainty), *transparency* (not withholding relevant information), *forthrightness* (proactively sharing useful information even when not asked), and *non-deception*. The paper develops training methods and metrics for each component. Key insight: honesty is a distinct capability from accuracy — a model can be honest and inaccurate (saying "I don't know" correctly) or dishonest and accurate (saying something right for the wrong reasons).

**Relevance to Family B design:**  
The multi-dimensional honesty framework maps directly onto Family B's evaluation goals. Family B should measure not just whether models choose the right action but whether they do so for the right reasons — specifically: does the model abstain because it genuinely lacks knowledge, or because it is being overly cautious? The forthrightness dimension — proactively sharing useful information — is an interesting framing for the verify action: should a model proactively verify rather than waiting for user prompt?

---

# PART 2: SYNTHESIS — ANSWERS TO 8 DESIGN QUESTIONS

---

## Q1: What action ontology is most defensible?

**The four-way {answer, clarify, verify, abstain} ontology is well-supported, but requires careful definition of each action's trigger conditions.**

The literature supports a minimum of three distinct action types:
- **Abstain** (refuse to respond due to insufficient knowledge) — supported by Wen et al. (2024), Yin et al. (2023), Madhusudhan et al. (2024), and the entire selective prediction literature
- **Clarify** (ask a clarifying question because the query is ambiguous and disambiguation would change the response) — supported by Zhang & Choi (2023), Kuhn et al. (2022/2023), Chen et al. (2024), Kim et al. (2024), CLAMBER
- **Answer** (respond directly) — the default action when the model has sufficient knowledge and the query is unambiguous

The **verify** action (invoke an external tool or source to check a claim before responding) is supported by KnowNo (Ren et al. 2023), MINT (Wang et al. 2023), and the routing literature (Zhang et al. 2025). However, it is less well-studied in the QA literature than the other three actions. Verify is distinct from answer in that the model signals its own uncertainty while seeking external confirmation — unlike abstain where it signals it cannot answer at all.

**Key distinctions the ontology must make:**
- **Clarify vs. Abstain**: The question is not unknown; the intent behind the question is unclear. Clarify when multiple valid interpretations exist and the correct one changes the answer. Abstain when no interpretation yields a known answer.
- **Clarify vs. Hedge-and-Answer**: Hedging is a verbal behavior within the answer action, not a separate action. The ACT paper (Chen et al. 2024) provides strong evidence that models conflate these and that they must be evaluated separately.
- **Verify vs. Answer-with-Confidence**: Verify involves external source access. If no tools are available, the model should either answer (if confident) or abstain (if not) — not pretend to verify.
- **Safety-refuse vs. Epistemic-abstain**: The survey (Wen et al. 2024) distinguishes refusing due to safety policy from abstaining due to epistemic uncertainty. Family B focuses on the latter; refusal-due-to-harm should be excluded from Family B scope.

**One defensible extension: Add "multi-interpret"** — a fifth action where the model provides answers for each major interpretation of an ambiguous question without asking (the "Tree of Clarifications" approach, Jeon et al. 2023). This is contextually appropriate when clarification is not possible (e.g., asynchronous settings) but should not be the default. Family B could include it as a scored alternative action with lower utility than clarify-then-answer but higher than incorrect single-interpretation answer.

---

## Q2: What output format is most parsable for structured evaluation?

**A two-field structured output is optimal: {action: string, content: string}**

The literature converges on several insights:
1. **Action-first format** is more reliable for evaluation than detecting action from prose. The ACT paper (Chen et al. 2024) and the CLAM pipeline (Kuhn et al. 2022) both use explicit action labels. Prose detection (checking whether a response "sounds like" clarification) is error-prone and subject to evaluator bias.
2. **AUCM-compatible format**: Madhusudhan et al.'s (2024) Answerable-Unanswerable Confusion Matrix requires binary action classification at a minimum. The AUCM naturally extends to a multi-class confusion matrix for 4-way action classification.
3. **Confidence score as optional third field**: Several papers (SaySelf, Wu et al. 2025) support eliciting an explicit confidence score alongside the action. This enables AUARC-style curve evaluation but may not be available from all models.

**Recommended format for Family B:**
```json
{
  "action": "answer" | "clarify" | "verify" | "abstain",
  "content": "[the answer text, clarifying question text, verification query, or abstention explanation]",
  "confidence": 0.0–1.0 (optional)
}
```

For multi-turn clarify sequences, the format must handle:
```json
{"action": "clarify", "content": "Which time period are you asking about?"}
// → [simulated user response]
{"action": "answer", "content": "The answer is X because [Y]."}
```

**Anti-patterns to avoid:**
- Free-form response with embedded uncertainty phrases ("I think...", "perhaps...") — unfaithful verbal calibration is established as unreliable (Yona et al. 2024)
- Multiple-choice force (forcing models into predefined answer tokens) — loses the verify/clarify content quality signals

---

## Q3: What metrics are strongest for this type of evaluation?

**Recommended metric stack, in priority order:**

**Primary metric: Utility-Weighted Action Accuracy (UWAA)**
Assign utility scores to each (true_action, predicted_action) pair in a payoff matrix and compute expected utility. This is the direct extension of Wu et al.'s (2025) (r_cor, r_inc, r_ref) framework to 4-way actions. A prototypical payoff matrix (values are relative utilities):

| Predicted ↓ / True → | Answer | Clarify | Verify | Abstain |
|----------------------|--------|---------|--------|---------|
| Answer (correct)     | +1.0   | +0.5   | +0.5   | +0.5   |
| Answer (incorrect)   | -1.0   | -0.5   | -0.5   | -0.5   |
| Clarify              | -0.2   | +1.0   | +0.5   | +0.3   |
| Verify               | -0.2   | +0.3   | +1.0   | +0.3   |
| Abstain              | -0.3   | +0.3   | +0.3   | +1.0   |

**Secondary metric: Action F1 per class**  
Report precision, recall, F1 for each action class. This detects biases (e.g., a model that always answers or always abstains). Per-class F1 is standard in multi-label classification evaluation.

**Tertiary metric: AUARC (Area Under Accuracy-Rejection Curve)**  
For models that output confidence scores, AUARC measures calibration quality across the entire abstention-rate spectrum (Tayebati et al. 2025). Higher AUARC means the model correctly ranks items by difficulty and abstains on harder items first.

**Supplementary metrics:**
- **Clarification utility score**: For clarify-action items, measure whether the clarification request would improve downstream answer quality (using simulated-user framework from CLAM)
- **False-positive clarification rate**: Rate at which models ask for clarification on unambiguous items (penalizes over-asking per Vijayvargiya et al. 2025)
- **AUCM (Answerable-Unanswerable Confusion Matrix)**: For abstain-action items, the 2×2 breakdown from Madhusudhan et al. (2024)

**Metrics to avoid:**
- Raw accuracy without penalizing wrong actions (rewards guess-everything models)
- Abstention rate alone (models can game by always abstaining)
- ROUGE/BLEU for clarifying questions (measures lexical overlap, not information gain)

---

## Q4: What makes clarify/verify/abstain items valid rather than noisy?

**Valid items must satisfy five criteria, derived from the literature:**

**1. Genuine ambiguity (for clarify items)**  
Per Kobalczyk et al.'s (2025) BED framework: there must be ≥2 distinct valid interpretations of the query, each leading to meaningfully different answers, and the expected information gain from asking is measurable. Operationally: annotators must be able to enumerate at least 2 interpretations and rate their answer-relevance distinctly.

**2. Genuine knowledge boundary (for abstain items)**  
Per Yin et al. (2023) and Cole et al. (2023): the item must be unanswerable for a well-defined reason (not just hard). Categories: temporally unknowable, subjectively opinion-dependent, controversial/no consensus, intrinsically unpredictable, or requires external evidence not in training. The annotator must articulate *why* the answer is unknown.

**3. Genuine verification need (for verify items)**  
Per KnowNo (Ren et al. 2023): the model should have meaningful uncertainty but external evidence would resolve it. Items should be designed where: (a) the model's internal confidence is below a threshold, and (b) a specific tool call or search would provide definitive evidence. Items should NOT be verify-appropriate if: (a) the model can answer confidently from training data, or (b) no tool/search would help.

**4. Answer items must be answerable without additional info**  
Items must have an unambiguous ground-truth answer that a model with appropriate knowledge could produce without clarification. Include difficulty-controlled variants.

**5. Cross-annotator agreement requirement**  
The correct action label must have ≥70% agreement across 3+ qualified annotators. Items with lower agreement should be flagged for revision or excluded. The agreement level is set higher than standard (50%) because action selection is more categorical than graded quality judgments.

**Additional validity requirements:**
- Avoid "trick" items that would fool a human expert (CLAMBER finding: CoT overconfidence leads to false clarity on trick items)
- Ambiguous items should be ambiguous in context, not just out of context (Zhang et al. 2024)
- Items should use realistic user phrasings, not laboratory constructions

---

## Q5: How have others handled multi-turn evaluation?

**Multi-turn evaluation should use simulated users with privileged intent information.**

The literature offers three approaches:

**Approach 1: Simulated user (recommended)**  
CLAM (Kuhn et al. 2022) and Zhang et al. (2024) show that a language model provided with "privileged information" (the true user intent) can reliably simulate user responses to clarification questions. This enables fully automated multi-turn evaluation. Validation: simulated-user CLAM evaluation has been shown to correlate well with human evaluation. Implementation: for each item, a parallel "gold interpretation" document is written by annotators; the simulating model is given this document and generates a realistic user response to any clarifying question.

**Approach 2: Fixed scripts**  
MT-Eval (Kwan et al. 2024) uses fixed multi-turn scripts constructed in advance. This is less flexible but more reproducible. Appropriate for turn patterns that can be enumerated in advance (recollection, expansion, refinement, follow-up). Less appropriate for open-ended clarification exchanges.

**Approach 3: Human-in-the-loop**  
Expensive but highest validity. Appropriate for benchmark construction (to validate simulated-user approach) but not scalable for standard evaluation runs.

**Key design lessons from MT-Eval and MINT:**
- Multi-turn performance is not predicted by single-turn performance — test both separately
- Error propagation is a significant failure mode: a wrong clarification in turn 1 compounds across turns
- Limit clarification exchanges to ≤3 turns to control complexity
- Measure both the *action decision* (clarify vs. answer) and the *quality* of the clarifying question separately

**Recommended Family B multi-turn protocol:**
1. Present item to model
2. Model takes action: answer → score immediately; clarify → proceed to step 3; verify → simulate tool response; abstain → score immediately
3. Simulated user responds to clarifying question using privileged-intent document
4. Model produces final answer
5. Score final answer quality AND retrospectively evaluate whether clarification was necessary

---

## Q6: What are the main failure modes in abstention/selective prediction benchmarks?

**Eight documented failure modes from the literature:**

**1. Gaming via universal abstention**  
Models can achieve high precision on unanswerable items by abstaining on everything. Mitigation: use balanced datasets with equal proportions of answerable items, and penalize excessive abstention (false-positive abstention hurts score).

**2. Gaming via universal answering**  
Models achieve high recall on answerable items by always answering. Mitigation: same as above — balanced datasets with penalty for incorrect answers.

**3. Threshold sensitivity**  
Binary abstention decisions are sensitive to the choice of confidence threshold. Kamath et al. (2020) showed that softmax thresholds fail under distribution shift. Mitigation: evaluate over the full coverage-accuracy curve (AUARC), not at a single threshold.

**4. CoT-induced overconfidence (CLAMBER finding)**  
Chain-of-thought prompting can make models less willing to abstain or clarify on ambiguous items, because the CoT reasoning process often resolves apparent ambiguity before the model checks its answer. Mitigation: evaluate both CoT and non-CoT conditions; note CoT-induced overconfidence as a failure mode.

**5. Verbal overconfidence / faithful uncertainty failure (Yona et al. 2024)**  
RLHF-aligned models tend to assert confidently even when internally uncertain. This means verbal hedges cannot be used as a proxy for correct action decisions. Mitigation: evaluate action selection explicitly, not just verbal tone.

**6. Domain bias in abstention rates**  
Models abstain more on under-represented domains (correct) but also on well-known domains where they should answer (incorrect over-abstention). Mitigation: stratify items by domain representativeness in the benchmark; report abstention rates by domain.

**7. Annotation noise in "ground truth" actions**  
Human annotators disagree on whether a question requires clarification vs. can be answered with a reasonable assumption. This creates noisy gold labels. Mitigation: require ≥70% inter-annotator agreement; adjudicate disagreements with expert annotation.

**8. Confounding difficulty with appropriate abstention**  
Hard items may look like abstain-appropriate items to models, but being hard does not make an item abstain-appropriate. Mitigation: include difficulty ratings as a covariate; show that abstention decisions correlate with item-level unanswerability markers, not just difficulty.

---

## Q7: What benchmark size and class balance is practical?

**Recommended: 600–1,000 items, balanced 4-way with intentional imbalance for realistic priors.**

**Size rationale:**
- CLAMBER (~12K items) is extremely large but was automated. Human-curated benchmarks like Abstain-QA (Madhusudhan et al. 2024) and SelfAware (Yin et al. 2023) typically use 200-1,000 items.
- For Family B, targeting 800 items is practical: enough for stable estimates of per-class metrics and enough to support AUARC curves, but small enough for careful human quality control.
- With 4 action classes, 200 items per class provides reasonable statistical power (CI for F1 ≈ ±7% at p=0.95 for a 200-item class).

**Class balance:**
- **Balanced (200 each)** is ideal for detection of biases — a model that always answers gets 50% on binary abstain/answer items, not 75%
- **Realistic priors alternative**: If Family B aims to simulate deployment conditions, balance based on estimated real-world rates. In practice, most user queries are answerable (70-80%), with 10-15% genuinely ambiguous, 5-10% requiring verification, and 5-10% genuinely unanswerable. This more realistic distribution prevents gaming but makes per-class accuracy statistics less interpretable.
- **Recommended**: Start balanced for benchmark construction; report both balanced and prior-weighted metrics.

**Item subtype distribution within each class:**
- Clarify: span at least 3 ambiguity types (lexical, referential, intent) per Zhang et al. (2024) and CLAMBER
- Abstain: span at least 3 unanswerability types (temporal, subjective, controversial) per SelfAware
- Verify: span at least 2 verification types (factual lookup, calculation check)
- Answer: span easy/medium/hard, multiple domains

---

## Q8: What scoring choices best resist gaming?

**Four anti-gaming design principles, supported by literature:**

**1. Penalize incorrect actions symmetrically**  
Wu et al. (2025) demonstrate that models miscalibrate their risk-sensitivity when only one type of error is penalized. Family B must penalize: wrong answers, unnecessary clarifications, unnecessary abstentions, and failed verifications. The utility matrix approach (with off-diagonal penalties) implements this.

**2. Use AUARC instead of single-threshold metrics**  
AUARC evaluates the model at every possible abstention threshold, not just the one the model chooses. This prevents threshold optimization gaming (tuning a post-hoc abstention threshold to hit a specific metric). AUARC requires confidence scores, which should be elicited explicitly from models.

**3. Calibration-weighted scoring**  
Combine action accuracy with calibration quality (ECE). A model that makes the right action choice but with poorly calibrated confidence gets partial credit. This prevents gaming by claiming confident abstention on hard items — the model must earn high confidence on items it correctly answers too.

**4. Hold out action labels until after evaluation**  
Item-level gold action labels should not be in the public benchmark. This prevents models from memorizing action labels during training. Use a held-out test set with private labels; public items should only be used for development.

**Additional anti-gaming measures:**
- Scramble item phrasings to prevent memorization (include paraphrase variants in construction but not in final benchmark)
- Include foil items — items that appear to require a specific action but actually require another (e.g., items that seem ambiguous but have a well-established convention that resolves the ambiguity for informed users)
- Test stability: evaluate the same underlying scenario from multiple angles to ensure consistent action decisions

---

# PART 3: WHAT THIS MEANS FOR FAMILY B DESIGN

---

## 3.1 Action Ontology (Keep 4-Way or Modify?)

**Recommendation: Keep the 4-way ontology {answer, clarify, verify, abstain}, with three clarifications.**

The literature strongly supports all four actions as distinct, necessary, and measurable. However, three clarifications are needed:

**Clarification 1: Define action triggers operationally**
Each action must have a stated trigger condition to guide annotators and evaluators:
- **Answer**: The model has sufficient parametric knowledge and the query is unambiguous
- **Clarify**: The query has ≥2 meaningfully distinct interpretations with different correct answers; asking would increase expected answer quality
- **Verify**: The model has an answer candidate but uncertain enough that external confirmation would improve reliability; verification is possible via a specific tool or source
- **Abstain**: The query is unanswerable (not just hard); no amount of clarification or verification would yield a correct answer

**Clarification 2: Exclude safety refusals from scope**
Safety refusals (refusing because the query is harmful/unsafe) are out of scope for Family B. Items must not be trivially classifiable as safety refusals. All items should be benign information requests.

**Clarification 3: Consider a "multi-interpret" action as a scored alternative**
For clarify-appropriate items where clarification is not possible (one-shot format), allow "multi-interpret" (providing answers for multiple interpretations) as a partially-credited action. This prevents penalizing models operating in zero-context single-turn settings unfairly.

---

## 3.2 Scoring Approach

**Recommendation: Three-tier scoring with utility matrix as primary, action F1 as diagnostic, AUARC as global quality.**

**Tier 1: Per-item utility score**  
Apply the payoff matrix to each item. The payoff matrix should be validated against human judgments of relative desirability. As a starting point (from Wu et al. 2025 and ReSearch):
- Correct answer: +1.0
- Correct abstain: +0.7 (useful to user: avoids wasted effort)
- Necessary clarification followed by correct answer: +0.9
- Unnecessary clarification (answer was clear): -0.2 (user friction)
- Incorrect answer: -0.8 (misinformation cost)
- False abstention (model can answer but doesn't): -0.3
- Correct verify followed by confirmed answer: +0.85

**Tier 2: Per-class action F1**  
Report precision, recall, F1 for each action class. This is the diagnostic tier — it shows where a model is systematically failing (e.g., never uses verify, over-abstains on clarify items, etc.).

**Tier 3: AUARC**  
For models that output confidence scores, report AUARC. This is the tier-3 global quality metric that is hardest to game.

**Do not use**: Raw accuracy, abstention rate alone, ROUGE for clarification quality, or verbal uncertainty as a proxy for correct action.

---

## 3.3 Item Design Principles

**Seven principles drawn from the literature:**

1. **Each item requires exactly one gold action.** Items with genuine disagreement about the correct action (ambiguous-about-action items) should be excluded or flagged for adjudication. Gold labels require ≥70% annotator agreement.

2. **Clarify items must enumerate competing interpretations.** Each clarify item should include an annotation of: (a) interpretation A → answer A, (b) interpretation B → answer B, (c) what clarifying question resolves the ambiguity, (d) what simulated user response each interpretation yields. This enables automated multi-turn evaluation via simulated users (CLAM methodology).

3. **Abstain items must specify why they are unanswerable.** Use the SelfAware taxonomy: temporal unknowns, subjective/opinion questions, inherently controversial questions, physically unknowable facts, and future-uncertain events. Each item must have an annotator justification for why no answer is correct.

4. **Verify items must specify what tool would help and what it would find.** Generic "this might benefit from search" is insufficient. Each verify item should include: (a) the specific uncertainty type, (b) the specific tool/source type that would resolve it, (c) the expected result.

5. **Include difficulty gradients within each class.** Easy items (clear-cut action), medium items (requires nuanced judgment), hard items (foils that look like they need one action but actually need another). Foil items are critical for anti-gaming.

6. **Avoid annotation contamination.** Do not release item-level gold action labels in public benchmark. Maintain a private evaluation server or use time-limited held-out sets.

7. **Multi-domain coverage.** Cover at least: general knowledge, science/technical, current events (with date constraints), subjective/opinion, domain-specific professional contexts. Domain balance prevents models from exploiting domain-specific abstention policies.

---

## 3.4 Multi-Turn Protocol

**Recommended: Simulated-user 2-turn protocol for clarify items.**

**Protocol:**
1. Present item to model (turn 1 input)
2. Model selects action + content
3. If action = clarify:
   - Simulated user (privileged-intent model) responds to the clarifying question
   - Model generates final answer (turn 3)
   - Score: action correctness (was clarification warranted?) + clarification quality (was the question informative?) + final answer quality
4. If action = answer: score immediately
5. If action = verify: simulate tool response (document lookup or calculation); model produces final answer; score action + final answer
6. If action = abstain: score immediately

**Max turns: 3** (initial → clarify → user response → final answer or initial → verify → tool → final answer)

**Simulated-user construction:** For each clarify item, write two "gold intent documents" (one per interpretation). Given a clarifying question from the model, a simulated-user model selects the appropriate intent document and generates a realistic natural-language response. Validate that simulated-user responses are natural and non-leading.

**Scoring clarification quality:** Use intent-entropy reduction as the quality measure (Zhang & Choi 2023): a good clarifying question reduces the entropy over the user's intent from H(intent) before asking to near-0 after the response. Items with low-information clarifying questions (that don't change the posterior over intents) should be partially credited or not credited.

---

## 3.5 What to Avoid

**Five anti-patterns to avoid, each grounded in literature:**

1. **Avoid binary abstain/answer evaluation only.** The literature (Wu et al. 2025, Zhang & Choi 2023, KnowNo) demonstrates that the clarify and verify actions are distinct from both answering and abstaining, and that conflating them misses systematic failure modes. A 2-way benchmark will not detect models that overhedge, over-ask, or fail to invoke verification when needed.

2. **Avoid verbal tone as a proxy for action.** Yona et al. (2024) demonstrate that verbal hedging is unfaithfully calibrated. A model that says "I think X might be..." could be making a confident or deeply uncertain assertion. Family B must evaluate action selection (the what), not verbal style (the how).

3. **Avoid single-threshold evaluation.** Evaluating at a single abstention threshold (e.g., "the model abstains when it says I don't know") is gameable and threshold-sensitive. Use AUARC or per-class F1 across the full coverage range.

4. **Avoid CoT-only test conditions.** HCMA (Zellinger & Thomson 2024) shows that CoT is counterproductive for selective prediction on free-form tasks. CLAMBER shows that CoT causes overconfidence on ambiguous items. Report results for both CoT and direct-answer conditions.

5. **Avoid unbalanced action distributions.** If 90% of items are answer-appropriate, a model that always answers gets 90% on a naive metric. Balance items across all four action classes, or at minimum report per-class metrics separately.

---

## 3.6 Summary Table: Literature-to-Design Mapping

| Design Decision | Supporting Papers | Recommendation |
|----------------|-------------------|----------------|
| 4-way action ontology | Wu et al. 2025; Zhang & Choi 2023; KnowNo; CLAMBER | Keep, with operational trigger definitions |
| Utility matrix scoring | Wu et al. 2025; ReSearch (Piché et al. 2024) | Primary metric; test risk-sensitivity |
| Action F1 per class | Madhusudhan et al. 2024 (AUCM) | Diagnostic secondary metric |
| AUARC as global metric | Tayebati et al. 2025; Kamath et al. 2020 | Tertiary metric for calibration quality |
| Simulated-user multi-turn | CLAM (Kuhn et al. 2022/2023); Zhang et al. 2024 | ≤3 turn protocol, privileged-intent document |
| Item validity criteria (clarify) | Kobalczyk et al. 2025; CLAMBER | ≥2 interpretations, high info-gain question |
| Item validity criteria (abstain) | Yin et al. 2023; Cole et al. 2023 | Must specify unanswerability type |
| Item validity criteria (verify) | KnowNo; MINT | Specify tool type and expected result |
| 600-1000 item size, balanced 4-way | Standard in literature (Abstain-QA, SelfAware) | 800 items, 200 per class |
| Avoid verbal tone proxy | Yona et al. 2024; Tomani et al. 2024 | Evaluate action, not hedging language |
| Avoid CoT-only | Zellinger & Thomson 2024; CLAMBER | Report both CoT and direct conditions |
| Anti-gaming: penalize all error types | Wu et al. 2025 | Symmetric utility matrix with off-diagonal penalties |
| Anti-gaming: private labels | Wen et al. 2024; McIntosh et al. 2024 | Holdout test labels; public dev only |

---

## Appendix: Additional Relevant Papers (Not Full Summaries)

- **Conformal Linguistic Calibration** (Jiang et al. 2025, arXiv 2502.19110): proposes unifying abstention and linguistic calibration under one framework; relevant for scoring hedge-and-answer vs. abstain
- **Rethinking the Uncertainty** (Beigi et al. 2024, arXiv 2410.20199): comprehensive review of uncertainty sources in LLMs; useful for item type design
- **SAUP: Situation Awareness Uncertainty Propagation** (Zhao et al. 2024): uncertainty propagation in multi-step agents; relevant for verify-action items
- **Adaptation with Self-Evaluation for Selective Prediction** (Chen et al. 2023, EMNLP Findings): parameter-efficient approach to selective prediction; useful baseline
- **Calibrating Verbal Uncertainty as Linear Feature** (Ji et al. 2025): identifies that verbal uncertainty is a single linear feature in representation space; supports verbal uncertainty elicitation as one valid signal
- **DeLLMa: Decision Making Under Uncertainty** (Liu et al. 2024): proposes decision-tree approach for LLM decision-making under uncertainty; relevant for verify action design
- **LACIE: Listener-Aware Finetuning for Confidence Calibration** (Stengel-Eskin et al. 2024): models listener perception of confidence; relevant for understanding how LLM confidence expressions are received by evaluators
- **Knowledge of Knowledge: Known-Unknowns** (Amayuelas et al. 2024): studies models' ability to articulate what they don't know; directly relevant to abstain-action item construction
- **To Believe or Not to Believe Your LLM** (Abbasi Yadkori et al. 2024): information-theoretic metric separating epistemic and aleatoric uncertainty; informs when abstain vs. clarify is appropriate
- **CondAmbigQA** (Li et al. 2025): benchmark for conditional ambiguous QA; model for constructing clarify-action items with conditioned interpretations
- **Selectively Answering Ambiguous Questions** (Cole et al. 2023, EMNLP): already summarized above, also proposes F1-based selective prediction metric under ambiguity
- **Navigating the Grey Area** (Zhou et al. 2023): how epistemic markers in input affect model behavior; relevant for designing foil items

---

*Literature review completed: March 2026*  
*Total papers surveyed: 50+ (25 full summaries, additional references in Appendix)*  
*Prepared for: MetaJudge Benchmark Project, Phase 1A*
