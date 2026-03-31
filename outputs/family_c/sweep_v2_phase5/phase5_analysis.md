# Sprint v2 Phase 5: Integrated Sweep Analysis
**Date:** 2026-03-31
**Protocol:** sweep_v2.py (third-person C1, reviewer's note C2, B0, confidence, edit-distance)
**Items:** 56 (45 existing + 11 Phase 4 new)
**Models:** 4 (anthropic/claude-sonnet-4.6, google/gemini-2.5-flash, openai/gpt-5-mini, openai/gpt-5.2)
**Total trials:** 224
**Note:** DeepSeek-R1 did not complete within timeout; analysis based on 4 models.

## Key Finding: New Items Add Discriminative Power

The 11 Phase 4 items show dramatically different behavior from the 45 existing items:

**sc_c2_wr_016 (custom mile definition):** 0% T1 accuracy across ALL 4 models — every model imported real-world conversion (1.609 km/mi) instead of using the stated custom definition (1.5 km/mi). This is a pure semantic override trap and produces the best model separation in the dataset.

**3 items at 75% T1 (wr_017, wr_023, wr_030):** Each fails on exactly 1 model, providing single-model differentiation. Sonnet fails on wr_023 (fractional exponent) and wr_030 (juxtaposition), Gemini fails on wr_017 (chained exponentiation).

## Headline Metrics

| Model | T1 Acc | T2 Acc | Δ | W→R | R→W | SC Rate |
|-------|--------|--------|---|-----|-----|---------|
| sonnet-4.6 | 83.9% | 85.7% | +1.8% | 2 | 1 | 22% |
| gem-flash | 78.6% | 85.7% | +7.1% | 6 | 2 | 50% |
| gpt-5-mini | 85.7% | 83.9% | -1.8% | 0 | 1 | 0% |
| gpt-5.2 | 87.5% | 85.7% | -1.8% | 1 | 2 | 14% |

## B0 Baseline (WR items only)

The critical methodological question: does C1/C2 add value beyond re-sampling?

| Model | T2 Acc | B0 Acc | C1−B0 | Interpretation |
|-------|--------|--------|-------|----------------|
| sonnet-4.6 | 84% | 84% | +0% | Re-sampling equivalent |
| gem-flash | 84% | 64% | +20% | Protocol adds value |
| gpt-5-mini | 84% | 84% | +0% | Re-sampling equivalent |
| gpt-5.2 | 84% | 88% | -4% | Re-sampling equivalent |

**Gemini-flash shows +20% C1−B0 delta** — the strongest evidence that the metacognitive protocol adds genuine value beyond re-sampling. The new C1 prompt (third-person, detect-only) appears to help Gemini identify errors it would reproduce on re-answering.

## Confidence Dynamics

All models show high confidence parsing rates (98-100%) with the new ANSWER: | CONFIDENCE: format.

Mean confidence is uniformly high (92-99%), with minimal T1→T2 change (±1%). This suggests models are overconfident even on items they get wrong — consistent with Mei et al. (2025) finding that reasoning models exceed 85% confidence on incorrect responses.

## Edit Distance Patterns

| Model | Mean Similarity | No Change (>0.9) | Targeted (0.4-0.9) | Rewrite (<0.4) |
|-------|----------------|-------------------|---------------------|----------------|
| sonnet-4.6 | 0.18 | 0 (0%) | 4 (7%) | 52 (93%) |
| gem-flash | 0.20 | 4 (7%) | 4 (7%) | 48 (86%) |
| gpt-5-mini | 0.61 | 17 (30%) | 21 (38%) | 18 (32%) |
| gpt-5.2 | 0.45 | 13 (23%) | 9 (16%) | 34 (61%) |

**GPT-5-mini shows the most targeted revision behavior** (38% targeted edits), while Sonnet does nearly all complete rewrites (93%). This aligns with SCoRe's finding that targeted edits indicate genuine correction while rewrites indicate re-generation.

## Gradeability Gate

Gradeable output: 214/224 (95.5%)
Gate (≥90%): **PASS**
