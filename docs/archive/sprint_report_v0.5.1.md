# MetaJudge Sprint Report v0.5.1
## March 21, 2026 — vNext Technical Fixes + Family B Expansion

**Run version:** v0.5.1  
**Previous version:** v0.5.0  
**Branch:** `sprint/refinement-v2`  
**Model:** 5-model sweep (Flash, Pro, Sonnet, Haiku, DeepSeek)  
**Calibration items:** 117  |  **Family B items:** 87

---

## Executive Summary

v0.5.1 lands the P0 technical fixes from the vNext sprint: IOED answer-key repairs, Family B v2 scorer wiring (corrective answers credited), per-model audit breakdown, and 12 new Family B items. Family B utility improved significantly (+0.16) driven by the v2 scorer crediting corrective non-answers. Calibration remains stable. The bridge layer confirms the core scientific finding: models make dramatically better control decisions when uncertain.

---

## 1. Calibration (Monitoring Benchmark)

### 5-Model Leaderboard

| Model | Score (1-Brier) | Accuracy | Mean Conf | ECE |
|-------|----------------|----------|-----------|-----|
| Gemini 2.5 Pro | 0.8853 | 102/117 (87%) | 0.968 | low |
| Gemini 2.5 Flash | 0.8824 | 102/117 (87%) | 0.953 | low |
| DeepSeek V3.1 | 0.8318 | 88/117 (75%) | 0.864 | moderate |
| Claude Sonnet 4 | 0.8155 | 91/117 (78%) | 0.880 | moderate |
| Claude Haiku 4.5 | 0.7807 | 84/117 (72%) | 0.874 | highest |

### Success Criteria

| # | Criterion | Threshold | v0.5.0 | v0.5.1 | Verdict |
|---|-----------|-----------|--------|--------|---------|
| C1 | Brier spread | >= 0.05 | 0.147 | **0.105** | **PASS** |
| C4 | Conf-acc gap items | >= 10 | 51 | **47** | **PASS** |
| C5 | ECE range | >= 0.03 | 0.122 | **0.073** | **PASS** |

All three verifiable criteria pass. Spread narrowed slightly (0.147→0.105) because Sonnet improved (+0.014) while Pro held steady — the models are converging but still clearly separable.

### Mechanism Performance (Gemini Pro)

| Mechanism | Items | Accuracy | Score | Assessment |
|-----------|-------|----------|-------|------------|
| AmbiguityMetacognition | 14 | 50% | 0.547 | **Hardest** — discriminates strongly |
| RLHF | 3 | 67% | 0.729 | Small n, moderate difficulty |
| MonitoringTrap | 20 | 85% | 0.864 | New items working — 15% error rate at high conf |
| ModifiedCRT | 18 | 89% | 0.888 | Strong discriminator |
| Prototype | 10 | 90% | 0.922 | Clean signal |
| Compositional | 17 | 94% | 0.957 | Approaching ceiling |
| Anchoring-CodeExec-IOED-CT | 35 | 97-100% | 0.97+ | Ceiling — low metacognitive value |

**IOED fix confirmed:** The 2 remaining IOED items now score 100% (was 0%). The 5 replacement computation items are performing as expected.

### What Changed in Calibration (v0.5.0 → v0.5.1)

| Change | Impact |
|--------|--------|
| 5 bad IOED items removed (wrong gold keys) | Removed artificial floor on accuracy |
| 5 verified computation items added | Clean Stratum A items, all models pass |
| IOED block no longer 0% accuracy | Mechanism map now accurate |
| No scoring changes to calibration | Stability preserved |

---

## 2. Family B (Control Benchmark)

### Headline Metrics

| Metric | v0.5.0 | v0.5.1 | Delta | Assessment |
|--------|--------|--------|-------|------------|
| Items | 75 | **87** | +12 | +6 verify, +6 false-presup |
| Action match | 53.3% | **54.0%** | +0.7pp | Modest improvement |
| Mean utility | +0.327 | **+0.487** | **+0.160** | Significant improvement |
| UWAA | 0.554 | **0.744** | **+0.190** | Large improvement |

### Per-Action Analysis

| Gold Action | Items | Match Rate | Utility | Assessment |
|-------------|-------|-----------|---------|------------|
| Answer | 15 | 100% | +0.867 | **Strong** — 14/15 correct answers |
| Clarify | 13 | 69% | +0.538 | **Decent** — model recognizes most ambiguity |
| Verify | 30 | 40% | +0.153 | **Weak** — still over-answers |
| Abstain | 29 | 38% | **+0.614** | **Big improvement** (was +0.157) |

### Abstain Class: v2 Scorer Impact

The single biggest improvement: abstain utility jumped from +0.157 to +0.614. This is entirely due to the v2 scorer crediting corrective non-answers on false-presupposition items. Previously, a model that said "the premise is false because..." got -0.5 (treated as wrong answer). Now it gets +0.5 (recognized as correct epistemic behavior).

### Model Action Distribution

| Action | Gold Distribution | Model Distribution | Gap |
|--------|------------------|--------------------|-----|
| Answer | 15 (17%) | 48 (55%) | **Over-answers by 38pp** |
| Clarify | 13 (15%) | 14 (16%) | Balanced |
| Verify | 30 (34%) | 12 (14%) | **Under-verifies by 20pp** |
| Abstain | 29 (33%) | 13 (15%) | **Under-abstains by 18pp** |

The core finding persists: **the model massively over-answers when it should verify or abstain.** This is the metacognitive control failure the benchmark is designed to detect.

### What Changed in Family B (v0.5.0 → v0.5.1)

| Change | Impact |
|--------|--------|
| v2 scorer wired into notebook | Corrective answers now credited (+0.5 on false-premise items) |
| abs_001 gold fixed (23→31) | 1 more correct answer-class item |
| abs_004 replaced (bad question) | Clean answer-class item |
| +6 hard verify items | Tests computational limits, stale knowledge |
| +6 false-presupposition items | Subtle wrong dates/locations/attributions |
| 23 total false-presup items | Up from 17 — broader coverage |

---

## 3. Bridge Report: Monitoring-Control Coupling

### Quadrant: monitoring_bad / control_bad
Both constructs show room for improvement, but the bridge signal is strong.

### Key Bridge Findings

| Confidence Band | Items | Mean Utility | Dominant Action | Interpretation |
|----------------|-------|-------------|-----------------|----------------|
| Very low (0-0.3) | 24 | **+0.91** | clarify/verify/abstain | When uncertain, model acts wisely |
| Very high (0.85-0.95) | 11 | +0.40 | mixed | Moderate — some good, some overconfident |
| Extreme (0.95+) | 47 | **+0.30** | answer (83%) | When confident, model over-answers |

**The core scientific finding strengthens:** There is a clear monotonic relationship between confidence and control quality. Low confidence → excellent control decisions (utility +0.91). High confidence → mediocre control (+0.30). This is the monitoring-control dissociation that the benchmark is designed to reveal.

### Failure Modes

| Mode | Count | Change from v0.5.0 |
|------|-------|-------------------|
| Overconfident wrong answer | 33 | +2 (more items) |
| False premise not caught | 0 | Same |
| Over-cautious | 0 | Same |
| Unnecessary clarification | 0 | Same |

---

## 4. Version Comparison

| Metric | v0.5.0 | v0.5.1 | Direction |
|--------|--------|--------|-----------|
| Cal items | 117 | 117 | = |
| Family B items | 75 | 87 | ↑ |
| Flash score | 0.865 | **0.882** | ↑ (+0.017) |
| Pro score | 0.887 | **0.885** | ≈ (−0.002) |
| Brier spread | 0.147 | **0.105** | ↓ (narrowing) |
| FB action match | 53.3% | **54.0%** | ↑ |
| FB mean utility | +0.327 | **+0.487** | ↑↑ (+0.160) |
| FB UWAA | 0.554 | **0.744** | ↑↑ (+0.190) |
| Abstain utility | +0.157 | **+0.614** | ↑↑↑ (+0.457) |

---

## 5. Progress Toward Competition Goals

### Strong

- **Monitoring-control framework** is scientifically coherent and producing genuine results
- **Bridge finding** (confidence→utility mapping) is publishable and competition-relevant
- **5-model discrimination** on calibration: clear tier separation (Google > DeepSeek ≈ Anthropic)
- **Family B detects real metacognitive failures**: 55% over-answering rate when model should verify/abstain
- **Grading infrastructure** working: per-model audit, v2 scorer, bridge analytics

### Needs Work Before Submission

| Priority | Issue | Estimated Effort |
|----------|-------|-----------------|
| **P1** | Verify class still weak (40% match) — models default to answering | Need harder verify items that punish confident wrong answers |
| **P1** | Brier spread narrowing (0.147→0.105) — Sonnet improved, reducing separation | Monitor; may need harder Stratum C items |
| **P1** | Writeup draft (1500 words) — competition requirement | 3 hours |
| **P2** | AmbiguityMetacognition at 50% on Pro — review if gold answers are defensible | 1 hour review |
| **P2** | Multi-model bridge comparison (currently single-model bridge report) | Need bridge across all 5 models |
| **P3** | Anchoring/CodeExec/CT at ceiling — consider retiring or reducing weight | Low urgency |

---

## 6. Highest-Yield Next Actions

### For v0.5.2 (iterative)
1. **Run multi-model bridge** — produce 5 bridge reports for comparison table
2. **Review AmbiguityMetacognition gold answers** — 50% accuracy suggests possible key issues
3. **Begin writeup outline** — structure the 1500-word narrative around the bridge finding

### For v0.6.0 (structural, if time permits)
4. Add harder verify items that specifically penalize stale parametric knowledge
5. Add calibration items targeting the 0.85-0.95 confidence band (where utility drops)
6. Composite score tuning based on bridge analysis

---

## Appendix: Run Metadata

| Field | Value |
|-------|-------|
| Run timestamp | 2026-03-21T23:38:12Z |
| Grading engine | grading_v2 |
| Registry rules | 7 (alias_plus_normalization, approx_numeric_small, approx_numeric_dynamic, code_output, tri_label, exact_constant, fraction_or_decimal) |
| Calibration audit rows | 611 (117 items × 5 models + retries) |
| Family B audit rows | 88 (87 items, 1 duplicate) |
| Bridge model | google/gemini-2.5-flash |
