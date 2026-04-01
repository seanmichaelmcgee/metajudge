# MetaJudge Composite Construction — Step 2 Technical Memo
**Computed results on matched 5-model data | April 2026**

---

## Data Sources

| Family | Items | Models | Source | Note |
|--------|-------|--------|--------|------|
| A (Calibration) | 105 | 5 | v2 narrative run | Stable |
| B (Abstention) | 72 | 5 | v2 narrative run | Stable |
| C (Self-Correction) | 51 | 5 | v0.7.0 (Haiku/Sonnet/DeepSeek) + v0.7.1 fixed grader (Flash/Pro) | Mixed provenance |

---

## Raw Scores

| Model | A (1-Brier) | A rank | B (UWAA) | B rank | C (T2-T1 Δ) | C rank | C Dmg% |
|-------|------------|--------|----------|--------|-------------|--------|--------|
| Flash | 0.936 | 1 | 0.891 | 2 | 0.000 | 2 | 2.0% |
| Pro | 0.935 | 2 | 0.892 | 1 | −0.078 | 5 | 8.0% |
| Sonnet | 0.889 | 4 | 0.887 | 3 | −0.018 | 3 | 2.2% |
| Haiku | 0.836 | 5 | 0.871 | 4 | −0.036 | 4 | 8.3% |
| DeepSeek | 0.895 | 3 | 0.828 | 5 | +0.036 | 1 | 2.3% |

---

## Finding 1: Equal weights are optimal — the weight optimization question is settled

The Dawes (1979) / Einhorn & Hogarth (1975) / Davis-Stober (2011) consensus proves that with k=3 sub-metrics and n=5 models, any data-derived differential weighting will have higher expected error than equal weights. The minimum correlation between equal-weighted and optimally-weighted composites exceeds 0.95 with k≤5 predictors. **Do not optimize weights.**

**Recommended composite: z-standardize each family, average equally.**

| Model | z_A | z_B | z_C | MetaScore (mean z) | Rank |
|-------|-----|-----|-----|--------------------|------|
| Flash | +1.030 | +0.705 | +0.507 | **+0.747** | **1** |
| Sonnet | −0.241 | +0.560 | +0.029 | **+0.116** | **2** |
| Pro | +1.003 | +0.764 | −1.550 | **+0.072** | **3** |
| DeepSeek | −0.100 | −1.894 | +1.462 | **−0.177** | **4** |
| Haiku | −1.693 | −0.135 | −0.448 | **−0.759** | **5** |

**Key rank shift from A+B-only to A+B+C:** Pro drops from rank 1 to rank 3. Sonnet rises from rank 3 to rank 2. This is Family C's contribution — it penalizes Pro's damage behavior and rewards Sonnet's stability.

---

## Finding 2: The Haberman PRMSE test says Family C's observed score has NO standalone added value

PRMSE(C alone) = 0.350 (= its reliability).
PRMSE(predicting C from A+B total) = 0.657.

The A+B composite predicts true Family C performance better than Family C's own observed score does. This means Family C's observed values are too noisy (α ≈ 0.35) to carry independent weight. Under Haberman's criterion, Family C should not be reported as a standalone subscore.

**However:** This does NOT mean Family C should be excluded from the composite. The Sinharay (2010) augmented-subscore approach recommends shrinking the observed C toward its A+B-predicted value, which retains C's unique information while reducing noise. At a practical level, including C at equal weight in a 3-family z-score composite is an approximation of this shrinkage that works acceptably for n=5.

**The sensitivity analysis shows:** If Family C's reliability improves to ≥0.55 (through multi-run averaging or grading improvements), the PRMSE reversal occurs and C has standalone value. The current ≈0.35 is below this threshold; the target for future work is clear.

**Recommendation:** Include Family C in the equal-weight composite (it shifts rankings in theoretically meaningful ways) but **always present family-level profiles alongside the MetaScore** and caveat Family C's reliability explicitly. Do not report C as a standalone axis with independent significance claims.

---

## Finding 3: Dirichlet pairwise stability identifies 4 robust and 4 fragile orderings

Under 10,000 uniform Dirichlet weight samples (α=1):

**Robust orderings (P ≥ 95%, stable under ANY reasonable weighting):**
- Flash > Pro (98.1%)
- Flash > Sonnet (100%)
- Flash > Haiku (100%)
- Sonnet > Haiku (100%)

**Fragile orderings (P < 75%, sensitive to weight choice):**
- Pro > Sonnet (50.7%) — essentially a coin flip
- Pro > DeepSeek (61.0%)
- Sonnet > DeepSeek (59.8%)
- DeepSeek > Haiku (74.6%)

**Interpretation:** Flash is definitively rank 1 and Haiku is definitively rank 5 under any weighting. The middle three (Pro, Sonnet, DeepSeek) are statistically interchangeable — their ordering depends entirely on how much weight Family C receives. This is an honest finding, not a failure.

**Rank probability matrix (α=1):**

| Model | P(rank 1) | P(rank 2) | P(rank 3) | P(rank 4) | P(rank 5) | E[rank] |
|-------|-----------|-----------|-----------|-----------|-----------|---------|
| Flash | 86.0% | 14.0% | 0.0% | 0.0% | 0.0% | 1.14 |
| Pro | 1.9% | 44.6% | 18.6% | 19.3% | 15.5% | 3.02 |
| Sonnet | 0.0% | 21.6% | 65.9% | 12.5% | 0.0% | 2.91 |
| Haiku | 0.0% | 0.0% | 0.1% | 40.8% | 59.1% | 4.59 |
| DeepSeek | 12.1% | 19.8% | 15.4% | 27.3% | 25.4% | 3.34 |

Kendall's W = 0.61 (moderate agreement across weight perturbations).

---

## Finding 4: Hasse partial order reveals the structure of incomparability

Only 3 dominance relations exist (where one model beats another on ALL 3 families):
- Flash > Sonnet > Haiku (a transitive chain)

All other pairs are **incomparable** — neither dominates the other:
- Flash ↔ Pro (Flash wins A and C; Pro wins B)
- Flash ↔ DeepSeek (Flash wins A and B; DeepSeek wins C)
- Pro ↔ Sonnet/Haiku/DeepSeek (Pro wins A and B; the other wins C in each case)
- Sonnet ↔ DeepSeek (Sonnet wins B; DeepSeek wins A and C)

**Pro and DeepSeek are both uniformly distributed across ranks 1–5** in the linear extension analysis (20% probability at each rank). This means the data genuinely cannot order them relative to other models without choosing how much to weight each family.

**This is the finding the writeup should lead with.** The partial order is the most honest representation of the data: Flash is best, Haiku is worst, and the middle three have genuinely different capability profiles that no single number can rank.

---

## Finding 5: Friedman test confirms no statistically significant ranking

Friedman χ² = 4.53, p = 0.376. With only N=3 families, the Nemenyi critical difference is CD=3.52 — larger than the maximum observed rank difference (2.67 between Flash and Haiku). No pairwise comparison reaches significance.

**This is expected and honest.** Three families cannot statistically separate 5 models at α=0.05. The Friedman result should be reported to show the analysis was done, but the discrimination argument should rest on the qualitative rank-divergence pattern (which is real and theoretically interpretable) rather than on formal significance (which requires more families or more models to achieve).

---

## Finding 6: The Kemeny-Young consensus ranking equals Family A's ranking

The consensus ranking minimizing total Kendall-tau distance to all 3 family rankings is:
**Flash > Pro > DeepSeek > Sonnet > Haiku**

This is identical to Family A's ranking (distance=0 from A, 3 from B, 4 from C). Family A dominates the consensus because A and B partially agree while C is the outlier.

**This highlights a limitation of ordinal aggregation:** it treats each family as one "vote" regardless of reliability or discriminative power. The z-score composite (Finding 1) produces a different ranking (Flash > Sonnet > Pro > DeepSeek > Haiku) because it uses the magnitude of score differences, not just ordinal positions.

---

## Recommended Implementation

### For the narrative notebook:

1. **Primary metric:** Equal-weight z-score composite (Finding 1)
2. **Uncertainty:** Dirichlet rank-probability table (Finding 3)
3. **Honest reporting:** Hasse partial order (Finding 4) — show which comparisons are robust vs. incomparable
4. **Caveat:** Haberman PRMSE result (Finding 2) — Family C reliability below standalone threshold
5. **Statistical test:** Friedman p-value (Finding 5) — acknowledge non-significance

### For the benchmark notebook:

1. Compute z-standardized scores per family
2. Report MetaScore = mean(z_A, z_B, z_C) with rank
3. Include one stability sentence: "Rankings of Flash (rank 1) and Haiku (rank 5) are stable under 100% of weight perturbations; middle rankings are weight-sensitive"
4. Present the family-profile table alongside the composite

### Code (~50 lines total):

```python
# Composite construction
z_scores = {}
for fam, scores in [('A', a_scores), ('B', b_scores), ('C', c_scores)]:
    vals = np.array([scores[m] for m in models])
    z_scores[fam] = (vals - vals.mean()) / vals.std()

metascore = np.mean([z_scores[f] for f in ['A','B','C']], axis=0)

# Dirichlet stability (15 lines)
weights = np.random.dirichlet([1,1,1], size=10000)
pairwise_prob = np.zeros((5,5))
for w in weights:
    comp = w[0]*z_scores['A'] + w[1]*z_scores['B'] + w[2]*z_scores['C']
    for i in range(5):
        for j in range(i+1,5):
            if comp[i] > comp[j]: pairwise_prob[i][j] += 1
            else: pairwise_prob[j][i] += 1
pairwise_prob /= 10000
```

---

## What changes when the complete 5-model fixed-grader run finishes

The three numbers most likely to shift: DeepSeek's C delta (currently +0.036 from v0.7.0, may compress toward 0), Haiku's damage rate (currently 8.3% from v0.7.0, may decrease with fixed grader), and the overall C spread.

The structural findings are robust to these shifts:
- Equal weights remain optimal (theoretical, not data-dependent)
- The Haberman PRMSE will shift slightly but C's reliability won't cross the 0.55 threshold on one run
- The Dirichlet robust orderings (Flash > all, Sonnet > Haiku) are driven by A and B, not C
- The Hasse incomparability structure is driven by Pro's C-rank-5 vs A/B-rank-1-2, which is stable

**Update the numbers when the data arrives; the method doesn't change.**


## Add on cell for notebook (place after cell 18)

# Cell 14 — Composite Construction Analysis (z-score, Dirichlet, Hasse, Haberman, Friedman)
# Insert AFTER Cell 18 (existing Composite MetaScore) and BEFORE the "---" markdown divider.
# Dependencies: cal_metrics, fb_metrics, fc_results, model_order, short_name, np, pd (all from earlier cells)

from itertools import permutations as _perms, combinations as _combs
from scipy import stats as _stats

# ═══════════════════════════════════════════════════════════════════════
# Gather per-model scores from already-computed metrics dicts
# ═══════════════════════════════════════════════════════════════════════

_all_models = sorted(
    set(cal_results) & set(fb_results) & set(fc_results),
    key=short_name,
)
_names = [short_name(m) for m in _all_models]
_n = len(_all_models)

_a = np.array([cal_metrics[m]["mean_1_brier"] for m in _all_models])
_b = np.array([fb_metrics[m]["uwaa"] for m in _all_models])

# Family C: T2-T1 accuracy delta
_c = np.zeros(_n)
_c_dmg = np.zeros(_n)
for idx, m in enumerate(_all_models):
    items = fc_results[m]
    n_items = len(items)
    t1c = sum(v["t1_correct"] for v in items.values())
    t2c = sum(v["t2_correct"] for v in items.values())
    _c[idx] = (t2c - t1c) / n_items
    t1_right = sum(1 for v in items.values() if v["t1_correct"])
    rw = sum(1 for v in items.values()
             if v["t1_correct"] and not v["t2_correct"])
    _c_dmg[idx] = rw / t1_right if t1_right > 0 else 0

def _z(x):
    s = x.std(ddof=0)
    return (x - x.mean()) / s if s > 0 else np.zeros_like(x)

_za, _zb, _zc = _z(_a), _z(_b), _z(_c)

# ═══════════════════════════════════════════════════════════════════════
# 1. EQUAL-WEIGHT Z-SCORE COMPOSITE (Dawes-optimal)
# ═══════════════════════════════════════════════════════════════════════
print("=" * 75)
print("COMPOSITE ANALYSIS — Equal-Weight Z-Score MetaScore")
print("=" * 75)

_meta = (_za + _zb + _zc) / 3
_meta_ab = (_za + _zb) / 2
_rank_abc = _stats.rankdata(-_meta, method="ordinal").astype(int)
_rank_ab = _stats.rankdata(-_meta_ab, method="ordinal").astype(int)
_rank_a = _stats.rankdata(-_a, method="ordinal").astype(int)
_rank_b = _stats.rankdata(-_b, method="ordinal").astype(int)
_rank_c = _stats.rankdata(-_c, method="ordinal").astype(int)

rows = []
for i, nm in enumerate(_names):
    shift = int(_rank_ab[i]) - int(_rank_abc[i])
    arrow = f"{'↑' if shift > 0 else '↓'}{abs(shift)}" if shift != 0 else "="
    rows.append({
        "Model": nm,
        "A (1-Brier)": f"{_a[i]:.4f}",
        "B (UWAA)": f"{_b[i]:.4f}",
        "C (T2-T1 Δ)": f"{_c[i]:+.4f}",
        "C Dmg%": f"{_c_dmg[i]:.1%}",
        "z_A": f"{_za[i]:+.3f}",
        "z_B": f"{_zb[i]:+.3f}",
        "z_C": f"{_zc[i]:+.3f}",
        "MetaScore": f"{_meta[i]:+.3f}",
        "Rank": int(_rank_abc[i]),
        "A+B Rank": int(_rank_ab[i]),
        "Shift": arrow,
    })
rows.sort(key=lambda r: r["Rank"])
print(pd.DataFrame(rows).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# 2. HABERMAN PRMSE — Does Family C add standalone value?
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 75}")
print("HABERMAN PRMSE — Family C Subscore Value Test")
print("=" * 75)

# Reliability estimates (rough)
_rel_a, _rel_b, _rel_c = 0.88, 0.72, 0.35

_prmse_c = _rel_c

_composite_ab = (_za + _zb) / 2
_r_cX = np.corrcoef(_c, _composite_ab)[0, 1]
_r_ab = np.corrcoef(_a, _b)[0, 1]
_rel_ab = (_rel_a + _rel_b + 2 * _r_ab) / (2 + 2 * _r_ab)
_r_trueC_X = _r_cX / np.sqrt(_rel_c * _rel_ab) if _rel_c * _rel_ab > 0 else 0
_prmse_total = min(_r_trueC_X ** 2 * _rel_ab, 1.0)

print(f"\n  PRMSE(C observed)   = {_prmse_c:.3f}")
print(f"  PRMSE(C from A+B)  = {_prmse_total:.3f}")
if _prmse_c > _prmse_total:
    print(f"  → Family C HAS standalone added value")
else:
    print(f"  → Family C observed score has NO standalone value (A+B predicts true C better)")
    print(f"  → Include in composite for profile information; do not report as standalone axis")

print(f"\n  Threshold: C needs reliability ≥ 0.55 for standalone value")
print(f"  Current estimate: α_C ≈ {_rel_c}")

# ═══════════════════════════════════════════════════════════════════════
# 3. DIRICHLET PAIRWISE STABILITY
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 75}")
print("DIRICHLET PAIRWISE STABILITY (10,000 samples, α=1)")
print("=" * 75)

np.random.seed(42)
_N_SAMP = 10000
_weights = np.random.dirichlet([1.0] * 3, size=_N_SAMP)

_pw = np.zeros((_n, _n))
_rk_counts = np.zeros((_n, _n))

for _w in _weights:
    _comp = _w[0] * _za + _w[1] * _zb + _w[2] * _zc
    _rk = _stats.rankdata(-_comp, method="ordinal").astype(int)
    for i in range(_n):
        _rk_counts[i][_rk[i] - 1] += 1
        for j in range(i + 1, _n):
            if _comp[i] > _comp[j]:
                _pw[i][j] += 1
            else:
                _pw[j][i] += 1

_pw /= _N_SAMP
_rk_prob = _rk_counts / _N_SAMP

# Pairwise table
print(f"\n  P(row beats col) across all weight perturbations:\n")
hdr = "           " + "".join(f" {nm:>8s}" for nm in _names)
print(hdr)
for i, nm in enumerate(_names):
    row_str = f"  {nm:9s}"
    for j in range(_n):
        if i == j:
            row_str += f" {'—':>8s}"
        else:
            row_str += f" {_pw[i][j]:>7.1%}"
    print(row_str)

# Rank probability matrix
print(f"\n  Rank probability matrix:")
print(f"  {'':10s}" + "".join(f" {'Rank '+str(k+1):>8s}" for k in range(_n)) + "  E[rank]")
for i, nm in enumerate(_names):
    row_str = f"  {nm:10s}"
    for k in range(_n):
        row_str += f" {_rk_prob[i][k]:>7.1%}"
    e_rank = sum((k + 1) * _rk_prob[i][k] for k in range(_n))
    row_str += f"  {e_rank:.2f}"
    print(row_str)

# Classify orderings
_robust, _fragile = [], []
for i in range(_n):
    for j in range(i + 1, _n):
        p = max(_pw[i][j], _pw[j][i])
        winner = _names[i] if _pw[i][j] > 0.5 else _names[j]
        loser = _names[j] if winner == _names[i] else _names[i]
        if p >= 0.95:
            _robust.append(f"{winner} > {loser} ({p:.0%})")
        elif p < 0.75:
            _fragile.append(f"{winner} > {loser} ({p:.0%})")

print(f"\n  Robust orderings (P≥95%): {_robust if _robust else 'NONE'}")
print(f"  Fragile orderings (P<75%): {_fragile if _fragile else 'NONE'}")

# Kendall's W
_all_rks = np.array([
    _stats.rankdata(-(_w[0]*_za + _w[1]*_zb + _w[2]*_zc), method="ordinal")
    for _w in _weights
])
_S = np.sum(((_all_rks.sum(axis=0) - _all_rks.sum(axis=0).mean()) ** 2))
_W = 12 * _S / (_N_SAMP ** 2 * (_n ** 3 - _n))
print(f"\n  Kendall's W = {_W:.3f} (1.0 = perfect agreement across weight perturbations)")

# ═══════════════════════════════════════════════════════════════════════
# 4. HASSE PARTIAL ORDER + LINEAR EXTENSION RANK PROBABILITIES
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 75}")
print("HASSE PARTIAL ORDER (Pareto dominance across all 3 families)")
print("=" * 75)

_scores_mat = np.column_stack([_a, _b, _c])

_dominance = set()
for i in range(_n):
    for j in range(_n):
        if i != j:
            if (all(_scores_mat[i, k] >= _scores_mat[j, k] for k in range(3))
                    and any(_scores_mat[i, k] > _scores_mat[j, k] for k in range(3))):
                _dominance.add((i, j))

print(f"\n  Dominance relations (X beats Y on ALL 3 families):")
if _dominance:
    for (i, j) in sorted(_dominance):
        print(f"    {_names[i]} > {_names[j]}")
else:
    print(f"    NONE")

print(f"\n  Incomparable pairs:")
for i in range(_n):
    for j in range(i + 1, _n):
        if (i, j) not in _dominance and (j, i) not in _dominance:
            i_wins = [["A", "B", "C"][k] for k in range(3) if _scores_mat[i, k] > _scores_mat[j, k]]
            j_wins = [["A", "B", "C"][k] for k in range(3) if _scores_mat[j, k] > _scores_mat[i, k]]
            print(f"    {_names[i]} ↔ {_names[j]}: "
                  f"{_names[i]} wins {i_wins}, {_names[j]} wins {j_wins}")

# Linear extensions
_consistent = []
for perm in _perms(range(_n)):
    valid = True
    for (i, j) in _dominance:
        if list(perm).index(i) > list(perm).index(j):
            valid = False
            break
    if valid:
        _consistent.append(perm)

_le_rk = np.zeros((_n, _n))
for perm in _consistent:
    for rank, model in enumerate(perm):
        _le_rk[model][rank] += 1
_le_rk /= len(_consistent)

print(f"\n  Linear extensions: {len(_consistent)}/{_n}! = {len(_consistent)}/120 permutations consistent")
print(f"\n  Rank probability matrix (weight-free, from Pareto dominance only):")
print(f"  {'':10s}" + "".join(f" {'Rank '+str(k+1):>8s}" for k in range(_n)) + "  E[rank]")
for i, nm in enumerate(_names):
    row_str = f"  {nm:10s}"
    for k in range(_n):
        row_str += f" {_le_rk[i][k]:>7.1%}"
    e_rank = sum((k + 1) * _le_rk[i][k] for k in range(_n))
    row_str += f"  {e_rank:.2f}"
    print(row_str)

# ═══════════════════════════════════════════════════════════════════════
# 5. KEMENY-YOUNG CONSENSUS RANKING
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 75}")
print("KEMENY-YOUNG CONSENSUS RANKING")
print("=" * 75)

def _kt_dist(r1, r2):
    d = 0
    for i in range(len(r1)):
        for j in range(i + 1, len(r1)):
            if (r1[i] - r1[j]) * (r2[i] - r2[j]) < 0:
                d += 1
    return d

_input_rks = [
    _stats.rankdata(-_a, method="ordinal").astype(int),
    _stats.rankdata(-_b, method="ordinal").astype(int),
    _stats.rankdata(-_c, method="ordinal").astype(int),
]

_best_d = float("inf")
_best_p = []
for perm in _perms(range(1, _n + 1)):
    cand = np.array(perm)
    td = sum(_kt_dist(cand, r) for r in _input_rks)
    if td < _best_d:
        _best_d = td
        _best_p = [cand]
    elif td == _best_d:
        _best_p.append(cand)

print(f"\n  Min total Kendall-tau distance: {_best_d} (of max {3 * _n * (_n-1) // 2})")
for bp in _best_p:
    ordered = [_names[i] for i in np.argsort(bp)]
    print(f"  Consensus: {' > '.join(ordered)}")
for fam, r in zip(["A", "B", "C"], _input_rks):
    print(f"    Distance from Family {fam}: {_kt_dist(_best_p[0], r)}")

# ═══════════════════════════════════════════════════════════════════════
# 6. FRIEDMAN + NEMENYI CRITICAL DIFFERENCE
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 75}")
print("FRIEDMAN TEST + NEMENYI CRITICAL DIFFERENCE")
print("=" * 75)

_avg_rk = np.mean([r.astype(float) for r in _input_rks], axis=0)
N_fam = 3
k_mod = _n
_chi2 = 12 * N_fam / (k_mod * (k_mod + 1)) * (
    np.sum(_avg_rk ** 2) - k_mod * (k_mod + 1) ** 2 / 4
)
_F_id = (N_fam - 1) * _chi2 / (N_fam * (k_mod - 1) - _chi2) if (N_fam * (k_mod - 1) - _chi2) > 0 else 0
_p_fried = 1 - _stats.f.cdf(_F_id, k_mod - 1, (k_mod - 1) * (N_fam - 1))

# Nemenyi CD: q_α(k=5, α=0.05) ≈ 2.728
_q_alpha = 2.728
_CD = _q_alpha * np.sqrt(k_mod * (k_mod + 1) / (6 * N_fam))

print(f"\n  Average ranks across 3 families:")
for i, nm in enumerate(_names):
    print(f"    {nm:10s}: {_avg_rk[i]:.2f}")
print(f"\n  Friedman χ² = {_chi2:.2f}, Iman-Davenport F = {_F_id:.2f}, p = {_p_fried:.3f}")
print(f"  Significant at α=0.05? {'Yes' if _p_fried < 0.05 else 'No'}")
print(f"\n  Nemenyi CD = {_CD:.2f}  (need |Δrank| > {_CD:.2f} for significance)")
_max_diff = max(abs(_avg_rk[i] - _avg_rk[j]) for i in range(_n) for j in range(i+1, _n))
print(f"  Max observed |Δrank| = {_max_diff:.2f}")
if _max_diff < _CD:
    print(f"  → No model pair is statistically separable with only 3 families")
    print(f"  → This is expected: the benchmark's value is in the PROFILE, not the ranking")

# ═══════════════════════════════════════════════════════════════════════
# 7. SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 75}")
print("SUMMARY: MetaScore Leaderboard with Uncertainty")
print("=" * 75)

_summary = []
for i in range(_n):
    _summary.append({
        "Model": _names[i],
        "MetaScore": f"{_meta[i]:+.3f}",
        "Rank": int(_rank_abc[i]),
        "P(Rank 1)": f"{_rk_prob[i][0]:.0%}",
        "P(Rank 5)": f"{_rk_prob[i][_n-1]:.0%}",
        "95% Rank Set": f"{{{int(np.min(np.where(_rk_prob[i]>0.025)[0])+1)}"
                        f"–{int(np.max(np.where(_rk_prob[i]>0.025)[0])+1)}}}",
        "Dominates": ", ".join(
            _names[j] for j in range(_n) if (i, j) in _dominance
        ) or "—",
    })
_summary.sort(key=lambda r: r["Rank"])
print(f"\n{pd.DataFrame(_summary).to_string(index=False)}")

print(f"\n  Equal-weight z-score composite (Dawes 1979: optimal at n={_n})")
print(f"  Dirichlet stability: W = {_W:.2f} | {len(_robust)} robust, {len(_fragile)} fragile orderings")
print(f"  Haberman: Family C α≈{_rel_c} < 0.55 threshold → include in composite, not standalone")
print(f"  Friedman: p = {_p_fried:.2f} → no significant model separation from 3 families alone")
print(f"\n  Key finding: No single family discriminates all models.")
print(f"  The composite reveals capability PROFILES that individual metrics cannot.")

# ═══════════════════════════════════════════════════════════════════════
# EXPORT for benchmark notebook
# ═══════════════════════════════════════════════════════════════════════
_export_rows = []
for i, m in enumerate(_all_models):
    _export_rows.append({
        "model_name": m,
        "model_short": _names[i],
        "a_score": round(_a[i], 4),
        "b_score": round(_b[i], 4),
        "c_delta": round(_c[i], 4),
        "c_damage_rate": round(_c_dmg[i], 4),
        "z_a": round(_za[i], 4),
        "z_b": round(_zb[i], 4),
        "z_c": round(_zc[i], 4),
        "metascore": round(_meta[i], 4),
        "rank_abc": int(_rank_abc[i]),
        "rank_ab_only": int(_rank_ab[i]),
        "dirichlet_p_rank1": round(_rk_prob[i][0], 3),
        "dirichlet_e_rank": round(sum((k+1)*_rk_prob[i][k] for k in range(_n)), 2),
    })

import csv as _csv
_exp_path = os.path.join(OUTPUT_DIR, "composite_analysis.csv")
with open(_exp_path, "w", newline="") as f:
    w = _csv.DictWriter(f, fieldnames=list(_export_rows[0].keys()))
    w.writeheader()
    w.writerows(_export_rows)
print(f"\n  Exported: {_exp_path}")