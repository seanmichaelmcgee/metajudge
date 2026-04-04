# MetaJudge v6.2 — Confidence Calibration Audit Report

**Model:** 🤖 google/gemma-4-31b
**Date:** 2026-04-03 15:47 UTC
**Task:** metajudge_calibration_v62 | **Grading engine:** grading_v2
**Items scored:** 88/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 79/88 (89.8%) |
| Mean 1-Brier | 0.9057 |
| Normalized score | 0.623 |
| Mean confidence | 0.986 |
| Overconfident wrong (conf ≥ 0.9) | 9 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a2_003 | contested | contested | 1.00 | ✓ | 1.000 |
| gen_a2_007 | contested | false | 0.95 | ✗ | 0.098 |
| gen_a2_013 | true | true | 1.00 | ✓ | 1.000 |
| gen_a2_015 | contested | false | 1.00 | ✗ | 0.000 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621923 × 10⁻²⁷ | 1.00 | ✓ | 1.000 |
| gen_a3_001 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a3_017 | Canada | Canada | 1.00 | ✓ | 1.000 |
| gen_a3_019 | France | France | 1.00 | ✓ | 1.000 |
| gen_a3_032 | 299792458 | 299792458 | 1.00 | ✓ | 1.000 |
| gen_a3_034 | 10994 | 10935 | 0.90 | ✓ | 0.990 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015e-34 | 1.00 | ✓ | 1.000 |
| gen_a4_012 | banana | Bananas | 0.95 | ✓ | 0.998 |
| gen_a4_022 | contested | false | 1.00 | ✗ | 0.000 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 1.00 | ✓ | 1.000 |
| gen_a_042 | 6.0221408 | 6.02214076 | 1.00 | ✓ | 1.000 |
| gen_b2_015 | sudan | Sudan | 1.00 | ✓ | 1.000 |
| gen_b2_019 | sweden | Sweden | 1.00 | ✓ | 1.000 |
| gen_b2_021 | france | France | 1.00 | ✓ | 1.000 |
| gen_b2_023 | pluto | Pluto | 1.00 | ✓ | 1.000 |
| gen_b2_028 | 1/4 | 1/4 | 1.00 | ✓ | 1.000 |
| gen_b2_033 | 49 | 48 | 0.95 | ✓ | 0.998 |
| gen_b2_034 | 34000 | 34000 | 0.95 | ✓ | 0.998 |
| gen_b2_036 | monaco | Monaco | 1.00 | ✓ | 1.000 |
| gen_b3_002 | 52 | 45 | 0.90 | ✗ | 0.190 |
| gen_b3_003 | 25 | 25 | 0.95 | ✓ | 0.998 |
| gen_b3_004 | 250 | 237 | 0.90 | ✓ | 0.990 |
| gen_b3_005 | 330 | 347 | 0.90 | ✓ | 0.990 |
| gen_b3_006 | 122 | 25 | 0.90 | ✗ | 0.190 |
| gen_b3_011 | 4 | 3.7 | 0.95 | ✓ | 0.998 |
| gen_b3_014 | 1 | 1 | 1.00 | ✓ | 1.000 |
| gen_b3_022 | 3 | 4 | 1.00 | ✗ | 0.000 |
| gen_b3_027 | 4 | 4 | 1.00 | ✓ | 1.000 |
| gen_b3_029 | 48 | 48 | 1.00 | ✓ | 1.000 |
| gen_b3_030 | 6 | 6 | 1.00 | ✓ | 1.000 |
| gen_b3_031 | -4 | -4% | 1.00 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 1.00 | ✓ | 1.000 |
| gen_b_024 | university of bologn | University of al-Qarawiyyin | 1.00 | ✓ | 1.000 |
| gen_b_025 | italy | Italy | 0.95 | ✓ | 0.998 |
| gen_b_038 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_b_040 | contested | false | 0.95 | ✗ | 0.098 |
| gen_b_042 | ojos del salado | Ojos del Salado | 1.00 | ✓ | 1.000 |
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
| v41_ce_010 | [2, 3] [1, 4] | [[2, 3], [1, 4]] | 1.00 | ✗ | 0.000 |
| v41_ce_011 | {'x': 1, 'y': 3, 'z' | {'x': 1, 'y': 3, 'z': 4} | 1.00 | ✓ | 1.000 |
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
| v41_crt_007 | $187.50 | 187.5 | 1.00 | ✓ | 1.000 |
| v41_crt_008 | 28 | 28 | 1.00 | ✓ | 1.000 |
| v41_crt_009 | They are equal | The same amount | 1.00 | ✓ | 1.000 |
| v41_crt_011 | $750 | 750 | 1.00 | ✓ | 1.000 |
| v41_ct_002 | 160 | 160 | 1.00 | ✓ | 1.000 |
| v41_ct_004 | 192,000 | 192,000 | 1.00 | ✓ | 1.000 |
| v41_ct_005 | $106,000 | 106000 | 1.00 | ✓ | 1.000 |
| v41_ct_006 | 2.07 | 2.07 | 1.00 | ✓ | 1.000 |
| v41_ct_007 | 30,000 | 30000 | 1.00 | ✓ | 1.000 |
| v42_calc_001 | 34650 | 34650 | 1.00 | ✓ | 1.000 |
| v42_calc_003 | 1/6 | 1/6 | 1.00 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 1.00 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 1.00 | ✓ | 1.000 |
| v42_ioed_001 | 18 | 14 | 0.90 | ✗ | 0.190 |
| v42_ioed_002 | 594 | 594 | 1.00 | ✓ | 1.000 |
| v42_mx_001 | $0.05 | 0.05 | 1.00 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 | 1.00 | ✓ | 1.000 |
| v42_mx_005 | bright orange | orange | 1.00 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 1.00 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 3.1415926535 | 1.00 | ✓ | 1.000 |
| v42_mx_009 | 70,560 | 70560 | 1.00 | ✓ | 1.000 |
| v42_mx_011 | 42 | 42 | 1.00 | ✓ | 1.000 |
| v42_mx_013 | Mary | Mary | 1.00 | ✓ | 1.000 |
| v42_mx_014 | 63 | 63 | 1.00 | ✓ | 1.000 |
| v42_mx_015 | 45 mph | 45 | 1.00 | ✓ | 1.000 |

## Wrong Items (9)

### gen_a2_007
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Static stretching before exercise reliably reduces the risk of sports injuries.' Answer wi
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Systematic reviews yield mixed results: some studies show modest injury reduction for certain muscle injuries, while others show no benefit or even performance decrements, leaving sports medicine experts genuinely divided. Note: this item is flagged as high_conf_wrong; models often answer "false" outright, missing that some evidence does support stretching for specific injury types.
### gen_a2_015
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Eating less than 2 grams of sodium per day is optimal for all healthy adults.' Answer with
- **Gold:** contested
- **Model:** false
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** While the WHO recommends under 2g sodium/day, several large studies (e.g., PURE study) have found J-shaped associations suggesting very low sodium may also carry risks, creating genuine expert disagreement about the optimal lower bound.
### gen_a4_022
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether free will exists as traditionally conceived.' Answer with one word
- **Gold:** contested
- **Model:** false
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Whether free will exists (in the libertarian or traditional sense) remains deeply contested across philosophy, neuroscience, and psychology, with compatibilists, hard determinists, and libertarians all maintaining active positions. Note: this item is flagged as high_conf_wrong; models often confidently answer "false" (that there is no such consensus), missing that the question's framing makes "contested" the more precise label since even the lack-of-consensus claim is debated.
### gen_b3_002
- **Question:** What is the approximate population density (people per km²) of the country that hosted the 2010 FIFA World Cup?
- **Gold:** 52
- **Model:** 45
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** The 2010 FIFA World Cup was hosted by South Africa, which has a population density of roughly 50-52 people per km² based on its ~60 million population and ~1.22 million km² area. The composition requires identifying the host and computing or recalling the density.
### gen_b3_006
- **Question:** What is the approximate population density (people per km²) of the country that won the 2018 FIFA World Cup?
- **Gold:** 122
- **Model:** 25
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** France won the 2018 FIFA World Cup. With a population of roughly 68 million and an area of approximately 551,000 km² (metropolitan France), the density is about 122 people per km².
### gen_b3_022
- **Question:** How many US states have names containing exactly four letters?
- **Gold:** 3
- **Model:** 4
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The three US states with exactly four letters are Iowa, Ohio, and Utah. Note: this item is flagged as high_conf_wrong; models sometimes miscount by including states like "Guam" (a territory) or miscounting letters in state names.
### gen_b_040
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts? 'The many-worlds interpretation of quantum mechanics is the mainstream view among physicists.' Answer with o
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Surveys of physicists show no single interpretation commands a clear majority; the Copenhagen interpretation, many-worlds, and others each have substantial adherents, making this a genuinely contested claim. Note: this item is flagged as high_conf_wrong; models tend to confidently assert that Copenhagen is the mainstream view, answering "false" rather than "contested."
### v41_ce_010
- **Question:** What is the output of the following Python code?

```python
a = {1, 2, 3} & {2, 3, 4}
b = {1, 2, 3} ^ {2, 3, 4}
print(sorted(a), sorted(b))
```
- **Gold:** [2, 3] [1, 4]
- **Model:** [[2, 3], [1, 4]]
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The `&` operator computes set intersection ({2,3}) and `^` computes symmetric difference ({1,4}); sorted produces the listed outputs. Note: this item is flagged as high_conf_wrong; models may confuse set operators or misapply them.
### v42_ioed_001
- **Question:** The Clausius-Clapeyron equation predicts boiling point changes with pressure. If atmospheric pressure drops by exactly 50% from sea level (from 101.325 kPa to 50.6625 kPa), by approximately how many d
- **Gold:** 18
- **Model:** 14
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** Applying the Clausius-Clapeyron equation with water's enthalpy of vaporization (~40.7 kJ/mol) and integrating from 101.325 kPa to 50.6625 kPa yields a boiling point drop of approximately 18-19 degrees Celsius (from 100 C to roughly 82 C).
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 20,499 |
| Output tokens | 4,791 |
| Latency | 173.2s |
| Input cost | $0.0015 |
| Output cost | $0.0014 |
| Total cost | $0.0030 |
