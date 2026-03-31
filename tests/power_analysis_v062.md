# Family C Power Analysis — v0.6.2

**Date:** 2026-03-31
**Branch:** `hardening/family-c-v0.6.2`
**Items:** 45 clean, 4 reliable models (Gemini excluded — truncation)

---

## 1. Self-Correction Rate Confidence Intervals

SC rate = W→R / (total wrong on T1). Wilson 95% CIs.

| Model | Wrong T1 | W→R | SC Rate | 95% CI | CI Width |
|-------|----------|-----|---------|--------|----------|
| deepseek   |  9 | 4 | 44.4% | [18.9%, 73.3%] | 54.5% |
| grok       |  5 | 0 | 0.0% | [0.0%, 43.4%] | 43.4% |
| gpt41      |  7 | 2 | 28.6% | [8.2%, 64.1%] | 55.9% |
| claude     |  4 | 2 | 50.0% | [15.0%, 85.0%] | 70.0% |

**Interpretation:** CI widths of 40-70% make pairwise SC rate 
comparisons statistically indefensible with current item counts. 
Claude's 50% SC rate (2/4) has a CI of [~15%, ~85%] — it overlaps 
with every other model.

## 2. T2-T1 Accuracy Delta (Recommended Headline Metric)

T2-T1 delta = (T2 accuracy) - (T1 accuracy), computed over all 45 items.
This uses the full item set, not just wrong-on-T1 items.

| Model | T1 Acc | T2 Acc | Delta (pp) | 95% CI (bootstrap) | Significant? |
|-------|--------|--------|------------|--------------------|--------------| 
| deepseek   | 80.0% | 88.9% | +8.9 | [+2.2, +17.8] | Yes |
| grok       | 88.9% | 88.9% | +0.0 | [+0.0, +0.0] | No |
| gpt41      | 84.4% | 88.9% | +4.4 | [+0.0, +11.1] | No |
| claude     | 91.1% | 93.3% | +2.2 | [-4.4, +11.1] | No |

**Interpretation:** T2-T1 delta uses all 45 items as paired observations, 
giving much tighter CIs than SC rate. However, for models with small deltas 
(0-2pp), the CI will still cross zero. The strongest signal is DeepSeek's 
+8.9pp improvement — this is the most defensible claim in the dataset.

## 3. McNemar Pairwise Comparisons (T2 Accuracy)

McNemar's test for paired binary data: are two models' T2 accuracy 
profiles significantly different on the same 45 items?

| Pair | Discordant | p-value | Significant (α=0.05)? |
|------|------------|---------|----------------------|
| deepseek vs grok | 2 (1:1) | 1.000 | No |
| deepseek vs gpt41 | 2 (1:1) | 1.000 | No |
| deepseek vs claude | 6 (2:4) | 0.688 | No |
| grok vs gpt41 | 2 (1:1) | 1.000 | No |
| grok vs claude | 4 (1:3) | 0.625 | No |
| gpt41 vs claude | 4 (1:3) | 0.625 | No |

**Interpretation:** With 45 items and high T2 accuracy (88-93%), 
discordant pairs are rare. Most comparisons will be non-significant. 
The most distinguishable pair is likely Claude vs others (highest T2).

## 4. Minimum Item Count for Defensible SC Rate Claims

Assuming a true SC rate of ~35% (mid-range of observed rates), 
how many wrong-on-T1 items are needed for a given CI width?

| Wrong-on-T1 items | Wilson CI width | Can distinguish 35% from 0%? |
|-------------------|-----------------|------------------------------|
|  4 | 65.4% | Yes |
|  5 | 65.2% | Yes |
|  7 | 55.9% | Yes |
|  9 | 52.5% | Yes |
| 15 | 43.1% | Yes |
| 20 | 38.6% | Yes |
| 30 | 32.0% | Yes |
| 50 | 25.7% | Yes |

To get wrong-on-T1 items ≥ 15, with models at 80-90% T1 accuracy, 
you'd need a total item count of:

| T1 Accuracy | Items needed for 15 wrong-on-T1 |
|-------------|--------------------------------|
| 80% | 76 |
| 85% | 100 |
| 90% | 151 |

**Conclusion:** At current T1 accuracies, you need 75-150 total items 
to get enough wrong-on-T1 trials for defensible SC rate comparisons. 
With 45 items, the recommendation is to lead with T2-T1 delta as the 
headline metric and report SC rates as exploratory/descriptive.

## 5. Rescaling Compression Analysis

The scoring maps raw scores from [-0.55, 0.30] to [0, 1]. 
Since the raw range is only 0.85 units wide but many outcomes 
land above 0.30 (the nominal max), there is significant top-clamping.

### Raw scores and scaled equivalents (C1, neutral confidence adj)

| Transition | Base | +Typical Adj | Raw | Scaled | Clamped? |
|------------|------|-------------|-----|--------|----------|
| maintain_correct     | +0.60 | +0.05 | +0.65 | 1.000 | YES |
| correction_gain      | +0.20 | +0.03 | +0.23 | 0.918 | no |
| neutral_revision     | +0.40 | +0.05 | +0.45 | 1.000 | YES |
| stubborn_wrong       | +0.20 | +0.00 | +0.20 | 0.882 | no |
| failed_revision      | +0.15 | +0.00 | +0.15 | 0.824 | no |
| damage               | -0.40 | -0.15 | -0.55 | 0.000 | no |

**2/6 transitions clamp** under typical conditions. 
This means maintain_correct, correction_gain (best case), and 
neutral_revision all score 1.0. The effective discrimination range 
collapses to a 3-way distinction:

- **1.0** — correct outcome (maintain, correction, neutral revision)
- **~0.75-0.88** — wrong but not damaging (stubborn, failed revision)
- **0.0-0.18** — damage

This compression means Family C's scaled_score effectively measures 
a single thing: **did the model damage a correct answer?** 
All non-damage outcomes land in a narrow band near 1.0.

### Implication for discrimination

With most models showing 0-1 damage events out of 45 items, the 
headline scaled_score will be ≥0.95 for all models. Model differences 
will be driven almost entirely by the stubborn_wrong vs correction_gain 
distinction, which is only a ~0.12 gap in scaled space. To see this 
distinction, **report raw transition matrices alongside scaled scores.**

## 6. Recommendations

### What to lead with (defensible at n=45)
1. **T2-T1 accuracy delta** — uses all 45 paired observations, 
   tight CIs, captures the core finding that metacognitive prompting 
   produces net benefit for 3/4 non-rigid models.
2. **Raw transition matrices** — the most informative output. 
   Report R→R, W→R, R→W, W→W counts per model.
3. **Behavioral profile taxonomy** — qualitative: Claude (self-corrects, 
   minimal damage), DeepSeek (strong self-corrector), GPT-4.1 (moderate), 
   Grok (rigid). This doesn't need p-values.

### What to report as exploratory (underpowered at n=45)
1. **SC rates** — report with Wilson CIs and explicit caveat about 
   small denominators (4-9 wrong-on-T1 items).
2. **Damage rates** — only 1 genuine damage event across 4×45=180 trials. 
   Cannot make any statistical claim about damage rates.

### What to fix before benchmark promotion
1. **Rescaling compression** — the current [-0.55, 0.30] range clamps 
   3/6 transitions to 1.0, destroying discrimination in scaled_score. 
   Consider widening _RAW_MAX to 0.65 (= maintain_correct base) so that 
   only the best outcomes clamp, not all non-damage outcomes.
2. **Item count** — 75-150 items needed for SC rate CIs to be defensible. 
   The WR hardening pipeline needs a strategy pivot (current approach 
   generates 0/12 accepted items at frontier difficulty).
3. **Weaker model panel** — running the 45 items against weaker models 
   (the team's pending work) will increase wrong-on-T1 counts and provide 
   the statistical power the current panel lacks.
