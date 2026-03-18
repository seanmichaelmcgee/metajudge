# Agent Team Plan — MetaJudge-AGI

## Overview

This document defines the multi-agent team structure for building the MetaJudge-AGI benchmark.
Each agent has a clear mandate, scope, inputs, outputs, dependencies, and handoff rules.

Source alignment: Implementation Plan §Agent Roles, Framework §11

---

## Agent 1: Orchestrator / Project Manager

**Mandate:** Coordinate all agents, enforce consistency, track progress, resolve conflicts.

**Scope boundaries:**
- Does NOT write task items or scoring code directly
- DOES maintain the backlog, phase plan, and dependency graph
- DOES resolve integration conflicts between agents

**Inputs:**
- Three source markdown files
- Agent status reports
- Verification log updates

**Outputs:**
- Phase plan updates
- Backlog updates
- Integration instructions
- Decision records

**Dependencies:** None (root agent)

**Success criteria:**
- All phases complete on time
- No unresolved cross-agent conflicts
- All deliverables traceable to source documents

**Expected artifacts:**
- `planning/phase_plan.md`
- `planning/backlog/*.md`
- `planning/decisions/*.md`

**Handoff rules:**
- Receives artifacts from all agents for integration review
- Escalates Kaggle SDK unknowns to Integration Agent
- Triggers QA Agent at phase boundaries

---

## Agent 2: Environment and Infrastructure

**Mandate:** Set up and maintain the Linux development environment, Git workflow, CI, and dependency management.

**Scope boundaries:**
- Repository bootstrap, venv, dependencies, Git hooks
- Does NOT author benchmark content
- Does NOT interact with Kaggle SDK

**Inputs:**
- `requirements.txt`
- `pyproject.toml`
- Repository structure plan

**Outputs:**
- Working Python environment
- Git repository with initial commit
- Development tooling (linting, formatting, testing)

**Dependencies:** None (first agent to execute)

**Success criteria:**
- `python -m pytest` runs without errors
- `import metajudge` succeeds
- All directories exist per plan

**Expected artifacts:**
- `.venv/`
- `.gitignore`
- `pyproject.toml`
- `requirements.txt`
- Initial git commit

**Handoff rules:**
- Hands off working environment to all other agents
- Notifies Orchestrator when environment is ready

---

## Agent 3: Schema / Interface Agent

**Mandate:** Define and maintain all structured response schemas, task item schemas, and metadata formats.

**Scope boundaries:**
- Pydantic models for all five task families
- Hidden metadata schema for evaluation
- Validation rules
- Does NOT author task content or scoring logic

**Inputs:**
- Framework §5.1-5.5 (response format specifications)
- Framework §6.2-6.3 (response fields, hidden metadata)

**Outputs:**
- `metajudge/schemas/response_schemas.py`
- Schema documentation
- Validation test suite

**Dependencies:** Environment Agent (working Python)

**Success criteria:**
- All five task-family schemas defined
- Hidden metadata schema defined
- All schemas pass Pydantic validation tests
- Schema matches Framework specifications

**Expected artifacts:**
- `metajudge/schemas/response_schemas.py`
- `tests/unit/test_schemas.py`
- `docs/schema_reference.md`

**Handoff rules:**
- Provides schemas to Task Authoring Agent and Scoring Agent
- Any schema change must be approved by Orchestrator
- Notifies Integration Agent of schema changes for Kaggle compatibility

---

## Agent 4: Dataset / Task Authoring Agent

**Mandate:** Author benchmark task items across all five families with appropriate difficulty gradients, adversarial variants, and metadata.

**Scope boundaries:**
- Creates task items (prompts, gold answers, metadata)
- Creates difficulty tiers and adversarial variants
- Does NOT implement scoring logic
- Does NOT handle Kaggle SDK integration

**Inputs:**
- Framework §5.1-5.5 (task family designs)
- Framework §4.1 (sub-benchmark structure)
- Implementation Plan §Phase 2 (dataset targets: 500-1500 items)
- Schemas from Agent 3

**Outputs:**
- Task item datasets (JSON/CSV) per family
- Metadata including difficulty, ambiguity class, optimal action
- Family/variant linkage for anti-gaming

**Dependencies:** Schema Agent (response schemas, metadata format)

**Success criteria:**
- Minimum 100 items per task family (500 total minimum)
- Each family has easy/medium/hard/deceptive/adversarial tiers
- Answerable and non-answerable items appropriately mixed
- All required metadata fields populated
- Self-correction items have both wrong-first and correct-first cases (Framework §8.2.5)

**Expected artifacts:**
- `data/raw_tasks/calibration_items.json`
- `data/raw_tasks/abstention_items.json`
- `data/raw_tasks/self_correction_items.json`
- `data/raw_tasks/source_awareness_items.json`
- `data/raw_tasks/strategy_adaptation_items.json`
- `docs/task_authoring_guide.md`

**Handoff rules:**
- Provides datasets to Scoring Agent for metric development
- Provides datasets to Anti-Gaming Agent for hardening
- Provides datasets to QA Agent for validation

---

## Agent 5: Scoring / Metrics Agent

**Mandate:** Implement all scoring logic — per-item, per-family, and composite.

**Scope boundaries:**
- Calibration metrics (Brier, ECE, overconfidence)
- Abstention utility scoring
- Self-correction quality metrics
- Source-awareness scoring
- Strategy adaptation metrics
- Composite score aggregation
- Does NOT author task items
- Does NOT handle Kaggle integration

**Inputs:**
- Framework §7 (scoring framework)
- Framework §5.x.5 (per-family scoring specs)
- Schemas from Agent 3
- Sample data from Agent 4

**Outputs:**
- `metajudge/scoring/*.py` — all scoring modules
- Unit tests for scoring functions
- Scoring documentation

**Dependencies:** Schema Agent, Dataset Agent (for test data)

**Success criteria:**
- All metrics from Framework §7.2 implemented
- Composite score satisfies four design principles (Framework §7.3)
- Unit tests pass with prototype data
- Overconfident error penalty is verifiably larger than low-confidence error

**Expected artifacts:**
- `metajudge/scoring/calibration_metrics.py`
- `metajudge/scoring/abstention_metrics.py`
- `metajudge/scoring/self_correction_metrics.py`
- `metajudge/scoring/source_awareness_metrics.py`
- `metajudge/scoring/strategy_metrics.py`
- `metajudge/scoring/composite_score.py`
- `tests/unit/test_scoring.py`

**Handoff rules:**
- Provides scoring functions to Integration Agent for Kaggle wrapping
- Reports any scoring design issues to Orchestrator
- Coordinates with Anti-Gaming Agent on penalty schedules

---

## Agent 6: Kaggle Integration Agent

**Mandate:** Build the Kaggle notebook, wrap tasks in @kbench.task, handle SDK integration, manage submission flow.

**Scope boundaries:**
- Kaggle notebook construction
- @kbench.task wrappers
- .evaluate() dataset integration
- Benchmark export/selection
- Does NOT define scoring logic (uses Scoring Agent's functions)
- Does NOT author task items

**Inputs:**
- Notebook Sketch (all cells)
- Framework §9 (Kaggle integration patterns)
- Scoring modules from Agent 5
- Task modules from Agents 3-4
- Kaggle SDK documentation

**Outputs:**
- `notebooks/kaggle_submission.py` (notebook-as-script)
- `metajudge/evaluation/kaggle_integration.py`
- SDK verification report

**Dependencies:** Schema, Dataset, Scoring agents

**Success criteria:**
- Notebook runs end-to-end in Kaggle environment
- All five task families registered as @kbench.task
- .evaluate() works over full dataset
- Benchmark export step confirmed

**Expected artifacts:**
- `notebooks/kaggle_submission.py`
- `metajudge/evaluation/kaggle_integration.py`
- `planning/verification/kaggle_sdk_verification.md`

**Handoff rules:**
- Receives scoring functions and schemas from other agents
- Reports SDK verification results to Orchestrator
- Coordinates with QA Agent for notebook testing

---

## Agent 7: Anti-Gaming / Robustness Agent

**Mandate:** Harden the benchmark against superficial optimization using all eight countermeasures.

**Scope boundaries:**
- Prompt paraphrasing and variation
- Decoy difficulty cues
- Symmetric correction setup verification
- Source-label adversarial item design
- Cross-template evaluation splits
- Verbosity independence checks
- Does NOT create base task items (works from Dataset Agent's output)
- Does NOT modify scoring weights

**Inputs:**
- Framework §8 (all anti-gaming requirements)
- Task items from Agent 4
- Scoring results from Agent 5

**Outputs:**
- `metajudge/anti_gaming/perturbations.py`
- Hardened dataset variants
- Anti-gaming validation report

**Dependencies:** Dataset Agent, Scoring Agent

**Success criteria:**
- All eight countermeasures from §8.2 have implementations or verified plans
- No single-action policy dominates composite score
- Paraphrase variants produce consistent scores
- Verbosity-score correlation < 0.2

**Expected artifacts:**
- `metajudge/anti_gaming/perturbations.py`
- `data/processed_tasks/*_hardened.json`
- `planning/verification/anti_gaming_report.md`

**Handoff rules:**
- Returns hardened datasets to Dataset Agent for integration
- Reports vulnerabilities to Orchestrator
- Coordinates with QA Agent for robustness testing

---

## Agent 8: QA / Validation Agent

**Mandate:** Validate all artifacts against source specifications. Run construct validity, discriminative validity, robustness, and anti-gaming checks.

**Scope boundaries:**
- Schema validation
- Scoring unit tests
- Dataset quality checks
- Cross-agent consistency verification
- Does NOT create new content
- Does NOT fix issues (reports them)

**Inputs:**
- Framework §14 (validation plan)
- All artifacts from all agents
- Source markdown files

**Outputs:**
- Validation reports
- Bug/issue reports
- Test suite results

**Dependencies:** All other agents (runs after phases complete)

**Success criteria:**
- All unit tests pass
- Schema validation passes
- No untracked divergence from source markdowns
- Validation axes from §14 addressed

**Expected artifacts:**
- `tests/unit/test_*.py`
- `tests/integration/test_*.py`
- `planning/verification/validation_report.md`

**Handoff rules:**
- Reports issues back to owning agent
- Blocks phase transitions on critical failures
- Signs off on phase completion to Orchestrator

---

## Agent 9: Documentation Agent

**Mandate:** Produce all documentation — benchmark charter, README, task authoring guide, scoring explanation, competition writeup.

**Scope boundaries:**
- README and benchmark card
- Competition writeup (Framework §11, Task 9)
- Task authoring guide
- Scoring documentation
- Decision records
- Does NOT modify code

**Inputs:**
- All code artifacts
- All planning documents
- Framework §10 (benchmark proposal structure)
- Framework §15 (limitations to acknowledge)

**Outputs:**
- `README.md`
- `docs/benchmark_charter.md`
- `docs/task_authoring_guide.md`
- `docs/scoring_explanation.md`
- `docs/competition_writeup.md`
- `docs/limitations.md`

**Dependencies:** All other agents (for content)

**Success criteria:**
- README is accurate and current
- Competition writeup addresses Framework §10 and §15
- All scoring weights and design decisions documented
- Anti-gaming measures explained clearly

**Expected artifacts:**
- All files in `docs/`
- Updated `README.md`

**Handoff rules:**
- Receives content from all agents
- Coordinates with Orchestrator on final submission materials

---

## Dependency Graph (Agent Execution Order)

```
Environment Agent (Agent 2)
    └── Schema Agent (Agent 3)
            ├── Dataset Agent (Agent 4) ─── Anti-Gaming Agent (Agent 7)
            └── Scoring Agent (Agent 5) ─── Kaggle Integration Agent (Agent 6)
                                                     │
QA Agent (Agent 8) ◄──────── All agents ─────────────┘
Documentation Agent (Agent 9) ◄──── All agents
Orchestrator (Agent 1) ◄──── All agents (continuous)
```

## Parallelization Opportunities

- Agents 3 (Schema) and 2 (Environment) can run in parallel
- Agents 4 (Dataset) and 5 (Scoring) can start once Agent 3 finishes
- Agent 7 (Anti-Gaming) can start once Agent 4 has initial items
- Agent 6 (Kaggle) can start architecture once Agent 3 finishes, but needs Agent 5 for scoring
- Agent 8 (QA) runs at every phase boundary
- Agent 9 (Documentation) runs continuously
