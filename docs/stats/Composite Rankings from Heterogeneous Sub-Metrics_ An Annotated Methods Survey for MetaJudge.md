# Composite rankings from heterogeneous sub-metrics: an annotated methods survey for MetaJudge

MetaJudge faces a composite-construction problem at the intersection of three literatures — LLM benchmarking, psychometric test theory, and multi-criteria decision analysis — yet its five constraining properties (heterogeneous metrics, n = 5, overlapping CIs, test-retest instability, divergent rank orderings) make most standard tools underpowered or inapplicable. **No existing LLM benchmark has solved this exact problem.** The closest precedents come from the OECD composite-indicator tradition, the Haberman subscore-value framework, and the Mogstad et al. rank-inference methodology. Equal weighting after standardization is the strong default; the open question is how to quantify ranking uncertainty, not how to optimize weights. This document surveys 30 papers and methods, organized by three research questions, to provide the menu of candidate approaches for computational evaluation.

---

## Q1 — How existing LLM benchmarks construct composites

The dominant pattern across major benchmarks is **normalize-then-average**, with surprisingly little formal sensitivity analysis. Most benchmarks either avoid producing a single composite (HELM) or use simple arithmetic means (MMLU, LiveBench, Open LLM Leaderboard). The few alternatives — Bradley-Terry models (Chatbot Arena), win-rate aggregation (AlpacaEval), social-choice methods (Vote'n'Rank) — each sidestep the heterogeneous-metric problem in different ways. Crucially, every composite methodology has drawn criticism, and **no benchmark with fewer than 10 models has attempted a formal composite with uncertainty quantification**.

---

### Liang et al. (2023) — Holistic Evaluation of Language Models (HELM)

**Venue:** arXiv / Transactions on Machine Learning Research; Stanford CRFM

**Method:** HELM Classic used **Mean Win Rate (MWR)**, a Borda-count variant: for each scenario, each model receives a win rate (fraction of other models it beats); the overall ranking equals the mean of per-scenario win rates. HELM 2025 abandoned MWR in favor of mean rescaled scores.

**Data properties:** 16 core scenarios, 7 metric dimensions (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency), 30+ models. Deliberately presents a scenarios × metrics grid rather than collapsing to one number.

**Key finding:** MWR avoids incommensurability but **depends on the competitor set** — adding or removing a weak model changes rankings of top models (violates independence of irrelevant alternatives). HELM's own 2025 documentation acknowledged this. The "Efficient Benchmarking" analysis (Choshen et al., NAACL 2024) showed a single rank change under MWR is unreliable.

**Relevance to MetaJudge:** With n = 5 models, MWR produces a score in {0, 0.25, 0.5, 0.75, 1} per scenario — extremely coarse. HELM's move away from MWR confirms its unsuitability for small panels. Addresses Property 1 (heterogeneous metrics) but fails on Property 2 (small n).

**Implementability:** Trivial — ~10 lines of Python. The conceptual issue, not the code, is the barrier.

---

### Beeching et al. (2023–2024) — Open LLM Leaderboard (HuggingFace)

**Venue:** HuggingFace Spaces; retired March 2025

**Method:** v1 used simple average of raw accuracy across 4–6 benchmarks. v2 introduced **random-baseline normalization**: `normalized = (raw − random_baseline) / (max − random_baseline) × 100`, then simple average across 6 benchmarks. Equal weighting throughout.

**Data properties:** v2: 6 benchmarks (MMLU-Pro, GPQA, MuSR, MATH Lvl 5, IFEval, BBH), 13,000+ models evaluated.

**Key finding:** Raw averaging in v1 gave disproportionate weight to easy benchmarks (HellaSwag at 95% dominated the composite). Baseline normalization in v2 partially addressed this. Criticisms included **model-merge gaming**, benchmark saturation, and the fact that simple averaging treats all benchmarks as equally important regardless of reliability. HuggingFace shut it down citing concerns that it "could encourage people to hill climb irrelevant directions."

**Relevance to MetaJudge:** Random-baseline normalization is the minimum viable standardization for heterogeneous sub-metrics (Property 1). The Open LLM Leaderboard's trajectory — simple average → normalized average → retirement — illustrates the limits of atheoretical aggregation.

**Implementability:** Trivial — ~5 lines of Python per metric.

---

### Chiang et al. (2024) — Chatbot Arena / LMSYS

**Venue:** ICML 2024 (arXiv 2403.04132)

**Method:** Pairwise human comparison → **Bradley-Terry maximum-likelihood estimation**. Logit(P(A beats B)) ∝ R_A − R_B. Produces a single latent "strength" parameter per model on an Elo-like scale with 95% bootstrap confidence intervals from 1,000 permutations.

**Data properties:** 6M+ pairwise human votes, 91+ models. Measures a single unified quantity (human preference), not a heterogeneous composite.

**Key finding:** The BT approach **completely sidesteps the composite-score problem** by measuring only one thing at a time. Separate BT fits are done per domain (coding, hard prompts, etc.) rather than combining. Vulnerable to vote manipulation, self-selection bias, and style-over-substance preference artifacts.

**Relevance to MetaJudge:** BT could convert MetaJudge's 3 family rankings into implied pairwise comparisons (3 rankings × C(5,2) = 30 comparisons), estimating 5 strength parameters. Addresses Property 5 (different orderings) elegantly. However, 30 implied comparisons with only 3 "judges" may be insufficient for stable estimation without Bayesian regularization. Does not address Properties 3–4 (CIs, instability).

**Implementability:** MLE version: ~30 lines with `scipy.optimize`. Bayesian version: ~50 lines with PyMC or Stan. The `choix` Python library implements Plackett-Luce/BT directly.

---

### Srivastava et al. (2023) — BIG-Bench / BIG-Bench Hard

**Venue:** Transactions on Machine Learning Research (BIG-Bench); arXiv (BBH, Suzgun et al. 2023)

**Method:** **Dynamic-range normalization** then averaging: `normalized = 100 × (raw − low) / (high − low)` where low = random baseline, high = human-expert or maximum score. Each task designates a preferred metric. BIG-Bench Extreme Hard (BBEH, 2025) switched to **harmonic mean** to penalize models strong on some tasks but weak on others.

**Data properties:** 204 tasks with different preferred metrics (exact-string match, multiple-choice score, Brier score, etc.) across varying item counts.

**Key finding:** Incommensurability across metrics was the central challenge — "you can't meaningfully average inches and kilograms." The normalization formula with task-specific bounds is the closest precedent for combining scores with different baselines and ceilings. The harmonic-mean variant penalizes imbalanced performance.

**Relevance to MetaJudge:** The low/high normalization is directly applicable to Families A, B, and C (Property 1). The harmonic-mean approach is relevant for Property 5 — it would penalize models that excel on one family but fail another, partially preserving dissociation. Equal task weighting regardless of reliability is a limitation shared with MetaJudge.

**Implementability:** Normalization: ~5 lines. Harmonic mean: 1 line (`scipy.stats.hmean`).

---

### Hendrycks et al. (2021) — MMLU

**Venue:** ICLR 2021 (MMLU); arXiv 2406.01574 (MMLU-Pro, Wang et al. 2024)

**Method:** Simple macro-average accuracy across 57 subjects. No normalization, no weighting by difficulty or item count.

**Data properties:** 15,908 questions across 57 subjects (MMLU), 12,000 questions across 14 subjects (MMLU-Pro). Random baselines: 25% (4-choice) and 10% (10-choice).

**Key finding:** A 2024 audit found **6.5% of MMLU questions contain errors** (57% of Virology questions had errors). GPT-4o showed **13 percentage-point variance** across different measurement implementations — measurement variance exceeded competitive differences by 13×. Demonstrates that even the simplest aggregation fails when sub-component measurement quality varies.

**Relevance to MetaJudge:** MMLU is the cautionary tale: simple averaging without normalization allows easier benchmarks to dominate variance. The measurement-variance finding (Property 4) directly parallels MetaJudge's Family C instability.

**Implementability:** Trivial.

---

### Dubois et al. (2024) — AlpacaEval 2.0

**Venue:** arXiv 2404.04475

**Method:** Win rate against GPT-4 Turbo across 805 instructions. **Length-Controlled (LC) win rates** fit a logistic GLM with model identity, normalized output-length difference, and instruction difficulty, then zero out the length term to produce a debiased counterfactual win rate. LC increased Spearman correlation with Chatbot Arena from 0.93 to 0.98.

**Data properties:** 805 instruction-following tasks, single auto-annotator judge.

**Key finding:** Raw win rates were gameably inflated by ~21% through verbosity prompting. The GLM-based debiasing reduced this to ~6%. This is an elegant example of regression-based confound removal applied to evaluation metrics.

**Relevance to MetaJudge:** If any MetaJudge family has known confounds (e.g., Family C delta correlating with T1 accuracy), a GLM could partial them out before aggregation. Addresses Property 1 (different metric types) through statistical standardization rather than normalization.

**Implementability:** ~20 lines with `statsmodels`.

---

### White et al. (2024) — LiveBench

**Venue:** arXiv 2406.19314

**Method:** Simple average of per-category scores across 6 categories (math, coding, reasoning, data analysis, instruction following, language). All scored on 0–100 with objective ground-truth scoring. Monthly question updates prevent contamination.

**Data properties:** 18 tasks across 6 categories, 49 models initially.

**Key finding:** Rank correlation between monthly updates > 0.997, suggesting that when tasks are designed on comparable scales from the start, simple averaging produces stable rankings. However, no formal sensitivity analysis of the aggregation method itself.

**Relevance to MetaJudge:** Demonstrates that simple averaging can work when metrics are homogeneous by design — the opposite of MetaJudge's situation. The monthly-update stability analysis is a model for reporting test-retest concordance (Property 4).

**Implementability:** Trivial.

---

### Burnell et al. (2023) — Rethink reporting of evaluation results in AI

**Venue:** *Science*, 380(6641), 136–138

**Method:** Not a statistical method but a policy argument. Shows that aggregate metrics obscure failure modes: a facial-recognition system at 90% overall accuracy misclassified darker-skinned females 34.5% of the time. Argues for instance-level reporting, performance-feature breakdowns, and granular sub-metric visibility alongside composites.

**Data properties:** Conceptual; draws on BIG-Bench, facial recognition, and medical AI examples.

**Key finding:** Aggregate metrics are **necessary for comparison but insufficient for understanding**. The central recommendation: always present both the composite and the full sub-metric breakdown, with instance-level data when possible.

**Relevance to MetaJudge:** Addresses Property 5 directly — the dissociation across families (Pro rank 1 on B, rank 5 on C) is exactly the kind of pattern that composites erase. The MetaScore should be presented alongside family profiles.

**Implementability:** N/A (design principle, not algorithm).

---

### Rofin et al. (2023) — Vote'n'Rank

**Venue:** EACL 2023

**Method:** Proposes 8 social-choice aggregation rules (Plurality, Dowdall, Borda, Copeland, Minimax, etc.) as alternatives to mean aggregation for multi-task benchmarks. Tasks act as voters, models as candidates.

**Data properties:** Applied to multi-task NLP benchmarks with 10–30 models and 5–15 tasks.

**Key finding:** Mean aggregation follows "unspoken utilitarian principles" that can create an "illusion of progress." Social-choice methods are more robust to outlier tasks. However, a 2025 follow-up (PAGC framework) found **nearly identical rankings** across Borda, Copeland, Condorcet, and linear aggregation when inputs are highly correlated — suggesting method choice matters less than input quality.

**Relevance to MetaJudge:** Directly proposes rank-based alternatives to score averaging (Property 1). With only 3 "voters" (families) and 5 candidates, most social-choice methods produce frequent ties (Property 2), limiting their discriminative power.

**Implementability:** Each method is 5–15 lines of Python.

---

### Zhang & Hardt (2024) — Diversity-stability trade-offs in multi-task benchmarks

**Venue:** ICML 2024 (Proceedings of Machine Learning Research, vol. 235, 58984–59002)

**Method:** Applies social-choice theory (Arrow's impossibility theorem) to multi-task benchmarks. Proves a formal **diversity-stability trade-off**: greater benchmark diversity (more heterogeneous tasks) inherently increases sensitivity to artifacts and methodological perturbations.

**Data properties:** Theoretical framework applied to Open LLM Leaderboard, HELM, and other benchmarks.

**Key finding:** Cardinal (score-based) methods can be sensitive to noise injected into individual tasks. Ordinal (rank-based) methods are sensitive to inclusion/exclusion of irrelevant models. **No aggregation method is simultaneously diverse, stable, and fair.** Low-rank structure in the benchmark-model matrix suggests PCA-like approaches could exploit redundancy.

**Relevance to MetaJudge:** Provides theoretical grounding for why MetaJudge's ranking will be unstable (Properties 2–4). With 3 diverse families, the diversity-stability trade-off is moderate — fewer components means less instability than HELM-scale benchmarks, but also less redundancy to stabilize estimates.

**Implementability:** N/A (theoretical result, not algorithm). The PCA suggestion requires more models than n = 5.

---

## Q2 — Psychometric foundations for composite construction with unreliable sub-components

The educational testing literature offers the most mature framework for this problem. Three findings dominate: **Haberman's PRMSE criterion** determines whether a sub-score is reliable enough to report; **Dawes's equal-weights result** shows that optimizing weights with small samples is counterproductive; and **Brennan's generalizability theory** provides the variance-decomposition framework for understanding Family C's instability. Together, these literatures converge on a clear message: with n = 5 and heterogeneous reliabilities, **standardize, weight equally, and report uncertainty honestly**.

---

### Haberman (2008) — When can subscores have value?

**Venue:** *Journal of Educational and Behavioral Statistics*, 33(2), 204–229

**Method:** Classical test theory framework comparing three estimators of the true subscore: the observed subscore alone (Kelley-regressed), the total score, and a weighted combination. Uses **PRMSE (Proportional Reduction in Mean Squared Error)** as the decision criterion. PRMSE_s = α_s (subscore reliability). PRMSE_x = [ρ(true_s, x)]² × α_x (total-score-based prediction). Report the subscore only if PRMSE_s > PRMSE_x.

**Data properties:** Applied to SAT Verbal (3 subscores, ~26 items each, α ≈ 0.79) and Praxis (4 subscores, ~25 items, α ≈ 0.72). Large examinee samples.

**Key finding:** A subscore has added value only when it has **high reliability**, the total has **low reliability**, and the subscore is **distinct** (low disattenuated correlation with the total). Most operational tests failed these criteria — subscores rarely add value.

**Relevance to MetaJudge:** Directly addresses whether Family C (51 items, estimated reliability ~0.35 from test-retest) should contribute to the composite (Properties 1, 4). If the MetaScore total predicts Family C's true score better than Family C's observed score does, Family C should be downweighted or excluded. The PRMSE computation requires only sample variances, correlations, and reliabilities.

**Implementability:** ~20 lines of Python with numpy. R packages `sirt::prmse.subscores.scales` and `subscore::CTTsub` exist.

---

### Sinharay (2010) — How often do subscores have added value?

**Venue:** *Journal of Educational Measurement*, 47(2), 150–174

**Method:** Comprehensive simulation plus operational-data study applying the Haberman (2008) PRMSE framework across 22 operational tests and systematic simulations varying item count, disattenuated correlations, and number of subscores.

**Data properties:** 22 operational tests with 2–7 subscores, item counts from 11 to 69, simulated data with disattenuated correlations from 0.7 to 1.0 and subscore lengths from 10 to 40 items.

**Key finding:** Tests with average disattenuated correlations ≥ 0.95 **never** had subscores with added value. Rule of thumb: subscores need **≥ 20 items AND disattenuated correlation ≤ ~0.80** to have hope of added value. Augmented subscores (combining subscore with total) more often had value.

**Relevance to MetaJudge:** Family C's 51 items likely meets the item-count threshold, but its low reliability (~0.35) is a red flag. The augmented-subscore approach — shrinking Family C toward a prediction from Families A and B — is the most promising way to retain Family C's unique information (Properties 1, 4, 5).

**Implementability:** ~25 lines of Python for the augmented subscore (multivariate Kelley regression). Requires the 3×3 observed covariance matrix and reliability estimates.

---

### Sinharay (2019) — Added value of subscores and hypothesis testing

**Venue:** *Journal of Educational and Behavioral Statistics*, 44(1), 25–44

**Method:** Provides a **formal significance test** for whether PRMSE_s > PRMSE_x, using Steiger's (1980) method for comparing dependent correlations. Moves the subscore-value question from point estimation to inferential testing.

**Data properties:** Simulation studies plus operational test data from ETS.

**Key finding:** Adds hypothesis-testing rigor to the Haberman framework. With small samples, the test has low power, which is itself informative — if you can't reject "no added value," the conservative choice is to downweight.

**Relevance to MetaJudge:** Provides a defensible statistical test for the Family C inclusion decision (Properties 2, 4). With n = 5 models, the test will almost certainly be underpowered, but the framework structures the decision.

**Implementability:** ~30 lines of Python using `scipy.stats` for correlation comparison.

---

### Brennan (2001) — Generalizability Theory

**Venue:** Springer-Verlag (monograph)

**Method:** G-theory decomposes observed score variance into components due to persons (p), items (i), occasions (o), and their interactions. For composites: **multivariate G-theory** handles weighted combinations of subtests with different designs. Key outputs: generalizability coefficient Eρ² = σ²(universe composite) / σ²(observed composite); **effective weights** (pp. 306–307) describing actual contribution of each component to composite variance; and **D-studies** projecting reliability under different designs (e.g., "what if we ran 5 replicates of Family C?").

**Data properties:** Framework accommodates any crossed or nested design. Illustrative examples: Listening-Writing assessment, 50 examinees, 12 tasks, 3 raters per skill.

**Key finding:** Composite reliability depends on component reliabilities, intercorrelations, variances, and weights. G-theory distinguishes **relative error** (for ranking) from **absolute error** (for threshold decisions). D-studies answer "how many runs would Family C need for adequate reliability?"

**Relevance to MetaJudge:** The natural framework for Family C's test-retest instability (Property 4). The 3-models × 3-runs × 51-items stability data can be decomposed into model variance vs. occasion variance vs. item variance vs. interactions. With only 3 models in the stability study, variance-component estimates will have large standard errors, but the D-study projection ("how many runs are needed?") is directly actionable.

**Implementability:** Multivariate composite formulas: ~30 lines of Python. Full G-study with ANOVA-based variance components: ~50 lines. Software: GENOVA, urGENOVA, mGENOVA (freely available). With n = 5 models, estimates will be imprecise.

---

### Nunnally & Bernstein (1994) — Psychometric Theory (composite reliability)

**Venue:** McGraw-Hill (textbook, 3rd edition)

**Method:** Chapter 7 provides the general formula for composite reliability (originating from Mosier, 1943): **ρ_composite = 1 − [w′Σ_e w] / [w′Σw]** where Σ is the observed covariance matrix, Σ_e is the diagonal error-covariance matrix with entries σ²_j(1 − ρ_j), and w is the weight vector. For unit-weighted composites: **ρ_c = 1 − Σ_j σ²_j(1 − ρ_j) / Σ_j Σ_k σ_jk**.

**Data properties:** General framework; textbook examples use 2–10 subtests with moderate to large examinee samples.

**Key finding:** When components have different reliabilities, the composite is dominated by the component with the largest (reliability × variance) product. Adding an unreliable component can **decrease** composite reliability if it has low correlation with the others and high error variance.

**Relevance to MetaJudge:** Provides the exact formula for computing composite reliability from Family A (α ≈ 0.88), Family B (α ≈ 0.72), and Family C (α ≈ 0.35) reliabilities, their SDs, and intercorrelations (Properties 1, 3, 4). Critical for determining whether including Family C helps or hurts composite reliability.

**Implementability:** ~10 lines of numpy. Build the 3×3 observed covariance matrix and error matrix, apply weights, compute ratio.

---

### Dawes (1979) — The robust beauty of improper linear models in decision making

**Venue:** *American Psychologist*, 34(7), 571–582

**Method:** Reviews evidence comparing "proper" linear models (OLS regression with optimized weights) to "improper" linear models (equal/unit weights, random sign-correct weights). Argues from a bias-variance trade-off perspective that optimal weights have high sampling variability that destroys their theoretical advantage.

**Data properties:** Multiple empirical examples: graduate-school prediction (n = 111, 3 predictors), marital happiness (n = 42, 2 predictors). Generally few predictors (2–5), moderate to small samples.

**Key finding:** Unit weights on standardized predictors often **outperform** regression-optimized weights, especially when the number of predictors is small, sample size is small, and predictors are intercorrelated. In the graduate-school example, the equal-weight composite correlated .48 with the criterion vs. .38 for cross-validated regression.

**Relevance to MetaJudge:** **The single strongest argument against optimizing weights with n = 5.** With 3 sub-metrics and 5 models, any data-derived weights are pure overfitting. Equal weights after z-standardization are not just simpler — they are likely more accurate (Properties 1, 2).

**Implementability:** The implication is trivial: `composite = mean(z_A, z_B, z_C)`.

---

### Einhorn & Hogarth (1975) — Unit weighting schemes for decision making

**Venue:** *Organizational Behavior and Human Performance*, 13(2), 171–192

**Method:** Derives the minimum possible correlation between a unit-weighted composite and an OLS-weighted composite as a function of inter-predictor correlation and number of predictors. Shows algebraically that the two composites are nearly identical under common conditions.

**Data properties:** Analytical results applicable to any number of predictors; most relevant for k ≤ 10.

**Key finding:** With ≤ 5 predictors and moderate intercorrelation, the minimum correlation between unit-weighted and optimally weighted composites typically exceeds **0.95**. Equal weights lose almost nothing relative to optimal weights.

**Relevance to MetaJudge:** With k = 3 MetaJudge families, even under worst-case scenarios, equal and optimal composites will be nearly identical (Property 2). Combined with Dawes (1979), this eliminates the case for differential weighting.

**Implementability:** N/A (theoretical justification, not algorithm).

---

### Davis-Stober (2011) — When fixed weighting schemes outperform OLS

**Venue:** *Psychometrika*, 76(4), 650–669

**Method:** Derives **closed-form conditions** under which fixed weights (including equal weights) have lower mean squared error than OLS, as a function of sample size n, number of predictors p, error variance, and model predictability. Maps the exact regions of parameter space favoring each approach.

**Data properties:** Analytical; applicable to any n and p. Confirmed empirically by Lichtenberg & Şimşek (2017, Proceedings of Machine Learning Research): equal weights outperformed all competing models for training-set sizes below 15.

**Key finding:** With p = 3 predictors and n = 5, OLS dramatically overfits. The region of parameter space favoring fixed weights **grows** as n shrinks and p grows. A follow-up (Davis-Stober et al., 2024, *Perspectives on Psychological Science*) showed that with very small N, empirical effect estimates are "practically indistinguishable from flipping a coin."

**Relevance to MetaJudge:** Definitive formal proof that **equal weights are optimal** at MetaJudge's sample size (Property 2). Any reliability-weighted, discriminability-weighted, or regression-derived weighting scheme will have higher expected error than equal weights.

**Implementability:** Equal weighting is trivially implementable. Davis-Stober's bounds can be computed analytically.

---

## Q3 — Methods for ranking stability and uncertainty quantification

This section casts the widest net, covering weight-uncertainty methods (Dirichlet sampling, OECD sensitivity analysis), score-uncertainty methods (bootstrap rank inference, Mogstad et al. confidence sets), rank-aggregation methods (Kemeny-Young, Borda, Bradley-Terry), multi-criteria decision analysis (TOPSIS), partial-order approaches (Hasse diagrams), and discriminability-based weighting. The most important finding: **Mogstad et al. (2024) provides the definitive frequentist framework for rank confidence sets**, while **Dirichlet weight sampling is the simplest and most interpretable approach to weight-uncertainty analysis**. For n = 5 models, exact enumeration methods (Kemeny-Young, Hasse linear extensions) are computationally trivial and should be preferred over sampling-based approximations.

---

### OECD/JRC (2008) — Handbook on constructing composite indicators

**Venue:** OECD Publishing, Paris. ISBN 978-92-64-04345-9. Authors: Nardo, Saisana, Saltelli, Tarantola (JRC); Hoffmann, Giovannini (OECD).

**Method:** A 10-step framework covering theoretical foundation, data selection, imputation, multivariate analysis, normalization, weighting/aggregation, robustness/sensitivity analysis, decomposition, external validation, and presentation. Step 6 covers 9 weighting methods (equal, PCA/FA, DEA, budget allocation, AHP, conjoint analysis, etc.). Step 7 prescribes Monte Carlo uncertainty analysis varying normalization, weighting, and aggregation choices simultaneously, combined with variance-based sensitivity analysis (Sobol indices) to decompose which methodological choices drive ranking variability.

**Data properties:** Designed for composite indicators with many units (countries) and moderate numbers of sub-indicators (5–50). Explicitly applicable to small numbers of criteria.

**Key finding:** "No weighting method is above criticism." Different weighting and normalization choices can produce different rankings; the Handbook's core prescription is to test sensitivity to all methodological choices simultaneously and report the resulting ranking distributions. Emphasis on transparency: present both composite and sub-indicator profiles.

**Relevance to MetaJudge:** The **gold standard** framework for composite construction. Directly applicable to all 5 properties. The Monte Carlo sensitivity approach subsumes Dirichlet weight sampling as a special case. The Handbook's emphasis on simultaneous variation of normalization, weighting, and aggregation is more thorough than varying weights alone.

**Implementability:** The framework is a design philosophy; individual components (Monte Carlo, Sobol indices) are 20–50 lines each. Full implementation with all variations: moderate effort (~200 lines).

---

### Saisana, Saltelli & Tarantola (2005) — Uncertainty and sensitivity analysis for composite indicators

**Venue:** *Journal of the Royal Statistical Society: Series A*, 168(2), 307–323

**Method:** Monte Carlo uncertainty analysis for composite indicators, randomly varying weights (via budget allocation and AHP), normalization methods, and imputation strategies. Uses variance-based sensitivity analysis (Sobol indices) to decompose ranking variability into contributions from each methodological choice.

**Data properties:** Applied to UN Technology Achievement Index (countries ranked on multiple technology indicators).

**Key finding:** Varying weights and normalization **simultaneously** reveals that normalization choice typically contributes more to ranking uncertainty than weight choice. Provides a template for reporting "uncertainty bands" around composite rankings.

**Relevance to MetaJudge:** Directly addresses Properties 1 and 3 (heterogeneous metrics, overlapping CIs). The simultaneous-variation approach is essential: MetaJudge should vary normalization method (z-score vs. min-max vs. rank), weighting, and whether to include Family C, not just weights.

**Implementability:** Monte Carlo loop: ~30 lines of Python. Sobol indices require a dedicated library (`SALib`) but the first-order approach is ~20 additional lines.

---

### Hall & Miller (2009) — Using the bootstrap to quantify the authority of an empirical ranking

**Venue:** *Annals of Statistics*, 37(6B), 3929–3959

**Method:** Bootstrap resampling to construct prediction intervals for rank positions. Demonstrates that the standard n-out-of-n bootstrap can produce **inconsistency** for ranks when population values are close. Proposes **m-out-of-n bootstrap** (m ≈ 0.355n suggested empirically) and independent-component bootstrap as alternatives.

**Data properties:** Designed for moderate to large p (number of items ranked) and any n (sample size). Specifically addresses cases where population values are close ("near-ties").

**Key finding:** When θ values are tied or near-tied, the rank distribution is discrete and degenerate — standard bootstrap prediction intervals become very wide and may be inconsistent. The m-out-of-n bootstrap provides valid coverage. Importantly, bootstrap correctly identifies the **support** of the asymptotic rank distribution even when point estimates are inconsistent.

**Relevance to MetaJudge:** **Highly relevant.** With 5 models and overlapping CIs, this is precisely the near-tied regime where Hall & Miller warn the standard bootstrap fails (Properties 2, 3). The m-out-of-n variant should be used instead of the naive bootstrap.

**Implementability:** Standard bootstrap: ~15 lines. m-out-of-n bootstrap: ~20 lines. Total < 30 lines of Python with numpy.

---

### Mogstad, Romano, Shaikh & Wilhelm (2024) — Inference for ranks

**Venue:** *The Review of Economic Studies*, 91(1), 476–518

**Method:** Constructs **frequentist confidence sets for ranks** — both marginal (CI for rank of one population) and simultaneous (CIs for all ranks jointly). Uses a stepwise multiple-testing procedure to control familywise error rate. For each model, reports the set of ranks consistent with the data at a given confidence level.

**Data properties:** Designed for any number of populations p ≥ 2, with potentially large within-population sample sizes. Applied to PISA data (country rankings) and intergenerational mobility (thousands of neighborhoods).

**Key finding:** Rankings of top and bottom performers are often robust to uncertainty, but **middle rankings are much less informative** once uncertainty is accounted for. With few populations and close values, confidence sets can span nearly {1, …, p}. For 5 models with overlapping CIs, expect confidence sets covering 2–4 rank positions.

**Relevance to MetaJudge:** **The definitive frequentist framework** for rank inference (Properties 2, 3). Provides exactly the output MetaJudge needs: "Model X has rank r ∈ {2, 3, 4} at 95% confidence." The `csranks` R package (Wilhelm & Morgen, 2024) implements all methods. Works with any p ≥ 2.

**Implementability:** R package `csranks` (CRAN, v1.2.3). Python adaptation of the step-down procedure: ~50 lines. Requires bootstrap or normal approximation for the joint distribution of score estimates.

---

### Dirichlet weight sampling — composite framework (Becker / COINr)

**Venue:** COINr R package (CRAN); European Commission Joint Research Centre documentation

**Method:** Sample N weight vectors from a Dirichlet(α, α, α) distribution over the 3-simplex. For each weight vector, compute the weighted composite score and rank the models. Report: (a) the fraction of samples preserving each pairwise ordering P(A > B); (b) the distribution of rank positions for each model; (c) Kendall's W across sampled rankings as a concordance measure. The concentration parameter α controls the prior: **α = 1** (uniform over simplex, maximum ignorance); α > 1 (concentrates near equal weights); α < 1 (concentrates at vertices, one metric dominates).

**Data properties:** No minimum sample size. Works with any number of criteria and alternatives.

**Key finding:** Sensitivity analysis via weight perturbation often reveals that normalization-method choice contributes more to ranking uncertainty than weight choice (Saisana et al., 2005). With 5 models and 3 criteria, even small weight changes can swap adjacent rankings if score gaps are small.

**Relevance to MetaJudge:** **The simplest and most interpretable approach to weight uncertainty** (Properties 1, 2, 3, 5). The pairwise-stability matrix P(A > B) directly quantifies which rankings are robust. Recommended baseline: α = 1, then sensitivity-test with α ∈ {0.5, 1, 2, 5}.

**Implementability:** < 15 lines of Python. Core loop: `weights = np.random.dirichlet([alpha]*3, size=10000)` → weighted sum → rank → count.

---

### Kemeny (1959) / Young & Levenglick (1978) — Optimal rank aggregation

**Venue:** *Daedalus*, 88(4), 577–591 (Kemeny); *Journal of Economic Theory*, 1978 (Young & Levenglick)

**Method:** Finds the ranking that minimizes the total Kendall-tau distance (number of pairwise disagreements) to all input rankings. Equivalent to the **maximum-likelihood estimator** of the true ranking under the Mallows model (Young's theorem). Satisfies Condorcet consistency, neutrality, anonymity, and consistency axioms.

**Data properties:** NP-hard in general, but **trivially solvable for n = 5** by brute force: enumerate all 5! = 120 permutations, compute Kendall-tau distance to each of 3 input rankings (3,600 total comparisons). Instant computation.

**Key finding:** Kemeny-Young has the strongest axiomatic foundation among rank-aggregation methods. It finds the consensus ranking that best explains the observed family rankings. Extensions by Akbari & Escobedo (2023, *Omega*) handle ties via generalized Kendall-tau distance.

**Relevance to MetaJudge:** Distribution-free, immune to scale differences (Property 1), trivial for n = 5 (Property 2), naturally handles divergent orderings (Property 5). Does not directly quantify uncertainty (Properties 3, 4), but combining with Dirichlet sampling produces Kemeny rankings for each weight vector, yielding a distribution.

**Implementability:** ~15 lines of Python with `itertools.permutations`. No specialized software needed.

---

### Brüggemann et al. (1995–2008) — Hasse diagram technique and partial orders

**Venue:** Multiple publications in *J. Chem. Inf. Comput. Sci.*, *Chemosphere*, and other environmental-science journals

**Method:** Constructs a partial order from multi-indicator data: Object A > Object B iff A ≥ B on **all** indicators (Pareto dominance). Visualizes incomparabilities via Hasse diagram. Derives **ranking probabilities** by counting linear extensions — the fraction of all total orderings consistent with the partial order that place each object at each rank. The averaged rank across all linear extensions gives a principled composite rank.

**Data properties:** Works best with 5–30 objects and 2–10 indicators. For n = 5 objects, exact computation of all linear extensions is trivial (at most 5! = 120 permutations to check).

**Key finding:** No weighting required — the partial order is determined purely by dominance. Ranking probabilities give a principled way to report uncertainty without choosing weights. Objects that are incomparable (neither dominates the other) receive overlapping rank-probability distributions.

**Relevance to MetaJudge:** **Highly relevant for Properties 1, 2, and 5.** With 5 models and 3 metrics, the Hasse diagram is small and interpretable. Ranking probabilities from linear-extension counting are a weight-free alternative to Dirichlet sampling. Models with divergent family profiles (Pro, DeepSeek) will be incomparable in the partial order, explicitly preserving the dissociation.

**Implementability:** ~30 lines of Python using `itertools.permutations` with dominance filtering. No specialized software needed.

---

### Rioux, Nitsure, Rigotti, Greenewald & Mroueh (2024) — Multivariate stochastic dominance for model benchmarking

**Venue:** NeurIPS 2024 (poster)

**Method:** Extends first-order stochastic dominance to the multivariate case using **optimal transport with entropic regularization**. Defines "multivariate violation ratios" measuring how much one model fails to dominate another across all metrics simultaneously. Provides hypothesis-testing framework with CLT and bootstrap consistency.

**Data properties:** Requires **per-instance** evaluation data (not just aggregate scores). Designed for comparing LLMs evaluated on multiple metrics with moderate to large item counts.

**Key finding:** Standard aggregation ignores dependencies between metrics. Multivariate stochastic dominance captures cross-metric dependencies and identifies models that dominate others across all metrics vs. those that are genuinely incomparable. Applied to LLM benchmarking.

**Relevance to MetaJudge:** The only method designed explicitly for LLM multi-metric comparison with formal statistical testing (Properties 1, 3, 5). Requires per-instance scores, which MetaJudge has. The 51-item Family C may have limited power for the within-family stochastic-dominance test.

**Implementability:** Requires optimal-transport libraries (POT in Python). Core Sinkhorn computation: > 50 lines. Not trivial from scratch, but `ot.sinkhorn` provides the heavy lifting.

---

### Hwang & Yoon (1981) — TOPSIS

**Venue:** Springer-Verlag, Lecture Notes in Economics and Mathematical Systems vol. 186

**Method:** Technique for Order Preference by Similarity to Ideal Solution. Normalizes a decision matrix (alternatives × criteria), constructs weighted normalized matrix, identifies positive-ideal and negative-ideal solutions, then ranks alternatives by the ratio of distance-from-negative-ideal to (distance-from-positive-ideal + distance-from-negative-ideal). Extensions: entropy-weight TOPSIS determines weights from data dispersion; fuzzy TOPSIS handles interval-valued scores.

**Data properties:** Works with any number of alternatives and criteria. Particularly well-suited for 3–10 alternatives with 2–15 criteria. No distributional assumptions.

**Key finding:** TOPSIS handles heterogeneous criteria naturally via normalization. The entropy-weighting variant objectively determines criterion weights from data dispersion — criteria with more variation across alternatives get more weight. Zanakis et al. found that for small numbers of alternatives (5–9), TOPSIS produces rankings very similar to simpler methods like SAW (simple additive weighting).

**Relevance to MetaJudge:** Addresses Properties 1 (heterogeneous metrics via normalization), 2 (works well with 5 alternatives), and 5 (handles conflicting criteria). The entropy-weighting variant provides data-driven weights without overfitting (unlike regression). Fuzzy extensions handle interval-valued scores (Property 3).

**Implementability:** Standard TOPSIS: ~25 lines of Python with numpy. Entropy weighting: ~10 additional lines.

---

### Demšar (2006) — Statistical comparisons of classifiers over multiple data sets

**Venue:** *Journal of Machine Learning Research*, 7, 1–30

**Method:** Recommends the **Friedman test** (non-parametric repeated-measures ANOVA) as an omnibus test for comparing k > 2 classifiers across N datasets, followed by **Nemenyi post-hoc test** for all-pairwise comparisons. Introduces **Critical Difference (CD) diagrams** for visualizing which classifiers are statistically indistinguishable.

**Data properties:** Explicitly designed for **small sample sizes**: "The sample size can therefore be as small as five and is usually well below 30." Running examples: 14 datasets, 4 classifiers.

**Key finding:** Parametric tests (paired t-test, ANOVA) are inappropriate for small-sample classifier comparisons. The Friedman + Nemenyi approach controls Type I error while identifying which pairwise differences are significant. CD diagrams show groups of classifiers connected by a bar (= statistically indistinguishable).

**Relevance to MetaJudge:** **Directly applicable** to Properties 2 and 3. Treats the 3 family rankings as 3 "datasets" and 5 models as 5 "classifiers." The Nemenyi CD diagram would show which model pairs are statistically separable across families. With only N = 3 "datasets," power will be very low — but this honestly reflects the evidence. For Bonferroni-Dunn (comparing against a control) or Holm step-down, power is slightly higher.

**Implementability:** Friedman test: `scipy.stats.friedmanchisquare`. Nemenyi: ~20 lines or use `scikit-posthocs`. CD diagram: `Orange` library or ~40 lines of matplotlib.

---

### Bradley & Terry (1952) / Plackett-Luce — Latent-strength estimation from rankings

**Venue:** *Biometrika*, 39(3/4), 324–345 (Bradley-Terry); Plackett (1975), Luce (1959)

**Method:** Assigns latent "strength" parameters β_i to each item such that P(i beats j) = exp(β_i) / (exp(β_i) + exp(β_j)). Rankings are decomposed into C(n,2) implied pairwise comparisons. MLE or Bayesian estimation produces interval-scale scores from ordinal rankings, with uncertainty quantification via posterior distributions or profile likelihood CIs.

**Data properties:** From 3 complete rankings of 5 models: 30 implied pairwise comparisons, 5 parameters to estimate (one fixed for identifiability). Frequentist MLE is feasible but may be unstable; Bayesian BT with weakly informative priors is recommended for small samples.

**Key finding:** BT converts ordinal rankings to interval-scale scores, recovering magnitude information that pure rank-aggregation methods discard. Calvo et al. (2022, *IEEE Trans. Evolutionary Computation*) showed that Bayesian Plackett-Luce produces well-calibrated posterior rank probabilities even with few permutations.

**Relevance to MetaJudge:** Addresses Properties 1 (heterogeneous metrics become pairwise comparisons), 2 (Bayesian version works with small n), and 5 (different orderings are naturally handled as disagreeing "judges"). The posterior P(model i is rank k) provides uncertainty quantification (Property 3).

**Implementability:** MLE: ~30 lines with `scipy.optimize`. Bayesian: ~50 lines with PyMC. The `choix` Python library provides Plackett-Luce out of the box.

---

### Qian et al. (2025) — Benchmark²: discriminability-based weighting

**Venue:** arXiv 2601.03986

**Method:** Proposes a **Discriminability Score (DS)** for meta-evaluating benchmarks — quantifying a benchmark's ability to differentiate between models by measuring performance-gap magnitudes. Higher DS means larger, more consistent gaps between models. Related concept: weight sub-metrics by their average pairwise Cohen's d or Fisher Discriminant Ratio (between-model variance / within-model variance).

**Data properties:** Applied to multiple LLM benchmarks with 10–100+ models.

**Key finding:** Benchmarks vary enormously in discriminability. Sub-metrics that produce near-identical scores for all models (low DS) contribute noise, not signal, to a composite. Weighting by discriminability is analogous to reliability weighting but uses between-model separation rather than test-retest stability.

**Relevance to MetaJudge:** Provides a principled alternative to equal weighting that doesn't require optimizing against a criterion (avoiding Dawes's objection). Family A (8/10 pairwise gaps > 0.02) likely has higher DS than Family C (wide CIs, narrow model spread). Addresses Properties 1, 3, and 5.

**Implementability:** Cohen's d per pair: 3 lines. Average d per family as weight: ~10 lines. Fisher ratio (between/within variance): ~15 lines.

---

### Kolde, Laur, Adler & Vilo (2012) — Robust Rank Aggregation

**Venue:** *Bioinformatics*, 28(4), 573–580

**Method:** Detects items ranked consistently better than expected under a null hypothesis of uncorrelated inputs. Normalizes ranks to [0,1], applies a beta-distribution model, assigns p-values (ρ scores) based on order statistics of normalized ranks.

**Data properties:** Designed for large N (thousands of genes) with partial, noisy ranking lists. The null model assumes uniform rank distribution.

**Key finding:** With many items, RRA identifies "signal" items ranked consistently well across lists. However, mean aggregation "will outperform or at least match RRA in classification performance while being significantly simpler."

**Relevance to MetaJudge:** **Limited applicability.** Designed for large-N settings with partial/noisy lists, not full rankings of 5 items. With N = 5 and 3 complete rankings, the statistical test has negligible power. Included for completeness as a commonly cited rank-aggregation method that should **not** be used here.

**Implementability:** R package `RobustRankAggreg`. Python reimplementation: ~30 lines. But not recommended for this problem.

---

### Kendall's W / Friedman test — concordance across weight vectors

**Venue:** Kendall & Gibbons (1990), *Rank Correlation Methods*, 5th ed., Oxford University Press

**Method:** Non-parametric measure of agreement among m raters ranking n objects. W = 12S / (m²(n³ − n)), where S = sum of squared deviations of rank sums from their mean. Ranges from 0 (no agreement) to 1 (perfect). Equivalent to the Friedman test statistic and to the average pairwise Spearman correlation: W = (1 + r̄(m−1)) / m.

**Data properties:** Works with any m (raters/weight-vectors) and n (objects/models). With n = 5, the chi-squared approximation may be poor — exact permutation testing is recommended (Legendre, 2005).

**Key finding:** Kendall's W provides a single summary statistic for ranking stability across weight perturbations. With n = 5 objects, even moderate disagreement produces low W values, and the statistic has **coarse resolution** — it doesn't identify which pairwise comparisons are stable vs. unstable.

**Relevance to MetaJudge:** Useful as a **supplementary summary statistic** alongside the Dirichlet pairwise-stability matrix (Properties 2, 5). Treating Dirichlet-sampled weight vectors as "raters," W summarizes overall concordance in one number. Low power with n = 5 limits utility as a standalone measure.

**Implementability:** ~10 lines of Python. `scipy.stats.friedmanchisquare` gives the test; W = χ² / (m(n−1)).

---

## Methods shortlist for computational evaluation

The following table presents 8 candidate methods spanning score-based composites, rank-based aggregation, and uncertainty-quantification approaches. Each should be implemented and tested against MetaJudge's actual data in Step 2. Methods are ordered from simplest to most complex.

| Method | What it does | What it assumes | Properties addressed | Complexity |
|---|---|---|---|---|
| **Equal-weight z-score average** | z-standardize each family score, average | Families contribute equally; z-scores meaningful with n=5 | 1 (heterogeneity), 2 (small n) | Trivial |
| **Dirichlet weight sampling + pairwise stability** | Sample 10,000 weight vectors from Dirichlet(1,1,1), report P(A>B) for all 10 pairs | Uniform prior over weight simplex; standardized scores are commensurable | 1, 2, 3, 5 | Trivial |
| **Kemeny-Young consensus ranking** | Find ranking minimizing total Kendall-tau distance to 3 family rankings | Only ordinal information matters; families are equally credible "judges" | 1, 2, 5 | Trivial |
| **Hasse partial order + linear-extension ranking probabilities** | Construct partial order from Pareto dominance; enumerate all consistent total orders; report rank-probability matrix | Dominance on all 3 metrics required for ordering; no metric trade-offs allowed | 1, 2, 3, 5 | Moderate |
| **Mogstad et al. confidence sets for ranks** | Construct simultaneous 95% confidence sets for each model's rank position via stepdown testing | Large within-family item counts for normal approximation; independence of score estimates | 2, 3 | Moderate |
| **TOPSIS with entropy weights** | Normalize decision matrix, compute entropy-based criterion weights, rank by relative closeness to ideal solution | Euclidean distance is meaningful in normalized space; entropy reflects information content | 1, 2, 5 | Moderate |
| **Bayesian Bradley-Terry from family rankings** | Treat 3 family rankings as implicit pairwise comparisons; estimate latent strength via Bayesian BT; report posterior rank probabilities | Rankings are conditionally independent given latent strengths; Plackett-Luce model holds | 1, 2, 3, 5 | Moderate |
| **Composite reliability analysis (Nunnally/Haberman)** | Compute composite reliability under different weight vectors; apply PRMSE criterion to Family C inclusion decision | Classical test theory assumptions; reliability estimates are accurate; linear model | 1, 3, 4 | Moderate |

Three operational notes for Step 2. First, the **Dawes/Einhorn/Davis-Stober consensus** is that equal weights will outperform any optimized weights at n = 5 — the question is not "what weights?" but "which families to include and how to report uncertainty." Second, methods addressing **different facets** of the problem should be **combined, not chosen among**: use Nunnally/Haberman to decide Family C's inclusion, equal-weight z-scores or Kemeny-Young to produce the point ranking, and Dirichlet sampling or Mogstad confidence sets to quantify uncertainty around it. Third, **multi-run averaging of Family C should precede all composite construction** — the order of operations (average runs → standardize → composite) is not interchangeable with (composite → average), and the OECD Handbook is explicit that uncertainty-propagation requires getting the sequence right.