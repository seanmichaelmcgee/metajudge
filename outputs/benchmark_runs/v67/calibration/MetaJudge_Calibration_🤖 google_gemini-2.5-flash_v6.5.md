# MetaJudge v6.5 — Confidence Calibration Audit Report

**Model:** 🤖 google/gemini-2.5-flash
**Date:** 2026-04-05 17:08 UTC
**Task:** metajudge_calibration_v65 | **Grading engine:** grading_v2
**Items scored:** 103/103

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 99/103 (96.1%) |
| Mean 1-Brier | 0.9661 |
| Normalized score | 0.864 |
| Mean confidence | 0.951 |
| Overconfident wrong (conf ≥ 0.9) | 2 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| 1-Brier | 0.9661 | 0.9731 |
| Normalized | 0.864 | 0.892 |
| Items matched | 103/103 |  |
| Item stability | 97/103 (94%) |  |
| Score range | 0.86 – 0.89 |  |

## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 0 |
| Output tokens | 0 |
| Latency | 0.0s |
| Input cost | $0.0000 |
| Output cost | $0.0000 |
| Total cost | $0.0000 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | false | 0.90 | ✗ | 0.190 |
| gen_a2_003 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a2_007 | contested | false | 0.90 | ✓ | 0.990 |
| gen_a2_013 | true | true | 0.90 | ✓ | 0.990 |
| gen_a2_015 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621924 × 10⁻²⁷ | 0.90 | ✓ | 0.990 |
| gen_a3_001 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a3_007 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a3_017 | Canada | Canada | 0.90 | ✓ | 0.990 |
| gen_a3_019 | France | France | 0.90 | ✓ | 0.990 |
| gen_a3_032 | 299792458 | 299792458 | 1.00 | ✓ | 1.000 |
| gen_a3_034 | 10994 | 10994 | 0.90 | ✓ | 0.990 |
| gen_a3_035 | 6.02214076e23 | 6.02214076 × 10^23 | 1.00 | ✓ | 1.000 |
| gen_a3_036 | 40075.017 | 40075.017 | 0.95 | ✓ | 0.998 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015 × 10⁻³⁴ J·s | 0.95 | ✓ | 0.998 |
| gen_a3_038 | 384400 | 384400 km | 0.85 | ✓ | 0.978 |
| gen_a4_012 | banana | Grapes | 0.70 | ✗ | 0.510 |
| gen_a4_022 | contested | false | 0.90 | ✓ | 0.990 |
| gen_a4_024 | contested | false | 0.95 | ✓ | 0.998 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 0.95 | ✓ | 0.998 |
| gen_a_042 | 6.0221408 | 6.02214076 | 1.00 | ✓ | 1.000 |
| gen_a_044 | 97.9 | 97.5 | 0.60 | ✓ | 0.840 |
| gen_b2_015 | sudan | Sudan | 0.90 | ✓ | 0.990 |
| gen_b2_019 | sweden | Sweden | 0.85 | ✓ | 0.978 |
| gen_b2_021 | france | France | 0.90 | ✓ | 0.990 |
| gen_b2_023 | pluto | Pluto | 0.90 | ✓ | 0.990 |
| gen_b2_028 | 1/4 | 1/4 | 1.00 | ✓ | 1.000 |
| gen_b2_033 | 49 | 49 | 0.95 | ✓ | 0.998 |
| gen_b2_034 | 34000 | 34000 | 0.90 | ✓ | 0.990 |
| gen_b2_036 | monaco | Macau | 0.95 | ✗ | 0.098 |
| gen_b3_001 | 9 | 9 | 0.90 | ✓ | 0.990 |
| gen_b3_002 | 52 | 49 | 0.90 | ✓ | 0.990 |
| gen_b3_003 | 25 | 26 | 0.90 | ✓ | 0.990 |
| gen_b3_004 | 250 | 220 | 0.85 | ✗ | 0.278 |
| gen_b3_005 | 330 | 334 | 0.80 | ✓ | 0.960 |
| gen_b3_006 | 122 | 119 | 0.90 | ✓ | 0.990 |
| gen_b3_007 | 95 | 94 | 0.90 | ✓ | 0.990 |
| gen_b3_009 | 61 | 59 | 0.90 | ✓ | 0.990 |
| gen_b3_011 | 4 | 4.2 | 0.90 | ✓ | 0.990 |
| gen_b3_022 | 3 | 3 | 1.00 | ✓ | 1.000 |
| gen_b3_027 | 4 | 4 | 0.95 | ✓ | 0.998 |
| gen_b3_029 | 48 | 48 | 1.00 | ✓ | 1.000 |
| gen_b3_030 | 6 | 6 | 0.95 | ✓ | 0.998 |
| gen_b3_031 | -4 | -4 | 1.00 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 0.90 | ✓ | 0.990 |
| gen_b_024 | university of bologn | University of Bologna | 0.95 | ✓ | 0.998 |
| gen_b_025 | italy | Italy | 0.85 | ✓ | 0.978 |
| gen_b_037 | false | false | 1.00 | ✓ | 1.000 |
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
| v41_crt_009 | They are equal | They are equal | 1.00 | ✓ | 1.000 |
| v41_crt_010 | 48 | 48 | 1.00 | ✓ | 1.000 |
| v41_crt_011 | $750 | 750 | 1.00 | ✓ | 1.000 |
| v41_ct_001 | 47% | 47 | 1.00 | ✓ | 1.000 |
| v41_ct_002 | 160 | 160 | 1.00 | ✓ | 1.000 |
| v41_ct_004 | 192,000 | 192000 | 1.00 | ✓ | 1.000 |
| v41_ct_005 | $106,000 | 106000 | 0.90 | ✓ | 0.990 |
| v41_ct_006 | 2.07 | 2.07 | 1.00 | ✓ | 1.000 |
| v41_ct_007 | 30,000 | 30000 | 0.95 | ✓ | 0.998 |
| v42_calc_001 | 34650 | 34650 | 0.95 | ✓ | 0.998 |
| v42_calc_002 | 9 | 9 | 0.95 | ✓ | 0.998 |
| v42_calc_003 | 1/6 | 1/6 | 1.00 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 1.00 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 0.95 | ✓ | 0.998 |
| v42_ioed_001 | 18 | 19 | 0.95 | ✓ | 0.998 |
| v42_ioed_002 | 594 | 594 | 0.95 | ✓ | 0.998 |
| v42_mx_001 | $0.05 | 0.05 | 1.00 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 days | 1.00 | ✓ | 1.000 |
| v42_mx_005 | bright orange | orange | 1.00 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 1.00 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 3.1415926535 | 0.90 | ✓ | 0.990 |
| v42_mx_009 | 70,560 | 70560 | 1.00 | ✓ | 1.000 |
| v42_mx_010 | 1081 | 1081 | 0.95 | ✓ | 0.998 |
| v42_mx_011 | 42 | 42 | 1.00 | ✓ | 1.000 |
| v42_mx_012 | false | False | 1.00 | ✓ | 1.000 |
| v42_mx_013 | Mary | Mary | 1.00 | ✓ | 1.000 |
| v42_mx_014 | 63 | 63 | 1.00 | ✓ | 1.000 |
| v42_mx_015 | 45 mph | 45 mph | 1.00 | ✓ | 1.000 |

## Wrong Items (4)

### gen_a2_001
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** While prolonged sitting is associated with increased mortality risk, the claim that it is "as harmful as smoking" is a specific quantitative comparison that experts disagree on -- some epidemiologists support the comparison while others argue it significantly overstates the risk. Note: this item is flagged as high_conf_wrong; models often confidently label this false, missing the genuine epidemiological debate about the magnitude of sedentary behavior risks.
### gen_a4_012
- **Gold:** banana
- **Model:** Grapes
- **Confidence:** 0.70
- **1-Brier:** 0.510

- **Justification:** FAOSTAT data consistently shows bananas (Cavendish and other cultivars, excluding plantains) as the world's most produced fruit by tonnage, ahead of watermelons, apples, and oranges. Note: this item is flagged as high_conf_wrong; models often answer apples or oranges, reflecting Western-centric dietary assumptions rather than global production data.
### gen_b2_036
- **Gold:** monaco
- **Model:** Macau
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Monaco has an estimated population density exceeding 26,000 people per km², which surpasses Vatican City's roughly 1,800-2,000 per km². The compositional step requires knowing that despite Vatican City's tiny size, Monaco's even higher ratio of residents to area gives it the top density ranking.
### gen_b3_004
- **Gold:** 250
- **Model:** 220
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** The 2022 FIFA World Cup was hosted by Qatar, a small Gulf state with a population of roughly 2.9 million and an area of approximately 11,586 km², yielding a density of around 250 people per km². The composition requires identifying Qatar as the host and then estimating its density.