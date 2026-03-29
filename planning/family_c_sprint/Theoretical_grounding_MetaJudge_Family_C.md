# Theoretical grounding for MetaJudge Family C (Self-Correction)

**MetaJudge Family C can be grounded in a robust theoretical and empirical foundation, but three design parameters require recalibration before release.** The most consequential finding in this memo is that the current damage:gain scoring ratio of 0.05 penalty versus 0.90 reward is inverted relative to its stated intent — it incentivizes reckless revision rather than conservative correction, and must be restructured around the prospect-theoretic anchor of λ ≈ 2. Beyond scoring, the literature since Huang et al. (ICLR 2024) has not overturned the core finding that intrinsic self-correction largely fails for reasoning, but Tyen et al. (2024) reframe the problem: the bottleneck is error *detection*, not error *repair*, which means C1 should be understood primarily as a monitoring probe rather than a control benchmark. Third, the "unresolved" outcome has strong theoretical backing in Nelson & Narens' FOK construct, but the 0.15 confidence-drop threshold is defensible only under optimistic reliability assumptions and should be empirically calibrated before hardcoding.

This memo addresses all seven research questions governing Family C's design. Three questions (Q1, Q5, Q6) are flagged for significant remaining uncertainty with specific follow-up recommendations.

---

## 1. Executive summary

**Q1 — Intrinsic self-correction signal:** Post-Huang literature (Kamoi et al. 2024; Tyen et al. 2024; Kumar et al. 2025) confirms intrinsic self-correction produces near-zero accuracy improvement for off-the-shelf models. However, *calibration revision* (confidence adjustment quality from Turn 1 to Turn 2) shows measurably more variance and should become C1's primary signal. C1 is defensible as a frontier probe with a discrimination floor of D ≥ 0.20.

**Q2 — Optimal number of turns:** Two turns capture the large majority of diagnostic signal. Self-Refine (Madaan et al. 2023) and probabilistic scaling theory (Yang et al. 2025) both show diminishing returns beyond iteration 2. Iatrogenic risks — sycophantic capitulation, confidence erosion, overthinking — increase meaningfully at Turn 3. Recommendation: include **5–7 three-turn items** (15–20% of the seed set) as targeted diagnostic probes for flip-back behavior and confidence erosion, not as standard protocol.

**Q3 — Item overlap:** The planned ~43% overlap exceeds the standard psychometric recommendation of 20–30% for anchor tests (Kolen & Brennan 2004). The strongest argument for overlap is enabling direct monitoring→control link testing across families. The strongest argument against is inflated inter-family correlations and reduced content coverage. Recommendation: reduce to ~25% designated linking items.

**Q4 — Same-budget fairness:** Kamoi et al. (2024) establish that compute-equivalent baselines are essential for credible self-correction evaluation. A **re-answering baseline** (same question, no review prompt) is critical for isolating whether C1's review prompt adds value beyond a second generation attempt. Comparison between C1 and C2 should use gain-over-own-baseline, never raw scores.

**Q5 — Damage rate asymmetry:** The current scoring structure (damage penalty 0.05, correction reward 0.90) creates an **18:1 reward-to-penalty ratio that incentivizes reckless revision** — the opposite of the stated intent. Prospect theory's meta-analytic loss aversion coefficient λ ≈ 1.96 (Brown et al. 2024) provides the empirical anchor. Recommendation: restructure to **2:1 or 3:1 damage-to-gain ratio** (penalty = 2–3× reward), and report results as sensitivity across ratios.

**Q6 — The "unresolved" outcome:** Nelson & Narens' (1990) Feeling of Knowing (FOK) construct provides direct theoretical grounding: "unresolved" maps to low FOK triggering search termination. The 0.15 confidence-drop threshold is defensible only if LLM confidence has test-retest reliability r ≥ 0.95 (Jacobson & Truax 1991 RCI). Recommendation: use 0.15 as a lower bound, empirically calibrate via test-retest, and consider a tiered threshold.

**Q7 — Benchmark positioning:** Ten existing benchmarks touch self-correction (Self-Refine, Reflexion, SelfCheckGPT, CorrectBench, Self-Correction Bench, etc.), but none combines metacognitive framing, behavioral scoring, asymmetric damage penalties, the C1/C2 split, and integration with calibration and abstention measures. MetaJudge Family C should be positioned as a *measurement instrument for correction decision quality*, not a technique for improving task performance.

---

## 2. Detailed findings

### Q1: Whether intrinsic self-correction produces usable signal

The weight of evidence since Huang et al. (2024) has not overturned the core negative result — it has refined it. **Kamoi et al. (TACL 2024)** conducted the most comprehensive survey, concluding that "no prior work demonstrates successful intrinsic self-correction with feedback from prompted LLMs" except for tasks "exceptionally suited for self-correction" such as safety filtering and format compliance. This finding is reinforced by **Zhang et al. (ACL 2025)**, who showed that review prompts like "Are you sure?" trigger internal dynamics indistinguishable from "You are wrong," inducing sycophantic flipping rather than genuine error detection.

The critical reframing comes from **Tyen et al. (ACL Findings 2024)**: the bottleneck is error *detection*, not error *repair*. When given oracle error locations, models correct effectively; their best model achieved only ~52.9% accuracy at independently locating errors. This means a generic review prompt fails not because the model cannot fix mistakes but because **it cannot find them**. For C1 design, this implies that accuracy-correction gain will show near-floor effects, but confidence-adjustment behavior may show meaningful variance — a model might appropriately lower confidence on items it got wrong without being able to produce the correct answer.

Positive results exist but under conditions outside C1's scope. **Kumar et al. (ICLR 2025 Oral, SCoRe)** achieved +15.6% on MATH via multi-turn RL training specifically for self-correction, but this requires purpose-built training, not off-the-shelf prompting. **Liu et al. (2024)** found intrinsic self-correction works with zero temperature and "fair" (unbiased) prompts, but their definition of "works" still shows modest gains relative to compute cost. **Bohnet et al. (Dec 2025)** demonstrated intrinsic self-critique improvements on planning tasks via many-shot prompting. None of these translate to generic C1 conditions.

Regarding **error types**, the literature suggests a clear hierarchy. Format/structural errors, simple arithmetic rechecking, and factual claims contradicting strong model knowledge are most amenable to intrinsic detection. Deep reasoning errors, trick questions, and overconfident systematic misconceptions are least amenable. The MetaJudge v0.5.5.1 data confirms this: compound interest (0% accuracy, 0.97 confidence) and bookworm problems (0% accuracy, 0.92 confidence) represent systematic blind spots that no generic review prompt will crack.

For the **Turn 2 review prompt**, the literature converges on a key insight: prompts implying the answer is wrong bias the model toward unnecessary changes. A neutral, permissive prompt — "You may review and optionally revise your answer and confidence. If your answer is already correct, you may confirm it without changes" — minimizes sycophantic flipping while preserving genuine correction signal. Process-oriented prompts ("check step by step") show marginal arithmetic benefits but do not overcome the detection bottleneck. **Metacognitive prompts** ("rate your confidence, then decide whether to revise") may be most valuable for C1 because they foreground the monitoring signal that shows the most variance.

The **minimum discrimination threshold** should follow classical test theory standards: item discrimination D ≥ 0.20 (Ebel & Frisbie 1991), point-biserial r_pbis ≥ 0.15. If C1's accuracy-correction component fails these thresholds across the model panel, it should be retained for calibration-revision measurement but reported with a floor-effect annotation. The recommended framing is as a **frontier metacognitive probe** — analogous to SuperGLUE including tasks at human-level difficulty where early models performed near chance.

*Confidence level: Moderate. The direction is clear (C1 accuracy correction will be minimal), but whether calibration revision alone carries enough variance to justify C1's inclusion requires empirical verification.* **⚑ Uncertainty flag — see Section 4.**

### Q2: Two turns capture most signal, but targeted three-turn probes add diagnostic value

Nelson & Narens (1990) describe metacognitive monitoring as implicitly iterative: Judgments of Learning occur repeatedly until a "norm of study" threshold is reached, and Feeling of Knowing judgments gate further memory search. However, the framework models a single monitoring→control cycle per retrieval episode, not explicit multi-pass review. **Zimmerman's (2000) cyclical self-regulated learning model** is explicitly iterative — forethought, performance, self-reflection phases feed forward recursively — but describes learning over extended periods, not rapid sequential judgments.

The **delayed-JOL effect** (Nelson & Dunlosky 1991; meta-analytic g = 0.93, Rhodes & Tauber 2011) directly supports the two-turn design: Turn 2 functions as a delayed judgment that accesses the item from a different cognitive state, dramatically improving metacognitive accuracy. A third turn would provide a further-delayed judgment, but with diminishing marginal returns.

Empirical evidence from LLM research confirms diminishing returns. **Self-Refine (Madaan et al. 2023)** showed that "the largest gains occur in the first 1–2 refinement rounds; later iterations yield smaller but occasionally non-trivial gains." **Yang et al. (EMNLP 2025)** provided a mathematical framework showing a maximum accuracy ceiling determined by the model's correct-preserving rate (CL) and error-fixing rate (CS), typically reached by round 3–5 with most gains captured at round 2.

The **iatrogenic risks** of a third turn are substantial. A preprint from Google DeepMind and UCL found LLMs update confidence **2.5× more strongly than warranted** when receiving criticism, creating steep confidence drops and position flips. **PARROT (Çelebi et al. 2025)** taxonomized eight behavioral states under sustained pressure, including "sycophantic compliance" and "confidence erosion." **SYCON Bench (Hong et al. 2025)** introduced "Turn of Flip" (ToF) metrics quantifying how many turns before a model capitulates — reasoning-optimized models (DeepSeek-R1, o3-mini) showed higher resistance than instruction-tuned counterparts.

**Recommendation for the 35-item seed set:** Include **5–7 three-turn items** (15–20%), strategically selected for three purposes: (1) flip-back detection — items where the model is correct in Turn 1, challenged in Turn 2, then given neutral re-evaluation in Turn 3; (2) confidence erosion probes — correct, confident answers subjected to sustained questioning; (3) genuine uncertainty escalation — ambiguous items where convergence toward "unresolved" over multiple turns indicates appropriate metacognitive behavior. Avoid three turns for clear factual or mathematical items where the signal is captured at Turn 2.

*Confidence level: High. The two-turn default is well-supported; the 15–20% three-turn allocation balances diagnostic value against iatrogenic risk.*

### Q3: Overlap should decrease to ~25% for psychometric defensibility

The plan to overlap ~43% of Family C items with the A/B pool sits well above the standard psychometric recommendation. **Kolen & Brennan (2004/2014)** recommend at least 20% overlap for anchor-based test equating. **Angoff (1984)** sets a floor of 20 items or 20% of test length. **Cook & Eignor (1991)** concur at 20%. No standard reference recommends above 30%.

The **strongest argument for overlap** is that it enables direct testing of the Nelson & Narens monitoring→control link: the same item, assessed for confidence calibration in Family A and for correction behavior in Family C, provides the cleanest possible test of whether knowing you're wrong predicts fixing the error. This is MetaJudge's core theoretical contribution and requires item-level linking.

The **strongest argument against** comes from **Wang, Cheng & Wilson (2005)**, who showed that items sharing common stimuli across scales violate local item independence assumptions, requiring specialized IRT models to analyze properly. Shared items inflate inter-family correlations through method variance, potentially creating illusory monitoring→control relationships. Additionally, 43% overlap means fewer unique items per family, reducing content validity.

LLM statelessness via `chats.new()` isolation eliminates *classical* practice effects (item-level familiarity, fatigue), which is a genuine advantage over human testing. However, **systematic content confounds** persist: a model's weight-level knowledge about a topic is fixed, meaning item difficulty is correlated across families regardless of session isolation. This is both a feature (enabling monitoring→control analysis) and a confound (inflating correlations).

**Recommendation:** Reduce overlap to **~25%** (approximately 8–9 items in a 35-item seed set). Designate these explicitly as "linking items" for cross-family equating and monitoring→control analysis. Report both shared-item and unique-item inter-family correlations separately, so that the inflation effect from overlap is transparent. If IRT analysis is pursued, model the overlap as a testlet effect using methods from Bradlow et al. (1999).

*Confidence level: High. The psychometric literature is clear; 43% is excessive for any standard purpose, and 25% satisfies the theoretical need.*

### Q4: Three baselines make C1-versus-C2 comparison defensible

**Kamoi et al. (TACL 2024)** provide the definitive framework: self-correction claims require compute-equivalent baselines. Many published positive results used "unfair" designs where the initial response was deliberately handicapped (e.g., weaker initial prompts) or the correction phase received resources (tools, knowledge) unavailable at generation. Their fairness taxonomy categorizes corrections as realistic/unrealistic and fair/unfair — C1 is fair (same model, same resources at both turns) while C2 is "fair-asymmetric" (correction receives additional evidence).

The **re-answering baseline** is essential for C1. Huang et al. (2024) demonstrated that multi-agent debate performs no better than self-consistency (Wang et al. 2023) with the same number of responses. **Self-consistency** — sampling multiple answers and taking a majority vote — achieved +17.9% on GSM8K through stochasticity alone, without any review process. If C1 cannot outperform a simple re-answering baseline (same question, fresh generation, no review prompt), the review prompt adds no value beyond giving the model another roll of the dice.

For comparing C1 and C2, **gain-over-own-baseline** is the fairest first-release metric. Each sub-family is normalized against its own no-review control: C1_gain = C1_score − re-ask_score; C2_gain = C2_score − evidence-without-review_score. This is standard "value-added" methodology from educational measurement and directly measures how much the correction process contributes beyond baseline conditions.

C2's evidence advantage can be further **calibrated through scaffolding levels**, following Wood, Bruner & Ross (1976). A graduated scale — C2-weak (vague hint: "Are you sure about that?"), C2-moderate (suggestive contradiction: "Some sources disagree"), C2-strong (specific evidence with source attribution), and C2-misleading (deliberately incorrect hint) — creates a dose-response curve revealing how much evidence a model needs before it can correct errors. The C2-misleading condition doubles as a sycophancy/robustness test.

**Recommended baselines for first release:**

- **B0 (single-shot):** Turn 1 answer only, no revision opportunity — establishes raw accuracy baseline.
- **B1-reask (re-answering):** Same question asked fresh without review prompt or Turn 1 context — isolates stochasticity contribution.
- **B-maintain (always-maintain):** Model always keeps Turn 1 answer — the null strategy baseline against which any revision behavior is compared.
- **Compute budget reporting:** State tokens consumed per condition, following the controlled-budget principle from Self-Correction Blind Spot (Tsui 2025).

*Confidence level: High. The literature is unambiguous that compute-equivalent baselines are required, and gain-over-baseline is standard methodology.*

### Q5: The current scoring ratio is inverted and must be restructured

This is the most consequential design finding in this memo. The current scoring assigns **damage (correct→wrong) a penalty of 0.05 and correction (wrong→correct) a reward of 0.90**, creating an 18:1 reward-to-penalty ratio. This means a model can damage 18 correct answers for every successful correction and still break even. Far from creating the intended conservative bias against careless revision, **this ratio incentivizes aggressive, indiscriminate revision** because each correction compensates for enormous numbers of damages.

The intended asymmetry — that breaking a correct answer should be penalized more heavily than failing to fix an error — requires the ratio to run in the opposite direction: **damage penalty > correction reward**.

**Prospect theory** provides the empirical anchor. Tversky & Kahneman (1992) originally estimated loss aversion λ = 2.25. **Brown et al.'s 2024 meta-analysis** across many studies refined this to λ = **1.955** (95% CI: 1.824–2.104). The robust consensus is that losses are weighted approximately **twice** as heavily as equivalent gains. Translating to MetaJudge: if correction gain = G, damage penalty should be approximately 2G.

No existing self-correction benchmark uses explicit asymmetric damage:gain scoring — **this is novel to MetaJudge** and a genuine contribution if calibrated correctly. Huang et al. (2024) and CorrectBench (2025) track correct→wrong and wrong→correct transitions separately but do not weight them asymmetrically. SCoRe's (Kumar et al. 2025) reward shaping is the closest precedent: they penalize second-attempt responses that degrade relative to first attempts, but without formalized ratios.

**Differential asymmetry between C1 and C2** is warranted. C1 damage — the model broke its own correct answer with no external provocation — represents a more fundamental failure of self-evaluation. C2 damage — the model was led astray by suggestive evidence — is partially expected; some sensitivity to evidence is desirable. Recommended structure: **C1 damage-to-gain ratio of 3:1** (unprompted damage severely penalized), **C2 damage-to-gain ratio of 2:1** (evidence-prompted damage penalized but more understandable), **C2-misleading: 3:1** (following incorrect evidence uncritically is as concerning as unprompted damage).

To prevent degenerate strategies: at a 2:1 ratio, a model must correct errors at least twice as often as it damages correct answers for revision to be net positive — a reasonable bar that rewards selective, accurate revision while penalizing indiscriminate behavior. A "never-revise" strategy scores exactly 0 on the behavioral component; its viability depends on base accuracy, but it should never dominate a model with even moderately successful correction behavior.

**Recommendation:** Restructure scoring so that correction gain = 0.30 and damage penalty = 0.60 (2:1) or 0.90 (3:1). **Report results as sensitivity across three ratios** (2:1, 3:1, 5:1) so readers can assess whether model rankings are stable or ratio-dependent. Always report raw transition matrices (correct→correct, correct→wrong, wrong→correct, wrong→wrong) alongside composite scores.

*Confidence level: Moderate-to-High on direction (the current ratio is clearly inverted), Moderate on the exact ratio (prospect theory provides a strong anchor at ~2:1 but the translation to benchmark scoring is imprecise).* **⚑ Uncertainty flag — see Section 4.**

### Q6: "Unresolved" has strong theoretical backing but needs empirical threshold calibration

The "unresolved" outcome — detecting uncertainty without committing to a revised answer — maps directly to **Feeling of Knowing (FOK)** in Nelson & Narens' (1990) metamemory framework. FOK is a prospective monitoring judgment made after failed recall: the person predicts whether they could eventually recognize the correct answer. When FOK is low, the control decision is to **terminate search** — this is functionally equivalent to "unresolved." Nelson & Narens describe three control actions: initiate, continue, and terminate. "Unresolved" represents termination informed by monitoring, the most metacognitively sophisticated response to recognized uncertainty.

The construct also connects to **Tip-of-the-Tongue (TOT) states** — the strong sense that an answer is accessible but currently unretrievable. TOT experiences enhance metacognitive sensitivity of subsequent judgments (Journal of Cognition, 2024). And in **Zimmerman's (2000) self-regulated learning model**, the self-reflection phase includes "defensive reactions" (withdrawing, avoiding) alongside adaptive reactions — another precedent for appropriate disengagement.

The current heuristic — **confidence drop ≥ 0.15 without revised answer** — requires scrutiny through the **Reliable Change Index** (Jacobson & Truax 1991). The RCI formula shows that for a change to exceed measurement error at p < .05, the drop must exceed 1.96 × SE_diff, where SE_diff = SD × √(2(1 − r)). With typical confidence SD ≈ 0.25 and test-retest reliability r ≈ 0.90, the threshold would be **0.22** — above 0.15. Only at r ≥ 0.95 does the RCI threshold approach 0.155. Since LLM confidence scores vary substantially across runs (temperature effects, sampling stochasticity, tendency to cluster at multiples of 5 per Xiong et al. 2024), reliability may well fall below 0.95.

**Normatively "unresolved" items** — where the correct response is genuine uncertainty — should constitute **10–15% of the seed set** (3–5 items). These include items with genuinely ambiguous answers, items requiring external information the model shouldn't confabulate, and boundary/edge cases where reasonable experts disagree. Models that report "unresolved" on these items demonstrate superior metacognitive calibration; models that commit to a definitive answer reveal overconfidence.

Scoring "unresolved" requires distinguishing **appropriate unresolved** (genuine metacognitive monitoring with specific identification of uncertainty, articulation of competing considerations, acknowledgment of what additional information would help) from **lazy unresolved** (generic hedging without engagement). The recommended scoring structure: appropriate unresolved on normatively ambiguous items receives full credit (1.0); appropriate unresolved on answerable items receives partial credit (0.3–0.5) — good monitoring but failed control; lazy unresolved receives minimal credit (0.1–0.2); and abandoning a correct Turn 1 answer receives zero (iatrogenic effect). Distinguishing these categories requires assessing Turn 2 reasoning quality, which can use a rubric evaluating specificity, engagement depth, and information gain.

*Confidence level: High on theoretical grounding, Moderate on the specific threshold.* **⚑ Uncertainty flag — see Section 4.**

### Q7: Family C occupies a distinct and defensible niche

Ten existing benchmarks touch LLM self-correction. **Self-Refine** (Madaan et al. 2023) and **Reflexion** (Shinn et al. 2023) measure iterative task performance improvement using single-model feedback loops or episodic memory — neither tracks metacognitive process. **SelfCheckGPT** (Manakul et al. 2023) detects hallucinations via sampling consistency — a monitoring tool, not a correction benchmark. **Self-Consistency** (Wang et al. 2023) improves generation via ensemble, with no metacognitive judgment. **REFINER** (Paul et al. 2024) uses a trained external critic — closer to C2 but without self-evaluation. **CorrectBench** (Tie et al. 2025) is the closest competitor, systematically comparing intrinsic, external, and fine-tuned correction paradigms across reasoning tasks, but it measures only whether task accuracy improves, not whether the correction *decision* was appropriate.

**Self-Correction Bench** (Tsui 2025) is perhaps the most conceptually aligned: it discovers a "Self-Correction Blind Spot" where models correct externally-presented errors but fail on their own mistakes (64.5% average blind spot rate), and finds that simply appending "Wait" reduces the blind spot by 89.3%. However, it uses controlled error injection rather than naturalistic errors and does not integrate with a broader metacognitive framework.

MetaJudge Family C's **unique contribution** lies in the intersection of five features no other benchmark combines: (1) explicit grounding in Nelson & Narens' monitoring→control metacognitive theory; (2) behavioral-only scoring that evaluates the quality of the correction *decision*, not just whether accuracy improved; (3) asymmetric damage penalties capturing the real-world harm of making things worse; (4) the C1/C2 split systematically comparing intrinsic versus evidence-assisted correction within a unified framework; (5) integration with Families A (calibration) and B (abstention) to enable full metacognitive loop testing.

From existing benchmarks, MetaJudge should **adopt** CorrectBench's three-paradigm taxonomy and Self-Correction Bench's error-injection methodology for validation studies. It should **reject** Self-Refine's scalar stopping criteria (too coarse), Self-Consistency's majority voting (measures output reliability, not metacognition), and Reflexion's memory persistence (incompatible with session-isolation design).

Claims to **avoid**: implying self-correction measures "reasoning ability" (it measures correction behavior); conflating intrinsic and evidence-assisted correction (maintain the C1/C2 separation rigorously); and ignoring the damage problem that plagues Self-Refine's reporting of average improvements.

**Positioning statement:** "MetaJudge Family C is the first benchmark to measure LLM self-correction as a metacognitive control process, scoring the quality of correction decisions — not just whether task performance improves — within an integrated framework linking confidence monitoring (Family A), selective abstention (Family B), and error repair (Family C)."

*Confidence level: High. The landscape is well-mapped and MetaJudge's distinctive niche is clear.*

---

## 3. Integrated recommendations

The seven questions yield a coherent set of implementable design decisions:

**Scoring architecture.** Restructure the damage:gain ratio from the current 0.05/0.90 to a damage-dominant configuration anchored at **2:1 to 3:1** (e.g., correction gain = 0.30, damage penalty = 0.60–0.90). Apply differential ratios: 3:1 for C1 and C2-misleading, 2:1 for standard C2. Always report raw transition matrices alongside composite scores, and publish results at 2:1, 3:1, and 5:1 as sensitivity analysis.

**Turn protocol.** Retain two turns as the standard protocol. Add **5–7 three-turn items** (15–20% of seed set) as targeted probes: 2–3 flip-back detection items, 2–3 confidence erosion probes, and 1–2 genuine uncertainty escalation items. Three-turn items should be flagged separately in scoring and not pooled with two-turn items for composite calculation.

**Item composition.** Reduce overlap with Families A/B from ~43% to **~25%** (8–9 designated linking items). Include **3–5 normatively "unresolved" items** (genuinely ambiguous, requiring "I don't know" as the correct metacognitive response). Ensure C1 items span the error-type hierarchy: include format/arithmetic errors (more catchable), reasoning errors (less catchable), and systematic blind-spot items (resistant to correction) to maximize variance.

**Baselines.** Implement three baselines: B0 (single-shot), B1-reask (re-answering without review), and B-maintain (always keep Turn 1 answer). Compare C1 against B1-reask to isolate review-prompt contribution. Compare C2 against B-maintain. Report C1 and C2 gains separately, never combined.

**Turn 2 prompt.** Use a neutral, non-biasing prompt: "You may review and optionally revise your answer and confidence. If your answer is already correct, you may confirm it without changes." This minimizes sycophantic flipping (per Zhang et al. 2025 and Liu et al. 2024's "fair prompt" requirement). For C2, follow with evidence of varying strength levels.

**"Unresolved" operationalization.** Use confidence drop ≥ 0.15 as a lower-bound heuristic, with empirical calibration via test-retest to compute the actual RCI for each model in the panel. Apply a tiered system: 0.15–0.24 = "possible unresolved" (flag for review), ≥ 0.25 = "definite unresolved." Score appropriate unresolved at 0.3–0.5 on answerable items, 1.0 on normatively ambiguous items, and 0.0 for abandoning correct Turn 1 answers.

**C1 framing.** Present C1 as a "frontier metacognitive probe" measuring two signals: (a) calibration revision quality (primary — expected to show meaningful variance), and (b) accuracy correction rate (secondary — expected to show floor effects, reported as such). Frame near-zero accuracy correction as a scientifically meaningful finding confirming the monitoring-control dissociation in current LLMs, and as a temporal baseline for tracking future model generations trained with self-correction capabilities (e.g., SCoRe-style RL).

---

## 4. Uncertainty flags

### ⚑ Q1: Whether C1 produces sufficient signal for inclusion

**What remains uncertain.** The literature is clear that accuracy-correction gain will be minimal, but it is unknown whether *calibration revision quality* — C1's proposed primary signal — will show enough inter-model variance to meet the D ≥ 0.20 discrimination threshold. No published study has measured calibration revision variance across a multi-model panel under neutral review prompts. It is also unclear which Turn 2 prompt formulation maximizes genuine (versus sycophantic) calibration adjustment.

**Recommended follow-up agent deployment.** Deploy two agents: (1) an **empirical pilot agent** that designs and describes the protocol for a small-scale (10-item, 3-model) empirical test of C1 calibration revision variance under three prompt variants (neutral, process-oriented, metacognitive), including power analysis for detecting D ≥ 0.20; (2) a **literature deepening agent** searching specifically for papers measuring confidence-change variance across LLMs in multi-turn settings, with search queries: "LLM confidence revision multi-turn," "calibration change self-correction," "confidence update two-turn LLM," and fetching any 2025–2026 papers from COLM, NeurIPS, or ICML proceedings on metacognitive benchmarking.

**Suggested prompting strategy.** For the empirical pilot agent: "Design a minimal viable experiment to test whether intrinsic self-correction (C1) produces inter-model variance ≥ D = 0.20 on calibration revision quality. Use 10 items spanning three error types (arithmetic, reasoning, factual), three prompt variants (neutral: 'You may review…'; process-oriented: 'Check step by step…'; metacognitive: 'Rate your confidence on each component, then decide…'), and three models from the existing panel. Specify exact prompts, measurement protocol, power analysis, and decision criteria for whether C1 is worth including." For the literature agent: "Search ACL Anthology, Semantic Scholar, and arXiv for papers published 2024–2026 measuring LLM confidence or calibration changes across multiple turns or review cycles. Prioritize empirical studies reporting inter-model variance statistics."

### ⚑ Q5: The exact damage-to-gain ratio

**What remains uncertain.** The direction is unambiguous (damage penalty must exceed correction reward), and prospect theory provides an anchor at λ ≈ 2. However, translating a psychological loss-aversion coefficient to a benchmark scoring ratio involves several unjustified assumptions: prospect theory describes human preferences over monetary gambles, not AI system evaluation; the "loss" in benchmark scoring is not experienced by the model; and the appropriate ratio may depend on downstream deployment context (medical applications warrant higher damage penalties than creative writing). Additionally, whether model rankings are robust across ratios in the 2:1–5:1 range is unknown — if rankings shift substantially, the choice of ratio becomes determinative rather than merely calibrative.

**Recommended follow-up agent deployment.** Deploy a **simulation agent** that constructs a Monte Carlo analysis: given the existing v0.5.5.1 transition matrices (or plausible synthetic ones based on literature base rates), simulate composite scores under damage:gain ratios of 1.5:1, 2:1, 3:1, 5:1, and 10:1 to determine (a) whether "never revise" becomes dominant at any ratio, (b) whether model rankings are stable across ratios, and (c) the minimum ratio at which "always revise" ceases to be optimal. Also deploy a **decision-theory agent** searching for precedents where asymmetric loss functions have been calibrated for evaluation (not training) contexts — search queries: "asymmetric scoring rule evaluation," "proper scoring rule damage penalty," "calibrated loss function benchmark design."

**Suggested prompting strategy.** For the simulation agent: "Using the following assumptions — 5 models with base accuracies [0.718, 0.762, 0.785, 0.831, 0.872], plausible self-correction rates from Huang et al. 2024 (models change ~15–25% of answers, with damage rate ≈ correction rate for intrinsic correction) — simulate composite MetaJudge C1 scores under damage:gain ratios of [1.5:1, 2:1, 3:1, 5:1, 10:1]. For each ratio, report: (1) whether 'never revise' dominates, (2) Spearman rank correlation of model ordering across ratios, (3) the ratio at which selective revision first dominates both 'never revise' and 'always revise.' Output a decision table." For the decision-theory agent: "Find literature on calibrating asymmetric loss functions for evaluation benchmarks (not training objectives). Focus on proper scoring rules with directional penalties, medical decision analysis harm-benefit ratios, and any AI evaluation frameworks that formalize damage asymmetry."

### ⚑ Q6: The 0.15 "unresolved" confidence-drop threshold

**What remains uncertain.** The threshold's defensibility hinges on LLM confidence test-retest reliability, which has not been systematically measured for the models in the MetaJudge panel. If reliability is r = 0.90 (reasonable estimate), the RCI threshold rises to 0.22, meaning 0.15 would flag noise as signal — producing false-positive "unresolved" classifications. Furthermore, the operationalization combines a continuous measure (confidence drop magnitude) with a categorical one (whether the answer was revised), and the interaction between these is not theoretically grounded. The distinction between "appropriate unresolved" and "lazy unresolved" requires assessing Turn 2 reasoning quality, which introduces a subjective scoring component that may undermine the benchmark's behavioral-only principle.

**Recommended follow-up agent deployment.** Deploy a **test-retest agent** that designs a protocol for empirically measuring LLM confidence reliability: run the same items 10 times per model at fixed temperature, compute ICC(2,1) and Pearson r for confidence scores, then derive the model-specific RCI threshold. Also deploy a **classification-boundary agent** searching for methods to operationalize "genuine" versus "lazy" uncertainty detection in LLMs without subjective narrative scoring — search for automated rubrics, linguistic markers of analytical depth, and information-theoretic measures of reasoning quality.

**Suggested prompting strategy.** For the test-retest agent: "Design a protocol to measure test-retest reliability of LLM confidence scores for the MetaJudge panel (Gemini 2.5 Flash, Gemini 2.5 Pro, Claude Sonnet 4, Claude Haiku 4.5, DeepSeek v3.1). Specify: number of repetitions per item (recommend ≥10), temperature settings (0.0, 0.3, 0.7), items to test (recommend 20 from the existing pool spanning difficulty levels), exact API parameters, and the statistical analysis plan (ICC, Pearson r, RCI derivation). Estimate the time and API cost." For the classification-boundary agent: "Search for methods to automatically distinguish genuine analytical uncertainty from lazy hedging in LLM outputs. Look for: linguistic markers of epistemic vs. performative uncertainty (Betz et al. 2024, Zhou et al. 2024), automated essay scoring rubrics applicable to reasoning depth, information-theoretic measures of content novelty in Turn 2 vs. Turn 1, and any benchmark that operationalizes metacognitive quality without human judgment."

---

## 5. Confidence assessment

| Question | Confidence | Basis |
|----------|-----------|-------|
| Q1: C1 signal | **Moderate** | Direction clear (low accuracy signal, possible calibration signal), but empirical verification needed for calibration variance |
| Q2: Optimal turns | **High** | Strong convergence across metacognition theory, empirical LLM data, and information-theoretic analysis |
| Q3: Item overlap | **High** | Psychometric standards are well-established and unambiguous on the 20–30% range |
| Q4: Same-budget fairness | **High** | Kamoi et al. 2024 and Huang et al. 2024 provide clear methodological standards |
| Q5: Damage ratio | **Moderate-High** | Direction certain (current ratio inverted), but exact calibration requires simulation |
| Q6: "Unresolved" | **Moderate** | Theoretical grounding strong, operational threshold requires empirical calibration |
| Q7: Benchmark positioning | **High** | Landscape well-mapped; MetaJudge's niche is clearly distinct |

The three flagged questions (Q1, Q5, Q6) share a common pattern: the *qualitative* design decision is well-supported by literature, but the *quantitative* parameter (discrimination threshold, scoring ratio, confidence threshold) requires empirical calibration that cannot be resolved through literature review alone.

---

## 6. Key citations

**Foundational metacognition:**
Nelson & Narens (1990) — metamemory framework (monitoring + control); Flavell (1979) — metacognition definition; Nelson & Dunlosky (1991) — delayed-JOL effect; Zimmerman (2000) — cyclical self-regulated learning model; Hart (1965) — Feeling of Knowing; Rhodes & Tauber (2011) — delayed-JOL meta-analysis (g = 0.93).

**LLM self-correction (core):**
Huang et al. (ICLR 2024) — intrinsic self-correction fails; Kamoi et al. (TACL 2024) — critical survey, fairness taxonomy; Tyen et al. (ACL Findings 2024) — detection bottleneck, not correction; Kumar et al. (ICLR 2025, SCoRe) — RL-based self-correction; Liu et al. (2024) — fair prompts + zero temp enable some correction; Zhang et al. (ACL 2025) — dark side of self-correction, sycophantic dynamics; Wu et al. (EMNLP 2024, ProCo) — key condition verification.

**LLM calibration and confidence:**
Kadavath et al. (Anthropic 2022) — models mostly know what they know; Xiong et al. (ICLR 2024) — systematic overconfidence in verbalized confidence; Sharma et al. (2023) — sycophancy as RLHF artifact.

**Iterative refinement and debate:**
Madaan et al. (NeurIPS 2023, Self-Refine) — diminishing returns after round 1–2; Shinn et al. (NeurIPS 2023, Reflexion) — verbal reinforcement learning; Du et al. (ICML 2024) — multiagent debate; Yang et al. (EMNLP 2025) — probabilistic inference scaling theory for self-correction; Jiang et al. (2025, PAG) — multi-turn RL with selective revision.

**Sycophancy and adversarial dynamics:**
Çelebi et al. (2025, PARROT) — eight behavioral states; Hong et al. (2025, SYCON Bench) — Turn of Flip metrics; Google DeepMind/UCL (2025) — 2.5× overweighting of criticism; Bohnet et al. (Dec 2025) — intrinsic self-critique for planning.

**Benchmarks:**
Tie et al. (NeurIPS 2025, CorrectBench) — systematic self-correction benchmark; Tsui (2025, Self-Correction Bench) — blind spot phenomenon; Manakul et al. (EMNLP 2023, SelfCheckGPT) — consistency-based hallucination detection; Wang et al. (ICLR 2023) — self-consistency; Paul et al. (EACL 2024, REFINER) — trained critic framework; Gou et al. (2023, CRITIC) — tool-interactive critiquing.

**Decision theory and psychometrics:**
Kahneman & Tversky (1979) — prospect theory; Tversky & Kahneman (1992) — λ = 2.25; Brown et al. (2024) — meta-analytic λ = 1.955; Jacobson & Truax (1991) — Reliable Change Index; Kolen & Brennan (2004/2014) — test equating; Angoff (1984) — anchor item standards; Wang, Cheng & Wilson (2005) — local item dependence across tests; Ebel & Frisbie (1991) — item discrimination thresholds; Wood, Bruner & Ross (1976) — scaffolding framework.