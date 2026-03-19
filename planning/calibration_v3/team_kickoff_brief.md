# Calibration Research Team — Kickoff Brief

**Repo:** https://github.com/seanmichaelmcgee/metajudge (branch: `main`, commit `a50276b`)
**Competition:** Kaggle "Measuring Progress Toward AGI" — Metacognition track
**Deadline:** April 16, 2026

---

## What this project is

MetaJudge is a confidence calibration benchmark. It gives 100 factual questions to frontier LLMs, asks each to answer and state a confidence score (0.0–1.0), then measures whether confidence tracks correctness via Brier scoring. The goal is a dataset that discriminates well-calibrated models from poorly-calibrated ones.

## The problem

Our March 19 sweep of 5 frontier models showed the dataset is too easy. 89/100 items are answered correctly by every model. Only 1 of 5 success criteria is met. We need to replace ~20 items with harder ones that produce confident wrong answers.

## Read these 5 files (in this order)

| # | File | What it tells you |
|---|------|-------------------|
| 1 | `SOUL.md` | Non-negotiable principles, verified model keys, success criteria, sweep protocol |
| 2 | `planning/calibration_research_brief.md` | Your primary assignment — 675 lines of research findings with ranked directions, academic references, and item strategy |
| 3 | `planning/progress_report_sprint2.md` | Sweep results, the 5 discriminator patterns, what worked and what didn't |
| 4 | `notebooks/metajudge_submission.ipynb` | The working Kaggle notebook (v3, 11 cells) — this is the product |
| 5 | `data/calibration_answer_key.json` | The 100-item answer key with gold answers and aliases |

## What we need from you

Deliver implementation-ready findings that let the execution team immediately begin replacing items. Specifically:

1. **Candidate question sets** — Concrete questions (not categories, not theory) following the patterns ranked in `calibration_research_brief.md` §6. Priority: person-attribution confusion, training-data-skewed superlatives, disguised adversarial factual questions.

2. **Pre-validation** — Each candidate should be checked: Is the gold answer unambiguous? Is there a single short correct answer suitable for alias matching? Does the question look like a normal factual question (not an obvious trick)?

3. **Schema compliance** — New items must match the existing `calibration_answer_key.json` format: `gold_answer` (string), `aliases` (array of strings), `answer_type`, `grader_rule`, `format_instruction`.

## Constraints

- Stay within the architecture defined in `SOUL.md` — single-turn, Brier scoring, 100-item count, 5-model panel
- Do not change the scoring function, notebook structure, or model panel
- New items must have unambiguous, verifiable correct answers with short canonical forms
- Target distribution after replacement: easy 5 / medium 15 / hard 30 / deceptive 30 / adversarial 20
- The execution team will run Flash spot-checks on all candidates before committing — your job is to deliver the strongest candidate pool possible

## What success looks like

A set of 25–30 candidate items (more than the ~20 we need, to allow for Flash pre-testing failures) with gold answers, aliases, difficulty classifications, and brief rationale for why each item should produce confident wrong answers from frontier models.
