# MetaJudge v6.1 — Confidence Calibration Audit Report

**Model:** 🤖 openai/gpt-5.4-2026-03-05
**Date:** 2026-04-03 04:11 UTC
**Task:** metajudge_calibration_v61 | **Grading engine:** grading_v2
**Items scored:** 32/105

## Performance Summary

| Metric | Value |
|--------|-------|
| Accuracy | 26/32 (81.2%) |
| Mean 1-Brier | 0.8418 |
| Normalized score | 0.367 |
| Mean confidence | 0.954 |
| Overconfident wrong (conf ≥ 0.9) | 5 |

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
| gen_a2_001 | contested | false | 0.93 | ✗ | 0.135 |
| gen_a2_007 | contested | false | 0.91 | ✗ | 0.172 |
| gen_a3_017 | Canada | Canada | 0.98 | ✓ | 1.000 |
| gen_a3_032 | 299792458 | 299792458 | 0.99 | ✓ | 1.000 |
| gen_a3_035 | 6.02214076e23 | 6.02214076 × 10^23 mol⁻¹ | 0.99 | ✓ | 1.000 |
| gen_a4_022 | contested | false | 0.98 | ✗ | 0.040 |
| gen_a_042 | 6.0221408 | 6.0221408 | 0.99 | ✓ | 1.000 |
| gen_b2_021 | france | France | 0.93 | ✓ | 0.995 |
| gen_b3_006 | 122 | 119 | 0.78 | ✓ | 0.952 |
| gen_b3_007 | 95 | 200 | 0.72 | ✗ | 0.482 |
| gen_b3_009 | 61 | 59 | 0.71 | ✓ | 0.916 |
| gen_b3_022 | 3 | 19 | 0.95 | ✗ | 0.098 |
| gen_b3_029 | 48 | 48 | 0.99 | ✓ | 1.000 |
| gen_b3_031 | -4 | 4% decrease | 0.99 | ✓ | 1.000 |
| gen_b3_033 | Sudan | Sudan | 0.97 | ✓ | 0.999 |
| gen_b_037 | false | false | 0.96 | ✓ | 0.998 |
| gen_b_040 | contested | false | 0.92 | ✗ | 0.154 |
| gen_b_042 | ojos del salado | Ojos del Salado | 0.98 | ✓ | 1.000 |
| v41_ce_003 | [[5], [5], [5]] | [[5], [5], [5]] | 0.99 | ✓ | 1.000 |
| v41_ce_012 | [1, 10, 4, 5] | [1, 10, 4, 5] | 0.99 | ✓ | 1.000 |
| v41_ce_013 | [6, 8] | [6, 8] | 0.99 | ✓ | 1.000 |
| v41_ce_014 | '' True 15 | '' True 15 | 0.99 | ✓ | 1.000 |
| v41_ce_015 | ['date', 'apple', 'b | ['date', 'apple', 'banana', 'cherry'] | 0.99 | ✓ | 1.000 |
| v41_comp_002 | 5.3 | 5.3 | 0.99 | ✓ | 1.000 |
| v41_comp_003 | 2,135 | 2135 | 0.99 | ✓ | 1.000 |
| v41_ct_001 | 47% | 47% | 0.99 | ✓ | 1.000 |
| v42_calc_004 | 2500 | 2500 | 0.99 | ✓ | 1.000 |
| v42_calc_005 | 259.81 | 259.81 | 0.99 | ✓ | 1.000 |
| v42_mx_002 | 47 days | 47 days | 0.99 | ✓ | 1.000 |
| v42_mx_005 | bright orange | orange | 0.99 | ✓ | 1.000 |
| v42_mx_006 | 4 | 4 | 0.99 | ✓ | 1.000 |
| v42_mx_007 | 3.1415926535 | 3.1415926536 | 0.99 | ✓ | 1.000 |

## Wrong Items (6)

### gen_a2_001
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.93
- **1-Brier:** 0.135

- **Justification:** While prolonged sitting is associated with increased mortality risk, the claim that it is "as harmful as smoking" is a specific quantitative comparison that experts disagree on -- some epidemiologists support the comparison while others argue it significantly overstates the risk. Note: this item is flagged as high_conf_wrong; models often confidently label this false, missing the genuine epidemiological debate about the magnitude of sedentary behavior risks.
### gen_a2_007
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.91
- **1-Brier:** 0.172

- **Justification:** Systematic reviews yield mixed results: some studies show modest injury reduction for certain muscle injuries, while others show no benefit or even performance decrements, leaving sports medicine experts genuinely divided. Note: this item is flagged as high_conf_wrong; models often answer "false" outright, missing that some evidence does support stretching for specific injury types.
### gen_a4_022
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.98
- **1-Brier:** 0.040

- **Justification:** Whether free will exists (in the libertarian or traditional sense) remains deeply contested across philosophy, neuroscience, and psychology, with compatibilists, hard determinists, and libertarians all maintaining active positions. Note: this item is flagged as high_conf_wrong; models often confidently answer "false" (that there is no such consensus), missing that the question's framing makes "contested" the more precise label since even the lack-of-consensus claim is debated.
### gen_b3_007
- **Gold:** 95
- **Model:** 200
- **Confidence:** 0.72
- **1-Brier:** 0.482

- **Justification:** Spain won the 2010 FIFA World Cup. With approximately 47 million people and an area of roughly 506,000 km², Spain's population density is approximately 93-95 people per km².
### gen_b3_022
- **Gold:** 3
- **Model:** 19
- **Confidence:** 0.95
- **1-Brier:** 0.098

- **Justification:** The three US states with exactly four letters are Iowa, Ohio, and Utah. Note: this item is flagged as high_conf_wrong; models sometimes miscount by including states like "Guam" (a territory) or miscounting letters in state names.
### gen_b_040
- **Gold:** contested
- **Model:** false
- **Confidence:** 0.92
- **1-Brier:** 0.154

- **Justification:** Surveys of physicists show no single interpretation commands a clear majority; the Copenhagen interpretation, many-worlds, and others each have substantial adherents, making this a genuinely contested claim. Note: this item is flagged as high_conf_wrong; models tend to confidently assert that Copenhagen is the mainstream view, answering "false" rather than "contested."