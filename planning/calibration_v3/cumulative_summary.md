# Cumulative Expansion Sprint Summary

**Date:** 2026-03-20  
**Status:** 89/100 target items — 11 items short of V1 milestone

## Pipeline Summary

| Batch | Generated | Survivors | Yield | Commit |
|-------|-----------|-----------|-------|--------|
| 1 | 91 | 19 | 20.9% | 6302761 |
| 2 | 75 | 25 | 33.3% | 30ced62 |
| 3 | 75 | 45 | 60.0% | (this commit) |
| **Total** | **241** | **89** | **36.9%** | — |

Yield improved dramatically with mechanism targeting:
- Batch 1: 20.9% (broad mechanism coverage)
- Batch 2: 33.3% (targeted high-yield mechanisms)
- Batch 3: 60.0% (further refined targeting)

## 4-Model Discrimination Matrix (89 items)

### Model Accuracy

| Model | Correct | Accuracy | Mean Brier |
|-------|---------|----------|------------|
| Sonnet 4 | 38/89 | 42.7% | 0.3047 |
| Gemini 2.5 Pro | 57/89 | 64.0% | 0.2771 |
| DeepSeek V3.1 | 54/89 | 60.7% | 0.1919 |
| Haiku 4.5 | 42/89 | 47.2% | 0.3180 |

### Discrimination

- **Discriminating items:** 47/89 (52.8%)
- Items where all 4 models agree correct: 22
- Items where all 4 models agree wrong: 20
- Items with mixed results: 47

### Per-Mechanism Performance

| Mechanism | Items | Discriminate | Rate |
|-----------|-------|-------------|------|
| Prototype | 11 | 9 | 82% |
| IOED | 8 | 7 | 88% |
| Anchoring | 10 | 6 | 60% |
| RLHF | 20 | 10 | 50% |
| AmbiguityMetacognition | 15 | 7 | 47% |
| ModifiedCRT | 7 | 3 | 43% |
| Compositional | 17 | 4 | 24% |
| CodeExecution | 1 | 1 | 100% |

### Key Findings

1. **IOED and Prototype are the best discriminators** — they consistently separate model capabilities
2. **Compositional items are hard but not discriminating** — all models fail similarly on multi-step chains
3. **Sonnet is intentionally the weakest** — items were selected for Sonnet failure in stress testing
4. **DeepSeek has the best calibration** (lowest mean Brier at 0.19) despite not the highest accuracy

### Tier Distribution

| Tier | Classification | Count |
|------|---------------|-------|
| 1 | STRONG_ACCEPT | 20 |
| 2 | ACCEPT | 17 |
| 3 | CONDITIONAL_ACCEPT | 1 |
| 4 | CONDITIONAL_ACCEPT | 4 |
| 5 | BORDERLINE | 47 |

## Path to 100

Need 11 more items. Options:
1. **Small Batch 4** (~25 items) targeting IOED and Prototype (high discrimination)
2. **Promote some Tier 5 BORDERLINE items** with strong discrimination signals
3. **Review the 20 items all models get wrong** — may indicate answer key issues

## Repository Structure

```
data/
  batch2/              # Batch 2 raw data
  batch3/              # Batch 3 raw data
  combined_survivors.json          # 89 merged survivors
  combined_discrimination_matrix.json  # Full 4-model matrix
  calibration_answer_key.json      # Batch 1 answer key (19 items)
  discrimination_matrix.json       # Batch 1 matrix (19 items)
src/
  batch2_stress_test.py
  batch2_multimodel_runner.py
  batch3_stress_test.py
  batch3_multimodel_runner.py
```

## Next Steps

1. Generate Batch 4 (~25 items, IOED + Prototype focus) to reach 100
2. Build unified answer key for all 100 items
3. Update calibration.csv for Kaggle format
4. First Kaggle submission
5. Document workflow for repeatability
