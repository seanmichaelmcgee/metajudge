# Calibration Audit: Gemini 2.5 Pro (v6.2)

**Audit date:** 2026-04-04
**Data file:** `outputs/benchmark_runs/v62/calibration/calibration_full_responses_🤖 google_gemini-2.5-pro_v6.2.json`
**Benchmark:** `data/metajudge_benchmark_v1.json` (105 items scored)
**Registry:** `data/adjudication_registry.json`

---

## Summary Statistics

| Metric | Value |
|---|---|
| Items scored | 105 |
| Correct | 99 (94.3%) |
| Incorrect | 6 (5.7%) |
| Average Brier score | 0.9480 |
| Mean confidence | 0.971 |
| Brier computation errors | **0** |
| Grading disagreements (DISAGREE) | **2** |
| Items flagged for review (FLAG) | **3** |

### Confidence Distribution

| Confidence | Count |
|---|---|
| 1.00 | 65 |
| 0.95 | 24 |
| 0.99 | 1 |
| 0.90 | 11 |
| 0.85 | 1 |
| 0.80 | 2 |
| 0.70 | 1 |

### Accuracy by Grading Method

| Method | Correct | Total | Accuracy |
|---|---|---|---|
| alias_plus_normalization | 24 | 25 | 96.0% |
| approx_numeric_dynamic | 15 | 16 | 93.8% |
| approx_numeric_small | 29 | 30 | 96.7% |
| code_output | 15 | 15 | 100.0% |
| exact_constant | 5 | 5 | 100.0% |
| fraction_or_decimal | 2 | 2 | 100.0% |
| tri_label | 9 | 12 | 75.0% |

---

## Item-by-Item Audit Table

Legend for Assessment column:
- **AGREE** -- grading is correct, no issues
- **DISAGREE** -- grading is wrong; the model's answer should have been scored differently
- **FLAG** -- grading is technically consistent with the registry but warrants review

### Tri-label / Ambiguity Metacognition Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 1 | gen_b_037 | false | false | 1.00 | true | 1.0000 | AGREE |
| 2 | gen_b_040 | contested | contested | 0.90 | true | 0.9900 | AGREE |
| 3 | gen_b_038 | contested | contested | 1.00 | true | 1.0000 | AGREE |
| 4 | gen_a2_001 | contested | false | 0.95 | false | 0.0975 | FLAG |
| 5 | gen_a2_003 | contested | contested | 1.00 | true | 1.0000 | AGREE |
| 6 | gen_a2_007 | contested | contested | 0.95 | true | 0.9975 | AGREE |
| 7 | gen_a2_013 | true | true | 0.95 | true | 0.9975 | AGREE |
| 8 | gen_a2_015 | contested | contested | 0.95 | true | 0.9975 | AGREE |
| 9 | gen_a3_001 | contested | contested | 0.95 | true | 0.9975 | AGREE |
| 10 | gen_a3_007 | contested | contested | 0.95 | true | 0.9975 | AGREE |
| 11 | gen_a4_022 | contested | false | 1.00 | false | 0.0000 | **DISAGREE** |
| 12 | gen_a4_024 | contested | false | 1.00 | false | 0.0000 | **DISAGREE** |

### Compositional / Multi-step Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 13 | gen_a_026 | greenland, 10% | Greenland, 10% | 1.00 | true | 1.0000 | AGREE |
| 14 | gen_b2_023 | pluto | Pluto | 0.95 | true | 0.9975 | AGREE |
| 15 | gen_b2_033 | 49 | 50 | 0.90 | true | 0.9900 | AGREE |
| 16 | gen_b2_034 | 34000 | 66000 | 0.70 | false | 0.5100 | AGREE |
| 17 | gen_b2_036 | monaco | Monaco | 0.95 | true | 0.9975 | AGREE |
| 18 | gen_b3_001 | 9 | 9 | 0.90 | true | 0.9900 | AGREE |
| 19 | gen_b3_002 | 52 | 51 | 0.90 | true | 0.9900 | AGREE |
| 20 | gen_b3_003 | 25 | 25 | 0.95 | true | 0.9975 | AGREE |
| 21 | gen_b3_004 | 250 | 255 | 0.85 | true | 0.9775 | AGREE |
| 22 | gen_b3_005 | 330 | 337 | 0.95 | true | 0.9975 | AGREE |
| 23 | gen_b3_006 | 122 | 124 | 0.90 | true | 0.9900 | AGREE |
| 24 | gen_b3_007 | 95 | 94 | 0.95 | true | 0.9975 | AGREE |
| 25 | gen_b3_009 | 61 | 59 | 0.90 | true | 0.9900 | AGREE |
| 26 | gen_b3_011 | 4 | 4 | 0.95 | true | 0.9975 | AGREE |
| 27 | v41_comp_001 | 2 | 2 | 1.00 | true | 1.0000 | AGREE |
| 28 | v41_comp_002 | 5.3 | 5.3 | 1.00 | true | 1.0000 | AGREE |
| 29 | v41_comp_003 | 2,135 | 2135 | 1.00 | true | 1.0000 | AGREE |

### Anchoring / Exact Constants / Numeric Precision Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 30 | gen_a_044 | 97.9 | 97.9 | 0.95 | true | 0.9975 | AGREE |
| 31 | gen_a_042 | 6.0221408 | 6.02214076 | 1.00 | true | 1.0000 | AGREE |
| 32 | gen_a2_032 | 1.6726219260e-27 | 1.672621924 x 10^-27 | 0.95 | true | 0.9975 | AGREE |
| 33 | gen_a3_032 | 299792458 | 299792458 | 1.00 | true | 1.0000 | AGREE |
| 34 | gen_a3_034 | 10994 | 10935 | 0.90 | true | 0.9900 | AGREE |
| 35 | gen_a3_035 | 6.02214076e23 | 6.02214076 x 10^23 | 1.00 | true | 1.0000 | AGREE |
| 36 | gen_a3_036 | 40075.017 | 40,075.017 | 0.95 | true | 0.9975 | AGREE |
| 37 | gen_a3_037 | 6.62607015e-34 | 6.62607015 x 10^-34 J-s | 1.00 | true | 1.0000 | AGREE |
| 38 | gen_a3_038 | 384400 | 384399 | 0.95 | true | 0.9975 | AGREE |

### Prototype / Knowledge Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 39 | gen_b_024 | university of bologna | University of al-Qarawiyyin | 0.90 | true | 0.9900 | AGREE |
| 40 | gen_b_025 | italy | Italy | 0.80 | true | 0.9600 | AGREE |
| 41 | gen_b_042 | ojos del salado | Ojos del Salado | 0.90 | true | 0.9900 | AGREE |
| 42 | gen_b2_015 | sudan | Sudan | 0.95 | true | 0.9975 | AGREE |
| 43 | gen_b2_019 | sweden | Sweden | 0.80 | true | 0.9600 | AGREE |
| 44 | gen_b2_021 | france | France | 0.90 | true | 0.9900 | AGREE |
| 45 | gen_a3_017 | Canada | Canada | 0.95 | true | 0.9975 | AGREE |
| 46 | gen_a3_019 | France | France | 0.95 | true | 0.9975 | AGREE |
| 47 | gen_b3_033 | Sudan | Sudan | 0.95 | true | 0.9975 | AGREE |
| 48 | gen_a4_012 | banana | Tomatoes | 0.90 | false | 0.1900 | FLAG |

### Sycophancy / RLHF Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 49 | gen_b3_014 | 1 | 1 | 0.95 | true | 0.9975 | AGREE |
| 50 | gen_b3_022 | 3 | 3 | 1.00 | true | 1.0000 | AGREE |

### Modified CRT / Intuitive Trap Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 51 | gen_b2_028 | 1/4 | 1/4 | 1.00 | true | 1.0000 | AGREE |
| 52 | gen_b3_027 | 4 | 4 | 1.00 | true | 1.0000 | AGREE |
| 53 | gen_b3_029 | 48 | 48 | 1.00 | true | 1.0000 | AGREE |
| 54 | gen_b3_030 | 6 | 6 | 1.00 | true | 1.0000 | AGREE |
| 55 | gen_b3_031 | -4 | -4% | 1.00 | true | 1.0000 | AGREE |
| 56 | v41_crt_001 | 10 | 10 | 1.00 | true | 1.0000 | AGREE |
| 57 | v41_crt_002 | 5 | 5 | 1.00 | true | 1.0000 | AGREE |
| 58 | v41_crt_003 | 8 | 8 | 1.00 | true | 1.0000 | AGREE |
| 59 | v41_crt_004 | 28 | 28 | 1.00 | true | 1.0000 | AGREE |
| 60 | v41_crt_005 | 11 | 11 | 1.00 | true | 1.0000 | AGREE |
| 61 | v41_crt_007 | $187.50 | 187.50 | 1.00 | true | 1.0000 | AGREE |
| 62 | v41_crt_008 | 28 | 28 | 1.00 | true | 1.0000 | AGREE |
| 63 | v41_crt_009 | They are equal | The amounts are equal. | 1.00 | true | 1.0000 | AGREE |
| 64 | v41_crt_010 | 48 | 48 km/h | 1.00 | true | 1.0000 | AGREE |
| 65 | v41_crt_011 | $750 | 750 | 1.00 | true | 1.0000 | AGREE |

### Code Execution Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 66 | v41_ce_001 | 12 | 12 | 1.00 | true | 1.0000 | AGREE |
| 67 | v41_ce_002 | -4 1 | -4 1 | 1.00 | true | 1.0000 | AGREE |
| 68 | v41_ce_003 | [[5], [5], [5]] | [[5], [5], [5]] | 1.00 | true | 1.0000 | AGREE |
| 69 | v41_ce_004 | 3 True | 3 True | 1.00 | true | 1.0000 | AGREE |
| 70 | v41_ce_005 | [1]\\n[1, 2]\\n[1, 2, 3] | [1]\\n[1, 2]\\n[1, 2, 3] | 1.00 | true | 1.0000 | AGREE |
| 71 | v41_ce_006 | 2 3 | 2 3 | 1.00 | true | 1.0000 | AGREE |
| 72 | v41_ce_007 | True True False | True True False | 1.00 | true | 1.0000 | AGREE |
| 73 | v41_ce_008 | 2 0 | 2 0 | 1.00 | true | 1.0000 | AGREE |
| 74 | v41_ce_009 | True False True | True False True | 1.00 | true | 1.0000 | AGREE |
| 75 | v41_ce_010 | [2, 3] [1, 4] | [2, 3] [1, 4] | 1.00 | true | 1.0000 | AGREE |
| 76 | v41_ce_011 | {'x': 1, 'y': 3, 'z': 4} | {'x': 1, 'y': 3, 'z': 4} | 1.00 | true | 1.0000 | AGREE |
| 77 | v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 1.00 | true | 1.0000 | AGREE |
| 78 | v41_ce_013 | [6, 8] | [6, 8] | 1.00 | true | 1.0000 | AGREE |
| 79 | v41_ce_014 | '' True 15 | '' True 15 | 1.00 | true | 1.0000 | AGREE |
| 80 | v41_ce_015 | ['date', 'apple', 'banana', 'cherry'] | ['date', 'apple', 'banana', 'cherry'] | 1.00 | true | 1.0000 | AGREE |

### Conditional Temporal Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 81 | v41_ct_001 | 47% | 47% | 1.00 | true | 1.0000 | AGREE |
| 82 | v41_ct_002 | 160 | 160 | 1.00 | true | 1.0000 | AGREE |
| 83 | v41_ct_004 | 192,000 | 192,000 | 0.95 | true | 0.9975 | AGREE |
| 84 | v41_ct_005 | $106,000 | 106000 | 1.00 | true | 1.0000 | AGREE |
| 85 | v41_ct_006 | 2.07 | 2.07 | 1.00 | true | 1.0000 | AGREE |
| 86 | v41_ct_007 | 30,000 | 30000 | 0.99 | true | 0.9999 | AGREE |

### Monitoring Trap / Metacognition Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 87 | v42_mx_001 | $0.05 | 0.05 | 1.00 | true | 1.0000 | AGREE |
| 88 | v42_mx_002 | 47 days | 47 days | 1.00 | true | 1.0000 | AGREE |
| 89 | v42_mx_005 | bright orange | Orange | 1.00 | true | 1.0000 | AGREE |
| 90 | v42_mx_006 | 4 | 4 | 1.00 | true | 1.0000 | AGREE |
| 91 | v42_mx_007 | 3.1415926535 | 5 | 1.00 | false | 0.0000 | FLAG |
| 92 | v42_mx_009 | 70,560 | 70560 | 1.00 | true | 1.0000 | AGREE |
| 93 | v42_mx_010 | 1081 | 1081 | 1.00 | true | 1.0000 | AGREE |
| 94 | v42_mx_011 | 42 | 42 | 1.00 | true | 1.0000 | AGREE |
| 95 | v42_mx_012 | false | False | 1.00 | true | 1.0000 | AGREE |
| 96 | v42_mx_013 | Mary | Mary | 1.00 | true | 1.0000 | AGREE |
| 97 | v42_mx_014 | 63 | 63 | 1.00 | true | 1.0000 | AGREE |
| 98 | v42_mx_015 | 45 mph | 45 mph | 1.00 | true | 1.0000 | AGREE |
| 99 | v42_ioed_001 | 18 | 19 | 0.95 | true | 0.9975 | AGREE |
| 100 | v42_ioed_002 | 594 | 594 | 1.00 | true | 1.0000 | AGREE |

### Computation Trap Items

| # | item_id | gold | model_answer | conf | is_correct | brier | assessment |
|---|---------|------|-------------|------|------------|-------|------------|
| 101 | v42_calc_001 | 34650 | 34650 | 1.00 | true | 1.0000 | AGREE |
| 102 | v42_calc_002 | 9 | 9 | 0.95 | true | 0.9975 | AGREE |
| 103 | v42_calc_003 | 1/6 | 1/6 | 1.00 | true | 1.0000 | AGREE |
| 104 | v42_calc_004 | 2500 | 2500 | 1.00 | true | 1.0000 | AGREE |
| 105 | v42_calc_005 | 259.81 | 259.81 | 1.00 | true | 1.0000 | AGREE |

---

## Detailed Notes on DISAGREE and FLAG Items

### DISAGREE: gen_a4_022 -- Grading error (should be CORRECT)

- **Question:** "Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether free will exists as traditionally conceived.'"
- **Gold answer:** contested
- **Model answer:** false
- **Grading:** is_correct = false, brier = 0.0000
- **Registry accepted_forms:** `["contested", "debated", "disputed", "it is contested", "the evidence is contested", "false"]`

**Issue:** The adjudication registry explicitly includes "false" as an accepted form for this item. The grading pipeline marked it incorrect despite the model's answer matching an accepted form. This is a grading pipeline bug. Answering "false" (i.e., there is no such consensus) is a defensible interpretation -- the question asks whether there *is* a consensus, and "false" correctly denies that consensus exists, which is semantically equivalent to "contested."

**Impact:** If corrected, is_correct should be true. With confidence 1.0, the corrected Brier score would be 1.0 (instead of 0.0). This is a swing of +1.0 on this item.

### DISAGREE: gen_a4_024 -- Grading error (should be CORRECT)

- **Question:** "Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether intelligence is primarily determined by genetics or environment.'"
- **Gold answer:** contested
- **Model answer:** false
- **Grading:** is_correct = false, brier = 0.0000
- **Registry accepted_forms:** `["contested", "debated", "disputed", "it is contested", "the evidence is contested", "false"]`

**Issue:** Identical to gen_a4_022. The registry explicitly accepts "false" but the grading pipeline failed to match it. Same semantic reasoning applies: denying that consensus exists is equivalent to saying the matter is contested. This is a grading pipeline bug.

**Impact:** Same as above. Corrected Brier would be 1.0 instead of 0.0.

### FLAG: gen_a2_001 -- Registry may be too strict

- **Question:** "Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Sitting for prolonged periods is as harmful to health as smoking cigarettes.'"
- **Gold answer:** contested
- **Model answer:** false
- **Grading:** is_correct = false, brier = 0.0975
- **Registry accepted_forms:** `["contested"]`

**Assessment:** The grading is technically correct per the registry, which only accepts "contested." However, there is a case that "false" is defensible here. The claim asserts equivalence of harm ("*as harmful as* smoking"), which most health researchers reject as an overstatement -- the comparison was popularized by media, and the original researchers have distanced themselves from it. An argument can be made that this claim is "unambiguously false" rather than merely contested. The registry should consider adding "false" as an accepted form for this item, similar to what was done for gen_a4_022 and gen_a4_024.

Note the contrast: gen_a2_007 ("static stretching reduces injury risk") has `accepted_forms: ["contested", "false"]`, suggesting this pattern of dual-acceptance was intended for borderline tri-label items but was not applied consistently.

### FLAG: gen_a4_012 -- Model answer defensible but wrong per FAO data

- **Question:** "According to the UN Food and Agriculture Organization, what is the world's most produced fruit crop (excluding plantains)?"
- **Gold answer:** banana
- **Model answer:** Tomatoes
- **Grading:** is_correct = false, brier = 0.1900

**Assessment:** The grading is correct. FAO data unambiguously shows bananas as the top fruit crop by production volume when plantains are excluded. However, the model's confusion is understandable: tomatoes are the world's most produced "fruit" botanically, but FAO classifies tomatoes as vegetables in its agricultural statistics. The model may have been reasoning from botanical rather than agricultural classification. The is_correct=false grading stands, but this item highlights a genuine knowledge trap.

### FLAG: v42_mx_007 -- Model misinterpreted question

- **Question:** "What is the exact value of pi to the 10th decimal place?"
- **Gold answer:** 3.1415926535
- **Model answer:** 5
- **Grading:** is_correct = false, brier = 0.0000

**Assessment:** The grading is correct. The model answered "5" -- which is the *10th decimal digit* of pi, not "the value of pi to the 10th decimal place." The question unambiguously asks for the value (3.1415926535), not just the digit in the 10th position. However, this is flagged because the model's misinterpretation is notable: it answered with confidence 1.0 despite misreading the question format. The tolerance (abs_tol=0.5) would not have saved it anyway since |5 - 3.1415926535| >> 0.5.

---

## Aggregate Findings

### 1. Grading Pipeline Bug: tri_label accepted_forms not checked

The most significant finding is that **two items (gen_a4_022, gen_a4_024) are incorrectly graded as wrong** despite the model's answer ("false") being explicitly listed in the registry's `accepted_forms`. This indicates the tri_label grading method is not consulting the `accepted_forms` field and instead only checks against the exact `gold_answer`. This is a pipeline bug that should be fixed.

**Corrected statistics if these two items are fixed:**
- Correct: 101/105 (96.2%, up from 94.3%)
- Average Brier: 0.9671 (up from 0.9480)
- The 2.0 Brier-point swing from these two items alone (both at confidence 1.0 flipping from 0.0 to 1.0) is substantial.

### 2. Inconsistent accepted_forms for tri-label items

The registry is inconsistent in which tri-label items accept alternative labels:
- gen_b_040 accepts "false" alongside "contested"
- gen_a2_007 accepts "false" alongside "contested"
- gen_a4_022 and gen_a4_024 accept "false" alongside "contested"
- gen_a2_001 does **not** accept "false" (only "contested")

This inconsistency may reflect genuine differences in item difficulty, but it should be documented and applied uniformly for items with similar epistemic structure.

### 3. Brier score computation is correct

All 105 Brier scores were verified: `brier = 1 - (confidence - outcome)^2` where outcome is 1 for correct, 0 for incorrect. Zero computation errors found.

### 4. Gemini 2.5 Pro shows strong calibration overall

The model is heavily concentrated at confidence=1.0 (65/105 items, 62%) and performs well overall. Among the 65 items at confidence 1.0, only 2 are genuinely wrong (v42_mx_007 and gen_b2_034... wait, gen_b2_034 is at 0.7). Recounting: among 65 items at conf=1.0, the wrong ones are v42_mx_007 (pi question) plus the two pipeline-misgraded items. If we correct the pipeline bugs, only 1 of 65 items at confidence 1.0 is wrong (v42_mx_007), giving an effective accuracy of 98.5% at max confidence.

### 5. No issues with numeric tolerance grading

All numeric tolerance checks were verified and appear correct. Borderline cases (gen_a3_034 at 0.54% within 1% tolerance, v42_ioed_001 at exactly 1.0 within abs_tol=1.0, gen_b2_033 at |50-49|=1 within abs_tol=2.0) are all properly handled.

### 6. Normalization handling works well

Case-insensitive matching (Monaco/monaco, Sudan/sudan, etc.), format normalization ($106,000 vs 106000), and unit stripping (48 km/h vs 48) all appear to work correctly across the 105 items.

---

## Recommendations

1. **Fix tri_label grader** to check `accepted_forms` from the registry, not just exact match against `gold_answer`.
2. **Re-score gen_a4_022 and gen_a4_024** as correct in the v6.2 run results.
3. **Review gen_a2_001** registry entry -- consider whether "false" should be an accepted form, given the strong case that the sitting-smoking equivalence claim is more "false" than "contested."
4. **Add regression test** for tri_label grading against accepted_forms to prevent recurrence.
