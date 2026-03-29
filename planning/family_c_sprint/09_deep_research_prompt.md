# Deep Research Prompt: Family C Theoretical Grounding

**Purpose:** This prompt is designed to be given to a deep research agent (separate
service) to produce theoretical grounding that will inform the final item design,
prompt engineering, and scoring decisions for MetaJudge Family C (Self-Correction).

**Expected output:** A research memo (5-15 pages) with specific, actionable
recommendations grounded in the academic literature and existing benchmark results.

---

## PROMPT BEGINS HERE

---

You are a research consultant for MetaJudge-AGI, a Kaggle benchmark that measures
epistemically robust metacognitive behavior in LLMs. The benchmark is organized
around two axes from Nelson & Narens (1990):

- **Axis I — Epistemic Monitoring:** Does the model track the reliability of its cognition?
- **Axis II — Cognitive Control:** Does the model use monitoring information to change behavior?

The benchmark currently has two live families:
- **Family A (Confidence Calibration):** 117 items, Brier-derived scoring, 5-model panel evaluated
- **Family B (Selective Abstention/Verification):** 84 items, UWAA utility scoring, 5-model panel evaluated

We are now designing **Family C (Self-Correction)**, which sits on the **Control axis**
and measures whether a model can detect and repair errors in its own prior output.

Family C is split into two mandatory subfamilies (per Huang et al., ICLR 2024):
- **C1: Intrinsic Self-Correction** — generic review prompt, no new evidence
- **C2: Evidence-Assisted Correction** — weak/suggestive contradiction or hint provided

Your task is to provide deep theoretical grounding for several open design questions.

---

## CONTEXT: What We Already Know

### Empirical Results from v0.5.5.1

We have run a 5-model panel (Gemini 2.5 Flash, Gemini 2.5 Pro, Claude Sonnet 4,
Claude Haiku 4.5, DeepSeek v3.1) on 117 calibration items and 84 abstention items.

**Key empirical findings:**

1. **Overconfidence is the dominant failure mode.** The bridge analysis shows a 73.6%
   overconfidence rate — models report 91.1% mean confidence but achieve only 76.4%
   accuracy. 33 cases of "overconfident wrong answer" in Family B.

2. **Model ordering differs on accuracy vs calibration.** Gemini models have highest
   accuracy (87.2%) but worst Brier scores (0.88). Haiku has lowest accuracy (71.8%)
   but best Brier (0.78). This suggests Family C may produce yet another ordering.

3. **Low confidence triggers good control, high confidence breaks it.** When models
   are uncertain (confidence < 0.3), they achieve 0.91 utility in Family B. When
   extremely confident (0.95+), only 0.30 utility. The monitoring→control link is
   present but inverted at high confidence.

4. **Specific items are consistently wrong across models.** Compound interest
   calculations (0% accuracy, 0.97 confidence), bookworm trick questions (0% accuracy,
   0.92 confidence), missing dollar paradox (10% accuracy, 0.97 confidence). These
   are strong wrong-to-right candidates for C1/C2.

5. **25 items have 100% accuracy across all 5 models.** These are natural
   right-to-right (damage resistance) candidates for Family C.

6. **36 items (30.8%) flagged in QA audit** as having ambiguous gold answers,
   evolving facts, or semantic matching issues. Family C item design must avoid
   these pitfalls.

### Governing Literature

The project is primarily grounded in:
- **Nelson & Narens (1990)** — two-process metacognition (monitoring + control)
- **Huang et al. (ICLR 2024)** — "Large Language Models Cannot Self-Correct Reasoning
  Yet" — demonstrates C1 (intrinsic) fails without oracle feedback; mandates C1/C2 separation
- **Kadavath et al. (2022)** — "Language Models (Mostly) Know What They Don't Know"
- **Xiong et al. (ICLR 2024)** — verbalized confidence is prompt-sensitive and overconfident
- **Flavell (1979)** — original metacognition framework (knowledge, monitoring, control, experience)

### Design Constraints Already Decided

- Two-turn design (Turn 1: answer + confidence; Turn 2: review + revised answer + revised confidence)
- Maintain/Revise/Unresolved triad (not binary change/no-change)
- Behavioral scoring only (narrative fields like `what_changed` are diagnostic, never scored)
- Asymmetric damage penalty (breaking a correct answer penalized more than missing a correction)
- Clean-set discipline (audit, quarantine, promote)
- C1 and C2 always reported separately

---

## RESEARCH QUESTIONS

Please investigate the following questions thoroughly. For each, provide:
- What the literature says
- What our empirical data suggests
- Your specific recommendation for MetaJudge
- Confidence level in your recommendation (high/medium/low)

### Question 1: C1 Intrinsic Self-Correction — Is There Signal?

**Context:** Huang et al. (2024) found that intrinsic self-correction largely fails.
Our data shows models are overconfident and wrong on many items. The concern is that
C1 will show a floor effect with near-zero variance across all models.

**Investigate:**
a) What does the post-Huang literature say? Have any papers found conditions under
   which intrinsic self-correction works (e.g., specific error types, specific prompt
   formulations, specific model architectures)?

b) Are there **error types** that are more amenable to intrinsic self-correction?
   Our data suggests arithmetic errors, order-of-operations errors, and spatial
   reasoning errors may be more catchable. Is this supported by the literature?

c) What **prompt engineering strategies** for the turn-2 review prompt maximize the
   probability of genuine (not obedient) self-correction? Consider:
   - "Please review your answer" (generic)
   - "Check your work step by step" (process-oriented)
   - "What is the most likely error in your previous answer?" (error-focused)
   - "Rate your confidence that your answer is correct, then decide whether to revise" (metacognitive)
   - Any other formulations studied in the literature

d) Is there a **minimum discrimination threshold** below which C1 is not worth including
   in a benchmark? What would a scientifically defensible floor-effect policy look like?

e) Given that we expect C1 performance to be low, how should the benchmark frame
   this to judges and the community? As a "frontier probe"? As a "negative result
   that constrains claims"? As "baseline for future capability tracking"?

### Question 2: Optimal Number of Turns

**Context:** Our current design uses 2 turns. A 3rd turn could test:
- Flip-back behavior (model reverts after second challenge)
- Confidence erosion under repeated challenge
- Escalation response (stronger challenge breaks what weaker didn't)

**Investigate:**
a) Does the metacognition literature distinguish between single-review and
   iterated-review protocols? What does each measure that the other doesn't?

b) Are there published benchmarks or experiments that used 3+ turns for
   self-correction? What did the additional turns reveal?

c) From an information-theoretic perspective, how much marginal information does
   a 3rd turn add beyond the 2nd? Is there a diminishing returns argument?

d) Would a 3rd turn risk **iatrogenic effects** — e.g., causing models to
   second-guess correct answers more after repeated challenges, introducing noise
   rather than signal?

e) **Recommendation:** For a 35-item seed set, should we include any 3-turn items?
   If so, how many and what type? If not, at what expansion phase would 3-turn
   items become worth piloting?

### Question 3: Item Overlap Between Families — Scientific Validity

**Context:** We plan to overlap ~43% of Family C items with the A/B item pool
(same questions, different task). This allows cross-family consistency analysis.

**Investigate:**
a) In psychometric test design, when is item overlap across subtests considered
   valid vs. problematic? What are the standard arguments for and against?

b) Does overlap risk **practice effects** or **priming** if the same model sees
   the same question in Family A and Family C? Note: in our benchmark, families
   are run in separate tasks with `chats.new()` isolation, so there is no
   within-session memory carryover. But models may have systematic biases on
   specific items regardless.

c) What is the strongest scientific argument FOR overlap? (Our hypothesis:
   it enables direct testing of the monitoring→control link — does high A-confidence
   predict C-maintenance? Does low A-confidence predict C-revision?)

d) What is the strongest argument AGAINST overlap? What could go wrong?

e) **Recommendation:** Is ~43% overlap appropriate, too high, or too low? Is there
   a principled way to determine the optimal overlap ratio?

### Question 4: Same-Budget Fairness for C1 vs C2

**Context:** C2 provides extra information (weak evidence) that C1 does not. Huang
et al. argue this makes C2 fundamentally different from C1. We need to ensure our
benchmark fairly compares the two without overclaiming.

**Investigate:**
a) How does the self-correction literature handle **same-budget baselines**?
   Is there a standard way to control for the "extra compute" that a second turn provides?

b) Should C1 be compared to a **re-answering baseline** — i.e., what would the
   model's accuracy be if simply asked the question again without any review prompt?
   If so, how do we implement this without doubling the item count?

c) What is the fairest way to compare C1 and C2 scores? Should we report:
   - Raw scores for each?
   - Gain over a baseline for each?
   - Normalized scores?

d) Could C2's evidence advantage be calibrated by varying evidence strength?
   (e.g., very weak hint vs. moderately suggestive contradiction vs. strong pointer)

e) **Recommendation:** What specific same-budget controls should MetaJudge
   implement for a defensible first release?

### Question 5: Damage Rate — How Asymmetric Should the Penalty Be?

**Context:** Our current scoring blueprint penalizes damage (correct→wrong) at
base 0.05 vs correction gain (wrong→correct) at 0.90. This is deliberately
asymmetric. The rationale is that breaking correct answers is worse than failing
to fix wrong ones.

**Investigate:**
a) Is there a psychometric or decision-theoretic basis for a specific asymmetry
   ratio? Our current ratio is roughly 18:1 (0.90 / 0.05). Is this too extreme,
   too mild, or about right?

b) How do existing self-correction benchmarks handle the damage/gain asymmetry?

c) Should the asymmetry differ between C1 and C2? (Our current plan: C1 damage
   is penalized more harshly because C1 revision is purely self-generated.)

d) Is there a risk that extreme asymmetry creates a **conservative bias** — models
   that never revise score acceptably (0.70 for maintain-correct, 0.30 for
   stubborn-wrong) while models that sometimes revise risk damage penalties?

e) **Recommendation:** What damage:gain ratio is defensible for a behavioral
   metacognition benchmark? Should it be configurable?

### Question 6: The "Unresolved" Outcome — Theoretical Status

**Context:** Our design includes an "unresolved" outcome where the model detects
uncertainty but does not commit to a revised answer. This is the third leg of
the maintain/revise/unresolved triad.

**Investigate:**
a) What is the theoretical basis for "unresolved" as a distinct metacognitive
   state? Is it equivalent to "feeling of knowing" (FOK) in the Nelson & Narens
   framework? Or is it closer to "judgment of learning" (JOL)?

b) How should "unresolved" be operationalized in a two-turn benchmark? What
   behavioral evidence distinguishes "unresolved" from "maintain"?
   Our current heuristic: confidence drops by ≥ 0.15 without a revised answer.

c) Is the 0.15 threshold defensible, or should it be empirically calibrated?

d) Are there items that are normatively "unresolved" — where the correct
   metacognitive response is genuine uncertainty, not revision or maintenance?

e) **Recommendation:** How should MetaJudge score "unresolved" outcomes?
   What distinguishes appropriate unresolved from lazy non-commitment?

### Question 7: Comparison to Existing Self-Correction Benchmarks

**Investigate:**
a) What existing benchmarks or evaluation suites test LLM self-correction?
   Consider: SelfCheckGPT, IfEval, TruthfulQA (with follow-up), any
   debate/revision protocols, any iterative refinement benchmarks.

b) How does MetaJudge Family C differ from these? What is our unique contribution?

c) Are there item types or scoring innovations from existing benchmarks that
   we should adopt or explicitly reject?

d) What claims do existing benchmarks make that MetaJudge should be careful
   NOT to make?

e) **Recommendation:** How should MetaJudge position Family C relative to the
   existing landscape? What is our distinctive claim?

---

## OUTPUT FORMAT

Please structure your response as a research memo with these sections:

1. **Executive Summary** (1 paragraph per question)
2. **Detailed Findings per Question** (with literature citations)
3. **Integrated Recommendations** (a coherent set of design recommendations
   that address all 7 questions together)
4. **Confidence Assessment** (where you're confident, where uncertainty remains)
5. **Key Citations** (papers, benchmarks, and datasets referenced)

Be specific and actionable. We need recommendations we can implement in code
and item design, not general commentary about metacognition.

---

## PROMPT ENDS HERE
