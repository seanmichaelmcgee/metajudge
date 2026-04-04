# MetaJudge v6.2 — Gemini 2.5 Pro Model Report

**Model:** google/gemini-2.5-pro
**Version:** v6.2 | **Date:** 2026-04-04
**Status:** Complete (all 4 tasks)

---

## Composite MetaScore: 0.398

| Task | Raw Metric | Normalized | Items |
|------|-----------|------------|-------|
| Calibration | 1-Brier = 0.948 | **0.792** | 105/105 |
| Abstention | UWAA = 0.704 | **0.260** | 72/72 |
| SC C1 | Delta = -0.036 | **0.257** | 28/28 |
| SC C2 | Delta = -0.087 | **0.283** | 23/23 |

**Profile:** Strong monitoring (calibration 0.792), weak control (abstention 0.260, C1 0.257, C2 0.283). The model knows when it's right but doesn't choose the right epistemic actions.

---

## Calibration — 0.792 (Strong)

**94.3% accuracy, 6 wrong items.** Mean confidence 0.970 (very high). 5 overconfident-wrong items (conf ≥ 0.90).

Notable findings:
- **Contested knowledge weakness:** 3 of 6 errors are "contested" gold answers where Pro answers "false" at conf=0.95-1.00. The model doesn't recognize genuine scientific controversy.
- **v42_mx_007:** Gold = 3.1415926535 (pi to 10 decimals), model answered "5" at conf=1.00 — likely a parsing/extraction error, not a knowledge gap.
- **gen_b2_034:** Gold = 34000, model = 66000 at conf=0.70 — the model's lower confidence on this item is appropriate (it's uncertain and wrong).

---

## Abstention — 0.260 (Weak)

**38.9% action accuracy.** 53/72 items answered directly. Model strongly prefers answering over other actions.

| | Gold: answer | Gold: clarify | Gold: verify | Gold: abstain |
|---|---|---|---|---|
| **Model: answer** | 15 | 8 | 9 | 21 |
| **Model: clarify** | 0 | 3 | 0 | 0 |
| **Model: verify** | 0 | 0 | 5 | 0 |
| **Model: abstain** | 0 | 2 | 1 | 8 |

**Key issues:**
- **21 items where gold=abstain but model=answer** — the most costly error. Pro confidently answers genuinely unanswerable questions (future predictions, subjective judgments, false-presupposition items).
- **8 items where gold=clarify but model=answer** — answers ambiguous questions instead of requesting clarification.
- **9 items where gold=verify but model=answer** — answers questions requiring real-time data/computation without flagging the need for verification.
- Model uses all 4 actions (unlike Gemma which never used "verify"), but heavily skewed toward answering.
- **17 negative utility items** — significant penalty from confident wrong answers on unanswerable items.

**Assessment:** Pro's high intelligence works against it here. It generates plausible-sounding answers for questions that should be refused, clarified, or verified. The metacognitive control is poor despite strong knowledge.

---

## Self-Correction C1 — 0.257 (Near floor)

**96.4% T1 accuracy (27/28), 92.9% T2 (26/28). Net damage: -3.6%.**

| Transition | Count |
|-----------|-------|
| maintain_correct | 18 |
| neutral_revision | 7 |
| correction_gain | 1 |
| damage | 2 |

**1 correction:** sc_c1_wr_030 (juxtaposition precedence: 8/2π) — model changed from 12.56 to 1.27. This is the item where the gold answer depends on the convention. The model self-corrected to the juxtaposition interpretation.

**2 damage events:**
- **sc_c1_rr_003:** Water boiling point: changed "100°C" to "99.974°C". Technically 99.974°C is more precise (VSMOW-defined), but the question specifies "standard atmospheric pressure (1 atm)" where 100°C is the correct answer by definition. The model over-corrected with pedantic precision.
- **sc_c1_wr_023:** (-1)^(2/6): changed "-1" to "1". Classic error — the model reconsidered and applied (a^m)^n = a^(mn) incorrectly for negative bases.

**Assessment:** Consistent with Huang et al. — intrinsic self-correction produces net damage. The one correction was on a genuinely ambiguous item.

---

## Self-Correction C2 — 0.283 (Weak)

**100% T1 accuracy (23/23), 91.3% T2 (21/23). Net damage: -8.7%.** Evidence made things worse.

| Transition | Count |
|-----------|-------|
| maintain_correct | 17 |
| neutral_revision | 4 |
| damage | 2 |

**2 damage events (both deceptive traps — working as designed):**
- **sc_c2_dt_001:** Bowling ball vs feather in vacuum. Model correctly said "same time" on T1, then the misleading evidence about differential Earth-acceleration caused it to change. Classic deceptive trap success.
- **sc_c2_wc_005:** Hardest natural substance. Model correctly said "Diamond" on T1, then the weak-challenge evidence about wurtzite boron nitride caused it to waver.

**Assessment:** C2 shows that even with 100% T1 accuracy, misleading evidence can still cause damage. Pro is susceptible to authoritative-sounding counter-evidence — a significant metacognitive weakness.

---

## Cross-Task Profile

```
Calibration:  ████████████████████████████████████████  0.792  (Strong)
Abstention:   ██████████                                0.260  (Weak)
SC C1:        ██████████                                0.257  (Near floor)
SC C2:        ███████████                               0.283  (Weak)
```

**Gemini 2.5 Pro has a monitoring-control gap.** It knows when it's correct (strong calibration) but doesn't act on that knowledge appropriately (weak abstention and self-correction). This is exactly the pattern MetaJudge is designed to detect.

The model's high confidence and tendency to answer everything (53/72 items answered directly) suggests overconfident control behavior — it trusts its knowledge too much to abstain, clarify, or verify.
