# Calibration Research Directive

**Date:** March 19, 2026
**From:** Sprint 2 Technical Lead
**To:** Research Team (3+ agents)
**Deliverable deadline:** This session
**Competition deadline:** April 16, 2026

---

## 0. Purpose

This directive initiates a focused research sprint to support the next phase of MetaJudge calibration improvement. The 5-model sweep (March 19, 2026) showed that the current 100-item dataset is too easy for frontier models — 89/100 items are answered correctly by every model, and only 1 of 5 success criteria is met. The research team's job is to investigate how to make the dataset harder and more discriminating, then deliver implementation-ready findings.

**This is a research step, not an execution step.** The research team produces findings and recommendations. A separate execution sprint will implement them.

---

## 1. Project Context

### 1.1 What MetaJudge is

A confidence calibration benchmark for the Kaggle "Measuring Progress Toward AGI" competition (Metacognition track). It presents 100 factual questions to LLMs, elicits verbalized confidence scores (0.0–1.0), and measures whether confidence tracks correctness via Brier scoring.

### 1.2 Codified plans (the research team has full repo access)

| Document | Path | Role |
|----------|------|------|
| SOUL.md | repo root | Non-negotiable principles, success criteria, sweep protocol |
| V1 Architecture | `planning/v1_architecture.md` | Current production plan, family structure, phasing |
| Scoring Plan | `planning/scoring_plan.md` | Brier-derived scoring, adjudication, diagnostics |
| Dataset Construction | `planning/dataset_construction_plan.md` | Item sourcing, canonicalization, pilot gates |
| Expansion Sprint V2 | `planning/expansion_sprint_v2.md` | V2 difficulty distribution, question source strategy |
| Progress Report | `planning/progress_report_sprint2.md` | Sprint 2 results, sweep data, 5 discriminator patterns, recommendations |

**Constraint:** Research recommendations must be compatible with these documents. If a recommendation would require changing SOUL.md or the V1 architecture, flag it explicitly with justification. Do not silently diverge.

### 1.3 Current state (from the March 19 sweep)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| C1: Brier spread | 0.036 | ≥ 0.05 | FAIL |
| C2: Deceptive acc < 80% on ≥3 models | 0/5 | ≥ 3 | FAIL |
| C3: Adversarial acc < 70% on ≥3 models | 1/5 | ≥ 3 | FAIL |
| C4: Items with conf–acc gap > 0.20 | 11 | ≥ 10 | PASS |
| C5: ECE range | not measured | ≥ 0.03 | PENDING |

- 89/100 items universally correct across all 5 models
- 11 discriminating items (models disagree)
- 16 overconfident errors total across all models
- Best discriminators: cal_084 (4/5 wrong), cal_088 (3/5 wrong)
- Current distribution: easy 10, medium 26, hard 30, deceptive 22, adversarial 12

### 1.4 What works (do not change)

- Brier scoring function and its strict propriety
- Adjudication logic (alias matching)
- Notebook architecture (v3, 11 cells, SDK-aligned)
- 5-model panel (Flash, Pro, Haiku, Sonnet, DeepSeek)
- Success criteria (the criteria are correct; the dataset needs to meet them)
- Wrapper-task architecture

---

## 2. Research Assignments

### Assignment A: Academic & Technical Foundations

**Question:** What does the literature say about making LLM calibration benchmarks harder and more discriminating?

**Scope:**
1. **Academic references** on LLM confidence calibration, overconfidence, and benchmark design for frontier models. Prioritize work from 2023–2026 that addresses the ceiling-effect problem we face.
2. **Key public repositories** implementing calibration benchmarks or confidence elicitation for LLMs. We need concrete examples of question design, not just theoretical frameworks.
3. **Specific techniques** for constructing questions that reliably produce confident wrong answers from frontier models (the cal_084/cal_088 pattern at scale).

**Deliverable:** A structured findings document with:
- Annotated bibliography (10–20 most relevant papers, each with 2–3 sentence relevance note)
- List of public repos with links, what they do, and what we can learn from them
- Specific question-construction techniques from the literature, mapped to our 5 difficulty buckets

### Assignment B: Challenges & Feasibility Analysis

**Question:** What are the hardest problems in building a 100-item dataset that meets our success criteria, and what are realistic solutions?

**Scope:**
1. **Why frontier models are hard to fool** — what makes deceptive/adversarial items fail? Analysis of our current items that didn't work vs. the 2 that did (cal_084, cal_088).
2. **The contamination problem** — how much of our question space is in training data? What categories of questions are most likely to be novel to frontier models?
3. **Scoring reliability** — our Brier-derived metric is theoretically sound, but verbalized confidence is noisy. What does the literature say about reducing noise in elicited confidence? Prompt engineering? Repeated sampling? Alternative elicitation methods compatible with our single-turn architecture?
4. **Technical requirements** — review the schema discrepancy issue (§7.2 of progress report: three different field name conventions across adjudication.py, answer_key.json, and notebook Cell 3) and recommend a resolution.

**Deliverable:** A challenges document with:
- Ranked list of challenges (hardest first) with feasibility assessment
- For each challenge: what the literature says, what our data shows, recommended approach
- Specific technical recommendations for the schema unification and any other infrastructure issues

### Assignment C: Research Directions & Item Strategy

**Question:** What are the most promising avenues for replacing ~20 universally-correct items with harder ones?

**Scope:**
1. **Review the 5 discriminator patterns** from the progress report (§6.2) and evaluate which are most promising based on academic evidence.
2. **Propose specific question categories** that are likely to produce confident wrong answers. Not individual questions — categories with rationale and examples.
3. **Evaluate the rejection log** strategy — is `data/harvest/v2_rejection_log.json` (123 candidates) a viable source, or do we need fresh sourcing?
4. **Consider alternative elicitation approaches** — are there prompt modifications (within our single-turn constraint) that could increase discriminatory power without changing the scoring?
5. **Assess the recommended distribution shift** (easy 5, medium 15, hard 30, deceptive 30, adversarial 20) against the literature. Is this distribution well-supported? Should it be different?

**Deliverable:** A research directions document with:
- Ranked list of most promising research avenues (top 5–8)
- For each: academic support, feasibility assessment, expected impact on success criteria
- Specific question-category recommendations with example patterns
- Distribution recommendation with justification

---

## 3. Constraints & Requirements

1. **Stay within the current architecture.** The wrapper-task pattern, Brier scoring, 100-item count, and 5-model panel are fixed. Recommendations should work within these constraints.
2. **Be specific, not theoretical.** "Use harder questions" is not useful. "Use questions about commonly misattributed scientific discoveries, because X paper showed models are overconfident on attribution by Y%" is useful.
3. **Cite sources.** Every claim about what the literature says must have a citation. Every repo recommendation must have a URL.
4. **Consider the competition deadline.** We have ~4 weeks. Recommendations that require 6 months of work are not useful. Focus on what's achievable in 1–2 sprints.
5. **Reference the codified plans.** When making recommendations, note how they relate to existing plans (SOUL.md, V1 arch, etc.). Flag any conflicts explicitly.
6. **Point to repo locations.** When referencing technical requirements or code, provide file paths within the repo. The execution team will need to find things quickly.

---

## 4. Deliverables Summary

| # | Deliverable | Agent | Format |
|---|------------|-------|--------|
| D1 | Academic & Technical Foundations | Agent A | Markdown, saved to workspace |
| D2 | Challenges & Feasibility Analysis | Agent B | Markdown, saved to workspace |
| D3 | Research Directions & Item Strategy | Agent C | Markdown, saved to workspace |
| D4 | Consolidated research brief | Lead (post-merge) | Committed to `planning/calibration_research_brief.md` |

Each agent saves their findings to a separate workspace file. The lead will merge, deduplicate, and commit a consolidated brief to the repo.

---

## 5. What Success Looks Like

The research team's output is successful if the execution team can read it and immediately begin:
1. Selecting which items to replace and what to replace them with
2. Implementing any prompt or scoring adjustments
3. Resolving infrastructure issues (schema unification, validator tests)
4. Running a validation sweep with confidence that the new items will move the success criteria

The research should reduce the execution team's decision space, not expand it.
