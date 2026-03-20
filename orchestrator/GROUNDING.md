# Orchestrator Grounding Protocol

This document defines how the orchestrator (and its agents) stay grounded
in the competition goal across sessions. Read this before doing anything.

---

## Competition goal (never forget this)

**Win or place in the Metacognition track of the Kaggle "Measuring Progress Toward AGI" competition.**

The deliverable is:
1. A Kaggle Community Benchmark with a single task (`metacog_calibration_v1_batch`)
2. A 1500-word writeup linking that benchmark
3. The benchmark must demonstrate discriminatory power across frontier models

The deadline is **April 16, 2026**. There is no partial credit for unsubmitted work.

---

## Session startup protocol

Every orchestration session MUST begin with these steps:

### Step 1: Read STATE.json
```
Read orchestrator/STATE.json
```
This tells you: current phase, blocking issues, next actions, dataset status,
notebook status, and milestone history.

### Step 2: Read SOUL.md
```
Read SOUL.md (first 50 lines minimum)
```
This tells you: non-negotiable principles, canonical schema, what agents must/must not do.

### Step 3: Check recent commits
```
git log --oneline -5
```
This tells you: what changed since last session.

### Step 4: Check blocking issues
Look at `STATE.json → blocking_issues`. If any are CRITICAL, they must be
addressed before any other work.

### Step 5: Decide work plan
Based on `STATE.json → next_actions` and blocking issues, decide what to work on.
Do NOT start new work streams while blockers are open.

---

## Decision framework

When choosing what to do, always ask:

1. **Does this serve discriminatory power?** The V2 dataset failed because it was
   too easy. Every change should make the benchmark harder to game or more
   discriminating across models.

2. **Does this serve submission readiness?** We need a working notebook with
   frozen data, passing success criteria, and a writeup. If something doesn't
   move us toward submission, defer it.

3. **Is this the minimum effective change?** SOUL.md says "Do not redesign from
   scratch." Prefer patches over rewrites. Prefer targeted fixes over sweeping changes.

4. **Can the user execute this in Kaggle?** The final notebook must run in
   Kaggle's environment. Any change that can't be tested there is speculative.

---

## File hierarchy (what lives where)

| Directory | Purpose | Who modifies |
|-----------|---------|-------------|
| `orchestrator/` | Orchestration state, agent definitions, grounding | Orchestrator only |
| `SOUL.md` | Governing principles | Orchestrator (with EA review) |
| `CLAUDE.md` | Agent onboarding | Orchestrator |
| `data/` | Dataset files | Dataset Reconstructor agent |
| `notebooks/` | Kaggle notebooks | Notebook Engineer agent |
| `metajudge/` | Python scoring package | Code Engineer agent |
| `planning/` | Design docs, research | Document Generator agent |
| `docs/` | Architecture docs | Document Generator agent |
| `tests/` | Unit tests | Code Engineer agent |
| `config/` | Benchmark config | Orchestrator |

---

## Branch naming convention

| Pattern | Use |
|---------|-----|
| `orchestrator/<topic>` | Orchestrator-initiated work (this session) |
| `feat/<feature>` | Feature branches for specific capabilities |
| `fix/<issue>` | Bug fixes |
| `data/<dataset-version>` | Dataset changes |

All work goes to feature branches. PRs to main require human review.

---

## Anti-drift rules

1. **Never start a new family (B, C, D, E)** without the user's explicit approval.
   V1 is Family A only.

2. **Never modify the scoring function** without EA review. The Brier-derived
   score is the competition deliverable.

3. **Never spend Kaggle quota** from this VPS. Only the user runs notebooks in Kaggle.

4. **Never commit directly to main.** Always use a feature branch + PR.

5. **Update STATE.json** after every material change (dataset rebuilt, notebook
   patched, blocker resolved, milestone reached).

---

## Recovery protocol

If you lose context or aren't sure what's happening:

1. Read `orchestrator/STATE.json` — it has the full project state
2. Read `orchestrator/AGENTS.md` — it defines your agent roster
3. Read `SOUL.md` — it defines what you must/must not do
4. Run `git log --oneline -10` — see what changed recently
5. Check `orchestrator/DECISION_LOG.md` — see past decisions and rationale
