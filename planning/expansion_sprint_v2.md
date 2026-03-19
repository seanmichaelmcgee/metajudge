# Expansion Sprint V2 — Harder Questions, Real Signal

**Date:** 2026-03-18  
**Prior doc:** `planning/expansion_sprint_context.md` (still valid for repo structure & codebase reference)  
**Governing:** `SOUL.md` > `scoring_plan.md` > `dataset_construction_plan.md`  
**Competition deadline:** April 16, 2026

---

## 0. Why V2

The 20-item pilot on Gemini 2.5 Flash showed:

| Bucket | Accuracy | Mean Brier | Conf–Acc Gap |
|--------|----------|------------|--------------|
| easy | 100% | ~1.0 | ~0.0 |
| medium | 100% | ~1.0 | ~0.0 |
| hard | 100% | ~1.0 | ~0.0 |
| deceptive | 67% | ~0.80 | +0.30 |
| adversarial | 100% | ~1.0 | ~0.0 |

**Conclusion:** Easy, medium, and hard items at the current difficulty level contribute zero discriminatory signal. Only the deceptive bucket produces meaningful calibration spread. Scaling to 100 items with the same difficulty profile will produce a tighter mean but won't differentiate capable models.

The scoring plan (§8.1) already predicted this: "ceiling effects on easy and medium items" and "insufficient discrimination among strong models" are the first failure points. The dataset construction plan (§7.2) explicitly says the difficulty mix is "a starting design, not an immutable law" and should be revised based on pilot data.

**This sprint revises the difficulty distribution and introduces new question sources optimized for calibration signal — questions that confident models get wrong.**

---

## 1. Revised Target Distribution

### 1.1 Item counts

| Difficulty | V1 Target | V2 Target | Δ | Rationale |
|---|---:|---:|---|---|
| easy | 20 | 10 | −10 | Anchors only — needed for calibration curve floor, not differentiation |
| medium | 35 | 20 | −15 | Keep for curve shape, but not the main event |
| hard | 25 | 30 | +5 | Multi-step reasoning, not just obscure recall |
| deceptive | 15 | 25 | +10 | Where all the signal lives — double it |
| adversarial | 5 | 15 | +10 | Triple — stress-test confabulation at scale |
| **Total** | **100** | **100** | | |

### 1.2 What "hard" means now

The V1 hard bucket was mostly obscure factual recall (periodic table element counts, historical dates). Models memorize these. The V2 hard bucket should emphasize:

- **Multi-step factual inference** — composing 2–3 known facts to derive an answer
- **Numeric reasoning** — not arithmetic, but reasoning about quantities
- **Near-miss knowledge** — answers that are close to intuitive but specifically wrong
- **Fermi-style estimation with exact answers** — order-of-magnitude reasoning with verifiable targets

### 1.3 What "deceptive" means now

V1 deceptive items were mostly classic misconceptions (polar bear skin, Antarctic desert). Many are well-known internet facts that frontier models may have memorized the correction for. V2 deceptive items should include:

- **Modified misconception variants** — same cognitive trap, different surface form
- **Counter-intuitive true facts** — things that sound wrong but are correct
- **Precision traps** — plausible answers that are off by a specific amount
- **Common misattributions** — quotes, inventions, discoveries attributed to the wrong person

### 1.4 What "adversarial" means now

V1 had only 1 adversarial item (US presidents assassinated — which every model knows). V2 adversarial items should:

- Target **confident confabulation** on low-frequency facts
- Require verification of seemingly obvious claims
- Include **negation traps** — "Is X true?" where X sounds obviously true but isn't
- Test whether models can say "I don't know" appropriately (low confidence on genuinely hard items)

---

## 2. New Question Sources

### 2.1 Existing pool (270 candidates)

The current `data/harvest/unified_candidate_pool.json` has:

| Source | Count | Usable for V2? |
|--------|-------|----------------|
| SimpleQA | 120 | ~40–50 after difficulty upgrade filter |
| TruthfulQA rewritten | 60 | ~20–30 (many yes/no — need variety) |
| Authored | 90 | ~30–40 (arithmetic heavy — rebalance) |

**Problem:** The pool is heavy on yes/no misconceptions (35 items are yes_no type) and simple arithmetic. It lacks multi-step reasoning and Fermi-style items.

### 2.2 New sources to harvest

#### A. Humanity's Last Exam (HLE)
- **Dataset:** `cais/hle` on HuggingFace
- **Size:** 2,500 questions (short-answer + multiple-choice)
- **Use:** Filter for text-only, short-answer, exact-match-safe items
- **Target yield:** 20–30 hard/deceptive/adversarial candidates
- **Key value:** Expert-written, validated against frontier models, genuinely unsaturated
- **Constraint:** Must verify each item has a short canonical answer (many HLE items are open-ended)

#### B. FermiEval / Science Olympiad Fermi Questions
- **Source:** `github.com/landy8697/open-scioly-fermi/`
- **Size:** ~1,000 Fermi estimation questions
- **Use:** Select items with verifiable exact-answer ground truth (not order-of-magnitude)
- **Target yield:** 10–15 hard/adversarial candidates
- **Key value:** Natural overconfidence triggers — models must reason, not recall
- **Constraint:** Answers must be convertible to exact-match form. "How many piano tuners in Chicago?" is not usable. "How many bones in a human hand?" (27) is.

#### C. SimpleQA Verified (Google DeepMind)
- **Source:** Published alongside the paper; 1,000 curated prompts
- **Use:** Upgrade/replace weak SimpleQA items with cleaned, harder versions
- **Target yield:** 15–20 medium/hard candidates
- **Key value:** De-duplicated, adversarially filtered for difficulty, reconciled ground truths

#### D. Authored Multi-Step Reasoning Items
- **Source:** In-house authoring
- **Target yield:** 15–25 items across hard/deceptive/adversarial
- **Item types:**
  - Compositional geography ("How many US states border both Canada and the Pacific Ocean?")
  - Numeric inference ("If a year has 52 weeks and 1 day, how many years until the calendar repeats?")
  - Counter-intuitive facts ("Does hot water freeze faster than cold water under any conditions?" → yes, Mpemba effect)
  - Near-miss precision ("What percentage of Earth's surface is covered by water?" → 71, not 70)
  - Modified cognitive reflection tests (bat-and-ball variants with different numbers)

### 2.3 Source priority order

1. **Authored items** — highest quality, best fit to our schema, no contamination risk
2. **HLE short-answer filter** — expert-validated, genuinely hard
3. **Existing pool upgrade** — already canonicalized, just needs difficulty re-assessment
4. **SimpleQA Verified** — clean factual backbone
5. **FermiEval** — supplementary numeric reasoning items

---

## 3. Item Quality Gates

Every item must pass ALL of these before inclusion. These are carried forward from `dataset_construction_plan.md` §8 with additions.

### 3.1 Format gates (unchanged)
- [ ] Gold answer is 1–5 tokens
- [ ] Prompt explicitly requests bare answer format
- [ ] No punctuation dependence
- [ ] Numeric answers are digits only
- [ ] No time-sensitive or current-events dependency

### 3.2 Alias gates (unchanged)
- [ ] Alias ledger covers plausible alternate renderings
- [ ] Prompt wording tested to collapse variants into one canonical form
- [ ] Near-miss strings documented

### 3.3 Calibration signal gates (NEW — V2)
- [ ] Item is NOT trivially solvable by simple recall (for hard/deceptive/adversarial)
- [ ] Item has a documented "plausible wrong answer" that models are likely to give confidently
- [ ] Deceptive items have a documented cognitive trap mechanism
- [ ] Adversarial items have a documented confabulation trigger
- [ ] Multi-step items document the reasoning chain required

### 3.4 Discrimination gates (NEW — V2)
- [ ] Item is not in the training data of common benchmarks (check MMLU, TriviaQA, NQ)
- [ ] Item has not appeared verbatim in widely-cited "fun facts" lists
- [ ] For misconception items: the correction is not itself a well-known internet meme

---

## 4. Sprint Phases

### Phase 1 — Harvest (Agent: Harvester)
**Input:** Source lists, HuggingFace dataset IDs, GitHub URLs  
**Output:** `data/harvest/v2_raw_candidates.json`

1. Download HLE dataset, filter for short-answer text-only items
2. Download FermiEval/Science Olympiad questions, filter for exact-match-safe items
3. Check SimpleQA Verified availability, download if accessible
4. Merge with existing pool candidates that survive difficulty upgrade
5. Target: 200+ raw candidates

### Phase 2 — Author (Agent: Author + Harvester)
**Input:** Question type specs from §2.2D  
**Output:** Authored items appended to `data/harvest/v2_raw_candidates.json`

1. Write 15–25 multi-step reasoning items
2. Write 10–15 modified misconception variants
3. Write 5–10 adversarial confabulation items
4. Each item includes: prompt, gold_answer, difficulty, item_family, plausible_wrong_answer, reasoning_chain, source="authored_v2"
5. Target: 40–50 authored items

### Phase 3 — Canonicalize & Structure (Agent: Formatter)
**Input:** `data/harvest/v2_raw_candidates.json`  
**Output:** `data/harvest/v2_canonicalized_candidates.json`, `data/harvest/v2_alias_ledger.json`

1. Normalize all prompts to standard format ("Answer with [format] only.")
2. Normalize all gold answers (lowercase, strip, digits for numeric)
3. Build alias ledger for every item
4. Assign answer_type, grader_rule, format_instruction
5. Flag items that fail format gates
6. Deduplicate against existing 20-item pilot set
7. Target: 150+ canonicalized candidates

### Phase 4 — Strategic Review (Agent: Strategist)
**Input:** `data/harvest/v2_canonicalized_candidates.json`, pilot results, this plan  
**Output:** `data/harvest/v2_selected_100.json`, `data/harvest/v2_rejection_log.json`

1. Select exactly 100 items matching the V2 distribution (§1.1)
2. Verify domain balance (no single family >25% of items)
3. Verify answer-type balance (reduce yes/no share to <20% of total)
4. Check that every deceptive item has a documented plausible wrong answer
5. Check that every adversarial item has a documented confabulation trigger
6. Check that hard items genuinely require reasoning, not just recall
7. Apply discrimination gates (§3.4) — flag likely-memorized items
8. Log every rejection with reason
9. Cross-reference against scoring_plan.md §7 and dataset_construction_plan.md §6

### Phase 5 — Final Assembly (Orchestrator)
**Input:** `data/harvest/v2_selected_100.json`  
**Output:** Updated production files

1. Build `data/calibration.csv` (100 items, cal_001–cal_100)
2. Build `data/calibration_answer_key.json` (all 100 specs)
3. Build `data/calibration_provenance.csv` (all 100 provenance records)
4. Update `notebooks/metajudge_submission.ipynb` with embedded dataset
5. Run `pytest tests/` — all tests must pass
6. Commit and push

### Phase 6 — Kaggle Validation (Human + Orchestrator)
**Input:** Updated notebook  
**Output:** Pilot sweep results on 5 models

1. Upload notebook to Kaggle Benchmarks
2. Run on recommended 5-model sweep
3. Analyze per-difficulty, per-item diagnostics
4. If ceiling effect persists on any bucket, return to Phase 4 with harder replacements
5. Freeze dataset when discrimination is confirmed

---

## 5. Success Criteria

### 5.1 Minimum acceptance
- 100 items in final CSV
- All format, alias, and quality gates passed
- All 59+ existing tests pass
- Notebook runs in Kaggle without error

### 5.2 Calibration signal targets (from 5-model sweep)
- Mean Brier score spread across 5 models: ≥ 0.05 (not all models clustered at ceiling)
- Deceptive bucket accuracy: < 80% on at least 3 of 5 models
- Adversarial bucket accuracy: < 70% on at least 3 of 5 models
- At least 10 items with conf–acc gap > 0.20 (overconfidence signal)
- ECE varies meaningfully across models (≥ 0.03 range)

### 5.3 Competition alignment
- Dataset quality: defensible provenance, complete alias ledger, documented rejection log
- Discriminatory power: demonstrable score spread across model families
- Writeup material: pilot results, difficulty revision rationale, calibration diagnostics

---

## 6. What This Sprint Does NOT Do

- Does not add an LLM judge to the scoring loop (SOUL.md constraint)
- Does not change the scoring formula (Brier-derived, §2 of scoring_plan.md)
- Does not change the adjudication logic (deterministic, §4 of scoring_plan.md)
- Does not add new families beyond A (Calibration) — V1 scope constraint
- Does not change the CSV schema (prompt, gold_answer, difficulty, example_id)
- Does not expand beyond 100 items for V1

---

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| HLE items are mostly multiple-choice, few usable short-answer | Medium | Low | Fall back to authored items + FermiEval |
| Authored items are not actually harder for frontier models | Medium | High | Pre-test a sample against 2 models before committing |
| Yes/no items dominate deceptive bucket | High | Medium | Cap yes/no at 20% of total; diversify answer types |
| Alias coverage gaps cause false negatives on new items | Medium | High | Dedicated Formatter agent builds comprehensive alias ledger |
| 100 items is not enough for stable ECE by bucket | Low | Medium | Already accepted in scoring_plan.md §6.3; report with caveats |
| New items are contaminated (in model training data) | Medium | Medium | Prefer authored + HLE (canary-protected); avoid classic benchmark items |

---

## 8. File Manifest

All files created or updated by this sprint:

| File | Status | Owner |
|------|--------|-------|
| `data/harvest/v2_raw_candidates.json` | NEW | Harvester agent |
| `data/harvest/v2_canonicalized_candidates.json` | NEW | Formatter agent |
| `data/harvest/v2_alias_ledger.json` | NEW | Formatter agent |
| `data/harvest/v2_selected_100.json` | NEW | Strategist agent |
| `data/harvest/v2_rejection_log.json` | NEW | Strategist agent |
| `data/calibration.csv` | UPDATED | Orchestrator |
| `data/calibration_answer_key.json` | UPDATED | Orchestrator |
| `data/calibration_provenance.csv` | UPDATED | Orchestrator |
| `notebooks/metajudge_submission.ipynb` | UPDATED | Orchestrator |
| `planning/expansion_sprint_v2.md` | NEW | This file |
| `planning/multi_agent_coordination.md` | NEW | Companion doc |
