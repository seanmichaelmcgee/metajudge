# MetaJudge Agent Architecture

This document defines the agent roster for the MetaJudge-AGI project orchestrator.
Agents are split into two tiers: **permanent** (instantiated on every orchestration session)
and **ad-hoc** (spun up for specific tasks, then discarded).

The orchestrator itself does almost no execution. It reads core docs, reasons about
the project state, dispatches work to agents, and reviews their outputs.

---

## Tier 1 — Permanent Agents

These agents are conceptual roles that the orchestrator invokes on every work session.
They share access to the workspace and repo, but each has a defined scope and model choice.

### 1. Executive Analyst (EA)

| Property | Value |
|----------|-------|
| Model | `claude_opus_4_6` |
| Role | Strategic reasoning, quality gate, SOUL.md compliance |
| Invocation | Every session start; before any PR or merge; when ambiguity arises |

**Responsibilities:**
- Review orchestrator plans against SOUL.md and competition goals
- Validate that proposed changes serve discriminatory power / calibration quality
- Flag scope creep, architecture drift, or principle violations
- Produce go/no-go verdicts on dataset freezes, notebook submissions, writeup drafts
- Resolve conflicts between other agents' outputs

**Input:** Current `orchestrator/STATE.json`, proposed plan or diff, SOUL.md
**Output:** Verdict (APPROVE / REVISE / BLOCK) with reasoning

**When NOT to invoke:** Routine file operations, formatting, git mechanics

---

### 2. Document Generator (DG)

| Property | Value |
|----------|-------|
| Model | `claude_sonnet_4_6` |
| Role | Produce all written artifacts: docs, writeup, commit messages, PR descriptions |
| Invocation | When any markdown, writeup prose, or documentation needs to be created or updated |

**Responsibilities:**
- Draft and revise the 1500-word competition writeup
- Update SOUL.md, README, planning docs when project state changes
- Generate commit messages that reference the relevant phase/family/milestone
- Produce PR descriptions with full context for human review
- Write progress reports and decision logs

**Input:** Task description, relevant source files, competition rubric
**Output:** Markdown or text artifacts, saved to workspace

**When NOT to invoke:** Code changes, data manipulation, git operations

---

### 3. Repo Manager (RM)

| Property | Value |
|----------|-------|
| Model | `claude_sonnet_4_6` |
| Role | All git operations, branch management, PR lifecycle |
| Invocation | When code/data needs to be committed, branches created, PRs opened |

**Responsibilities:**
- Create feature branches with consistent naming (`orchestrator/<topic>`)
- Stage, commit, and push changes with well-structured messages
- Open pull requests with full descriptions
- Verify branch state, resolve merge conflicts
- Maintain clean git history (no orphan branches, no stale PRs)

**Input:** Files to commit, branch name, commit message, PR details
**Output:** Commit SHAs, PR URLs, branch status

**When NOT to invoke:** Content generation, strategic decisions, data analysis

---

## Tier 2 — Ad-Hoc Agents

These are spun up for specific tasks and discarded after completion.
The orchestrator decides which to invoke based on the current work item.

### A. Dataset Reconstructor

| Property | Value |
|----------|-------|
| Model | `claude_sonnet_4_6` |
| Type | `general_purpose` subagent |
| Invocation | When dataset files need to be rebuilt, merged, validated, or exported |

**Task pattern:**
- Read batch source files + combined_survivors.json + CDM
- Fix truncation, normalize schema, validate counts
- Export canonical frozen artifact
- Run integrity checks (no duplicates, no truncation, schema consistency)

---

### B. Notebook Engineer

| Property | Value |
|----------|-------|
| Model | `claude_sonnet_4_6` |
| Type | `general_purpose` subagent |
| Invocation | When notebook cells need patching, new cells need writing, or notebook structure changes |

**Task pattern:**
- Read current notebook JSON
- Apply targeted patches to specific cells
- Validate notebook structure (cell count, %choose, task names)
- Preserve cells that don't need changes

---

### C. Research Scout

| Property | Value |
|----------|-------|
| Model | `claude_sonnet_4_6` |
| Type | `research` subagent |
| Invocation | When external information is needed (Kaggle docs, SDK changes, competition updates, academic refs) |

**Task pattern:**
- Search web for specific information
- Fetch and extract from URLs
- Cross-reference findings with repo assumptions
- Save findings to workspace files

---

### D. Code Engineer

| Property | Value |
|----------|-------|
| Model | `claude_sonnet_4_6` |
| Type | `general_purpose` subagent |
| Invocation | When Python code needs to be written, tested, or debugged |

**Task pattern:**
- Write Python scripts for data processing, validation, export
- Run tests and verify outputs
- Fix bugs in existing code

---

### E. Quality Auditor

| Property | Value |
|----------|-------|
| Model | `claude_opus_4_6` |
| Type | `general_purpose` subagent |
| Invocation | Before any PR merge, dataset freeze, or notebook publication |

**Task pattern:**
- Cross-check all files for internal consistency
- Verify SOUL.md compliance
- Check for deprecated field names, schema drift, count mismatches
- Produce a pass/fail report with specific findings

---

## Agent Communication Protocol

1. **Workspace is the shared bus.** Agents read from and write to `/home/user/workspace/metajudge-repo/`.
2. **No agent modifies files outside its scope** without orchestrator approval.
3. **Ad-hoc agents save outputs to workspace files** — they do not return large data inline.
4. **The orchestrator reviews all outputs** before passing to the Repo Manager for commit.
5. **STATE.json is the single source of truth** for project progress — agents read it, only the orchestrator updates it.

---

## Model Selection Rationale

- **Opus** for Executive Analyst and Quality Auditor: These roles require deep reasoning about
  tradeoffs, compliance, and strategic fit. The extra reasoning capability justifies the cost.
- **Sonnet** for all other roles: Fast, capable, cost-effective for execution tasks. Document
  generation, code writing, git operations, and data manipulation don't need Opus-level reasoning.
- The orchestrator itself runs on whatever model the platform assigns — it delegates
  all heavy lifting to agents.
