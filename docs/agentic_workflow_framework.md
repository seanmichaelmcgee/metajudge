# MetaJudge Agentic Workflow Framework

## Purpose

Standard operating procedure for complex multi-agent tasks in this project.
Designed to balance thoroughness (opus reasoning) with speed (sonnet execution)
while protecting against session timeout and context loss.

Adapted for the v6.5 upgrade: sequential workstreams of code changes, scoring
logic, notebook edits, and tests — touching shared files that require ordered
execution and per-stream validation.

---

## Hierarchy

```
ORCHESTRATOR (main context — opus)
│   Holds full project context and plan state. Never delegated.
│   Commits after each stream completes. Gates stream transitions.
│   Delegates bounded tasks, synthesizes results, verifies integration.
│
├── STREAM LEAD (1 per workstream — opus, foreground or background)
│   │   Owns one sequential stream (e.g., "C1 scoring fixes").
│   │   Reads plans, writes code, runs tests within stream scope.
│   │   Reports: files changed, tests passing, issues found.
│   │
│   ├── TASK AGENT (up to 3 per stream lead — opus or sonnet)
│   │   Executes a specific bounded task within the stream.
│   │   Model selection:
│   │     opus: scoring logic, transition classification, semantic grading
│   │     sonnet: data file edits, JSON/YAML creation, formatting, simple tests
│   │
│   └── TASK AGENT
│
├── STREAM LEAD (next workstream — launched AFTER previous completes)
│
└── VALIDATOR (opus, launched after each stream)
    Reads changed files, runs tests, checks for regressions.
    Confirms stream is clean before orchestrator gates the next one.
```

---

## v6.5 Upgrade: Stream Execution Order

Streams are **sequential** because they touch shared files (especially
`self_correction_v2.py`, `abstention_metrics.py`, notebooks). Running them
in parallel risks merge conflicts and accidentally reverting changes.

```
Stream 1: C1/C2 Scoring (CJ-001, CJ-002, CJ-003)
  Plan: docs/plans/c1_scoring_fixes_v65.md
  Scope: maintain/neutral boundary, opportunity-conditioned scoring,
         new functions in self_correction_v2.py, unit tests
  │
  ├── Commit + push + validate
  │
Stream 2: Item Quarantine (CJ-009)
  Plan: docs/plans/item_quarantine_v65.md
  Scope: scoring_status metadata in item JSONs, notebook filtering
  │
  ├── Commit + push + validate
  │
Stream 3: Abstention Pipeline (CJ-004, CJ-005)
  Plan: docs/plans/family_b_abstention_fixes_v65.md
  Scope: YAML config, new scoring functions in abstention_metrics.py,
         Unicode fix in grading_v2.py, unit tests
  │
  ├── Commit + push + validate
  │
Stream 4: Bug Fixes & Calibration (CJ-006, CJ-007, CJ-008)
  Scope: tri_label re-run prep, sc_c2_wc_005, calibration dual-run
  │
  ├── Commit + push + validate
  │
Stream 5: Documentation & Notebook Final Pass
  Scope: METHODOLOGY.md, README, scoring_overview, notebook version bumps
  │
  └── Final commit + push → ready for Kaggle upload
```

### Why sequential?

| Concern | Sequential fix |
|---------|---------------|
| Shared files (`self_correction_v2.py`, `abstention_metrics.py`) | Each stream owns its files; no merge conflicts |
| Accidental reversion | Tests gate each stream; regressions caught before next stream |
| Documentation drift | Docs updated per-stream, not at the end |
| Session timeout | Each stream is a recoverable unit (~15-30 min) |
| Context window | Orchestrator summarizes completed streams, doesn't carry raw output |

---

## Principles

### 1. Orchestrator Protection
- The orchestrator (main thread) holds irreplaceable project context
- NEVER delegate understanding to agents — orchestrator synthesizes
- Agents execute bounded tasks and return results
- If an agent fails/times out, orchestrator can re-spin with adjusted scope
- Orchestrator reads key changed files after each stream to verify intent

### 2. Commit-Gate Workflow
- Each stream: plan → implement → test → commit → validate → gate
- **Gate:** Orchestrator reviews stream output, confirms tests pass,
  then launches next stream. User can intervene at any gate.
- Commit messages reference CJ numbers and stream IDs
- Every commit is on `submission/v6.5` — rollback to any commit is safe

### 3. Model Selection

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Scoring logic (classify_transition, coarse_bucket, conditioned_rates) | opus | Semantic reasoning about transition categories |
| YAML config creation | sonnet | Mechanical — copying pattern from existing config |
| JSON data edits (scoring_status flags, tolerance fields) | sonnet | Bulk metadata updates |
| Unit test writing | opus | Needs to understand scoring contracts |
| Notebook cell edits | opus | Must understand scoring pipeline end-to-end |
| Grading engine fixes (Unicode, tolerance) | sonnet | Small, well-specified changes |
| Documentation updates | sonnet | Follows existing patterns |
| Integration validation | opus | Must reason about cross-file interactions |

### 4. Timeout Mitigation

| Risk | Mitigation |
|------|-----------|
| Stream exceeds 30 min | Break into sub-tasks; stream lead delegates to task agents |
| Agent timeout on large file | Provide exact line numbers and code snippets in prompt |
| Multiple agents queue | Max 3 parallel task agents per stream lead |
| Session timeout | Commit-gate ensures all work saved. New session picks up from last gate. |
| Context window fill | Orchestrator summarizes completed streams as 3-5 line status blocks |

### 5. Failure Recovery
- All plans committed as markdown before execution starts
- Each stream's changes are committed independently
- Agent prompts are self-contained: include file paths, line numbers, exact code to write
- A new session reads the last commit + plan files to reconstruct state
- Test suite grows with each stream — regression detection is cumulative

### 6. Agent Prompt Quality
- Brief agents like a colleague who just walked in — full context, no assumptions
- Include: file paths, line numbers, existing function signatures to preserve
- Include: what NOT to change (backward compat requirements)
- Include: expected output format and verification command
- For coding tasks: provide the plan excerpt, not the full plan

---

## Stream-Specific Agent Configurations

### Stream 1: C1/C2 Scoring

```
Stream Lead (opus, foreground)
├── Task: Implement coarse_transition_bucket + compute_conditioned_rates
│   (opus — scoring logic)
├── Task: Implement compute_family_c_headline_v65 + extend build_audit_row
│   (opus — scoring logic)
├── Task: Write unit tests for all new functions + regression tests
│   (opus — must understand scoring contracts)
└── Task: Update notebook cells to use v6.5 headline
    (opus — end-to-end pipeline understanding)
```

### Stream 2: Item Quarantine

```
Stream Lead (opus, foreground)
├── Task: Add scoring_status to family_c_items.json
│   (sonnet — bulk JSON edit)
├── Task: Add scoring_status to calibration items
│   (sonnet — bulk JSON edit)
└── Task: Update notebook filtering logic
    (opus — must filter correctly without breaking diagnostics)
```

### Stream 3: Abstention Pipeline

```
Stream Lead (opus, foreground)
├── Task: Create family_b_scoring.yaml
│   (sonnet — follows existing YAML pattern)
├── Task: Implement config loader + matrix from config
│   (opus — must preserve backward compat)
├── Task: Implement compute_family_b_score_v65 + answer-rate penalty
│   (opus — scoring logic)
├── Task: Unicode minus fix in grading_v2.py
│   (sonnet — 2-line change)
├── Task: Write unit tests
│   (opus — must understand scoring contracts)
└── Task: Update abstention notebook
    (opus — end-to-end pipeline)
```

### Stream 4: Bug Fixes & Calibration

```
Stream Lead (opus, foreground)
├── Task: Verify tri_label fix is deployed, prep re-run
│   (sonnet — code inspection)
├── Task: Fix sc_c2_wc_005 answer extraction
│   (opus — semantic parsing logic)
└── Task: Add calibration dual-run pattern
    (sonnet — copy pattern from abstention notebook)
```

### Stream 5: Documentation

```
Stream Lead (sonnet, foreground)
├── Task: Update METHODOLOGY.md
│   (sonnet — follows plan)
├── Task: Update README.md + scoring_overview.md
│   (sonnet — follows plan)
└── Task: Final notebook version bumps
    (sonnet — mechanical)
```

---

## Template: Stream Lead Prompt

```markdown
# Stream [N]: [Name]

## Your role
You are the stream lead for this workstream. Implement all changes
described below, then report back with: files changed, tests passing,
issues found.

## Plan
[Paste relevant plan excerpt — NOT the full plan]

## Files you own (read + write)
[Exact paths with line numbers for key functions]

## Files you must NOT modify
[Files owned by other streams]

## Backward compatibility requirements
[Functions that must continue working unchanged]

## Verification
Run: [exact test command]
Expected: [what passing looks like]

## Scope limits
- Do NOT modify files outside your ownership list
- Do NOT add features beyond the plan
- Do NOT refactor code you didn't change
- If you encounter an issue outside your scope, report it — don't fix it
```

## Template: Task Agent Prompt

```markdown
# Task: [specific bounded task]

## Context
[2-3 sentences — just enough to understand the task]

## Files
[Exact file paths + line numbers]

## What to do
[Numbered steps with code snippets where possible]

## What NOT to do
[Backward compat, scope limits]

## Output
[What to return or where to write]
```
