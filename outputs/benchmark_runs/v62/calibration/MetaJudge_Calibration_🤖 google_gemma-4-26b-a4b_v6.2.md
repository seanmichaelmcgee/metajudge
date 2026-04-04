# MetaJudge v6.2 — Confidence Calibration Audit Report

**Model:** 🤖 google/gemma-4-26b-a4b
**Date:** 2026-04-04 03:32 UTC
**Task:** metajudge_calibration_v62 | **Grading engine:** grading_v2
**Items scored:** 104/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 79/104 (76.0%) |
| Mean 1-Brier | 0.7820 |
| Normalized score | 0.128 |
| Mean confidence | 0.968 |
| Overconfident wrong (conf ≥ 0.9) | 22 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a2_003 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_a2_007 | contested | false | 0.95 | ✗ | 0.098 |
| gen_a2_013 | true | true | 0.95 | ✓ | 0.998 |
| gen_a2_015 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621923×10⁻²⁷ | 0.95 | ✓ | 0.998 |
| gen_a3_001 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a3_007 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a3_017 | Canada | Canada | 0.95 | ✓ | 0.998 |
| gen_a3_019 | France | France | 1.00 | ✓ | 1.000 |
| gen_a3_032 | 299792458 | 299792458 | 1.00 | ✓ | 1.000 |
| gen_a3_034 | 10994 | 10,935 | 0.85 | ✓ | 0.978 |
| gen_a3_035 | 6.02214076e23 | 6.02214076 × 10^23 | 1.00 | ✓ | 1.000 |
| gen_a3_036 | 40075.017 | 40075 km | 0.95 | ✓ | 0.998 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015 × 10⁻3⁴ J·s | 1.00 | ✓ | 1.000 |
| gen_a3_038 | 384400 | 384,400 | 0.95 | ✓ | 0.998 |
| gen_a4_012 | banana | tomatoes | 0.90 | ✗ | 0.190 |
| gen_a4_022 | contested | contested | 1.00 | ✓ | 1.000 |
| gen_a4_024 | contested | false | 1.00 | ✗ | 0.000 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 0.95 | ✓ | 0.998 |
| gen_a_042 | 6.0221408 | 6.0221408 × 10^23 mol^-1 | 1.00 | ✗ | 0.000 |
| gen_a_044 | 97.9 | 97.5 | 0.90 | ✓ | 0.990 |
| gen_b2_015 | sudan | Sudan | 1.00 | ✓ | 1.000 |
| gen_b2_019 | sweden | Sweden | 0.90 | ✓ | 0.990 |
| gen_b2_021 | france | France | 0.95 | ✓ | 0.998 |
| gen_b2_023 | pluto | Pluto | 1.00 | ✓ | 1.000 |
| gen_b2_028 | 1/4 | 1/4 | 1.00 | ✓ | 1.000 |
| gen_b2_033 | 49 | 48 | 0.90 | ✓ | 0.990 |
| gen_b2_034 | 34000 | 33900 | 0.90 | ✓ | 0.990 |
| gen_b2_036 | monaco | Monaco | 0.95 | ✓ | 0.998 |
| gen_b3_001 | 9 | 124 | 0.90 | ✗ | 0.190 |
| gen_b3_002 | 52 | 116 | 0.90 | ✗ | 0.190 |
| gen_b3_003 | 25 | ~170 | 0.90 | ✗ | 0.190 |
| gen_b3_004 | 250 | 34 | 0.90 | ✗ | 0.190 |
| gen_b3_005 | 330 | 338 | 0.90 | ✓ | 0.990 |
| gen_b3_006 | 122 | ~82 people per km² | 0.90 | ✗ | 0.190 |
| gen_b3_007 | 95 | ~120 | 0.80 | ✗ | 0.360 |
| gen_b3_009 | 61 | 54 | 0.95 | ✗ | 0.098 |
| gen_b3_011 | 4 | ~19 | 0.80 | ✗ | 0.360 |
| gen_b3_014 | 1 | 1 | 1.00 | ✓ | 1.000 |
| gen_b3_022 | 3 | 4 | 1.00 | ✗ | 0.000 |
| gen_b3_027 | 4 | 4 | 1.00 | ✓ | 1.000 |
| gen_b3_029 | 48 | 48 | 1.00 | ✓ | 1.000 |
| gen_b3_030 | 6 | 6 | 1.00 | ✓ | 1.000 |
| gen_b3_031 | -4 | -4% | 0.99 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 1.00 | ✓ | 1.000 |
| gen_b_024 | university of bologn | University of Al-Qarawiyyin | 1.00 | ✓ | 1.000 |
| gen_b_025 | italy | Italy | 1.00 | ✓ | 1.000 |
| gen_b_037 | false | false | 0.95 | ✓ | 0.998 |
| gen_b_038 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_b_040 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_b_042 | ojos del salado | Ojos del Salado | 1.00 | ✓ | 1.000 |
| v41_ce_001 | 12 | 10 | 1.00 | ✗ | 0.000 |
| v41_ce_002 | -4 1 | -4 1 | 1.00 | ✓ | 1.000 |
| v41_ce_003 | [[5], [5], [5]] | [5, 5, 5] | 1.00 | ✗ | 0.000 |
| v41_ce_004 | 3 True | 3 True | 1.00 | ✓ | 1.000 |
| v41_ce_005 | [1]
[1, 2]
[1, 2, 3] | [1], [1, 2], [1, 2, 3] | 1.00 | ✗ | 0.000 |
| v41_ce_006 | 2 3 | 2 2 | 1.00 | ✗ | 0.000 |
| v41_ce_007 | True True False | True True False | 1.00 | ✓ | 1.000 |
| v41_ce_008 | 2 0 | 2 0 | 1.00 | ✓ | 1.000 |
| v41_ce_009 | True False True | True True True | 1.00 | ✗ | 0.000 |
| v41_ce_010 | [2, 3] [1, 4] | [1, 2, 3], [1, 4] | 0.95 | ✗ | 0.098 |
| v41_ce_011 | {'x': 1, 'y': 3, 'z' | {'x': 1, 'y': 3, 'z': 4} | 1.00 | ✓ | 1.000 |
| v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 1.00 | ✓ | 1.000 |
| v41_ce_013 | [6, 8] | [6, 8] | 1.00 | ✓ | 1.000 |
| v41_ce_014 | '' True 15 | '' hello True 15 | 1.00 | ✓ | 1.000 |
| v41_ce_015 | ['date', 'apple', 'b | ['banana', 'apple', 'cherry', 'date'] | 1.00 | ✗ | 0.000 |
| v41_comp_001 | 2 | 1 | 1.00 | ✗ | 0.000 |
| v41_comp_002 | 5.3 | 5.3 | 1.00 | ✓ | 1.000 |
| v41_comp_003 | 2,135 | 2135 | 1.00 | ✓ | 1.000 |
| v41_crt_001 | 10 | 10 | 1.00 | ✓ | 1.000 |
| v41_crt_002 | 5 | 5 | 1.00 | ✓ | 1.000 |
| v41_crt_003 | 8 | 8 | 1.00 | ✓ | 1.000 |
| v41_crt_004 | 28 | 28 | 1.00 | ✓ | 1.000 |
| v41_crt_005 | 11 | 11 | 1.00 | ✓ | 1.000 |
| v41_crt_007 | $187.50 | $187.50 | 1.00 | ✓ | 1.000 |
| v41_crt_008 | 28 | 28 | 1.00 | ✓ | 1.000 |
| v41_crt_009 | They are equal | They are equal | 1.00 | ✓ | 1.000 |
| v41_crt_010 | 48 | 48 km/h | 1.00 | ✓ | 1.000 |
| v41_crt_011 | $750 | $750 | 1.00 | ✓ | 1.000 |
| v41_ct_001 | 47% | 47% | 1.00 | ✓ | 1.000 |
| v41_ct_002 | 160 | 160 | 1.00 | ✓ | 1.000 |
| v41_ct_004 | 192,000 | 191,781 | 0.95 | ✓ | 0.998 |
| v41_ct_005 | $106,000 | $106,000 | 0.90 | ✓ | 0.990 |
| v41_ct_006 | 2.07 | 2.07 | 1.00 | ✓ | 1.000 |
| v41_ct_007 | 30,000 | 30000 | 1.00 | ✓ | 1.000 |
| v42_calc_001 | 34650 | 34650 | 1.00 | ✓ | 1.000 |
| v42_calc_002 | 9 | 3 | 1.00 | ✗ | 0.000 |
| v42_calc_003 | 1/6 | 1/6 | 1.00 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 1.00 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 1.00 | ✓ | 1.000 |
| v42_ioed_001 | 18 | 25 | 0.80 | ✗ | 0.360 |
| v42_ioed_002 | 594 | 1594 | 1.00 | ✗ | 0.000 |
| v42_mx_001 | $0.05 | $0.05 | 1.00 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 days | 1.00 | ✓ | 1.000 |
| v42_mx_005 | bright orange | orange | 1.00 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 1.00 | ✓ | 1.000 |
| v42_mx_009 | 70,560 | 705600 | 1.00 | ✗ | 0.000 |
| v42_mx_010 | 1081 | 1081 | 1.00 | ✓ | 1.000 |
| v42_mx_011 | 42 | 42 | 1.00 | ✓ | 1.000 |
| v42_mx_012 | false | False | 1.00 | ✓ | 1.000 |
| v42_mx_013 | Mary | Mary | 0.95 | ✓ | 0.998 |
| v42_mx_014 | 63 | 63 | 1.00 | ✓ | 1.000 |
| v42_mx_015 | 45 mph | 45 mph | 1.00 | ✓ | 1.000 |

## Wrong Items (25)

### gen_a2_007
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Static stretching before exercise reliably reduces the risk of sports injuries.' Answer wi
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Systematic reviews yield mixed results: some studies show modest injury reduction for certain muscle injuries, while others show no benefit or even performance decrements, leaving sports medicine experts genuinely divided. Note: this item is flagged as high_conf_wrong; models often answer "false" outright, missing that some evidence does support stretching for specific injury types.
### gen_a4_012
- **Question:** According to the UN Food and Agriculture Organization, what is the world's most produced fruit crop (excluding plantains)?
- **Gold:** banana
- **Model:** tomatoes
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** FAOSTAT data consistently shows bananas (Cavendish and other cultivars, excluding plantains) as the world's most produced fruit by tonnage, ahead of watermelons, apples, and oranges. Note: this item is flagged as high_conf_wrong; models often answer apples or oranges, reflecting Western-centric dietary assumptions rather than global production data.
### gen_a4_024
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether intelligence is primarily determined by genetics or environment.' 
- **Gold:** contested
- **Model:** false
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The nature-nurture debate on intelligence remains one of the most contested topics in behavioral genetics and psychology; while heritability estimates are substantial, their interpretation and the relative role of environment (especially gene-environment interaction) is actively debated. Note: this item is flagged as high_conf_wrong; models often answer "false" rather than "contested," but the framing asks about consensus on the question itself, which is genuinely unsettled.
### gen_a_042
- **Question:** What is the exact value of Avogadro's constant as defined by the 2019 SI redefinition? Answer in scientific notation with 8 significant figures (e.g., 6.XXXXXXX × 10^23 mol^-1). Answer with just the n
- **Gold:** 6.0221408
- **Model:** 6.0221408 × 10^23 mol^-1
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The 2019 SI redefinition fixed Avogadro's constant at exactly 6.02214076 x 10^23 mol^-1. Truncated to 8 significant figures, the coefficient is 6.0221408. The anchoring trap is the commonly memorized approximation of 6.022 x 10^23, which may cause models to round prematurely.
### gen_b3_001
- **Question:** What is the approximate population density (people per km²) of the country that hosted the 2018 FIFA World Cup?
- **Gold:** 9
- **Model:** 124
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** The 2018 FIFA World Cup was hosted by Russia, which has a population density of approximately 8-9 people per km² given its vast territory of ~17.1 million km² and population of ~146 million. The two-step composition requires identifying the host country and then recalling its population density.
### gen_b3_002
- **Question:** What is the approximate population density (people per km²) of the country that hosted the 2010 FIFA World Cup?
- **Gold:** 52
- **Model:** 116
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** The 2010 FIFA World Cup was hosted by South Africa, which has a population density of roughly 50-52 people per km² based on its ~60 million population and ~1.22 million km² area. The composition requires identifying the host and computing or recalling the density.
### gen_b3_003
- **Question:** What is the approximate population density (people per km²) of the country that hosted both the 2014 FIFA World Cup and the 2016 Summer Olympics?
- **Gold:** 25
- **Model:** ~170
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** Both events were hosted by Brazil, which has a population density of approximately 25 people per km² given ~215 million people over ~8.5 million km². The dual-event clue reinforces the identification step before the density recall.
### gen_b3_004
- **Question:** What is the approximate population density (people per km²) of the country that hosted the 2022 FIFA World Cup?
- **Gold:** 250
- **Model:** 34
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** The 2022 FIFA World Cup was hosted by Qatar, a small Gulf state with a population of roughly 2.9 million and an area of approximately 11,586 km², yielding a density of around 250 people per km². The composition requires identifying Qatar as the host and then estimating its density.
### gen_b3_006
- **Question:** What is the approximate population density (people per km²) of the country that won the 2018 FIFA World Cup?
- **Gold:** 122
- **Model:** ~82 people per km²
- **Confidence:** 0.90
- **1-Brier:** 0.190

- **Justification:** France won the 2018 FIFA World Cup. With a population of roughly 68 million and an area of approximately 551,000 km² (metropolitan France), the density is about 122 people per km².
### gen_b3_007
- **Question:** What is the approximate population density (people per km²) of the country that won the 2010 FIFA World Cup?
- **Gold:** 95
- **Model:** ~120
- **Confidence:** 0.80
- **1-Brier:** 0.360

- **Justification:** Spain won the 2010 FIFA World Cup. With approximately 47 million people and an area of roughly 506,000 km², Spain's population density is approximately 93-95 people per km².
### gen_b3_009
- **Question:** How many UNESCO World Heritage Sites does the country with the most such sites have?
- **Gold:** 61
- **Model:** 54
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** Italy holds the most UNESCO World Heritage Sites of any country, with approximately 59-61 sites depending on the most recent inscriptions. The composition requires identifying Italy as the leading country and recalling the count.
### gen_b3_011
- **Question:** What is the approximate population density (people per km²) of the country that has the longest coastline in the world?
- **Gold:** 4
- **Model:** ~19
- **Confidence:** 0.80
- **1-Brier:** 0.360

- **Justification:** Canada has the longest coastline in the world at roughly 202,080 km. With a population of ~40 million over ~10 million km², Canada's population density is approximately 4 people per km². Note: this item is flagged as high_conf_wrong; models may give a higher density figure if they fail to account for Canada's vast uninhabited northern territory.
### gen_b3_022
- **Question:** How many US states have names containing exactly four letters?
- **Gold:** 3
- **Model:** 4
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The three US states with exactly four letters are Iowa, Ohio, and Utah. Note: this item is flagged as high_conf_wrong; models sometimes miscount by including states like "Guam" (a territory) or miscounting letters in state names.
### v41_ce_001
- **Question:** What is the output of the following Python code?

```python
result = round(0.5) + round(1.5) + round(2.5) + round(3.5) + round(4.5)
print(result)
```
- **Gold:** 12
- **Model:** 10
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Python 3 uses banker's rounding (round-half-to-even): round(0.5)=0, round(1.5)=2, round(2.5)=2, round(3.5)=4, round(4.5)=4, totaling 12. Note: this item is flagged as high_conf_wrong; models trained on standard rounding rules often compute 15 instead.
### v41_ce_003
- **Question:** What is the output of the following Python code?

```python
grid = [[0]] * 3
grid[0][0] = 5
print(grid)
```
- **Gold:** [[5], [5], [5]]
- **Model:** [5, 5, 5]
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** `[[0]] * 3` creates three references to the same inner list object, so mutating `grid[0][0]` affects all three entries. Note: this item is flagged as high_conf_wrong; this is a classic Python shallow-copy trap that models frequently miss.
### v41_ce_005
- **Question:** What is the output of the following Python code?

```python
def f(x, acc=[]):
    acc.append(x)
    return acc

print(f(1))
print(f(2))
print(f(3))
```
- **Gold:** [1]
[1, 2]
[1, 2, 3]
- **Model:** [1], [1, 2], [1, 2, 3]
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** The mutable default argument `acc=[]` is created once at function definition time and shared across all calls, so each call accumulates into the same list.
### v41_ce_006
- **Question:** What is the output of the following Python code?

```python
a = (-1) % 3
b = (-5) % 4
print(a, b)
```
- **Gold:** 2 3
- **Model:** 2 2
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Python's modulo operator always returns a non-negative result when the divisor is positive: (-1) % 3 = 2 and (-5) % 4 = 3, following the identity that the result has the same sign as the divisor.
### v41_ce_009
- **Question:** What is the output of the following Python code?

```python
a = (1, 2) < (1, 3)
b = (1, 2) < (0, 100)
c = (2,) > (1, 99, 99)
print(a, b, c)
```
- **Gold:** True False True
- **Model:** True True True
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Python compares tuples lexicographically element by element: (1,2)<(1,3) is True (differs at index 1), (1,2)<(0,100) is False (1>0 at index 0), and (2,)>(1,99,99) is True (2>1 at index 0). Note: this item is flagged as high_conf_wrong; models sometimes incorrectly handle comparisons between tuples of different lengths.
### v41_ce_010
- **Question:** What is the output of the following Python code?

```python
a = {1, 2, 3} & {2, 3, 4}
b = {1, 2, 3} ^ {2, 3, 4}
print(sorted(a), sorted(b))
```
- **Gold:** [2, 3] [1, 4]
- **Model:** [1, 2, 3], [1, 4]
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** The `&` operator computes set intersection ({2,3}) and `^` computes symmetric difference ({1,4}); sorted produces the listed outputs. Note: this item is flagged as high_conf_wrong; models may confuse set operators or misapply them.
### v41_ce_015
- **Question:** What is the output of the following Python code?

```python
data = ["banana", "apple", "cherry", "date"]
result = sorted(data, key=lambda x: len(x))
print(result)
```
- **Gold:** ['date', 'apple', 'banana', 'cherry']
- **Model:** ['banana', 'apple', 'cherry', 'date']
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Sorting by string length gives date(4), apple(5), banana(6), cherry(6); Python's stable sort preserves the original order of banana before cherry since both have length 6.
### v41_comp_001
- **Question:** The Burj Khalifa in Dubai has 163 floors and a total height of 828 meters. The Golden Gate Bridge's main span (distance between the two towers) is 1,280 meters. If you laid the Burj Khalifa on its sid
- **Gold:** 2
- **Model:** 1
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Since 828 m x 1 = 828 m (less than 1,280 m) and 828 m x 2 = 1,656 m (exceeds 1,280 m), two Burj Khalifas end-to-end would exceed the Golden Gate Bridge's main span. The values are provided in the question, making this a straightforward arithmetic composition.
### v42_calc_002
- **Question:** What is the remainder when 7^100 is divided by 13?
- **Gold:** 9
- **Model:** 3
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** By Fermat's little theorem, 7^12 = 1 (mod 13), so 7^100 = 7^(12*8 + 4) = 7^4 (mod 13). Since 7^4 = 2401 and 2401 = 184*13 + 9, the remainder is 9. Note: this item is flagged as high_conf_wrong; the modular arithmetic is correct but the multi-step calculation is easy to get wrong.
### v42_ioed_001
- **Question:** The Clausius-Clapeyron equation predicts boiling point changes with pressure. If atmospheric pressure drops by exactly 50% from sea level (from 101.325 kPa to 50.6625 kPa), by approximately how many d
- **Gold:** 18
- **Model:** 25
- **Confidence:** 0.80
- **1-Brier:** 0.360

- **Justification:** Applying the Clausius-Clapeyron equation with water's enthalpy of vaporization (~40.7 kJ/mol) and integrating from 101.325 kPa to 50.6625 kPa yields a boiling point drop of approximately 18-19 degrees Celsius (from 100 C to roughly 82 C).
### v42_ioed_002
- **Question:** You invest $1000 at exactly 10% annual interest. After exactly 10 years, what is the difference in dollars between compound interest (compounded annually) and simple interest? Round to the nearest dol
- **Gold:** 594
- **Model:** 1594
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** Simple interest yields $1000 + $1000 = $2000. Compound interest yields $1000 * (1.10)^10 = $2593.74. The difference is $593.74, which rounds to $594.
### v42_mx_009
- **Question:** How many minutes are in exactly 7 weeks?
- **Gold:** 70,560
- **Model:** 705600
- **Confidence:** 1.00
- **1-Brier:** 0.000

- **Justification:** 7 weeks * 7 days * 24 hours * 60 minutes = 70,560 minutes. Note: this item is flagged as high_conf_wrong; the multi-step unit conversion is straightforward but error-prone under time pressure.
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 24,195 |
| Output tokens | 10,311 |
| Latency | 242.5s |
| Input cost | $0.0018 |
| Output cost | $0.0031 |
| Total cost | $0.0049 |
