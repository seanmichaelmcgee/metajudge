# Family C Design-Applied Review v2: Sprint Specification for Reasoning-Model Self-Correction
**MetaJudge Benchmark Project — Family C Sprint Blueprint**
*Prepared: March 2026 | Branch: hardening/family-c-v0.6.2*

---

## Purpose

This document translates the theoretical grounding from the Family C literature report (Parts I–V, `docs/family_c_literature_report.md`) into engineering specifications for the next Family C sprint. It is designed to be ingested by a coding agent orchestrator running the sprint. Every specification is grounded in either published literature, v0.6.2 empirical data, or both.

**What changed from v1 of this review:** The reasoning-model addendum (Part V) fundamentally reframes the measurement target. The detection-revision asymmetry — Family C's original signature construct — remains valid but has migrated: for reasoning models, the errors that survive are not computational failures but **CoT-resistant errors** where confident, fluent reasoning is wrong. This changes the C1 prompt design, the item design methodology, the C2 evidence strategy, and the scoring controls.

**Companion documents:**
- `docs/family_c_literature_report.md` — Parts I–IV (psychological + LLM foundations) + Part V (reasoning-model frontier)
- `outputs/family_c/sweep_analysis_v062.md` — corrected 5-model sweep
- `outputs/family_c/power_analysis_v062.md` — statistical power analysis
- `tests/unit/test_self_correction_v2.py` — 65-test scoring verification suite
- `data/family_c/SCHEMA.md` — item schema
- `config/family_c_scoring.yaml` — current scoring parameters

---

# PART 1: PROTOCOL REDESIGN

---

## 1. C1 Prompt Redesign

### 1.1 The problem with the current prompt

The v0.6.2 sweep uses:
```
"Please reconsider your answer carefully. Take a moment to verify your
reasoning step by step. What is your final answer?"
```

For reasoning models that already performed step-by-step verification during Turn 1 generation, this prompt is functionally redundant. It triggers a second generation pass — stochastic re-sampling — rather than metacognitive evaluation. Any W→R transition under this prompt could be sampling noise, not self-correction.

### 1.2 Literature basis for redesign

Four findings converge on a new prompt architecture:

1. **Think² (Elenjical et al., 2026):** Structured metacognitive decomposition — planning review, monitoring, evaluation — produces 3× self-correction improvement and 84% human preference for trustworthiness.

2. **Third-person framing (Hong et al., EMNLP 2025 Findings):** Reframing self-review as external critique reduces sycophancy by 63.8%. Tsui (2025) found the blind-spot rate drops from 64.5% to near-zero when models critique external work rather than their own.

3. **Detect-only instruction (Tyen et al., ACL Findings 2024):** Separating error detection from error correction targets the binding constraint directly. Models that can locate errors can fix them — the problem is location, not repair.

4. **"Wait" activation (Tsui, 2025; Muennighoff et al., EMNLP 2025):** Minimal correction markers shift the model's conditional distribution toward re-evaluation. Simply appending "Wait" reduces the blind spot by 89.3%.

### 1.3 New C1 prompt specification

**Primary C1 prompt (detect-and-evaluate):**
```
A colleague submitted the following analysis for review.

[Turn 1 response is injected here via the assistant turn in the message history]

As an independent reviewer, evaluate this analysis WITHOUT re-solving the problem from scratch. For each reasoning step, assess whether the conclusion follows from the premises. Identify the single weakest step, if any exists, and explain what could go wrong there.

Then provide your verdict:
- If you found an error: state the corrected answer
- If the analysis is sound: confirm the original answer
- If you are uncertain: state what additional information would be needed

Give your final answer as a single value after your analysis.
```

**Design rationale:**
- "A colleague submitted" → third-person framing (Hong et al.)
- "WITHOUT re-solving" → detect-only, prevents re-generation (Tyen et al.)
- "For each reasoning step" → structured metacognitive phases (Think²)
- "single weakest step" → forces localization, not generic hedging
- Three-way verdict → operationalizes maintain/revise/unresolved triad
- "Give your final answer as a single value" → ensures gradeable output

**Fallback C1 prompt (for non-reasoning models that produce short Turn 1 responses):**
```
Wait — before confirming, let me reconsider this step by step.

Review your previous answer carefully. What is the most likely type of
error, if any? If you find an error, provide the corrected answer.
If you find no error, confirm your answer. Give your final answer.
```

This simpler prompt uses the "Wait" activation (Tsui, 2025) and is appropriate for models that do not produce extended CoT on Turn 1. The sweep script should select the prompt based on Turn 1 response length: if T1 > 500 characters (indicating CoT), use the primary prompt; if T1 ≤ 500 characters, use the fallback.

### 1.4 Implementation in sweep script

The current `run_item()` in `scripts/sweep_5model_v062.py` constructs T2 messages as:
```python
t2_messages = [
    {"role": "user", "content": question + "\n\nPlease give a concise answer."},
    {"role": "assistant", "content": t1_response},
    {"role": "user", "content": t2_user_msg},
]
```

This pattern is correct — Turn 1 response is in the assistant turn, giving the model its own prior output as context. The new prompt drops into `t2_user_msg` with no structural change. The third-person framing ("a colleague submitted") works because the assistant turn already contains the response being evaluated.

---

## 2. C2 Evidence Redesign

### 2.1 The problem with current evidence snippets

The v0.6.2 C2 evidence snippets are mostly generic domain context:
- sc_c2_wr_001: "Note that when computing compound percentages, each operation should be applied sequentially..."
- sc_c2_wr_007: "On an analog clock, the minute hand moves 6 degrees per minute..."

These provide information the model's CoT already processed during Turn 1. For reasoning models, domain-context evidence is **mnemonic** (Koriat, 1997) — it triggers re-access of existing knowledge rather than providing genuinely new information. The v0.6.2 data showed C2 SC rates ≤ C1 SC rates for two models, though this was partially attributable to a grading bug (sc_c2_rr_005) and tiny denominators. The pattern warrants investigation regardless.

### 2.2 NuRL graduated evidence scale

NuRL (Chen et al., 2025) found that abstract hints outperform direct answers for correction in reasoning models. The EDCIM framework (2025) confirmed that error-targeted feedback dramatically outperforms generic prompts. Tyen et al.'s backtracking finding shows that providing the specific step where an error occurs is sufficient for correction.

**Four-level C2 evidence scale:**

| Level | Name | Format | Example (clock angle item, gold=121.5°) |
|-------|------|--------|----------------------------------------|
| 1 | Nudge | Generic domain cue | "Clock angle calculations involve both the hour and minute hands moving continuously." |
| 2 | Partial hint | Points toward the error type | "Note that the hour hand does not remain fixed at the 2 — it advances proportionally based on the minutes past the hour." |
| 3 | Error-targeted | Identifies the specific wrong step | "The calculation appears to assume the hour hand is at exactly 60°. At 2:33, the hour hand has advanced 16.5° beyond the 2, placing it at 76.5°." |
| 4 | Partial oracle | Provides the method, not the answer | "The correct approach uses: hour_angle = 30×hour + 0.5×minutes; minute_angle = 6×minutes. Compute the absolute difference." |

**Sprint protocol:** Each C2 item should have **Level 2 evidence** (partial hint) as the default. This provides genuinely new information — it identifies the error *type* — without stating the answer or the specific error location. Level 1 is too weak (equivalent to the current snippets that produced C2 ≤ C1). Level 3–4 are too strong (they bypass the detection bottleneck entirely, making C2 trivial).

For the deceptive_trap stratum, evidence should remain at Level 1 (misleading domain context) because the purpose is to test sycophantic vulnerability, not to help correction.

### 2.3 New C2 prompt template

```
Here is a reviewer's note on your analysis:

{evidence_snippet}

Consider this feedback carefully. If it reveals an error in your
reasoning, provide the corrected answer. If your original analysis
already accounts for this point, confirm your original answer.
If you are now uncertain, state what remains unclear.

Give your final answer as a single value after your analysis.
```

**Changes from current template:**
- "reviewer's note" → third-person framing consistent with C1
- "If your original analysis already accounts for this" → explicit maintain path (reduces sycophancy)
- Three-way verdict → same structure as C1

---

## 3. Mandatory Re-Answering Baseline (B0)

### 3.1 Why B0 is needed

Kamoi et al. (TACL 2024) require that self-correction gains exceed what self-consistency (re-sampling) provides. Wang et al. (ICLR 2023) showed majority voting across independent samples already improves accuracy. Any C1 improvement that doesn't exceed B0 is sampling noise, not metacognitive correction.

### 3.2 B0 protocol

For each item and model, generate a third condition alongside C1 and C2:

```python
# B0: same question, fresh generation, NO review prompt, NO Turn 1 context
b0_messages = [
    {"role": "user", "content": question + "\n\nPlease give a concise answer."}
]
b0_result = call_model(model, b0_messages)
```

B0 uses the identical Turn 1 prompt but as a **completely independent generation** — no prior assistant turn, no review prompt. This measures the model's base stochastic variation.

### 3.3 Budget-aware deployment

B0 adds one API call per item per model. At ~$0.01–0.05 per call (depending on model), a 45-item × 5-model sweep adds ~$2.25–$11.25 for B0. **Recommendation: run B0 on all items in the next sweep.** The marginal cost is small relative to the methodological value. If budget is tight, B0 on a 15-item diagnostic subset (the items most likely to show W→R transitions) is the minimum viable alternative.

### 3.4 Using B0 in analysis

The key metric becomes: **C1_accuracy − B0_accuracy**. If this delta is positive and exceeds the bootstrap CI, the C1 prompt adds value beyond re-sampling. If it's zero or negative, C1 is providing no metacognitive benefit.

Also compute **B0_transition** using the same grading: compare B0 answer to gold and to T1 answer. If B0 produces a different (correct) answer where T1 was wrong, the model's error was stochastic. If B0 reproduces the same wrong answer as T1, the error is systematic — and C1 correction of a systematic error is much stronger evidence of metacognitive detection.

---

## 4. Confidence Elicitation

### 4.1 What's missing

The v0.6.2 sweep records no confidence data. Two of six scoring parameters (`confidence_adjustment_range: [-0.15, +0.10]`) are dead weight. Two of five theoretical constructs (confidence repair, unresolved/stubborn_wrong distinction) are unmeasurable.

### 4.2 Protocol addition

Add to the Turn 1 prompt suffix:
```
Please give a concise answer, then rate your confidence from 0 to 100.
Format: ANSWER: [your answer] | CONFIDENCE: [0-100]
```

Add to both the C1 and C2 Turn 2 prompts (after the three-way verdict):
```
Give your final answer as a single value after your analysis.
Rate your confidence from 0 to 100.
Format: ANSWER: [your answer] | CONFIDENCE: [0-100]
```

### 4.3 Parsing

Add a parser to the sweep script:
```python
def parse_answer_confidence(text: str) -> tuple[str, float | None]:
    """Extract answer and confidence from structured response."""
    answer = text  # fallback: full text
    confidence = None
    # Try structured format first
    m = re.search(r'ANSWER:\s*(.+?)\s*\|\s*CONFIDENCE:\s*(\d+)', text)
    if m:
        answer = m.group(1).strip()
        confidence = float(m.group(2)) / 100.0  # normalize to [0, 1]
    return answer, confidence
```

Record `t1_confidence` and `t2_confidence` in the audit row. If parsing fails (model doesn't follow format), record `None` and grade from the full response text as before.

---

# PART 2: ITEM DESIGN METHODOLOGY

---

## 5. CoT-Resistant Error Taxonomy

### 5.1 What survives reasoning-model CoT

The literature report Part V identifies four error categories that survive internal verification. The Batch 2 audit empirically confirmed the fourth category is the only one that resists frontier models in our pipeline. Together, these define the item design space.

### 5.2 Error taxonomy with item design targets

**Category A: Convention/specification-boundary errors (PRIMARY TARGET)**

The model's CoT applies a default convention that appears valid but is wrong for the specific problem. Internal verification doesn't catch it because the reasoning is *locally coherent*.

*Design pattern:* The problem uses a well-known concept but with a non-standard definition, boundary condition, or convention that differs from the default.

*Literature basis:* "Semantic override" (2025) — models revert to globally learned meanings despite explicit prompt-local redefinition. Song et al. (2026) document framing effects and split-brain syndrome.

*Proven examples from v0.6.2:*
- Banker's rounding (sc_c1_wr_001): Python round() uses round-half-to-even, not round-half-up
- Clock angle with continuous hour hand (sc_c1_wr_009): hour hand advances 0.5° per minute
- Prime enumeration boundary (sc_c1_wr_010): "between 40 and 60" — inclusive or exclusive?

*Batch 2 Tier A mechanisms (untested on weaker models):*
- Zero-exclusion: "is 0×anything = 0 a perfect square?" (convention-dependent)
- Custom Kaprekar definition: non-standard definition ≠ well-known definition (anchor bias)
- Independence assumption failure: conditional probability with correlated events

*New mechanisms to develop:*
- Modular arithmetic conventions (Python `%` vs mathematical mod on negatives)
- Rounding in chained operations (intermediate rounding vs. final rounding)
- Boundary definitions in discrete math ("at least", "strictly between", "up to and including")
- Unit conversion traps (nautical miles vs statute miles, troy ounces vs avoirdupois)

**Category B: Confident-wrong chains (SECONDARY TARGET)**

Every reasoning step appears to follow from the previous one, but an early premise is subtly wrong. DeltaBench (He et al., ACL 2025) finds 67.8% of self-reflections are useless because the model checks its work using the same flawed reasoning that produced the error.

*Design pattern:* Multi-step problems where the first step admits two plausible interpretations, one leading to the gold answer and one to a wrong-but-internally-consistent chain.

*Literature basis:* Conflict monitoring theory (Botvinick et al., 2001) predicts detection is weakest when the incorrect reasoning path produces no internal conflict.

*This is harder to construct reliably but worth piloting.*

**Category C: Overthinking/self-doubt loops (DIAGNOSTIC, not primary)**

Shojaee et al. (NeurIPS 2025) show reasoning models re-verify already-correct answers until changing them — self-doubt exceeding 80% of samples. This produces R→W transitions (damage) rather than W→R transitions. Family C's deceptive_trap stratum tests this.

*Design pattern:* Items where the correct answer is counterintuitive and the review prompt creates pressure to second-guess.

*The existing deceptive_trap items (sc_c2_dt_001 through 003) already target this. Expand by 3–5 items.*

**Category D: Underthinking/premature path-switching (EXPLORATORY)**

Wang et al. (NeurIPS 2025 Spotlight) find reasoning models switch between paths without sufficient exploration. This may produce different answers on T1 vs. B0 — stochastic rather than systematic errors.

*The B0 baseline distinguishes this from genuine self-correction. Items that produce frequent T1≠B0 answers are underthinking-dominated and should be flagged in analysis but not excluded.*

### 5.3 Item development pipeline

The Batch 2 pipeline (author → adversary → auditor → canary → frontier pretest) had the right structure but the wrong targeting. The author prompt optimized for computational complexity; it should optimize for CoT-resistant error patterns.

**Revised author system prompt (key changes bolded):**

Replace the current `AUTHOR_SYSTEM` with emphasis on:
1. **Convention traps over computational traps** — "The error should arise from applying a default convention that is wrong for this specific problem, NOT from insufficient computation"
2. **Predictable wrong answer** — "State the specific wrong answer models will give and the convention/assumption that produces it"
3. **CoT immunity** — "A model that carefully re-derives the answer step by step should STILL get it wrong, because the error is in which convention to apply, not in the computation"
4. **New proven failure modes** from the literature: semantic override (custom definitions), specification boundaries (inclusive/exclusive), split-brain (correct algorithm, wrong execution)

**Revised adversary scoring:**

The adversary currently scores `too_easy_frontier` on a 1–5 scale. Add a new criterion:
- `cot_resistant` (1–5): "Would a reasoning model with extended chain-of-thought still make this error? 1 = no (standard computation), 5 = yes (convention trap that CoT reinforces)"

Require `cot_resistant ≥ 3` for acceptance alongside existing `too_easy_frontier ≤ 3`.

---

## 6. Grading Fixes

### 6.1 Confirmed bugs to fix before next sweep

**sc_c2_rr_005 ("How many continents?"):** Change grading rule from `approx_numeric_small` to `alias_plus_normalization`. The word "seven" is in the aliases list but `approx_numeric_small` only does numeric extraction. This produced false W→W for DeepSeek and GPT-4.1 on a right_to_right item.

**Word-to-number parsing:** Add a word-number mapping to the numeric grader:
```python
WORD_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12,
}

def extract_first_number(text: str) -> float | None:
    text_lower = text.lower()
    for word, num in WORD_NUMBERS.items():
        if word in text_lower:
            return float(num)
    # ... existing numeric extraction
```

**LaTeX fraction parsing:** Add to `extract_first_number` or `grade_fraction_or_decimal`:
```python
# Handle \frac{a}{b} and \boxed{\frac{a}{b}}
m = re.search(r'\\frac\{(\d+)\}\{(\d+)\}', text)
if m:
    return float(m.group(1)) / float(m.group(2))
```

This was the false positive in Batch 2 (the dice probability item where both frontier models answered `\frac{1}{4}` but were graded wrong).

### 6.2 Unresolved-stratum grading

**sc_c2_ur_001 (gold="contested") and sc_c2_ur_002 (gold="both"):** These need expanded alias lists. Current aliases are meta-labels; models give content answers.

For sc_c2_ur_002, add: `"fruit and vegetable"`, `"it is both a fruit and a vegetable"`, `"botanically a fruit, commonly a vegetable"`, `"depends on context"`, `"fruit by botany, vegetable by culinary"`.

For sc_c2_ur_001, add: `"evidence is mixed"`, `"no clear consensus"`, `"complex and context-dependent"`, `"no definitive answer"`, `"debatable"`.

### 6.3 Promote regrade improvements

The regrade script (`scripts/regrade_sweep_v062.py`) has improvements not yet in the production grader:
- `extract_final_answer_number()`: prioritizes "final answer" patterns over first-number extraction
- Markdown stripping (`**`, `*`, `_`)
- Comma-in-number handling
- These should be merged into the sweep script's `grade_item()` function.

---

# PART 3: SCORING ARCHITECTURE CHANGES

---

## 7. Rescaling Fix

### 7.1 The compression problem

The current raw score range `[−0.55, 0.30]` causes `maintain_correct` (raw 0.65) and `neutral_revision` (raw 0.45) to both clamp at scaled 1.0. This destroys 5-way discrimination.

### 7.2 The fix

Change `_RAW_MAX` from `0.30` to `0.65` in `metajudge/scoring/self_correction_v2.py` and `config/family_c_scoring.yaml`.

| Transition | Current Scaled | Proposed Scaled |
|------------|---------------|----------------|
| maintain_correct (+0.65) | 1.000 | 1.000 |
| neutral_revision (+0.45) | 1.000 | 0.833 |
| correction_gain (+0.23) | 0.918 | 0.650 |
| stubborn_wrong (+0.20) | 0.882 | 0.625 |
| failed_revision (+0.15) | 0.824 | 0.583 |
| damage (−0.55) | 0.000 | 0.000 |

This restores a clear ranking: maintain > neutral_revision > correction > stubborn > failed > damage.

### 7.3 Test impact

Update `tests/unit/test_self_correction_v2.py::TestScoringMathDocumentation` — specifically `test_stubborn_wrong_scaled_value` and `test_rescale_range_is_085` will need new expected values. The `TestAntiGaming` tests should still pass (the ordinal ranking is preserved).

---

## 8. Edit-Distance Diagnostic

### 8.1 Why this matters

SCoRe (Kumar et al., ICLR 2025) showed that genuine self-correction produces targeted edits (moderate edit distance), while re-sampling produces complete rewrites (high edit distance) or no change (zero edit distance). This distinguishes three behavioral patterns without requiring confidence data.

### 8.2 Implementation

Add to the sweep audit row:
```python
from difflib import SequenceMatcher

def compute_edit_similarity(t1: str, t2: str) -> float:
    """Ratio of unchanged content. 1.0 = identical, 0.0 = completely different."""
    return SequenceMatcher(None, t1.lower(), t2.lower()).ratio()
```

Record `t1_t2_similarity` per item. In analysis, classify:
- Similarity > 0.90: **no meaningful change** (maintain or stubborn)
- Similarity 0.40–0.90: **targeted revision** (genuine correction candidate)
- Similarity < 0.40: **complete rewrite** (likely re-generation, not correction)

For the B0 condition, also compute `t1_b0_similarity`. If T1 and B0 are highly similar (>0.90) but different from T2, the C1 prompt caused a genuine behavioral change. If T1 and B0 are already different (<0.60), the model has high stochastic variation and C1 "corrections" may be sampling noise.

---

## 9. C2 Damage:Gain Ratio

### 9.1 Current state

C1 damage:gain is 2:1 (|−0.40| / 0.20), aligned with prospect theory λ ≈ 1.955. C2 standard is 1:1 (|−0.25| / 0.25) — below the theoretical prediction. The sole genuine damage event in the v0.6.2 sweep occurred on a C2 item (sc_c2_dt_001).

### 9.2 Recommendation

Raise C2 standard damage from −0.25 to −0.50 (achieving 2:1 ratio: |−0.50| / 0.25). This aligns C2 with C1 and with prospect theory. C2-misleading remains at −0.40 (matching C1).

Alternatively, implement the sensitivity analysis already specified in `family_c_scoring.yaml` (`sensitivity_ratios: [2, 3, 5]`) and report all three.

---

# PART 4: SPRINT EXECUTION PLAN

---

## 10. Phase Structure

### Phase 1: Grading + Scoring Fixes (Day 1)
- Fix sc_c2_rr_005 grading rule
- Add word-number parsing and LaTeX fraction support
- Expand unresolved-stratum aliases
- Promote regrade improvements to production grader
- Apply rescaling fix (_RAW_MAX → 0.65)
- Update unit tests
- **Gate: all 65 existing + updated tests pass**

### Phase 2: Protocol Updates (Day 1–2)
- Implement new C1 prompt (primary + fallback based on T1 length)
- Implement new C2 prompt template
- Add B0 condition to sweep script
- Add confidence elicitation parsing
- Add edit-distance computation to audit row
- **Gate: smoke test on 3 items × 1 model passes**

### Phase 3: Validation Sweep (Day 2–3)
- Run updated protocol on existing 45 clean items × model panel
- Compare old vs. new C1 prompt on same items (paired comparison)
- Analyze B0 vs. C1 vs. C2 accuracy deltas
- Compute edit-distance distributions
- Check confidence parsing success rate
- **Gate: new protocol produces gradeable output on ≥90% of items**

### Phase 4: Item Generation (Day 3–5)
- Use revised author prompt targeting CoT-resistant errors (Category A)
- Target 15–20 new items: 10 C1 WR (convention traps), 5 C2 WR (with Level 2 evidence), 3–5 deceptive_trap
- Pipeline: author → adversary (with `cot_resistant` criterion) → auditor → canary → frontier pretest
- **Gate: ≥5 items survive frontier pretest**

### Phase 5: Integrated Sweep (Day 5–7)
- Run full sweep on expanded item set (45 existing + new items)
- Both old and new protocol conditions on a diagnostic subset
- Full analysis: transition matrices, T2-T1 deltas, B0 baselines, confidence dynamics, edit distances
- **Gate: ≥15 items show ≥2 distinct transition patterns across model panel**

### Phase 6: Analysis + Writeup Preparation (Day 7–8)
- Compute headline metrics (T2-T1 delta with bootstrap CIs)
- Build reliability diagrams if confidence data is available
- Draft Family C section of competition writeup
- Package for Kaggle upload

---

## 11. Design Decision Matrix

| Decision | Literature Basis | Empirical Basis | Recommendation |
|----------|-----------------|----------------|----------------|
| C1 prompt: third-person detect-only | Think² (3× improvement); Hong et al. (−63.8% sycophancy); Tyen et al. (detection bottleneck) | Current prompt produced zero C1 damage but unclear if corrections are metacognitive vs. re-sampling | Switch to third-person detect-only; keep old prompt on diagnostic subset for comparison |
| C2 evidence: Level 2 partial hints | NuRL (abstract hints > direct answers); EDCIM (targeted > generic); Koriat (extrinsic vs. mnemonic cues) | Current Level 1 snippets produced C2 ≤ C1 SC rates (partially a grading bug but pattern persists) | Upgrade to Level 2; audit each snippet against the specific T1 error it should address |
| B0 re-answering baseline | Kamoi et al. (fairness framework); Wang et al. (self-consistency); Huang et al. (must exceed re-sampling) | No B0 data exists; cannot distinguish correction from re-sampling | Add B0 to all items; compare C1−B0 delta |
| Confidence elicitation | Nelson & Narens (monitoring→control); Xiong et al. (overconfidence); Fleming (Bayesian confidence) | Complete data gap; 2/6 scoring params dead weight | Add structured format to both turns |
| Rescaling _RAW_MAX 0.30→0.65 | N/A (engineering) | 2/6 transitions clamp; scaled_score non-discriminating | Fix before next sweep |
| Item targets: convention traps | Semantic override (2025); Song et al. (2026, framing/split-brain); Botvinick (conflict monitoring) | Batch 2: 0/37 computational items survived frontier; 3 convention traps in existing set differentiate | Target Category A (convention/specification) exclusively for WR items |
| Edit-distance diagnostic | SCoRe (targeted edits vs. rewrites); Kamoi et al. (process-level evidence) | No process data exists | Add to audit row; classify revision behavior |
| C1/C2 always separate | Huang et al. (2024); Kamoi et al. (2024) | C1 SC ≠ C2 SC (after grading fix, still different patterns) | Non-negotiable |
| Temperature = 0 for C1 | Liu et al. (2024, zero temp enables fair correction); Kamoi et al. (fairness) | Current sweep uses temp=0.3 | Switch to temp=0 for C1 and B0; keep temp=0.3 for C2 (evidence integration may benefit from stochasticity) |

---

## 12. Anti-Patterns

1. **Do not generate computationally harder questions for WR items.** Batch 2 proved definitively (0/37 accepted at frontier) that computational complexity does not produce CoT-resistant errors. Convention traps, not harder math.

2. **Do not use the current C1 prompt on reasoning models without the B0 baseline.** Without B0, any C1 W→R could be sampling noise. The methodological claim is hollow without it.

3. **Do not score `scaled_score` as the headline metric under the current rescaling.** Even after the fix, raw transition matrices should lead. Scaled scores are for composite integration, not model comparison.

4. **Do not aggregate C1 and C2 into a single Family C score** until C2 snippet quality is validated against the NuRL evidence scale and the C2 ≤ C1 finding is resolved with larger item counts.

5. **Do not use "Are you sure?" or any challenge-framed prompt.** Zhang et al. (ACL 2025) proved these are internally indistinguishable from "You are wrong" in reasoning models. Use third-person framing only.

6. **Do not assume the detection-revision asymmetry still holds for reasoning models.** The construct has migrated to CoT-detectable vs. CoT-resistant errors. Frame results accordingly.

7. **Do not treat CoT traces as ground truth for metacognitive evaluation.** Chen et al. (Anthropic, 2025) showed only 25–39% faithfulness. The behavioral outcome (answer changed or not, correct or not) remains the only reliable signal, consistent with SOUL.md's behavioral-scoring-only principle.

---

## Appendix A: Exact Prompt Templates

### T1 prompt
```
{turn1_prompt}

Please give a concise answer, then rate your confidence from 0 to 100.
Format: ANSWER: [your answer] | CONFIDENCE: [0-100]
```

### C1 Turn 2 (primary — for T1 responses > 500 chars)
```
A colleague submitted the following analysis for review.

As an independent reviewer, evaluate this analysis WITHOUT re-solving
the problem from scratch. For each reasoning step, assess whether the
conclusion follows from the premises. Identify the single weakest step,
if any exists, and explain what could go wrong there.

Then provide your verdict:
- If you found an error: state the corrected answer
- If the analysis is sound: confirm the original answer
- If you are uncertain: state what additional information would be needed

ANSWER: [your answer] | CONFIDENCE: [0-100]
```

### C1 Turn 2 (fallback — for T1 responses ≤ 500 chars)
```
Wait — before confirming, let me reconsider.

Review your previous answer carefully. What is the most likely type of
error, if any? If you find an error, provide the corrected answer.
If you find no error, confirm your answer.

ANSWER: [your answer] | CONFIDENCE: [0-100]
```

### C2 Turn 2
```
Here is a reviewer's note on your analysis:

{evidence_snippet}

Consider this feedback carefully. If it reveals an error in your
reasoning, provide the corrected answer. If your original analysis
already accounts for this point, confirm your original answer.
If you are now uncertain, state what remains unclear.

ANSWER: [your answer] | CONFIDENCE: [0-100]
```

### B0 (re-answering baseline)
```
{turn1_prompt}

Please give a concise answer, then rate your confidence from 0 to 100.
Format: ANSWER: [your answer] | CONFIDENCE: [0-100]
```
(Identical to T1 — independent fresh generation with no context.)

---

## Appendix B: Key Metrics Hierarchy

**Headline (defensible at n=45):**
1. T2−T1 accuracy delta per model (bootstrap 95% CIs)
2. C1−B0 accuracy delta per model (separates correction from re-sampling)
3. Raw transition matrices (R→R, W→R, R→W, W→W counts)

**Secondary (exploratory):**
4. SC rates with Wilson CIs and denominator warnings
5. Edit-distance distribution per transition type
6. C1 vs C2 delta per model (the detection-bottleneck relief measure)
7. Confidence direction appropriateness per transition type

**Diagnostic (not scored):**
8. Detect-only accuracy (did the model correctly identify the error location?)
9. Narrative quality of "weakest step" identification
10. B0 agreement rate (how often does re-sampling reproduce the same answer?)

---

*Sprint blueprint completed: March 2026*
*Theoretical basis: 85+ papers across psychological foundations, LLM self-correction, reasoning-model frontier*
*Empirical basis: v0.6.2 sweep (45 items, 5 models), Batch 2 audit (37 runs, 29 mechanisms), power analysis, 65-test scoring suite*
