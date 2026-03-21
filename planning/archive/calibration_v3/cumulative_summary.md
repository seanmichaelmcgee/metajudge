# Cumulative Expansion Sprint Summary — 102 Items

**Date:** 2026-03-20
**Status:** 102/100 target items — V1 MILESTONE REACHED

## Pipeline Summary

| Batch | Generated | Survivors | Yield | Commit |
|-------|-----------|-----------|-------|--------|
| 1 | 91 | 19 | 20.9% | 6302761 |
| 2 | 75 | 25 | 33.3% | 30ced62 |
| 3 | 75 | 45 | 60.0% | a86d0c4 |
| 4 | 25 | 13 | 52.0% | (this commit) |
| **Total** | **266** | **102** | **38.3%** | — |

## 4-Model Discrimination Matrix (102 items)

### Model Accuracy

| Model | Correct | Accuracy | Mean Brier |
|-------|---------|----------|------------|
| Sonnet 4 | 48/102 | 47.1% | 0.2899 |
| Gemini 2.5 Pro | 58/102 | 56.9% | 0.2586 |
| DeepSeek V3.1 | 64/102 | 62.7% | 0.1869 |
| Haiku 4.5 | 44/102 | 43.1% | 0.2917 |

### Discrimination

- **Discriminating items:** 58/102 (56.9%)
- Items where all 4 agree correct: 22
- Items where all 4 agree wrong: 22
- Items with mixed results: 58

### Per-Mechanism Performance

| Mechanism | Items | Discriminate | Rate |
|-----------|-------|-------------|------|
| IOED | 16 | 15 | 94% |
| Prototype | 12 | 10 | 83% |
| Anchoring | 10 | 6 | 60% |
| RLHF | 20 | 10 | 50% |
| AmbiguityMetacognition | 19 | 9 | 47% |
| ModifiedCRT | 7 | 3 | 43% |
| Compositional | 17 | 4 | 24% |
| CodeExecution | 1 | 1 | 100% |

### Tier Distribution

| Tier | Classification | Count |
|------|---------------|-------|
| 1 | STRONG_ACCEPT | 22 |
| 2 | ACCEPT | 18 |
| 3 | CONDITIONAL_ACCEPT | 1 |
| 4 | CONDITIONAL_ACCEPT | 4 |
| 5 | BORDERLINE | 57 |

### Key Findings

1. **IOED is the star mechanism** — 94% discrimination, consistently separates models
2. **Prototype items perform excellently** — 83% discrimination from counter-stereotypical facts
3. **Compositional items are hard but not discriminating** — all models fail similarly
4. **DeepSeek has best calibration** (0.19 mean Brier) despite mid-range accuracy
5. **Haiku is the weakest overall** (43.1%) — useful as a lower baseline
6. **Yield improved from 21% to 60%** through iterative mechanism targeting

## Mechanism Coverage

| Mechanism | Count | % of Total |
|-----------|-------|-----------|
| RLHF | 20 | 19.6% |
| AmbiguityMetacognition | 19 | 18.6% |
| Compositional | 17 | 16.7% |
| IOED | 16 | 15.7% |
| Prototype | 12 | 11.8% |
| Anchoring | 10 | 9.8% |
| ModifiedCRT | 7 | 6.9% |
| CodeExecution | 1 | 1.0% |

## Next Steps

1. Build unified calibration_answer_key.json for all 102 items
2. Generate calibration.csv in Kaggle submission format
3. First Kaggle submission
4. Document full workflow in SOUL.md
5. Consider second metacognition domain for diversity
