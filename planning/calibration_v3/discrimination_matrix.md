# 4-Model Discrimination Matrix — Batch 1 Survivors

## Model Accuracy Summary

| Model | Correct | Total | Accuracy | Avg Brier |
|:------|--------:|------:|---------:|----------:|
| Claude Sonnet 4 | 13 | 19 | 68.4% | 0.2416 |
| Gemini 2.5 Flash | 0 | 3 | 0.0% | 0.9350 |
| Gemini 2.5 Pro | 16 | 19 | 84.2% | 0.1166 |
| DeepSeek V3.1 | 12 | 19 | 63.2% | 0.1278 |
| Claude Haiku 4.5 | 8 | 19 | 42.1% | 0.3578 |

**Brier spread:** 0.8184 (target: ≥0.05)
**Best:** Gemini 2.5 Pro (0.1166)
**Worst:** Gemini 2.5 Flash (0.9350)

## Per-Item Discrimination Matrix

| Item ID | Mechanism | Tier | Gold | Sonnet | Flash | Pro | DeepSeek | Haiku | Disc |
|:--------|:----------|:----:|:-----|:------:|:-----:|:---:|:--------:|:-----:|:----:|
| gen_b_037 | AmbiguityMet | 1 | false | ✗ 0.80 | — | ✓ 1.00 | ✓ 0.90 | ✗ 0.85 | 0.50 |
| gen_a_030 | IOED | 2 | 70 | ✗ 0.70 | — | ✓ 0.95 | ✓ 0.60 | ✗ 0.72 | 0.50 |
| gen_a_044 | Anchoring | 4 | 97.9 | ✓ 0.30 | — | ✓ 0.95 | ✗ 0.40 | ✗ 0.35 | 0.50 |
| gen_b_024 | Prototype | 5 | university of b | ✓ 0.70 | — | ✗ 0.95 | ✓ 0.80 | ✗ 0.60 | 0.50 |
| gen_a_016 | CodeExecutio | 5 | 6 | ✓ 0.95 | ✗ 1.00 | ✓ 1.00 | ✗ 0.90 | ✗ 0.95 | 0.40 |
| gen_a_042 | Anchoring | 5 | 6.02214076 | ✓ 0.85 | ✗ 0.95 | ✓ 1.00 | ✓ 0.95 | ✗ 0.85 | 0.40 |
| gen_b_004 | ModifiedCRT | 1 | 4/5 | ✗ 0.85 | — | ✓ 0.95 | ✗ 0.00 | ✗ 0.75 | 0.25 |
| gen_b_039 | AmbiguityMet | 1 | false | ✗ 0.85 | — | ✗ 0.95 | ✓ 0.90 | ✗ 0.85 | 0.25 |
| gen_b_040 | AmbiguityMet | 1 | contested | ✗ 0.80 | — | ✓ 0.90 | ✗ 0.80 | ✗ 0.92 | 0.25 |
| gen_a_033 | IOED | 5 | 92 | ✓ 0.70 | — | ✓ 0.95 | ✓ 0.60 | ✗ 0.72 | 0.25 |
| gen_b_030 | RLHF | 5 | 36 | ✓ 0.70 | — | ✓ 1.00 | ✗ 0.00 | ✓ 0.85 | 0.25 |
| gen_b_031 | RLHF | 5 | 10 | ✓ 0.70 | — | ✓ 0.95 | ✗ 0.00 | ✓ 0.85 | 0.25 |
| gen_b_038 | AmbiguityMet | 5 | contested | ✓ 0.90 | ✗ 0.95 | ✓ 1.00 | ✓ 0.85 | ✓ 0.92 | 0.20 |
| gen_b_028 | RLHF | 3 | 274 | ✗ 0.30 | — | ✗ 0.60 | ✗ 0.40 | ✗ 0.35 | 0.00 |
| gen_a_026 | Compositiona | 5 | greenland, 10% | ✓ 0.80 | — | ✓ 0.98 | ✓ 0.80 | ✓ 0.85 | 0.00 |
| gen_a_035 | IOED | 5 | 95 | ✓ 0.70 | — | ✓ 0.95 | ✓ 0.65 | ✓ 0.72 | 0.00 |
| gen_b_025 | Prototype | 5 | italy | ✓ 0.70 | — | ✓ 0.85 | ✓ 0.80 | ✓ 0.45 | 0.00 |
| gen_b_034 | RLHF | 5 | 193 | ✓ 0.70 | — | ✓ 0.95 | ✓ 0.90 | ✓ 0.75 | 0.00 |
| gen_b_042 | Prototype | 5 | ojos del salado | ✓ 0.70 | — | ✓ 0.98 | ✓ 0.80 | ✓ 0.60 | 0.00 |

## Key Discrimination Items

Items where models disagree most (discrimination score > 0):

### gen_b_037 (AmbiguityMetacognition, Tier 1)
- Gold: false
- Correct (2): Gemini 2.5 Pro, DeepSeek V3.1
- Wrong (2): Claude Sonnet 4, Claude Haiku 4.5

### gen_a_030 (IOED, Tier 2)
- Gold: 70
- Correct (2): Gemini 2.5 Pro, DeepSeek V3.1
- Wrong (2): Claude Sonnet 4, Claude Haiku 4.5

### gen_a_044 (Anchoring, Tier 4)
- Gold: 97.9
- Correct (2): Claude Sonnet 4, Gemini 2.5 Pro
- Wrong (2): DeepSeek V3.1, Claude Haiku 4.5

### gen_b_024 (Prototype, Tier 5)
- Gold: university of bologna
- Correct (2): Claude Sonnet 4, DeepSeek V3.1
- Wrong (2): Gemini 2.5 Pro, Claude Haiku 4.5

### gen_a_016 (CodeExecution, Tier 5)
- Gold: 6
- Correct (2): Claude Sonnet 4, Gemini 2.5 Pro
- Wrong (3): Gemini 2.5 Flash, DeepSeek V3.1, Claude Haiku 4.5

### gen_a_042 (Anchoring, Tier 5)
- Gold: 6.02214076
- Correct (3): Claude Sonnet 4, Gemini 2.5 Pro, DeepSeek V3.1
- Wrong (2): Gemini 2.5 Flash, Claude Haiku 4.5

### gen_b_004 (ModifiedCRT, Tier 1)
- Gold: 4/5
- Correct (1): Gemini 2.5 Pro
- Wrong (3): Claude Sonnet 4, DeepSeek V3.1, Claude Haiku 4.5

### gen_b_039 (AmbiguityMetacognition, Tier 1)
- Gold: false
- Correct (1): DeepSeek V3.1
- Wrong (3): Claude Sonnet 4, Gemini 2.5 Pro, Claude Haiku 4.5

### gen_b_040 (AmbiguityMetacognition, Tier 1)
- Gold: contested
- Correct (1): Gemini 2.5 Pro
- Wrong (3): Claude Sonnet 4, DeepSeek V3.1, Claude Haiku 4.5

### gen_a_033 (IOED, Tier 5)
- Gold: 92
- Correct (3): Claude Sonnet 4, Gemini 2.5 Pro, DeepSeek V3.1
- Wrong (1): Claude Haiku 4.5

### gen_b_030 (RLHF, Tier 5)
- Gold: 36
- Correct (3): Claude Sonnet 4, Gemini 2.5 Pro, Claude Haiku 4.5
- Wrong (1): DeepSeek V3.1

### gen_b_031 (RLHF, Tier 5)
- Gold: 10
- Correct (3): Claude Sonnet 4, Gemini 2.5 Pro, Claude Haiku 4.5
- Wrong (1): DeepSeek V3.1

### gen_b_038 (AmbiguityMetacognition, Tier 5)
- Gold: contested
- Correct (4): Claude Sonnet 4, Gemini 2.5 Pro, DeepSeek V3.1, Claude Haiku 4.5
- Wrong (1): Gemini 2.5 Flash

## Assessment

- **Items with any model disagreement:** 13/19
- **Items with high discrimination (≥0.3):** 6/19
- **Items where ALL models correct:** 5
- **Items where ALL models wrong:** 1
