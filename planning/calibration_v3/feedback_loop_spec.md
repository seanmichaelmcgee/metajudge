# Feedback Loop Specification — V4 Adversarial Calibration Items

**Version:** 4.0  
**Date:** March 19, 2026  
**Purpose:** Enable iterative improvement of the generator pipeline without returning to the research team. Specifies how Phase 3 data feeds back into generator prompt revisions.  
**Audience:** Orchestration team and feedback loop agent (Claude Opus 4.6).

---

## Table of Contents

1. [Pipeline Calibration Data Schema](#1-pipeline-calibration-data-schema)
2. [Structural Feature Analysis Protocol](#2-structural-feature-analysis-protocol)
3. [Generator Prompt Revision Protocol](#3-generator-prompt-revision-protocol)
4. [Yield Forecasting](#4-yield-forecasting)
5. [Failure Analysis Questions](#5-failure-analysis-questions)

---

## 1. Pipeline Calibration Data Schema

After Phase 3 (live API testing), the results analyzer MUST produce this structured JSON. This is the core artifact enabling iterative improvement.

### 1.1 Full Schema

```json
{
  "pipeline_calibration": {
    "meta": {
      "batch_id": "v4_batch_001",
      "date": "2026-03-XX",
      "total_candidates_generated": 85,
      "total_phase2_survivors": 55,
      "total_phase3_tested": 55,
      "total_phase3_survivors": 30,
      "overall_yield": 0.353,
      "phase2_yield": 0.647,
      "phase3_yield": 0.545
    },

    "survival_rate_by_mechanism": {
      "code_execution": {
        "generated": 18,
        "phase2_survivors": 15,
        "phase3_survivors": 10,
        "overall_yield": 0.556,
        "phase2_yield": 0.833,
        "phase3_yield": 0.667,
        "dominant_failure_mode": "model_correct_high_confidence",
        "notes": "Banker's rounding items had highest survival; generator exhaustion items rejected at phase2 (gold answers were wrong)"
      },
      "compositional": {
        "generated": 12,
        "phase2_survivors": 9,
        "phase3_survivors": 5,
        "overall_yield": 0.417,
        "phase2_yield": 0.750,
        "phase3_yield": 0.556,
        "dominant_failure_mode": "models_retrieved_both_facts_correctly",
        "notes": "Area comparisons worked best; speed comparisons were too easy"
      },
      "modified_crt": {
        "generated": 15,
        "phase2_survivors": 12,
        "phase3_survivors": 7,
        "overall_yield": 0.467,
        "phase2_yield": 0.800,
        "phase3_yield": 0.583,
        "dominant_failure_mode": "models_solved_from_scratch_instead_of_pattern_matching",
        "notes": "Items with deeper structural changes survived; surface-level modifications did not"
      },
      "ioed": {
        "generated": 7,
        "phase2_survivors": 5,
        "phase3_survivors": 2,
        "overall_yield": 0.286,
        "phase2_yield": 0.714,
        "phase3_yield": 0.400,
        "dominant_failure_mode": "models_know_the_principle_exception",
        "notes": "Most IOED items are in training data as 'did you know' facts"
      },
      "prototype": {
        "generated": 11,
        "phase2_survivors": 8,
        "phase3_survivors": 3,
        "overall_yield": 0.273,
        "phase2_yield": 0.727,
        "phase3_yield": 0.375,
        "dominant_failure_mode": "model_correct_medium_confidence",
        "notes": "Models know many 'the real answer is...' corrections already"
      },
      "anchoring": {
        "generated": 5,
        "phase2_survivors": 4,
        "phase3_survivors": 2,
        "overall_yield": 0.400,
        "phase2_yield": 0.800,
        "phase3_yield": 0.500,
        "dominant_failure_mode": "model_gives_correct_precise_value",
        "notes": "Items requiring 4+ digit precision fared better"
      },
      "rlhf_overconfidence": {
        "generated": 9,
        "phase2_survivors": 6,
        "phase3_survivors": 1,
        "overall_yield": 0.111,
        "phase2_yield": 0.667,
        "phase3_yield": 0.167,
        "dominant_failure_mode": "models_answered_correctly_with_appropriate_confidence",
        "notes": "RLHF items are extremely difficult to design — models' parametric memory is better than expected"
      },
      "conditional_temporal": {
        "generated": 4,
        "phase2_survivors": 3,
        "phase3_survivors": 2,
        "overall_yield": 0.500,
        "phase2_yield": 0.750,
        "phase3_yield": 0.667,
        "dominant_failure_mode": "none_dominant",
        "notes": "Conditional reasoning items with multi-step computation worked well"
      },
      "ambiguity_metacognition": {
        "generated": 4,
        "phase2_survivors": 3,
        "phase3_survivors": 0,
        "overall_yield": 0.000,
        "phase2_yield": 0.750,
        "phase3_yield": 0.000,
        "dominant_failure_mode": "models_correctly_identified_contested",
        "notes": "Models are good at recognizing ambiguity — this mechanism may not work"
      }
    },

    "survival_rate_by_structural_feature": {
      "requires_computation": {
        "generated": 45,
        "survivors": 22,
        "yield": 0.489,
        "notes": "Multi-step computation (3+ steps) survived at 0.62; single-step at 0.31"
      },
      "requires_recall": {
        "generated": 30,
        "survivors": 6,
        "yield": 0.200,
        "notes": "Pure recall items have worst survival — consistent with V1 findings"
      },
      "requires_code_simulation": {
        "generated": 18,
        "survivors": 10,
        "yield": 0.556,
        "notes": "Highest structural feature yield — confirms code execution as primary asymmetry"
      },
      "requires_multi_fact_integration": {
        "generated": 15,
        "survivors": 6,
        "yield": 0.400,
        "notes": "3-fact items survived at 0.57; 2-fact items at 0.29"
      },
      "requires_precise_boundary_knowledge": {
        "generated": 12,
        "survivors": 4,
        "yield": 0.333,
        "notes": "4+ digit precision items survived better than 2-3 digit"
      }
    },

    "model_discrimination_matrix": {
      "example_item_p3_001": {
        "flash_brier": 0.0975,
        "pro_brier": 0.9025,
        "sonnet_brier": 0.0400,
        "haiku_brier": 0.0625,
        "deepseek_brier": 0.0100,
        "brier_spread": 0.8925,
        "best_model": "pro",
        "worst_model": "flash"
      }
    },

    "confidence_distribution_by_model": {
      "flash": {"mean": 0.87, "std": 0.12, "median": 0.90, "pct_above_90": 0.65},
      "pro": {"mean": 0.82, "std": 0.15, "median": 0.85, "pct_above_90": 0.48},
      "sonnet": {"mean": 0.85, "std": 0.13, "median": 0.88, "pct_above_90": 0.55},
      "haiku": {"mean": 0.88, "std": 0.11, "median": 0.92, "pct_above_90": 0.70},
      "deepseek": {"mean": 0.83, "std": 0.14, "median": 0.87, "pct_above_90": 0.52}
    },

    "brier_spread_analysis": {
      "target": 0.08,
      "achieved": null,
      "per_item_spreads": {
        "mean": null,
        "median": null,
        "max": null,
        "min": null,
        "pct_above_005": null
      }
    },

    "ece_bin_coverage": {
      "bins": [
        {"range": "[0.0, 0.1)", "item_count": null, "models_with_data": null},
        {"range": "[0.1, 0.2)", "item_count": null, "models_with_data": null},
        {"range": "[0.2, 0.3)", "item_count": null, "models_with_data": null},
        {"range": "[0.3, 0.4)", "item_count": null, "models_with_data": null},
        {"range": "[0.4, 0.5)", "item_count": null, "models_with_data": null},
        {"range": "[0.5, 0.6)", "item_count": null, "models_with_data": null},
        {"range": "[0.6, 0.7)", "item_count": null, "models_with_data": null},
        {"range": "[0.7, 0.8)", "item_count": null, "models_with_data": null},
        {"range": "[0.8, 0.9)", "item_count": null, "models_with_data": null},
        {"range": "[0.9, 1.0]", "item_count": null, "models_with_data": null}
      ],
      "populated_bins": null,
      "target_populated_bins": 6
    },

    "refusal_analysis": {
      "total_refusals": null,
      "refusal_rate_by_model": {
        "flash": null, "pro": null, "sonnet": null, "haiku": null, "deepseek": null
      },
      "items_with_universal_refusal": [],
      "items_with_majority_refusal": []
    }
  }
}
```

### 1.2 Required Fields vs Template Fields

The schema above includes template values (null) that MUST be filled in after Phase 3 testing. The `survival_rate_by_mechanism` section includes example narrative values that should be replaced with actual observations. The structure itself is fixed — do not add or remove top-level keys.

---

## 2. Structural Feature Analysis Protocol

### 2.1 Why Features, Not Just Mechanisms

V1 failed because all items shared the same structural feature: `requires_recall`. The mechanism labels (person attribution, cultural origin) were diverse, but the underlying cognitive demand was identical. Clustering survivors by structural feature reveals the TRUE predictors of survival.

### 2.2 Analysis Procedure

After Phase 3, compute the following:

**Step 1: Feature Survival Matrix**

Build a table: rows = structural features, columns = survival/rejection counts.

```
Feature                          | Generated | Survived | Yield  | Δ from mean
---------------------------------|-----------|----------|--------|------------
requires_computation             |    45     |    22    | 0.489  | +0.137
requires_recall                  |    30     |     6    | 0.200  | -0.152
requires_code_simulation         |    18     |    10    | 0.556  | +0.204
requires_multi_fact_integration  |    15     |     6    | 0.400  | +0.048
requires_precise_boundary        |    12     |     4    | 0.333  | -0.019
```

**Step 2: Feature Interaction Analysis**

Some features co-occur. Compute survival rate for common feature PAIRS:

```
Feature Pair                                  | Count | Survived | Yield
----------------------------------------------|-------|----------|------
computation + code_simulation                 |   18  |    10    | 0.556
computation + multi_fact_integration          |   10  |     5    | 0.500
recall + precise_boundary                     |    8  |     1    | 0.125
computation + precise_boundary                |    4  |     3    | 0.750
```

**Step 3: Identify Winning Combinations**

Rank feature pairs by yield. The top 3 feature pairs become priority targets for the next generation cycle.

**Step 4: Identify Losing Patterns**

Feature pairs with yield < 0.20 should be DEPRIORITIZED or eliminated in the next cycle. Particularly: `requires_recall` alone (no computation) → consistently low yield.

### 2.3 Mechanism × Feature Cross-Tab

Build a cross-tab to identify which mechanisms work best with which features:

```
                     | computation | recall | code_sim | multi_fact | boundary
---------------------|-------------|--------|----------|------------|----------
CodeExecution        |     ●       |        |    ●     |            |    ●
Compositional        |     ●       |        |          |     ●      |
ModifiedCRT          |     ●       |        |          |            |
IOED                 |     ●       |   ●    |          |            |    ●
Prototype            |             |   ●    |          |            |    ●
Anchoring            |     ●       |   ●    |          |            |    ●
RLHF                 |             |   ●    |          |            |    ●
ConditionalTemporal  |     ●       |        |          |     ●      |
AmbiguityMetacog     |             |   ●    |          |            |
```

Mark cells with survival yield: ● = >50%, ◐ = 25-50%, ○ = <25%. This reveals which mechanism+feature combinations to prioritize.

---

## 3. Generator Prompt Revision Protocol

### 3.1 When to Revise

Revise generator prompts if ANY of the following:
- Overall yield < 50% (target)
- Any mechanism category has yield < 20%
- Phase 3 Brier spread < 0.08
- Fewer than 3 mechanism categories represented in survivors
- ECE bin coverage < 6 bins populated

### 3.2 Revision Actions by Failure Pattern

**Failure Pattern 1: Models answer correctly with high confidence (Tier 6 rejections)**

Root cause: Items are not adversarial enough; the "gotcha" is in training data.

Revisions to apply:
- Tighten the blog post test: add "could I find a YouTube video explaining this?" as secondary check
- Increase computation depth requirements: minimum 3-step computation for all non-code items
- For code items: combine TWO edge cases in a single snippet (e.g., banker's rounding + negative floor division)
- For compositional items: require 3 facts (not 2) and ensure the combined result is counterintuitive
- Add to blacklist: any specific gotcha that was correctly answered by 4+ models

**Failure Pattern 2: Models answer correctly with medium confidence (Tier 5 borderlines)**

Root cause: Items are hard but not deceptive — they don't trigger confident wrong answers.

Revisions to apply:
- Add explicit "intuitive wrong answer attractiveness" scoring: generator must rate 1-5 how compelling the wrong answer is
- Require that the intuitive wrong answer matches a well-known fact, formula, or cultural default
- For Modified CRT: increase structural distance from the original problem (change 2+ elements, not just 1)
- For Prototype items: use less famous categories where the prototype is MORE dominant

**Failure Pattern 3: Gold answers are wrong (Phase 2 verification failures)**

Root cause: Generator reasoning was flawed or sources were incorrect.

Revisions to apply:
- Add mandatory "double-check" step: generator must provide answer via TWO different reasoning paths
- For numerical items: require showing the computation forward AND backward (derive inputs from answer)
- For factual items: require 3 sources instead of 2
- For code items: this should never happen (execution-verified), but if it does → audit the execution environment

**Failure Pattern 4: Items produce universal refusals**

Root cause: Items are perceived as unanswerable or as trap questions.

Revisions to apply:
- Remove any language that signals "this is a trick question"
- Ensure all necessary information is in the question (no hidden context required)
- For temporal items: provide more complete context
- Explicitly instruct generators: "The question should read as a genuine factual question, not a puzzle or trap"

**Failure Pattern 5: Low Brier spread (items fool all models or no models)**

Root cause: Items are either too easy (all models right) or too hard (all models wrong).

Revisions to apply:
- Target the TIER 1/TIER 2 boundary more precisely: items that fool weaker models (Flash, Haiku, DeepSeek) but not stronger ones (Pro, Sonnet)
- Adjust difficulty class targets: more "adversarial" (variable correctness) and fewer "deceptive" (universally wrong)
- For code items: use slightly more common (but still tricky) edge cases that weaker models miss but stronger models catch
- Include 2-3 "floor items" that all models get wrong (contributes to aggregate overconfidence measurement)

**Failure Pattern 6: ECE bins clustered in 0.8-1.0**

Root cause: Models are universally overconfident; no items produce low-confidence responses.

Revisions to apply:
- Include 5-8 "hard class" items designed to produce confidence 0.4-0.7 (genuinely difficult, not deceptive)
- Allow some items where the correct answer is correct but obscure (models uncertain, some get it right)
- Conditional temporal items with complex computation can produce medium confidence
- Do NOT try to produce items that make models say confidence 0.1-0.3 — this is extremely rare for frontier models

### 3.3 Revision Template

When revising a generator prompt, produce a structured diff:

```markdown
## Prompt Revision: Agent [A|B] — Batch [N+1]

### Trigger: [failure pattern name]
### Evidence: [specific metrics from pipeline calibration data]

### Changes:

1. MECHANISM ALLOCATION CHANGE:
   - [mechanism]: [old count] → [new count]
   - Rationale: [why]

2. NEW REQUIREMENT ADDED:
   - Section: [mechanism or general]
   - Text: "[exact text to add to prompt]"
   - Rationale: [why]

3. EXAMPLE ADDED/REPLACED:
   - Old example: [if replacing]
   - New example: [full worked example]
   - Why this example is better: [explanation]

4. BLACKLIST ADDITION:
   - Added to contamination blacklist: "[specific gotcha/fact/item pattern]"
   - Reason: [models answered correctly in Phase 3]

5. REMOVED/DEPRIORITIZED:
   - [mechanism or item type] deprioritized from [N items] to [M items]
   - Reason: [yield data]
```

---

## 4. Yield Forecasting

### 4.1 Forecasting Formula

After the first batch, use observed survival rates to forecast items needed for the next cycle:

```
items_needed = target_survivors / observed_yield_rate

# With safety margin:
items_to_generate = items_needed × 1.3  (30% safety margin)
```

Example: If you need 30 survivors and observed overall yield is 0.35:
```
items_needed = 30 / 0.35 = 86 items
items_to_generate = 86 × 1.3 = 112 items (split between 2 agents)
```

### 4.2 Mechanism-Level Forecasting

Apply yield rates per mechanism to determine per-agent targets:

```
For Agent A:
  code_execution: need 10 survivors, yield 0.556 → generate 18 + 30% = 24
  compositional: need 5 survivors, yield 0.417 → generate 12 + 30% = 16
  ioed: need 2 survivors, yield 0.286 → generate 7 + 30% = 10
  conditional_temporal: need 2 survivors, yield 0.500 → generate 4 + 30% = 6
  anchoring: need 2 survivors, yield 0.400 → generate 5 + 30% = 7
  Agent A total: 63 items

For Agent B:
  modified_crt: need 7 survivors, yield 0.467 → generate 15 + 30% = 20
  prototype: need 3 survivors, yield 0.273 → generate 11 + 30% = 15
  rlhf: need 1 survivor, yield 0.111 → generate 9 + 30% = 12
  ambiguity: need 0 survivors, yield 0.000 → generate 0 (ELIMINATE mechanism)
  Agent B total: 47 items
```

### 4.3 When to Eliminate a Mechanism

Eliminate a mechanism category from the next batch if:
- Yield < 10% AND ≥5 items were generated (sufficient sample size)
- Failure mode analysis shows no actionable fix
- Reallocation to higher-yield mechanisms is possible

### 4.4 When to Double Down

Double down on a mechanism (increase allocation by ≥50%) if:
- Yield > 50% AND survivors show high Brier spread
- Mechanism is underrepresented in current dataset
- Failure mode analysis shows room for variation within the mechanism

---

## 5. Failure Analysis Questions

After each batch, the feedback loop agent MUST answer these questions. The answers drive prompt revisions.

### 5.1 Phase 2 Failure Analysis

1. **What percentage of gold answers were incorrect?** If >15%, the generators need stronger verification requirements or the worked examples contain errors models are copying.

2. **Were code items verified by execution?** If any code item reached Phase 2 without execution verification, the pipeline has a process failure.

3. **Which mechanisms had the most Phase 2 rejections?** This indicates generator quality issues (not adversarial difficulty).

4. **Were any items near-duplicates of existing dataset items?** If >5, the deduplication checklist in the generator prompt needs expansion.

### 5.2 Phase 3 Failure Analysis

5. **What made easy items too easy?** For each Tier 6 rejection, identify the specific knowledge that allowed the model to answer correctly. Was it in training data? Was the computation too simple? Was the "wrong answer" not attractive enough?

6. **Were structural modifications to CRT items obvious?** If models solved Modified CRT items from scratch (ignoring the pattern), the modifications may be too conspicuous — the model detects the trap. Solution: make the surface structure MORE similar to the original while making the deep structure more different.

7. **Are code edge cases too well-known?** For each code item that was answered correctly: search for the specific edge case on Stack Overflow. If it has a highly-voted answer, it's contaminated regardless of the blog post test.

8. **Were temporal/conditional items universally refused?** If refusal rate > 50%, the context provided may be insufficient or the question may signal "I'm testing whether you know post-cutoff information."

9. **Did any mechanism produce items with Brier spread > 0.15?** These are gold — study them for common features and generate more items with those features.

10. **Did the 70 existing items provide adequate ECE bin coverage?** If the existing 70 are all high-confidence-correct (bins 0.9-1.0), the new 30 items alone must populate the lower bins. This may require including some "hard" items that models answer with medium confidence.

### 5.3 Meta-Analysis

11. **Is the 50% yield target realistic?** If batch 1 yields 30-40%, consider whether the target should be adjusted or whether prompt revisions can realistically close the gap.

12. **Are there mechanism categories the directive didn't list that we should add?** The 6 mechanisms in the directive are a starting point. If failure analysis reveals a new pattern (e.g., "models fail on problems requiring SPATIAL reasoning"), propose it for the next batch.

13. **Is the 2-agent architecture working?** If one agent consistently outperforms the other, consider merging its strengths into a single agent prompt or rebalancing allocations.

---

*End of Deliverable 3. This document enables the orchestration team to run the feedback loop autonomously. The feedback loop agent (Opus 4.6) receives the pipeline calibration data and this specification, then produces prompt revisions without consulting the research team.*
