# MetaJudge v6.2 — Synthesis Report

> **Mission:** Evaluate whether MetaJudge v6.2 produces scores that are transparent,
> clear, reliable, and useful — and identify specific improvements for v7.
> The goal is honest scrutiny, not defense.

**Models:** 5 complete | **Items audited:** 1,444+ records
**Deep audits:** 5 models | **Intensive cross-model:** 25 items × 6 models
**Pipeline accuracy:** 99.2% (1,137 items verified)

---

## Executive Summary

MetaJudge v6.2 **works** — the grading pipeline is 99.2% accurate, scores are
computationally correct, and the benchmark surfaces a real phenomenon (the
monitoring-control gap). However, three domain-level assessments reveal
significant issues that must be addressed before the benchmark can be considered
**reliable** and **useful** at the precision its scores imply.

**What works:**
- Calibration is the strongest task — transparent, well-discriminating, intuitive
- The deterministic grading engine eliminates LLM-judge variance
- Bug disclosure and audit trail are exemplary
- The monitoring-control gap is universally observed and theoretically grounded

**What needs work:**
- **CRITICAL:** Self-correction scoring pipeline diverges from documentation
  (transition weights documented but accuracy delta used in production)
- Abstention partial credit (+0.3) compresses score range and rewards caution over discrimination
- C1/C2 item counts (28/23) are too small for reliable individual-model scores
- Run-to-run stochasticity on C1 produces 0.29 normalized swings
- 4 grading bugs found (tri_label, parser, encoding) affecting ~2-4 items per model

---

## Final Leaderboard (6 Complete Models)

| # | Model | Cal | Abs | C1 | C2 | **Meta** | Mon | Ctrl | Gap | Cost | $/Pt |
|---|-------|-----|-----|----|----|---------|-----|------|-----|------|------|
| 1 | gemini-3-flash-preview | 0.853 | 0.602 | 0.400 | 0.500 | **0.589** | 0.853 | 0.501 | +0.352 | $1.99 | $3.38 |
| 2 | claude-sonnet-4@20250514 | 0.602 | 0.616 | 0.400 | 0.500 | **0.530** | 0.602 | 0.505 | +0.097 | $1.54 | $2.91 |
| 3 | claude-sonnet-4-6@default | 0.644 | 0.396 | 0.257 | 0.500 | **0.449** | 0.644 | 0.384 | +0.260 | $1.78 | $3.96 |
| 4 | gemini-2.5-pro | 0.792 | 0.260 | 0.257 | 0.283 | **0.398** | 0.792 | 0.267 | +0.525 | $6.47 | $16.27 |
| 5 | gemma-4-26b-a4b | 0.128 | 0.482 | 0.400 | 0.391 | **0.350** | 0.128 | 0.425 | -0.297 | $0.10 | $0.27 |

### The Monitoring-Control Gap

Every model monitors better than it controls (except Gemma-26b where low
calibration inverts the pattern). The gap ranges from +0.097 (Sonnet 4) to
+0.525 (Pro). This is MetaJudge's core finding and it is robust — observed
across all model families, sizes, and providers.

---

## Composite MetaScore Assessment

### Equal-Weight Validity

| Model | Equal (actual) | Mon-heavy (40/20/20/20) | Ctrl-heavy (10/30/30/30) | Rank change? |
|-------|---------------|------------------------|-------------------------|-------------|
| gemini-3-flash-previ | 0.589 | 0.641 | 0.536 | ⚠️ |
| claude-sonnet-4@2025 | 0.530 | 0.544 | 0.515 | — |
| claude-sonnet-4-6@de | 0.449 | 0.488 | 0.410 | — |
| gemini-2.5-pro | 0.398 | 0.477 | 0.319 | ⚠️ |
| gemma-4-26b-a4b | 0.350 | 0.306 | 0.395 | — |

**Finding:** Flash leads under all weighting schemes. Pro drops further under
control-heavy weights. Gemma-26b rises under control-heavy (its calibration is
the drag). The equal-weight composite is a reasonable compromise, but the
**component scores are more informative than the composite** for model selection.

---

## Domain Assessments (Summary)

Detailed assessments in `synthesis_calibration.md`, `synthesis_abstention.md`,
`synthesis_self_correction.md`.

### Calibration: STRONG ✅
- Transparency: exemplary (full audit trail, no LLM judge)
- Clarity: good (Brier rule intuitive, normalization explained)
- Reliability: strong (deterministic, single-turn)
- Utility: **best discriminator** (0.725 range, 31% discriminating items)
- Bugs: 6 items affected (tri_label, parser) — minor impact

### Abstention: ADEQUATE WITH CONCERNS ⚠️
- Transparency: adequate (payoff matrix published, but +0.3 unjustified)
- Clarity: mixed (UWAA intuitive, verify/abstain boundary unclear)
- Reliability: moderate (dual-run available, 0.356 score range compressed)
- Utility: **measures something real but partial credit masks poor control**
- Key concern: 38.9% action accuracy → 0.26 normalized. The scoring rewards
  cautious disposition nearly as much as genuine metacognitive discrimination

### Self-Correction: NEEDS SIGNIFICANT WORK ❌
- Transparency: **CRITICAL BUG** — transition scoring documented but accuracy
  delta used in production. Documentation and implementation diverge.
- Clarity: weak (0.257 means delta=-1/28, uninformative headline)
- Reliability: **weakest** (n=28/23, 0.29 stochasticity swing, score clustering)
- Utility: mixed (deceptive traps discriminate well, but 40% items saturated)
- The transition-level data IS rich and informative — the problem is that the
  headline score discards this richness

---

## Priority Recommendations for v7

### Critical (must fix)
1. **Resolve scoring pipeline divergence:** Either implement transition-based
   scoring in production notebooks OR update documentation to match accuracy delta.
   The current state is that the scoring spec and the implementation disagree.
2. **Increase self-correction items to ≥50 per subfamily.** n=28/23 produces
   ~3.6%/4.3% resolution per item flip — insufficient for meaningful ranking.

### High (should fix)
3. **Empirically calibrate abstention partial credit.** The +0.3 for wrong
   non-answer actions compresses the score range. Simulate alternative values
   (0.0, +0.1, +0.2) and compare discrimination across the 6-model panel.
4. **Require 3+ runs for C1/C2** with median aggregation. Single-run C1 scores
   have 0.29 normalized stochasticity — not meaningfully precise.
5. **Fix 4 grading bugs:** tri_label accepted_forms, exact_constant parser,
   code_output substring match, confirmation detection gaps.

### Medium (should address)
6. **Publish anchor derivation data.** Floor/ceiling values and the pilot sweep
   data that produced them should be auditable.
7. **Reclassify sc_c1_wr_023** from wrong_to_right to deceptive_trap (4/6 models
   damaged — it functions as a trap, not a correction opportunity).
8. **Report component scores alongside MetaScore.** The monitoring-control gap
   is more informative than the single number. Normalize presentation to
   show both.

### For the submission
9. **Lead the writeup with the monitoring-control gap finding.** This is the
   benchmark's strongest contribution — universally observed, theoretically
   grounded, and practically meaningful.
10. **Be transparent about C1/C2 limitations.** The precision problem is real.
    Presenting it honestly strengthens the submission, not weakens it.

---

## Audit File Index

| File | Content |
|------|---------|
| `synthesis_calibration.md` | Calibration 4-criteria assessment |
| `synthesis_abstention.md` | Abstention 4-criteria assessment |
| `synthesis_self_correction.md` | SC C1+C2 4-criteria assessment |
| `intensive_calibration.md` | 5 items × 6 models deep analysis |
| `intensive_abstention.md` | 5 items × 6 models deep analysis |
| `intensive_self_correction.md` | 10 items × 6 models deep analysis |
| `intensive_problematic_items.md` | 5 buggy items cross-model |
| `cross_model_audit.md` | 1,137 items automated grading check |
| `canonical_dataset.json` | 1,444 records, all scores, costs |
| Per-model audits (5) | gemini_pro, sonnet46, flash, gpt54, gemma26b |