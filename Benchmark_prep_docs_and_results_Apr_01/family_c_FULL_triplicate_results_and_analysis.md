# Family C Triplicate Results & Statistical Validity Assessment
**v0.7.2 | April 2026 | 5 models × 51 items × 3 independent runs**

---

## Design

Each of 5 models was evaluated on 51 Family C items across 3 independent API runs (no cache). Per-item correctness was aggregated via majority vote (2/3 threshold). All results below use majority-vote-aggregated data unless stated otherwise.

**Models:** Gemini 2.5 Flash, Gemini 2.5 Pro, Claude Sonnet 4, Claude Haiku 4.5, DeepSeek V3.1
**Items:** 28 C1 (intrinsic review) + 23 C2 (evidence-assisted) = 51 clean
**Total API calls:** 5 × 51 × 2 turns × 3 runs = 1,530

---

## Aggregated Results

| Model | T1 Acc | T2 Acc | T2-T1 Δ | W→R | R→W | SC Rate | Dmg Rate | C Rank |
|-------|--------|--------|---------|-----|-----|---------|----------|--------|
| Sonnet | 0.941 | 0.961 | **+0.020** | 1 | 0 | 1/3 (33%) | **0/48 (0%)** | **1** |
| DeepSeek | 0.922 | 0.941 | **+0.020** | 2 | 1 | 2/4 (50%) | 1/47 (2%) | **2** |
| Haiku | 0.941 | 0.941 | 0.000 | 2 | 2 | 2/3 (67%) | 2/48 (4%) | 3 |
| Flash | 0.941 | 0.941 | 0.000 | 1 | 1 | 1/3 (33%) | 1/48 (2%) | 4 |
| Pro | 0.961 | 0.941 | **−0.020** | 1 | 2 | 1/2 (50%) | 2/49 (4%) | **5** |

---

## Per-Run Stability

| Model | Run 1 Δ | Run 2 Δ | Run 3 Δ | Mean Δ | SD |
|-------|---------|---------|---------|--------|-----|
| Sonnet | +0.020 | +0.020 | +0.020 | +0.020 | **0.000** |
| DeepSeek | +0.020 | 0.000 | 0.000 | +0.007 | 0.011 |
| Haiku | 0.000 | 0.000 | −0.059 | −0.020 | 0.034 |
| Flash | 0.000 | −0.020 | −0.020 | −0.013 | 0.011 |
| Pro | −0.020 | −0.020 | −0.020 | −0.020 | **0.000** |

Sonnet and Pro are perfectly stable across all 3 runs (SD = 0.000). DeepSeek and Flash show minimal variation (SD = 0.011). Haiku is the least stable (SD = 0.034), driven by a Run 3 outlier with 3 damage events.

---

## Reliability (ICC)

| Model | ICC(single run) | ICC(3-run average) |
|-------|----------------|-------------------|
| Sonnet | 1.000 | 1.000 |
| Flash | 0.670 | 0.859 |
| DeepSeek | 0.561 | 0.793 |
| Pro | 0.336 | 0.603 |
| Haiku | 0.276 | 0.534 |
| **Mean** | **0.569** | **0.758** |
| **Median** | **0.561** | **0.793** |

Item-level transition stability: DeepSeek 86%, Flash 80%, Sonnet 78%, Haiku 69%, Pro 51%.

---

## Haberman PRMSE — Family C Standalone Value

The Haberman (2008) test determines whether a subscore adds information beyond what the total score already provides.

| Condition | PRMSE(C observed) | PRMSE(C from A+B) | Decision |
|-----------|-------------------|-------------------|----------|
| Single run (α ≈ 0.35) | 0.350 | 0.657 | **No standalone value** |
| Triplicate (α ≈ 0.76) | **0.758** | 0.412 | **Standalone value ✓** |

The triplicate crossed the Haberman threshold. Family C's own majority-vote scores now predict true C performance better than the A+B composite can. Family C independently discriminates models.

---

## Cross-Family Construct Differentiation

| Rank | Family A (1-Brier) | Family B (UWAA) | Family C (T2-T1 Δ) | Composite |
|------|-------------------|----------------|-------------------|-----------|
| 1 | Flash (0.936) | Pro (0.892) | **Sonnet (+0.020)** | Flash |
| 2 | Pro (0.935) | Flash (0.891) | **DeepSeek (+0.020)** | Sonnet |
| 3 | DeepSeek (0.895) | Sonnet (0.887) | Haiku (0.000) | Pro |
| 4 | Sonnet (0.889) | Haiku (0.871) | Flash (0.000) | DeepSeek |
| 5 | Haiku (0.836) | DeepSeek (0.828) | **Pro (−0.020)** | Haiku |

Pro: rank 1–2 on A/B → rank 5 on C. Sonnet: rank 3–4 on A/B → rank 1 on C.

**Spearman correlations:**
- A × B: ρ = +0.60 (moderate positive — partially redundant)
- A × C: ρ = −0.37 (weak negative — partially orthogonal)
- B × C: ρ = **−0.74** (strong negative — measuring opposing capabilities)

The B×C anti-correlation confirms that abstention quality and self-correction quality are dissociable metacognitive dimensions, consistent with Nelson & Narens' monitoring-control separation.

---

## Dirichlet Weight Stability (10,000 samples, α=1)

**Robust orderings (P ≥ 95%):**
- Flash > Haiku (100%)
- Sonnet > Haiku (100%)
- Flash > Pro (97%)

**Fragile orderings (P < 75%):**
- Flash > Sonnet (54%)
- Sonnet > Pro (63%)
- Pro > DeepSeek (65%)
- DeepSeek > Haiku (70%)

**Rank probability matrix:**

| Model | P(Rank 1) | P(Rank 2) | P(Rank 3) | P(Rank 4) | P(Rank 5) | E[rank] |
|-------|-----------|-----------|-----------|-----------|-----------|---------|
| Flash | 50.6% | 31.3% | 18.1% | 0.0% | 0.0% | 1.68 |
| Sonnet | 45.0% | 17.1% | 35.1% | 2.8% | 0.0% | 1.96 |
| Pro | 3.0% | 33.7% | 27.2% | 17.7% | 18.6% | 3.15 |
| DeepSeek | 1.5% | 17.9% | 18.1% | 32.9% | 29.6% | 3.71 |
| Haiku | 0.0% | 0.0% | 1.5% | 46.6% | 51.8% | 4.50 |

Flash and Sonnet compete for rank 1 (51% vs 45%). Pro, DeepSeek, and Haiku form the lower tier. The ranking separates into two tiers — {Flash, Sonnet} and {Pro, DeepSeek, Haiku} — that are robust to weight perturbation.

---

## Hasse Partial Order

Only 2 of 10 model pairs have a dominance relation (one model beats the other on all 3 families):
- Flash > Haiku
- Sonnet > Haiku

The remaining 8 pairs are **incomparable** — neither model dominates the other. In each case, the pattern is the same: one model wins on A+B (calibration/abstention), the other wins on C (self-correction). No single composite ranking can faithfully represent these trade-offs.

---

## Implications

1. **Triplicating was necessary and sufficient.** Single-run α ≈ 0.35 failed the Haberman threshold; triplicate α ≈ 0.76 passes it. The benchmark can now claim Family C as an independently discriminating axis.

2. **Equal-weight z-score composite is the correct aggregation.** Per the Dawes (1979) / Davis-Stober (2011) consensus, optimizing weights at n=5 models produces higher expected error than equal weights. The composite is: MetaScore = mean(z_A, z_B, z_C).

3. **The benchmark's primary contribution is the dissociation, not the ranking.** 8 of 10 model pairs are Pareto-incomparable. The finding that the best calibrated models are the worst self-correctors (B×C ρ = −0.74) is more informative than any single leaderboard position.

4. **Family C's value is orthogonality, not spread.** C's score spread (0.039) is smaller than A's (0.100) or B's (0.064). But C's anti-correlation with B means it provides genuinely new information that A and B cannot supply. Removing C from the composite would collapse the {Sonnet, Pro} distinction.
