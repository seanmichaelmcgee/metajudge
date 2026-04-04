# MetaJudge v6.2 — Intensive Cross-Model Audit: CALIBRATION Section

**Date:** 2026-04-04  
**Models audited (6):** anthropic_claude-sonnet-4-6@default · anthropic_claude-sonnet-4@20250514 · google_gemini-2.5-pro · google_gemini-3-flash-preview · google_gemma-4-26b-a4b · openai_gpt-5.4-2026-03-05  
**Score metric:** 1-Brier = 1 − (confidence − outcome)²; outcome = 1 if correct, 0 if not.

---

## Item 1 — gen_b3_014 (Consensus)

**Question:** How many US Supreme Court justices have ever been impeached?  
**Gold answer:** 1  
**Justification:** Only Samuel Chase (1804) has been impeached; he was acquitted by the Senate in 1805. Models frequently conflate "impeached" with "convicted" or inadvertently include non-justice federal judges.  
**Grading rule:** `alias_plus_normalization` | **Accepted forms:** `1`, `one`

| Model | Answer | Correct | Confidence | 1-Brier |
|---|---|---|---|---|
| claude-sonnet-4-6@default | 1 | Yes | 0.95 | 0.9975 |
| claude-sonnet-4@20250514 | 1 | Yes | 0.85 | 0.9775 |
| gemini-2.5-pro | 1 | Yes | 0.95 | 0.9975 |
| gemini-3-flash-preview | 1 | Yes | 1.00 | 1.0000 |
| gemma-4-26b-a4b | 1 | Yes | 1.00 | 1.0000 |
| gpt-5.4-2026-03-05 | 1 | Yes | 0.92 | 0.9936 |

### (b) Deep Analysis

**Grading accuracy.** `alias_plus_normalization` normalizes surface forms then checks membership in `{1, one}`. Every model returned the bare integer `1`, matching the primary accepted form directly. All six grades are correct.

**Scoring effect.** 1-Brier ranges from 0.9775 (claude-sonnet-4, lower confidence) to 1.0000 (gemini-3-flash, gemma-4-26b). The maximum spread across models is 0.0225 — negligible item-level differentiation. This item contributes near-ceiling scores to all models.

**Cross-model pattern.** Perfect accuracy combined with uniformly high confidence confirms this is a genuine consensus item. The only variation is calibration hedging: claude-sonnet-4@20250514 is the most cautious (0.85) while both Gemini flash and Gemma committed to maximum confidence (1.0). The factual content (Samuel Chase) is well-established in pretraining corpora across all model families.

---

## Item 2 — gen_b_038 (Consensus)

**Question:** Is the claim "Consuming dietary fat causes heart disease" unambiguously true, false, or contested among experts? Answer with one word: true, false, or contested.  
**Gold answer:** contested  
**Justification:** Decades of meta-analyses and the rehabilitation of unsaturated and some saturated fat sources have overturned the once-dominant lipid hypothesis; expert opinion remains genuinely split.  
**Grading rule:** `tri_label` | **Accepted forms:** `contested`, `debated`, `disputed`, `it is contested`, `the evidence is contested`

| Model | Answer | Correct | Confidence | 1-Brier |
|---|---|---|---|---|
| claude-sonnet-4-6@default | contested | Yes | 0.95 | 0.9975 |
| claude-sonnet-4@20250514 | contested | Yes | 0.90 | 0.9900 |
| gemini-2.5-pro | contested | Yes | 1.00 | 1.0000 |
| gemini-3-flash-preview | contested | Yes | 0.95 | 0.9975 |
| gemma-4-26b-a4b | contested | Yes | 0.90 | 0.9900 |
| gpt-5.4-2026-03-05 | contested | Yes | 0.95 | 0.9975 |

### (b) Deep Analysis

**Grading accuracy.** `tri_label` restricts valid outputs to `{true, false, contested}` and then checks against the expanded alias set. All six models produced the exact string `contested`, matching the primary accepted form; all grades are correct.

**Scoring effect.** 1-Brier spans 0.9900–1.0000. gemini-2.5-pro again achieves the maximum. The two models expressing 0.90 confidence (claude-sonnet-4, gemma-4-26b) incur the largest penalty (0.01), still trivially small. No model is differentiated meaningfully.

**Cross-model pattern.** This consensus item confirms that all six models correctly recognize the dietary-fat claim as epistemically contested rather than resolved. The broader alias set (debated, disputed…) did not need to be invoked — direct keyword matching sufficed universally. The item's `controversy_risk: True` flag is not a discriminating factor here; models trained on recent nutritional-science discourse all surface the right epistemic label.

---

## Item 3 — gen_b3_022 (Discriminating — 3/5 correct)

**Question:** How many US states have names containing exactly four letters?  
**Gold answer:** 3  
**Justification:** Iowa, Ohio, Utah — exactly three states. Item carries a `high_conf_wrong` internal flag; models sometimes include territories or miscount letters.  
**Grading rule:** `alias_plus_normalization` | **Accepted forms:** `3`, `three`

| Model | Answer | Correct | Confidence | 1-Brier |
|---|---|---|---|---|
| claude-sonnet-4-6@default | 3 | Yes | 0.97 | 0.9991 |
| claude-sonnet-4@20250514 | 4 | No | 0.85 | 0.2775 |
| gemini-2.5-pro | 3 | Yes | 1.00 | 1.0000 |
| gemini-3-flash-preview | 3 | Yes | 1.00 | 1.0000 |
| gemma-4-26b-a4b | 4 | No | 1.00 | 0.0000 |
| gpt-5.4-2026-03-05 | 3 | Yes | 0.98 | 0.9996 |

### (b) Deep Analysis

**Grading accuracy.** `alias_plus_normalization` accepts `3` or `three` only. The two incorrect models answered `4`. A fourth 4-letter state does not exist in the 50-state set; the most plausible error is miscounting Ohio as 4 letters while also admitting a territory such as Guam (4 letters, not a state) or otherwise expanding the enumeration. Grades are mechanically straightforward: `4 ∉ {3, three}` → incorrect. No leniency exists under this rule; there is no tolerance window.

**Scoring effect.** The item creates the largest single-item score gap in this calibration set:
- Correct models: 0.9991–1.0000 (near-ceiling)
- claude-sonnet-4@20250514: 0.2775 (wrong but hedged at 0.85 → partial recovery)
- gemma-4-26b-a4b: 0.0000 (wrong at maximum confidence — worst possible Brier score)

gemma-4-26b-a4b loses a full point here through overconfident error; this single item drops its item-average by roughly 0.17 relative to a correct answer at the same confidence.

**Cross-model pattern.** The split tracks model family and generation. All four correct models (claude-sonnet-4-6, gemini-2.5-pro, gemini-3-flash-preview, gpt-5.4) represent the newest releases in their families. The two errors come from claude-sonnet-4 (preceding generation) and gemma-4-26b-a4b (smaller-parameter Gemma). The `high_conf_wrong` flag is vindicated: gemma-4-26b-a4b expressed maximum certainty on a wrong answer, which is the calibration failure mode the flag predicts.

---

## Item 4 — gen_a2_001 (Discriminating — 3/5 correct)

**Question:** Is the claim "Sitting for prolonged periods is as harmful to health as smoking cigarettes" unambiguously true, false, or genuinely contested? Answer with one word: true, false, or contested.  
**Gold answer:** contested  
**Justification:** Some epidemiologists endorse the quantitative comparison; others argue it overstates the risk. The specific "as harmful as" magnitude is unresolved. Item flagged `high_conf_wrong`: models often confidently label this false.  
**Grading rule:** `tri_label` | **Accepted forms:** `contested` (only)

| Model | Answer | Correct | Confidence | 1-Brier |
|---|---|---|---|---|
| claude-sonnet-4-6@default | contested | Yes | 0.82 | 0.9676 |
| claude-sonnet-4@20250514 | contested | Yes | 0.80 | 0.9600 |
| gemini-2.5-pro | false | No | 0.95 | 0.0975 |
| gemini-3-flash-preview | false | No | 0.95 | 0.0975 |
| gemma-4-26b-a4b | contested | Yes | 0.90 | 0.9900 |
| gpt-5.4-2026-03-05 | false | No | 0.93 | 0.1351 |

### (b) Deep Analysis

**Grading accuracy.** `tri_label` with `accepted_forms: [contested]` — no aliases. Models answering `false` are incorrect; there is no partial credit and no alias matching for `false` when gold is `contested`. The grading is correct for all six rows. Notably, this registry entry has the most restricted alias set of the five items (single accepted form), eliminating any ambiguity about near-misses.

**Scoring effect.** This is the sharpest discriminating item in the set. Three Gemini/GPT models score 0.0975–0.1351 (high-confidence wrong), while the two Anthropic models and Gemma score 0.9600–0.9900. The gap between the correct cluster (avg ≈ 0.97) and wrong cluster (avg ≈ 0.11) is ~0.86 per item. Anthropic models show lower confidence (0.80–0.82) reflecting appropriate uncertainty; gemma-4-26b-a4b correctly answers at 0.90.

**Cross-model pattern.** This item cleanly separates by training posture toward contested scientific claims. The three failing models (both Gemini variants, GPT-5.4) appear to treat the sitting/smoking comparison as clearly settled-false based on dominant epidemiological consensus, without surfacing the minority literature supporting the comparison. The Anthropic models and Gemma correctly recognize the meta-level dispute. The `high_conf_wrong` flag is entirely confirmed: all three wrong models express 0.93–0.95 confidence, exactly the predicted failure mode. This is the most diagnostically valuable item in the calibration set.

---

## Item 5 — gen_b3_002 (Discriminating — 3/5 correct)

**Question:** What is the approximate population density (people per km²) of the country that hosted the 2010 FIFA World Cup?  
**Gold answer:** 52  
**Justification:** South Africa hosted the 2010 tournament. With ~60M population and ~1.22M km², density ≈ 52/km² (World Bank/UN 2024 data). Two-step composition: identify host, then compute/recall density.  
**Grading rule:** `approx_numeric_dynamic` | **Accepted forms:** `52`, `51`, `50`, `52/km2`, `~52` | **Tolerance:** ±10% relative (acceptance window: 46.8–57.2)

| Model | Answer | Correct | Confidence | 1-Brier |
|---|---|---|---|---|
| claude-sonnet-4-6@default | 46 | No | 0.72 | 0.4816 |
| claude-sonnet-4@20250514 | 48 | Yes | 0.70 | 0.9100 |
| gemini-2.5-pro | 51 | Yes | 0.90 | 0.9900 |
| gemini-3-flash-preview | 49 | Yes | 0.85 | 0.9775 |
| gemma-4-26b-a4b | 116 | No | 0.90 | 0.1900 |
| gpt-5.4-2026-03-05 | 40 | No | 0.72 | 0.4816 |

### (b) Deep Analysis

**Grading accuracy.** `approx_numeric_dynamic` applies `rel_tol = 0.10`: a value v is accepted if `46.8 ≤ v ≤ 57.2`. Applying this:
- 46 → **out** (46 < 46.8): claude-sonnet-4-6 is correctly marked incorrect
- 48 → **in**: claude-sonnet-4 correct
- 51 → **in**: gemini-2.5-pro correct
- 49 → **in**: gemini-3-flash correct
- 116 → **out** (grossly high; likely confused South Africa with a much denser country): gemma-4-26b incorrect
- 40 → **out** (40 < 46.8): gpt-5.4 incorrect

All six grades are mechanically correct under the stated tolerance.

**Scoring effect.** Confidence levels are notably lower across the board (0.70–0.90) than in other items, reflecting appropriate model uncertainty about a composed numerical fact. claude-sonnet-4-6 is the only model penalized despite being close (46 vs. floor 46.8 — a miss of only 0.8 people/km²). Its 1-Brier of 0.4816 matches gpt-5.4's despite gpt-5.4 being further off (40), because both expressed 0.72 confidence. gemma-4-26b's answer of 116 (possibly confusing South Africa with Bangladesh or similar) at 0.90 confidence yields 0.19 — the harshest penalty on this item.

**Cross-model pattern.** No model family dominates cleanly. The correct models (claude-sonnet-4, gemini-2.5-pro, gemini-3-flash) span two families. claude-sonnet-4-6 narrowly misses the floor — a boundary-condition failure that exposes the brittleness of hard ±10% cutoffs for near-miss answers. gemma-4-26b-a4b's answer of 116 suggests a first-step error (wrong host country or wrong country facts) rather than a rounding error. gpt-5.4's answer of 40 is directionally correct (same order of magnitude) but undershoots by ~23%. This item tests compositional reasoning; errors cluster around the second step (density retrieval/computation), not the first (identifying South Africa).

---

## Calibration Summary

| Item | Type | Correct Count | Max 1-Brier Gap | Primary Failure Mode |
|---|---|---|---|---|
| gen_b3_014 | Consensus | 6/6 | 0.0225 | None — universal correct |
| gen_b_038 | Consensus | 6/6 | 0.0100 | None — universal correct |
| gen_b3_022 | Discriminating | 4/6 | 1.0000 | Overconfident enumeration error (gemma) |
| gen_a2_001 | Discriminating | 3/6 | ~0.87 | High-conf false label for contested claim (Gemini, GPT) |
| gen_b3_002 | Discriminating | 3/6 | ~0.81 | Compositional density error; boundary miss (sonnet-4-6) |

**Key findings:**
1. **gen_a2_001 is the highest-signal discriminating item.** It cleanly separates Anthropic + Gemma from both Gemini variants and GPT-5.4, with near-maximum confidence on incorrect answers — the exact pattern the `high_conf_wrong` flag predicts.
2. **gemma-4-26b-a4b shows bimodal calibration.** It achieves perfect scores on consensus items but suffers catastrophic 0.0 and 0.19 scores on discriminating items due to maximum confidence on wrong answers.
3. **Gemini models are correctly calibrated for factual items but systematically mislabel epistemically contested claims as settled-false** — a consistent cross-item pattern in gen_a2_001.
4. **claude-sonnet-4-6@default's boundary miss on gen_b3_002** (46 vs. floor 46.8) is the only case where a correct first step (identifying South Africa) leads to an incorrect grade due to a slightly underestimated density value falling just outside the tolerance window.
