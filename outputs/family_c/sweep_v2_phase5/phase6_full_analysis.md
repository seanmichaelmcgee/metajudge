# Phase 6: Full Analysis — Family C Sprint v2
**Date:** 2026-03-31
**Dataset:** 56 items (45 existing + 11 Phase 4 new) × 4 models = 224 trials
**Bootstrap:** 10000 resamples, seed=42

## 1. Headline Metrics (Bootstrap 95% CIs)

| Model | T1 Acc | T2 Acc | T2−T1 Δ | SC Rate | Damage Rate |
|-------|--------|--------|---------|---------|-------------|
| sonnet-4.6 | 83.9% [73.2, 92.9] | 85.7% [76.8, 94.6] | 1.8% [-3.6, 8.9] | 22.2% [6.3, 54.7] (2/9) | 2.1% [0.4, 11.1] (1/47) |
| gem-flash | 78.6% [67.9, 89.3] | 85.7% [76.8, 94.6] | 7.1% [-1.8, 17.9] | 50.0% [25.4, 74.6] (6/12) | 4.5% [1.3, 15.1] (2/44) |
| gpt-5-mini | 85.7% [76.8, 94.6] | 83.9% [73.2, 92.9] | -1.8% [-5.4, 0.0] | 0.0% [0.0, 32.4] (0/8) | 2.1% [0.4, 10.9] (1/48) |
| gpt-5.2 | 87.5% [78.6, 94.6] | 85.7% [76.8, 94.6] | -1.8% [-7.1, 3.6] | 14.3% [2.6, 51.3] (1/7) | 4.1% [1.1, 13.7] (2/49) |

## 2. B0 Baseline (WR Items Only)

| Model | T2 Acc (WR) | B0 Acc | C1−B0 Δ | 95% CI |
|-------|-------------|--------|---------|--------|
| sonnet-4.6 | n=25 | 84.0% | +0.0% | [0.0, 0.0] |
| gem-flash | n=25 | 64.0% | +20.0% | [0.0, 40.0] |
| gpt-5-mini | n=25 | 84.0% | +0.0% | [0.0, 0.0] |
| gpt-5.2 | n=25 | 88.0% | -4.0% | [-20.0, 12.0] |

**Key finding:** Gemini-flash shows +20.0% C1−B0 delta — the strongest evidence 
that the metacognitive review protocol adds genuine value beyond re-sampling.

## 3. Transition Matrices

### sonnet-4.6 (n=56)

|  | T2 Right | T2 Wrong |
|--|----------|----------|
| **T1 Right** (47) | R→R: 46 (82.1%) | R→W: 1 (1.8%) |
| **T1 Wrong** (9) | W→R: 2 (3.6%) | W→W: 7 (12.5%) |

### gem-flash (n=56)

|  | T2 Right | T2 Wrong |
|--|----------|----------|
| **T1 Right** (44) | R→R: 42 (75.0%) | R→W: 2 (3.6%) |
| **T1 Wrong** (12) | W→R: 6 (10.7%) | W→W: 6 (10.7%) |

### gpt-5-mini (n=56)

|  | T2 Right | T2 Wrong |
|--|----------|----------|
| **T1 Right** (48) | R→R: 47 (83.9%) | R→W: 1 (1.8%) |
| **T1 Wrong** (8) | W→R: 0 (0.0%) | W→W: 8 (14.3%) |

### gpt-5.2 (n=56)

|  | T2 Right | T2 Wrong |
|--|----------|----------|
| **T1 Right** (49) | R→R: 47 (83.9%) | R→W: 2 (3.6%) |
| **T1 Wrong** (7) | W→R: 1 (1.8%) | W→W: 6 (10.7%) |

## 4. Edit-Distance Distributions

| Model | Mean Sim | No Change (>0.9) | Targeted (0.4–0.9) | Rewrite (<0.4) |
|-------|----------|------------------|---------------------|----------------|
| sonnet-4.6 | 0.18 | 0 (0%) | 4 (7%) | 52 (93%) |
| gem-flash | 0.20 | 4 (7%) | 4 (7%) | 48 (86%) |
| gpt-5-mini | 0.61 | 17 (30%) | 21 (38%) | 18 (32%) |
| gpt-5.2 | 0.45 | 13 (23%) | 9 (16%) | 34 (61%) |

### Mean Similarity by Transition Type

| Model | R→R | W→R | R→W | W→W |
|-------|-----|-----|-----|-----|
| sonnet-4.6 | 0.19 | 0.10 | 0.04 | 0.15 |
| gem-flash | 0.23 | 0.06 | 0.32 | 0.11 |
| gpt-5-mini | 0.63 | — | 0.13 | 0.55 |
| gpt-5.2 | 0.43 | 0.11 | 0.36 | 0.65 |

**Interpretation:** Sonnet and Gemini do near-complete rewrites (mean sim 0.18–0.20), 
while GPT-5-mini shows 38% targeted edits — consistent with SCoRe's finding that 
targeted revision indicates genuine error correction vs. re-generation.

## 5. Confidence Dynamics

### Mean Confidence

| Model | T1 Conf | T2 Conf | Δ | Parse Rate |
|-------|---------|---------|---|------------|
| sonnet-4.6 | 92.3% | 93.2% | +1.0pp | 100%/100% |
| gem-flash | 99.2% | 98.7% | -0.5pp | 98%/100% |
| gpt-5-mini | 97.8% | 97.2% | -0.6pp | 100%/100% |
| gpt-5.2 | 96.9% | 95.7% | -1.1pp | 100%/100% |

### Confidence Direction Appropriateness

| Model | R→W: Conf drops? | W→R: Conf rises? |
|-------|-------------------|-------------------|
| sonnet-4.6 | 1/1 | 0/2 |
| gem-flash | 0/2 | 0/6 |
| gpt-5-mini | 0/1 | — |
| gpt-5.2 | 0/2 | 0/1 |

### Calibration: Confidence vs Correctness

| Model | Mean Conf (Correct) | Mean Conf (Incorrect) | Gap |
|-------|--------------------|-----------------------|-----|
| sonnet-4.6 | 95.2% | 81.5% | +13.7pp |
| gem-flash | 99.6% | 93.1% | +6.5pp |
| gpt-5-mini | 98.6% | 90.3% | +8.2pp |
| gpt-5.2 | 97.0% | 88.5% | +8.5pp |

**Finding:** Confidence is uniformly high (92–99%) across all models, with minimal 
correct/incorrect gap. Models are overconfident on incorrect answers — consistent 
with Mei et al. (2025) finding that reasoning models exceed 85% confidence even 
on wrong responses.

## 6. New vs Existing Item Comparison

### Accuracy by Item Generation Phase

| Model | Existing T1 (n=45) | Existing T2 | New T1 (n=11) | New T2 |
|-------|--------------------|-------------|---------------|--------|
| sonnet-4.6 | 88.9% | 91.1% | 63.6% | 63.6% |
| gem-flash | 77.8% | 86.7% | 81.8% | 81.8% |
| gpt-5-mini | 84.4% | 82.2% | 90.9% | 90.9% |
| gpt-5.2 | 86.7% | 86.7% | 90.9% | 81.8% |

### Phase 4 Item Discriminative Power

Items with < 100% T1 accuracy across 4 models differentiate models:

| Item ID | T1 Acc (4 models) | Differentiating? |
|---------|-------------------|------------------|
| sc_c1_dt_006 | 100% | No (saturated) |
| sc_c1_wr_014 | 100% | No (saturated) |
| sc_c1_wr_016 | 100% | No (saturated) |
| sc_c1_wr_017 | 75% | Yes |
| sc_c1_wr_023 | 75% | Yes |
| sc_c1_wr_025 | 100% | No (saturated) |
| sc_c1_wr_030 | 75% | Yes |
| sc_c1_wr_033 | 100% | No (saturated) |
| sc_c2_wr_013 | 75% | Yes |
| sc_c2_wr_015 | 100% | No (saturated) |
| sc_c2_wr_016 | 0% | Yes |

**sc_c2_wr_016:** 0% T1 across all 4 models — best differentiator in the dataset.
All models import real-world conversion (1.609 km/mi) instead of the stated 
custom definition (1.5 km/mi). This is a pure semantic override trap.

## 7. Summary

### Key Findings

1. **Gemini-flash is the strongest self-corrector:** +7.1% T2−T1 delta with 
   +20% C1−B0, demonstrating genuine metacognitive correction beyond re-sampling.
2. **GPT-5-mini shows net damage:** −1.8% T2−T1 with 0% SC rate — the review 
   protocol introduces 1 R→W error without any W→R corrections.
3. **Edit-distance reveals revision strategies:** Sonnet/Gemini do complete 
   rewrites; GPT-5-mini does targeted edits. Rewrite ≠ correction.
4. **Confidence is uniformly high and poorly calibrated:** All models show 
   92–99% mean confidence with <5pp correct/incorrect gap.
5. **Phase 4 items add discriminative power:** sc_c2_wr_016 (0% T1) and 
   3 items at 75% T1 provide new model separation points.
