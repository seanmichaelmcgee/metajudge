# Family C Pilot Orchestrator Instructions

**Version:** v0.6.1
**Date:** 2026-03-29
**For:** Agent team tasked with smoke testing, piloting, and triaging Family C items
**Source branch:** `claude/family-c-build-v061`
**Your working branch:** `claude/plan-family-c-sprint-XMcbR`

---

## 0. What This Document Is

You are receiving a fully built Family C (Self-Correction) dataset package.
Your job is to **validate it works**, **run it against real models**, and
**triage the items into clean/quarantine sets**. You are NOT building new
items, NOT modifying scoring logic, and NOT touching Families A or B.

Your output is:
1. Code fixes committed to your branch (if anything breaks)
2. Raw pilot results saved to `outputs/family_c/`
3. A summary report at `outputs/family_c/pilot_report_v061.md`

---

## 1. Recontextualize Yourself

Read these files **in this order** before doing anything else:

| Order | File | Why |
|-------|------|-----|
| 1 | `SOUL.md` | Non-negotiable project principles. Wins on any conflict. |
| 2 | `CLAUDE.md` | Dev commands, package structure, hard rules |
| 3 | `planning/v1_architecture.md` | Overall architecture (skim §1-3) |
| 4 | `planning/family_c_sprint/00_executive_roadmap.md` | Why Family C, what it measures |
| 5 | `planning/family_c_sprint/11_integration_notes.md` | **KEY**: File manifest, scoring pipeline, model routing |
| 6 | `planning/family_c_sprint/12_validation_promotion.md` | **KEY**: Promotion criteria, success thresholds |
| 7 | `data/family_c/SCHEMA.md` | Item bundle field definitions |
| 8 | `config/family_c_scoring.yaml` | Scoring parameters (damage:gain ratios, rescaling) |

**Do not skip this.** The scoring has an intentionally inverted damage:gain
ratio (damage penalty EXCEEDS correction reward). This is correct and
grounded in prospect theory. Do not "fix" it.

---

## 2. Key File Locations

```
# Scoring
metajudge/scoring/self_correction_v2.py    # Production scoring module
config/family_c_scoring.yaml                # All tunable parameters

# Task runner
metajudge/tasks/self_correction_v2.py       # Prompt builders, grading, batch runner

# Item bundles
data/family_c/family_c_c1_candidates.json   # 15 C1 items (intrinsic, no evidence)
data/family_c/family_c_c2_candidates.json   # 20 C2 items (evidence-assisted)
data/family_c/SCHEMA.md                     # Schema reference

# OpenRouter client
scripts/openrouter/client.py                # Multi-model query utility

# Prior results (DO NOT RERUN — reference only)
outputs/results-narrative-v0551/             # v0.5.5.1.1 A+B results
data/clean_subset_manifest.json             # Excluded items from A/B
```

---

## 3. Branch Setup

```bash
git fetch origin claude/family-c-build-v061
git checkout -b claude/plan-family-c-sprint-XMcbR origin/claude/family-c-build-v061
```

All your work goes on `claude/plan-family-c-sprint-XMcbR`. Push regularly.

---

## 4. Environment Setup

```bash
pip install -e ".[dev]"
export OPENROUTER_API_KEY="<key will be provided at runtime>"
```

Verify the key is set:
```bash
python -c "import os; assert os.environ.get('OPENROUTER_API_KEY'), 'KEY NOT SET'"
```

---

## 5. Phase 1: Smoke Test

**Goal:** Confirm OpenRouter connectivity and all 5 models respond.

```bash
python scripts/openrouter/client.py
```

Expected output: 5 models, each showing `OK (<latency>ms)`.

**If any model fails:**
- 429 (rate limit): wait 30s, retry once
- 403/401: key issue — stop and report
- Timeout: increase timeout in `client.py` → `smoke_test()`, retry
- Network error: check proxy/firewall, report if persistent

Save the smoke test output to `outputs/family_c/smoke_test_results.txt`.

**Spin up approach:** This is a single sequential task. Run it directly, do
not parallelize.

---

## 6. Phase 2: Pilot Run (2 Tier-A Models)

**Goal:** Run all 35 items against DeepSeek-Chat and Grok-3-Mini.
Validate parsing, check stratum alignment, identify broken items.

### 6.1 Write the pilot runner

Create `scripts/pilot_family_c.py`. It should:

1. Load items from `data/family_c/family_c_c1_candidates.json` and
   `data/family_c/family_c_c2_candidates.json`
2. Import `run_family_c_batch` from `metajudge.tasks.self_correction_v2`
3. Import `query` from `scripts.openrouter.client`
4. Run each model through `run_family_c_batch(items, query, model, json_mode=True)`
5. Save raw audit rows to `outputs/family_c/pilot_raw_{model}.jsonl`
6. Save per-item summary to `outputs/family_c/pilot_summary_{model}.csv`

The CSV should have columns:
```
item_id, subfamily, stratum, normative_action, correct_1, correct_2,
transition, revised, conf_1, conf_2, base_score, scaled_score, model
```

### 6.2 Run pilot

Pilot models (Tier A only — cheap, fast):
- `deepseek-chat`
- `grok-3-mini`

**Budget guard:** 35 items × 2 turns × 2 models = 140 API calls.
At Tier A pricing this should be well under $1.

### 6.3 Spin up approach

Launch **two parallel agents**, one per model. Each agent:
1. Loads the items
2. Runs `run_family_c_batch` for its assigned model
3. Saves JSONL and CSV
4. Reports: items completed, parse failures, any errors

Then a **third sequential agent** merges results and produces the
pilot analysis (see §8).

**If `run_family_c_batch` fails or the task module has import errors:**
Fix the code. Common issues to watch for:
- Import path resolution (run from repo root, or use `PYTHONPATH=.`)
- `query` function signature mismatch (the batch runner expects
  `query_fn(model, messages, **kwargs) -> dict` with key `response_text`)
- JSON parsing failures (models may return markdown-wrapped JSON)

Commit fixes to your branch with clear commit messages.

---

## 7. Phase 3: Triage Items

**Goal:** Promote items to "clean" or quarantine them based on pilot data.

### 7.1 Triage criteria

For each of the 35 items, check:

| Check | Pass | Quarantine |
|-------|------|------------|
| JSON parse success (both models) | Both parse | Either fails |
| T1 accuracy matches stratum | Within ±20% of expected | Wildly off |
| Gold answer correctness | Gold is clearly right | Gold is wrong or ambiguous |
| Evidence snippet effectiveness (C2) | Creates appropriate pressure | Too obvious or no effect |

Expected stratum accuracy ranges:

| Stratum | Expected T1 accuracy | Quarantine if |
|---------|---------------------|---------------|
| wrong_to_right | 0–60% | >80% both models |
| right_to_right | 80–100% | <60% both models |
| deceptive_trap | 60–100% | <40% both models |
| unresolved | N/A (graded differently) | Both give identical flat answer |
| weak_challenge (C2) | 80–100% | <60% both models |

### 7.2 Update item files

For each item, update `draft_status` in the JSON:
- `"clean"` — passes all checks
- `"quarantine"` — fails any check; add explanation to `audit_notes`

Write the updated files back to:
- `data/family_c/family_c_c1_candidates.json`
- `data/family_c/family_c_c2_candidates.json`

### 7.3 Minimum viable set

We need ≥ 25 clean items total (≥10 C1, ≥15 C2). If retention drops
below 70%, flag it in the report — do NOT generate replacement items.

### 7.4 Spin up approach

This is analytical work on the pilot CSVs. Run a **single agent** that:
1. Reads both pilot summary CSVs
2. Applies triage criteria
3. Updates the JSON files
4. Produces a triage summary table

---

## 8. Deliverables

All outputs go in `outputs/family_c/`. Create the directory if needed.

### 8.1 Required files

| File | Content |
|------|---------|
| `outputs/family_c/smoke_test_results.txt` | Smoke test output (5 models, pass/fail) |
| `outputs/family_c/pilot_raw_deepseek-chat.jsonl` | Raw audit rows, DeepSeek |
| `outputs/family_c/pilot_raw_grok-3-mini.jsonl` | Raw audit rows, Grok |
| `outputs/family_c/pilot_summary_deepseek-chat.csv` | Per-item summary, DeepSeek |
| `outputs/family_c/pilot_summary_grok-3-mini.csv` | Per-item summary, Grok |
| `outputs/family_c/pilot_report_v061.md` | **Summary report** (see template below) |
| `data/family_c/family_c_c1_candidates.json` | Updated with draft_status |
| `data/family_c/family_c_c2_candidates.json` | Updated with draft_status |
| `scripts/pilot_family_c.py` | The pilot runner script |

### 8.2 Summary report template

`outputs/family_c/pilot_report_v061.md` must follow this structure:

```markdown
# Family C Pilot Report — v0.6.1

## Smoke Test
- Date/time:
- Models tested: [5]
- Results: [table: model, status, latency_ms]
- Blockers: [none / describe]

## Pilot Results

### Per-Model Summary
| Model | Items Run | Parse Success | Mean Scaled Score | Damage Rate | Revision Rate |
|-------|-----------|--------------|-------------------|-------------|---------------|
| deepseek-chat | 35 | X/35 | 0.XX | X% | X% |
| grok-3-mini | 35 | X/35 | 0.XX | X% | X% |

### Transition Distribution
| Transition | DeepSeek Count | Grok Count |
|------------|---------------|------------|
| correction_gain | | |
| maintain_correct | | |
| neutral_revision | | |
| damage | | |
| stubborn_wrong | | |
| failed_revision | | |

### C1 vs C2 Breakdown
| Subfamily | Model | Headline Score | Damage Rate |
|-----------|-------|---------------|-------------|
| C1 | deepseek-chat | | |
| C1 | grok-3-mini | | |
| C2 | deepseek-chat | | |
| C2 | grok-3-mini | | |

## Item Triage
| Status | C1 Count | C2 Count | Total |
|--------|----------|----------|-------|
| clean | | | |
| quarantine | | | |

### Quarantined Items
| item_id | Reason | Recommendation |
|---------|--------|---------------|
| ... | ... | ... |

## Code Issues Encountered
| Issue | File | Fix Applied | Commit |
|-------|------|-------------|--------|
| ... | ... | ... | ... |

## File Locations
All outputs: `outputs/family_c/`
Updated items: `data/family_c/`
Pilot script: `scripts/pilot_family_c.py`

## Recommendations for Full Sweep
- Ready for 5-model sweep? [yes/no]
- Items needing attention before sweep: [list]
- Estimated budget for full sweep: [$ estimate]
```

---

## 9. Agent Orchestration Plan

Here is the recommended agent spin-up sequence:

```
┌─────────────────────────────────┐
│  PHASE 1: Context + Smoke Test  │
│  Single agent, sequential       │
│  1. Read docs (§1)              │
│  2. Setup env (§4)              │
│  3. Run smoke test (§5)         │
│  4. Save results                │
│  Gate: all 5 models OK?         │
│         ↓ yes                   │
├─────────────────────────────────┤
│  PHASE 2: Pilot (parallel)      │
│                                 │
│  Agent A              Agent B   │
│  ┌──────────┐   ┌──────────┐   │
│  │ deepseek │   │ grok-3   │   │
│  │ 35 items │   │ 35 items │   │
│  │ save JSONL│   │ save JSONL│  │
│  │ save CSV │   │ save CSV │   │
│  └──────────┘   └──────────┘   │
│         ↓              ↓        │
│         └──────┬───────┘        │
│                ↓                │
├─────────────────────────────────┤
│  PHASE 3: Analysis + Triage     │
│  Single agent, sequential       │
│  1. Load both CSVs              │
│  2. Compute metrics             │
│  3. Apply triage criteria (§7)  │
│  4. Update JSON files           │
│  5. Write pilot_report_v061.md  │
│  6. Commit + push               │
└─────────────────────────────────┘
```

**Total: 4 agents** (1 setup, 2 parallel pilot, 1 analysis).
Do NOT spin up more than 2 agents concurrently during the pilot phase
to avoid hitting OpenRouter rate limits.

---

## 10. Hard Rules

1. **Do NOT rerun Families A or B.** Their results are final (v0.5.5.1.1).
2. **Do NOT modify scoring logic** in `self_correction_v2.py` or
   `family_c_scoring.yaml` unless you find a clear bug (document it).
3. **Do NOT generate replacement items.** Flag shortfalls in the report.
4. **Do NOT push to `main`.** All work stays on your branch.
5. **Budget cap:** $5 total for pilot phase. Tier A models only.
6. **Commit often.** Every phase completion = one commit minimum.
7. **If something breaks**, fix it, commit the fix with a clear message,
   note it in the report under "Code Issues Encountered."

---

## 11. Competition Context

This is for the Kaggle "Measuring Progress Toward AGI — Cognitive Abilities"
competition. Deadline: **April 16, 2026**. Budget: $500 total, $50/day.

MetaJudge measures metacognitive behavior — not reasoning ability. Family C
(Self-Correction) is the first Control-axis family. It tests whether models
can appropriately revise incorrect answers AND resist inappropriately
revising correct ones. The key insight: **damage (correct→wrong) is scored
more harshly than correction (wrong→correct) is rewarded.** This is
intentional and grounded in prospect theory.

The pilot phase you're running is Gate 1 in our validation protocol.
Your report determines whether we proceed to the full 5-model sweep
or need to fix items first.
