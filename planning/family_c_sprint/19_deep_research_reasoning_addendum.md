# Deep Research Prompt: Reasoning-Model Addendum to Family C Literature Report

**Context:** You previously produced the document "Self-Correction as Metacognitive Control: From Error-Related Negativity to LLM Revision Benchmarks" (`docs/family_c_literature_report.md`). That document traces self-correction from its psychological origins through the 2024–2025 LLM literature and establishes the detection-revision asymmetry as Family C's signature construct.

**The problem:** The literature you reviewed is already partially obsolete for the purpose it needs to serve. The core papers — Huang et al. (ICLR 2024), Tyen et al. (ACL Findings 2024), Kamoi et al. (TACL 2024) — tested models that do not have native chain-of-thought reasoning as an architectural feature. GPT-3.5, GPT-4, Llama-2 — these are instruction-tuned models, not reasoning models. Since those papers were published, a new class of models has emerged:

- **OpenAI o1/o3 family** (released late 2024–2025): native chain-of-thought with internal verification loops
- **DeepSeek-R1** (Nature, 2025): self-correction emerged spontaneously from pure RL training; extended CoT with self-verification is an intrinsic behavior, not a prompting technique
- **Anthropic Claude with extended thinking** (2025): configurable thinking budgets that produce multi-step internal reasoning before output
- **Google Gemini reasoning mode** (2025–2026): similar architecture with internal deliberation
- **QwQ, Qwen-with-thinking, and open-source reasoning models** (2025–2026)

These models change the self-correction measurement problem fundamentally. Tyen et al.'s detection bottleneck — "models can correct errors once located but cannot locate them" — may no longer be the binding constraint for reasoning models, because **these models already perform internal error detection as part of their standard generation process**. When you prompt a reasoning model to "review your answer," you are not triggering a metacognitive review — you are triggering a second pass of the same CoT process that already included self-verification. The C1 construct (intrinsic self-correction without external evidence) becomes ambiguous: are you measuring metacognitive control, or are you measuring whether the model gets a second roll of its own reasoning dice?

**Your task:** Produce an addendum to the existing literature report that addresses this gap. The addendum should be structured as a new Part (Part V, inserted before the Conclusion) titled something like "The Reasoning-Model Frontier: Self-Correction After Internalized Chain-of-Thought." It should be 200–400 lines and should be insertable into the existing document without modifying Parts I–IV.

---

## RESEARCH QUESTIONS

### Q1: What does self-correction mean when the model already self-corrects during generation?

The existing literature distinguishes C1 (intrinsic, no external evidence) from C2 (evidence-assisted). But reasoning models blur this boundary. A model that produces extended CoT with "Wait, let me reconsider..." during Turn 1 has already performed intrinsic self-correction *within a single generation*. Does a Turn 2 review prompt add anything beyond a second sample from the same process?

**Investigate:**
- Are there papers (late 2025 or 2026) that specifically study self-correction behavior in o1-class, DeepSeek-R1, or other reasoning models?
- Does the self-correction literature distinguish between **inter-turn correction** (what Family C measures: revise after a review prompt) and **intra-turn correction** (what reasoning models do: revise within a single CoT generation)?
- Is there a theoretical framework for when inter-turn correction adds value beyond intra-turn correction? The DeepSeek-R1 paper (Nature, 2025) describes self-correction emerging from RL training — does it discuss when the model's internal correction succeeds vs. fails?
- What does SCoRe (Kumar et al., ICLR 2025) imply about the relationship between training-time correction and inference-time correction? SCoRe trains correction jointly under the model's own error distribution — does this make subsequent prompted correction redundant?

### Q2: What kinds of errors survive reasoning-model CoT?

If reasoning models already self-verify during generation, the errors they produce on Turn 1 are not random failures but **errors that survived internal verification**. These should be qualitatively different from the errors older models produce.

**Investigate:**
- Are there analyses of the *error types* that reasoning models produce? We have empirical evidence from our own data: in MetaJudge's Batch 2 WR hardening audit, both GPT-5.2 and DeepSeek-R1 solved every computationally complex item (sequences, enumeration, floor division, etc.) but we predict they would fail on convention traps, precision execution, and definition-boundary ambiguities. Is this pattern documented in the literature?
- Tsui's (2025) Self-Correction Bench found a "blind spot" where models correct others' errors but miss identical errors in their own output. Does this blind spot persist in reasoning models, or does internal CoT reduce it?
- Bohnet et al. (Dec 2025) showed dramatic self-correction on planning tasks. Does this extend to mathematical reasoning, factual recall, or other domains? What makes planning tasks amenable to self-correction that other tasks are not?
- Is there a taxonomy of "CoT-resistant errors" — errors that reasoning models make *because* of their CoT (e.g., the CoT is fluent, confident, and wrong — no internal conflict to detect)?

### Q3: How should C1 be designed for reasoning models?

The current C1 Turn 2 prompt is: "Please reconsider your answer carefully. Take a moment to verify your reasoning step by step." For a reasoning model that already verified step-by-step on Turn 1, this prompt is redundant. It may still produce corrections (via stochastic variation if temperature > 0), but those corrections are not evidence of metacognitive control — they're evidence of sampling noise.

**Investigate:**
- Are there proposed alternatives to generic review prompts that would specifically trigger metacognitive evaluation rather than re-generation in reasoning models?
- The Tsui (2025) finding that appending "Wait" reduces the blind spot by 89.3% suggests that even minimal prompts can trigger detection. But "Wait" works *within* a single generation (intra-turn). What is the equivalent for inter-turn correction?
- Hong et al. (Findings of EMNLP 2025) found that third-person framing ("A reviewer is checking this answer") reduces sycophancy by 63.8%. Would this framing also help separate metacognitive review from CoT re-generation?
- Should C1 for reasoning models explicitly instruct the model to *not* re-derive the answer but instead evaluate its existing reasoning? Something like: "Do not re-solve the problem. Instead, identify the most likely error in your previous reasoning, if any exists. If you find an error, state what it is and provide a corrected answer. If you find no error, confirm your original answer." This targets the detection bottleneck directly rather than giving the model another chance to generate.
- Is there any literature on "detect-only" prompts (asking the model to find errors without correcting them) vs. "detect-and-correct" prompts? The Tyen et al. decomposition into mistake-finding and output-correction suggests these should be measured separately.

### Q4: How should C2 evidence snippets be designed for reasoning models?

Reasoning models have already processed the problem deeply during Turn 1 CoT. A C2 evidence snippet that provides domain context is redundant — the model already has that context from its own reasoning. Effective C2 evidence for reasoning models needs to provide information that the model's CoT *specifically missed or got wrong*.

**Investigate:**
- Are there approaches to "targeted" evidence design — evidence that addresses the specific error a model made, rather than providing generic domain information?
- Tyen et al.'s finding that oracle error locations enable correction suggests that C2 evidence should function as a partial oracle — pointing toward the error without stating the answer. Is there a graduated scale of evidence specificity in the literature?
- The distinction between Koriat's extrinsic cues (new external information) and mnemonic cues (prompts that trigger re-access of existing knowledge) is relevant: for reasoning models, domain-context evidence is mnemonic (they already have it), while error-specific evidence is extrinsic (genuinely new). Are there papers that study how reasoning models respond to different cue types?
- Kamoi et al.'s fairness framework requires that evidence augments rather than replaces the initial response. How does this interact with reasoning models where the initial response already includes extensive deliberation?

### Q5: What does the scoring framework need to change for reasoning models?

The current scoring assumes a clean distinction between Turn 1 (initial answer) and Turn 2 (revision after review). But reasoning models may produce different Turn 1 answers on different samples due to stochastic CoT. If the model's Turn 1 answer is unstable (it would have given a different answer on a re-sample), then Turn 2 "correction" may just be the model sampling a different CoT path.

**Investigate:**
- Is there a self-consistency-based approach to measuring self-correction? Wang et al. (ICLR 2023) showed that self-consistency (majority vote across samples) improves accuracy. Kamoi et al. warned that self-correction gains must exceed what self-consistency provides. How should Family C control for this?
- Should a **re-answering baseline** (same question, no review prompt, fresh generation) be mandatory for C1? This would measure the "second roll of the dice" baseline against which genuine self-correction can be assessed.
- For reasoning models with visible thinking traces, should the scoring framework evaluate the *quality of the revision reasoning* (did the model genuinely identify an error, or did it just generate a different answer)? This would mean reading the CoT, which violates MetaJudge's "behavioral scoring only" principle. Is there a way to use CoT information without scoring narrative content?
- The power analysis for the existing 45-item sweep showed that T2-T1 accuracy delta is the most defensible metric. Does this remain true for reasoning models, where T1 accuracy is likely higher (fewer correction opportunities)?

### Q6: What does the latest preprint frontier (late 2025 – early 2026) reveal?

This is the most important search task. The reasoning-model revolution is approximately 12–18 months old. The earliest papers testing self-correction *specifically in reasoning models* are likely appearing in 2025–2026 preprints and workshops.

**Search specifically for:**
- Papers testing self-correction in o1, o3, DeepSeek-R1, or other reasoning-class models
- Papers on "overthinking" or "reasoning degradation" in CoT models — cases where more thinking produces worse answers (this is the CoT-resistant error pattern we need for item design)
- Papers on the interaction between reasoning training (RL for CoT) and sycophancy/compliance behavior
- Papers on measuring metacognition *separately from reasoning* in models that reason as part of generation (the DMC framework from Wang et al. AAAI 2025 is relevant but predates the reasoning-model wave)
- Benchmark papers that specifically target reasoning-model failure modes
- Papers on "prompt injection into CoT" — adversarial inputs that exploit the model's reasoning process rather than its surface compliance
- Workshop papers from NeurIPS 2025, ICLR 2026, AAAI 2026, or ACL 2026 workshops on LLM reasoning, self-correction, or metacognition

---

## OUTPUT FORMAT

Produce the addendum as a standalone section (Part V) that can be inserted into the existing literature report before the Conclusion. The addendum should:

1. **Open with the problem statement**: why reasoning models change the self-correction measurement target
2. **Organize findings by research question** (Q1–Q6), but write them as a narrative, not as Q&A
3. **Produce specific, actionable design recommendations** for C1 and C2 item/prompt design for reasoning models
4. **Identify which findings from Parts I–IV of the existing report still hold for reasoning models and which need qualification**
5. **Include a mini source inventory** for any new papers not already cited in the existing report, in the same structured table format (Authors | Year | Title | Venue | Key Contribution)
6. **Close with an assessment** of whether the detection-revision asymmetry — the signature construct from the existing conclusion — remains the right framing for reasoning models, or whether a different asymmetry (e.g., "confident-wrong CoT" vs. "uncertain CoT that self-corrects") better describes the frontier

Target length: 200–400 lines. The existing document is ~335 lines; the addendum should not exceed the main body in length.

---

## WHAT THIS ENABLES

After this addendum, the combined document (Parts I–V + Conclusion) becomes the theoretical foundation for a Family C design sprint that targets reasoning models specifically. The sprint will use API calls through OpenRouter to generate and test items, using a methodology grounded in what the literature says about:
- What error types survive reasoning-model CoT (from Q2)
- How to prompt C1 review without just triggering re-generation (from Q3)
- How to design C2 evidence that adds genuine information beyond what CoT already provides (from Q4)
- What scoring/baseline controls are needed to separate metacognitive correction from stochastic re-sampling (from Q5)

The goal is not statistical power (that requires 75–150 items at current accuracies). The goal is **content validity**: a small set of items (10–20) that reliably produce different self-correction profiles across models, grounded in the specific error types and correction mechanisms that the literature identifies as theoretically meaningful. Those items then become the seed for expansion.
