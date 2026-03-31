# Phase 2 WR Hardening — Batch 1 Report

## Date
2026-03-30

## Model Routing
- **Author**: `anthropic/claude-sonnet-4.6` (Tier 2)
- **Adversary**: `x-ai/grok-4.1-fast` (Tier 2, different family)
- **Auditor**: `openai/gpt-5.2` (Tier 2, third family)
- **Canaries**: `google/gemini-2.5-flash-lite`, `x-ai/grok-3-mini`, `openai/gpt-5-mini`

## Items Generated

### ACCEPTED: sc_c1_wr_012 — Digit Reversal Counting
- **Question**: How many 4-digit integers N have reversal exactly 3267 larger than N?
- **Gold answer**: 42
- **Mechanism**: `digit_range_boundary_error` — models exclude b=0 for interior digits
- **Intended wrong answer**: 36 (treating all digit variables as ≥1)
- **Canary results**: 1/3 correct (grok-3-mini correct, gemini-flash and gpt-5-mini wrong)
- **Adversary**: PASS at iteration 1, gold verified
- **Auditor**: ACCEPT, confidence 0.98, gold independently verified as 42
- **Status**: `draft` — needs 5-model validation sweep before promotion to clean

### ACCEPTED: sc_c1_wr_013 — Sticker Distribution with Upper Bound
- **Question**: Distribute 12 identical stickers to 4 students, each gets 2-5 stickers. How many ways?
- **Gold answer**: 31
- **Mechanism**: `upper_bound_omission_in_stars_and_bars` — models apply stars-and-bars without enforcing upper bound
- **Intended wrong answer**: 35 (stars-and-bars C(7,3) without subtracting 4 violations)
- **Canary results**: 2/3 correct (grok-3-mini and gpt-5-mini correct, gemini-flash wrong)
- **Adversary**: PASS at iteration 1, gold verified
- **Auditor**: ACCEPT, confidence 0.97, gold independently verified as 31
- **Status**: `draft` — needs validation sweep. Canary accuracy (67%) is above target; may be easier than desired.

### ACCEPTED: sc_c2_wr_012 — pH of Water at 37°C
- **Question**: What is the pH of pure water at 37°C?
- **Gold answer**: 6.81 (tolerance: ±0.05)
- **Mechanism**: `temperature_dependent_kw_ignored` — models default to pH=7.0
- **Evidence snippet**: CRC Handbook Kw values showing temperature dependence, with note that neutrality ≠ pH 7
- **Canary results**: 0/3 correct (all answered 7.0)
- **Adversary**: PASS at iteration 1, gold verified
- **Auditor**: ACCEPT, confidence 0.88, gold independently verified as 6.808
- **Status**: `draft` — canary accuracy (0%) suggests this may be harder than the 40-60% target; frontier models may do better.

### REJECTED: Odd Balls in Boxes (C1 WR)
- **Question**: Distribute 7 identical balls into 3 boxes, each with odd number
- **Gold answer**: 6
- **Rejected because**: Canaries scored 3/3 (100%) — too easy for even cheap models
- **Not added to dataset**

## Batch Statistics
- Items attempted: 4 (3 accepted, 1 rejected for being too easy)
- Total API calls: ~24 (4 author + 4 adversary + 9 canary + 3 audit + retries)
- Author-adversary iterations: All items passed on first adversary review
- Three different model families used throughout (Anthropic / xAI / OpenAI)

## Canary Accuracy Summary

| Item | Canary Acc | Target | Assessment |
|------|-----------|--------|------------|
| sc_c1_wr_012 (digit reversal) | 33% | 40-60% | Below target — may be harder than intended |
| sc_c1_wr_013 (stickers) | 67% | 40-60% | Above target — monitor during frontier validation |
| sc_c2_wr_012 (pH) | 0% | 40-60% | Well below — likely harder than target, frontier models may differ |
| Odd balls (rejected) | 100% | 40-60% | Rejected |

## Concerns and Next Steps
1. **All items passed adversary on first try** — this suggests the adversary bar may not be high enough, or the author is producing strong items. Consider using Tier 3 adversary (deepseek-r1 or grok-4) for harder critique in batch 2.
2. **Canary accuracy is polarized** — items are either very hard (0-33%) or too easy (67-100%). The 40-60% sweet spot is hard to hit. May need to calibrate question difficulty more carefully.
3. **No multi-turn iteration occurred** — all items passed on first adversary pass. Batch 2 should attempt harder failure modes that require genuine iteration.
4. **Items need 5-model frontier validation** before promotion to `clean` status.
