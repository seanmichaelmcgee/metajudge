# Verification Log — Risks, Unknowns, and Placeholders

## Purpose
This document tracks all known uncertainties, placeholder assumptions, and items
requiring live verification. Nothing here is resolved by assumption — each item
must be verified through testing or documentation review.

Source: Notebook Sketch §Important verification notes, §Practical guidance

---

## CRITICAL UNKNOWNS (Block Phase 6)

### V-001: Kaggle Benchmarks SDK API Surface
**Status:** UNVERIFIED
**Source:** Notebook Sketch §Verification note 1
**What we assume:** `@kbench.task` decorator, `llm.prompt()`, `kbench.assertions`, `.evaluate()` over DataFrames, structured output support via schemas.
**What must be verified:**
- Exact decorator signature and parameters
- Method names on LLM object (`.prompt()`, `.chat()`, `.generate()`)
- Assertion methods available
- Structured output mechanism (schema parameter? separate method?)
- Dataset evaluation helper exact signature
- Multi-turn chat API
- Tool-use API (if relevant)
**How to verify:** Open a Kaggle notebook in the competition, import kaggle_benchmarks, inspect available methods.
**Impact if wrong:** All @kbench.task implementations must be rewritten.

### V-002: Benchmark Export / Selection Mechanism
**Status:** UNVERIFIED
**Source:** Notebook Sketch Cell 27
**What we assume:** Either a notebook magic (`%choose`), a function (`kbench.export_benchmark()`), or a UI action.
**How to verify:** Check competition starter notebooks and documentation.
**Impact if wrong:** Cannot submit benchmark.

### V-003: Model Availability in Competition Environment
**Status:** UNVERIFIED
**Source:** Notebook Sketch §Verification note 2
**What we assume:** Multiple backend models available via `kbench.llm`, list may include Gemini models.
**How to verify:** List available models in a live notebook.
**Impact if wrong:** May need to adjust evaluation strategy for limited model set.

### V-004: Multi-Turn Interaction Support
**Status:** UNVERIFIED
**Source:** Framework §9.1 claims support; Notebook Sketch Cell 21 uses it
**What we assume:** Can call `llm.prompt()` multiple times within a single task function for self-correction and strategy tasks.
**How to verify:** Test in live notebook.
**Impact if wrong:** Self-correction (Task C) and Strategy Adaptation (Task E) may need redesign.

---

## HIGH-PRIORITY UNKNOWNS (Block specific features)

### V-005: Judge Model API
**Status:** UNVERIFIED
**Source:** Framework §13, §9.1
**What we assume:** `assess_response_with_judge` function available for limited rubric checks.
**How to verify:** Check SDK documentation and test in live notebook.
**Impact if wrong:** Must use purely deterministic scoring (actually this may be fine — Framework recommends minimizing judge usage).

### V-006: Structured Output SDK Support
**Status:** UNVERIFIED
**Source:** Framework §9.1, §9.3
**What we assume:** Can pass Pydantic/dataclass schema to `llm.prompt()` and get parsed output.
**How to verify:** Test schema parameter in live notebook.
**Impact if wrong:** Must use JSON prompting + manual parsing (Notebook Sketch Cell 7 approach).

### V-007: Competition Timeline and Deadlines
**Status:** PARTIALLY KNOWN
**What we know:** Competition exists on Kaggle. Our internal plan is 14-21 days.
**What must be verified:** Exact submission deadline, any interim milestones, evaluation criteria weighting.
**How to verify:** Check competition page.

---

## MODERATE UNKNOWNS (Affect quality, not blocking)

### V-008: Scoring Weight Optimization
**Status:** PLACEHOLDER
**Source:** Framework §7.1
**Current assumption:** 25/20/20/15/20 split per framework recommendation.
**What must be verified:** Whether these weights produce meaningful composite differentiation across models.
**How to verify:** Phase 7 pilot evaluation.

### V-009: Dataset Size Adequacy
**Status:** PLACEHOLDER
**Source:** Implementation Plan §Phase 2 targets 500-1500
**What must be verified:** Whether 500 items provides sufficient statistical power for calibration metrics.
**How to verify:** Power analysis during pilot.

### V-010: Anti-Gaming Effectiveness
**Status:** PLACEHOLDER
**Source:** Framework §8
**What must be verified:** Whether countermeasures actually prevent gaming.
**How to verify:** Test with known cheap strategies during pilot (Phase 7).

### V-011: Source-Label Defensibility
**Status:** DESIGN RISK
**Source:** Framework §5.4, Notebook Sketch §Must document clearly
**What the risk is:** Gold source-type labels may be subjective. "Memory" vs "inference" boundary is fuzzy for LLMs.
**Mitigation:** Focus on clear cases (prompt-stated vs everything else). Document ambiguous cases.

### V-012: Self-Correction Task Statefulness
**Status:** DESIGN QUESTION
**Source:** Framework §5.3.3
**Question:** Does the model retain context from turn 1 when processing turn 2? Or must turn 2 include turn-1 output?
**How to resolve:** Depends on V-004 (multi-turn API). If no stateful chat, include turn-1 output in turn-2 prompt.

---

## LOW-PRIORITY UNKNOWNS

### V-013: Notebook Runtime Limits
**Status:** UNKNOWN
**What matters:** Running 500+ items through LLM calls may hit time limits.
**Mitigation:** Design for subset evaluation if needed.

### V-014: Exact Leaderboard Artifact Format
**Status:** UNKNOWN
**Source:** Notebook Sketch §Verification note 3
**What must be verified:** How benchmark results appear on competition leaderboard.

### V-015: Reproducibility Across Runs
**Status:** UNKNOWN
**Source:** Notebook Sketch Cell 3
**What matters:** Model-side nondeterminism may affect reproducibility.
**Mitigation:** Document variability, use seed where possible.

---

## Resolution Tracking

| ID | Status | Resolution Date | Resolution Notes |
|----|--------|-----------------|------------------|
| V-001 | UNVERIFIED | — | — |
| V-002 | UNVERIFIED | — | — |
| V-003 | UNVERIFIED | — | — |
| V-004 | UNVERIFIED | — | — |
| V-005 | UNVERIFIED | — | — |
| V-006 | UNVERIFIED | — | — |
| V-007 | PARTIALLY KNOWN | — | — |
| V-008 | PLACEHOLDER | — | — |
| V-009 | PLACEHOLDER | — | — |
| V-010 | PLACEHOLDER | — | — |
| V-011 | DESIGN RISK | — | — |
| V-012 | DESIGN QUESTION | — | — |
| V-013 | UNKNOWN | — | — |
| V-014 | UNKNOWN | — | — |
| V-015 | UNKNOWN | — | — |
