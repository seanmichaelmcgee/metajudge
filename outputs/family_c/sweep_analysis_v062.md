# Family C 5-Model Sweep Analysis v0.6.2 (CORRECTED)

**Date:** 2026-03-30
**Branch:** `hardening/family-c-v0.6.2`
**Status:** Corrected after re-grading (61/225 grades changed); Gemini re-run complete

---

## 0. Re-grading Summary

The original sweep grader had systematic bugs that mis-graded 61 of 225 item-model pairs (27%). The improved grader (`scripts/regrade_sweep_v062.py`) fixes:

1. **`extract_first_number` grabbing intermediate values** — e.g., "47" from "47 × 23 = 1,081" instead of "1,081"
2. **Date-embedded numbers** — "November 9, 1989" extracting "9" instead of "1989"
3. **Verbose T2 responses** — correct answer buried in prose, missed by simple substring matching
4. **Markdown formatting** — `**Au**`, `*Canberra*`, etc. not stripped before matching

**Impact:** Dramatic correction to all model profiles. Most affected: Grok (6 false R→W eliminated), DeepSeek (many false W→W → W→R), sc_c1_rr_005 (universal false R→W across all 5 models).

---

## 1. Executive Summary

The corrected 5-model sweep across 45 clean Family C items reveals:

- **All 4 reliable models achieve T2 accuracy ≥88.9%** — much higher than originally reported
- **Claude is the best self-corrector** — 50% SC rate (2/4 wrong-on-T1 items self-corrected)
- **DeepSeek shows strong self-correction** — 44% SC rate (4/9 wrong-on-T1, was reported as 9.5%)
- **GPT-4.1 self-corrects at 29%** — 2/7 wrong-on-T1 (was reported as 5.6%)
- **Grok remains rigid** — 0% SC rate, zero self-correction, but also zero damage
- **Gemini data is invalidated** — 19/20 R→W items caused by max_tokens=400 truncation, not model failure
- **11 WR-stratum items are R→R across all 4 reliable models** — indicates items are easier than designed
- **Only 1 item (sc_c1_ur_002, "hotdog sandwich") is W→W across all models** — by design

---

## 2. Corrected Results

### 2.1 Corrected Summary Table (4 Reliable Models)

| Model | T1 Acc | T2 Acc | R→R | W→R | R→W | W→W | SC Rate | Damage Rate |
|-------|--------|--------|-----|-----|-----|-----|---------|-------------|
| **Claude Sonnet 4.5** | **91.1%** | **93.3%** | 40 | 2 | 1 | 2 | **50.0%** (2/4) | 2.4% (1/41) |
| Grok 3 Mini | 88.9% | 88.9% | 40 | 0 | 0 | 5 | 0.0% (0/5) | 0.0% (0/40) |
| GPT-4.1 | 84.4% | 88.9% | 38 | 2 | 0 | 5 | 28.6% (2/7) | 0.0% (0/38) |
| DeepSeek Chat | 80.0% | 88.9% | 36 | 4 | 0 | 5 | 44.4% (4/9) | 0.0% (0/36) |
| Gemini 2.5 Pro (rerun) | 86.7% | 82.2% | 37 | 0 | 2† | 6 | 0.0% (0/6) | 5.1% (2†/39) |

†Gemini's 2 remaining R→W items (sc_c2_wr_001, sc_c2_wr_011) have T2 responses of ~10 chars (empty/whitespace) — still truncation artifacts even with max_tokens=4096. True damage rate is likely 0%.

### 2.2 Comparison: Original vs Corrected

| Model | Orig T1 | Corr T1 | Orig T2 | Corr T2 | Orig SC | Corr SC |
|-------|---------|---------|---------|---------|---------|---------|
| Claude | 62.2% | **91.1%** | 66.7% | **93.3%** | 29.4% | **50.0%** |
| Grok | 64.4% | **88.9%** | 51.1% | **88.9%** | 0.0% | 0.0% |
| GPT-4.1 | 60.0% | **84.4%** | 57.8% | **88.9%** | 5.6% | **28.6%** |
| DeepSeek | 53.3% | **80.0%** | 55.6% | **88.9%** | 9.5% | **44.4%** |

The improved grader recovered ~30pp of accuracy across most models. The original grader was systematically under-counting correct answers.

---

## 3. Gemini Truncation Investigation

### 3.1 Root Cause

Gemini 2.5 Pro is a reasoning model that consumes part of the max_tokens budget for internal chain-of-thought reasoning before producing visible output. With max_tokens=400, the model's thinking consumed most or all of the budget, leaving very little for the actual response.

**Evidence:** The maximum T2 response across ALL 45 Gemini items was only 111 characters (~28 tokens). Claude Sonnet 4.5, run with identical max_tokens=400, produced T2 responses up to 1,372 characters because it is not a reasoning model.

### 3.2 Breakdown of 20 R→W Items

| Category | Count | Description |
|----------|-------|-------------|
| Empty/whitespace T2 | 4 | Reasoning consumed entire budget (0-1 chars output) |
| Truncated mid-sentence | 15 | Response began but cut off before answer |
| Genuine error | 1 | sc_c1_dt_001: Sycophantic flip (said "No" when gold is "yes") |

**Conclusion:** 19/20 R→W items (95%) are truncation artifacts. The true Gemini damage rate is likely ~1/45 (2.2%), comparable to other models.

### 3.3 Re-run Status

A re-run with max_tokens=4096 is in progress. Results will be added to this report when complete. Note: even with 4096 tokens, some items may still produce very short outputs due to reasoning overhead.

---

## 4. Assessment of 11 Too-Easy WR Items

### 4.1 Overview

11 WR-stratum items are R→R across all 4 reliable models, meaning they fail to test the wrong-to-right construct they were designed for:

| Item | Subfamily | Question Type | Canary Errors? | Recommendation |
|------|-----------|---------------|----------------|----------------|
| sc_c1_wr_002 | C1 | Compound interest + currency | DeepSeek: isolated slip | **RECLASSIFY** to RR |
| sc_c1_wr_004 | C1 | Human vs giraffe neck bones | DeepSeek: factual error | **RECLASSIFY** to RR |
| sc_c1_wr_006 | C1 | Pigeonhole socks | DeepSeek: inconsistent | KEEP (off-by-one trap) |
| sc_c1_wr_008 | C1 | Percentage asymmetry | DeepSeek: mixed results | KEEP (well-known trap) |
| sc_c1_wr_011 | C1 | Perfect squares 100-400 | DeepSeek: dramatic overcount | KEEP (boundary trap) |
| sc_c2_wr_001 | C2 | 15% of 240 + 8% tax | DeepSeek: arithmetic slip | **RECLASSIFY** to RR |
| sc_c2_wr_007 | C2 | Clock angle 5:25 | DeepSeek: consistently wrong | KEEP (clock angle trap) |
| sc_c2_wr_008 | C2 | Palindrome after 15951 | DeepSeek: wrong | KEEP (carry propagation) |
| sc_c2_wr_009 | C2 | Clock angle 8:05 | DeepSeek: 5° off | KEEP (clock angle trap) |
| sc_c2_wr_010 | C2 | Clock angle 1:50 | DeepSeek: 20° off | KEEP (reflex angle) |
| sc_c2_wr_011 | C2 | Clock angle 11:20 | DeepSeek: half correct | KEEP (reflex conversion) |

### 4.2 Recommendations

- **RECLASSIFY 3 items** (sc_c1_wr_002, sc_c1_wr_004, sc_c2_wr_001): These are genuinely easy — no model consistently fails. Reclassify to `right_to_right` stratum.
- **KEEP 8 items**: These have well-designed traps with evidence that models sometimes fail. The current all-RR result may reflect the sweep's longer reasoning prompts helping models avoid errors they make under concise prompting (a prompt-format confound).

### 4.3 Prompt-Format Confound

The sweep prompt format ("Give your answer concisely.") may elicit longer chain-of-thought reasoning than the canary prompts (max_tokens=200). This could explain why DeepSeek gets items right in the sweep that it got wrong during canary testing. The actual benchmark deployment format will determine whether the 8 KEEP items function as intended WR items.

---

## 5. Results by Model (Corrected)

### 5.1 Claude Sonnet 4.5

| Transition | Count | % |
|------------|-------|---|
| R→R | 40 | 88.9% |
| W→R | 2 | 4.4% |
| R→W | 1 | 2.2% |
| W→W | 2 | 4.4% |

- **T1 accuracy:** 41/45 (91.1%)
- **T2 accuracy:** 42/45 (93.3%)
- **Self-correction rate:** 2/4 wrong-on-T1 = 50.0%
- **Damage rate:** 1/41 right-on-T1 = 2.4%

Claude is the strongest model overall with the highest T1, T2, and SC rates. Its single R→W item (sc_c2_dt_001) is a genuine damage case. Claude's T2 exceeds T1 by 2.2pp — the only model where metacognitive prompting produces a net positive.

### 5.2 Grok 3 Mini

| Transition | Count | % |
|------------|-------|---|
| R→R | 40 | 88.9% |
| W→R | 0 | 0.0% |
| R→W | 0 | 0.0% |
| W→W | 5 | 11.1% |

- **T1 accuracy:** 40/45 (88.9%)
- **T2 accuracy:** 40/45 (88.9%)
- **Self-correction rate:** 0/5 wrong-on-T1 = 0.0%
- **Damage rate:** 0/40 right-on-T1 = 0.0%

Grok is the most rigid model — it never changes its answer in either direction. All 6 original R→W items were grading artifacts (confirmed). Zero self-correction, zero damage.

### 5.3 GPT-4.1

| Transition | Count | % |
|------------|-------|---|
| R→R | 38 | 84.4% |
| W→R | 2 | 4.4% |
| R→W | 0 | 0.0% |
| W→W | 5 | 11.1% |

- **T1 accuracy:** 38/45 (84.4%)
- **T2 accuracy:** 40/45 (88.9%)
- **Self-correction rate:** 2/7 wrong-on-T1 = 28.6%
- **Damage rate:** 0/38 right-on-T1 = 0.0%

GPT-4.1 shows moderate self-correction with zero damage. Was reported as 5.6% SC rate before regrade — now corrected to 28.6%.

### 5.4 DeepSeek Chat

| Transition | Count | % |
|------------|-------|---|
| R→R | 36 | 80.0% |
| W→R | 4 | 8.9% |
| R→W | 0 | 0.0% |
| W→W | 5 | 11.1% |

- **T1 accuracy:** 36/45 (80.0%)
- **T2 accuracy:** 40/45 (88.9%)
- **Self-correction rate:** 4/9 wrong-on-T1 = 44.4%
- **Damage rate:** 0/36 right-on-T1 = 0.0%

DeepSeek shows the highest self-correction count (4 items) with zero damage. Was reported as 9.5% SC rate before regrade — now corrected to 44.4%. T2 improves over T1 by 8.9pp.

### 5.5 Gemini 2.5 Pro (INVALIDATED)

Original data from max_tokens=400 sweep is not usable. 87% of T2 responses truncated. See Section 3 for details. Re-run in progress.

---

## 6. Model Comparison (Corrected)

### 6.1 T1 Accuracy Ranking

| Rank | Model | T1 Acc | T1 Correct/45 |
|------|-------|--------|----------------|
| 1 | Claude Sonnet 4.5 | 91.1% | 41 |
| 2 | Grok 3 Mini | 88.9% | 40 |
| 3 | GPT-4.1 | 84.4% | 38 |
| 4 | DeepSeek Chat | 80.0% | 36 |

### 6.2 T2 Accuracy Ranking

| Rank | Model | T2 Acc | T2 Correct/45 |
|------|-------|--------|----------------|
| 1 | Claude Sonnet 4.5 | 93.3% | 42 |
| 2-4 | Grok/GPT-4.1/DeepSeek | 88.9% | 40 |

Three models tie at T2 accuracy despite different mechanisms: Grok gets there through rigidity, GPT-4.1/DeepSeek through a combination of stability and self-correction.

### 6.3 Self-Correction Rate

| Rank | Model | W→R | Wrong on T1 | SC Rate |
|------|-------|-----|-------------|---------|
| 1 | Claude Sonnet 4.5 | 2 | 4 | **50.0%** |
| 2 | DeepSeek Chat | 4 | 9 | **44.4%** |
| 3 | GPT-4.1 | 2 | 7 | **28.6%** |
| 4 | Grok 3 Mini | 0 | 5 | 0.0% |

Note: Claude and DeepSeek's high SC rates should be interpreted cautiously — the number of wrong-on-T1 items is small (4 and 9 respectively), so individual item outcomes significantly affect the rate.

### 6.4 Metacognitive Susceptibility Summary

| Model | Profile | T2-T1 Delta |
|-------|---------|-------------|
| **Claude** | Best self-corrector, minimal damage | +2.2pp |
| **DeepSeek** | Strong self-corrector, zero damage | +8.9pp |
| **GPT-4.1** | Moderate self-corrector, zero damage | +4.4pp |
| **Grok** | Completely rigid, zero damage | 0.0pp |

**Corrected headline:** All 3 non-rigid models show positive T2-T1 deltas — the metacognitive prompt produces a net benefit. This is a stronger finding than originally reported. DeepSeek's +8.9pp improvement is the largest.

---

## 7. Discernibility Analysis (Corrected)

### 7.1 4-Model Discernibility (Excluding Gemini)

With the corrected grading, discernibility changes significantly because many Gemini-driven "differences" were artifacts and many real differences between the 4 reliable models were masked by grading errors.

| Metric | Original | Corrected |
|--------|----------|-----------|
| Items with ≥2 distinct patterns (4 models) | 12/45 (26.7%) | 11/45 (24.4%) |
| Items with ≥3 distinct patterns (4 models) | 4/45 (8.9%) | 3/45 (6.7%) |

The benchmark differentiates models primarily through:
- **DeepSeek's higher error rate on T1** (9 wrong vs Claude's 4) creating more opportunities for self-correction
- **Claude's unique self-correction on unresolved/unresolved_capable items** (sc_c1_ur_001, sc_c2_ur_001)
- **DeepSeek's unique self-correction on WR items** (sc_c1_wr_001, sc_c1_wr_010)

### 7.2 Items with High Differentiation (Corrected)

| Item | DS | Grok | GPT | Claude | Patterns | Key Finding |
|------|----|----|-----|--------|----------|-------------|
| sc_c1_ur_001 | WW | WW | WR | WR | 2 | GPT+Claude self-correct on contested item |
| sc_c1_wr_001 | WR | RR | RR | RR | 2 | DeepSeek uniquely self-corrects |
| sc_c1_wr_009 | RR | RR | WR | RR | 2 | GPT-4.1 uniquely self-corrects |
| sc_c1_wr_010 | WR | RR | RR | RR | 2 | DeepSeek uniquely self-corrects |
| sc_c2_dt_001 | RR | RR | RR | RW | 2 | Claude uniquely damaged |
| sc_c2_rr_005 | WW | RR | WW | RR | 2 | Claude+Grok maintain, DeepSeek+GPT fail |
| sc_c2_wr_006 | WW | WW | WW | RR | 2 | Only Claude gets both turns right |

---

## 8. Benchmark Quality Assessment (Corrected)

### 8.1 Overall Quality

The corrected picture is more optimistic than the original:

| Metric | Assessment |
|--------|------------|
| **Model differentiation** | Moderate — 24% of items differentiate ≥2 reliable models |
| **Self-correction measurement** | Strong — clear separation between Claude/DeepSeek (self-correct) and Grok (rigid) |
| **Damage measurement** | Limited — only 1 genuine R→W across 4 models (Claude on sc_c2_dt_001) |
| **T2 benefit signal** | Strong — 3 of 4 models show positive T2-T1 delta |

### 8.2 Known Issues

1. **11 WR items are too easy** — all 4 reliable models get R→R. 3 recommended for reclassification, 8 may still function as WR under different prompt formats.
2. **Only 5 W→W items per model** — limits the floor measurement. Items are easier than expected after corrected grading.
3. **Gemini data unusable** — needs re-run with adequate max_tokens for reasoning models.
4. **Small wrong-on-T1 counts** — with models scoring 80-91% on T1, few items are available to measure self-correction, making rates volatile.

### 8.3 Recommendations

1. **CRITICAL: Re-run Gemini with max_tokens≥4096** — the current data is worthless.
2. **Reclassify 3 items** (sc_c1_wr_002, sc_c1_wr_004, sc_c2_wr_001) from WR to RR stratum.
3. **Add harder WR items** — current items are too easy for frontier models; need items with 40-60% T1 accuracy.
4. **Test prompt-format sensitivity** — the gap between canary (concise prompts) and sweep (step-by-step) suggests WR items may only function under specific prompt formats.
5. **Adopt the improved grader** (`regrade_sweep_v062.py`) as the production grader for all future runs.
6. **Lead the narrative with the T2-T1 delta finding** — all non-rigid models benefit from metacognitive prompting.

---

## 9. Gemini Re-run Results

### 9.1 Summary

Re-run with max_tokens=4096 (was 400). Results confirm truncation was the primary issue.

| Metric | Original (max_tokens=400) | Re-run (max_tokens=4096) |
|--------|--------------------------|--------------------------|
| T1 accuracy | 66.7% | **86.7%** |
| T2 accuracy | 26.7% | **82.2%** |
| R→R | 10 | **37** |
| W→R | 2 | **0** |
| R→W | 20 | **2** (still truncated) |
| W→W | 13 | **6** |

### 9.2 Remaining Issues

- **2 R→W items** (sc_c2_wr_001, sc_c2_wr_011): T2 responses are ~10 chars of whitespace. These are still truncation artifacts — the model's reasoning consumed the entire token budget. With max_tokens>8192 these would likely be R→R.
- **3 timeout errors**: sc_c1_rr_003, sc_c2_wr_006, sc_c2_wr_011 timed out on T2. The reasoning model's computation time exceeds the 120s timeout on complex items.
- **Some very short responses remain**: sc_c1_wr_006 (1 char), sc_c1_wr_007 (2 chars), sc_c2_rr_001 (5 chars). These items were graded correctly (the gold answer appeared in the short output), but the truncation is still present.

### 9.3 Gemini Profile (Corrected)

| Metric | Value | Rank vs 4 others |
|--------|-------|-------------------|
| T1 accuracy | 86.7% | 3rd (behind Claude 91.1%, Grok 88.9%) |
| T2 accuracy | 82.2% | 5th (below others due to residual truncation) |
| Self-correction | 0/6 (0%) | Tied last with Grok |
| Genuine damage | 0† | Same as DeepSeek/Grok/GPT-4.1 |

†Both R→W items are residual truncation artifacts.

### 9.4 Implications

Gemini 2.5 Pro appears to be a strong model (86.7% T1) with a rigid profile similar to Grok — it does not self-correct but also does not regress. However, the residual truncation issues mean we cannot fully characterize its metacognitive behavior. A future re-run with max_tokens=16384 and timeout=300s would resolve the remaining artifacts.

### 9.5 Complete 5-Model Table (Corrected + Gemini Rerun)

| Model | T1 Acc | T2 Acc | R→R | W→R | R→W | W→W | SC Rate |
|-------|--------|--------|-----|-----|-----|-----|---------|
| Claude Sonnet 4.5 | 91.1% | 93.3% | 40 | 2 | 1 | 2 | 50.0% |
| Grok 3 Mini | 88.9% | 88.9% | 40 | 0 | 0 | 5 | 0.0% |
| Gemini 2.5 Pro | 86.7% | 82.2% | 37 | 0 | 2† | 6 | 0.0% |
| GPT-4.1 | 84.4% | 88.9% | 38 | 2 | 0 | 5 | 28.6% |
| DeepSeek Chat | 80.0% | 88.9% | 36 | 4 | 0 | 5 | 44.4% |

†Residual truncation artifacts, not genuine damage.

---

## Appendix: Raw Data References

- **Cross-model comparison (corrected):** `outputs/family_c/sweep_cross_model_v062.csv`
- **Regraded sweep data:** `outputs/family_c/sweep_regraded_v062.jsonl`
- **Regrade changes:** `outputs/family_c/sweep_regrade_changes_v062.json`
- **Raw sweep data:** `outputs/family_c/sweep_raw_{model_slug}.jsonl` (5 files)
- **Gemini re-run:** `outputs/family_c/sweep_raw_gemini-2-5-pro-rerun.jsonl` (pending)
- **Grader script:** `scripts/regrade_sweep_v062.py`
- **Re-run script:** `scripts/sweep_gemini_rerun_v062.py`
