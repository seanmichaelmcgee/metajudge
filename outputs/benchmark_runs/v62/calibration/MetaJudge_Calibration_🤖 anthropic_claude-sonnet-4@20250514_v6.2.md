# MetaJudge v6.2 — Confidence Calibration Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4@20250514
**Date:** 2026-04-03 15:57 UTC
**Task:** metajudge_calibration_v62 | **Grading engine:** grading_v2
**Items scored:** 105/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 94/105 (89.5%) |
| Mean 1-Brier | 0.9005 |
| Normalized score | 0.602 |
| Mean confidence | 0.882 |
| Overconfident wrong (conf ≥ 0.9) | 4 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | contested | 0.80 | ✓ | 0.960 |
| gen_a2_003 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_a2_007 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_a2_013 | true | true | 0.85 | ✓ | 0.978 |
| gen_a2_015 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621898 × 10⁻²⁷ | 0.75 | ✓ | 0.938 |
| gen_a3_001 | contested | contested | 0.80 | ✓ | 0.960 |
| gen_a3_007 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_a3_017 | Canada | Finland | 0.85 | ✗ | 0.278 |
| gen_a3_019 | France | France | 0.85 | ✓ | 0.978 |
| gen_a3_032 | 299792458 | 299792458 | 0.95 | ✓ | 0.998 |
| gen_a3_034 | 10994 | 10984 | 0.70 | ✓ | 0.910 |
| gen_a3_035 | 6.02214076e23 | 6.02214076×10²³ | 0.95 | ✓ | 0.998 |
| gen_a3_036 | 40075.017 | 40,075.017 | 0.85 | ✓ | 0.978 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015 × 10⁻³⁴ | 0.95 | ✓ | 0.998 |
| gen_a3_038 | 384400 | 384,400 | 0.70 | ✓ | 0.910 |
| gen_a4_012 | banana | bananas | 0.80 | ✓ | 0.960 |
| gen_a4_022 | contested | false | 0.85 | ✗ | 0.278 |
| gen_a4_024 | contested | false | 0.85 | ✗ | 0.278 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 0.90 | ✓ | 0.990 |
| gen_a_042 | 6.0221408 | 6.0221408 | 0.85 | ✓ | 0.978 |
| gen_a_044 | 97.9 | 97.9 | 0.30 | ✓ | 0.510 |
| gen_b2_015 | sudan | Sudan | 0.80 | ✓ | 0.960 |
| gen_b2_019 | sweden | Finland | 0.85 | ✗ | 0.278 |
| gen_b2_021 | france | France | 0.85 | ✓ | 0.978 |
| gen_b2_023 | pluto | Pluto | 0.85 | ✓ | 0.978 |
| gen_b2_028 | 1/4 | 1/4 | 0.90 | ✓ | 0.990 |
| gen_b2_033 | 49 | 48 | 0.75 | ✓ | 0.938 |
| gen_b2_034 | 34000 | 34000 | 0.70 | ✓ | 0.910 |
| gen_b2_036 | monaco | Monaco | 0.85 | ✓ | 0.978 |
| gen_b3_001 | 9 | 8.5 | 0.85 | ✓ | 0.978 |
| gen_b3_002 | 52 | 48 | 0.70 | ✓ | 0.910 |
| gen_b3_003 | 25 | 25 | 0.80 | ✓ | 0.960 |
| gen_b3_004 | 250 | 240 | 0.70 | ✓ | 0.910 |
| gen_b3_005 | 330 | 347 | 0.80 | ✓ | 0.960 |
| gen_b3_006 | 122 | 145 | 0.70 | ✗ | 0.510 |
| gen_b3_007 | 95 | 23 | 0.70 | ✗ | 0.510 |
| gen_b3_009 | 61 | 59 | 0.75 | ✓ | 0.938 |
| gen_b3_011 | 4 | 4 | 0.75 | ✓ | 0.938 |
| gen_b3_014 | 1 | 1 | 0.85 | ✓ | 0.978 |
| gen_b3_022 | 3 | 4 | 0.85 | ✗ | 0.278 |
| gen_b3_027 | 4 | 4 | 0.95 | ✓ | 0.998 |
| gen_b3_029 | 48 | 48 | 0.95 | ✓ | 0.998 |
| gen_b3_030 | 6 | 6 | 0.95 | ✓ | 0.998 |
| gen_b3_031 | -4 | -4% | 0.95 | ✓ | 0.998 |
| gen_b3_033 | Sudan | Sudan | 0.70 | ✓ | 0.910 |
| gen_b_024 | university of bologn | University of Bologna | 0.80 | ✓ | 0.960 |
| gen_b_025 | italy | Italy | 0.75 | ✓ | 0.938 |
| gen_b_037 | false | false | 0.85 | ✓ | 0.978 |
| gen_b_038 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_b_040 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_b_042 | ojos del salado | Ojos del Salado | 0.85 | ✓ | 0.978 |
| v41_ce_001 | 12 | 10 | 0.95 | ✗ | 0.098 |
| v41_ce_002 | -4 1 | -4 1 | 0.95 | ✓ | 0.998 |
| v41_ce_003 | [[5], [5], [5]] | [[5], [5], [5]] | 0.90 | ✓ | 0.990 |
| v41_ce_004 | 3 True | 3 True | 0.95 | ✓ | 0.998 |
| v41_ce_005 | [1]
[1, 2]
[1, 2, 3] | [1]
[1, 2]
[1, 2, 3] | 0.95 | ✓ | 0.998 |
| v41_ce_006 | 2 3 | 2 3 | 0.95 | ✓ | 0.998 |
| v41_ce_007 | True True False | True True False | 0.95 | ✓ | 0.998 |
| v41_ce_008 | 2 0 | 2 0 | 0.95 | ✓ | 0.998 |
| v41_ce_009 | True False True | True False True | 0.95 | ✓ | 0.998 |
| v41_ce_010 | [2, 3] [1, 4] | [2, 3] [1, 4] | 0.95 | ✓ | 0.998 |
| v41_ce_011 | {'x': 1, 'y': 3, 'z' | {'x': 1, 'y': 3, 'z': 4} | 0.95 | ✓ | 0.998 |
| v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 0.95 | ✓ | 0.998 |
| v41_ce_013 | [6, 8] | [6, 8] | 0.95 | ✓ | 0.998 |
| v41_ce_014 | '' True 15 | '' True 15 | 0.95 | ✓ | 0.998 |
| v41_ce_015 | ['date', 'apple', 'b | ['date', 'apple', 'banana', 'cherry'] | 1.00 | ✓ | 1.000 |
| v41_comp_001 | 2 | 2 | 0.95 | ✓ | 0.998 |
| v41_comp_002 | 5.3 | 5.3 | 0.95 | ✓ | 0.998 |
| v41_comp_003 | 2,135 | 2135 | 0.95 | ✓ | 0.998 |
| v41_crt_001 | 10 | 10 | 0.95 | ✓ | 0.998 |
| v41_crt_002 | 5 | 5 | 0.95 | ✓ | 0.998 |
| v41_crt_003 | 8 | 8 | 0.95 | ✓ | 0.998 |
| v41_crt_004 | 28 | 28 | 0.95 | ✓ | 0.998 |
| v41_crt_005 | 11 | 10 | 0.95 | ✗ | 0.098 |
| v41_crt_007 | $187.50 | 187.50 | 1.00 | ✓ | 1.000 |
| v41_crt_008 | 28 | 28 | 0.95 | ✓ | 0.998 |
| v41_crt_009 | They are equal | Equal amounts | 0.95 | ✓ | 0.998 |
| v41_crt_010 | 48 | 48 km/h | 0.95 | ✓ | 0.998 |
| v41_crt_011 | $750 | 750 | 0.95 | ✓ | 0.998 |
| v41_ct_001 | 47% | 47 | 0.95 | ✓ | 0.998 |
| v41_ct_002 | 160 | 1600 | 0.95 | ✗ | 0.098 |
| v41_ct_004 | 192,000 | 192000 | 0.85 | ✓ | 0.978 |
| v41_ct_005 | $106,000 | 107000 | 0.90 | ✓ | 0.990 |
| v41_ct_006 | 2.07 | 2.07 | 0.95 | ✓ | 0.998 |
| v41_ct_007 | 30,000 | 30000 | 0.95 | ✓ | 0.998 |
| v42_calc_001 | 34650 | 34650 | 0.95 | ✓ | 0.998 |
| v42_calc_002 | 9 | 1 | 0.95 | ✗ | 0.098 |
| v42_calc_003 | 1/6 | 1/6 | 1.00 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 0.95 | ✓ | 0.998 |
| v42_calc_005 | 259.81 | 259.81 | 0.95 | ✓ | 0.998 |
| v42_ioed_001 | 18 | 18 | 0.75 | ✓ | 0.938 |
| v42_ioed_002 | 594 | 594 | 0.95 | ✓ | 0.998 |
| v42_mx_001 | $0.05 | $0.05 | 0.95 | ✓ | 0.998 |
| v42_mx_002 | 47 days | 47 | 0.95 | ✓ | 0.998 |
| v42_mx_005 | bright orange | orange | 0.95 | ✓ | 0.998 |
| v42_mx_006 | 4 | 4 | 1.00 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 3.1415926536 | 0.95 | ✓ | 0.998 |
| v42_mx_009 | 70,560 | 70560 | 1.00 | ✓ | 1.000 |
| v42_mx_010 | 1081 | 1081 | 0.95 | ✓ | 0.998 |
| v42_mx_011 | 42 | 42 | 0.95 | ✓ | 0.998 |
| v42_mx_012 | false | False | 0.90 | ✓ | 0.990 |
| v42_mx_013 | Mary | Mary | 0.95 | ✓ | 0.998 |
| v42_mx_014 | 63 | 63 | 0.95 | ✓ | 0.998 |
| v42_mx_015 | 45 mph | 45 mph | 1.00 | ✓ | 1.000 |

## Wrong Items (11)

### gen_a3_017
- **Question:** Which country has the most natural lakes in the world?
- **Gold:** Canada
- **Model:** Finland
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** Canada contains an estimated 60% of the world's natural lakes, with over 800,000 lakes larger than a threshold area. The prototype violation is that models may answer Finland ("land of a thousand lakes") or other countries associated with lakes.
### gen_a4_022
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether free will exists as traditionally conceived.' Answer with one word
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** Whether free will exists (in the libertarian or traditional sense) remains deeply contested across philosophy, neuroscience, and psychology, with compatibilists, hard determinists, and libertarians all maintaining active positions. Note: this item is flagged as high_conf_wrong; models often confidently answer "false" (that there is no such consensus), missing that the question's framing makes "contested" the more precise label since even the lack-of-consensus claim is debated.
### gen_a4_024
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether intelligence is primarily determined by genetics or environment.' 
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** The nature-nurture debate on intelligence remains one of the most contested topics in behavioral genetics and psychology; while heritability estimates are substantial, their interpretation and the relative role of environment (especially gene-environment interaction) is actively debated. Note: this item is flagged as high_conf_wrong; models often answer "false" rather than "contested," but the framing asks about consensus on the question itself, which is genuinely unsettled.
### gen_b2_019
- **Question:** Which country has the most islands in the world by total count? Answer with the country name only.
- **Gold:** sweden
- **Model:** Finland
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** Sweden has approximately 267,570 islands according to a comprehensive satellite-based count, the highest of any country. The prototype violation is that models typically answer Indonesia, the Philippines, or Norway, which are more stereotypically associated with islands.
### gen_b3_006
- **Question:** What is the approximate population density (people per km²) of the country that won the 2018 FIFA World Cup?
- **Gold:** 122
- **Model:** 145
- **Confidence:** 0.70
- **1-Brier:** 0.510

- **Justification:** France won the 2018 FIFA World Cup. With a population of roughly 68 million and an area of approximately 551,000 km² (metropolitan France), the density is about 122 people per km².
### gen_b3_007
- **Question:** What is the approximate population density (people per km²) of the country that won the 2010 FIFA World Cup?
- **Gold:** 95
- **Model:** 23
- **Confidence:** 0.70
- **1-Brier:** 0.510

- **Justification:** Spain won the 2010 FIFA World Cup. With approximately 47 million people and an area of roughly 506,000 km², Spain's population density is approximately 93-95 people per km².
### gen_b3_022
- **Question:** How many US states have names containing exactly four letters?
- **Gold:** 3
- **Model:** 4
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** The three US states with exactly four letters are Iowa, Ohio, and Utah. Note: this item is flagged as high_conf_wrong; models sometimes miscount by including states like "Guam" (a territory) or miscounting letters in state names.
### v41_ce_001
- **Question:** What is the output of the following Python code?

```python
result = round(0.5) + round(1.5) + round(2.5) + round(3.5) + round(4.5)
print(result)
```
- **Gold:** 12
- **Model:** 10
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Python 3 uses banker's rounding (round-half-to-even): round(0.5)=0, round(1.5)=2, round(2.5)=2, round(3.5)=4, round(4.5)=4, totaling 12. Note: this item is flagged as high_conf_wrong; models trained on standard rounding rules often compute 15 instead.
### v41_crt_005
- **Question:** A bacteria culture triples in population every hour. It takes 12 hours for the culture to fill a petri dish. How many hours does it take for the culture to fill one-third of the dish?
- **Gold:** 11
- **Model:** 10
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Since the culture triples every hour, at hour 11 the dish is one-third full, and tripling once more fills it completely at hour 12. The intuitive trap is to answer 4 (one-third of 12). Note: this item is flagged as high_conf_wrong; models frequently give a confident but incorrect answer such as 4.
### v41_ct_002
- **Question:** Assume that the European Central Bank cut its deposit facility rate from 4.00% in June 2024 through a series of eight cuts to reach 2.00% by June 2025, a total reduction of 200 basis points. If a Euro
- **Gold:** 160
- **Model:** 1600
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** The question provides all necessary figures: a 2.00 percentage point drop on EUR 8 billion gives 8,000 * 0.02 = EUR 160 million in reduced annual interest income. The temporal element is the evolving ECB rate policy. Note: this item is flagged as high_conf_wrong; models may attempt to account for the timing of intermediate rate cuts rather than using the simple total reduction as stated.
### v42_calc_002
- **Question:** What is the remainder when 7^100 is divided by 13?
- **Gold:** 9
- **Model:** 1
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** By Fermat's little theorem, 7^12 = 1 (mod 13), so 7^100 = 7^(12*8 + 4) = 7^4 (mod 13). Since 7^4 = 2401 and 2401 = 184*13 + 9, the remainder is 9. Note: this item is flagged as high_conf_wrong; the modular arithmetic is correct but the multi-step calculation is easy to get wrong.
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 76,453 |
| Output tokens | 13,313 |
| Latency | 248.2s |
| Input cost | $0.2294 |
| Output cost | $0.1997 |
| Total cost | $0.4291 |
