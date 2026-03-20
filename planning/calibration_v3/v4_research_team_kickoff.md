# Calibration Research Team — V4 Kickoff Brief

**Repo:** https://github.com/seanmichaelmcgee/metajudge (branch: `main`, commit `50eea09`)
**Competition:** Kaggle "Measuring Progress Toward AGI" — Metacognition track
**Deadline:** April 16, 2026

---

## What this project is

MetaJudge is a confidence calibration benchmark. It gives 100 factual questions to frontier LLMs, asks each to answer and state a confidence score (0.0–1.0), then measures whether confidence tracks correctness via Brier scoring. The goal is a dataset that discriminates well-calibrated models from poorly-calibrated ones.

## What failed and why

### V1: Misconception items (29/30 rejected)

Our first attempt delivered 30 "surprising facts" / misconception items. Flash pre-testing showed 29/30 answered correctly with high confidence. The ONE accepted item (cand_h03, Hawaiian alphabet count — gold: 13, Flash answered 12 at 0.95 confidence) succeeded because it required disambiguation under uncertainty, not pure recall.

**The lesson:** Frontier models have already ingested the corrections. The "misconception → correction" pathway is itself well-trodden in training data. Every item where the model could *recall* the answer was rejected.

### Current dataset problem

Our March 19 sweep of 5 frontier models showed the dataset is too easy:
- 89/100 items answered correctly by every model
- Brier spread only 0.036 (need ≥0.05)
- Only 1/5 success criteria met (C4: items with conf-acc gap >0.20)
- Best model (Pro) 98/100, worst (DeepSeek) 93/100

Current difficulty distribution: Easy 10 / Medium 26 / Hard 30 / Deceptive 22 / Adversarial 12
Target after replacement: Easy 5 / Medium 15 / Hard 30 / Deceptive 30 / Adversarial 20

We need to replace ~30 items (removing easy/medium ceiling items, adding deceptive/adversarial/hard items).

## The V4 approach: Adversarial search, not trivia authoring

The V4 directive reframes item design as an **adversarial search problem**. We exploit 7 asymmetries between our authoring pipeline (multi-agent, tool-augmented, deep computation) and the test model's inference (single-turn, no tools, pattern-matching from parametric memory). See the full directive for details.

**The research team's job is NOT to produce items.** It is to produce the execution plans, agent prompts, verification protocols, and feedback loop specifications that the build-and-test sprint will use.

## Read these files (in this order)

| # | File | What it tells you | Priority |
|---|------|-------------------|----------|
| 1 | `SOUL.md` | Non-negotiable principles, verified model keys, success criteria, sweep protocol, schema conventions | MUST READ |
| 2 | `planning/calibration_v3/adversarial_search_directive.md` | V4 directive — the master document. 7 asymmetries, 6 metacognitive failure mechanisms, contamination strategy, 2-agent architecture, 4-phase pipeline, tiered API testing, Brier scoring strategy, environment spec, deliverable specs | MUST READ |
| 3 | `data/calibration_answer_key.json` | The 100-item answer key with gold_answer, aliases, and rule fields. Shows current schema and the items you need to work around | MUST READ |
| 4 | `data/calibration.csv` | The 100-item dataset with prompts and difficulty tags. Shows what currently exists | MUST READ |
| 5 | `planning/calibration_v3/v1_candidate_items_brief.md` | V1 research team's deliverable — what they tried and why it failed. Learn from their mistakes | SHOULD READ |
| 6 | `data/pretest/v1_flash_pretest_results.json` | Raw Flash pre-test results. 29/30 rejected. Study the failure patterns | SHOULD READ |
| 7 | `notebooks/metajudge_submission.ipynb` | The working Kaggle notebook — this is the product. Shows the actual prompt, response format, scoring | REFERENCE |

## What we need from you

Produce **4 separate markdown deliverables** (specified in V4 directive §9):

### Deliverable 1: Generator Agent Prompts (`generator_agent_prompts.md`)

For each of the 2 generator agents, a complete prompt including:

1. Mechanism categories with allocations (V4 §4)
2. **5+ worked examples per mechanism** — genuinely novel, NOT copied from the directive
3. Output schema (V4 §4 JSON format)
4. Contamination blacklist (V4 §3, including the "blog post test")
5. Existing dataset item list for deduplication (extract from `data/calibration.csv`)
6. Environment constraints (V4 §7) including refusal handling protocol
7. Code execution verification requirement
8. Structural feature tagging requirements

Agent allocations:
- **Agent A:** Code Execution + Compositional + IOED + Conditional Temporal + Anchoring (40–45 items)
- **Agent B:** Modified CRT + Prototype Interference + RLHF Overconfidence + Ambiguity-as-Metacognition (35–45 items)

**Critical for code items:** Target Python 3.11+ behavior. Each snippet 3–15 lines, self-contained, must print/evaluate to unambiguous output. DO NOT use mutable default args, `is` vs `==` on small ints, GIL, or any CRUXEval/HumanEval/LeetCode example. DO target banker's rounding, negative floor division, list multiplication aliasing, boolean arithmetic, string comparison, generator exhaustion, dict ordering with deletion, zip() truncation, tuple packing, walrus operator scope. Every code item verified by EXECUTION, not reasoning.

**Critical for compositional items:** Require integrating 2–3 independently verifiable facts. Facts must be common knowledge individually; their combination produces a non-obvious result. Show: Fact 1 (source) + Fact 2 (source) → Computation → Gold answer.

**Critical for Modified CRT:** Must STRUCTURALLY resemble a well-known problem type but modification changes the ANSWER, not just the numbers. DO NOT just change dollar amounts in bat-and-ball.

### Deliverable 2: Verification Protocol (`verification_protocol.md`)

1. Verification procedures by item type (numerical, factual, code, temporal)
2. Stress-test prompt = actual benchmark prompt (NOT enhanced — V4 §4 Phase 2 change)
3. 6-tier accept/reject thresholds including soft-reject with 2-model confirmation
4. Code execution verification script (subprocess-based)
5. Refusal detection logic
6. Orchestrator coordination protocol (Phase 2 pipeline)

### Deliverable 3: Feedback Loop Specification (`feedback_loop_spec.md`)

1. Pipeline calibration data schema (V4 §4 Phase 3 JSON structure)
2. Structural feature analysis — cluster survivors by feature, not just mechanism
3. Generator prompt revision protocol — specific modifications per failure pattern
4. Yield forecasting based on observed survival rates
5. Failure analysis questions

### Deliverable 4: Risk Assessment (`risk_assessment.md`)

1. Overall yield <50% fallback approaches
2. Mechanism categories ranked by expected yield
3. Minimum viable set for ≥4/5 success criteria
4. Code items: what if models are better than literature suggests?
5. Temporal items: model update mid-sprint contamination risk
6. Brier spread: high per-item but cancels across dataset
7. Yield floor contingency: below 30% → double down on code execution
8. ECE bin coverage risk
9. Refusal cascade risk

## Constraints

- Stay within the architecture defined in `SOUL.md` — single-turn, Brier scoring, 100-item count, 5-model panel
- Do not change the scoring function, notebook structure, or model panel
- New items must have unambiguous, verifiable correct answers with short canonical forms
- Schema: `gold_answer` / `aliases` / `rule` (see answer key for format)
- Budget: ~$10–20 for API testing in Phase 3; $50/day Kaggle quota
- 2 generator agents (not 3) — Agent C was eliminated in V4
- Use actual benchmark prompt for stress testing (not enhanced)
- The 5 verified model keys: `google/gemini-2.5-flash`, `google/gemini-2.5-pro`, `anthropic/claude-sonnet-4@20250514`, `anthropic/claude-haiku-4-5@20251001`, `deepseek-ai/deepseek-v3.1`

## What success looks like

The 4 deliverables above, each as a standalone markdown file that the orchestration team can hand to subagents with no additional context needed. The generator prompts should be copy-pasteable. The verification protocol should be implementable as-is. The feedback loop spec should enable iterative improvement without returning to the research team.

**This sprint's 30-item output is a pipeline calibration batch.** Success criteria (from V4 §8):

1. ≥15/30 items surviving to Kaggle notebook verification (50% yield)
2. Brier spread ≥0.08 across the 5-model panel
3. Pipeline calibration data enabling higher yield in next cycle
4. ≥3 mechanism categories represented in survivors
5. Structured feedback specifying how the next batch should differ

## V1 lessons to internalize

| V1 Pattern | V4 Response |
|-----------|-------------|
| Pure recall items → all rejected | Shift to computation, code simulation, compositional reasoning |
| Misconception/correction items → in training data | Use blog post test; freshly author novel instances |
| Single mechanism (person attribution, cultural origin) | Diversify across 6+ mechanisms |
| No code execution items | Target 15–20 code items (expect 8–12 survivors) |
| No compositional items | Target 10–13 compositional items |
| No temporal/conditional items | Target 3–5 conditional-reasoning-on-given-context items |
| Items tested only against Flash | Tiered testing: Flash+Haiku → Pro+Sonnet → Opus |
| Binary accept/reject | 6-tier system with soft-reject + 2-model confirmation |
| No pipeline calibration data | Structured output from Phase 3 for iterative improvement |

---

*End of kickoff. The V4 directive is the master document — this kickoff is the entry point that tells you what to read and what to produce.*
