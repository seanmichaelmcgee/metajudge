# MetaJudge v5.1 — Theoretical Backgrounder

> **Purpose:** Single reference document for the two-axis metacognition framework, task mapping, scoring methodology, and stochasticity approach. The v5.1 notebook markdowns point here for theoretical grounding rather than inlining citations.
>
> **Version:** 5.1 | **Date:** 2026-04-02

---

## 1. Framework: Monitoring and Control

MetaJudge is built on the two-process model of metacognition established by Nelson & Narens (1990). Their framework defines exactly two information flows:

- **Monitoring** — evaluating the state of cognition. Information flows from the object level to the meta level. *"How am I doing?"* Examples: confidence judgments, feeling-of-knowing, calibration accuracy.
- **Control** — using metacognitive judgments to change behavior. Information flows from the meta level back to the object level. *"What should I do about it?"* Examples: abstention, verification requests, strategy switching, self-correction.

These two processes are exhaustive. Every metacognitive behavior is either monitoring (assessing cognitive state) or control (acting on that assessment). MetaJudge's four tasks map onto these two processes, not four independent axes.

---

## 2. Task-to-Process Mapping

| Task | Items | Process | Reasoning |
|------|-------|---------|-----------|
| Confidence Calibration | 105 | **Monitoring** | Measures whether stated confidence tracks actual correctness. Pure monitoring — the model reports a probability, and we score how well it tracks truth. No action decision is involved. |
| Selective Abstention | 72 | **Control** | The model uses its uncertainty judgment to choose an epistemic action: answer, clarify, verify, or abstain. The monitoring happens internally; the measured outcome is the action decision — a control behavior. |
| Intrinsic Self-Correction (C1) | 28 | **Control** | The model receives a review prompt and decides whether to revise its answer. The scored outcome is revision quality — a control action. See §3 for the monitoring→control nuance. |
| Evidence-Assisted Self-Correction (C2) | 23 | **Control** | Same as C1, but with an external evidence snippet that may be accurate, misleading, or irrelevant. Tests whether the model can appropriately integrate or reject new information — a control decision under uncertainty. |

---

## 3. The C1 Nuance: Monitoring as Bottleneck, Control as Measurement

Tyen et al. (2024, "LLMs Cannot Find Reasoning Errors") demonstrated that the bottleneck in self-correction is *detection* (a monitoring process), not *repair* (a control process). Models that detect errors can usually fix them; the hard part is knowing something is wrong. Huang et al. (ICLR 2024, "Large Language Models Cannot Self-Correct Reasoning Yet") showed further that intrinsic self-correction — without external feedback — rarely improves performance, because the same reasoning that produced the error also governs the correction attempt.

C1 therefore tests the full monitoring→control pipeline. The binding constraint is monitoring (error detection), but the scored outcome is control (the revision itself). We classify C1 as **Control** because that is what the benchmark measures, while acknowledging that monitoring is the capacity being tested.

---

## 4. Scoring Methodology

Each of the four tasks returns an **anchor-normalized** score in [0, 1], where the anchors represent floor and ceiling performance levels derived from the 5-model pilot sweep:

| Task | Low Anchor | High Anchor | Metric |
|------|-----------|-------------|--------|
| Calibration | 0.75 | 1.00 | 1 − Brier score (strictly proper) |
| Abstention | 0.60 | 1.00 | UWAA (Utility-Weighted Action Accuracy) |
| C1 | −0.10 | +0.15 | Mean transition score |
| C2 | −0.20 | +0.20 | Mean transition score |

The Kaggle Benchmarks platform averages the four normalized scores into the leaderboard MetaScore. This equal-weight average is justified by Dawes (1979) and Davis-Stober (2011), who proved that with small k (number of components) and small n (number of observations), any data-derived differential weighting will have higher expected error than equal weights. Anchor normalization follows the BIG-Bench precedent (Srivastava et al., 2023) and the Open LLM Leaderboard v2 (Beeching et al., 2024).

---

## 5. Stochasticity Approach

LLM responses are non-deterministic. MetaJudge uses a **dual-run reproducibility check** on tasks B, C1, and C2: Run 1 is cached (deterministic baseline); Run 2 is independent (measures response variance). Item-level agreement and score-level spread are reported.

This approach is grounded in the triplicate analysis conducted during development (5 models × 3 independent runs), which yielded ICC = 0.758 averaged across models — above the 0.75 threshold for "good" reliability (Koo & Li, 2016). Family A (Confidence Calibration) is excluded from dual-run because it is single-turn with negligible variance observed in pilot testing.

---

## 6. Design Principle

> *"MetaJudge scores metacognition by the consequences of self-monitoring on task behavior, not by what the model says about itself."*
>
> — Adapted from the Metacognition Assessor Recommendations memo

---

## 7. Detailed Documentation

| Document | Path | Covers |
|----------|------|--------|
| Metacognition Literature Report | `docs/metacognition_literature_report.md` | 80+ paper bibliography: Hart (1965) → Nelson & Narens (1990) → 2024–2026 LLM frontier |
| References BibTeX | `docs/references.bib` | Full citations |
| Family B Literature Review | `docs/family_b_literature_review.md` | 12-theme review of selective abstention research |
| Family B Scoring Spec | `docs/family_b_scoring_spec.md` | Payoff matrix, UWAA derivation, acceptable alternatives |
| Family C Literature Report | `planning/family_c_sprint/20_family_c_literature_report.md` | Rabbitt (1966) → ERN → Nelson & Narens control → LLM self-correction |
| Family C Theoretical Grounding | `planning/family_c_sprint/Theoretical_grounding_MetaJudge_Family_C.md` | 7 design questions, damage:gain ratio, prospect theory, FOK |
| Family C Design Review v2 | `planning/family_c_sprint/21_family_c_design_review_v2.md` | Engineering spec, reasoning-model addendum, CoT-resistant errors |
| Scientific Constraints (C) | `planning/family_c_sprint/01_scientific_constraints.md` | Non-negotiable principles, monitoring→control link |
| Scoring Blueprint (C) | `planning/family_c_sprint/03_scoring_blueprint.md` | Transition classification, asymmetric damage penalty |
| Assessor Recommendations | `docs/metacognition_assessor_recommendations.md` | "Score by consequences, not self-report" principle |
| Composite Methods Survey | `docs/stats/Composite Rankings...Methods Survey.md` | 30-paper survey, equal-weight justification |
| Composite Step 2 | `docs/stats/composite_construction_step2.md` | Spearman correlations, Haberman PRMSE, B×C anti-correlation |
| Power Analysis (C) | `docs/stats/power_analysis_family_c.md` | CI widths, ICC, significance testing |
| Triplicate Results | `Benchmark_prep_docs_and_results_Apr_01/family_c_FULL_triplicate_results_and_analysis.md` | 5 models × 3 runs, anchor derivation data |
| Stats Backgrounder (A+B) | `docs/stats/stats_backgrounder_families_ab.md` | Paired-data structure, Friedman/Nemenyi tests |
| Item Development | `docs/item_development_methodology.md` | Authoring, filtering, contamination strategy |

---

## References

- Beeching, E., et al. (2024). Open LLM Leaderboard v2. Hugging Face.
- Davis-Stober, C. P. (2011). When is a linear combination of predictors optimal? *Psychometrika*, 76(4), 602–614.
- Dawes, R. M. (1979). The robust beauty of improper linear models in decision making. *American Psychologist*, 34(7), 571–582.
- Huang, J., et al. (2024). Large Language Models Cannot Self-Correct Reasoning Yet. *ICLR 2024*.
- Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients. *Journal of Chiropractic Medicine*, 15(2), 155–163.
- Nelson, T. O., & Narens, L. (1990). Metamemory: A theoretical framework and new findings. *Psychology of Learning and Motivation*, 26, 125–173.
- Srivastava, A., et al. (2023). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. *TMLR*.
- Tyen, G., et al. (2024). LLMs Cannot Find Reasoning Errors, but Can Correct Them! *ACL 2024 Findings*.
