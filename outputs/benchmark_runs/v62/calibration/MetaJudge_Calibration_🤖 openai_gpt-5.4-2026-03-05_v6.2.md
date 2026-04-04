# MetaJudge v6.2 — Confidence Calibration Audit Report

**Model:** 🤖 openai/gpt-5.4-2026-03-05
**Date:** 2026-04-04 03:58 UTC
**Task:** metajudge_calibration_v62 | **Grading engine:** grading_v2
**Items scored:** 105/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 99/105 (94.3%) |
| Mean 1-Brier | 0.9404 |
| Normalized score | 0.762 |
| Mean confidence | 0.925 |
| Overconfident wrong (conf ≥ 0.9) | 3 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | false | 0.93 | ✗ | 0.135 |
| gen_a2_003 | contested | contested | 0.88 | ✓ | 0.986 |
| gen_a2_007 | contested | false | 0.91 | ✗ | 0.172 |
| gen_a2_013 | true | true | 0.96 | ✓ | 0.998 |
| gen_a2_015 | contested | contested | 0.93 | ✓ | 0.995 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621925 × 10⁻²⁷ | 0.57 | ✓ | 0.815 |
| gen_a3_001 | contested | contested | 0.79 | ✓ | 0.956 |
| gen_a3_007 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a3_017 | Canada | Canada | 0.99 | ✓ | 1.000 |
| gen_a3_019 | France | France | 0.86 | ✓ | 0.980 |
| gen_a3_032 | 299792458 | 299792458 | 0.99 | ✓ | 1.000 |
| gen_a3_034 | 10994 | 10935 | 0.38 | ✓ | 0.616 |
| gen_a3_035 | 6.02214076e23 | 6.02214076×10^23 mol^-1 | 0.99 | ✓ | 1.000 |
| gen_a3_036 | 40075.017 | 40075.017 | 0.86 | ✓ | 0.980 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015×10⁻³⁴ J·s | 0.99 | ✓ | 1.000 |
| gen_a3_038 | 384400 | 384400 | 0.99 | ✓ | 1.000 |
| gen_a4_012 | banana | Bananas | 0.72 | ✓ | 0.922 |
| gen_a4_022 | contested | contested | 0.96 | ✓ | 0.998 |
| gen_a4_024 | contested | contested | 0.97 | ✓ | 0.999 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 0.99 | ✓ | 1.000 |
| gen_a_042 | 6.0221408 | 6.0221408 | 0.99 | ✓ | 1.000 |
| gen_a_044 | 97.9 | 97.9 | 0.55 | ✓ | 0.797 |
| gen_b2_015 | sudan | Sudan | 0.97 | ✓ | 0.999 |
| gen_b2_019 | sweden | Sweden | 0.94 | ✓ | 0.996 |
| gen_b2_021 | france | France | 0.86 | ✓ | 0.980 |
| gen_b2_023 | pluto | Pluto | 0.97 | ✓ | 0.999 |
| gen_b2_028 | 1/4 | 1/4 | 0.98 | ✓ | 1.000 |
| gen_b2_033 | 49 | 49 | 0.80 | ✓ | 0.960 |
| gen_b2_034 | 34000 | 34000 | 0.78 | ✓ | 0.952 |
| gen_b2_036 | monaco | Monaco | 0.97 | ✓ | 0.999 |
| gen_b3_001 | 9 | 9 | 0.86 | ✓ | 0.980 |
| gen_b3_002 | 52 | 40 | 0.72 | ✗ | 0.482 |
| gen_b3_003 | 25 | 25 | 0.88 | ✓ | 0.986 |
| gen_b3_004 | 250 | 240 | 0.62 | ✓ | 0.856 |
| gen_b3_005 | 330 | 347 | 0.76 | ✓ | 0.942 |
| gen_b3_006 | 122 | 119 | 0.72 | ✓ | 0.922 |
| gen_b3_007 | 95 | 200 | 0.66 | ✗ | 0.564 |
| gen_b3_009 | 61 | 60 | 0.42 | ✓ | 0.664 |
| gen_b3_011 | 4 | 4 | 0.78 | ✓ | 0.952 |
| gen_b3_014 | 1 | 1 | 0.92 | ✓ | 0.994 |
| gen_b3_022 | 3 | 3 | 0.98 | ✓ | 1.000 |
| gen_b3_027 | 4 | 4 | 0.98 | ✓ | 1.000 |
| gen_b3_029 | 48 | 48 | 0.99 | ✓ | 1.000 |
| gen_b3_030 | 6 | 6 | 0.93 | ✓ | 0.995 |
| gen_b3_031 | -4 | 4% decrease | 0.99 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 0.97 | ✓ | 0.999 |
| gen_b_024 | university of bologn | University of al-Qarawiyyin | 0.74 | ✓ | 0.932 |
| gen_b_025 | italy | Italy | 0.79 | ✓ | 0.956 |
| gen_b_037 | false | false | 0.98 | ✓ | 1.000 |
| gen_b_038 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_b_040 | contested | false | 0.84 | ✗ | 0.294 |
| gen_b_042 | ojos del salado | Ojos del Salado | 0.99 | ✓ | 1.000 |
| v41_ce_001 | 12 | 10 | 0.98 | ✗ | 0.040 |
| v41_ce_002 | -4 1 | -4 1 | 0.99 | ✓ | 1.000 |
| v41_ce_003 | [[5], [5], [5]] | [[5], [5], [5]] | 0.99 | ✓ | 1.000 |
| v41_ce_004 | 3 True | 3 True | 0.99 | ✓ | 1.000 |
| v41_ce_005 | [1]
[1, 2]
[1, 2, 3] | [1]
[1, 2]
[1, 2, 3] | 0.99 | ✓ | 1.000 |
| v41_ce_006 | 2 3 | 2 3 | 0.99 | ✓ | 1.000 |
| v41_ce_007 | True True False | True True False | 0.99 | ✓ | 1.000 |
| v41_ce_008 | 2 0 | 2 0 | 0.99 | ✓ | 1.000 |
| v41_ce_009 | True False True | True False True | 0.98 | ✓ | 1.000 |
| v41_ce_010 | [2, 3] [1, 4] | [2, 3] [1, 4] | 0.99 | ✓ | 1.000 |
| v41_ce_011 | {'x': 1, 'y': 3, 'z' | {'x': 1, 'y': 3, 'z': 4} | 0.99 | ✓ | 1.000 |
| v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 0.99 | ✓ | 1.000 |
| v41_ce_013 | [6, 8] | [6, 8] | 0.98 | ✓ | 1.000 |
| v41_ce_014 | '' True 15 | '' True 15 | 0.99 | ✓ | 1.000 |
| v41_ce_015 | ['date', 'apple', 'b | ['date', 'apple', 'banana', 'cherry'] | 0.99 | ✓ | 1.000 |
| v41_comp_001 | 2 | 2 | 0.99 | ✓ | 1.000 |
| v41_comp_002 | 5.3 | 5.3 | 0.99 | ✓ | 1.000 |
| v41_comp_003 | 2,135 | 2135 | 0.99 | ✓ | 1.000 |
| v41_crt_001 | 10 | 10 | 0.99 | ✓ | 1.000 |
| v41_crt_002 | 5 | 5 | 0.99 | ✓ | 1.000 |
| v41_crt_003 | 8 | 8 | 0.99 | ✓ | 1.000 |
| v41_crt_004 | 28 | 28 | 0.99 | ✓ | 1.000 |
| v41_crt_005 | 11 | 11 | 0.99 | ✓ | 1.000 |
| v41_crt_007 | $187.50 | 187.50 | 0.99 | ✓ | 1.000 |
| v41_crt_008 | 28 | 28 | 0.99 | ✓ | 1.000 |
| v41_crt_009 | They are equal | Equal | 0.99 | ✓ | 1.000 |
| v41_crt_010 | 48 | 48 km/h | 0.99 | ✓ | 1.000 |
| v41_crt_011 | $750 | 750 | 0.99 | ✓ | 1.000 |
| v41_ct_001 | 47% | 47% | 0.98 | ✓ | 1.000 |
| v41_ct_002 | 160 | 160 | 0.99 | ✓ | 1.000 |
| v41_ct_004 | 192,000 | 192,000 | 0.99 | ✓ | 1.000 |
| v41_ct_005 | $106,000 | $106,000 | 0.98 | ✓ | 1.000 |
| v41_ct_006 | 2.07 | 2.07 | 0.99 | ✓ | 1.000 |
| v41_ct_007 | 30,000 | 30000 | 0.99 | ✓ | 1.000 |
| v42_calc_001 | 34650 | 34650 | 0.99 | ✓ | 1.000 |
| v42_calc_002 | 9 | 9 | 0.98 | ✓ | 1.000 |
| v42_calc_003 | 1/6 | 1/6 | 0.99 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 0.99 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 0.99 | ✓ | 1.000 |
| v42_ioed_001 | 18 | 18 | 0.82 | ✓ | 0.968 |
| v42_ioed_002 | 594 | 594 | 0.99 | ✓ | 1.000 |
| v42_mx_001 | $0.05 | $0.05 | 0.99 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 days | 0.99 | ✓ | 1.000 |
| v42_mx_005 | bright orange | orange | 0.99 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 0.99 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 3.1415926536 | 0.99 | ✓ | 1.000 |
| v42_mx_009 | 70,560 | 70560 | 1.00 | ✓ | 1.000 |
| v42_mx_010 | 1081 | 1081 | 0.99 | ✓ | 1.000 |
| v42_mx_011 | 42 | 42 | 0.99 | ✓ | 1.000 |
| v42_mx_012 | false | False | 0.99 | ✓ | 1.000 |
| v42_mx_013 | Mary | Mary | 0.99 | ✓ | 1.000 |
| v42_mx_014 | 63 | 63 | 0.99 | ✓ | 1.000 |
| v42_mx_015 | 45 mph | 45 mph | 0.99 | ✓ | 1.000 |

## Wrong Items (6)

### gen_a2_001
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Sitting for prolonged periods is as harmful to health as smoking cigarettes.' Answer with 
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.93
- **1-Brier:** 0.135

- **Justification:** While prolonged sitting is associated with increased mortality risk, the claim that it is "as harmful as smoking" is a specific quantitative comparison that experts disagree on -- some epidemiologists support the comparison while others argue it significantly overstates the risk. Note: this item is flagged as high_conf_wrong; models often confidently label this false, missing the genuine epidemiological debate about the magnitude of sedentary behavior risks.
### gen_a2_007
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Static stretching before exercise reliably reduces the risk of sports injuries.' Answer wi
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.91
- **1-Brier:** 0.172

- **Justification:** Systematic reviews yield mixed results: some studies show modest injury reduction for certain muscle injuries, while others show no benefit or even performance decrements, leaving sports medicine experts genuinely divided. Note: this item is flagged as high_conf_wrong; models often answer "false" outright, missing that some evidence does support stretching for specific injury types.
### gen_b3_002
- **Question:** What is the approximate population density (people per km²) of the country that hosted the 2010 FIFA World Cup?
- **Gold:** 52
- **Model:** 40
- **Confidence:** 0.72
- **1-Brier:** 0.482

- **Justification:** The 2010 FIFA World Cup was hosted by South Africa, which has a population density of roughly 50-52 people per km² based on its ~60 million population and ~1.22 million km² area. The composition requires identifying the host and computing or recalling the density.
### gen_b3_007
- **Question:** What is the approximate population density (people per km²) of the country that won the 2010 FIFA World Cup?
- **Gold:** 95
- **Model:** 200
- **Confidence:** 0.66
- **1-Brier:** 0.564

- **Justification:** Spain won the 2010 FIFA World Cup. With approximately 47 million people and an area of roughly 506,000 km², Spain's population density is approximately 93-95 people per km².
### gen_b_040
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts? 'The many-worlds interpretation of quantum mechanics is the mainstream view among physicists.' Answer with o
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.84
- **1-Brier:** 0.294

- **Justification:** Surveys of physicists show no single interpretation commands a clear majority; the Copenhagen interpretation, many-worlds, and others each have substantial adherents, making this a genuinely contested claim. Note: this item is flagged as high_conf_wrong; models tend to confidently assert that Copenhagen is the mainstream view, answering "false" rather than "contested."
### v41_ce_001
- **Question:** What is the output of the following Python code?

```python
result = round(0.5) + round(1.5) + round(2.5) + round(3.5) + round(4.5)
print(result)
```
- **Gold:** 12
- **Model:** 10
- **Confidence:** 0.98
- **1-Brier:** 0.040

- **Justification:** Python 3 uses banker's rounding (round-half-to-even): round(0.5)=0, round(1.5)=2, round(2.5)=2, round(3.5)=4, round(4.5)=4, totaling 12. Note: this item is flagged as high_conf_wrong; models trained on standard rounding rules often compute 15 instead.
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 31,335 |
| Output tokens | 6,224 |
| Latency | 152.5s |
| Input cost | $0.0783 |
| Output cost | $0.0934 |
| Total cost | $0.1717 |
