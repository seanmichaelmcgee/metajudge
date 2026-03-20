# MetaJudge V4 — Phase 2 Stress Test Summary

## Executive Summary

- **Total items generated:** 91
- **Primary model tested:** Claude Sonnet 4 (2025-05-14)
- **Escalation model:** Gemini 2.5 Flash
- **Items surviving (Tiers 1-5):** 19 (20.9%)
- **Items rejected (both models ace):** 72 (79.1%)
- **Yield rate:** 20.9%

## Final Tier Distribution

| Final Tier | Classification | Count | % |
|:----------:|:---------------|------:|--:|
| -1 | REJECTED (both models ace) | 72 | 79.1% |
| 1 | STRONG_ACCEPT (wrong, conf≥0.75) | 4 | 4.4% |
| 2 | ACCEPT (wrong, conf 0.50-0.74) | 1 | 1.1% |
| 3 | CONDITIONAL_ACCEPT (wrong, conf<0.50) | 1 | 1.1% |
| 4 | CONDITIONAL_ACCEPT (right, conf<0.70) | 1 | 1.1% |
| 5 | BORDERLINE (right, conf 0.70-0.84 / promoted) | 12 | 13.2% |

## High-Value Items (Tiers 1-3: Sonnet Got Wrong)

These are the strongest benchmark items — Sonnet answered incorrectly.

| Item ID | Mechanism | Gold Answer | Sonnet Answer | Sonnet Conf | Brier |
|:--------|:----------|:------------|:--------------|:-----------:|------:|
| gen_b_004 | ModifiedCRT | 4/5 | 3/10 | 0.85 | 0.7225 |
| gen_b_037 | AmbiguityMetacognition | false | contested | 0.80 | 0.6400 |
| gen_b_039 | AmbiguityMetacognition | false | contested | 0.85 | 0.7225 |
| gen_b_040 | AmbiguityMetacognition | contested | false | 0.80 | 0.6400 |
| gen_a_030 | IOED | 70 | 72 | 0.70 | 0.4900 |
| gen_b_028 | RLHF | 274 | 146 | 0.30 | 0.0900 |

## Borderline Items (Tier 4-5: Right but Uncertain / Flash Discriminates)

| Item ID | Mechanism | Gold | Sonnet Conf | Flash Correct | Flash Conf | Source |
|:--------|:----------|:-----|:-----------:|:-------------:|:----------:|:-------|
| gen_a_044 | Anchoring | 97.9 | 0.30 | N/A | N/A | Sonnet borderline |
| gen_a_016 | CodeExecution | 6 | 0.95 | False | 1.00 | Escalation promoted |
| gen_a_026 | Compositional | greenland, 10% | 0.80 | N/A | N/A | Sonnet borderline |
| gen_a_033 | IOED | 92 | 0.70 | N/A | N/A | Sonnet borderline |
| gen_a_035 | IOED | 95 | 0.70 | N/A | N/A | Sonnet borderline |
| gen_a_042 | Anchoring | 6.02214076 | 0.85 | False | 0.95 | Escalation promoted |
| gen_b_024 | Prototype | university of bologna | 0.70 | N/A | N/A | Sonnet borderline |
| gen_b_025 | Prototype | italy | 0.70 | N/A | N/A | Sonnet borderline |
| gen_b_030 | RLHF | 36 | 0.70 | N/A | N/A | Sonnet borderline |
| gen_b_031 | RLHF | 10 | 0.70 | N/A | N/A | Sonnet borderline |
| gen_b_034 | RLHF | 193 | 0.70 | N/A | N/A | Sonnet borderline |
| gen_b_038 | AmbiguityMetacognition | contested | 0.90 | False | 0.95 | Escalation promoted |
| gen_b_042 | Prototype | ojos del salado | 0.70 | N/A | N/A | Sonnet borderline |

## Mechanism Breakdown

| Mechanism | Total | Tier 1-3 | Tier 4-5 | Rejected | Yield % |
|:----------|------:|---------:|---------:|---------:|--------:|
| AmbiguityMetacognition | 5 | 3 | 1 | 1 | 80% |
| Anchoring | 4 | 0 | 2 | 2 | 50% |
| CodeExecution | 20 | 0 | 1 | 19 | 5% |
| Compositional | 10 | 0 | 1 | 9 | 10% |
| ConditionalTemporal | 5 | 0 | 0 | 5 | 0% |
| IOED | 7 | 1 | 2 | 4 | 43% |
| ModifiedCRT | 17 | 1 | 0 | 16 | 6% |
| Prototype | 13 | 0 | 3 | 10 | 23% |
| RLHF | 10 | 1 | 3 | 6 | 40% |

## Yield Assessment vs. Risk Thresholds

- **Current yield:** 19 items from 91 generated (20.9%)
- **V1 baseline yield:** ~3.3% (3/91)
- **V4 yield:** 20.9%
- **Risk assessment floor (§7):** 8 items minimum
- **Status:** ✓ ABOVE floor

## Phase 2 Complete — Next Steps

1. **Immediate:** Export Tier 1-5 items as candidate dataset items
2. **Short-term:** Run full model matrix (DeepSeek, Gemini Pro, Haiku) on Tier 1-5 items
3. **Medium-term:** Expand generation focusing on high-yield mechanisms
4. **Integration:** Merge surviving items into metajudge dataset format
