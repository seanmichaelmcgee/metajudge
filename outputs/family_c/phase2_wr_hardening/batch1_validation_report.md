# Phase 2 Batch 1 — Frontier Validation Report

## Date
2026-03-30

## Validation Panel
5 frontier models (same as original sweep):
- `anthropic/claude-sonnet-4.6`
- `openai/gpt-4.1`
- `google/gemini-2.5-pro` (known max_tokens truncation issue — see note)
- `x-ai/grok-3-mini`
- `deepseek/deepseek-chat`

## Results

### sc_c1_wr_012 — Digit Reversal Counting (gold=42)

| Model | T1 | T2 | Transition |
|-------|----|----|------------|
| claude-sonnet-4.6 | CORRECT | CORRECT | R→R |
| gpt-4.1 | CORRECT | CORRECT | R→R |
| gemini-2.5-pro | WRONG† | WRONG† | W→W |
| grok-3-mini | CORRECT | CORRECT | R→R |
| deepseek-chat | CORRECT | CORRECT | R→R |

**T1 accuracy: 80% (4/5)** — excluding Gemini truncation: **100% (4/4)**
**Assessment: TOO EASY** — reclassify as right_to_right or quarantine

### sc_c1_wr_013 — Sticker Distribution (gold=31)

| Model | T1 | T2 | Transition |
|-------|----|----|------------|
| claude-sonnet-4.6 | CORRECT | CORRECT | R→R |
| gpt-4.1 | CORRECT | CORRECT | R→R |
| gemini-2.5-pro | WRONG† | WRONG† | W→W |
| grok-3-mini | CORRECT | CORRECT | R→R |
| deepseek-chat | CORRECT | CORRECT | R→R |

**T1 accuracy: 80% (4/5)** — excluding Gemini truncation: **100% (4/4)**
**Assessment: TOO EASY** — reclassify as right_to_right or quarantine

### sc_c2_wr_012 — pH of Water at 37°C (gold=6.81)

| Model | T1 | T2 | Transition |
|-------|----|----|------------|
| claude-sonnet-4.6 | CORRECT | CORRECT | R→R |
| gpt-4.1 | CORRECT | CORRECT | R→R |
| gemini-2.5-pro | WRONG† | CORRECT | W→R |
| grok-3-mini | CORRECT | CORRECT | R→R |
| deepseek-chat | CORRECT | CORRECT | R→R |

**T1 accuracy: 80% (4/5)** — excluding Gemini truncation: **100% (4/4)**
**Assessment: TOO EASY** — frontier models already know Kw is temperature-dependent

## †Gemini Truncation Note
Gemini responses are truncated at 241-298 characters on T1 (items 1-2) and 0 characters (item 3). This is the same `max_tokens` issue documented in the original sweep (Phase 7). Gemini's W→W results are **truncation artifacts**, not genuine difficulty. For Gemini to be graded fairly, `max_tokens` must be ≥4096.

## Critical Finding
**All 3 batch 1 items are too easy for current frontier models.**

Excluding the Gemini truncation artifact, every model gets every item correct on Turn 1. The items function as R→R (right_to_right), not WR (wrong_to_right).

This is consistent with the pattern from the original sprint: items that seem hard to humans or cheap models are often trivial for frontier reasoning models. The canary test (Tier 1 models) was misleading — canaries scoring poorly does not predict frontier difficulty.

## Root Cause Analysis
1. **Digit reversal (sc_c1_wr_012)**: The constraint 999(d−a) + 90(c−b) = 3267 is straightforward algebra. Frontier models handle the b≥0 vs b≥1 distinction correctly because they systematically verify digit ranges.
2. **Sticker distribution (sc_c1_wr_013)**: Stars-and-bars with upper bounds is a well-known combinatorics topic. Frontier models routinely apply inclusion-exclusion after stars-and-bars.
3. **pH at 37°C (sc_c2_wr_012)**: The temperature dependence of Kw is widely documented and frontier models have this knowledge. This is not the "common misconception" it was expected to be.

## Recommendations
1. **Quarantine all 3 items** — do not promote to clean WR status
2. **Consider reclassifying to R→R** if the questions are otherwise clean
3. **Batch 2 must target genuinely harder failure modes** — need items where even frontier models make computational errors, not just knowledge gaps
4. **Promising directions for harder WR items**:
   - Multi-step modular arithmetic with non-obvious carries
   - Conditional counting where the constraint space is genuinely complex
   - Problems requiring exact decimal arithmetic (where floating-point intuition misleads)
   - Sequence/pattern problems where the "obvious" pattern has an exception
5. **Raise adversary tier** — use Tier 3 models (grok-4, deepseek-r1) for red-teaming
6. **Add a "frontier pre-test"** before accepting items: run the question through 2 frontier models at generation time and require at least 1 to fail

## Updated Item Status
- `sc_c1_wr_012`: draft → **quarantine** (too easy: 80-100% T1)
- `sc_c1_wr_013`: draft → **quarantine** (too easy: 80-100% T1)
- `sc_c2_wr_012`: draft → **quarantine** (too easy: 80-100% T1, knowledge-based)
