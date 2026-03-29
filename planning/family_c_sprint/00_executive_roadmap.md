# Family C Sprint: Executive Roadmap

**Status:** Decision-ready draft
**Date:** 2026-03-29
**Governing docs:** SOUL.md, recommendations memo, v1_architecture.md, scoring_plan.md

---

## 1. Executive Recommendation

**Build Family C next.** It is the highest-yield expansion for MetaJudge.

Family C (Self-Correction) opens the **cognitive control axis** of the benchmark.
The current benchmark surface (A: calibration, B: selective abstention) lives
entirely on the monitoring axis. Adding Family C transforms MetaJudge from a
monitoring-only suite into a monitoring-and-control benchmark, which is the
project's stated scientific identity (Nelson & Narens 1990, two-axis frame).

**Constraints on this recommendation:**
- Start with a compact seed set (30-40 items), not a large dataset
- Keep C1 (intrinsic) and C2 (evidence-assisted) as separate subfamilies from day one
- Launch as analysis-only; promote to official benchmark surface only after validation
- Do not modify existing A/B scoring or composite weights until C is validated

---

## 2. Why Family C Is High-Yield

### 2.1 Scientific value

Family C measures a cognitive operation that A and B cannot reach:
**the ability to use monitoring information to revise behavior.**

- Family A asks: "Does the model know when it's uncertain?"
- Family B asks: "Does the model act appropriately on uncertainty?"
- Family C asks: "Can the model detect and repair its own errors?"

This is the monitoring-to-control link that Nelson & Narens (1990) identify as
the core of metacognition. Without Family C, MetaJudge measures only half the
construct it claims to benchmark.

### 2.2 Discrimination value

Self-correction is likely to **reorder models** in ways calibration cannot.
The literature (Huang et al., ICLR 2024) shows that:
- Most models do not reliably self-correct without external evidence (C1 is hard)
- Models vary substantially in how they respond to weak contradictions (C2 discriminates)
- Some models damage correct answers under review pressure (overcorrection)

This means Family C should produce meaningful spread across the 5-model panel,
not just echo the A/B ranking.

### 2.3 Why C before D or E

| Factor | C (Self-Correction) | D (Grounding) | E (Control-Policy) |
|--------|---------------------|---------------|---------------------|
| Existing code scaffolding | Task, schema, scoring modules exist | Task + schema exist | Task + schema exist |
| Two-turn capability proven | SDK supports it cleanly | Single-turn | Two-turn, more complex |
| Literature grounding | Huang et al. directly applicable | Weaker for LLMs | Least studied |
| Expected model discrimination | High (revise/maintain split) | Medium | Unknown |
| Implementation complexity | Moderate | Moderate | High |
| Connection to A/B | Direct (confidence → revision) | Indirect | Indirect |

Family C builds most directly on the A/B foundation, requires the least
speculative design, and has the strongest literature support for what "good"
and "bad" model behavior should look like.

### 2.4 Pressure-testing the hypothesis

**Where the case is strong:**
- Family C measures a distinct cognitive operation
- Existing codebase has substantial scaffolding ready
- SDK multi-turn pattern is verified and clean
- The maintain/revise/unresolved triad is well-defined

**Where uncertainty remains:**
- We don't yet know whether C1 (intrinsic) will discriminate or whether all
  models simply fail. If all models score ~0 on C1, its benchmark value is low.
  *Mitigation: seed-set evaluation will answer this before promotion.*
- Damage rate may be very low across all models, making the damage penalty
  largely decorative. *Mitigation: include right-to-right robustness items.*
- Two-turn cost is ~2x single-turn. Budget impact must be managed.
  *Mitigation: 30-40 items, caching, n_jobs=8.*

---

## 3. Benchmark Claim

Family C supports the following defensible claim:

> **"MetaJudge Family C measures whether a language model can detect errors in
> its own prior output and revise appropriately, without overcorrecting correct
> answers or blindly deferring to weak challenges."**

This claim is:
- Behavioral (measured by answer changes and confidence shifts, not self-report)
- Conservative (does not claim models "understand" their errors)
- Testable (operationalized via the maintain/revise/unresolved triad)
- Distinct from A/B (measures control, not just monitoring)

---

## 4. Recommended Task Architecture

### 4.1 Subfamily structure

```
Family C
├── C1: Intrinsic Self-Correction
│   Turn 1: Answer + confidence
│   Turn 2: Generic review prompt ("Review your answer...")
│   No new evidence provided
│
└── C2: Evidence-Assisted Correction
    Turn 1: Answer + confidence
    Turn 2: Weak contradiction or hint provided
    Evidence is suggestive, not conclusive
```

C1 and C2 must be **separate tasks** from day one. This is non-negotiable
per Huang et al. — mixing them conflates two different cognitive operations.

### 4.2 Module layout

```
metajudge/
├── scoring/
│   └── self_correction_metrics.py  ← EXISTS, needs enhancement
├── schemas/
│   └── response_schemas.py         ← EXISTS, SelfCorrectionResponse defined
├── tasks/
│   └── self_correction.py          ← EXISTS, needs C1/C2 split
config/
└── benchmark_config.yaml           ← EXISTS, C1/C2 weights defined (0.10/0.15)
data/
└── family_c/
    ├── family_c_seed_v1.json       ← NEW: seed dataset
    └── clean_subset_manifest.json  ← NEW: clean-set tracking
notebooks/
├── metajudge_benchmark.ipynb       ← UPDATE when promoted
└── family_c_analysis.ipynb         ← NEW: analysis-only notebook
```

### 4.3 Relationship to existing benchmark

**Near-term (this sprint):**
- Family C runs in a separate analysis notebook
- Produces audit CSVs and diagnostic outputs
- Does NOT modify the official `%choose` benchmark score
- Bridge metrics extended to include C-axis coupling analysis

**Medium-term (after validation):**
- Family C promoted into composite score with pre-defined weights (C1: 0.10, C2: 0.15)
- Official benchmark notebook updated
- New `%choose` task wraps A + B + C

**Long-term:**
- Families D and E added, full composite realized
- Bridge analysis spans all five families

---

## 5. Phased Implementation Plan

### Phase 1: Seed Set (this sprint)
- Build 30-40 gold items across C1 and C2
- Run 5-model panel
- Audit results, quarantine suspects
- Decision gate: does Family C discriminate?

### Phase 2: Expansion (next sprint if Phase 1 passes)
- Adversarial expansion to 60-80 items
- Disagreement mining from Phase 1 results
- Clean-set promotion
- Decision gate: is scoring stable?

### Phase 3: Promotion (following sprint if Phase 2 passes)
- Integrate into official benchmark notebook
- Update composite score
- Publish alongside A/B results

---

## 6. Sprint Plan File Index

| File | Contents |
|------|----------|
| `01_scientific_constraints.md` | Non-negotiable design principles from literature |
| `02_item_design.md` | Item taxonomy, strata, seed-set plan |
| `03_scoring_blueprint.md` | Scoring design, damage penalties, confidence |
| `04_task_architecture.md` | SDK patterns, module layout, notebook plan |
| `05_validation_plan.md` | 5-model evaluation, statistics, promotion criteria |
| `06_risks_and_gates.md` | Failure modes, risks, decision gates |
| `07_sprint_checklist.md` | Step-by-step execution plan |

---

## 7. Open Questions for User Decision

1. **Seed-set size:** Recommend 30-40 items. Is this the right scale, or should we start smaller (20)?
2. **C1/C2 ratio:** Recommend roughly equal (15-20 each). Should C2 be larger given higher expected discrimination?
3. **Analysis-only vs. direct promotion:** Recommend analysis-only first. Is there pressure to promote immediately?
4. **Budget allocation:** Two-turn items cost ~2x. Acceptable within $50/day limit?
5. **Item sourcing:** Should seed items overlap with A/B item pool (same questions, different task) or be entirely new questions?
