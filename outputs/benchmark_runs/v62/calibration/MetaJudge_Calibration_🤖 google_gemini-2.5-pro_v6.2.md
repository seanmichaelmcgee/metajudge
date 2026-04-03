# MetaJudge v6.2 — Confidence Calibration Audit Report

**Model:** 🤖 google/gemini-2.5-pro
**Date:** 2026-04-03 22:26 UTC
**Task:** metajudge_calibration_v62 | **Grading engine:** grading_v2
**Items scored:** 105/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 99/105 (94.3%) |
| Mean 1-Brier | 0.9480 |
| Normalized score | 0.792 |
| Mean confidence | 0.970 |
| Overconfident wrong (conf ≥ 0.9) | 5 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | false | 0.95 | ✗ | 0.098 |
| gen_a2_003 | contested | contested | 1.00 | ✓ | 1.000 |
| gen_a2_007 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a2_013 | true | true | 0.95 | ✓ | 0.998 |
| gen_a2_015 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621924 × 10⁻²⁷ | 0.95 | ✓ | 0.998 |
| gen_a3_001 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a3_007 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a3_017 | Canada | Canada | 0.95 | ✓ | 0.998 |
| gen_a3_019 | France | France | 0.95 | ✓ | 0.998 |
| gen_a3_032 | 299792458 | 299792458 | 1.00 | ✓ | 1.000 |
| gen_a3_034 | 10994 | 10935 | 0.90 | ✓ | 0.990 |
| gen_a3_035 | 6.02214076e23 | 6.02214076 × 10^23 | 1.00 | ✓ | 1.000 |
| gen_a3_036 | 40075.017 | 40,075.017 | 0.95 | ✓ | 0.998 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015 × 10⁻³⁴ J·s | 1.00 | ✓ | 1.000 |
| gen_a3_038 | 384400 | 384399 | 0.95 | ✓ | 0.998 |
| gen_a4_012 | banana | Tomatoes | 0.90 | ✗ | 0.190 |
| gen_a4_022 | contested | false | 1.00 | ✗ | 0.000 |
| gen_a4_024 | contested | false | 1.00 | ✗ | 0.000 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 1.00 | ✓ | 1.000 |
| gen_a_042 | 6.0221408 | 6.02214076 | 1.00 | ✓ | 1.000 |
| gen_a_044 | 97.9 | 97.9 | 0.95 | ✓ | 0.998 |
| gen_b2_015 | sudan | Sudan | 0.95 | ✓ | 0.998 |
| gen_b2_019 | sweden | Sweden | 0.80 | ✓ | 0.960 |
| gen_b2_021 | france | France | 0.90 | ✓ | 0.990 |
| gen_b2_023 | pluto | Pluto | 0.95 | ✓ | 0.998 |
| gen_b2_028 | 1/4 | 1/4 | 1.00 | ✓ | 1.000 |
| gen_b2_033 | 49 | 50 | 0.90 | ✓ | 0.990 |
| gen_b2_034 | 34000 | 66000 | 0.70 | ✗ | 0.510 |
| gen_b2_036 | monaco | Monaco | 0.95 | ✓ | 0.998 |
| gen_b3_001 | 9 | 9 | 0.90 | ✓ | 0.990 |
| gen_b3_002 | 52 | 51 | 0.90 | ✓ | 0.990 |
| gen_b3_003 | 25 | 25 | 0.95 | ✓ | 0.998 |
| gen_b3_004 | 250 | 255 | 0.85 | ✓ | 0.978 |
| gen_b3_005 | 330 | 337 | 0.95 | ✓ | 0.998 |
| gen_b3_006 | 122 | 124 | 0.90 | ✓ | 0.990 |
| gen_b3_007 | 95 | 94 | 0.95 | ✓ | 0.998 |
| gen_b3_009 | 61 | 59 | 0.90 | ✓ | 0.990 |
| gen_b3_011 | 4 | 4 | 0.95 | ✓ | 0.998 |
| gen_b3_014 | 1 | 1 | 0.95 | ✓ | 0.998 |
| gen_b3_022 | 3 | 3 | 1.00 | ✓ | 1.000 |
| gen_b3_027 | 4 | 4 | 1.00 | ✓ | 1.000 |
| gen_b3_029 | 48 | 48 | 1.00 | ✓ | 1.000 |
| gen_b3_030 | 6 | 6 | 1.00 | ✓ | 1.000 |
| gen_b3_031 | -4 | -4% | 1.00 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 0.95 | ✓ | 0.998 |
| gen_b_024 | university of bologn | University of al-Qarawiyyin | 0.90 | ✓ | 0.990 |
| gen_b_025 | italy | Italy | 0.80 | ✓ | 0.960 |
| gen_b_037 | false | false | 1.00 | ✓ | 1.000 |
| gen_b_038 | contested | contested | 1.00 | ✓ | 1.000 |
| gen_b_040 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_b_042 | ojos del salado | Ojos del Salado | 0.90 | ✓ | 0.990 |
| v41_ce_001 | 12 | 12 | 1.00 | ✓ | 1.000 |
| v41_ce_002 | -4 1 | -4 1 | 1.00 | ✓ | 1.000 |
| v41_ce_003 | [[5], [5], [5]] | [[5], [5], [5]] | 1.00 | ✓ | 1.000 |
| v41_ce_004 | 3 True | 3 True | 1.00 | ✓ | 1.000 |
| v41_ce_005 | [1]
[1, 2]
[1, 2, 3] | [1]
[1, 2]
[1, 2, 3] | 1.00 | ✓ | 1.000 |
| v41_ce_006 | 2 3 | 2 3 | 1.00 | ✓ | 1.000 |
| v41_ce_007 | True True False | True True False | 1.00 | ✓ | 1.000 |
| v41_ce_008 | 2 0 | 2 0 | 1.00 | ✓ | 1.000 |
| v41_ce_009 | True False True | True False True | 1.00 | ✓ | 1.000 |
| v41_ce_010 | [2, 3] [1, 4] | [2, 3] [1, 4] | 1.00 | ✓ | 1.000 |
| v41_ce_011 | {'x': 1, 'y': 3, 'z' | {'x': 1, 'y': 3, 'z': 4} | 1.00 | ✓ | 1.000 |
| v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 1.00 | ✓ | 1.000 |
| v41_ce_013 | [6, 8] | [6, 8] | 1.00 | ✓ | 1.000 |
| v41_ce_014 | '' True 15 | '' True 15 | 1.00 | ✓ | 1.000 |
| v41_ce_015 | ['date', 'apple', 'b | ['date', 'apple', 'banana', 'cherry'] | 1.00 | ✓ | 1.000 |
| v41_comp_001 | 2 | 2 | 1.00 | ✓ | 1.000 |
| v41_comp_002 | 5.3 | 5.3 | 1.00 | ✓ | 1.000 |
| v41_comp_003 | 2,135 | 2135 | 1.00 | ✓ | 1.000 |
| v41_crt_001 | 10 | 10 | 1.00 | ✓ | 1.000 |
| v41_crt_002 | 5 | 5 | 1.00 | ✓ | 1.000 |
| v41_crt_003 | 8 | 8 | 1.00 | ✓ | 1.000 |
| v41_crt_004 | 28 | 28 | 1.00 | ✓ | 1.000 |
| v41_crt_005 | 11 | 11 | 1.00 | ✓ | 1.000 |
| v41_crt_007 | $187.50 | 187.50 | 1.00 | ✓ | 1.000 |
| v41_crt_008 | 28 | 28 | 1.00 | ✓ | 1.000 |
| v41_crt_009 | They are equal | The amounts are equal. | 1.00 | ✓ | 1.000 |
| v41_crt_010 | 48 | 48 km/h | 1.00 | ✓ | 1.000 |
| v41_crt_011 | $750 | 750 | 1.00 | ✓ | 1.000 |
| v41_ct_001 | 47% | 47% | 1.00 | ✓ | 1.000 |
| v41_ct_002 | 160 | 160 | 1.00 | ✓ | 1.000 |
| v41_ct_004 | 192,000 | 192,000 | 0.95 | ✓ | 0.998 |
| v41_ct_005 | $106,000 | 106000 | 1.00 | ✓ | 1.000 |
| v41_ct_006 | 2.07 | 2.07 | 1.00 | ✓ | 1.000 |
| v41_ct_007 | 30,000 | 30000 | 0.99 | ✓ | 1.000 |
| v42_calc_001 | 34650 | 34650 | 1.00 | ✓ | 1.000 |
| v42_calc_002 | 9 | 9 | 0.95 | ✓ | 0.998 |
| v42_calc_003 | 1/6 | 1/6 | 1.00 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 1.00 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 1.00 | ✓ | 1.000 |
| v42_ioed_001 | 18 | 19 | 0.95 | ✓ | 0.998 |
| v42_ioed_002 | 594 | 594 | 1.00 | ✓ | 1.000 |
| v42_mx_001 | $0.05 | 0.05 | 1.00 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 days | 1.00 | ✓ | 1.000 |
| v42_mx_005 | bright orange | Orange | 1.00 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 1.00 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 5 | 1.00 | ✗ | 0.000 |
| v42_mx_009 | 70,560 | 70560 | 1.00 | ✓ | 1.000 |
| v42_mx_010 | 1081 | 1081 | 1.00 | ✓ | 1.000 |
| v42_mx_011 | 42 | 42 | 1.00 | ✓ | 1.000 |
| v42_mx_012 | false | False | 1.00 | ✓ | 1.000 |
| v42_mx_013 | Mary | Mary | 1.00 | ✓ | 1.000 |
| v42_mx_014 | 63 | 63 | 1.00 | ✓ | 1.000 |
| v42_mx_015 | 45 mph | 45 mph | 1.00 | ✓ | 1.000 |

## Wrong Items (6)

### gen_a2_001
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Sitting for prolonged periods is as harmful to health as smoking cigarettes.' Answer with 
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** While prolonged sitting is associated with increased mortality risk, the claim that it is "as harmful as smoking" is a specific quantitative comparison that experts disagree on -- some epidemiologists support the comparison while others argue it significantly overstates the risk. Note: this item is flagged as high_conf_wrong; models often confidently label this false, missing the genuine epidemiological debate about the magnitude of sedentary behavior risks.
### gen_a4_012
- **Question:** According to the UN Food and Agriculture Organization, what is the world's most produced fruit crop (excluding plantains)?
- **Gold:** banana
- **Model:** Tomatoes
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** FAOSTAT data consistently shows bananas (Cavendish and other cultivars, excluding plantains) as the world's most produced fruit by tonnage, ahead of watermelons, apples, and oranges. Note: this item is flagged as high_conf_wrong; models often answer apples or oranges, reflecting Western-centric dietary assumptions rather than global production data.
### gen_a4_022
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether free will exists as traditionally conceived.' Answer with one word
- **Gold:** contested
- **Model:** false
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Whether free will exists (in the libertarian or traditional sense) remains deeply contested across philosophy, neuroscience, and psychology, with compatibilists, hard determinists, and libertarians all maintaining active positions. Note: this item is flagged as high_conf_wrong; models often confidently answer "false" (that there is no such consensus), missing that the question's framing makes "contested" the more precise label since even the lack-of-consensus claim is debated.
### gen_a4_024
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether intelligence is primarily determined by genetics or environment.' 
- **Gold:** contested
- **Model:** false
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The nature-nurture debate on intelligence remains one of the most contested topics in behavioral genetics and psychology; while heritability estimates are substantial, their interpretation and the relative role of environment (especially gene-environment interaction) is actively debated. Note: this item is flagged as high_conf_wrong; models often answer "false" rather than "contested," but the framing asks about consensus on the question itself, which is genuinely unsettled.
### gen_b2_034
- **Question:** Alaska has a longer total coastline than all the other 49 US states combined. Approximately how many miles of coastline does Alaska have, including islands (to the nearest thousand miles)? Answer with
- **Gold:** 34000
- **Model:** 66000
- **Confidence:** 0.70
- **1-Brier:** 0.510

- **Justification:** NOAA's measurement of Alaska's tidal coastline, including islands, is approximately 33,904 miles, which rounds to 34,000 to the nearest thousand. The compositional element involves recognizing that the question asks for the total inclusive of islands, not just the mainland shoreline.
### v42_mx_007
- **Question:** What is the exact value of pi to the 10th decimal place?
- **Gold:** 3.1415926535
- **Model:** 5
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Pi to 10 decimal places is 3.1415926535, a well-established mathematical constant.
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 29,127 |
| Output tokens | 8,966 |
| Latency | 1065.5s |
| Input cost | $0.0364 |
| Output cost | $1.0596 |
| Total cost | $1.0960 |
