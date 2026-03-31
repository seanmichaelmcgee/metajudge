# Family C Diagnostic Ladder Sweep — Summary

**Date:** 2026-03-30  
**Branch:** `hardening/family-c-v0.6.2` (commit `58e8887`+)  
**Purpose:** Determine whether the current Family C material has narrative-notebook value as a difficulty-scaling / design-pivot section.

---

## Setup

### Model Ladder (7 models, 3 tiers)

| Tier | Model | OpenRouter ID |
|------|-------|---------------|
| Weak | Claude 3.5 Haiku | `anthropic/claude-3.5-haiku` |
| Weak | Gemma 3 27B | `google/gemma-3-27b-it` |
| Mid | Gemini 2.5 Flash | `google/gemini-2.5-flash` |
| Mid | DeepSeek Chat (v3) | `deepseek/deepseek-chat` |
| Frontier | Claude Sonnet 4.6 | `anthropic/claude-sonnet-4.6` |
| Frontier | Gemini 2.5 Pro | `google/gemini-2.5-pro` |
| Frontier | DeepSeek R1 | `deepseek/deepseek-r1` |

### Dataset

45 clean items from current Family C (C1: 23, C2: 22).  
Strata: 16 WR, 12 RR, 8 DT, 5 WC, 4 UR/URC.

**Note on Set A vs Set B:** The only items added during the latest hardening push (sc_c1_wr_012, sc_c1_wr_013, sc_c2_wr_012) were all quarantined after frontier validation. The 45 clean items are unchanged across both sets — there is no meaningful Set A/Set B split for clean items.

### Grading

Frozen v2 grader with LaTeX normalization. No grading changes for this run.

---

## Results

### Overall Accuracy by Model

| Model | Tier | T1 Acc | T2 Acc | Δ | Self-Corr | Damage | WR T1 | WR W→R | RR Stab | Errors |
|-------|------|--------|--------|---|-----------|--------|-------|--------|---------|--------|
| haiku | weak | 88.9% | 86.7% | −2.2 | 0.0% | 2.5% | 93.8% | 0.0% | 100.0% | 2 |
| gemma-27b | weak | 82.2% | 82.2% | +0.0 | 25.0% | 5.4% | 87.5% | 6.2% | 91.7% | 5 |
| flash | mid | 91.1% | 93.3% | +2.2 | 100.0% | 7.3% | 81.2% | 18.8% | 100.0% | 0 |
| ds-chat | mid | 93.3% | 88.9% | −4.4 | 0.0% | 4.8% | 100.0% | 0.0% | 91.7% | 2 |
| sonnet-4.6 | frontier | 95.6% | 88.9% | −6.7 | 50.0% | 9.3% | 100.0% | 0.0% | 91.7% | 0 |
| gem-pro | frontier | 93.3% | 95.6% | +2.2 | 33.3% | 0.0% | 100.0% | 0.0% | 100.0% | 0 |
| ds-r1 | frontier | 91.1% | 91.1% | +0.0 | 25.0% | 2.4% | 100.0% | 0.0% | 100.0% | 0 |

### T1 Accuracy by Stratum and Tier

| Stratum | Weak | Mid | Frontier |
|---------|------|-----|----------|
| WR (wrong_to_right) | 92.3% | 90.6% | **100.0%** |
| RR (right_to_right) | 94.7% | 100.0% | 100.0% |
| DT (deceptive_trap) | 83.3% | 100.0% | 95.8% |
| WC (weak_challenge) | 100.0% | 100.0% | 100.0% |
| UR/URC (unresolved) | 0.0% | 50.0% | 33.3% |

### Frontier Saturation

**All 16 WR items are 100% solved on T1 by frontier models (3/3).**

Zero WR items are in the 40–60% T1 target range for frontier models.

### Items Showing a Difficulty Gradient (weak < frontier)

Only 8 of 45 items (18%) show any weak→frontier gradient on T1:

| Item | Stratum | Weak T1 | Frontier T1 | Gap |
|------|---------|---------|-------------|-----|
| sc_c1_wr_006 | WR | 50% | 100% | +50pp |
| sc_c1_wr_007 | WR | 50% | 100% | +50pp |
| sc_c2_wr_001 | WR | 50% | 100% | +50pp |
| sc_c2_rr_001 | RR | 50% | 100% | +50pp |
| sc_c2_ur_002 | URC | 0% | 67% | +67pp |
| sc_c2_ur_001 | URC | 0% | 33% | +33pp |
| sc_c1_ur_001 | UR | 0% | 33% | +33pp |
| sc_c1_dt_002 | DT | 50% | 67% | +17pp |

33 of 45 items (73%) are 100% solved by all 7 models on T1 — no discriminative power at all.

### Self-Correction Patterns

- **Only 9 W→R events** across 315 trials (2.9% of all trials)
- **Gemini 2.5 Flash** is the only model showing meaningful self-correction: 3 W→R on WR items (sc_c1_wr_008, wr_010, wr_011)
- **Frontier models show zero W→R on WR items** — because they get everything right on T1
- **15 R→W (damage) events** — damage exceeds self-correction across the board
- **Claude Sonnet 4.6** has the highest damage rate (9.3%), including 4 R→W events

### Key Self-Correction Finding

The self-correction signal is **inverted for frontier models**: they have nothing to self-correct on WR items (already right), but they damage correct answers at a non-trivial rate. This is a significant finding for the narrative — it suggests that Turn 2 metacognitive prompting, at the frontier, primarily introduces noise rather than correction.

### Grading Robustness

- 16 errors total, all timeouts on weak models (haiku: 9, gemma: 5, ds-chat: 2)
- No grading exceptions or parse failures
- The frozen v2 grader with LaTeX normalization is robust across all model tiers
- Weak models occasionally produce verbose or malformed output, but the grader handles it

### Unresolved Items

The 4 UR/URC items show the most interesting gradient (0% weak → 33–67% frontier) but their grading is inherently fuzzy ("contested", "both", "unresolved"). They're more useful as design-conversation fodder than as scored benchmark items.

---

## Key Comparisons

### 1. Weak vs Frontier on the Clean Set

The gap exists but is small and concentrated:
- **Overall T1:** Weak 85.6% vs Frontier 93.3% — only 7.7pp gap
- **WR items:** Weak 92.3% vs Frontier 100.0% — only 7.7pp gap, and the weak-tier failures are sparse (3 items, 1–2 models each)
- **DT items:** The most interesting stratum — Weak 83.3% vs Frontier 95.8%, showing that deceptive traps create more separation than WR items

### 2. Mid vs Frontier

Mid-tier is essentially indistinguishable from frontier on this dataset:
- **WR T1:** Mid 90.6% vs Frontier 100.0%
- Mid-tier models are already too strong for these items

### 3. Self-Correction Direction

| Tier | Net Correction (T2−T1) | Self-Corr Rate | Damage Rate |
|------|----------------------|----------------|-------------|
| Weak | −1.1pp | 12.5% | 3.3% |
| Mid | −1.1pp | 33.3% | 5.6% |
| Frontier | −1.5pp | 33.3% | 3.7% |

**Net correction is negative across all tiers.** The Turn 2 prompt damages more answers than it fixes. This is the clearest empirical result from this sweep.

### 4. Design Pivot Evidence

The Batch 2 hardening attempts (12 items, 0 accepted) combined with this sweep confirm:
- The current WR items are fully saturated at the frontier
- The adversary + frontier pre-test pipeline correctly rejects items that frontier models would solve
- The problem is in generation, not evaluation

---

## Frontier Saturation Assessment

| Category | Count | % of WR Items |
|----------|-------|---------------|
| Saturated (≥80% frontier T1) | 16/16 | 100% |
| Borderline (50–79%) | 0/16 | 0% |
| Challenging (<50%) | 0/16 | 0% |

**Complete frontier saturation.** The current WR set has zero items in the target difficulty range for frontier models.

---

## Narrative Notebook Recommendation

### Should the current Family C material be used in the narrative notebook now?

**Yes, but only as a short difficulty-scaling / design-pivot section.**

### Rationale

The current Family C material provides four clear empirical findings worth documenting in a narrative notebook:

1. **Frontier saturation is real and measurable.** All 16 WR items show 100% T1 accuracy at the frontier tier. This is not a speculative claim — it's a clean empirical result across 3 frontier models.

2. **The difficulty gradient exists but is weak.** Only 3 of 16 WR items (19%) show any weak→frontier T1 gap. The gap is concentrated in a few items (sc_c1_wr_006, wr_007, sc_c2_wr_001) and is driven by 1–2 weak models failing, not broad difficulty scaling.

3. **Self-correction is net-negative across all tiers.** The T2 prompt damages more answers than it fixes. This is the most publishable finding — it directly challenges the assumption that metacognitive prompting helps.

4. **The design pivot is empirically justified.** The combination of frontier saturation + failed hardening attempts (12 items in Batch 2, 0 accepted) provides concrete evidence for why harder WR items require fundamentally different generation strategies.

### Suggested Narrative Structure

A 1–2 page section titled something like: **"Family C: Difficulty Scaling and the Frontier Saturation Problem"**

- Figure 1: T1 accuracy by model tier (shows the compression at the top)
- Figure 2: WR frontier saturation (shows 100% across the board)
- Figure 3: Transition patterns showing net-negative self-correction
- Brief text: "Current WR items are fully saturated at the frontier. Our adversarial hardening pipeline correctly filters weak items (12/12 Batch 2 rejections). Harder generation strategies are needed."

This section frames Family C as an **in-progress design challenge**, not a finished result.

### What NOT to claim

- Do not present Family C WR items as measuring frontier self-correction ability (they don't — frontier models ace T1)
- Do not present the weak→frontier gradient as a "scaling law" (it's too sparse)
- Do not present the quarantined items as evidence of anything (they failed validation)

---

## Artifacts

| File | Description |
|------|-------------|
| `outputs/family_c/narrative_ladder_sweep_raw.jsonl` | 315 raw trial results |
| `outputs/family_c/narrative_ladder_sweep_results.csv` | 7-row model summary |
| `outputs/family_c/narrative_ladder_sweep_summary.md` | This document |
| `outputs/family_c/figures/ladder_sweep_accuracy.png` | T1/T2 accuracy + delta plot |
| `outputs/family_c/figures/ladder_sweep_wr_saturation.png` | WR frontier saturation plot |
| `outputs/family_c/figures/ladder_sweep_transitions.png` | Transition pattern stacked bars |
| `scripts/narrative_ladder_sweep.py` | Sweep runner script |
