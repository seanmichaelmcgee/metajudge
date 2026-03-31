# Deep Research Prompt: Family C Self-Correction — Annotated Bibliography and Theoretical Grounding

**Purpose:** Produce a foundational literature review for MetaJudge Family C (Self-Correction) comparable in scope, academic register, and narrative depth to the existing Family B grounding documents.

**Output format:** A single document: an annotated bibliography with narrative synthesis, structured as a review article that traces the intellectual lineage of self-correction as a metacognitive construct from its psychological origins through to the 2024–2026 LLM evaluation frontier. This document will serve as the theoretical foundation for all subsequent Family C design, scoring, and positioning decisions.

**What this document must be (and must not be):**
- It must read as an **independent intellectual argument** for why self-correction is a distinct metacognitive construct worth measuring, not as answers to pre-specified engineering questions.
- It must trace a **narrative arc** — a lineage of ideas, not a list of papers.
- It must bridge **foundational psychology**, **modern cognitive science**, and **LLM self-correction research** with explicit connection points between domains.
- It must be the kind of document a benchmark reviewer could read and conclude: "this benchmark is grounded in the right science."
- It must **not** be a design memo, a sprint plan, or an engineering specification. Those outputs come later, standing on this document.

---

## CONTEXT: The MetaJudge Ecosystem

MetaJudge-AGI is a Kaggle benchmark measuring epistemically robust metacognitive behavior in LLMs, organized around Nelson & Narens' (1990) two-axis framework: monitoring and control.

**Family A (Confidence Calibration)** measures monitoring: does the model know when it's likely correct or incorrect? 117 items, Brier scoring, 5-model panel evaluated.

**Family B (Selective Abstention/Verification)** measures the monitoring-to-control transition: given uncertainty, does the model choose the right epistemic action? 84 items, utility-matrix scoring.

**Family C (Self-Correction)** measures cognitive control: can the model detect and repair errors in its own prior output? This is the family you are grounding. It is split into:
- **C1: Intrinsic self-correction** — no new evidence; the model must self-correct from internal re-examination alone
- **C2: Evidence-assisted correction** — weak/suggestive evidence is provided; the model must integrate it without blind flipping

Family C is currently at 45 clean items across a 5-model sweep. Empirical results show:
- 3 of 4 non-rigid models show positive T2-T1 accuracy deltas when given a metacognitive review prompt
- Self-correction rates are measurable but volatile (denominators of 4–9 wrong-on-T1 items per model)
- Damage (correct→wrong under review) is extremely rare — 1 genuine case across 180 model-item trials
- One model (Grok) shows complete rigidity: zero revision in either direction
- The strongest self-corrector (DeepSeek) shows +8.9 percentage points T2-T1 improvement

The existing theoretical grounding for Family C is thin compared to Family B. Family B has:
- `docs/metacognition_literature_report.md` — a 371-line annotated bibliography tracing metacognition from Hart (1965) through LLM evaluation (2026), structured as a narrative review with 80+ sources across three historical domains, culminating in a unified 5-construct theoretical framework
- `docs/family_b_literature_review.md` — a 718-line paper-by-paper design research review covering 50+ papers with full summaries and direct design implications

Family C currently has only the `Theoretical_grounding_MetaJudge_Family_C.md` memo (226 lines) — a well-researched but engineering-focused document answering 7 pre-specified design questions. It does not trace self-correction through its own intellectual lineage.

**Your task is to close this gap.**

---

## STRUCTURE REQUESTED

Model the document on the structure that made `metacognition_literature_report.md` effective:

### Part I: Psychological Foundations of Error Detection and Correction

Trace the construct of self-correction through its psychological origins. This is not "background" — it is the theoretical argument for why self-correction is a distinct metacognitive operation that A and B cannot measure.

Key threads to trace (not exhaustive — follow the literature where it leads):

**Error monitoring and conflict detection.** The ability to detect that something has gone wrong is the prerequisite for correction. Cover the psychological lineage:
- Rabbitt's (1966) error detection without external feedback — the earliest demonstration that humans can detect their own errors
- Conflict monitoring theory (Botvinick, Braver, Barch & Carter, 2001) — the ACC-based model of how the cognitive system detects processing conflicts
- Error-related negativity (ERN/Ne) as a neural signature of error monitoring (Gehring et al., 1993; Falkenstein et al., 1991) — the earliest evidence that error detection occurs even before conscious awareness
- How does this map to what we're measuring in LLMs? The C1 task is structurally analogous to ERN-mediated correction: can the system detect an error without external feedback?

**The hypercorrection effect and the paradox of confident errors.** Metcalfe's program:
- Butterfield & Metcalfe (2001) — high-confidence errors are *more* correctable after feedback, not less
- Metcalfe (2017) — the productive role of error detection in learning
- This is directly relevant to Family C's design: items where models are wrong with high confidence (the overconfident-wrong cluster from Family A data) may be the *most* amenable to self-correction, not the least
- Does the LLM self-correction literature confirm or refute the hypercorrection analogy?

**The metacognitive control of revision.** Nelson & Narens' control arm:
- The distinction between monitoring signals (FOK, JOL, confidence) and control actions (allocation of study time, termination of search, revision of output)
- Koriat & Goldsmith's (1996) report/withhold framework — the Family B foundation — but now viewed from the *revision* angle: what does it mean to "withhold" a previously given answer?
- Zimmerman's (2000) self-regulated learning cycle: forethought → performance → self-reflection — does the two-turn C1/C2 protocol map to the performance→self-reflection transition?

**Feeling of Knowing and the "unresolved" outcome.** The theoretical basis for why "I'm not sure anymore but I can't fix it" is a legitimate metacognitive response:
- Hart (1965) — FOK as prospective monitoring after failed recall
- Nelson & Narens' (1990) FOK → search termination mapping
- The distinction between FOK ("I could recognize the answer") and TOT ("I almost have it") — which does the "unresolved" outcome in Family C correspond to?
- Reliability of metacognitive judgments: Jacobson & Truax (1991) Reliable Change Index — what confidence drop constitutes a real signal vs. noise?

### Part II: The Self-Correction Turn in LLM Research (2023–2026)

This is where the narrative should shift from psychology to ML/AI. The key papers cluster into several threads:

**The Huang et al. negative result and its aftermath.** This is the watershed:
- Huang, Xu, Lam, Li & Liang (ICLR 2024) — "Large Language Models Cannot Self-Correct Reasoning Yet" — the paper that forced the C1/C2 separation
- Trace the *response* to Huang: who confirmed, who qualified, who found exceptions?
- Kamoi, Miltsakaki, Goyal et al. (TACL 2024) — the critical survey that established fairness criteria for self-correction evaluation
- Tyen, Mansoor, Chen, Mak & Cãmara (ACL Findings 2024) — the detection-bottleneck reframing: models can fix errors they can locate, but they can't locate them

**Conditions under which self-correction works.** The positive results, carefully bounded:
- Kumar, Zhan, Ni, Swersky, Hashimoto, Levine, Lu (ICLR 2025, SCoRe) — RL-trained self-correction (+15.6% on MATH), but this requires purpose-built training
- Liu et al. (2024) — zero temperature + "fair" prompts enable modest correction
- Bohnet et al. (Dec 2025) — intrinsic self-critique for planning tasks
- What is the **boundary**: when does intrinsic self-correction work, and when does it fail?

**The sycophancy problem — self-correction's dark twin.** A model that "self-corrects" by flipping to whatever the review prompt implies is not metacognitively correcting — it's complying. This is the central confound Family C must navigate:
- Zhang et al. (ACL 2025) — "Are you sure?" is internally indistinguishable from "You are wrong"
- Sharma et al. (2023) — sycophancy as RLHF artifact
- Çelebi et al. (2025, PARROT) — eight behavioral states for sycophancy
- Hong et al. (2025, SYCON Bench) — Turn of Flip metrics
- Google DeepMind/UCL (2025) — 2.5× overweighting of criticism
- How does MetaJudge Family C's maintain/revise/unresolved triad address the sycophancy confound?

**Iterative refinement and when more turns help.** The multi-turn question:
- Madaan et al. (NeurIPS 2023, Self-Refine) — iterative self-refinement, diminishing returns after round 1–2
- Shinn et al. (NeurIPS 2023, Reflexion) — verbal reinforcement learning with episodic memory
- Yang et al. (EMNLP 2025) — probabilistic inference scaling theory for self-correction
- Jiang et al. (2025, PAG) — multi-turn RL with selective revision
- What does the convergence/diminishing-returns pattern tell us about optimal number of turns?

**Existing self-correction benchmarks.** The competitive landscape:
- Tie et al. (NeurIPS 2025, CorrectBench) — three-paradigm taxonomy (intrinsic/external/fine-tuned)
- Tsui (2025, Self-Correction Bench) — the "blind spot" phenomenon: models correct others' errors but not their own
- Gou et al. (2023, CRITIC) — tool-interactive critiquing
- Paul et al. (EACL 2024, REFINER) — trained external critic
- SelfCheckGPT (Manakul et al., EMNLP 2023) — consistency-based hallucination detection
- Wu et al. (EMNLP 2024, ProCo) — key condition verification
- What does each measure? What does none of them measure that Family C does?

### Part III: Bridging Constructs — From Psychology to LLM Benchmark Design

This section should do what the Family B report's "Toward a Theoretical Framework" section did: synthesize the preceding two domains into constructs that are directly testable.

Proposed constructs (refine based on what the literature review reveals):

1. **Error Detection Without External Feedback** — the C1 core. Psychological basis: ERN, conflict monitoring. LLM basis: Tyen et al. detection bottleneck. Measurement: does the model identify that its T1 answer may be wrong?

2. **Evidence-Calibrated Revision** — the C2 core. Psychological basis: Bayesian updating under uncertainty, Koriat's cue-utilization. LLM basis: Kamoi et al. fairness framework. Measurement: does the model revise appropriately given weak evidence, without blind flipping?

3. **Damage Avoidance as Metacognitive Constraint** — the anti-sycophancy mechanism. Psychological basis: prospect theory (Kahneman & Tversky 1979), loss aversion λ ≈ 2 (Brown et al. 2024 meta-analysis). LLM basis: the sycophancy literature. Measurement: is the damage penalty sufficient to prevent "always revise" gaming?

4. **Confidence Repair** — the monitoring-control link made visible. Psychological basis: Nelson & Narens' monitoring→control information flow. LLM basis: Xiong et al. (ICLR 2024) on prompt-sensitive overconfidence. Measurement: does confidence move in the epistemically appropriate direction across turns?

5. **Appropriate Search Termination** — the "unresolved" outcome. Psychological basis: FOK → search termination (Nelson & Narens 1990), TOT states. LLM basis: the distinction between "I don't know" and "I was wrong." Measurement: can the model lower confidence without forcing a revision it can't justify?

### Part IV: Comprehensive Source Inventory

Organized by domain, with full bibliographic entries:
- Domain 1: Foundational psychology (error monitoring, conflict detection, metacognitive control, FOK/TOT, hypercorrection)
- Domain 2: Modern cognitive science (self-regulated learning, confidence as inference, meta-reasoning)
- Domain 3: LLM self-correction (the core papers from 2023–2026)
- Domain 4: LLM sycophancy and adversarial dynamics
- Domain 5: Decision theory and psychometrics (prospect theory, RCI, item discrimination)
- Domain 6: Existing benchmarks

### Conclusion

Synthesize the entire arc into a single insight — comparable in clarity to the Family B report's "the monitoring-control gap is the primary metacognitive failure mode" conclusion. What is Family C's equivalent?

---

## RESEARCH SCOPE AND QUALITY STANDARDS

**Temporal range:** 1965 (Hart, Rabbitt) through March 2026. Weight recent LLM work (2024–2026) heavily but do not neglect the psychological foundations — they are what distinguish this from a survey paper.

**Source priority:** Peer-reviewed proceedings and journals first (ACL, EMNLP, ICLR, NeurIPS, NAACL, Psychological Review, Annual Review of Psychology). High-quality arXiv preprints when they are foundational to the LLM self-correction discourse. Conference workshops only if they introduce a novel construct.

**Citation depth:** For foundational papers (Hart, Nelson & Narens, Metcalfe, Botvinick, Huang et al., Kamoi et al., Tyen et al.), provide full annotated entries: authors, year, venue, key findings, methodological details, and explicit connection to Family C design. For supporting papers, a shorter entry in the source inventory is sufficient.

**What makes this document succeed:**
- A reader with no prior knowledge of MetaJudge should be able to read it and understand why self-correction is a distinct metacognitive construct, what the state of the art is for measuring it in LLMs, and where the gaps are that Family C fills.
- A reader who has read the Family B literature report should recognize the same intellectual seriousness and depth applied to a different construct.
- A Kaggle judge evaluating benchmark quality should find this document sufficient to conclude that Family C's design decisions are grounded in science, not engineering convenience.

**What makes this document fail:**
- If it reads as a list of papers rather than a narrative argument
- If the psychological foundations feel like obligatory "background" rather than the theoretical core
- If the LLM section doesn't engage critically with the literature (e.g., just listing papers as "relevant" without explaining what they actually found and where they disagree)
- If the bridging section doesn't produce testable constructs with clear operationalizations
- If the source inventory is incomplete or sloppily formatted

---

## EXISTING MATERIAL TO BUILD ON

The following documents contain partial grounding that this report should subsume and extend:

1. `planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md` — 226-line research memo answering 7 design questions. Contains good citations (Kamoi et al. 2024, Tyen et al. 2024, Kumar et al. 2025, Brown et al. 2024 meta-analysis on loss aversion) but organized as Q&A rather than narrative. The scoring-ratio analysis (Q5) and "unresolved" analysis (Q6) are particularly strong and should be incorporated.

2. `planning/family_c_sprint/01_scientific_constraints.md` — 184-line design principles memo. Contains 7 non-negotiable principles with brief literature justification. These principles should emerge naturally from the review rather than being stated axiomatically.

3. `planning/family_c_sprint/09_deep_research_prompt.md` — the prompt that produced document #1. Contains empirical context from v0.5.5.1 results that should be referenced.

4. `docs/metacognition_literature_report.md` — the Family B annotated bibliography. This covers the shared theoretical foundations (Nelson & Narens, Koriat & Goldsmith, Flavell, Fleming) and should be cross-referenced but not duplicated. The Family C report should extend these foundations into the self-correction domain, not re-derive them.

5. Key empirical findings from the v0.6.2 sweep that the review should engage with:
   - T2-T1 delta is the most powerful metric (DeepSeek +8.9pp is the only significant result)
   - Frontier reasoning models (GPT-5.2, DeepSeek-R1) solve all candidate WR items via CoT — the difficulty gap between canary-hard and frontier-hard is a chasm, not a gradient
   - Self-correction rates have Wilson CI widths of 40–70% at current item counts (4–9 wrong-on-T1 per model)
   - Only 1 genuine damage event across 180 trials — damage is near-zero empirically
   - One model (Grok) is completely rigid — zero revision behavior in either direction

---

## DELIVERABLE

A single Markdown document titled: **"From Error Detection to Self-Repair: The Metacognitive Science of Self-Correction and Its Measurement in Large Language Models"** (or a better title that emerges from the research).

Target length: 400–700 lines (comparable to the Family B literature report, not the shorter design memo). Quality over quantity — a tighter 450-line document with strong narrative is preferable to a padded 700-line survey.

Place at: `docs/family_c_literature_report.md`
