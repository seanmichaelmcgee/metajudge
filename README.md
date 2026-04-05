# MetaJudge-AGI

A behavioral benchmark for metacognitive monitoring and control in frontier language models.

[Kaggle Measuring Progress Toward AGI](https://www.kaggle.com/competitions/kaggle-measuring-agi) — Metacognition track.

---

## What This Measures

MetaJudge evaluates whether LLMs can **track the reliability of their own outputs** (monitoring) and **act on that information** (control), per Nelson & Narens (1990). Scores are based on behavioral consequences, not self-report.

| Task | Process | Items | Metric |
|------|---------|-------|--------|
| Confidence Calibration | Monitoring | 105 | Brier rule (strictly proper) |
| Selective Abstention | Control | 72 | UWAA (config-driven matrix + answer-rate penalty) |
| Self-Correction C1 | Control | 28 | Opportunity-conditioned (intrinsic, no evidence) |
| Self-Correction C2 | Control | 23 | Opportunity-conditioned (evidence-assisted) |

**MetaScore** = platform average of 4 anchor-normalized task scores. Equal weights (Dawes 1979).

---

## Repository Map

| Path | What |
|------|------|
| `notebooks/` | 4 Kaggle Benchmark task notebooks (v6.5) |
| `metajudge/` | Scoring package: grading engine, UWAA, opportunity-conditioned scoring (7 modules) |
| `data/` | Benchmark items, registry, manifest, gold answer justifications |
| `config/` | Scoring parameters: Family B (`family_b_scoring.yaml`) and Family C (`family_c_scoring.yaml`) |
| `docs/` | Scientific foundation: literature reports, scoring specs, statistical methods |
| `docs/scoring_overview.md` | End-to-end scoring explainer |
| `docs/theoretical_backgrounder.md` | Two-process framework and task mapping |
| `audit/` | Grading accuracy validation (Families A/B and C) |
| `outputs/benchmark_runs/` | Per-model run outputs (CSVs, JSONs, audit reports) |
| `outputs/scoring_audit/` | Scoring validity analysis and findings |
| `METHODOLOGY.md` | Development progression: survey → design → items → scoring → validation |
| `SOUL.md` | Governing principles |

---

## How to Read This

1. **`docs/theoretical_backgrounder.md`** — the framework
2. **`docs/scoring_overview.md`** — how scores work (Brier, UWAA, transitions, anchors)
3. **`METHODOLOGY.md`** — how the benchmark was built
4. **`notebooks/`** — the 4 task notebooks (each is self-contained)
5. **`outputs/benchmark_runs/`** — actual model results
6. **`audit/`** + **`outputs/scoring_audit/`** — validation evidence

---

## Key Design Decisions

- **No LLM judge.** Deterministic 8-rule grading engine. Every score is reproducible.
- **Asymmetric damage penalties.** Breaking a correct answer costs more than fixing a wrong one.
- **Dual-run stochasticity.** Tasks B, C1, C2 run twice to surface response variance.
- **Equal-weight composite.** Provably optimal at small n (Davis-Stober 2011).
- **Behavioral evidence only.** What models do, not what they claim.
- **Item quarantine system.** 11 items (1 quarantined, 10 shadow-scored) excluded from headline scores to remove structurally ambiguous or non-discriminating items while retaining them for diagnostics.

---

## Current Status

v6.5 upgrade in progress. Key changes from v6.2: opportunity-conditioned C1/C2 headline (preserve_rate + repair_rate), config-driven Family B matrix with differentiated verify/abstain off-diagonals and answer-rate penalty, item quarantine system (11 items excluded from headline). 15 models evaluated on v6.1, 4+ on v6.2. Grading fixes applied (confirmation detection, answer truncation, tri-label).

---

## To-Do

- [ ] **Notebook cell ordering:** Move the rich task description (`def` with docstring) into the `@kbench.task` without `store_task=False` — that cell displays when someone opens the task on Kaggle. Currently the main task cell (with report generation code) displays instead of the useful explanation.
- [ ] **Abstention justification audit:** Many justifications are unclear or potentially wrong (e.g., abs_001 gold=31 may actually be 63). Read and audit all 84 abstention justifications for clarity and accuracy.
- [ ] **Abstention grading clarity:** Ensure explanations of utility scoring are clear — particularly how clarify-vs-abstain receives partial credit (+0.3) rather than penalty, and what drives negative utility.
- [ ] **Complete scoring reporting (WS3b):** Expand notebook methodology markdowns with intuitive score interpretation, anchor context, and pointer to `docs/scoring_overview.md`.
- [ ] **Benchmark description text (WS3c):** Write the 3-sentence intro + 5 scoring methodology bullets for the Kaggle benchmark description page (requires clean v6.2 runs).
- [ ] **Extract remaining model outputs:** Pull all v6.2 notebook outputs via Kaggle API for full-panel scoring audit.
- [ ] **Scoring discrimination analysis:** With full panel data, assess per-task discrimination, item-level separation, ceiling/floor effects (especially C1/C2 clustering).
- [ ] **Write RESULTS_SUMMARY.md:** Cross-model findings narrative (blocked on complete v6.2 runs).
- [ ] **Write WRITEUP.md:** 1,500-word competition entry (blocked on results).
- [ ] **Sync submission branch:** Final sync of notebooks, docs, and results before deadline.

---

## License

MIT
