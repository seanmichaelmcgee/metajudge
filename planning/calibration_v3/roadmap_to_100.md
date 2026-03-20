# Roadmap: 100-Item Calibration Dataset → First Submission

**Date:** March 19, 2026  
**Status:** Active — Phase 2 stress testing complete, expansion in progress  
**Governs:** All work from now through first Kaggle submission

---

## Current Inventory

| Source | Count | Status |
|:-------|------:|:-------|
| V2 existing dataset (calibration.csv) | 100 | Frozen, in production notebook |
| V4 Batch 1 survivors (Tiers 1-5) | 19 | Tested Sonnet + Flash; awaiting Pro + DeepSeek |
| **Total available** | **119** | |

The existing 100 items scored too easy in the 5-model sweep (SOUL.md §History): Sonnet 95/100, DeepSeek 93/100. Only 1/5 success criteria met (C4). The V4 items are designed to fix this — they target the deceptive/adversarial buckets specifically.

---

## Target: 100-Item Hard Calibration Set

**Goal:** Replace ceiling items in the existing 100 with V4 survivors + new batches until we have a 100-item set that meets ≥4/5 success criteria.

**Why 100 (not 300):** The dataset_construction_plan (§6) specifies 100 items for V1. The 250-350 figure (§7) is the candidate harvest pool, not the final set. SOUL.md confirms "100 V2 items" in Cell 3. The Kaggle rubric rewards quality over quantity. 100 items × 5 models = 500 calls per sweep, fitting the $50/day budget.

**Milestone sequence:**

| # | Milestone | Items | Gate |
|:--|:----------|------:|:-----|
| M1 | Complete 4-model matrix on 19 survivors | 19 | Confirm discrimination across models |
| M2 | Run expansion Batch 2 (~75 new candidates) | ~15 new survivors | Merge with M1 survivors |
| M3 | Run expansion Batch 3 (~75 new candidates) | ~15 new survivors | Merge |
| M4 | Integrate best ~30-50 V4 items into the 100-item set | 100 | Replace ceiling items |
| M5 | Full 5-model Kaggle sweep | 100 | ≥4/5 success criteria |
| M6 | First Kaggle submission | 100 | Submit benchmark + writeup draft |

---

## Expansion Strategy: Batches of ~75

Each batch follows the established pipeline:

1. **Generate** ~75 items via 2-agent architecture (Agent A + Agent B)
2. **Verify** code items by execution (if any)
3. **Stress test** against Claude Sonnet (primary model)
4. **Escalate** Tier 6 items against Gemini Flash
5. **Classify** into final tiers, keep Tiers 1-5
6. **Expected yield:** ~20% (15 survivors per batch, based on Batch 1 empirical rate)

### Mechanism allocation per batch (informed by Batch 1 yields)

| Mechanism | Batch 1 Yield | Batch 2+ Allocation | Rationale |
|:----------|:--------------|:-------------------:|:----------|
| AmbiguityMetacognition | 80% (4/5) | 10-12 items | Highest yield, double down |
| RLHF | 40% (4/10) | 10-12 items | High yield, large design space |
| IOED | 43% (3/7) | 10-12 items | High yield, proven mechanism |
| Anchoring | 50% (2/4) | 8-10 items | Good yield but small sample |
| Prototype | 23% (3/13) | 8-10 items | Moderate yield, distinct failures |
| Compositional | 10% (1/10) | 5-8 items | Low yield but keep some |
| ModifiedCRT | 6% (1/17) | 5-8 items | Low yield, reduce allocation |
| CodeExecution | 5% (1/20) | 3-5 items | Nearly zero yield vs frontier |
| ConditionalTemporal | 0% (0/5) | 0-2 items | Eliminate unless redesigned |

### Items needed to reach target

- Current survivors: 19
- Target new deceptive/adversarial items: ~30-50 (to replace ceiling items)
- At 20% yield per batch of 75: need ~2-3 more batches
- Conservative plan: 3 batches × 75 = 225 candidates → ~45 survivors
- Combined with 19 existing: ~64 V4 survivors to draw from

---

## Immediate Tasks (This Session)

1. ✅ Sonnet stress test complete (91 items)
2. ✅ Flash escalation complete (75 Tier 6 items)
3. **Next:** Run 19 survivors through Gemini Pro (same API key)
4. **Next:** Run 19 survivors through DeepSeek V3.1 (via OpenRouter free tier)
5. **Next:** Produce 4-model discrimination matrix
6. **Next:** Generate Batch 2 (~75 items, high-yield mechanisms)

---

## Future Plans (Pinned, Not Active)

These are codified for reference but NOT in scope until after first submission.

### Post-Submission Phase 1: Workflow Documentation
- Document the generation → stress-test → escalation pipeline as a reproducible workflow
- Identify highest-yield avenues with statistical backing
- Confirm robust scoring on the full 5-model panel

### Post-Submission Phase 2: Second Metacognition Domain
- Family B (Selective Abstention / Verification) is next per SOUL.md
- Develop a parallel item set for abstention behavior
- Compare calibration and abstention as complementary metacognitive axes

### Post-Submission Phase 3: Scale to 300
- dataset_construction_plan §7 targets 250-350 candidate harvest pool
- At that scale, multiple difficulty tiers and domain coverage become meaningful
- Consider expanding to 200-300 final items for statistical power
- This is the "long-term benchmark" vs. the "competition submission"

### Competition Timeline
- **Deadline:** April 16, 2026 (28 days from now)
- **First submission target:** After M6 (~1-2 weeks)
- **Iteration budget:** 2-3 submission iterations before deadline

---

## Files Referenced

| File | Role |
|:-----|:-----|
| `SOUL.md` | Governing principles, success criteria, model panel |
| `planning/dataset_construction_plan.md` | 100-item composition, 250-350 harvest target |
| `planning/calibration_v3/adversarial_search_directive.md` | V4 mechanism definitions, contamination strategy |
| `planning/calibration_v3/risk_assessment.md` | Yield thresholds, fallback tiers |
| `planning/calibration_v3/feedback_loop_spec.md` | Pipeline calibration schema, generator revision protocol |
| `planning/calibration_v3/generator_agent_prompts.md` | Agent A + B prompt templates |
| `data/phase2_final_results.json` | All 91 items with Sonnet + Flash results |
| `data/escalation_progress.json` | Flash escalation raw data |
