# MetaJudge-AGI

**A behavioral benchmark for metacognitive monitoring and control in frontier language models.**

Built for the [Kaggle Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi) hackathon (Metacognition track).

---

## What This Measures

MetaJudge evaluates whether language models can **track the reliability of their own outputs** and **act appropriately on that information**. This maps to the two-process model of metacognition established by Nelson & Narens (1990):

- **Monitoring** — evaluating the state of cognition. *"How am I doing?"*
- **Control** — using that judgment to change behavior. *"What should I do about it?"*

The benchmark scores metacognition by the consequences of self-monitoring on task behavior, not by what the model says about itself.

### Four Tasks

| Task | Process | Items | What It Tests |
|------|---------|-------|---------------|
| **Confidence Calibration** | Monitoring | 105 | Does stated confidence track actual accuracy? |
| **Selective Abstention** | Control | 72 | Does the model choose the right epistemic action under uncertainty? |
| **Intrinsic Self-Correction (C1)** | Control | 28 | Can the model detect and repair its own errors without external evidence? |
| **Evidence-Assisted Self-Correction (C2)** | Control | 23 | Does external evidence help or damage the model's performance? |

Each task runs as an independent Kaggle Benchmark notebook returning one anchor-normalized score. The platform averages the four scores into the leaderboard **MetaScore**.

### Scoring

- **Calibration:** Brier rule (strictly proper). 8-rule deterministic grading engine — no LLM judge.
- **Abstention:** UWAA (Utility-Weighted Action Accuracy) with 5×4 payoff matrix. Four actions: answer, clarify, verify, abstain.
- **Self-Correction (C1/C2):** Transition-based scoring. Six outcomes from correction_gain to damage. Asymmetric penalties — damage costs more than correction gains.
- **Composite:** Equal-weight average, justified by Dawes (1979) and Davis-Stober (2011).

---

## Repository Structure

```
notebooks/                              # v6.1 Kaggle Benchmark task notebooks
  metajudge_calibration.ipynb           #   Monitoring — anchor-normalized Brier
  metajudge_abstention.ipynb            #   Control — dual-run, anchor-normalized UWAA
  metajudge_sc_c1.ipynb                 #   Control — dual-run, intrinsic self-correction
  metajudge_sc_c2.ipynb                 #   Control — dual-run, evidence-assisted

metajudge/                              # Scoring package (7 modules)
  scoring/
    grading_v2.py                       #   8-rule deterministic grading engine
    abstention_metrics.py               #   UWAA, utility matrix
    self_correction_v2.py               #   Transition scoring, confidence adjustment
  tasks/
    self_correction_v2.py               #   C1/C2 prompts, parsing, grading

data/                                   # Benchmark datasets
  metajudge_benchmark_v1.json           #   117 calibration items
  family_b_pilot_v2.json                #   84 abstention items
  family_c_items.json                   #   65 self-correction items (C1 + C2)
  adjudication_registry.json            #   132 grading rules
  clean_subset_manifest.json            #   Exclusion lists
  metajudge_v51_gold_answer_justifications.md  # 266 gold answer justifications

docs/                                   # Scientific foundation
  theoretical_backgrounder.md           #   Two-process framework, task mapping
  metacognition_literature_report.md    #   65+ papers: Hart (1965) → LLM frontier
  family_b_literature_review.md         #   80+ papers on abstention/verification
  family_c_literature_report.md         #   Self-correction: ERN → detection → LLMs
  family_b_scoring_spec.md              #   UWAA derivation, payoff matrix
  family_c_design_review.md             #   C1/C2 design grounded in literature
  item_development_methodology.md       #   Item generation, contamination strategy
  metacognition_assessor_recommendations.md  # "Score by consequences, not self-report"
  metajudge_program_charter.md          #   Scientific defensibility mission
  references.bib                        #   Full bibliography
  stats/                                #   Statistical methodology
    composite_construction.md           #     Equal-weight justification, Haberman
    composite_methods_survey.md         #     30-paper survey on metric aggregation
    power_analysis_family_c.md          #     Effect sizes, ICC, CI widths
    stats_backgrounder_families_ab.md   #     Paired testing, Friedman/Nemenyi

audit/                                  # Validation evidence
  family_ab_audit_summary.md            #   A+B grading accuracy
  family_c_audit_summary.md             #   C grading accuracy, exclusions

config/
  family_c_scoring.yaml                 #   Damage:gain ratios, scoring parameters

SOUL.md                                 #   Governing principles
```

---

## How to Read This Repository

**Start with the framework:**
1. `docs/theoretical_backgrounder.md` — the two-process model and how each task maps to it
2. `SOUL.md` — governing principles and non-negotiables

**Understand the science:**
3. `docs/metacognition_literature_report.md` — the psychological lineage
4. `docs/family_b_literature_review.md` + `docs/family_c_literature_report.md` — per-family depth

**See how it's built:**
5. `docs/item_development_methodology.md` — how items were generated and validated
6. `docs/family_b_scoring_spec.md` + `docs/family_c_design_review.md` — scoring rationale

**Check the math:**
7. `docs/stats/composite_construction.md` — why equal weights
8. `audit/` — grading accuracy validation

**Run the benchmark:**
9. The four notebooks in `notebooks/` — each is self-contained

---

## Key Design Decisions

**No LLM judge.** All grading is deterministic (8-rule engine with numeric tolerance, alias matching, and tri-label classification). This eliminates judge model bias and makes results exactly reproducible.

**Asymmetric damage penalties.** In self-correction, changing a correct answer to wrong (damage) is penalized more heavily than changing wrong to right (correction). This reflects the real-world cost structure: a model that "helps" by correcting one error but introduces two new ones is net harmful.

**Dual-run stochasticity checks.** Abstention and self-correction tasks run twice — once cached (scored), once independent (display only). This surfaces response variance without affecting the scored result.

**Equal-weight composite.** With 4 tasks and 5 models, any data-derived weighting overfits. Equal weights provably minimize expected error at small n (Dawes 1979, Davis-Stober 2011).

---

## Theoretical Grounding

MetaJudge is grounded in the distinction between metacognitive monitoring and control (Nelson & Narens, 1990), operationalized through the report/withhold paradigm (Koriat & Goldsmith, 1996). Family C extends this to error detection and repair — a capacity that Huang et al. (ICLR 2024) showed rarely occurs without external evidence, and where Tyen et al. (2024) demonstrated the bottleneck is detection (monitoring), not repair (control).

For the full bibliography, see `docs/references.bib`.

---

## Version

v6.1 — Resilient evaluation, dual-run stochasticity, inline audit reports with SDK usage tracking.

## License

MIT
