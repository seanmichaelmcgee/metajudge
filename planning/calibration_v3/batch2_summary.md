# Batch 2 Summary — Expansion Sprint

**Date:** 2026-03-19  
**Commit:** (this commit)

## Overview

Batch 2 generated 75 new calibration items targeting high-yield metacognition mechanisms identified from Batch 1. Items were stress-tested through the full Sonnet → Flash pipeline, then survivors were evaluated across all 4 models.

## Generation

| Source | Items | Mechanisms |
|--------|-------|------------|
| Agent A | 38 | AmbiguityMetacognition (15), IOED (12), Anchoring (11) |
| Agent B | 37 | RLHF (14), Prototype (10), ModifiedCRT (8), Compositional (5) |
| **Total** | **75** | 7 mechanism types |

## Stress Test Results

### Sonnet Phase (75 items)

| Tier | Classification | Count |
|------|---------------|-------|
| 1 | STRONG_ACCEPT | 4 |
| 2 | ACCEPT | 5 |
| 4 | CONDITIONAL_ACCEPT | 3 |
| 5 | BORDERLINE | 11 |
| 6 | SOFT_REJECT | 52 |

### Flash Escalation (52 Tier 6 items)

- **REJECT:** 50 (Flash answered correctly with high confidence)
- **KEEP → Tier 5:** 2 (promoted to BORDERLINE)

### Final Classification

| Tier | Count | % |
|------|-------|---|
| 1-5 (Survivors) | **25** | 33.3% |
| 6-7 (Rejected) | 50 | 66.7% |

**Yield: 33.3%** — significantly better than Batch 1's 20.9%.

## 4-Model Evaluation (25 survivors)

| Model | Accuracy | Mean Brier |
|-------|----------|------------|
| Sonnet 4 | 36.0% (9/25) | — |
| Gemini 2.5 Pro | 76.0% (19/25) | 0.17 |
| DeepSeek V3.1 | 72.0% (18/25) | 0.13 |
| Haiku 4.5 | 64.0% (16/25) | 0.30 |

Note: Sonnet accuracy is intentionally low — these items were selected for their ability to fool Sonnet in the stress test.

## Combined Pool (Batch 1 + Batch 2)

| Metric | Value |
|--------|-------|
| Total survivors | **44** |
| Batch 1 | 19 |
| Batch 2 | 25 |
| Discriminating items | 30/44 (68.2%) |

### Combined Per-Model Accuracy

| Model | Accuracy |
|-------|----------|
| Sonnet 4 | 36.4% (16/44) |
| Gemini 2.5 Pro | 79.5% (35/44) |
| DeepSeek V3.1 | 68.2% (30/44) |
| Haiku 4.5 | 54.5% (24/44) |

### Mechanism Coverage

| Mechanism | Items | Discriminate |
|-----------|-------|-------------|
| AmbiguityMetacognition | 10 | 7 (70%) |
| RLHF | 10 | 4 (40%) |
| Prototype | 8 | 7 (88%) |
| Compositional | 5 | 4 (80%) |
| IOED | 4 | 3 (75%) |
| Anchoring | 4 | 3 (75%) |
| ModifiedCRT | 2 | 1 (50%) |
| CodeExecution | 1 | 1 (100%) |

## Progress Toward 100-Item Target

- **Current V4 survivors:** 44
- **Remaining needed:** ~56 items
- **Estimated batches:** 3-4 more at ~75 items each (assuming ~15-25 survivors per batch)
- **Next batch priority:** Continue high-yield mechanisms (AmbiguityMetacognition, Prototype, Compositional), consider adding new mechanisms

## Files

- `data/batch2/` — All Batch 2 raw data and intermediate results
- `data/combined_survivors.json` — 44 merged survivors
- `data/combined_discrimination_matrix.json` — Full 4-model matrix
- `src/batch2_stress_test.py` — Stress test pipeline
- `src/batch2_multimodel_runner.py` — Multi-model evaluation runner
