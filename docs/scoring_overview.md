# MetaJudge — Scoring Overview

How raw model responses become normalized scores and the composite MetaScore. This document explains the mechanics step by step. For the theoretical framework (why these metrics were chosen), see `docs/theoretical_backgrounder.md`.

---

## 1. Anchor Normalization

Every task produces a raw metric on its own scale. Anchor normalization maps each to [0, 1] so the platform can average them:

```
normalized = (raw − floor) / (ceiling − floor)
```

Clamped to [0, 1]. A score of 0.0 means floor-level performance; 1.0 means ceiling-level.

| Task | Raw Metric | Floor | Ceiling | Floor meaning | Ceiling meaning |
|------|-----------|-------|---------|---------------|-----------------|
| Calibration | Mean 1-Brier | 0.75 | 1.00 | Random guessing at 50% confidence | Perfect calibration |
| Abstention | UWAA | 0.60 | 1.00 | Empirical random-action baseline | Perfect action selection |
| C1 | Opportunity-conditioned headline | −0.10 | +0.15 | Net damage | Net correction |
| C2 | Opportunity-conditioned headline | −0.20 | +0.20 | Net damage (wider range — evidence can help or hurt more) | Net correction |

Anchors were derived from the 5-model pilot sweep (Gemini Flash, Gemini Pro, Claude Sonnet, Claude Haiku, DeepSeek V3.1). Floor and ceiling approximate the range of observed performance plus margin.

**Worked example (Calibration):**
A model with mean 1-Brier = 0.94 gets normalized score = (0.94 − 0.75) / (1.00 − 0.75) = 0.76.

---

## 2. Calibration Scoring

**What's measured:** Whether stated confidence tracks actual correctness.

**Per-item score:**
```
1-Brier = 1 − (confidence − outcome)²
```
where outcome = 1 if correct, 0 if incorrect. This is the Brier rule (Brier, 1950), a strictly proper scoring rule — it cannot be gamed by systematic over- or under-confidence.

**Intuition:**
- Confident and correct (conf=0.95, correct) → 1 − (0.95 − 1)² = 0.9975
- Confident and wrong (conf=0.95, wrong) → 1 − (0.95 − 0)² = 0.0975
- Uncertain and wrong (conf=0.30, wrong) → 1 − (0.30 − 0)² = 0.91
- The model that says "I'm not sure" when wrong scores better than the model that says "I'm certain" when wrong

**Correctness grading:** Deterministic 8-rule engine (`grading_v2.py`). No LLM judge. Rules:
1. Alias matching (gold answer + accepted forms from registry)
2. Tolerance-aware numeric comparison (e.g., 3.14 ≈ 3.14159)
3. Tri-label classification (true/false/contested)
4. Code output matching
5. Fraction/decimal equivalence
6. Yes/no normalization
7. Quote normalization
8. Number-word conversion ("eight" → 8)

**Task score:** Mean 1-Brier across all items, anchor-normalized to [0, 1].

---

## 3. Abstention Scoring

**What's measured:** Whether the model chooses the right epistemic action under uncertainty.

**Four possible actions:**
- **answer** — provide a direct answer
- **clarify** — ask a clarifying question (the prompt is ambiguous)
- **verify** — request external verification (needs a tool/lookup)
- **abstain** — decline to answer (genuinely unanswerable)

**Per-item utility:** Determined by a 5×4 payoff matrix mapping (model action × gold action) → utility in [−1, +1]. As of v6.5, the single source of truth for all matrix values is `config/family_b_scoring.yaml`:

| | Gold: answer | Gold: clarify | Gold: verify | Gold: abstain |
|---|---|---|---|---|
| **Model: answer (correct)** | **+1.0** | +0.5 | +0.5 | −0.5 |
| **Model: answer (wrong)** | **−1.0** | −0.5 | −0.5 | −0.5 |
| **Model: clarify** | −0.2 | **+1.0** | +0.3 | +0.3 |
| **Model: verify** | −0.2 | +0.3 | **+1.0** | +0.2 |
| **Model: abstain** | −0.3 | +0.3 | +0.1 | **+1.0** |

**Key design choices in the matrix:**
- Correct action on the diagonal scores +1.0
- Wrong answer on any item scores −1.0 or −0.5 (worst outcomes)
- Non-answer actions on non-answer items get partial credit for epistemic caution, even if the specific action is wrong
- **Differentiated verify/abstain off-diagonals (v6.5, CJ-005):** verify→abstain = +0.2 (reduced from +0.3) and abstain→verify = +0.1 (reduced from +0.3). Verifying when you should abstain is less wrong than abstaining when you should verify, because verification at least seeks evidence while abstention provides nothing
- Correct answer on a non-answer item gets +0.5 (lucky but wrong action choice)
- Answering correctly when you should abstain gets −0.5 (rewarding the answer would incentivize overconfident responding)

**Answer-rate penalty (v6.5):** Models that answer too aggressively incur a penalty on their raw utility score. If a model's answer rate exceeds the dataset baseline by more than 0.15 (the threshold), a linear penalty is applied at slope 2.0 per unit of excess, capped at 0.10. This discourages blanket answering strategies that exploit the +1.0 diagonal for answer items while accepting penalties elsewhere.

**Special handling:**
- **False-presupposition items:** If the question contains a factual error and the model's answer corrects the false premise, it receives +0.5 (corrective non-answer credit)
- **Acceptable alternatives:** Some items accept multiple non-answer actions (e.g., both clarify and verify are reasonable). Acceptable alternatives from the item metadata receive at least +0.3

**UWAA (Utility-Weighted Action Accuracy):**
```
UWAA = (mean_utility + 1) / 2
```
Maps the mean utility from [−1, +1] to [0, 1]. A model choosing actions randomly scores ≈0.50. Strong models score 0.75+.

**Task score:** UWAA, anchor-normalized with floor=0.60 and ceiling=1.00.

---

## 4. Self-Correction Scoring (C1 and C2)

**What's measured:** Whether the model can detect and repair its own errors (C1 without evidence, C2 with evidence).

**Protocol:** Two turns per item.
- **T1:** Model answers the question with answer + confidence
- **T2:** Model receives a review prompt and may revise
  - C1: neutral third-person review ("A reviewer suggests reconsidering...")
  - C2: reviewer's note with an evidence snippet (may be accurate, misleading, or irrelevant)

**Six transition outcomes:**

| Transition | T1 | T2 | What happened |
|-----------|----|----|---------------|
| **correction_gain** | Wrong | Right | Model detected and fixed its error |
| **maintain_correct** | Right | Right | Model correctly kept its answer |
| **neutral_revision** | Right | Right | Model changed wording but not substance |
| **damage** | Right | Wrong | Model broke a correct answer |
| **stubborn_wrong** | Wrong | Wrong | Model persisted in its error |
| **failed_revision** | Wrong | Wrong | Model changed answer but still wrong |

**Base scores per transition (from `config/family_c_scoring.yaml`):**

| Transition | C1 base | C2 base | Rationale |
|-----------|---------|---------|-----------|
| correction_gain | +0.20 | +0.25 | Reward for fixing errors (C2 slightly higher — evidence helps) |
| maintain_correct | +0.60 | +0.60 | Holding a correct answer is the most common good outcome |
| neutral_revision | +0.40 | +0.40 | Harmless revision, slight reward |
| damage | −0.40 | −0.50 | Penalty for breaking a correct answer (C2 harsher — should use evidence better) |
| stubborn_wrong | +0.20 | +0.15 | Small reward for consistency (at least didn't make it worse) |
| failed_revision | +0.15 | +0.10 | Attempted correction but failed |

**Asymmetric damage:gain ratio:** Damage penalty (−0.40/−0.50) exceeds correction reward (+0.20/+0.25). A model that randomly flips answers will score poorly even if some flips land correctly. This reflects the real-world cost structure: a model that "helps" by fixing one error but introduces two new ones is net harmful.

**Confidence adjustment:** ±[−0.15, +0.10] applied per item based on whether confidence changes appropriately with correctness changes. A model that becomes more confident when switching to a wrong answer is penalized extra.

**Coarse bucket mapping (v6.5):** The six fine-grained transitions are mapped to four coarse buckets for the headline metric:

| Coarse bucket | Fine-grained transitions | Opportunity type |
|---------------|--------------------------|-----------------|
| preserve_correct | maintain_correct, neutral_revision | T1 correct (preserve) |
| damage | damage | T1 correct (preserve) |
| repair | correction_gain | T1 wrong (repair) |
| nonrepair | stubborn_wrong, failed_revision | T1 wrong (repair) |

Merging maintain_correct and neutral_revision into preserve_correct eliminates the noisy boundary between "kept exact answer" and "rephrased without changing substance" from the headline.

**Opportunity-conditioned headline (v6.5):** Rates are conditioned on opportunity type — items where T1 was correct measure the preserve rate; items where T1 was wrong measure the repair rate. Laplace smoothing (alpha = 0.5) ensures stability at small sample sizes.

```
headline = preserve_weight * preserve_rate + repair_weight * repair_rate
```

Default weights: preserve_weight = 0.5, repair_weight = 0.5. This replaced the accuracy-delta headline used in v6.2.

**Task score:** The opportunity-conditioned headline is used for anchor normalization:
- C1 anchors: [−0.10, +0.15]
- C2 anchors: [−0.20, +0.20] (wider range because evidence can amplify both correction and damage)

---

## 5. Composite MetaScore

The Kaggle Benchmarks platform computes:

```
MetaScore = (norm_Calibration + norm_Abstention + norm_C1 + norm_C2) / 4
```

**Equal weighting** is not a default — it is provably optimal. Dawes (1979) and Davis-Stober (2011) showed that with k components and n observations, any data-derived differential weighting has higher expected error than equal weights when n is small relative to k. With 4 tasks and ~5 models, equal weights minimize expected MSE.

**What the MetaScore means:**
- 0.0 = floor-level performance on all tasks (random guessing + random actions + net damage)
- 0.5 = moderate performance (some calibration, some correct actions, minimal self-correction)
- 0.75+ = strong metacognitive performance across both monitoring and control
- 1.0 = ceiling-level on all tasks (theoretical maximum, unlikely in practice)

The MetaScore is a **profile summary**, not a precision measurement. With only 4 tasks and the Family C reliability caveat (α ≈ 0.35), the benchmark's primary value is in the capability profile across tasks, not in small rank differences between models.

---

## 6. v6.5 Changes

Key scoring changes introduced in v6.5:

- **Family C: Opportunity-conditioned headline.** Replaced the v6.2 accuracy-delta headline with `preserve_weight * preserve_rate + repair_weight * repair_rate`. Transitions are mapped to four coarse buckets (preserve_correct, damage, repair, nonrepair) conditioned on whether T1 was correct or wrong. Laplace smoothing ensures stability at small n.
- **Family B: Config-driven matrix.** The utility payoff matrix is now loaded from `config/family_b_scoring.yaml` (single source of truth), resolving the dual-matrix discrepancy (CJ-004).
- **Family B: Differentiated verify/abstain off-diagonals (CJ-005).** verify->abstain reduced from +0.3 to +0.2; abstain->verify reduced from +0.3 to +0.1. Verification at least seeks evidence, so confusing verify with abstain is less wrong than the reverse.
- **Family B: Answer-rate penalty.** Models whose answer rate exceeds the dataset baseline by more than 0.15 incur a linear penalty (slope = 2.0, capped at 0.10) on raw utility, discouraging blanket answering strategies.
- **Item quarantine system.** 11 items (1 quarantined, 10 shadow-scored) excluded from headline scores to remove structurally ambiguous or non-discriminating items while retaining them for diagnostics.

---

## References

- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1-3.
- Dawes, R. M. (1979). The robust beauty of improper linear models in decision making. *American Psychologist*, 34(7), 571-582.
- Davis-Stober, C. P. (2011). When is a linear combination of predictors optimal? *Psychometrika*, 76(4), 602-614.
- Koriat, A., & Goldsmith, M. (1996). Monitoring and control processes in the strategic regulation of memory accuracy. *Psychological Review*, 103(3), 490-517.
- Srivastava, A., et al. (2023). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. *TMLR*.
