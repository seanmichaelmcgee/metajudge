# Risk Assessment — V4 Adversarial Calibration Items

**Version:** 4.0  
**Date:** March 19, 2026  
**Purpose:** Identify, rank, and mitigate risks to the V4 adversarial calibration item sprint.  
**Audience:** Project lead and orchestration team.

---

## Table of Contents

1. [Overall Yield Risk](#1-overall-yield-risk)
2. [Mechanism Categories Ranked by Expected Yield](#2-mechanism-categories-ranked-by-expected-yield)
3. [Minimum Viable Set for Success Criteria](#3-minimum-viable-set-for-success-criteria)
4. [Code Items: Model Capability Risk](#4-code-items-model-capability-risk)
5. [Temporal Items: Mid-Sprint Contamination Risk](#5-temporal-items-mid-sprint-contamination-risk)
6. [Brier Spread Cancellation Risk](#6-brier-spread-cancellation-risk)
7. [Yield Floor Contingency](#7-yield-floor-contingency)
8. [ECE Bin Coverage Risk](#8-ece-bin-coverage-risk)
9. [Refusal Cascade Risk](#9-refusal-cascade-risk)
10. [Additional Risks](#10-additional-risks)
11. [Risk Priority Matrix](#11-risk-priority-matrix)

---

## 1. Overall Yield Risk

### Risk: Overall yield falls below 50%

**Probability:** MEDIUM-HIGH (40–55%). V1 had a 3.3% yield (1/30). Even with the V4 adversarial search reframing, frontier models are very capable. Literature base rates suggest 30–50% yield for adversarial item generation against frontier models.

**Impact:** HIGH. Below 50% yield means fewer than 15 items survive to Kaggle notebook verification. This is the minimum to calibrate the pipeline for the next cycle.

### Fallback approaches (ordered by priority):

**Fallback 1: Double down on highest-yield mechanisms (trigger: yield 30–50%)**
- Reallocate ALL generation budget to the top 2–3 mechanisms by observed yield
- Expected: Code execution and Modified CRT will have highest yields
- Generate 40–50 additional items in high-yield categories only
- Cost: One additional Opus generation run (~$2–3)

**Fallback 2: Increase candidate pool (trigger: yield 20–30%)**
- Increase total generation from 80–90 to 140–160 items
- Split across 3 Opus runs (restore Agent C, or split Agent A into A1/A2)
- More candidates at same yield rate = more survivors
- Cost: ~$5–8 additional generation, ~$10 additional Phase 3 testing
- Timeline risk: adds 1–2 days

**Fallback 3: Relax Tier 6 threshold (trigger: yield 15–25%)**
- Change soft-reject threshold from confidence ≥ 0.85 to ≥ 0.92
- This keeps more "borderline" items that weaker models may still miss
- Risk: reduces discrimination power of surviving items
- Should be combined with Fallback 1

**Fallback 4: Hybrid approach — use existing rejection log (trigger: yield < 15%)**
- V2 expansion sprint produced 123 rejected candidates (`data/harvest/v2_rejection_log.json`)
- Re-test these against the 5-model panel (they were only tested against Flash)
- Some may discriminate between models even if Flash answered correctly
- Cost: ~$3–5 for API testing
- Expected yield: low (5–10%), but it's a cheap supplement

**Fallback 5: Accept fewer than 30 replacements (trigger: yield < 10%)**
- Replace only the items that are clearly ceiling items (easy/medium, 100% accuracy, high confidence)
- A partial improvement (replacing 15–20 items instead of 30) still improves the dataset
- Recalibrate success criteria accordingly
- This is the worst case — it means the pipeline needs fundamental rethinking for the next sprint

---

## 2. Mechanism Categories Ranked by Expected Yield

Based on literature review, V1 results, and the structure of each mechanism:

| Rank | Mechanism | Expected Yield | Confidence in Estimate | Rationale |
|------|-----------|---------------|----------------------|-----------|
| 1 | **Code Execution** | 50–65% | HIGH | CRUXEval data shows GPT-4 at 75% on code prediction; our items target less-discussed edge cases. Zero contamination. Provably correct gold answers. |
| 2 | **Modified CRT** | 40–55% | MEDIUM | Literature shows 50% accuracy drops on structural modifications. Risk: models may detect "trick question" framing. |
| 3 | **Conditional Temporal** | 40–55% | MEDIUM | Novel mechanism — no published benchmarks test this. Models can't refuse (context provided). Risk: small sample size (3–5 items). |
| 4 | **Compositional** | 30–45% | MEDIUM | Multi-hop failures documented at 7.6–32.2% cascade. Risk: models may retrieve composed facts if the specific comparison is in training data. |
| 5 | **Anchoring** | 25–40% | MEDIUM-LOW | Larger RLHF models are more susceptible. Risk: models may have precise values for common constants. |
| 6 | **IOED** | 20–35% | LOW | Principle exceptions are popular "did you know" content. Risk: most IOED items will be in training data as corrections. |
| 7 | **Prototype Interference** | 15–30% | LOW | "The real answer is..." corrections are proliferating in training data. Models are getting better at non-prototypical retrieval. |
| 8 | **RLHF Overconfidence** | 10–20% | LOW | The mechanism is real, but designing items that EXPLOIT it (vs just demonstrating it) is very hard. Models' parametric memory is stronger than expected. |
| 9 | **Ambiguity-as-Metacognition** | 5–15% | LOW | Frontier models are surprisingly good at recognizing contested claims. May need to be eliminated entirely. |

### Recommended allocation adjustment based on risk:

If first-batch yields confirm the ranking above:
- **Increase:** Code Execution (+5 items), Modified CRT (+3 items), Conditional Temporal (+2 items)
- **Hold:** Compositional, Anchoring
- **Decrease:** IOED (−3 items), Prototype (−3 items), RLHF (−4 items)
- **Eliminate:** Ambiguity-as-Metacognition (reallocate to Code Execution)

---

## 3. Minimum Viable Set for Success Criteria

The 5 success criteria require ≥4/5 to pass. Here is the minimum item composition to meet each:

### C1: Brier spread ≥ 0.05

**Requirement:** At least 1 model's Brier headline score must be ≥0.05 below the best model's score.
**Minimum items needed:** 8–12 items where at least 2 models are confidently wrong and at least 1 model is correct.
**Most likely to provide:** Code execution items (model capability varies), compositional items (multi-hop failure rates vary by model).
**Risk:** If all 5 models fail/succeed on the same items, spread stays low. Mitigation: include items targeting specific model weaknesses (DeepSeek on code, Haiku on compositional).

### C2: Deceptive bucket accuracy < 80% on ≥ 3 models

**Requirement:** The "deceptive" difficulty bucket must fool at least 3 models on at least 20% of items.
**Minimum items needed:** 8–10 deceptive items where 3+ models are wrong.
**Most likely to provide:** Code items with intuitive-but-wrong answers, modified CRT items.
**Risk:** If deceptive items are too hard (all models wrong), they become "floor" items, not discriminators. Need the RIGHT level of difficulty.

### C3: Adversarial bucket accuracy < 70% on ≥ 3 models

**Requirement:** The "adversarial" difficulty bucket must fool at least 3 models on at least 30% of items.
**Minimum items needed:** 6–8 adversarial items with ≥ 30% wrong across 3+ models.
**Most likely to provide:** Prototype interference items, anchoring items, RLHF items.
**Risk:** Hardest criterion to meet. Adversarial items that fool 3+ models at 30%+ are rare. Mitigation: include items that produce SPLIT results (2 models right, 3 wrong).

### C4: ≥ 10 items with conf–acc gap > 0.20

**Requirement:** At least 10 items where some model's confidence exceeds accuracy by > 0.20.
**Note:** This criterion is ALREADY MET in the current dataset (only criterion passing). New items should maintain or improve this.
**Minimum items needed:** 5–8 new items contributing to the count (existing items cover the rest).
**Most likely to provide:** ANY item where a model is confidently wrong.

### C5: ECE range ≥ 0.03

**Requirement:** The Expected Calibration Error must vary by ≥ 0.03 across models.
**Minimum items needed:** Sufficient items to populate ≥6 confidence bins with ≥2 data points each.
**Most likely to provide:** Mix of easy (high confidence, correct) and hard (medium confidence) items.
**Risk:** See §8 — ECE bin coverage is a real concern.

### Minimum Viable Set (MVP)

To hit ≥ 4/5 criteria with the least risk:

| Item Type | Count | Primary Criterion Served |
|-----------|-------|-------------------------|
| Code execution (deceptive) | 8 | C1, C2, C4 |
| Modified CRT (deceptive) | 5 | C2, C4 |
| Compositional (adversarial) | 4 | C1, C3 |
| Conditional temporal (hard) | 3 | C1, C5 |
| Anchoring (adversarial) | 3 | C3, C4 |
| IOED (hard) | 3 | C5 |
| Prototype (adversarial) | 2 | C3 |
| Buffer/contingency | 2 | Any |
| **Total** | **30** | |

This set prioritizes C1 (Brier spread) and C2 (deceptive difficulty) as the most achievable, with C3 (adversarial difficulty) as the stretch goal. C4 is already met. C5 depends on ECE bin coverage.

---

## 4. Code Items: Model Capability Risk

### Risk: Models are better at code simulation than literature suggests

**Probability:** MEDIUM (30–40%). CRUXEval and related papers are 1–2 years old. GPT-4's 75% on code prediction may have improved to 85–90% in current frontier models.

**Evidence for the risk:**
- Claude Sonnet 4 and Gemini 2.5 Pro both have strong code capabilities
- RLHF training on coding tasks has intensified since CRUXEval
- Python edge cases like banker's rounding are increasingly discussed in training data

**Evidence against the risk:**
- CRUXEval tests were relatively simple (3–13 lines); our items target LESS COMMON edge cases
- Models predict code output by reasoning, not executing — this fundamental limitation hasn't changed
- The specific edge cases targeted (walrus scope leak, dict.fromkeys aliasing) are less popular than mutable defaults

**Mitigation strategies:**

1. **Combine edge cases:** Instead of one gotcha per snippet, combine 2. E.g., banker's rounding inside a list comprehension with zip truncation. Models must track BOTH simultaneously.

2. **Increase code complexity to 10–15 lines:** Longer snippets with more state to track. But stay under 15 lines to avoid parsing failures.

3. **Test against ALL 5 models in Tier 1:** Don't just test against Flash. Code capability varies significantly: DeepSeek may be weakest on non-standard Python behaviors.

4. **Prepare a "hard code" reserve:** Author 5–8 extra-tricky code items (combining 3 edge cases each) as reserves if the main set is too easy.

### Worst case: Code items yield only 20–30%

If this happens, code items are still the highest-yield mechanism. Increase volume: generate 30 code items instead of 18, accept that 6–9 will survive. Combine with Modified CRT (also computation-heavy) to fill the gap.

---

## 5. Temporal Items: Mid-Sprint Contamination Risk

### Risk: Model updates during the sprint invalidate temporal items

**Probability:** LOW (10–15%) for the 2-week sprint window. Model updates are typically monthly.

**Impact:** LOW-MEDIUM. Only 3–5 temporal items are planned. Losing all of them reduces the batch by 3–5 items but doesn't break the pipeline.

**The real temporal risk: Conditional temporal items don't actually require post-cutoff knowledge.**

Our V4 approach reframes temporal items as "conditional reasoning on given context." The model receives all necessary information in the prompt. This means:
- Model updates don't invalidate the items (the context is self-contained)
- The risk is NOT contamination — it's that models can reason correctly on provided context
- The actual risk is that conditional temporal items behave like computation items (which is fine — they just merge into that category)

**Residual risk: 0–2 pure post-cutoff recall items**

If included (the directive says 0–2), these are fragile. Mitigation:
- Flag with `"time_sensitive": true` in metadata
- Include source URLs for re-verification
- Accept that these may be invalidated and have backup items ready

### Mitigation:

- Tag ALL temporal items with `"time_sensitive": true`
- For conditional items: ensure gold answer depends ONLY on provided context
- For pure recall items (if any): verify gold answer immediately before Kaggle notebook integration
- Have 2 non-temporal backup items ready to swap in

---

## 6. Brier Spread Cancellation Risk

### Risk: High per-item Brier spread cancels out across the dataset

**Probability:** MEDIUM (25–35%). This is a real statistical concern.

**How it happens:** Item A produces Brier spread of 0.30 (Model X scores 0.10, Model Y scores 0.40). Item B produces the SAME spread but in the OPPOSITE direction (Model X scores 0.40, Model Y scores 0.10). Across both items, Model X and Y have the same mean Brier score — zero spread at the dataset level.

**This is the most subtle risk in the entire design.**

**Detection:** After Phase 3, compute the MODEL-LEVEL Brier spread, not just the per-item spread. If:
- Per-item spread mean > 0.10 but model-level spread < 0.05 → cancellation is occurring

**Mitigation strategies:**

1. **Directional consistency:** Ensure items consistently favor the SAME model ordering. If Pro and Sonnet tend to outperform Flash and Haiku on code items, and also outperform on compositional items, the spread is additive, not cancelling.

2. **Track model rankings per item:** For each surviving item, record which models rank 1st through 5th. If the rankings are consistent across items → low cancellation risk. If rankings are random → high cancellation risk.

3. **Weighted item selection:** In Phase 4 (final selection), prefer items where the WEAKER models (Flash, Haiku, DeepSeek) are confidently wrong and the STRONGER models (Pro, Sonnet) are correct or uncertain. This ensures spread accumulates in one direction.

4. **Floor items help:** 2–3 items where ALL models are confidently wrong contribute to aggregate overconfidence measurement and push the weakest model's score further from perfect.

### Monte Carlo estimation:

Before finalizing the 30-item batch, simulate the expected dataset-level Brier spread:

```python
import numpy as np

def estimate_dataset_spread(item_brier_matrices):
    """Estimate dataset-level Brier spread from per-item model scores.
    
    item_brier_matrices: list of dicts, each {model_name: brier_score}
    """
    models = list(item_brier_matrices[0].keys())
    model_means = {}
    for model in models:
        scores = [item[model] for item in item_brier_matrices]
        model_means[model] = np.mean(scores)
    
    spread = max(model_means.values()) - min(model_means.values())
    return spread, model_means
```

If estimated spread < 0.06, reconsider item selection before proceeding to Kaggle verification.

---

## 7. Yield Floor Contingency

### Trigger: Overall yield falls below 30%

**This is the emergency protocol.** If fewer than 25 items out of 80–90 candidates survive Phase 3:

**Immediate action: Double down on code execution exclusively.**

Rationale:
- Code execution has the highest expected yield (50–65%)
- Zero contamination risk
- Provably correct gold answers
- The space of Python edge cases is very large — we can generate many more novel items
- Code items have the best Brier spread potential (model capability varies significantly on code)

**Emergency generation plan:**
1. Author 40 additional code items (Agent A only)
2. Combine 2 edge cases per snippet (higher difficulty)
3. Target 10–15 line snippets (more state to track)
4. Run through abbreviated pipeline: execution verification → Tier 1 testing only
5. Expected yield on code-only batch: 50–65% → 20–26 survivors
6. Combined with initial batch survivors: should reach 30+

**Cost:** ~$3 generation, ~$5 testing = $8 total. Within budget.

**Timeline:** 1–2 additional days. Still within April 16 deadline.

**Tradeoff:** The final dataset would be heavily skewed toward code simulation items. This reduces mechanism diversity but maximizes discrimination power. For the first pipeline calibration batch, this is acceptable — diversity can be improved in the next sprint.

---

## 8. ECE Bin Coverage Risk

### Risk: Model confidence clusters in 1–2 bins, preventing meaningful ECE computation

**Probability:** HIGH (50–60%). Frontier models are known to be systematically overconfident. Confidence scores cluster in the 0.80–1.00 range.

**Impact:** MEDIUM. ECE range (C5) is one of 5 success criteria. If bins are underpopulated, ECE is unreliable as a metric, but Brier score (the primary metric) is unaffected.

**Current situation:** The existing 70 "keeper" items are mostly easy/medium with high accuracy. Models answer these with confidence 0.85–1.00. This means the existing dataset populates only bins 8–10 (0.80–1.00).

**What the new 30 items must do:** Populate bins 1–7 (0.00–0.70). This requires items that make models UNCERTAIN, not just wrong.

**The tension:** We want items that produce CONFIDENT wrong answers (high Brier loss) AND items that produce UNCERTAIN responses (bin coverage). These are somewhat contradictory goals.

**Mitigation strategies:**

1. **Include 3–5 "hard class" items** that are genuinely difficult but answerable. Models will respond with confidence 0.40–0.70. These contribute to bin coverage without being deceptive/adversarial.

2. **Conditional temporal items** naturally produce medium confidence (models are uncertain about reasoning on novel context).

3. **Report Brier as primary, ECE as diagnostic.** If ECE bin coverage is insufficient, acknowledge it in the writeup: "ECE is reported with the caveat that bin coverage is limited to X bins; Brier score remains the primary metric."

4. **Include a reliability diagram as the primary visual** instead of a calibration table. Reliability diagrams are interpretable even with sparse bins.

5. **Accept C5 as the most likely criterion to fail.** Plan for 4/5 success criteria with C5 as the miss. The other 4 criteria are more actionable.

---

## 9. Refusal Cascade Risk

### Risk: Models strategically refuse difficult items, producing Brier = 0.00 and zero discrimination

**Probability:** LOW-MEDIUM (15–25%). Most frontier models are trained to attempt answers. But some models (particularly Claude) may refuse on items perceived as unanswerable or adversarial.

**Impact:** MEDIUM. If 5+ items produce 4+/5 refusals, those items are dead weight. Worse: if one model systematically refuses more than others, it artificially lowers its Brier score (refusal = 0.00 = "good calibration"), rewarding avoidance over genuine metacognition.

**Detection:** Track `refusal_rate_by_model` in pipeline calibration data. If any model's refusal rate > 10% → investigate.

**Mitigation strategies:**

1. **Design items that don't invite refusal.** The V4 directive already addresses this — provide all necessary context, avoid "trick question" signals, make questions read as genuine factual queries.

2. **Monitor the prompt.** The benchmark prompt says "Provide your best answer" — this should discourage refusal. If a model still refuses, it's a model behavior issue, not an item design issue.

3. **Report refusal rate alongside Brier score.** In the writeup: "Model X had a refusal rate of Y%, which artificially lowers its Brier score. The 'effective Brier score' excluding refused items is Z."

4. **Flag avoidant behavior:** If a model's Brier score is low AND its refusal rate is high, flag it as "low-Brier + high-refusal = avoidant, not calibrated."

5. **Reject items with universal refusal:** Any item with ≥4/5 refusals in Phase 3 is dropped. This is already in the verification protocol.

---

## 10. Additional Risks

### 10.1 Generator Prompt Quality Risk

**Risk:** The generator prompts (Deliverable 1) produce low-quality or off-target items.
**Probability:** MEDIUM (25–35%).
**Mitigation:** The worked examples in the prompts serve as calibration anchors. If first-batch quality is poor, revise the examples (per feedback loop spec) before generating batch 2.

### 10.2 Schema Compliance Risk

**Risk:** Generator agents produce items with missing or malformed fields.
**Probability:** LOW (10–15%). Opus 4.6 is reliable at following structured output requirements.
**Mitigation:** The orchestrator validates schema before Phase 2. Items with missing fields are rejected immediately.

### 10.3 Budget Overrun Risk

**Risk:** Phase 3 API testing exceeds the $10–20 budget.
**Probability:** LOW (10–15%). Tier 1 uses Flash (free) + Haiku (~$0.50/60 items). Tier 2 uses Pro + Sonnet (~$5–8/50 items). Tier 3 uses Opus (~$3–5/25 items). Total: ~$9–14.
**Mitigation:** Track spending after each tier. If approaching $20, reduce Tier 3 volume.

### 10.4 Kaggle Notebook Integration Risk

**Risk:** Items that pass API testing fail in the Kaggle notebook environment.
**Probability:** LOW-MEDIUM (15–25%). The Kaggle notebook uses the same prompt and models, but the SDK may handle response parsing differently.
**Mitigation:** Run the first 5 surviving items through the actual Kaggle notebook before committing all 30. This catches parsing issues early.

### 10.5 April 16 Deadline Risk

**Risk:** The pipeline takes longer than expected, leaving insufficient time for the sweep + writeup.
**Probability:** MEDIUM (25–30%). The pipeline has 4 phases plus Kaggle verification.
**Mitigation:** Strict timebox per phase:
  - Phase 1 (generation): 1 day
  - Phase 2 (verification): 1 day
  - Phase 3 (API testing): 2 days
  - Phase 4 (selection + integration): 1 day
  - Kaggle sweep + writeup: 3–5 days
  - Buffer: 2–3 days
  Total: ~10–12 days. With kickoff on March 19 and deadline April 16, we have 28 days. Comfortable even with one full pipeline iteration + revision.

### 10.6 Answer Key Ambiguity Risk

**Risk:** Gold answers are defensibly wrong — a model gives a correct answer that isn't in the aliases list.
**Probability:** MEDIUM (20–30%). This is the most insidious risk for factual and numerical items.
**Mitigation:**
- Verifier agent must generate comprehensive alias lists
- For numerical items: include integer, float, and word forms
- For factual items: include all common spellings, abbreviations, and alternate names
- Run a "reverse stress test": have an agent try to find alternative correct answers to each question

---

## 11. Risk Priority Matrix

| # | Risk | Probability | Impact | Priority | Primary Mitigation |
|---|------|------------|--------|----------|-------------------|
| 1 | Overall yield < 50% | MEDIUM-HIGH | HIGH | **CRITICAL** | Fallback cascade (§1) |
| 2 | Brier spread cancellation | MEDIUM | HIGH | **HIGH** | Directional consistency check (§6) |
| 3 | ECE bin coverage | HIGH | MEDIUM | **HIGH** | Hard-class items + Brier as primary metric (§8) |
| 4 | Code model capability | MEDIUM | MEDIUM | **MEDIUM** | Combined edge cases + reserve items (§4) |
| 5 | Answer key ambiguity | MEDIUM | MEDIUM | **MEDIUM** | Comprehensive aliases + reverse stress test (§10.6) |
| 6 | Deadline pressure | MEDIUM | MEDIUM | **MEDIUM** | Strict phase timeboxes (§10.5) |
| 7 | Refusal cascade | LOW-MEDIUM | MEDIUM | **MEDIUM** | Item design guidelines + reporting (§9) |
| 8 | Generator prompt quality | MEDIUM | LOW-MEDIUM | **LOW** | Feedback loop revision (§10.1) |
| 9 | Temporal contamination | LOW | LOW-MEDIUM | **LOW** | time_sensitive tagging (§5) |
| 10 | Budget overrun | LOW | LOW | **LOW** | Per-tier spending tracking (§10.3) |

### Decision: Which 4/5 success criteria to target?

Based on risk analysis, the most achievable combination is:

**Target: C1 + C2 + C4 + C5** (Brier spread + deceptive difficulty + conf-acc gap + ECE range)

- C1 (Brier spread): Achievable with 8–12 discriminating items
- C2 (Deceptive < 80%): Achievable with code + CRT items
- C4 (Conf-acc gap): Already met; new items maintain it
- C5 (ECE range): Achievable with hard-class items + diverse confidence levels

**Stretch target: C3** (Adversarial < 70% on 3+ models). This is the hardest criterion because it requires items that fool 3+ frontier models at a 30% rate. If we achieve this, we'll have 5/5.

**Backup if C5 fails:** C3 becomes the target. Report ECE as diagnostic-only in the writeup.

---

*End of Deliverable 4. This risk assessment covers all identified risks with concrete mitigations. The orchestration team should review the Risk Priority Matrix and plan contingency actions for CRITICAL and HIGH priority risks before starting Phase 1.*
