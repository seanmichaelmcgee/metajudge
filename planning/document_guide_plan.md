# Plan: Create `docs/DOCUMENT_GUIDE.md`

## Context

MetaJudge has 100+ markdown documents spanning theory, design, scoring, orchestration, audits, and historical artifacts across `docs/`, `planning/`, `outputs/`, `orchestrator/`, and root. Three partial classification systems exist but none covers the full landscape. A reasoning agent needs a single entry-point that maps the documentation, traces theory→implementation pipelines, and flags superseded docs.

## Approach

Create `docs/DOCUMENT_GUIDE.md` — a comprehensive guide classifying every significant document using a 5-tier taxonomy (Governance, Authoritative, Reference, Historical, Operational). Includes orchestrator docs as a full section. Archives get a single paragraph summary.

## Taxonomy

| Tier | Label | Meaning |
|------|-------|---------|
| **G** | Governance | Non-negotiable principles, wins all conflicts |
| **A** | Authoritative | Currently governs decisions in its scope |
| **R** | Reference | Valuable context, not binding |
| **H** | Historical | Superseded or completed |
| **O** | Operational | Runbooks, checklists, agent prompts |

## Sections

1. **Governance & Project Identity** (G) — SOUL.md, CLAUDE.md, README.md
2. **Theoretical Foundations** (A/R) — metacognition_assessor_recommendations, literature reports, scientific constraints, Family C theoretical grounding
3. **Composite & Statistical Methodology** (A) — composite_construction_step2, methods survey, stats backgrounder, power analysis
4. **Family Design & Scoring Specs** (A per family) — scoring_plan (A), family_b_scoring_spec (B), scoring_blueprint + item_design + SCHEMA + config (C)
5. **Item Development Methodology** (R) — item_development_methodology, design_review_v2
6. **Agent Architecture & Orchestration** (O/R) — GROUNDING.md, AGENTS.md, DECISION_LOG.md
7. **Validation & Audit Trail** (A) — audit summaries, gold answer justifications, sweep analyses
8. **Notebook & Kaggle Integration** (O) — notebook_architecture_memo, kaggle_upload_runbook
9. **Sprint Checkpoints** (H) — completed execution state docs
10. **Historical/Superseded** — single paragraph noting archive contents

## Intellectual Pipeline (traced end-to-end)

```
Theory → Design → Build → Validate → Score → Composite
```

Each section maps docs to the code artifacts they govern or produced.

## Files to create/modify

| File | Action |
|------|--------|
| `docs/DOCUMENT_GUIDE.md` | Create — main deliverable (~300 lines) |

## Verification

- Every .md in docs/, planning/ (non-archive), outputs/, orchestrator/, root is classified
- Readable in <10 minutes by a new agent
- At least 3 theory→implementation paths traced
- All known false starts flagged
