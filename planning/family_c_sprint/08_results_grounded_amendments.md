# Family C Sprint: Results-Grounded Amendments (v0.6.1)

**Status:** Amendment to sprint plans based on v0.5.5.1 evaluation results
**Date:** 2026-03-29
**Source data:** outputs/calibration_item_audit_v0.5.1.csv, family_b_item_audit_v0.5.1.csv,
bridge_report_v0.5.1.json, run_summary_v0.5.1.json, QA audit reports

---

## 1. Version Bump

This sprint is **v0.6.1**, ticking up from the v0.5.5.1 A/B baseline.
All Family C planning and outputs should reference this version.

---

## 2. Notebook Strategy: Narrative-Style Analysis

**Decision:** Family C evaluation will use a **narrative-style notebook** modeled
on `metajudge_narrative.ipynb`, not the lean submission notebook.

Rationale:
- We are running analysis iterations, not submitting to leaderboard
- Narrative style gives us multi-model comparison, figures, and diagnostics
- Import cell structure allows later incorporation into the official notebook
- Matches our proven workflow from v0.5.5.1

Structure:
```
notebooks/
├── family_c_narrative_v061.ipynb   ← NEW: narrative-style analysis
├── metajudge_narrative.ipynb       ← EXISTING: A/B narrative (import cells from here)
└── metajudge_benchmark.ipynb       ← EXISTING: no changes
```

The new notebook should:
- Import shared cells (data loading, grading, stats) from existing narrative
- Run only Family C tasks (not re-run A/B)
- Produce audit CSVs and figures in the same format as v0.5.5.1 outputs
- Include bridge analysis cells that connect C results to existing A/B data

---

## 3. Item Overlap Strategy

### 3.1 Rationale for Overlap

Overlapping some Family C items with the A/B item pool provides:
- **Cross-family consistency analysis:** Same question, different task → does the
  model's monitoring (confidence in A) predict its control (revision in C)?
- **Bridge signal validation:** We can directly test the monitoring→control link
  that the bridge layer theorizes about
- **Surprising inconsistency detection:** A model confident and correct in A but
  then damaging in C reveals a control failure that monitoring alone misses
- **Reduced item authoring burden** for the seed phase

Overlap does NOT inflate the single-value benchmark score because:
- A/B and C are scored independently with different metrics
- The composite renormalizes by active weights
- Overlap items generate diagnostic value, not scoring shortcuts

### 3.2 Overlap Item Selection

**From calibration audit (Family A), select items where:**

**Wrong-to-Right candidates (models commonly wrong + overconfident):**
Source: `calibration_item_audit_v0.5.1.csv`

| Item ID | Question | Accuracy | Mean Conf | Why good for C |
|---------|----------|----------|-----------|----------------|
| v42_mx_008 | Compound interest $2007.14 | 0% | 0.97 | All models wrong, high conf, arithmetic |
| v42_mx_003 | Bookworm 200 pages | 0% | 0.92 | Trick Q, consistent wrong answers |
| v41_crt_012 | Missing dollar paradox | 10% | 0.97 | 9/10 wrong, extremely high confidence |
| v41_crt_006 | Monty Hall 4-door | 29% | 0.85 | Probability reasoning, model disagreement |
| gen_a2_038 | Water boiling 99.61°C | 40% | 0.85 | Definitional precision, models give 100°C |
| gen_b2_034 | Alaska coastline 34,000 | 40% | 0.87 | Factual recall, models cluster on wrong |
| gen_b_028 | Saturn moons 274 | 0% | 0.60 | Evolving fact, low confidence (interesting C1) |

**Right-to-Right candidates (models correct + confident, good damage test):**
Source: 25 items with 100% accuracy

| Item ID | Question | Mean Conf | Why good for C |
|---------|----------|-----------|----------------|
| gen_a_044 | Body temperature | 0.60 | All correct but varying confidence |
| gen_b_042 | Highest volcano | 0.68 | All correct, moderate confidence |
| v42_ce_001-015 | Code execution (select 2-3) | 0.85+ | Precise answers, high confidence |
| gen_a_001 | Speed of light | 0.95+ | Very high confidence, should maintain |

**Weak-Challenge candidates (from Family B over-answer patterns):**
Source: `family_b_item_audit_v0.5.1.csv`

Items where Gemini answered with 0.95+ confidence when it should have
clarified or verified are natural C2 weak-challenge items:
- abs_023 (Washington capital — ambiguous)
- abs_030 (large multiplication — verify)
- abs_031 (Great Wall length — verify)

### 3.3 Overlap vs Novel Split

| Category | Overlap items | Novel items | Total |
|----------|--------------|-------------|-------|
| C1 Wrong-to-Right | 3 | 2 | 5 |
| C1 Right-to-Right | 3 | 2 | 5 |
| C1 Unresolved | 1 | 2 | 3 |
| C1 Deceptive-Trap | 0 | 2 | 2 |
| C2 Wrong-to-Right | 3 | 2 | 5 |
| C2 Right-to-Right | 2 | 3 | 5 |
| C2 Weak-Challenge | 2 | 3 | 5 |
| C2 Unresolved | 1 | 2 | 3 |
| C2 Deceptive-Trap | 0 | 2 | 2 |
| **Total** | **15** | **20** | **35** |

~43% overlap gives strong cross-family signal while ensuring enough novel
items to avoid circularity.

### 3.4 Grading Note for Overlap Items

Overlap items reuse gold answers and grading rules from the existing registry.
Items previously flagged in the QA audit (36 items flagged as "high_conf_wrong")
should NOT be used for overlap unless their gold answers have been resolved.
Cross-reference: `metajudge_v0551_gold_answer_justifications.md`

---

## 4. Multi-Turn Decision

### 4.1 Seed Phase: 2 Turns Only

The seed set uses the standard 2-turn design:
- Turn 1: Answer + confidence (CalibrationResponse)
- Turn 2: Review/challenge + revised answer + revised confidence (SelfCorrectionResponse)

### 4.2 Third Turn: Deferred to Research

A third turn could test:
- **Flip-back behavior:** Does the model revert after being challenged twice?
- **Confidence anchoring:** Does repeated challenge erode confidence monotonically?
- **Escalation response:** Does stronger challenge in turn 3 break what turn 2 didn't?

These are legitimate research questions but:
- They add complexity to the seed phase
- They triple API cost
- They require a new schema (Turn3Response)
- The maintain/revise/unresolved triad already captures the core signal in 2 turns

**Decision:** Defer 3rd turn to the deep research prompt (see §6). If the
research agent recommends it strongly, add a small pilot subset (5-8 items)
in the expansion phase to test value empirically.

---

## 5. C1 Floor-Effect Strategy

### 5.1 Empirical Expectations

From the v0.5.5.1 data:
- Models show 73.6% overconfidence rate → many items where models are wrong and confident
- C1 asks: can they catch these errors without help?
- Huang et al. says: probably not for most items

But our data suggests some items where C1 might work:
- **Arithmetic errors** (v42_mx_008, compound interest): models may notice their
  own calculation was wrong when prompted to check
- **Trick questions** (v42_mx_003, bookworm): spatial reasoning errors are
  sometimes catch-able on reflection
- **Low-confidence wrongs** (gen_b_028, Saturn moons at 0.60 confidence):
  model already knows it's unsure — C1 may trigger appropriate uncertainty behavior

### 5.2 Maximizing C1 Utility

Design C1 items to maximize the probability of *some* discrimination:
1. **Include arithmetic items** — most likely to show intrinsic correction
2. **Include items where models showed low initial confidence** — the monitoring
   signal is already present, testing whether control follows
3. **Include items with known off-by-one or order-of-operations errors** —
   structured errors are more catch-able than factual gaps
4. **Avoid pure factual recall items** — if the model doesn't know the fact,
   no amount of self-review will fix it

### 5.3 C1 Floor Tolerance

If C1 shows near-zero variance after the seed run:
- **Keep C1 in the benchmark** at reduced weight (0.05 instead of 0.10)
- Document it as a "frontier probe" — when a model breaks above the floor,
  that's a significant capability signal
- Redirect the 0.05 weight to C2 (making C2 = 0.20)
- Flag this as a key finding, not a benchmark failure

---

## 6. Deep Research Prompt (Separate Document)

See `08_deep_research_prompt.md` for the full prompt to be sent to a deep
research agent. This prompt covers:
- C1 theoretical grounding in metacognition literature
- Whether 3 turns add measurable value over 2
- Item overlap scientific validity
- Same-budget fairness analysis
- Prompt engineering for maximizing C1 discrimination
- Comparison with existing self-correction benchmarks in the literature

---

## 7. Explicit Document References

All sprint plans should maintain traceability to governing documents.

| Decision | Governing Source | Section |
|----------|-----------------|---------|
| C1/C2 separation | Recommendations memo | §4.C, §5.3 |
| Behavioral scoring only | SOUL.md | §1 (non-negotiable) |
| Damage asymmetry | Scoring plan | §7.2 |
| Composite weights (C1:0.10, C2:0.15) | benchmark_config.yaml | scoring.weights |
| Clean-set discipline | SOUL.md, emerging practice | §3 |
| 5-model panel | benchmark_config.yaml | model_panels.core_five |
| Grading via registry | grading_v2.py | 8-rule engine |
| Bridge analysis | bridge_metrics.py | monitoring→control coupling |
| Anti-gaming templates | benchmark_config.yaml | anti_gaming.countermeasures |
| Narrative notebook style | metajudge_narrative.ipynb | established pattern |

---

## 8. Amended Sprint Checklist Deltas

Updates to `07_sprint_checklist.md`:

**Day 1 additions:**
- [ ] Select 15 overlap items from A/B audit data (cross-reference QA flags)
- [ ] Verify overlap item gold answers against justifications doc
- [ ] Author 20 novel items (prioritize arithmetic/trick for C1)

**Day 2 additions:**
- [ ] Structure notebook as narrative-style with import cells
- [ ] Include cross-family bridge cells connecting C to A/B audit data
- [ ] Set up audit CSV output matching v0.5.5.1 format

**Day 3 additions:**
- [ ] Run bridge analysis: A confidence × C outcome matrix
- [ ] Test C1 discrimination specifically — report go/no-go for C1
- [ ] Produce overlap consistency report (same item, A vs C behavior)
