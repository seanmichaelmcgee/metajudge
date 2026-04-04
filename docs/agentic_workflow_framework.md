# MetaJudge Agentic Workflow Framework

## Purpose

Standard operating procedure for complex multi-agent tasks in this project.
Designed to balance thoroughness (opus reasoning) with speed (sonnet execution)
while protecting against session timeout and context loss.

---

## Hierarchy

```
ORCHESTRATOR (main context — opus)
│   Holds full project context. Never delegated.
│   Commits frequently. Stops for user input at phase boundaries.
│
├── EXEC ASSISTANT (1 per large task — opus, background)
│   │   Manages one major workstream. Reports back to orchestrator.
│   │   Has task-specific context loaded via prompt.
│   │
│   ├── ADMIN AGENT (up to 3 per exec — sonnet, background)
│   │   │   Coordinates sub-teams. Collates results.
│   │   │
│   │   ├── WORKER (up to 3 per admin — sonnet or opus)
│   │   │   Executes specific bounded tasks.
│   │   │   Model selection:
│   │   │     opus: complex reasoning, semantic grading judgments
│   │   │     sonnet: data parsing, formatting, computation
│   │   │
│   │   ├── WORKER
│   │   └── WORKER
│   │
│   ├── ADMIN AGENT
│   └── ADMIN AGENT
│
└── EXEC ASSISTANT (for second workstream, if needed)
```

## Principles

### 1. Orchestrator Protection
- The orchestrator (main thread) holds irreplaceable project context
- NEVER delegate understanding to agents — orchestrator synthesizes
- Agents execute bounded tasks and return results
- If an agent fails/times out, orchestrator can re-spin with adjusted scope

### 2. Commit-First Workflow
- Codify plan as markdown → commit → THEN execute
- After each agent completes → commit results → THEN launch next
- Phase boundaries: commit + push + stop for user input
- Commit messages include: what's done, what's running, what's next

### 3. Model Selection

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Semantic grading judgment | opus | Needs reasoning about answer equivalence |
| Cross-referencing registry | sonnet | Mechanical lookup + comparison |
| Data parsing/formatting | sonnet | No complex reasoning needed |
| Synthesizing findings | opus | Needs to weigh evidence and form conclusions |
| Writing reports | sonnet | Follows template, fills in data |
| Debugging grading issues | opus | Needs to trace code logic |

### 4. Timeout Mitigation

| Risk | Mitigation |
|------|-----------|
| Agent exceeds 30 min | Chunk work into <15 min units |
| Multiple agents queue | Launch max 3 parallel, monitor |
| Session timeout | Frequent commits preserve all work |
| Context window fill | Orchestrator summarizes, doesn't paste full agent output |

### 5. Failure Recovery
- All plans and intermediate results are committed markdown files
- Canonical dataset (JSON) can reconstruct any analysis
- Agent prompts are self-contained (include file paths, criteria)
- A new session can pick up from the last commit message

---

## Applying This Framework

### For Deep Per-Model Audits (Task A)
```
Orchestrator
└── 3 Worker agents (sonnet, parallel)
    ├── Flash audit (focused: wrong items + 10 spot-checks/task)
    ├── Gemma-26b audit (same scope)
    └── GPT-5.4 audit (same scope)
```
No exec/admin needed — scope is bounded, orchestrator collates.

### For Intensive Cross-Model Audit (Task B)
```
Orchestrator
└── Exec Assistant (opus, sequential)
    ├── Phase 1: Item selection (orchestrator does this inline)
    ├── Phase 2: Per-task deep analysis
    │   ├── Admin: Calibration (sonnet)
    │   │   └── 5 item analysts (sonnet, questions are mechanical)
    │   ├── Admin: Abstention (sonnet)
    │   │   └── 5 item analysts
    │   ├── Admin: SC C1 (opus — transition reasoning is complex)
    │   │   └── 5 item analysts (opus)
    │   └── Admin: SC C2 (opus)
    │       └── 5 item analysts (opus)
    └── Phase 3: Synthesis (opus — weighing cross-model patterns)
```

---

## Template: Agent Task Prompt

```markdown
# Task: [specific bounded task]

## Context (minimal)
[2-3 sentences about the project, just enough to understand the task]

## Data locations
[Exact file paths]

## What to do
[Specific steps, numbered]

## Output format
[Exact file path and structure]

## Scope limits
[What NOT to do — prevents scope creep and timeout]
```
