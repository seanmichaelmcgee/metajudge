# From Feeling-of-Knowing to "I Don't Know": Metacognition's Journey from Psychology to LLMs

## An Annotated Bibliography and Theoretical Framework for Testing Selective Verification, Clarification, and Abstention

---

**Abstract.** The capacity to know what you don't know — and act on that knowledge — is among the most consequential abilities studied in cognitive science, and it is now the central unsolved problem in trustworthy AI. A coherent intellectual lineage connects Hart's 1965 feeling-of-knowing experiments, through Nelson and Narens' monitoring-control framework, Koriat and Goldsmith's report/withhold paradigm, and modern signal-detection approaches to metacognition, directly to the 2024–2026 explosion of research on LLM calibration, selective abstention, and hallucination-as-metacognitive-failure. This report traces that lineage across three research domains — foundational psychological theory, modern cognitive psychology, and recent AI/ML research — identifying over 80 key papers that collectively define the science of selective clarification, verification, and abstention as metacognition. The convergence is not merely analogical: recent bridging papers by Steyvers and Peters (2025), Wang et al. (2025, AAAI), and Ackerman et al. (2025) now explicitly apply psychological metacognition theory — including Fleming and Lau's meta-d' framework and animal-cognition paradigms — to evaluate and improve LLM self-knowledge.

---

## Table of Contents

1. [Domain 1: The Psychological Architecture of Knowing What You Know](#domain-1-the-psychological-architecture-of-knowing-what-you-know)
   - [Flavell's Taxonomy and the Birth of Metacognition](#flavells-taxonomy-and-the-birth-of-metacognition-as-a-field)
   - [Nelson and Narens: Monitoring-Control Framework](#nelson-and-narens-the-monitoring-control-architecture)
   - [FOK, JOL, and TOT: The Empirical Paradigms](#fok-jol-and-tot-the-empirical-paradigms)
   - [Metcalfe and the Productive Role of Error Detection](#metcalfe-and-the-productive-role-of-metacognitive-error-detection)
   - [Calibration, Overconfidence, and Dunning-Kruger](#calibration-overconfidence-and-the-dunning-kruger-problem)
   - [Koriat's Cue-Utilization Theory](#koriats-cue-utilization-theory-why-metacognitive-monitoring-is-inferential)
   - [The Goldsmith-Koriat Framework: Selective Reporting](#the-goldsmith-koriat-framework-metacognitive-regulation-of-accuracy-through-selective-reporting)
   - [Epistemic Vigilance](#epistemic-vigilance-and-the-social-dimension-of-metacognition)
2. [Domain 2: Modern Advances in Metacognitive Science (2012–2025)](#domain-2-modern-advances-in-metacognitive-science-20122025)
   - [Signal Detection Theory and meta-d'](#signal-detection-theory-and-the-meta-d-revolution)
   - [Fleming's Synthesis: Confidence as Inference](#flemings-synthesis-confidence-as-model-based-inference)
   - [Meta-Reasoning: Feeling of Rightness](#meta-reasoning-the-feeling-of-rightness-and-strategic-effort-allocation)
   - [Children's Selective Trust](#childrens-selective-trust-developmental-origins-of-epistemic-verification)
   - [Curiosity and Deliberate Ignorance](#curiosity-as-metacognitive-signal-and-deliberate-ignorance-as-metacognitive-strategy)
   - [Help-Seeking as Metacognition](#help-seeking-as-metacognitive-behavior)
3. [Domain 3: LLM Metacognition — The Critical Frontier (2022–2026)](#domain-3-llm-metacognition--the-critical-frontier-20222026)
   - [Language Models (Mostly) Know What They Know](#the-foundational-finding-language-models-mostly-know-what-they-know)
   - [Calibration and the Overconfidence Problem](#calibration-and-confidence-the-overconfidence-problem-replicates)
   - [RLHF Degrades Calibration](#rlhf-degrades-calibration-and-induces-sycophancy)
   - [Semantic Entropy](#semantic-entropy-detecting-uncertainty-at-the-level-of-meaning)
   - [Self-Consistency and Introspection](#self-consistency-and-introspective-capabilities)
   - [Selective Prediction and Abstention](#selective-prediction-and-abstention-teaching-models-when-not-to-answer)
   - [Hallucination as Metacognitive Failure](#hallucination-as-metacognitive-failure)
   - [Conformal Prediction](#conformal-prediction-formal-uncertainty-guarantees-for-llms)
   - [The Psychology-AI Bridge](#the-emerging-psychology-ai-bridge-two-landmark-papers)
4. [Comprehensive Source Inventory](#comprehensive-source-inventory-organized-by-domain)
5. [Theoretical Framework for Robust Testing](#toward-a-theoretical-framework-for-testing-metacognitive-selective-verification-clarification-and-abstention)
6. [Conclusion](#conclusion)

---

## Domain 1: The Psychological Architecture of Knowing What You Know

### Flavell's Taxonomy and the Birth of Metacognition as a Field

John Flavell's 1979 paper in *American Psychologist* ("Metacognition and Cognitive Monitoring: A New Area of Cognitive-Developmental Inquiry") coined the term **metacognition** and proposed a four-component model: metacognitive knowledge (subdivided into person, task, and strategy variables), metacognitive experiences, goals, and actions. This taxonomy established that humans possess structured knowledge about their own cognitive capacities and limitations — the conceptual prerequisite for any theory of selective verification or abstention. Flavell's developmental findings showed that younger children are poor at monitoring their own readiness and comprehension, implying that metacognitive monitoring is a skill that matures, not a fixed capacity.

> **Relevance to LLMs:** Flavell's distinction between metacognitive *knowledge* (what the system knows about its own capabilities) and metacognitive *experiences* (real-time signals of cognitive difficulty) maps directly onto the distinction between learned self-knowledge (P(IK) in Kadavath et al., 2022) and online uncertainty signals (semantic entropy in Kuhn et al., 2023).

### Nelson and Narens: The Monitoring-Control Architecture

The field's dominant process architecture came from **Nelson and Narens (1990)**, who formalized the distinction between an **object-level** (where cognition occurs) and a **meta-level** (which monitors and controls the object-level). Their framework identifies two information flows: monitoring (object→meta, analogous to listening) and control (meta→object, analogous to speaking). Critically, they enumerated four distinct monitoring judgments — **ease-of-learning (EOL), judgments of learning (JOL), feeling-of-knowing (FOK), and confidence judgments** — and showed these are not highly correlated, suggesting they tap different aspects of memory through multidimensional underlying structures. The monitoring-control architecture remains the standard theoretical scaffold for metacognition research and, as discussed below, has been directly imported into LLM evaluation frameworks.

> **Relevance to LLMs:** The monitoring-control distinction is the single most important theoretical import for LLM metacognition research. Orgad et al. (2024) demonstrated that LLMs can possess monitoring (internal truthfulness encoding) without effective control (appropriate response selection) — precisely the dissociation Nelson and Narens' architecture predicts.

### FOK, JOL, and TOT: The Empirical Paradigms

The experimental study of metacognitive monitoring began with **Hart (1965)**, who developed the **recall-judgment-recognition (RJR) paradigm**: participants attempt recall, make FOK judgments for nonrecalled items, then take a recognition test. Hart's foundational finding — that recognition performance was significantly above chance for items eliciting strong FOK, and at chance for items not eliciting FOK — established that people have genuine if imperfect access to what is stored in memory, even when they cannot retrieve it. His "target strength" account proposed that FOK directly taps memory trace activation.

**Nelson and Dunlosky (1991)** transformed JOL research with the **delayed-JOL effect**: judgments of learning made after a short delay (on the cue alone) are "extremely accurate" at predicting subsequent recall, because delayed JOLs are based on covert retrieval from long-term memory rather than short-term accessibility. This finding has major implications for self-regulated learning and demonstrates that monitoring accuracy depends critically on the conditions under which judgments are made.

**Brown and McNeill (1966)** provided the first systematic study of tip-of-the-tongue (TOT) states, showing that during retrieval failure, participants retain accurate partial information — number of syllables, first letter, stress pattern — a phenomenon they termed "generic recall." Schwartz (1999, 2006) reframed TOT as a **metacognitive experience** rather than a purely cognitive state, arguing that TOTs are based on heuristic inference from cues like cue familiarity and accessibility of partial information. Schwartz and Metcalfe (2011) synthesized direct-access and inferential accounts, showing that TOTs prompt metacognitive control processes — increased information-seeking and extended retrieval attempts — directly relevant to selective verification behavior.

### Metcalfe and the Productive Role of Metacognitive Error Detection

Janet Metcalfe's program of research revealed that metacognitive monitoring of errors can be *productive*. The **hypercorrection effect** (Butterfield & Metcalfe, 2001) showed that high-confidence errors are more easily corrected after feedback than low-confidence errors — counterintuitively, the stronger one's mistaken belief, the better the subsequent learning. The mechanism appears to involve **metacognitive mismatch**: when confident expectations collide with corrective feedback, the resulting surprise captures attention and enhances encoding (Butterfield & Metcalfe, 2006). Metcalfe's broader review (2017, *Annual Review of Psychology*) argued that error avoidance is counterproductive for learning — errorful learning followed by feedback is beneficial, especially when learners strongly believed their incorrect answers. This work demonstrates that the metacognitive system can productively use the detection of "not knowing" to drive enhanced learning.

Metcalfe (1986) also revealed a critical dissociation: FOK predicted recognition performance for trivia questions but **did not predict problem-solving success** for insight problems, demonstrating that metacognitive monitoring operates differently across cognitive domains — a finding with implications for understanding domain-specificity of LLM self-knowledge.

### Calibration, Overconfidence, and the Dunning-Kruger Problem

The empirical observation motivating much of the abstention literature is that **human confidence judgments are systematically miscalibrated**. Lichtenstein, Fischhoff, and Phillips (1982), in their landmark review within *Judgment under Uncertainty*, documented pervasive overconfidence: when people report 90% confidence, they are typically correct only 70–80% of the time. They identified the **hard-easy effect** — overconfidence is exaggerated for difficult items and may reverse to mild underconfidence for easy items.

**Kruger and Dunning (1999)** extended this observation with their "dual-burden" account: participants in the bottom quartile of performance estimated themselves at the 62nd percentile (actual: 12th percentile). The same skills needed to produce correct answers are needed to evaluate answer quality, creating a metacognitive blind spot precisely where monitoring is most needed. Study 4 demonstrated that training in logical reasoning improved bottom-quartile calibration, confirming the metacognitive explanation. The Dunning-Kruger effect has direct relevance to LLM calibration: as documented below, worse-performing models exhibit the most severe overconfidence, paralleling the human pattern.

### Koriat's Cue-Utilization Theory: Why Metacognitive Monitoring is Inferential

Asher Koriat's work fundamentally changed the field's understanding of metacognitive mechanisms. His **accessibility model of FOK** (Koriat, 1993) proposed that FOK is "parasitic on retrieval processes" — based on the amount and speed of partial information that comes to mind, regardless of whether that information is correct. FOK increases with greater accessibility of related information, even when wrong. His **cue-utilization framework for JOLs** (Koriat, 1997) distinguished three cue classes: intrinsic cues (item properties), extrinsic cues (study conditions), and mnemonic cues (processing fluency, accessibility). The critical finding: people discount extrinsic factors and rely primarily on intrinsic cues and heuristics, producing systematic biases. Koriat and Levy-Sadot (2001) proposed a **cascaded model** integrating cue familiarity and accessibility, with familiarity effects occurring early and accessibility effects later.

The inferential, heuristic nature of metacognitive judgments explains why selective abstention is difficult: the monitoring signals that drive report/withhold decisions can be systematically misleading.

### The Goldsmith-Koriat Framework: Metacognitive Regulation of Accuracy Through Selective Reporting

The most directly relevant body of psychological work for understanding selective abstention is **Koriat and Goldsmith's (1996) monitoring-and-control framework** for the strategic regulation of memory accuracy. This framework posits a three-stage process:

1. **Generation** of a candidate answer
2. **Monitoring** — subjective confidence assessment
3. **Control** — comparison of confidence against a criterion to decide whether to **report or withhold**

When free to withhold, people substantially enhance accuracy (output-bound measure) at the cost of reduced quantity (input-bound measure), producing an **accuracy-quantity tradeoff**.

Goldsmith, Koriat, and Weinberg-Eliezer (2002) extended this to **grain-size regulation**: rememberers strategically coarsen their answers (e.g., "sometime in the early evening" instead of "6:30 PM") when uncertain, increasing accuracy at the cost of informativeness — a satisficing model. Their comprehensive review (Goldsmith & Koriat, 2007) integrated both control mechanisms into a **dual-criterion model**: people strive for the most precise-informative answer that jointly satisfies minimum-confidence and minimum-informativeness criteria.

This framework is the direct psychological analog of LLM selective prediction: effective abstention requires both good monitoring (discriminating correct from incorrect) and appropriate control policy (setting the right threshold). Koriat, Goldsmith, Schneider, and Nakash-Dura (2001) applied the framework developmentally, showing that even 7–9 year-olds can enhance accuracy through selective reporting, with improvement through age 12 — demonstrating that metacognitive regulation of accuracy through abstention develops gradually.

> **Key insight for LLM testing:** The Goldsmith-Koriat framework implies that testing LLM abstention requires evaluating *both* monitoring quality (can the model discriminate its correct from incorrect answers?) and control policy (does the model set appropriate thresholds for reporting vs. withholding?). These are separable capacities.

### Epistemic Vigilance and the Social Dimension of Metacognition

Sperber et al. (2010) introduced **epistemic vigilance** — cognitive mechanisms for evaluating the reliability and trustworthiness of communicated information — arguing it operates via vigilance toward the source (assessing competence and benevolence) and vigilance toward the content (evaluating coherence with background knowledge). This is not the opposite of trust but the opposite of *blind trust*; communication can only remain advantageous if receivers maintain sufficient vigilance. Mercier and Sperber (2011) reinterpreted reasoning itself as evolved for argumentative contexts — producing arguments to convince others and evaluating others' arguments — explaining the confirmation bias as a feature of argument production rather than a general reasoning deficit. The critical asymmetry: argument **production** is biased, but argument **evaluation** is more objective, explaining why groups that debate outperform individuals.

Epistemic vigilance provides the evolutionary and communicative context for understanding why agents — human or artificial — need metacognitive monitoring of information reliability.

---

## Domain 2: Modern Advances in Metacognitive Science (2012–2025)

### Signal Detection Theory and the meta-d' Revolution

The measurement of metacognition was transformed by **Maniscalco and Lau (2012)**, who proposed **meta-d'** — a signal-detection-theory measure of metacognitive sensitivity that quantifies how much information is available for metacognition in signal-to-noise units, free from confounds of response bias and first-order performance. If meta-d' equals d', the observer is "metacognitively ideal"; typically **meta-d' < d'**, reflecting metacognitive inefficiency. The ratio **meta-d'/d' (Mratio)** provides a performance-controlled metric of metacognitive capacity. Fleming (2017) released the **HMeta-d toolbox** for hierarchical Bayesian estimation, now the standard method for group-level analysis.

Mazancieux et al. (2020) found positive correlations in metacognitive efficiency across perception and memory tasks, suggesting a **domain-general component** of metacognition alongside domain-specific variance. Rahnev et al. (2020) aggregated confidence data from many labs into the Confidence Database, enabling large-scale comparative studies.

> **Relevance to LLMs:** The meta-d' framework has been directly imported into LLM evaluation: Wang et al. (2025, AAAI) explicitly use SDT-based metrics from Fleming and Lau's framework to decouple metacognitive ability from cognitive ability in LLMs.

### Fleming's Synthesis: Confidence as Model-Based Inference

Stephen Fleming's comprehensive 2024 review in *Annual Review of Psychology* ("Metacognition and Confidence: A Review and Synthesis") represents the most authoritative modern synthesis. The central concept is **propositional confidence** — confidence in one's own decisions as informed by self-models that can be inaccurate. Key neural findings include the critical role of **rostrolateral PFC (BA10/46)** for metacognitive accuracy and distinct brain systems supporting metacognition in perception versus memory. Fleming and Daw (2017) proposed a Bayesian framework where confidence is computed via a noisy readout of the decision variable plus a learned prior over expected performance, explaining confidence biases as resulting from inaccurate self-models.

Rollwage, Dolan, and Fleming (2018) demonstrated that people holding radical beliefs showed **reduced metacognitive sensitivity** — less ability to update confidence in response to disconfirming evidence. Rollwage et al. (2020) showed that confidence causally biases subsequent evidence processing, creating a "neural confirmation bias." These findings demonstrate real-world consequences of metacognitive failure that parallel LLM overconfidence and sycophancy.

### Meta-Reasoning: The Feeling of Rightness and Strategic Effort Allocation

Ackerman and Thompson (2017) developed the **meta-reasoning framework**, extending metacognition to reasoning and problem-solving. They introduced the **Feeling of Rightness (FOR)** — an initial fluency-based metacognitive assessment of an answer — and showed that fluency is a pervasive but unreliable cue: answers that come quickly engender strong FOR regardless of accuracy. Low FOR triggers deeper analytical processing; high FOR may lead to premature termination. Critically, they observed that in laboratory reasoning tasks, "reasoners are not afforded the opportunity to 'give up,' even though this option is available in most real-world contexts" — highlighting that strategic abstention is a natural metacognitive control behavior systematically excluded from standard experimental paradigms.

### Children's Selective Trust: Developmental Origins of Epistemic Verification

Research by Koenig, Harris, and Corriveau established that young children are **not indiscriminately credulous**. Harris and Corriveau (2011) demonstrated that children as young as 3 track informant accuracy and maintain preferences for previously accurate informants for at least one week. Koenig and Harris (2005) showed preschoolers preferentially trust accurate over inaccurate speakers. Harris et al. (2018, *Annual Review of Psychology*) synthesized decades of work, showing children evaluate informants based on accuracy, confidence, consensus, group membership, and access to information. The developmental trajectory — emerging selectivity at 3, robust selective trust by 4–5 — establishes that epistemic verification is a foundational human cognitive capacity, not a sophisticated adult skill.

### Curiosity as Metacognitive Signal and Deliberate Ignorance as Metacognitive Strategy

Kidd and Hayden (2015) advocated a functional approach to curiosity, noting that infants show a **Goldilocks effect** — preference for intermediate information content. Gruber, Gelman, and Ranganath (2014) demonstrated that curiosity enhances memory for target information and incidental material, with neural mechanisms involving midbrain dopaminergic circuits and enhanced hippocampal connectivity. Gruber and Ranganath (2019) proposed the **PACE framework**: Prediction errors → Appraisal → Curiosity → Exploration — explicitly linking uncertainty detection to metacognitive appraisal and strategic information-seeking. Metcalfe, Schwartz, and Eich (2020) proposed that epistemic curiosity is calibrated to the **Region of Proximal Learning** — people are most curious about information they feel close to knowing, not things they know or are entirely ignorant about.

On the opposite end, **Hertwig and Engel (2016)** defined "deliberate ignorance" — the conscious choice not to seek or use knowledge — showing that up to 90% of people in some contexts choose not to learn predictive information. Their edited volume (2021, MIT Press) explored deliberate ignorance across domains. Vu et al. (2023, *Psychological Bulletin*) conducted a meta-analysis across 33,603 decisions, finding that the ability to avoid information about consequences decreases altruistic behavior. These findings establish that strategic not-knowing is adaptive — a form of metacognitive control where agents deliberately limit their own information to improve outcomes.

### Help-Seeking as Metacognitive Behavior

Undorf, Livneh, and Ackerman (2021) compared help-seeking and answer-withholding as metacognitive strategies, finding that the confidence-help-seeking association was **weaker** than the confidence-withholding association. This suggests help-seeking involves social and strategic considerations beyond simple confidence monitoring — it is guided by a wider variety of metacognitive and social signals, making it qualitatively different from simple abstention.

---

## Domain 3: LLM Metacognition — The Critical Frontier (2022–2026)

### The Foundational Finding: Language Models (Mostly) Know What They Know

**Kadavath et al. (2022)** from Anthropic established the empirical foundation with "Language Models (Mostly) Know What They Know." Studying models up to 52B parameters across diverse QA datasets, they found that **larger models are well-calibrated** on multiple-choice and true/false questions. Models can self-evaluate via **P(True)** — proposing answers then evaluating their own correctness — with performance improving when models consider many of their own samples. They trained **P(IK) ("probability I know")**, a question-only confidence predictor that generalizes across tasks. This paper (370+ citations) established that LLMs possess meaningful metacognitive-like abilities and spawned the entire field of LLM self-knowledge research.

### Calibration and Confidence: The Overconfidence Problem Replicates

A central finding across multiple 2024–2025 papers is that **LLMs are systematically overconfident**, mirroring human metacognitive biases. Xiong et al. (2024, ICLR) developed a systematic framework for confidence elicitation — prompting strategies, sampling methods, and aggregation techniques — and found that verbalized confidence values cluster in the **80–100% range in multiples of 5**, mimicking human confidence patterns. Calibration improves with model scale but remains far from ideal, and no technique consistently dominates. Groot and Valdenegro-Toro (2024) confirmed systematic overconfidence in verbalized uncertainty across both language and vision-language models.

A counterintuitive finding from **Tian et al. (2023, EMNLP)** is that for RLHF-trained models (ChatGPT, GPT-4, Claude), **verbalized confidence is often better-calibrated than token-level conditional probabilities**, reducing Expected Calibration Error by ~50% relatively. This was preceded by the foundational work of **Lin, Hilton, and Evans (2022, TMLR)**, who first demonstrated that GPT-3 can learn to express calibrated uncertainty in natural language without logit access. However, **Yona, Aharoni, and Geva (2024, EMNLP)** provided an important counterpoint: with standard decoding, models answer decisively even when internally uncertain, and when prompted to hedge, hedges are not faithful to intrinsic uncertainty — revealing a gap between internal knowledge and expressed uncertainty.

The **Dunning-Kruger effect replicates in LLMs**: Singh et al. (2024/2025) found systematic overconfidence patterns where poorly performing models exhibit the most severe overconfidence (ECE = 0.726 for worst-performing model), with better-performing models showing progressively better calibration.

### RLHF Degrades Calibration and Induces Sycophancy

**Leng et al. (2024, ICLR 2025)** demonstrated that RLHF leads models to express verbalized overconfidence because reward models exhibit inherent biases toward high-confidence scores regardless of response quality. Their proposed PPO-M (Calibrated Reward Modeling) reduces ECE by 6.44 points while increasing accuracy on GSM8K. **Sharma et al. (2023, ICLR 2024)** documented sycophancy — five state-of-the-art AI assistants consistently agree with users across four free-form tasks, sometimes sacrificing truthfulness. Sycophancy represents a **metacognitive control failure**: models prioritize agreement over truthful self-assessment. A 2025 study in *npj Digital Medicine* found up to 100% initial compliance with illogical medical requests, highlighting the tension RLHF creates between helpfulness and accuracy.

The emerging solution involves calibration-aware training: **Bani-Harouni et al. (ICLR 2026)** used RL with a logarithmic scoring rule reward to train LLMs to express calibrated confidence, penalizing both over- and under-confidence, with models generalizing to unseen tasks.

### Semantic Entropy: Detecting Uncertainty at the Level of Meaning

A major methodological advance came from **Kuhn, Gal, and Farquhar (2023, ICLR)**, who introduced **semantic entropy** — entropy computed over clusters of semantically equivalent outputs rather than individual token sequences, addressing the fundamental problem that different sentences can mean the same thing. **Farquhar et al. (2024, *Nature*)** extended this to detect "confabulations" — their proposed replacement for "hallucination" — by sampling multiple answers, clustering by semantic equivalence using NLI models, and computing entropy within clusters. High semantic entropy indicates likely confabulation, working across datasets without ground-truth answers. Published in *Nature* with 600+ citations, this work established semantic-level uncertainty estimation as the state of the art. **Kossen et al. (2024)** introduced Semantic Entropy Probes (SEPs) that approximate semantic entropy from hidden states of a single generation, reducing computational cost 5–10x while maintaining performance.

### Self-Consistency and Introspective Capabilities

**Wang et al. (2023, ICLR)** introduced self-consistency decoding — sampling diverse reasoning paths and selecting the most consistent answer via marginalization — boosting Chain-of-Thought performance by up to 17.9% on GSM8K. Low consistency serves as an implicit indicator of low confidence, conferring "some ability for the model to 'know when it doesn't know.'" **Azaria and Mitchell (2023, Findings of EMNLP)** showed that classifiers trained on internal model activations can predict whether LLM outputs are truthful, demonstrating that internal states encode information about truthfulness. An ICML 2025 position paper argued that "truly self-improving agents require intrinsic metacognitive learning," proposing a formal framework comprising metacognitive knowledge, planning, and evaluation.

### Selective Prediction and Abstention: Teaching Models When Not to Answer

The abstention literature has exploded since 2024. **Wen et al. (2025, TACL)** provide the most comprehensive survey, introducing a three-perspective framework examining abstention from query, model, and human-values perspectives, arguing that abstention should be treated as a **"meta-capability" transcending specific tasks**. **Zhang et al. (2024, NAACL, Outstanding Paper)** introduced **R-Tuning** — Refusal-Aware Instruction Tuning — training models to refuse when uncertain by constructing refusal-aware datasets at the knowledge intersection. Their key finding: refusal ability is a **transferable meta-skill** that generalizes across tasks and domains. **Cheng et al. (2024, ICML)** used a **knowledge quadrants** framework (Known Knowns, Known Unknowns, Unknown Knowns, Unknown Unknowns) to evaluate AI assistant self-knowledge, aligning models using SFT, DPO, and PPO to refuse unknown questions.

**AbstentionBench (2025)** represents the most comprehensive evaluation benchmark, spanning 20 diverse datasets and 20 frontier LLMs. Its most striking finding: **reasoning fine-tuning degrades abstention by 24% on average**, even in domains where reasoning models excel. This reveals a fundamental tension — optimizing for cognitive capability may come at the cost of metacognitive capability.

**Xu et al. (2024, EMNLP)** introduced **SaySelf**, which trains LLMs to express fine-grained confidence and produce **self-reflective rationales** identifying knowledge gaps — the closest existing work to implementing Nelson and Narens' monitoring-plus-reporting architecture in an LLM. Srinivasan et al. (2024) addressed the complementary problem of over-abstention with ReCoVERR, which searches for confirming evidence before committing to abstention — implementing a metacognitive verification loop analogous to human "double-checking."

### Hallucination as Metacognitive Failure

The reconceptualization of hallucination as a metacognitive problem — rather than a purely generative one — represents a major theoretical advance. **Wang et al. (2025, AAAI)** proposed the **DMC (Decoupling Metacognition from Cognition) framework**, drawing directly from cognitive psychology's Signal Detection Theory and the Fleming and Lau meta-d' framework. Their approach separately quantifies metacognitive ability independent of task performance, finding that **enhancing metacognition holds promise for alleviating hallucination**. They explicitly argue that hallucination's root cause is the absence of metacognition in LLMs.

**Orgad et al. (2024, ICLR 2025)** demonstrated that LLMs' internal representations encode far more truthfulness information than previously recognized, concentrated in specific "answer tokens." Their critical finding: **LLMs may internally encode the correct answer yet consistently generate an incorrect one** — a fundamental metacognitive failure where monitoring exists but control does not. This directly parallels the monitoring-control distinction in Nelson and Narens' framework and provides empirical evidence for a computational analog to the human gap between metacognitive awareness and metacognitive regulation.

**Gekhman et al. (2024, EMNLP)** showed that fine-tuning on examples with new knowledge (not in pretraining) is learned slower and, once learned, increases hallucination tendency — suggesting that standard SFT can disrupt metacognitive calibration by preventing models from distinguishing what they know from what they don't.

### Conformal Prediction: Formal Uncertainty Guarantees for LLMs

Conformal prediction has emerged as a principled framework providing distribution-free coverage guarantees. **Quach et al. (2024, ICLR)** produced prediction sets with formal guarantees for language models, including methods to identify non-hallucinated phrases. **Wang et al. (2024, EMNLP Findings)** introduced ConU, integrating self-consistency with conformal prediction for black-box LLMs, achieving strict correctness coverage control across 7 LLMs. Campos et al. (2024, *Transactions of the ACL*) provided a comprehensive survey of conformal prediction techniques in NLP. These approaches offer something psychological metacognition cannot: formal mathematical guarantees on the reliability of uncertainty estimates.

### The Emerging Psychology-AI Bridge: Two Landmark Papers

Two papers published in 2025 represent the emergence of a genuine interdisciplinary field connecting cognitive science metacognition theory to LLM evaluation.

**Steyvers and Peters (2025, *Current Directions in Psychological Science*)** provide the most comprehensive bridging paper, directly comparing human and LLM metacognitive capacities. Their key findings: both humans and LLMs exhibit overconfidence; both achieve similar **metacognitive sensitivity** (confidence discriminates correct from incorrect); LLMs match human perception of linguistic uncertainty; and metacognitive sensitivity can be improved through fine-tuning, paralleling human training effects. A critical difference: training on single-question confidence does NOT transfer to pairwise comparison tasks, suggesting different metacognitive skills must be developed together. They explicitly use AUROC type-2, ECE, and Brier score from the human metacognition literature.

**Ackerman et al. (2025)** introduce a methodology for evaluating LLM metacognition **inspired by research on metacognition in nonhuman animals** — eschewing self-reports in favor of behavioral tests of strategic deployment of internal state knowledge. Using confidence-based bet sizing and anticipating own answers, they find frontier LLMs since early 2024 show **increasingly strong metacognitive abilities** that are nevertheless limited in resolution, context-dependent, and seemingly qualitatively different from humans. This represents the most rigorous attempt to apply cognitive science paradigms to LLMs without relying on the potentially unreliable self-report.

**Wang et al. (2024, NAACL)** proposed **Metacognitive Prompting (MP)**, explicitly operationalizing Flavell's metacognitive stages in a five-stage prompting framework: understanding input, preliminary judgment, critical evaluation of that judgment, final judgment, and confidence expression — outperforming Chain-of-Thought across 10 NLU datasets.

---

## Comprehensive Source Inventory Organized by Domain

### Domain 1: Foundational Psychological Literature

| Authors | Year | Title | Venue | Key Contribution |
|---------|------|-------|-------|-----------------|
| Flavell | 1979 | Metacognition and Cognitive Monitoring | *American Psychologist*, 34(10), 906–911 | Coined metacognition; person/task/strategy taxonomy |
| Nelson & Narens | 1990 | Metamemory: A Theoretical Framework and New Findings | *Psychology of Learning and Motivation*, 26, 125–173 | Object-level/meta-level; monitoring-control architecture |
| Hart | 1965 | Memory and the Feeling-of-Knowing Experience | *J. Educational Psychology*, 56(4), 208–216 | First FOK study; RJR paradigm |
| Hart | 1967 | Memory and the Memory-Monitoring Process | *J. Verbal Learning and Verbal Behavior*, 6(5), 685–691 | Extended FOK to paired-associates |
| Nelson & Dunlosky | 1991 | When People's JOLs Are Extremely Accurate | *Psychological Science*, 2(4), 267–270 | Delayed-JOL effect |
| Brown & McNeill | 1966 | The "Tip of the Tongue" Phenomenon | *J. Verbal Learning and Verbal Behavior*, 5(4), 325–337 | First TOT study; generic recall |
| Schwartz | 2006 | Tip-of-the-Tongue States as Metacognition | *Metacognition and Learning*, 1(2), 149–158 | TOT as metacognitive experience |
| Schwartz & Metcalfe | 2011 | TOT States: Retrieval, Behavior, and Experience | *Memory & Cognition*, 39(5), 737–749 | Synthesis of direct-access and inferential views |
| Metcalfe | 1986 | Feeling of Knowing in Memory and Problem Solving | *J. Exp. Psych: LMC*, 12(2), 288–294 | FOK dissociation: memory vs. insight |
| Butterfield & Metcalfe | 2001 | Errors Committed with High Confidence Are Hypercorrected | *J. Exp. Psych: LMC*, 27(6), 1491–1494 | Hypercorrection effect |
| Metcalfe | 2017 | Learning from Errors | *Annual Review of Psychology*, 68, 465–489 | Error tolerance benefits learning |
| Lichtenstein et al. | 1982 | Calibration of Probabilities: State of the Art to 1980 | *Judgment under Uncertainty*, Cambridge UP, 306–334 | Pervasive overconfidence; hard-easy effect |
| Kruger & Dunning | 1999 | Unskilled and Unaware of It | *JPSP*, 77(6), 1121–1134 | Dual-burden metacognitive account |
| Koriat | 1993 | How Do We Know That We Know? The Accessibility Model of FOK | *Psychological Review*, 100(4), 609–639 | FOK based on accessible partial information |
| Koriat | 1997 | Monitoring One's Own Knowledge During Study | *J. Exp. Psych: General*, 126(4), 349–370 | Cue-utilization framework |
| Koriat & Levy-Sadot | 2001 | Combined Contributions of Cue-Familiarity and Accessibility to FOK | *J. Exp. Psych: LMC*, 27(1), 34–53 | Cascaded model of FOK |
| Koriat & Goldsmith | 1996 | Monitoring and Control in Strategic Regulation of Memory Accuracy | *Psychological Review*, 103(3), 490–517 | Report/withhold paradigm |
| Koriat & Goldsmith | 1994 | Memory in Naturalistic and Laboratory Contexts | *J. Exp. Psych: General*, 123(3), 297–315 | Storehouse vs. correspondence metaphors |
| Goldsmith et al. | 2002 | Strategic Regulation of Grain Size in Memory Reporting | *J. Exp. Psych: General*, 131(1), 73–95 | Grain-size satisficing model |
| Goldsmith & Koriat | 2007 | Strategic Regulation of Memory Accuracy and Informativeness | *Psych. of Learning and Motivation*, 48, 1–60 | Dual-criterion model |
| Sperber et al. | 2010 | Epistemic Vigilance | *Mind & Language*, 25(4), 359–393 | Source and content vigilance |
| Mercier & Sperber | 2011 | Why Do Humans Reason? | *BBS*, 34(2), 57–74 | Argumentative theory of reasoning |
| Metcalfe & Shimamura | 1994 | *Metacognition: Knowing About Knowing* | MIT Press | Landmark edited volume |

### Domain 2: Modern Cognitive Psychology (2012–2025)

| Authors | Year | Title | Venue | Key Contribution |
|---------|------|-------|-------|-----------------|
| Maniscalco & Lau | 2012 | SDT Approach for Estimating Metacognitive Sensitivity | *Consciousness and Cognition*, 21(1), 422–430 | Meta-d' measure |
| Fleming | 2017 | HMeta-d: Hierarchical Bayesian Estimation | *Neuroscience of Consciousness*, 3(1), nix007 | Standard Bayesian toolbox |
| Fleming | 2024 | Metacognition and Confidence: A Review and Synthesis | *Annual Review of Psychology*, 75, 241–268 | Most comprehensive modern review |
| Fleming & Daw | 2017 | Self-Evaluation of Decision-Making | *Psychological Review*, 124(1), 91–114 | Bayesian metacognitive computation |
| Fleming & Lau | 2014 | How to Measure Metacognition | *Frontiers in Human Neuroscience*, 8, 443 | Methods comparison |
| Mazancieux et al. | 2020 | Is There a G Factor for Metacognition? | *J. Exp. Psych: General*, 149(9), 1788–1799 | Domain-general component |
| Rollwage et al. | 2018 | Metacognitive Failure as Feature of Radical Beliefs | *Current Biology*, 28(24), 4014–4021 | Radical beliefs → reduced metacognition |
| Ackerman & Thompson | 2017 | Meta-Reasoning: Monitoring and Control of Thinking | *Trends in Cognitive Sciences*, 21(8), 607–617 | FOR framework |
| Harris & Corriveau | 2011 | Young Children's Selective Trust in Informants | *Phil. Trans. R. Soc. B*, 366, 1179–1187 | Informant tracking by age 3 |
| Harris et al. | 2018 | Cognitive Foundations of Learning from Testimony | *Annual Review of Psychology*, 69, 251–273 | Children's epistemic trust review |
| Koenig & Harris | 2005 | Preschoolers Mistrust Ignorant and Inaccurate Speakers | *Child Development*, 76(6), 1261–1277 | Preferential trust in accuracy |
| Kidd & Hayden | 2015 | The Psychology and Neuroscience of Curiosity | *Neuron*, 88(3), 449–460 | Goldilocks effect |
| Gruber et al. | 2014 | States of Curiosity Modulate Hippocampus-Dependent Learning | *Neuron*, 84(2), 486–496 | Curiosity enhances memory |
| Gruber & Ranganath | 2019 | PACE Framework | *Trends in Cognitive Sciences*, 23(12), 1014–1025 | Prediction → Appraisal → Curiosity → Exploration |
| Metcalfe et al. | 2020 | Epistemic Curiosity and the Region of Proximal Learning | *Current Directions in Psychological Science* | Curiosity calibrated to knowledge |
| Hertwig & Engel | 2016 | Homo Ignorans: Deliberately Choosing Not to Know | *Perspectives on Psychological Science*, 11(3), 359–372 | Deliberate ignorance taxonomy |
| Undorf et al. | 2021 | Metacognitive Control: Help Seeking and Withholding | *Metacognition and Learning*, 16, 547–576 | Help-seeking ≠ simple confidence |
| Rahnev et al. | 2020 | The Confidence Database | *Nature Human Behaviour*, 4(3), 317–325 | Standardized confidence repository |

### Domain 3: LLM Metacognition (2022–2026)

| Authors | Year | Title | Venue | Key Contribution |
|---------|------|-------|-------|-----------------|
| Kadavath et al. | 2022 | Language Models (Mostly) Know What They Know | arXiv:2207.05221 | P(True), P(IK), calibration scaling |
| Xiong et al. | 2024 | Can LLMs Express Their Uncertainty? | ICLR 2024 | Confidence elicitation framework |
| Tian et al. | 2023 | Just Ask for Calibration | EMNLP 2023 | Verbalized > logit confidence |
| Lin et al. | 2022 | Teaching Models to Express Uncertainty in Words | TMLR 2022 | First verbalized uncertainty |
| Yona et al. | 2024 | Can LLMs Faithfully Express Intrinsic Uncertainty? | EMNLP 2024 | Internal-expressed uncertainty gap |
| Kuhn et al. | 2023 | Semantic Uncertainty | ICLR 2023 | Semantic entropy |
| Farquhar et al. | 2024 | Detecting Hallucinations Using Semantic Entropy | *Nature*, 630, 625–630 | Confabulation detection |
| Kossen et al. | 2024 | Semantic Entropy Probes | arXiv:2406.15927 | Hidden-state approximation |
| Wang et al. | 2023 | Self-Consistency Improves Chain of Thought | ICLR 2023 | Diversity as confidence |
| Azaria & Mitchell | 2023 | Internal State of an LLM Knows When It's Lying | Findings of EMNLP 2023 | Activation classifiers |
| Leng et al. | 2024 | Taming Overconfidence: Reward Calibration in RLHF | ICLR 2025 | RLHF → overconfidence |
| Sharma et al. | 2023 | Towards Understanding Sycophancy | ICLR 2024 | Sycophancy as metacognitive failure |
| Bani-Harouni et al. | 2025 | Rewarding Doubt | ICLR 2026 | RL for calibrated confidence |
| Zhang et al. | 2024 | R-Tuning: Instructing LLMs to Say "I Don't Know" | NAACL 2024 | Refusal as transferable meta-skill |
| Cheng et al. | 2024 | Can AI Assistants Know What They Don't Know? | ICML 2024 | Knowledge quadrants framework |
| Wen et al. | 2025 | Know Your Limits: Survey of Abstention in LLMs | TACL, 13, 529–556 | Comprehensive abstention survey |
| AbstentionBench | 2025 | AbstentionBench | arXiv:2506.09038 | 20 datasets; reasoning degrades abstention |
| Wang et al. (DMC) | 2025 | Decoupling Metacognition from Cognition | AAAI 2025, 39(24), 25353–25361 | SDT-based LLM metacognition |
| Orgad et al. | 2024 | LLMs Know More Than They Show | ICLR 2025 | Internal truthfulness encoding |
| Steyvers & Peters | 2025 | Metacognition and Uncertainty in Humans and LLMs | *Current Directions in Psychological Science* | Key bridging paper |
| Ackerman et al. | 2025 | Evidence for Limited Metacognition in LLMs | arXiv:2509.21545 | Animal-cognition paradigms for LLMs |
| Wang et al. (MP) | 2024 | Metacognitive Prompting | NAACL 2024 | Flavell's stages in prompting |
| Xu et al. | 2024 | SaySelf | EMNLP 2024 | Self-reflective rationales |
| Geng et al. | 2024 | Survey of Confidence Estimation and Calibration | NAACL 2024 | Comprehensive calibration survey |
| Gekhman et al. | 2024 | Does Fine-Tuning on New Knowledge Encourage Hallucinations? | EMNLP 2024 | SFT disrupts calibration |
| Quach et al. | 2024 | Conformal Language Modeling | ICLR 2024 | Formal prediction-set guarantees |
| Wang et al. (ConU) | 2024 | ConU: Conformal Uncertainty | EMNLP 2024 Findings | Self-consistency + conformal prediction |
| Srinivasan et al. | 2024 | Selective "Selective Prediction" (ReCoVERR) | arXiv:2402.15610 | Verification before abstention |
| Li et al. | 2025 | A Survey on the Honesty of LLMs | TMLR 2025 | Honesty = self-knowledge + self-expression |
| Singh et al. | 2025 | Dunning-Kruger Effect in LLMs | arXiv:2603.09985 | Overconfidence replicates D-K pattern |
| Steyvers et al. | 2025 | What LLMs Know and What People Think They Know | *Nature Machine Intelligence* | Calibration gap; discrimination gap |
| Campos et al. | 2024 | Conformal Prediction for NLP: A Survey | *Transactions of the ACL* | CP survey for NLP |

---

## Toward a Theoretical Framework for Testing Metacognitive Selective Verification, Clarification, and Abstention

The intellectual lineage traced above suggests a unified framework with **five core constructs** that apply symmetrically to human and artificial agents:

### Construct 1: Metacognitive Monitoring

**Definition:** The agent's capacity to discriminate its own correct from incorrect outputs.

**Human measurement:** Meta-d'/d' (Maniscalco & Lau, 2012), FOK accuracy (Hart, 1965), JOL resolution (Nelson & Dunlosky, 1991).

**LLM measurement:** AUROC for failure prediction, verbalized confidence discrimination (Xiong et al., 2024), semantic entropy (Kuhn et al., 2023). The DMC framework (Wang et al., 2025) provides a direct computational translation of Fleming and Lau's signal-detection approach.

**Testing principle:** Present the model with questions spanning a wide difficulty range. Compare expressed confidence (or internal uncertainty signals) against actual correctness using SDT-based metrics that control for first-order performance.

### Construct 2: Metacognitive Control

**Definition:** The agent's capacity to act adaptively on monitoring signals — reporting when confident, withholding when uncertain, seeking clarification when monitoring is ambiguous.

**Human measurement:** Koriat and Goldsmith's (1996) report/withhold paradigm; accuracy-quantity tradeoff curves.

**LLM measurement:** R-Tuning refusal rates (Zhang et al., 2024); knowledge-quadrants alignment (Cheng et al., 2024).

**Testing principle:** Give models the option to abstain or request clarification. Measure whether abstention rates correlate with actual error rates, and whether abstention improves output accuracy (output-bound score). The critical finding from Orgad et al. (2024) — monitoring without effective control — should be specifically tested.

### Construct 3: Calibration

**Definition:** The correspondence between expressed confidence and actual accuracy.

**Human measurement:** ECE, Brier score, calibration curves (Lichtenstein et al., 1982).

**LLM measurement:** Same metrics applied to verbalized or logit-derived confidence (Xiong et al., 2024; Tian et al., 2023).

**Testing principle:** Evaluate across difficulty levels to detect the hard-easy effect. Test whether RLHF-trained models show the predicted overconfidence inflation (Leng et al., 2024). Compare verbalized vs. internal calibration (Yona et al., 2024).

### Construct 4: Strategic Abstention

**Definition:** The decision to withhold a response when monitoring signals indicate insufficient reliability.

**Human measurement:** Goldsmith and Koriat's dual-criterion model (2007) — accuracy-quantity tradeoff curves and grain-size regulation.

**LLM measurement:** AbstentionBench (2025) provides the most comprehensive benchmark. Selective prediction metrics (coverage-accuracy tradeoffs).

**Testing principle:** Evaluate the accuracy-coverage tradeoff. A metacognitively competent model should show monotonically increasing accuracy as it withholds more answers (lowest-confidence first). Test whether abstention skill transfers across domains (R-Tuning's key finding). Critically test whether reasoning-optimized models show degraded abstention (AbstentionBench's finding).

### Construct 5: Epistemic Regulation

**Definition:** Higher-order strategies agents use to manage their own knowledge states — selective information-seeking, deliberate ignorance, help-seeking, and source evaluation.

**Human measurement:** Curiosity as metacognitive signal (Gruber & Ranganath, 2019), deliberate ignorance (Hertwig & Engel, 2016), help-seeking (Undorf et al., 2021), epistemic vigilance (Sperber et al., 2010).

**LLM measurement:** SaySelf's self-reflective rationales (Xu et al., 2024); Metacognitive Prompting (Wang et al., 2024).

**Testing principle:** Present models with scenarios where they should seek additional information rather than answer directly. Test whether models can identify *what specific knowledge they lack* (not just that they are uncertain). Evaluate whether models appropriately regulate grain size — providing vaguer answers when uncertain rather than fabricating precise ones.

### Cross-Cutting Design Principles

A robust testing framework should:

1. **Evaluate each construct independently and in interaction.** Monitoring can exist without control; good calibration can coexist with poor abstention.
2. **Use behavioral paradigms from animal cognition** (Ackerman et al., 2025) to avoid the circularity of relying on self-report from systems whose self-report we are trying to evaluate.
3. **Test transfer across domains** to distinguish genuine metacognitive capacity from task-specific calibration artifacts.
4. **Include adversarial conditions** — sycophancy-inducing prompts, leading questions, social pressure to answer — to test whether metacognitive control survives pressure, as Sharma et al. (2023) documented it typically does not.
5. **Measure the monitoring-control gap directly** by comparing internal state analysis (Orgad et al., 2024; Azaria & Mitchell, 2023) with expressed behavior (verbalized confidence, abstention rates).

---

## Conclusion

The most consequential insight from this literature synthesis is that **the monitoring-control gap — not the absence of monitoring per se — is the primary metacognitive failure mode in both humans and LLMs**. Orgad et al.'s finding that LLMs encode truthfulness internally but fail to act on it, AbstentionBench's finding that better reasoners are worse abstainers, and the Dunning-Kruger pattern's replication across species all point to the same conclusion: knowing and knowing-that-you-know are computationally distinct capacities. The Koriat-Goldsmith framework's formalization of the accuracy-quantity tradeoff provides the theoretical language, and the emerging DMC/meta-d' bridge provides the measurement infrastructure, to build principled evaluations of LLM metacognition grounded in six decades of psychological science.

The most promising research frontier lies not in making models more accurate, but in making them more *accurately uncertain* — endowing them with the metacognitive architecture that allows selective verification, clarification, and abstention to function as genuine epistemic self-regulation rather than post-hoc behavioral mimicry.

---

*Report compiled March 2026. See accompanying `references.bib` for all BibTeX entries.*
