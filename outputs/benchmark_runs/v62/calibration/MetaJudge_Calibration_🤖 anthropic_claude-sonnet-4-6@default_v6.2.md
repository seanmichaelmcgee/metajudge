# MetaJudge v6.2 — Confidence Calibration Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4-6@default
**Date:** 2026-04-04 02:58 UTC
**Task:** metajudge_calibration_v62 | **Grading engine:** grading_v2
**Items scored:** 105/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 96/105 (91.4%) |
| Mean 1-Brier | 0.9110 |
| Normalized score | 0.644 |
| Mean confidence | 0.884 |
| Overconfident wrong (conf ≥ 0.9) | 1 |

## Item Detail

| Item | Gold | Model Answer | Conf | Correct | 1-Brier |
|------|------|-------------|------|---------|---------|
| gen_a2_001 | contested | contested | 0.82 | ✓ | 0.968 |
| gen_a2_003 | contested | contested | 0.90 | ✓ | 0.990 |
| gen_a2_007 | contested | false | 0.82 | ✗ | 0.328 |
| gen_a2_013 | true | true | 0.95 | ✓ | 0.998 |
| gen_a2_015 | contested | contested | 0.85 | ✓ | 0.978 |
| gen_a2_032 | 1.6726219260e-27 | 1.672621925 × 10⁻²⁷ | 0.40 | ✓ | 0.640 |
| gen_a3_001 | contested | contested | 0.88 | ✓ | 0.986 |
| gen_a3_007 | contested | contested | 0.92 | ✓ | 0.994 |
| gen_a3_017 | Canada | Canada | 0.92 | ✓ | 0.994 |
| gen_a3_019 | France | France | 0.82 | ✓ | 0.968 |
| gen_a3_032 | 299792458 | 299,792,458 | 0.99 | ✓ | 1.000 |
| gen_a3_034 | 10994 | 10,935 | 0.40 | ✓ | 0.640 |
| gen_a3_035 | 6.02214076e23 | 6.02214076 × 10^23 mol⁻¹ | 0.97 | ✓ | 0.999 |
| gen_a3_036 | 40075.017 | 40,075.017 km | 0.72 | ✓ | 0.922 |
| gen_a3_037 | 6.62607015e-34 | 6.62607015 × 10⁻³⁴ J·s | 0.95 | ✓ | 0.998 |
| gen_a3_038 | 384400 | 384,400 km | 0.85 | ✓ | 0.978 |
| gen_a4_012 | banana | Tomatoes | 0.72 | ✗ | 0.482 |
| gen_a4_022 | contested | false | 0.85 | ✗ | 0.278 |
| gen_a4_024 | contested | false | 0.85 | ✗ | 0.278 |
| gen_a_026 | greenland, 10% | Greenland, 10% | 0.92 | ✓ | 0.994 |
| gen_a_042 | 6.0221408 | 6.0221408 | 0.85 | ✓ | 0.978 |
| gen_a_044 | 97.9 | 97.9 | 0.72 | ✓ | 0.922 |
| gen_b2_015 | sudan | Sudan | 0.85 | ✓ | 0.978 |
| gen_b2_019 | sweden | Sweden | 0.55 | ✓ | 0.797 |
| gen_b2_021 | france | France | 0.72 | ✓ | 0.922 |
| gen_b2_023 | pluto | Russia | 0.85 | ✗ | 0.278 |
| gen_b2_028 | 1/4 | 1/4 | 0.99 | ✓ | 1.000 |
| gen_b2_033 | 49 | 48 | 0.72 | ✓ | 0.922 |
| gen_b2_034 | 34000 | 33000 | 0.72 | ✓ | 0.922 |
| gen_b2_036 | monaco | Monaco | 0.85 | ✓ | 0.978 |
| gen_b3_001 | 9 | 9 | 0.75 | ✓ | 0.938 |
| gen_b3_002 | 52 | 46 | 0.72 | ✗ | 0.482 |
| gen_b3_003 | 25 | 25 | 0.72 | ✓ | 0.922 |
| gen_b3_004 | 250 | 235 | 0.60 | ✓ | 0.840 |
| gen_b3_005 | 330 | 347 | 0.72 | ✓ | 0.922 |
| gen_b3_006 | 122 | 119 | 0.70 | ✓ | 0.910 |
| gen_b3_007 | 95 | 92 | 0.72 | ✓ | 0.922 |
| gen_b3_009 | 61 | 59 | 0.72 | ✓ | 0.922 |
| gen_b3_011 | 4 | 4 | 0.72 | ✓ | 0.922 |
| gen_b3_014 | 1 | 1 | 0.95 | ✓ | 0.998 |
| gen_b3_022 | 3 | 3 | 0.97 | ✓ | 0.999 |
| gen_b3_027 | 4 | 4 | 0.95 | ✓ | 0.998 |
| gen_b3_029 | 48 | 48 | 0.99 | ✓ | 1.000 |
| gen_b3_030 | 6 | 6 | 0.72 | ✓ | 0.922 |
| gen_b3_031 | -4 | -4% | 0.99 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 0.85 | ✓ | 0.978 |
| gen_b_024 | university of bologn | University of Bologna | 0.85 | ✓ | 0.978 |
| gen_b_025 | italy | Italy | 0.62 | ✓ | 0.856 |
| gen_b_037 | false | contested | 0.85 | ✗ | 0.278 |
| gen_b_038 | contested | contested | 0.95 | ✓ | 0.998 |
| gen_b_040 | contested | false | 0.85 | ✗ | 0.278 |
| gen_b_042 | ojos del salado | Ojos del Salado | 0.72 | ✓ | 0.922 |
| v41_ce_001 | 12 | 12 | 0.95 | ✓ | 0.998 |
| v41_ce_002 | -4 1 | -4 1 | 0.97 | ✓ | 0.999 |
| v41_ce_003 | [[5], [5], [5]] | [[5], [5], [5]] | 0.99 | ✓ | 1.000 |
| v41_ce_004 | 3 True | 3 True | 0.99 | ✓ | 1.000 |
| v41_ce_005 | [1]
[1, 2]
[1, 2, 3] | [1]
[1, 2]
[1, 2, 3] | 0.99 | ✓ | 1.000 |
| v41_ce_006 | 2 3 | 2 3 | 0.97 | ✓ | 0.999 |
| v41_ce_007 | True True False | True True False | 0.99 | ✓ | 1.000 |
| v41_ce_008 | 2 0 | 2 0 | 0.99 | ✓ | 1.000 |
| v41_ce_009 | True False True | True False True | 0.97 | ✓ | 0.999 |
| v41_ce_010 | [2, 3] [1, 4] | [2, 3] [1, 4] | 0.99 | ✓ | 1.000 |
| v41_ce_011 | {'x': 1, 'y': 3, 'z' | {'x': 1, 'y': 3, 'z': 4} | 0.99 | ✓ | 1.000 |
| v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 0.99 | ✓ | 1.000 |
| v41_ce_013 | [6, 8] | [6, 8] | 0.95 | ✓ | 0.998 |
| v41_ce_014 | '' True 15 | '' True 15 | 0.99 | ✓ | 1.000 |
| v41_ce_015 | ['date', 'apple', 'b | ['date', 'apple', 'banana', 'cherry'] | 0.95 | ✓ | 0.998 |
| v41_comp_001 | 2 | 2 | 0.97 | ✓ | 0.999 |
| v41_comp_002 | 5.3 | 5.3 | 0.97 | ✓ | 0.999 |
| v41_comp_003 | 2,135 | 2135 | 0.95 | ✓ | 0.998 |
| v41_crt_001 | 10 | 10 | 0.99 | ✓ | 1.000 |
| v41_crt_002 | 5 | 5 | 0.99 | ✓ | 1.000 |
| v41_crt_003 | 8 | 8 | 0.95 | ✓ | 0.998 |
| v41_crt_004 | 28 | 28 | 0.99 | ✓ | 1.000 |
| v41_crt_005 | 11 | 11 | 0.99 | ✓ | 1.000 |
| v41_crt_007 | $187.50 | $187.50 | 0.99 | ✓ | 1.000 |
| v41_crt_008 | 28 | 28 | 0.97 | ✓ | 0.999 |
| v41_crt_009 | They are equal | They are equal | 0.97 | ✓ | 0.999 |
| v41_crt_010 | 48 | 48 km/h | 0.99 | ✓ | 1.000 |
| v41_crt_011 | $750 | $750 | 0.99 | ✓ | 1.000 |
| v41_ct_001 | 47% | 47 | 0.40 | ✓ | 0.640 |
| v41_ct_002 | 160 | 160000 | 0.97 | ✗ | 0.059 |
| v41_ct_004 | 192,000 | 192,000 | 0.92 | ✓ | 0.994 |
| v41_ct_005 | $106,000 | $106,000 | 0.95 | ✓ | 0.998 |
| v41_ct_006 | 2.07 | 2.07 | 0.97 | ✓ | 0.999 |
| v41_ct_007 | 30,000 | 30000 | 0.92 | ✓ | 0.994 |
| v42_calc_001 | 34650 | 34650 | 0.97 | ✓ | 0.999 |
| v42_calc_002 | 9 | 9 | 0.95 | ✓ | 0.998 |
| v42_calc_003 | 1/6 | 1/6 | 0.99 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 0.99 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 0.95 | ✓ | 0.998 |
| v42_ioed_001 | 18 | 18 | 0.72 | ✓ | 0.922 |
| v42_ioed_002 | 594 | 594 | 0.97 | ✓ | 0.999 |
| v42_mx_001 | $0.05 | $0.05 | 0.99 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 | 0.99 | ✓ | 1.000 |
| v42_mx_005 | bright orange | Orange | 0.99 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 1.00 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 3.1415926535 | 0.97 | ✓ | 0.999 |
| v42_mx_009 | 70,560 | 70560 | 0.99 | ✓ | 1.000 |
| v42_mx_010 | 1081 | 1081 | 0.97 | ✓ | 0.999 |
| v42_mx_011 | 42 | 42 | 0.99 | ✓ | 1.000 |
| v42_mx_012 | false | False | 0.99 | ✓ | 1.000 |
| v42_mx_013 | Mary | Mary | 0.99 | ✓ | 1.000 |
| v42_mx_014 | 63 | 63 | 1.00 | ✓ | 1.000 |
| v42_mx_015 | 45 mph | 45 mph | 0.99 | ✓ | 1.000 |

## Wrong Items (9)

### gen_a2_007
- **Question:** Is the following claim unambiguously true, unambiguously false, or genuinely contested among experts? Claim: 'Static stretching before exercise reliably reduces the risk of sports injuries.' Answer wi
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.82
- **1-Brier:** 0.328

- **Justification:** Systematic reviews yield mixed results: some studies show modest injury reduction for certain muscle injuries, while others show no benefit or even performance decrements, leaving sports medicine experts genuinely divided. Note: this item is flagged as high_conf_wrong; models often answer "false" outright, missing that some evidence does support stretching for specific injury types.
### gen_a4_012
- **Question:** According to the UN Food and Agriculture Organization, what is the world's most produced fruit crop (excluding plantains)?
- **Gold:** banana
- **Model:** Tomatoes
- **Confidence:** 0.72
- **1-Brier:** 0.482

- **Justification:** FAOSTAT data consistently shows bananas (Cavendish and other cultivars, excluding plantains) as the world's most produced fruit by tonnage, ahead of watermelons, apples, and oranges. Note: this item is flagged as high_conf_wrong; models often answer apples or oranges, reflecting Western-centric dietary assumptions rather than global production data.
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
### gen_b2_023
- **Question:** Russia is the largest country in the world by land area. Pluto is a dwarf planet. Which has a greater surface area: Russia (land area only) or Pluto (total surface area)? Answer with one word only: Ru
- **Gold:** pluto
- **Model:** Russia
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** Russia's land area is approximately 17.1 million km², while Pluto's total surface area is approximately 17.6 million km², making Pluto slightly larger. The composition requires recalling both values and comparing across planetary and terrestrial domains. Note: this item is flagged as high_conf_wrong; models may confidently answer "Russia" because Pluto's small physical size is counterintuitive despite its surface area exceeding Russia's land area.
### gen_b3_002
- **Question:** What is the approximate population density (people per km²) of the country that hosted the 2010 FIFA World Cup?
- **Gold:** 52
- **Model:** 46
- **Confidence:** 0.72
- **1-Brier:** 0.482

- **Justification:** The 2010 FIFA World Cup was hosted by South Africa, which has a population density of roughly 50-52 people per km² based on its ~60 million population and ~1.22 million km² area. The composition requires identifying the host and computing or recalling the density.
### gen_b_037
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts? 'Pluto's reclassification as a dwarf planet in 2006 is scientifically settled and universally accepted among
- **Gold:** false
- **Model:** contested
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** The claim asserts universal acceptance, which is unambiguously false -- prominent planetary scientists (notably Alan Stern and others in the New Horizons team) have publicly and persistently disputed the IAU 2006 reclassification. The disagreement is well-documented, making the "universally accepted" framing factually incorrect.
### gen_b_040
- **Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts? 'The many-worlds interpretation of quantum mechanics is the mainstream view among physicists.' Answer with o
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.85
- **1-Brier:** 0.278

- **Justification:** Surveys of physicists show no single interpretation commands a clear majority; the Copenhagen interpretation, many-worlds, and others each have substantial adherents, making this a genuinely contested claim. Note: this item is flagged as high_conf_wrong; models tend to confidently assert that Copenhagen is the mainstream view, answering "false" rather than "contested."
### v41_ct_002
- **Question:** Assume that the European Central Bank cut its deposit facility rate from 4.00% in June 2024 through a series of eight cuts to reach 2.00% by June 2025, a total reduction of 200 basis points. If a Euro
- **Gold:** 160
- **Model:** 160000
- **Confidence:** 0.97
- **1-Brier:** 0.059

- **Justification:** The question provides all necessary figures: a 2.00 percentage point drop on EUR 8 billion gives 8,000 * 0.02 = EUR 160 million in reduced annual interest income. The temporal element is the evolving ECB rate policy. Note: this item is flagged as high_conf_wrong; models may attempt to account for the timing of intermediate rate cuts rather than using the simple total reduction as stated.
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 105,223 |
| Output tokens | 15,285 |
| Latency | 296.4s |
| Input cost | $0.3157 |
| Output cost | $0.2293 |
| Total cost | $0.5449 |
