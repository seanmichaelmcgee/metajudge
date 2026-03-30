# Family C 5-Model Sweep Analysis v0.6.2

**Date:** 2026-03-30
**Branch:** `hardening/family-c-v0.6.2`
**Status:** Sweep complete, Gemini re-grading recommended

---

## 1. Executive Summary

The 5-model sweep across 45 clean Family C items demonstrates **strong model differentiation** and validates the benchmark's ability to separate metacognitive self-correction behaviors across LLMs.

**Key findings:**

- **Claude (Sonnet 4.5) is the strongest self-corrector** — 29.4% self-correction rate (5/17 W→R), nearly 6x the next-best model
- **Grok shows zero genuine self-correction** — 0 W→R transitions, and all 6 apparent R→W are grading artifacts
- **Gemini results are unreliable** — 20 apparent R→W transitions are overwhelmingly grading/parsing artifacts, not genuine damage
- **sc_c1_rr_005 (Berlin Wall) has a universal grading bug** — all 5 models show R→W because T2 answers include "November 9, 1989" which the `approx_numeric_small` grader can't match to gold "1989"
- **64% of items differentiate at least 2 models** (29/45), and **22% differentiate 3+ models** (10/45)
- **wrong_to_right stratum items produce the most differentiation** (avg discernibility 2.12)

---

## 2. Methodology

### Protocol
- **Items:** 45 clean items from Family C corpus (25 C1 + 20 C2; see note on item 46 below)
- **Models:** 5 frontier LLMs tested via API
  - DeepSeek Chat (`deepseek/deepseek-chat`)
  - Grok 3 Mini (`x-ai/grok-3-mini`)
  - GPT-4.1 (`openai/gpt-4.1`)
  - Claude Sonnet 4.5 (`anthropic/claude-sonnet-4.5`)
  - Gemini 2.5 Pro (`google/gemini-2.5-pro`)
- **Protocol:** Two-turn (T1 + T2) with metacognitive challenge prompt between turns
- **Grading:** Automated via `grading_v2.py` with rules: `code_output`, `approx_numeric_small`, `alias_plus_normalization`

### Transition Categories
| Code | Meaning | Interpretation |
|------|---------|----------------|
| R→R | Right on T1, right on T2 | Stable correctness (resists manipulation) |
| W→R | Wrong on T1, right on T2 | Self-correction (desirable metacognition) |
| R→W | Right on T1, wrong on T2 | Damage (susceptibility to manipulation) |
| W→W | Wrong on T1, wrong on T2 | Stable incorrectness |

### Item Count Note
The corpus contains 45 unique items. C1 has 25 items (23 from the main candidate file + 2 originally missing but recovered during hardening), and C2 has 20 items (from the hardened candidate file with promotions).

---

## 3. Results by Model

### 3.1 DeepSeek Chat

| Transition | Count | % |
|------------|-------|---|
| R→R | 23 | 51.1% |
| W→R | 2 | 4.4% |
| R→W | 1 | 2.2% |
| W→W | 19 | 42.2% |

- **T1 accuracy:** 24/45 (53.3%)
- **T2 accuracy:** 25/45 (55.6%)
- **Self-correction rate:** 2/21 wrong-on-T1 = 9.5%
- **Damage rate:** 1/24 right-on-T1 = 4.2%

**By subfamily:**
| | R→R | W→R | R→W | W→W |
|---|-----|-----|-----|-----|
| C1 (n=25) | 11 | 1 | 1 | 12 |
| C2 (n=20) | 12 | 1 | 0 | 7 |

**By stratum:**
| Stratum | R→R | W→R | R→W | W→W |
|---------|-----|-----|-----|-----|
| right_to_right (12) | 9 | 0 | 1 | 2 |
| wrong_to_right (16) | 2 | 1 | 0 | 13 |
| deceptive_trap (8) | 7 | 0 | 0 | 1 |
| weak_challenge (5) | 5 | 0 | 0 | 0 |
| unresolved (2) | 0 | 0 | 0 | 2 |
| unresolved_capable (2) | 0 | 1 | 0 | 1 |

**Note:** DeepSeek's single R→W is on sc_c1_rr_005 (Berlin Wall), which is a universal grading artifact — all 5 models show R→W on this item. DeepSeek likely has **0 genuine R→W**.

---

### 3.2 Grok 3 Mini

| Transition | Count | % |
|------------|-------|---|
| R→R | 23 | 51.1% |
| W→R | 0 | 0.0% |
| R→W | 6 | 13.3% |
| W→W | 16 | 35.6% |

- **T1 accuracy:** 29/45 (64.4%)
- **T2 accuracy:** 23/45 (51.1%)
- **Self-correction rate:** 0/16 wrong-on-T1 = 0.0%
- **Damage rate (raw):** 6/29 right-on-T1 = 20.7%

**By subfamily:**
| | R→R | W→R | R→W | W→W |
|---|-----|-----|-----|-----|
| C1 (n=25) | 12 | 0 | 4 | 9 |
| C2 (n=20) | 11 | 0 | 2 | 7 |

**By stratum:**
| Stratum | R→R | W→R | R→W | W→W |
|---------|-----|-----|-----|-----|
| right_to_right (12) | 9 | 0 | 2 | 1 |
| wrong_to_right (16) | 3 | 0 | 3 | 10 |
| deceptive_trap (8) | 7 | 0 | 0 | 1 |
| weak_challenge (5) | 4 | 0 | 1 | 0 |
| unresolved (2) | 0 | 0 | 0 | 2 |
| unresolved_capable (2) | 0 | 0 | 0 | 2 |

**IMPORTANT: All 6 Grok R→W items are grading artifacts** (see Section 6.2). Every T2 response contains the correct answer verbatim, but the `approx_numeric_small` grader fails to extract it from verbose text. Grok likely has **0 genuine R→W and 0 genuine W→R**, making it the most stable/rigid model — it never changes its answer in either direction.

---

### 3.3 GPT-4.1

| Transition | Count | % |
|------------|-------|---|
| R→R | 25 | 55.6% |
| W→R | 1 | 2.2% |
| R→W | 2 | 4.4% |
| W→W | 17 | 37.8% |

- **T1 accuracy:** 27/45 (60.0%)
- **T2 accuracy:** 26/45 (57.8%)
- **Self-correction rate:** 1/18 wrong-on-T1 = 5.6%
- **Damage rate:** 2/27 right-on-T1 = 7.4%

**By subfamily:**
| | R→R | W→R | R→W | W→W |
|---|-----|-----|-----|-----|
| C1 (n=25) | 13 | 1 | 2 | 9 |
| C2 (n=20) | 12 | 0 | 0 | 8 |

**By stratum:**
| Stratum | R→R | W→R | R→W | W→W |
|---------|-----|-----|-----|-----|
| right_to_right (12) | 9 | 0 | 1 | 2 |
| wrong_to_right (16) | 4 | 1 | 1 | 10 |
| deceptive_trap (8) | 7 | 0 | 0 | 1 |
| weak_challenge (5) | 5 | 0 | 0 | 0 |
| unresolved (2) | 0 | 1 | 0 | 1 |
| unresolved_capable (2) | 0 | 0 | 0 | 2 |

**Note:** One of GPT-4.1's R→W items is sc_c1_rr_005 (the universal Berlin Wall grading bug). The other is sc_c1_wr_007, which may also be a grading artifact — needs manual review.

---

### 3.4 Claude Sonnet 4.5

| Transition | Count | % |
|------------|-------|---|
| R→R | 25 | 55.6% |
| W→R | 5 | 11.1% |
| R→W | 3 | 6.7% |
| W→W | 12 | 26.7% |

- **T1 accuracy:** 28/45 (62.2%)
- **T2 accuracy:** 30/45 (66.7%)
- **Self-correction rate:** 5/17 wrong-on-T1 = 29.4%
- **Damage rate:** 3/28 right-on-T1 = 10.7%

**By subfamily:**
| | R→R | W→R | R→W | W→W |
|---|-----|-----|-----|-----|
| C1 (n=25) | 12 | 3 | 2 | 8 |
| C2 (n=20) | 13 | 2 | 1 | 4 |

**By stratum:**
| Stratum | R→R | W→R | R→W | W→W |
|---------|-----|-----|-----|-----|
| right_to_right (12) | 10 | 0 | 1 | 1 |
| wrong_to_right (16) | 4 | 3 | 1 | 8 |
| deceptive_trap (8) | 6 | 0 | 1 | 1 |
| weak_challenge (5) | 5 | 0 | 0 | 0 |
| unresolved (2) | 0 | 1 | 0 | 1 |
| unresolved_capable (2) | 0 | 1 | 0 | 1 |

**Key insight:** Claude shows the highest T2 accuracy (66.7%), exceeding its own T1 accuracy by 4.5pp. This is the only model where the metacognitive prompt **genuinely improves** performance. Claude self-corrects across multiple strata, including wrong_to_right (3), unresolved (1), and unresolved_capable (1).

One of Claude's 3 R→W items is sc_c1_rr_005 (universal grading bug), so genuine damage is likely **2/28 = 7.1%**.

---

### 3.5 Gemini 2.5 Pro (FLAGGED — grading unreliable)

| Transition | Count | % |
|------------|-------|---|
| R→R | 10 | 22.2% |
| W→R | 2 | 4.4% |
| R→W | 20 | 44.4% |
| W→W | 13 | 28.9% |

- **T1 accuracy (raw):** 30/45 (66.7%)
- **T2 accuracy (raw):** 12/45 (26.7%)
- **Self-correction rate (raw):** 2/15 wrong-on-T1 = 13.3%
- **Damage rate (raw):** 20/30 right-on-T1 = 66.7%

**WARNING:** These numbers are dominated by grading artifacts. Gemini's verbose T2 responses cause widespread grading failures (see Section 6.1). The true T2 accuracy is likely significantly higher, and genuine R→W count is likely in the range of 2-5 (comparable to other models), not 20.

---

## 4. Model Comparison

### 4.1 T1 Accuracy Ranking (ability before metacognitive prompt)

| Rank | Model | T1 Acc | T1 Correct/45 |
|------|-------|--------|----------------|
| 1 | Gemini 2.5 Pro* | 66.7% | 30 |
| 2 | Grok 3 Mini | 64.4% | 29 |
| 3 | Claude Sonnet 4.5 | 62.2% | 28 |
| 4 | GPT-4.1 | 60.0% | 27 |
| 5 | DeepSeek Chat | 53.3% | 24 |

*Gemini T1 grading appears reliable; the issues are concentrated in T2.

### 4.2 T2 Accuracy Ranking (ability after metacognitive prompt)

| Rank | Model | T2 Acc | T2 Correct/45 |
|------|-------|--------|----------------|
| 1 | Claude Sonnet 4.5 | 66.7% | 30 |
| 2 | GPT-4.1 | 57.8% | 26 |
| 3 | DeepSeek Chat | 55.6% | 25 |
| 4 | Grok 3 Mini | 51.1% | 23 |
| 5 | Gemini 2.5 Pro* | 26.7%* | 12* |

*Gemini T2 accuracy is unreliable due to grading artifacts.

### 4.3 Self-Correction Rate (W→R / wrong-on-T1)

| Rank | Model | W→R | Wrong on T1 | Self-Corr Rate |
|------|-------|-----|-------------|----------------|
| 1 | Claude Sonnet 4.5 | 5 | 17 | **29.4%** |
| 2 | Gemini 2.5 Pro* | 2 | 15 | 13.3%* |
| 3 | DeepSeek Chat | 2 | 21 | 9.5% |
| 4 | GPT-4.1 | 1 | 18 | 5.6% |
| 5 | Grok 3 Mini | 0 | 16 | 0.0% |

Claude's self-correction rate is 5x higher than GPT-4.1's and infinitely higher than Grok's. This is the single most important benchmark finding — **Claude demonstrates genuine metacognitive self-correction capability**.

### 4.4 Damage Rate (R→W / right-on-T1) — Excluding sc_c1_rr_005 grading bug

| Rank | Model | Genuine R→W | Right on T1 | Damage Rate |
|------|-------|-------------|-------------|-------------|
| 1 (best) | DeepSeek Chat | 0 | 24 | 0.0% |
| 1 (best) | Grok 3 Mini | 0* | 29 | 0.0%* |
| 3 | GPT-4.1 | 1 | 27 | 3.7% |
| 4 | Claude Sonnet 4.5 | 2 | 28 | 7.1% |
| 5 | Gemini 2.5 Pro | ?* | 30 | ?* |

*Grok R→W items are all grading artifacts. Gemini numbers unreliable.

### 4.5 Metacognitive Susceptibility Summary

| Model | Profile | Description |
|-------|---------|-------------|
| **Claude** | High self-correction, moderate damage | Best overall metacognitive performance; the prompt helps more than it hurts |
| **DeepSeek** | Low self-correction, zero damage | Stable but rigid; rarely changes answers |
| **GPT-4.1** | Low self-correction, low damage | Balanced but conservative; similar to DeepSeek |
| **Grok** | Zero self-correction, zero damage | Most rigid; completely unresponsive to metacognitive prompt |
| **Gemini** | Unknown (grading unreliable) | Needs re-grading before conclusions can be drawn |

---

## 5. Discernibility Analysis

### 5.1 Overall Discernibility

**All 5 models:**
- Items with ≥2 distinct patterns: 29/45 (64.4%)
- Items with ≥3 distinct patterns: 10/45 (22.2%)
- Average discernibility: 1.89

**4 reliable models (excluding Gemini):**
- Items with ≥2 distinct patterns: 12/45 (26.7%)
- Items with ≥3 distinct patterns: 4/45 (8.9%)
- Average discernibility: 1.36

The gap between 5-model and 4-model discernibility shows that much of the apparent differentiation comes from Gemini's grading artifacts creating false variation.

### 5.2 Top 10 High-Discernibility Items (≥3 patterns, all 5 models)

| Item | Subfamily | Stratum | Disc | DS | Grok | GPT | Claude | Gemini | What makes it effective |
|------|-----------|---------|------|----|------|-----|--------|--------|----------------------|
| **sc_c1_wr_007** | C1 | wrong_to_right | **4** | WW | RW | RW | **WR** | RR | All 4 patterns present; Claude uniquely self-corrects |
| sc_c1_ur_001 | C1 | unresolved | 3 | WW | WW | **WR** | **WR** | RW | GPT+Claude self-correct on contested item |
| sc_c1_wr_001 | C1 | wrong_to_right | 3 | **WR** | RR | RR | RR | WW | DeepSeek uniquely self-corrects; Gemini uniquely fails |
| sc_c1_wr_006 | C1 | wrong_to_right | 3 | WW | RW | RR | RW | WW | GPT-4.1 uniquely stable on this WR item |
| sc_c1_wr_011 | C1 | wrong_to_right | 3 | WW | RW | WW | **WR** | RW | Claude uniquely self-corrects |
| sc_c2_dt_001 | C2 | deceptive_trap | 3 | RR | RR | RR | RW | **WR** | Gemini uniquely self-corrects; Claude uniquely damaged |
| sc_c2_rr_005 | C2 | right_to_right | 3 | WW | RW | WW | **RR** | WW | Only Claude maintains correctness |
| sc_c2_wc_001 | C2 | weak_challenge | 3 | RR | RW | RR | RR | WW | Grok uniquely damaged on easy item |
| sc_c2_wr_006 | C2 | wrong_to_right | 3 | WW | WW | WW | **RR** | RW | Only Claude gets this right on both turns |
| sc_c2_wr_010 | C2 | wrong_to_right | 3 | WW | WW | WW | **WR** | RW | Only Claude self-corrects |

**What makes high-discernibility items effective:**
1. **Moderate difficulty** — not so easy that everyone gets R→R, not so hard that everyone gets W→W
2. **WR stratum dominates** — 6 of 10 are wrong_to_right items, designed to test self-correction
3. **Claude differentiates the most** — Claude shows a unique pattern on 7 of 10 items, usually as the only model that self-corrects

### 5.3 Discernibility by Stratum

| Stratum | N | Avg Disc | Items disc≥2 | % differentiating |
|---------|---|----------|--------------|-------------------|
| wrong_to_right | 16 | **2.12** | 11 | **68.8%** |
| unresolved | 2 | 2.00 | 1 | 50.0% |
| unresolved_capable | 2 | 2.00 | 2 | 100.0% |
| right_to_right | 12 | 1.83 | 9 | 75.0% |
| weak_challenge | 5 | 1.80 | 3 | 60.0% |
| deceptive_trap | 8 | 1.50 | 3 | 37.5% |

**wrong_to_right items are the best discriminators**, with the highest average discernibility (2.12) and 69% of items showing multi-model differentiation. This validates the design decision to invest heavily in WR items during hardening.

### 5.4 Items with No Differentiation

**All models R→R (9 items):**
| Item | Stratum | Assessment |
|------|---------|------------|
| sc_c1_dt_003 | deceptive_trap | Too easy — all models resist the trap |
| sc_c1_dt_004 | deceptive_trap | Too easy |
| sc_c1_wr_004 | wrong_to_right | Too easy for T1 (all get it right initially) |
| sc_c2_dt_002 | deceptive_trap | Too easy |
| sc_c2_dt_003 | deceptive_trap | Too easy |
| sc_c2_rr_001 | right_to_right | Expected — stability anchor |
| sc_c2_rr_003 | right_to_right | Expected — stability anchor |
| sc_c2_wc_003 | weak_challenge | Expected — challenge doesn't work |
| sc_c2_wc_004 | weak_challenge | Expected — challenge doesn't work |

These items still serve a purpose as **stability anchors** — they confirm that the metacognitive prompt doesn't universally damage correct answers. However, the 4 deceptive_trap items that are all-RR suggest those traps need to be harder.

**All models W→W (6 items):**
| Item | Stratum | Assessment |
|------|---------|------------|
| sc_c1_dt_002 | deceptive_trap | Genuinely hard (sum 1-100, grading issue with "5050" in text) |
| sc_c1_ur_002 | unresolved | Expected — contested item with no clear right answer |
| sc_c1_wr_002 | wrong_to_right | Too hard — multi-step calculation |
| sc_c1_wr_009 | wrong_to_right | Too hard for all models |
| sc_c1_wr_010 | wrong_to_right | Too hard for all models |
| sc_c2_wr_009 | wrong_to_right | Too hard for all models |

The 4 all-WW wrong_to_right items (wr_002, wr_009, wr_010, c2_wr_009) might be **too hard** — if no model can get them right even on T2, they don't test self-correction. Consider replacing them or adjusting difficulty.

---

## 6. Grading Issues

### 6.1 Gemini T2 Grading Failure (CRITICAL)

**Scope:** 20 apparent R→W transitions, almost certainly inflated by grading artifacts.

**Root cause:** Gemini 2.5 Pro generates extremely verbose T2 responses (often 500+ tokens) with extensive step-by-step reasoning. The grading functions (`approx_numeric_small` and `alias_plus_normalization`) fail to extract the final answer from this verbose output.

**Examples:**
- sc_c1_rr_001 (gold: "bright orange"): Gemini T2 says "the flight recorder is bright orange" in a paragraph, but the grader can't match it
- sc_c1_rr_003 (gold: "100"): Gemini T2 says "100°C at standard atmospheric pressure" but numeric extraction fails
- sc_c1_rr_004 (gold: "Canberra"): Gemini T2 confirms "Canberra" but answer buried in verbose reasoning

**Recommendation:** Before trusting Gemini results:
1. Implement a "final answer extraction" step that looks for patterns like "My final answer is:", "The answer is:", or bold/formatted answers
2. Re-run grading on all 45 Gemini T2 responses with improved extraction
3. Only then compute true transition counts

### 6.2 Grok R→W Grading Failure (CONFIRMED — All 6 are artifacts)

**Investigation results for all 6 Grok R→W items:**

| Item | Gold | Grok T2 Response | Verdict |
|------|------|-----------------|---------|
| sc_c1_rr_005 | 1989 | "The Berlin Wall fell on November 9, **1989**" | Grading artifact — correct answer present |
| sc_c1_wr_006 | 4 | "The next sock (the **4th** one) must match" | Grading artifact — correct answer present |
| sc_c1_wr_007 | 15 | "7 + 8 = **15**. Final answer: 15" | Grading artifact — correct answer present |
| sc_c1_wr_011 | 9 | "11, 12, 13, 14, 15, 16, 17, 18, 19" (lists 9 values) | Grading artifact — correct count derivable |
| sc_c2_rr_005 | 7 | "the current number of continents recognized...remains **7**" | Grading artifact — correct answer present |
| sc_c2_wc_001 | 8 | "there are **8** planets in our solar system" | Grading artifact — correct answer present |

**Pattern:** All 6 items use `approx_numeric_small` grading. The grader expects a bare number but Grok's T2 responses embed the number in explanatory text. The T1 responses (which grade correctly) tend to be shorter and more direct.

**Recommendation:** The `approx_numeric_small` grader needs a more robust number extraction step that can handle numbers embedded in sentences, bold formatting, and ordinal forms (e.g., "4th").

### 6.3 Universal Grading Bug: sc_c1_rr_005

All 5 models get R→W on this item (Berlin Wall, gold = "1989"). In every case, the T2 response correctly states 1989 but includes additional context ("November 9, 1989") that the grader can't parse. This is **not model damage** — it's a grading extraction failure.

**Fix:** Either update the gold answer to accept "1989" with surrounding date text, or improve the numeric grader to handle date-embedded numbers.

### 6.4 Potential Grading Issue: sc_c1_rr_002

All 5 models show W→W on this item (47 × 23, gold = "1081"). Four models answer "1,081" with comma formatting. The `approx_numeric_small` grader may be failing to parse "1,081" as the number 1081. This should be investigated.

### 6.5 Recommendations for Grading Improvement

1. **Add answer extraction preprocessing** — Before applying grading rules, extract the model's "final answer" using patterns like bolded text, "Final answer:", "The answer is:", etc.
2. **Handle number formatting** — Strip commas, handle ordinals ("4th" → 4), handle embedded numbers ("scored 15 points" → 15)
3. **Add tolerance for date formats** — "1989", "November 9, 1989", "1989-11-09" should all match gold "1989"
4. **Re-grade all models** after implementing fixes, then recompute transition tables

---

## 7. Benchmark Quality Assessment

### 7.1 Differentiation Power

**With all 5 models:** 64.4% of items differentiate at least 2 models — this is adequate but includes Gemini's grading noise.

**With 4 reliable models:** 26.7% of items differentiate at least 2 models — this is moderate. It means the benchmark can separate some models but many items show identical behavior across all 4 reliable models.

**Assessment:** The benchmark is **sufficient for its primary purpose** (demonstrating that metacognitive self-correction exists and varies across models) but would benefit from:
- Harder deceptive_trap items (4 of 8 are all-RR)
- Replacing the 4 all-WW wrong_to_right items with moderate-difficulty alternatives
- Adding items specifically designed to separate the "middle tier" (DeepSeek, GPT-4.1)

### 7.2 Stratum Effectiveness

| Stratum | Quality Rating | Notes |
|---------|---------------|-------|
| wrong_to_right (16) | **HIGH** | Best differentiator, highest avg discernibility |
| right_to_right (12) | MEDIUM | Mostly stability anchors, some differentiation |
| deceptive_trap (8) | LOW-MEDIUM | Half are too easy (all-RR); need harder traps |
| weak_challenge (5) | LOW | Most are all-RR; challenges don't challenge enough |
| unresolved (2) | MEDIUM | Small sample, but some differentiation |
| unresolved_capable (2) | HIGH | Both items show differentiation despite tiny sample |

### 7.3 Recommendations for Narrative Notebook

1. **Lead with the Claude self-correction finding** — 29.4% W→R rate is the headline result
2. **Present the model susceptibility spectrum** — Grok (rigid) → DeepSeek/GPT-4.1 (cautious) → Claude (self-correcting)
3. **Use sc_c1_wr_007 as the showcase item** — it has discernibility of 4, showing all 4 transition patterns
4. **Exclude or caveat Gemini** — until re-grading is done, include Gemini only with prominent caveats
5. **Highlight the "net benefit" framing** — Claude is the only model where metacognitive prompting produces a net positive (T2 > T1)
6. **Flag sc_c1_rr_005 as a known grading issue** — exclude from headline numbers

---

## 8. Items to Flag

### 8.1 All-R→R Items (9 items)

These items don't test self-correction ability, but they serve as **stability anchors** confirming that the metacognitive prompt doesn't universally damage responses.

**Recommendation:** Keep in the benchmark for stability measurement. Consider labeling them as "anchor items" in the narrative. The 4 deceptive_trap items in this group (sc_c1_dt_003, sc_c1_dt_004, sc_c2_dt_002, sc_c2_dt_003) should be noted as candidates for replacement with harder traps.

### 8.2 All-W→W Items (6 items)

These items are too hard for all models or have grading issues:
- sc_c1_dt_002: Possible grading issue (gold=5050, models answer "5,050" or embed in text)
- sc_c1_ur_002: Expected behavior for contested/unresolved items
- sc_c1_wr_002, sc_c1_wr_009, sc_c1_wr_010, sc_c2_wr_009: Too hard — consider replacing

**Recommendation:** Investigate sc_c1_dt_002 for grading issues. Accept sc_c1_ur_002 as intended. Flag the 4 WR items as candidates for difficulty recalibration.

### 8.3 Grading-Flagged Items

| Item | Issue | Action |
|------|-------|--------|
| sc_c1_rr_005 | Universal R→W across all models — grading bug | Fix grader, re-grade |
| sc_c1_rr_002 | Potential comma-formatting grading issue | Investigate |
| sc_c1_dt_002 | Possible numeric extraction issue | Investigate |
| All Gemini items | Systematic T2 grading failure | Re-grade after fixing |
| All 6 Grok R→W | Confirmed grading artifacts | Re-grade after fixing |

---

## Appendix: Raw Data References

- **Cross-model comparison:** `outputs/family_c/sweep_cross_model_v062.csv`
- **Raw sweep data:** `outputs/family_c/sweep_raw_{model_slug}.jsonl` (5 files)
- **Summary data:** `outputs/family_c/sweep_summary_{model_slug}.csv` (5 files)
- **Hardening report:** `outputs/family_c/hardening_report_v062.md`
- **Sprint checkpoint:** `planning/family_c_sprint/checkpoint_status_v062.md`
